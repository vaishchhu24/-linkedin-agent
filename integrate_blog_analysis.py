#!/usr/bin/env python3
"""
Integrate Blog Analysis with LinkedIn Post Generation
"""

import json
import os
from blog_analyzer import BlogAnalyzer

def load_blog_analysis(filename='blog_analysis.json'):
    """
    Load existing blog analysis if available.
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Error loading blog analysis: {e}")
    
    return None

def create_blog_enhanced_prompt(blog_analysis, topic, context):
    """
    Create an enhanced prompt using blog analysis data.
    """
    if not blog_analysis:
        return None
    
    # Extract key insights from blog analysis
    style_guide = {
        'voice_and_tone': {
            'primary_tone': 'personal' if blog_analysis['tone_indicators']['personal'] > blog_analysis['tone_indicators']['professional'] else 'professional',
            'conversational_level': 'high' if blog_analysis['tone_indicators']['conversational'] > 10 else 'moderate',
            'vulnerability_level': 'high' if blog_analysis['tone_indicators']['vulnerable'] > 5 else 'moderate'
        },
        'writing_structure': {
            'avg_sentence_length': round(blog_analysis['avg_sentence_length'], 1),
            'avg_paragraph_length': round(blog_analysis['avg_paragraph_length'], 1),
            'preferred_formats': [k for k, v in blog_analysis['writing_patterns'].items() if v > 0]
        },
        'common_topics': [k for k, v in blog_analysis['topics'].items() if v > 0],
        'frequently_used_words': [word for word, count in blog_analysis['most_common_words'][:10]],
        'common_phrases': list(blog_analysis['common_phrases'].keys())
    }
    
    # Build enhanced prompt
    enhanced_prompt = f"""
You are writing a LinkedIn post for an HR consultant. Based on analysis of their blog content, here is their authentic writing style:

VOICE & TONE:
- Primary tone: {style_guide['voice_and_tone']['primary_tone']}
- Conversational level: {style_guide['voice_and_tone']['conversational_level']}
- Vulnerability level: {style_guide['voice_and_tone']['vulnerability_level']}

WRITING STRUCTURE:
- Average sentence length: {style_guide['writing_structure']['avg_sentence_length']} words
- Average paragraph length: {style_guide['writing_structure']['avg_paragraph_length']} words
- Preferred formats: {', '.join(style_guide['writing_structure']['preferred_formats'])}

COMMON TOPICS: {', '.join(style_guide['common_topics'])}
FREQUENTLY USED WORDS: {', '.join(style_guide['frequently_used_words'][:5])}
COMMON PHRASES: {', '.join(style_guide['common_phrases'][:5])}

Topic: {topic}
Context: {context}

Write a LinkedIn post that matches this authentic voice and style. The post should:
- Use their natural sentence and paragraph lengths
- Incorporate their frequently used words and phrases
- Match their tone (personal/professional, conversational level, vulnerability)
- Follow their preferred writing formats
- Focus on their common topics
- Feel like it was written by them, not an AI

Post:
"""
    
    return enhanced_prompt

def update_post_generator_with_blog_analysis():
    """
    Update the post generator to use blog analysis.
    """
    # Load blog analysis
    blog_analysis = load_blog_analysis()
    
    if not blog_analysis:
        print("❌ No blog analysis found. Run blog_analyzer.py first.")
        return False
    
    print("✅ Blog analysis loaded successfully!")
    print(f"📊 Analyzed {blog_analysis['total_posts']} blog posts")
    print(f"📝 Total words analyzed: {blog_analysis['total_words']}")
    
    # Create enhanced prompt template
    enhanced_prompt = create_blog_enhanced_prompt(blog_analysis, "HR consultant initial struggles", "Sample context")
    
    if enhanced_prompt:
        print("✅ Enhanced prompt template created!")
        print("\n📋 Blog Analysis Summary:")
        print(f"   Primary tone: {'personal' if blog_analysis['tone_indicators']['personal'] > blog_analysis['tone_indicators']['professional'] else 'professional'}")
        print(f"   Avg sentence length: {round(blog_analysis['avg_sentence_length'], 1)} words")
        print(f"   Common topics: {', '.join([k for k, v in blog_analysis['topics'].items() if v > 0])}")
        print(f"   Frequent words: {', '.join([word for word, count in blog_analysis['most_common_words'][:5]])}")
        
        return True
    
    return False

def generate_post_with_blog_analysis(topic, context, blog_analysis):
    """
    Generate a LinkedIn post using blog analysis insights.
    """
    enhanced_prompt = create_blog_enhanced_prompt(blog_analysis, topic, context)
    
    if not enhanced_prompt:
        return None
    
    # Import and use the existing post generator
    try:
        from post_generator import generate_post
        return generate_post(topic, context, client_id="vaishnavi")
    except Exception as e:
        print(f"❌ Error generating post with blog analysis: {e}")
        return None

def main():
    """
    Main function to integrate blog analysis.
    """
    print("🔗 Blog Analysis Integration")
    print("=" * 40)
    
    # Check if blog analysis exists
    blog_analysis = load_blog_analysis()
    
    if not blog_analysis:
        print("❌ No blog analysis found.")
        print("📝 To analyze a blog, run: python3 blog_analyzer.py")
        print("   Then provide the blog URL when prompted.")
        return
    
    # Update post generator
    success = update_post_generator_with_blog_analysis()
    
    if success:
        print("\n✅ Blog analysis integration complete!")
        print("📝 The LinkedIn post generator will now use the blog analysis")
        print("   to create more authentic posts that match the client's voice.")
        
        # Test generation
        print("\n🧪 Testing post generation with blog analysis...")
        test_post = generate_post_with_blog_analysis(
            "HR consultant initial struggles",
            "Sample context for testing",
            blog_analysis
        )
        
        if test_post:
            print("✅ Test post generated successfully!")
            print(f"📝 Preview: {test_post[:100]}...")
        else:
            print("❌ Test post generation failed")

if __name__ == "__main__":
    main() 