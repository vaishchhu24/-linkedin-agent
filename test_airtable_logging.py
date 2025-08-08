#!/usr/bin/env python3
"""
Test script to log a new post to Airtable with improved content style.
"""

import os
import sys
from datetime import datetime, timezone

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger

def test_airtable_logging():
    """Test logging a new post to Airtable."""
    
    print("📝 Testing Airtable Logging with Improved Content")
    print("=" * 50)
    
    # Initialize Airtable logger
    airtable_logger = AirtableLogger()
    
    # Sample improved post content
    improved_post = """💥BOOM! I'm about to drop a TRUTH BOMB!💥

Yesterday, I found myself face-to-face with a client who looked like they'd just been hit by a BUS. Their team was evaporating faster than water in a desert, and they were DESPERATE for help.

Here's what I told them (and what I'm telling YOU):

1️⃣ STOP trying to be everything to everyone. You're not a superhero (even though you feel like one sometimes).

2️⃣ START focusing on what you do BEST. That's where your REAL value lies.

3️⃣ BUILD systems that work FOR you, not against you. Your time is PRECIOUS.

The result? They went from losing 3 people a month to ZERO in 60 days. 

Here's the thing: HR consultants are CONSTANTLY putting out fires. But what if we stopped being firefighters and started being architects?

My mission is to help brilliant HR consultants build businesses that actually work FOR them, not against them.

Because you deserve to THRIVE, not just survive.

#HRConsultants #BusinessGrowth #StopTheBurnout"""

    # Log the post
    topic = "HR consultant burnout and systems"
    
    print(f"📝 Logging post about: {topic}")
    print(f"📊 Post length: {len(improved_post)} characters")
    
    success = airtable_logger.write_post_to_airtable(topic, improved_post)
    
    if success:
        print("✅ Successfully logged post to Airtable!")
        print("🔗 Check your Airtable to see the new post")
    else:
        print("❌ Failed to log post to Airtable")

if __name__ == "__main__":
    test_airtable_logging() 