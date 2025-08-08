import openai
import json
import os
import sys

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import importlib.util
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
FINE_TUNED_MODEL = config.FINE_TUNED_MODEL

from email_utils.icp_profile import get_icp
from feedback_retriever import get_feedback_context
from trends.perplexity_fetcher import fetch_reddit_insights

def generate_post(topic, context, client_id="vaishnavi"):
    """
    Generate a LinkedIn post using the natural content generator with content pillars and fresh insights.
    
    Args:
        topic: The topic to write about
        context: Additional context for the post
        client_id: Client identifier for feedback
        
    Returns:
        str: Generated LinkedIn post
    """
    try:
        # Use the new natural content generator
        from natural_content_generator import NaturalContentGenerator
        generator = NaturalContentGenerator()
        
        print(f"🎯 Using content pillars and fresh insights for topic: {topic}")
        
        # Generate post with topic and research
        post = generator.generate_post_with_research(topic, client_id)
        
        # Smart quality check the post
        try:
            from smart_quality_checker import SmartQualityChecker
            checker = SmartQualityChecker()
            print(f"🔍 Running smart quality check...")
            passes_quality = checker.validate_post_before_posting(post)
            
            if not passes_quality:
                print(f"⚠️ Post failed smart quality check - consider regenerating")
            else:
                print(f"✅ Post passed smart quality check")
        except Exception as e:
            print(f"⚠️ Smart quality check failed: {e}")
        
        print(f"✅ Post generated successfully using content pillars and fresh insights")
        return post
        
    except Exception as e:
        print(f"❌ Error generating post: {e}")
        # Return a fallback post if everything fails
        return f"I've been thinking about {topic} lately. It's something many HR consultants struggle with when transitioning from corporate. The key is to focus on your unique value and the real impact you can make. What's your biggest challenge with {topic}? #hrconsultants #hrleaders"

def clean_post(post):
    """
    Clean up the generated post.
    """
    if not post:
        return ""
    
    # Remove "Post:" prefix if present
    if post.startswith("Post:"):
        post = post[5:].strip()
    
    # Remove quotes if present
    if post.startswith('"') and post.endswith('"'):
        post = post[1:-1].strip()
    
    # Clean up extra whitespace
    import re
    post = re.sub(r'\n\s*\n', '\n\n', post)
    post = re.sub(r' +', ' ', post)
    
    return post.strip()

def generate_post_with_reddit_insights(topic, client_id="vaishnavi"):
    """
    Generate a post with Reddit insights for context.
    """
    try:
        # Fetch Reddit insights
        print(f"🔍 Fetching Reddit insights for: {topic}")
        reddit_insights = fetch_reddit_insights(topic)
        
        # Build context
        context = f"""
Reddit insights about {topic}:
{reddit_insights}

Use these insights to make the post more relevant and authentic.
"""
        
        # Generate post
        post = generate_post(topic, context, client_id)
        
        return post, reddit_insights
        
    except Exception as e:
        print(f"❌ Error generating post with Reddit insights: {e}")
        return "", ""

def generate_post_from_content_pillar(pillar_name, client_id="vaishnavi"):
    """
    Generate a post using a specific content pillar.
    """
    try:
        # Load content pillars
        with open('data/content_pillars.json', 'r') as f:
            pillars_data = json.load(f)
        
        # Find the pillar
        pillar = None
        for p in pillars_data.get('content_pillars', []):
            if pillar_name.lower() in p.get('title', '').lower():
                pillar = p
                break
        
        if not pillar:
            print(f"❌ Content pillar '{pillar_name}' not found")
            return ""
        
        # Build context from pillar
        context = f"""
Content Pillar: {pillar.get('title')}
Description: {pillar.get('description')}
Topics: {', '.join(pillar.get('topics', []))}
Hooks: {', '.join(pillar.get('hooks', []))}
"""
        
        # Use first topic or default
        topic = pillar.get('topics', ['HR consultant challenges'])[0]
        
        # Generate post
        post = generate_post(topic, context, client_id)
        
        return post
        
    except Exception as e:
        print(f"❌ Error generating post from content pillar: {e}")
        return ""

if __name__ == "__main__":
    # Test the post generator
    topic = "HR consultant initial struggles"
    post, insights = generate_post_with_reddit_insights(topic)
    
    print("Generated Post:")
    print("=" * 50)
    print(post)
    print("=" * 50) 