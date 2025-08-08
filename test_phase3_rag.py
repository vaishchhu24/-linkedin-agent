#!/usr/bin/env python3
"""
Test Phase 3 RAG Workflow
Demonstrates the complete RAG-based learning system
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feedback_loop import FeedbackLoop
from content_handler.post_generator import PostGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
from airtable_logger import AirtableLogger
from rag_memory import RAGMemory
from config.email_config import EmailSettings

def test_phase3_workflow():
    """Test the complete Phase 3 RAG workflow."""
    
    print("🧠 Phase 3 RAG Workflow Test")
    print("=" * 50)
    
    # Initialize components
    feedback_loop = FeedbackLoop()
    post_generator = PostGenerator()
    icp_checker = ICPPillarChecker()
    airtable_logger = AirtableLogger()
    rag_memory = RAGMemory()
    
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📚 RAG Store: {rag_memory.get_stats()}")
    print("-" * 30)
    
    # Step 1: Simulate approved posts in Airtable
    print("📝 Step 1: Simulating approved posts in Airtable...")
    
    approved_posts = [
        {
            "topic": "pricing your services",
            "post": "The biggest mistake I see with pricing your services is undervaluing yourself. I used to charge way less than I should have because I was afraid of overpricing. But here's the thing - your expertise is valuable. Don't sell yourself short! #hrconsultants #pricing",
            "feedback": "Yes, this is perfect! Love the tone and message.",
            "voice_quality": 9,
            "post_quality": 8
        },
        {
            "topic": "imposter syndrome",
            "post": "Imposter syndrome is real, and it affects so many HR consultants. I remember feeling like I didn't deserve my success. But here's what I learned - everyone feels this way sometimes. The key is to keep pushing forward and trust in your abilities. You've got this! #impostersyndrome #hrconsultants",
            "feedback": "Excellent post! Very relatable and encouraging.",
            "voice_quality": 8,
            "post_quality": 9
        }
    ]
    
    # Add posts to Airtable (simulated)
    for i, post_data in enumerate(approved_posts):
        print(f"  📊 Adding post {i+1}: {post_data['topic']}")
        # In real scenario, these would be added via the automated workflow
    
    print("✅ Simulated approved posts added")
    print("-" * 30)
    
    # Step 2: Run feedback loop to add to RAG
    print("🔄 Step 2: Running feedback loop to add posts to RAG...")
    
    # Simulate adding posts to RAG store
    for post_data in approved_posts:
        rag_data = {
            "topic": post_data["topic"],
            "post": post_data["post"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_id": "sam_eaton",
            "feedback": post_data["feedback"],
            "voice_quality": post_data["voice_quality"],
            "post_quality": post_data["post_quality"],
            "post_hash": f"test_hash_{post_data['topic'].replace(' ', '_')}"
        }
        
        success = rag_memory.add_post(rag_data)
        if success:
            print(f"  ✅ Added to RAG: {post_data['topic']}")
        else:
            print(f"  ❌ Failed to add to RAG: {post_data['topic']}")
    
    print("✅ Feedback loop completed")
    print("-" * 30)
    
    # Step 3: Test RAG-enhanced content generation
    print("📝 Step 3: Testing RAG-enhanced content generation...")
    
    test_topics = [
        "pricing your services",
        "imposter syndrome",
        "client acquisition"
    ]
    
    for topic in test_topics:
        print(f"\n🎯 Testing topic: {topic}")
        
        # Get ICP data
        icp_data = icp_checker.get_icp_for_topic(topic)
        pillar_info = icp_checker.get_most_relevant_pillar(topic)
        
        # Get RAG context
        rag_context = post_generator._get_rag_context(topic)
        
        if rag_context:
            print(f"📚 RAG Context found: {len(rag_context.split('Topic:')) - 1} similar posts")
        else:
            print("📭 No RAG context found")
        
        # Generate post with RAG context
        result = post_generator.generate_from_insights(
            topic=topic,
            insights=[],  # No insights for this test
            icp_data=icp_data,
            pillar_data=pillar_info,
            topic_analysis={"topic": topic}
        )
        
        if result.get('success'):
            post_content = result['post']
            word_count = result.get('word_count', 0)
            print(f"✅ Generated post ({word_count} words)")
            print(f"📝 Preview: {post_content[:100]}...")
        else:
            print(f"❌ Failed to generate post: {result.get('error')}")
    
    print("-" * 30)
    
    # Step 4: Show RAG store statistics
    print("📊 Step 4: RAG Store Statistics")
    stats = rag_memory.get_stats()
    print(f"  Total Posts: {stats.get('total_posts', 0)}")
    print(f"  Unique Clients: {stats.get('unique_clients', 0)}")
    print(f"  Avg Voice Quality: {stats.get('avg_voice_quality', 0)}/10")
    print(f"  Avg Post Quality: {stats.get('avg_post_quality', 0)}/10")
    print(f"  FAISS Available: {stats.get('faiss_available', False)}")
    
    print("\n" + "=" * 50)
    print("✅ Phase 3 RAG Workflow Test Completed!")

def test_rag_retrieval():
    """Test RAG retrieval functionality."""
    
    print("\n🔍 Testing RAG Retrieval")
    print("=" * 30)
    
    rag_memory = RAGMemory()
    
    # Test retrieval for different topics
    test_queries = [
        ("pricing", "sam_eaton"),
        ("imposter syndrome", "sam_eaton"),
        ("client acquisition", "sam_eaton")
    ]
    
    for query, client_id in test_queries:
        print(f"\n🔍 Query: '{query}' for client '{client_id}'")
        similar_posts = rag_memory.retrieve_similar_posts(query, client_id)
        
        if similar_posts:
            print(f"📚 Found {len(similar_posts)} similar posts:")
            for i, post in enumerate(similar_posts, 1):
                print(f"  {i}. {post.get('topic', 'Unknown')} (Quality: {post.get('voice_quality', 0)}/10)")
        else:
            print("📭 No similar posts found")

def main():
    """Run all Phase 3 tests."""
    
    print("🚀 Phase 3 RAG System Test Suite")
    print("=" * 60)
    
    # Test complete workflow
    test_phase3_workflow()
    
    # Test RAG retrieval
    test_rag_retrieval()
    
    print("\n" + "=" * 60)
    print("✅ All Phase 3 tests completed!")

if __name__ == "__main__":
    main() 