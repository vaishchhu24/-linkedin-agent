#!/usr/bin/env python3
"""
Content Handler - Content Generator Module
Generates LinkedIn posts using the existing natural_content_generator
"""

import sys
import os
import json
from typing import Dict, Optional, List
from datetime import datetime, timezone

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import existing natural content generator
from natural_content_generator import NaturalContentGenerator
from trends.perplexity_fetcher import fetch_reddit_insights

class ContentGenerator:
    def __init__(self):
        """Initialize the content generator."""
        self.natural_generator = NaturalContentGenerator()
        print("🎯 Content Generator initialized")
    
    def generate_from_pillars(self) -> str:
        """Generate post using content pillars (when no specific topic provided)."""
        try:
            print("📝 Generating post from content pillars...")
            
            # Get a specific HR consulting topic from content pillars
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from content_handler.icp_pillar_checker import ICPPillarChecker
            icp_checker = ICPPillarChecker()
            
            # Get a random pillar and topic
            pillar = icp_checker.get_random_pillar()
            if pillar and pillar.get('topics'):
                import random
                topic = random.choice(pillar['topics'])
                print(f"📝 Selected topic from pillar: {topic}")
                
                # Generate post with specific topic
                post = self.natural_generator.generate_natural_post(topic=topic)
                return post
            else:
                # Fallback to specific HR consulting topic
                fallback_topics = [
                    "pricing strategies for HR consultants",
                    "client acquisition challenges",
                    "imposter syndrome in consulting",
                    "work-life balance for consultants",
                    "building credibility as an HR consultant"
                ]
                import random
                topic = random.choice(fallback_topics)
                print(f"📝 Using fallback topic: {topic}")
                post = self.natural_generator.generate_natural_post(topic=topic)
                return post
                
        except Exception as e:
            print(f"❌ Error generating from pillars: {e}")
            return self._generate_fallback_post("HR consulting challenges")
    
    def generate_from_detailed_content(self, detailed_content: str) -> str:
        """Generate post from detailed user content."""
        try:
            print("📝 Generating post from detailed content...")
            
            # Extract key elements from the detailed content
            key_elements = self._extract_content_elements(detailed_content)
            
            # Generate post using the natural generator with the detailed content as context
            post = self.natural_generator.generate_natural_post(
                topic=key_elements.get('main_topic', 'personal experience'),
                client_id="vaishnavi"
            )
            
            # Enhance the post with specific details from user content
            enhanced_post = self._enhance_post_with_details(post, key_elements)
            
            return enhanced_post
            
        except Exception as e:
            print(f"❌ Error generating from detailed content: {e}")
            return self._generate_fallback_post("detailed content")
    
    def generate_from_insights(self, topic: str, insights: str, icp_data: Dict, pillar_data: Dict) -> str:
        """Generate post from topic and fetched insights."""
        try:
            print(f"📝 Generating post from insights for topic: {topic}")
            
            # Use the natural generator with the specific topic
            post = self.natural_generator.generate_natural_post(
                topic=topic,
                client_id="vaishnavi"
            )
            
            # If the post is too generic, enhance it with insights
            if len(post) < 300 or "generic" in post.lower():
                enhanced_post = self._enhance_post_with_insights(post, insights, icp_data, pillar_data)
                return enhanced_post
            
            return post
            
        except Exception as e:
            print(f"❌ Error generating from insights: {e}")
            return self._generate_fallback_post(topic)
    
    def _extract_content_elements(self, content: str) -> Dict:
        """Extract key elements from detailed content."""
        try:
            # Use the existing content checker to extract elements
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from content_handler.content_checker import ContentChecker
            checker = ContentChecker()
            return checker.extract_key_elements(content)
        except Exception as e:
            print(f"❌ Error extracting content elements: {e}")
            return {
                "main_topic": "personal experience",
                "emotions": [],
                "details": [],
                "insights": [],
                "audience": "HR consultants"
            }
    
    def _enhance_post_with_details(self, base_post: str, key_elements: Dict) -> str:
        """Enhance the base post with specific details from user content."""
        try:
            # If the post is already substantial, return as is
            if len(base_post) > 500:
                return base_post
            
            # Extract specific details to add
            details = key_elements.get('details', [])
            insights = key_elements.get('insights', [])
            emotions = key_elements.get('emotions', [])
            
            if not details and not insights:
                return base_post
            
            # Create enhancement
            enhancement = "\n\n"
            
            if details:
                enhancement += "Here's what I learned:\n"
                for detail in details[:3]:  # Limit to 3 details
                    enhancement += f"• {detail}\n"
            
            if insights:
                enhancement += "\nKey insights:\n"
                for insight in insights[:2]:  # Limit to 2 insights
                    enhancement += f"• {insight}\n"
            
            # Add to base post
            enhanced_post = base_post + enhancement
            
            return enhanced_post
            
        except Exception as e:
            print(f"❌ Error enhancing post with details: {e}")
            return base_post
    
    def _enhance_post_with_insights(self, base_post: str, insights: str, icp_data: Dict, pillar_data: Dict) -> str:
        """Enhance the base post with fetched insights."""
        try:
            # If insights are substantial, incorporate them
            if len(insights) > 100:
                # Extract key points from insights
                key_points = self._extract_key_points_from_insights(insights)
                
                if key_points:
                    enhancement = "\n\nBased on what I'm seeing in the industry:\n"
                    for point in key_points[:2]:  # Limit to 2 points
                        enhancement += f"• {point}\n"
                    
                    enhanced_post = base_post + enhancement
                    return enhanced_post
            
            return base_post
            
        except Exception as e:
            print(f"❌ Error enhancing post with insights: {e}")
            return base_post
    
    def _extract_key_points_from_insights(self, insights: str) -> List[str]:
        """Extract key points from insights text."""
        try:
            # Simple extraction - look for bullet points or numbered items
            lines = insights.split('\n')
            key_points = []
            
            for line in lines:
                line = line.strip()
                if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                    # Remove bullet/number and clean
                    clean_point = line.lstrip('•-*1234567890. ').strip()
                    if len(clean_point) > 10:  # Only meaningful points
                        key_points.append(clean_point)
            
            return key_points[:3]  # Limit to 3 points
            
        except Exception as e:
            print(f"❌ Error extracting key points: {e}")
            return []
    
    def _generate_fallback_post(self, topic: str) -> str:
        """Generate a fallback post if main generation fails."""
        try:
            return self.natural_generator.generate_fallback_post(topic, {})
        except Exception as e:
            print(f"❌ Error generating fallback post: {e}")
            
            # Ensure topic is HR consulting focused
            if "hr" not in topic.lower() and "consultant" not in topic.lower():
                topic = "HR consulting challenges"
            
            return f"I've been thinking about {topic} lately.\n\nThis is something I see HR consultants struggle with ALL the time.\n\nThe key is to focus on your unique value and the real impact you can make.\n\nWhat's your biggest challenge with {topic}?\n\n#hrconsultants #hrleaders"
    
    def generate_with_specific_topic(self, topic: str) -> str:
        """Generate post with a specific topic."""
        try:
            print(f"📝 Generating post for specific topic: {topic}")
            return self.natural_generator.generate_natural_post(topic=topic)
        except Exception as e:
            print(f"❌ Error generating with specific topic: {e}")
            return self._generate_fallback_post(topic)
    
    def generate_with_feedback(self, original_post: str, feedback: str) -> str:
        """Generate refined post based on feedback."""
        try:
            print("🔄 Generating refined post based on feedback...")
            
            # Use the natural generator with feedback context
            # This would integrate with the feedback system
            refined_post = self.natural_generator.generate_natural_post(
                topic="feedback_refinement",
                client_id="vaishnavi"
            )
            
            return refined_post
            
        except Exception as e:
            print(f"❌ Error generating with feedback: {e}")
            return original_post
    
    def validate_post_quality(self, post: str) -> Dict:
        """Validate the quality of generated post."""
        validation_result = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "word_count": len(post.split()),
            "character_count": len(post)
        }
        
        # Check length
        if len(post) < 200:
            validation_result["issues"].append("Post is too short")
            validation_result["suggestions"].append("Add more detail or personal story")
        
        if len(post) > 1000:
            validation_result["suggestions"].append("Post is quite long - consider breaking into multiple posts")
        
        # Check for required elements
        if "mission" not in post.lower() and "help" not in post.lower():
            validation_result["suggestions"].append("Consider adding mission statement or call to action")
        
        if not any(word in post.lower() for word in ["i", "me", "my", "we"]):
            validation_result["suggestions"].append("Add personal perspective or experience")
        
        # Check for CAPS usage (client's style)
        caps_count = sum(1 for c in post if c.isupper())
        if caps_count < 5:
            validation_result["suggestions"].append("Consider adding more CAPS for emphasis (client's style)")
        
        if validation_result["issues"]:
            validation_result["is_valid"] = False
        
        return validation_result 