#!/usr/bin/env python3
"""
RAG Cleanup Script
Clean up old posts from RAG store
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory

def main():
    """Main function to run RAG cleanup."""
    print("🧹 RAG Store Cleanup")
    print("=" * 50)
    
    rag_memory = RAGMemory()
    
    # Show current stats
    stats = rag_memory.get_stats()
    print(f"📊 Current RAG Store:")
    print(f"   Total posts: {stats['total_posts']}")
    print(f"   Average quality: {stats['avg_post_quality']}/10")
    
    # Show posts with dates
    print(f"\n📅 Recent posts:")
    posts = rag_memory.retrieve_similar_posts("", "", after_days=0, top_k=5)
    for i, post in enumerate(posts[:5], 1):
        try:
            post_date = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
            days_old = (datetime.now(timezone.utc) - post_date).days
            print(f"   {i}. {post.get('topic', 'Unknown')} ({days_old} days old)")
        except:
            print(f"   {i}. {post.get('topic', 'Unknown')} (date unknown)")
    
    # Run cleanup
    print(f"\n🧹 Cleaning up posts older than 45 days...")
    removed_count = rag_memory.cleanup_old_posts(days_old=45)
    
    if removed_count > 0:
        print(f"✅ Cleanup complete: removed {removed_count} old posts")
    else:
        print("✅ No old posts found to remove")
    
    # Show updated stats
    stats = rag_memory.get_stats()
    print(f"\n📊 Updated RAG Store:")
    print(f"   Total posts: {stats['total_posts']}")
    print(f"   Average quality: {stats['avg_post_quality']}/10")

if __name__ == "__main__":
    main() 