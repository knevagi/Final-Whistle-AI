#!/usr/bin/env python3
"""
English Football Fixture Service
A Python service that manages English football fixtures and automatically triggers
the crew AI system to create articles after each match.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import time
from pathlib import Path

# Add the parent directory to the path to import crew_workflow
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from dotenv import load_dotenv
from crew_workflow import AutonomousSportsBlogCrew
import google.generativeai as genai
from PIL import Image
import io
import base64

# Load environment variables
load_dotenv()

# Configure logging (keeping for errors only)
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fixture_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Fixture:
    """Data class for fixture information"""
    id: str
    competition: str
    season: str
    match_date: str
    match_time: Optional[str]
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    venue: Optional[str]
    matchday: Optional[int]
    round: Optional[str]

class FixtureService:
    """
    Service for managing English football fixtures and triggering crew AI processing
    """
    
    def __init__(self):
        """
        Initialize the fixture service
        """
        # Get Supabase configuration
        from config import FixtureServiceConfig
        try:
            supabase_url, supabase_key = FixtureServiceConfig.get_supabase_config()
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except ValueError as e:
            raise ValueError(f"Supabase configuration error: {e}")
        
        # Initialize the crew AI system
        self.crew = AutonomousSportsBlogCrew()
        
        # Configure Google Generative AI for image generation
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        print("✅ Fixture Service initialized successfully")
    


    def test_connection(self):
        """Test Supabase connection"""
        try:
            # Test with a simple query
            result = self.supabase.table('fixtures').select('*').limit(1).execute()
            print("✅ Supabase connection successful")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def generate_image_with_gemini(self, article_title: str, article_content: str = "") -> Optional[bytes]:
        """Generate an image using Gemini 2.5 Flash Image Preview based on article title and content"""
        try:
            # Extract key information from article content for more accurate image generation
            content_summary = ""
            if article_content:
                # Take first 200 characters of content for context
                content_summary = article_content[:200] + "..." if len(article_content) > 200 else article_content
            
            # Create a detailed prompt for football-related image generation
            prompt = f"""Create a professional football match thumbnail image for the article titled: "{article_title}". 
            
            Article context: {content_summary}
            
            The image should be:
            - 400x250 pixels
            - Professional sports photography style
            - Football/soccer themed
            - High quality and engaging
            - Suitable for a sports blog thumbnail
            - Clean and modern design with football elements like stadium, players, or match action
            - Dynamic and exciting composition
            - There should not be any text in the image
            - Professional lighting and colors
            - Reflect the specific match or teams mentioned in the article context"""
            
            # Use Gemini's image generation model
            model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
            
            # Generate the image using the prompt
            response = model.generate_content(prompt)
            
            # Check if the response contains image data
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Extract image data
                        image_data = part.inline_data.data
                        
                        # Check if data is already in bytes format or needs base64 decoding
                        if isinstance(image_data, bytes):
                            decoded_data = image_data
                        else:
                            decoded_data = base64.b64decode(image_data)
                        
                        # Validate image format
                        if decoded_data.startswith(b'\xff\xd8') or decoded_data.startswith(b'\x89\x50\x4e\x47'):
                            print(f"✅ Generated image for article: {article_title}")
                            return decoded_data
            
            # If no image data found, create a fallback image using PIL
            print(f"⚠️ No image data returned from Gemini for article: {article_title}")
            img = Image.new('RGB', (400, 250), color='#1e40af')  # Blue background
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            print(f"✅ Created fallback image for article: {article_title}")
            return img_buffer.getvalue()
            
        except Exception as e:
            print(f"❌ Error generating image with Gemini: {e}")
            return None
    
    def upload_image_to_storage(self, article_id: str, image_data: bytes) -> Optional[str]:
        """Upload image to Supabase storage and return the public URL"""
        try:
            # Upload the image to Supabase storage
            response = self.supabase.storage.from_('article-images').upload(
                f"{article_id}.jpg",
                image_data,
                file_options={"content-type": "image/jpeg"}
            )
            
            if response:
                # Get the public URL
                public_url = self.supabase.storage.from_('article-images').get_public_url(f"{article_id}.jpg")
                print(f"✅ Uploaded image for article {article_id}")
                
                # Handle different URL formats
                if isinstance(public_url, dict) and 'publicUrl' in public_url:
                    return public_url['publicUrl']
                elif isinstance(public_url, str):
                    return public_url
                else:
                    # Fallback to manual construction
                    supabase_url = os.getenv('SUPABASE_URL')
                    if supabase_url:
                        return f"{supabase_url}/storage/v1/object/public/article-images/{article_id}.jpg"
                    return str(public_url)
            else:
                print(f"❌ Failed to upload image for article {article_id}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading image for article {article_id}: {e}")
            return None
    

    
    async def get_unprocessed_completed_fixtures(self) -> List[Fixture]:
        """
        Get all completed fixtures that haven't been processed by the crew
        
        A fixture is considered completed if it has been more than 3 hours since the match started.
        All match dates and times are in GMT.
        
        Returns:
            List of unprocessed completed fixtures
        """
        try:
            from datetime import datetime
            
            # Current time in GMT
            now_gmt = datetime.utcnow()
            
            print(f"🔍 Looking for all completed fixtures...")
            print(f"🕒 Current GMT time: {now_gmt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get all fixtures (no date filtering)
            all_fixtures = self.supabase.table('fixtures').select(
                'id, competition, season, match_date, match_time, home_team, away_team, '
                'home_score, away_score, status, venue, matchday, round'
            ).execute()
            
            # Get processed fixture IDs
            processed = self.supabase.table('fixture_processing_status').select(
                'fixture_id'
            ).eq('processing_status', 'completed').execute()
            
            processed_ids = {row['fixture_id'] for row in processed.data}
            
            # Filter fixtures based on completion time (3+ hours since match start)
            fixtures = []
            for row in all_fixtures.data:
                if row['id'] not in processed_ids:
                    try:
                        # Parse match date and time (GMT)
                        match_date_str = row['match_date']
                        match_time_str = row['match_time'] or '15:00:00'  # Default to 3 PM if no time
                        
                        # Handle both HH:MM and HH:MM:SS formats
                        if match_time_str and len(match_time_str.split(':')) == 2:
                            # Add seconds if missing (HH:MM -> HH:MM:SS)
                            match_time_str = f"{match_time_str}:00"
                        
                        # Combine date and time to create full datetime
                        match_datetime_str = f"{match_date_str} {match_time_str}"
                        match_datetime_gmt = datetime.strptime(match_datetime_str, '%Y-%m-%d %H:%M:%S')
                        
                        # Calculate time elapsed since match start
                        time_since_match = now_gmt - match_datetime_gmt
                        hours_since_match = time_since_match.total_seconds() / 3600
                        
                        # Check if fixture is completed (3+ hours since start)
                        is_completed = hours_since_match >= 3
                        
                        if is_completed:
                            print(f"⚽ Found completed fixture: {row['home_team']} vs {row['away_team']} "
                                  f"({match_datetime_gmt.strftime('%Y-%m-%d %H:%M')} GMT, "
                                  f"{hours_since_match:.1f}h ago)")
                            
                            fixtures.append(Fixture(
                                id=str(row['id']),
                                competition=row['competition'],
                                season=row['season'],
                                match_date=str(row['match_date']),
                                match_time=str(row['match_time']) if row['match_time'] else None,
                                home_team=row['home_team'],
                                away_team=row['away_team'],
                                home_score=row['home_score'],
                                away_score=row['away_score'],
                                status=row['status'],
                                venue=row['venue'],
                                matchday=row['matchday'],
                                round=row['round']
                            ))                            
                    except ValueError as e:
                        print(f"⚠️ Error parsing date/time for fixture {row['id']}: {e}")
                        continue
            
            print(f"📋 Found {len(fixtures)} unprocessed completed fixtures")
            return fixtures
            
        except Exception as e:
            logger.error(f"Error getting unprocessed fixtures: {e}")
            raise
    
    async def mark_fixture_processing_started(self, fixture_id: str) -> str:
        """
        Mark a fixture as processing started
        
        Args:
            fixture_id: ID of the fixture
            
        Returns:
            Processing status ID
        """
        try:
            crew_execution_id = f"crew_{int(time.time())}"
            
            # Check if processing status already exists
            existing = self.supabase.table('fixture_processing_status').select('id').eq(
                'fixture_id', fixture_id
            ).execute()
            
            if existing.data:
                # Update existing
                processing_id = existing.data[0]['id']
                self.supabase.table('fixture_processing_status').update({
                    'processing_status': 'in_progress',
                    'crew_execution_id': crew_execution_id
                }).eq('id', processing_id).execute()
            else:
                # Insert new
                result = self.supabase.table('fixture_processing_status').insert({
                    'fixture_id': fixture_id,
                    'processing_status': 'in_progress',
                    'crew_execution_id': crew_execution_id
                }).execute()
                processing_id = result.data[0]['id']
                
            
            print(f"🟡 Marked fixture {fixture_id} as processing started")
            return str(processing_id)
            
        except Exception as e:
            logger.error(f"Error marking fixture processing started: {e}")
            raise
    
    async def mark_fixture_processing_completed(self, fixture_id: str, articles_generated: int, topics_generated: int):
        """
        Mark a fixture as processing completed
        
        Args:
            fixture_id: ID of the fixture
            articles_generated: Number of articles generated
            topics_generated: Number of topics generated
        """
        try:
            self.supabase.table('fixture_processing_status').update({
                'processing_status': 'completed',
                'articles_generated': articles_generated,
                'topics_generated': topics_generated
            }).eq('fixture_id', fixture_id).execute()
            
            print(f"✅ Marked fixture {fixture_id} as processing completed")
            
        except Exception as e:
            logger.error(f"Error marking fixture processing completed: {e}")
            raise
    
    async def mark_fixture_processing_failed(self, fixture_id: str, error_message: str):
        """
        Mark a fixture as processing failed
        
        Args:
            fixture_id: ID of the fixture
            error_message: Error message
        """
        try:
            self.supabase.table('fixture_processing_status').update({
                'processing_status': 'failed',
                'error_message': error_message
            }).eq('fixture_id', fixture_id).execute()
            
            logger.error(f"Marked fixture {fixture_id} as processing failed: {error_message}")
            
        except Exception as e:
            logger.error(f"Error marking fixture processing failed: {e}")
            raise
    
    async def save_generated_articles(self, fixture_id: str, processing_id: str, articles: List[Dict]):
        """
        Save generated articles to the database and export as markdown files
        
        Args:
            fixture_id: ID of the fixture
            processing_id: ID of the processing status
            articles: List of article dictionaries
        """
        try:
            # Create generated_articles directory if it doesn't exist
            articles_dir = Path("generated_articles")
            articles_dir.mkdir(exist_ok=True)
            
            article_data = []
            markdown_files_created = []
            
            for i, article in enumerate(articles):
                # Get article details
                title = article.get('title', f'Article_{i+1}')
                content = article.get('content', '')
                article_type = article.get('article_type', 'match_report')
                word_count = article.get('word_count', 0)
                fixture_match = article.get('fixture_match', 'Unknown_Match')
                match_date = article.get('match_date', 'Unknown_Date')
                
                # Create safe filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')[:100]  # Limit length
                
                # Create filename with timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{safe_title}.md"
                file_path = articles_dir / filename
                
                # Create markdown content with metadata
                markdown_content = f"""---
                                    title: "{title}"
                                    fixture_id: {fixture_id}
                                    processing_id: {processing_id}
                                    article_type: {article_type}
                                    word_count: {word_count}
                                    fixture_match: "{fixture_match}"
                                    match_date: {match_date}
                                    generated_date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                                    ---

                                    # {title}

                                    {content}

                                    ---
                                    *Generated by Autonomous Sports Blog AI*  
                                    *Fixture ID: {fixture_id}*  
                                    *Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
                                    """
                
                # Save markdown file
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    markdown_files_created.append(str(file_path))
                    print(f"📄 Created markdown file: {filename}")
                except Exception as e:
                    print(f"⚠️ Failed to create markdown file {filename}: {e}")
                    markdown_files_created.append("")
                
                # Prepare database data
                article_data.append({
                    'fixture_id': fixture_id,
                    'processing_id': processing_id,
                    'title': title,
                    'content': content,
                    'article_type': article_type,
                    'word_count': word_count,
                    'file_path': str(file_path) if markdown_files_created[-1] else ''
                })
            
            # Save to database and generate images
            if article_data:
                # Insert articles and get their IDs
                insert_result = self.supabase.table('generated_articles').insert(article_data).execute()
                
                # Generate images for each article
                for i, article in enumerate(articles):
                    if i < len(insert_result.data):
                        article_id = insert_result.data[i]['id']
                        title = article.get('title', '')
                        content = article.get('content', '')
                        
                        print(f"🖼️ Generating image for article: {title}")
                        
                        # Generate image using Gemini
                        image_data = self.generate_image_with_gemini(title, content)
                        
                        if image_data:
                            # Upload to Supabase storage
                            image_url = self.upload_image_to_storage(article_id, image_data)
                            if image_url:
                                print(f"✅ Image generated and stored for article: {title}")
                            else:
                                print(f"⚠️ Image generated but failed to upload for article: {title}")
                        else:
                            print(f"⚠️ Failed to generate image for article: {title}")
            
            successful_files = [f for f in markdown_files_created if f]
            print(f"💾 Saved {len(articles)} articles for fixture {fixture_id}")
            print(f"📁 Created {len(successful_files)} markdown files in generated_articles/")
            
        except Exception as e:
            logger.error(f"Error saving articles: {e}")
            raise
    
    async def process_completed_fixture(self, fixture: Fixture) -> bool:
        """
        Process a completed fixture using the crew AI system
        
        Args:
            fixture: Fixture object to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print(f"⚽ Processing completed fixture: {fixture.home_team} vs {fixture.away_team} (Date: {fixture.match_date})")
            
            # Mark processing as started
            processing_id = await self.mark_fixture_processing_started(fixture.id)
            
            # Prepare fixture details for the crew AI
            fixture_details = {
                'id': fixture.id,  # Add fixture ID for score updates
                'home_team': fixture.home_team,
                'away_team': fixture.away_team,
                'home_score': fixture.home_score,
                'away_score': fixture.away_score,
                'match_date': fixture.match_date,
                'match_time': fixture.match_time,
                'competition': fixture.competition,
                'season': fixture.season,
                'venue': fixture.venue,
                'matchday': fixture.matchday,
                'round': fixture.round
            }
            
            print(f"📝 Generating articles for specific fixture: {fixture.home_team} {fixture.home_score}-{fixture.away_score} {fixture.away_team}")
            
            # Generate articles using the crew for this specific fixture
            result = self.crew.create_articles_for_specific_fixture(
                fixture_details=fixture_details,
                target_length="800-1200 words"
            )
            
            if not result or 'error' in result:
                error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                await self.mark_fixture_processing_failed(fixture.id, error_msg)
                return False
            
            # Extract articles from the result
            articles = result.get('articles', [])
            topics = result.get('topics', [])
            
            # Check if score was updated during data collection
            score_update_result = result.get('score_update_result', {})
            if score_update_result.get('updated', False):
                print(f"✅ Score updated during data collection: {score_update_result.get('old_score', 'N/A')} → {score_update_result.get('found_score', 'N/A')}")
            elif score_update_result.get('found', False):
                print(f"ℹ️ Score confirmed during data collection: {score_update_result.get('found_score', 'N/A')}")
            
            print(f"📰 Generated {len(articles)} articles and {len(topics)} topics for {fixture.home_team} vs {fixture.away_team}")
            
            # Save articles to database
            if articles:
                await self.save_generated_articles(fixture.id, processing_id, articles)
            
            # Mark processing as completed
            await self.mark_fixture_processing_completed(
                fixture.id,
                len(articles),
                len(topics)
            )
            
            print(f"🎉 Successfully processed fixture {fixture.id}: {fixture.home_team} vs {fixture.away_team}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing fixture {fixture.id}: {e}")
            await self.mark_fixture_processing_failed(fixture.id, str(e))
            return False
        
    async def run_fixture_processing(self):
        """
        Process all completed fixtures that haven't been processed yet
        """
        print(f"🚀 Starting fixture processing for all completed fixtures...")
        
        try:
            # Get unprocessed completed fixtures
            fixtures = await self.get_unprocessed_completed_fixtures()
            
            if not fixtures:
                print(f"ℹ️ No unprocessed completed fixtures found")
                return
            
            # Process each fixture
            for fixture in fixtures:
                print(f"⚡ Processing fixture: {fixture.home_team} vs {fixture.away_team} (Date: {fixture.match_date})")
                success = await self.process_completed_fixture(fixture)
                
                if success:
                    print(f"✅ Successfully processed fixture: {fixture.home_team} vs {fixture.away_team}")
                else:
                    print(f"❌ Failed to process fixture: {fixture.home_team} vs {fixture.away_team}")
                    
        except Exception as e:
            logger.error(f"Error in fixture processing: {e}")
            raise
    
    async def get_articles_without_images(self) -> List[Dict]:
        """
        Get all articles that don't have images in Supabase storage
        
        Returns:
            List of article dictionaries that need images
        """
        try:
            # Get all articles from the database
            articles_result = self.supabase.table('generated_articles').select(
                'id, title, content, fixture_id, fixtures!inner(home_team, away_team, match_date)'
            ).execute()
            
            articles_without_images = []
            
            for article in articles_result.data:
                article_id = article['id']
                
                # Check if image exists in Supabase storage
                try:
                    # Try to get the file from storage
                    self.supabase.storage.from_('article-images').download(f"{article_id}.jpg")
                    # If no exception, image exists, skip this article
                    continue
                except Exception:
                    # Image doesn't exist, add to list
                    articles_without_images.append({
                        'id': article_id,
                        'title': article['title'],
                        'content': article['content'],
                        'fixture_id': article['fixture_id'],
                        'fixture': article.get('fixtures', {})
                    })
            
            print(f"📋 Found {len(articles_without_images)} articles without images")
            return articles_without_images
            
        except Exception as e:
            logger.error(f"Error getting articles without images: {e}")
            return []
    
    async def generate_images_for_articles(self, articles: List[Dict]):
        """
        Generate images for articles that don't have them
        
        Args:
            articles: List of article dictionaries
        """
        if not articles:
            print("ℹ️ No articles need image generation")
            return
        
        print(f"🖼️ Generating images for {len(articles)} articles...")
        
        for article in articles:
            article_id = article['id']
            title = article['title']
            content = article['content']
            fixture = article.get('fixture', {})
            
            print(f"🖼️ Generating image for article: {title}")
            print(f"   Fixture: {fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}")
            
            try:
                # Generate image using Gemini
                image_data = self.generate_image_with_gemini(title, content)
                
                if image_data:
                    # Upload to Supabase storage
                    image_url = self.upload_image_to_storage(article_id, image_data)
                    if image_url:
                        print(f"✅ Image generated and stored for article: {title}")
                    else:
                        print(f"⚠️ Image generated but failed to upload for article: {title}")
                else:
                    print(f"⚠️ Failed to generate image for article: {title}")
                
                # Add a small delay to avoid overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error generating image for article {title}: {e}")
                continue
        
        print(f"🏁 Image generation completed for {len(articles)} articles")

    async def run_fixture_processing(self):
        """
        Process all completed fixtures that haven't been processed yet
        and generate images for articles that don't have them
        """
        print(f"🚀 Starting fixture processing for all completed fixtures...")
        
        try:
            # Step 1: Get unprocessed completed fixtures
            fixtures = await self.get_unprocessed_completed_fixtures()
            
            if fixtures:
                print(f"📝 Processing {len(fixtures)} unprocessed completed fixtures...")
                # Process each fixture
                for fixture in fixtures:
                    print(f"⚡ Processing fixture: {fixture.home_team} vs {fixture.away_team} (Date: {fixture.match_date})")
                    success = await self.process_completed_fixture(fixture)
                    
                    if success:
                        print(f"✅ Successfully processed fixture: {fixture.home_team} vs {fixture.away_team}")
                    else:
                        print(f"❌ Failed to process fixture: {fixture.home_team} vs {fixture.away_team}")
                    
                    # Add a small delay between processing to avoid overwhelming the API
                    await asyncio.sleep(2)
                
                print(f"✅ Processed {len(fixtures)} unprocessed completed fixtures.")
            else:
                print(f"ℹ️ No unprocessed completed fixtures found")
            
            # Step 2: Generate images for articles that don't have them
            print(f"🖼️ Checking for articles without images...")
            articles_without_images = await self.get_articles_without_images()
            
            if articles_without_images:
                await self.generate_images_for_articles(articles_without_images)
            else:
                print(f"ℹ️ All articles already have images")
            
            print(f"🏁 Fixture processing completed.")
            
        except Exception as e:
            logger.error(f"Error during fixture processing: {e}")
    
    async def run_service(self, processing_interval: int = 3600):
        """
        Run the fixture service continuously to process all completed fixtures
        
        Args:
            processing_interval: Interval in seconds between processing runs (default: 5 minutes)
        """
        print("🚀 Starting Fixture Processing Service...")
        print(f"⏰ Processing interval: {processing_interval} seconds")
        print(f"📅 Processing all completed fixtures")
        
        try:
            while True:
                # Run fixture processing for all completed fixtures
                await self.run_fixture_processing()
                
                # Wait for next cycle
                print(f"⏳ Processing cycle completed. Waiting {processing_interval} seconds...")
                await asyncio.sleep(processing_interval)
                
        except KeyboardInterrupt:
            print("🛑 Fixture Service stopped by user")
        except Exception as e:
            logger.error(f"Fixture Service error: {e}")
            raise

async def main():
    """Main entry point for the fixture service"""
    try:
        # Initialize the service
        service = FixtureService()
        
        # Run the processing service
        await service.run_service()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
