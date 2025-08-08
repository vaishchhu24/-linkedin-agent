# Production Deployment Guide

## 🚀 Production Setup

This guide walks you through deploying the LinkedIn Content Generation System in production.

## 📋 Pre-Deployment Checklist

- [ ] Python 3.9+ installed on server
- [ ] All API keys obtained and tested
- [ ] Email domain configured with Resend
- [ ] Airtable workspace set up (for Phase 3)
- [ ] Server with 24/7 uptime capability

## 🛠️ Server Setup

### 1. Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 10GB+ available space
- **Network**: Stable internet connection

### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git supervisor nginx -y
```

### 3. Clone and Setup Project
```bash
# Clone repository
git clone <repository-url>
cd linkedin_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## 🔧 Environment Configuration

### 1. Create Production Environment File
```bash
# Create .env file
cp .env.example .env
nano .env
```

### 2. Configure Environment Variables
```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
RESEND_API_KEY=re-your-resend-key-here

# Email Configuration
TO_EMAIL=client@example.com
FROM_EMAIL=noreply@yourdomain.com

# Airtable Configuration (Phase 3)
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE_NAME=your_table_name

# Perplexity API (Phase 2)
PERPLEXITY_API_KEY=your_perplexity_api_key

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3. Test Configuration
```bash
# Test Phase 1
python3 test_phase1.py

# Test email sending
python3 -c "
from email_handler.email_scheduler import EmailScheduler
scheduler = EmailScheduler()
scheduler.manual_send_prompt()
"
```

## 🚀 Production Deployment

### 1. Supervisor Configuration
Create supervisor configuration for process management:

```bash
sudo nano /etc/supervisor/conf.d/linkedin-agent.conf
```

Add the following configuration:
```ini
[program:linkedin-agent]
command=/path/to/linkedin_agent/venv/bin/python /path/to/linkedin_agent/email_handler/email_scheduler.py
directory=/path/to/linkedin_agent
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/linkedin-agent.err.log
stdout_logfile=/var/log/linkedin-agent.out.log
environment=PYTHONPATH="/path/to/linkedin_agent"
```

### 2. Start Supervisor
```bash
# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start the service
sudo supervisorctl start linkedin-agent

# Check status
sudo supervisorctl status linkedin-agent
```

### 3. Nginx Configuration (Optional)
If you need web interface or API endpoints:

```bash
sudo nano /etc/nginx/sites-available/linkedin-agent
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/linkedin-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoring & Logging

### 1. Log Management
```bash
# View logs
sudo tail -f /var/log/linkedin-agent.out.log
sudo tail -f /var/log/linkedin-agent.err.log

# Log rotation
sudo nano /etc/logrotate.d/linkedin-agent
```

Add log rotation configuration:
```
/var/log/linkedin-agent.*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 2. Health Checks
Create a health check script:

```bash
nano /path/to/linkedin_agent/health_check.py
```

```python
#!/usr/bin/env python3
import requests
import sys
from email_handler.email_scheduler import EmailScheduler

def health_check():
    try:
        scheduler = EmailScheduler()
        status = scheduler.get_scheduler_status()
        
        if status['scheduler_running']:
            print("✅ Scheduler is running")
            return 0
        else:
            print("❌ Scheduler is not running")
            return 1
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(health_check())
```

### 3. Cron Job for Health Checks
```bash
# Add to crontab
crontab -e

# Add this line to check every 5 minutes
*/5 * * * * /path/to/linkedin_agent/venv/bin/python /path/to/linkedin_agent/health_check.py
```

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. File Permissions
```bash
# Set proper permissions
sudo chown -R www-data:www-data /path/to/linkedin_agent
sudo chmod 600 /path/to/linkedin_agent/.env
sudo chmod 755 /path/to/linkedin_agent
```

### 3. SSL Certificate (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## 🔄 Backup Strategy

### 1. Database Backup (Airtable)
- Airtable provides automatic backups
- Export data monthly for additional safety

### 2. Configuration Backup
```bash
# Create backup script
nano /path/to/linkedin_agent/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/linkedin-agent"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
cp .env $BACKUP_DIR/.env.$DATE
cp -r data/ $BACKUP_DIR/data.$DATE/

# Compress backup
tar -czf $BACKUP_DIR/backup.$DATE.tar.gz $BACKUP_DIR/.env.$DATE $BACKUP_DIR/data.$DATE/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "backup.*.tar.gz" -mtime +7 -delete
```

### 3. Automated Backups
```bash
# Add to crontab for daily backups
0 2 * * * /path/to/linkedin_agent/backup.sh
```

## 🚨 Troubleshooting

### Common Production Issues

#### 1. Service Not Starting
```bash
# Check supervisor status
sudo supervisorctl status linkedin-agent

# Check logs
sudo tail -f /var/log/linkedin-agent.err.log

# Restart service
sudo supervisorctl restart linkedin-agent
```

#### 2. API Rate Limits
- Monitor OpenAI API usage
- Implement rate limiting if needed
- Set up alerts for quota warnings

#### 3. Email Delivery Issues
```bash
# Test email sending
python3 -c "
from email_handler.send_prompt import EmailPromptSender
sender = EmailPromptSender()
print(sender.send_topic_prompt('test@example.com'))
"
```

#### 4. Memory Issues
```bash
# Monitor memory usage
htop
free -h

# Check Python process
ps aux | grep python
```

## 📈 Performance Optimization

### 1. Resource Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop

# Monitor system resources
htop
iotop
```

### 2. Database Optimization (Phase 3)
- Index Airtable fields for faster queries
- Implement caching for frequently accessed data
- Optimize API calls to reduce rate limiting

### 3. Email Optimization
- Batch email processing
- Implement retry logic for failed sends
- Monitor email delivery rates

## 🔄 Updates and Maintenance

### 1. Update Process
```bash
# Pull latest changes
cd /path/to/linkedin_agent
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo supervisorctl restart linkedin-agent
```

### 2. Scheduled Maintenance
```bash
# Add to crontab for weekly maintenance
0 3 * * 0 /path/to/linkedin_agent/maintenance.sh
```

### 3. Version Management
- Use git tags for releases
- Maintain changelog
- Test updates in staging environment

## 📞 Support and Monitoring

### 1. Alert Setup
- Set up email alerts for service failures
- Monitor API quota usage
- Track email delivery rates

### 2. Documentation
- Keep deployment documentation updated
- Document any custom configurations
- Maintain runbook for common issues

### 3. Backup Contacts
- Maintain list of backup administrators
- Document escalation procedures
- Keep emergency contact information

---

**Production Status**: Ready for deployment ✅

For additional support, refer to the main README.md or open an issue on GitHub. 