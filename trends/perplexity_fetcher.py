# perplexity_fetcher.py
import requests
import json
import sys
import os
import time

# Add project root to path for imports - more robust approach
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from the root config.py file
import importlib.util
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
PERPLEXITY_API_KEY = config.PERPLEXITY_API_KEY

def fetch_reddit_insights(topic, max_retries=3):
    """
    Fetch real Reddit insights for a given topic using Perplexity API.
    Retries multiple times to ensure we get real insights.
    """
    print(f"🔍 Fetching real Reddit insights for: {topic}")
    
    for attempt in range(max_retries):
        try:
            # Construct a more specific search query for Reddit insights
            search_query = f"Reddit pain points challenges {topic} HR consulting business coaching entrepreneur"
            
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # More specific prompt to get real Reddit insights
            prompt = f"""Search Reddit for real pain points and challenges related to '{topic}' in HR consulting, business coaching, and entrepreneurship.

IMPORTANT: Only return insights from actual Reddit discussions, not generic advice.

Search these specific subreddits:
- r/consulting
- r/entrepreneur  
- r/smallbusiness
- r/humanresources
- r/coaching
- r/recruiting
- r/freelance
- r/startups

Look for:
- Recent posts (last 6 months) asking for help with {topic}
- Comments sharing real struggles and frustrations
- Specific examples and situations people describe
- Emotional pain points (fear, confusion, overwhelm)

Return ONLY a numbered list of 3-5 real pain points in this exact format:
1. [Specific real pain point from Reddit] - [Brief context from actual discussion]
2. [Specific real pain point from Reddit] - [Brief context from actual discussion]
3. [Specific real pain point from Reddit] - [Brief context from actual discussion]

If you can't find specific Reddit discussions about {topic}, search for broader HR consulting challenges and adapt them to {topic}.

Keep each point under 80 words. No explanations, just the real pain points from Reddit."""
            
            data = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            print(f"   Attempt {attempt + 1}/{max_retries}: Calling Perplexity API...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                insights = result['choices'][0]['message']['content'].strip()
                
                # Validate that we got real insights, not generic content
                if insights and len(insights) > 50 and not insights.startswith("I don't have"):
                    print(f"✅ Successfully fetched real Reddit insights!")
                    print(f"   Insights length: {len(insights)} characters")
                    return insights
                else:
                    print(f"   Attempt {attempt + 1}: Got empty or generic response, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
            else:
                print(f"   Attempt {attempt + 1}: API error {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                    
        except Exception as e:
            print(f"   Attempt {attempt + 1}: Error - {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
    
    # Only fall back to generic content if all attempts failed
    print(f"⚠️ All attempts failed. Using fallback content for: {topic}")
    return f"""1. Imposter syndrome and self-doubt - Feeling unqualified despite experience
2. Pricing uncertainty - Not knowing how much to charge for services  
3. Client acquisition struggles - Difficulty finding and converting prospects
4. Time management challenges - Balancing client work with business development
5. Building credibility - Establishing trust without extensive case studies"""

if __name__ == "__main__":
    # Test the function
    test_topic = "Getting first clients"
    print(f"Testing Reddit insights for: {test_topic}")
    insights = fetch_reddit_insights(test_topic)
    print(f"Final insights:")
    print(insights)
# rag_fetcher.py
# Fetches trending insights for a given topic using the Perplexity API

import requests
import os

def fetch_rag_insights(topic: str) -> str:
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    PERPLEXITY_API_URL = "https://api.perplexity.ai/search"

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": topic,
        "sources": ["news", "reddit"],
        "freshness": "day",
        "numResults": 5
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            return "No recent insights found."

        summaries = [f"- {r.get('title', '')}: {r.get('snippet', '')}" for r in results]
        return "\n".join(summaries)

    except Exception as e:
        return f"Failed to fetch RAG insights: {str(e)}"
