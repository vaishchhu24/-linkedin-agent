#!/usr/bin/env python3
"""
Content Handler - Content Checker Module
Assesses the detail level of user-provided content
"""

import openai
import json
from typing import Dict, List
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import OPENAI_API_KEY

class ContentChecker:
    def __init__(self):
        """Initialize the content checker."""
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Content assessment criteria
        self.detail_indicators = {
            'detailed': [
                'personal story', 'experience', 'specific incident', 'client case',
                'detailed description', 'concrete example', 'real situation',
                'what happened', 'how I felt', 'what I learned', 'specific outcome'
            ],
            'brief': [
                'topic', 'general idea', 'concept', 'problem', 'challenge',
                'question', 'thought', 'opinion', 'trend', 'issue'
            ]
        }
    
    def assess_content(self, content: str) -> Dict:
        """Assess the detail level of provided content."""
        try:
            # Quick heuristic check first
            heuristic_result = self._heuristic_assessment(content)
            
            # Use OpenAI for more accurate assessment
            ai_result = self._ai_assessment(content)
            
            # Combine results
            final_assessment = self._combine_assessments(heuristic_result, ai_result)
            
            return final_assessment
            
        except Exception as e:
            print(f"❌ Error assessing content: {e}")
            # Fallback to heuristic assessment
            return self._heuristic_assessment(content)
    
    def _heuristic_assessment(self, content: str) -> Dict:
        """Quick heuristic assessment based on content characteristics."""
        content_lower = content.lower()
        word_count = len(content.split())
        
        # Count detail indicators
        detailed_score = 0
        brief_score = 0
        
        for indicator in self.detail_indicators['detailed']:
            if indicator in content_lower:
                detailed_score += 1
        
        for indicator in self.detail_indicators['brief']:
            if indicator in content_lower:
                brief_score += 1
        
        # Determine level based on scores and word count
        if word_count > 100 and detailed_score > brief_score:
            level = 'detailed'
        elif word_count > 50 and detailed_score >= brief_score:
            level = 'detailed'
        elif word_count < 20:
            level = 'brief'
        else:
            level = 'brief'
        
        return {
            'level': level,
            'word_count': word_count,
            'detailed_score': detailed_score,
            'brief_score': brief_score,
            'method': 'heuristic'
        }
    
    def _ai_assessment(self, content: str) -> Dict:
        """Use OpenAI to assess content detail level."""
        try:
            prompt = f"""
            Assess the detail level of this content for LinkedIn post generation:
            
            Content: "{content}"
            
            Determine if this is:
            1. DETAILED - Contains personal stories, specific experiences, concrete examples, or detailed descriptions
            2. BRIEF - Contains general topics, concepts, questions, or brief thoughts
            
            Respond with JSON format:
            {{
                "level": "detailed" or "brief",
                "confidence": 0.0-1.0,
                "reasoning": "explanation of why",
                "suggestions": ["list of suggestions for improvement"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a content assessment expert. Analyze content detail level for LinkedIn post generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                result['method'] = 'ai'
                return result
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_ai_response_fallback(result_text)
                
        except Exception as e:
            print(f"❌ Error in AI assessment: {e}")
            return {
                'level': 'brief',
                'confidence': 0.5,
                'reasoning': 'AI assessment failed',
                'method': 'ai_fallback'
            }
    
    def _parse_ai_response_fallback(self, response_text: str) -> Dict:
        """Fallback parsing for AI response if JSON parsing fails."""
        response_lower = response_text.lower()
        
        if 'detailed' in response_lower:
            level = 'detailed'
        else:
            level = 'brief'
        
        return {
            'level': level,
            'confidence': 0.7,
            'reasoning': 'Parsed from AI response',
            'method': 'ai_fallback'
        }
    
    def _combine_assessments(self, heuristic: Dict, ai: Dict) -> Dict:
        """Combine heuristic and AI assessments."""
        # Weight AI assessment more heavily
        ai_weight = 0.7
        heuristic_weight = 0.3
        
        # If AI confidence is low, rely more on heuristic
        if ai.get('confidence', 0.5) < 0.6:
            ai_weight = 0.3
            heuristic_weight = 0.7
        
        # Determine final level
        if ai['level'] == heuristic['level']:
            final_level = ai['level']
            confidence = max(ai.get('confidence', 0.5), 0.8)
        else:
            # Use weighted decision
            if ai_weight > heuristic_weight:
                final_level = ai['level']
                confidence = ai.get('confidence', 0.5)
            else:
                final_level = heuristic['level']
                confidence = 0.7
        
        return {
            'level': final_level,
            'confidence': confidence,
            'word_count': heuristic.get('word_count', 0),
            'reasoning': ai.get('reasoning', 'Combined assessment'),
            'suggestions': ai.get('suggestions', []),
            'method': 'combined'
        }
    
    def get_content_type(self, content: str) -> str:
        """Get the type of content (story, topic, question, etc.)."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['story', 'experience', 'happened', 'felt', 'learned']):
            return 'personal_story'
        elif any(word in content_lower for word in ['question', 'how', 'what', 'why', 'when']):
            return 'question'
        elif any(word in content_lower for word in ['problem', 'challenge', 'issue', 'struggle']):
            return 'problem'
        elif any(word in content_lower for word in ['topic', 'subject', 'about', 'regarding']):
            return 'topic'
        else:
            return 'general'
    
    def extract_key_elements(self, content: str) -> Dict:
        """Extract key elements from content for post generation."""
        try:
            prompt = f"""
            Extract key elements from this content for LinkedIn post generation:
            
            Content: "{content}"
            
            Extract:
            1. Main topic/theme
            2. Key emotions or feelings
            3. Specific details or examples
            4. Lessons learned or insights
            5. Target audience
            
            Respond in JSON format:
            {{
                "main_topic": "string",
                "emotions": ["list of emotions"],
                "details": ["list of specific details"],
                "insights": ["list of insights"],
                "audience": "string"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a content analysis expert. Extract key elements for LinkedIn post generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                return self._extract_elements_fallback(content)
                
        except Exception as e:
            print(f"❌ Error extracting key elements: {e}")
            return self._extract_elements_fallback(content)
    
    def _extract_elements_fallback(self, content: str) -> Dict:
        """Fallback method for extracting key elements."""
        return {
            "main_topic": content[:50] + "..." if len(content) > 50 else content,
            "emotions": [],
            "details": [],
            "insights": [],
            "audience": "HR consultants"
        } 