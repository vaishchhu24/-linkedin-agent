#!/usr/bin/env python3

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from natural_content_generator import NaturalContentGenerator
from post_generator import generate_post

def test_old_vs_new():
    """Compare old rigid system vs new natural system."""
    
    print("🔄 Testing Old vs New Content Generation Systems")
    print("=" * 60)
    
    # Test topic
    topic = "pricing confidence"
    
    print(f"\n📝 Topic: {topic}")
    print("-" * 40)
    
    # Test old system (rigid)
    print("\n🔴 OLD SYSTEM (Rigid):")
    print("-" * 20)
    try:
        old_post = generate_post(topic, "Testing old system", "vaishnavi")
        print(old_post)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test new system (natural)
    print("\n🟢 NEW SYSTEM (Natural with Content Pillars):")
    print("-" * 20)
    try:
        generator = NaturalContentGenerator()
        new_post = generator.generate_post_with_research(topic, "vaishnavi")
        print(new_post)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Key Differences:")
    print("• OLD: Rigid structure, same format every time")
    print("• NEW: Natural variation, uses content pillars")
    print("• OLD: No fresh insights")
    print("• NEW: Integrates Perplexity/Reddit research")
    print("• OLD: Formulaic prompts")
    print("• NEW: Conversational, varied tone")

def test_content_pillar_rotation():
    """Test that the system rotates through different content pillars."""
    
    print("\n🔄 Testing Content Pillar Rotation")
    print("=" * 60)
    
    generator = NaturalContentGenerator()
    
    print("\n📊 Available Content Pillars:")
    pillars = generator.get_content_pillar_ideas()
    for i, pillar in enumerate(pillars, 1):
        print(f"{i}. {pillar['title']}")
        print(f"   Topics: {', '.join(pillar['topics'])}")
        print()
    
    print("\n🎲 Generating 3 posts to show variety:")
    print("-" * 40)
    
    for i in range(3):
        print(f"\n📝 Post {i+1}:")
        print("-" * 20)
        try:
            post = generator.generate_natural_post()
            print(post)
            print()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_old_vs_new()
    test_content_pillar_rotation() 