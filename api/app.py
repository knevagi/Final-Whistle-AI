#!/usr/bin/env python3
"""
Football Focus API - Flask Backend
Provides REST API endpoints for the Football Focus blog website
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import io
import base64
from PIL import Image
import shutil

# Add the parent directory to the path to import from crew_ai
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Google Generative AI
# Note: You need to set GOOGLE_API_KEY in your .env file
# For image generation, ensure you have access to Gemini 2.5 Flash Image Preview
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api:Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Helper functions for image generation and storage
def ensure_images_directory():
    """Ensure the local images directory exists"""
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"INFO: Created local images directory: {images_dir}")
    return images_dir

def clean_supabase_url(url):
    """Clean and validate Supabase storage URLs"""
    if not url:
        return None
    
    # Convert to string if it's not already
    url_str = str(url)
    
    # Remove trailing query parameters that might be malformed
    url_str = url_str.rstrip('?').rstrip('&')
    
    # Ensure it's a valid URL
    if url_str.startswith('http'):
        return url_str
    
    return None

def ensure_supabase_bucket():
    """Ensure the article-images bucket exists in Supabase storage"""
    try:
        bucket_name = 'article-images'
        
        # Try to list files in the bucket to check if it exists
        try:
            files_response = api.storage.from_(bucket_name).list()
            print(f"INFO: Bucket '{bucket_name}' exists and is accessible")
            print(f"DEBUG: Found {len(files_response)} files in bucket")
            return True
        except Exception as e:
            error_str = str(e)
            print(f"DEBUG: Bucket check error: {error_str}")
            
            if "Bucket not found" in error_str or "404" in error_str:
                print(f"ERROR: Bucket '{bucket_name}' not found")
                print(f"ERROR: Please check your Supabase dashboard:")
                print(f"ERROR: 1. Go to Storage section")
                print(f"ERROR: 2. Verify bucket '{bucket_name}' exists")
                print(f"ERROR: 3. Ensure bucket is set to PUBLIC")
                print(f"ERROR: 4. Check bucket permissions")
                return False
            elif "permission" in error_str.lower() or "unauthorized" in error_str.lower():
                print(f"ERROR: Permission denied accessing bucket '{bucket_name}'")
                print(f"ERROR: Check your Supabase API key permissions")
                print(f"ERROR: Ensure the key has storage access")
                return False
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                print(f"ERROR: Network error accessing bucket '{bucket_name}'")
                print(f"ERROR: Check your internet connection and Supabase URL")
                return False
            else:
                print(f"ERROR: Unexpected error checking bucket '{bucket_name}': {e}")
                print(f"ERROR: Error type: {type(e).__name__}")
                return False
                
    except Exception as e:
        print(f"ERROR: Error ensuring Supabase bucket: {e}")
        print(f"ERROR: Error type: {type(e).__name__}")
        return False

def store_image_locally(article_id: str, image_data: bytes) -> Optional[str]:
    """Store image locally in the images folder"""
    try:
        images_dir = ensure_images_directory()
        local_path = os.path.join(images_dir, f"{article_id}.jpg")
        
        # Write the image data to local file
        with open(local_path, 'wb') as f:
            f.write(image_data)
        
        print(f"SUCCESS: Stored image locally for article {article_id} at {local_path}")
        return local_path
        
    except Exception as e:
        print(f"ERROR: Failed to store image locally for article {article_id}: {e}")
        return None

def check_image_exists_in_storage(article_id: str) -> bool:
    """Check if an image exists in Supabase storage or locally for the given article ID"""
    try:
        # First check if image exists locally
        images_dir = ensure_images_directory()
        local_path = os.path.join(images_dir, f"{article_id}.jpg")
        if os.path.exists(local_path):
            print(f"DEBUG: Found local image for article {article_id}")
            return True
        
        # Then check Supabase storage
        response = api.storage.from_('article-images').download(f"{article_id}.jpg")
        if response is not None:
            print(f"DEBUG: Found Supabase image for article {article_id}")
            return True
            
        print(f"DEBUG: No image found for article {article_id}")
        return False
    except Exception as e:
        print(f"DEBUG: Image not found for article {article_id}: {e}")
        return False

def generate_image_with_gemini(article_title: str, article_content: str = "") -> Optional[bytes]:
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
        
        # First, test if the model can handle basic text generation
        print("DEBUG: Testing model with simple text generation first...")
        try:
            test_response = model.generate_content("Hello, can you generate images?")
            print(f"DEBUG: Model test successful: {test_response.text[:100]}...")
        except Exception as test_error:
            print(f"ERROR: Model test failed: {test_error}")
            print("ERROR: Model may not be available or accessible")
            return None
        
        # Generate the image using the prompt
        print(f"DEBUG: Attempting to generate image with prompt: {prompt[:100]}...")
        try:
            response = model.generate_content(prompt)
            print(f"DEBUG: API call successful, response type: {type(response)}")
        except Exception as api_error:
            print(f"ERROR: API call failed: {api_error}")
            print(f"DEBUG: Error type: {type(api_error)}")
            print(f"DEBUG: Full error details: {str(api_error)}")
            
            # Check if it's a server error
            if "500" in str(api_error) or "Internal" in str(api_error):
                print("ERROR: Google API server error - this is a temporary issue on Google's side")
                print("ERROR: The gemini-2.5-flash-image-preview model may not support image generation")
                print("ERROR: Falling back to placeholder image")
                return None
            
            # Try alternative approach with explicit generation config
            try:
                print("DEBUG: Trying alternative API call with generation config...")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'max_output_tokens': 8192,
                        'temperature': 0.7,
                    }
                )
                print(f"DEBUG: Alternative API call successful")
            except Exception as alt_error:
                print(f"ERROR: Alternative API call also failed: {alt_error}")
                print(f"ERROR: Both API calls failed, using fallback image")
                return None
        
        # Check if the response contains image data
        print(f"DEBUG: Response has parts: {hasattr(response, 'parts')}")
        if hasattr(response, 'parts') and response.parts:
            print(f"DEBUG: Number of parts: {len(response.parts)}")
            for i, part in enumerate(response.parts):
                print(f"DEBUG: Part {i} attributes: {dir(part)}")
                
                # Check all possible ways the part might contain image data
                if hasattr(part, 'inline_data') and part.inline_data:
                    print(f"DEBUG: Part {i} has inline_data with attributes: {dir(part.inline_data)}")
                    if hasattr(part.inline_data, 'mime_type'):
                        print(f"DEBUG: inline_data mime_type: {part.inline_data.mime_type}")
                
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Extract image data
                    image_data = part.inline_data.data
                    print(f"DEBUG: Found inline_data for article: {article_title}")
                    print(f"DEBUG: Raw image_data type: {type(image_data)}")
                    print(f"DEBUG: Raw image_data length: {len(image_data) if image_data else 0}")
                    print(f"DEBUG: Raw image_data first 100 chars: {str(image_data)[:100] if image_data else 'None'}")
                    
                    try:
                        # Check if data is already in bytes format (PNG/JPEG headers) or needs base64 decoding
                        if isinstance(image_data, bytes):
                            # Data is already in bytes format, use it directly
                            decoded_data = image_data
                            print(f"DEBUG: Image data is already in bytes format ({len(decoded_data)} bytes)")
                        else:
                            # Data needs base64 decoding
                            decoded_data = base64.b64decode(image_data)
                            print(f"DEBUG: Decoded base64 data length: {len(decoded_data)} bytes")
                        
                        print(f"DEBUG: First 20 bytes: {decoded_data[:20]}")
                        
                        # More flexible validation for different image formats
                        is_valid_image = False
                        image_format = "unknown"
                        
                        if decoded_data.startswith(b'\xff\xd8'):  # JPEG
                            is_valid_image = True
                            image_format = "JPEG"
                        elif decoded_data.startswith(b'\x89\x50\x4e\x47'):  # PNG
                            is_valid_image = True
                            image_format = "PNG"
                        elif decoded_data.startswith(b'RIFF') and b'WEBP' in decoded_data[:12]:  # WebP
                            is_valid_image = True
                            image_format = "WebP"
                        elif decoded_data.startswith(b'GIF87a') or decoded_data.startswith(b'GIF89a'):  # GIF
                            is_valid_image = True
                            image_format = "GIF"
                        elif len(decoded_data) > 1000:  # If it's large enough, might be a valid image
                            is_valid_image = True
                            image_format = "Unknown but large"
                        
                        if is_valid_image:
                            print(f"SUCCESS: Valid {image_format} image data detected ({len(decoded_data)} bytes)")
                            return decoded_data
                        else:
                            print(f"WARNING: Invalid image data detected ({len(decoded_data)} bytes)")
                            print(f"DEBUG: Data doesn't match known image headers")
                            
                            # If the data is very small, it might be an error message
                            if len(decoded_data) < 500:
                                try:
                                    error_text = decoded_data.decode('utf-8', errors='ignore')
                                    print(f"DEBUG: Small response might be text: {error_text}")
                                except:
                                    pass
                            return None
                            
                    except Exception as decode_error:
                        print(f"ERROR: Failed to decode image data: {decode_error}")
                        return None
                elif hasattr(part, 'text') and part.text:
                    # Check if the text contains base64 image data
                    text_content = part.text
                    print(f"DEBUG: Part {i} text content: {text_content[:200]}...")
                    print(f"DEBUG: Full text length: {len(text_content)}")
                    
                    # Check for various image data formats in text
                    if 'data:image' in text_content or 'base64' in text_content.lower():
                        print(f"SUCCESS: Found image data in text response for article: {article_title}")
                        # Extract base64 data from text
                        import re
                        base64_match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', text_content)
                        if base64_match:
                            try:
                                decoded_data = base64.b64decode(base64_match.group(1))
                                if len(decoded_data) > 100 and decoded_data.startswith(b'\xff\xd8'):
                                    print(f"DEBUG: Valid JPEG image data from text ({len(decoded_data)} bytes)")
                                    return decoded_data
                                else:
                                    print(f"WARNING: Invalid image data from text ({len(decoded_data)} bytes)")
                                    return None
                            except Exception as decode_error:
                                print(f"ERROR: Failed to decode image data from text: {decode_error}")
                                return None
        
        # Try alternative approach - check if response has text that might contain image data
        if hasattr(response, 'text') and response.text:
            print(f"INFO: Gemini response text: {response.text[:500]}...")
        
        # Check if there are other attributes we might have missed
        print(f"DEBUG: Response object attributes: {dir(response)}")
        if hasattr(response, 'candidates') and response.candidates:
            print(f"DEBUG: Response has {len(response.candidates)} candidates")
            for i, candidate in enumerate(response.candidates):
                print(f"DEBUG: Candidate {i} attributes: {dir(candidate)}")
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"DEBUG: Candidate {i} content attributes: {dir(candidate.content)}")
        
        # If no image data found, create a fallback image using PIL
        print(f"WARNING: No image data returned from Gemini for article: {article_title}")
        print(f"DEBUG: This might indicate the model returned only text or an error")
        
        # Create a fallback image with article title
        try:
            img = Image.new('RGB', (400, 250), color='#1e40af')  # Blue background
            
            # You could add text rendering here if needed
            # For now, just return the basic image
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            print(f"INFO: Created proper fallback image for article: {article_title}")
            return img_buffer.getvalue()
        except Exception as fallback_error:
            print(f"ERROR: Error creating fallback image: {fallback_error}")
            return None
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"ERROR: Gemini API quota exceeded. Please wait or upgrade your plan. Error: {e}")
        elif "not supported" in error_msg.lower() or "cannot generate" in error_msg.lower():
            print(f"ERROR: Image generation not supported with current model. Error: {e}")
        else:
            print(f"ERROR: Error generating image with Gemini: {e}")
        return None

def upload_image_to_storage(article_id: str, image_data: bytes) -> Optional[str]:
    """Upload image to Supabase storage and store locally, return the public URL"""
    try:
        # First store the image locally
        local_path = store_image_locally(article_id, image_data)
        if local_path:
            print(f"INFO: Image stored locally at {local_path}")
        
        # Check if Supabase bucket exists before trying to upload
        if not ensure_supabase_bucket():
            print(f"WARNING: Supabase bucket not available, skipping upload for article {article_id}")
            return None
        
        # Upload the image to Supabase storage
        response = api.storage.from_('article-images').upload(
            f"{article_id}.jpg",
            image_data,
            file_options={"content-type": "image/jpeg"}
        )
        
        if response:
            # Get the public URL
            public_url = api.storage.from_('article-images').get_public_url(f"{article_id}.jpg")
            print(f"SUCCESS: Uploaded image for article {article_id}")
            print(f"DEBUG: Upload public URL: {public_url}")
            
            # Handle different URL formats
            if isinstance(public_url, dict) and 'publicUrl' in public_url:
                actual_url = clean_supabase_url(public_url['publicUrl'])
                if actual_url:
                    print(f"DEBUG: Extracted upload URL: {actual_url}")
                    return actual_url
            elif isinstance(public_url, str):
                clean_url = clean_supabase_url(public_url)
                if clean_url:
                    print(f"DEBUG: Direct upload URL: {clean_url}")
                    return clean_url
            
            print(f"WARNING: Unexpected or invalid upload URL format: {public_url}")
            # Fallback to manual construction
            supabase_url = os.getenv('SUPABASE_URL')
            if supabase_url:
                manual_url = f"{supabase_url}/storage/v1/object/public/article-images/{article_id}.jpg"
                print(f"DEBUG: Manual upload URL: {manual_url}")
                return manual_url
            return str(public_url)
        else:
            print(f"ERROR: Failed to upload image for article {article_id}")
            return None
            
    except Exception as e:
        print(f"ERROR: Error uploading image for article {article_id}: {e}")
        return None

def get_or_generate_article_image(article_id: str, article_title: str, article_content: str = "") -> str:
    """Get existing image or generate new one for article"""
    try:
        # Step 1: Check if Supabase bucket exists
        if not ensure_supabase_bucket():
            print(f"WARNING: Supabase bucket not available, skipping Supabase check for article {article_id}")
            # Skip to local check
        else:
            # Step 2: Check if image exists in Supabase storage
            try:
                # First check if the file exists in the bucket
                files_response = api.storage.from_('article-images').list()
                file_exists = any(file['name'] == f"{article_id}.jpg" for file in files_response)
                
                if file_exists:
                    # Image exists in Supabase, return the URL
                    public_url = api.storage.from_('article-images').get_public_url(f"{article_id}.jpg")
                    print(f"INFO: Using existing Supabase image for article {article_id}")
                    print(f"DEBUG: Supabase public URL: {public_url}")
                    
                    # Check if the URL format is correct and try to fix it if needed
                    if isinstance(public_url, dict) and 'publicUrl' in public_url:
                        actual_url = clean_supabase_url(public_url['publicUrl'])
                        if actual_url:
                            print(f"DEBUG: Extracted public URL: {actual_url}")
                            return actual_url
                    elif isinstance(public_url, str):
                        clean_url = clean_supabase_url(public_url)
                        if clean_url:
                            print(f"DEBUG: Direct public URL: {clean_url}")
                            return clean_url
                    
                    print(f"WARNING: Unexpected or invalid URL format: {public_url}")
                    # Try to construct the URL manually
                    supabase_url = os.getenv('SUPABASE_URL')
                    if supabase_url:
                        manual_url = f"{supabase_url}/storage/v1/object/public/article-images/{article_id}.jpg"
                        print(f"DEBUG: Manual URL construction: {manual_url}")
                        return manual_url
                else:
                    print(f"DEBUG: No Supabase image found for article {article_id} - file not in bucket")
            except Exception as e:
                print(f"DEBUG: Error checking Supabase storage for article {article_id}: {e}")
        
        # Step 3: Check if image exists locally
        try:
            images_dir = ensure_images_directory()
            local_path = os.path.join(images_dir, f"{article_id}.jpg")
            if os.path.exists(local_path):
                # Serve local image via API endpoint
                local_url = f"/api/images/{article_id}.jpg"
                print(f"INFO: Using local image for article {article_id}: {local_url}")
                return local_url
            else:
                print(f"DEBUG: No local image found for article {article_id}")
        except Exception as e:
            print(f"DEBUG: Error checking local image for article {article_id}: {e}")
        
        # Step 4: Generate new image using Gemini API
        print(f"INFO: Generating new image for article {article_id}: {article_title}")
        image_data = generate_image_with_gemini(article_title, article_content)
        
        if image_data:
            # Step 5: Store both locally and in Supabase storage (if bucket exists)
            if ensure_supabase_bucket():
                image_url = upload_image_to_storage(article_id, image_data)
                if image_url:
                    print(f"SUCCESS: Generated and stored image for article {article_id}")
                    return image_url
            else:
                # Just store locally if Supabase bucket is not available
                local_path = store_image_locally(article_id, image_data)
                if local_path:
                    local_url = f"/api/images/{article_id}.jpg"
                    print(f"SUCCESS: Generated and stored image locally for article {article_id}")
                    return local_url
        
        # Fallback to placeholder if generation fails
        print(f"WARNING: Image generation failed for article {article_id}, using placeholder")
        return f"/api/placeholder/400/250"
        
    except Exception as e:
        print(f"ERROR: Error getting/generating image for article {article_id}: {e}")
        return f"/api/placeholder/400/250"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Football Focus API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """
    Get articles with optional filtering
    
    Query parameters:
    - category: Filter by category
    - limit: Number of articles to return (default: 10)
    - offset: Number of articles to skip for pagination (default: 0)
    - featured: Get only featured articles (true/false)
    - search: Search in title and content
    - fixture_id: Filter by specific fixture ID
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        featured = request.args.get('featured', '').lower() == 'true'
        search = request.args.get('search', '')
        
        # Build the query
        query = api.table('generated_articles').select(
            'id, title, content, article_type, word_count, file_path, created_at, '
            'fixture_id, processing_id, '
            'fixtures!inner(home_team, away_team, match_date, home_score, away_score, competition)'
        )
        
        # Apply filters
        if category and category != 'All':
            query = query.eq('article_type', category)
        
        if search:
            # Search in title and content (basic search)
            query = query.or_(f'title.ilike.%{search}%,content.ilike.%{search}%')
        
        # Filter by fixture_id if provided
        fixture_id = request.args.get('fixture_id')
        if fixture_id:
            query = query.eq('fixture_id', fixture_id)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Order by creation date (newest first)
        query = query.order('created_at', desc=True)
        
        # Execute query
        result = query.execute()
        
        # Transform the data for frontend
        articles = []
        for row in result.data:
            fixture = row.get('fixtures', {})
            
            # Get or generate image for the article
            article_image_url = get_or_generate_article_image(row['id'], row['title'], row['content'])
            
            # Create article object
            article = {
                'id': row['id'],
                'title': row['title'],
                'content': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],  # Excerpt
                'excerpt': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],
                'category': row['article_type'],
                'word_count': row['word_count'],
                'created_at': row['created_at'],
                'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
                'match_date': fixture.get('match_date', ''),
                'home_team': fixture.get('home_team', ''),
                'away_team': fixture.get('away_team', ''),
                'score': f"{fixture.get('home_score', 0)}-{fixture.get('away_score', 0)}" if fixture.get('home_score') is not None else '',
                'competition': fixture.get('competition', 'Premier League'),
                'tags': [
                    fixture.get('home_team', ''),
                    fixture.get('away_team', ''),
                    fixture.get('competition', 'Premier League')
                ],
                'author': 'Final Whistle AI',
                'readTime': f"{max(1, row['word_count'] // 200)} min read",
                'featured': False,  # We'll implement featured logic later
                'image': article_image_url
            }
            
            articles.append(article)
        
        return jsonify({
            'success': True,
            'data': articles,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(articles)  # We'll implement total count later
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving articles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article by ID"""
    try:
        result = api.table('generated_articles').select(
            'id, title, content, article_type, word_count, file_path, created_at, '
            'fixture_id, processing_id, '
            'fixtures!inner(home_team, away_team, match_date, match_time, home_score, away_score, competition, venue)'
        ).eq('id', article_id).execute()
        
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'Article not found'
            }), 404
        
        row = result.data[0]
        fixture = row.get('fixtures', {})
        
        # Get or generate image for the article
        article_image_url = get_or_generate_article_image(row['id'], row['title'], row['content'])
        
        article = {
            'id': row['id'],
            'title': row['title'],
            'content': row['content'],
            'category': row['article_type'],
            'word_count': row['word_count'],
            'created_at': row['created_at'],
            'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
            'match_date': fixture.get('match_date', ''),
            'match_time': fixture.get('match_time', ''),
            'home_team': fixture.get('home_team', ''),
            'away_team': fixture.get('away_team', ''),
            'home_score': fixture.get('home_score', 0),
            'away_score': fixture.get('away_score', 0),
            'competition': fixture.get('competition', 'Premier League'),
            'venue': fixture.get('venue', ''),
            'tags': [
                fixture.get('home_team', ''),
                fixture.get('away_team', ''),
                fixture.get('competition', 'Premier League')
            ],
            'author': 'Final Whistle AI',
            'readTime': f"{max(1, row['word_count'] // 200)} min read",
            'image': article_image_url
        }
        
        return jsonify({
            'success': True,
            'data': article
        })
        
    except Exception as e:
        logger.error(f"Error retrieving article {article_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available article categories with counts"""
    try:
        # Get article type counts
        result = api.rpc('get_article_categories_with_counts').execute()
        
        if not result.data:
            # Fallback: get distinct categories manually
            result = api.table('generated_articles').select('article_type').execute()
            categories_data = {}
            for row in result.data:
                category = row['article_type']
                categories_data[category] = categories_data.get(category, 0) + 1
        else:
            categories_data = {row['article_type']: row['count'] for row in result.data}
        
        # Map to frontend format with colors
        color_map = {
            'match_report': 'bg-green-500',
            'player_focus': 'bg-blue-500', 
            'tactical_analysis': 'bg-purple-500',
            'transfer_news': 'bg-orange-500',
            'weekly_roundup': 'bg-red-500'
        }
        
        categories = []
        for category, count in categories_data.items():
            # Convert category name to display format
            display_name = category.replace('_', ' ').title()
            if display_name == 'Match Report':
                display_name = 'Match Reports'
            elif display_name == 'Player Focus':
                display_name = 'Player Focus'
            elif display_name == 'Tactical Analysis':
                display_name = 'Tactical Analysis'
            elif display_name == 'Transfer News':
                display_name = 'Transfer News'
            elif display_name == 'Weekly Roundup':
                display_name = 'Weekly Roundup'
            
            categories.append({
                'name': display_name,
                'value': category,
                'count': count,
                'color': color_map.get(category, 'bg-gray-500')
            })
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trending', methods=['GET'])
def get_trending():
    """Get trending topics based on recent articles"""
    try:
        # Get recent articles from last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        result = api.table('generated_articles').select(
            'title, fixtures!inner(home_team, away_team)'
        ).gte('created_at', week_ago).limit(10).execute()
        
        trending_topics = []
        teams_mentioned = {}
        
        for row in result.data:
            fixture = row.get('fixtures', {})
            home_team = fixture.get('home_team', '')
            away_team = fixture.get('away_team', '')
            
            # Count team mentions
            if home_team:
                teams_mentioned[home_team] = teams_mentioned.get(home_team, 0) + 1
            if away_team:
                teams_mentioned[away_team] = teams_mentioned.get(away_team, 0) + 1
        
        # Get top trending teams/topics
        sorted_teams = sorted(teams_mentioned.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for team, count in sorted_teams:
            trending_topics.append(f"{team} Match Analysis")
        
        # Add some generic trending topics if not enough
        if len(trending_topics) < 5:
            generic_topics = [
                "Premier League Title Race",
                "Transfer Window Updates", 
                "VAR Controversy Analysis",
                "Player Performance Reviews",
                "Tactical Innovations"
            ]
            trending_topics.extend(generic_topics[:5-len(trending_topics)])
        
        return jsonify({
            'success': True,
            'data': trending_topics[:5]
        })
        
    except Exception as e:
        logger.error(f"Error retrieving trending topics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/featured', methods=['GET'])
def get_featured_article():
    """Get the most recent featured article"""
    try:
        # For now, get the most recent article as featured
        # Later we can add a featured flag to the database
        result = api.table('generated_articles').select(
            'id, title, content, article_type, word_count, created_at, '
            'fixtures!inner(home_team, away_team, match_date, home_score, away_score, competition)'
        ).order('created_at', desc=True).limit(1).execute()
        
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'No featured article found'
            }), 404
        
        row = result.data[0]
        fixture = row.get('fixtures', {})
        
        # Get or generate image for the article
        article_image_url = get_or_generate_article_image(row['id'], row['title'], row['content'])
        
        article = {
            'id': row['id'],
            'title': row['title'],
            'content': row['content'][:300] + '...' if len(row['content']) > 300 else row['content'],
            'excerpt': row['content'][:300] + '...' if len(row['content']) > 300 else row['content'],
            'category': row['article_type'],
            'word_count': row['word_count'],
            'created_at': row['created_at'],
            'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
            'match_date': fixture.get('match_date', ''),
            'home_team': fixture.get('home_team', ''),
            'away_team': fixture.get('away_team', ''),
            'score': f"{fixture.get('home_score', 0)}-{fixture.get('away_score', 0)}" if fixture.get('home_score') is not None else '',
            'competition': fixture.get('competition', 'Premier League'),
            'tags': [
                fixture.get('home_team', ''),
                fixture.get('away_team', ''),
                fixture.get('competition', 'Premier League')
            ],
            'author': 'Final Whistle AI',
            'readTime': f"{max(1, row['word_count'] // 200)} min read",
            'featured': True,
            'image': article_image_url
        }
        
        return jsonify({
            'success': True,
            'data': article
        })
        
    except Exception as e:
        logger.error(f"Error retrieving featured article: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gameweek/latest', methods=['GET'])
def get_latest_gameweek_match_reports():
    """Get match reports for the latest completed gameweek"""
    try:
        # Get the latest completed gameweek with match reports
        # First, find the most recent fixture with articles
        latest_fixture = api.table('fixtures').select(
            'matchday, match_date, generated_articles!inner(fixture_id)'
        ).order('match_date', desc=True).limit(1).execute()
        print(latest_fixture.data)
        if not latest_fixture.data:
            # Fallback: get the highest matchday with completed fixtures
            result = api.table('fixtures').select(
                'matchday'
            ).not_.is_('home_score', 'null').order('matchday', desc=True).limit(1).execute()
            
            if not result.data:
                return jsonify({
                    'success': False,
                    'error': 'No completed gameweeks found'
                }), 404
            
            latest_matchday = result.data[0]['matchday']
        else:
            latest_matchday = latest_fixture.data[0]['matchday']
        
        # Get all match reports for this gameweek
        gameweek_articles = api.table('generated_articles').select(
            'id, title, content, article_type, word_count, created_at, '
            'fixtures!inner(id, home_team, away_team, match_date, match_time, home_score, away_score, competition, venue, matchday)'
        ).eq('fixtures.matchday', latest_matchday).eq('article_type', 'match_report').order('match_date', desc=False, foreign_table='fixtures').execute()
        
        # Transform data for frontend
        match_reports = []
        seen_fixtures = set()
        for row in gameweek_articles.data:
            fixture = row.get('fixtures', {})
            fixture_id = fixture.get('id')
            
            # Skip if we've already seen this fixture
            if fixture_id in seen_fixtures:
                continue
            seen_fixtures.add(fixture_id)
            
            home_score_raw = fixture.get('home_score')
            away_score_raw = fixture.get('away_score')
            home_score_safe = 0 if home_score_raw is None else home_score_raw
            away_score_safe = 0 if away_score_raw is None else away_score_raw
            score_display_value = f"{home_score_raw}-{away_score_raw}" if (home_score_raw is not None and away_score_raw is not None) else ''
            if home_score_raw is not None and away_score_raw is not None:
                result_value = 'W' if home_score_raw > away_score_raw else 'L' if home_score_raw < away_score_raw else 'D'
            else:
                result_value = ''
            
            # Get or generate image for the article
            article_image_url = get_or_generate_article_image(row['id'], row['title'], row['content'])
            match_report = {
                'id': row['id'],
                'title': row['title'],
                'excerpt': row['content'][:250] + '...' if len(row['content']) > 250 else row['content'],
                'category': 'Match Reports',
                'word_count': row['word_count'],
                'created_at': row['created_at'],
                'fixture_id': fixture.get('id'),
                'home_team': fixture.get('home_team', ''),
                'away_team': fixture.get('away_team', ''),
                'home_score': home_score_safe,
                'away_score': away_score_safe,
                'match_date': fixture.get('match_date', ''),
                'match_time': fixture.get('match_time', ''),
                'competition': fixture.get('competition', 'Premier League'),
                'venue': fixture.get('venue', ''),
                'matchday': fixture.get('matchday', 0),
                'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
                'score_display': score_display_value,
                'result': result_value,
                'tags': [
                    fixture.get('home_team', ''),
                    fixture.get('away_team', ''),
                    f"Matchday {fixture.get('matchday', 0)}",
                    fixture.get('competition', 'Premier League')
                ],
                'author': 'Final Whistle AI',
                'readTime': f"{max(1, row['word_count'] // 200)} min read",
                'image': article_image_url
            }
            
            match_reports.append(match_report)
        
        # Get gameweek summary
        total_matches = len(match_reports)
        total_goals = sum(report['home_score'] + report['away_score'] for report in match_reports)
        avg_goals_per_match = round(total_goals / total_matches, 1) if total_matches > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'matchday': latest_matchday,
                'match_reports': match_reports,
                'summary': {
                    'total_matches': total_matches,
                    'total_goals': total_goals,
                    'avg_goals_per_match': avg_goals_per_match,
                    'gameweek_complete': total_matches >= 10  # Premier League typically has 10 matches per gameweek
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving latest gameweek match reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gameweek/<int:matchday>', methods=['GET'])
def get_gameweek_match_reports(matchday):
    """Get match reports for a specific gameweek"""
    try:
        # Get all match reports for the specified gameweek
        gameweek_articles = api.table('generated_articles').select(
            'id, title, content, article_type, word_count, created_at, '
            'fixtures!inner(id, home_team, away_team, match_date, match_time, home_score, away_score, competition, venue, matchday)'
        ).eq('fixtures.matchday', matchday).eq('article_type', 'match_report').order('match_date', desc=False, foreign_table='fixtures').execute()
        
        if not gameweek_articles.data:
            return jsonify({
                'success': False,
                'error': f'No match reports found for matchday {matchday}'
            }), 404
        
        # Transform data for frontend
        match_reports = []
        seen_fixtures = set()
        for row in gameweek_articles.data:
            fixture = row.get('fixtures', {})
            fixture_id = fixture.get('id')
            
            # Skip if we've already seen this fixture
            if fixture_id in seen_fixtures:
                continue
            seen_fixtures.add(fixture_id)
            
            home_score_raw = fixture.get('home_score')
            away_score_raw = fixture.get('away_score')
            home_score_safe = 0 if home_score_raw is None else home_score_raw
            away_score_safe = 0 if away_score_raw is None else away_score_raw
            score_display_value = f"{home_score_raw}-{away_score_raw}" if (home_score_raw is not None and away_score_raw is not None) else ''
            if home_score_raw is not None and away_score_raw is not None:
                result_value = 'W' if home_score_raw > away_score_raw else 'L' if home_score_raw < away_score_raw else 'D'
            else:
                result_value = ''
            
            # Get or generate image for the article
            article_image_url = get_or_generate_article_image(row['id'], row['title'], row['content'])
            
            match_report = {
                'id': row['id'],
                'title': row['title'],
                'excerpt': row['content'][:250] + '...' if len(row['content']) > 250 else row['content'],
                'category': 'Match Reports',
                'word_count': row['word_count'],
                'created_at': row['created_at'],
                'fixture_id': fixture.get('id'),
                'home_team': fixture.get('home_team', ''),
                'away_team': fixture.get('away_team', ''),
                'home_score': home_score_safe,
                'away_score': away_score_safe,
                'match_date': fixture.get('match_date', ''),
                'match_time': fixture.get('match_time', ''),
                'competition': fixture.get('competition', 'Premier League'),
                'venue': fixture.get('venue', ''),
                'matchday': fixture.get('matchday', 0),
                'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
                'score_display': score_display_value,
                'result': result_value,
                'tags': [
                    fixture.get('home_team', ''),
                    fixture.get('away_team', ''),
                    f"Matchday {fixture.get('matchday', 0)}",
                    fixture.get('competition', 'Premier League')
                ],
                'author': 'Final Whistle AI',
                'readTime': f"{max(1, row['word_count'] // 200)} min read",
                'image': article_image_url
            }
            
            match_reports.append(match_report)
        
        # Get gameweek summary
        total_matches = len(match_reports)
        total_goals = sum(report['home_score'] + report['away_score'] for report in match_reports)
        avg_goals_per_match = round(total_goals / total_matches, 1) if total_matches > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'matchday': matchday,
                'match_reports': match_reports,
                'summary': {
                    'total_matches': total_matches,
                    'total_goals': total_goals,
                    'avg_goals_per_match': avg_goals_per_match,
                    'gameweek_complete': total_matches >= 10
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving gameweek {matchday} match reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gameweek/strip', methods=['GET'])
def get_gameweek_strip():
    """Get one match report per fixture for latest gameweek - optimized for horizontal strip display"""
    try:
        # Get the latest completed gameweek with match reports
        latest_fixture = api.table('fixtures').select(
            'matchday, match_date, generated_articles!inner(fixture_id)'
        ).order('match_date', desc=True).limit(1).execute()
        
        if not latest_fixture.data:
            # Fallback: get the highest matchday with completed fixtures
            result = api.table('fixtures').select(
                'matchday'
            ).not_.is_('home_score', 'null').order('matchday', desc=True).limit(1).execute()
            
            if not result.data:
                return jsonify({
                    'success': False,
                    'error': 'No completed gameweeks found'
                }), 404
            
            latest_matchday = result.data[0]['matchday']
        else:
            latest_matchday = latest_fixture.data[0]['matchday']
        
        # Get one match report per fixture for this gameweek (distinct fixture_id)
        gameweek_articles = api.table('generated_articles').select(
            'id, title, fixture_id, '
            'fixtures!inner(id, home_team, away_team, home_score, away_score, match_date)'
        ).eq('fixtures.matchday', latest_matchday).eq('article_type', 'match_report').order('match_date', desc=False, foreign_table='fixtures').execute()
        
        # Create unique fixtures list (one article per fixture)
        strip_cards = []
        seen_fixtures = set()
        
        for row in gameweek_articles.data:
            fixture = row.get('fixtures', {})
            fixture_id = fixture.get('id')
            
            # Skip if we've already processed this fixture
            if fixture_id in seen_fixtures:
                continue
            seen_fixtures.add(fixture_id)
            
            home_score = fixture.get('home_score', 0)
            away_score = fixture.get('away_score', 0)
            home_team = fixture.get('home_team', '')
            away_team = fixture.get('away_team', '')
            
            # Get or generate image for the article
            article_image_url = get_or_generate_article_image(row['id'], row['title'], row['content'] if 'content' in row else '')
            
            strip_card = {
                'id': row['id'],
                'title': row['title'],
                'fixture_id': fixture_id,
                'fixture_label': f"{home_team} vs {away_team}",
                'home_team': home_team,
                'away_team': away_team,
                'score': f"{home_score}-{away_score}" if home_score is not None and away_score is not None else '',
                'image': article_image_url,
                'match_date': fixture.get('match_date', '')
            }
            
            strip_cards.append(strip_card)
        
        return jsonify({
            'success': True,
            'data': {
                'matchday': latest_matchday,
                'total_matches': len(strip_cards),
                'strip_cards': strip_cards
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving gameweek strip data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/images/<filename>', methods=['GET'])
def serve_local_image(filename):
    """Serve local images from the images directory"""
    try:
        images_dir = ensure_images_directory()
        image_path = os.path.join(images_dir, filename)
        
        if os.path.exists(image_path):
            from flask import send_file
            return send_file(image_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bucket/status', methods=['GET'])
def check_bucket_status():
    """Check the status of the Supabase storage bucket"""
    try:
        bucket_name = 'article-images'
        
        # Test different operations to diagnose the issue
        test_results = {
            'bucket_name': bucket_name,
            'supabase_url': os.getenv('SUPABASE_URL'),
            'api_key_exists': bool(os.getenv('SUPABASE_KEY')),
            'tests': {}
        }
        
        # Test 1: Try to list all buckets
        try:
            buckets = api.storage.list_buckets()
            test_results['tests']['list_buckets'] = {
                'success': True,
                'buckets': [bucket.name for bucket in buckets] if buckets else []
            }
        except Exception as e:
            test_results['tests']['list_buckets'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test 2: Try to access the specific bucket
        try:
            files = api.storage.from_(bucket_name).list()
            test_results['tests']['access_bucket'] = {
                'success': True,
                'file_count': len(files),
                'files': [f['name'] for f in files[:5]]  # Show first 5 files
            }
        except Exception as e:
            test_results['tests']['access_bucket'] = {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
        
        # Test 3: Try to get public URL for a test file
        try:
            test_file = f"{bucket_name}/test.jpg"
            public_url = api.storage.from_(bucket_name).get_public_url("test.jpg")
            test_results['tests']['get_public_url'] = {
                'success': True,
                'url': str(public_url)
            }
        except Exception as e:
            test_results['tests']['get_public_url'] = {
                'success': False,
                'error': str(e)
            }
        
        # Overall status
        bucket_accessible = test_results['tests']['access_bucket']['success']
        
        return jsonify({
            'success': True,
            'bucket_accessible': bucket_accessible,
            'test_results': test_results,
            'message': 'Bucket is accessible' if bucket_accessible else 'Bucket access failed - check error details'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/test/image/<article_id>', methods=['GET'])
def test_image_access(article_id):
    """Test if we can access an image directly"""
    try:
        import requests
        
        # Try the cleaned URL
        cleaned_url = get_or_generate_article_image(article_id, "Test", "Test article content for image generation")
        
        # Test if the URL is accessible
        try:
            response = requests.head(cleaned_url, timeout=10)
            accessible = response.status_code == 200
        except:
            accessible = False
        
        return jsonify({
            'success': True,
            'article_id': article_id,
            'image_url': cleaned_url,
            'accessible': accessible,
            'status_code': response.status_code if accessible else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test/supabase-url/<article_id>', methods=['GET'])
def test_supabase_url_directly(article_id):
    """Test Supabase URL generation directly"""
    try:
        bucket_name = 'article-images'
        
        # Try to get the public URL directly
        try:
            public_url = api.storage.from_(bucket_name).get_public_url(f"{article_id}.jpg")
            url_str = str(public_url)
            cleaned_url = clean_supabase_url(public_url)
            
            # Test if the URL is accessible
            import requests
            test_results = {}
            
            # Test both raw and cleaned URLs
            for url_type, url in [("raw", url_str), ("cleaned", cleaned_url)]:
                try:
                    response = requests.head(url, timeout=10)
                    test_results[url_type] = {
                        'url': url,
                        'accessible': response.status_code == 200,
                        'status_code': response.status_code,
                        'headers': dict(response.headers)
                    }
                except Exception as req_error:
                    test_results[url_type] = {
                        'url': url,
                        'accessible': False,
                        'status_code': None,
                        'error': str(req_error)
                    }
            
            # Check if file exists in bucket
            try:
                files = api.storage.from_(bucket_name).list()
                file_exists = any(f['name'] == f"{article_id}.jpg" for f in files)
                file_info = next((f for f in files if f['name'] == f"{article_id}.jpg"), None)
            except Exception as e:
                file_exists = False
                file_info = None
            
            return jsonify({
                'success': True,
                'article_id': article_id,
                'bucket_name': bucket_name,
                'file_exists_in_bucket': file_exists,
                'file_info': file_info,
                'test_results': test_results,
                'recommendations': [
                    "If URLs return 404: Check bucket is set to PUBLIC in Supabase dashboard",
                    "If URLs return 403: Check bucket permissions and CORS settings",
                    "If file doesn't exist: The image needs to be uploaded to Supabase first"
                ]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'article_id': article_id,
                'bucket_name': bucket_name,
                'error': str(e),
                'error_type': type(e).__name__
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug/image/<article_id>', methods=['GET'])
def debug_image_url(article_id):
    """Debug endpoint to check image URL for an article"""
    try:
        # Check if image exists in Supabase storage
        files_response = api.storage.from_('article-images').list()
        file_exists = any(file['name'] == f"{article_id}.jpg" for file in files_response)
        
        debug_info = {
            'article_id': article_id,
            'file_exists_in_bucket': file_exists,
            'bucket_files': [f['name'] for f in files_response if f['name'].endswith('.jpg')][:10],  # Show first 10 jpg files
        }
        
        if file_exists:
            public_url = api.storage.from_('article-images').get_public_url(f"{article_id}.jpg")
            debug_info['raw_supabase_url'] = str(public_url)
            debug_info['url_type'] = type(public_url).__name__
            
            # Clean the URL
            cleaned_url = clean_supabase_url(public_url)
            debug_info['cleaned_url'] = cleaned_url
            
            # Try to construct manual URL
            supabase_url = os.getenv('SUPABASE_URL')
            if supabase_url:
                manual_url = f"{supabase_url}/storage/v1/object/public/article-images/{article_id}.jpg"
                debug_info['manual_url'] = manual_url
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get general statistics about the blog"""
    try:
        # Get total articles count
        articles_result = api.table('generated_articles').select('id', count='exact').execute()
        total_articles = articles_result.count or 0
        
        # Get total fixtures processed
        fixtures_result = api.table('fixture_processing_status').select('id', count='exact').eq('processing_status', 'completed').execute()
        total_fixtures = fixtures_result.count or 0
        
        # Get articles from last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_articles = api.table('generated_articles').select('id', count='exact').gte('created_at', week_ago).execute()
        recent_count = recent_articles.count or 0
        
        # Get latest gameweek number
        latest_gameweek_result = api.table('fixtures').select('matchday').not_.is_('home_score', 'null').order('matchday', desc=True).limit(1).execute()
        latest_gameweek = latest_gameweek_result.data[0]['matchday'] if latest_gameweek_result.data else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_articles': total_articles,
                'total_fixtures_processed': total_fixtures,
                'articles_this_week': recent_count,
                'latest_gameweek': latest_gameweek,
                'last_updated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Check database connection on startup
    try:
        test_result = api.table('generated_articles').select('id').limit(1).execute()
        logger.info("✅ Database connection test successful")
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        exit(1)
    
    # Start the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Football Focus API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
