#!/usr/bin/env python3
"""
Clean RAG store to keep only posts from sam_posts_rag.json
"""

import json
from rag_memory import RAGMemory

def clean_rag_store():
    # Load the authentic Sam Eaton posts
    with open('sam_posts_rag.json', 'r') as f:
        authentic_posts = json.load(f)
    
    # Extract content from authentic posts for comparison
    authentic_content = []
    for post in authentic_posts:
        content = post.get('content', '').strip()
        if content:
            # Take first 100 characters as a unique identifier
            authentic_content.append(content[:100])
    
    print(f"📋 Found {len(authentic_content)} authentic posts in sam_posts_rag.json")
    
    # Load current RAG store
    rag = RAGMemory()
    current_posts = rag.metadata.copy()
    
    print(f"📊 Current RAG store has {len(current_posts)} posts")
    
    # Filter posts to keep only those that match authentic content
    posts_to_keep = []
    posts_to_remove = []
    
    for post in current_posts:
        post_content = post.get('post', '').strip()
        post_preview = post_content[:100]
        
        # Check if this post matches any authentic content
        is_authentic = any(post_preview in auth_content or auth_content in post_preview 
                          for auth_content in authentic_content)
        
        if is_authentic:
            posts_to_keep.append(post)
        else:
            posts_to_remove.append(post)
    
    print(f"✅ Keeping {len(posts_to_keep)} authentic posts")
    print(f"🗑️ Removing {len(posts_to_remove)} non-authentic posts")
    
    # Show what's being removed
    print("\n📋 Posts being removed:")
    for i, post in enumerate(posts_to_remove, 1):
        print(f"{i}. Topic: {post.get('topic', 'unknown')}")
        print(f"   Preview: {post.get('post', '')[:80]}...")
        print("")
    
    # Update RAG store with only authentic posts
    rag.metadata = posts_to_keep
    rag._save_metadata()
    
    # Rebuild FAISS index
    rag._rebuild_index()
    
    print(f"✅ RAG store cleaned! Now contains {len(posts_to_keep)} authentic posts")
    print("✅ FAISS index rebuilt")

if __name__ == "__main__":
    clean_rag_store() 