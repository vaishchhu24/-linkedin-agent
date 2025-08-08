#!/usr/bin/env python3
"""
Feedback Loop System - Phase 3
Monitors Airtable for approved posts and adds them to RAG vector store
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import hashlib

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from rag_memory import RAGMemory
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackLoop:
    """Monitors Airtable for approved posts and manages RAG learning."""
    
    def __init__(self):
        """Initialize the feedback loop system."""
        self.airtable_logger = AirtableLogger()
        self.rag_memory = RAGMemory()
        self.client_id = EmailSettings.CLIENT_NAME.lower().replace(" ", "_")
        
        logger.info("🔄 Feedback Loop initialized")
    
    def monitor_airtable_for_approvals(self, hours_back: int = 24) -> List[Dict]:
        """
        Monitor Airtable for recently approved posts.
        
        Args:
            hours_back: How many hours back to look for approvals
            
        Returns:
            List of approved posts that should be added to RAG
        """
        try:
            logger.info(f"🔍 Monitoring Airtable for approvals (last {hours_back} hours)")
            
            # Get all records from Airtable
            all_records = self.airtable_logger.get_all_records()
            
            if not all_records:
                logger.info("📭 No records found in Airtable")
                return []
            
            approved_posts = []
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            for record in all_records:
                try:
                    fields = record.get('fields', {})
                    
                    # Check if post has required fields
                    if not all(key in fields for key in ['post', 'topic', 'timestamp']):
                        continue
                    
                    # Check if feedback indicates approval
                    feedback = fields.get('feedback', '').lower()
                    if not self._is_approval_feedback(feedback):
                        continue
                    
                    # Check if post is recent enough
                    timestamp_str = fields.get('timestamp', '')
                    if not timestamp_str:
                        continue
                    
                    try:
                        # Parse timestamp (handle different formats)
                        if 'UTC' in timestamp_str:
                            post_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
                        else:
                            post_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        
                        if post_time < cutoff_time:
                            continue
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse timestamp '{timestamp_str}': {e}")
                        continue
                    
                    # Check if post is already in RAG store
                    post_hash = self._generate_post_hash(fields['post'])
                    if self.rag_memory.post_exists(post_hash):
                        logger.info(f"📋 Post already in RAG store: {fields.get('topic', 'Unknown')}")
                        continue
                    
                    # This is a new approved post
                    approved_post = {
                        'record_id': record.get('id'),
                        'topic': fields.get('topic', ''),
                        'post': fields.get('post', ''),
                        'timestamp': timestamp_str,
                        'feedback': feedback,
                        'voice_quality': fields.get('voice_quality', 0),
                        'post_quality': fields.get('post_quality', 0),
                        'post_hash': post_hash
                    }
                    
                    approved_posts.append(approved_post)
                    logger.info(f"✅ Found approved post: {approved_post['topic']}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing record {record.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"📊 Found {len(approved_posts)} new approved posts")
            return approved_posts
            
        except Exception as e:
            logger.error(f"❌ Error monitoring Airtable: {e}")
            return []
    
    def _is_approval_feedback(self, feedback: str) -> bool:
        """
        Check if feedback indicates approval.
        
        Args:
            feedback: Feedback text from Airtable
            
        Returns:
            True if feedback indicates approval
        """
        if not feedback:
            return False
        
        feedback_lower = feedback.lower()
        
        # Direct approval indicators
        approval_indicators = [
            'yes', 'approved', 'like', 'love', 'great', 'perfect', 'excellent',
            'good', 'amazing', 'fantastic', 'wonderful', 'outstanding'
        ]
        
        # Check for approval indicators
        for indicator in approval_indicators:
            if indicator in feedback_lower:
                return True
        
        # Check for numerical ratings (7+ indicates approval)
        try:
            # Look for numbers in feedback
            import re
            numbers = re.findall(r'\d+', feedback)
            if numbers:
                rating = int(numbers[0])
                if rating >= 7:
                    return True
        except:
            pass
        
        return False
    
    def _generate_post_hash(self, post_content: str) -> str:
        """
        Generate a hash for the post content to prevent duplicates.
        
        Args:
            post_content: The post content
            
        Returns:
            Hash string
        """
        return hashlib.md5(post_content.encode()).hexdigest()
    
    def add_approved_posts_to_rag(self, approved_posts: List[Dict]) -> bool:
        """
        Add approved posts to the RAG vector store.
        
        Args:
            approved_posts: List of approved posts to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not approved_posts:
                logger.info("📭 No approved posts to add to RAG")
                return True
            
            logger.info(f"📚 Adding {len(approved_posts)} approved posts to RAG store")
            
            for post_data in approved_posts:
                try:
                    # Prepare data for RAG store
                    rag_data = {
                        "topic": post_data['topic'],
                        "post": post_data['post'],
                        "timestamp": post_data['timestamp'],
                        "client_id": self.client_id,
                        "feedback": post_data['feedback'],
                        "voice_quality": post_data.get('voice_quality', 0),
                        "post_quality": post_data.get('post_quality', 0),
                        "post_hash": post_data['post_hash']
                    }
                    
                    # Add to RAG store
                    success = self.rag_memory.add_post(rag_data)
                    
                    if success:
                        logger.info(f"✅ Added to RAG: {post_data['topic']}")
                        
                        # Update Airtable to mark as processed
                        self._mark_as_rag_processed(post_data['record_id'])
                    else:
                        logger.error(f"❌ Failed to add to RAG: {post_data['topic']}")
                        
                except Exception as e:
                    logger.error(f"❌ Error adding post to RAG: {e}")
                    continue
            
            logger.info("🎉 Finished adding approved posts to RAG")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding posts to RAG: {e}")
            return False
    
    def _mark_as_rag_processed(self, record_id: str):
        """
        Mark a record as processed in Airtable.
        
        Args:
            record_id: Airtable record ID
        """
        try:
            # Add a field to indicate RAG processing
            self.airtable_logger.update_record(record_id, {
                "rag_processed": True,
                "rag_processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
        except Exception as e:
            logger.warning(f"⚠️ Could not mark record {record_id} as processed: {e}")
    
    def run_feedback_loop(self, hours_back: int = 24):
        """
        Run the complete feedback loop process.
        
        Args:
            hours_back: How many hours back to look for approvals
        """
        try:
            logger.info("🔄 Starting feedback loop process...")
            
            # Step 1: Monitor Airtable for approvals
            approved_posts = self.monitor_airtable_for_approvals(hours_back)
            
            if not approved_posts:
                logger.info("📭 No new approved posts found")
                return
            
            # Step 2: Add approved posts to RAG
            success = self.add_approved_posts_to_rag(approved_posts)
            
            if success:
                logger.info("✅ Feedback loop completed successfully")
                logger.info(f"📚 Added {len(approved_posts)} posts to RAG store")
            else:
                logger.error("❌ Feedback loop failed")
                
        except Exception as e:
            logger.error(f"❌ Error in feedback loop: {e}")

def main():
    """Main function to run the feedback loop."""
    
    print("🔄 Feedback Loop System - Phase 3")
    print("=" * 50)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("📊 Monitoring Airtable for approved posts")
    print("📚 Adding approved posts to RAG store")
    print("=" * 50)
    
    try:
        feedback_loop = FeedbackLoop()
        feedback_loop.run_feedback_loop(hours_back=24)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main() 