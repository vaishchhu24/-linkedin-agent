#!/usr/bin/env python3
"""
Automated Workflow with RAG Learning - Complete System
Integrates email monitoring, content generation, and RAG-based learning
"""

import sys
import os
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.real_email_fetcher import RealEmailFetcher
from email_handler.email_scheduler import EmailScheduler
from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
from content_handler.content_assessor import ContentAssessor
from airtable_logger import AirtableLogger
from feedback_loop import FeedbackLoop
from config.email_config import EmailSettings
from feedback_processor import FeedbackProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedWorkflowWithRAG:
    """Complete automated workflow with RAG learning capabilities."""
    
    def __init__(self):
        """Initialize the complete automated workflow system."""
        self.email_fetcher = RealEmailFetcher()
        self.email_scheduler = EmailScheduler()
        self.post_generator = PostGenerator()
        self.icp_checker = ICPPillarChecker()
        self.content_assessor = ContentAssessor()
        self.airtable_logger = AirtableLogger()
        self.feedback_loop = FeedbackLoop()
        self.feedback_processor = FeedbackProcessor()
        
        # Track processed emails to avoid duplicates
        self.processed_emails = set()
        
        logger.info("🤖 Automated Workflow with RAG initialized")
    
    def monitor_and_process_replies(self, check_interval: int = 300, rag_interval: int = 3600, feedback_interval: int = 600):
        """
        Continuously monitor for Sam's email replies and process them automatically.
        Also runs RAG learning and feedback processing periodically.
        
        Args:
            check_interval: How often to check for new emails (in seconds)
            rag_interval: How often to run RAG learning (in seconds)
            feedback_interval: How often to check for feedback (in seconds)
        """
        logger.info("🔄 Starting automated email monitoring with RAG learning and feedback processing...")
        logger.info(f"📧 Monitoring: {EmailSettings.FROM_EMAIL}")
        logger.info(f"👤 Client: {EmailSettings.CLIENT_NAME}")
        logger.info(f"⏰ Email check interval: {check_interval} seconds")
        logger.info(f"🧠 RAG learning interval: {rag_interval} seconds")
        logger.info(f"🔄 Feedback processing interval: {feedback_interval} seconds")
        
        last_rag_run = time.time()
        last_feedback_run = time.time()
        
        while True:
            try:
                current_time = time.time()
                
                # Check for new email replies
                logger.info("🔍 Checking for new email replies...")
                email_replies = self.email_fetcher.fetch_recent_replies(hours_back=1)
                
                for reply in email_replies:
                    email_id = reply.get('email_id')
                    
                    # Skip if already processed
                    if email_id in self.processed_emails:
                        continue
                    
                    logger.info(f"📧 Processing new email from: {reply.get('from_email')}")
                    logger.info(f"📝 Subject: {reply.get('subject')}")
                    
                    # Process the email through the complete workflow
                    success = self.process_email_workflow(reply)
                    
                    if success:
                        # Mark as processed
                        self.processed_emails.add(email_id)
                        logger.info(f"✅ Successfully processed email: {email_id}")
                    else:
                        logger.error(f"❌ Failed to process email: {email_id}")
                
                # Run feedback processing periodically
                if current_time - last_feedback_run >= feedback_interval:
                    logger.info("🔄 Running feedback processing...")
                    self.run_feedback_processing()
                    last_feedback_run = current_time
                
                # Run RAG learning periodically
                if current_time - last_rag_run >= rag_interval:
                    logger.info("🧠 Running RAG learning process...")
                    self.run_rag_learning()
                    last_rag_run = current_time
                
                # Wait before next check
                logger.info(f"⏳ Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopping automated workflow...")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def process_email_workflow(self, email_reply: Dict) -> bool:
        """
        Process a single email reply through the complete workflow with RAG enhancement.
        
        Args:
            email_reply: Email reply data from the fetcher
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            email_content = email_reply.get('content', '')
            from_email = email_reply.get('from_email', '')
            
            logger.info("🔄 Starting email workflow processing with RAG...")
            
            # Step 1: Process user response
            logger.info("📝 Step 1: Processing user response...")
            response_data = self.email_scheduler.process_user_response(email_content)
            
            if response_data.get('response_type') == 'no':
                logger.info("❌ User declined - no content to generate")
                return True
            
            if response_data.get('response_type') == 'error':
                logger.error("❌ Error processing user response")
                return False
            
            # Step 2: Extract content elements
            logger.info("🔍 Step 2: Extracting content elements...")
            content_elements = self.content_assessor.extract_content_elements(
                response_data.get('content', email_content)
            )
            
            topic = content_elements.get('main_topic', 'HR consulting')
            logger.info(f"🎯 Extracted topic: {topic}")
            
            # Step 3: Get ICP and pillar data
            logger.info("🎯 Step 3: Getting ICP and pillar data...")
            icp_data = self.icp_checker.get_icp_for_topic(topic)
            pillar_info = self.icp_checker.get_most_relevant_pillar(topic)
            
            logger.info(f"📊 ICP Segment: {icp_data.get('segment', 'Unknown')}")
            logger.info(f"📋 Pillar: {pillar_info.get('title', 'Unknown')}")
            
            # Step 4: Generate LinkedIn post with RAG enhancement
            logger.info("📝 Step 4: Generating LinkedIn post with RAG enhancement...")
            
            if response_data.get('content_type') == 'detailed_content':
                # Generate from detailed content
                result = self.post_generator.generate_from_detailed_content(
                    response_data.get('content', email_content),
                    content_elements,
                    icp_data,
                    pillar_info
                )
            else:
                # Generate from insights (for general topics)
                from content_handler.insight_fetcher import InsightFetcher
                insight_fetcher = InsightFetcher()
                insights = insight_fetcher.fetch_topic_insights(topic)
                
                result = self.post_generator.generate_from_insights(
                    topic,
                    insights or [],
                    icp_data,
                    pillar_info,
                    {"topic": topic}
                )
            
            if not result.get('success'):
                logger.error(f"❌ Failed to generate post: {result.get('error')}")
                return False
            
            post_content = result['post']
            word_count = result.get('word_count', 0)
            
            logger.info(f"✅ Generated post with RAG enhancement ({word_count} words)")
            
            # Step 5: Log to Airtable
            logger.info("📊 Step 5: Logging to Airtable...")
            
            airtable_success = self.airtable_logger.write_post_to_airtable(
                topic=topic,
                post=post_content
            )
            
            if airtable_success:
                logger.info("✅ Successfully logged to Airtable")
                logger.info("📋 Post is now waiting for Sam's feedback in Airtable")
            else:
                logger.error("❌ Failed to log to Airtable")
                return False
            
            # Step 6: Log workflow completion
            logger.info("🎉 Complete workflow with RAG processed successfully!")
            logger.info(f"📧 Email from: {from_email}")
            logger.info(f"🎯 Topic: {topic}")
            logger.info(f"📝 Post length: {word_count} words")
            logger.info(f"📊 ICP Segment: {icp_data.get('segment')}")
            logger.info(f"📋 Pillar: {pillar_info.get('title')}")
            logger.info("🧠 RAG enhancement: Applied")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in workflow processing: {e}")
            return False
    
    def run_rag_learning(self):
        """Run the RAG learning process to update the knowledge base."""
        try:
            logger.info("🧠 Starting RAG learning process...")
            
            # Run feedback loop to add approved posts to RAG
            self.feedback_loop.run_feedback_loop(hours_back=24)
            
            # Get RAG store statistics
            from rag_memory import RAGMemory
            rag_memory = RAGMemory()
            stats = rag_memory.get_stats()
            
            logger.info("📊 RAG Learning completed!")
            logger.info(f"  Total Posts in RAG: {stats.get('total_posts', 0)}")
            logger.info(f"  Avg Voice Quality: {stats.get('avg_voice_quality', 0)}/10")
            logger.info(f"  Avg Post Quality: {stats.get('avg_post_quality', 0)}/10")
            
        except Exception as e:
            logger.error(f"❌ Error in RAG learning: {e}")
    
    def run_feedback_processing(self):
        """Run the feedback processing to handle client feedback and post regeneration."""
        try:
            logger.info("🔄 Starting feedback processing...")
            
            # Run feedback processor to handle client feedback
            self.feedback_processor.run_feedback_loop(hours_back=24)
            
            logger.info("✅ Feedback processing completed")
            
        except Exception as e:
            logger.error(f"❌ Error in feedback processing: {e}")
    
    def get_workflow_status(self) -> Dict:
        """Get the current status of the automated workflow with RAG."""
        try:
            from rag_memory import RAGMemory
            rag_memory = RAGMemory()
            rag_stats = rag_memory.get_stats()
            
            return {
                "monitoring_active": True,
                "processed_emails_count": len(self.processed_emails),
                "last_check": datetime.now(timezone.utc).isoformat(),
                "client": EmailSettings.CLIENT_NAME,
                "monitoring_email": EmailSettings.FROM_EMAIL,
                "rag_learning": {
                    "total_posts": rag_stats.get('total_posts', 0),
                    "avg_voice_quality": rag_stats.get('avg_voice_quality', 0),
                    "avg_post_quality": rag_stats.get('avg_post_quality', 0),
                    "faiss_available": rag_stats.get('faiss_available', False)
                }
            }
        except Exception as e:
            logger.error(f"❌ Error getting workflow status: {e}")
            return {}

def main():
    """Main function to start the automated workflow with RAG."""
    
    print("🚀 Starting Automated Workflow with RAG Learning and Feedback Processing")
    print("=" * 70)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📧 Monitoring: {EmailSettings.FROM_EMAIL}")
    print(f"📧 Client Email: {EmailSettings.TO_EMAIL}")
    print("⏰ Email Check: Every 5 minutes")
    print("🔄 Feedback Processing: Every 10 minutes")
    print("🧠 RAG Learning: Every hour")
    print("=" * 70)
    print("🔄 The system will now:")
    print("   1. Monitor for Sam's email replies")
    print("   2. Process replies with RAG enhancement")
    print("   3. Generate LinkedIn posts using learned patterns")
    print("   4. Log to Airtable for feedback")
    print("   5. Monitor for client feedback")
    print("   6. Regenerate posts based on feedback")
    print("   7. Add approved posts to RAG store")
    print("   8. Continuously improve content quality")
    print("=" * 70)
    print("🛑 Press Ctrl+C to stop the automated workflow")
    print()
    
    try:
        # Initialize and start the automated workflow with RAG
        workflow = AutomatedWorkflowWithRAG()
        workflow.monitor_and_process_replies(check_interval=300, rag_interval=3600, feedback_interval=600)
        
    except KeyboardInterrupt:
        print("\n🛑 Automated workflow with RAG stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 