import os
import sys
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.email_config import EmailSettings
from airtable_logger import AirtableLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackLoop:
    """
    Phase 3: Feedback Loop System
    Monitors Airtable for client feedback, rewrites posts, and prepares fine-tuning data.
    """
    
    def __init__(self):
        """Initialize the feedback loop system."""
        self.airtable_logger = AirtableLogger()
        self.openai_client = self._init_openai_client()
        self.training_data_dir = "training_data"
        self.fine_tune_queue_file = os.path.join(self.training_data_dir, "fine_tune_queue.jsonl")
        
        # Ensure training data directory exists
        os.makedirs(self.training_data_dir, exist_ok=True)
        
        logger.info("🔄 Feedback Loop System initialized")
    
    def _init_openai_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            client = openai.OpenAI(api_key=EmailSettings.OPENAI_API_KEY)
            return client
        except ImportError:
            logger.error("❌ OpenAI library not installed")
            return None
    
    def monitor_airtable_for_feedback(self) -> List[Dict]:
        """
        Monitor Airtable for new feedback on pending posts.
        
        Returns:
            List of records that need feedback processing
        """
        try:
            logger.info("🔍 Monitoring Airtable for new feedback...")
            
            # Get all records from Airtable
            records = self.airtable_logger.get_all_records()
            
            # Filter for pending posts with feedback
            pending_with_feedback = []
            
            for record in records:
                fields = record.get('fields', {})
                
                # Check if status is "Pending" and feedback exists
                status = fields.get('status', '')
                feedback = fields.get('feedback', '')
                
                if (status == "Pending" and 
                    feedback and 
                    feedback.strip() and
                    feedback.lower() not in ['yes', 'approved']):
                    
                    pending_with_feedback.append({
                        'record_id': record['id'],
                        'fields': fields
                    })
            
            logger.info(f"✅ Found {len(pending_with_feedback)} posts with feedback to process")
            return pending_with_feedback
            
        except Exception as e:
            logger.error(f"❌ Error monitoring Airtable: {e}")
            return []
    
    def process_feedback(self, record_data: Dict) -> bool:
        """
        Process feedback for a single post.
        
        Args:
            record_data: Airtable record with feedback
            
        Returns:
            True if processing was successful
        """
        try:
            record_id = record_data['record_id']
            fields = record_data['fields']
            
            post_content = fields.get('post_content', '')
            feedback = fields.get('feedback', '')
            voice_quality = fields.get('voice_quality', 0)
            post_quality = fields.get('post_quality', 0)
            
            logger.info(f"📝 Processing feedback for post: {record_id}")
            logger.info(f"📊 Feedback: {feedback}")
            logger.info(f"📊 Voice Quality: {voice_quality}/10")
            logger.info(f"📊 Post Quality: {post_quality}/10")
            
            # Generate revised post based on feedback
            revised_post = self._generate_revised_post(post_content, feedback)
            
            if revised_post:
                # Update Airtable with revised post
                success = self._update_airtable_with_revision(
                    record_id, 
                    revised_post, 
                    feedback
                )
                
                if success:
                    # Optionally send email notification
                    self._notify_client_of_revision(record_id, revised_post)
                    
                    logger.info(f"✅ Successfully processed feedback for {record_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error processing feedback: {e}")
            return False
    
    def _generate_revised_post(self, original_post: str, feedback: str) -> Optional[str]:
        """
        Generate a revised post based on client feedback using OpenAI.
        
        Args:
            original_post: The original post content
            feedback: Client feedback
            
        Returns:
            Revised post content or None if generation failed
        """
        try:
            if not self.openai_client:
                logger.error("❌ OpenAI client not available")
                return None
            
            # Construct the revision prompt
            revision_prompt = f"""
Here's the original post:

{original_post}

The client gave this feedback:

{feedback}

Please rewrite the post while preserving the core message and fixing the issue mentioned.
Generate: hook, body, CTA in the client's tone.

Requirements:
- Use natural, conversational language
- Include CAPS for emphasis where appropriate
- No dashes in formatting
- Make it authentic and engaging
- Keep the same topic and core message
- Address the specific feedback provided

Return only the revised post content:
"""
            
            # Use fine-tuned model if available, otherwise use base model
            model_to_use = EmailSettings.FINE_TUNED_MODEL_ID if hasattr(EmailSettings, 'FINE_TUNED_MODEL_ID') else "gpt-3.5-turbo"
            
            response = self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": "You are an expert LinkedIn content writer who specializes in HR consulting posts. Write in a natural, conversational tone with strategic use of CAPS for emphasis."},
                    {"role": "user", "content": revision_prompt}
                ],
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            revised_post = response.choices[0].message.content.strip()
            
            if len(revised_post) < 50:
                logger.warning("⚠️ Generated post too short, regenerating...")
                return self._generate_revised_post(original_post, feedback)
            
            logger.info(f"✅ Generated revised post ({len(revised_post)} characters)")
            return revised_post
            
        except Exception as e:
            logger.error(f"❌ Error generating revised post: {e}")
            return None
    
    def _update_airtable_with_revision(self, record_id: str, revised_post: str, feedback: str) -> bool:
        """
        Update Airtable record with revised post.
        
        Args:
            record_id: Airtable record ID
            revised_post: The revised post content
            feedback: Original feedback for reference
            
        Returns:
            True if update was successful
        """
        try:
            update_data = {
                "revised_post": revised_post,
                "status": "Revised",
                "version": 2,
                "revision_timestamp": datetime.now(timezone.utc).isoformat(),
                "original_feedback": feedback
            }
            
            success = self.airtable_logger.update_record(record_id, update_data)
            
            if success:
                logger.info(f"✅ Updated Airtable record {record_id} with revision")
                return True
            else:
                logger.error(f"❌ Failed to update Airtable record {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating Airtable: {e}")
            return False
    
    def _notify_client_of_revision(self, record_id: str, revised_post: str) -> bool:
        """
        Send email notification to client about revised post.
        
        Args:
            record_id: Airtable record ID
            revised_post: The revised post content
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Get client email from Airtable record
            record = self.airtable_logger.get_record(record_id)
            if not record:
                logger.warning(f"⚠️ Could not find record {record_id} for email notification")
                return False
            
            client_email = record.get('fields', {}).get('client_email', '')
            if not client_email:
                logger.warning(f"⚠️ No client email found for record {record_id}")
                return False
            
            # Send email using Resend
            email_data = {
                "from": EmailSettings.SENDER_EMAIL,
                "to": client_email,
                "subject": "Here's the updated version of your LinkedIn post ✨",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Your LinkedIn Post Has Been Updated! ✨</h2>
                    
                    <p>Hi there!</p>
                    
                    <p>I've revised your LinkedIn post based on your feedback. Here's the updated version:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="white-space: pre-wrap; margin: 0;">{revised_post}</p>
                    </div>
                    
                    <p><strong>Do you approve this version?</strong></p>
                    
                    <p>If yes, we'll publish it and fine-tune our model to match your style for even better future posts!</p>
                    
                    <p>Best regards,<br>Your Content Team</p>
                </div>
                """
            }
            
            # Send email using Resend API
            headers = {
                "Authorization": f"Bearer {EmailSettings.RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.resend.com/emails",
                headers=headers,
                json=email_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email notification sent for record {record_id}")
                return True
            else:
                logger.error(f"❌ Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending email notification: {e}")
            return False
    
    def check_for_final_approval(self) -> List[Dict]:
        """
        Check for posts that have received final approval.
        
        Returns:
            List of approved posts ready for fine-tuning
        """
        try:
            logger.info("🔍 Checking for final approvals...")
            
            records = self.airtable_logger.get_all_records()
            approved_posts = []
            
            for record in records:
                fields = record.get('fields', {})
                
                status = fields.get('status', '')
                feedback = fields.get('feedback', '').lower()
                
                # Check for final approval
                if (status == "Approved" or 
                    feedback in ['yes', 'approved', 'i like this post a lot, this can be posted']):
                    
                    approved_posts.append({
                        'record_id': record['id'],
                        'fields': fields
                    })
            
            logger.info(f"✅ Found {len(approved_posts)} approved posts for fine-tuning")
            return approved_posts
            
        except Exception as e:
            logger.error(f"❌ Error checking for approvals: {e}")
            return []
    
    def prepare_fine_tuning_data(self, approved_posts: List[Dict]) -> bool:
        """
        Prepare approved posts for fine-tuning by creating JSONL file.
        
        Args:
            approved_posts: List of approved post records
            
        Returns:
            True if preparation was successful
        """
        try:
            logger.info(f"📝 Preparing {len(approved_posts)} posts for fine-tuning...")
            
            fine_tune_entries = []
            
            for post_data in approved_posts:
                fields = post_data['fields']
                
                # Get the final approved post content
                post_content = fields.get('revised_post') or fields.get('post_content', '')
                original_topic = fields.get('original_topic', 'HR consulting topic')
                client_name = fields.get('client_name', 'HR Consultant')
                
                if post_content:
                    # Create fine-tuning entry
                    entry = {
                        "messages": [
                            {
                                "role": "system", 
                                "content": f"Write in the voice of {client_name}."
                            },
                            {
                                "role": "user", 
                                "content": original_topic
                            },
                            {
                                "role": "assistant", 
                                "content": post_content
                            }
                        ]
                    }
                    
                    fine_tune_entries.append(entry)
            
            # Write to JSONL file
            if fine_tune_entries:
                with open(self.fine_tune_queue_file, 'a', encoding='utf-8') as f:
                    for entry in fine_tune_entries:
                        f.write(json.dumps(entry) + '\n')
                
                logger.info(f"✅ Added {len(fine_tune_entries)} entries to fine-tuning queue")
                
                # Update Airtable to mark as queued for fine-tuning
                for post_data in approved_posts:
                    self.airtable_logger.update_record(
                        post_data['record_id'],
                        {"fine_tune_status": "Queued"}
                    )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error preparing fine-tuning data: {e}")
            return False
    
    def run_feedback_loop(self, max_iterations: int = 10, delay_seconds: int = 60):
        """
        Run the complete feedback loop system.
        
        Args:
            max_iterations: Maximum number of monitoring cycles
            delay_seconds: Delay between monitoring cycles
        """
        logger.info("🚀 Starting Feedback Loop System...")
        
        iteration = 0
        while iteration < max_iterations:
            try:
                logger.info(f"🔄 Feedback Loop Iteration {iteration + 1}/{max_iterations}")
                
                # 1. Monitor for new feedback
                pending_feedback = self.monitor_airtable_for_feedback()
                
                # 2. Process feedback
                for feedback_record in pending_feedback:
                    self.process_feedback(feedback_record)
                
                # 3. Check for final approvals
                approved_posts = self.check_for_final_approval()
                
                # 4. Prepare fine-tuning data
                if approved_posts:
                    self.prepare_fine_tuning_data(approved_posts)
                
                # 5. Wait before next iteration
                if iteration < max_iterations - 1:
                    logger.info(f"⏳ Waiting {delay_seconds} seconds before next check...")
                    time.sleep(delay_seconds)
                
                iteration += 1
                
            except KeyboardInterrupt:
                logger.info("⏹️ Feedback loop stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in feedback loop iteration {iteration}: {e}")
                time.sleep(delay_seconds)
                iteration += 1
        
        logger.info("🏁 Feedback Loop System completed")


if __name__ == "__main__":
    # Initialize and run feedback loop
    feedback_loop = FeedbackLoop()
    feedback_loop.run_feedback_loop(max_iterations=5, delay_seconds=30) 