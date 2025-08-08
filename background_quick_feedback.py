#!/usr/bin/env python3
"""
Background Quick Feedback Processor
Checks latest Airtable record every 300 seconds, classifies feedback, regenerates or adds to RAG, and clears feedback.
"""
import sys
import os
import time
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_logger import AirtableLogger
from rag_memory import RAGMemory
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

CHECK_INTERVAL = 300  # seconds

POSITIVE_KEYWORDS = ["good", "great", "love", "like", "excellent", "perfect", "amazing", "yes", "approved", "works", "keep", "positive", "happy", "satisfied", "awesome", "fantastic", "brilliant", "superb", "thank you", "this is it", "this works"]
NEGATIVE_KEYWORDS = ["no", "not", "bad", "wrong", "short", "long", "change", "fix", "improve", "negative", "dislike", "hate", "redo", "regenerate", "reject", "problem", "issue", "missing", "incorrect", "unsatisfied", "unhappy", "don't like", "needs work", "needs improvement"]

# Use OpenAI to classify feedback
async def classify_feedback(feedback):
    prompt = f"""Classify the following feedback as POSITIVE or NEGATIVE. Only output POSITIVE or NEGATIVE.\n\nFeedback: {feedback}"""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only outputs POSITIVE or NEGATIVE."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        result = response.choices[0].message.content.strip().upper()
        if "POSITIVE" in result:
            return "POSITIVE"
        if "NEGATIVE" in result:
            return "NEGATIVE"
        # fallback: keyword check
        for word in POSITIVE_KEYWORDS:
            if word in feedback.lower():
                return "POSITIVE"
        for word in NEGATIVE_KEYWORDS:
            if word in feedback.lower():
                return "NEGATIVE"
        return "NEGATIVE"
    except Exception as e:
        print(f"Error classifying feedback: {e}")
        # fallback: keyword check
        for word in POSITIVE_KEYWORDS:
            if word in feedback.lower():
                return "POSITIVE"
        for word in NEGATIVE_KEYWORDS:
            if word in feedback.lower():
                return "NEGATIVE"
        return "NEGATIVE"

def regenerate_post(topic, original_post, feedback):
    prompt = f"""You are an expert LinkedIn content creator.\n\nREGENERATE THE POST based on client feedback.\n\nORIGINAL POST:\n{original_post}\n\nCLIENT FEEDBACK:\n{feedback}\n\nINSTRUCTIONS:\n- Create a COMPLETELY NEW post on the same topic\n- Address the specific feedback provided\n- Keep the same core topic and message\n- Make it significantly different from the original\n- Ensure it's engaging and authentic\n- 400-800 words for comprehensive posts\n- Use CAPS sparingly for emphasis\n- Include conversational elements\n\nReturn the new post:"""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert LinkedIn content creator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        new_post = response.choices[0].message.content.strip()
        if new_post.startswith('"') and new_post.endswith('"'):
            new_post = new_post[1:-1]
        return new_post
    except Exception as e:
        print(f"Error regenerating post: {e}")
        return None

def main():
    airtable_logger = AirtableLogger()
    rag_memory = RAGMemory()
    print("🚀 Background Quick Feedback Processor (every 300s)")
    print("=" * 60)
    while True:
        try:
            all_records = airtable_logger.get_all_records()
            if not all_records:
                print("❌ No records found in Airtable")
                time.sleep(CHECK_INTERVAL)
                continue
            latest = all_records[-1]
            fields = latest.get('fields', {})
            feedback = fields.get('Feedback', '').strip()
            topic = fields.get('Topic', '')
            post = fields.get('Post', '')
            record_id = latest.get('id')
            print(f"\n[{datetime.now().isoformat()}] Checking latest record: {record_id} | Topic: {topic}")
            if not feedback:
                print("   No feedback found. Sleeping...")
                time.sleep(CHECK_INTERVAL)
                continue
            print(f"   Feedback: {feedback[:100]}...")
            # Classify feedback
            sentiment = None
            import asyncio
            sentiment = asyncio.run(classify_feedback(feedback))
            print(f"   Classified as: {sentiment}")
            if sentiment == "NEGATIVE":
                print("   Regenerating post...")
                new_post = regenerate_post(topic, post, feedback)
                if new_post:
                    print(f"   New post length: {len(new_post)}")
                    print(f"   Preview: {new_post[:100]}...")
                    airtable_logger.write_post_to_airtable(topic, new_post)
                    print("   ✅ Regenerated post saved to Airtable!")
                else:
                    print("   ❌ Failed to regenerate post!")
            elif sentiment == "POSITIVE":
                print("   Adding post to RAG store...")
                rag_memory.add_post_to_rag(post, topic)
                print("   ✅ Post added to RAG store!")
            # Keep feedback history (don't clear)
            print("   ✅ Feedback processed - keeping history in Airtable")
        except Exception as e:
            print(f"Error in background loop: {e}")
        print(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 