import json
import random
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import openai

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import importlib.util
project_root = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

from trends.perplexity_fetcher import fetch_reddit_insights
from trends.insight_cache import InsightCache
from email_utils.icp_profile import get_icp
from feedback_retriever import get_feedback_context
from airtable_logger import write_post_to_airtable
from email_utils.scheduler import send_topic_prompt_email, send_manual_topic_prompt

class NaturalContentGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.content_pillars = self.load_content_pillars()
        self.voice_analysis = self.load_voice_analysis()
        self.used_topics = self.load_used_topics()
        self.insight_cache = InsightCache()
        
    def load_content_pillars(self) -> Dict:
        """Load content pillars for topic selection."""
        try:
            with open('data/content_pillars.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Content pillars file not found")
            return {"content_pillars": []}
    
    def load_voice_analysis(self) -> Dict:
        """Load client voice analysis."""
        try:
            with open('data/client_voice_analysis.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Voice analysis file not found")
            return {}
    
    def load_used_topics(self) -> List[str]:
        """Load recently used topics to avoid repetition."""
        try:
            with open('data/used_topics.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_used_topic(self, topic: str):
        """Save used topic to avoid repetition."""
        self.used_topics.append(topic)
        # Keep only last 20 topics
        self.used_topics = self.used_topics[-20:]
        try:
            with open('data/used_topics.json', 'w') as f:
                json.dump(self.used_topics, f)
        except Exception as e:
            print(f"Could not save used topic: {e}")
    
    def select_content_pillar(self) -> Dict:
        """Select a content pillar, avoiding recently used ones."""
        pillars = self.content_pillars.get('content_pillars', [])
        if not pillars:
            return {}
        
        # Filter out recently used pillars and topics
        available_pillars = []
        for pillar in pillars:
            pillar_title = pillar.get('title', '')
            pillar_topics = pillar.get('topics', [])
            
            # Check if pillar title or any of its topics were recently used
            recently_used = (pillar_title in self.used_topics[-10:] or 
                           any(topic in self.used_topics[-10:] for topic in pillar_topics))
            
            if not recently_used:
                available_pillars.append(pillar)
        
        # If all pillars recently used, reset and use all
        if not available_pillars:
            available_pillars = pillars
            print("🔄 All pillars recently used, resetting selection")
        
        selected_pillar = random.choice(available_pillars)
        return selected_pillar
    
    def select_topic_from_pillar(self, pillar: Dict) -> str:
        """Select a specific topic from the pillar."""
        topics = pillar.get('topics', [])
        if not topics:
            topic = pillar.get('title', 'HR consulting')
        else:
            topic = random.choice(topics)
        
        # Save the actual topic used
        self.save_used_topic(topic)
        return topic
    
    def get_fresh_insights(self, topic: str) -> str:
        """Get fresh insights from cache or Perplexity/Reddit for the topic."""
        
        # First, try to get cached insight
        cached_insight = self.insight_cache.get_cached_insight(topic)
        if cached_insight:
            return f"Cached insights: {cached_insight[:200]}..."
        
        # If no cache, try to get related insights
        related_insights = self.insight_cache.get_related_insights(topic)
        if related_insights:
            related_insight = related_insights[0]['insight']
            return f"Related insights: {related_insight[:200]}..."
        
        # If no cache or related insights, fetch fresh ones
        try:
            print(f"🔍 Fetching fresh insights for: {topic}")
            insights = fetch_reddit_insights(topic)
            if insights and len(insights) > 50:
                # Cache the new insight
                self.insight_cache.cache_insight(topic, insights)
                return f"Fresh insights found: {insights[:200]}..."
            else:
                return "No fresh insights found, using pillar content."
        except Exception as e:
            print(f"Error fetching insights: {e}")
            return "Using pillar content for topic."
    
    def generate_natural_post(self, topic: Optional[str] = None, client_id: str = "vaishnavi") -> str:
        """Generate a natural, conversational post using content pillars and fresh insights."""
        
        # Select content pillar and topic
        if not topic:
            pillar = self.select_content_pillar()
            topic = self.select_topic_from_pillar(pillar)
        else:
            pillar = self.select_content_pillar()  # Still get pillar for context
        
        # Get best available insights
        fresh_insights = self.get_best_insights_for_topic(topic)
        
        # Get feedback context
        feedback_context = get_feedback_context(client_id)
        icp = get_icp()
        
        # Build natural prompt
        prompt = f"""
You are creating a LinkedIn post for Mindability Business Coaching. The client has a conversational, direct, and relatable voice.

CONTENT PILLAR SELECTED:
{json.dumps(pillar, indent=2)}

TOPIC: {topic}

CONTENT PILLAR CONTEXT:
Title: {pillar.get('title', '')}
Description: {pillar.get('description', '')}
Available Topics: {', '.join(pillar.get('topics', []))}
Available Hooks: {', '.join(pillar.get('hooks', []))}

FRESH INSIGHTS: {fresh_insights}

CLIENT VOICE REQUIREMENTS:
* RAW, HONEST tone like talking to a friend
* Personal stories with specific details and real experiences
* Direct address to reader with "you"
* Use CAPS for emphasis throughout
* Short, punchy sentences
* Natural flow and rhythm
* 300-600 words (substantial, detailed posts)
* 2-3 relevant hashtags
* MUST include personal story with vulnerability
* MUST include specific lessons learned
* MUST include clear mission/values

CLIENT FEEDBACK: {feedback_context}

AUDIENCE: {icp}

CRITICAL: Use the EXACT raw, honest style from the example above.

WRITE LIKE THIS:
* Short, punchy sentences
* LOTS of CAPS for emphasis
* Bullet points for key insights and lessons
* Dashes for sub-points and details
* Raw vulnerability and honesty
* Personal stories with specific details
* Clear lessons learned in bullet format
* Mission statement at the end

AVOID:
* Quiz format (overused)
* Long paragraphs
* Formal language
* Generic advice

HOOK DIVERSITY: Use different opening styles:
- Direct statements: "I made a $50K mistake last year..."
- Questions: "What if the biggest hurdle isn't what you expect?"
- Scenarios: "You're in the middle of a client crisis..."
- Confessions: "I nearly quit 3 months into consulting..."
- Surprises: "The unexpected truth about..."
- Memories: "I remember the moment..."

Choose the format that best fits the topic, but prioritize story/humor and mistakes/struggles formats over quiz format.

The post should be substantial (400-800 words) with:
* Engaging hook that grabs attention
* Personal story with specific details and vulnerability
* Real lessons learned and insights
* Clear value and mission
* Natural conversation flow
* MUST be detailed and comprehensive

USE bullet points and dashes for clear structure. Write in organized, scannable format with bullet points for key points and dashes for sub-points. Use natural language, CAPS for emphasis, and make it feel authentic and valuable.

Write a natural, conversational LinkedIn post about the topic: {topic}

EXAMPLE STYLE (Raw, Honest, CAPS-heavy with bullet points):
"My first year in HR consulting was TOUGH.

• Tough to define my services
• Tough to talk about my revenue  
• Tough to have conversations about hourly rates

I felt like I was selling my time, rather than my expertise.

But here's what I learned:

• Clients NEED clarity on pricing
• Hourly rates give them comfort and transparency
• Daily rates work better for project-based work
• It's about VALUE, not time

The key shift:
- Stop selling your time
- Start selling your expertise
- Focus on outcomes, not hours

My mission is to help HR consultants build businesses that actually work for them."

Replace "[Topic]" with the actual topic name in the quiz title.

CRITICAL REQUIREMENT: The post MUST be about HR consulting and specifically about: {topic}

Choose the best format for the topic:
- Quiz format for interactive, engaging content
- Story with humor for relatable, light-hearted content  
- Mistakes and struggles for vulnerable, authentic content

DO NOT write:
- Jokes or unrelated content
- Generic business advice
- Personal life updates
- Anything that doesn't help HR consultants

ONLY write HR consulting posts that help HR consultants grow their business.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=config.FINE_TUNED_MODEL,
                messages=[
                    {"role": "system", "content": "You are a LinkedIn content creator who writes RAW, HONEST posts with LOTS of CAPS for emphasis and CLEAR BULLET POINTS for structure. Use the exact style from the example - short punchy sentences, organized bullet points, vulnerability, and authenticity. Write about HR consulting topics only. ALWAYS write substantial posts (400-800 words) with detailed personal stories and insights. Use CAPS for emphasis throughout, bullet points for key points, and dashes for sub-points."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # Higher temperature for more natural variation
                max_tokens=800,   # Ensure substantial posts
                presence_penalty=0.1,  # Encourage diverse content
                frequency_penalty=0.1   # Reduce repetition
            )
            
            post = response.choices[0].message.content
            cleaned_post = self.clean_post(post)
            
            # Log to Airtable with proper timestamp
            try:
                # Add timestamp to post for tracking
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"📅 Generated at: {timestamp}")
                
                write_post_to_airtable(
                    topic=topic,
                    post=cleaned_post
                )
                print("✅ Logged post to Airtable")
                
                # Small delay to ensure proper timestamp separation
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Failed to log to Airtable: {e}")
            
            return cleaned_post
            
        except Exception as e:
            print(f"Error generating post: {e}")
            return self.generate_fallback_post(topic, pillar)
    
    def clean_post(self, post: str) -> str:
        """Clean up the generated post."""
        # Remove any "Post:" prefixes
        if post.startswith("Post:"):
            post = post[5:].strip()
        
        # Remove any markdown formatting
        post = post.replace("**", "").replace("*", "")
        
        # Ensure proper spacing
        post = "\n\n".join([line.strip() for line in post.split("\n") if line.strip()])
        
        return post
    
    def generate_fallback_post(self, topic: str, pillar: Dict) -> str:
        """Generate a substantial fallback post if AI fails."""
        hooks = pillar.get('hooks', [])
        hook = random.choice(hooks) if hooks else f"I remember the moment I realized {topic.lower()} was the key to everything."
        
        return f"""{hook}

I spent YEARS struggling with this exact challenge.

At first, I thought it was about credentials. Then I thought it was about experience. But the truth? It's about MINDSET.

I learned this the hard way when I lost my biggest client because I was so focused on proving my worth that I forgot to actually deliver value.

It was humiliating. I questioned everything.

But here's what I discovered: {topic.lower()} isn't about perfection - it's about progress.

Now I help HR consultants navigate these exact challenges every day.

My mission? To help brilliant HR consultants build businesses that actually work for them.

What's your biggest struggle with {topic.lower()} right now?

#hrconsultants #hrleaders #mindset"""
    
    def generate_post_with_research(self, topic: str, client_id: str = "vaishnavi") -> str:
        """Generate a post with specific topic and research."""
        return self.generate_natural_post(topic, client_id)
    
    def get_content_pillar_ideas(self) -> List[Dict]:
        """Get all available content pillar ideas."""
        return self.content_pillars.get('content_pillars', [])
    
    def get_insight_stats(self) -> Dict:
        """Get insight cache statistics."""
        return self.insight_cache.get_cache_stats()
    
    def get_best_insights_for_topic(self, topic: str) -> str:
        """Get the best available insights for a topic, combining cache and fresh data."""
        
        # Get cached insight
        cached_insight = self.insight_cache.get_cached_insight(topic)
        if cached_insight:
            return f"📋 CACHED: {cached_insight}"
        
        # Get related insights
        related_insights = self.insight_cache.get_related_insights(topic)
        if related_insights:
            best_related = max(related_insights, key=lambda x: len(x['insight']))
            return f"🔗 RELATED: {best_related['insight']}"
        
        # Fetch fresh insights
        try:
            insights = fetch_reddit_insights(topic)
            if insights and len(insights) > 50:
                self.insight_cache.cache_insight(topic, insights)
                return f"🆕 FRESH: {insights}"
        except Exception as e:
            print(f"Error fetching insights: {e}")
        
        return "📚 Using pillar content and general HR consulting insights."
    
    def send_topic_prompt_email(self, client_email: str = "vaishnavisingh24011@gmail.com") -> bool:
        """Send a topic prompt email to the client."""
        try:
            success = send_topic_prompt_email(client_email)
            if success:
                print(f"📧 Topic prompt email sent to {client_email}")
            return success
        except Exception as e:
            print(f"❌ Error sending topic prompt email: {e}")
            return False
    
    def send_manual_topic_prompt(self, client_email: str = "vaishnavisingh24011@gmail.com") -> bool:
        """Send a manual topic prompt email to the client."""
        try:
            success = send_manual_topic_prompt(client_email)
            if success:
                print(f"📧 Manual topic prompt email sent to {client_email}")
            return success
        except Exception as e:
            print(f"❌ Error sending manual topic prompt email: {e}")
            return False

# Example usage
if __name__ == "__main__":
    generator = NaturalContentGenerator()
    
    print("🎯 Available Content Pillars:")
    for pillar in generator.get_content_pillar_ideas():
        print(f"- {pillar['title']}: {pillar['description']}")
        print(f"  Topics: {', '.join(pillar['topics'])}")
        print()
    
    # Check if user wants to send email prompt
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--email":
        print("📧 Sending topic prompt email...")
        success = generator.send_topic_prompt_email()
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")
        exit()
    
    print("📝 Generating natural post...")
    post = generator.generate_natural_post()
    print("\n" + "="*50)
    print("GENERATED POST:")
    print("="*50)
    print(post)
    print("="*50)
    
    # Show cache statistics
    stats = generator.get_insight_stats()
    print(f"\n📊 Insight Cache Stats:")
    print(f"Total cached topics: {stats['total_cached_topics']}")
    print(f"Recent cached topics: {stats['recent_cached_topics']}") 