#!/usr/bin/env python3
"""
Debug Feedback Processing
Check what feedback exists and why it's not being processed
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from feedback_processor import FeedbackProcessor
from config.email_config import EmailSettings

def debug_feedback_processing():
    """Debug the feedback processing logic."""
    
    print("🔍 Debugging Feedback Processing")
    print("=" * 50)
    
    airtable_logger = AirtableLogger()
    feedback_processor = FeedbackProcessor()
    
    # Step 1: Get all records and check feedback
    print("📊 Step 1: Analyzing all records...")
    all_records = airtable_logger.get_all_records()
    
    if not all_records:
        print("❌ No records found")
        return
    
    print(f"✅ Found {len(all_records)} records")
    
    # Step 2: Check feedback field values
    print("\n📝 Step 2: Checking feedback field values...")
    
    feedback_records = []
    no_feedback_records = []
    
    for record in all_records:
        fields = record.get('fields', {})
        feedback = fields.get('feedback', '').strip()
        
        if feedback:
            feedback_records.append({
                'id': record.get('id'),
                'topic': fields.get('topic', 'N/A'),
                'feedback': feedback,
                'timestamp': fields.get('timestamp', 'N/A'),
                'feedback_processed': fields.get('feedback_processed', False)
            })
        else:
            no_feedback_records.append({
                'id': record.get('id'),
                'topic': fields.get('topic', 'N/A'),
                'timestamp': fields.get('timestamp', 'N/A')
            })
    
    print(f"📝 Records WITH feedback: {len(feedback_records)}")
    print(f"📝 Records WITHOUT feedback: {len(no_feedback_records)}")
    
    # Step 3: Show sample feedback
    if feedback_records:
        print("\n📋 Sample feedback records:")
        for i, record in enumerate(feedback_records[:5], 1):
            print(f"  {i}. ID: {record['id']}")
            print(f"     Topic: {record['topic']}")
            print(f"     Feedback: {record['feedback']}")
            print(f"     Processed: {record['feedback_processed']}")
            print(f"     Timestamp: {record['timestamp']}")
            print()
    
    # Step 4: Check why feedback isn't being processed
    print("🔍 Step 4: Checking why feedback isn't being processed...")
    
    # Test the feedback monitoring logic
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    print(f"⏰ Cutoff time: {cutoff_time}")
    
    recent_feedback = []
    for record in feedback_records:
        try:
            timestamp_str = record['timestamp']
            if 'UTC' in timestamp_str:
                post_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
            else:
                post_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            if post_time > cutoff_time:
                recent_feedback.append(record)
                
        except Exception as e:
            print(f"⚠️ Error parsing timestamp '{timestamp_str}': {e}")
    
    print(f"📊 Recent feedback (last 24h): {len(recent_feedback)}")
    
    # Step 5: Test feedback classification
    print("\n🎯 Step 5: Testing feedback classification...")
    
    if recent_feedback:
        for record in recent_feedback[:3]:
            feedback = record['feedback'].lower()
            is_approval = feedback_processor._is_approval_feedback(feedback)
            is_rejection = feedback_processor._is_rejection_feedback(feedback)
            
            print(f"📝 Feedback: {record['feedback']}")
            print(f"   Approval: {is_approval}")
            print(f"   Rejection: {is_rejection}")
            print()
    
    # Step 6: Test the actual monitoring function
    print("🔄 Step 6: Testing feedback monitoring function...")
    
    try:
        posts_with_feedback = feedback_processor.monitor_for_feedback(hours_back=24)
        print(f"📊 monitor_for_feedback returned: {len(posts_with_feedback)} posts")
        
        if posts_with_feedback:
            for post in posts_with_feedback:
                print(f"  - Topic: {post.get('topic', 'N/A')}")
                print(f"    Feedback: {post.get('feedback', 'N/A')}")
                print(f"    Record ID: {post.get('record_id', 'N/A')}")
        else:
            print("📭 No posts returned by monitor_for_feedback")
            
    except Exception as e:
        print(f"❌ Error in monitor_for_feedback: {e}")
    
    print("=" * 50)

def test_feedback_processing_with_real_data():
    """Test processing with real feedback data."""
    
    print("\n🔄 Testing Feedback Processing with Real Data")
    print("=" * 50)
    
    feedback_processor = FeedbackProcessor()
    
    # Get real feedback data
    posts_with_feedback = feedback_processor.monitor_for_feedback(hours_back=24)
    
    if posts_with_feedback:
        print(f"📊 Processing {len(posts_with_feedback)} posts with feedback...")
        
        for i, post_data in enumerate(posts_with_feedback, 1):
            print(f"\n🔄 Processing post {i}:")
            print(f"  Topic: {post_data.get('topic', 'N/A')}")
            print(f"  Feedback: {post_data.get('feedback', 'N/A')}")
            
            # Process the feedback
            success = feedback_processor.process_feedback(post_data)
            print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
    else:
        print("📭 No posts with feedback to process")
    
    print("=" * 50)

def main():
    """Run the debug tests."""
    
    print("🚀 Feedback Debug Suite")
    print("=" * 60)
    
    # Debug feedback processing
    debug_feedback_processing()
    
    # Test with real data
    test_feedback_processing_with_real_data()
    
    print("\n" + "=" * 60)
    print("✅ Feedback debug completed!")

if __name__ == "__main__":
    main() 