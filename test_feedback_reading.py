#!/usr/bin/env python3
"""
Test Feedback Reading from Airtable
Verifies that the system can actually read feedback from Airtable
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from feedback_processor import FeedbackProcessor
from config.email_config import EmailSettings

def test_airtable_reading():
    """Test reading from Airtable."""
    
    print("🔍 Testing Airtable Reading")
    print("=" * 40)
    
    airtable_logger = AirtableLogger()
    
    # Test 1: Get all records
    print("📊 Test 1: Getting all records from Airtable...")
    try:
        all_records = airtable_logger.get_all_records()
        print(f"✅ Successfully retrieved {len(all_records)} records from Airtable")
        
        if all_records:
            print("📋 Sample records:")
            for i, record in enumerate(all_records[:3], 1):
                fields = record.get('fields', {})
                print(f"  {i}. ID: {record.get('id', 'N/A')}")
                print(f"     Topic: {fields.get('topic', 'N/A')}")
                print(f"     Feedback: {fields.get('feedback', 'N/A')}")
                print(f"     Timestamp: {fields.get('timestamp', 'N/A')}")
                print()
        else:
            print("📭 No records found in Airtable")
            
    except Exception as e:
        print(f"❌ Error reading from Airtable: {e}")
    
    print("-" * 40)

def test_feedback_monitoring():
    """Test feedback monitoring functionality."""
    
    print("🔄 Testing Feedback Monitoring")
    print("=" * 40)
    
    feedback_processor = FeedbackProcessor()
    
    # Test 2: Monitor for feedback
    print("📊 Test 2: Monitoring for feedback...")
    try:
        posts_with_feedback = feedback_processor.monitor_for_feedback(hours_back=24)
        print(f"✅ Found {len(posts_with_feedback)} posts with feedback")
        
        if posts_with_feedback:
            print("📝 Posts with feedback:")
            for i, post in enumerate(posts_with_feedback, 1):
                print(f"  {i}. Topic: {post.get('topic', 'N/A')}")
                print(f"     Feedback: {post.get('feedback', 'N/A')}")
                print(f"     Record ID: {post.get('record_id', 'N/A')}")
                print()
        else:
            print("📭 No posts with feedback found")
            
    except Exception as e:
        print(f"❌ Error monitoring feedback: {e}")
    
    print("-" * 40)

def test_airtable_fields():
    """Test specific Airtable fields."""
    
    print("📋 Testing Airtable Fields")
    print("=" * 40)
    
    airtable_logger = AirtableLogger()
    
    try:
        all_records = airtable_logger.get_all_records()
        
        if all_records:
            print("📊 Analyzing Airtable fields...")
            
            # Check what fields are available
            sample_record = all_records[0]
            fields = sample_record.get('fields', {})
            
            print("📋 Available fields:")
            for field_name, field_value in fields.items():
                print(f"  - {field_name}: {type(field_value).__name__} = {str(field_value)[:50]}...")
            
            print()
            
            # Check for feedback field specifically
            feedback_count = 0
            for record in all_records:
                fields = record.get('fields', {})
                if fields.get('feedback'):
                    feedback_count += 1
            
            print(f"📝 Records with feedback: {feedback_count}/{len(all_records)}")
            
            # Show sample feedback
            if feedback_count > 0:
                print("📋 Sample feedback:")
                for record in all_records[:3]:
                    fields = record.get('fields', {})
                    if fields.get('feedback'):
                        print(f"  - {fields.get('feedback', '')}")
            
        else:
            print("📭 No records to analyze")
            
    except Exception as e:
        print(f"❌ Error analyzing Airtable fields: {e}")
    
    print("-" * 40)

def test_feedback_processing():
    """Test actual feedback processing with real data."""
    
    print("🔄 Testing Real Feedback Processing")
    print("=" * 40)
    
    feedback_processor = FeedbackProcessor()
    
    try:
        # Get real posts with feedback
        posts_with_feedback = feedback_processor.monitor_for_feedback(hours_back=24)
        
        if posts_with_feedback:
            print(f"📊 Processing {len(posts_with_feedback)} posts with feedback...")
            
            for i, post_data in enumerate(posts_with_feedback, 1):
                print(f"\n🔄 Processing post {i}:")
                print(f"  Topic: {post_data.get('topic', 'N/A')}")
                print(f"  Feedback: {post_data.get('feedback', 'N/A')}")
                
                # Test feedback classification
                feedback = post_data.get('feedback', '').lower()
                is_approval = feedback_processor._is_approval_feedback(feedback)
                is_rejection = feedback_processor._is_rejection_feedback(feedback)
                
                print(f"  Classification: Approval={is_approval}, Rejection={is_rejection}")
                
                # Process the feedback
                success = feedback_processor.process_feedback(post_data)
                print(f"  Processing Result: {'✅ Success' if success else '❌ Failed'}")
                
        else:
            print("📭 No posts with feedback to process")
            
    except Exception as e:
        print(f"❌ Error in feedback processing: {e}")
    
    print("-" * 40)

def main():
    """Run all feedback reading tests."""
    
    print("🚀 Feedback Reading Test Suite")
    print("=" * 60)
    
    # Test Airtable reading
    test_airtable_reading()
    
    # Test feedback monitoring
    test_feedback_monitoring()
    
    # Test Airtable fields
    test_airtable_fields()
    
    # Test real feedback processing
    test_feedback_processing()
    
    print("\n" + "=" * 60)
    print("✅ All feedback reading tests completed!")

if __name__ == "__main__":
    main() 