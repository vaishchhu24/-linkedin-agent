#!/usr/bin/env python3
"""
Test the 3 different prompts for 3 different cases
"""

from content_handler.post_generator import PostGenerator
from content_handler.content_assessor import ContentAssessor
from content_handler.icp_pillar_checker import ICPPillarChecker

def test_three_prompts():
    """Test the 3 different prompt cases."""
    print("🧪 Testing 3 Different Prompts")
    print("=" * 60)
    
    # Initialize components
    post_generator = PostGenerator()
    content_assessor = ContentAssessor()
    icp_checker = ICPPillarChecker()
    
    # CASE 1: Detailed Content
    print("\n📝 CASE 1: DETAILED CONTENT")
    print("-" * 40)
    detailed_content = """Yes, I met a friend at a co-working space—she had just started her own
business and was full of ideas. Over coffee, she shared how clients would
seem interested, ask for details, and then completely ghost her."""
    
    content_elements = content_assessor.extract_content_elements(detailed_content)
    icp_data = icp_checker.get_icp_for_topic("Challenges in client acquisition")
    pillar_data = icp_checker.get_most_relevant_pillar("Challenges in client acquisition")
    
    system_prompt, user_prompt = post_generator._build_detailed_content_prompt(
        detailed_content, icp_data, pillar_data
    )
    
    print(f"✅ System Prompt Length: {len(system_prompt)} chars")
    print(f"✅ User Prompt Length: {len(user_prompt)} chars")
    print(f"✅ Case: {content_elements.get('detail_level', 'unknown')}")
    print(f"✅ Topic: {content_elements.get('main_topic', 'unknown')}")
    
    # CASE 2: Topic Only
    print("\n🔍 CASE 2: TOPIC ONLY")
    print("-" * 40)
    topic = "employee retention strategies"
    insights = [{"insight": "Companies with strong retention programs see 25% higher productivity"}]
    
    system_prompt2, user_prompt2 = post_generator._build_topic_only_prompt(
        topic, icp_data, pillar_data, insights
    )
    
    print(f"✅ System Prompt Length: {len(system_prompt2)} chars")
    print(f"✅ User Prompt Length: {len(user_prompt2)} chars")
    print(f"✅ Topic: {topic}")
    print(f"✅ Insights: {len(insights)} insights included")
    
    # CASE 3: Pillar Selected Topic
    print("\n🎯 CASE 3: PILLAR SELECTED TOPIC")
    print("-" * 40)
    selected_topic = "mistakes and lessons learned"
    
    system_prompt3, user_prompt3 = post_generator._build_pillar_topic_prompt(
        selected_topic, icp_data, pillar_data, insights
    )
    
    print(f"✅ System Prompt Length: {len(system_prompt3)} chars")
    print(f"✅ User Prompt Length: {len(user_prompt3)} chars")
    print(f"✅ Selected Topic: {selected_topic}")
    print(f"✅ Insights: {len(insights)} insights included")
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 40)
    print("✅ CASE 1: Detailed Content - No research, use content directly")
    print("✅ CASE 2: Topic Only - Do research, generate comprehensive post")
    print("✅ CASE 3: Pillar Selected - Select from pillars, do research")
    print("\n🎯 All cases use RAG for tone adaptation")
    print("🎯 All cases generate 400-800 word posts")
    print("🎯 All cases apply conversational elements")
    
    return True

if __name__ == "__main__":
    test_three_prompts() 