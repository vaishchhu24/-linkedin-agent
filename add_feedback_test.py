#!/usr/bin/env python3
"""
Test script to add feedback to Airtable and test the feedback system.
"""

import importlib.util
import os
import requests
import json

def add_feedback_to_airtable():
    """
    Add feedback to the most recent post in Airtable.
    """
    try:
        # Import config
        project_root = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        AIRTABLE_API_KEY = config.AIRTABLE_API_KEY
        AIRTABLE_BASE_ID = config.AIRTABLE_BASE_ID
        AIRTABLE_TABLE_NAME = config.AIRTABLE_TABLE_NAME
        
        # First, get the most recent record
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Get recent records
        params = {
            "sort": [{"field": "Timestamp", "direction": "desc"}],
            "maxRecords": 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                record_id = records[0]['id']
                print(f"✅ Found recent record: {record_id}")
                
                # Add feedback to this record
                feedback_data = {
                    "records": [
                        {
                            "id": record_id,
                            "fields": {
                                "Feedback": "Great story-based content! Love the personal experience about starting the business. Keep this authentic, conversational tone. Maybe add more specific details about the mistakes made and how you learned from them."
                            }
                        }
                    ]
                }
                
                # Update the record with feedback
                update_response = requests.patch(url, headers=headers, json=feedback_data, timeout=10)
                
                if update_response.status_code == 200:
                    print("✅ Feedback added successfully!")
                    print("📝 Feedback: Great story-based content! Love the personal experience about starting the business. Keep this authentic, conversational tone. Maybe add more specific details about the mistakes made and how you learned from them.")
                else:
                    print(f"❌ Error adding feedback: {update_response.status_code}")
                    print(f"Response: {update_response.text}")
            else:
                print("📝 No records found to add feedback to")
        else:
            print(f"❌ Error getting records: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error adding feedback: {e}")

def test_feedback_reading():
    """
    Test reading feedback from Airtable.
    """
    try:
        from feedback_retriever import get_feedback_context
        print("🧪 Testing feedback reading...")
        context = get_feedback_context()
        print(f"📝 Feedback context: {context[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Error testing feedback: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Airtable Feedback System")
    print("=" * 50)
    
    # Add feedback
    add_feedback_to_airtable()
    
    print("\n" + "=" * 50)
    
    # Test reading feedback
    test_feedback_reading() 