#!/usr/bin/env python3
"""
Approval Handler - Email Final Post Module
Sends final posts for client approval
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

from config import RESEND_API_KEY

class FinalPostEmailer:
    def __init__(self):
        """Initialize the final post emailer."""
        self.api_key = RESEND_API_KEY
        self.from_email = "Empowrd Agent <vaishnavis@valixio.site>"
        print("📧 Final Post Emailer initialized")
    
    def send_final_post(self, post_content: str, client_email: str = "vaishnavisingh24011@gmail.com") -> bool:
        """Send final post for client approval."""
        try:
            data = {
                "from": self.from_email,
                "to": [client_email],
                "subject": "Your LinkedIn post is ready for approval!",
                "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Your LinkedIn post is ready! 🎉</h2>
                        <p>Here's your refined LinkedIn post based on your feedback:</p>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="white-space: pre-wrap; font-family: 'Courier New', monospace; line-height: 1.6;">
                                {post_content}
                            </p>
                        </div>
                        
                        <p><strong>Please reply with:</strong></p>
                        <ul>
                            <li><strong>"I like this post a lot, this can be posted"</strong> - to approve and post</li>
                            <li><strong>"I don't like this post"</strong> - to request further changes</li>
                            <li><strong>Specific feedback</strong> - to provide detailed suggestions</li>
                        </ul>
                        
                        <p>Looking forward to your response!</p>
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
            print(f"📧 Final post email sent at {timestamp}")
            print(f"📧 Email status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Final post email sent to {client_email}")
                return True
            else:
                print(f"❌ Error sending final post email: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending final post email: {e}")
            return False 