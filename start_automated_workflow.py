#!/usr/bin/env python3
"""
Start Automated Workflow
Simple script to start the automated workflow that monitors for Sam's email replies
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_workflow import AutomatedWorkflow
from config.email_config import EmailSettings

def main():
    """Start the automated workflow."""
    
    print("🚀 Starting Automated Workflow")
    print("=" * 50)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📧 Monitoring: {EmailSettings.FROM_EMAIL}")
    print(f"📧 Client Email: {EmailSettings.TO_EMAIL}")
    print("⏰ Check Interval: Every 5 minutes")
    print("=" * 50)
    print("🔄 The system will now:")
    print("   1. Monitor for Sam's email replies")
    print("   2. Process replies automatically")
    print("   3. Generate LinkedIn posts")
    print("   4. Log to Airtable")
    print("   5. Wait for Sam's feedback")
    print("=" * 50)
    print("🛑 Press Ctrl+C to stop the automated workflow")
    print()
    
    try:
        # Initialize and start the automated workflow
        workflow = AutomatedWorkflow()
        workflow.monitor_and_process_replies(check_interval=300)  # Check every 5 minutes
        
    except KeyboardInterrupt:
        print("\n🛑 Automated workflow stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 