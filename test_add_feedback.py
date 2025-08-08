#!/usr/bin/env python3
"""
Test Adding Feedback to Airtable
Simulates adding feedback to test the feedback processing system
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from feedback_processor import FeedbackProcessor
from config.email_config import EmailSettings

def test_add_feedback():
    """Test adding feedback to Airtable and processing it."""
    
    print("📝 Testing Adding Feedback to Airtable")
    print("=" * 50)
    
    airtable_logger = AirtableLogger()
    feedback_processor = FeedbackProcessor()
    
    # Step 1: Get existing records
    print("📊 Step 1: Getting existing records...")
    all_records = airtable_logger.get_all_records()
    
    if not all_records:
        print("❌ No records found in Airtable")
        return
    
    print(f"✅ Found {len(all_records)} records")
    
    # Step 2: Find a record without feedback
    print("\n🔍 Step 2: Finding a record without feedback...")
    record_to_update = None
    
    for record in all_records:
        fields = record.get('fields', {})
        if not fields.get('feedback') and fields.get('post'):
            record_to_update = record
            break
    
    if not record_to_update:
        print("❌ No records found without feedback")
        return
    
    record_id = record_to_update.get('id')
    fields = record_to_update.get('fields', {})
    
    print(f"✅ Found record to update: {record_id}")
    print(f"📝 Topic: {fields.get('topic', 'N/A')}")
    print(f"📄 Post preview: {fields.get('post', '')[:100]}...")
    
    # Step 3: Add test feedback
    print("\n📝 Step 3: Adding test feedback...")
    test_feedback = "No, this is too generic. Make it more personal and specific to my experience."
    
    try:
        success = airtable_logger.update_record(record_id, {
            "feedback": test_feedback
        })
        
        if success:
            print(f"✅ Successfully added feedback: {test_feedback}")
        else:
            print("❌ Failed to add feedback")
            return
            
    except Exception as e:
        print(f"❌ Error adding feedback: {e}")
        return
    
    # Step 4: Test feedback processing
    print("\n🔄 Step 4: Testing feedback processing...")
    
    try:
        # Monitor for feedback
        posts_with_feedback = feedback_processor.monitor_for_feedback(hours_back=24)
        
        if posts_with_feedback:
            print(f"✅ Found {len(posts_with_feedback)} posts with feedback")
            
            # Process the feedback
            for post_data in posts_with_feedback:
                print(f"\n🔄 Processing feedback for: {post_data.get('topic', 'N/A')}")
                print(f"📝 Feedback: {post_data.get('feedback', 'N/A')}")
                
                success = feedback_processor.process_feedback(post_data)
                print(f"✅ Processing result: {'Success' if success else 'Failed'}")
        else:
            print("❌ No posts with feedback found")
            
    except Exception as e:
        print(f"❌ Error processing feedback: {e}")
    
    print("\n" + "=" * 50)

def test_approval_feedback():
    """Test adding approval feedback."""
    
    print("\n✅ Testing Approval Feedback")
    print("=" * 40)
    
    airtable_logger = AirtableLogger()
    feedback_processor = FeedbackProcessor()
    
    # Find another record without feedback
    all_records = airtable_logger.get_all_records()
    record_to_update = None
    
    for record in all_records:
        fields = record.get('fields', {})
        if not fields.get('feedback') and fields.get('post'):
            record_to_update = record
            break
    
    if not record_to_update:
        print("❌ No records found without feedback")
        return
    
    record_id = record_to_update.get('id')
    fields = record_to_update.get('fields', {})
    
    print(f"✅ Found record to update: {record_id}")
    print(f"📝 Topic: {fields.get('topic', 'N/A')}")
    
    # Add approval feedback
    approval_feedback = "Yes, this is perfect! Love the tone and message."
    
    try:
        success = airtable_logger.update_record(record_id, {
            "feedback": approval_feedback
        })
        
        if success:
            print(f"✅ Successfully added approval feedback: {approval_feedback}")
            
            # Process the feedback
            posts_with_feedback = feedback_processor.monitor_for_feedback(hours_back=24)
            
            if posts_with_feedback:
                for post_data in posts_with_feedback:
                    if post_data.get('record_id') == record_id:
                        print("🔄 Processing approval feedback...")
                        success = feedback_processor.process_feedback(post_data)
                        print(f"✅ Approval processing result: {'Success' if success else 'Failed'}")
                        break
        else:
            print("❌ Failed to add approval feedback")
            
    except Exception as e:
        print(f"❌ Error with approval feedback: {e}")
    
    print("=" * 40)

def main():
    """Run the feedback testing."""
    
    print("🚀 Feedback Testing Suite")
    print("=" * 60)
    
    # Test adding rejection feedback
    test_add_feedback()
    
    # Test adding approval feedback
    test_approval_feedback()
    
    print("\n" + "=" * 60)
    print("✅ Feedback testing completed!")

if __name__ == "__main__":
    main() 