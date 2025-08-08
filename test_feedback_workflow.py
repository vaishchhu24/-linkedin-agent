#!/usr/bin/env python3
"""
Test Complete Feedback Workflow
Simulates the entire feedback process from adding feedback to processing it
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from feedback_processor import FeedbackProcessor
from config.email_config import EmailSettings

def test_complete_feedback_workflow():
    """Test the complete feedback workflow."""
    
    print("🔄 Testing Complete Feedback Workflow")
    print("=" * 60)
    
    airtable_logger = AirtableLogger()
    feedback_processor = FeedbackProcessor()
    
    # Step 1: Find a record to add feedback to
    print("📊 Step 1: Finding a record to add feedback to...")
    all_records = airtable_logger.get_all_records()
    
    if not all_records:
        print("❌ No records found in Airtable")
        return
    
    # Find a record without feedback
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
    
    # Step 2: Add rejection feedback
    print("\n❌ Step 2: Adding rejection feedback...")
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
    
    # Step 3: Test feedback processing
    print("\n🔄 Step 3: Testing feedback processing...")
    
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
    """Test the approval workflow."""
    
    print("\n✅ Testing Approval Workflow")
    print("=" * 50)
    
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

def test_feedback_classification():
    """Test feedback classification with various examples."""
    
    print("\n🎯 Testing Feedback Classification")
    print("=" * 50)
    
    feedback_processor = FeedbackProcessor()
    
    # Test various feedback examples
    test_cases = [
        # Approval examples
        ("Yes, this is perfect!", "approval"),
        ("I love it, approved", "approval"),
        ("Great post, publish it", "approval"),
        ("Looks good to me", "approval"),
        ("Excellent work", "approval"),
        ("Go ahead and post it", "approval"),
        
        # Rejection examples
        ("No, this doesn't work", "rejection"),
        ("Please regenerate this", "rejection"),
        ("I don't like the tone", "rejection"),
        ("Can you rewrite this?", "rejection"),
        ("Not quite right", "rejection"),
        ("Try again", "rejection"),
        
        # Ambiguous examples
        ("Maybe", "ambiguous"),
        ("I'm not sure", "ambiguous"),
        ("It's okay", "ambiguous"),
    ]
    
    print("📝 Testing feedback classification:")
    for feedback, expected in test_cases:
        is_approval = feedback_processor._is_approval_feedback(feedback)
        is_rejection = feedback_processor._is_rejection_feedback(feedback)
        
        status = "✅ Approval" if is_approval else "❌ Rejection" if is_rejection else "🤔 Ambiguous"
        print(f"  '{feedback}' -> {status}")
    
    print("=" * 50)

def test_rag_learning():
    """Test RAG learning with approved posts."""
    
    print("\n📚 Testing RAG Learning")
    print("=" * 40)
    
    feedback_processor = FeedbackProcessor()
    
    # Check RAG store stats
    try:
        stats = feedback_processor.rag_memory.get_stats()
        print("📊 RAG Store Statistics:")
        print(f"  Total posts: {stats.get('total_posts', 0)}")
        print(f"  Unique clients: {stats.get('unique_clients', 0)}")
        print(f"  Average quality: {stats.get('avg_quality', 0)}")
        print(f"  FAISS available: {stats.get('faiss_available', False)}")
        
        if stats.get('total_posts', 0) > 0:
            print("✅ RAG store has approved posts for learning")
        else:
            print("📭 RAG store is empty - no approved posts yet")
            
    except Exception as e:
        print(f"❌ Error getting RAG stats: {e}")
    
    print("=" * 40)

def main():
    """Run the complete feedback workflow test."""
    
    print("🚀 Complete Feedback Workflow Test")
    print("=" * 70)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("🔄 Testing: Feedback addition, processing, and RAG learning")
    print("=" * 70)
    
    # Test complete feedback workflow
    test_complete_feedback_workflow()
    
    # Test approval workflow
    test_approval_workflow()
    
    # Test feedback classification
    test_feedback_classification()
    
    # Test RAG learning
    test_rag_learning()
    
    print("\n" + "=" * 70)
    print("✅ Complete feedback workflow test completed!")
    print("\n🎯 Next Steps:")
    print("1. Check Airtable to see the processed feedback")
    print("2. Run the automated workflow to see it in action:")
    print("   python3 start_complete_workflow.py")
    print("3. Add more feedback in Airtable to test further")

if __name__ == "__main__":
    main() 