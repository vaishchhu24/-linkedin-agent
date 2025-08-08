"""
Content Assessor Module
Handles content analysis and topic relevance assessment using OpenAI
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAssessor:
    """
    Content Assessor for analyzing user input and topic relevance
    """
    
    def __init__(self):
        """Initialize the content assessor with OpenAI client."""
        self.client = OpenAI(api_key=EmailSettings.OPENAI_API_KEY)
        logger.info("🔍 Content Assessor initialized")
    
    def extract_content_elements(self, content: str) -> Dict:
        """
        Extract key elements from detailed content using OpenAI.
        
        Args:
            content: Detailed user content to analyze
            
        Returns:
            Dict with extracted elements
        """
        try:
            logger.info("🔍 Extracting content elements...")
            
            # Check if this is a "No" response (no topic provided)
            content_lower = content.lower().strip()
            
            # More comprehensive "No" detection
            no_indicators = [
                'no', 'no.', 'no....', 'no, sorry', 'no sorry', 'no, sorry....',
                'not really', 'not sure', 'i don\'t know', 'i dont know',
                'nothing specific', 'no topic', 'no idea'
            ]
            
            # Check if content starts with "No" or contains only no indicators
            if (content_lower in no_indicators or 
                content_lower.startswith('no') and len(content_lower) < 20):
                logger.info("📝 Detected 'No' response - user doesn't have a specific topic")
                return {
                    "main_topic": "general_hr_consulting",
                    "detail_level": "general",
                    "emotions": ["uncertainty", "openness"],
                    "details": ["No specific topic provided"],
                    "insights": ["User open to system-generated topics"],
                    "audience": "HR consultants",
                    "story_elements": ["general consulting"],
                    "lessons_learned": ["System should generate topic"],
                    "pain_points": ["Need for topic generation"],
                    "solutions": ["AI-generated content"]
                }
            
            # Check if this is a "Yes" response with topic
            if content_lower.startswith('yes') or content_lower.startswith('yeah') or content_lower.startswith('sure'):
                logger.info("📝 Detected 'Yes' response with topic - processing content")
                # Continue with normal processing
            
            prompt = f"""Analyze the following LinkedIn content and extract key elements:

Content: "{content}"

Extract and return ONLY a JSON object with these fields:
{{
    "main_topic": "primary topic or theme",
    "detail_level": "detailed/general (detailed if user provided specific story/experience, general if brief topic only)",
    "emotions": ["emotion1", "emotion2"],
    "details": ["specific detail 1", "specific detail 2"],
    "insights": ["key insight 1", "key insight 2"],
    "audience": "target audience",
    "story_elements": ["story element 1", "story element 2"],
    "lessons_learned": ["lesson 1", "lesson 2"],
    "pain_points": ["pain point 1", "pain point 2"],
    "solutions": ["solution 1", "solution 2"]
}}

Focus on HR consulting relevance. Return ONLY the JSON object."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content analysis expert specializing in HR consulting content. Extract key elements accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                elements = json.loads(result_text)
                logger.info("✅ Content elements extracted successfully")
                return elements
            except json.JSONDecodeError:
                logger.warning("⚠️ Failed to parse JSON, using fallback extraction")
                return self._fallback_content_extraction(content)
                
        except Exception as e:
            logger.error(f"❌ Error extracting content elements: {e}")
            return self._fallback_content_extraction(content)
    
    def analyze_topic_relevance(self, topic: str) -> Dict:
        """
        Analyze topic relevance for HR consulting using OpenAI.
        
        Args:
            topic: Brief topic to analyze
            
        Returns:
            Dict with relevance analysis
        """
        try:
            logger.info(f"🔍 Analyzing topic relevance: {topic}")
            
            prompt = f"""Analyze the relevance of this topic for HR consulting content:

Topic: "{topic}"

Return ONLY a JSON object with these fields:
{{
    "relevance_score": 0.0-1.0,
    "hr_consulting_relevance": "high/medium/low",
    "target_audience": ["audience1", "audience2"],
    "pain_points": ["pain point 1", "pain point 2"],
    "content_angles": ["angle 1", "angle 2"],
    "trending_status": "trending/stable/declining",
    "engagement_potential": "high/medium/low"
}}

Focus on HR consulting relevance. Return ONLY the JSON object."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an HR consulting content strategist. Analyze topic relevance accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                analysis = json.loads(result_text)
                logger.info(f"✅ Topic relevance analyzed: {analysis.get('relevance_score', 0)}")
                return analysis
            except json.JSONDecodeError:
                logger.warning("⚠️ Failed to parse JSON, using fallback analysis")
                return self._fallback_topic_analysis(topic)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing topic relevance: {e}")
            return self._fallback_topic_analysis(topic)
    
    def validate_content_quality(self, content: str) -> Dict:
        """
        Validate content quality and authenticity.
        
        Args:
            content: Content to validate
            
        Returns:
            Dict with validation results
        """
        try:
            logger.info("🔍 Validating content quality...")
            
            prompt = f"""Validate the quality and authenticity of this content:

Content: "{content}"

Return ONLY a JSON object with these fields:
{{
    "quality_score": 0.0-1.0,
    "authenticity": "high/medium/low",
    "specificity": "high/medium/low",
    "relevance": "high/medium/low",
    "engagement_potential": "high/medium/low",
    "issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"],
    "recommendations": ["recommendation1", "recommendation2"]
}}

Focus on authenticity and specificity. Return ONLY the JSON object."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content quality validator. Assess authenticity and specificity."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                validation = json.loads(result_text)
                logger.info(f"✅ Content quality validated: {validation.get('quality_score', 0)}")
                return validation
            except json.JSONDecodeError:
                logger.warning("⚠️ Failed to parse JSON, using fallback validation")
                return self._fallback_content_validation(content)
                
        except Exception as e:
            logger.error(f"❌ Error validating content quality: {e}")
            return self._fallback_content_validation(content)
    
    def _fallback_content_extraction(self, content: str) -> Dict:
        """Fallback content extraction when AI analysis fails."""
        # Check if this is a "No" response (no topic provided)
        content_lower = content.lower().strip()
        if content_lower in ['no', 'no.', 'no....', 'no, sorry', 'no sorry', 'no, sorry....']:
            logger.info("📝 Fallback: Detected 'No' response - user doesn't have a specific topic")
            return {
                "main_topic": "general_hr_consulting",
                "detail_level": "general",
                "emotions": ["uncertainty", "openness"],
                "details": ["No specific topic provided"],
                "insights": ["User open to system-generated topics"],
                "audience": "HR consultants",
                "story_elements": ["general consulting"],
                "lessons_learned": ["System should generate topic"],
                "pain_points": ["Need for topic generation"],
                "solutions": ["AI-generated content"]
            }
        
        # Default fallback for other content
        return {
            "main_topic": "personal experience",
            "detail_level": "general",
            "emotions": ["determination", "frustration"],
            "details": [content[:100] + "..." if len(content) > 100 else content],
            "insights": ["Experience-based learning"],
            "audience": "HR consultants",
            "story_elements": ["client interaction", "problem solving"],
            "lessons_learned": ["Practical solutions work"],
            "pain_points": ["Client challenges"],
            "solutions": ["Process improvement"]
        }
    
    def _fallback_topic_analysis(self, topic: str) -> Dict:
        """Fallback topic analysis when AI analysis fails."""
        return {
            "relevance_score": 0.7,
            "hr_consulting_relevance": "medium",
            "target_audience": ["HR consultants", "HR managers"],
            "pain_points": ["Common HR challenges"],
            "content_angles": ["Problem-solving approach"],
            "trending_status": "stable",
            "engagement_potential": "medium"
        }
    
    def _fallback_content_validation(self, content: str) -> Dict:
        """Fallback content validation when AI validation fails."""
        return {
            "quality_score": 0.6,
            "authenticity": "medium",
            "specificity": "medium",
            "relevance": "medium",
            "engagement_potential": "medium",
            "issues": ["Limited detail"],
            "strengths": ["Relevant topic"],
            "recommendations": ["Add more specific details"]
        }
    
    def get_status(self) -> Dict:
        """Get component status."""
        return {
            "status": "operational",
            "component": "content_assessor",
            "timestamp": datetime.now().isoformat()
        }


# Test function
def test_content_assessor():
    """Test the content assessor functionality."""
    assessor = ContentAssessor()
    
    # Test content extraction
    test_content = "I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months."
    
    print("🧪 Testing Content Assessor")
    print("=" * 40)
    
    # Test content extraction
    print("📝 Testing content extraction...")
    elements = assessor.extract_content_elements(test_content)
    print(f"Main topic: {elements.get('main_topic', 'N/A')}")
    print(f"Emotions: {elements.get('emotions', [])}")
    print(f"Details: {elements.get('details', [])}")
    
    # Test topic analysis
    print("\n📊 Testing topic analysis...")
    analysis = assessor.analyze_topic_relevance("hiring challenges")
    print(f"Relevance score: {analysis.get('relevance_score', 0)}")
    print(f"HR relevance: {analysis.get('hr_consulting_relevance', 'N/A')}")
    print(f"Target audience: {analysis.get('target_audience', [])}")
    
    # Test content validation
    print("\n✅ Testing content validation...")
    validation = assessor.validate_content_quality(test_content)
    print(f"Quality score: {validation.get('quality_score', 0)}")
    print(f"Authenticity: {validation.get('authenticity', 'N/A')}")
    print(f"Specificity: {validation.get('specificity', 'N/A')}")


if __name__ == "__main__":
    test_content_assessor() 