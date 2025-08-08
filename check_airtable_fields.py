#!/usr/bin/env python3
"""
Script to check the actual fields in the Airtable table.
"""

import importlib.util
import os
import requests
import json

def check_airtable_fields():
    """
    Check what fields are actually available in the Airtable table.
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
        
        print(f"🔍 Checking Airtable table: {AIRTABLE_TABLE_NAME}")
        print(f"🔍 Base ID: {AIRTABLE_BASE_ID}")
        
        # Get table schema
        url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get('tables', [])
            
            print(f"📊 Found {len(tables)} tables in base")
            
            for table in tables:
                table_name = table.get('name', 'Unknown')
                print(f"\n📋 Table: {table_name}")
                
                if table_name == AIRTABLE_TABLE_NAME:
                    fields = table.get('fields', [])
                    print(f"✅ Found target table with {len(fields)} fields:")
                    
                    for field in fields:
                        field_name = field.get('name', 'Unknown')
                        field_type = field.get('type', 'Unknown')
                        print(f"   • {field_name} ({field_type})")
                    
                    # Check if Feedback field exists
                    feedback_field = next((f for f in fields if f.get('name') == 'Feedback'), None)
                    if feedback_field:
                        print(f"\n✅ Feedback field found: {feedback_field.get('name')} ({feedback_field.get('type')})")
                    else:
                        print(f"\n❌ Feedback field not found")
                        print("Available fields:")
                        for field in fields:
                            print(f"   - {field.get('name')}")
                else:
                    print(f"   (Not the target table)")
        else:
            print(f"❌ Error getting table schema: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking fields: {e}")

def test_simple_record_fetch():
    """
    Test fetching a simple record to see what works.
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
        
        # Try to get a simple record
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try without any parameters first
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            print(f"✅ Successfully fetched {len(records)} records")
            
            if records:
                print(f"📋 Checking multiple records for data...")
                
                # Check first 20 records to find one with data
                for i, record in enumerate(records[:20]):
                    if record.get('fields'):
                        print(f"\nRecord {i+1} (has data):")
                        print(f"  ID: {record.get('id', 'No ID')}")
                        
                        fields = list(record['fields'].keys())
                        print(f"  Field count: {len(fields)}")
                        for field in fields:
                            value = record['fields'].get(field, '')
                            print(f"    - {field}: {str(value)[:50]}...")
                        
                        # Check for Feedback field
                        if 'Feedback' in fields:
                            feedback = record['fields'].get('Feedback', '')
                            if feedback:
                                print(f"  ✅ Found feedback: {feedback[:100]}...")
                            else:
                                print(f"  📝 Feedback field exists but is empty")
                        else:
                            print(f"  ❌ No Feedback field found")
                        
                        # Only show first few records with data
                        if i >= 2:
                            break
                
                # Check if we found any records with data
                records_with_data = [r for r in records[:10] if r.get('fields')]
                if records_with_data:
                    print(f"\n✅ Found {len(records_with_data)} records with data")
                else:
                    print(f"\n❌ No records with data found in first 10 records")
        else:
            print(f"❌ Error fetching records: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing record fetch: {e}")

if __name__ == "__main__":
    print("🔍 Checking Airtable Table Structure")
    print("=" * 50)
    
    check_airtable_fields()
    
    print("\n" + "=" * 50)
    print("🧪 Testing Simple Record Fetch")
    print("=" * 50)
    
    test_simple_record_fetch() 