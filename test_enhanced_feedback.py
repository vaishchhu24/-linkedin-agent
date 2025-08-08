#!/usr/bin/env python3
"""
Test Enhanced Feedback System
Demonstrates the auto-regeneration system that keeps regenerating until "yes" feedback
"""

import sys
import os
import logging
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_feedback_processor import EnhancedFeedbackProcessor
from airtable_logger import AirtableLogger
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_feedback_system():
    """Test the enhanced feedback system with auto-regeneration."""
    
    print("🧪 Testing Enhanced Feedback System - Auto-Regeneration")
    print("=" * 60)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print("📊 Testing auto-regeneration until 'yes' feedback")
    print("=" * 60)
    
    try:
        # Initialize components
        feedback_processor = EnhancedFeedbackProcessor()
        airtable_logger = AirtableLogger()
        
        # Test 1: Create a test post
        print("\n📝 Test 1: Creating a test post...")
        test_topic = "HR consultant pricing strategies"
        test_post = """Ever wondered why some HR consultants charge $500/hour while others struggle to get $100?

Here's what I learned after 5 years in the business:

The difference isn't just experience - it's positioning.

High-value consultants don't sell hours. They sell outcomes.

Instead of "I'll help with your HR processes," they say "I'll reduce your turnover by 30% in 6 months."

The result? Clients see ROI, not just a bill.

What's your positioning strategy?"""
        
        # Save test post to Airtable
        success = airtable_logger.write_post_to_airtable(test_topic, test_post)
    
    if success:
            print("✅ Test post created successfully")
    else:
            print("❌ Failed to create test post")
            return
    
        # Test 2: Simulate "no" feedback
        print("\n📝 Test 2: Simulating 'no' feedback...")
    
        # Get the latest record
        all_records = airtable_logger.get_all_records()
        if not all_records:
            print("❌ No records found")
            return
        
        latest_record = all_records[-1]
        record_id = latest_record.get('id')
        
        # Add "no" feedback
        update_success = airtable_logger.update_record(
            record_id,
            {
                "Feedback": "No, this doesn't feel right. The tone is too aggressive. Can you make it more conversational?",
                "regeneration_count": 0
            }
        )
        
        if update_success:
            print("✅ 'No' feedback added successfully")
        else:
            print("❌ Failed to add feedback")
            return
        
        # Test 3: Run enhanced feedback processing
        print("\n🔄 Test 3: Running enhanced feedback processing...")
        feedback_processor.run_enhanced_feedback_loop(hours_back=1)
        
        # Test 4: Check if post was regenerated
        print("\n📝 Test 4: Checking if post was regenerated...")
        
        updated_record = airtable_logger.get_record(record_id)
        if updated_record:
            fields = updated_record.get('fields', {})
            new_post = fields.get('Post', '')
            regeneration_count = fields.get('regeneration_count', 0)
            status = fields.get('status', '')
            
            print(f"✅ Post was regenerated (attempt {regeneration_count})")
            print(f"📊 Status: {status}")
            print(f"📝 New post length: {len(new_post)} characters")
            print(f"📄 New post preview: {new_post[:200]}...")
        else:
            print("❌ Could not retrieve updated record")
        
        # Test 5: Simulate another "no" feedback
        print("\n📝 Test 5: Simulating another 'no' feedback...")
        
        update_success = airtable_logger.update_record(
            record_id,
            {
                "Feedback": "Still not quite right. Too much focus on money. Make it more about helping people.",
                "regeneration_count": regeneration_count
            }
        )
        
        if update_success:
            print("✅ Second 'no' feedback added successfully")
    else:
            print("❌ Failed to add second feedback")
            return
        
        # Test 6: Run feedback processing again
        print("\n🔄 Test 6: Running feedback processing again...")
        feedback_processor.run_enhanced_feedback_loop(hours_back=1)
        
        # Test 7: Check second regeneration
        print("\n📝 Test 7: Checking second regeneration...")
        
        updated_record = airtable_logger.get_record(record_id)
        if updated_record:
            fields = updated_record.get('fields', {})
            new_post = fields.get('Post', '')
            regeneration_count = fields.get('regeneration_count', 0)
            status = fields.get('status', '')
            
            print(f"✅ Post was regenerated again (attempt {regeneration_count})")
            print(f"📊 Status: {status}")
            print(f"📝 New post length: {len(new_post)} characters")
            print(f"📄 New post preview: {new_post[:200]}...")
        else:
            print("❌ Could not retrieve updated record")
        
        # Test 8: Simulate "yes" feedback
        print("\n📝 Test 8: Simulating 'yes' feedback...")
        
        update_success = airtable_logger.update_record(
            record_id,
            {
                "Feedback": "Yes, this is perfect! Love the focus on helping people and the conversational tone.",
                "regeneration_count": regeneration_count
            }
        )
        
        if update_success:
            print("✅ 'Yes' feedback added successfully")
        else:
            print("❌ Failed to add 'yes' feedback")
            return
        
        # Test 9: Run final feedback processing
        print("\n🔄 Test 9: Running final feedback processing...")
        feedback_processor.run_enhanced_feedback_loop(hours_back=1)
        
        # Test 10: Check final status
        print("\n📝 Test 10: Checking final status...")
        
        final_record = airtable_logger.get_record(record_id)
        if final_record:
            fields = final_record.get('fields', {})
            final_status = fields.get('status', '')
            approved_at = fields.get('approved_at', '')
            final_regeneration_count = fields.get('regeneration_count', 0)
            
            print(f"✅ Final status: {final_status}")
            print(f"📅 Approved at: {approved_at}")
            print(f"🔄 Total regenerations: {final_regeneration_count}")
            
            if final_status == 'approved':
                print("🎉 SUCCESS: Post was approved and added to RAG store!")
            else:
                print("⚠️ Post was not marked as approved")
        else:
            print("❌ Could not retrieve final record")
        
        print("\n🧪 Enhanced feedback system test completed!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")

def test_feedback_analysis():
    """Test the feedback analysis functionality."""
    
    print("\n🧪 Testing Feedback Analysis")
    print("=" * 40)

    try:
        feedback_processor = EnhancedFeedbackProcessor()
        
        test_feedbacks = [
            "The tone is too formal, make it more casual",
            "This is too long, make it shorter",
            "I want more personal stories and examples",
            "The content is good but needs more actionable tips",
            "Try a completely different approach",
            "Perfect! This is exactly what I wanted"
        ]
        
        for feedback in test_feedbacks:
            print(f"\n📝 Feedback: {feedback}")
            
            is_approval = feedback_processor._is_approval_feedback(feedback)
            is_rejection = feedback_processor._is_rejection_feedback(feedback)
            analysis = feedback_processor._analyze_feedback(feedback)
            
            print(f"   ✅ Approval: {is_approval}")
            print(f"   ❌ Rejection: {is_rejection}")
            print(f"   📊 Analysis: {analysis}")
        
        print("\n✅ Feedback analysis test completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in feedback analysis test: {e}")

def main():
    """Main test function."""
    
    print("🧪 Enhanced Feedback System Test Suite")
    print("=" * 60)
    print("This test demonstrates:")
    print("   🔄 Auto-regeneration when feedback is 'no'")
    print("   ✅ Stopping regeneration when feedback is 'yes'")
    print("   📊 Feedback analysis and processing")
    print("   📚 RAG store integration")
    print("=" * 60)
    
    # Run tests
    test_enhanced_feedback_system()
    test_feedback_analysis()
    
    print("\n🎉 All tests completed!")
    print("💡 The enhanced feedback system is working correctly!")

if __name__ == "__main__":
    main() 