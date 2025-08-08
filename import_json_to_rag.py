#!/usr/bin/env python3
"""
Simple JSON to RAG Importer
Import posts from JSON file to RAG store
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory
from config.email_config import EmailSettings

def import_json_posts(json_file):
    """Import posts from JSON to RAG."""
    print(f"📚 Importing posts from: {json_file}")
    
    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict) and 'posts' in data:
        posts = data['posts']
    elif isinstance(data, dict) and 'data' in data:
        posts = data['data']
    else:
        posts = [data]  # Single post
    
    print(f"📋 Found {len(posts)} posts to import")
    
    rag_memory = RAGMemory()
    success_count = 0
    
    for i, post in enumerate(posts, 1):
        try:
            # Extract post data (flexible field names)
            content = post.get('Content', post.get('content', post.get('post', post.get('text', ''))))
            topic = post.get('Topic', post.get('topic', post.get('title', '')))
            reactions = post.get('Reactions', post.get('reactions', post.get('feedback', 'yes')))
            
            if not content:
                print(f"⚠️  Skipping post {i}: no content")
                continue
            
            # Create topic if not provided
            if not topic:
                topic = content.split('\n')[0][:50] + "..."
            
            # Determine feedback
            feedback = "yes"
            if reactions:
                if isinstance(reactions, str) and reactions.lower() in ['yes', 'approved', 'like', 'love']:
                    feedback = reactions.lower()
                elif isinstance(reactions, (int, float)) and reactions > 0:
                    feedback = "yes"
            
            post_data = {
                "topic": topic,
                "post": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "client_id": EmailSettings.TO_EMAIL.split('@')[0],
                "feedback": feedback,
                "voice_quality": post.get('voice_quality', 8),
                "post_quality": post.get('post_quality', 8),
                "post_hash": f"json_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            if rag_memory.add_post(post_data):
                success_count += 1
                print(f"✅ Added post {i}: {topic[:30]}...")
            else:
                print(f"❌ Failed to add post {i}")
                
        except Exception as e:
            print(f"❌ Error processing post {i}: {e}")
    
    print(f"\n🎉 Successfully imported {success_count} posts to RAG store!")
    return success_count

if __name__ == "__main__":
    # Look for JSON files
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'post' in f.lower()]
    
    if json_files:
        print("📁 Found JSON files:")
        for i, file in enumerate(json_files, 1):
            print(f"   {i}. {file}")
        
        if len(json_files) == 1:
            json_file = json_files[0]
        else:
            choice = input(f"Enter number (1-{len(json_files)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(json_files):
                json_file = json_files[int(choice) - 1]
            else:
                print("❌ Invalid choice")
                sys.exit(1)
    else:
        json_file = input("Enter JSON file path: ").strip()
    
    if os.path.exists(json_file):
        import_json_posts(json_file)
    else:
        print(f"❌ File not found: {json_file}") 