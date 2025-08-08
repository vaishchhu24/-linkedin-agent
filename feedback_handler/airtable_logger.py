#!/usr/bin/env python3
"""
Feedback Handler - Airtable Logger Module
Enhanced Airtable logging with feedback tracking
"""

import requests
import json
from datetime import datetime, timezone
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME

class AirtableLogger:
    def __init__(self):
        """Initialize the Airtable logger."""
        self.api_key = AIRTABLE_API_KEY
        self.base_id = AIRTABLE_BASE_ID
        self.table_name = AIRTABLE_TABLE_NAME
        self.api_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        
        print("📊 Airtable Logger initialized")
    
    def log_post(self, topic: str, post_content: str, timestamp: str, feedback_status: str = "pending") -> str:
        """Log a post to Airtable with feedback tracking."""
        try:
            # Headers for Airtable API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Data to send to Airtable
            data = {
                "records": [
                    {
                        "fields": {
                            "Timestamp": timestamp,
                            "Topic": topic,
                            "Post": post_content,
                            "Feedback_Status": feedback_status,
                            "Generation_Date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                            "Word_Count": len(post_content.split()),
                            "Character_Count": len(post_content)
                        }
                    }
                ]
            }
            
            # Debug: Print what we're about to save
            print(f"📝 Saving to Airtable:")
            print(f"   Timestamp: {timestamp}")
            print(f"   Topic: {topic}")
            print(f"   Post length: {len(post_content)} characters")
            print(f"   Feedback Status: {feedback_status}")
            
            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                record_id = result['records'][0]['id']
                print(f"✅ Post successfully saved to Airtable!")
                print(f"   Record ID: {record_id}")
                print(f"   Created: {result['records'][0]['createdTime']}")
                return record_id
            else:
                print(f"❌ Error saving to Airtable: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error logging post to Airtable: {e}")
            return None
    
    def update_status(self, record_id: str, new_status: str) -> bool:
        """Update the feedback status of a post."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "records": [
                    {
                        "id": record_id,
                        "fields": {
                            "Feedback_Status": new_status,
                            "Last_Updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                        }
                    }
                ]
            }
            
            response = requests.patch(self.api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"✅ Status updated to: {new_status}")
                return True
            else:
                print(f"❌ Error updating status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            return False
    
    def add_feedback(self, record_id: str, feedback: str, feedback_type: str = "client") -> bool:
        """Add feedback to a post record."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Get current record to append feedback
            get_response = requests.get(f"{self.api_url}/{record_id}", headers=headers)
            
            if get_response.status_code == 200:
                current_record = get_response.json()
                current_feedback = current_record['fields'].get('Feedback', '')
                
                # Append new feedback
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                new_feedback_entry = f"[{timestamp}] {feedback_type.upper()}: {feedback}\n"
                updated_feedback = current_feedback + new_feedback_entry
                
                # Update record with new feedback
                data = {
                    "records": [
                        {
                            "id": record_id,
                            "fields": {
                                "Feedback": updated_feedback,
                                "Last_Feedback": timestamp,
                                "Feedback_Type": feedback_type
                            }
                        }
                    ]
                }
                
                update_response = requests.patch(self.api_url, headers=headers, json=data)
                
                if update_response.status_code == 200:
                    print(f"✅ Feedback added: {feedback}")
                    return True
                else:
                    print(f"❌ Error adding feedback: {update_response.status_code}")
                    return False
            else:
                print(f"❌ Error getting current record: {get_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding feedback: {e}")
            return False
    
    def get_pending_feedback_posts(self) -> list:
        """Get posts that are waiting for feedback."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Filter for pending feedback
            params = {
                "filterByFormula": "{Feedback_Status} = 'pending'"
            }
            
            response = requests.get(self.api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pending_posts = []
                
                for record in data.get('records', []):
                    pending_posts.append({
                        'id': record['id'],
                        'topic': record['fields'].get('Topic', ''),
                        'post': record['fields'].get('Post', ''),
                        'timestamp': record['fields'].get('Timestamp', ''),
                        'created_time': record['createdTime']
                    })
                
                print(f"📋 Found {len(pending_posts)} posts pending feedback")
                return pending_posts
            else:
                print(f"❌ Error getting pending posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting pending feedback posts: {e}")
            return []
    
    def get_post_by_id(self, record_id: str) -> dict:
        """Get a specific post by record ID."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/{record_id}", headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                return {
                    'id': record['id'],
                    'topic': record['fields'].get('Topic', ''),
                    'post': record['fields'].get('Post', ''),
                    'timestamp': record['fields'].get('Timestamp', ''),
                    'feedback_status': record['fields'].get('Feedback_Status', ''),
                    'feedback': record['fields'].get('Feedback', ''),
                    'created_time': record['createdTime']
                }
            else:
                print(f"❌ Error getting post: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting post by ID: {e}")
            return {}
    
    def get_recent_posts(self, limit: int = 10) -> list:
        """Get recent posts from Airtable."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "maxRecords": limit,
                "sort": [{"field": "Timestamp", "direction": "desc"}]
            }
            
            response = requests.get(self.api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                recent_posts = []
                
                for record in data.get('records', []):
                    recent_posts.append({
                        'id': record['id'],
                        'topic': record['fields'].get('Topic', ''),
                        'post': record['fields'].get('Post', '')[:200] + "...",  # Truncate for display
                        'timestamp': record['fields'].get('Timestamp', ''),
                        'feedback_status': record['fields'].get('Feedback_Status', ''),
                        'created_time': record['createdTime']
                    })
                
                return recent_posts
            else:
                print(f"❌ Error getting recent posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting recent posts: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test the Airtable connection."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(self.api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Airtable connection successful!")
                print(f"   Base ID: {self.base_id}")
                print(f"   Table: {self.table_name}")
                print(f"   Current records: {len(data.get('records', []))}")
                return True
            else:
                print(f"❌ Airtable connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Airtable connection: {e}")
            return False 