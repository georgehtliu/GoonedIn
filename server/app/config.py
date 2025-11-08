"""
GoonedIn Backend - Configuration
Handles environment variables and app configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Perplexity API
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Data storage
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # Matching configuration
    MAX_MATCHES_PER_REQUEST = 20


