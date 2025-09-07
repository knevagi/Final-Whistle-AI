#!/usr/bin/env python3
"""
Launcher Script for European Football Blog Crew AI
Simple interface to run the system with different options for European football content
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

def save_article_to_file(article_content, topic, article_type, output_dir="generated_articles"):
    """Save the generated article to a file with proper formatting."""
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate filename with timestamp and sanitized topic
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sanitize the topic for filename - remove invalid characters
    safe_topic = topic
    # Remove or replace invalid filename characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '**', '...']
    for char in invalid_chars:
        safe_topic = safe_topic.replace(char, '')
    
    # Remove extra spaces and replace with underscores
    safe_topic = " ".join(safe_topic.split())  # Normalize spaces
    safe_topic = safe_topic.replace(' ', '_')
    
    # Remove any remaining special characters that might cause issues
    safe_topic = "".join(c for c in safe_topic if c.isalnum() or c in ('_', '-'))
    
    # Ensure the filename isn't too long (Windows has a 255 character limit)
    if len(safe_topic) > 100:
        safe_topic = safe_topic[:100]
    
    # Create a clean filename
    filename = f"{timestamp}_{safe_topic}_{article_type}.md"
    
    file_path = output_path / filename
    
    # Format the article content with metadata
    formatted_content = f"""# {topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Type:** {article_type}
**AI System:** European Football Blog Crew AI

---

{article_content}

---

*This article was automatically generated using AI agents specialized in European football content creation.*
"""
    
    # Save to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    return file_path

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="European Football Blog Crew AI Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_crew.py                                    # Run basic workflow
  python run_crew.py --test                            # Run system tests
  python run_crew.py --examples                        # Run usage examples
  python run_crew.py --topic "El Clásico Analysis" --type tactical_analysis
  python run_crew.py --topic "Haaland Transfer News" --type transfer_news
  python run_crew.py --config                          # Show configuration
        """
    )
    
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run system tests to verify installation"
    )
    
    parser.add_argument(
        "--examples", 
        action="store_true", 
        help="Run usage examples and demonstrations"
    )
    
    parser.add_argument(
        "--topic", 
        type=str, 
        help="Topic for European football article creation"
    )
    
    parser.add_argument(
        "--type", 
        type=str, 
        choices=["match_report", "player_analysis", "transfer_news", "tactical_analysis", "league_roundup"],
        default="match_report",
        help="Type of European football article to create"
    )
    
    parser.add_argument(
        "--length", 
        type=str, 
        default="800-1200 words",
        help="Target length for the football article"
    )
    
    parser.add_argument(
        "--config", 
        action="store_true", 
        help="Show current configuration"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="generated_articles",
        help="Directory to save generated articles (default: generated_articles)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save article to file (just display in terminal)"
    )
    
    parser.add_argument(
        "--from-results",
        action="store_true",
        help="Generate articles from recent football results (requires --competition and --days-back)"
    )
    
    parser.add_argument(
        "--competition",
        type=str,
        help="Competition name for --from-results (e.g., 'Premier League', 'La Liga')"
    )
    
    parser.add_argument(
        "--days-back",
        type=int,
        default=7,
        help="Number of days to look back for --from-results (default: 7)"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("crew_workflow.py").exists():
        print("❌ Error: Please run this script from the crew_ai directory")
        print("Current directory:", Path.cwd())
        print("Expected files not found. Please navigate to the crew_ai directory.")
        return 1
    
    # Check for API key AFTER loading .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're in the crew_ai directory")
        print("2. Check that .env file exists (not .env.txt)")
        print("3. Verify the .env file format: OPENAI_API_KEY=sk-your_key_here")
        print("4. Try restarting your terminal")
        return 1
    
    try:
        if args.test:
            print("🧪 Running system tests...")
            from test_system import run_all_tests
            success = run_all_tests()
            return 0 if success else 1
            
        elif args.examples:
            print("📚 Running European football usage examples...")
            from example_usage import main as run_examples
            run_examples()
            return 0
            
        elif args.config:
            print("⚙️ Current European Football Configuration:")
            print("=" * 40)
            from crew_config import get_config
            
            configs = ["llm", "agents", "workflow", "content_types", "seo", "qa"]
            for config_type in configs:
                config = get_config(config_type)
                print(f"\n{config_type.upper()}:")
                for key, value in list(config.items())[:3]:  # Show first 3 items
                    print(f"  {key}: {value}")
                if len(config) > 3:
                    print(f"  ... and {len(config) - 3} more settings")
            return 0
            
        elif args.topic:
            print(f"⚽ Creating European football article: {args.topic}")
            print(f"Type: {args.type}")
            print(f"Length: {args.length}")
            print("=" * 60)
            
            from crew_workflow import AutonomousSportsBlogCrew
            
            crew = AutonomousSportsBlogCrew()
            if args.verbose:
                crew.crew.verbose = True
            
            result = crew.create_article(
                topic=args.topic,
                article_type=args.type,
                target_length=args.length
            )
            
            print(f"\n✅ European football article completed!")
            print(f"Status: {result['workflow_status']}")
            print(f"Agents used: {', '.join(result['agents_used'])}")
            
            # Save article to file if requested
            if not args.no_save and 'article_content' in result:
                try:
                    file_path = save_article_to_file(
                        result['article_content'], 
                        args.topic, 
                        args.type, 
                        args.output_dir
                    )
                    print(f"\n💾 Article saved to: {file_path}")
                    print(f"📁 Output directory: {Path(args.output_dir).absolute()}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not save article to file: {e}")
                    print("Article content displayed above")
            elif 'article_content' in result and result['article_content']:
                print(f"\n📄 Article content:")
                print("=" * 60)
                print(result['article_content'])
            elif 'article_content' in result and not result['article_content']:
                print(f"\n⚠️ Warning: Article content is empty!")
                print("This might indicate an issue with the Crew AI workflow.")
                if 'raw_result' in result:
                    print(f"\n🔍 Raw workflow result:")
                    print("=" * 60)
                    print(result['raw_result'])
                print(f"\n💡 Try running with --verbose flag for more details")
            else:
                print(f"\n📋 Workflow result: {result}")
                if args.verbose:
                    print(f"\n🔍 Full result details:")
                    for key, value in result.items():
                        print(f"  {key}: {type(value).__name__} = {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            
            return 0
            
        elif args.from_results:
            print(f"🔍 Fetching recent {args.competition} results and generating articles...")
            print(f"Looking back {args.days_back} days")
            print(f"Target length: {args.length}")
            print("=" * 60)
            
            from crew_workflow import AutonomousSportsBlogCrew
            
            crew = AutonomousSportsBlogCrew()
            if args.verbose:
                crew.crew.verbose = True
            
            result = crew.create_multiple_articles_from_results(
                competition=args.competition,
                days_back=args.days_back,
                target_length=args.length
            )
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                if 'raw_result' in result:
                    print(f"\n🔍 Raw result: {result['raw_result']}")
                return 1
            
            print(f"\n✅ Multiple articles workflow completed!")
            print(f"Competition: {result['competition']}")
            print(f"Topics generated: {result['topics_generated']}")
            print(f"Articles created: {result['articles_created']}")
            print(f"Agents used: {', '.join(result['agents_used'])}")
            
            # Save all articles to files
            if not args.no_save:
                saved_articles = []
                for article_data in result['articles']:
                    if 'article_result' in article_data and 'article_content' in article_data['article_result']:
                        try:
                            topic_info = article_data['topic_info']
                            article_content = article_data['article_result']['article_content']
                            
                            file_path = save_article_to_file(
                                article_content,
                                topic_info['title'],
                                topic_info.get('article_type', 'match_report'),
                                args.output_dir
                            )
                            saved_articles.append(file_path)
                            print(f"💾 Article {article_data['topic_number']} saved to: {file_path}")
                            
                        except Exception as e:
                            print(f"⚠️ Warning: Could not save article {article_data['topic_number']}: {e}")
                    else:
                        print(f"⚠️ Article {article_data['topic_number']} had no content to save")
                
                if saved_articles:
                    print(f"\n📁 All articles saved to: {Path(args.output_dir).absolute()}")
                    print(f"📊 Summary: {len(saved_articles)}/{result['articles_created']} articles saved successfully")
            
            # Display topics and article summaries
            print(f"\n📋 Generated Topics:")
            for i, topic in enumerate(result['topics'], 1):
                print(f"\n{i}. {topic.get('title', 'Untitled')}")
                if 'description' in topic:
                    print(f"   Description: {topic['description']}")
                if 'article_type' in topic:
                    print(f"   Type: {topic['article_type']}")
            
            return 0
            
        else:
            # Default: run basic workflow
            print("⚽ European Football Blog Crew AI")
            print("=" * 50)
            print("Running basic European football workflow...")
            print()
            
            from crew_workflow import main as run_workflow
            run_workflow()
            return 0
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
