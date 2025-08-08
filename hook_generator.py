import random
import json
import os
from datetime import datetime

class HookGenerator:
    def __init__(self):
        self.used_hooks_file = "data/used_hooks.json"
        self.load_used_hooks()
        
        # Diverse hook templates organized by style
        self.hook_templates = {
            "question": [
                "Ever wondered why {topic}?",
                "What if I told you {topic}?",
                "Have you ever noticed how {topic}?",
                "Why do so many people struggle with {topic}?",
                "What's the real reason behind {topic}?",
                "How come {topic}?",
                "What if {topic} wasn't what you thought?",
                "Ever asked yourself why {topic}?",
                "What's stopping you from {topic}?",
                "How many times have you wondered about {topic}?"
            ],
            "observation": [
                "Something I've noticed about {topic}...",
                "I've been seeing a pattern with {topic}...",
                "There's something about {topic} that keeps coming up...",
                "I can't help but notice how {topic}...",
                "It's fascinating how {topic}...",
                "Something that keeps happening with {topic}...",
                "I've observed that {topic}...",
                "There's a trend I'm seeing with {topic}...",
                "It's interesting how {topic}...",
                "I keep noticing that {topic}..."
            ],
            "scenario": [
                "Picture this: {topic}...",
                "Imagine you're {topic}...",
                "Here's a scenario: {topic}...",
                "Let's say you're {topic}...",
                "Consider this situation: {topic}...",
                "Think about this: {topic}...",
                "What if you were {topic}...",
                "Envision this: {topic}...",
                "Suppose you're {topic}...",
                "Let me paint you a picture: {topic}..."
            ],
            "statement": [
                "The biggest mistake I see with {topic}...",
                "The truth about {topic} is...",
                "What most people get wrong about {topic}...",
                "The real challenge with {topic}...",
                "The biggest barrier to {topic}...",
                "The most common misconception about {topic}...",
                "The hardest part about {topic}...",
                "The biggest struggle with {topic}...",
                "The real issue with {topic}...",
                "The biggest obstacle to {topic}..."
            ],
            "reflection": [
                "Looking back on my journey with {topic}...",
                "When I think about {topic}...",
                "Reflecting on {topic}...",
                "As I look back on {topic}...",
                "Thinking about {topic}...",
                "When I consider {topic}...",
                "Looking at {topic} now...",
                "As I reflect on {topic}...",
                "When I think back to {topic}...",
                "Considering {topic}..."
            ],
            "challenge": [
                "One of the hardest things about {topic}...",
                "The toughest part of {topic}...",
                "What makes {topic} so challenging...",
                "The biggest struggle with {topic}...",
                "Why {topic} feels impossible...",
                "The most difficult aspect of {topic}...",
                "What's really hard about {topic}...",
                "The challenging reality of {topic}...",
                "Why {topic} is so tough...",
                "The hardest lesson about {topic}..."
            ],
            "realization": [
                "It took me years to realize {topic}...",
                "I finally understood that {topic}...",
                "The moment I realized {topic}...",
                "It dawned on me that {topic}...",
                "I came to understand that {topic}...",
                "The revelation about {topic}...",
                "When I finally figured out {topic}...",
                "The breakthrough moment with {topic}...",
                "It hit me that {topic}...",
                "The epiphany about {topic}..."
            ],
            "memory": [
                "I remember when {topic}...",
                "There was this time when {topic}...",
                "I'll never forget when {topic}...",
                "Back when {topic}...",
                "I can still remember {topic}...",
                "There's this moment when {topic}...",
                "I recall when {topic}...",
                "I remember the day {topic}...",
                "There was this period when {topic}...",
                "I can't forget when {topic}..."
            ],
            "confession": [
                "I have to admit {topic}...",
                "Let me be honest about {topic}...",
                "I need to confess that {topic}...",
                "The truth is {topic}...",
                "I'll be real with you about {topic}...",
                "Let me be transparent about {topic}...",
                "I have to tell you {topic}...",
                "The honest truth about {topic}...",
                "I need to share that {topic}...",
                "Let me be candid about {topic}..."
            ],
            "surprise": [
                "You won't believe what I learned about {topic}...",
                "The surprising truth about {topic}...",
                "What shocked me about {topic}...",
                "The unexpected reality of {topic}...",
                "What I discovered about {topic}...",
                "The revelation about {topic}...",
                "What surprised me most about {topic}...",
                "The unexpected lesson about {topic}...",
                "What I never expected about {topic}...",
                "The shocking truth about {topic}..."
            ]
        }
    
    def load_used_hooks(self):
        """Load the history of used hooks"""
        try:
            if os.path.exists(self.used_hooks_file):
                with open(self.used_hooks_file, 'r') as f:
                    self.used_hooks = json.load(f)
            else:
                self.used_hooks = {"hooks": [], "last_reset": datetime.now().isoformat()}
        except Exception as e:
            print(f"Error loading used hooks: {e}")
            self.used_hooks = {"hooks": [], "last_reset": datetime.now().isoformat()}
    
    def save_used_hooks(self):
        """Save the history of used hooks"""
        try:
            os.makedirs(os.path.dirname(self.used_hooks_file), exist_ok=True)
            with open(self.used_hooks_file, 'w') as f:
                json.dump(self.used_hooks, f, indent=2)
        except Exception as e:
            print(f"Error saving used hooks: {e}")
    
    def reset_if_needed(self):
        """Reset used hooks if it's been more than 30 days"""
        try:
            last_reset = datetime.fromisoformat(self.used_hooks["last_reset"])
            days_since_reset = (datetime.now() - last_reset).days
            
            if days_since_reset > 30:
                print("🔄 Resetting hook history (30+ days old)")
                self.used_hooks = {"hooks": [], "last_reset": datetime.now().isoformat()}
                self.save_used_hooks()
        except Exception as e:
            print(f"Error checking reset: {e}")
    
    def generate_hook(self, topic):
        """Generate a diverse hook for the given topic"""
        self.reset_if_needed()
        
        # Get all available hook styles
        all_styles = list(self.hook_templates.keys())
        
        # Prioritize styles that haven't been used recently
        recent_hooks = self.used_hooks["hooks"][-10:]  # Last 10 hooks
        recent_styles = [hook.get("style") for hook in recent_hooks]
        
        # Find styles that haven't been used recently
        available_styles = [style for style in all_styles if style not in recent_styles]
        
        # If all styles have been used recently, use any style
        if not available_styles:
            available_styles = all_styles
        
        # Choose a random style from available ones
        chosen_style = random.choice(available_styles)
        
        # Get templates for the chosen style
        templates = self.hook_templates[chosen_style]
        
        # Choose a random template
        template = random.choice(templates)
        
        # Format the hook with the topic
        hook = template.format(topic=topic.lower())
        
        # Record this hook usage
        hook_record = {
            "hook": hook,
            "style": chosen_style,
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }
        
        self.used_hooks["hooks"].append(hook_record)
        
        # Keep only last 50 hooks to prevent file from growing too large
        if len(self.used_hooks["hooks"]) > 50:
            self.used_hooks["hooks"] = self.used_hooks["hooks"][-50:]
        
        self.save_used_hooks()
        
        print(f"🎣 Generated {chosen_style} hook: {hook}")
        return hook

# Global instance
hook_generator = HookGenerator()

def get_diverse_hook(topic):
    """Get a diverse hook for the given topic"""
    return hook_generator.generate_hook(topic)

if __name__ == "__main__":
    # Test the hook generator
    test_topics = [
        "pricing your services",
        "getting your first client", 
        "imposter syndrome",
        "time management",
        "building credibility"
    ]
    
    print("🧪 Testing Hook Generator:")
    print("=" * 50)
    
    for topic in test_topics:
        hook = get_diverse_hook(topic)
        print(f"Topic: {topic}")
        print(f"Hook: {hook}")
        print("-" * 30) 