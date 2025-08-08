#!/usr/bin/env python3
"""
Test Different Content Formats
Tests various content formats including quiz-style content
"""

import os
import sys
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker

def test_quiz_format():
    """Test quiz-style content generation."""
    
    print("🧪 Testing Quiz Format Content")
    print("=" * 40)
    
    generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    
    # Get quiz pillar
    quiz_pillar = icp_checker.get_pillar_by_title("Quiz & Interactive Content")
    
    if not quiz_pillar:
        print("❌ Quiz pillar not found")
        return
    
    # Sample quiz content
    quiz_content = "I want to create a quiz to help HR consultants assess their pricing confidence"
    content_elements = {
        "main_topic": "pricing confidence quiz",
        "emotions": ["uncertainty", "confidence"],
        "details": ["quiz format", "self-assessment"],
        "insights": ["Many HR consultants undervalue their services"],
        "lessons_learned": ["Confidence comes from understanding your value"]
    }
    
    # Get ICP data
    icp_data = icp_checker.get_icp_data()
    
    result = generator.generate_from_detailed_content(
        quiz_content, content_elements, icp_data, quiz_pillar
    )
    
    if result.get('success'):
        print("✅ Quiz format generated successfully!")
        print(f"📊 Word count: {result['word_count']}")
        print(f"🎯 ICP Segment: {result['icp_segment']}")
        print("\n📝 Generated Quiz Content:")
        print("-" * 40)
        print(result['post'])
        print("-" * 40)
    else:
        print(f"❌ Failed to generate quiz content: {result.get('error')}")

def test_story_format():
    """Test story-style content generation."""
    
    print("\n🧪 Testing Story Format Content")
    print("=" * 40)
    
    generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    
    # Get story pillar
    story_pillar = icp_checker.get_pillar_by_title("Story Hooks & Personal Tales")
    
    if not story_pillar:
        print("❌ Story pillar not found")
        return
    
    # Sample story content
    story_content = "I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months."
    content_elements = {
        "main_topic": "employee retention client story",
        "emotions": ["frustration", "determination"],
        "details": ["client meeting", "3-step process", "40% reduction"],
        "insights": ["Process-based solutions work"],
        "lessons_learned": ["Systematic approach is key"]
    }
    
    # Get ICP data
    icp_data = icp_checker.get_icp_data()
    
    result = generator.generate_from_detailed_content(
        story_content, content_elements, icp_data, story_pillar
    )
    
    if result.get('success'):
        print("✅ Story format generated successfully!")
        print(f"📊 Word count: {result['word_count']}")
        print(f"🎯 ICP Segment: {result['icp_segment']}")
        print("\n📝 Generated Story Content:")
        print("-" * 40)
        print(result['post'])
        print("-" * 40)
    else:
        print(f"❌ Failed to generate story content: {result.get('error')}")

def test_question_format():
    """Test question-style content generation."""
    
    print("\n🧪 Testing Question Format Content")
    print("=" * 40)
    
    generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    
    # Get question pillar
    question_pillar = icp_checker.get_pillar_by_title("Question & Reflection Hooks")
    
    if not question_pillar:
        print("❌ Question pillar not found")
        return
    
    # Sample question content
    question_content = "I want to ask HR consultants to reflect on whether they're building a business or just a job"
    content_elements = {
        "main_topic": "business vs job reflection",
        "emotions": ["reflection", "awareness"],
        "details": ["self-assessment", "business model"],
        "insights": ["Many consultants create jobs instead of businesses"],
        "lessons_learned": ["Mindset shift is crucial for scaling"]
    }
    
    # Get ICP data
    icp_data = icp_checker.get_icp_data()
    
    result = generator.generate_from_detailed_content(
        question_content, content_elements, icp_data, question_pillar
    )
    
    if result.get('success'):
        print("✅ Question format generated successfully!")
        print(f"📊 Word count: {result['word_count']}")
        print(f"🎯 ICP Segment: {result['icp_segment']}")
        print("\n📝 Generated Question Content:")
        print("-" * 40)
        print(result['post'])
        print("-" * 40)
    else:
        print(f"❌ Failed to generate question content: {result.get('error')}")

def test_diverse_hooks():
    """Test the diverse hook generator with different topics."""
    print("🎣 Testing Diverse Hook Generator")
    print("=" * 50)
    
    test_topics = [
        "pricing your services",
        "getting your first client", 
        "imposter syndrome",
        "time management",
        "building credibility"
    ]
    
    from hook_generator import get_diverse_hook
    
    for topic in test_topics:
        hook = get_diverse_hook(topic)
        print(f"Topic: {topic}")
        print(f"Hook: {hook}")
        print("-" * 30)

def test_content_generation_with_hooks():
    """Test content generation with diverse hooks."""
    print("\n📝 Testing Content Generation with Diverse Hooks")
    print("=" * 50)
    
    from content_handler.post_generator import PostGenerator
    from content_handler.icp_pillar_checker import ICPPillarChecker
    
    generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    
    # Test topics
    test_cases = [
        {
            "topic": "pricing your services",
            "user_content": "I've been struggling with pricing my HR consulting services. I know I'm good at what I do, but I'm not sure how much to charge."
        },
        {
            "topic": "imposter syndrome", 
            "user_content": "Sometimes I feel like I don't deserve the success I've had. Other HR consultants seem so much more confident than me."
        }
    ]
    
    for case in test_cases:
        print(f"\n🎯 Topic: {case['topic']}")
        print(f"📝 User Content: {case['user_content']}")
        
        # Get ICP data
        icp_data = icp_checker.get_icp_for_topic(case['topic'])
        pillar_info = icp_checker.get_most_relevant_pillar(case['topic'])
        
        # Generate hook
        from hook_generator import get_diverse_hook
        hook = get_diverse_hook(case['topic'])
        print(f"🎣 Generated Hook: {hook}")
        
        # Generate post
        result = generator.generate_from_detailed_content(
            case['user_content'], 
            {"main_topic": case['topic']}, 
            icp_data, 
            pillar_info
        )
        
        if result.get('post'):
            print(f"📄 Generated Post:\n{result['post']}")
        else:
            print("❌ Failed to generate post")
        
        print("-" * 50)

def main():
    """Test all content formats."""
    
    print("🚀 Testing Different Content Formats")
    print("=" * 50)
    
    # Test quiz format
    test_quiz_format()
    
    # Test story format
    test_story_format()
    
    # Test question format
    test_question_format()
    
    print("\n🎉 All content format tests completed!")

if __name__ == "__main__":
    test_diverse_hooks()
    test_content_generation_with_hooks() 