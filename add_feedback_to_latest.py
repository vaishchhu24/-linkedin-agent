#!/usr/bin/env python3
"""
Add Feedback to Latest Post
Adds feedback to the most recent post in Airtable for testing
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger

def add_feedback_to_latest():
    """Add feedback to the most recent post."""
    print("📝 Adding Feedback to Latest Post")
    print("=" * 50)
    
    # Initialize Airtable logger
    airtable_logger = AirtableLogger()
    
    # Get all records
    all_records = airtable_logger.get_all_records()
    
    if not all_records:
        print("❌ No records found in Airtable")
        return False
    
    # Get most recent record
    most_recent = all_records[-1]
    record_id = most_recent.get('id')
    fields = most_recent.get('fields', {})
    
    print(f"📋 Most Recent Post:")
    print(f"   ID: {record_id}")
    print(f"   Topic: {fields.get('Topic', 'N/A')}")
    print(f"   Current Feedback: {fields.get('Feedback', 'None')}")
    
    # Add specific feedback about overused phrases and questions
    test_feedback = """Over use of the word crickets and truth bomb - I wouldn't use either of these phrases. Also too many questions - just ask 2 to 3 really focused and sharp clairfying questions - such as STATEMENT - most of us know we are underselling our services - we are just afraid of the rejection so we BUY our services and brag about the purchase. QUESTION  does that really replace your corporate income? I am frequently asked HOW do i replace my corporate income - 'can't you just tell me'. It's not that easy, I'm not you - and you are not me."""
    
    print(f"\n📝 Adding feedback: '{test_feedback}'")
    
    # Update the record
    success = airtable_logger.update_record(record_id, {
        "Feedback": test_feedback
    })
    
    if success:
        print("✅ Successfully added feedback to most recent post")
        print("🔄 Now you can run the enhanced feedback processor to test regeneration")
        return True
    else:
        print("❌ Failed to add feedback")
        return False

if __name__ == "__main__":
    add_feedback_to_latest() 