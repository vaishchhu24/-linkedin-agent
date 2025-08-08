#!/usr/bin/env python3
"""
Process the crickets feedback specifically
"""

from enhanced_feedback_processor import EnhancedFeedbackProcessor
from airtable_logger import AirtableLogger

def process_crickets_feedback():
    """Process the crickets feedback specifically."""
    print("🔄 Processing Crickets Feedback")
    print("=" * 50)
    
    # Find the crickets feedback record
    al = AirtableLogger()
    records = al.get_all_records()
    
    crickets_record = None
    for r in records:
        if 'Feedback' in r.get('fields', {}) and 'crickets' in r.get('fields', {}).get('Feedback', '').lower():
            crickets_record = r
            break
    
    if not crickets_record:
        print("❌ No crickets feedback found")
        return False
    
    print(f"📝 Found crickets feedback:")
    print(f"   ID: {crickets_record.get('id')}")
    print(f"   Topic: {crickets_record.get('fields', {}).get('Topic', 'N/A')}")
    print(f"   Feedback: {crickets_record.get('fields', {}).get('Feedback', 'N/A')}")
    
    # Create post data for processing
    fields = crickets_record.get('fields', {})
    post_data = {
        'record_id': crickets_record.get('id'),
        'topic': fields.get('Topic', ''),
        'post': fields.get('Post', ''),
        'timestamp': fields.get('Timestamp', ''),
        'feedback': fields.get('Feedback', ''),
        'voice_quality': fields.get('voice score', 0),
        'post_quality': fields.get('quality score', 0),
        'regeneration_count': fields.get('regeneration_count', 0)
    }
    
    # Process the feedback
    feedback_processor = EnhancedFeedbackProcessor()
    success = feedback_processor.process_feedback(post_data)
    
    if success:
        print("✅ Successfully processed crickets feedback")
    else:
        print("❌ Failed to process crickets feedback")
    
    return success

if __name__ == "__main__":
    process_crickets_feedback() 