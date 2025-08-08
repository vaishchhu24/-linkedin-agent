import json
import re
from typing import Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
import os
import sys

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import importlib.util
project_root = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

class SmartQualityChecker:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        self.voice_analysis = self.load_voice_analysis()
        
    def load_voice_analysis(self) -> Dict:
        """Load the client voice analysis."""
        try:
            with open('data/client_voice_analysis.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Voice analysis file not found")
            return {}
    
    def analyze_voice_consistency(self, post_text: str) -> Dict:
        """Use AI to analyze if the post matches the client's voice."""
        
        voice_context = self.voice_analysis.get('client_voice_analysis', {})
        
        prompt = f"""
You are an expert content quality analyst specializing in brand voice consistency.

CLIENT VOICE PROFILE:
{json.dumps(voice_context, indent=2)}

TASK: Analyze if the following LinkedIn post matches the client's authentic voice and style.

EVALUATION CRITERIA:
1. **Tone Consistency**: Does it match the conversational, direct, relatable tone?
2. **Content Style**: Does it include personal stories/experiences + practical insights?
3. **Audience Alignment**: Is it written for HR professionals transitioning to consulting?
4. **Authenticity**: Does it sound like a real person sharing genuine experiences?
5. **Engagement**: Does it address real pain points and provide value?

POST TO ANALYZE:
{post_text}

Provide your analysis in this exact JSON format:
{{
    "voice_consistency_score": 85,
    "tone_match": true,
    "content_style_match": true,
    "audience_alignment": true,
    "authenticity_score": 90,
    "engagement_potential": 85,
    "voice_issues": ["List any issues with voice consistency"],
    "voice_strengths": ["List what works well"],
    "specific_feedback": "Detailed feedback on voice consistency"
}}
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = json.loads(response.content)
            return analysis
        except Exception as e:
            print(f"Error in voice analysis: {e}")
            return {"voice_consistency_score": 0, "voice_issues": ["Analysis failed"]}
    
    def analyze_content_quality(self, post_text: str) -> Dict:
        """Use AI to analyze overall content quality."""
        
        prompt = f"""
You are an expert LinkedIn content strategist. Analyze the quality of this LinkedIn post.

QUALITY CRITERIA:
1. **Hook Effectiveness**: Does it grab attention immediately?
2. **Value Delivery**: Does it provide actionable insights or lessons?
3. **Readability**: Is it easy to read and understand?
4. **Call-to-Action**: Does it encourage engagement?
5. **Length Optimization**: Is it the right length for LinkedIn?
6. **Hashtag Usage**: Are hashtags relevant and not excessive?

POST TO ANALYZE:
{post_text}

Provide your analysis in this exact JSON format:
{{
    "overall_quality_score": 85,
    "hook_effectiveness": 90,
    "value_delivery": 85,
    "readability": 95,
    "cta_effectiveness": 80,
    "length_optimization": 85,
    "hashtag_quality": 90,
    "quality_issues": ["List any quality issues"],
    "quality_strengths": ["List what works well"],
    "specific_improvements": "Detailed suggestions for improvement"
}}
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = json.loads(response.content)
            return analysis
        except Exception as e:
            print(f"Error in quality analysis: {e}")
            return {"overall_quality_score": 0, "quality_issues": ["Analysis failed"]}
    
    def detect_forbidden_patterns(self, post_text: str) -> Dict:
        """Use AI to detect problematic patterns and content."""
        
        prompt = f"""
You are a content compliance expert. Detect any problematic patterns in this LinkedIn post.

FORBIDDEN PATTERNS TO DETECT:
1. Generic corporate language ("Check out this link", "See what our clients say")
2. Excessive hashtag usage (more than 3)
3. Link drops without context
4. Hypothetical scenarios (should be real experiences)
5. Overly formal business speak
6. Generic motivational content
7. Spammy or promotional language
8. Inappropriate audience targeting

POST TO ANALYZE:
{post_text}

Provide your analysis in this exact JSON format:
{{
    "forbidden_patterns_found": ["List any forbidden patterns detected"],
    "spam_score": 15,
    "corporate_language_detected": false,
    "excessive_hashtags": false,
    "link_drop_without_context": false,
    "hypothetical_content": false,
    "overly_formal": false,
    "generic_motivational": false,
    "pattern_analysis": "Detailed analysis of problematic patterns"
}}
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = json.loads(response.content)
            return analysis
        except Exception as e:
            print(f"Error in pattern detection: {e}")
            return {"forbidden_patterns_found": [], "spam_score": 0}
    
    def generate_improvement_suggestions(self, post_text: str, issues: List[str]) -> str:
        """Use AI to generate specific improvement suggestions."""
        
        prompt = f"""
You are an expert LinkedIn content strategist. Generate specific, actionable suggestions to improve this post.

CURRENT POST:
{post_text}

ISSUES IDENTIFIED:
{issues}

CLIENT VOICE REQUIREMENTS:
- Conversational, direct, relatable tone
- Personal stories + practical insights
- Target audience: HR professionals transitioning to consulting
- Maximum 250 words
- Maximum 3 hashtags

Generate 3-5 specific, actionable suggestions to improve this post. Focus on:
1. Voice consistency improvements
2. Content quality enhancements
3. Engagement optimization
4. Specific rewording suggestions

Format your response as a clear, numbered list of actionable suggestions.
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Error generating suggestions: {e}"
    
    def comprehensive_quality_check(self, post_text: str) -> Dict:
        """Run comprehensive quality analysis using AI."""
        
        print("🔍 Running smart quality analysis...")
        
        # Run all analyses
        voice_analysis = self.analyze_voice_consistency(post_text)
        quality_analysis = self.analyze_content_quality(post_text)
        pattern_analysis = self.detect_forbidden_patterns(post_text)
        
        # Calculate overall score
        voice_score = voice_analysis.get('voice_consistency_score', 0)
        quality_score = quality_analysis.get('overall_quality_score', 0)
        spam_score = pattern_analysis.get('spam_score', 0)
        
        # Weighted overall score
        overall_score = (voice_score * 0.4 + quality_score * 0.4 + (100 - spam_score) * 0.2)
        
        # Determine if post passes
        passes_quality = (
            overall_score >= 75 and 
            len(pattern_analysis.get('forbidden_patterns_found', [])) == 0 and
            voice_score >= 70
        )
        
        # Collect all issues
        all_issues = []
        all_issues.extend(voice_analysis.get('voice_issues', []))
        all_issues.extend(quality_analysis.get('quality_issues', []))
        all_issues.extend(pattern_analysis.get('forbidden_patterns_found', []))
        
        # Generate improvement suggestions
        improvement_suggestions = self.generate_improvement_suggestions(post_text, all_issues)
        
        results = {
            "passes_quality_check": passes_quality,
            "overall_score": round(overall_score, 1),
            "voice_consistency_score": voice_score,
            "content_quality_score": quality_score,
            "spam_score": spam_score,
            "issues": all_issues,
            "voice_strengths": voice_analysis.get('voice_strengths', []),
            "quality_strengths": quality_analysis.get('quality_strengths', []),
            "improvement_suggestions": improvement_suggestions,
            "detailed_analysis": {
                "voice": voice_analysis,
                "quality": quality_analysis,
                "patterns": pattern_analysis
            }
        }
        
        return results
    
    def validate_post_before_posting(self, post_text: str) -> bool:
        """Final validation with detailed reporting."""
        
        results = self.comprehensive_quality_check(post_text)
        
        print("🔍 Smart Content Quality Check Results:")
        print(f"Overall Score: {results['overall_score']}/100")
        print(f"Voice Consistency: {results['voice_consistency_score']}/100")
        print(f"Content Quality: {results['content_quality_score']}/100")
        print(f"Spam Score: {results['spam_score']}/100")
        print(f"Passes: {'✅' if results['passes_quality_check'] else '❌'}")
        
        if results['voice_strengths']:
            print(f"\n✅ Voice Strengths:")
            for strength in results['voice_strengths']:
                print(f"  - {strength}")
        
        if results['quality_strengths']:
            print(f"\n✅ Quality Strengths:")
            for strength in results['quality_strengths']:
                print(f"  - {strength}")
        
        if results['issues']:
            print(f"\n❌ Issues Found:")
            for issue in results['issues']:
                print(f"  - {issue}")
        
        if results['improvement_suggestions']:
            print(f"\n💡 Improvement Suggestions:")
            print(results['improvement_suggestions'])
        
        return results['passes_quality_check']

# Example usage
if __name__ == "__main__":
    checker = SmartQualityChecker()
    
    # Test with the bad example
    bad_post = """Are you a #hrleader, #hrdirector, #hrmanager or #compliance consultant looking to grow? Check out this link to see what our clients say about us. https://lnkd.in/eJY_vnK #hrconsultants #hrleaders #hrmanagers #hrcommunity"""
    
    print("Testing bad post:")
    checker.validate_post_before_posting(bad_post)
    
    # Test with a good example
    good_post = """I recently worked with an HR director who was terrified of leaving her 'safe' corporate salary. She'd been thinking about consulting for months but couldn't pull the trigger.

Sound familiar?

Here's what changed everything for her: she stopped focusing on what she'd lose and started focusing on what she'd gain. Freedom. Flexibility. The chance to actually make an impact.

Within 8 months, she'd replaced her corporate income and was working with clients she actually enjoyed.

The lesson? Your fear of leaving corporate is valid. But staying stuck because of that fear is optional.

What's really holding you back from making the leap?

#hrconsultants #hrleaders"""
    
    print("\n\nTesting good post:")
    checker.validate_post_before_posting(good_post) 