#!/usr/bin/env python3
"""
Test Most Recent Feedback Processing
Demonstrates how the system only processes feedback on the most recent post
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_feedback_processor import EnhancedFeedbackProcessor
from airtable_logger import AirtableLogger

def test_most_recent_feedback():
    """Test the most recent feedback processing."""
    print("🧪 Testing Most Recent Feedback Processing")
    print("=" * 60)
    
    # Initialize components
    feedback_processor = EnhancedFeedbackProcessor()
    airtable_logger = AirtableLogger()
    
    print("📊 Current Airtable Status:")
    print("-" * 40)
    
    # Get all records
    all_records = airtable_logger.get_all_records()
    print(f"📋 Total records in Airtable: {len(all_records)}")
    
    # Find records with feedback
    feedback_records = [r for r in all_records if 'Feedback' in r.get('fields', {}) and r.get('fields', {}).get('Feedback', '').strip()]
    print(f"📝 Records with feedback: {len(feedback_records)}")
    
    # Show most recent record
    if all_records:
        most_recent = all_records[-1]
        fields = most_recent.get('fields', {})
        print(f"\n📋 Most Recent Record:")
        print(f"   ID: {most_recent.get('id')}")
        print(f"   Topic: {fields.get('Topic', 'N/A')}")
        print(f"   Has Feedback: {'Yes' if 'Feedback' in fields and fields.get('Feedback', '').strip() else 'No'}")
        if 'Feedback' in fields and fields.get('Feedback', '').strip():
            print(f"   Feedback: {fields.get('Feedback', '')}")
    
    print("\n🔍 Testing Feedback Processing:")
    print("-" * 40)
    
    # Test the feedback monitoring
    posts_with_feedback = feedback_processor.monitor_for_feedback()
    
    if posts_with_feedback:
        print(f"✅ Found {len(posts_with_feedback)} posts with feedback (most recent only)")
        for post in posts_with_feedback:
            print(f"   Topic: {post['topic']}")
            print(f"   Feedback: {post['feedback']}")
            
            # Test processing
            print(f"   Processing feedback...")
            success = feedback_processor.process_feedback(post)
            if success:
                print(f"   ✅ Feedback processed successfully")
            else:
                print(f"   ❌ Failed to process feedback")
    else:
        print("📭 No feedback found on most recent post")
    
    print("\n💡 How to Test:")
    print("-" * 40)
    print("1. Add a new post to Airtable (most recent)")
    print("2. Add 'no' feedback to that post")
    print("3. Run the enhanced feedback processor")
    print("4. It will automatically regenerate the post")
    
    return True

if __name__ == "__main__":
    test_most_recent_feedback() 