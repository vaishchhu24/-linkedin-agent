#!/bin/bash
# AWS EC2 Deployment Script for LinkedIn Agent
# Run this on a fresh Ubuntu 20.04+ EC2 instance

set -e

echo "🚀 Setting up LinkedIn Agent on AWS EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv git supervisor nginx htop -y

# Create application directory
sudo mkdir -p /opt/linkedin-agent
sudo chown ubuntu:ubuntu /opt/linkedin-agent

# Clone your repository (replace with your actual repo)
cd /opt/linkedin-agent
# git clone https://github.com/yourusername/linkedin_agent.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create production config
cat > config.py << 'EOF'
import os

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

# Email settings
EMAIL_SEND_TIME = "10:00"
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Fine-tuned model
FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-1106:personal:linkedintone:By2MD8pX"

# Production settings
ENVIRONMENT = "production"
LOG_LEVEL = "INFO"
EOF

# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/linkedin-agent.conf > /dev/null << 'EOF'
[program:linkedin-agent]
command=/opt/linkedin-agent/venv/bin/python /opt/linkedin-agent/automated_workflow.py
directory=/opt/linkedin-agent
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/linkedin-agent.err.log
stdout_logfile=/var/log/linkedin-agent.out.log
environment=PYTHONPATH="/opt/linkedin-agent"
EOF

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start linkedin-agent

echo "✅ LinkedIn Agent deployed successfully!"
echo "📊 Check status: sudo supervisorctl status linkedin-agent"
echo "📝 View logs: sudo tail -f /var/log/linkedin-agent.out.log" 