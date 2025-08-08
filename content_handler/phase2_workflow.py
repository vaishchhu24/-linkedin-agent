"""
Phase 2: Content Assessment and Generation Workflow
Handles three distinct scenarios for LinkedIn content generation
"""

import os
import sys
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_handler.content_assessor import ContentAssessor
from content_handler.insight_fetcher import InsightFetcher
from content_handler.icp_pillar_checker import ICPPillarChecker
from content_handler.post_generator import PostGenerator
from config.email_config import ContentClassificationSettings
from airtable_logger import write_post_to_airtable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2Workflow:
    """
    Phase 2 Workflow Coordinator
    Handles three distinct scenarios for content generation
    """
    
    def __init__(self):
        """Initialize Phase 2 workflow components."""
        self.content_assessor = ContentAssessor()
        self.insight_fetcher = InsightFetcher()
        self.icp_checker = ICPPillarChecker()
        self.post_generator = PostGenerator()
        
        logger.info("🎯 Phase 2 Workflow initialized")
    
    def process_user_input(self, user_input: str, content_type: str) -> Dict:
        """
        Main entry point for Phase 2 processing.
        
        Args:
            user_input: User's content or topic
            content_type: Classification from Phase 1 ("detailed_content", "general_topic", "declined")
            
        Returns:
            Dict with generated post and metadata
        """
        try:
            logger.info(f"🚀 Starting Phase 2 processing for content type: {content_type}")
            
            # Route to appropriate scenario handler based on Phase 1 classification
            if content_type == "detailed_content":
                return self._handle_detailed_content_scenario(user_input)
            elif content_type == "general_topic":
                return self._handle_brief_topic_scenario(user_input)
            elif content_type == "declined":
                return self._handle_no_input_scenario()
            else:
                logger.warning(f"⚠️ Unknown content type: {content_type}, treating as declined")
                return self._handle_no_input_scenario()
                
        except Exception as e:
            logger.error(f"❌ Error in Phase 2 processing: {e}")
            return self._generate_fallback_post(user_input, content_type)
    
    def _handle_detailed_content_scenario(self, detailed_content: str) -> Dict:
        """
        ✅ Scenario 1: Detailed Content Provided
        Trigger: User replies with "Yes" and provides a story or personal experience
        Logic: Pass directly to fine-tuned model
        Output: Full LinkedIn post (Hook, Body, CTA) in client's tone
        Source Tag: "DetailedContent"
        """
        try:
            logger.info("📝 Scenario 1: Processing detailed user content")
            
            # Extract key elements from detailed content
            content_elements = self.content_assessor.extract_content_elements(detailed_content)
            main_topic = content_elements.get('main_topic', 'detailed_content')
            
            # Get relevant ICP and pillar data for context
            icp_data = self.icp_checker.get_icp_data()
            if isinstance(icp_data, str):
                icp_data = {"target_audience": "HR consultants", "pain_points": [], "goals": []}
            
            # Get the most relevant content pillar for this topic
            relevant_pillar = self.icp_checker.get_most_relevant_pillar(main_topic)
            
            # If no relevant pillar found, get a random pillar focused on HR consulting
            if not relevant_pillar:
                relevant_pillar = self.icp_checker.get_random_pillar()
            
            # Fetch insights related to the main topic for additional value
            insights = self.insight_fetcher.fetch_topic_insights(
                topic=main_topic,
                max_insights=2,
                source="reddit"
            )
            
            # Validate insights
            validated_insights = self.insight_fetcher.validate_insights_quality(insights)
            
            # Generate post using fine-tuned model with enhanced context
            post_result = self.post_generator.generate_from_detailed_content(
                detailed_content=detailed_content,
                content_elements=content_elements,
                icp_data=icp_data,
                pillar_data=relevant_pillar,
                insights=validated_insights
            )
            
            # Log to Airtable
            try:
                write_post_to_airtable(
                    topic=main_topic,
                    post=post_result["post"]
                )
                logger.info("✅ Post logged to Airtable")
            except Exception as e:
                logger.error(f"❌ Error logging to Airtable: {e}")
            
            return {
                "scenario": "detailed_content",
                "success": True,
                "post": post_result["post"],
                "source_tag": "DetailedContent",
                "metadata": {
                    "content_type": "detailed_content",
                    "word_count": post_result.get("word_count", 0),
                    "generation_method": "fine_tuned_model",
                    "content_elements": content_elements,
                    "pillar_used": relevant_pillar.get('title', 'N/A'),
                    "insights_count": len(validated_insights),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "message": "Post generated from detailed user content using fine-tuned model"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in detailed content scenario: {e}")
            return self._generate_fallback_post(detailed_content, "detailed_content")
    
    def _handle_brief_topic_scenario(self, brief_topic: str) -> Dict:
        """
        ⚠️ Scenario 2: Brief Topic Provided
        Trigger: User replies with "Yes" and provides only a short/abstract topic
        Logic: NEVER send brief topic directly to LLM. Always enrich with Perplexity + Pillars + ICP
        Output: Hook, body, CTA — highly relevant and grounded in real pain points
        Source Tag: "BriefTopic + Reddit"
        """
        try:
            logger.info(f"📝 Scenario 2: Processing brief topic: {brief_topic}")
            
            # Step 1: Identify topic relevance using OpenAI
            topic_analysis = self.content_assessor.analyze_topic_relevance(brief_topic)
            
            # Step 2: Fetch Reddit insights via Perplexity API (ANTI-HALLUCINATION)
            insights = self.insight_fetcher.fetch_topic_insights(
                topic=brief_topic,
                max_insights=3,
                source="reddit"
            )
            
            # Step 3: Validate insights to avoid hallucinations
            validated_insights = self.insight_fetcher.validate_insights_quality(insights)
            
            # Step 4: Cross-reference with ICP and content pillars
            icp_data = self.icp_checker.get_icp_data()
            if isinstance(icp_data, str):
                icp_data = {"target_audience": "HR consultants", "pain_points": [], "goals": []}
            relevant_pillar = self.icp_checker.get_most_relevant_pillar(brief_topic)
            
            # Step 5: Generate post with verified insights (NEVER send brief topic directly)
            post_result = self.post_generator.generate_from_insights(
                topic=brief_topic,
                insights=validated_insights,
                icp_data=icp_data,
                pillar_data=relevant_pillar,
                topic_analysis=topic_analysis
            )
            
            # Log to Airtable
            try:
                write_post_to_airtable(
                    topic=brief_topic,
                    post=post_result["post"]
                )
                logger.info("✅ Post logged to Airtable")
            except Exception as e:
                logger.error(f"❌ Error logging to Airtable: {e}")
            
            return {
                "scenario": "brief_topic",
                "success": True,
                "post": post_result["post"],
                "source_tag": "BriefTopic + Reddit",
                "metadata": {
                    "content_type": "general_topic",
                    "word_count": post_result.get("word_count", 0),
                    "generation_method": "insights_enhanced",
                    "insights_count": len(validated_insights),
                    "topic_relevance": topic_analysis.get('relevance_score', 0.0),
                    "pillar_used": relevant_pillar.get('title', 'N/A'),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "message": f"Post generated from brief topic '{brief_topic}' using verified insights"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in brief topic scenario: {e}")
            return self._generate_fallback_post(brief_topic, "general_topic")
    
    def _handle_no_input_scenario(self) -> Dict:
        """
        🚫 Scenario 3: User Says "No"
        Trigger: User replies simply with "No"
        Logic: Auto-select relevant topic from content pillars, match with ICP, use Perplexity for fresh insights
        Output: A post generated without needing user input
        Source Tag: "NoInput + Pillar"
        """
        try:
            logger.info("📝 Scenario 3: Processing declined response")
            
            # Step 1: Auto-select a relevant topic from content pillars
            trending_topics = self.icp_checker.get_trending_topics()
            
            # Step 2: Match with ICP segment
            icp_data = self.icp_checker.get_icp_data()
            if isinstance(icp_data, str):
                icp_data = {"target_audience": "HR consultants", "pain_points": [], "goals": []}
            
            # Step 3: Select best topic for ICP alignment
            selected_topic = self.icp_checker.select_best_topic_for_icp(trending_topics, icp_data)
            
            # Step 4: Use Perplexity to fetch fresh insights on that topic
            insights = self.insight_fetcher.fetch_topic_insights(
                topic=selected_topic,
                max_insights=3,
                source="reddit"
            )
            
            # Step 5: Validate insights
            validated_insights = self.insight_fetcher.validate_insights_quality(insights)
            
            # Step 6: Get relevant pillar for the selected topic
            relevant_pillar = self.icp_checker.get_most_relevant_pillar(selected_topic)
            
            # Step 7: Generate trending post with all context
            post_result = self.post_generator.generate_trending_post(
                topic=selected_topic,
                insights=validated_insights,
                icp_data=icp_data,
                pillar_data=relevant_pillar
            )
            
            # Log to Airtable
            try:
                write_post_to_airtable(
                    topic=selected_topic,
                    post=post_result["post"]
                )
                logger.info("✅ Post logged to Airtable")
            except Exception as e:
                logger.error(f"❌ Error logging to Airtable: {e}")
            
            return {
                "scenario": "declined_response",
                "success": True,
                "post": post_result["post"],
                "source_tag": "NoInput + Pillar",
                "metadata": {
                    "content_type": "declined",
                    "word_count": post_result.get("word_count", 0),
                    "generation_method": "trending_insights",
                    "selected_topic": selected_topic,
                    "insights_count": len(validated_insights),
                    "pillar_used": relevant_pillar.get('title', 'N/A'),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "message": f"Post generated from trending topic '{selected_topic}' using content pillars"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in no input scenario: {e}")
            return self._generate_fallback_post("HR consulting insights", "declined")
    
    def _generate_fallback_post(self, user_input: str, content_type: str) -> Dict:
        """
        Generate fallback post when main processing fails
        """
        try:
            logger.warning(f"⚠️ Using fallback post generation for content type: {content_type}")
            
            # Generate basic fallback post
            fallback_post = self.post_generator._generate_fallback_post(
                topic=user_input or "HR consulting insights",
                content_type=content_type
            )
            
            return {
                "scenario": "fallback",
                "success": False,
                "post": fallback_post,
                "metadata": {
                    "content_type": content_type,
                    "word_count": len(fallback_post.split()),
                    "generation_method": "fallback",
                    "error": "Main processing failed, using fallback",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "message": "Fallback post generated due to processing error"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in fallback post generation: {e}")
            return {
                "scenario": "error",
                "success": False,
                "post": "I've been thinking about HR consulting challenges lately. This is something I see HR consultants struggle with ALL the time. The key is to focus on your unique value and the real impact you can make. What's your biggest challenge with HR consulting? #hrconsultants #hrleaders",
                "metadata": {
                    "content_type": content_type,
                    "word_count": 0,
                    "generation_method": "hardcoded_fallback",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "message": "Hardcoded fallback post due to complete system failure"
            }
    
    def get_workflow_status(self) -> Dict:
        """Get current workflow status and component health."""
        try:
            return {
                "workflow_status": "operational",
                "components": {
                    "content_assessor": self.content_assessor.get_status(),
                    "insight_fetcher": self.insight_fetcher.get_status(),
                    "icp_checker": self.icp_checker.get_status(),
                    "post_generator": self.post_generator.get_status()
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting workflow status: {e}")
            return {
                "workflow_status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Main execution for testing
def main():
    """Test Phase 2 workflow with different scenarios."""
    workflow = Phase2Workflow()
    
    # Test scenarios
    test_cases = [
        {
            "input": "I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months.",
            "type": "detailed_content",
            "description": "Detailed personal experience"
        },
        {
            "input": "hiring challenges",
            "type": "general_topic",
            "description": "Brief topic"
        },
        {
            "input": "",
            "type": "declined",
            "description": "User declined"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print("=" * 50)
        
        result = workflow.process_user_input(test_case["input"], test_case["type"])
        
        print(f"Scenario: {result['scenario']}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Word Count: {result['metadata']['word_count']}")
        print(f"Post Preview: {result['post'][:200]}...")
        print()


if __name__ == "__main__":
    main() 