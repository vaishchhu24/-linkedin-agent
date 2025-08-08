import json
import re

def load_voice_standards():
    """Load the client voice analysis and content generation system."""
    try:
        with open('data/client_voice_analysis.json', 'r') as f:
            voice_analysis = json.load(f)
        with open('data/content_generation_system.json', 'r') as f:
            content_system = json.load(f)
        return voice_analysis, content_system
    except FileNotFoundError:
        print("⚠️ Voice analysis files not found")
        return {}, {}

def check_post_quality(post_text):
    """
    Check if a post meets the client's voice standards.
    
    Args:
        post_text (str): The LinkedIn post to check
        
    Returns:
        dict: Quality check results with issues and suggestions
    """
    voice_analysis, content_system = load_voice_standards()
    
    results = {
        "passes_quality_check": True,
        "issues": [],
        "suggestions": [],
        "score": 100
    }
    
    # Check word count
    word_count = len(post_text.split())
    if word_count > 250:
        results["issues"].append(f"Post too long: {word_count} words (max 250)")
        results["score"] -= 20
    elif word_count < 100:
        results["issues"].append(f"Post too short: {word_count} words (min 100)")
        results["score"] -= 15
    
    # Check hashtag count
    hashtags = re.findall(r'#\w+', post_text)
    if len(hashtags) > 3:
        results["issues"].append(f"Too many hashtags: {len(hashtags)} (max 3)")
        results["score"] -= 25
    elif len(hashtags) == 0:
        results["issues"].append("No hashtags found")
        results["score"] -= 10
    
    # Check for forbidden elements
    forbidden_phrases = [
        "check out this link",
        "see what our clients say",
        "looking to grow",
        "compliance consultant",
        "hrdirector",
        "hrmanager"
    ]
    
    for phrase in forbidden_phrases:
        if phrase.lower() in post_text.lower():
            results["issues"].append(f"Forbidden phrase detected: '{phrase}'")
            results["score"] -= 30
    
    # Check for required elements
    required_elements = {
        "personal_pronouns": ["I", "me", "my", "we", "our"],
        "direct_address": ["you", "your"],
        "story_indicators": ["recently", "worked with", "client", "experience", "story"],
        "pain_points": ["struggle", "challenge", "fear", "terrified", "worried", "overwhelmed"]
    }
    
    missing_elements = []
    for element, keywords in required_elements.items():
        found = any(keyword.lower() in post_text.lower() for keyword in keywords)
        if not found:
            missing_elements.append(element)
    
    if missing_elements:
        results["issues"].append(f"Missing required elements: {', '.join(missing_elements)}")
        results["score"] -= len(missing_elements) * 15
    
    # Check tone indicators
    tone_issues = []
    if "!" in post_text and post_text.count("!") > 2:
        tone_issues.append("Too many exclamation marks")
    
    formal_phrases = ["we are pleased to", "it is our pleasure", "kindly", "please be advised"]
    for phrase in formal_phrases:
        if phrase.lower() in post_text.lower():
            tone_issues.append(f"Too formal: '{phrase}'")
    
    if tone_issues:
        results["issues"].extend(tone_issues)
        results["score"] -= len(tone_issues) * 10
    
    # Generate suggestions
    if len(hashtags) > 3:
        results["suggestions"].append("Remove excess hashtags - keep only 2-3 most relevant")
    
    if word_count > 250:
        results["suggestions"].append("Shorten the post to under 250 words for better engagement")
    
    if not any(keyword.lower() in post_text.lower() for keyword in ["recently", "worked with", "client"]):
        results["suggestions"].append("Add a personal story or client experience")
    
    if not any(keyword.lower() in post_text.lower() for keyword in ["you", "your"]):
        results["suggestions"].append("Address the reader directly with 'you'")
    
    # Determine if post passes
    if results["score"] < 70 or len(results["issues"]) > 3:
        results["passes_quality_check"] = False
    
    return results

def suggest_improvements(post_text):
    """
    Suggest specific improvements for a post.
    
    Args:
        post_text (str): The LinkedIn post to improve
        
    Returns:
        str: Improved version of the post
    """
    # This is a simplified version - in practice, you might want to use AI to rewrite
    suggestions = []
    
    # Check for common issues and suggest fixes
    if "check out this link" in post_text.lower():
        suggestions.append("Replace generic link drop with personal story or experience")
    
    if len(re.findall(r'#\w+', post_text)) > 3:
        suggestions.append("Reduce hashtags to 2-3 most relevant ones")
    
    if len(post_text.split()) > 250:
        suggestions.append("Shorten post to under 250 words")
    
    return suggestions

def validate_post_before_posting(post_text):
    """
    Final validation before posting.
    
    Args:
        post_text (str): The LinkedIn post to validate
        
    Returns:
        bool: True if post should be published, False if it needs revision
    """
    results = check_post_quality(post_text)
    
    print("🔍 Content Quality Check Results:")
    print(f"Score: {results['score']}/100")
    print(f"Passes: {'✅' if results['passes_quality_check'] else '❌'}")
    
    if results['issues']:
        print("\n❌ Issues Found:")
        for issue in results['issues']:
            print(f"  - {issue}")
    
    if results['suggestions']:
        print("\n💡 Suggestions:")
        for suggestion in results['suggestions']:
            print(f"  - {suggestion}")
    
    return results['passes_quality_check']

# Example usage
if __name__ == "__main__":
    # Test with the bad example from the user
    bad_post = """Are you a #hrleader, #hrdirector, #hrmanager or #compliance consultant looking to grow? Check out this link to see what our clients say about us. https://lnkd.in/eJY_vnK #hrconsultants #hrleaders #hrmanagers #hrcommunity"""
    
    print("Testing bad post:")
    validate_post_before_posting(bad_post)
    
    # Test with a good example
    good_post = """I recently worked with an HR director who was terrified of leaving her 'safe' corporate salary. She'd been thinking about consulting for months but couldn't pull the trigger.

Sound familiar?

Here's what changed everything for her: she stopped focusing on what she'd lose and started focusing on what she'd gain. Freedom. Flexibility. The chance to actually make an impact.

Within 8 months, she'd replaced her corporate income and was working with clients she actually enjoyed.

The lesson? Your fear of leaving corporate is valid. But staying stuck because of that fear is optional.

What's really holding you back from making the leap?

#hrconsultants #hrleaders"""
    
    print("\n\nTesting good post:")
    validate_post_before_posting(good_post) 