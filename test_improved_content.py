#!/usr/bin/env python3
"""
Test Improved Content Generation
Demonstrates content generation with proper topics, research, and value
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_handler.phase2_workflow import Phase2Workflow
from content_handler.icp_pillar_checker import ICPPillarChecker
from content_handler.insight_fetcher import InsightFetcher

def test_improved_content_generation():
    """Test the improved content generation with topics and research."""
    
    print("🧪 Testing Improved Content Generation")
    print("=" * 60)
    
    # Test content pillars and ICP
    print("🔍 Step 1: Testing Content Pillars and ICP")
    print("-" * 40)
    
    icp_checker = ICPPillarChecker()
    
    # Show available content pillars
    pillars = icp_checker.get_all_pillars()
    print(f"✅ Available Content Pillars: {len(pillars)}")
    for i, pillar in enumerate(pillars[:3]):  # Show first 3
        print(f"   {i+1}. {pillar.get('title', 'N/A')}")
        print(f"      Topics: {', '.join(pillar.get('topics', [])[:2])}")
        print(f"      Hooks: {', '.join(pillar.get('hooks', [])[:1])}")
        print()
    
    # Show ICP data
    icp_data = icp_checker.get_icp_data()
    print(f"✅ ICP Target Audience: {icp_data.get('target_audience', 'N/A')}")
    print(f"✅ ICP Pain Points: {', '.join(icp_data.get('pain_points', [])[:3])}")
    print(f"✅ ICP Goals: {', '.join(icp_data.get('goals', [])[:3])}")
    print()
    
    # Test insight fetching
    print("🔍 Step 2: Testing Insight Fetching")
    print("-" * 40)
    
    insight_fetcher = InsightFetcher()
    
    # Test fetching insights for a relevant topic
    test_topic = "pricing strategies for HR consultants"
    print(f"📝 Fetching insights for: {test_topic}")
    
    insights = insight_fetcher.fetch_topic_insights(
        topic=test_topic,
        max_insights=2,
        source="reddit"
    )
    
    print(f"✅ Fetched {len(insights)} insights")
    for i, insight in enumerate(insights[:2]):
        print(f"   Insight {i+1}: {insight.get('content', 'N/A')[:100]}...")
    print()
    
    # Test improved content generation
    print("🚀 Step 3: Testing Improved Content Generation")
    print("-" * 40)
    
    workflow = Phase2Workflow()
    
    # Test with a detailed user input
    detailed_input = """Yes, I had a breakthrough with a client this week. She was struggling with pricing her HR consulting services and was constantly undercharging. I shared my own experience of how I went from charging $50/hour to $500/hour by focusing on value-based pricing. She implemented the strategy and just landed a $15,000 retainer! The key was helping her understand that she wasn't selling time, she was selling transformation."""
    
    print(f"📝 User Input: {detailed_input[:100]}...")
    print()
    
    result = workflow.process_user_input(
        user_input=detailed_input,
        content_type="detailed_content"
    )
    
    print(f"✅ Generation Success: {result['success']}")
    print(f"✅ Word Count: {result.get('word_count', 'N/A')}")
    print(f"✅ Generation Method: {result.get('generation_method', 'N/A')}")
    
    if 'metadata' in result:
        metadata = result['metadata']
        print(f"✅ Pillar Used: {metadata.get('pillar_used', 'N/A')}")
        print(f"✅ Insights Count: {metadata.get('insights_count', 'N/A')}")
    
    print()
    print("📝 Generated Post:")
    print("-" * 40)
    print(result['post'])
    print()
    
    # Test with a brief topic
    print("🚀 Step 4: Testing Brief Topic Generation")
    print("-" * 40)
    
    brief_topic = "client acquisition challenges"
    print(f"📝 Brief Topic: {brief_topic}")
    print()
    
    result2 = workflow.process_user_input(
        user_input=brief_topic,
        content_type="general_topic"
    )
    
    print(f"✅ Generation Success: {result2['success']}")
    print(f"✅ Word Count: {result2.get('word_count', 'N/A')}")
    print(f"✅ Generation Method: {result2.get('generation_method', 'N/A')}")
    
    if 'metadata' in result2:
        metadata = result2['metadata']
        print(f"✅ Pillar Used: {metadata.get('pillar_used', 'N/A')}")
        print(f"✅ Insights Count: {metadata.get('insights_count', 'N/A')}")
    
    print()
    print("📝 Generated Post:")
    print("-" * 40)
    print(result2['post'])
    print()
    
    print("🎯 Test Complete!")

if __name__ == "__main__":
    test_improved_content_generation() 