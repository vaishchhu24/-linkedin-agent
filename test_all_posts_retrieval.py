#!/usr/bin/env python3
"""
Test ALL Posts Retrieval
Verifies that the system retrieves ALL approved posts by the client
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory
from config.email_config import EmailSettings

def test_all_posts_retrieval():
    """Test that ALL approved posts are retrieved."""
    
    print("🧪 Testing ALL Posts Retrieval")
    print("=" * 50)
    
    rag_memory = RAGMemory()
    client_id = EmailSettings.CLIENT_NAME.lower().replace(" ", "_")
    
    print(f"👤 Client ID: {client_id}")
    print(f"📚 Current RAG Store Stats: {rag_memory.get_stats()}")
    print("-" * 30)
    
    # Test 1: Retrieve ALL posts (no recency filter)
    print("🔍 Test 1: Retrieving ALL posts (no recency filter)")
    all_posts = rag_memory.retrieve_similar_posts(
        topic="pricing",
        client_id=client_id,
        after_days=0,  # No recency filter
        top_k=None     # Get ALL posts
    )
    
    print(f"📊 Found {len(all_posts)} posts:")
    for i, post in enumerate(all_posts, 1):
        print(f"  {i}. {post.get('topic', 'Unknown')} (Quality: {post.get('voice_quality', 0)}/10)")
    
    print("-" * 30)
    
    # Test 2: Retrieve ALL posts for different topics
    test_topics = ["pricing", "imposter syndrome", "client acquisition", "hr consulting"]
    
    for topic in test_topics:
        print(f"🔍 Testing topic: '{topic}'")
        posts = rag_memory.retrieve_similar_posts(
            topic=topic,
            client_id=client_id,
            after_days=0,  # No recency filter
            top_k=None     # Get ALL posts
        )
        
        print(f"📊 Found {len(posts)} posts for '{topic}':")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post.get('topic', 'Unknown')}")
        print()
    
    print("-" * 30)
    
    # Test 3: Compare with limited retrieval
    print("🔍 Test 3: Comparing ALL vs Limited retrieval")
    
    all_posts = rag_memory.retrieve_similar_posts(
        topic="pricing",
        client_id=client_id,
        after_days=0,
        top_k=None  # ALL posts
    )
    
    limited_posts = rag_memory.retrieve_similar_posts(
        topic="pricing",
        client_id=client_id,
        after_days=0,
        top_k=3     # Only 3 posts
    )
    
    print(f"📊 ALL posts: {len(all_posts)}")
    print(f"📊 Limited posts: {len(limited_posts)}")
    
    if len(all_posts) > len(limited_posts):
        print("✅ Success: ALL posts retrieval returns more posts than limited retrieval")
    else:
        print("⚠️ Warning: ALL posts retrieval returns same number as limited retrieval")
    
    print("=" * 50)

def test_rag_context_generation():
    """Test RAG context generation with ALL posts."""
    
    print("\n📝 Testing RAG Context Generation")
    print("=" * 40)
    
    from content_handler.post_generator import PostGenerator
    
    post_generator = PostGenerator()
    
    # Test RAG context generation
    test_topics = ["pricing", "imposter syndrome", "hr consulting"]
    
    for topic in test_topics:
        print(f"🎯 Testing topic: '{topic}'")
        
        # Get RAG context
        rag_context = post_generator._get_rag_context(topic)
        
        if rag_context:
            # Count how many posts are in the context
            post_count = rag_context.count("Topic:")
            print(f"📚 RAG Context contains {post_count} posts")
            print(f"📝 Context preview: {rag_context[:200]}...")
        else:
            print("📭 No RAG context found")
        
        print()
    
    print("=" * 40)

def main():
    """Run all tests."""
    
    print("🚀 ALL Posts Retrieval Test Suite")
    print("=" * 60)
    
    # Test ALL posts retrieval
    test_all_posts_retrieval()
    
    # Test RAG context generation
    test_rag_context_generation()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 