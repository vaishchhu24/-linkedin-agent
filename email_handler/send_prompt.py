#!/usr/bin/env python3
"""
Email Handler - Send Prompt Module
Handles sending topic prompt emails to clients
"""

import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.email_config import EmailSettings

class EmailPromptSender:
    def __init__(self):
        """Initialize the email prompt sender."""
        self.api_key = EmailSettings.RESEND_API_KEY
        self.from_email = EmailSettings.FROM_EMAIL
        self.password = EmailSettings.EMAIL_PASSWORD
    
    def send_topic_prompt_smtp(self, client_email: str = "vaishnavisingh24011@gmail.com") -> bool:
        """Send a topic prompt email using SMTP (Gmail)."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "What's on your mind for your LinkedIn post today?"
            msg['From'] = self.from_email
            msg['To'] = client_email
            
            # HTML content
            html_content = """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Hey Sam! 👋</h2>
                    <p>What's on your mind for your LinkedIn post today?</p>
                    <p>Do you have a specific topic or experience you'd like to share?</p>
                    <p>Just reply with:</p>
                    <ul>
                        <li><strong>"Yes"</strong> + your topic/experience</li>
                        <li><strong>"No"</strong> and we'll handle it</li>
                    </ul>
                    <p>Looking forward to creating something amazing for you!</p>
                    <p>Best regards,<br>Your LinkedIn Content Team</p>
                </div>
            """
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email using SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.from_email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, client_email, text)
            server.quit()
            
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"📧 Email sent at {timestamp}")
            print(f"✅ Topic prompt email sent to {client_email} via SMTP")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email via SMTP: {e}")
            return False
    
    def send_topic_prompt(self, client_email: str = "vaishnavisingh24011@gmail.com") -> bool:
        """Send a topic prompt email to the client."""
        try:
            data = {
                "from": self.from_email,
                "to": [client_email],
                "subject": "What's on your mind for your LinkedIn post today?",
                "html": """
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Hey! 👋</h2>
                        <p>What's on your mind for your LinkedIn post today?</p>
                        <p>Do you have a specific topic or experience you'd like to share?</p>
                        <p>Just reply with:</p>
                        <ul>
                            <li><strong>"Yes"</strong> + your topic/experience</li>
                            <li><strong>"No"</strong> and we'll handle it</li>
                        </ul>
                        <p>Looking forward to creating something amazing for you!</p>
                        <p>Best regards,<br>Your LinkedIn Content Team</p>
                    </div>
                """
            }

            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=data
            )

            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"📧 Email sent at {timestamp}")
            print(f"📧 Email status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Topic prompt email sent to {client_email}")
                return True
            else:
                print(f"❌ Error sending email: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending topic prompt email: {e}")
            return False
    
    def send_reminder_email(self, client_email: str = "vaishnavisingh24011@gmail.com") -> bool:
        """Send a reminder email if no response received."""
        try:
            data = {
                "from": self.from_email,
                "to": [client_email],
                "subject": "Reminder: Your LinkedIn post is waiting for your input",
                "html": """
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Quick reminder! ⏰</h2>
                        <p>We're ready to create your LinkedIn post, but we need your input.</p>
                        <p>Just reply with your topic or experience, or let us know if you'd like us to choose something for you.</p>
                        <p>Can't wait to create something amazing!</p>
                        <p>Best regards,<br>Your LinkedIn Content Team</p>
                    </div>
                """
            }

            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=data
            )

            if response.status_code == 200:
                print(f"✅ Reminder email sent to {client_email}")
                return True
            else:
                print(f"❌ Error sending reminder email: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending reminder email: {e}")
            return False 