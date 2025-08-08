import json
import os
from datetime import datetime, timedelta
import requests

def get_feedback_from_airtable(client_id="vaishnavi"):
    """
    Get feedback from the same Airtable table where posts are logged.
    Looks for a 'Feedback' column in the most recent records.
    
    Args:
        client_id: Client identifier (not used for single client setup)
        
    Returns:
        dict: Feedback data from Airtable or None if not available
    """
    try:
        # Import Airtable config
        import importlib.util
        project_root = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        AIRTABLE_API_KEY = config.AIRTABLE_API_KEY
        AIRTABLE_BASE_ID = config.AIRTABLE_BASE_ID
        AIRTABLE_TABLE_NAME = config.AIRTABLE_TABLE_NAME
        
        # Airtable API endpoint for the posts table
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Get recent records (last 20) to check for feedback
        params = {
            "maxRecords": 20
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                # Look for records with feedback
                feedback_records = []
                for record in records:
                    fields = record.get('fields', {})
                    if 'Feedback' in fields and fields['Feedback']:
                        feedback_records.append({
                            'feedback': fields['Feedback'],
                            'timestamp': fields.get('Timestamp', ''),
                            'topic': fields.get('Topic', ''),
                            'post': fields.get('Post', '')
                        })
                
                if feedback_records:
                    # Get the most recent feedback
                    latest_feedback = feedback_records[0]
                    print(f"✅ Found feedback in Airtable from {latest_feedback['timestamp']}")
                    print(f"   Topic: {latest_feedback['topic']}")
                    print(f"   Feedback: {latest_feedback['feedback'][:100]}...")
                    return latest_feedback
                else:
                    print(f"📝 No feedback found in recent Airtable records")
                    return None
            else:
                print(f"📝 No records found in Airtable table")
                return None
        else:
            print(f"❌ Airtable API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting feedback from Airtable: {e}")
        return None

def get_feedback_context(client_id="vaishnavi"):
    """
    Get feedback context from Airtable posts table, with fallback to default.
    Always returns comprehensive feedback context.
    
    Args:
        client_id: Client identifier
        
    Returns:
        str: Feedback context for the client
    """
    try:
        # First, try to get feedback from Airtable posts table
        print(f"📝 Checking Airtable posts table for feedback...")
        airtable_feedback = get_feedback_from_airtable(client_id)
        
        if airtable_feedback:
            # Use Airtable feedback
            feedback_context = format_airtable_feedback(airtable_feedback)
            print(f"✅ Using feedback from Airtable posts table")
            return feedback_context
        else:
            # Fallback to default feedback
            print(f"📝 No Airtable feedback found, using default feedback")
            default_feedback = create_default_feedback()
            return format_feedback_context(default_feedback)
        
    except Exception as e:
        print(f"❌ Error getting feedback context: {e}")
        # Return comprehensive default feedback as fallback
        return create_fallback_feedback_context()

def format_airtable_feedback(airtable_feedback):
    """
    Format Airtable feedback data into a readable context string.
    
    Args:
        airtable_feedback: Feedback data from Airtable
        
    Returns:
        str: Formatted feedback context
    """
    feedback_text = airtable_feedback.get('feedback', '')
    
    if not feedback_text:
        return create_fallback_feedback_context()
    
    # Parse the feedback text to extract different types of feedback
    context_parts = []
    
    # Add the raw feedback
    context_parts.append(f"Client Feedback: {feedback_text}")
    
    # Add context about when this feedback was given
    if airtable_feedback.get('timestamp'):
        context_parts.append(f"Feedback Date: {airtable_feedback['timestamp']}")
    
    if airtable_feedback.get('topic'):
        context_parts.append(f"Related Topic: {airtable_feedback['topic']}")
    
    # Add default preferences that should always be followed
    context_parts.append("Default Preferences: Authentic and conversational tone, Focus on HR consulting challenges, Use 2-3 hashtags maximum, Write 120-180 words, Avoid promotional language")
    
    return "\n\n".join(context_parts)

def create_default_feedback():
    """
    Create comprehensive default feedback for new clients.
    """
    return {
        "tone_preferences": [
            "Authentic and conversational",
            "No overly promotional language",
            "Share real experiences and lessons learned",
            "Be encouraging but not preachy",
            "Use casual, friendly tone",
            "Avoid robotic or formal lingo"
        ],
        "content_preferences": [
            "Focus on HR consulting challenges and solutions",
            "Share behind-the-scenes insights",
            "Include practical tips and actionable advice",
            "Avoid generic motivational content",
            "Use real Reddit insights for authenticity",
            "Focus on specific pain points HR consultants face"
        ],
        "style_preferences": [
            "Use short paragraphs for readability",
            "Include personal stories when relevant",
            "Keep it casual and natural",
            "End with encouragement or reflection",
            "Use 2-3 hashtags maximum",
            "Write 120-180 words"
        ],
        "avoid": [
            "Overly promotional language",
            "Generic motivational quotes",
            "Hard selling or aggressive CTAs",
            "Story format (prefer other content pillars)",
            "Workshop announcements",
            "Free webinar promotions",
            "Join my mastermind calls",
            "Sign up for free sessions"
        ],
        "recent_feedback": [
            "Posts should feel authentic and not AI-generated",
            "Focus on real HR consultant struggles and solutions",
            "Keep the tone conversational and relatable",
            "Avoid making up hypothetical data",
            "Use diversity in opening hooks",
            "Make posts feel like real conversations"
        ],
        "content_pillars": [
            "Pricing & Money Talk",
            "Case Studies",
            "Opinion & Industry Trends",
            "Behind-the-Scenes"
        ],
        "hook_preferences": [
            "Short and compelling",
            "Diverse opening sentences",
            "Avoid repeated phrases like 'ever wondered'",
            "Make hooks feel natural and conversational"
        ]
    }

def create_fallback_feedback_context():
    """
    Create fallback feedback context if everything else fails.
    """
    return """Client Feedback: No specific feedback available yet. Using default preferences.

Default Preferences: Authentic and conversational tone, Focus on HR consulting challenges, Use 2-3 hashtags maximum, Write 120-180 words, Avoid promotional language

Tone: Authentic and conversational, No overly promotional language, Share real experiences and lessons learned, Be encouraging but not preachy, Use casual, friendly tone, Avoid robotic or formal lingo

Content: Focus on HR consulting challenges and solutions, Share behind-the-scenes insights, Include practical tips and actionable advice, Avoid generic motivational content, Use real Reddit insights for authenticity, Focus on specific pain points HR consultants face

Style: Use short paragraphs for readability, Include personal stories when relevant, Keep it casual and natural, End with encouragement or reflection, Use 2-3 hashtags maximum, Write 120-180 words

Avoid: Overly promotional language, Generic motivational quotes, Hard selling or aggressive CTAs, Story format (prefer other content pillars), Workshop announcements, Free webinar promotions, Join my mastermind calls, Sign up for free sessions

Recent feedback: Posts should feel authentic and not AI-generated, Focus on real HR consultant struggles and solutions, Keep the tone conversational and relatable, Avoid making up hypothetical data, Use diversity in opening hooks, Make posts feel like real conversations"""

def format_feedback_context(feedback_data):
    """
    Format feedback data into a readable context string.
    """
    context_parts = []
    
    if "tone_preferences" in feedback_data:
        context_parts.append("Tone: " + ", ".join(feedback_data["tone_preferences"]))
    
    if "content_preferences" in feedback_data:
        context_parts.append("Content: " + ", ".join(feedback_data["content_preferences"]))
    
    if "style_preferences" in feedback_data:
        context_parts.append("Style: " + ", ".join(feedback_data["style_preferences"]))
    
    if "avoid" in feedback_data:
        context_parts.append("Avoid: " + ", ".join(feedback_data["avoid"]))
    
    if "recent_feedback" in feedback_data:
        context_parts.append("Recent feedback: " + ", ".join(feedback_data["recent_feedback"]))
    
    if "hook_preferences" in feedback_data:
        context_parts.append("Hook preferences: " + ", ".join(feedback_data["hook_preferences"]))
    
    return "\n\n".join(context_parts)

def save_feedback_file(client_id, feedback_data):
    """
    Save feedback data to file (for backup purposes).
    """
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        feedback_file = f'data/feedback_{client_id}.json'
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        print(f"✅ Feedback file saved for {client_id}")
        
    except Exception as e:
        print(f"❌ Error saving feedback file: {e}")

def save_feedback(client_id, feedback_type, feedback_text):
    """
    Save new feedback for the client (for backup purposes).
    
    Args:
        client_id: Client identifier
        feedback_type: Type of feedback (tone, content, style, etc.)
        feedback_text: The feedback text
    """
    try:
        feedback_file = f'data/feedback_{client_id}.json'
        
        # Load existing feedback or create new
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                feedback_data = json.load(f)
        else:
            feedback_data = create_default_feedback()
        
        # Add new feedback
        if feedback_type in feedback_data:
            feedback_data[feedback_type].append(feedback_text)
        else:
            feedback_data["recent_feedback"].append(feedback_text)
        
        # Save updated feedback
        save_feedback_file(client_id, feedback_data)
        
    except Exception as e:
        print(f"❌ Error saving feedback: {e}")

def get_client_preferences(client_id="vaishnavi"):
    """
    Get specific client preferences for post generation.
    """
    try:
        # Try Airtable first
        airtable_feedback = get_feedback_from_airtable(client_id)
        if airtable_feedback:
            return airtable_feedback
        
        # Fallback to file
        feedback_file = f'data/feedback_{client_id}.json'
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                return json.load(f)
        return create_default_feedback()
    except Exception as e:
        print(f"Error getting client preferences: {e}")
        return create_default_feedback()

def update_feedback_preferences(client_id, new_preferences):
    """
    Update client feedback preferences (for backup purposes).
    
    Args:
        client_id: Client identifier
        new_preferences: Dictionary of new preferences to update
    """
    try:
        # Get current preferences
        current_preferences = get_client_preferences(client_id)
        
        # Update with new preferences
        for key, value in new_preferences.items():
            if key in current_preferences:
                if isinstance(value, list):
                    current_preferences[key].extend(value)
                else:
                    current_preferences[key] = value
            else:
                current_preferences[key] = value
        
        # Save updated preferences
        save_feedback_file(client_id, current_preferences)
        print(f"✅ Updated feedback preferences for {client_id}")
        
    except Exception as e:
        print(f"❌ Error updating feedback preferences: {e}") 