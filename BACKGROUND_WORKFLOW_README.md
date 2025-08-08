# LinkedIn Background Workflow System

A complete automated LinkedIn content system that runs in the background and sends **3 daily emails at 1-hour intervals**.

## 🚀 Features

- **📧 Automated Email Sending**: Sends 3 emails daily at 9 AM, 10 AM, and 11 AM UK time
- **🔄 Continuous Monitoring**: Monitors for email replies 24/7
- **🧠 AI Content Generation**: Creates LinkedIn posts using advanced AI
- **📚 RAG Learning**: Learns from feedback using Retrieval-Augmented Generation
- **🔄 Feedback Processing**: Automatically processes client feedback
- **🛡️ Background Operation**: Runs continuously in the background
- **📊 Comprehensive Logging**: Detailed logs for monitoring and debugging

## 📧 Email Schedule

The system sends 3 emails daily at these times (UK timezone):

| Email | Time | Purpose |
|-------|------|---------|
| Email 1 | 9:00 AM | Morning prompt |
| Email 2 | 10:00 AM | Mid-morning prompt |
| Email 3 | 11:00 AM | Late morning prompt |

## 🛠️ Installation & Setup

### Prerequisites

1. Python 3.8+ installed
2. All required dependencies from `requirements.txt`
3. Proper configuration in `config.py`

### Quick Start

1. **Start the background workflow:**
   ```bash
   ./manage_background_workflow.sh start
   ```

2. **Check status:**
   ```bash
   ./manage_background_workflow.sh status
   ```

3. **View live logs:**
   ```bash
   ./manage_background_workflow.sh logs
   ```

## 📋 Management Commands

### Using the Management Script

```bash
# Start the background workflow
./manage_background_workflow.sh start

# Stop the background workflow
./manage_background_workflow.sh stop

# Restart the background workflow
./manage_background_workflow.sh restart

# Check current status
./manage_background_workflow.sh status

# View live logs
./manage_background_workflow.sh logs

# Show help
./manage_background_workflow.sh help
```

### Using Python Directly

```bash
# Start the system
python3 background_workflow_system.py start

# Stop the system
python3 background_workflow_system.py stop

# Check status
python3 background_workflow_system.py status

# Restart the system
python3 background_workflow_system.py restart
```

## 🔧 System Architecture

### Background Workflow System (`background_workflow_system.py`)

The main background system that:

1. **Initializes Components**: Sets up email scheduler, integrated system, and logging
2. **Manages Process**: Handles PID files, signal handling, and graceful shutdown
3. **Runs Continuous Loop**: Executes the 3-phase workflow every 5 minutes
4. **Provides Status**: Offers comprehensive system status and monitoring

### Email Scheduler (`email_handler/email_scheduler.py`)

Enhanced to support multiple daily emails:

- **Multiple Schedule Times**: Configurable times for 3 daily emails
- **APScheduler Integration**: Uses APScheduler for reliable scheduling
- **Background Operation**: Runs independently of the main workflow
- **Status Monitoring**: Provides detailed scheduler status

### Integrated System (`final_integrated_system.py`)

The core workflow with 3 phases:

1. **Phase 1**: Email Monitoring - Detects client replies
2. **Phase 2**: Content Generation - Creates LinkedIn posts with RAG
3. **Phase 3**: Feedback Processing - Handles client feedback & learning

## 📁 File Structure

```
linkedin_agent/
├── background_workflow_system.py          # Main background system
├── manage_background_workflow.sh          # Management script
├── linkedin-background-workflow.service   # Systemd service file
├── background_workflow.log                # Background system logs
├── background_workflow.pid                # Process ID file
├── config/
│   └── email_config.py                    # Email configuration
├── email_handler/
│   └── email_scheduler.py                 # Enhanced email scheduler
└── final_integrated_system.py             # Core workflow system
```

## 🔍 Monitoring & Logging

### Log Files

- **`background_workflow.log`**: Main background system logs
- **`linkedin_system.log`**: Integrated system logs
- **`automated_workflow.log`**: Legacy workflow logs

### Status Monitoring

```bash
# Check if system is running
./manage_background_workflow.sh status

# View recent logs
tail -n 20 background_workflow.log

# Monitor live logs
./manage_background_workflow.sh logs
```

### System Status Information

The system provides detailed status including:

- Process ID and running status
- Email scheduler status
- Recent activity logs
- Email schedule information
- RAG store statistics
- Airtable record counts

## ⚙️ Configuration

### Email Schedule Configuration

Edit `config/email_config.py` to modify email times:

```python
# Scheduler Configuration - 3 emails daily at 1-hour intervals
SCHEDULE_TIMES = ["09:00", "10:00", "11:00"]  # 9 AM, 10 AM, 11 AM
SCHEDULE_TIMEZONE = "Europe/London"  # UK timezone
```

### System Configuration

Key configuration files:

- **`config.py`**: API keys and main configuration
- **`config/email_config.py`**: Email-specific settings
- **`data/content_pillars.json`**: Content topics and pillars

## 🚨 Troubleshooting

### Common Issues

1. **System won't start:**
   ```bash
   # Check if already running
   ./manage_background_workflow.sh status
   
   # Check logs for errors
   tail -n 50 background_workflow.log
   ```

2. **Emails not being sent:**
   ```bash
   # Check email scheduler status
   python3 background_workflow_system.py status
   
   # Verify configuration
   python3 -c "from config.email_config import EmailSettings; print(EmailSettings.validate_config())"
   ```

3. **Process stuck:**
   ```bash
   # Force stop and restart
   ./manage_background_workflow.sh stop
   sleep 5
   ./manage_background_workflow.sh start
   ```

### Debug Mode

For debugging, you can run the system in foreground mode:

```bash
python3 background_workflow_system.py start
```

This will show all logs in the terminal instead of writing to log files.

## 🔄 Workflow Process

### Daily Email Cycle

1. **9:00 AM**: First email sent to client
2. **10:00 AM**: Second email sent to client  
3. **11:00 AM**: Third email sent to client
4. **Continuous**: System monitors for replies every 5 minutes

### Content Generation Process

1. **Email Detection**: System detects client email replies
2. **Content Analysis**: Analyzes content detail level and topic
3. **Research**: Fetches insights using Perplexity API (if needed)
4. **Generation**: Creates LinkedIn post using AI
5. **Logging**: Saves post to Airtable
6. **Learning**: Updates RAG store for future learning

### Feedback Processing

1. **Feedback Detection**: Monitors for client feedback
2. **Analysis**: Processes feedback sentiment and suggestions
3. **Learning**: Updates RAG store with feedback insights
4. **Improvement**: Uses feedback to improve future content

## 📊 Performance Metrics

The system tracks various metrics:

- **Email Processing**: Number of emails processed
- **Content Generation**: Posts created and success rate
- **Feedback Processing**: Feedback items processed
- **RAG Learning**: Knowledge base updates
- **System Uptime**: Continuous operation time

## 🔒 Security & Reliability

### Process Management

- **PID File Tracking**: Prevents multiple instances
- **Graceful Shutdown**: Handles signals properly
- **Auto-restart**: Systemd service can auto-restart on failure
- **Log Rotation**: Comprehensive logging for debugging

### Data Protection

- **API Key Security**: Keys stored in config.py (not in logs)
- **Email Privacy**: Email content processed securely
- **Backup Systems**: RAG store and Airtable provide data backup

## 🎯 Use Cases

### For HR Consultants

- **Automated Content**: Generate LinkedIn posts from client experiences
- **Consistent Posting**: Maintain regular posting schedule
- **Quality Content**: AI-powered content with human-like tone
- **Feedback Learning**: Continuously improve based on client feedback

### For Content Managers

- **Scalable System**: Handle multiple clients with same system
- **Quality Control**: Built-in content assessment and feedback processing
- **Analytics**: Track performance and engagement
- **Automation**: Reduce manual content creation workload

## 🚀 Future Enhancements

Potential improvements:

- **Multi-client Support**: Handle multiple clients simultaneously
- **Advanced Analytics**: Detailed performance metrics and insights
- **Content Calendar**: Advanced scheduling and content planning
- **Integration APIs**: Connect with other marketing tools
- **Mobile App**: Mobile interface for monitoring and control

## 📞 Support

For issues or questions:

1. Check the logs: `./manage_background_workflow.sh logs`
2. Review this documentation
3. Check system status: `./manage_background_workflow.sh status`
4. Restart if needed: `./manage_background_workflow.sh restart`

---

**🎉 Your LinkedIn content system is now running in the background with 3 daily emails at 1-hour intervals!** 