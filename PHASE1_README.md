# Phase 1: Email Scheduler and User Response Handling

## Overview

Phase 1 implements the automated email scheduling and user response processing system for the LinkedIn content generation workflow. This module handles:

- **Automated Daily Emails**: Sends prompts at 10:00 AM UK time daily
- **User Response Processing**: Extracts and classifies user content
- **Content Classification**: Uses OpenAI GPT-3.5 Turbo to categorize responses
- **Robust Error Handling**: Comprehensive error handling for all operations

## Features

### 🕐 Email Scheduler
- **APScheduler Integration**: Uses APScheduler for reliable background scheduling
- **UK Timezone**: Configured for 10:00 AM UK time (configurable)
- **Automated Daily Prompts**: Sends the specified email template daily
- **Manual Trigger**: Support for manual email sending (testing)

### 📧 Email Template
The system sends this friendly email daily:

```
Subject: What's your LinkedIn post idea for today? 🚀

Hey! 👋

What's on your mind for your LinkedIn post today?

Do you have a specific topic or experience you'd like to share?

Just reply with:

- "Yes" + your topic/experience
- "No" and we'll handle it

Looking forward to creating something amazing for you!

Best regards,  
Your LinkedIn Content Team
```

### 🤖 User Response Handling
- **Yes/No Detection**: Automatically detects user intent
- **Content Extraction**: Extracts content after "Yes" responses
- **Content Classification**: Uses AI to classify content into:
  - `detailed_content`: Personal experience, recent story, specific incident
  - `general_topic`: General topic idea, broad subject, concept

### 🔧 Configuration
- **Environment Variables**: Secure configuration via environment variables
- **Modular Settings**: Centralized configuration management
- **Validation**: Automatic configuration validation on startup

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with:
```bash
RESEND_API_KEY=your_resend_api_key
TO_EMAIL=client@example.com
OPENAI_API_KEY=your_openai_api_key
FROM_EMAIL=noreply@yourdomain.com  # Optional
```

### 3. Required Environment Variables
- `RESEND_API_KEY`: Your Resend API key for email sending
- `TO_EMAIL`: The email address to send prompts to
- `OPENAI_API_KEY`: Your OpenAI API key for content classification
- `FROM_EMAIL`: Sender email (optional, defaults to noreply@yourdomain.com)

## Usage

### Start the Email Scheduler
```bash
python3 email_handler/email_scheduler.py
```

### Test the System
```bash
python3 test_phase1.py
```

### Manual Email Trigger
```python
from email_handler.email_scheduler import EmailScheduler

scheduler = EmailScheduler()
scheduler.manual_send_prompt()
```

## API Reference

### EmailScheduler Class

#### Methods

##### `start_scheduler()`
Starts the background scheduler with daily email at 10:00 AM UK time.

##### `stop_scheduler()`
Stops the background scheduler.

##### `send_daily_prompt()`
Sends the daily LinkedIn post prompt email.

##### `process_user_response(email_content: str) -> Dict`
Processes user's email response and classifies content.

**Returns:**
```python
{
    "has_content": bool,
    "content_type": str,  # "detailed_content", "general_topic", "declined", etc.
    "extracted_content": str,
    "confidence": float,  # Only for classified content
    "message": str
}
```

##### `get_scheduler_status() -> Dict`
Gets current scheduler status and job information.

##### `manual_send_prompt()`
Manually triggers the daily prompt (for testing).

### Configuration Classes

#### EmailSettings
- `RESEND_API_KEY`: Resend API key
- `FROM_EMAIL`: Sender email address
- `TO_EMAIL`: Recipient email address
- `SCHEDULE_TIME`: Daily schedule time (default: "10:00")
- `SCHEDULE_TIMEZONE`: Timezone (default: "Europe/London")
- `EMAIL_SUBJECT`: Email subject line
- `EMAIL_BODY`: Email body template

#### ContentClassificationSettings
- `CLASSIFICATION_MODEL`: OpenAI model (default: "gpt-3.5-turbo")
- `CLASSIFICATION_MAX_TOKENS`: Max tokens for classification
- `CLASSIFICATION_TEMPERATURE`: Temperature for classification
- `DETAILED_CONTENT`: Category for detailed content
- `GENERAL_TOPIC`: Category for general topics
- `DETAILED_KEYWORDS`: Keywords for fallback classification
- `MIN_DETAILED_LENGTH`: Minimum length for detailed classification

#### ResponseProcessingSettings
- `RESPONSE_YES`: "Yes" response identifier
- `RESPONSE_NO`: "No" response identifier
- `RESPONSE_DECLINED`: Declined response type
- `RESPONSE_UNCLEAR`: Unclear response type
- `RESPONSE_EMPTY`: Empty response type
- `RESPONSE_ERROR`: Error response type
- `YES_PREFIX_LENGTH`: Length of "Yes" prefix to remove

## Content Classification Examples

### Detailed Content (Personal Experience)
```
Input: "Yes I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months."

Classification: detailed_content:0.9
```

### General Topic
```
Input: "Yes recruitment challenges"

Classification: general_topic:0.8
```

### Declined Response
```
Input: "No"

Classification: declined
```

## Error Handling

The system includes comprehensive error handling for:

- **Email Sending Failures**: Graceful handling of email delivery issues
- **API Failures**: Fallback mechanisms for OpenAI API issues
- **Configuration Errors**: Clear error messages for missing environment variables
- **Scheduler Issues**: Robust scheduler management with error recovery
- **Content Processing**: Fallback classification when AI classification fails

## Testing

Run the comprehensive test suite:
```bash
python3 test_phase1.py
```

The test suite covers:
- Configuration validation
- Content classification with various inputs
- Scheduler status checking
- Error handling scenarios

## Integration

This Phase 1 module is designed to integrate seamlessly with the complete LinkedIn content generation workflow:

- **Phase 2**: Content assessment and generation based on classified responses
- **Phase 3**: Feedback and iteration using processed content
- **Phase 4**: Final approval and model fine-tuning

## Security

- **API Key Management**: All API keys stored as environment variables
- **Email Security**: Uses Resend API for secure email delivery
- **Content Privacy**: User content processed securely with OpenAI API
- **Error Logging**: Comprehensive logging without exposing sensitive data

## Monitoring

The system provides detailed logging for monitoring:
- Email sending status
- User response processing
- Content classification results
- Scheduler status
- Error conditions

## Troubleshooting

### Common Issues

1. **Configuration Errors**
   - Ensure all required environment variables are set
   - Check API key validity

2. **Email Sending Failures**
   - Verify Resend API key
   - Check email addresses are valid

3. **Content Classification Issues**
   - Verify OpenAI API key
   - Check API quota and limits

4. **Scheduler Issues**
   - Ensure system time is correct
   - Check timezone settings

### Debug Mode
Enable debug logging by modifying the logging level in the email scheduler.

## Next Steps

After implementing Phase 1, proceed to:
- **Phase 2**: Content assessment and generation
- **Phase 3**: Feedback and iteration
- **Phase 4**: Final approval and fine-tuning

This modular approach ensures each phase can be developed and tested independently while maintaining full integration capabilities. 