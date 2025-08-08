import imaplib
import email
import re
import json
import os
from datetime import datetime, timedelta
from email.header import decode_header
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib.util
import os
import sys

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from the root config.py file
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
RESEND_API_KEY = config.RESEND_API_KEY

class EmailReplyHandler:
    def __init__(self, email_address, password, imap_server="imap.gmail.com", imap_port=993):
        """
        Initialize email reply handler.
        
        Args:
            email_address: Gmail address to check for replies
            password: App password for Gmail
            imap_server: IMAP server (default: Gmail)
            imap_port: IMAP port (default: 993 for SSL)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.last_check_time = None
        
    def connect_to_mailbox(self):
        """Connect to Gmail IMAP server."""
        try:
            # Connect to Gmail IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            return mail
        except Exception as e:
            print(f"❌ Error connecting to mailbox: {e}")
            return None
    
    def decode_email_subject(self, subject):
        """Decode email subject from bytes to string."""
        try:
            decoded_parts = decode_header(subject)
            subject_parts = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        subject_parts.append(part.decode(encoding))
                    else:
                        subject_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    subject_parts.append(part)
            return ''.join(subject_parts)
        except Exception as e:
            print(f"❌ Error decoding subject: {e}")
            return str(subject)
    
    def extract_email_body(self, email_message):
        """Extract email body from email message."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = str(email_message.get_payload())
        
        return body.strip()
    
    def parse_topic_response(self, email_body):
        """
        Parse email body to extract topic response.
        
        Returns:
            dict: {'has_topic': bool, 'topic': str, 'raw_response': str}
        """
        if not email_body:
            return {'has_topic': False, 'topic': '', 'raw_response': email_body}
        
        # Clean up the email body - remove quoted text and email headers
        cleaned_body = self.clean_email_body(email_body)
        
        if not cleaned_body:
            return {'has_topic': False, 'topic': '', 'raw_response': email_body}
        
        # Convert to lowercase for easier parsing
        body_lower = cleaned_body.lower().strip()
        
        # Check for "no" responses
        if body_lower in ['no', 'no.', 'no thanks', 'no thank you', 'nope']:
            return {'has_topic': False, 'topic': '', 'raw_response': cleaned_body}
        
        # Check for "yes" responses with topics
        yes_patterns = [
            r'yes\s*[:\-]?\s*(.+)',
            r'yes\s*[:\-]?\s*(.+)',
            r'topic\s*[:\-]?\s*(.+)',
            r'write\s+about\s*(.+)',
            r'can\s+you\s+write\s+about\s*(.+)',
            r'please\s+write\s+about\s*(.+)'
        ]
        
        for pattern in yes_patterns:
            match = re.search(pattern, body_lower, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                if topic and len(topic) > 3:  # Ensure topic has some content
                    return {'has_topic': True, 'topic': topic, 'raw_response': cleaned_body}
        
        # If no clear pattern, check if there's substantial content
        if len(body_lower) > 10 and not body_lower.startswith('no'):
            return {'has_topic': True, 'topic': body_lower, 'raw_response': cleaned_body}
        
        return {'has_topic': False, 'topic': '', 'raw_response': cleaned_body}
    
    def clean_email_body(self, email_body):
        """
        Clean email body by removing quoted text, headers, and other noise.
        """
        if not email_body:
            return ""
        
        # Split by common email quote markers
        lines = email_body.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip quoted text (lines starting with >)
            if line.startswith('>'):
                continue
            
            # Skip email headers and metadata
            if any(marker in line.lower() for marker in [
                'from:', 'to:', 'subject:', 'date:', 'sent:', 'received:',
                'on ', 'wrote:', 'wrote at', 'original message',
                'empowrd agent', 'linkedin content team'
            ]):
                continue
            
            # Skip lines that are just email formatting
            if line in ['--', '---', '___', '===']:
                continue
            
            cleaned_lines.append(line)
        
        # Join the cleaned lines
        cleaned_body = '\n'.join(cleaned_lines).strip()
        
        # Remove any remaining quoted text patterns
        cleaned_body = re.sub(r'On .*?wrote:.*', '', cleaned_body, flags=re.DOTALL | re.IGNORECASE)
        cleaned_body = re.sub(r'From:.*?To:.*?Subject:.*', '', cleaned_body, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned_body.strip()
    
    def check_for_replies(self, hours_back=24):
        """
        Check for email replies in the last N hours.
        
        Args:
            hours_back: Number of hours to look back for emails
            
        Returns:
            list: List of parsed topic responses
        """
        mail = self.connect_to_mailbox()
        if not mail:
            return []
        
        try:
            # Select inbox
            mail.select('INBOX')
            
            # Calculate time range
            now = datetime.now()
            since_date = now - timedelta(hours=hours_back)
            date_string = since_date.strftime("%d-%b-%Y")
            
            # Search for emails from the client
            search_criteria = f'(SINCE {date_string})'
            status, messages = mail.search(None, search_criteria)
            
            if status != 'OK':
                print("❌ Error searching emails")
                return []
            
            topic_responses = []
            
            for num in messages[0].split():
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(num, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Get email details
                    subject = self.decode_email_subject(email_message['subject'])
                    from_email = email_message['from']
                    date = email_message['date']
                    
                    # Check if it's a reply to our topic prompt
                    if self.is_topic_prompt_reply(subject, from_email):
                        body = self.extract_email_body(email_message)
                        parsed_response = self.parse_topic_response(body)
                        
                        if parsed_response['raw_response']:  # Only add if there's content
                            topic_responses.append({
                                'from_email': from_email,
                                'subject': subject,
                                'date': date,
                                'parsed_response': parsed_response
                            })
                            
                            print(f"📧 Found reply from {from_email}")
                            print(f"📧 Subject: {subject}")
                            print(f"📧 Has topic: {parsed_response['has_topic']}")
                            if parsed_response['has_topic']:
                                print(f"📧 Topic: {parsed_response['topic']}")
                            print("---")
                
                except Exception as e:
                    print(f"❌ Error processing email: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            return topic_responses
            
        except Exception as e:
            print(f"❌ Error checking for replies: {e}")
            try:
                mail.close()
                mail.logout()
            except:
                pass
            return []
    
    def is_topic_prompt_reply(self, subject, from_email):
        """
        Check if email is a reply to our topic prompt.
        
        Args:
            subject: Email subject
            from_email: Sender email address
            
        Returns:
            bool: True if it's a topic prompt reply
        """
        # Check if it's from our client
        client_email = "vaishnavisingh24011@gmail.com"
        if client_email.lower() not in from_email.lower():
            return False
        
        # Check if it's a reply (Re: or Fwd: in subject)
        subject_lower = subject.lower()
        if 're:' in subject_lower or 'fwd:' in subject_lower:
            return True
        
        # Check if it's a direct response to our topic prompt
        topic_prompt_subjects = [
            "got a topic in mind for today's post?",
            "topic for today's post",
            "linkedin post topic"
        ]
        
        for prompt_subject in topic_prompt_subjects:
            if prompt_subject.lower() in subject_lower:
                return True
        
        return False
    
    def save_topic_response(self, response_data):
        """
        Save topic response to a file for the main system to use.
        
        Args:
            response_data: Parsed topic response data
        """
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Save to topic_responses.json
            filename = 'data/topic_responses.json'
            
            # Load existing responses
            existing_responses = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        existing_responses = json.load(f)
                except:
                    existing_responses = []
            
            # Add timestamp
            response_data['timestamp'] = datetime.now().isoformat()
            
            # Add to existing responses
            existing_responses.append(response_data)
            
            # Keep only last 10 responses
            if len(existing_responses) > 10:
                existing_responses = existing_responses[-10:]
            
            # Save back to file
            with open(filename, 'w') as f:
                json.dump(existing_responses, f, indent=2)
            
            print(f"✅ Topic response saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving topic response: {e}")
    
    def get_latest_topic(self):
        """
        Get the latest topic from saved responses.
        
        Returns:
            str: Latest topic or empty string if none
        """
        try:
            filename = 'data/topic_responses.json'
            if not os.path.exists(filename):
                return ""
            
            with open(filename, 'r') as f:
                responses = json.load(f)
            
            if not responses:
                return ""
            
            # Get the most recent response with a topic
            for response in reversed(responses):
                if response.get('parsed_response', {}).get('has_topic'):
                    return response['parsed_response']['topic']
            
            return ""
            
        except Exception as e:
            print(f"❌ Error getting latest topic: {e}")
            return ""

def check_and_process_replies():
    """
    Main function to check for and process email replies.
    """
    # Email configuration
    email_address = "vaishchhu24@gmail.com"
    password = "wmdh hilc zgrf ozaf"  # Gmail App Password
    
    print("📧 Checking for email replies...")
    
    handler = EmailReplyHandler(email_address, password)
    replies = handler.check_for_replies(hours_back=24)
    
    if not replies:
        print("📧 No new replies found")
        return []
    
    print(f"📧 Found {len(replies)} reply(ies)")
    
    # Process and save each reply
    for reply in replies:
        handler.save_topic_response(reply)
    
    return replies

if __name__ == "__main__":
    check_and_process_replies()
