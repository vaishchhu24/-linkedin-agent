#!/usr/bin/env python3
"""
Automated LinkedIn Content Workflow
Sends daily prompt emails at 10 AM UK time and processes replies immediately
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from email_handler.send_prompt import EmailPromptSender
from email_handler.real_email_fetcher import RealEmailFetcher
from final_integrated_system import FinalIntegratedSystem
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedWorkflow:
    def __init__(self):
        """Initialize the automated workflow system."""
        self.email_sender = EmailPromptSender()
        self.email_fetcher = RealEmailFetcher()
        self.integrated_system = FinalIntegratedSystem()
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.last_processed_time = None
        
        logger.info("🚀 Automated Workflow System initialized")
        logger.info(f"📧 Client: {EmailSettings.CLIENT_NAME}")
        logger.info(f"📧 Email: {EmailSettings.TO_EMAIL}")
        logger.info(f"⏰ Schedule: Daily at {EmailSettings.SCHEDULE_TIME} {EmailSettings.SCHEDULE_TIMEZONE}")
    
    def start_automated_workflow(self):
        """Start the complete automated workflow."""
        try:
            logger.info("🚀 Starting Automated LinkedIn Content Workflow")
            logger.info("=" * 80)
            
            # Start the scheduler for daily emails
            self._start_email_scheduler()
            
            # Start continuous reply monitoring
            self._start_reply_monitoring()
            
            # Keep the system running
            self.is_running = True
            logger.info("✅ Automated workflow started successfully")
            logger.info("🛑 Press Ctrl+C to stop the system")
            
            try:
                while self.is_running:
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down automated workflow...")
                self.stop_workflow()
                
        except Exception as e:
            logger.error(f"❌ Error starting automated workflow: {e}")
            self.stop_workflow()
    
    def _start_email_scheduler(self):
        """Start the scheduler for daily prompt emails."""
        try:
            # Schedule daily email at 10 AM UK time
            hour, minute = EmailSettings.SCHEDULE_TIME.split(':')
            self.scheduler.add_job(
                func=self._send_daily_prompt,
                trigger=CronTrigger(
                    hour=int(hour), 
                    minute=int(minute), 
                    timezone=EmailSettings.SCHEDULE_TIMEZONE
                ),
                id='daily_linkedin_prompt',
                name='Send daily LinkedIn post prompt',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info(f"✅ Email scheduler started - daily prompts at {EmailSettings.SCHEDULE_TIME} {EmailSettings.SCHEDULE_TIMEZONE}")
            
        except Exception as e:
            logger.error(f"❌ Error starting email scheduler: {e}")
            raise
    
    def _start_reply_monitoring(self):
        """Start continuous monitoring for email replies."""
        def monitor_replies():
            logger.info("📧 Starting continuous reply monitoring...")
            
            while self.is_running:
                try:
                    # Check for new replies every 2 minutes
                    self._check_for_replies()
                    time.sleep(120)  # Wait 2 minutes
                    
                except Exception as e:
                    logger.error(f"❌ Error in reply monitoring: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor_replies, daemon=True)
        monitor_thread.start()
        logger.info("✅ Reply monitoring started in background")
    
    def _send_daily_prompt(self):
        """Send the daily LinkedIn post prompt email."""
        try:
            logger.info("📧 Sending daily LinkedIn post prompt...")
            
            # Send the email using SMTP
            success = self.email_sender.send_topic_prompt_smtp(EmailSettings.TO_EMAIL)
            
            if success:
                logger.info("✅ Daily prompt email sent successfully")
                logger.info("⏳ Waiting for client reply...")
            else:
                logger.error("❌ Failed to send daily prompt email")
                
        except Exception as e:
            logger.error(f"❌ Error sending daily prompt: {e}")
    
    def _check_for_replies(self):
        """Check for new email replies and process them."""
        try:
            # Fetch recent replies (last 5 minutes)
            replies = self.email_fetcher.fetch_recent_replies(hours_back=0.1)  # 6 minutes
            
            if not replies:
                return
            
            # Filter out already processed replies
            new_replies = []
            for reply in replies:
                reply_time = reply.get('timestamp', '')
                if reply_time and self._is_new_reply(reply_time):
                    new_replies.append(reply)
            
            if new_replies:
                logger.info(f"📧 Found {len(new_replies)} new reply(ies)")
                self._process_replies(new_replies)
            
        except Exception as e:
            logger.error(f"❌ Error checking for replies: {e}")
    
    def _is_new_reply(self, reply_time: str) -> bool:
        """Check if this reply is new (not already processed)."""
        try:
            if not self.last_processed_time:
                return True
            
            # Parse reply time
            if 'UTC' in reply_time:
                reply_dt = datetime.strptime(reply_time, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
            else:
                reply_dt = datetime.fromisoformat(reply_time.replace('Z', '+00:00'))
            
            return reply_dt > self.last_processed_time
            
        except Exception as e:
            logger.error(f"❌ Error parsing reply time: {e}")
            return True  # Assume new if we can't parse
    
    def _process_replies(self, replies: List[Dict]):
        """Process new email replies using the integrated system."""
        try:
            logger.info("🔄 Processing new email replies...")
            
            # Update last processed time
            self.last_processed_time = datetime.now(timezone.utc)
            
            # Process each reply
            for reply in replies:
                logger.info(f"📧 Processing reply from: {reply.get('from_email', 'Unknown')}")
                logger.info(f"📝 Subject: {reply.get('subject', 'No subject')}")
                
                # Run the integrated workflow for this reply
                self._run_workflow_for_reply(reply)
                
        except Exception as e:
            logger.error(f"❌ Error processing replies: {e}")
    
    def _run_workflow_for_reply(self, reply: Dict):
        """Run the complete integrated workflow for a single reply."""
        try:
            logger.info("🚀 Starting integrated workflow for reply...")
            
            # Phase 1: Email monitoring (we already have the reply)
            logger.info("📧 Phase 1: Email received and validated")
            
            # Phase 2: Content generation
            logger.info("🧠 Phase 2: Generating content...")
            generated_posts = self.integrated_system.run_phase2_content_generation([reply])
            
            if generated_posts:
                logger.info(f"✅ Generated {len(generated_posts)} posts")
            else:
                logger.warning("⚠️ No posts generated from reply")
            
            # Phase 3: Feedback processing
            logger.info("🔄 Phase 3: Processing feedback...")
            processed_feedback = self.integrated_system.run_phase3_feedback_processing()
            
            if processed_feedback:
                logger.info(f"✅ Processed {len(processed_feedback)} feedback items")
            
            logger.info("✅ Workflow completed for this reply")
            
        except Exception as e:
            logger.error(f"❌ Error running workflow for reply: {e}")
    
    def send_manual_prompt(self):
        """Send a manual prompt email (for testing)."""
        try:
            logger.info("📧 Sending manual prompt email...")
            success = self.email_sender.send_topic_prompt_smtp(EmailSettings.TO_EMAIL)
            
            if success:
                logger.info("✅ Manual prompt email sent successfully")
            else:
                logger.error("❌ Failed to send manual prompt email")
                
        except Exception as e:
            logger.error(f"❌ Error sending manual prompt: {e}")
    
    def stop_workflow(self):
        """Stop the automated workflow."""
        try:
            self.is_running = False
            self.scheduler.shutdown()
            logger.info("🛑 Automated workflow stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping workflow: {e}")

def main():
    """Main function to run the automated workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated LinkedIn Content Workflow')
    parser.add_argument('--manual-prompt', action='store_true', 
                       help='Send a manual prompt email')
    parser.add_argument('--demo', action='store_true',
                       help='Run in demo mode (no actual emails sent)')
    
    args = parser.parse_args()
    
    # Initialize the workflow
    workflow = AutomatedWorkflow()
    
    if args.manual_prompt:
        # Send manual prompt
        workflow.send_manual_prompt()
    elif args.demo:
        # Demo mode
        logger.info("🎬 DEMO MODE - Automated Workflow")
        logger.info("📧 Would send daily prompts at 10:00 AM UK time")
        logger.info("📧 Would monitor for replies continuously")
        logger.info("🚀 Would start integrated workflow on reply")
    else:
        # Start the full automated workflow
        workflow.start_automated_workflow()

if __name__ == "__main__":
    main() 