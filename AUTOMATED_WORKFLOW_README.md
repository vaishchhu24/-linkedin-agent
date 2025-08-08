# 🤖 Automated LinkedIn Content Workflow

This system automatically sends daily prompt emails at **10 AM UK time** and processes replies immediately to generate LinkedIn posts.

## 🚀 Quick Start

### Option 1: Using the Startup Script (Recommended)
```bash
./start_automated_workflow.sh
```

### Option 2: Direct Python Command
```bash
python3 automated_workflow.py
```

## 📋 How It Works

### 1. **Daily Email Sending (10 AM UK Time)**
- ✅ Automatically sends prompt emails to Sam at 10:00 AM UK time
- ✅ Uses Gmail SMTP for reliable delivery
- ✅ Email subject: "What's on your mind for your LinkedIn post today?"

### 2. **Continuous Reply Monitoring**
- ✅ Monitors for Sam's replies every 2 minutes
- ✅ Only processes LinkedIn-related replies
- ✅ Ignores other emails automatically

### 3. **Immediate Workflow Processing**
- ✅ As soon as Sam replies, the integrated workflow starts
- ✅ Generates LinkedIn posts using AI
- ✅ Logs posts to Airtable
- ✅ Processes any existing feedback

## 🛠️ Available Commands

### Start Full Automated Workflow
```bash
python3 automated_workflow.py
```

### Send Manual Prompt Email (Testing)
```bash
python3 automated_workflow.py --manual-prompt
```

### Demo Mode (No Actual Emails)
```bash
python3 automated_workflow.py --demo
```

## 📧 Email Flow

```
10:00 AM UK Time → Send Prompt Email to Sam
                    ↓
              Sam receives email
                    ↓
              Sam replies with topic
                    ↓
           System detects reply (within 2 min)
                    ↓
           Integrated workflow starts immediately
                    ↓
           Generate LinkedIn post + Log to Airtable
```

## ⚙️ Configuration

### Email Settings (config/email_config.py)
- **Schedule Time**: `10:00` (10 AM)
- **Timezone**: `Europe/London` (UK time)
- **Client Email**: `vaishnavisingh24011@gmail.com`
- **System Email**: `vaishchhu24@gmail.com`

### Monitoring Settings
- **Reply Check Interval**: Every 2 minutes
- **Email Filtering**: Only LinkedIn replies
- **Processing**: Immediate workflow start

## 📊 System Features

### ✅ **Automated Email Sending**
- Daily prompts at 10 AM UK time
- Gmail SMTP integration
- HTML email templates

### ✅ **Smart Reply Detection**
- Filters only LinkedIn replies
- Prevents duplicate processing
- Timestamp-based tracking

### ✅ **Integrated Workflow**
- Content generation with AI
- RAG-enhanced learning
- Airtable logging
- Feedback processing

### ✅ **Error Handling**
- Automatic retry on failures
- Comprehensive logging
- Graceful shutdown

## 🔧 Troubleshooting

### Email Not Sending
1. Check Gmail credentials in `config.py`
2. Verify email password is correct
3. Check internet connection

### Replies Not Detected
1. Ensure email filtering is working
2. Check IMAP settings
3. Verify client email address

### Workflow Not Starting
1. Check system logs in `automated_workflow.log`
2. Verify all dependencies are installed
3. Ensure config files are properly set

## 📝 Log Files

- **Main Log**: `automated_workflow.log`
- **Console Output**: Real-time status updates
- **Error Tracking**: Detailed error messages

## 🛑 Stopping the System

Press `Ctrl+C` to gracefully stop the automated workflow.

## 🎯 Production Deployment

### For 24/7 Operation
1. Use a cloud server (AWS, DigitalOcean, etc.)
2. Set up as a system service
3. Configure automatic restarts
4. Monitor logs for issues

### Example Systemd Service
```ini
[Unit]
Description=LinkedIn Content Workflow
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/linkedin_agent
ExecStart=/usr/bin/python3 automated_workflow.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📞 Support

If you encounter issues:
1. Check the log files
2. Verify configuration settings
3. Test individual components
4. Review error messages

---

**🎉 Your automated LinkedIn content system is ready to run 24/7!** 