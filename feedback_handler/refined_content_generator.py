#!/usr/bin/env python3
"""
Feedback Handler - Refined Content Generator Module
Generates refined posts based on feedback
"""

import sys
import os
from typing import Dict, Optional

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from content_handler.content_generator import ContentGenerator

class RefinedContentGenerator:
    def __init__(self):
        """Initialize the refined content generator."""
        self.content_generator = ContentGenerator()
        print("🔄 Refined Content Generator initialized")
    
    def generate_refined_post(self, original_post: str, feedback: Dict) -> str:
        """Generate a refined post based on feedback."""
        try:
            print("🔄 Generating refined post based on feedback...")
            
            # Use the content generator with feedback context
            refined_post = self.content_generator.generate_with_feedback(
                original_post=original_post,
                feedback=str(feedback)
            )
            
            return refined_post
            
        except Exception as e:
            print(f"❌ Error generating refined post: {e}")
            return original_post 