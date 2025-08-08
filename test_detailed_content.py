#!/usr/bin/env python3
"""
Test detailed content processing
"""

from content_handler.post_generator import PostGenerator
from content_handler.content_assessor import ContentAssessor
from content_handler.icp_pillar_checker import ICPPillarChecker

def test_detailed_content():
    """Test processing the detailed content email."""
    print("🧪 Testing Detailed Content Processing")
    print("=" * 50)
    
    # Your detailed email content
    detailed_content = """Yes, I met a friend at a co-working space—she had just started her own
business and was full of ideas. Over coffee, she shared how clients would
seem interested, ask for details, and then completely ghost her. It was
something I hadn't thought much about, but she said it happened more often
than expected. Still, she wasn't discouraged—just learning how to set
clearer boundaries and move on quicker. We kept meeting up, talking about
work and swapping tips. It was nice seeing a friend navigate the ups and
downs of running something on her own."""
    
    print(f"📧 Detailed Content: {detailed_content[:100]}...")
    print("-" * 50)
    
    # Initialize components
    content_assessor = ContentAssessor()
    post_generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    
    # Step 1: Content Assessment
    print("🔍 Step 1: Content Assessment")
    content_elements = content_assessor.extract_content_elements(detailed_content)
    print(f"   Detail Level: {content_elements.get('detail_level', 'unknown')}")
    print(f"   Main Topic: {content_elements.get('main_topic', 'unknown')}")
    
    # Step 2: ICP and Pillar Data
    print("\n🎯 Step 2: ICP and Pillar Data")
    topic = content_elements.get('main_topic', detailed_content)
    icp_data = icp_checker.get_icp_for_topic(topic)
    pillar_data = icp_checker.get_most_relevant_pillar(topic)
    
    print(f"   Topic: {topic}")
    print(f"   ICP Segment: {icp_data.get('segment', 'unknown')}")
    print(f"   Pillar: {pillar_data.get('name', 'unknown')}")
    
    # Step 3: Generate Post
    print("\n📝 Step 3: Generate Post from Detailed Content")
    try:
        result = post_generator.generate_from_detailed_content(
            detailed_content, content_elements, icp_data, pillar_data
        )
        
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
    
    print("\n💡 Summary:")
    print("-" * 50)
    print("✅ Should process as detailed content (no research needed)")
    print("✅ Should use your written story directly")
    print("✅ Should apply RAG tone/style from approved posts")
    print("✅ Should generate quickly without insights")
    
    return True

if __name__ == "__main__":
    test_detailed_content() 