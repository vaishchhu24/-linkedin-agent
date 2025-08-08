# Phase 3: Feedback Loop System

## Overview
The Phase 3 feedback loop system automatically monitors Airtable for client feedback, rewrites posts based on feedback, and prepares data for model fine-tuning.

## Features

### 📥 1. Airtable Monitoring
- **Monitors** Airtable for new feedback on pending posts
- **Filters** for posts where `status == "Pending"` and `feedback != null`
- **Tracks** feedback quality scores (voice_quality, post_quality)

### ✍️ 2. Intelligent Post Revision
- **Uses OpenAI** (GPT-3.5 Turbo or fine-tuned model) to rewrite posts
- **Preserves** core message while addressing specific feedback
- **Maintains** client's tone and style (CAPS, no dashes, natural language)
- **Updates** Airtable with revised version and status

### 📤 3. Client Notification
- **Sends email** notifications when posts are revised
- **Includes** revised post content in beautiful HTML format
- **Asks** for approval with clear call-to-action

### ✅ 4. Fine-tuning Preparation
- **Detects** final approvals (`feedback == "Yes"` or approval keywords)
- **Creates** JSONL training data in correct format
- **Stores** in `/training_data/fine_tune_queue.jsonl`
- **Updates** Airtable with fine-tuning status

## File Structure

```
feedback_handler/
├── feedback_loop.py          # Main feedback loop system
└── __init__.py

training_data/
└── fine_tune_queue.jsonl     # Fine-tuning training data

test_feedback_loop.py         # Comprehensive test suite
```

## Usage

### Running the Complete System
```bash
# Run complete workflow (Phase 1 → 2 → 3)
python3 main.py --mode complete

# Run only feedback loop
python3 main.py --mode feedback --iterations 10 --delay 60

# Run only Phase 3
python3 main.py --mode phase3
```

### Testing the System
```bash
# Run comprehensive tests
python3 test_feedback_loop.py
```

### Manual Feedback Processing
```python
from feedback_handler.feedback_loop import FeedbackLoop

# Initialize system
feedback_loop = FeedbackLoop()

# Monitor for feedback
pending_feedback = feedback_loop.monitor_airtable_for_feedback()

# Process feedback
for feedback_record in pending_feedback:
    feedback_loop.process_feedback(feedback_record)

# Check for approvals
approved_posts = feedback_loop.check_for_final_approval()

# Prepare fine-tuning data
feedback_loop.prepare_fine_tuning_data(approved_posts)
```

## Airtable Schema

### Required Columns
- `post_content` - Original post content
- `feedback` - Client feedback ("Yes", "No", "Regenerate", or custom)
- `voice_quality` - Rating 1-10
- `post_quality` - Rating 1-10
- `timestamp` - When feedback was given
- `status` - "Pending", "Revised", "Approved"

### Generated Columns
- `revised_post` - Revised version based on feedback
- `version` - Version number (2 for revised)
- `revision_timestamp` - When revision was made
- `original_feedback` - Copy of original feedback
- `fine_tune_status` - "Queued" when ready for fine-tuning

## Fine-tuning Data Format

The system creates JSONL files in the correct format for OpenAI fine-tuning:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Write in the voice of [Client Name]."
    },
    {
      "role": "user", 
      "content": "[Original Topic or Input]"
    },
    {
      "role": "assistant",
      "content": "[Final Approved Post Text]"
    }
  ]
}
```

## Email Templates

### Revision Notification
- **Subject**: "Here's the updated version of your LinkedIn post ✨"
- **Content**: Beautiful HTML with revised post and approval CTA
- **CTA**: "Do you approve this version? If yes, we'll publish and fine-tune our model to match it."

## Configuration

### API Keys Required
- **OpenAI API Key** - For post revision generation
- **Airtable API Key** - For monitoring and updating records
- **Resend API Key** - For email notifications

### Settings
- **Monitoring Frequency** - Configurable delay between checks
- **Max Iterations** - Number of monitoring cycles
- **Training Data Directory** - Where JSONL files are stored

## Error Handling

### Robust Error Recovery
- **API Failures** - Graceful handling of OpenAI/Airtable API errors
- **Network Issues** - Retry logic for connectivity problems
- **Invalid Data** - Validation of feedback and post content
- **Missing Records** - Safe handling of non-existent Airtable records

### Logging
- **Comprehensive logging** of all operations
- **Error tracking** with detailed error messages
- **Success metrics** for monitoring system health

## Integration

### With Phase 1 & 2
- **Seamless integration** with email scheduler and content generation
- **Automatic triggering** when posts are generated
- **Data flow** from generation → Airtable → feedback → revision → fine-tuning

### With Main System
```python
from main import LinkedInContentSystem

system = LinkedInContentSystem()

# Run complete workflow including feedback loop
system.run_complete_workflow()

# Run only feedback loop
system.run_feedback_only()
```

## Testing

### Test Coverage
- **Airtable monitoring** - Tests record fetching and filtering
- **Feedback processing** - Tests post revision generation
- **Fine-tuning preparation** - Tests JSONL format and file creation
- **Email notifications** - Tests email sending functionality

### Sample Data
- **Sample posts** for testing revision generation
- **Mock feedback** for testing processing logic
- **Test approvals** for testing fine-tuning preparation

## Future Enhancements

### Planned Features
- **Batch processing** for multiple feedback items
- **Advanced analytics** on feedback patterns
- **Automated fine-tuning** trigger when enough data is collected
- **Feedback categorization** for better revision prompts
- **Client preference learning** for personalized revisions

### Scalability
- **Database optimization** for large numbers of posts
- **Async processing** for better performance
- **Distributed processing** for high-volume scenarios
- **Caching layer** for frequently accessed data

## Troubleshooting

### Common Issues
1. **Airtable Connection** - Check API key and base ID
2. **OpenAI API** - Verify API key and model availability
3. **Email Sending** - Check Resend API key and email configuration
4. **File Permissions** - Ensure write access to training_data directory

### Debug Commands
```bash
# Test Airtable connection
python3 test_airtable_simple.py

# Test OpenAI API
python3 -c "import openai; print('OpenAI working')"

# Test feedback loop
python3 test_feedback_loop.py
```

## Performance

### Optimization
- **Efficient polling** with configurable delays
- **Batch operations** for Airtable updates
- **Caching** of frequently accessed data
- **Connection pooling** for API calls

### Monitoring
- **Response times** for API calls
- **Success rates** for operations
- **Error frequencies** for troubleshooting
- **Data volumes** for capacity planning 