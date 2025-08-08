#!/usr/bin/env python3
"""
Send daily prompt email to client
"""

from final_integrated_system import FinalIntegratedSystem

def send_prompt_email():
    print("📧 SENDING DAILY PROMPT EMAIL")
    print("=" * 50)
    
    system = FinalIntegratedSystem()
    success = system.send_daily_prompt_email()
    
    if success:
        print("✅ Daily prompt email sent successfully!")
        print(f"📧 Sent to: {system.airtable_logger.client_email}")
    else:
        print("❌ Failed to send daily prompt email")
    
    return success

if __name__ == "__main__":
    send_prompt_email() 