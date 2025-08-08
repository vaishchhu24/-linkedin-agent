#!/usr/bin/env python3
"""
Email Configuration Settings
Centralized configuration for email settings, OpenAI API keys, and scheduler parameters
"""

import os
import sys
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main config.py file (not the config package)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py"))
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    OPENAI_API_KEY = config_module.OPENAI_API_KEY
    RESEND_API_KEY = config_module.RESEND_API_KEY
    PERPLEXITY_API_KEY = config_module.PERPLEXITY_API_KEY
    FINE_TUNED_MODEL = config_module.FINE_TUNED_MODEL
    AIRTABLE_API_KEY = config_module.AIRTABLE_API_KEY
    AIRTABLE_BASE_ID = config_module.AIRTABLE_BASE_ID
    AIRTABLE_TABLE_NAME = config_module.AIRTABLE_TABLE_NAME
except ImportError:
    # Fallback to environment variables if config.py not available
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    FINE_TUNED_MODEL = os.getenv('FINE_TUNED_MODEL')
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

class EmailSettings:
    """Email configuration settings."""
    
    # Resend API Configuration
    RESEND_API_KEY = RESEND_API_KEY
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'vaishchhu24@gmail.com')  # System operator
    TO_EMAIL = os.getenv('TO_EMAIL', 'vaishnavisingh24011@gmail.com')  # Sam Eaton's client email
    
    # Client Information
    CLIENT_NAME = "Sam Eaton"
    
    # Client Email
    TO_EMAIL = os.getenv('TO_EMAIL', 'vaishnavisingh24011@gmail.com')  # Updated client email
    
    # Email Password for IMAP
    EMAIL_PASSWORD = config_module.EMAIL_PASSWORD if hasattr(config_module, 'EMAIL_PASSWORD') else os.getenv('EMAIL_PASSWORD')
    
    # OpenAI Configuration
    OPENAI_API_KEY = OPENAI_API_KEY
    
    # Fine-tuned Model
    FINE_TUNED_MODEL_ID = FINE_TUNED_MODEL
    
    # Airtable Configuration
    AIRTABLE_API_KEY = AIRTABLE_API_KEY
    AIRTABLE_BASE_ID = AIRTABLE_BASE_ID
    AIRTABLE_TABLE_NAME = AIRTABLE_TABLE_NAME
    
    # Perplexity Configuration
    PERPLEXITY_API_KEY = PERPLEXITY_API_KEY
    
    # Scheduler Configuration - 3 emails daily at 1-hour intervals
    # First email at 9 AM, second at 10 AM, third at 11 AM UK Time
    SCHEDULE_TIMES = ["09:00", "10:00", "11:00"]  # 9 AM, 10 AM, 11 AM
    SCHEDULE_TIMEZONE = "Europe/London"  # UK timezone
    
    # Legacy single time (kept for backward compatibility)
    SCHEDULE_TIME = "10:00"  # 10:00 AM
    
    # Email Template
    EMAIL_SUBJECT = "What's on your mind for your LinkedIn post today?"
    EMAIL_BODY = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Hey Sam! 👋</h2>
        <p>What's on your mind for your LinkedIn post today?</p>
        <p>Do you have a specific topic or experience you'd like to share?</p>
        <p>Just reply with:</p>
        <ul>
            <li><strong>"Yes"</strong> + your topic/experience</li>
            <li><strong>"No"</strong> and we'll handle it</li>
        </ul>
        <p>Looking forward to creating something amazing for you!</p>
        <p>Best regards,<br>Your LinkedIn Content Team</p>
    </div>
    """
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        required_keys = [
            cls.RESEND_API_KEY,
            cls.OPENAI_API_KEY,
            cls.FINE_TUNED_MODEL_ID,
            cls.AIRTABLE_API_KEY,
            cls.AIRTABLE_BASE_ID,
            cls.AIRTABLE_TABLE_NAME
        ]
        
        missing_keys = [key for key in required_keys if not key]
        
        if missing_keys:
            print(f"❌ Missing required configuration: {missing_keys}")
            return False
        
        return True

class ContentClassificationSettings:
    """Content classification settings."""
    
    # OpenAI Model for Classification
    CLASSIFICATION_MODEL = "gpt-3.5-turbo"
    CLASSIFICATION_MAX_TOKENS = 50
    CLASSIFICATION_TEMPERATURE = 0.1
    
    # Content Types
    DETAILED_CONTENT = "detailed_content"
    GENERAL_TOPIC = "general_topic"
    
    # Minimum length for detailed content
    MIN_DETAILED_LENGTH = 100
    
    # Keywords that suggest detailed content
    DETAILED_KEYWORDS = [
        "client", "story", "experience", "helped", "worked with",
        "result", "outcome", "achieved", "success", "transformation"
    ]

class ResponseProcessingSettings:
    """Response processing settings."""
    
    # Response types
    RESPONSE_YES = "yes"
    RESPONSE_NO = "no"
    RESPONSE_EMPTY = "empty"
    RESPONSE_DECLINED = "declined"
    RESPONSE_UNCLEAR = "unclear"
    RESPONSE_ERROR = "error"
    
    # Prefix length for "Yes" responses
    YES_PREFIX_LENGTH = 3
    
    # Email cleaning patterns
    EMAIL_QUOTE_PATTERNS = [
        ">",
        "On ",
        "From:",
        "Sent:",
        "To:",
        "Subject:",
        "---",
        "___"
    ] 