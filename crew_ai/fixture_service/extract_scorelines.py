#!/usr/bin/env python3
"""
Scoreline Extraction Script
Standalone script to extract scorelines from generated articles and update fixtures table.
"""

import os
import sys
import asyncio
from typing import Optional

# Add the fixture service directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fixture_service import FixtureService

async def main():
    """
    Main function to run scoreline extraction
    """
    print("🎯 Scoreline Extraction Script")
    print("=" * 50)
    
    try:
        # Initialize the fixture service
        service = FixtureService()
        
        # Test connection
        service.test_connection()
        
        # Check if a specific fixture ID was provided
        fixture_id = None
        if len(sys.argv) > 1:
            fixture_id = sys.argv[1]
            print(f"🎯 Processing specific fixture: {fixture_id}")
        else:
            print("🔍 Processing all fixtures with missing scores...")
        
        # Run the scoreline extraction
        result = await service.extract_and_update_scorelines(fixture_id)
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 RESULTS")
        print("=" * 50)
        
        if result['success']:
            print(f"✅ Success: {result.get('message', 'Operation completed')}")
            print(f"📈 Fixtures Updated: {result['fixtures_updated']}")
            
            if 'total_fixtures_found' in result:
                print(f"🔍 Total Fixtures Found: {result['total_fixtures_found']}")
                print(f"📰 Fixtures with Articles: {result['fixtures_with_articles']}")
            
            if 'scoreline' in result:
                scoreline = result['scoreline']
                print(f"⚽ Extracted Scoreline: {scoreline['home_score']}-{scoreline['away_score']}")
                
        else:
            print(f"❌ Error: {result.get('error', result.get('message', 'Unknown error'))}")
            print(f"📈 Fixtures Updated: {result['fixtures_updated']}")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
