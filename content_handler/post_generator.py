"""
Post Generator Module
Handles fine-tuned OpenAI model integration for LinkedIn post generation
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
from content_handler.time_aware_generator import TimeAwareGenerator
from content_handler.icp_pillar_checker import ICPPillarChecker
from hook_agent import get_ai_hook
from rag_memory import RAGMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostGenerator:
    """
    Post Generator using fine-tuned OpenAI model
    Generates LinkedIn posts in the client's authentic voice
    """
    
    def __init__(self):
        """Initialize the post generator."""
        self.client = OpenAI(api_key=EmailSettings.OPENAI_API_KEY)
        self.fine_tuned_model = EmailSettings.FINE_TUNED_MODEL_ID
        self.base_model = "gpt-4"
        self.time_aware_generator = TimeAwareGenerator()
        self.icp_checker = ICPPillarChecker()
        self.rag_memory = RAGMemory()
        self.client_id = EmailSettings.CLIENT_NAME.lower().replace(" ", "_")
        
        logger.info("🎯 Post Generator initialized")
        logger.info(f"🔧 Fine-tuned model ID: {self.fine_tuned_model}")
        logger.info(f"🔧 Base model: {self.base_model}")
    
    def generate_from_detailed_content(self, detailed_content: str, content_elements: Dict, 
                                     icp_data: Dict, pillar_data: Dict, insights: List[Dict] = None) -> Dict:
        """
        Generate LinkedIn post from detailed user content.
        
        Args:
            detailed_content: User's detailed content/story
            content_elements: Extracted content elements
            icp_data: ICP data (will be enhanced with topic-specific data)
            pillar_data: Content pillar data
            insights: Optional insights from research
            
        Returns:
            Generated post with metadata
        """
        try:
            logger.info("🎯 Generating post from detailed content")
            
            # Get topic-specific ICP data
            topic = content_elements.get('main_topic', 'HR consulting')
            topic_specific_icp = self.icp_checker.get_icp_for_topic(topic)
            
            # Merge with provided ICP data
            enhanced_icp = {**icp_data, **topic_specific_icp}
            
            # Build the generation prompt
            system_prompt, user_prompt = self._build_detailed_content_prompt(
                detailed_content, enhanced_icp, pillar_data
            )
            
            # Combine prompts
            prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate the post
            post_content = self._generate_post_with_fallback(prompt)
            
            if not post_content:
                logger.error("❌ Failed to generate post content")
                return {"success": False, "error": "Failed to generate post"}
            
            # Enhance post quality
            enhanced_post = self._enhance_post_quality(
                post_content, 
                {"topic": topic, "icp_segment": topic_specific_icp.get('segment', 'General')},
                prompt
            )
            
            if not enhanced_post:
                logger.error("❌ Failed to enhance post quality")
                return {"success": False, "error": "Failed to enhance post"}
            
            # Calculate word count
            word_count = len(enhanced_post.split())
            
            return {
                "success": True,
                "post": enhanced_post,
                "word_count": word_count,
                "topic": topic,
                "icp_segment": topic_specific_icp.get('segment', 'General'),
                "metadata": {
                    "generation_method": "detailed_content",
                    "icp_targeted": True,
                    "content_elements_used": list(content_elements.keys()),
                    "insights_count": len(insights) if insights else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating from detailed content: {e}")
            return {"success": False, "error": str(e)}

    def generate_from_topic_only(self, topic: str, insights: List[Dict], icp_data: Dict, pillar_data: Dict) -> Dict:
        """
        Generate post from topic only - CASE 2: User provided topic, need research.
        
        Args:
            topic: User-provided topic
            insights: Research insights
            icp_data: ICP data
            pillar_data: Pillar data
            
        Returns:
            Generated post with metadata
        """
        try:
            logger.info(f"🎯 CASE 2: Generating post from topic only: {topic}")
            
            # Build prompt for topic-only content
            system_prompt, user_prompt = self._build_topic_only_prompt(
                topic, icp_data, pillar_data, insights
            )
            
            # Combine prompts
            prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate post using fine-tuned model
            post = self._generate_post_with_fallback(prompt)
            
            if not post:
                logger.error("❌ Failed to generate post from topic only")
                return {"success": False, "error": "Failed to generate post"}
            
            # Enhance post quality
            enhanced_post = self._enhance_post_quality(
                post, 
                {"topic": topic, "generation_method": "topic_only"},
                prompt
            )
            
            if not enhanced_post:
                logger.error("❌ Failed to enhance post quality")
                return {"success": False, "error": "Failed to enhance post"}
            
            # Calculate word count
            word_count = len(enhanced_post.split())
            
            return {
                "success": True,
                "post": enhanced_post,
                "word_count": word_count,
                "topic": topic,
                "generation_method": "topic_only",
                "insights_used": len(insights),
                "rag_context_used": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating from topic only: {e}")
            return {"success": False, "error": str(e)}

    def generate_from_pillar_topic(self, selected_topic: str, insights: List[Dict], icp_data: Dict, pillar_data: Dict) -> Dict:
        """
        Generate post from pillar-selected topic - CASE 3: No user topic, selected from pillars.
        
        Args:
            selected_topic: Topic selected from content pillars
            insights: Research insights
            icp_data: ICP data
            pillar_data: Pillar data
            
        Returns:
            Generated post with metadata
        """
        try:
            logger.info(f"🎯 CASE 3: Generating post from pillar topic: {selected_topic}")
            
            # Build prompt for pillar-selected topic
            system_prompt, user_prompt = self._build_pillar_topic_prompt(
                selected_topic, icp_data, pillar_data, insights
            )
            
            # Combine prompts
            prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate post using fine-tuned model
            post = self._generate_post_with_fallback(prompt)
            
            if not post:
                logger.error("❌ Failed to generate post from pillar topic")
                return {"success": False, "error": "Failed to generate post"}
            
            # Enhance post quality
            enhanced_post = self._enhance_post_quality(
                post, 
                {"topic": selected_topic, "generation_method": "pillar_topic"},
                prompt
            )
            
            if not enhanced_post:
                logger.error("❌ Failed to enhance post quality")
                return {"success": False, "error": "Failed to enhance post"}
            
            # Calculate word count
            word_count = len(enhanced_post.split())
            
            return {
                "success": True,
                "post": enhanced_post,
                "word_count": word_count,
                "topic": selected_topic,
                "generation_method": "pillar_topic",
                "insights_used": len(insights),
                "rag_context_used": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating from pillar topic: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_from_insights(self, topic: str, insights: List[Dict], icp_data: Dict, 
                              pillar_data: Dict, topic_analysis: Dict) -> Dict:
        """
        Generate post from insights using fine-tuned model.
        
        Args:
            topic: Brief topic
            insights: Validated insights
            icp_data: Ideal Customer Profile data
            pillar_data: Content pillar data
            topic_analysis: Topic relevance analysis
            
        Returns:
            Dict with generated post and metadata
        """
        try:
            logger.info(f"🎯 Generating post from insights for topic: {topic}")
            
            # Construct prompt for insights-based generation
            system_prompt, user_prompt = self._build_insights_prompt(
                topic, insights, icp_data, pillar_data
            )
            
            # Combine prompts
            prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate post using fine-tuned model
            post = self._generate_post_with_fallback(prompt)
            
            # Enhance post quality with original prompt for regeneration
            enhanced_post = self._enhance_post_quality(post, {
                "content_type": "insights_based",
                "icp_data": icp_data,
                "pillar_data": pillar_data,
                "topic": topic,
                "topic_analysis": topic_analysis
            }, original_prompt=prompt)
            
            return {
                "success": True,
                "post": enhanced_post,
                "topic": topic,
                "word_count": len(enhanced_post.split()),
                "generation_method": "fine_tuned_insights",
                "insights_used": len(insights),
                "topic_relevance": topic_analysis.get('relevance_score', 0),
                "rag_context_used": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating from insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "post": "",
                "topic": topic
            }
    
    def generate_trending_post(self, topic: str, insights: List[Dict], icp_data: Dict, 
                              pillar_data: Dict) -> Dict:
        """
        Generate trending post using fine-tuned model.
        
        Args:
            topic: Selected trending topic
            insights: Validated trending insights
            icp_data: Ideal Customer Profile data
            pillar_data: Content pillar data
            
        Returns:
            Dict with generated post and metadata
        """
        try:
            logger.info(f"🎯 Generating trending post for topic: {topic}")
            
            # Build prompt for trending topic
            system_prompt, user_prompt = self._build_trending_prompt(
                topic, icp_data, pillar_data
            )
            
            # Combine prompts
            prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate post using fine-tuned model
            post = self._generate_post_with_fallback(prompt)
            
            # Validate and enhance post with original prompt for regeneration
            enhanced_post = self._enhance_post_quality(post, {
                "topic": topic, 
                "trending": True,
                "content_type": "trending_post"
            }, original_prompt=prompt)
            
            return {
                "success": True,
                "post": enhanced_post,
                "topic": topic,
                "word_count": len(enhanced_post.split()),
                "generation_method": "fine_tuned_trending",
                "trending_topic": topic,
                "insights_used": len(insights),
                "rag_context_used": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating trending post: {e}")
            return {
                "success": False,
                "error": str(e),
                "post": "",
                "topic": topic
            }
    
    def _generate_fallback_post(self, topic: str, content_type: str = "general") -> str:
        """
        Generate fallback post when main generation fails.
        
        Args:
            topic: Topic for fallback post
            content_type: Type of content
            
        Returns:
            Fallback post content
        """
        try:
            logger.warning(f"⚠️ Generating fallback post for topic: {topic}")
            
            # Use fine-tuned model for fallback
            prompt = self._build_fallback_prompt(topic, content_type)
            
            response = self.client.chat.completions.create(
                model=self.fine_tuned_model,
                messages=[
                    {"role": "system", "content": "You are a business coach helping HR consultants build successful businesses. You are NOT an HR consultant offering HR services. You have built 6, 7, and 8-figure HR consultancy businesses. Write from HR consultant's perspective struggling to sell services, then provide recommendations from your expert business coach position. Use a conversational, direct tone with CAPS for emphasis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            post = response.choices[0].message.content.strip()
            return post
            
        except Exception as e:
            logger.error(f"❌ Error generating fallback post: {e}")
            return f"I've been thinking about {topic} lately. This is something I see HR consultants struggle with ALL the time. The key is to focus on your unique value and the real impact you can make. What's your biggest challenge with {topic}? #hrconsultants #hrleaders"
    
    def _build_detailed_content_prompt(self, user_content: str, icp_data: Dict, pillar_info: Dict) -> Tuple[str, str]:
        """Build prompt for detailed user content - CASE 1: User provided detailed story."""
        
        # Get a diverse hook based on the content
        hook = get_ai_hook(self._extract_topic_from_content(user_content))
        
        format_style = self._determine_content_format(user_content, pillar_info)
        
        # Get RAG context for tone adaptation
        topic = self._extract_topic_from_content(user_content)
        rag_context = self._get_rag_context(topic)
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"""CRITICAL TONE ADAPTATION:

Here are ALL past posts that the client approved:
{rag_context}

STUDY THESE APPROVED POSTS AND COPY THEIR EXACT:
- Writing style and tone
- Sentence structure and length
- Use of CAPS and emphasis
- Conversational elements and pauses
- Authentic voice and personality
- Storytelling approach
- Emotional expression
- Professional yet personal balance

CREATE A NEW POST that:
- SOUNDS EXACTLY LIKE the client's voice from the examples above
- Uses the SAME writing patterns and style
- Maintains the SAME level of authenticity and vulnerability
- Matches the SAME tone, humor, and approach
- Feels like it was written by the SAME person

DO NOT copy specific content, but DO copy the exact writing style, tone, and voice."""
        
        system_prompt = f"""You are an expert LinkedIn content creator.
The client has provided a detailed idea in their own words.
Write a LinkedIn post in the client's voice using this exact idea without adding external research.

Rules:
- Preserve the client's tone and voice style
- Use storytelling and structure naturally
- Avoid adding facts not mentioned in the idea
- Optimize for engagement with a hook and a clear flow
- 400-800 words for comprehensive posts
- Use CAPS sparingly for emphasis
- Include conversational elements
- USE bullet points and dashes for clear structure
- Write in organized, scannable format with bullet points for key points and dashes for sub-points
- ADD humor and wit throughout - make it entertaining and relatable
- Include light-hearted moments and self-deprecating humor
- Use humor to make serious points more digestible

Your audience: {icp_data.get('description', 'HR professionals')}

Use this hook: "{hook}"

{rag_section}

Generate a {format_style} post that's engaging and valuable."""

        user_prompt = f"""Idea:
{user_content}

Create a LinkedIn post using the hook and following the voice guidelines above."""

        return system_prompt, user_prompt

    def _build_topic_only_prompt(self, topic: str, icp_data: Dict, pillar_info: Dict, insights: List[Dict]) -> Tuple[str, str]:
        """Build prompt for topic-only content - CASE 2: User provided topic, need research."""
        
        # Get a diverse hook based on the topic
        hook = get_ai_hook(topic)
        
        format_style = self._determine_content_format(topic, pillar_info)
        
        # Get RAG context for tone adaptation
        rag_context = self._get_rag_context(topic)
        
        # Build insights section
        insights_section = ""
        if insights:
            insights_text = "\n".join([f"- {insight.get('insight', '')}" for insight in insights])
            insights_section = f"""RECENT INSIGHTS ON THIS TOPIC:
{insights_text}"""
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"""CRITICAL TONE ADAPTATION:

Here are ALL past posts that the client approved:
{rag_context}

STUDY THESE APPROVED POSTS AND COPY THEIR EXACT:
- Writing style and tone
- Sentence structure and length
- Use of CAPS and emphasis
- Conversational elements and pauses
- Authentic voice and personality
- Storytelling approach
- Emotional expression
- Professional yet personal balance

CREATE A NEW POST that:
- SOUNDS EXACTLY LIKE the client's voice from the examples above
- Uses the SAME writing patterns and style
- Maintains the SAME level of authenticity and vulnerability
- Matches the SAME tone, humor, and approach
- Feels like it was written by the SAME person

DO NOT copy specific content, but DO copy the exact writing style, tone, and voice."""
        
        system_prompt = f"""You are an expert LinkedIn content creator.
The client has provided a short topic. Research has been done to expand it.

Rules:
- Merge the topic with the research insights
- Keep the post in the client's tone and voice
- Make it engaging, structured, and informative
- Include relevant facts from the research naturally
- 400-800 words for comprehensive posts
- Use CAPS sparingly for emphasis
- Include conversational elements
- USE bullet points and dashes for clear structure
- Write in organized, scannable format with bullet points for key points and dashes for sub-points
- ADD humor and wit throughout - make it entertaining and relatable
- Include light-hearted moments and self-deprecating humor
- Use humor to make serious points more digestible

Your audience: {icp_data.get('description', 'HR professionals')}

Use this hook: "{hook}"

{insights_section}

{rag_section}

Generate a {format_style} post that's engaging and valuable."""

        user_prompt = f"""Topic:
{topic}

Research Summary:
{insights_section}

Create a LinkedIn post using the hook and following the voice guidelines above."""

        return system_prompt, user_prompt

    def _build_pillar_topic_prompt(self, selected_topic: str, icp_data: Dict, pillar_info: Dict, insights: List[Dict]) -> Tuple[str, str]:
        """Build prompt for pillar-selected topic - CASE 3: No user topic, selected from pillars."""
        
        # Get a diverse hook based on the topic
        hook = get_ai_hook(selected_topic)
        
        format_style = self._determine_content_format(selected_topic, pillar_info)
        
        # Get RAG context for tone adaptation
        rag_context = self._get_rag_context(selected_topic)
        
        # Build insights section
        insights_section = ""
        if insights:
            insights_text = "\n".join([f"- {insight.get('insight', '')}" for insight in insights])
            insights_section = f"""RECENT INSIGHTS ON THIS TOPIC:
{insights_text}"""
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"""CRITICAL TONE ADAPTATION:

Here are ALL past posts that the client approved:
{rag_context}

STUDY THESE APPROVED POSTS AND COPY THEIR EXACT:
- Writing style and tone
- Sentence structure and length
- Use of CAPS and emphasis
- Conversational elements and pauses
- Authentic voice and personality
- Storytelling approach
- Emotional expression
- Professional yet personal balance

CREATE A NEW POST that:
- SOUNDS EXACTLY LIKE the client's voice from the examples above
- Uses the SAME writing patterns and style
- Maintains the SAME level of authenticity and vulnerability
- Matches the SAME tone, humor, and approach
- Feels like it was written by the SAME person

DO NOT copy specific content, but DO copy the exact writing style, tone, and voice."""
        
        system_prompt = f"""You are an expert LinkedIn content creator.
The client did not provide an idea. A topic has been selected from their content pillars.

Rules:
- Build a LinkedIn post in the client's voice
- Ensure it aligns with the chosen pillar and ICP
- Keep it relevant and insightful
- Make it engaging with a strong hook
- 400-800 words for comprehensive posts
- Use CAPS sparingly for emphasis
- Include conversational elements
- USE bullet points and dashes for clear structure
- Write in organized, scannable format with bullet points for key points and dashes for sub-points

Your audience: {icp_data.get('description', 'HR professionals')}

Use this hook: "{hook}"

{rag_section}

Generate a {format_style} post that's engaging and valuable."""

        user_prompt = f"""Content Pillar:
{pillar_info.get('name', 'General HR')}

Selected Topic:
{selected_topic}

Research Summary:
{insights_section}

Create a LinkedIn post using the hook and following the voice guidelines above."""

        return system_prompt, user_prompt

    def _determine_content_format(self, topic: str, pillar_data: Dict) -> str:
        """Determine the best content format based on topic and pillar."""
        topic_lower = topic.lower()
        pillar_title = pillar_data.get('title', '').lower()
        
        # Quiz format for certain topics
        quiz_keywords = ['quiz', 'assessment', 'check', 'test', 'score', 'points']
        if any(keyword in topic_lower for keyword in quiz_keywords) or 'quiz' in pillar_title:
            return "quiz_format"
        
        # Story format for personal experiences
        story_keywords = ['client', 'meeting', 'experience', 'story', 'happened', 'yesterday']
        if any(keyword in topic_lower for keyword in story_keywords):
            return "story_format"
        
        # Question format for reflection
        question_keywords = ['wonder', 'question', 'think', 'reflect', 'consider']
        if any(keyword in topic_lower for keyword in question_keywords):
            return "question_format"
        
        # Default to story format
        return "story_format"
    
    def _extract_topic_from_content(self, content: str) -> str:
        """Extract a topic from user content for hook generation."""
        # Clean up the content first
        content = content.strip()
        
        # Remove common prefixes that shouldn't be part of the topic
        prefixes_to_remove = [
            "post about", "post on", "write about", "write on", 
            "yes, post about", "yes, post on", "yes, write about",
            "i want to post about", "i want to write about"
        ]
        
        cleaned_content = content.lower()
        for prefix in prefixes_to_remove:
            if cleaned_content.startswith(prefix):
                # Remove the prefix and capitalize first letter
                topic = content[len(prefix):].strip()
                if topic:
                    # Capitalize first letter
                    topic = topic[0].upper() + topic[1:]
                    return topic
        
        # If no prefix found, try to extract the main topic
        # Look for key phrases that indicate the main topic
        key_phrases = [
            "speaking gig", "flight delay", "backup plan", "business lesson",
            "client meeting", "employee retention", "pricing strategy",
            "time management", "imposter syndrome", "first client"
        ]
        
        content_lower = content.lower()
        for phrase in key_phrases:
            if phrase in content_lower:
                # Find the sentence containing this phrase
                sentences = content.split('.')
                for sentence in sentences:
                    if phrase in sentence.lower():
                        # Extract a meaningful topic from this sentence
                        words = sentence.split()[:8]  # Take first 8 words
                        topic = " ".join(words)
                        topic = topic.strip().rstrip('.!?')
                        if len(topic) > 10:  # Ensure it's substantial enough
                            return topic
        
        # Fallback: take first meaningful sentence
        sentences = content.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 10:
                # Take first 8 words of the first sentence
                words = first_sentence.split()[:8]
                topic = " ".join(words)
                topic = topic.strip().rstrip('.!?')
                return topic
        
        # Final fallback
        return "HR consulting business lessons"
    
    def _build_insights_prompt(self, topic: str, insights: List[Dict], icp_data: Dict, pillar_info: Dict) -> Tuple[str, str]:
        """Build prompt for insights-based content generation."""
        
        # Get a diverse hook based on the topic
        hook = get_ai_hook(topic)
        
        format_style = self._determine_content_format(topic, pillar_info)
        
        # Get RAG context from all approved posts
        rag_context = self._get_rag_context(topic)
        
        # Build insights text
        insights_text = ""
        if insights:
            insights_text = "INSIGHTS TO INCORPORATE:\n"
            for i, insight in enumerate(insights, 1):
                insights_text += f"{i}. {insight.get('content', '')}\n"
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"""CRITICAL TONE ADAPTATION INSTRUCTIONS:

Here are ALL past posts that the client approved:
{rag_context}

STUDY THESE APPROVED POSTS AND COPY THEIR EXACT:
- Writing style and tone
- Sentence structure and length
- Use of CAPS and emphasis
- Conversational elements and pauses
- Authentic voice and personality
- Storytelling approach
- Emotional expression
- Professional yet personal balance

CREATE A NEW POST about "{topic}" that:
- SOUNDS EXACTLY LIKE the client's voice from the examples above
- Uses the SAME writing patterns and style
- Maintains the SAME level of authenticity and vulnerability
- Matches the SAME tone, humor, and approach
- Feels like it was written by the SAME person

DO NOT copy specific content, but DO copy the exact writing style, tone, and voice."""
        
        system_prompt = f"""You are {EmailSettings.CLIENT_NAME}, a business coach helping HR consultants build successful businesses.

CRITICAL POSITIONING:
- You are a business coach helping HR consultants succeed
- You are NOT an HR consultant offering HR services
- You have built 6, 7, and 8-figure HR consultancy businesses
- You are their trusted source and expert advisor
- Write from HR consultant's perspective struggling to sell services, then provide recommendations from your expert business coach position
- Key reminder: "I am NOT an HR consultant - I am a business coach helping HR consultants succeed"

WRITE ENGAGING, DIRECT CONTENT:
- Be clear and to the point - no beating around the bush
- Use light humor, not goofy jokes
- Share real insights and actionable advice
- Use CAPS sparingly for emphasis on key points
- Be professional but approachable
- 200-400 words MAX
- Make every sentence count

CONVERSATIONAL ELEMENTS:
- Include natural pauses like "..." for dramatic effect
- Add dramatic pauses "..." after bold statements or uncomfortable truths
- Use phrases like "let's be honest", "truth bomb", "reality check"
- Include "right?" or "am I right?" for engagement
- Add "yikes", "ouch", or "wow" for authentic reactions
- Use "we've all been there" or "sound familiar?" for relatability

Your audience: {icp_data.get('description', 'HR professionals')}
Their pain points: {icp_data.get('pain_points', [])}
Their goals: {icp_data.get('goals', [])}

Use this hook: "{hook}"

{rag_section}

Generate a {format_style} post using these insights:
{insights_text}"""

        user_prompt = f"""Create a LinkedIn post about {topic} using the hook, insights, and approved post patterns provided."""

        return system_prompt, user_prompt

    def _build_trending_prompt(self, topic: str, icp_data: Dict, pillar_info: Dict) -> Tuple[str, str]:
        """Build prompt for trending topic content generation."""
        
        # Get a diverse hook based on the topic
        hook = get_ai_hook(topic)
        
        format_style = self._determine_content_format(topic, pillar_info)
        
        # Get RAG context from all approved posts
        rag_context = self._get_rag_context(topic)
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"""CRITICAL TONE ADAPTATION INSTRUCTIONS:

Here are ALL past posts that the client approved:
{rag_context}

STUDY THESE APPROVED POSTS AND COPY THEIR EXACT:
- Writing style and tone
- Sentence structure and length
- Use of CAPS and emphasis
- Conversational elements and pauses
- Authentic voice and personality
- Storytelling approach
- Emotional expression
- Professional yet personal balance

CREATE A NEW POST about "{topic}" that:
- SOUNDS EXACTLY LIKE the client's voice from the examples above
- Uses the SAME writing patterns and style
- Maintains the SAME level of authenticity and vulnerability
- Matches the SAME tone, humor, and approach
- Feels like it was written by the SAME person

DO NOT copy specific content, but DO copy the exact writing style, tone, and voice."""
        
        system_prompt = f"""You are {EmailSettings.CLIENT_NAME}, a business coach helping HR consultants build successful businesses.

CRITICAL POSITIONING:
- You are a business coach helping HR consultants succeed
- You are NOT an HR consultant offering HR services
- You have built 6, 7, and 8-figure HR consultancy businesses
- You are their trusted source and expert advisor
- Write from HR consultant's perspective struggling to sell services, then provide recommendations from your expert business coach position
- Key reminder: "I am NOT an HR consultant - I am a business coach helping HR consultants succeed"

WRITE ENGAGING, DIRECT CONTENT:
- Be clear and to the point - no beating around the bush
- Use light humor, not goofy jokes
- Share real insights and actionable advice
- Use CAPS sparingly for emphasis on key points
- Be professional but approachable
- 200-400 words MAX
- Make every sentence count

CONVERSATIONAL ELEMENTS:
- Include natural pauses like "..." for dramatic effect
- Add dramatic pauses "..." after bold statements or uncomfortable truths
- Use phrases like "let's be honest", "truth bomb", "reality check"
- Include "right?" or "am I right?" for engagement
- Add "yikes", "ouch", or "wow" for authentic reactions
- Use "we've all been there" or "sound familiar?" for relatability

Your audience: {icp_data.get('description', 'HR professionals')}
Their pain points: {icp_data.get('pain_points', [])}
Their goals: {icp_data.get('goals', [])}

Use this hook: "{hook}"

{rag_section}

Generate a {format_style} post about {topic}."""

        user_prompt = f"""Create a LinkedIn post about {topic} using the hook, approved post patterns, and following the voice guidelines."""

        return system_prompt, user_prompt
    
    def _build_fallback_prompt(self, topic: str, content_type: str) -> str:
        """Build prompt for fallback post generation."""
        return f"""Generate a LinkedIn post about this topic:

TOPIC: {topic}
CONTENT TYPE: {content_type}

Generate a LinkedIn post that:
- Addresses the topic authentically
- Uses CAPS for emphasis
- Is 200-400 words
- Includes 2-3 relevant hashtags
- Feels raw, honest, and conversational
- Provides value to HR consultants

Post:"""
    
    def _generate_with_fine_tuned_model(self, prompt: str) -> str:
        """
        Generate post using fine-tuned model ONLY.
        
        Args:
            prompt: Generation prompt
            
        Returns:
            Generated post content
        """
        try:
            # Use fine-tuned model only
            response = self.client.chat.completions.create(
                model=self.fine_tuned_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            post = response.choices[0].message.content.strip()
            logger.info("✅ Generated post using fine-tuned model")
            return post
            
        except Exception as e:
            logger.error(f"❌ Fine-tuned model failed: {e}")
            return ""
    
    def _generate_post_with_fallback(self, prompt: str) -> str:
        """
        Generate post using base model for better RAG tone adaptation, with fine-tuned model as fallback.
        
        Args:
            prompt: The generation prompt
            
        Returns:
            Generated post content or empty string if both models fail
        """
        try:
            # Check if prompt contains RAG context (indicates we want tone adaptation)
            has_rag_context = "Here are ALL past posts that the client approved:" in prompt
            
            if has_rag_context:
                # Use base model for better RAG tone adaptation
                logger.info("🎯 Using base model for RAG tone adaptation")
                try:
                    response = self.client.chat.completions.create(
                        model=self.base_model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1000,
                        temperature=0.7,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )
                    
                    post = response.choices[0].message.content.strip()
                    if post and len(post.strip()) >= 50:
                        logger.info(f"✅ Generated post using base model for tone adaptation (length: {len(post)})")
                        return post.strip()
                except Exception as e:
                    logger.warning(f"⚠️ Base model failed, falling back to fine-tuned model: {e}")
            
            # Fallback to fine-tuned model
            logger.info("🎯 Using fine-tuned model")
            post = self._generate_with_fine_tuned_model(prompt)
            
            if post and len(post.strip()) >= 50:
                logger.info(f"✅ Generated post using fine-tuned model (length: {len(post)})")
                return post.strip()
            
            # If both models fail, return empty
            logger.error("❌ Both models failed to generate content")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error in post generation: {e}")
            return ""
    
    # Removed _generate_with_base_model method - only using fine-tuned model
    
    def _enhance_post_quality(self, post: str, context: Dict, original_prompt: str = None) -> str:
        """
        Enhance post quality by adding CAPS emphasis, hashtags, and conversational elements.
        
        Args:
            post: Original post content
            context: Context information
            original_prompt: Original generation prompt for regeneration
            
        Returns:
            Enhanced post content
        """
        try:
            # Check if post is too short
            if len(post.strip()) < 50:
                logger.warning("⚠️ Post too short, attempting regeneration...")
                if original_prompt:
                    # Try to regenerate with the same prompt
                    regenerated = self._generate_post_with_fallback(original_prompt)
                    if regenerated and len(regenerated.strip()) >= 50:
                        post = regenerated
                        logger.info("✅ Successfully regenerated post")
                    else:
                        logger.error("❌ Failed to regenerate post - returning empty")
                        return ""
                else:
                    logger.error("❌ Post too short and no original prompt available")
                    return ""
            
            # Add CAPS emphasis if missing
            if not any(word.isupper() for word in post.split() if len(word) > 3):
                logger.warning("⚠️ Post lacks CAPS emphasis, enhancing...")
                post = self._add_caps_emphasis(post)
            
            # Add conversational elements (awkward pauses, dramatic pauses, etc.)
            logger.info("🎭 Adding conversational elements...")
            post = self._add_conversational_elements(post, context)
            
            # Add hashtags (if not already added by conversational elements)
            if not post.endswith('#'):
                post = self._add_hashtags(post, context)
            
            return post
            
        except Exception as e:
            logger.error(f"❌ Error enhancing post quality: {e}")
            return post
    
    def _regenerate_on_topic(self, topic: str, context: Dict) -> str:
        """Regenerate post on the same topic with enhanced prompt."""
        try:
            logger.info(f"🔄 Regenerating post on topic: {topic}")
            
            # Build a more specific prompt for the topic
            enhanced_prompt = f"""
            Create a LinkedIn post about: {topic}
            
            Requirements:
            - Use the client's authentic voice (CAPS for emphasis, conversational tone)
            - Include specific insights and examples related to {topic}
            - Make it 300-600 words
            - Include actionable value for HR consultants
            - Use the client's style: natural, honest, CAPS-heavy, no dashes
            
            Context: {context.get('content_type', 'HR consulting')}
            
            Create a compelling LinkedIn post that provides real value on this specific topic.
            """
            
            return self._generate_post_with_fallback(enhanced_prompt)
            
        except Exception as e:
            logger.error(f"❌ Error regenerating on topic: {e}")
            return f"LinkedIn post about {topic} - content generation in progress."
    
    def _enhance_short_post(self, post: str, context: Dict) -> str:
        """Enhance a short post to make it more substantial."""
        try:
            # Add more context and details
            enhanced_prompt = f"""
            Enhance this LinkedIn post to be more substantial and valuable:
            
            Original Post: {post}
            
            Context: {context.get('content_type', 'HR consulting')}
            
            Make it:
            - 300-600 words
            - Include specific examples or insights
            - Add actionable value for HR consultants
            - Maintain the authentic, CAPS-heavy style
            - Include a clear mission or lesson learned
            
            Enhanced Post:"""
            
            response = self.client.chat.completions.create(
                model=self.base_model,
                messages=[{"role": "user", "content": enhanced_prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error enhancing short post: {e}")
            return post
    
    def _add_caps_emphasis(self, post: str) -> str:
        """Add CAPS emphasis to key words in the post."""
        try:
            # Words that should be emphasized
            emphasis_words = [
                "success", "challenge", "important", "key", "critical", "essential",
                "transform", "breakthrough", "achievement", "victory", "struggle",
                "overcome", "build", "create", "develop", "grow", "scale",
                "confidence", "courage", "strength", "power", "impact", "change"
            ]
            
            enhanced_post = post
            for word in emphasis_words:
                if word.lower() in enhanced_post.lower():
                    # Replace the word with CAPS version
                    enhanced_post = enhanced_post.replace(word, word.upper())
                    enhanced_post = enhanced_post.replace(word.title(), word.upper())
            
            return enhanced_post
            
        except Exception as e:
            logger.error(f"❌ Error adding CAPS emphasis: {e}")
            return post
    
    def _add_hashtags(self, post: str, context: Dict) -> str:
        """Add relevant hashtags to the post."""
        try:
            # Add standard HR consulting hashtags
            hashtags = "#hrconsultants #hrleaders"
            
            # Add topic-specific hashtags
            topic = context.get('topic', '').lower()
            if 'hiring' in topic or 'recruitment' in topic:
                hashtags += " #hiring #recruitment"
            elif 'pricing' in topic or 'strategy' in topic:
                hashtags += " #pricing #strategy"
            elif 'client' in topic or 'business' in topic:
                hashtags += " #clientacquisition #businessgrowth"
            
            return f"{post}\n\n{hashtags}"
            
        except Exception as e:
            logger.error(f"❌ Error adding hashtags: {e}")
            return f"{post}\n\n#hrconsultants #hrleaders"
    
    def _add_conversational_elements(self, post: str, context: Dict) -> str:
        """
        Add conversational elements like awkward pauses and authentic human touches.
        
        Args:
            post: Original post content
            context: Context information including topic and tone
            
        Returns:
            Enhanced post with conversational elements
        """
        try:
            # Don't add too many elements - keep it natural
            if len(post.split()) < 50:
                return post  # Too short to add elements
            
            enhanced_post = post
            topic = context.get('topic', '').lower()
            
            # Conversational elements to add
            conversational_elements = [
                # Awkward pauses and reactions
                "...",
                "awkward silence",
                "yikes",
                "ouch",
                "wow",
                "seriously",
                "I mean",
                "right?",
                "am I right?",
                "you know what I mean?",
                "let's be honest",
                "truth bomb",
                "reality check"
            ]
            
            # Topic-specific elements
            if any(word in topic for word in ['pricing', 'money', 'cost', 'fee']):
                conversational_elements.extend([
                    "money talk",
                    "the elephant in the room",
                    "let's talk about money",
                    "the uncomfortable truth"
                ])
            
            if any(word in topic for word in ['client', 'difficult', 'challenge', 'problem']):
                conversational_elements.extend([
                    "we've all been there",
                    "sound familiar?",
                    "raise your hand if",
                    "anyone else?",
                    "just me?"
                ])
            
            if any(word in topic for word in ['success', 'achievement', 'win', 'victory']):
                conversational_elements.extend([
                    "boom",
                    "mic drop",
                    "nailed it",
                    "that's how it's done"
                ])
            
            # Strategic placement of elements
            sentences = enhanced_post.split('. ')
            if len(sentences) >= 3:
                # Add elements at natural break points
                insertions = []
                
                # Add dramatic pause after a bold statement
                for i, sentence in enumerate(sentences):
                    if any(word in sentence.lower() for word in ['truth', 'reality', 'honest', 'real']):
                        if i < len(sentences) - 1:  # Not the last sentence
                            insertions.append((i + 1, "..."))
                
                # Add "..." for dramatic pause
                for i, sentence in enumerate(sentences):
                    if any(word in sentence.lower() for word in ['but', 'however', 'yet', 'still']):
                        if i < len(sentences) - 1:
                            insertions.append((i + 1, "..."))
                
                # Add topic-specific elements
                if any(word in topic for word in ['pricing', 'money']):
                    for i, sentence in enumerate(sentences):
                        if any(word in sentence.lower() for word in ['money', 'cost', 'fee', 'price']):
                            if i < len(sentences) - 1:
                                insertions.append((i + 1, "the elephant in the room"))
                
                # Apply insertions (in reverse order to maintain indices)
                insertions.sort(reverse=True)
                for index, element in insertions:
                    if index < len(sentences):
                        sentences.insert(index, element)
                
                enhanced_post = '. '.join(sentences)
            
            # Add hashtags with conversational elements
            if enhanced_post != post:
                enhanced_post = self._add_hashtags(enhanced_post, context)
            
            return enhanced_post
            
        except Exception as e:
            logger.error(f"❌ Error adding conversational elements: {e}")
            return post
    
    def get_status(self) -> Dict:
        """Get component status."""
        return {
            "status": "operational",
            "component": "post_generator",
            "fine_tuned_model": self.fine_tuned_model,
            "base_model": self.base_model,
            "timestamp": datetime.now().isoformat()
        }

    def _get_rag_context(self, topic: str) -> str:
        """
        Get RAG context from ALL approved posts by the client.
        
        Args:
            topic: The topic to find similar posts for
            
        Returns:
            Formatted context string with all approved posts
        """
        try:
            # Retrieve ALL approved posts from RAG store (no recency filter)
            similar_posts = self.rag_memory.retrieve_similar_posts(
                topic=topic,
                client_id=self.client_id,
                after_days=0,  # No recency filter - get ALL posts
                top_k=None     # Get ALL posts
            )
            
            if not similar_posts:
                logger.info("📭 No RAG context found for topic")
                return ""
            
            # Format all approved posts for context
            context_parts = []
            
            # Add the excellent example template first
            context_parts.append("EXCELLENT EXAMPLE TEMPLATE (FOLLOW THIS STYLE):")
            context_parts.append("As an HR consultant, I'm sure you are used to going into present your services to prospects. How often have you had that awkward moment where you ask 'Please let me know if you have any questions.' You don't know what to do with yourself as that tumbleweed of silence turns into an awkward moment.")
            context_parts.append("")
            context_parts.append("How about asking:")
            context_parts.append("- 'How can I best support you from here?'")
            context_parts.append("- 'What do you feel I didn't cover that would be helpful for you today?'")
            context_parts.append("")
            context_parts.append("For some reason - that 'Any questions' line - just seems to be super awkward.")
            context_parts.append("")
            context_parts.append("This shows humor, it shows I've been there and understanding it - it also gives 2-3 examples of how to ask the same question but differently to encourage engagement and to move the conversation one step closer to a potential sale.")
            context_parts.append("")
            context_parts.append("#hrconsultants #hrleaders")
            context_parts.append("")
            context_parts.append("IDEAL POST TEMPLATE (USE THIS STYLE):")
            context_parts.append("Oh, I've heard that one before. And if you're an HR professional, I bet you have too.")
            context_parts.append("")
            context_parts.append("Let me paint you a picture.")
            context_parts.append("")
            context_parts.append("You're in the middle of a meeting, navigating through the labyrinth of employee engagement strategies, benefits packages, and the latest HR tech tools when suddenly, it happens.")
            context_parts.append("")
            context_parts.append("The presenter delivers the dreaded line - 'Please let me know if you have any questions.'")
            context_parts.append("")
            context_parts.append("And what follows? Dead silence. A tumbleweed could roll through the room and it wouldn't feel out of place.")
            context_parts.append("")
            context_parts.append("Why? Well, we've all been there. The fear of asking a 'stupid' question, or not wanting to be 'that person' who holds up the meeting with a query.")
            context_parts.append("")
            context_parts.append("But here's the kicker:")
            context_parts.append("")
            context_parts.append("Questions are the lifeblood of understanding. The MORE we ask, the MORE we learn.")
            context_parts.append("")
            context_parts.append("Now, I'm not suggesting we turn every meeting into an episode of 'Who Wants To Be A Millionaire'. But it's crucial to create an environment where questions are ENCOURAGED, not feared.")
            context_parts.append("")
            context_parts.append("So, how do we do that?")
            context_parts.append("")
            context_parts.append("- Make it clear that NO question is off the table or too 'silly' to ask.")
            context_parts.append("- Make it SAFE to ask anything. People need to feel comfortable, not judged.")
            context_parts.append("- Make sure to RESPOND positively to every question. That reinforcement goes a long way.")
            context_parts.append("- Make time for QUESTIONS in each meeting. Don't rush through them.")
            context_parts.append("")
            context_parts.append("Let's flip the script - instead of a tumbleweed moment, let's turn 'Any questions?' into a gateway for engaging discussions and deeper understanding.")
            context_parts.append("")
            context_parts.append("And remember, if you're not asking questions, you're probably not learning anything new. So next time someone asks 'Any questions?' - raise your hand high and proud. It's your time to shine!")
            context_parts.append("")
            context_parts.append("As they say, the only stupid question is the one that isn't asked.")
            context_parts.append("")
            context_parts.append("So, dear HR folks, let's make our workplaces a haven for curiosity and learning. Because ultimately, it's the questions we ask today that shape the solutions of tomorrow.")
            context_parts.append("")
            context_parts.append("But hey, don't take my word for it. Please let me know if you have any questions. 😉")
            context_parts.append("")
            context_parts.append("#hrconsultants #hrleaders")
            context_parts.append("")
            context_parts.append("BUSINESS COACH TEMPLATE (FOLLOW THIS STYLE):")
            context_parts.append("As an HR consultant, I'm sure you are used to going into present your services to prospects. How often have you had that awkward moment where you ask 'Please let me know if you have any questions.' You don't know what to do with yourself as that tumbleweed of silence turns into an awkward moment.")
            context_parts.append("")
            context_parts.append("How about asking:")
            context_parts.append("- 'How can I best support you from here?'")
            context_parts.append("- 'What do you feel I didn't cover that would be helpful for you today?'")
            context_parts.append("")
            context_parts.append("For some reason - that 'Any questions' line - just seems to be super awkward.")
            context_parts.append("")
            context_parts.append("This shows humor, it shows I've been there and understanding it - it also gives 2-3 examples of how to ask the same question but differently to encourage engagement and to move the conversation one step closer to a potential sale.")
            context_parts.append("")
            context_parts.append("#hrconsultants #hrleaders")
            context_parts.append("")
            context_parts.append("APPROVED POSTS FROM CLIENT:")
            
            for i, post in enumerate(similar_posts, 1):
                # Handle case where post might be a string instead of dict
                if isinstance(post, str):
                    context_parts.append(f"{i}. Post: {post[:200]}...")
                    context_parts.append("")
                    continue
                
                # Handle dictionary format
                if isinstance(post, dict):
                    context_parts.append(f"{i}. Topic: {post.get('topic', 'Unknown')}")
                    context_parts.append(f"   Post: {post.get('post', '')[:200]}...")
                    context_parts.append(f"   Quality: Voice {post.get('voice_quality', 0)}/10, Post {post.get('post_quality', 0)}/10")
                    context_parts.append("")
                else:
                    # Fallback for unknown format
                    context_parts.append(f"{i}. Post: {str(post)[:200]}...")
                    context_parts.append("")
            
            rag_context = "\n".join(context_parts)
            logger.info(f"📚 Retrieved ALL {len(similar_posts)} approved posts for RAG context")
            
            return rag_context
            
        except Exception as e:
            logger.error(f"❌ Error getting RAG context: {e}")
            return ""


# Test function
def test_post_generator():
    """Test the post generator functionality."""
    generator = PostGenerator()
    
    print("🧪 Testing Post Generator")
    print("=" * 40)
    
    # Test detailed content generation
    print("📝 Testing detailed content generation...")
    detailed_content = "I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months."
    content_elements = {
        "main_topic": "employee retention",
        "emotions": ["frustration", "determination"],
        "details": ["client meeting", "3-step process", "40% reduction"],
        "insights": ["Process-based solutions work"],
        "lessons_learned": ["Systematic approach is key"]
    }
    
    result = generator.generate_from_detailed_content(
        detailed_content, content_elements, 
        {"target_audience": "HR consultants"}, 
        {"title": "Employee Retention"}
    )
    
    print(f"Generated post ({result['word_count']} words):")
    print(result['post'][:200] + "...")
    
    print("\n✅ Post generation test completed!")


if __name__ == "__main__":
    test_post_generator() 