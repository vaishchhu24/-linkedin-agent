#!/usr/bin/env python3
"""
Manual RAG Post Adder
Add posts to the RAG store manually for learning
"""

import sys
import os
import json
from datetime import datetime, timezone
from typing import Dict, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory
from config.email_config import EmailSettings

def add_single_post():
    """Add a single post manually."""
    print("📝 Adding Single Post to RAG Store")
    print("=" * 50)
    
    # Get post details
    topic = input("Enter topic: ").strip()
    if not topic:
        print("❌ Topic is required")
        return False
    
    print("\nEnter the post content (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    post_content = "\n".join(lines[:-1])  # Remove the last empty line
    if not post_content.strip():
        print("❌ Post content is required")
        return False
    
    # Get quality scores
    try:
        voice_quality = int(input("Enter voice quality score (1-10): ") or "8")
        post_quality = int(input("Enter post quality score (1-10): ") or "8")
    except ValueError:
        print("❌ Invalid quality scores, using defaults (8)")
        voice_quality = 8
        post_quality = 8
    
    # Get feedback (optional)
    feedback = input("Enter feedback (optional, e.g., 'yes', 'approved'): ").strip() or "yes"
    
    # Create post data
    post_data = {
        "topic": topic,
        "post": post_content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_id": EmailSettings.CLIENT_EMAIL.split('@')[0],  # Use email prefix as client ID
        "feedback": feedback,
        "voice_quality": voice_quality,
        "post_quality": post_quality,
        "post_hash": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    # Add to RAG
    rag_memory = RAGMemory()
    success = rag_memory.add_post(post_data)
    
    if success:
        print("✅ Post added successfully to RAG store!")
        return True
    else:
        print("❌ Failed to add post to RAG store")
        return False

def add_multiple_posts():
    """Add multiple posts from a JSON file."""
    print("📚 Adding Multiple Posts from JSON File")
    print("=" * 50)
    
    file_path = input("Enter JSON file path: ").strip()
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            posts = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False
    
    if not isinstance(posts, list):
        print("❌ JSON file should contain a list of posts")
        return False
    
    print(f"📋 Found {len(posts)} posts to add")
    
    # Validate posts
    valid_posts = []
    for i, post in enumerate(posts):
        if not isinstance(post, dict):
            print(f"⚠️  Skipping post {i+1}: not a dictionary")
            continue
        
        required_fields = ['topic', 'post']
        missing_fields = [field for field in required_fields if field not in post]
        
        if missing_fields:
            print(f"⚠️  Skipping post {i+1}: missing fields {missing_fields}")
            continue
        
        # Add default values
        post.setdefault('timestamp', datetime.now(timezone.utc).isoformat())
        post.setdefault('client_id', EmailSettings.CLIENT_EMAIL.split('@')[0])
        post.setdefault('feedback', 'yes')
        post.setdefault('voice_quality', 8)
        post.setdefault('post_quality', 8)
        post.setdefault('post_hash', f"manual_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        valid_posts.append(post)
    
    if not valid_posts:
        print("❌ No valid posts found")
        return False
    
    print(f"✅ {len(valid_posts)} valid posts ready to add")
    
    # Add posts
    rag_memory = RAGMemory()
    success_count = 0
    
    for i, post in enumerate(valid_posts):
        print(f"📝 Adding post {i+1}/{len(valid_posts)}: {post['topic']}")
        if rag_memory.add_post(post):
            success_count += 1
        else:
            print(f"❌ Failed to add post: {post['topic']}")
    
    print(f"✅ Successfully added {success_count}/{len(valid_posts)} posts to RAG store")
    return success_count > 0

def show_rag_stats():
    """Show current RAG store statistics."""
    print("📊 Current RAG Store Statistics")
    print("=" * 50)
    
    rag_memory = RAGMemory()
    stats = rag_memory.get_stats()
    
    print(f"📚 Total posts: {stats.get('total_posts', 0)}")
    print(f"👥 Unique clients: {stats.get('unique_clients', 0)}")
    print(f"🎯 Average voice quality: {stats.get('avg_voice_quality', 0)}/10")
    print(f"📝 Average post quality: {stats.get('avg_post_quality', 0)}/10")
    print(f"🔧 FAISS available: {stats.get('faiss_available', False)}")
    print(f"📏 Index size: {stats.get('index_size', 0)}")

def show_recent_posts():
    """Show recent posts in RAG store."""
    print("📋 Recent Posts in RAG Store")
    print("=" * 50)
    
    rag_memory = RAGMemory()
    
    # Get all posts (no filtering)
    posts = rag_memory.retrieve_similar_posts(
        topic="", 
        client_id="", 
        after_days=0, 
        top_k=10
    )
    
    if not posts:
        print("📭 No posts found in RAG store")
        return
    
    for i, post in enumerate(posts[:10], 1):
        print(f"\n{i}. Topic: {post.get('topic', 'Unknown')}")
        print(f"   Quality: Voice {post.get('voice_quality', 0)}/10, Post {post.get('post_quality', 0)}/10")
        print(f"   Feedback: {post.get('feedback', 'Unknown')}")
        print(f"   Content: {post.get('post', '')[:100]}...")

def create_sample_json():
    """Create a sample JSON file for multiple posts."""
    sample_posts = [
        {
            "topic": "HR consultant pricing strategies",
            "post": "Just had a client ask me about pricing their HR consulting services. Here's what I told them:\n\n1. Start with your value, not your costs\n2. Price based on outcomes, not hours\n3. Don't compete on price - compete on results\n\nWhen you focus on the transformation you deliver, clients will pay premium rates.\n\nWhat's your pricing strategy?",
            "voice_quality": 9,
            "post_quality": 9,
            "feedback": "yes"
        },
        {
            "topic": "Client acquisition for HR consultants",
            "post": "The biggest mistake I see HR consultants make?\n\nTrying to be everything to everyone.\n\nInstead, focus on ONE specific problem you solve exceptionally well.\n\nFor me, it's helping HR consultants build systems that scale.\n\nWhen you niche down, you become the go-to expert.\n\nWhat's your specific niche?",
            "voice_quality": 8,
            "post_quality": 9,
            "feedback": "approved"
        },
        {
            "topic": "Building systems for HR consulting business",
            "post": "Your HR consulting business will never scale if you're the system.\n\nI learned this the hard way.\n\nNow I have:\n- Standardized processes for every client\n- Templates for common deliverables\n- Automated follow-up sequences\n- Clear onboarding procedures\n\nSystems = Freedom\n\nWhat systems do you need to build?",
            "voice_quality": 9,
            "post_quality": 8,
            "feedback": "yes"
        }
    ]
    
    filename = "sample_posts.json"
    with open(filename, 'w') as f:
        json.dump(sample_posts, f, indent=2)
    
    print(f"✅ Created sample file: {filename}")
    print("📝 You can edit this file and use it to add multiple posts")

def main():
    """Main menu."""
    while True:
        print("\n" + "=" * 60)
        print("🎯 Manual RAG Post Manager")
        print("=" * 60)
        print("1. Add single post")
        print("2. Add multiple posts from JSON file")
        print("3. Show RAG statistics")
        print("4. Show recent posts")
        print("5. Create sample JSON file")
        print("6. Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            add_single_post()
        elif choice == "2":
            add_multiple_posts()
        elif choice == "3":
            show_rag_stats()
        elif choice == "4":
            show_recent_posts()
        elif choice == "5":
            create_sample_json()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 