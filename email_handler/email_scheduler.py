import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import openai
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_handler.send_prompt import EmailPromptSender
from email_handler.receive_response import EmailResponseReceiver
from email_handler.real_email_fetcher import RealEmailFetcher
from config.email_config import EmailSettings, ContentClassificationSettings, ResponseProcessingSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailScheduler:
    def __init__(self):
        """Initialize the email scheduler with APScheduler."""
        self.scheduler = BackgroundScheduler()
        self.email_sender = EmailPromptSender()
        self.response_receiver = EmailResponseReceiver()
        self.real_email_fetcher = RealEmailFetcher()
        
        # Initialize OpenAI client
        openai.api_key = EmailSettings.OPENAI_API_KEY
        
        logger.info("📅 Email Scheduler initialized")
    
    def start_scheduler(self):
        """Start the background scheduler with 3 daily emails at 1-hour intervals."""
        try:
            # Schedule 3 daily emails at configured times
            for i, schedule_time in enumerate(EmailSettings.SCHEDULE_TIMES):
                hour, minute = schedule_time.split(':')
                job_id = f'daily_linkedin_prompt_{i+1}'
                job_name = f'Send daily LinkedIn post prompt {i+1}'
                
                self.scheduler.add_job(
                    func=self.send_daily_prompt,
                    trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=EmailSettings.SCHEDULE_TIMEZONE),
                    id=job_id,
                    name=job_name,
                    replace_existing=True
                )
                
                logger.info(f"📅 Scheduled email {i+1} for {schedule_time} {EmailSettings.SCHEDULE_TIMEZONE}")
            
            self.scheduler.start()
            logger.info(f"✅ Email scheduler started - 3 daily prompts scheduled at {', '.join(EmailSettings.SCHEDULE_TIMES)} {EmailSettings.SCHEDULE_TIMEZONE}")
            
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
            raise
    
    def stop_scheduler(self):
        """Stop the background scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("🛑 Email scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    def send_daily_prompt(self):
        """Send the daily LinkedIn post prompt email."""
        try:
            logger.info("📧 Sending daily LinkedIn post prompt...")
            
            # Send the email using SMTP
            success = self.email_sender.send_topic_prompt_smtp(EmailSettings.TO_EMAIL)
            
            if success:
                logger.info("✅ Daily prompt email sent successfully")
            else:
                logger.error("❌ Failed to send daily prompt email")
                
        except Exception as e:
            logger.error(f"❌ Error sending daily prompt: {e}")
    
    def process_user_response(self, email_content: str) -> Dict:
        """
        Process user's email response to determine content type and extract content.
        
        Args:
            email_content: Raw email content from user
            
        Returns:
            Dict with response type and extracted content
        """
        try:
            # Clean the email content
            cleaned_content = self._clean_email_content(email_content)
            
            # Check if response starts with "Yes"
            if cleaned_content.lower().startswith("yes"):
                # Extract content after "Yes"
                content_after_yes = cleaned_content[3:].strip()
                
                if content_after_yes:
                    # Classify the content
                    content_type = self._classify_content(content_after_yes)
                    
                    return {
                        "response_type": "yes",
                        "content": content_after_yes,
                        "content_type": content_type,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    # "Yes" with no additional content
                    return {
                        "response_type": "yes",
                        "content": "",
                        "content_type": "general_topic",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            
            # Check if response is "No"
            elif cleaned_content.lower().strip() == "no":
                return {
                    "response_type": "no",
                    "content": "",
                    "content_type": "declined",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Handle unclear responses
            else:
                return {
                    "response_type": "unclear",
                    "content": cleaned_content,
                    "content_type": "general_topic",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing user response: {e}")
            return {
                "response_type": "error",
                "content": email_content,
                "content_type": "general_topic",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _clean_email_content(self, email_content: str) -> str:
        """
        Clean email content by removing quotes, signatures, etc.
        
        Args:
            email_content: Raw email content
            
        Returns:
            Cleaned email content
        """
        try:
            # Remove email quotes (lines starting with >)
            lines = email_content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip quoted lines and common email artifacts
                if (line.strip().startswith('>') or 
                    line.strip().startswith('On ') and ' wrote:' in line or
                    line.strip().startswith('From:') or
                    line.strip().startswith('Sent:') or
                    line.strip().startswith('To:') or
                    line.strip().startswith('Subject:') or
                    '---' in line or
                    '___' in line):
                    continue
                
                cleaned_lines.append(line)
            
            # Join lines and clean up
            cleaned_content = '\n'.join(cleaned_lines).strip()
            
            # Remove multiple spaces and newlines
            cleaned_content = ' '.join(cleaned_content.split())
            
            return cleaned_content
            
        except Exception as e:
            logger.error(f"❌ Error cleaning email content: {e}")
            return email_content
    
    def _classify_content(self, content: str) -> str:
        """
        Classify content using OpenAI GPT-3.5 Turbo.
        
        Args:
            content: Content to classify
            
        Returns:
            Content type classification
        """
        try:
            client = openai.OpenAI(api_key=EmailSettings.OPENAI_API_KEY)
            
            prompt = f"""
            Classify this content as either "detailed_content" or "general_topic":
            
            Content: {content}
            
            Rules:
            - "detailed_content": Personal stories, specific experiences, detailed examples, client testimonials, specific results
            - "general_topic": Brief topics, general ideas, simple questions, vague concepts
            
            Respond with ONLY: detailed_content OR general_topic
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            classification = response.choices[0].message.content.strip().lower()
            
            # Validate classification
            if classification in ["detailed_content", "general_topic"]:
                return classification
            else:
                # Default to general_topic if unclear
                return "general_topic"
                
        except Exception as e:
            logger.error(f"❌ Error classifying content: {e}")
            return "general_topic"
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status."""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "scheduler_running": self.scheduler.running,
                "jobs": jobs
            }
        except Exception as e:
            logger.error(f"❌ Error getting scheduler status: {e}")
            return {"scheduler_running": False, "jobs": []}
    
    def manual_send_prompt(self):
        """Manually trigger the daily prompt (for testing)."""
        try:
            logger.info("📧 Manually sending prompt...")
            self.send_daily_prompt()
        except Exception as e:
            logger.error(f"❌ Error in manual send: {e}")

    def process_real_email_responses(self) -> List[Dict]:
        """
        Process real email responses from the inbox.
        
        Returns:
            List of processed email responses
        """
        try:
            logger.info("📧 Processing real email responses...")
            
            # Fetch real email replies
            email_replies = self.real_email_fetcher.fetch_recent_replies(hours_back=24)
            
            processed_responses = []
            
            for reply in email_replies:
                try:
                    # Process each email reply
                    processed_response = self.process_user_response(reply['content'])
                    
                    # Add email metadata
                    processed_response.update({
                        'email_id': reply['email_id'],
                        'from_email': reply['from_email'],
                        'subject': reply['subject'],
                        'email_date': reply['date'],
                        'fetched_at': reply['fetched_at']
                    })
                    
                    processed_responses.append(processed_response)
                    
                    logger.info(f"✅ Processed email from: {reply['from_email']}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {reply.get('email_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Processed {len(processed_responses)} real email responses")
            return processed_responses
            
        except Exception as e:
            logger.error(f"❌ Error processing real email responses: {e}")
            return []


# Main execution function for testing
def main():
    """Main function for testing the email scheduler."""
    try:
        # Validate configuration
        if not EmailSettings.validate_config():
            logger.error("❌ Configuration validation failed")
            return
        
        logger.info("✅ Configuration validated")
        
        # Initialize and start scheduler
        scheduler = EmailScheduler()
        scheduler.start_scheduler()
        
        # Keep the script running
        import time
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        scheduler.stop_scheduler()
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")


if __name__ == "__main__":
    main() 