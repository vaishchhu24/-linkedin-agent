#!/usr/bin/env python3
"""
Quick RAG Post Adder
Quickly add a single post to RAG store from command line
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory
from config.email_config import EmailSettings

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 quick_add_post.py 'topic' 'post content' [voice_quality] [post_quality]")
        print("Example: python3 quick_add_post.py 'pricing strategies' 'Your post content here...' 9 8")
        sys.exit(1)
    
    topic = sys.argv[1]
    post_content = sys.argv[2]
    voice_quality = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    post_quality = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    
    # Create post data
    post_data = {
        "topic": topic,
        "post": post_content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_id": EmailSettings.CLIENT_EMAIL.split('@')[0],
        "feedback": "yes",
        "voice_quality": voice_quality,
        "post_quality": post_quality,
        "post_hash": f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    # Add to RAG
    rag_memory = RAGMemory()
    success = rag_memory.add_post(post_data)
    
    if success:
        print("✅ Post added successfully to RAG store!")
        print(f"📝 Topic: {topic}")
        print(f"🎯 Quality: Voice {voice_quality}/10, Post {post_quality}/10")
    else:
        print("❌ Failed to add post to RAG store")
        sys.exit(1)

if __name__ == "__main__":
    main() 