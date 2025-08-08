#!/usr/bin/env python3
"""
RAG Memory System
Stores and retrieves approved posts using FAISS vector store
"""

import sys
import os
import json
import logging
import pickle
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available, using simple storage")

from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGMemory:
    """RAG memory system for storing and retrieving approved posts."""
    
    def __init__(self, storage_dir: str = "data/rag_store"):
        """Initialize the RAG memory system."""
        self.storage_dir = storage_dir
        self.index_file = os.path.join(storage_dir, "faiss_index.bin")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self.post_hashes_file = os.path.join(storage_dir, "post_hashes.json")
        
        # Create storage directory
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize storage
        self.post_hashes = self._load_post_hashes()
        self.metadata = self._load_metadata()
        
        if FAISS_AVAILABLE:
            self.index = self._load_or_create_index()
        else:
            self.index = None
            logger.warning("⚠️ Using simple storage (FAISS not available)")
        
        logger.info("📚 RAG Memory initialized")
    
    def _load_post_hashes(self) -> Dict[str, str]:
        """Load existing post hashes."""
        try:
            if os.path.exists(self.post_hashes_file):
                with open(self.post_hashes_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Could not load post hashes: {e}")
        return {}
    
    def _save_post_hashes(self):
        """Save post hashes to file."""
        try:
            with open(self.post_hashes_file, 'w') as f:
                json.dump(self.post_hashes, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving post hashes: {e}")
    
    def _load_metadata(self) -> List[Dict]:
        """Load metadata from file."""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Could not load metadata: {e}")
        return []
    
    def _save_metadata(self):
        """Save metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving metadata: {e}")
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one."""
        if not FAISS_AVAILABLE:
            return None
            
        try:
            if os.path.exists(self.index_file):
                logger.info("📚 Loading existing FAISS index")
                return faiss.read_index(self.index_file)
            else:
                logger.info("📚 Creating new FAISS index")
                # Create a simple index for text embeddings (768 dimensions for typical embeddings)
                dimension = 768
                index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                return index
        except Exception as e:
            logger.error(f"❌ Error loading/creating FAISS index: {e}")
            return None
    
    def _save_index(self):
        """Save FAISS index to file."""
        if not FAISS_AVAILABLE or self.index is None:
            return
            
        try:
            faiss.write_index(self.index, self.index_file)
        except Exception as e:
            logger.error(f"❌ Error saving FAISS index: {e}")
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        For now, using a simple hash-based embedding.
        In production, use OpenAI embeddings or similar.
        """
        try:
            # Simple hash-based embedding (replace with OpenAI embeddings in production)
            import hashlib
            
            # Create a simple embedding vector
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Convert to 768-dimensional vector
            embedding = np.zeros(768, dtype=np.float32)
            for i, byte in enumerate(hash_bytes):
                if i < 768:
                    embedding[i] = (byte - 128) / 128.0  # Normalize to [-1, 1]
            
            # Normalize the vector
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            return np.zeros(768, dtype=np.float32)
    
    def post_exists(self, post_hash: str) -> bool:
        """
        Check if a post already exists in the RAG store.
        
        Args:
            post_hash: Hash of the post content
            
        Returns:
            True if post exists, False otherwise
        """
        return post_hash in self.post_hashes
    
    def add_post(self, post_data: Dict) -> bool:
        """
        Add a post to the RAG store.
        
        Args:
            post_data: Post data with topic, post, timestamp, etc.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            post_hash = post_data.get('post_hash')
            if not post_hash:
                logger.error("❌ No post hash provided")
                return False
            
            # Check if post already exists
            if self.post_exists(post_hash):
                logger.info(f"📋 Post already exists: {post_data.get('topic', 'Unknown')}")
                return True
            
            # Generate embedding
            combined_text = f"{post_data.get('topic', '')} {post_data.get('post', '')}"
            embedding = self._generate_embedding(combined_text)
            
            # Add to FAISS index if available
            if FAISS_AVAILABLE and self.index is not None:
                # Reshape embedding for FAISS
                embedding_reshaped = embedding.reshape(1, -1).astype(np.float32)
                self.index.add(embedding_reshaped)
                self._save_index()
            
            # Store metadata
            metadata_entry = {
                'id': len(self.metadata),
                'post_hash': post_hash,
                'topic': post_data.get('topic', ''),
                'post': post_data.get('post', ''),
                'timestamp': post_data.get('timestamp', ''),
                'client_id': post_data.get('client_id', ''),
                'feedback': post_data.get('feedback', ''),
                'voice_quality': post_data.get('voice_quality', 0),
                'post_quality': post_data.get('post_quality', 0),
                'added_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.metadata.append(metadata_entry)
            self._save_metadata()
            
            # Store post hash
            self.post_hashes[post_hash] = post_data.get('topic', 'Unknown')
            self._save_post_hashes()
            
            logger.info(f"✅ Added post to RAG store: {post_data.get('topic', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding post to RAG: {e}")
            return False
    
    def retrieve_similar_posts(self, topic: str, client_id: str, after_days: int = 0, top_k: int = None) -> List[Dict]:
        """
        Retrieve ALL posts for tone and style learning, prioritizing high-quality approved posts.
        
        Args:
            topic: The topic (used for context but not strict matching)
            client_id: Client ID to filter by
            after_days: Exclude posts from last N days
            top_k: Number of posts to retrieve (None = ALL posts for tone learning)
            
        Returns:
            List of ALL posts for tone and style learning
        """
        try:
            logger.info(f"🔍 Retrieving ALL posts for tone and style learning (topic: {topic})")
            
            # Generate embedding for the query topic
            query_embedding = self._generate_embedding(topic)
            
            # Calculate cutoff date
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=after_days)
            
            # Filter posts by client and date
            filtered_posts = []
            for post in self.metadata:
                # Check client ID
                if post.get('client_id') != client_id:
                    continue
                
                # Check date (exclude posts from last N days)
                # SKIP date filtering for tone learning - we want ALL posts
                # try:
                #     post_date = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                #     if post_date >= cutoff_date:  # Changed from > to >= to be more inclusive
                #         continue
                # except:
                #     continue
                
                # Don't exclude posts based on topic similarity - we want to learn tone from ALL posts
                # Only exclude if it's the exact same topic to avoid repetition
                # REMOVED: if topic.lower().strip() == post.get('topic', '').lower().strip():
                #     continue
                
                filtered_posts.append(post)
            
            if not filtered_posts:
                logger.info("📭 No similar posts found")
                return []
            
            # Calculate similarities if FAISS is available and has enough posts
            if FAISS_AVAILABLE and self.index is not None and self.index.ntotal >= len(filtered_posts):
                similarities = []
                for post in filtered_posts:
                    # Generate embedding for this post
                    post_text = f"{post.get('topic', '')} {post.get('post', '')}"
                    post_embedding = self._generate_embedding(post_text)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, post_embedding)
                    similarities.append((similarity, post))
                
                # Sort by similarity
                similarities.sort(key=lambda x: x[0], reverse=True)
                
                # Return ALL posts by default for tone learning, or top k if specified
                if top_k is None:
                    top_posts = [post for _, post in similarities]
                else:
                    top_posts = [post for _, post in similarities[:top_k]]
            else:
                # Simple fallback: prioritize posts by quality and recency for tone learning
                # This ensures we get ALL posts when FAISS index is incomplete
                logger.info(f"📚 Using simple fallback (FAISS index has {self.index.ntotal if self.index else 0} posts, need {len(filtered_posts)})")
                scored_posts = []
                
                for post in filtered_posts:
                    # Calculate a score based on quality and recency
                    voice_quality = post.get('voice_quality', 5)
                    post_quality = post.get('post_quality', 5)
                    avg_quality = (voice_quality + post_quality) / 2
                    
                    # Get post date for recency scoring
                    try:
                        post_date = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                        days_old = (datetime.now(timezone.utc) - post_date).days
                        recency_score = max(0, 10 - (days_old / 10))  # Higher score for newer posts
                    except:
                        recency_score = 5
                    
                    # Combined score (70% quality, 30% recency)
                    total_score = (avg_quality * 0.7) + (recency_score * 0.3)
                    scored_posts.append((total_score, post))
                
                # Sort by score (highest first)
                scored_posts.sort(key=lambda x: x[0], reverse=True)
                top_posts = [post for _, post in scored_posts]
                
                # Return ALL posts by default for tone learning, or top k if specified
                if top_k is not None:
                    top_posts = top_posts[:top_k]
            
            logger.info(f"📚 Retrieved {len(top_posts)} posts for tone and style learning")
            return top_posts
            
        except Exception as e:
            logger.error(f"❌ Error retrieving similar posts: {e}")
            return []
    
    def _is_similar_topic(self, topic1: str, topic2: str) -> bool:
        """
        Check if two topics are too similar (to avoid repetition).
        
        Args:
            topic1: First topic
            topic2: Second topic
            
        Returns:
            True if topics are too similar
        """
        if not topic1 or not topic2:
            return False
        
        # Simple similarity check (replace with more sophisticated NLP in production)
        words1 = set(topic1.lower().split())
        words2 = set(topic2.lower().split())
        
        if not words1 or not words2:
            return False
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return False
        
        similarity = intersection / union
        return similarity > 0.9  # 90% similarity threshold (less aggressive)
    
    def cleanup_old_posts(self, days_old: int = 45) -> int:
        """
        Remove posts older than specified days.
        
        Args:
            days_old: Remove posts older than this many days (default: 45)
            
        Returns:
            Number of posts removed
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            posts_to_remove = []
            
            # Find posts to remove
            for i, post in enumerate(self.metadata):
                try:
                    post_date = datetime.fromisoformat(post.get('timestamp', '').replace('Z', '+00:00'))
                    if post_date < cutoff_date:
                        posts_to_remove.append((i, post))
                except:
                    # If we can't parse the date, keep the post
                    continue
            
            if not posts_to_remove:
                logger.info(f"📭 No posts older than {days_old} days found")
                return 0
            
            # Remove posts (in reverse order to maintain indices)
            removed_count = 0
            for index, post in reversed(posts_to_remove):
                try:
                    # Remove from metadata
                    removed_post = self.metadata.pop(index)
                    
                    # Remove from post hashes
                    post_hash = removed_post.get('post_hash')
                    if post_hash in self.post_hashes:
                        del self.post_hashes[post_hash]
                    
                    # Remove from FAISS index if available
                    if FAISS_AVAILABLE and self.index is not None:
                        # Note: FAISS doesn't support deletion, so we'll rebuild the index
                        logger.info("🔄 Rebuilding FAISS index after cleanup...")
                        self._rebuild_index()
                    
                    removed_count += 1
                    logger.info(f"🗑️ Removed old post: {removed_post.get('topic', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error removing post at index {index}: {e}")
            
            # Save updated data
            self._save_metadata()
            self._save_post_hashes()
            
            logger.info(f"✅ Cleanup complete: removed {removed_count} posts older than {days_old} days")
            return removed_count
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0
    
    def _rebuild_index(self):
        """Rebuild FAISS index after cleanup."""
        try:
            if not FAISS_AVAILABLE:
                return
            
            # Create new index
            embedding_dim = 1536  # OpenAI embedding dimension
            self.index = faiss.IndexFlatIP(embedding_dim)
            
            # Re-add all remaining posts
            for post in self.metadata:
                combined_text = f"{post.get('topic', '')} {post.get('post', '')}"
                embedding = self._generate_embedding(combined_text)
                embedding_reshaped = embedding.reshape(1, -1).astype(np.float32)
                self.index.add(embedding_reshaped)
            
            self._save_index()
            logger.info("✅ FAISS index rebuilt successfully")
            
        except Exception as e:
            logger.error(f"❌ Error rebuilding FAISS index: {e}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the RAG store."""
        try:
            total_posts = len(self.metadata)
            unique_clients = len(set(post.get('client_id') for post in self.metadata))
            
            # Calculate average quality scores
            voice_scores = [post.get('voice_quality', 0) for post in self.metadata if post.get('voice_quality', 0) > 0]
            post_scores = [post.get('post_quality', 0) for post in self.metadata if post.get('post_quality', 0) > 0]
            
            avg_voice_quality = sum(voice_scores) / len(voice_scores) if voice_scores else 0
            avg_post_quality = sum(post_scores) / len(post_scores) if post_scores else 0
            
            return {
                'total_posts': total_posts,
                'unique_clients': unique_clients,
                'avg_voice_quality': round(avg_voice_quality, 2),
                'avg_post_quality': round(avg_post_quality, 2),
                'faiss_available': FAISS_AVAILABLE,
                'index_size': self.index.ntotal if self.index else 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}

def main():
    """Main function to test RAG memory system."""
    
    print("📚 RAG Memory System Test")
    print("=" * 50)
    
    try:
        rag_memory = RAGMemory()
        
        # Test adding a post
        test_post = {
            "topic": "pricing your services",
            "post": "This is a test post about pricing HR consulting services.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_id": "sam_eaton",
            "feedback": "yes",
            "voice_quality": 8,
            "post_quality": 9,
            "post_hash": "test_hash_123"
        }
        
        print("📝 Adding test post...")
        success = rag_memory.add_post(test_post)
        
        if success:
            print("✅ Test post added successfully")
            
            # Test retrieval
            print("🔍 Testing retrieval...")
            similar_posts = rag_memory.retrieve_similar_posts("pricing", "sam_eaton")
            print(f"📚 Found {len(similar_posts)} similar posts")
            
            # Get stats
            stats = rag_memory.get_stats()
            print(f"📊 RAG Store Stats: {stats}")
        else:
            print("❌ Failed to add test post")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main() 