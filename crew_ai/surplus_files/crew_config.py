"""
Configuration file for European Football Blog Crew AI workflow.
Easily customize agent parameters, LLM settings, and workflow behavior.
"""

from typing import Dict, Any

# LLM Configuration
LLM_CONFIG = {
    "default_model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 4000,
    "fallback_model": "gpt-3.5-turbo"
}

# Agent Configuration
AGENT_CONFIG = {
    "content_planner": {
        "role": "European Football Content Strategist",
        "goal": "Research and create comprehensive content outlines for European football blog articles",
        "backstory": """You are an expert European football analyst and content strategist with deep knowledge 
        of the Premier League, La Liga, Serie A, Bundesliga, Ligue 1, and other European competitions. You have 
        a knack for identifying compelling angles from recent matches, player performances, transfer news, and 
        tactical developments. Your expertise spans from match analysis to player profiles, transfer rumors, 
        and emerging trends across European football.""",
        "verbose": True,
        "allow_delegation": False
    },
    
    "content_writer": {
        "role": "European Football Journalist",
        "goal": "Transform detailed content outlines into engaging, well-researched European football articles",
        "backstory": """You are a talented European football journalist and content creator who specializes 
        in making complex football topics accessible and engaging to readers. You have a strong writing voice 
        that combines tactical analysis with storytelling flair. Your articles are known for their clear 
        explanations of match events, compelling player narratives, and ability to connect with both casual 
        fans and football connoisseurs across Europe.""",
        "verbose": True,
        "allow_delegation": False
    },
    
    "content_editor": {
        "role": "European Football Content Editor",
        "goal": "Review, edit, and finalize European football articles to ensure high quality and consistency",
        "backstory": """You are a meticulous editor with years of experience in European football journalism 
        and digital content. You have an eagle eye for grammar, style, and factual accuracy. Your expertise 
        in European football ensures that tactical content is precise while maintaining readability. You're 
        known for elevating good content to excellent content through careful editing and strategic improvements, 
        especially in match reports and player analysis.""",
        "verbose": True,
        "allow_delegation": False
    }
}

# Task Configuration
TASK_CONFIG = {
    "planning": {
        "description_template": """
        Research and create a comprehensive content outline for an article about: {topic}
        
        Article Type: {article_type}
        Target Length: {target_length}
        
        Your outline should include:
        1. Key research points and recent match data
        2. Main sections and subsections
        3. Key player quotes or manager statements to include
        4. Relevant statistics, form data, and performance metrics
        5. SEO keywords and meta description
        6. Target audience and tone recommendations
        
        Focus on European football relevance, recent results, and current player news.
        Include specific leagues, teams, and players where relevant.
        """,
        "expected_output": "A detailed content outline with research notes, structure, and recommendations"
    },
    
    "writing": {
        "description_template": """
        Using the detailed outline provided, write a complete European football blog article about: {topic}
        
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
        
        Make the content accessible to both casual European football fans and dedicated followers.
        Focus on recent events, current form, and emerging storylines.
        """,
        "expected_output": "A complete, well-written European football blog article ready for editing"
    },
    
    "editing": {
        "description_template": """
        Review and edit the completed European football blog article to ensure:
        
        1. Grammar, spelling, and punctuation are perfect
        2. Content flows logically and is well-structured
        3. Football facts, player names, and team information are accurate
        4. Writing style is consistent and engaging
        5. SEO optimization is implemented
        6. Fact-checking is completed (especially player stats and match results)
        7. Content meets editorial standards for European football coverage
        
        Make any necessary improvements while preserving the author's voice and intent.
        Pay special attention to accuracy of player names, team names, and recent match results.
        """,
        "expected_output": "A polished, publication-ready European football blog article with editorial notes"
    }
}

# Workflow Configuration
WORKFLOW_CONFIG = {
    "process_type": "sequential",
    "verbose": True,
    "max_iterations": 3,
    "memory": True
}

# Content Types and Templates
CONTENT_TYPES = {
    "match_report": {
        "structure": ["Match Summary", "Key Moments", "Player Analysis", "Tactical Breakdown", "Manager Comments", "Conclusion"],
        "tone": "Exciting and detailed",
        "target_length": "800-1200 words"
    },
    "player_analysis": {
        "structure": ["Player Background", "Recent Form", "Key Statistics", "Tactical Role", "Future Prospects", "Conclusion"],
        "tone": "Analytical and insightful",
        "target_length": "1000-1500 words"
    },
    "transfer_news": {
        "structure": ["Transfer Overview", "Player Profile", "Club Analysis", "Financial Details", "Impact Assessment", "Conclusion"],
        "tone": "Informative and engaging",
        "target_length": "800-1200 words"
    },
    "tactical_analysis": {
        "structure": ["Formation Overview", "Key Tactics", "Player Roles", "Opponent Analysis", "Match Impact", "Conclusion"],
        "tone": "Technical and analytical",
        "target_length": "1000-1500 words"
    },
    "league_roundup": {
        "structure": ["Weekend Overview", "Key Results", "Standings Impact", "Player Performances", "Manager Changes", "Conclusion"],
        "tone": "Comprehensive and engaging",
        "target_length": "1200-1800 words"
    }
}

# SEO Configuration
SEO_CONFIG = {
    "default_keywords": [
        "European football",
        "Premier League",
        "La Liga",
        "Serie A",
        "Bundesliga",
        "Ligue 1",
        "Champions League",
        "Europa League",
        "football transfer news",
        "match results"
    ],
    "meta_description_length": 155,
    "title_max_length": 60
}

# Quality Assurance Settings
QA_CONFIG = {
    "fact_checking": True,
    "grammar_checking": True,
    "plagiarism_detection": False,
    "readability_score_target": 70,
    "minimum_word_count": 600,
    "football_accuracy_check": True
}

# Scaling Configuration
SCALING_CONFIG = {
    "max_concurrent_agents": 5,
    "agent_pool_size": 10,
    "load_balancing": True,
    "fallback_agents": True
}

def get_config(config_type: str) -> Dict[str, Any]:
    """
    Get configuration by type.
    
    Args:
        config_type: Type of configuration to retrieve
        
    Returns:
        Configuration dictionary
    """
    configs = {
        "llm": LLM_CONFIG,
        "agents": AGENT_CONFIG,
        "tasks": TASK_CONFIG,
        "workflow": WORKFLOW_CONFIG,
        "content_types": CONTENT_TYPES,
        "seo": SEO_CONFIG,
        "qa": QA_CONFIG,
        "scaling": SCALING_CONFIG
    }
    
    return configs.get(config_type, {})

def update_config(config_type: str, updates: Dict[str, Any]) -> None:
    """
    Update configuration values.
    
    Args:
        config_type: Type of configuration to update
        updates: Dictionary of updates to apply
    """
    configs = {
        "llm": LLM_CONFIG,
        "agents": AGENT_CONFIG,
        "tasks": TASK_CONFIG,
        "workflow": WORKFLOW_CONFIG,
        "content_types": CONTENT_TYPES,
        "seo": SEO_CONFIG,
        "qa": QA_CONFIG,
        "scaling": SCALING_CONFIG
    }
    
    if config_type in configs:
        configs[config_type].update(updates)
        print(f"Updated {config_type} configuration")
    else:
        print(f"Unknown configuration type: {config_type}")
