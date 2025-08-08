#!/usr/bin/env python3
"""
LinkedIn Content Generation System - Main Coordinator
Coordinates the entire workflow from user prompt to final approval
"""

import os
import sys
import logging
from datetime import datetime, timezone

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.email_scheduler import EmailScheduler
from content_handler.phase2_workflow import Phase2Workflow
from feedback_handler.feedback_loop import FeedbackLoop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInContentSystem:
    """
    Complete LinkedIn Content Generation System
    Coordinates all phases: Email prompts, content generation, and feedback loop.
    """
    
    def __init__(self):
        """Initialize the complete system."""
        self.email_scheduler = EmailScheduler()
        self.phase2_workflow = Phase2Workflow()
        self.feedback_loop = FeedbackLoop()
        
        logger.info("🚀 LinkedIn Content System initialized")
    
    def run_phase1(self):
        """Run Phase 1: Email prompt and response handling."""
        try:
            logger.info("📧 Starting Phase 1: Email Prompt System")
            
            # Send daily prompt
            self.email_scheduler.send_daily_prompt()
            
            # Process any existing responses
            responses = self.email_scheduler.process_user_responses()
            
            logger.info(f"✅ Phase 1 completed. Processed {len(responses)} responses")
            return responses
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 1: {e}")
            return []
    
    def run_phase2(self, user_responses):
        """Run Phase 2: Content generation based on user responses."""
        try:
            logger.info("📝 Starting Phase 2: Content Generation")
            
            generated_posts = []
            
            for response in user_responses:
                try:
                    # Process each user response through Phase 2 workflow
                    result = self.phase2_workflow.process_user_input(
                        user_input=response.get('content', ''),
                        user_intent=response.get('intent', 'general'),
                        metadata=response.get('metadata', {})
                    )
                    
                    if result:
                        generated_posts.append(result)
                        logger.info(f"✅ Generated post for response: {response.get('id', 'unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing response: {e}")
                    continue
            
            logger.info(f"✅ Phase 2 completed. Generated {len(generated_posts)} posts")
            return generated_posts
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 2: {e}")
            return []
    
    def run_phase3(self):
        """Run Phase 3: Feedback loop monitoring and processing."""
        try:
            logger.info("🔄 Starting Phase 3: Feedback Loop System")
            
            # Run feedback loop for a limited number of iterations
            # This will monitor Airtable, process feedback, and prepare fine-tuning data
            self.feedback_loop.run_feedback_loop(max_iterations=3, delay_seconds=30)
            
            logger.info("✅ Phase 3 completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 3: {e}")
            return False
    
    def run_complete_workflow(self):
        """Run the complete workflow: Phase 1 → Phase 2 → Phase 3."""
        try:
            logger.info("🎯 Starting Complete LinkedIn Content Workflow")
            logger.info("=" * 60)
            
            # Phase 1: Email prompts and responses
            user_responses = self.run_phase1()
            
            if user_responses:
                # Phase 2: Content generation
                generated_posts = self.run_phase2(user_responses)
                
                if generated_posts:
                    logger.info(f"📊 Generated {len(generated_posts)} posts for client review")
                    
                    # Phase 3: Feedback loop (runs in background)
                    self.run_phase3()
                else:
                    logger.warning("⚠️ No posts generated in Phase 2")
            else:
                logger.info("ℹ️ No user responses to process")
            
            logger.info("🏁 Complete workflow finished")
            
        except Exception as e:
            logger.error(f"❌ Error in complete workflow: {e}")
    
    def run_feedback_only(self):
        """Run only the feedback loop system (for testing or manual operation)."""
        try:
            logger.info("🔄 Running Feedback Loop Only")
            self.run_phase3()
        except Exception as e:
            logger.error(f"❌ Error running feedback loop: {e}")
    
    def run_content_generation_only(self, user_input: str):
        """Run only content generation (for testing or manual operation)."""
        try:
            logger.info("📝 Running Content Generation Only")
            
            result = self.phase2_workflow.process_user_input(
                user_input=user_input,
                user_intent='detailed',
                metadata={'manual_input': True}
            )
            
            if result:
                logger.info("✅ Content generated successfully")
                return result
            else:
                logger.error("❌ Failed to generate content")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in content generation: {e}")
            return None


def main():
    """Main entry point for the LinkedIn Content System."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Content Generation System')
    parser.add_argument('--mode', choices=['complete', 'phase1', 'phase2', 'phase3', 'feedback', 'generate'], 
                       default='complete', help='Operation mode')
    parser.add_argument('--input', type=str, help='User input for content generation (used with --mode generate)')
    parser.add_argument('--iterations', type=int, default=5, help='Number of feedback loop iterations')
    parser.add_argument('--delay', type=int, default=60, help='Delay between feedback loop iterations (seconds)')
    
    args = parser.parse_args()
    
    # Initialize system
    system = LinkedInContentSystem()
    
    try:
        if args.mode == 'complete':
            system.run_complete_workflow()
            
        elif args.mode == 'phase1':
            system.run_phase1()
            
        elif args.mode == 'phase2':
            if args.input:
                system.run_content_generation_only(args.input)
            else:
                logger.error("❌ --input required for phase2 mode")
                
        elif args.mode == 'phase3':
            system.run_phase3()
            
        elif args.mode == 'feedback':
            system.feedback_loop.run_feedback_loop(
                max_iterations=args.iterations, 
                delay_seconds=args.delay
            )
            
        elif args.mode == 'generate':
            if args.input:
                result = system.run_content_generation_only(args.input)
                if result:
                    print("\n" + "="*50)
                    print("GENERATED CONTENT:")
                    print("="*50)
                    print(result.get('post_content', 'No content generated'))
                    print("="*50)
            else:
                logger.error("❌ --input required for generate mode")
                
    except KeyboardInterrupt:
        logger.info("⏹️ System stopped by user")
    except Exception as e:
        logger.error(f"❌ System error: {e}")


if __name__ == "__main__":
    main()
