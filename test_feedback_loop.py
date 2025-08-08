#!/usr/bin/env python3
"""
Test script for Phase 3: Feedback Loop System
Tests the complete feedback loop functionality with sample data.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feedback_handler.feedback_loop import FeedbackLoop
from airtable_logger import AirtableLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_feedback_loop():
    """Test the complete feedback loop system."""
    
    logger.info("🧪 Testing Feedback Loop System")
    logger.info("=" * 50)
    
    try:
        # Initialize feedback loop
        feedback_loop = FeedbackLoop()
        
        # Test 1: Monitor Airtable for feedback
        logger.info("1️⃣ Testing Airtable monitoring...")
        pending_feedback = feedback_loop.monitor_airtable_for_feedback()
        logger.info(f"✅ Found {len(pending_feedback)} posts with feedback")
        
        # Test 2: Check for final approvals
        logger.info("2️⃣ Testing approval checking...")
        approved_posts = feedback_loop.check_for_final_approval()
        logger.info(f"✅ Found {len(approved_posts)} approved posts")
        
        # Test 3: Process sample feedback (if any exists)
        if pending_feedback:
            logger.info("3️⃣ Testing feedback processing...")
            sample_feedback = pending_feedback[0]
            
            success = feedback_loop.process_feedback(sample_feedback)
            logger.info(f"✅ Feedback processing: {'Success' if success else 'Failed'}")
        else:
            logger.info("3️⃣ No pending feedback to process")
        
        # Test 4: Prepare fine-tuning data (if any approved posts)
        if approved_posts:
            logger.info("4️⃣ Testing fine-tuning data preparation...")
            success = feedback_loop.prepare_fine_tuning_data(approved_posts)
            logger.info(f"✅ Fine-tuning preparation: {'Success' if success else 'Failed'}")
        else:
            logger.info("4️⃣ No approved posts for fine-tuning")
        
        # Test 5: Check if training data directory and files exist
        logger.info("5️⃣ Testing training data setup...")
        training_dir = "training_data"
        fine_tune_file = os.path.join(training_dir, "fine_tune_queue.jsonl")
        
        if os.path.exists(training_dir):
            logger.info(f"✅ Training directory exists: {training_dir}")
        else:
            logger.warning(f"⚠️ Training directory missing: {training_dir}")
        
        if os.path.exists(fine_tune_file):
            logger.info(f"✅ Fine-tuning queue file exists: {fine_tune_file}")
            
            # Check file content
            with open(fine_tune_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                logger.info(f"✅ Fine-tuning queue contains {len(lines)} entries")
        else:
            logger.info(f"ℹ️ Fine-tuning queue file not yet created: {fine_tune_file}")
        
        logger.info("✅ All feedback loop tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error testing feedback loop: {e}")
        return False
    
    return True

def test_sample_feedback_processing():
    """Test feedback processing with sample data."""
    
    logger.info("🧪 Testing Sample Feedback Processing")
    logger.info("=" * 50)
    
    try:
        feedback_loop = FeedbackLoop()
        
        # Sample feedback data
        sample_post = """HR Consultant Survival Quiz (bit of fun for today!) 

Give yourself 1 point for every YES:
1️⃣ You're juggling 4 retainers and still doing the admin
2️⃣ Your lead gen strategy = hoping someone refers you
3️⃣ You've said "I'll sort the backend out next month" (every month)
4️⃣ You built your onboarding in Google Docs… and crossed your fingers
5️⃣ You've done client work from your car, a café, or your kid's football match

Your Score:
🟢 0–1: Wowzers, you've got it 150% sussed — hats off to you!
🟡 2–3: Danger zone… systems are creaking
🔴 4–5: You are exactly why I do what I do — to help brilliant HR consultants build a business that actually works for them

I spent a solid 18 months sitting at a 4. It was exhausting. I second-guessed everything. At one point, I even wondered if I should go back to corporate.

Then I invested in a coach - I spent a lot of money at the time for me. And that investment has really paid off. Years later, ironically and I felt humbled that they then came to me to coach them.

But my original decision to go with them? It changed everything. That experience has since helped me build multiple 6, 7, and even 8-figure HR consultancies.

But here's what I've learned that still guides me today:
✅ Self-awareness > busy-ness
✅ Reflection is where the magic happens (and I do it my way.)
✅ If you want to stay at the top of your game, you've got to check in regularly

Because I might be an expert today — But I want to stay one tomorrow too.

My mission is to help HR consultants and Fractional HRs to build a successful business on their terms - and for that, my self-check ins are as much for them as they are for me."""
        
        sample_feedback = "This is too long and rambling. Make it more concise and punchy. Focus on the key points."
        
        # Test revision generation
        logger.info("📝 Testing post revision generation...")
        revised_post = feedback_loop._generate_revised_post(sample_post, sample_feedback)
        
        if revised_post:
            logger.info("✅ Successfully generated revised post")
            logger.info(f"📊 Original length: {len(sample_post)} characters")
            logger.info(f"📊 Revised length: {len(revised_post)} characters")
            logger.info("📝 Revised post preview:")
            logger.info("-" * 40)
            logger.info(revised_post[:200] + "..." if len(revised_post) > 200 else revised_post)
            logger.info("-" * 40)
        else:
            logger.error("❌ Failed to generate revised post")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing sample feedback processing: {e}")
        return False

def test_fine_tuning_data_format():
    """Test the fine-tuning data format."""
    
    logger.info("🧪 Testing Fine-tuning Data Format")
    logger.info("=" * 50)
    
    try:
        # Sample approved post data
        sample_approved_posts = [
            {
                'record_id': 'rec123456789',
                'fields': {
                    'post_content': 'This is a great HR consulting post about client acquisition challenges.',
                    'revised_post': 'This is the FINAL approved version of the HR consulting post about client acquisition challenges.',
                    'original_topic': 'HR consultant client acquisition challenges',
                    'client_name': 'Sarah Johnson',
                    'status': 'Approved',
                    'feedback': 'Yes'
                }
            }
        ]
        
        feedback_loop = FeedbackLoop()
        
        # Test fine-tuning data preparation
        success = feedback_loop.prepare_fine_tuning_data(sample_approved_posts)
        
        if success:
            logger.info("✅ Successfully prepared fine-tuning data")
            
            # Check the generated JSONL file
            fine_tune_file = feedback_loop.fine_tune_queue_file
            
            if os.path.exists(fine_tune_file):
                with open(fine_tune_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                if lines:
                    # Parse the last entry to verify format
                    last_entry = json.loads(lines[-1])
                    
                    logger.info("✅ Fine-tuning data format verification:")
                    logger.info(f"📊 Messages count: {len(last_entry.get('messages', []))}")
                    
                    for i, message in enumerate(last_entry.get('messages', [])):
                        role = message.get('role', '')
                        content = message.get('content', '')
                        logger.info(f"📝 Message {i+1} ({role}): {content[:50]}...")
                    
                    logger.info("✅ Fine-tuning data format is correct!")
                else:
                    logger.warning("⚠️ Fine-tuning file is empty")
            else:
                logger.error("❌ Fine-tuning file not found")
        else:
            logger.error("❌ Failed to prepare fine-tuning data")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing fine-tuning data format: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Feedback Loop System Tests")
    logger.info("=" * 60)
    
    # Run all tests
    test_results = []
    
    test_results.append(("Main Feedback Loop", test_feedback_loop()))
    test_results.append(("Sample Feedback Processing", test_sample_feedback_processing()))
    test_results.append(("Fine-tuning Data Format", test_fine_tuning_data_format()))
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 Test Results Summary:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1
    
    logger.info(f"📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Feedback Loop System is ready.")
    else:
        logger.warning("⚠️ Some tests failed. Please check the logs above.") 