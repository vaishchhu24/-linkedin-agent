#!/usr/bin/env python3
"""
Test Real Email Reading
Shows how to set up and test real email reading from your inbox
"""

import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.real_email_fetcher import RealEmailFetcher
from email_handler.email_scheduler import EmailScheduler

def setup_email_reading():
    """Set up real email reading."""
    
    print("📧 Setting Up Real Email Reading")
    print("=" * 50)
    
    # Check if email password is set in config
    from config.email_config import EmailSettings
    
    if not EmailSettings.EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD not set in config")
        print("\n💡 To set it up:")
        print("1. Go to your Gmail account settings")
        print("2. Enable 2-factor authentication")
        print("3. Generate an 'App Password'")
        print("4. Add it to config.py:")
        print("   EMAIL_PASSWORD = 'your-16-digit-app-password'")
        return False
    
    print("✅ EMAIL_PASSWORD is set in config")
    print(f"📧 Email: {EmailSettings.FROM_EMAIL}")
    print(f"🔑 Password length: {len(EmailSettings.EMAIL_PASSWORD)} characters")
    
    # Check if password looks like a Gmail app password
    if len(EmailSettings.EMAIL_PASSWORD) != 16:
        print("⚠️ Warning: Gmail app passwords should be exactly 16 characters")
        print("💡 Make sure you're using the correct app password format")
    
    return True

def test_email_connection():
    """Test email connection."""
    
    print("\n🔗 Testing Email Connection")
    print("=" * 30)
    
    fetcher = RealEmailFetcher()
    
    # Test connection
    mail = fetcher.connect_to_inbox()
    
    if mail:
        print("✅ Email connection successful!")
        mail.close()
        mail.logout()
        return True
    else:
        print("❌ Email connection failed")
        return False

def test_email_fetching():
    """Test fetching real emails."""
    
    print("\n📧 Testing Email Fetching")
    print("=" * 30)
    
    fetcher = RealEmailFetcher()
    
    # Fetch recent replies
    replies = fetcher.fetch_recent_replies(hours_back=24)
    
    if replies:
        print(f"✅ Found {len(replies)} recent replies:")
        for i, reply in enumerate(replies[:3], 1):
            print(f"\n  {i}. From: {reply['from_email']}")
            print(f"     Subject: {reply['subject']}")
            print(f"     Date: {reply['date']}")
            print(f"     Content: {reply['content'][:100]}...")
    else:
        print("ℹ️ No recent replies found")
        print("💡 Try sending yourself a test email with 'LinkedIn' in the subject")
    
    return replies

def test_email_processing():
    """Test processing real email responses."""
    
    print("\n🔄 Testing Email Processing")
    print("=" * 30)
    
    scheduler = EmailScheduler()
    
    # Process real email responses
    processed_responses = scheduler.process_real_email_responses()
    
    if processed_responses:
        print(f"✅ Processed {len(processed_responses)} email responses:")
        for i, response in enumerate(processed_responses, 1):
            print(f"\n  {i}. From: {response.get('from_email', 'Unknown')}")
            print(f"     Has Topic: {response.get('has_topic', False)}")
            print(f"     Content Type: {response.get('content_type', 'Unknown')}")
            print(f"     Topic: {response.get('topic_input', 'None')[:50]}...")
    else:
        print("ℹ️ No email responses to process")
    
    return processed_responses

def main():
    """Main test function."""
    
    print("🚀 Real Email Reading Test")
    print("=" * 50)
    
    # Step 1: Setup
    if not setup_email_reading():
        return
    
    # Step 2: Test connection
    if not test_email_connection():
        return
    
    # Step 3: Test fetching
    replies = test_email_fetching()
    
    # Step 4: Test processing
    if replies:
        processed = test_email_processing()
        
        if processed:
            print(f"\n🎉 SUCCESS! Found and processed {len(processed)} real email responses!")
            print("💡 Your system is now reading REAL emails from your inbox!")
        else:
            print("\n⚠️ Found emails but couldn't process them")
    else:
        print("\n💡 No emails found - try sending yourself a test email")
        print("   Subject: 'LinkedIn post topic'")
        print("   Content: 'Yes, I want to talk about client acquisition challenges'")

if __name__ == "__main__":
    main() 