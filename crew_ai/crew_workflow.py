#!/usr/bin/env python3
"""
European Football Blog - Crew AI Workflow
A scalable agent system for automated European football content creation
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool,WebsiteSearchTool


# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("SERPER_API_KEY"):
    print("❌ CRITICAL ERROR: SERPER_API_KEY not found!")
    print("   The search tools will not work without this key.")
    print("   Please add SERPER_API_KEY=your_key_here to your .env file")
    print("   Get a free key from: https://serper.dev/")
    exit(1)

# Instantiate tools
search_tool = SerperDevTool()

# Initialize RAG tool with error handling for Docker environments
try:
    rag_tool = WebsiteSearchTool()
except PermissionError:
    # Fallback: Use only search_tool if RAG tool fails due to permissions
    print("⚠️ Warning: WebsiteSearchTool initialization failed due to permissions. Using SerperDevTool only.")
    rag_tool = search_tool

print(f"✅ Tools initialized:")
print(f"  - Search Tool: {search_tool.__class__.__name__}")
print(f"  - SERPER_API_KEY: {'✅ Set' if os.getenv('SERPER_API_KEY') else '❌ Missing'}")

class AutonomousSportsBlogCrew:
    """
    Crew AI workflow for European football blog content creation.
    Focused on creating multiple articles from recent football results.
    """
    
    def _sanitize_team_name(self, team_name: str) -> str:
        """
        Sanitize team name for use in file paths by removing shell special characters.
        
        Args:
            team_name: Original team name
            
        Returns:
            Sanitized team name safe for file paths
        """
        # Replace shell special characters with underscores or remove them
        sanitized = team_name.replace('&', 'and')  # Brighton & Hove Albion -> Brighton and Hove Albion
        sanitized = sanitized.replace(' ', '_')    # Spaces to underscores
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in ('_', '-'))  # Keep only alphanumeric, underscores, hyphens
        return sanitized
    
    def _extract_and_update_score_from_data(self, match_data: str, fixture_id: str, home_team: str, away_team: str, current_home_score: int, current_away_score: int) -> Dict[str, Any]:
        """
        Extract score from collected match data using LLM agent and update the fixtures table if a different score is found.
        
        Args:
            match_data: Collected match data text
            fixture_id: ID of the fixture in the database
            home_team: Home team name
            away_team: Away team name
            current_home_score: Current home score in database
            current_away_score: Current away score in database
            
        Returns:
            Dictionary with score extraction and update results
        """
        try:
            # Create a specialized agent for score extraction
            score_extraction_agent = Agent(
                role="Score Extraction Specialist",
                goal="Extract the final match score from match data and reports",
                backstory="""You are a specialized football data analyst with expertise in extracting accurate 
                match scores from various sources including match reports, live updates, and official results. 
                You have a keen eye for identifying the definitive final score from match data and can distinguish 
                between provisional scores, half-time scores, and the actual final result.""",
                allow_delegation=False,
                llm=self.llm,
                tools=[search_tool, rag_tool]
            )
            
            # Create task for score extraction
            score_extraction_task = Task(
                description=f"""
                Analyze the following match data and extract the FINAL SCORE for the match between {home_team} and {away_team}.
                
                MATCH DATA TO ANALYZE:
                {match_data}
                
                CURRENT DATABASE SCORE: {current_home_score}-{current_away_score} {"(NO SCORE IN DATABASE)" if current_home_score is None or current_away_score is None else ""}
                
                Your task is to:
                1. Carefully read through all the match data provided
                2. Identify the definitive final score of the match
                3. Look for phrases like "final score", "result", "ended", "finished", "victory", "defeat"
                4. Extract the score in the format "home_score-away_score" (e.g., "2-1", "0-0", "3-2")
                5. If you find multiple score mentions, prioritize the final/definitive score
                6. If no clear final score is found, respond with "NO_SCORE_FOUND"
                
                IMPORTANT RULES:
                - Only extract the FINAL score, not half-time or provisional scores
                - The score should be in format "home_score-away_score" where home_score is {home_team}'s goals and away_score is {away_team}'s goals
                - If the current database score is None-None (no score in database) and you find a score, return the found score
                - If the score matches the current database score ({current_home_score}-{current_away_score}), respond with "SCORE_CONFIRMED"
                - If you find a different score than what's in the database, respond with just the score (e.g., "2-1")
                - If you cannot determine the final score with confidence, respond with "NO_SCORE_FOUND"
                
                CRITICAL: If the database has no score (None-None) and you find a score in the match data, you MUST return the found score, NOT "SCORE_CONFIRMED".
                
                EXAMPLES:
                - If database shows "None-None" and you find "0-3", return "0-3"
                - If database shows "0-0" and you find "0-3", return "0-3" 
                - If database shows "0-3" and you find "0-3", return "SCORE_CONFIRMED"
                - If database shows "0-3" and you find "1-2", return "1-2"
                - If no clear score found, return "NO_SCORE_FOUND"
                
                Respond with ONLY one of these options:
                
                Respond with ONLY one of these options:
                - "SCORE_CONFIRMED" (if score matches database)
                - "NO_SCORE_FOUND" (if no clear final score found)
                - The actual score in format "X-Y" (if different score found)
                
                Example responses:
                - "SCORE_CONFIRMED"
                - "NO_SCORE_FOUND" 
                - "2-1"
                - "0-0"
                - "3-2"
                """,
                agent=score_extraction_agent,
                expected_output="Either 'SCORE_CONFIRMED', 'NO_SCORE_FOUND', or a score in format 'X-Y'",
                verbose=False
            )
            
            # Debug: Print the task description for troubleshooting
            print(f"🔍 DEBUG: Score extraction task description:")
            print(f"  Home team: {home_team}")
            print(f"  Away team: {away_team}")
            print(f"  Current DB score: {current_home_score}-{current_away_score}")
            print(f"  Has None values: {current_home_score is None or current_away_score is None}")
            print(f"  Match data length: {len(match_data)} characters")
            print(f"  Match data preview: {match_data[:200]}...")
            
            # Execute the score extraction task
            crew = Crew(
                agents=[score_extraction_agent],
                tasks=[score_extraction_task],
                process=Process.sequential
            )
            
            result = crew.kickoff()
            extracted_result = str(result).strip()
            
            print(f"🔍 LLM extracted result: '{extracted_result}'")
            
            # Parse the result
            if extracted_result == "SCORE_CONFIRMED":
                # Check if this is a valid confirmation (not None-None)
                if current_home_score is None or current_away_score is None:
                    print(f"⚠️ WARNING: LLM returned SCORE_CONFIRMED but database has None values")
                    return {
                        'found': False,
                        'updated': False,
                        'message': 'LLM incorrectly confirmed None-None score'
                    }
                return {
                    'found': True,
                    'updated': False,
                    'found_score': f"{current_home_score}-{current_away_score}",
                    'message': 'Score confirmed by LLM analysis'
                }
            elif extracted_result == "NO_SCORE_FOUND":
                return {
                    'found': False,
                    'updated': False,
                    'message': 'LLM could not find a definitive final score'
                }
            elif "-" in extracted_result and len(extracted_result.split("-")) == 2:
                try:
                    # Parse the extracted score
                    home_score_str, away_score_str = extracted_result.split("-")
                    home_score = int(home_score_str.strip())
                    away_score = int(away_score_str.strip())
                    
                    # Validate reasonable score range (0-20 for each team)
                    if 0 <= home_score <= 20 and 0 <= away_score <= 20:
                        extracted_score = {
                            'home': home_score,
                            'away': away_score
                        }
                        
                        # Check if the extracted score is different from current score
                        if (extracted_score['home'] == current_home_score and extracted_score['away'] == current_away_score):
                            return {
                                'found': True,
                                'updated': False,
                                'found_score': f"{extracted_score['home']}-{extracted_score['away']}",
                                'message': 'LLM confirmed current database score'
                            }
                        
                        # Update the database with the new score
                        if fixture_id:
                            try:
                                # Import Supabase client
                                from supabase import create_client, Client
                                from dotenv import load_dotenv
                                import os
                                
                                # Load environment variables
                                load_dotenv()
                                
                                # Get Supabase configuration
                                from config import FixtureServiceConfig
                                supabase_url, supabase_key = FixtureServiceConfig.get_supabase_config()
                                supabase: Client = create_client(supabase_url, supabase_key)
                                
                                # Update the fixture with the new score
                                update_result = supabase.table('fixtures').update({
                                    'home_score': extracted_score['home'],
                                    'away_score': extracted_score['away']
                                }).eq('id', fixture_id).execute()
                                
                                if update_result.data:
                                    return {
                                        'found': True,
                                        'updated': True,
                                        'old_score': f"{current_home_score}-{current_away_score}",
                                        'new_score': extracted_score,
                                        'found_score': f"{extracted_score['home']}-{extracted_score['away']}",
                                        'message': f'LLM extracted and updated score from {current_home_score}-{current_away_score} to {extracted_score["home"]}-{extracted_score["away"]}'
                                    }
                                else:
                                    return {
                                        'found': True,
                                        'updated': False,
                                        'found_score': f"{extracted_score['home']}-{extracted_score['away']}",
                                        'message': 'LLM found different score but database update failed'
                                    }
                                    
                            except Exception as e:
                                return {
                                    'found': True,
                                    'updated': False,
                                    'found_score': f"{extracted_score['home']}-{extracted_score['away']}",
                                    'message': f'LLM found different score but database update error: {str(e)}'
                                }
                        else:
                            return {
                                'found': True,
                                'updated': False,
                                'found_score': f"{extracted_score['home']}-{extracted_score['away']}",
                                'message': 'LLM found different score but no fixture_id provided for database update'
                            }
                    else:
                        return {
                            'found': False,
                            'updated': False,
                            'message': f'LLM extracted invalid score range: {extracted_result}'
                        }
                        
                except (ValueError, IndexError) as e:
                    return {
                        'found': False,
                        'updated': False,
                        'message': f'LLM extracted invalid score format: {extracted_result} (error: {str(e)})'
                    }
            else:
                # LLM returned unexpected format, try fallback regex extraction
                print(f"🔍 LLM returned unexpected format: '{extracted_result}', attempting fallback regex extraction...")
                
                # Fallback: Try simple regex extraction if LLM failed
                import re
                
                # Look for common score patterns
                score_patterns = [
                    r'FINAL SCORE:\s*(\d+)-(\d+)',
                    r'final score[:\s]*(\d+)-(\d+)',
                    r'result[:\s]*(\d+)-(\d+)',
                    r'ended[:\s]*(\d+)-(\d+)',
                    r'finished[:\s]*(\d+)-(\d+)',
                    r'(\d+)-(\d+)\s*\(.*?\)',  # Pattern like "0-3 (Nottingham Forest - West Ham United)"
                ]
                
                for pattern in score_patterns:
                    match = re.search(pattern, match_data, re.IGNORECASE)
                    if match:
                        try:
                            home_score = int(match.group(1))
                            away_score = int(match.group(2))
                            
                            if 0 <= home_score <= 20 and 0 <= away_score <= 20:
                                print(f"✅ Fallback regex found score: {home_score}-{away_score}")
                                
                                # Update database if we have a fixture_id
                                if fixture_id and (home_score != current_home_score or away_score != current_away_score):
                                    try:
                                        # Import Supabase client
                                        from supabase import create_client, Client
                                        from dotenv import load_dotenv
                                        import os
                                        
                                        # Load environment variables
                                        load_dotenv()
                                        
                                        # Get Supabase configuration
                                        from config import FixtureServiceConfig
                                        supabase_url, supabase_key = FixtureServiceConfig.get_supabase_config()
                                        supabase: Client = create_client(supabase_url, supabase_key)
                                        
                                        # Update the fixture with the new score
                                        update_result = supabase.table('fixtures').update({
                                            'home_score': home_score,
                                            'away_score': away_score
                                        }).eq('id', fixture_id).execute()
                                        
                                        if update_result.data:
                                            return {
                                                'found': True,
                                                'updated': True,
                                                'old_score': f"{current_home_score}-{current_away_score}",
                                                'new_score': {'home': home_score, 'away': away_score},
                                                'found_score': f"{home_score}-{away_score}",
                                                'message': f'Fallback regex extracted and updated score from {current_home_score}-{current_away_score} to {home_score}-{away_score}'
                                            }
                                        else:
                                            return {
                                                'found': True,
                                                'updated': False,
                                                'found_score': f"{home_score}-{away_score}",
                                                'message': 'Fallback regex found score but database update failed'
                                            }
                                            
                                    except Exception as e:
                                        return {
                                            'found': True,
                                            'updated': False,
                                            'found_score': f"{home_score}-{away_score}",
                                            'message': f'Fallback regex found score but database update error: {str(e)}'
                                        }
                                else:
                                    return {
                                        'found': True,
                                        'updated': False,
                                        'found_score': f"{home_score}-{away_score}",
                                        'message': 'Fallback regex found score but no fixture_id provided for database update'
                                    }
                        except (ValueError, IndexError):
                            continue
                
                # If we get here, neither LLM nor regex found a valid score
                return {
                    'found': False,
                    'updated': False,
                    'message': f'Neither LLM nor fallback regex could extract a valid score. LLM returned: {extracted_result}'
                }
                
        except Exception as e:
            return {
                'found': False,
                'updated': False,
                'message': f'Error in LLM score extraction: {str(e)}'
            }
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the crew with specified LLM model.
        
        Args:
            model_name: OpenAI model to use for all agents
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _create_english_football_data_agent(self) -> Agent:
        """Create the English Football Data Agent responsible for fetching recent fixtures and results."""
        return Agent(
            role="English Football Data Specialist",
            goal="Fetch and analyze recent English football fixtures, results, and key statistics to identify compelling storylines",
            backstory="""You are a dedicated English football data analyst with access to comprehensive 
            match databases covering the Premier League, Championship, FA Cup, Carabao Cup, and other English competitions. 
            You have expertise in analyzing match results, goal statistics, player performances, and emerging trends. 
            Your role is to provide accurate, up-to-date information about recent matches, unexpected results, 
            standout performances, and developing narratives that would interest football fans and content creators.""",
            allow_delegation=False,
            llm=self.llm,
            tools=[search_tool,rag_tool],
        )
    
    def _create_topic_generation_agent(self) -> Agent:
        """Create the Topic Generation Agent responsible for creating interesting article topics from match results."""
        return Agent(
            role="English Football Topic Strategist",
            goal="Analyze match results and data to identify the 5 most interesting and engaging article topics",
            backstory="""You are a creative content strategist specializing in English football who excels at 
            identifying compelling angles from match results, statistics, and player performances. You have a 
            keen understanding of what makes football content engaging - from dramatic comebacks and tactical 
            masterclasses to emerging player stories and managerial decisions. You can spot patterns, trends, 
            and narratives that would captivate both casual fans and football enthusiasts. Your topics are 
            always timely, relevant, and have strong potential for engaging content creation.""",
            allow_delegation=False,
            llm=self.llm,
            tools=[search_tool,rag_tool]
        )
    
    def _create_content_planner(self) -> Agent:
        """Create the European Football Content Strategist agent responsible for research and topic outlines."""
        return Agent(
            role="European Football Content Strategist",
            goal="Research and create comprehensive content outlines for European football blog articles",
            backstory="""You are an expert European football analyst and content strategist with deep knowledge 
            of the Premier League, La Liga, Serie A, Bundesliga, Ligue 1, and other European competitions. You have 
            a knack for identifying compelling angles from recent matches, player performances, transfer news, and 
            tactical developments. Your expertise spans from match analysis to player profiles, transfer rumors, 
            and emerging trends across European football.""",
            allow_delegation=False,
            tools=[search_tool,rag_tool],
            llm=self.llm
        )
    
    def _create_content_writer(self) -> Agent:
        """Create the European Football Journalist agent responsible for expanding outlines into full articles."""
        return Agent(
            role="European Football Journalist",
            goal="Transform detailed content outlines into engaging, well-researched European football articles",
            backstory="""You are a talented European football journalist and content creator who specializes 
            in making complex football topics accessible and engaging to readers. You have a strong writing voice 
            that combines tactical analysis with storytelling flair. Your articles are known for their clear 
            explanations of match events, compelling player narratives, and ability to connect with both casual 
            fans and football connoisseurs across Europe.""",
            allow_delegation=False,
            tools=[search_tool,rag_tool],
            llm=self.llm
        )
    
    def _create_content_editor(self) -> Agent:
        """Create the European Football Content Editor agent responsible for proofreading and finalizing articles."""
        return Agent(
            role="European Football Content Editor",
            goal="Review, edit, and finalize European football articles to ensure high quality and consistency",
            backstory="""You are a meticulous editor with years of experience in European football journalism 
            and digital content. You have an eagle eye for grammar, style, and factual accuracy. Your expertise 
            in European football ensures that tactical content is precise while maintaining readability. You're 
            known for elevating good content to excellent content through careful editing and strategic improvements, 
            especially in match reports and player analysis.""",
            allow_delegation=False,
            tools=[search_tool,rag_tool],
            llm=self.llm
        )
    
    def create_articles_for_specific_fixture(self, fixture_details: Dict[str, Any], target_length: str = "800-1200 words") -> Dict[str, Any]:
        """
        Create articles for a specific completed fixture.
        
        Args:
            fixture_details: Dictionary containing fixture information (home_team, away_team, score, date, etc.)
            target_length: Target word count for articles
            
        Returns:
            Dictionary containing generated articles and workflow metadata
        """
        
        # Extract fixture details
        home_team = fixture_details.get('home_team', '')
        away_team = fixture_details.get('away_team', '')
        home_score = fixture_details.get('home_score', 0)
        away_score = fixture_details.get('away_score', 0)
        match_date = fixture_details.get('match_date', '')
        competition = fixture_details.get('competition', 'Premier League')
        fixture_id = fixture_details.get('id', '')
        
        # Sanitize team names for file paths
        safe_home_team = self._sanitize_team_name(home_team)
        safe_away_team = self._sanitize_team_name(away_team)
        
        # Create match topic
        match_topic = f"{home_team} vs {away_team} - {home_score}-{away_score} Match Analysis ({match_date})"
        
        # Initialize agents
        data_agent = self._create_english_football_data_agent()
        topic_agent = self._create_topic_generation_agent()
        
        # Task 1: Collect specific match data and score
        data_collection_task = Task(
            description=f"""
            Collect detailed information about the specific match: {home_team} vs {away_team} played on {match_date}.
            
            CRITICAL: You MUST find and extract the FINAL SCORE of this match from reliable sources.
            Look for the exact final score (e.g., "2-1", "0-0", "3-2") in match reports, results pages, and live score updates.
            
            Use search tools to find:
            - Match report and analysis from reliable sources (BBC Sport, Sky Sports, Guardian, ESPN, Premier League official site)
            - Live score results and final score confirmation
            - Key moments, goals, cards, substitutions
            - Manager comments and press conference quotes
            - Player ratings and performances
            - Post-match statistics and analysis
            - Fan reactions and social media highlights
            
            Focus ONLY on this specific match. Do not include other matches or general team news.
            
            Provide structured data including:
            - FINAL SCORE (this is the most important piece of information)
            - Match details (date, venue, attendance)
            - Goal scorers and assists
            - Key incidents (cards, penalties, VAR decisions)
            - Manager and player quotes
            - Statistical highlights
            - Source URLs for verification
            
            IMPORTANT: If you find a different score than what was provided ({home_score}-{away_score}), 
            clearly indicate the correct score in your output. The score should be in format "home_score-away_score".
            
            Output must be comprehensive and factual, based only on this specific fixture.
            """,
            agent=data_agent,
            expected_output="Detailed match data and analysis for the specific fixture, including the final score",
            output_file=f'match_data/match_data_{safe_home_team}_{safe_away_team}_{match_date}.md'
        )
        
        # Task 2: Generate focused topics for this match
        topic_generation_task = Task(
            description=f"""
            Using the detailed match data collected in the previous task, generate 3-5 focused article topics 
            that tell the story of {home_team} vs {away_team}.
            
            IMPORTANT: Use the specific match information, statistics, quotes, and incidents from the data collection 
            to create topics that are grounded in actual match events and facts.
            
            Consider the collected data about:
            - The significance of the result based on actual context
            - Outstanding individual performances mentioned in reports
            - Tactical aspects and key moments identified
            - Impact on league standings or team form
            - Controversial incidents or VAR decisions that occurred
            - Manager reactions and player quotes from the match
            - Statistical highlights and performance metrics
            
            Each topic should:
            - Be specific to this match and based on collected data
            - Reference actual events, players, or incidents from the match
            - Have strong narrative potential supported by facts
            - Appeal to football fans with authentic details
            - Be suitable for {target_length} articles
            
            Format as JSON array with topic titles that reflect the actual match story.
            Example: ["[Actual Player Name] Masterclass Leads [Team] to Victory", "[Specific Incident]: The Turning Point in [Team] vs [Team]"]
            
            Base your topics on the real data collected, not generic football topics.
            """,
            agent=topic_agent,
            expected_output="JSON array of 3-5 data-driven, match-specific article topics",
            context=[data_collection_task],
            output_file=f'topic_data/topics_{safe_home_team}_{safe_away_team}_{match_date}.md'
        )
        
        # Create articles for each topic
        articles = []
        topics = []
        match_data_context = ""
        
        try:
            # Execute data collection and topic generation together so topic agent has access to collected data
            data_and_topic_crew = Crew(
                agents=[data_agent, topic_agent],
                tasks=[data_collection_task, topic_generation_task],
                process=Process.sequential
            )
            
            # Get both data collection and topic generation results
            combined_result = data_and_topic_crew.kickoff()
            
            # Extract the data collection output for context
            # The data collection task writes to a file, so we can read it
            try:
                data_file_path = f'match_data/match_data_{safe_home_team}_{safe_away_team}_{match_date}.md'
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    match_data_context = f.read()
                print(f"✅ Successfully read match data from file: {data_file_path}")
            except (FileNotFoundError, UnicodeDecodeError, PermissionError) as e:
                print(f"⚠️ Could not read match data file ({e}), extracting from combined result...")
                # Fallback to extracting from combined result
                combined_text = str(combined_result)
                
                # Try multiple patterns to extract data collection content
                if "Task 1:" in combined_text and "Task 2:" in combined_text:
                    match_data_context = combined_text.split("Task 2:")[0].replace("Task 1:", "").strip()
                elif "Data Collection" in combined_text and "Topic Generation" in combined_text:
                    match_data_context = combined_text.split("Topic Generation")[0].replace("Data Collection", "").strip()
                else:
                    # Use first significant portion of the result
                    match_data_context = combined_text[:max(1000, len(combined_text)//2)]
                
                print(f"📝 Extracted {len(match_data_context)} characters of match data from result")
            
            # Extract score from collected data and update database if needed
            score_update_result = self._extract_and_update_score_from_data(match_data_context, fixture_id, home_team, away_team, home_score, away_score)
            if score_update_result['updated']:
                print(f"✅ Score updated in database: {score_update_result['old_score']} → {score_update_result['new_score']}")
                # Update local variables with new score
                home_score = score_update_result['new_score']['home']
                away_score = score_update_result['new_score']['away']
            elif score_update_result['found']:
                print(f"ℹ️ Score confirmed: {score_update_result['found_score']}")
            else:
                print(f"⚠️ Could not extract score from collected data")
            
            topic_result = combined_result  # Use combined result for topic parsing
            
            # If we didn't get good data context, create a comprehensive one from fixture details
            if not match_data_context or len(match_data_context) < 100:
                match_data_context = f"""
                Match Details:
                - Teams: {home_team} vs {away_team}
                - Final Score: {home_score}-{away_score}
                - Date: {match_date}
                - Competition: {competition}
                - Venue: {fixture_details.get('venue', 'N/A')}
                - Matchday: {fixture_details.get('matchday', 'N/A')}
                - Season: {fixture_details.get('season', 'N/A')}
                """
            else:
                # Enhance the collected data with fixture details for completeness
                match_data_context = f"""
                FIXTURE DETAILS:
                - Teams: {home_team} vs {away_team}
                - Final Score: {home_score}-{away_score}
                - Date: {match_date}
                - Competition: {competition}
                - Venue: {fixture_details.get('venue', 'N/A')}
                - Matchday: {fixture_details.get('matchday', 'N/A')}
                - Season: {fixture_details.get('season', 'N/A')}
                
                COLLECTED MATCH DATA:
                {match_data_context}
                """
            
            # Update match topic with potentially updated scores
            match_topic = f"{home_team} vs {away_team} - {home_score}-{away_score} Match Analysis ({match_date})"
            
            # Parse topics from the result
            import json
            import re
            
            # Try to extract JSON from the topic generation result
            topic_result_text = str(topic_result)
            json_match = re.search(r'\[.*?\]', topic_result_text, re.DOTALL)
            
            if json_match:
                try:
                    topics = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    # Fallback to default topics if parsing fails
                    topics = [
                        f"Match Report: {home_team} {home_score}-{away_score} {away_team}",
                        f"Player Analysis: Key Performances in {home_team} vs {away_team}",
                        f"Tactical Breakdown: How the Match Was Won"
                    ]
            else:
                # Fallback topics
                topics = [
                    f"Match Report: {home_team} {home_score}-{away_score} {away_team}",
                    f"Player Analysis: Key Performances in {home_team} vs {away_team}",
                    f"Tactical Breakdown: How the Match Was Won"
                ]
            
            # Create articles for each topic with match data context
            for i, topic in enumerate(topics[:3]):  # Limit to 3 articles
                print(f"Creating article for topic: {topic}")
                try:
                    article_result = self.create_article(
                        topic=str(topic), 
                        article_type="match_report",
                        target_length=target_length,
                        context_data=match_data_context  # Pass the collected match data
                    )
                    if article_result and 'article_content' in article_result:
                        articles.append({
                            'title': str(topic),
                            'content': article_result['article_content'],
                            'article_type': 'match_report',
                            'word_count': article_result.get('word_count', 0),
                            'fixture_match': f"{home_team} vs {away_team}",
                            'match_date': match_date,
                            'context_used': bool(match_data_context),
                            'article_result': article_result
                        })
                        
                except Exception as e:
                    print(f"Error creating article for topic '{topic}': {e}")
                    
        except Exception as e:
            print(f"Error in fixture-specific workflow: {e}")
            return {
                'error': str(e),
                'fixture': fixture_details,
                'articles': [],
                'topics': []
            }
        
        return {
            "fixture": fixture_details,
            "match_topic": match_topic,
            "topics_generated": len(topics),
            "articles_created": len(articles),
            "topics": topics,
            "articles": articles,
            "match_data_collected": bool(match_data_context and len(match_data_context) > 100),
            "context_data_length": len(match_data_context) if match_data_context else 0,
            "score_update_result": score_update_result,  # Include score update information
            "final_score": f"{home_score}-{away_score}",  # Include final score after potential updates
            "workflow_status": "completed",
            "agents_used": ["English Football Data Specialist", "English Football Topic Strategist", "European Football Content Strategist", "European Football Journalist", "European Football Content Editor"]
        }

    def create_article(self, topic: str, article_type: str = "match_report", target_length: str = "800-1200 words", context_data: str = None) -> Dict[str, Any]:
        """
        Execute the complete European football article creation workflow.
        
        Args:
            topic: The main topic or headline for the article
            article_type: Type of article (match_report, player_analysis, transfer_news, etc.)
            target_length: Target word count for the final article
            context_data: Additional context data to inform the article (match details, statistics, etc.)
            
        Returns:
            Dictionary containing the final article and workflow metadata
        """
        
        # Task 1: Content Planning
        planning_task = Task(
            description=f"""
            Research and create a comprehensive content outline for a European football article about: {topic}
            
            Article Type: {article_type}
            Target Length: {target_length}
            
            {f"CONTEXT DATA PROVIDED: Use this specific match information as the foundation for your outline:{chr(10)}{context_data}{chr(10)}" if context_data else ""}
            
            Use the search tool to go into the provided urls to get the accurate information about the events of the game.
            Your outline should include:
            1. Key research points and recent match data
            2. Main sections and subsections
            3. Key player quotes or manager statements to include
            4. Relevant statistics, form data, and performance metrics
            5. SEO keywords and meta description
            6. Target audience and tone recommendations
            
            {("IMPORTANT: Base your outline on the provided context data about this specific match. Use the actual match details, scores, and information provided above." if context_data else "Focus on European football relevance, recent results, and current player news.")}CRITICAL ERROR: SERPER_API_KEY not found!
            Include specific leagues, teams, and players where relevant.
            """,
            agent=self._create_content_planner(),
            expected_output="A detailed content outline with research notes, structure, and recommendations",
            verbose=True
        )
        
        # Task 2: Content Writing
        writing_task = Task(
            description=f"""
            Using the detailed outline provided, write a complete European football blog article about: {topic}
            
            {f"CONTEXT DATA FOR REFERENCE: Base your article on this specific match information:{chr(10)}{context_data}{chr(10)}" if context_data else ""}
            Use the search tool to go into the provided urls to get the accurate information about the events of the game.
            Requirements:
            - Follow the outline structure exactly
            - Target length: {target_length}
            - Write in an engaging, journalistic style
            - Include relevant statistics, recent results, and player performance data
            - Maintain accuracy in tactical details and player information
            - Use appropriate football terminology and European football context
            - Include a compelling headline and introduction
            - End with a strong conclusion
            - Reference specific matches, players, and teams accurately
            {"- CRITICAL: Use the specific match data provided in the context to ensure accuracy and relevance" if context_data else ""}
            
            Make the content accessible to both casual European football fans and dedicated followers.
            Focus on recent events, current form, and emerging storylines.
            """,
            agent=self._create_content_writer(),
            expected_output="A complete, well-written European football blog article ready for editing",
            context=[planning_task]
        )
        
        # Task 3: Content Editing
        editing_task = Task(
            description=f"""
            Review and edit the completed European football blog article to ensure:
            Use the search tool to go into the provided urls to get the accurate information about the events of the game.
            1. Grammar, spelling, and punctuation are perfect
            2. Content flows logically and is well-structured
            3. Football facts, player names, and team information are accurate
            4. Writing style is consistent and engaging
            5. SEO optimization is implemented
            6. Fact-checking is completed (especially player stats and match results)
            7. Content meets editorial standards for European football coverage
            
            Make any necessary improvements while preserving the author's voice and intent.
            Pay special attention to accuracy of player names, team names, and recent match results.
            
            IMPORTANT: Return ONLY the final, polished article content. Do not include any editorial notes, 
            comments, or metadata in your response. Just the clean, publication-ready article.
            """,
            agent=self._create_content_editor(),
            expected_output="A polished, publication-ready European football blog article (content only, no notes)",
            context=[writing_task]
        )
        
        # Set up the crew for this workflow
        crew = Crew(
            agents=[
                self._create_content_planner(),
                self._create_content_writer(),
                self._create_content_editor()
            ],
            tasks=[planning_task, writing_task, editing_task],
            process=Process.sequential
        )
        
        # Execute the workflow
        result = crew.kickoff()
        
        # Extract the article content from the result
        article_content = ""
        if result:
            # Try different ways to extract the content
            if isinstance(result, str):
                article_content = result
            elif isinstance(result, dict):
                # Look for common Crew AI result keys
                for key in ['output', 'result', 'content', 'article', 'text']:
                    if key in result and result[key]:
                        article_content = str(result[key])
                        break
                # If no specific key found, try to get the first non-empty value
                if not article_content:
                    for value in result.values():
                        if value and isinstance(value, str) and len(value) > 100:
                            article_content = value
                            break
            elif hasattr(result, 'output'):
                article_content = str(result.output)
            elif hasattr(result, 'result'):
                article_content = str(result.result)
        
        # If still no content, use the raw result
        if not article_content and result:
            article_content = str(result)
        
        return {
            "topic": topic,
            "article_type": article_type,
            "target_length": target_length,
            "article_content": article_content,
            "workflow_status": "completed",
            "agents_used": ["European Football Content Strategist", "European Football Journalist", "European Football Content Editor"],
            "raw_result": str(result) if result else ""
        }


def main():
    """Example usage of the European Football Blog Crew."""
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    if not os.getenv("SERPER_API_KEY"):
        print("⚠️  Warning: SERPER_API_KEY not found in environment variables")
        print("   SerperDevTool (search_tool) will not work without this key")
        print("   Please add SERPER_API_KEY=your_key_here to your .env file")
        print("   This will affect the data collection agent's ability to fetch recent results")
        print()
    
    # Check if crewai_tools is properly installed
    try:
        import crewai_tools
        print(f"✅ crewai_tools imported successfully: {crewai_tools.__version__ if hasattr(crewai_tools, '__version__') else 'version unknown'}")
    except ImportError as e:
        print(f"❌ Error importing crewai_tools: {e}")
        print("Please install with: pip install crewai-tools")
        return
    
    # Initialize the crew
    print("⚽ Initializing European Football Blog Crew...")
    crew = AutonomousSportsBlogCrew()
    
    # Example: Create multiple articles from recent results
    print(f"\n📝 Creating multiple articles from recent Premier League results...")
    try:
        result = crew.create_multiple_articles_from_results(
            competition="Premier League",
            days_back=7,
            target_length="800-1200 words"
        )
        
        print(f"\n✅ Multiple articles workflow completed!")
        print(f"Competition: {result['competition']}")
        print(f"Topics Generated: {result['topics_generated']}")
        print(f"Status: {result['workflow_status']}")
        
    except Exception as e:
        print(f"❌ Error during workflow execution: {str(e)}")
        print("Please check your API key and internet connection")


if __name__ == "__main__":
    main()
