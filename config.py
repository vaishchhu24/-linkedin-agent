
import os

# Get API keys from environment variables (Railway will set these)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

# Email settings
EMAIL_SEND_TIME = "10:00"
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Fine-tuned model
FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-1106:personal:linkedintone:By2MD8pX"

# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

# Production settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

