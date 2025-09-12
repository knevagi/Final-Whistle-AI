#!/usr/bin/env python3
"""
Configuration settings for Football Focus API
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # API settings
    API_TITLE = 'Football Focus API'
    API_VERSION = '1.0.0'
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Cache settings
    CACHE_TIMEOUT = 3600  # 60 minutes
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate required configuration"""
        missing = {}
        
        if not cls.SUPABASE_URL:
            missing['SUPABASE_URL'] = 'Required for database connection'
        
        if not cls.SUPABASE_KEY:
            missing['SUPABASE_KEY'] = 'Required for database authentication'
        
        return missing

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
