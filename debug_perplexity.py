#!/usr/bin/env python3
"""
Debug script to test Perplexity API directly
"""

import sys
import os
import requests
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Debugging Perplexity API")
print("=" * 50)

# Test 1: Check API key loading
print("\n1️⃣ Testing API key loading:")
try:
    from config.email_config import EmailSettings
    api_key = EmailSettings.PERPLEXITY_API_KEY
    print(f"✅ API Key loaded: {api_key[:20]}..." if api_key else "❌ No API key")
except Exception as e:
    print(f"❌ Error loading API key: {e}")

# Test 2: Test direct API call
print("\n2️⃣ Testing direct API call:")
try:
    from config.email_config import EmailSettings
    api_key = EmailSettings.PERPLEXITY_API_KEY
    
    if not api_key:
        print("❌ No API key available")
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a comprehensive web research assistant specializing in deep web scraping and analysis. Conduct thorough research across multiple sources including industry reports, news articles, expert blogs, case studies, and professional discussions."
                },
                {
                    "role": "user",
                    "content": "Conduct deep web research on the top 3 challenges HR consultants face today. Include industry reports, expert analysis, case studies, and market data. Return as JSON array with fields: source, content, relevance_score, date, author_type, data_type."
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.2
        }
        
        print("📡 Making API request...")
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=120  # Increased timeout for deep research
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Success! Response: {content[:200]}...")
        else:
            print(f"❌ Error response: {response.text}")
            
except Exception as e:
    print(f"❌ Error testing API: {e}")

# Test 3: Check API documentation
print("\n3️⃣ Checking API documentation:")
print("📖 Perplexity API docs: https://docs.perplexity.ai/")
print("📖 Model list: https://docs.perplexity.ai/models")

print("\n" + "=" * 50)
print("�� Debug complete") 