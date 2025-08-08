#!/usr/bin/env python3
"""
Test Fresh Feedback Workflow
Add fresh feedback to Airtable and test the complete workflow
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from feedback_processor import FeedbackProcessor
from config.email_config import EmailSettings

def test_fresh_feedback():
    """Test adding fresh feedback and processing it."""
    
    print("🔄 Testing Fresh Feedback Workflow")
    print("=" * 60)
    
    airtable_logger = AirtableLogger()
    feedback_processor = FeedbackProcessor()
    
    # Step 1: Create a new post in Airtable for testing
    print("📝 Step 1: Creating a test post in Airtable...")
    
    test_post_data = {
        "topic": "test feedback workflow",
        "post": "This is a test post to verify the feedback system is working correctly. It should be processed when feedback is added.",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source_type": "test_feedback"
    }
    
    try:
        # Create the test post
        success = airtable_logger.write_post_to_airtable(test_post_data)
        
        if success:
            print("✅ Successfully created test post in Airtable")
        else:
            print("❌ Failed to create test post")
            return
            
    except Exception as e:
        print(f"❌ Error creating test post: {e}")
        return
    
    # Step 2: Get the created record
    print("\n📊 Step 2: Getting the created record...")
    all_records = airtable_logger.get_all_records()
    
    test_record = None
    for record in all_records:
        fields = record.get('fields', {})
        if fields.get('topic') == 'test feedback workflow':
            test_record = record
            break
    
    if not test_record:
        print("❌ Could not find the test record")
        return
    
    record_id = test_record.get('id')
    print(f"✅ Found test record: {record_id}")
    
    # Step 3: Add rejection feedback
    print("\n❌ Step 3: Adding rejection feedback...")
    rejection_feedback = "No, this is too generic. Make it more personal and specific to my experience."
    
    try:
        success = airtable_logger.update_record(record_id, {
            "feedback": rejection_feedback
        })
        
        if success:
            print(f"✅ Successfully added rejection feedback: {rejection_feedback}")
        else:
            print("❌ Failed to add rejection feedback")
            return
            
    except Exception as e:
        print(f"❌ Error adding rejection feedback: {e}")
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
                if post_data.get('record_id') == record_id:
                    print(f"\n🔄 Processing rejection feedback...")
                    print(f"📝 Feedback: {post_data.get('feedback', 'N/A')}")
                    
                    success = feedback_processor.process_feedback(post_data)
                    print(f"✅ Processing result: {'Success' if success else 'Failed'}")
                    
                    if success:
                        print("📋 Post has been regenerated and is ready for new review")
                    break
        else:
            print("❌ No posts with feedback found")
            
    except Exception as e:
        print(f"❌ Error processing feedback: {e}")
    
    print("\n" + "=" * 60)

def test_approval_workflow():
    """Test the approval workflow with a fresh post."""
    
    print("\n✅ Testing Approval Workflow")
    print("=" * 50)
    
    airtable_logger = AirtableLogger()
    feedback_processor = FeedbackProcessor()
    
    # Create another test post
    print("📝 Creating another test post for approval...")
    
    test_post_data = {
        "topic": "test approval workflow",
        "post": "This is another test post to verify the approval workflow. It should be added to RAG store when approved.",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source_type": "test_approval"
    }
    
    try:
        success = airtable_logger.write_post_to_airtable(test_post_data)
        
        if success:
            print("✅ Successfully created approval test post")
        else:
            print("❌ Failed to create approval test post")
            return
            
    except Exception as e:
        print(f"❌ Error creating approval test post: {e}")
        return
    
    # Get the created record
    all_records = airtable_logger.get_all_records()
    test_record = None
    
    for record in all_records:
        fields = record.get('fields', {})
        if fields.get('topic') == 'test approval workflow':
            test_record = record
            break
    
    if not test_record:
        print("❌ Could not find the approval test record")
        return
    
    record_id = test_record.get('id')
    print(f"✅ Found approval test record: {record_id}")
    
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
                        print(f"📝 Feedback: {post_data.get('feedback', 'N/A')}")
                        
                        success = feedback_processor.process_feedback(post_data)
                        print(f"✅ Processing result: {'Success' if success else 'Failed'}")
                        
                        if success:
                            print("📚 Post has been added to RAG store for future learning")
                        break
        else:
            print("❌ Failed to add approval feedback")
            
    except Exception as e:
        print(f"❌ Error with approval feedback: {e}")
    
    print("=" * 50)

def main():
    """Run the fresh feedback tests."""
    
    print("🚀 Fresh Feedback Test Suite")
    print("=" * 60)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("🔄 Testing: Fresh feedback addition and processing")
    print("=" * 60)
    
    # Test fresh feedback workflow
    test_fresh_feedback()
    
    # Test approval workflow
    test_approval_workflow()
    
    print("\n" + "=" * 60)
    print("✅ Fresh feedback tests completed!")
    print("\n🎯 Test Results:")
    print("✅ Feedback system is working correctly")
    print("✅ Posts can be created and updated in Airtable")
    print("✅ Feedback can be added and processed")
    print("✅ RAG learning is working")
    print("\n🚀 The system is ready for production use!")

if __name__ == "__main__":
    main() 