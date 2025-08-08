#!/usr/bin/env python3
"""
Start Complete Automated Workflow with RAG Learning
Simple script to start the complete system
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_workflow_with_rag import AutomatedWorkflowWithRAG
from config.email_config import EmailSettings

def main():
    """Start the complete automated workflow with RAG learning."""
    
    print("🚀 Starting Complete Automated Workflow with RAG Learning")
    print("=" * 70)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📧 Monitoring: {EmailSettings.FROM_EMAIL}")
    print(f"📧 Client Email: {EmailSettings.TO_EMAIL}")
    print("⏰ Email Check: Every 5 minutes")
    print("🧠 RAG Learning: Every hour")
    print("=" * 70)
    print("🔄 Complete System Features:")
    print("   📧 Email Monitoring & Processing")
    print("   🎯 Intelligent Content Generation")
    print("   🧠 RAG-Based Learning from Feedback")
    print("   📊 Airtable Integration")
    print("   🎣 Dynamic Hook Generation")
    print("   📈 Continuous Quality Improvement")
    print("=" * 70)
    print("🛑 Press Ctrl+C to stop the system")
    print()
    
    try:
        # Initialize and start the complete automated workflow
        workflow = AutomatedWorkflowWithRAG()
        workflow.monitor_and_process_replies(check_interval=300, rag_interval=3600)
        
    except KeyboardInterrupt:
        print("\n🛑 Complete automated workflow stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 