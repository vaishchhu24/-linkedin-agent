#!/usr/bin/env python3
"""
Test Email Sending Functionality
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.send_prompt import EmailPromptSender
from config.email_config import EmailSettings

def test_email_sending():
    """Test sending an email to Sam."""
    
    print("📧 Testing Email Sending")
    print("=" * 50)
    
    # Show current configuration
    print(f"📧 From: {EmailSettings.FROM_EMAIL}")
    print(f"📧 To: {EmailSettings.TO_EMAIL}")
    print(f"📧 Client: {EmailSettings.CLIENT_NAME}")
    print("-" * 30)
    
    # Initialize email sender
    email_sender = EmailPromptSender()
    
    # Send test email
    print("📤 Sending test email to Sam...")
    success = email_sender.send_topic_prompt_smtp(EmailSettings.TO_EMAIL)
    
    if success:
        print("✅ Email sent successfully!")
        print("📧 Check Sam's inbox at:", EmailSettings.TO_EMAIL)
    else:
        print("❌ Failed to send email")
    
    print("=" * 50)

if __name__ == "__main__":
    test_email_sending() 