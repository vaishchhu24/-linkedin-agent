
import os

# Get API keys from environment variables (Railway will set these)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', "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")
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', "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")
RESEND_API_KEY = os.getenv('RESEND_API_KEY', "re_htt6wAd9_GpTb4zHbnhLo9JGptdMZxg6q")

# Email settings
EMAIL_SEND_TIME = "10:00"
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', "wmdhhilczgrfozaf")

# Fine-tuned model
FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-1106:personal:linkedintone:By2MD8pX"

# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY', "patep0NA8WJrFnJNF.c456029e73b802f78fa8cb38875e30df9ccd55940e788291dab9691e2185e2e7")
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', "apppflHrhOR5WOgEZ")
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', "Table 1 Copy")

# Production settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

