#!/usr/bin/env python3
"""
Example Usage Script for European Football Blog Crew AI
Demonstrates various ways to use the workflow system for European football content
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crew_workflow import AutonomousSportsBlogCrew
from crew_config import get_config, update_config

def example_basic_workflow():
    """Basic example of creating a European football article."""
    print("📝 Example 1: Basic European Football Article Creation")
    print("=" * 60)
    
    crew = AutonomousSportsBlogCrew()
    
    result = crew.create_article(
        topic="Manchester City's Tactical Masterclass Against Arsenal",
        article_type="match_report",
        target_length="1000-1200 words"
    )
    
    print(f"✅ Article created successfully!")
    print(f"Topic: {result['topic']}")
    print(f"Type: {result['article_type']}")
    print(f"Status: {result['workflow_status']}")
    print(f"Agents used: {', '.join(result['agents_used'])}")
    print()

def example_batch_articles():
    """Example of creating multiple European football articles in sequence."""
    print("📚 Example 2: Batch European Football Article Creation")
    print("=" * 60)
    
    crew = AutonomousSportsBlogCrew()
    
    topics = [
        "Haaland's Record-Breaking Season: A Statistical Analysis",
        "Real Madrid vs Barcelona: El Clásico Tactical Breakdown",
        "Premier League Title Race: The Final Sprint Analysis"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"Creating article {i}/{len(topics)}: {topic}")
        
        result = crew.create_article(
            topic=topic,
            article_type="player_analysis" if i == 1 else "tactical_analysis",
            target_length="800-1000 words"
        )
        
        print(f"✅ Article {i} completed: {result['workflow_status']}")
        print()
    
    print("🎉 All European football articles completed successfully!")

def example_custom_configuration():
    """Example of using custom configuration for European football content."""
    print("⚙️ Example 3: Custom Configuration for European Football")
    print("=" * 60)
    
    # Get current configuration
    llm_config = get_config("llm")
    print(f"Current LLM model: {llm_config['default_model']}")
    
    # Update configuration
    update_config("llm", {"temperature": 0.5, "max_tokens": 6000})
    print("Updated LLM configuration for more focused European football output")
    
    # Create crew with custom settings
    crew = AutonomousSportsBlogCrew(model_name="gpt-4o-mini")
    
    result = crew.create_article(
        topic="Bundesliga Title Race: Leverkusen's Historic Season",
        article_type="league_roundup",
        target_length="1500-2000 words"
    )
    
    print(f"✅ Bundesliga analysis completed with custom settings!")
    print()

def example_specialized_agents():
    """Example of adding specialized agents for European football coverage."""
    print("🚀 Example 4: Adding Specialized European Football Agents")
    print("=" * 60)
    
    crew = AutonomousSportsBlogCrew()
    
    # Display initial crew info
    crew_info = crew.get_crew_info()
    print(f"Initial crew size: {crew_info['total_agents']}")
    print(f"Current agents: {', '.join(crew_info['agent_roles'])}")
    
    # Example of how you could add a specialized agent
    print("\n💡 To add specialized European football agents, you would:")
    print("1. Create a new agent class (e.g., Transfer Market Specialist, Tactical Analyst)")
    print("2. Use crew.add_specialized_agent() method")
    print("3. Integrate into the workflow")
    
    print("\nExample specialized agents for European football:")
    print("- Transfer Market Specialist")
    print("- Tactical Analysis Expert")
    print("- Player Performance Analyst")
    print("- Match Statistics Expert")
    print("- European Competition Specialist")
    print()

def example_error_handling():
    """Example of error handling and fallback strategies for football content."""
    print("🛡️ Example 5: Error Handling and Fallbacks for European Football")
    print("=" * 60)
    
    try:
        # Try to create an article
        crew = AutonomousSportsBlogCrew()
        
        result = crew.create_article(
            topic="Champions League Quarter-Final: Tactical Preview",
            article_type="tactical_analysis",
            target_length="800-1000 words"
        )
        
        print("✅ Champions League article created successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print("\n🔄 Implementing fallback strategies:")
        print("1. Retry with different LLM model")
        print("2. Simplify article requirements")
        print("3. Use cached content if available")
        print("4. Alert human editor for manual intervention")
        print()

def example_european_football_topics():
    """Example of various European football content types."""
    print("⚽ Example 6: European Football Content Types")
    print("=" * 60)
    
    content_types = get_config("content_types")
    
    print("Available content types for European football:")
    for content_type, config in content_types.items():
        print(f"\n{content_type.replace('_', ' ').title()}:")
        print(f"  Structure: {', '.join(config['structure'])}")
        print(f"  Tone: {config['tone']}")
        print(f"  Length: {config['target_length']}")
    
    print("\n💡 Content ideas for each type:")
    print("Match Report: Recent Premier League, La Liga, or Champions League matches")
    print("Player Analysis: Star players, emerging talents, or players in form")
    print("Transfer News: Latest transfer rumors, completed deals, or transfer analysis")
    print("Tactical Analysis: Formation changes, tactical innovations, or match strategies")
    print("League Roundup: Weekend results, title races, or relegation battles")
    print()

def main():
    """Run all European football examples."""
    print("⚽ European Football Blog Crew AI - Examples")
    print("=" * 70)
    print()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        print("\nExample .env file content:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    try:
        # Run examples
        example_basic_workflow()
        example_batch_articles()
        example_custom_configuration()
        example_specialized_agents()
        example_error_handling()
        example_european_football_topics()
        
        print("🎉 All European football examples completed successfully!")
        print("\n💡 Next steps:")
        print("1. Customize the configuration in crew_config.py")
        print("2. Add your own specialized European football agents")
        print("3. Integrate with your football blog publishing system")
        print("4. Monitor and optimize agent performance for football content")
        print("\n⚽ Ready to create amazing European football content!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please check your configuration and API key")

if __name__ == "__main__":
    main()
