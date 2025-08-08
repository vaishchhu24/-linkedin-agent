#!/usr/bin/env python3
"""
Test the complete workflow: Email Response → Content Generation → Airtable Logging
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
from content_handler.content_assessor import ContentAssessor
from airtable_logger import AirtableLogger
from hook_generator import get_diverse_hook

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_workflow():
    """Test the complete workflow from email response to Airtable logging."""
    
    print("🚀 Complete Workflow Test")
    print("=" * 50)
    
    # Initialize components
    post_generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    content_assessor = ContentAssessor()
    airtable_logger = AirtableLogger()
    
    # Simulate Sam's email response
    sams_email_response = """
    Yes, I want to create a post about pricing my HR consulting services. 
    I've been struggling with this for months. I know I'm good at what I do, 
    but I'm not sure how much to charge. I see other consultants charging 
    much more than me, but I don't want to overprice myself. What do you think?
    """
    
    print(f"📧 Sam's Email Response:")
    print(f"'{sams_email_response.strip()}'")
    print("-" * 50)
    
    # Step 1: Assess content detail level
    print("🔍 Step 1: Assessing Content Detail Level")
    content_elements = content_assessor.extract_content_elements(sams_email_response)
    print(f"Content Elements: {content_elements}")
    
    # Step 2: Get ICP and pillar data
    print("\n🎯 Step 2: Getting ICP and Pillar Data")
    topic = content_elements.get('main_topic', 'pricing services')
    icp_data = icp_checker.get_icp_for_topic(topic)
    pillar_info = icp_checker.get_most_relevant_pillar(topic)
    
    print(f"Topic: {topic}")
    print(f"ICP Segment: {icp_data.get('segment', 'Unknown')}")
    print(f"Pillar: {pillar_info.get('title', 'Unknown')}")
    
    # Step 3: Generate diverse hook
    print("\n🎣 Step 3: Generating Diverse Hook")
    hook = get_diverse_hook(topic)
    print(f"Generated Hook: {hook}")
    
    # Step 4: Generate LinkedIn post
    print("\n📝 Step 4: Generating LinkedIn Post")
    result = post_generator.generate_from_detailed_content(
        sams_email_response,
        content_elements,
        icp_data,
        pillar_info
    )
    
    if result.get('success'):
        post_content = result['post']
        print(f"✅ Generated Post ({result['word_count']} words):")
        print(f"'{post_content}'")
        
        # Step 5: Log to Airtable
        print("\n📊 Step 5: Logging to Airtable")
        try:
            airtable_result = airtable_logger.write_post_to_airtable(
                topic=topic,
                post=post_content
            )
            
            if airtable_result:
                print(f"✅ Logged to Airtable successfully!")
            else:
                print(f"❌ Airtable logging failed")
                
        except Exception as e:
            print(f"❌ Error logging to Airtable: {e}")
    
    else:
        print(f"❌ Failed to generate post: {result.get('error')}")
    
    print("\n" + "=" * 50)
    print("🎉 Complete Workflow Test Finished!")

if __name__ == "__main__":
    test_complete_workflow() 