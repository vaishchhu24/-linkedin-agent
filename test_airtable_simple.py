#!/usr/bin/env python3
"""
Simple test to see what's in the Airtable table.
"""

import importlib.util
import os
import requests
import json

def test_airtable_simple():
    """
    Simple test to see what's in the Airtable table.
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
        
        print(f"🔍 Testing Airtable table: {AIRTABLE_TABLE_NAME}")
        
        # Get records
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            print(f"✅ Found {len(records)} records")
            
            # Show first few records
            for i, record in enumerate(records[:3]):
                print(f"\nRecord {i+1}:")
                print(f"  ID: {record.get('id')}")
                print(f"  Created: {record.get('createdTime')}")
                print(f"  Fields: {list(record.get('fields', {}).keys())}")
                
                fields = record.get('fields', {})
                if fields:
                    for field_name, field_value in fields.items():
                        if isinstance(field_value, str) and len(field_value) > 100:
                            print(f"    {field_name}: {field_value[:100]}...")
                        else:
                            print(f"    {field_name}: {field_value}")
                else:
                    print(f"    (No fields)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_airtable_simple() 