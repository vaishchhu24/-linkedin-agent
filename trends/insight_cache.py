import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class InsightCache:
    def __init__(self, cache_file: str = "data/insight_cache.json"):
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self) -> Dict:
        """Load existing cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}
    
    def save_cache(self):
        """Save cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_cached_insight(self, topic: str, max_age_days: int = 7) -> Optional[str]:
        """Get cached insight if it exists and is not too old."""
        if topic in self.cache:
            cached_data = self.cache[topic]
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            
            if datetime.now() - cached_time < timedelta(days=max_age_days):
                print(f"📋 Using cached insight for: {topic}")
                return cached_data['insight']
            else:
                print(f"🗑️ Cached insight expired for: {topic}")
                del self.cache[topic]
        
        return None
    
    def cache_insight(self, topic: str, insight: str):
        """Cache a new insight."""
        self.cache[topic] = {
            'insight': insight,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache()
        print(f"💾 Cached new insight for: {topic}")
    
    def get_related_insights(self, topic: str) -> list:
        """Get insights for related topics."""
        related_insights = []
        topic_keywords = topic.lower().split()
        
        for cached_topic, data in self.cache.items():
            # Check if topics are related
            if any(keyword in cached_topic.lower() for keyword in topic_keywords):
                related_insights.append({
                    'topic': cached_topic,
                    'insight': data['insight']
                })
        
        return related_insights
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_cached = len(self.cache)
        recent_cached = sum(
            1 for data in self.cache.values()
            if datetime.now() - datetime.fromisoformat(data['timestamp']) < timedelta(days=1)
        )
        
        return {
            'total_cached_topics': total_cached,
            'recent_cached_topics': recent_cached,
            'cache_file': self.cache_file
        } 