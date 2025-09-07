#!/usr/bin/env python3
"""
Test script for LLM-based score extraction functionality in the crew workflow.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crew_workflow import AutonomousSportsBlogCrew

def test_llm_score_extraction():
    """Test the LLM-based score extraction functionality"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    if not os.getenv("SERPER_API_KEY"):
        print("❌ Error: SERPER_API_KEY not found in environment variables")
        print("Please add SERPER_API_KEY=your_key_here to your .env file")
        return
    
    # Initialize the crew
    crew = AutonomousSportsBlogCrew()
    
    # Test data with different score scenarios
    test_cases = [
        {
            'name': 'Clear final score in match report',
            'data': """
            Match Report: Manchester United vs Liverpool
            
            The final score was 2-1 with Manchester United defeating Liverpool at Old Trafford.
            Goals were scored by Rashford (15') and Fernandes (67') for United, while Salah (45') 
            netted for Liverpool. The match ended in a 2-1 victory for the home side.
            """,
            'expected': {'home': 2, 'away': 1}
        },
        {
            'name': 'Score confirmed in database',
            'data': """
            Arsenal vs Chelsea Match Analysis
            
            The match between Arsenal and Chelsea ended in a 0-0 draw at the Emirates Stadium.
            Both teams had chances but failed to convert, resulting in a goalless draw.
            The final result was 0-0, confirming the current database entry.
            """,
            'expected': {'home': 0, 'away': 0}
        },
        {
            'name': 'Multiple score mentions with final score',
            'data': """
            Tottenham vs Everton Live Updates
            
            Half-time: Tottenham 1-0 Everton (Kane 23')
            Full-time: Tottenham 3-2 Everton
            Final score: 3-2 to Tottenham with goals from Kane (23', 67') and Son (45'), 
            while Everton scored through Calvert-Lewin (55') and Richarlison (78').
            """,
            'expected': {'home': 3, 'away': 2}
        },
        {
            'name': 'No clear final score',
            'data': """
            Brighton vs Newcastle Match Summary
            
            The match between Brighton and Newcastle was an exciting encounter with both teams 
            creating numerous chances. The game was closely contested throughout with several 
            near misses and excellent saves from both goalkeepers.
            """,
            'expected': None
        },
        {
            'name': 'Score with different format',
            'data': """
            Crystal Palace vs West Ham Result
            
            Crystal Palace secured a 2:1 victory over West Ham at Selhurst Park.
            The Eagles scored twice through Zaha and Eze, while West Ham's lone goal 
            came from Antonio. The final result was 2-1 to Palace.
            """,
            'expected': {'home': 2, 'away': 1}
        }
    ]
    
    print("🧪 Testing LLM-based score extraction functionality...")
    print("⚠️  Note: This test requires OpenAI API calls and may take some time")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test_case['name']}")
        print(f"{'='*60}")
        print(f"Input data:\n{test_case['data']}")
        
        try:
            # Test the LLM score extraction method
            result = crew._extract_and_update_score_from_data(
                match_data=test_case['data'],
                fixture_id='test_fixture_123',
                home_team='Test Home',
                away_team='Test Away',
                current_home_score=0,
                current_away_score=0
            )
            
            print(f"\nLLM Result: {result}")
            
            if test_case['expected'] is None:
                if not result['found']:
                    print("✅ PASS: LLM correctly found no score")
                else:
                    print("❌ FAIL: LLM found score when none expected")
            else:
                if result['found']:
                    extracted_score = result.get('found_score', '')
                    expected_score = f"{test_case['expected']['home']}-{test_case['expected']['away']}"
                    if extracted_score == expected_score:
                        print("✅ PASS: LLM correctly extracted score")
                    else:
                        print(f"❌ FAIL: Expected {expected_score}, got {extracted_score}")
                else:
                    print("❌ FAIL: LLM failed to extract expected score")
                    
        except Exception as e:
            print(f"❌ ERROR: Test failed with exception: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 LLM-based score extraction testing completed!")
    print("="*60)

if __name__ == "__main__":
    test_llm_score_extraction()
