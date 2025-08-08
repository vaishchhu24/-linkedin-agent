#!/usr/bin/env python3
"""
Automated Feedback Processor
Reads feedback from Airtable, regenerates posts, and sends them back
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoFeedbackProcessor:
    def __init__(self):
        self.airtable_logger = AirtableLogger()
        self.post_generator = PostGenerator()
        self.icp_checker = ICPPillarChecker()
    
    def process_all_feedback(self):
        """Process only the most recent post with feedback in Airtable."""
        print("🔄 Automated Feedback Processor - Most Recent Post Only")
        print("=" * 60)
        
        # Get all records from Airtable
        all_records = self.airtable_logger.get_all_records()
        
        if not all_records:
            print("❌ No records found in Airtable")
            return False
        
        # Find the most recent post with feedback
        most_recent_with_feedback = None
        for record in reversed(all_records):  # Start from most recent
            fields = record.get('fields', {})
            feedback = fields.get('Feedback', '').strip()
            
            if feedback:
                most_recent_with_feedback = record
                break
        
        if not most_recent_with_feedback:
            print("❌ No posts with feedback found in Airtable")
            return False
        
        # Process the most recent post with feedback
        fields = most_recent_with_feedback.get('fields', {})
        feedback = fields.get('Feedback', '').strip()
        
        print(f"📝 Processing most recent post with feedback:")
        print(f"   Record ID: {most_recent_with_feedback.get('id')}")
        print(f"   Topic: {fields.get('Topic', 'N/A')}")
        print(f"   Feedback: {feedback[:100]}...")
        
        success = self.process_single_feedback(most_recent_with_feedback, fields, feedback)
        
        if success:
            print(f"\n✅ Successfully processed most recent feedback!")
        else:
            print(f"\n❌ Failed to process feedback!")
        
        return success
    
    def process_single_feedback(self, record, fields, feedback):
        """Process feedback for a single post."""
        try:
            record_id = record.get('id')
            topic = fields.get('Topic', '')
            original_post = fields.get('Post', '')
            
            # Get ICP and pillar data
            icp_data = self.icp_checker.get_icp_for_topic(topic)
            pillar_data = self.icp_checker.get_most_relevant_pillar(topic)
            
            # Build regeneration prompt with feedback
            regeneration_prompt = self._build_regeneration_prompt(
                original_post, feedback, topic, icp_data, pillar_data
            )
            
            # Generate new post
            new_post = self.post_generator._generate_with_fine_tuned_model(regeneration_prompt)
            
            if not new_post:
                print("   ❌ Failed to generate new post")
                return False
            
            # Clean up the post
            new_post = new_post.strip()
            if new_post.startswith('"') and new_post.endswith('"'):
                new_post = new_post[1:-1]
            
            print(f"   📝 New post length: {len(new_post)} characters")
            print(f"   📄 Preview: {new_post[:100]}...")
            
            # Save to Airtable
            success = self.airtable_logger.write_post_to_airtable(topic, new_post)
            
            if success:
                print("   ✅ Successfully saved to Airtable")
                return True
            else:
                print("   ❌ Failed to save to Airtable")
                return False
                
        except Exception as e:
            print(f"   ❌ Error processing feedback: {e}")
            return False
    
    def _build_regeneration_prompt(self, original_post, feedback, topic, icp_data, pillar_data):
        """Build a prompt for regenerating the post based on feedback."""
        
        # Get RAG context for tone adaptation
        rag_context = self.post_generator._get_rag_context(topic)
        
        # Build RAG section
        rag_section = ""
        if rag_context:
            rag_section = f"""CRITICAL TONE ADAPTATION:

Here are ALL past posts that the client approved:
{rag_context}

STUDY THESE APPROVED POSTS AND COPY THEIR EXACT:
- Writing style and tone
- Sentence structure and length
- Use of CAPS and emphasis
- Conversational elements and pauses
- Authentic voice and personality
- Storytelling approach
- Emotional expression
- Professional yet personal balance

CREATE A NEW POST that:
- SOUNDS EXACTLY LIKE the client's voice from the examples above
- Uses the SAME writing patterns and style
- Maintains the SAME level of authenticity and vulnerability
- Matches the SAME tone, humor, and approach
- Feels like it was written by the SAME person

DO NOT copy specific content, but DO copy the exact writing style, tone, and voice."""
        
        prompt = f"""You are an expert LinkedIn content creator.

REGENERATE THE POST based on client feedback.

ORIGINAL POST:
{original_post}

CLIENT FEEDBACK:
{feedback}

INSTRUCTIONS:
- Create a COMPLETELY NEW post on the same topic
- Address the specific feedback provided
- Keep the same core topic and message
- Make it significantly different from the original
- Ensure it's engaging and authentic
- 400-800 words for comprehensive posts
- Use CAPS sparingly for emphasis
- Include conversational elements

Your audience: {icp_data.get('description', 'HR professionals')}

{rag_section}

Return the new post:"""
        
        return prompt

def main():
    """Main function to run the automated feedback processor."""
    processor = AutoFeedbackProcessor()
    success = processor.process_all_feedback()
    
    if success:
        print("\n🎯 Automated feedback processing completed successfully!")
    else:
        print("\n❌ Automated feedback processing failed!")

if __name__ == "__main__":
    main() 