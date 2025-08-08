#!/usr/bin/env python3
"""
Feedback Processor - Enhanced Feedback Loop
Handles client feedback, post regeneration, and RAG learning
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
from content_handler.content_assessor import ContentAssessor
from rag_memory import RAGMemory
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackProcessor:
    """Handles client feedback, post regeneration, and RAG learning."""
    
    def __init__(self):
        """Initialize the feedback processor."""
        self.airtable_logger = AirtableLogger()
        self.post_generator = PostGenerator()
        self.icp_checker = ICPPillarChecker()
        self.content_assessor = ContentAssessor()
        self.rag_memory = RAGMemory()
        self.client_id = EmailSettings.CLIENT_NAME.lower().replace(" ", "_")
        
        logger.info("🔄 Feedback Processor initialized")
    
    def monitor_for_feedback(self, hours_back: int = 24) -> List[Dict]:
        """
        Monitor Airtable for new feedback on posts.
        
        Args:
            hours_back: How many hours back to look for feedback
            
        Returns:
            List of posts with new feedback
        """
        try:
            logger.info(f"🔍 Monitoring Airtable for feedback (last {hours_back} hours)")
            
            # Get all records from Airtable
            all_records = self.airtable_logger.get_all_records()
            
            if not all_records:
                logger.info("📭 No records found in Airtable")
                return []
            
            posts_with_feedback = []
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            for record in all_records:
                try:
                    fields = record.get('fields', {})
                    
                    # Check if post has required fields (using actual Airtable field names)
                    if not all(key in fields for key in ['Post', 'Topic', 'Timestamp']):
                        continue
                    
                    # Check if feedback exists and is recent
                    feedback = fields.get('Feedback', '').strip()
                    if not feedback:
                        continue
                    
                    # Check if post is recent enough
                    timestamp_str = fields.get('Timestamp', '')
                    if not timestamp_str:
                        continue
                    
                    try:
                        # Parse timestamp
                        if 'UTC' in timestamp_str:
                            post_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
                        elif timestamp_str.endswith('Z'):
                            post_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            # Handle timestamp without timezone info
                            post_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                        
                        if post_time < cutoff_time:
                            continue
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse timestamp '{timestamp_str}': {e}")
                        continue
                    
                    # Check if feedback is new (not already processed)
                    # Note: feedback_processed field doesn't exist in current Airtable
                    # In production, you'd add this field to track processed feedback
                    # if fields.get('feedback_processed'):
                    #     continue
                    
                    # This is a new feedback
                    post_with_feedback = {
                        'record_id': record.get('id'),
                        'topic': fields.get('Topic', ''),
                        'post': fields.get('Post', ''),
                        'timestamp': timestamp_str,
                        'feedback': feedback,
                        'voice_quality': fields.get('voice score', 0),
                        'post_quality': fields.get('quality score', 0)
                    }
                    
                    posts_with_feedback.append(post_with_feedback)
                    logger.info(f"📝 Found new feedback: {feedback[:50]}...")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing record {record.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"📊 Found {len(posts_with_feedback)} posts with new feedback")
            return posts_with_feedback
            
        except Exception as e:
            logger.error(f"❌ Error monitoring for feedback: {e}")
            return []
    
    def process_feedback(self, post_data: Dict) -> bool:
        """
        Process feedback for a single post.
        
        Args:
            post_data: Post data with feedback
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            feedback = post_data.get('feedback', '').lower()
            topic = post_data.get('topic', '')
            original_post = post_data.get('post', '')
            record_id = post_data.get('record_id')
            
            logger.info(f"🔄 Processing feedback for topic: {topic}")
            logger.info(f"📝 Feedback: {feedback[:100]}...")
            
            # Determine feedback type
            if self._is_approval_feedback(feedback):
                logger.info("✅ Client approved the post")
                return self._handle_approval(post_data)
            elif self._is_rejection_feedback(feedback):
                logger.info("❌ Client rejected the post - revising based on feedback")
                return self._handle_rejection(post_data)
            else:
                logger.info("🤔 Ambiguous feedback - treating as rejection for regeneration")
                return self._handle_rejection(post_data)
                
        except Exception as e:
            logger.error(f"❌ Error processing feedback: {e}")
            return False
    
    def _is_approval_feedback(self, feedback: str) -> bool:
        """Check if feedback indicates approval."""
        if not feedback:
            return False
        
        approval_indicators = [
            'yes', 'approved', 'like', 'love', 'great', 'perfect', 'excellent',
            'good', 'amazing', 'fantastic', 'wonderful', 'outstanding', 'publish',
            'post it', 'go ahead', 'sounds good', 'looks good'
        ]
        
        feedback_lower = feedback.lower()
        return any(indicator in feedback_lower for indicator in approval_indicators)
    
    def _is_rejection_feedback(self, feedback: str) -> bool:
        """Check if feedback indicates rejection."""
        if not feedback:
            return False
        
        rejection_indicators = [
            'no', 'reject', 'don\'t like', 'not good', 'bad', 'terrible',
            'regenerate', 'rewrite', 'change', 'modify', 'edit', 'fix',
            'not right', 'doesn\'t work', 'try again'
        ]
        
        feedback_lower = feedback.lower()
        return any(indicator in feedback_lower for indicator in rejection_indicators)
    
    def _handle_approval(self, post_data: Dict) -> bool:
        """
        Handle approved post - add to RAG store.
        
        Args:
            post_data: Post data with feedback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🎉 Post approved - adding to RAG store")
            
            # Add to RAG store
            rag_data = {
                "topic": post_data['topic'],
                "post": post_data['post'],
                "timestamp": post_data['timestamp'],
                "client_id": self.client_id,
                "feedback": post_data['feedback'],
                "voice_quality": post_data.get('voice_quality', 0),
                "post_quality": post_data.get('post_quality', 0),
                "post_hash": self._generate_post_hash(post_data['post'])
            }
            
            success = self.rag_memory.add_post(rag_data)
            
            if success:
                logger.info("✅ Successfully added approved post to RAG store")
                
                # Mark as processed in Airtable
                self._mark_feedback_processed(
                    post_data['record_id'],
                    "approved",
                    "Post approved and added to RAG store"
                )
                
                return True
            else:
                logger.error("❌ Failed to add approved post to RAG store")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling approval: {e}")
            return False
    
    def _handle_rejection(self, post_data: Dict) -> bool:
        """
        Handle rejected post - revise based on feedback.
        
        Args:
            post_data: Post data with feedback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🔄 Revising post based on feedback")
            
            # Extract content elements from original topic
            content_elements = self.content_assessor.extract_content_elements(
                post_data.get('topic', '')
            )
            
            # Get ICP and pillar data
            icp_data = self.icp_checker.get_icp_for_topic(post_data['topic'])
            pillar_info = self.icp_checker.get_most_relevant_pillar(post_data['topic'])
            
            # Build revision prompt with feedback
            revision_prompt = self._build_regeneration_prompt(
                post_data['topic'],
                post_data['post'],
                post_data['feedback'],
                icp_data,
                pillar_info
            )
            
            # Revise post using fine-tuned model
            result = self.post_generator._generate_post_with_fallback(revision_prompt)
            
            if not result:
                logger.error("❌ Failed to revise post")
                return False
            
            # Update Airtable with revised post
            update_success = self.airtable_logger.update_record(
                post_data['record_id'],
                {
                    "Post": result,  # Use correct field name with capital P
                    "Feedback": "",  # Clear feedback for new review
                    "quality score": post_data.get('post_quality', 0),  # Keep existing quality score
                    "voice score": post_data.get('voice_quality', 0)  # Keep existing voice score
                }
            )
            
            if update_success:
                logger.info("✅ Successfully revised and updated post")
                logger.info("📋 Revised post is ready for new client review")
                return True
            else:
                logger.error("❌ Failed to update Airtable with revised post")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling rejection: {e}")
            return False
    
    def _build_regeneration_prompt(self, topic: str, original_post: str, feedback: str, 
                                  icp_data: Dict, pillar_info: Dict) -> str:
        """
        Build prompt for post revision based on feedback.
        
        Args:
            topic: Original topic
            original_post: Original post content
            feedback: Client feedback
            icp_data: ICP data
            pillar_info: Pillar information
            
        Returns:
            Revision prompt
        """
        # Get RAG context from all approved posts
        rag_context = self.post_generator._get_rag_context(topic)
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"Here are ALL past posts that the client approved:\n{rag_context}\nStudy these patterns and revise the post to fit naturally with this collection."
        
        prompt = f"""You are {EmailSettings.CLIENT_NAME}, an HR consultant who creates engaging, direct LinkedIn posts.

REVISE THE EXISTING POST based on client feedback. DO NOT create a completely new post.

ORIGINAL POST:
{original_post}

CLIENT FEEDBACK:
{feedback}

INSTRUCTIONS:
- Keep the same core message and structure
- Make specific changes based on the feedback
- If feedback mentions tone, adjust the tone accordingly
- If feedback mentions length, adjust the length
- If feedback mentions specific content, modify that content
- Keep the same topic and main points
- Maintain the same voice and style
- Only change what the feedback specifically requests

Your audience: {icp_data.get('description', 'HR professionals')}
Their pain points: {icp_data.get('pain_points', [])}
Their goals: {icp_data.get('goals', [])}

{rag_section}

REVISION TASK:
Revise the original post above based on the client's feedback. Keep the same core message, topic, and structure. Only make the specific changes requested in the feedback.

Return the revised post:"""

        return prompt
    
    def _generate_post_hash(self, post_content: str) -> str:
        """Generate a hash for the post content."""
        import hashlib
        return hashlib.md5(post_content.encode()).hexdigest()
    
    def _mark_feedback_processed(self, record_id: str, status: str, message: str):
        """Mark feedback as processed in Airtable."""
        try:
            # Check if the feedback tracking fields exist in Airtable
            # For now, we'll skip the Airtable update since the fields don't exist
            # In a production system, you'd add these fields to the Airtable
            logger.info(f"✅ Feedback processed: {status} - {message}")
            logger.info(f"📝 Note: Airtable update skipped - feedback tracking fields not configured")
            
            # If you want to add feedback tracking, you'd need to add these fields to Airtable:
            # - Feedback_Processed (Checkbox)
            # - Feedback_Status (Single line text)
            # - Feedback_Processed_At (Date)
            # - Feedback_Message (Long text)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not mark feedback as processed: {e}")
    
    def run_feedback_loop(self, hours_back: int = 24):
        """
        Run the complete feedback processing loop.
        
        Args:
            hours_back: How many hours back to look for feedback
        """
        try:
            logger.info("🔄 Starting feedback processing loop...")
            
            # Step 1: Monitor for new feedback
            posts_with_feedback = self.monitor_for_feedback(hours_back)
            
            if not posts_with_feedback:
                logger.info("📭 No new feedback found")
                return
            
            # Step 2: Process each feedback
            processed_count = 0
            for post_data in posts_with_feedback:
                success = self.process_feedback(post_data)
                if success:
                    processed_count += 1
            
            logger.info(f"✅ Feedback loop completed: {processed_count}/{len(posts_with_feedback)} processed")
            
            # Cleanup old posts (older than 45 days)
            logger.info("🧹 Running RAG cleanup...")
            removed_count = self.rag_memory.cleanup_old_posts(days_old=45)
            if removed_count > 0:
                logger.info(f"🗑️ Cleaned up {removed_count} old posts from RAG store")
            
        except Exception as e:
            logger.error(f"❌ Error in feedback loop: {e}")

def main():
    """Main function to run the feedback processor."""
    
    print("🔄 Feedback Processor - Enhanced Feedback Loop")
    print("=" * 50)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("📊 Monitoring Airtable for client feedback")
    print("🔄 Regenerating posts based on feedback")
    print("📚 Adding approved posts to RAG store")
    print("=" * 50)
    
    try:
        feedback_processor = FeedbackProcessor()
        feedback_processor.run_feedback_loop(hours_back=24)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main() 