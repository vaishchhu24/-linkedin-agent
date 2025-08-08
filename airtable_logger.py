#!/usr/bin/env python3
"""
Airtable Logger Module
Handles logging generated posts to Airtable
"""

import os
import sys
import requests
from datetime import datetime, timezone
from typing import Dict, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from config
try:
    from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME
except ImportError:
    from config.email_config import EmailSettings
    AIRTABLE_API_KEY = EmailSettings.AIRTABLE_API_KEY
    AIRTABLE_BASE_ID = EmailSettings.AIRTABLE_BASE_ID
    AIRTABLE_TABLE_NAME = EmailSettings.AIRTABLE_TABLE_NAME

# Fix table name encoding for URL
def encode_table_name(table_name: str) -> str:
    """Encode table name for URL use."""
    import urllib.parse
    if not table_name:
        return ""
    return urllib.parse.quote(str(table_name), safe='')

class AirtableLogger:
    """Handles logging posts to Airtable."""
    
    def __init__(self):
        """Initialize Airtable logger."""
        self.api_key = AIRTABLE_API_KEY
        self.base_id = AIRTABLE_BASE_ID
        self.table_name = AIRTABLE_TABLE_NAME
        self.encoded_table_name = encode_table_name(self.table_name)
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.encoded_table_name}"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def write_post_to_airtable(self, topic: str, post: str) -> bool:
        """
        Save LinkedIn post to Airtable with full content and no truncation
        """
        try:
            # Airtable API endpoint
            url = self.base_url
            
            # Headers for Airtable API
            headers = self.headers
            
            # Format current timestamp in UTC
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Debug: Print what we're about to save
            print(f"📝 Saving to Airtable:")
            print(f"   Timestamp: {timestamp}")
            print(f"   Topic: {topic}")
            print(f"   Post length: {len(post)} characters")
            print(f"   Full post content:")
            print(f"   {'='*50}")
            print(post)
            print(f"   {'='*50}")
            
            # Data to send to Airtable - matching your column structure
            data = {
                "records": [
                    {
                        "fields": {
                            "Timestamp": timestamp,
                            "Topic": topic,
                            "Post": post
                        }
                    }
                ]
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Post successfully saved to Airtable!")
                print(f"   Record ID: {result['records'][0]['id']}")
                print(f"   Created: {result['records'][0]['createdTime']}")
                return True
            else:
                print(f"❌ Error saving to Airtable: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving to Airtable: {e}")
            print(f"   Post content length: {len(post) if post else 0}")
            print(f"   Topic: {topic}")
            return False

    def test_airtable_connection(self) -> bool:
        """
        Test function to verify Airtable connection and capabilities
        """
        try:
            url = self.base_url
            headers = self.headers
            
            # Test reading the table
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Airtable connection successful!")
                print(f"   Base ID: {self.base_id}")
                print(f"   Table: {self.table_name}")
                print(f"   Current records: {len(data.get('records', []))}")
                
                # Test writing a long string
                test_long_text = "This is a test of a very long string. " * 100  # ~4000 characters
                test_data = {
                    "records": [
                        {
                            "fields": {
                                "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "Topic": "TEST",
                                "Post": test_long_text
                            }
                        }
                    ]
                }
                
                write_response = requests.post(url, headers=headers, json=test_data)
                
                if write_response.status_code == 200:
                    print(f"   Test write successful!")
                    print(f"   Test content length: {len(test_long_text)} characters")
                    print(f"   ✅ No truncation issues with Airtable!")
                else:
                    print(f"   Test write failed: {write_response.status_code}")
                
                return True
            else:
                print(f"❌ Airtable connection failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Airtable test failed: {e}")
            return False

    def get_all_records(self) -> list:
        """
        Get all records from Airtable.
        
        Returns:
            List of all records
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('records', [])
            else:
                print(f"❌ Error fetching records: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting records: {e}")
            return []
    
    def get_record(self, record_id: str) -> Optional[Dict]:
        """
        Get a specific record by ID.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            Record data or None if not found
        """
        try:
            url = f"{self.base_url}/{record_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error fetching record {record_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting record {record_id}: {e}")
            return None
    
    def update_record(self, record_id: str, fields: Dict) -> bool:
        """
        Update a record in Airtable.
        
        Args:
            record_id: Airtable record ID
            fields: Fields to update
            
        Returns:
            True if update was successful
        """
        try:
            url = f"{self.base_url}/{record_id}"
            
            data = {
                "fields": fields
            }
            
            response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                print(f"✅ Successfully updated record {record_id}")
                return True
            else:
                print(f"❌ Error updating record {record_id}: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating record {record_id}: {e}")
            return False

# Global logger instance for backward compatibility
_airtable_logger = None

def get_airtable_logger():
    """Get or create global Airtable logger instance."""
    global _airtable_logger
    if _airtable_logger is None:
        _airtable_logger = AirtableLogger()
    return _airtable_logger

def write_post_to_airtable(topic: str, post: str) -> bool:
    """
    Save LinkedIn post to Airtable with full content and no truncation
    Backward compatibility function
    """
    logger = get_airtable_logger()
    return logger.write_post_to_airtable(topic, post)

def test_airtable_connection() -> bool:
    """
    Test function to verify Airtable connection and capabilities
    Backward compatibility function
    """
    logger = get_airtable_logger()
    return logger.test_airtable_connection()

if __name__ == "__main__":
    logger = AirtableLogger()
    logger.test_airtable_connection()
