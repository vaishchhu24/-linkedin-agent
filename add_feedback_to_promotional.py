#!/usr/bin/env python3
"""
Script to add feedback to the promotional post.
"""

import importlib.util
import os
import requests
import json

def add_feedback_to_promotional_post():
    """
    Add feedback to the promotional post.
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
        
        print(f"🔍 Adding feedback to promotional post...")
        
        # The promotional post record ID
        record_id = "recuD6ecb2V4T8L4p"
        
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Add feedback to this specific record
        feedback_data = {
            "records": [
                {
                    "id": record_id,
                    "fields": {
                        "Feedback": "This is too promotional! I want authentic, story-based content like the previous post. No business coach language, no 'I am looking for 5 HR Consultants', no promotional offers. Focus on real personal experiences and struggles, not selling services. Keep it conversational and vulnerable like the previous post about leaving corporate America."
                    }
                }
            ]
        }
        
        # Update the record with feedback
        update_response = requests.patch(url, headers=headers, json=feedback_data, timeout=10)
        
        if update_response.status_code == 200:
            print("✅ Feedback added successfully to promotional post!")
            print("📝 Feedback: This is too promotional! I want authentic, story-based content like the previous post. No business coach language, no 'I am looking for 5 HR Consultants', no promotional offers. Focus on real personal experiences and struggles, not selling services. Keep it conversational and vulnerable like the previous post about leaving corporate America.")
        else:
            print(f"❌ Error adding feedback: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            
    except Exception as e:
        print(f"❌ Error adding feedback: {e}")

if __name__ == "__main__":
    add_feedback_to_promotional_post() 