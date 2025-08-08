#!/usr/bin/env python3
"""
Test Automated Workflow
Simulates the complete automated workflow with a sample email reply
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_workflow import AutomatedWorkflow

def test_automated_workflow():
    """Test the automated workflow with a sample email reply."""
    
    print("🧪 Testing Automated Workflow")
    print("=" * 50)
    
    # Initialize the automated workflow
    workflow = AutomatedWorkflow()
    
    # Simulate Sam's email reply
    sample_email_reply = {
        "email_id": "test_email_001",
        "from_email": "vaishnavisingh24011@gmail.com",
        "subject": "Re: What's on your mind for your LinkedIn post today?",
        "content": """
        Yes, I want to create a post about pricing my HR consulting services. 
        I've been struggling with this for months. I know I'm good at what I do, 
        but I'm not sure how much to charge. I see other consultants charging 
        much more than me, but I don't want to overprice myself. What do you think?
        """,
        "date": datetime.now(timezone.utc).isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }
    
    print("📧 Simulating Sam's email reply:")
    print(f"From: {sample_email_reply['from_email']}")
    print(f"Subject: {sample_email_reply['subject']}")
    print(f"Content: {sample_email_reply['content'].strip()}")
    print("-" * 50)
    
    # Process the email through the automated workflow
    print("🔄 Processing through automated workflow...")
    success = workflow.process_email_workflow(sample_email_reply)
    
    if success:
        print("✅ Automated workflow completed successfully!")
        
        # Get workflow status
        status = workflow.get_workflow_status()
        print(f"📊 Workflow Status:")
        print(f"  - Monitoring Active: {status['monitoring_active']}")
        print(f"  - Processed Emails: {status['processed_emails_count']}")
        print(f"  - Last Check: {status['last_check']}")
        print(f"  - Client: {status['client']}")
        
    else:
        print("❌ Automated workflow failed")
    
    print("=" * 50)

def test_workflow_status():
    """Test the workflow status functionality."""
    
    print("\n📊 Testing Workflow Status")
    print("=" * 30)
    
    workflow = AutomatedWorkflow()
    status = workflow.get_workflow_status()
    
    print("Current Workflow Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")

def main():
    """Run all automated workflow tests."""
    
    print("🚀 Automated Workflow Test Suite")
    print("=" * 60)
    
    # Test the complete workflow
    test_automated_workflow()
    
    # Test workflow status
    test_workflow_status()
    
    print("\n" + "=" * 60)
    print("✅ All automated workflow tests completed!")

if __name__ == "__main__":
    main() 