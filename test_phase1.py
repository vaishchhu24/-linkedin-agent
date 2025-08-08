#!/usr/bin/env python3
"""
Test script for Phase 1: Email Scheduler and User Response Handling
"""

import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.email_scheduler import EmailScheduler
from config.email_config import EmailSettings

def test_content_classification():
    """Test the content classification functionality."""
    print("🧪 Testing Content Classification")
    print("=" * 50)
    
    try:
        # Initialize scheduler
        scheduler = EmailScheduler()
        
        # Test cases
        test_responses = [
            # Detailed content examples
            "Yes I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months.",
            
            "Yes Last week I was working with a startup that had no HR processes. Here's what happened when I implemented their first employee handbook - they were so grateful and it completely transformed their onboarding.",
            
            # General topic examples
            "Yes recruitment challenges",
            
            "Yes hiring tips for small businesses",
            
            # Declined responses
            "No",
            
            "No thanks",
            
            # Unclear responses
            "Maybe later",
            
            "I'll think about it"
        ]
        
        for i, response in enumerate(test_responses, 1):
            print(f"\n📝 Test {i}: {response[:50]}...")
            result = scheduler.process_user_response(response)
            
            print(f"   Has Content: {result['has_content']}")
            print(f"   Content Type: {result['content_type']}")
            print(f"   Extracted: {result['extracted_content'][:100]}...")
            print(f"   Message: {result['message']}")
            
            if 'confidence' in result:
                print(f"   Confidence: {result['confidence']}")
        
        print("\n✅ Content classification tests completed")
        
    except Exception as e:
        print(f"❌ Error in content classification test: {e}")

def test_scheduler_status():
    """Test the scheduler status functionality."""
    print("\n📅 Testing Scheduler Status")
    print("=" * 50)
    
    try:
        scheduler = EmailScheduler()
        status = scheduler.get_scheduler_status()
        
        print(f"Scheduler Running: {status['scheduler_running']}")
        print(f"Number of Jobs: {len(status['jobs'])}")
        
        for job in status['jobs']:
            print(f"  - Job: {job['name']}")
            print(f"    ID: {job['id']}")
            print(f"    Next Run: {job['next_run']}")
            print(f"    Trigger: {job['trigger']}")
        
        print("\n✅ Scheduler status test completed")
        
    except Exception as e:
        print(f"❌ Error in scheduler status test: {e}")

def test_configuration():
    """Test the configuration validation."""
    print("\n⚙️ Testing Configuration")
    print("=" * 50)
    
    try:
        if EmailSettings.validate_config():
            print("✅ Configuration validated successfully")
            config_summary = EmailSettings.get_config_summary()
            print(f"From Email: {config_summary['from_email']}")
            print(f"To Email: {config_summary['to_email']}")
            print(f"Resend API Key: {config_summary['resend_api_key']}")
            print(f"OpenAI API Key: {config_summary['openai_api_key']}")
            print(f"Schedule Time: {config_summary['schedule_time']} {config_summary['schedule_timezone']}")
        else:
            print("❌ Configuration validation failed")
            print("\nRequired environment variables:")
            print("- RESEND_API_KEY")
            print("- TO_EMAIL") 
            print("- OPENAI_API_KEY")
            print("- FROM_EMAIL (optional, defaults to noreply@yourdomain.com)")
        
    except Exception as e:
        print(f"❌ Error in configuration test: {e}")

def main():
    """Main test function."""
    print("🚀 Phase 1: Email Scheduler and User Response Handling Test")
    print("=" * 70)
    
    # Test configuration first
    test_configuration()
    
    # Test content classification
    test_content_classification()
    
    # Test scheduler status
    test_scheduler_status()
    
    print("\n" + "=" * 70)
    print("✅ All Phase 1 tests completed")
    print("\nTo start the actual scheduler, run:")
    print("python3 email_handler/email_scheduler.py")

if __name__ == "__main__":
    main() 