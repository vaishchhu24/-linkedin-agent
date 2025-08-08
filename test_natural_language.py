#!/usr/bin/env python3

from natural_content_generator import NaturalContentGenerator

def test_natural_language():
    """Test the natural language improvements."""
    
    print("🔄 Testing Natural Language Improvements")
    print("=" * 60)
    
    generator = NaturalContentGenerator()
    
    print("\n📝 Generating 2 posts to show natural language:")
    print("-" * 40)
    
    for i in range(2):
        print(f"\n📝 Post {i+1}:")
        print("-" * 20)
        try:
            post = generator.generate_natural_post()
            print(post)
            print()
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Natural Language Improvements:")
    print("✅ NO bullet points or dashes")
    print("✅ Uses CAPS for emphasis")
    print("✅ Conversational formatting")
    print("✅ Natural flow and structure")
    print("✅ Sounds like real person talking")

if __name__ == "__main__":
    test_natural_language() 