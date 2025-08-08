#!/usr/bin/env python3
"""
Quick Feedback Processor - Fast and Simple
Only processes the most recent post with feedback
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
import openai
import os

# Set up OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def process_latest_feedback():
    """Process only the most recent post with feedback."""
    print("⚡ Quick Feedback Processor")
    print("=" * 40)
    
    # Initialize Airtable logger
    airtable_logger = AirtableLogger()
    
    # Get all records
    all_records = airtable_logger.get_all_records()
    
    if not all_records:
        print("❌ No records found in Airtable")
        return False
    
    # Find the most recent post with feedback
    most_recent_with_feedback = None
    for record in reversed(all_records):
        fields = record.get('fields', {})
        feedback = fields.get('Feedback', '').strip()
        
        if feedback:
            most_recent_with_feedback = record
            break
    
    if not most_recent_with_feedback:
        print("❌ No posts with feedback found")
        return False
    
    # Get the data
    fields = most_recent_with_feedback.get('fields', {})
    topic = fields.get('Topic', '')
    original_post = fields.get('Post', '')
    feedback = fields.get('Feedback', '').strip()
    
    print(f"📝 Processing feedback:")
    print(f"   Topic: {topic}")
    print(f"   Feedback: {feedback[:100]}...")
    
    # Build simple prompt
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

Return the new post:"""
    
    try:
        print("   🔄 Generating new post...")
        
        # Generate new post using OpenAI directly
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert LinkedIn content creator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        new_post = response.choices[0].message.content.strip()
        
        # Clean up the post
        if new_post.startswith('"') and new_post.endswith('"'):
            new_post = new_post[1:-1]
        
        print(f"   📝 New post length: {len(new_post)} characters")
        print(f"   📄 Preview: {new_post[:100]}...")
        
        # Save to Airtable
        success = airtable_logger.write_post_to_airtable(topic, new_post)
        
        if success:
            print("   ✅ Successfully saved to Airtable")
            print("\n🎯 Quick feedback processing completed!")
            return True
        else:
            print("   ❌ Failed to save to Airtable")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    process_latest_feedback() 