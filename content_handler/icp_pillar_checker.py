#!/usr/bin/env python3
"""
Content Handler - ICP Pillar Checker Module
Handles ICP data and content pillar selection
"""

import json
import sys
import os
from typing import Dict, List, Optional

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class ICPPillarChecker:
    def __init__(self):
        """Initialize the ICP pillar checker."""
        self.icp_data = self._load_icp_data()
        self.content_pillars = self._load_content_pillars()
        print("🎯 ICP Pillar Checker initialized")
    
    def _load_icp_data(self) -> Dict:
        """Load ICP data from icp_profile.json."""
        try:
            with open('data/icp_profile.json', 'r') as f:
                icp_data = json.load(f)
                
                # Get all ICP segments
                icp_segments = icp_data.get('Ideal Client Profiles', [])
                
                if icp_segments:
                    # Create a combined profile from all segments
                    combined_pain_points = []
                    combined_goals = []
                    combined_psychographics = []
                    
                    for segment in icp_segments:
                        combined_pain_points.extend(segment.get('Challenges Faced', []))
                        combined_goals.extend(segment.get('Primary Goals', []))
                        combined_psychographics.extend(segment.get('Psychographics', []))
                    
                    return {
                        "target_audience": "HR consultants and business owners",
                        "overview": "Early-stage to established HR consultants building profitable businesses",
                        "pain_points": combined_pain_points[:5],  # Top 5 pain points
                        "goals": combined_goals[:5],  # Top 5 goals
                        "psychographics": combined_psychographics[:3],  # Top 3 psychographics
                        "segments": icp_segments,
                        "who_they_are": icp_segments[0].get('Who They Are', []) if icp_segments else []
                    }
                
                return self._get_default_icp()
                
        except FileNotFoundError:
            print("⚠️ ICP profile file not found")
            return self._get_default_icp()
        except Exception as e:
            print(f"❌ Error loading ICP data: {e}")
            return self._get_default_icp()
    
    def _get_default_icp(self) -> Dict:
        """Get default ICP data if file loading fails."""
        return {
            "target_audience": "HR consultants",
            "pain_points": ["pricing", "client acquisition", "imposter syndrome"],
            "goals": ["build successful business", "help other HR consultants"],
            "psychographics": ["growth-oriented", "care about people"]
        }
    
    def _load_content_pillars(self) -> Dict:
        """Load content pillars from content_pillars.json."""
        try:
            with open('data/content_pillars.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Content pillars file not found")
            return {"content_pillars": []}
        except Exception as e:
            print(f"❌ Error loading content pillars: {e}")
            return {"content_pillars": []}
    
    def get_icp_data(self) -> Dict:
        """Get ICP data."""
        return self.icp_data
    
    def get_all_icp_segments(self) -> List[Dict]:
        """Get all ICP segments."""
        try:
            with open('data/icp_profile.json', 'r') as f:
                icp_data = json.load(f)
                return icp_data.get('Ideal Client Profiles', [])
        except Exception as e:
            print(f"❌ Error loading all ICP segments: {e}")
            return []
    
    def get_relevant_pillar(self, topic: str) -> Dict:
        """Get the most relevant content pillar for a topic."""
        try:
            pillars = self.content_pillars.get('content_pillars', [])
            if not pillars:
                return {}
            
            # Score each pillar based on topic relevance
            pillar_scores = []
            for pillar in pillars:
                score = self._calculate_pillar_relevance(pillar, topic)
                pillar_scores.append((score, pillar))
            
            # Sort by score and return the best match
            pillar_scores.sort(key=lambda x: x[0], reverse=True)
            
            if pillar_scores:
                return pillar_scores[0][1]
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error getting relevant pillar: {e}")
            return {}
    
    def _calculate_pillar_relevance(self, pillar: Dict, topic: str) -> float:
        """Calculate how relevant a pillar is to the given topic."""
        try:
            topic_lower = topic.lower()
            score = 0.0
            
            # Check pillar title
            title = pillar.get('title', '').lower()
            if any(word in title for word in topic_lower.split()):
                score += 2.0
            
            # Check pillar description
            description = pillar.get('description', '').lower()
            if any(word in description for word in topic_lower.split()):
                score += 1.5
            
            # Check pillar topics
            topics = pillar.get('topics', [])
            for pillar_topic in topics:
                pillar_topic_lower = pillar_topic.lower()
                if any(word in pillar_topic_lower for word in topic_lower.split()):
                    score += 2.0
                    break
            
            # Check hooks for relevance
            hooks = pillar.get('hooks', [])
            for hook in hooks:
                hook_lower = hook.lower()
                if any(word in hook_lower for word in topic_lower.split()):
                    score += 1.0
            
            return score
            
        except Exception as e:
            print(f"❌ Error calculating pillar relevance: {e}")
            return 0.0
    
    def get_all_pillars(self) -> List[Dict]:
        """Get all content pillars."""
        return self.content_pillars.get('content_pillars', [])
    
    def get_pillar_by_title(self, title: str) -> Optional[Dict]:
        """Get a specific pillar by title."""
        try:
            pillars = self.content_pillars.get('content_pillars', [])
            for pillar in pillars:
                if pillar.get('title', '').lower() == title.lower():
                    return pillar
            return None
        except Exception as e:
            print(f"❌ Error getting pillar by title: {e}")
            return None
    
    def get_random_pillar(self) -> Dict:
        """Get a random content pillar."""
        try:
            import random
            pillars = self.content_pillars.get('content_pillars', [])
            if pillars:
                return random.choice(pillars)
            else:
                return {}
        except Exception as e:
            print(f"❌ Error getting random pillar: {e}")
            return {}
    
    def get_pillar_topics(self, pillar_title: str) -> List[str]:
        """Get topics from a specific pillar."""
        try:
            pillar = self.get_pillar_by_title(pillar_title)
            if pillar:
                return pillar.get('topics', [])
            else:
                return []
        except Exception as e:
            print(f"❌ Error getting pillar topics: {e}")
            return []
    
    def get_pillar_hooks(self, pillar_title: str) -> List[str]:
        """Get hooks from a specific pillar."""
        try:
            pillar = self.get_pillar_by_title(pillar_title)
            if pillar:
                return pillar.get('hooks', [])
            else:
                return []
        except Exception as e:
            print(f"❌ Error getting pillar hooks: {e}")
            return []
    
    def validate_topic_against_icp(self, topic: str) -> Dict:
        """Validate if a topic is relevant to the ICP."""
        try:
            topic_lower = topic.lower()
            icp_audience = self.icp_data.get('target_audience', '').lower()
            icp_pain_points = [point.lower() for point in self.icp_data.get('pain_points', [])]
            icp_goals = [goal.lower() for goal in self.icp_data.get('goals', [])]
            
            relevance_score = 0.0
            reasons = []
            
            # Check audience relevance
            if any(word in topic_lower for word in icp_audience.split()):
                relevance_score += 1.0
                reasons.append("Relevant to target audience")
            
            # Check pain point relevance
            for pain_point in icp_pain_points:
                if any(word in topic_lower for word in pain_point.split()):
                    relevance_score += 1.0
                    reasons.append(f"Addresses pain point: {pain_point}")
            
            # Check goal relevance
            for goal in icp_goals:
                if any(word in topic_lower for word in goal.split()):
                    relevance_score += 0.5
                    reasons.append(f"Supports goal: {goal}")
            
            # Determine relevance level
            if relevance_score >= 2.0:
                relevance_level = "high"
            elif relevance_score >= 1.0:
                relevance_level = "medium"
            else:
                relevance_level = "low"
            
            return {
                "relevance_score": relevance_score,
                "relevance_level": relevance_level,
                "reasons": reasons,
                "is_relevant": relevance_score >= 1.0
            }
            
        except Exception as e:
            print(f"❌ Error validating topic against ICP: {e}")
            return {
                "relevance_score": 0.0,
                "relevance_level": "unknown",
                "reasons": ["Error in validation"],
                "is_relevant": False
            }
    
    def get_most_relevant_pillar(self, topic: str) -> Dict:
        """Get the most relevant content pillar for a topic (alias for get_relevant_pillar)."""
        return self.get_relevant_pillar(topic)
    
    def get_trending_topics(self) -> List[str]:
        """Get trending topics from content pillars."""
        try:
            trending_topics = []
            pillars = self.content_pillars.get('content_pillars', [])
            
            for pillar in pillars:
                topics = pillar.get('topics', [])
                trending_topics.extend(topics[:2])  # Take first 2 topics from each pillar
            
            # Remove duplicates and limit
            unique_topics = list(set(trending_topics))
            return unique_topics[:10]  # Limit to 10 trending topics
            
        except Exception as e:
            print(f"❌ Error getting trending topics: {e}")
            return ["pricing strategies", "client acquisition", "imposter syndrome", "work-life balance"]
    
    def select_best_topic_for_icp(self, topics: List[str], icp_data: Dict) -> str:
        """Select the best topic for ICP alignment."""
        try:
            best_topic = topics[0] if topics else "HR consulting insights"
            best_score = 0.0
            
            for topic in topics:
                validation = self.validate_topic_against_icp(topic)
                if validation['relevance_score'] > best_score:
                    best_score = validation['relevance_score']
                    best_topic = topic
            
            return best_topic
            
        except Exception as e:
            print(f"❌ Error selecting best topic: {e}")
            return topics[0] if topics else "HR consulting insights"
    
    def get_icp_pain_points(self) -> List[str]:
        """Get ICP pain points."""
        return self.icp_data.get('pain_points', [])
    
    def get_icp_goals(self) -> List[str]:
        """Get ICP goals."""
        return self.icp_data.get('goals', [])
    
    def get_icp_psychographics(self) -> List[str]:
        """Get ICP psychographics."""
        return self.icp_data.get('psychographics', [])
    
    def get_status(self) -> Dict:
        """Get component status."""
        return {
            "status": "operational",
            "component": "icp_pillar_checker",
            "icp_loaded": bool(self.icp_data),
            "pillars_loaded": len(self.content_pillars.get('content_pillars', [])),
            "timestamp": "2025-07-31T17:52:00"
        } 

    def get_icp_for_topic(self, topic: str) -> Dict:
        """
        Get the most relevant ICP segment for a given topic.
        
        Args:
            topic: The topic to match against ICP segments
            
        Returns:
            Most relevant ICP segment data
        """
        try:
            segments = self.icp_data.get('segments', [])
            if not segments:
                return self.icp_data
            
            topic_lower = topic.lower()
            
            # Business Club Member keywords (early-stage, solo, first 1-5 years)
            business_club_keywords = [
                "early", "solo", "first", "start", "begin", "new", "referral", 
                "reactionary", "lonely", "isolation", "diy", "fatigue", "overgiving",
                "boundary", "imposter", "confidence", "pricing", "positioning",
                "client acquisition", "pitch", "uncertainty", "burnout"
            ]
            
            # Mastermind Member keywords (established, scale, team, 3-7 years)
            mastermind_keywords = [
                "scale", "team", "associate", "retainer", "corporate", "contract",
                "delegate", "automate", "brand", "positioning", "sophisticated",
                "leveraged", "pipeline", "thought-leader", "advisory", "ceo",
                "strategic", "growth", "system", "leverage"
            ]
            
            business_club_score = sum(1 for keyword in business_club_keywords if keyword in topic_lower)
            mastermind_score = sum(1 for keyword in mastermind_keywords if keyword in topic_lower)
            
            if business_club_score > mastermind_score and len(segments) > 0:
                segment = segments[0]  # Business Club Member
                print(f"🎯 Matched topic '{topic}' to Business Club Member segment")
            elif len(segments) > 1:
                segment = segments[1]  # Mastermind Member
                print(f"🎯 Matched topic '{topic}' to Mastermind Member segment")
            else:
                segment = segments[0] if segments else {}
                print(f"🎯 Using general ICP data for topic '{topic}'")
            
            return {
                "target_audience": f"HR consultants - {segment.get('Segment', 'General')}",
                "pain_points": segment.get("Challenges Faced", [])[:3],
                "goals": segment.get("Primary Goals", [])[:3],
                "psychographics": segment.get("Psychographics", [])[:2],
                "segment": segment.get("Segment", "General"),
                "overview": segment.get("Overview", "")
            }
            
        except Exception as e:
            print(f"❌ Error getting ICP for topic: {e}")
            return self.icp_data 