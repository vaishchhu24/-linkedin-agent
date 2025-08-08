#!/usr/bin/env python3
"""
Test Email Processing
Test how the system processes email replies with topics
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_handler.content_assessor import ContentAssessor
from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker

def test_email_processing():
    """Test email processing with your actual content."""
    print("🧪 Testing Email Processing")
    print("=" * 50)
    
    # Initialize components
    content_assessor = ContentAssessor()
    post_generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    
    # Your actual email content
    test_content = "Yes, client retention strategies for HR consultants"
    
    print(f"📧 Test Email Content: '{test_content}'")
    print("-" * 50)
    
    # Step 1: Content Assessment
    print("🔍 Step 1: Content Assessment")
    content_elements = content_assessor.extract_content_elements(test_content)
    print(f"   Detail Level: {content_elements.get('detail_level', 'unknown')}")
    print(f"   Main Topic: {content_elements.get('main_topic', 'unknown')}")
    print(f"   Emotions: {content_elements.get('emotions', [])}")
    print(f"   Details: {content_elements.get('details', [])}")
    
    # Step 2: ICP and Pillar Data
    print("\n🎯 Step 2: ICP and Pillar Data")
    topic = content_elements.get('main_topic', test_content)
    icp_data = icp_checker.get_icp_for_topic(topic)
    pillar_data = icp_checker.get_most_relevant_pillar(topic)
    
    print(f"   Topic: {topic}")
    print(f"   ICP Segment: {icp_data.get('segment', 'unknown')}")
    print(f"   Pillar: {pillar_data.get('name', 'unknown')}")
    
    # Step 3: Content Generation Decision
    print("\n🧠 Step 3: Content Generation Decision")
    if content_elements.get('detail_level') == 'detailed':
        print("   📝 Decision: Generate from detailed content")
        print("   🔄 Method: generate_from_detailed_content()")
    else:
        print("   🔍 Decision: Generate from topic with research")
        print("   🔄 Method: generate_trending_post()")
    
    # Step 4: Test Generation
    print("\n📝 Step 4: Test Post Generation")
    try:
        if content_elements.get('detail_level') == 'detailed':
            result = post_generator.generate_from_detailed_content(
                test_content, content_elements, icp_data, pillar_data
            )
        else:
            from content_handler.insight_fetcher import InsightFetcher
            insight_fetcher = InsightFetcher()
            insights = insight_fetcher.fetch_topic_insights(topic)
            result = post_generator.generate_trending_post(topic, insights, icp_data, pillar_data)
        
        if result and result.get('success'):
            print("   ✅ Post generated successfully!")
            print(f"   📝 Post length: {len(result.get('post', ''))} characters")
            print(f"   🎯 Topic: {result.get('topic', 'unknown')}")
            print(f"   📊 Method: {result.get('generation_method', 'unknown')}")
            
            # Show first 200 characters of the post
            post_preview = result.get('post', '')[:200] + "..." if len(result.get('post', '')) > 200 else result.get('post', '')
            print(f"   📄 Preview: {post_preview}")
        else:
            print(f"   ❌ Failed to generate post: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Error during generation: {e}")
    
    print("\n💡 Analysis:")
    print("-" * 50)
    print("The system should process 'Yes, client retention...' as:")
    print("1. ✅ 'Yes' response (not 'No')")
    print("2. 📝 Detailed content (not general)")
    print("3. 🎯 Topic: client retention strategies")
    print("4. 📝 Generate from detailed content method")
    
    return True

if __name__ == "__main__":
    test_email_processing() 