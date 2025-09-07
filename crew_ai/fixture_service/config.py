#!/usr/bin/env python3
"""
Configuration for the English Football Fixture Service
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FixtureServiceConfig:
    """Configuration class for the fixture service"""
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')  # Project URL: https://your-project.supabase.co
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # Anon/public key
    
    # API configuration
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
    API_FOOTBALL_BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    # OpenAI configuration (for crew AI)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # Serper API configuration (for search)
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')
    
    # Service intervals (in seconds)
    SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '3600'))  # 1 hour
    PROCESSING_INTERVAL = int(os.getenv('PROCESSING_INTERVAL', '300'))  # 5 minutes
    
    # Competition settings
    DEFAULT_COMPETITION = os.getenv('DEFAULT_COMPETITION', 'Premier League')
    DEFAULT_SEASON = int(os.getenv('DEFAULT_SEASON', '2025'))
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'fixture_service.log')
    
    # Article generation settings
    DEFAULT_ARTICLE_LENGTH = os.getenv('DEFAULT_ARTICLE_LENGTH', '800-1200 words')
    DAYS_BACK_FOR_ARTICLES = int(os.getenv('DAYS_BACK_FOR_ARTICLES', '1'))
    
    # Processing settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '60'))  # seconds
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        Validate the configuration and return any missing required values
        
        Returns:
            Dictionary of missing required configuration values
        """
        missing_config = {}
        
        # Required configuration
        if not cls.SUPABASE_URL:
            missing_config['SUPABASE_URL'] = 'Required for database connection'
        
        if not cls.OPENAI_API_KEY:
            missing_config['OPENAI_API_KEY'] = 'Required for crew AI functionality'
        
        if not cls.SERPER_API_KEY:
            missing_config['SERPER_API_KEY'] = 'Required for search functionality'
        
        # Optional but recommended
        if not cls.API_FOOTBALL_KEY:
            missing_config['API_FOOTBALL_KEY'] = 'Optional: Will use mock data if not provided'
        
        return missing_config
    
    @classmethod
    def get_supabase_config(cls) -> tuple:
        """Get Supabase configuration for client initialization"""
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required but not set")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required but not set")
        
        return cls.SUPABASE_URL, cls.SUPABASE_KEY
    
    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration"""
        print("=" * 50)
        print("Fixture Service Configuration Summary")
        print("=" * 50)
        
        print(f"Database URL: {'✅ Set' if cls.SUPABASE_URL else '❌ Missing'}")
        print(f"OpenAI API Key: {'✅ Set' if cls.OPENAI_API_KEY else '❌ Missing'}")
        print(f"Serper API Key: {'✅ Set' if cls.SERPER_API_KEY else '❌ Missing'}")
        print(f"API Football Key: {'✅ Set' if cls.API_FOOTBALL_KEY else '⚠️  Using mock data'}")
        
        print(f"\nService Settings:")
        print(f"  Sync Interval: {cls.SYNC_INTERVAL} seconds ({cls.SYNC_INTERVAL/3600:.1f} hours)")
        print(f"  Processing Interval: {cls.PROCESSING_INTERVAL} seconds ({cls.PROCESSING_INTERVAL/60:.1f} minutes)")
        print(f"  Default Competition: {cls.DEFAULT_COMPETITION}")
        print(f"  Default Season: {cls.DEFAULT_SEASON}")
        print(f"  Article Length: {cls.DEFAULT_ARTICLE_LENGTH}")
        print(f"  Days Back for Articles: {cls.DAYS_BACK_FOR_ARTICLES}")
        
        print(f"\nLogging:")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Log File: {cls.LOG_FILE}")
        
        # Check for missing required configuration
        missing = cls.validate_config()
        if missing:
            print(f"\n⚠️  Missing Required Configuration:")
            for key, description in missing.items():
                print(f"  - {key}: {description}")
        else:
            print(f"\n✅ All required configuration is set")
        
        print("=" * 50)

# Default configuration instance
config = FixtureServiceConfig()
