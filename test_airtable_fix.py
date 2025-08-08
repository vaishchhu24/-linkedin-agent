#!/usr/bin/env python3
"""
Test Airtable Table Name Fix
Try different table name formats to find the correct one
"""

import requests
import urllib.parse

# Your Airtable credentials
AIRTABLE_API_KEY = "patep0NA8WJrFnJNF.c456029e73b802f78fa8cb38875e30df9ccd55940e788291dab9691e2185e2e7"
AIRTABLE_BASE_ID = "apppflHrhOR5WOgEZ"

# Different table name formats to try
table_names = [
    "Table 1 Copy",
    "Table%201%20Copy",
    "Table+1+Copy",
    "LinkedIn Posts",
    "LinkedIn%20Posts",
    "LinkedIn+Posts",
    "Posts",
    "Content"
]

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def test_table_name(table_name):
    """Test if a table name works."""
    try:
        # Try different encoding methods
        encoded_names = [
            table_name,
            urllib.parse.quote(table_name, safe=''),
            urllib.parse.quote(table_name.replace(' ', '%20'), safe=''),
            urllib.parse.quote(table_name.replace(' ', '+'), safe='')
        ]
        
        for encoded_name in encoded_names:
            url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{encoded_name}"
            print(f"Testing: {url}")
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with table name: '{table_name}' (encoded as: '{encoded_name}')")
                data = response.json()
                print(f"   Records found: {len(data.get('records', []))}")
                return table_name, encoded_name
            else:
                print(f"❌ Failed with status {response.status_code}: {response.text[:100]}")
                
    except Exception as e:
        print(f"❌ Error testing '{table_name}': {e}")
    
    return None, None

def main():
    print("🔍 Testing Airtable Table Names")
    print("=" * 50)
    
    working_table = None
    working_encoded = None
    
    for table_name in table_names:
        print(f"\n📝 Testing table name: '{table_name}'")
        print("-" * 40)
        
        table, encoded = test_table_name(table_name)
        if table:
            working_table = table
            working_encoded = encoded
            break
    
    if working_table:
        print(f"\n🎯 WORKING TABLE FOUND!")
        print(f"   Table Name: '{working_table}'")
        print(f"   Encoded Name: '{working_encoded}'")
        
        # Test writing a record
        print(f"\n📝 Testing record creation...")
        test_record = {
            "fields": {
                "Topic": "Test Topic",
                "Post": "This is a test post to verify Airtable connection.",
                "Timestamp": "2025-07-31T12:00:00Z"
            }
        }
        
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{working_encoded}"
        response = requests.post(url, headers=headers, json=test_record)
        
        if response.status_code == 200:
            print("✅ Record created successfully!")
            data = response.json()
            print(f"   Record ID: {data.get('id', 'N/A')}")
        else:
            print(f"❌ Failed to create record: {response.status_code} - {response.text}")
    else:
        print("\n❌ No working table name found. Please check your Airtable configuration.")

if __name__ == "__main__":
    main() 