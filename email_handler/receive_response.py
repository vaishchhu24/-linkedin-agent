#!/usr/bin/env python3
"""
Email Handler - Receive Response Module
Handles receiving and parsing email responses from clients
"""

import re
import json
from datetime import datetime, timezone
from typing import Dict, Optional
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class EmailResponseReceiver:
    def __init__(self):
        """Initialize the email response receiver."""
        self.response_patterns = {
            'yes': r'\b(yes|yeah|yep|sure|ok|okay|absolutely|definitely)\b',
            'no': r'\b(no|nope|nah|not really|not today)\b',
            'topic': r'(?i)(topic|about|regarding|concerning|on|experience|story|situation)'
        }
    
    def parse_email_response(self, email_content: str) -> Dict:
        """Parse email response to extract user intent and topic."""
        try:
            email_content = email_content.lower().strip()
            
            # Check for yes/no response
            has_topic = False
            topic_input = ""
            
            # Look for yes patterns
            if re.search(self.response_patterns['yes'], email_content):
                has_topic = True
                
                # Extract topic content
                # Remove common email reply text
                cleaned_content = self._clean_email_content(email_content)
                
                # Look for topic indicators
                topic_match = re.search(self.response_patterns['topic'], cleaned_content)
                if topic_match:
                    # Extract content after topic indicators
                    topic_start = topic_match.end()
                    topic_input = cleaned_content[topic_start:].strip()
                else:
                    # If no topic indicator, take the main content
                    topic_input = cleaned_content
            
            # Look for no patterns
            elif re.search(self.response_patterns['no'], email_content):
                has_topic = False
                topic_input = ""
            
            # If neither yes nor no, assume they provided content
            else:
                has_topic = True
                topic_input = self._clean_email_content(email_content)
            
            return {
                "has_topic": has_topic,
                "topic_input": topic_input,
                "raw_content": email_content,
                "parsed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
        except Exception as e:
            print(f"❌ Error parsing email response: {e}")
            return {
                "has_topic": False,
                "topic_input": "",
                "raw_content": email_content,
                "error": str(e),
                "parsed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
    
    def _clean_email_content(self, content: str) -> str:
        """Clean email content by removing common reply text."""
        # Remove common email reply patterns
        patterns_to_remove = [
            r'^.*?wrote:.*?$',  # "On date, person wrote:"
            r'^.*?sent:.*?$',   # "On date, person sent:"
            r'^.*?from:.*?$',   # "From: person"
            r'^.*?to:.*?$',     # "To: person"
            r'^.*?subject:.*?$', # "Subject: ..."
            r'^.*?date:.*?$',   # "Date: ..."
            r'^-{3,}.*?$',      # "--- original message ---"
            r'^>.*?$',          # Quote lines starting with >
            r'^\s*$',           # Empty lines
        ]
        
        cleaned = content
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def extract_topic_from_response(self, response_data: Dict) -> Optional[str]:
        """Extract specific topic from parsed response."""
        if not response_data.get("has_topic"):
            return None
        
        topic_input = response_data.get("topic_input", "")
        
        # If topic is too short, it might not be meaningful
        if len(topic_input) < 10:
            return None
        
        return topic_input
    
    def validate_response(self, response_data: Dict) -> Dict:
        """Validate the parsed response and provide feedback."""
        validation_result = {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }
        
        if not response_data.get("has_topic"):
            validation_result["suggestions"].append("No specific topic provided - will use content pillars")
        else:
            topic_input = response_data.get("topic_input", "")
            
            if len(topic_input) < 10:
                validation_result["issues"].append("Topic input is too short")
                validation_result["suggestions"].append("Please provide more detail about your topic")
            
            if len(topic_input) > 500:
                validation_result["suggestions"].append("Topic input is quite long - this will be treated as detailed content")
        
        if validation_result["issues"]:
            validation_result["is_valid"] = False
        
        return validation_result 