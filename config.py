
import os
from typing import Optional

class Config:
    """Application configuration"""

    # Google AI API Configuration
    GOOGLE_AI_API_KEY = "AIzaSyB-eQdOarmEG7xoH3c5p8ottrXdD-I1DVY"
    GOOGLE_AI_MODEL = "gemini-1.5-flash"
    GOOGLE_AI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fanfocus-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

    # Session Settings
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'

    # Fan Profile Settings
    MAX_CHAT_HISTORY = 50  # Maximum number of chat messages to store per fan
    KYC_PHASE0_STEPS = 9
    KYC_PHASE1_THRESHOLD = 70  # Percentage completion needed to activate Phase 1

    # Response Settings
    MAX_RESPONSE_LENGTH = 250
    DEFAULT_CONFIDENCE_LEVEL = "LOW"

    # UI Settings
    CREATOR_MODELS = {
        "ella": "Ella Blair",
        "vanp": "Vanp",
        "yana": "Yana Sinner", 
        "venessa": "Venessa"
    }

    # S&S Framework Settings
    FAN_TYPES = {
        "BS": "Big Spender",
        "BO": "Occasional Buyer", 
        "FT": "Free Trial",
        "TW": "Time Waster",
        "LK": "Lurker"
    }

    CONFIDENCE_LEVELS = ["LOW", "MED", "HIGH"]

    PERSONALITY_TYPES = [
        "ROMANTIC DREAMER",
        "SHY SUB", 
        "BANTER BUDDY",
        "HIGH-ROLLER",
        "PRAISE-SEEKER",
        "COLLECTOR",
        "SHOCK-CHASER"
    ]

    # AI Settings
    TEMPERATURE = 0.7
    MAX_TOKENS = 300
    TOP_P = 0.9

    @classmethod
    def get_google_ai_url(cls) -> str:
        """Get the complete Google AI API URL"""
        return cls.GOOGLE_AI_ENDPOINT.format(model=cls.GOOGLE_AI_MODEL)

    @classmethod
    def get_headers(cls) -> dict:
        """Get headers for Google AI API requests"""
        return {
            'Content-Type': 'application/json',
            'x-goog-api-key': cls.GOOGLE_AI_API_KEY
        }

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')

# Configuration selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
