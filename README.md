# LinkedIn Content Generation System

A comprehensive, AI-powered LinkedIn content generation system that automates the entire workflow from user prompts to final approved posts.

## 🚀 Features

### Phase 1: Email Scheduler & User Response Handling ✅
- **Automated Daily Emails**: Sends prompts at 10:00 AM UK time daily
- **Smart Response Processing**: Extracts and classifies user content using AI
- **Content Classification**: Distinguishes between detailed content and general topics
- **Robust Error Handling**: Comprehensive fallback mechanisms

### Phase 2: Content Assessment & Generation (In Progress)
- **Content Pillar Integration**: Uses predefined HR consulting content categories
- **Perplexity API Research**: Fetches real-time insights from Reddit
- **ICP Alignment**: Ensures content matches target audience needs
- **Natural Content Generation**: Creates authentic, conversational posts

### Phase 3: Feedback & Iteration (Planned)
- **Airtable Integration**: Logs posts for client review
- **Feedback Processing**: Analyzes client feedback using AI
- **Refined Generation**: Creates improved posts based on feedback

### Phase 4: Final Approval & Fine-tuning (Planned)
- **Email Approval System**: Sends final posts for client approval
- **Model Fine-tuning**: Uses approved posts to improve AI output
- **Post Prioritization**: Ranks posts for training data quality

## 📋 Prerequisites

- Python 3.9+
- OpenAI API key
- Resend API key (for email sending)
- Airtable account (for post logging)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd linkedin_agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file in the project root:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
RESEND_API_KEY=your_resend_api_key_here

# Email Configuration
TO_EMAIL=client@example.com
FROM_EMAIL=noreply@yourdomain.com

# Airtable Configuration (for Phase 3)
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE_NAME=your_table_name

# Perplexity API (for Phase 2)
PERPLEXITY_API_KEY=your_perplexity_api_key
```

### 4. Verify Installation
```bash
python3 test_phase1.py
```

## 🚀 Quick Start

### Start the Email Scheduler (Phase 1)
```bash
python3 email_handler/email_scheduler.py
```

This will:
- Start the background scheduler
- Send daily prompts at 10:00 AM UK time
- Process user responses automatically
- Classify content using AI

### Test the System
```bash
# Test Phase 1 functionality
python3 test_phase1.py

# Test content generation
python3 post_generator.py
```

## 📁 Project Structure

```
linkedin_agent/
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── email_config.py              # Email settings
│   ├── airtable_config.py           # Airtable settings
│   ├── perplexity_config.py         # Perplexity API settings
│   └── openai_config.py             # OpenAI settings
├── email_handler/                   # Phase 1: Email management
│   ├── __init__.py
│   ├── email_scheduler.py           # Main scheduler
│   ├── send_prompt.py               # Email sending
│   └── receive_response.py          # Response processing
├── content_handler/                 # Phase 2: Content generation
│   ├── __init__.py
│   ├── content_checker.py           # Content assessment
│   ├── content_generator.py         # Post generation
│   ├── icp_pillar_checker.py        # ICP and pillar management
│   └── insight_fetcher.py           # Perplexity API integration
├── feedback_handler/                # Phase 3: Feedback processing
│   ├── __init__.py
│   ├── airtable_logger.py           # Airtable integration
│   ├── feedback_processor.py        # Feedback analysis
│   └── refined_content_generator.py # Refined post generation
├── approval_handler/                # Phase 4: Approval system
│   ├── __init__.py
│   ├── email_final_post.py          # Final post emails
│   └── approval_processor.py        # Approval processing
├── fine_tuning/                     # Model improvement
│   ├── __init__.py
│   ├── fine_tune_model.py           # Model fine-tuning
│   └── prioritize_posts.py          # Post prioritization
├── data/                            # Data files
│   ├── content_pillars.json         # Content categories
│   ├── icp_profile.json             # Target audience data
│   └── client_voice_analysis.json   # Client communication style
├── trends/                          # Research and insights
│   ├── __init__.py
│   ├── perplexity_fetcher.py        # Perplexity API
│   └── insight_cache.py             # Insight caching
├── main.py                          # Main workflow coordinator
├── post_generator.py                # Legacy post generator
├── requirements.txt                 # Python dependencies
├── test_phase1.py                   # Phase 1 tests
└── README.md                        # This file
```

## 🔧 Configuration

### Email Settings (`config/email_config.py`)
```python
# Schedule time (24-hour format)
SCHEDULE_TIME = "10:00"  # 10:00 AM
SCHEDULE_TIMEZONE = "Europe/London"

# Email template
EMAIL_SUBJECT = "What's your LinkedIn post idea for today? 🚀"
```

### Content Classification Settings
```python
# OpenAI model for classification
CLASSIFICATION_MODEL = "gpt-3.5-turbo"
CLASSIFICATION_MAX_TOKENS = 50
CLASSIFICATION_TEMPERATURE = 0.1
```

## 📊 Usage Examples

### Phase 1: Email Response Processing

**User Response**: "Yes I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months."

**System Classification**: `detailed_content: 0.95`

**User Response**: "Yes recruitment challenges"

**System Classification**: `general_topic: 0.9`

### Content Generation

The system generates posts in the client's authentic voice:
- Raw, honest tone with CAPS for emphasis
- Personal stories with vulnerability
- Specific lessons learned
- Clear mission statements
- 300-600 words of substantial content

## 🔒 Security

- **API Key Management**: All keys stored as environment variables
- **Email Security**: Uses Resend API for secure delivery
- **Content Privacy**: User content processed securely
- **Error Logging**: Comprehensive logging without sensitive data exposure

## 📈 Monitoring

### Logs
The system provides detailed logging for:
- Email sending status
- User response processing
- Content classification results
- Scheduler status
- Error conditions

### Airtable Dashboard (Phase 3)
- Generated posts tracking
- Feedback status
- Approval workflow
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

#### 1. Configuration Errors
```bash
❌ Missing required environment variables: RESEND_API_KEY, TO_EMAIL
```
**Solution**: Ensure all required environment variables are set in `.env`

#### 2. Email Sending Failures
```bash
❌ Error sending email: 401
```
**Solution**: Verify Resend API key and email addresses

#### 3. OpenAI API Issues
```bash
❌ Error classifying content: Invalid API key
```
**Solution**: Check OpenAI API key and quota

#### 4. Import Errors
```bash
ModuleNotFoundError: No module named 'email_handler'
```
**Solution**: Ensure you're running from the project root directory

### Debug Mode
Enable detailed logging by modifying logging levels in the respective modules.

## 🔄 Development Workflow

### Adding New Features
1. Create feature branch
2. Implement in appropriate phase module
3. Add tests
4. Update documentation
5. Submit pull request

### Testing
```bash
# Run all tests
python3 test_phase1.py

# Test specific functionality
python3 -m pytest tests/
```

## 📚 API Reference

### EmailScheduler
```python
from email_handler.email_scheduler import EmailScheduler

scheduler = EmailScheduler()
scheduler.start_scheduler()
scheduler.process_user_response("Yes recruitment challenges")
```

### ContentGenerator
```python
from content_handler.content_generator import ContentGenerator

generator = ContentGenerator()
post = generator.generate_from_pillars()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

## 🗺️ Roadmap

### Phase 2: Content Assessment & Generation
- [ ] Complete content pillar integration
- [ ] Implement Perplexity API research
- [ ] Add ICP alignment
- [ ] Enhance natural content generation

### Phase 3: Feedback & Iteration
- [ ] Airtable integration
- [ ] Feedback processing
- [ ] Refined content generation

### Phase 4: Final Approval & Fine-tuning
- [ ] Email approval system
- [ ] Model fine-tuning
- [ ] Post prioritization

---

**Status**: Phase 1 Complete ✅ | Phase 2 In Progress 🔄 | Phase 3-4 Planned 📋 