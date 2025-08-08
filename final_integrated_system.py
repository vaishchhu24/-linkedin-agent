#!/usr/bin/env python3
"""
Final Integrated LinkedIn Content System
Combines all 3 phases: Email Monitoring, Content Generation, and Feedback Processing
"""

import sys
import os
import time
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.real_email_fetcher import RealEmailFetcher
from email_handler.email_scheduler import EmailScheduler
from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
from content_handler.content_assessor import ContentAssessor
from airtable_logger import AirtableLogger
from enhanced_feedback_processor import EnhancedFeedbackProcessor
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalIntegratedSystem:
    """Complete integrated LinkedIn content system with all 3 phases."""
    
    def __init__(self):
        """Initialize the complete integrated system."""
        self.email_fetcher = RealEmailFetcher()
        self.email_scheduler = EmailScheduler()
        self.post_generator = PostGenerator()
        self.icp_checker = ICPPillarChecker()
        self.content_assessor = ContentAssessor()
        self.airtable_logger = AirtableLogger()
        self.feedback_processor = EnhancedFeedbackProcessor()
        
        # Track processed emails to avoid duplicates
        self.processed_emails = set()
        
        logger.info("🚀 Final Integrated LinkedIn Content System initialized")
        logger.info(f"👤 Client: {EmailSettings.CLIENT_NAME}")
        logger.info(f"📧 Monitoring: {EmailSettings.FROM_EMAIL}")
        logger.info(f"📧 Client Email: {EmailSettings.TO_EMAIL}")
    
    def run_phase1_email_monitoring(self):
        """Phase 1: Monitor for Sam's email replies."""
        try:
            logger.info("📧 Phase 1: Email Monitoring")
            logger.info("🔍 Checking for new email replies...")
            
            email_replies = self.email_fetcher.fetch_recent_replies(hours_back=1)
            
            if not email_replies:
                logger.info("📭 No new email replies found")
                return []
            
            new_replies = []
            for reply in email_replies:
                email_id = reply.get('email_id')
                
                # Skip if already processed
                if email_id in self.processed_emails:
                    continue
                
                logger.info(f"📧 New email from: {reply.get('from_email')}")
                logger.info(f"📝 Subject: {reply.get('subject')}")
                logger.info(f"📄 Content: {reply.get('content', '')[:100]}...")
                
                new_replies.append(reply)
                self.processed_emails.add(email_id)
            
            logger.info(f"✅ Found {len(new_replies)} new email replies")
            return new_replies
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 1: {e}")
            return []
    
    def run_phase2_content_generation(self, email_replies):
        """Phase 2: Generate content based on email replies."""
        try:
            logger.info("🧠 Phase 2: Content Generation")
            
            generated_posts = []
            
            for reply in email_replies:
                logger.info(f"🔄 Processing email reply...")
                
                # Extract user content from email
                user_content = reply.get('content', '').strip()
                
                if not user_content:
                    logger.warning("⚠️ Empty email content, skipping")
                    continue
                
                # Assess content detail level
                content_elements = self.content_assessor.extract_content_elements(user_content)
                logger.info(f"📊 Content assessment: {content_elements.get('detail_level', 'unknown')}")
                
                # Get ICP and pillar data
                topic = content_elements.get('main_topic', user_content)
                icp_data = self.icp_checker.get_icp_for_topic(topic)
                pillar_data = self.icp_checker.get_most_relevant_pillar(topic)
                
                # Generate post based on content type
                if content_elements.get('detail_level') == 'detailed':
                    logger.info("📝 CASE 1: Generating from detailed content...")
                    result = self.post_generator.generate_from_detailed_content(user_content, content_elements, icp_data, pillar_data)
                else:
                    # Check if user doesn't have a topic (replied with "No")
                    if content_elements.get('main_topic') == 'general_hr_consulting':
                        logger.info("🎯 CASE 3: User doesn't have a topic - selecting from content pillars")
                        # Select a random topic from content pillars instead of using "No" as topic
                        selected_topic = self._select_random_pillar_topic()
                        logger.info(f"🎯 Selected topic from pillars: {selected_topic}")
                        
                        # Use the selected topic instead of user content
                        from content_handler.insight_fetcher import InsightFetcher
                        insight_fetcher = InsightFetcher()
                        insights = insight_fetcher.fetch_topic_insights(selected_topic)
                        result = self.post_generator.generate_from_pillar_topic(selected_topic, insights, icp_data, pillar_data)
                    else:
                        logger.info("🔍 CASE 2: Generating from topic with research...")
                        # For general topics, we need to get insights first
                        from content_handler.insight_fetcher import InsightFetcher
                        insight_fetcher = InsightFetcher()
                        insights = insight_fetcher.fetch_topic_insights(user_content)
                        result = self.post_generator.generate_from_topic_only(user_content, insights, icp_data, pillar_data)
                
                if result and result.get('success'):
                    post_data = {
                        'topic': result.get('topic', ''),
                        'post': result.get('post', ''),
                        'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                        'source_type': 'email_reply',
                        'email_id': reply.get('email_id'),
                        'generation_method': result.get('generation_method', ''),
                        'rag_context_used': result.get('rag_context_used', False)
                    }
                    
                    # Log to Airtable
                    success = self.airtable_logger.write_post_to_airtable(
                        post_data['topic'], 
                        post_data['post']
                    )
                    
                    if success:
                        logger.info("✅ Post generated and logged to Airtable")
                        generated_posts.append(post_data)
                    else:
                        logger.error("❌ Failed to log post to Airtable")
                else:
                    logger.error(f"❌ Failed to generate post: {result.get('error', 'Unknown error')}")
            
            logger.info(f"✅ Generated {len(generated_posts)} posts")
            return generated_posts
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 2: {e}")
            return []
    
    def run_phase3_feedback_processing(self):
        """Phase 3: Process client feedback and RAG learning."""
        try:
            logger.info("🔄 Phase 3: Feedback Processing & RAG Learning")
            
            # Monitor for new feedback and run enhanced feedback loop
            self.feedback_processor.run_enhanced_feedback_loop(hours_back=24)
            
            # Get processed feedback for reporting
            posts_with_feedback = self.feedback_processor.monitor_for_feedback(hours_back=1)
            processed_feedback = []
            
            for post_data in posts_with_feedback:
                logger.info(f"🔄 Processing feedback for: {post_data.get('topic', 'N/A')}")
                logger.info(f"📝 Feedback: {post_data.get('feedback', 'N/A')}")
                
                # Process the feedback
                success = self.feedback_processor.process_feedback(post_data)
                
                if success:
                    logger.info("✅ Feedback processed successfully")
                    processed_feedback.append(post_data)
                else:
                    logger.error("❌ Failed to process feedback")
            
            logger.info(f"✅ Processed {len(processed_feedback)} feedback items")
            
            # Cleanup old posts (older than 45 days)
            logger.info("🧹 Running RAG cleanup...")
            removed_count = self.feedback_processor.rag_memory.cleanup_old_posts(days_old=45)
            if removed_count > 0:
                logger.info(f"🗑️ Cleaned up {removed_count} old posts from RAG store")
            
            return processed_feedback
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 3: {e}")
            return []
    
    def run_complete_workflow(self, check_interval: int = 300):
        """
        Run the complete integrated workflow.
        
        Args:
            check_interval: How often to check for new emails/feedback (in seconds)
        """
        logger.info("🚀 Starting Complete Integrated LinkedIn Content System")
        logger.info("=" * 80)
        logger.info("📋 System Overview:")
        logger.info("   Phase 1: Email Monitoring - Detects Sam's replies")
        logger.info("   Phase 2: Content Generation - Creates LinkedIn posts with RAG")
        logger.info("   Phase 3: Feedback Processing - Handles client feedback & learning")
        logger.info("=" * 80)
        logger.info(f"⏰ Check interval: {check_interval} seconds")
        logger.info("🛑 Press Ctrl+C to stop the system")
        logger.info("=" * 80)
        
        # Send daily prompt email when system starts
        logger.info("📧 Sending initial daily prompt email...")
        self.send_daily_prompt_email()
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                
                logger.info(f"\n🔄 Cycle {cycle_count} - {current_time}")
                logger.info("-" * 60)
                
                # Phase 1: Email Monitoring
                email_replies = self.run_phase1_email_monitoring()
                
                # Phase 2: Content Generation (if new emails)
                if email_replies:
                    generated_posts = self.run_phase2_content_generation(email_replies)
                    logger.info(f"📝 Generated {len(generated_posts)} posts from {len(email_replies)} emails")
                else:
                    logger.info("📭 No new emails to process")
                
                # Phase 3: Feedback Processing
                processed_feedback = self.run_phase3_feedback_processing()
                if processed_feedback:
                    logger.info(f"🔄 Processed {len(processed_feedback)} feedback items")
                else:
                    logger.info("📭 No new feedback to process")
                
                # System status
                self.print_system_status()
                
                logger.info(f"⏳ Waiting {check_interval} seconds before next cycle...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 System stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main workflow: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def print_system_status(self):
        """Print current system status."""
        try:
            # Get RAG store stats
            rag_stats = self.feedback_processor.rag_memory.get_stats()
            
            # Get Airtable stats
            all_records = self.airtable_logger.get_all_records()
            
            logger.info("\n📊 System Status:")
            logger.info(f"   📧 Processed emails: {len(self.processed_emails)}")
            logger.info(f"   📝 Total posts in Airtable: {len(all_records)}")
            logger.info(f"   📚 RAG store posts: {rag_stats.get('total_posts', 0)}")
            logger.info(f"   🧠 RAG learning active: {rag_stats.get('faiss_available', False)}")
            
        except Exception as e:
            logger.error(f"❌ Error getting system status: {e}")
    
    def run_demo_mode(self):
        """Run in demo mode for client presentation."""
        logger.info("🎬 DEMO MODE - LinkedIn Content System")
        logger.info("=" * 80)
        logger.info("📋 System Features:")
        logger.info("   ✅ Automated email monitoring")
        logger.info("   ✅ AI-powered content generation")
        logger.info("   ✅ RAG-enhanced learning")
        logger.info("   ✅ Client feedback processing")
        logger.info("   ✅ Continuous quality improvement")
        logger.info("=" * 80)
        
        # Show system capabilities
        self.print_system_status()
        
        # Test each phase
        logger.info("\n🧪 Testing System Components:")
        
        # Test Phase 1
        logger.info("📧 Testing Phase 1: Email Monitoring...")
        email_replies = self.run_phase1_email_monitoring()
        logger.info(f"✅ Phase 1: Found {len(email_replies)} email replies")
        
        # Test Phase 2 (if emails found)
        if email_replies:
            logger.info("🧠 Testing Phase 2: Content Generation...")
            generated_posts = self.run_phase2_content_generation(email_replies)
            logger.info(f"✅ Phase 2: Generated {len(generated_posts)} posts")
        
        # Test Phase 3
        logger.info("🔄 Testing Phase 3: Feedback Processing...")
        processed_feedback = self.run_phase3_feedback_processing()
        logger.info(f"✅ Phase 3: Processed {len(processed_feedback)} feedback items")
        
        logger.info("\n🎉 Demo completed successfully!")
        logger.info("🚀 System is ready for production use!")

    def _select_random_pillar_topic(self) -> str:
        """
        Select a random topic from the content pillars when user doesn't have a specific topic.
        
        Returns:
            Selected topic string
        """
        try:
            import json
            import random
            
            # Load content pillars
            pillars_file = "data/content_pillars.json"
            with open(pillars_file, 'r') as f:
                pillars_data = json.load(f)
            
            # Collect all topics from all pillars
            all_topics = []
            for pillar in pillars_data.get('content_pillars', []):
                topics = pillar.get('topics', [])
                all_topics.extend(topics)
            
            if not all_topics:
                logger.warning("⚠️ No topics found in content pillars, using fallback")
                return "HR consultant business growth strategies"
            
            # Select a random topic
            selected_topic = random.choice(all_topics)
            logger.info(f"🎯 Selected topic from {len(all_topics)} available topics")
            
            return selected_topic
            
        except Exception as e:
            logger.error(f"❌ Error selecting pillar topic: {e}")
            # Fallback topics
            fallback_topics = [
                "HR consultant pricing strategies",
                "Client acquisition for HR consultants", 
                "Building systems for HR consulting business",
                "Managing difficult client conversations",
                "Scaling HR consulting business",
                "HR consultant burnout prevention"
            ]
            return random.choice(fallback_topics)

    def send_daily_prompt_email(self):
        """Send the daily prompt email to the client."""
        try:
            logger.info("📧 Sending daily prompt email to client...")
            
            # Import email sending functionality
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = EmailSettings.FROM_EMAIL
            msg['To'] = EmailSettings.TO_EMAIL
            msg['Subject'] = EmailSettings.EMAIL_SUBJECT
            
            # Email body
            body = f"""Hi {EmailSettings.CLIENT_NAME},

{EmailSettings.EMAIL_SUBJECT}

What's on your mind for your LinkedIn post today? Share your thoughts, experiences, or topics you'd like to write about.

Looking forward to hearing from you!

Best regards,
Your LinkedIn Content System"""

            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EmailSettings.FROM_EMAIL, EmailSettings.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EmailSettings.FROM_EMAIL, EmailSettings.TO_EMAIL, text)
            server.quit()
            
            logger.info(f"✅ Daily prompt email sent to {EmailSettings.TO_EMAIL}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending daily prompt email: {e}")
            return False

def main():
    """Main function to run the integrated system."""
    
    print("🚀 Final Integrated LinkedIn Content System")
    print("=" * 80)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("📧 Email: {EmailSettings.TO_EMAIL}")
    print("=" * 80)
    print("🎯 System Phases:")
    print("   1. 📧 Email Monitoring - Detects client replies")
    print("   2. 🧠 Content Generation - Creates posts with RAG learning")
    print("   3. 🔄 Feedback Processing - Handles feedback & continuous learning")
    print("=" * 80)
    
    # Initialize system
    system = FinalIntegratedSystem()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        system.run_demo_mode()
    else:
        print("🚀 Starting automated workflow...")
        print("💡 Use 'python3 final_integrated_system.py demo' for demo mode")
        print("=" * 80)
        system.run_complete_workflow()

if __name__ == "__main__":
    main() 