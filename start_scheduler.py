#!/usr/bin/env python3
"""
Start Automated Email Scheduler
Runs the email scheduler that sends daily prompts at 10 AM UK time
"""

import sys
import os
import time
import signal
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.email_scheduler import EmailScheduler
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("🛑 Received shutdown signal, stopping scheduler...")
    if 'scheduler' in globals():
        scheduler.stop_scheduler()
    sys.exit(0)

def main():
    """Start the automated email scheduler."""
    
    print("🚀 Starting Automated Email Scheduler")
    print("=" * 50)
    print(f"📧 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📧 To: {EmailSettings.TO_EMAIL}")
    print(f"⏰ Schedule: Daily at {EmailSettings.SCHEDULE_TIME} {EmailSettings.SCHEDULE_TIMEZONE}")
    print("=" * 50)
    
    try:
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize and start scheduler
        global scheduler
        scheduler = EmailScheduler()
        
        # Validate configuration
        if not EmailSettings.validate_config():
            logger.error("❌ Configuration validation failed")
            return
        
        logger.info("✅ Configuration validated")
        
        # Start the scheduler
        scheduler.start_scheduler()
        
        logger.info("✅ Scheduler started successfully!")
        logger.info("📅 Daily emails will be sent at 10:00 AM UK time")
        logger.info("🔄 Scheduler is running... Press Ctrl+C to stop")
        
        # Keep the script running
        while True:
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        if 'scheduler' in globals():
            scheduler.stop_scheduler()
    except Exception as e:
        logger.error(f"❌ Error in scheduler: {e}")
        if 'scheduler' in globals():
            scheduler.stop_scheduler()

if __name__ == "__main__":
    main() 