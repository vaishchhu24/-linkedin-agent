#!/usr/bin/env python3
"""
Test Email Scheduler with 10 AM UK Time
"""

import sys
import os
from datetime import datetime, timezone
import pytz

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.email_scheduler import EmailScheduler
from config.email_config import EmailSettings

def test_scheduler_configuration():
    """Test the scheduler configuration."""
    
    print("📅 Testing Email Scheduler Configuration")
    print("=" * 50)
    
    # Show current configuration
    print(f"📧 From: {EmailSettings.FROM_EMAIL}")
    print(f"📧 To: {EmailSettings.TO_EMAIL}")
    print(f"📧 Client: {EmailSettings.CLIENT_NAME}")
    print(f"⏰ Schedule Time: {EmailSettings.SCHEDULE_TIME}")
    print(f"🌍 Timezone: {EmailSettings.SCHEDULE_TIMEZONE}")
    print("-" * 30)
    
    # Calculate next run time
    uk_tz = pytz.timezone(EmailSettings.SCHEDULE_TIMEZONE)
    now_uk = datetime.now(uk_tz)
    
    # Parse schedule time
    hour, minute = map(int, EmailSettings.SCHEDULE_TIME.split(':'))
    
    # Calculate next 10 AM UK time
    next_run = now_uk.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if next_run <= now_uk:
        # If it's already past 10 AM today, schedule for tomorrow
        from datetime import timedelta
        next_run += timedelta(days=1)
    
    print(f"🕐 Current UK Time: {now_uk.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"📅 Next Scheduled Run: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"⏱️ Time Until Next Run: {next_run - now_uk}")
    
    return True

def test_scheduler_functionality():
    """Test the scheduler functionality."""
    
    print("\n🔧 Testing Scheduler Functionality")
    print("=" * 50)
    
    try:
        # Initialize scheduler
        scheduler = EmailScheduler()
        
        # Get scheduler status
        status = scheduler.get_scheduler_status()
        print(f"📊 Scheduler Running: {status['scheduler_running']}")
        print(f"📋 Jobs: {len(status['jobs'])}")
        
        for job in status['jobs']:
            print(f"  - {job['name']}: {job['next_run']}")
        
        # Test manual send
        print("\n📤 Testing Manual Email Send...")
        scheduler.manual_send_prompt()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
        return False

def main():
    """Main test function."""
    
    print("🚀 Email Scheduler Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_scheduler_configuration()
    
    if config_ok:
        # Test functionality
        func_ok = test_scheduler_functionality()
        
        if func_ok:
            print("\n✅ All tests passed!")
            print("📅 Scheduler is ready for 10 AM UK time daily emails")
        else:
            print("\n❌ Functionality test failed")
    else:
        print("\n❌ Configuration test failed")

if __name__ == "__main__":
    main() 