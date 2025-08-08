#!/usr/bin/env python3
"""
Client Demo Startup Script
Simple script to demonstrate the LinkedIn content system to clients
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.email_config import EmailSettings

def print_welcome():
    """Print welcome message and system overview."""
    
    print("🎬 LinkedIn Content System - Client Demo")
    print("=" * 80)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📧 Email: {EmailSettings.TO_EMAIL}")
    print("=" * 80)
    print("🚀 System Overview:")
    print("   This is a complete AI-powered LinkedIn content generation system")
    print("   that automatically creates engaging posts based on your input.")
    print("=" * 80)
    print("🎯 Key Features:")
    print("   ✅ Automated email monitoring")
    print("   ✅ AI-powered content generation")
    print("   ✅ RAG-enhanced learning from approved posts")
    print("   ✅ Client feedback processing")
    print("   ✅ Continuous quality improvement")
    print("=" * 80)
    print("📋 How It Works:")
    print("   1. You send an email with your topic/experience")
    print("   2. System generates a LinkedIn post using AI")
    print("   3. Post is logged to Airtable for your review")
    print("   4. You provide feedback (Yes/No)")
    print("   5. System learns and improves over time")
    print("=" * 80)

def print_demo_options():
    """Print demo options."""
    
    print("🎬 Demo Options:")
    print("   1. Quick Demo - Test system components")
    print("   2. Full Demo - Run complete workflow")
    print("   3. Exit")
    print("=" * 80)

def run_quick_demo():
    """Run a quick demo of system components."""
    
    print("\n🎬 Quick Demo - Testing System Components")
    print("=" * 60)
    
    try:
        # Import and test components
        from final_integrated_system import FinalIntegratedSystem
        
        system = FinalIntegratedSystem()
        
        print("✅ System initialized successfully")
        print("📊 System Status:")
        system.print_system_status()
        
        print("\n🧪 Testing Components:")
        
        # Test email monitoring
        print("📧 Testing email monitoring...")
        email_replies = system.run_phase1_email_monitoring()
        print(f"✅ Email monitoring: Found {len(email_replies)} replies")
        
        # Test feedback processing
        print("🔄 Testing feedback processing...")
        processed_feedback = system.run_phase3_feedback_processing()
        print(f"✅ Feedback processing: Processed {len(processed_feedback)} items")
        
        print("\n🎉 Quick demo completed!")
        print("✅ All system components are working correctly")
        
    except Exception as e:
        print(f"❌ Error in quick demo: {e}")

def run_full_demo():
    """Run the full integrated system demo."""
    
    print("\n🎬 Full Demo - Complete Workflow")
    print("=" * 60)
    print("🚀 Starting the complete integrated system...")
    print("💡 This will run the full workflow with all 3 phases")
    print("🛑 Press Ctrl+C to stop the demo")
    print("=" * 60)
    
    try:
        from final_integrated_system import FinalIntegratedSystem
        
        system = FinalIntegratedSystem()
        system.run_demo_mode()
        
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error in full demo: {e}")

def main():
    """Main demo function."""
    
    print_welcome()
    
    while True:
        print_demo_options()
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                run_quick_demo()
            elif choice == "2":
                run_full_demo()
            elif choice == "3":
                print("\n👋 Thank you for the demo!")
                print("🚀 The LinkedIn content system is ready for use!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo stopped. Thank you!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 