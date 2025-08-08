from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import json
import os
from datetime import datetime
import importlib.util
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
FINE_TUNED_MODEL = config.FINE_TUNED_MODEL

class HookAgent:
    def __init__(self):
        self.used_hooks_file = "data/used_hooks.json"
        self.load_used_hooks()
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name=FINE_TUNED_MODEL,  # Using fine-tuned model for authentic hook generation
            temperature=0.8,  # Higher creativity for hooks
            max_tokens=150
        )
        
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Define tools for the hook agent
        self.tools = [
            Tool(
                name="HookStyleAnalyzer",
                func=self.analyze_hook_style,
                description="Analyzes the topic and determines the best hook style (question, observation, scenario, statement, reflection, challenge, realization, memory, confession, surprise) based on the topic content and emotional tone."
            ),
            Tool(
                name="HookHistoryChecker",
                func=self.check_recent_hooks,
                description="Checks what hook styles have been used recently to avoid repetition. Returns a list of recently used styles to avoid."
            ),
            Tool(
                name="HookGenerator",
                func=self.generate_hook_variation,
                description="Generates a creative hook based on the topic, chosen style, and avoiding recent patterns. Creates engaging, diverse hooks that match the client's tone."
            )
        ]
        
        # Initialize the agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )
    
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
    
    def analyze_hook_style(self, topic):
        """Analyze the topic and determine the best hook style"""
        analysis_prompt = f"""
        Analyze this topic: "{topic}"
        
        Determine the BEST hook style for maximum engagement and impact:
        - question: For topics that create immediate curiosity and make people think
        - observation: For topics where you've noticed powerful patterns or insights
        - scenario: For topics that benefit from vivid storytelling or visualization
        - statement: For topics with bold, controversial, or surprising claims
        - reflection: For topics about deep personal growth or life-changing lessons
        - challenge: For topics about difficult obstacles that create tension
        - realization: For topics about breakthrough moments or epiphanies
        - memory: For topics about powerful, emotional past experiences
        - confession: For topics about raw vulnerabilities or honest truths
        - surprise: For topics with shocking or unexpected revelations
        
        Consider:
        - Which style will create the strongest emotional reaction?
        - Which style will make people stop scrolling and read?
        - Which style will create the most curiosity and engagement?
        - Which style matches the topic's emotional intensity?
        - Which style will make the reader feel something immediately?
        
        Choose the style that will create the MOST POWERFUL opening.
        Return ONLY the style name (e.g., "question", "observation", etc.)
        """
        
        try:
            response = self.llm.predict(analysis_prompt)
            style = response.strip().lower()
            print(f"🎯 Analyzed topic '{topic}' - Best style: {style}")
            return style
        except Exception as e:
            print(f"Error analyzing hook style: {e}")
            return "question"  # Default fallback
    
    def check_recent_hooks(self, topic):
        """Check what hook styles have been used recently"""
        self.reset_if_needed()
        
        recent_hooks = self.used_hooks["hooks"][-10:]  # Last 10 hooks
        recent_styles = [hook.get("style") for hook in recent_hooks]
        
        # Get all available styles
        all_styles = ["question", "observation", "scenario", "statement", "reflection", 
                     "challenge", "realization", "memory", "confession", "surprise"]
        
        # Count recent usage of each style
        style_counts = {}
        for style in recent_styles:
            style_counts[style] = style_counts.get(style, 0) + 1
        
        # If any style has been used 3+ times recently, prioritize other styles
        overused_styles = [style for style, count in style_counts.items() if count >= 3]
        
        # Find styles that haven't been used recently or aren't overused
        available_styles = [style for style in all_styles if style not in overused_styles]
        
        # If all styles are overused, reset and use all styles
        if not available_styles:
            available_styles = all_styles
            print("🔄 All styles overused, resetting to use all styles")
        
        result = {
            "recent_styles": recent_styles,
            "available_styles": available_styles,
            "recent_count": len(recent_styles),
            "overused_styles": overused_styles
        }
        
        print(f"📊 Recent styles used: {recent_styles}")
        print(f"🚫 Overused styles: {overused_styles}")
        print(f"🎯 Available styles: {available_styles}")
        return json.dumps(result)
    
    def generate_hook_variation(self, inputs):
        """Generate a creative hook based on topic, style, and history"""
        try:
            # Parse inputs (topic, style, history)
            if isinstance(inputs, str):
                # Try to parse as JSON, otherwise treat as topic
                try:
                    data = json.loads(inputs)
                    topic = data.get("topic", inputs)
                    style = data.get("style", "question")
                    history = data.get("history", "{}")
                except:
                    topic = inputs
                    style = "question"
                    history = "{}"
            else:
                topic = inputs.get("topic", "HR consulting")
                style = inputs.get("style", "question")
                history = inputs.get("history", "{}")
            
            history_data = json.loads(history) if isinstance(history, str) else history
            
            hook_prompt = f"""
            Generate a SHORT, COMPELLING hook for this topic: "{topic}" in your authentic voice.
            
            Hook style: {style}
            Recent styles to avoid: {history_data.get('recent_styles', [])}
            
            Create a hook that:
            - Is 1 sentence maximum (keep it short and punchy)
            - Matches the {style} style perfectly
            - Is specific to "{topic}"
            - Avoids patterns from recent hooks
            - Creates immediate curiosity and engagement
            - Makes people stop scrolling and read
            - Sounds like your natural, conversational voice
            - NO dashes or hyphens anywhere in the hook
            
            Style guidelines for SHORT, COMPELLING hooks in your voice:
            - question: "What if {topic} isn't what you think?" or "Why do most people fail at {topic}?"
            - observation: "The most successful people with {topic} all do this one thing..."
            - scenario: "Picture this: you're about to {topic} and everything changes..."
            - statement: "The biggest lie about {topic} is..." or "What most people get wrong about {topic}..."
            - reflection: "The moment I truly understood {topic} changed everything..."
            - challenge: "The hardest truth about {topic} is..." or "What makes {topic} so impossible..."
            - realization: "It took me years to realize {topic} isn't about..."
            - memory: "I remember the exact moment {topic} became clear..."
            - confession: "I have to admit something about {topic}..."
            - surprise: "You won't believe what I discovered about {topic}..."
            
            CRITICAL REQUIREMENTS:
            - Keep it SHORT (1 sentence maximum)
            - Make it COMPELLING and curiosity-driven
            - Be SPECIFIC to the topic
            - Use your natural, conversational tone
            - NO dashes or hyphens
            - Use periods, commas, or question marks for punctuation
            
            Return ONLY the hook text, nothing else.
            """
            
            hook = self.llm.invoke(hook_prompt).content.strip()
            
            # Clean up the hook
            if hook.startswith('"') and hook.endswith('"'):
                hook = hook[1:-1]
            
            print(f"🎣 Generated {style} hook: {hook}")
            return hook
            
        except Exception as e:
            print(f"Error generating hook: {e}")
            return f"Ever wondered about {topic}?"
    
    def generate_hook(self, topic):
        """Main method to generate a diverse hook - optimized for speed"""
        print(f"🤖 Hook Agent analyzing topic: {topic}")
        
        try:
            # Quick style selection without complex analysis
            import random
            styles = ["question", "observation", "scenario", "statement", "reflection", "challenge", "realization", "memory", "confession", "surprise"]
            
            # Simple check for recent styles to avoid repetition
            recent_styles = [h.get("style", "") for h in self.used_hooks.get("hooks", [])[-5:]]
            available_styles = [s for s in styles if s not in recent_styles]
            
            if available_styles:
                style = random.choice(available_styles)
            else:
                style = random.choice(styles)
            
            print(f"   🎯 Selected style: {style}")
            
            # Generate hook directly
            hook_inputs = {"topic": topic, "style": style}
            hook = self.generate_hook_variation(hook_inputs)
            
            # Quick record
            hook_record = {
                "hook": hook,
                "style": style,
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            }
            
            self.used_hooks["hooks"].append(hook_record)
            
            # Keep only last 20 hooks for speed
            if len(self.used_hooks["hooks"]) > 20:
                self.used_hooks["hooks"] = self.used_hooks["hooks"][-20:]
            
            self.save_used_hooks()
            
            return hook
            
        except Exception as e:
            print(f"Error with hook agent: {e}")
            print("   Falling back to simple generation...")
            return f"Ever wondered about {topic}?"

# Global instance
hook_agent = HookAgent()

def get_ai_hook(topic):
    """Get an AI-generated hook for the given topic"""
    return hook_agent.generate_hook(topic)

if __name__ == "__main__":
    # Test the hook agent
    test_topics = [
        "pricing your services",
        "getting your first client", 
        "imposter syndrome",
        "time management",
        "building credibility"
    ]
    
    print("🧪 Testing Hook Agent:")
    print("=" * 50)
    
    for topic in test_topics:
        hook = get_ai_hook(topic)
        print(f"Topic: {topic}")
        print(f"AI Hook: {hook}")
        print("-" * 30) 