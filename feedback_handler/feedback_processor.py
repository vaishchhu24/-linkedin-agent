#!/usr/bin/env python3
"""
Feedback Handler - Feedback Processor Module
Processes and analyzes client feedback
"""

import re
import json
from typing import Dict, List
from datetime import datetime, timezone

class FeedbackProcessor:
    def __init__(self):
        """Initialize the feedback processor."""
        self.feedback_patterns = {
            'positive': r'\b(like|love|good|great|excellent|perfect|amazing|wonderful|fantastic|awesome)\b',
            'negative': r'\b(don\'t like|hate|bad|terrible|awful|horrible|dislike|not good|poor|wrong)\b',
            'neutral': r'\b(okay|fine|alright|maybe|not sure|indifferent|neutral)\b'
        }
        print("🔄 Feedback Processor initialized")
    
    def process_feedback(self, feedback: str) -> Dict:
        """Process and analyze client feedback."""
        try:
            feedback_lower = feedback.lower().strip()
            
            # Determine feedback sentiment
            sentiment = self._analyze_sentiment(feedback_lower)
            
            # Extract specific issues and suggestions
            issues = self._extract_issues(feedback_lower)
            suggestions = self._extract_suggestions(feedback_lower)
            
            # Determine feedback type
            feedback_type = self._determine_feedback_type(feedback_lower)
            
            return {
                "sentiment": sentiment,
                "feedback_type": feedback_type,
                "issues": issues,
                "suggestions": suggestions,
                "raw_feedback": feedback,
                "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
        except Exception as e:
            print(f"❌ Error processing feedback: {e}")
            return {
                "sentiment": "neutral",
                "feedback_type": "general",
                "issues": [],
                "suggestions": [],
                "raw_feedback": feedback,
                "error": str(e),
                "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
    
    def _analyze_sentiment(self, feedback: str) -> str:
        """Analyze the sentiment of feedback."""
        positive_score = len(re.findall(self.feedback_patterns['positive'], feedback))
        negative_score = len(re.findall(self.feedback_patterns['negative'], feedback))
        neutral_score = len(re.findall(self.feedback_patterns['neutral'], feedback))
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    def _extract_issues(self, feedback: str) -> List[str]:
        """Extract specific issues from feedback."""
        issues = []
        
        # Common issue patterns
        issue_patterns = [
            r'too (short|long|generic|formal|casual)',
            r'not (enough|specific|personal|engaging)',
            r'missing (story|details|emotion|context)',
            r'needs (more|less|different|better)',
            r'(boring|confusing|unclear|vague)',
            r'(tone|style|format) (wrong|off|not right)'
        ]
        
        for pattern in issue_patterns:
            matches = re.findall(pattern, feedback)
            for match in matches:
                if isinstance(match, tuple):
                    issue = ' '.join(match)
                else:
                    issue = match
                if issue not in issues:
                    issues.append(issue)
        
        return issues
    
    def _extract_suggestions(self, feedback: str) -> List[str]:
        """Extract suggestions from feedback."""
        suggestions = []
        
        # Common suggestion patterns
        suggestion_patterns = [
            r'(add|include|put) (more|some|a) (.+?)(?:\s|$)',
            r'(make|change|try) (.+?)(?:\s|$)',
            r'(should|could|would) (.+?)(?:\s|$)',
            r'(like|want) (.+?)(?:\s|$)',
            r'(prefer|rather) (.+?)(?:\s|$)'
        ]
        
        for pattern in suggestion_patterns:
            matches = re.findall(pattern, feedback)
            for match in matches:
                if isinstance(match, tuple):
                    suggestion = ' '.join(match)
                else:
                    suggestion = match
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _determine_feedback_type(self, feedback: str) -> str:
        """Determine the type of feedback."""
        if any(word in feedback for word in ['tone', 'style', 'voice']):
            return "tone_style"
        elif any(word in feedback for word in ['length', 'short', 'long']):
            return "length"
        elif any(word in feedback for word in ['story', 'personal', 'experience']):
            return "content"
        elif any(word in feedback for word in ['topic', 'subject', 'theme']):
            return "topic"
        else:
            return "general"
    
    def generate_refinement_prompt(self, feedback_data: Dict) -> str:
        """Generate a prompt for refining the post based on feedback."""
        try:
            sentiment = feedback_data.get('sentiment', 'neutral')
            issues = feedback_data.get('issues', [])
            suggestions = feedback_data.get('suggestions', [])
            
            prompt = f"Based on client feedback:\n\n"
            
            if sentiment == "negative":
                prompt += "The client didn't like the post. "
            elif sentiment == "positive":
                prompt += "The client liked the post but wants improvements. "
            else:
                prompt += "The client provided neutral feedback. "
            
            if issues:
                prompt += f"\n\nIssues to address:\n"
                for issue in issues:
                    prompt += f"• {issue}\n"
            
            if suggestions:
                prompt += f"\n\nSuggestions to incorporate:\n"
                for suggestion in suggestions:
                    prompt += f"• {suggestion}\n"
            
            prompt += f"\n\nPlease generate a refined version that addresses these points while maintaining the client's authentic voice and style."
            
            return prompt
            
        except Exception as e:
            print(f"❌ Error generating refinement prompt: {e}")
            return "Please refine the post based on client feedback while maintaining authenticity."
    
    def validate_feedback(self, feedback: str) -> Dict:
        """Validate if feedback is actionable."""
        try:
            validation_result = {
                "is_actionable": True,
                "issues": [],
                "suggestions": []
            }
            
            if len(feedback.strip()) < 5:
                validation_result["is_actionable"] = False
                validation_result["issues"].append("Feedback too short")
            
            if feedback.lower() in ['yes', 'no', 'ok', 'fine']:
                validation_result["issues"].append("Feedback too vague")
                validation_result["suggestions"].append("Please provide more specific feedback")
            
            if not any(word in feedback.lower() for word in ['like', 'don\'t', 'good', 'bad', 'change', 'add', 'make']):
                validation_result["issues"].append("No clear feedback direction")
                validation_result["suggestions"].append("Please specify what you like or don't like")
            
            return validation_result
            
        except Exception as e:
            print(f"❌ Error validating feedback: {e}")
            return {
                "is_actionable": False,
                "issues": ["Error in validation"],
                "suggestions": []
            } 