#!/usr/bin/env python3
"""
Script to add feedback to the incomplete post.
"""

import importlib.util
import os
import requests
import json

def add_feedback_to_incomplete_post():
    """
    Add feedback to the incomplete post.
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
        
        print(f"🔍 Adding feedback to incomplete post...")
        
        # The incomplete post record ID (the one that cuts off at "I've got your")
        record_id = "recYlaIdL5XL3e940"
        
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
                        "Feedback": "This post is incomplete - it cuts off mid-sentence at 'I've got your'. Posts must be complete and properly finished. Also, it's getting too promotional at the end with 'I've got a great way to help you get started for FREE!' - avoid promotional language. Keep it authentic and story-based without selling anything."
                    }
                }
            ]
        }
        
        # Update the record with feedback
        update_response = requests.patch(url, headers=headers, json=feedback_data, timeout=10)
        
        if update_response.status_code == 200:
            print("✅ Feedback added successfully to incomplete post!")
            print("📝 Feedback: This post is incomplete - it cuts off mid-sentence at 'I've got your'. Posts must be complete and properly finished. Also, it's getting too promotional at the end with 'I've got a great way to help you get started for FREE!' - avoid promotional language. Keep it authentic and story-based without selling anything.")
        else:
            print(f"❌ Error adding feedback: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            
    except Exception as e:
        print(f"❌ Error adding feedback: {e}")

if __name__ == "__main__":
    add_feedback_to_incomplete_post() 