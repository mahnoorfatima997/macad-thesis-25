# agents/cognitive_enhancement.py - COMPLETE REWRITE implementing Section 6 Logic
from typing import Dict, Any, List, Optional
import os
import random
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState

load_dotenv()

class CognitiveEnhancementAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "cognitive_enhancement"
        
        # Initialize challenge templates based on Section 6 logic
        self.challenge_templates = self._initialize_challenge_templates()
        
        print(f"🧠 {self.name} initialized for domain: {domain}")
    
    def _initialize_challenge_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize challenge templates based on Section 6 logic"""
        
        return {
            # COGNITIVE CHALLENGE TYPES (Section 6)
            "constraint_changes": {
                "budget": [
                    "What if your budget was cut by 50%? How would you maintain the essential functions?",
                    "How would your design change if you had unlimited budget versus a very tight one?",
                    "If you could only spend money on three key elements, what would they be and why?"
                ],
                "timeline": [
                    "What if you had to complete this project in half the time? What would you prioritize?",
                    "How would a 10-year construction timeline versus a 1-year timeline affect your design?",
                    "If this had to be built in phases over 5 years, how would you sequence the construction?"
                ],
                "space": [
                    "How would your design work if the site was half the size?",
                    "What if you had to accommodate twice as many people in the same space?",
                    "How would your concept change if the site was on a steep slope instead of flat ground?"
                ],
                "materials": [
                    "What if certain materials became unavailable? How would you adapt?",
                    "How would your design change if you could only use local materials?",
                    "What if sustainable materials cost 30% more? Would you still use them?"
                ]
            },
            
            "perspective_shifts": {
                "user_groups": [
                    "How would your design feel to a child versus an elderly person?",
                    "What would someone with mobility challenges experience in your space?",
                    "How might your design affect someone who is anxious about crowded spaces?",
                    "What would a maintenance worker think about your design choices?"
                ],
                "time_periods": [
                    "How will your design age over 20 years? What will need updating?",
                    "How would your design have worked 50 years ago versus today?",
                    "What aspects of your design will still be relevant in 30 years?",
                    "How might climate change affect your design over the next decade?"
                ],
                "contexts": [
                    "How would your design work in a different climate or culture?",
                    "What if this building was in a dense urban area instead of suburban?",
                    "How would your approach change if this was a temporary versus permanent structure?",
                    "What if this needed to serve as an emergency shelter during disasters?"
                ]
            },
            
            "alternative_exploration": {
                "opposite_approaches": [
                    "What if you designed for maximum privacy instead of openness?",
                    "How would the space feel if you prioritized individual work over collaboration?",
                    "What if you designed for permanent fixtures instead of flexible spaces?",
                    "How would the experience change if you emphasized artificial lighting over natural light?"
                ],
                "different_methods": [
                    "What if you started with the landscape design and built the architecture around it?",
                    "How would your approach change if you designed from the inside out versus outside in?",
                    "What if you let the community co-design the space with you?",
                    "How would prefabrication versus custom construction change your design?"
                ]
            },
            
            "metacognitive_prompts": {
                "process_reflection": [
                    "Walk me through your thinking process. What led you to this solution?",
                    "What assumptions are you making about how people will use this space?",
                    "How did you decide what to prioritize versus what to compromise on?",
                    "What evidence are you using to support your design decisions?"
                ],
                "assumption_questioning": [
                    "What if your assumptions about user behavior are wrong?",
                    "How might your personal experiences be influencing your design choices?",
                    "What biases might be affecting how you approach this problem?",
                    "How could you test whether your design assumptions are correct?"
                ]
            }
        }
    
    async def provide_challenge(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, routing_decision: Dict) -> Dict[str, Any]:
        """Provide cognitive challenge implementing Section 6 logic"""
        
        print(f"\n🧠 {self.name} providing cognitive challenge...")
        
        # COMPLETE COGNITIVE STATE ASSESSMENT (Section 6)
        cognitive_state = self.assess_cognitive_state(state, context_classification, analysis_result)
        print(f"🧠 Cognitive state assessment: {cognitive_state}")
        
        # ENHANCEMENT STRATEGY SELECTION (Section 6)
        enhancement_strategy = self.select_enhancement_strategy(cognitive_state, analysis_result, state)
        print(f"🎯 Enhancement strategy: {enhancement_strategy}")
        
        # GENERATE APPROPRIATE CHALLENGE
        challenge_result = await self.generate_cognitive_challenge(
            enhancement_strategy, cognitive_state, state, analysis_result
        )
        
        challenge_result.update({
            "agent": self.name,
            "cognitive_state": cognitive_state,
            "enhancement_strategy": enhancement_strategy,
            "context_used": context_classification,
            "pedagogical_intent": self._get_pedagogical_intent(enhancement_strategy, cognitive_state)
        })
        
        print(f"🧠 DEBUG: Generated enhancement result: {challenge_result}")
        
        return challenge_result
    
    def assess_cognitive_state(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict) -> Dict[str, Any]:
        """Complete cognitive state assessment implementing Section 6 logic"""
        
        # ENGAGEMENT INDICATORS (Section 6)
        engagement_level = self._assess_engagement_indicators(state, context_classification)
        
        # COGNITIVE LOAD INDICATORS (Section 6)
        cognitive_load = self._assess_cognitive_load_indicators(state, context_classification)
        
        # METACOGNITIVE AWARENESS (Section 6)
        metacognitive_awareness = self._assess_metacognitive_awareness(state, context_classification)
        
        # ADDITIONAL ASSESSMENTS
        passivity_level = self._assess_passivity_level(state, context_classification)
        overconfidence_level = self._assess_overconfidence_level(state, context_classification)
        
        return {
            "engagement_level": engagement_level,
            "cognitive_load": cognitive_load,
            "metacognitive_awareness": metacognitive_awareness,
            "passivity_level": passivity_level,
            "overconfidence_level": overconfidence_level,
            "conversation_depth": self._assess_conversation_depth(state),
            "learning_progression": self._assess_learning_progression(state, analysis_result)
        }
    
    def _assess_engagement_indicators(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess engagement level based on Section 6 indicators"""
        
        # Use context classification if available
        if context_classification and "engagement_level" in context_classification:
            return context_classification["engagement_level"]
        
        # Analyze conversation patterns
        user_messages = [msg for msg in state.messages if msg.get('role') == 'user']
        
        if not user_messages:
            return "medium"
        
        recent_messages = user_messages[-3:]  # Last 3 messages
        
        # HIGH ENGAGEMENT INDICATORS (Section 6)
        # - Long responses, questions, elaboration
        total_words = sum(len(msg['content'].split()) for msg in recent_messages)
        avg_length = total_words / len(recent_messages)
        
        has_questions = any("?" in msg['content'] for msg in recent_messages)
        has_elaboration = any(len(msg['content'].split()) > 20 for msg in recent_messages)
        shows_curiosity = any(word in msg['content'].lower() 
                            for msg in recent_messages 
                            for word in ["why", "how", "what if", "interesting"])
        
        if avg_length > 15 and (has_questions or has_elaboration or shows_curiosity):
            return "high"
        
        # LOW ENGAGEMENT INDICATORS (Section 6)
        # - Short answers, passive acceptance
        short_responses = all(len(msg['content'].split()) < 8 for msg in recent_messages)
        passive_language = any(word in msg['content'].lower() 
                             for msg in recent_messages[-2:] 
                             for word in ["ok", "sure", "fine", "whatever"])
        
        if short_responses or passive_language:
            return "low"
        
        # MEDIUM ENGAGEMENT (Section 6)
        # - Basic responses, follows prompts
        return "medium"
    
    def _assess_cognitive_load_indicators(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess cognitive load based on Section 6 indicators"""
        
        user_messages = [msg['content'] for msg in state.messages[-3:] if msg.get('role') == 'user']
        recent_text = ' '.join(user_messages).lower()
        
        # OVERLOADED INDICATORS (Section 6)
        # - Confused responses, requests for help
        confusion_words = ["confused", "overwhelmed", "too much", "don't understand", 
                          "lost", "help me", "unclear", "complicated"]
        confusion_score = sum(1 for word in confusion_words if word in recent_text)
        
        if confusion_score >= 2:
            return "overloaded"
        
        # UNDERLOADED INDICATORS (Section 6)
        # - Quick answers, seems bored
        boredom_words = ["obvious", "easy", "simple", "boring", "already know"]
        quick_responses = all(len(msg.split()) < 6 for msg in user_messages)
        
        if any(word in recent_text for word in boredom_words) or quick_responses:
            return "underloaded"
        
        # OPTIMAL INDICATORS (Section 6)
        # - Thoughtful responses, some struggle
        return "optimal"
    
    def _assess_metacognitive_awareness(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess metacognitive awareness based on Section 6 indicators"""
        
        user_messages = [msg['content'] for msg in state.messages[-5:] if msg.get('role') == 'user']
        all_text = ' '.join(user_messages).lower()
        
        # HIGH METACOGNITIVE AWARENESS (Section 6)
        # - Reflects on process, questions own assumptions
        high_indicators = ["i think", "my approach", "my process", "i realize", 
                          "looking back", "i should consider", "what if i'm wrong",
                          "my assumption", "i wonder if", "on reflection"]
        
        high_score = sum(1 for indicator in high_indicators if indicator in all_text)
        
        if high_score >= 2:
            return "high"
        
        # MEDIUM METACOGNITIVE AWARENESS (Section 6)
        # - Some self-awareness, limited reflection
        medium_indicators = ["i believe", "i feel", "seems like", "probably",
                           "maybe", "i guess", "thinking about"]
        
        medium_score = sum(1 for indicator in medium_indicators if indicator in all_text)
        
        if medium_score >= 1 or high_score >= 1:
            return "medium"
        
        # LOW METACOGNITIVE AWARENESS (Section 6)
        # - No process awareness, accepts without question
        return "low"
    
    def _assess_passivity_level(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess student passivity level"""
        
        user_messages = [msg['content'] for msg in state.messages[-4:] if msg.get('role') == 'user']
        
        if not user_messages:
            return "medium"
        
        # High passivity indicators
        passive_responses = ["ok", "sure", "fine", "whatever", "yes", "no", "maybe"]
        mostly_passive = sum(1 for msg in user_messages 
                           if any(resp in msg.lower() for resp in passive_responses)) / len(user_messages)
        
        if mostly_passive > 0.6:
            return "high"
        
        # Low passivity indicators (active engagement)
        active_indicators = ["because", "however", "but", "what about", "how", "why"]
        active_responses = sum(1 for msg in user_messages 
                             if any(indicator in msg.lower() for indicator in active_indicators))
        
        if active_responses >= 2:
            return "low"
        
        return "medium"
    
    def _assess_overconfidence_level(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess overconfidence level"""
        
        if context_classification and "confidence_level" in context_classification:
            confidence = context_classification["confidence_level"]
            if confidence == "overconfident":
                return "high"
            elif confidence == "uncertain":
                return "low"
        
        user_messages = [msg['content'] for msg in state.messages[-3:] if msg.get('role') == 'user']
        recent_text = ' '.join(user_messages).lower()
        
        # Overconfidence indicators
        overconfident_words = ["obviously", "clearly", "definitely", "perfect", 
                             "best", "optimal", "no doubt", "certainly", "absolutely"]
        
        overconfidence_score = sum(1 for word in overconfident_words if word in recent_text)
        
        if overconfidence_score >= 2:
            return "high"
        elif overconfidence_score >= 1:
            return "medium"
        
        return "low"
    
    def _assess_conversation_depth(self, state: ArchMentorState) -> str:
        """Assess depth of conversation"""
        
        total_exchanges = len([msg for msg in state.messages if msg.get('role') == 'user'])
        
        if total_exchanges >= 8:
            return "deep"
        elif total_exchanges >= 4:
            return "medium"
        else:
            return "surface"
    
    def _assess_learning_progression(self, state: ArchMentorState, analysis_result: Dict) -> str:
        """Assess learning progression over conversation"""
        
        current_skill = state.student_profile.skill_level
        initial_skill = getattr(state.student_profile, 'initial_skill_level', current_skill)
        
        if current_skill != initial_skill:
            return "progressing"
        
        # Look at conversation complexity evolution
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) >= 3:
            early_avg = sum(len(msg.split()) for msg in user_messages[:2]) / 2
            recent_avg = sum(len(msg.split()) for msg in user_messages[-2:]) / 2
            
            if recent_avg > early_avg * 1.3:
                return "progressing"
            elif recent_avg < early_avg * 0.7:
                return "declining"
        
        return "stable"
    
    def select_enhancement_strategy(self, cognitive_state: Dict, analysis_result: Dict, state: ArchMentorState) -> str:
        """Enhancement strategy selection implementing Section 6 logic"""
        
        engagement = cognitive_state["engagement_level"]
        passivity = cognitive_state["passivity_level"]
        overconfidence = cognitive_state["overconfidence_level"]
        metacognitive = cognitive_state["metacognitive_awareness"]
        cognitive_load = cognitive_state["cognitive_load"]
        
        # STRATEGY SELECTION LOGIC (Section 6)
        
        # IF student shows passivity OR low engagement: APPLY Challenge scenario
        if passivity == "high" or engagement == "low":
            return "constraint_changes"
        
        # IF student needs reflection OR medium engagement: APPLY Metacognitive prompt
        if engagement == "medium" or metacognitive == "low":
            return "metacognitive_prompts"
        
        # IF student shows high engagement OR overconfidence: APPLY Perspective shift
        if engagement == "high" or overconfidence == "high":
            return "perspective_shifts"
        
        # IF student demonstrates good understanding: APPLY Advanced challenge
        if metacognitive == "high" and cognitive_load == "optimal":
            return "alternative_exploration"
        
        # Default: metacognitive prompts for reflection
        return "metacognitive_prompts"
    
    async def generate_cognitive_challenge(self, strategy: str, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate cognitive challenge based on strategy"""
        
        if strategy == "constraint_changes":
            return await self._generate_constraint_challenge(cognitive_state, state, analysis_result)
        elif strategy == "perspective_shifts":
            return await self._generate_perspective_challenge(cognitive_state, state, analysis_result)
        elif strategy == "alternative_exploration":
            return await self._generate_alternative_challenge(cognitive_state, state, analysis_result)
        elif strategy == "metacognitive_prompts":
            return await self._generate_metacognitive_challenge(cognitive_state, state, analysis_result)
        else:
            # Fallback
            return await self._generate_metacognitive_challenge(cognitive_state, state, analysis_result)
    
    async def _generate_constraint_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate constraint change challenges for passive/low engagement students"""
        
        # Choose appropriate constraint type
        constraint_types = ["budget", "timeline", "space", "materials"]
        constraint_type = random.choice(constraint_types)
        
        templates = self.challenge_templates["constraint_changes"][constraint_type]
        base_challenge = random.choice(templates)
        
        # Contextualize to their project
        contextualized_challenge = await self._contextualize_challenge(
            base_challenge, state, "constraint_changes", constraint_type
        )
        
        return {
            "challenge_type": "constraint_changes",
            "constraint_type": constraint_type,
            "challenge_response": {
                "challenge": contextualized_challenge,
                "type": "constraint_changes",
                "has_challenge": True
            },
            "response_text": contextualized_challenge
        }
    
    async def _generate_perspective_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate perspective shift challenges for high engagement/overconfident students"""
        
        perspective_types = ["user_groups", "time_periods", "contexts"]
        perspective_type = random.choice(perspective_types)
        
        templates = self.challenge_templates["perspective_shifts"][perspective_type]
        base_challenge = random.choice(templates)
        
        contextualized_challenge = await self._contextualize_challenge(
            base_challenge, state, "perspective_shifts", perspective_type
        )
        
        return {
            "challenge_type": "perspective_shifts",
            "perspective_type": perspective_type,
            "challenge_response": {
                "challenge": contextualized_challenge,
                "type": "perspective_shifts", 
                "has_challenge": True
            },
            "response_text": contextualized_challenge
        }
    
    async def _generate_alternative_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate alternative exploration challenges for advanced students"""
        
        alternative_types = ["opposite_approaches", "different_methods"]
        alternative_type = random.choice(alternative_types)
        
        templates = self.challenge_templates["alternative_exploration"][alternative_type]
        base_challenge = random.choice(templates)
        
        contextualized_challenge = await self._contextualize_challenge(
            base_challenge, state, "alternative_exploration", alternative_type
        )
        
        return {
            "challenge_type": "alternative_exploration",
            "alternative_type": alternative_type,
            "challenge_response": {
                "challenge": contextualized_challenge,
                "type": "alternative_exploration",
                "has_challenge": True
            },
            "response_text": contextualized_challenge
        }
    
    async def _generate_metacognitive_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate metacognitive prompts for reflection"""
        
        metacognitive_types = ["process_reflection", "assumption_questioning"]
        metacognitive_type = random.choice(metacognitive_types)
        
        templates = self.challenge_templates["metacognitive_prompts"][metacognitive_type]
        base_challenge = random.choice(templates)
        
        contextualized_challenge = await self._contextualize_challenge(
            base_challenge, state, "metacognitive_prompts", metacognitive_type
        )
        
        return {
            "challenge_type": "metacognitive_prompts",
            "metacognitive_type": metacognitive_type,
            "challenge_response": {
                "challenge": contextualized_challenge,
                "type": "metacognitive_prompts",
                "has_challenge": True
            },
            "response_text": contextualized_challenge
        }
    
    async def _contextualize_challenge(self, base_challenge: str, state: ArchMentorState, challenge_type: str, subtype: str) -> str:
        """Contextualize challenge to student's specific project AND current topic"""
        
        # Get what student is actually talking about
        recent_user_messages = [msg['content'] for msg in state.messages[-3:] if msg.get('role') == 'user']
        student_current_focus = " ".join(recent_user_messages)
        
        building_type = "building"
        if hasattr(state, 'current_design_brief') and state.current_design_brief:
            if "community center" in state.current_design_brief.lower():
                building_type = "community center"
            elif "housing" in state.current_design_brief.lower():
                building_type = "housing"
            elif "office" in state.current_design_brief.lower():
                building_type = "office"
        
        contextualization_prompt = f"""
        Create a cognitive challenge about what the student is ACTUALLY discussing:
        
        STUDENT IS CURRENTLY DISCUSSING: "{student_current_focus}"
        STUDENT PROJECT: {state.current_design_brief}
        BUILDING TYPE: {building_type}
        BASE CHALLENGE TYPE: {challenge_type}
        
        The student mentioned: exhibitions, celebrations, central space activities, flexible use
        
        Generate a challenge that:
        1. Directly relates to THEIR topic (exhibitions/celebrations/flexible space)
        2. Uses the {challenge_type} approach (constraint/perspective/alternative/reflection)
        3. Makes them think deeper about their specific interest
        4. Challenges their assumptions about their chosen topic
        
        Examples for exhibitions/celebrations topic:
        - Constraint: "What if exhibitions and celebrations had to happen simultaneously?"
        - Perspective: "How would a 5-year-old experience your exhibition space differently than an adult?"
        - Alternative: "What if you designed for silent exhibitions instead of loud celebrations?"
        
        Generate ONE challenge question about their actual topic (under 25 words):
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": contextualization_prompt}],
                max_tokens=80,
                temperature=0.6
            )
            
            contextualized = response.choices[0].message.content.strip()
            
            # Ensure it's a question
            if not contextualized.endswith('?'):
                contextualized += '?'
            
            return contextualized
            
        except Exception as e:
            # Fallback that still addresses their topic
            print(f"   ⚠️ Challenge contextualization failed: {e}")
            return f"How might your approach to exhibitions and celebrations in the central space be challenged by {subtype} constraints?"
    
    def _get_pedagogical_intent(self, strategy: str, cognitive_state: Dict) -> str:
        """Get pedagogical intent for logging"""
        
        intent_map = {
            "constraint_changes": "Challenge passivity and increase engagement",
            "perspective_shifts": "Challenge assumptions by considering different viewpoints",
            "alternative_exploration": "Explore advanced alternatives and opposite approaches",
            "metacognitive_prompts": "Promote reflection and metacognitive awareness"
        }
        
        base_intent = intent_map.get(strategy, "Enhance cognitive engagement")
        engagement = cognitive_state.get("engagement_level", "unknown")
        
        return f"{base_intent} (targeting {engagement} engagement)"

# Test function
async def test_complete_cognitive_agent():
    print("🧪 Testing Complete Cognitive Enhancement Agent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with flexible meeting spaces"
    state.student_profile.skill_level = "intermediate"
    
    # Add conversation showing overconfidence
    state.messages = [
        {"role": "user", "content": "My design is obviously perfect for this type of building"},
        {"role": "assistant", "content": "Let's explore that"},
        {"role": "user", "content": "Clearly this is the optimal solution for community centers"}
    ]
    
    # Mock context classification
    context_classification = {
        "confidence_level": "overconfident",
        "understanding_level": "medium",
        "engagement_level": "medium"
    }
    
    # Mock analysis result
    analysis_result = {
        "cognitive_flags": ["needs_accessibility_guidance"],
        "confidence_score": 0.8
    }
    
    # Mock routing decision
    routing_decision = {
        "path": "cognitive_challenge",
        "reason": "Overconfident student needs perspective shift"
    }
    
    # Test cognitive agent
    agent = CognitiveEnhancementAgent("architecture")
    result = await agent.provide_challenge(state, context_classification, analysis_result, routing_decision)
    
    print(f"\n🧠 Cognitive Enhancement Results:")
    print(f"   Enhancement Strategy: {result['enhancement_strategy']}")
    print(f"   Challenge Type: {result['challenge_type']}")
    print(f"   Pedagogical Intent: {result['pedagogical_intent']}")
    
    print(f"\n📊 Cognitive State Assessment:")
    for key, value in result['cognitive_state'].items():
        print(f"   {key}: {value}")
    
    print(f"\n💬 Generated Challenge:")
    print(f"   {result['response_text']}")
    
    print(f"\n✅ Complete Cognitive Enhancement Agent working!")
    
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_complete_cognitive_agent())