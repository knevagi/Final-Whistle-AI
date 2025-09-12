#!/usr/bin/env python3
"""
CLI script to run the English Football Fixture Service
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixture_service import FixtureService
from config import FixtureServiceConfig



async def run_processing_only():
    """Run only the fixture processing"""
    print(f"📝 Running fixture processing for all completed fixtures...")
    service = FixtureService()
    await service.run_fixture_processing()
    print("✅ Fixture processing completed")

async def run_full_service(processing_interval: int = None):
    """Run the full service with custom interval"""
    print(f"🚀 Starting fixture processing service for all completed fixtures...")
    
    # Use config defaults if not provided
    processing_interval = processing_interval or FixtureServiceConfig.PROCESSING_INTERVAL
    
    service = FixtureService()
    await service.run_service(processing_interval)

async def test_connection():
    """Test database and API connections"""
    print("🔍 Testing connections...")
    
    try:
        service = FixtureService()
        
        # Test Supabase connection
        print("  Testing Supabase connection...")
        service.test_connection()
        print("  ✅ Supabase connection successful")
        
        # Test crew AI initialization
        print("  Testing crew AI initialization...")
        crew = service.crew
        print("  ✅ Crew AI initialized successfully")
        
        print("✅ All connection tests passed!")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        sys.exit(1)

def show_config():
    """Show current configuration"""
    FixtureServiceConfig.print_config_summary()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="English Football Fixture Service CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_service.py --full                    # Run processing service for all completed fixtures
  python run_service.py --process-only            # Run fixture processing once for all completed fixtures
  python run_service.py --test                    # Test connections
  python run_service.py --config                  # Show configuration
  python run_service.py --full --process-interval 600  # Custom processing interval
        """
    )
    
    # Action arguments
    parser.add_argument('--full', action='store_true', 
                       help='Run the processing service continuously')
    parser.add_argument('--process-only', action='store_true',
                       help='Run fixture processing once')
    parser.add_argument('--test', action='store_true',
                       help='Test database and crew AI connections')
    parser.add_argument('--config', action='store_true',
                       help='Show current configuration')
    
    # Configuration arguments
    parser.add_argument('--process-interval', type=int,
                       help='Processing interval in seconds (default: 3600)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Please copy env_template.txt to .env and configure your settings")
        print("   Or set environment variables directly")
        print()
    
    # Show configuration if requested
    if args.config:
        show_config()
        return
    
    # Validate configuration
    missing_config = FixtureServiceConfig.validate_config()
    if missing_config:
        print("❌ Missing required configuration:")
        for key, description in missing_config.items():
            print(f"   - {key}: {description}")
        print("\nPlease set the required environment variables and try again.")
        sys.exit(1)
    
    # Run the appropriate action
    try:
        if args.test:
            asyncio.run(test_connection())
        elif args.process_only:
            asyncio.run(run_processing_only())
        elif args.full:
            asyncio.run(run_full_service(args.process_interval))
        else:
            # Default to processing service if no action specified
            print("No action specified, running processing service...")
            asyncio.run(run_full_service(args.process_interval))
            
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
