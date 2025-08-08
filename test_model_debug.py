#!/usr/bin/env python3
"""
Debug Fine-tuned Model ID
Check what's happening with the model ID loading
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_loading():
    """Test loading the fine-tuned model ID."""
    
    print("🔍 Debugging Fine-tuned Model ID Loading")
    print("=" * 50)
    
    # Test 1: Direct import from config.py
    print("📝 Test 1: Direct import from config.py")
    try:
        from config import FINE_TUNED_MODEL
        print(f"✅ FINE_TUNED_MODEL from config.py: {FINE_TUNED_MODEL}")
        print(f"   Type: {type(FINE_TUNED_MODEL)}")
        print(f"   Length: {len(FINE_TUNED_MODEL) if FINE_TUNED_MODEL else 'None'}")
    except Exception as e:
        print(f"❌ Error importing from config.py: {e}")
    
    print()
    
    # Test 2: Import from email_config
    print("📝 Test 2: Import from email_config")
    try:
        from config.email_config import EmailSettings
        model_id = EmailSettings.FINE_TUNED_MODEL_ID
        print(f"✅ FINE_TUNED_MODEL_ID from EmailSettings: {model_id}")
        print(f"   Type: {type(model_id)}")
        print(f"   Length: {len(model_id) if model_id else 'None'}")
        print(f"   Starts with 'ft:': {model_id.startswith('ft:') if model_id else False}")
    except Exception as e:
        print(f"❌ Error importing from email_config: {e}")
    
    print()
    
    # Test 3: Test PostGenerator initialization
    print("📝 Test 3: PostGenerator initialization")
    try:
        from content_handler.post_generator import PostGenerator
        generator = PostGenerator()
        print(f"✅ PostGenerator initialized successfully")
        print(f"   Fine-tuned model: {generator.fine_tuned_model}")
        print(f"   Base model: {generator.base_model}")
    except Exception as e:
        print(f"❌ Error initializing PostGenerator: {e}")
    
    print()
    
    # Test 4: Test actual API call
    print("📝 Test 4: Test actual API call")
    try:
        from content_handler.post_generator import PostGenerator
        generator = PostGenerator()
        
        test_prompt = "Generate a short LinkedIn post about HR consulting."
        
        print(f"   Testing with model: {generator.fine_tuned_model}")
        response = generator.client.chat.completions.create(
            model=generator.fine_tuned_model,
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"✅ API call successful!")
        print(f"   Response: {response.choices[0].message.content[:100]}...")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
    
    print()
    print("🎯 Debug Complete!")

if __name__ == "__main__":
    test_model_loading() 