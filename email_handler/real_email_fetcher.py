#!/usr/bin/env python3
"""
Real Email Fetcher
Actually reads from your email inbox to get real replies
"""

import os
import sys
import imaplib
import email
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealEmailFetcher:
    """Fetches real email replies from your inbox."""
    
    def __init__(self):
        """Initialize the email fetcher."""
        # Read from the system operator's email (where client replies are received)
        self.email_address = EmailSettings.FROM_EMAIL  # vaishchhu24@gmail.com
        self.password = EmailSettings.EMAIL_PASSWORD  # Get from config
        self.imap_server = "imap.gmail.com"  # For Gmail
        self.imap_port = 993
        
        # Track processed emails to avoid duplicates
        self.processed_emails = set()
        
        logger.info(f"📧 Real Email Fetcher initialized for: {self.email_address}")
        
        if not self.password:
            logger.warning("⚠️ EMAIL_PASSWORD not set in config")
    
    def connect_to_inbox(self):
        """Connect to email inbox."""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # Login
            mail.login(self.email_address, self.password)
            
            # Select inbox
            mail.select('INBOX')
            
            logger.info("✅ Connected to email inbox")
            return mail
            
        except Exception as e:
            logger.error(f"❌ Error connecting to inbox: {e}")
            return None
    
    def fetch_recent_replies(self, hours_back: int = 24) -> List[Dict]:
        """
        Fetch recent email replies from the last N hours.
        Only returns emails that are replies to LinkedIn prompt emails.
        
        Args:
            hours_back: How many hours back to look for emails
            
        Returns:
            List of email replies with content and metadata
        """
        try:
            mail = self.connect_to_inbox()
            if not mail:
                return []
            
            # Calculate date range
            now = datetime.now(timezone.utc)
            since_date = now - timedelta(hours=hours_back)
            date_string = since_date.strftime("%d-%b-%Y")
            
            # Search for emails from the last N hours
            search_criteria = f'(SINCE "{date_string}")'
            status, message_numbers = mail.search(None, search_criteria)
            
            if status != 'OK':
                logger.error("❌ Error searching emails")
                return []
            
            email_list = message_numbers[0].split()
            replies = []
            
            for num in email_list[-10:]:  # Get last 10 emails
                try:
                    status, msg_data = mail.fetch(num, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Only process emails that are replies to LinkedIn prompts
                    if self._is_reply_to_prompt(email_message):
                        reply_data = self._extract_reply_content(email_message)
                        if reply_data:
                            replies.append(reply_data)
                            logger.info(f"📧 Found LinkedIn reply: {reply_data.get('subject', 'No subject')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing email {num}: {e}")
                    continue
            
            # Close connection
            mail.close()
            mail.logout()
            
            logger.info(f"✅ Fetched {len(replies)} recent replies")
            return replies
            
        except Exception as e:
            logger.error(f"❌ Error fetching recent replies: {e}")
            return []
    
    def _is_reply_to_prompt(self, email_message) -> bool:
        """Check if this email is a reply to our LinkedIn prompt."""
        try:
            subject = email_message.get('Subject', '').lower()
            from_email = email_message.get('From', '').lower()
            
            # Check if it's from the client's email address
            client_email = EmailSettings.TO_EMAIL.lower()
            if client_email not in from_email:
                return False
            
            # Check if it's a reply to our prompt (subject contains "Re:" and LinkedIn keywords)
            if not subject.startswith('re:'):
                return False
            
            # Check for LinkedIn prompt keywords
            prompt_keywords = ['linkedin', 'post', 'content', 'topic', 'mind']
            return any(keyword in subject for keyword in prompt_keywords)
            
        except Exception as e:
            logger.error(f"❌ Error checking if reply to prompt: {e}")
            return False
    
    def _extract_reply_content(self, email_message) -> Optional[Dict]:
        """Extract content from email reply."""
        try:
            email_id = email_message.get('Message-ID', '')
            
            # Skip if already processed
            if email_id in self.processed_emails:
                return None
            
            subject = email_message.get('Subject', '')
            from_email = email_message.get('From', '')
            date = email_message.get('Date', '')
            
            # Extract email body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
            
            # Clean the body
            cleaned_body = self._clean_email_body(body)
            
            if cleaned_body.strip():
                reply_data = {
                    'email_id': email_id,
                    'subject': subject,
                    'from_email': from_email,
                    'date': date,
                    'content': cleaned_body,
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                }
                
                # Mark as processed
                self.processed_emails.add(email_id)
                
                return reply_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting reply content: {e}")
            return None
    
    def _clean_email_body(self, body: str) -> str:
        """Clean email body by removing quotes and formatting."""
        try:
            # Remove quoted text (lines starting with >)
            lines = body.split('\n')
            cleaned_lines = []
            
            for line in lines:
                if not line.strip().startswith('>'):
                    cleaned_lines.append(line)
            
            cleaned_body = '\n'.join(cleaned_lines)
            
            # Remove common email reply patterns
            patterns_to_remove = [
                r'On .*? wrote:.*',
                r'From: .*',
                r'To: .*',
                r'Subject: .*',
                r'Date: .*',
                r'-{3,}.*',
                r'_{3,}.*'
            ]
            
            for pattern in patterns_to_remove:
                cleaned_body = re.sub(pattern, '', cleaned_body, flags=re.MULTILINE | re.IGNORECASE)
            
            return cleaned_body.strip()
            
        except Exception as e:
            logger.error(f"❌ Error cleaning email body: {e}")
            return body
    
    def mark_as_processed(self, email_id: str):
        """Mark an email as processed to avoid duplicates."""
        self.processed_emails.add(email_id)
    
    def get_unprocessed_replies(self) -> List[Dict]:
        """Get all unprocessed email replies."""
        return self.fetch_recent_replies(hours_back=24)


def test_real_email_fetching():
    """Test real email fetching functionality."""
    print("🧪 Testing Real Email Fetching")
    print("=" * 40)
    
    fetcher = RealEmailFetcher()
    
    # Check if email password is set
    if not EmailSettings.EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD not set in config")
        print("💡 Set it with: export EMAIL_PASSWORD='your-app-password'")
        return
    
    # Test connection
    print("🔗 Testing email connection...")
    mail = fetcher.connect_to_inbox()
    
    if mail:
        print("✅ Email connection successful!")
        mail.close()
        mail.logout()
        
        # Test fetching replies
        print("📧 Fetching recent replies...")
        replies = fetcher.fetch_recent_replies(hours_back=24)
        
        if replies:
            print(f"✅ Found {len(replies)} recent replies:")
            for i, reply in enumerate(replies[:3], 1):
                print(f"  {i}. From: {reply['from_email']}")
                print(f"     Subject: {reply['subject']}")
                print(f"     Content: {reply['content'][:100]}...")
                print()
        else:
            print("ℹ️ No recent replies found")
    else:
        print("❌ Email connection failed")


if __name__ == "__main__":
    test_real_email_fetching() 