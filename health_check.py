#!/usr/bin/env python3
"""
Health Check Script for LinkedIn Content Generation System
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from email_handler.email_scheduler import EmailScheduler
    from config.email_config import EmailSettings
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_configuration():
    """Check if all required configuration is present."""
    try:
        if EmailSettings.validate_config():
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
    except Exception as e:
        print(f"❌ Configuration check error: {e}")
        return False

def check_scheduler():
    """Check if the email scheduler is working."""
    try:
        scheduler = EmailScheduler()
        status = scheduler.get_scheduler_status()
        
        if status['scheduler_running']:
            print("✅ Scheduler is running")
            return True
        else:
            print("❌ Scheduler is not running")
            return False
    except Exception as e:
        print(f"❌ Scheduler check error: {e}")
        return False

def check_api_connections():
    """Check API connections."""
    try:
        # Test OpenAI connection (simple test)
        import openai
        from openai import OpenAI
        
        client = OpenAI(api_key=EmailSettings.OPENAI_API_KEY)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI API connection working")
            return True
        else:
            print("❌ OpenAI API test failed")
            return False
            
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def check_content_classification():
    """Test content classification functionality."""
    try:
        scheduler = EmailScheduler()
        
        # Test with a simple response
        test_response = "Yes recruitment challenges"
        result = scheduler.process_user_response(test_response)
        
        if result['has_content'] and result['content_type'] in ['detailed_content', 'general_topic']:
            print("✅ Content classification working")
            return True
        else:
            print("❌ Content classification test failed")
            return False
            
    except Exception as e:
        print(f"❌ Content classification error: {e}")
        return False

def main():
    """Main health check function."""
    print("🏥 LinkedIn Content Generation System Health Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Configuration", check_configuration),
        ("Scheduler", check_scheduler),
        ("API Connections", check_api_connections),
        ("Content Classification", check_content_classification)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_function in checks:
        print(f"🔍 Checking {check_name}...")
        if check_function():
            passed_checks += 1
        print()
    
    # Summary
    print("📊 Health Check Summary")
    print("=" * 30)
    print(f"Passed: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("✅ All health checks passed - System is healthy!")
        return 0
    else:
        print("❌ Some health checks failed - System needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 