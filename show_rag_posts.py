#!/usr/bin/env python3
"""
Show all posts in RAG store for review
"""

from rag_memory import RAGMemory

def show_all_posts():
    rag = RAGMemory()
    
    print("📋 ALL POSTS IN RAG STORE:")
    print("=" * 80)
    
    for i, post in enumerate(rag.metadata, 1):
        print(f"{i}. Topic: {post.get('topic', 'unknown')}")
        print(f"   Client ID: {post.get('client_id', 'unknown')}")
        print(f"   Quality: Voice {post.get('voice_quality', 0)}/10, Post {post.get('post_quality', 0)}/10")
        print(f"   Timestamp: {post.get('timestamp', 'unknown')}")
        print(f"   Post Preview: {post.get('post', '')[:150]}...")
        print("")

if __name__ == "__main__":
    show_all_posts() 