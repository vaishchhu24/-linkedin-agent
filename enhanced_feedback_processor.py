#!/usr/bin/env python3
"""
Enhanced Feedback Processor - Auto-Regeneration System
Automatically regenerates posts when feedback is "no" and continues until "yes"
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
from content_handler.insight_fetcher import InsightFetcher
from rag_memory import RAGMemory
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFeedbackProcessor:
    """Enhanced feedback processor with auto-regeneration until approval."""
    
    def __init__(self):
        """Initialize the enhanced feedback processor."""
        self.airtable_logger = AirtableLogger()
        self.post_generator = PostGenerator()
        self.icp_checker = ICPPillarChecker()
        self.content_assessor = ContentAssessor()
        self.insight_fetcher = InsightFetcher()
        self.rag_memory = RAGMemory()
        self.client_id = EmailSettings.CLIENT_NAME.lower().replace(" ", "_")
        
        logger.info("🔄 Enhanced Feedback Processor initialized")
    
    def monitor_for_feedback(self, hours_back: int = 24) -> List[Dict]:
        """
        Monitor Airtable for new feedback on posts.
        
        Args:
            hours_back: How many hours back to look for feedback
            
        Returns:
            List of posts with new feedback (most recent feedback first)
        """
        try:
            logger.info(f"🔍 Monitoring Airtable for feedback (most recent feedback first)")
            
            # Get all records from Airtable
            all_records = self.airtable_logger.get_all_records()
            
            if not all_records:
                logger.info("📭 No records found in Airtable")
                return []
            
            posts_with_feedback = []
            
            # Check all records for feedback, starting from most recent
            for record in reversed(all_records):
                try:
                    fields = record.get('fields', {})
                    
                    # Check if post has required fields
                    if not all(key in fields for key in ['Post', 'Topic', 'Timestamp']):
                        continue
                    
                    # Check if feedback exists
                    feedback = fields.get('Feedback', '').strip()
                    if not feedback:
                        continue
                    
                    # This is a post with feedback
                    post_with_feedback = {
                        'record_id': record.get('id'),
                        'topic': fields.get('Topic', ''),
                        'post': fields.get('Post', ''),
                        'timestamp': fields.get('Timestamp', ''),
                        'feedback': feedback,
                        'voice_quality': fields.get('voice score', 0),
                        'post_quality': fields.get('quality score', 0),
                        'regeneration_count': fields.get('regeneration_count', 0)
                    }
                    
                    posts_with_feedback.append(post_with_feedback)
                    logger.info(f"📝 Found feedback: {feedback[:50]}... on topic: {fields.get('Topic', 'N/A')}")
                    
                    # Only process the most recent feedback to avoid duplicates
                    break
                    
                except Exception as e:
                    logger.error(f"❌ Error processing record {record.get('id', 'unknown')}: {e}")
            
            logger.info(f"📊 Found {len(posts_with_feedback)} posts with feedback (most recent feedback first)")
            return posts_with_feedback
            
        except Exception as e:
            logger.error(f"❌ Error monitoring for feedback: {e}")
            return []
    
    def process_feedback(self, post_data: Dict) -> bool:
        """
        Process feedback for a single post with auto-regeneration.
        
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
            regeneration_count = post_data.get('regeneration_count', 0)
            
            logger.info(f"🔄 Processing feedback for topic: {topic}")
            logger.info(f"📝 Feedback: {feedback[:100]}...")
            logger.info(f"🔄 Regeneration count: {regeneration_count}")
            
            # Determine feedback type
            if self._is_approval_feedback(feedback):
                logger.info("✅ Client approved the post - adding to RAG store")
                return self._handle_approval(post_data)
            elif self._is_rejection_feedback(feedback):
                logger.info("❌ Client rejected the post - regenerating with feedback")
                return self._handle_rejection_and_regenerate(post_data)
            else:
                logger.info("🤔 Ambiguous feedback - treating as rejection for regeneration")
                return self._handle_rejection_and_regenerate(post_data)
                
        except Exception as e:
            logger.error(f"❌ Error processing feedback: {e}")
            return False
    
    def _is_approval_feedback(self, feedback: str) -> bool:
        """Check if feedback indicates approval."""
        if not feedback:
            return False
        
        # Check for explicit rejection first
        rejection_phrases = [
            'no,', 'not good', 'not great', 'not perfect', 'not excellent',
            'doesn\'t sound good', 'doesn\'t look good', 'not what i wanted'
        ]
        
        feedback_lower = feedback.lower()
        for phrase in rejection_phrases:
            if phrase in feedback_lower:
                return False
        
        approval_indicators = [
            'yes', 'approved', 'like', 'love', 'great', 'perfect', 'excellent',
            'good', 'amazing', 'fantastic', 'wonderful', 'outstanding', 'publish',
            'post it', 'go ahead', 'sounds good', 'looks good', 'perfect',
            'that works', 'good to go', 'ready to post'
        ]
        
        return any(indicator in feedback_lower for indicator in approval_indicators)
    
    def _is_rejection_feedback(self, feedback: str) -> bool:
        """Check if feedback indicates rejection."""
        if not feedback:
            return False
        
        rejection_indicators = [
            'no', 'reject', 'don\'t like', 'not good', 'bad', 'terrible',
            'regenerate', 'rewrite', 'change', 'modify', 'edit', 'fix',
            'not right', 'doesn\'t work', 'try again', 'different',
            'not what i wanted', 'not the right tone', 'too long', 'too short'
        ]
        
        feedback_lower = feedback.lower()
        return any(indicator in feedback_lower for indicator in rejection_indicators)
    
    def _handle_approval(self, post_data: Dict) -> bool:
        """
        Handle approved post - add to RAG store and mark as approved.
        
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
                
                # Mark as approved in Airtable (using only available fields)
                update_success = self.airtable_logger.update_record(
                    post_data['record_id'],
                    {
                        # Keep feedback history (don't clear)
                    }
                )
                
                if update_success:
                    logger.info("✅ Successfully marked post as approved in Airtable")
                    return True
                else:
                    logger.error("❌ Failed to mark post as approved in Airtable")
                    return False
            else:
                logger.error("❌ Failed to add approved post to RAG store")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling approval: {e}")
            return False
    
    def _handle_rejection_and_regenerate(self, post_data: Dict) -> bool:
        """
        Handle rejected post - regenerate with feedback and update Airtable.
        
        Args:
            post_data: Post data with feedback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🔄 Regenerating post based on feedback")
            
            # Increment regeneration count
            regeneration_count = post_data.get('regeneration_count', 0) + 1
            
            # Check if we've hit the maximum regeneration limit
            max_regenerations = 5
            if regeneration_count > max_regenerations:
                logger.warning(f"⚠️ Maximum regenerations ({max_regenerations}) reached for topic: {post_data['topic']}")
                return self._handle_max_regenerations_reached(post_data)
            
            # Skip complex processing for regeneration - use simple approach
            icp_data = {"description": "HR professionals", "pain_points": [], "goals": []}
            pillar_info = {"name": "general", "title": "HR Consulting"}
            insights = []
            
            # Build regeneration prompt with feedback
            regeneration_prompt = self._build_regeneration_prompt(
                post_data['topic'],
                post_data['post'],
                post_data['feedback'],
                icp_data,
                pillar_info,
                insights,
                regeneration_count
            )
            
            # Generate new post using fast model
            result = self.post_generator._generate_with_fine_tuned_model(regeneration_prompt)
            
            if not result:
                logger.error("❌ Failed to regenerate post")
                return False
            
            # Update Airtable with regenerated post (using only available fields)
            update_success = self.airtable_logger.update_record(
                post_data['record_id'],
                {
                    "Post": result,  # New regenerated post
                    # Keep feedback history (don't clear)
                }
            )
            
            if update_success:
                logger.info(f"✅ Successfully regenerated post (attempt {regeneration_count})")
                logger.info("📋 Regenerated post is ready for new client review")
                logger.info(f"📝 New post length: {len(result)} characters")
                return True
            else:
                logger.error("❌ Failed to update Airtable with regenerated post")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling rejection and regeneration: {e}")
            return False
    
    def _handle_max_regenerations_reached(self, post_data: Dict) -> bool:
        """
        Handle case when maximum regenerations are reached.
        
        Args:
            post_data: Post data with feedback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.warning("⚠️ Maximum regenerations reached - marking for manual review")
            
            # Update Airtable to mark for manual review (using only available fields)
            update_success = self.airtable_logger.update_record(
                post_data['record_id'],
                {
                    "Feedback": "MAX_REGENERATIONS_REACHED - Manual review needed"
                }
            )
            
            if update_success:
                logger.info("✅ Marked post for manual review due to max regenerations")
                return True
            else:
                logger.error("❌ Failed to mark post for manual review")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling max regenerations: {e}")
            return False
    
    def _build_regeneration_prompt(self, topic: str, original_post: str, feedback: str, 
                                  icp_data: Dict, pillar_info: Dict, insights: Dict, 
                                  regeneration_count: int) -> str:
        """
        Build prompt for post regeneration based on feedback.
        
        Args:
            topic: Original topic
            original_post: Original post content
            feedback: Client feedback
            icp_data: ICP data
            pillar_info: Pillar information
            insights: Topic insights
            regeneration_count: Number of regeneration attempts
            
        Returns:
            Regeneration prompt
        """
        # Get RAG context from ALL approved posts for tone learning
        rag_context = self.post_generator._get_rag_context(topic)
        
        # Build RAG context section
        rag_section = ""
        if rag_context and isinstance(rag_context, str):
            rag_section = f"Here are ALL past posts that the client approved:\n{rag_context}\nStudy these patterns and create a post that fits naturally with this collection."
        elif rag_context and isinstance(rag_context, list):
            # Handle list format
            rag_text = "\n\n".join([str(item) for item in rag_context])
            rag_section = f"Here are ALL past posts that the client approved:\n{rag_text}\nStudy these patterns and create a post that fits naturally with this collection."
        
        # Build insights section
        insights_section = ""
        if insights:
            if isinstance(insights, dict) and insights.get('insights'):
                insights_section = f"Recent insights on this topic:\n{insights.get('insights', '')}\n"
            elif isinstance(insights, list):
                insights_text = "\n".join([str(insight) for insight in insights])
                insights_section = f"Recent insights on this topic:\n{insights_text}\n"
        
        # Build feedback analysis
        feedback_analysis = self._analyze_feedback(feedback)
        
        prompt = f"""You are {EmailSettings.CLIENT_NAME}, an HR consultant.

REGENERATE this post based on client feedback:

ORIGINAL POST:
{original_post}

CLIENT FEEDBACK:
{feedback}

INSTRUCTIONS:
- Create a NEW post on the same topic
- Address the feedback: {feedback_analysis}
- Make it different from the original
- Keep it engaging and authentic

Return the new post:"""

        return prompt
    
    def _analyze_feedback(self, feedback: str) -> str:
        """
        Analyze feedback to provide guidance for regeneration.
        
        Args:
            feedback: Client feedback
            
        Returns:
            Feedback analysis
        """
        feedback_lower = feedback.lower()
        
        analysis = []
        
        # Tone analysis
        if any(word in feedback_lower for word in ['tone', 'voice', 'sounds']):
            if any(word in feedback_lower for word in ['formal', 'professional', 'business']):
                analysis.append("- Adjust tone to be more professional and business-like")
            elif any(word in feedback_lower for word in ['casual', 'friendly', 'conversational']):
                analysis.append("- Make tone more casual and conversational")
            elif any(word in feedback_lower for word in ['direct', 'straightforward']):
                analysis.append("- Make tone more direct and straightforward")
        
        # Length analysis
        if any(word in feedback_lower for word in ['long', 'lengthy', 'too much']):
            analysis.append("- Make the post shorter and more concise")
        elif any(word in feedback_lower for word in ['short', 'brief', 'not enough']):
            analysis.append("- Make the post longer with more detail")
        
        # Content analysis
        if any(word in feedback_lower for word in ['story', 'example', 'experience']):
            analysis.append("- Include more personal stories or examples")
        elif any(word in feedback_lower for word in ['tips', 'advice', 'strategies']):
            analysis.append("- Focus more on actionable tips and strategies")
        elif any(word in feedback_lower for word in ['different', 'another', 'alternative']):
            analysis.append("- Take a completely different approach to the topic")
        
        if not analysis:
            analysis.append("- Create a fresh take on the topic")
        
        return "\n".join(analysis)
    
    def _generate_post_hash(self, post_content: str) -> str:
        """Generate a hash for the post content."""
        import hashlib
        return hashlib.md5(post_content.encode()).hexdigest()
    
    def run_enhanced_feedback_loop(self, hours_back: int = 24):
        """
        Run the complete enhanced feedback processing loop.
        
        Args:
            hours_back: How many hours back to look for feedback (ignored, only checks most recent)
        """
        try:
            logger.info("🔄 Starting enhanced feedback processing loop (most recent post only)...")
            
            # Step 1: Monitor for new feedback (most recent post only)
            posts_with_feedback = self.monitor_for_feedback(hours_back)
            
            if not posts_with_feedback:
                logger.info("📭 No new feedback found")
                return
            
            # Step 2: Process each feedback
            processed_count = 0
            regenerated_count = 0
            approved_count = 0
            
            for post_data in posts_with_feedback:
                success = self.process_feedback(post_data)
                if success:
                    processed_count += 1
                    
                    # Track statistics
                    if self._is_approval_feedback(post_data.get('feedback', '')):
                        approved_count += 1
                    else:
                        regenerated_count += 1
            
            logger.info(f"✅ Enhanced feedback loop completed:")
            logger.info(f"   📊 Total processed: {processed_count}/{len(posts_with_feedback)}")
            logger.info(f"   ✅ Approved: {approved_count}")
            logger.info(f"   🔄 Regenerated: {regenerated_count}")
            
            # Cleanup old posts (older than 45 days)
            logger.info("🧹 Running RAG cleanup...")
            removed_count = self.rag_memory.cleanup_old_posts(days_old=45)
            if removed_count > 0:
                logger.info(f"🗑️ Cleaned up {removed_count} old posts from RAG store")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced feedback loop: {e}")

def main():
    """Main function to run the enhanced feedback processor."""
    
    print("🔄 Enhanced Feedback Processor - Auto-Regeneration System")
    print("=" * 60)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("📊 Monitoring Airtable for client feedback")
    print("🔄 Auto-regenerating posts when feedback is 'no'")
    print("✅ Stopping regeneration when feedback is 'yes'")
    print("📚 Adding approved posts to RAG store")
    print("=" * 60)
    
    try:
        feedback_processor = EnhancedFeedbackProcessor()
        feedback_processor.run_enhanced_feedback_loop(hours_back=24)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main() 