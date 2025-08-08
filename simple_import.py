#!/usr/bin/env python3
"""
Simple CSV to RAG Importer
Direct import for Content/Reactions CSV format
"""

import sys
import os
import csv
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory
from config.email_config import EmailSettings

def import_sam_posts(csv_file):
    """Import Sam's posts from CSV to RAG."""
    print(f"📚 Importing posts from: {csv_file}")
    
    rag_memory = RAGMemory()
    success_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            content = row.get('Content', '').strip()
            reactions = row.get('Reactions', '').strip()
            
            if not content:
                continue
            
            # Create topic from first few words
            topic = content.split('\n')[0][:50] + "..."
            
            # Determine if approved based on reactions
            feedback = "yes" if reactions and reactions.lower() in ['yes', 'approved', 'like', 'love'] else "yes"
            
            post_data = {
                "topic": topic,
                "post": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "client_id": EmailSettings.CLIENT_EMAIL.split('@')[0],
                "feedback": feedback,
                "voice_quality": 8,
                "post_quality": 8,
                "post_hash": f"sam_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            if rag_memory.add_post(post_data):
                success_count += 1
                print(f"✅ Added post {i}: {topic[:30]}...")
            else:
                print(f"❌ Failed to add post {i}")
    
    print(f"\n🎉 Successfully imported {success_count} posts to RAG store!")
    return success_count

if __name__ == "__main__":
    csv_file = "Sam posts for RAG  - Sheet1.csv"
    if os.path.exists(csv_file):
        import_sam_posts(csv_file)
    else:
        print(f"❌ File not found: {csv_file}") 