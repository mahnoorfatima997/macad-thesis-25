# agents/cognitive_enhancement.py - Basic Cognitive Agent
from typing import Dict, Any, List
import os
from openai import OpenAI
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_manager import ArchMentorState

load_dotenv()

class CognitiveEnhancementAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "cognitive_enhancement"
        
        # Challenge types with example question to guide llm
        self.challenge_types = {
            "constraint_changes": [
                "What if your budget was cut by 50%?",
                "How would your design change if the site was half the size?",
                "What if you had to build this in 6 months instead of 2 years?"
            ],
            "perspective_shifts": [
                "How would a child experience your design?",
                "What would someone with mobility challenges think?",
                "How might this work in a different climate?"
            ],
            "alternative_exploration": [
                "What would happen if you approached this completely differently?",
                "Can you think of the opposite solution and why it might work?",
                "What if you had to use entirely different materials?"
            ],
            "metacognitive_prompts": [
                "Can you walk me through your thinking process?",
                "What assumptions are you making that you haven't questioned?",
                "How confident are you in this approach and why?"
            ]
        }
        
        print(f"🧠 {self.name} initialized for domain: {domain}")
    
    async def provide_challenge(self, state: ArchMentorState, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide cognitive challenges based on student state"""
        print(f"\n🧠 {self.name} providing cognitive challenge...")

        challenge_type = self.select_challenge_type(context_analysis, state)
        challenge_response = await self.generate_challenge(challenge_type, state, context_analysis)
        challenge_text = challenge_response.get("challenge", "[No challenge generated]")
        
        return {
            "agent": self.name,
            "challenge_type": challenge_type,
            "challenge_response": challenge_response,  # Keep this for debugging
            "response_text": challenge_text,  # ADD THIS - synthesizer expects this field
            "pedagogical_intent": self.get_challenge_intent(challenge_type),
            "context_used": context_analysis
        }


    # complete assessment logic(below old version with only select_challenge_type):
    def assess_cognitive_state(self, state: ArchMentorState, context: Dict) -> Dict[str, Any]:
        """Implement Section 6 cognitive state assessment"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        # ENGAGEMENT INDICATORS
        engagement = "low"  # default
        if user_messages:
            avg_length = sum(len(msg.split()) for msg in user_messages) / len(user_messages)
            has_questions = any("?" in msg for msg in user_messages[-3:])  # Recent questions
            has_elaboration = any(len(msg.split()) > 20 for msg in user_messages[-2:])  # Recent elaboration
            
            if has_questions and has_elaboration and avg_length > 15:
                engagement = "high"
            elif avg_length > 8 or has_questions:
                engagement = "medium"
        
        # COGNITIVE LOAD INDICATORS
        confusion_signals = ["confused", "don't understand", "unclear", "help me"]
        recent_messages = " ".join(user_messages[-2:]).lower()
        
        if any(signal in recent_messages for signal in confusion_signals):
            cognitive_load = "overloaded"
        elif engagement == "medium" and context.get("word_count", 0) > 10:
            cognitive_load = "optimal"
        else:
            cognitive_load = "underloaded"
        
        # METACOGNITIVE AWARENESS
        metacognitive_indicators = ["thinking", "process", "approach", "strategy", "why", "because"]
        has_metacognition = any(indicator in recent_messages for indicator in metacognitive_indicators)
        
        if has_metacognition and engagement == "high":
            metacognitive_awareness = "high"
        elif has_metacognition:
            metacognitive_awareness = "medium"
        else:
            metacognitive_awareness = "low"
        
        return {
            "engagement": engagement,
            "cognitive_load": cognitive_load,
            "metacognitive_awareness": metacognitive_awareness
        }

    def select_challenge_type(self, context: Dict[str, Any], state: ArchMentorState) -> str:
        """Enhanced selection based on complete cognitive assessment"""
        
        cognitive_state = self.assess_cognitive_state(state, context)
        
        # ENHANCEMENT STRATEGY SELECTION (per document)
        if cognitive_state["engagement"] == "low":
            return "constraint_changes"  # Challenge scenario
        elif cognitive_state["engagement"] == "medium":
            return "metacognitive_prompts"  # Reflection
        elif context.get("confidence_level") == "overconfident":
            return "perspective_shifts"  # Different viewpoints
        elif cognitive_state["metacognitive_awareness"] == "high":
            return "alternative_exploration"  # Advanced challenge
        else:
            return "metacognitive_prompts"  # Default to reflection    
        
    # def select_challenge_type(self, context: Dict[str, Any], state: ArchMentorState) -> str:
    #     """Select appropriate challenge type based on student state"""
        
    #     confidence = context.get("confidence_level", "uncertain")
    #     engagement = context.get("engagement_level", "medium")
    #     understanding = context.get("understanding_level", "medium")
        
    #     # Selection logic from your document
    #     if confidence == "overconfident":
    #         return "perspective_shifts"  # Challenge assumptions
    #     elif engagement == "low":
    #         return "constraint_changes"  # Add interesting constraints
    #     elif understanding == "high":
    #         return "alternative_exploration"  # Push boundaries
    #     else:
    #         return "metacognitive_prompts"  # Encourage reflection
    
    async def generate_challenge(self, challenge_type: str, state: ArchMentorState, context: Dict) -> Dict[str, Any]:
        """Generate contextual cognitive challenge"""
        
        # Get base challenge templates
        base_challenges = self.challenge_types.get(challenge_type, self.challenge_types["metacognitive_prompts"])
        
        # Generate contextual challenge using GPT-4
        challenge_prompt = f"""
        You are a cognitive enhancement agent helping architecture students think deeper.
        
        STUDENT'S PROJECT: {state.current_design_brief}
        CHALLENGE TYPE: {challenge_type}
        STUDENT CONTEXT: {context.get('classification', 'unknown')} with {context.get('confidence_level', 'uncertain')} confidence
        
        BASE CHALLENGE IDEAS: {base_challenges}
        
        Generate ONE specific cognitive challenge that:
        1. Is directly relevant to their project
        2. Challenges their current thinking
        3. Encourages deeper consideration
        4. Is appropriate for their level
        5. Connects to their specific design context
        
        Make it thought-provoking but not overwhelming.
        Response should be 1-2 sentences max.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cognitive enhancement specialist. Generate one specific, contextual challenge question."},
                    {"role": "user", "content": challenge_prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            challenge_text = response.choices[0].message.content.strip()
            
            return {
                "challenge": challenge_text,
                "type": challenge_type,
                "has_challenge": True
            }
            
        except Exception as e:
            print(f"❌ Challenge generation failed: {e}")
            
            # Fallback to template
            import random
            fallback_challenge = random.choice(base_challenges)
            
            return {
                "challenge": fallback_challenge,
                "type": challenge_type,
                "has_challenge": True,
                "fallback": True
            }
    
    def get_challenge_intent(self, challenge_type: str) -> str:
        """Get pedagogical intent for challenge type"""
        
        intents = {
            "constraint_changes": "Force creative problem-solving under new limitations",
            "perspective_shifts": "Challenge assumptions by considering different viewpoints",
            "alternative_exploration": "Encourage exploration of radically different approaches",
            "metacognitive_prompts": "Develop self-awareness of thinking processes"
        }
        
        return intents.get(challenge_type, "Enhance cognitive engagement")
    



# Test the cognitive agent
async def test_cognitive_agent():
    print("🧪 Testing Cognitive Enhancement Agent...")
    
    from state_manager import ArchMentorState, StudentProfile
    
    # Test overconfident student
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    context = {
        "confidence_level": "overconfident",
        "engagement_level": "medium",
        "understanding_level": "medium",
        "classification": "statement"
    }
    
    agent = CognitiveEnhancementAgent("architecture")
    result = await agent.provide_challenge(state, context)
    
    print(f"\n🧠 Cognitive Challenge Results:")
    print(f"   Challenge Type: {result['challenge_type']}")
    print(f"   Intent: {result['pedagogical_intent']}")
    print(f"   Challenge: {result['challenge_response']['challenge']}")
    
    print(f"\n✅ Cognitive Enhancement Agent working!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cognitive_agent())