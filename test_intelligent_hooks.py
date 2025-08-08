#!/usr/bin/env python3
"""
Test Intelligent Hook Selection with Perplexity Insights
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hook_agent import get_ai_hook
from content_handler.insight_fetcher import InsightFetcher
from content_handler.icp_pillar_checker import ICPPillarChecker

def test_intelligent_hook_selection():
    """Test intelligent hook selection with different topics."""
    
    print("🧠 Testing Intelligent Hook Selection")
    print("=" * 50)
    
    # Test topics with different emotional intensities
    test_topics = [
        "pricing your services",
        "imposter syndrome", 
        "getting your first client",
        "time management",
        "building credibility",
        "client acquisition challenges",
        "work-life balance",
        "scaling your HR business"
    ]
    
    for topic in test_topics:
        print(f"\n🎯 Topic: {topic}")
        hook = get_ai_hook(topic)
        print(f"🎣 AI-Generated Hook: {hook}")
        print("-" * 40)

def test_hooks_with_insights():
    """Test hook generation with Perplexity insights."""
    
    print("\n🔍 Testing Hooks with Perplexity Insights")
    print("=" * 50)
    
    insight_fetcher = InsightFetcher()
    icp_checker = ICPPillarChecker()
    
    # Test topics that would benefit from insights
    test_topics = [
        "pricing your services",
        "imposter syndrome",
        "client acquisition"
    ]
    
    for topic in test_topics:
        print(f"\n🎯 Topic: {topic}")
        
        # Get ICP data
        icp_data = icp_checker.get_icp_for_topic(topic)
        print(f"📊 ICP Segment: {icp_data.get('segment', 'Unknown')}")
        
        # Fetch insights
        print("🔍 Fetching insights...")
        insights = insight_fetcher.fetch_topic_insights(topic)
        
        if insights:
            print(f"📈 Found {len(insights)} insights")
            # Show first insight
            first_insight = insights[0]
            print(f"💡 Key Insight: {first_insight.get('content', '')[:100]}...")
            
            # Generate hook with topic + insight context
            enhanced_topic = f"{topic} - {first_insight.get('content', '')[:50]}"
            hook = get_ai_hook(enhanced_topic)
            print(f"🎣 Enhanced Hook: {hook}")
        else:
            print("❌ No insights found")
            hook = get_ai_hook(topic)
            print(f"🎣 Basic Hook: {hook}")
        
        print("-" * 40)

def test_hook_style_analysis():
    """Test the hook style analysis for different topic types."""
    
    print("\n🎨 Testing Hook Style Analysis")
    print("=" * 50)
    
    # Different types of topics to test style selection
    topic_types = {
        "question_topics": [
            "why do HR consultants struggle with pricing?",
            "what makes client acquisition so difficult?"
        ],
        "observation_topics": [
            "the pattern I see with successful HR consultants",
            "what all high-performing consultants do differently"
        ],
        "scenario_topics": [
            "imagine you're about to pitch to your biggest client",
            "picture this: you're scaling your HR business"
        ],
        "statement_topics": [
            "the biggest lie about HR consulting",
            "what most people get wrong about pricing"
        ],
        "reflection_topics": [
            "the moment I truly understood my value",
            "how my perspective on HR consulting changed"
        ],
        "challenge_topics": [
            "the hardest truth about building a consulting business",
            "what makes imposter syndrome so difficult to overcome"
        ],
        "realization_topics": [
            "it took me years to realize this about HR consulting",
            "the breakthrough moment that changed everything"
        ],
        "memory_topics": [
            "I remember the exact moment I knew I could do this",
            "the client meeting that changed my perspective"
        ],
        "confession_topics": [
            "I have to admit something about my pricing strategy",
            "the honest truth about my biggest business mistake"
        ],
        "surprise_topics": [
            "you won't believe what I discovered about client retention",
            "the shocking truth about HR consultant success rates"
        ]
    }
    
    for style, topics in topic_types.items():
        print(f"\n🎭 {style.replace('_', ' ').title()}:")
        for topic in topics:
            hook = get_ai_hook(topic)
            print(f"  Topic: {topic}")
            print(f"  Hook: {hook}")
            print()

def main():
    """Run all hook tests."""
    
    print("🚀 Intelligent Hook Selection Test Suite")
    print("=" * 60)
    
    # Test basic hook selection
    test_intelligent_hook_selection()
    
    # Test hooks with insights
    test_hooks_with_insights()
    
    # Test style analysis
    test_hook_style_analysis()
    
    print("\n" + "=" * 60)
    print("✅ All hook tests completed!")

if __name__ == "__main__":
    main() 