# agents/socratic_tutor.py - Sophisticated Socratic Tutoring Implementation
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

class SocraticTutorAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "socratic_tutor"
        print(f"🤔 {self.name} initialized for domain: {domain}")
    
    #3107 ADDED DOMAIN EXPERT RESULT ONLY
    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any], context_classification: Optional[Dict] = None, domain_expert_result: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate sophisticated Socratic responses with advanced analysis"""
        
        print(f"\n🤔 {self.name} generating sophisticated Socratic response...")
        
        # Get user's last input
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        if not last_message:
            return self._generate_fallback_response()
        
        # 0208 UPDATED: Check if this is a first-time interaction or early in conversation
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        is_early_conversation = len(user_messages) <= 2
        
        # Advanced analysis of student state
        student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
        conversation_progression = self._analyze_conversation_progression(state, last_message)
        student_insights = self._extract_student_insights(state, last_message)
        
        # 3107-BELOW LINE: Check if we have domain expert results (examples) to ask questions about
        # 0108 added before: has_examples = domain_expert_result and domain_expert_result.get("response_text", "")Only consider it has examples if it's not a cognitive protection response
        has_examples = (domain_expert_result and 
                       domain_expert_result.get("response_text", "") and 
                       domain_expert_result.get("response_type") != "cognitive_protection_response")
        
        # Determine response strategy based on analysis
        response_strategy = self._determine_response_strategy(student_analysis, conversation_progression)
        
        print(f"📊 Student Analysis: {student_analysis}")
        print(f"🔄 Conversation Stage: {conversation_progression['stage']}")
        print(f"💡 Student Insights: {student_insights['key_insights']}")
        print(f"🎯 Response Strategy: {response_strategy}")
        
        # 0208 UPDATED: For early conversations, prioritize clarification over detailed examples
        if is_early_conversation and not has_examples:
            print("🆕 Early conversation detected - providing clarifying guidance")
            response_result = await self._generate_clarifying_guidance(state, student_analysis, conversation_progression)
        # 3107-BEFORE IT WAS if response_strategy == "clarifying_guidance": Generate response based on strategy, with special handling for examples
        elif has_examples:
            # If we have examples from domain expert, ask questions about them
            print("📚 Domain expert provided examples - generating questions about those examples")
            response_result = await self._generate_example_based_question(state, student_analysis, conversation_progression, domain_expert_result)
        elif response_strategy == "clarifying_guidance":
            response_result = await self._generate_clarifying_guidance(state, student_analysis, conversation_progression)
        elif response_strategy == "supportive_guidance":
            response_result = await self._generate_supportive_guidance(state, student_analysis, conversation_progression)
        elif response_strategy == "challenging_question":
            response_result = await self._generate_challenging_question(state, student_analysis, conversation_progression)
        elif response_strategy == "exploratory_question":
            response_result = await self._generate_exploratory_question(state, student_analysis, conversation_progression)
        elif response_strategy == "assumption_challenge":
            response_result = await self._generate_assumption_challenge(state, student_analysis, conversation_progression)
        elif response_strategy == "depth_promotion":
            response_result = await self._generate_depth_promotion(state, student_analysis, conversation_progression)
        else:
            response_result = await self._generate_adaptive_question(state, student_analysis, conversation_progression, response_strategy)
        
        # Add analysis metadata
        response_result.update({
            "agent": self.name,
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression,
            "student_insights": student_insights,
            "response_strategy": response_strategy,
            "educational_intent": self._get_educational_intent(response_strategy, student_analysis)
        })
        
        return response_result
    
    def _analyze_student_state(self, state: ArchMentorState, analysis_result: Dict, context_classification: Optional[Dict]) -> Dict[str, Any]:
        """Analyze student's current learning state and confidence"""
        
        # Get confidence and understanding from context classification
        confidence_level = context_classification.get("confidence_level", "confident") if context_classification else "confident"
        understanding_level = context_classification.get("understanding_level", "medium") if context_classification else "medium"
        engagement_level = context_classification.get("engagement_level", "medium") if context_classification else "medium"
        
        # Analyze conversation patterns
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        total_messages = len(user_messages)
        
        # Detect confusion indicators
        confusion_indicators = ["confused", "don't understand", "not sure", "unclear", "help", "what do you mean"]
        shows_confusion = any(indicator in " ".join(user_messages).lower() for indicator in confusion_indicators)
        
        # Detect overconfidence indicators
        overconfidence_indicators = ["obviously", "clearly", "definitely", "absolutely", "perfect", "best"]
        shows_overconfidence = any(indicator in " ".join(user_messages).lower() for indicator in overconfidence_indicators)
        
        # Analyze question complexity
        avg_question_length = sum(len(msg.split()) for msg in user_messages) / max(len(user_messages), 1)
        question_complexity = "simple" if avg_question_length < 8 else "moderate" if avg_question_length < 15 else "complex"
        
        return {
            "confidence_level": confidence_level,
            "understanding_level": understanding_level,
            "engagement_level": engagement_level,
            "shows_confusion": shows_confusion,
            "shows_overconfidence": shows_overconfidence,
            "question_complexity": question_complexity,
            "total_messages": total_messages,
            "learning_progression": self._assess_learning_progression(state)
        }
    
    def _analyze_conversation_progression(self, state: ArchMentorState, current_message: str) -> Dict[str, Any]:
        """Analyze the progression of the conversation"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) <= 1:
            stage = "initial"
            progression_summary = "First interaction"
        elif len(user_messages) <= 3:
            stage = "exploration"
            progression_summary = "Exploring initial concepts"
        elif len(user_messages) <= 6:
            stage = "deepening"
            progression_summary = "Diving deeper into specific topics"
        else:
            stage = "advanced"
            progression_summary = "Advanced discussion and synthesis"
        
        # Analyze topic evolution
        topic_evolution = self._analyze_topic_evolution(user_messages)
        
        # Detect conversation patterns
        patterns = {
            "seeking_clarification": any("what do you mean" in msg.lower() or "can you explain" in msg.lower() for msg in user_messages[-3:]),
            "requesting_examples": any("example" in msg.lower() or "show me" in msg.lower() for msg in user_messages[-3:]),
            "seeking_feedback": any("feedback" in msg.lower() or "review" in msg.lower() for msg in user_messages[-3:]),
            "exploring_alternatives": any("alternative" in msg.lower() or "different" in msg.lower() for msg in user_messages[-3:])
        }
        
        return {
            "stage": stage,
            "progression_summary": progression_summary,
            "topic_evolution": topic_evolution,
            "patterns": patterns,
            "message_count": len(user_messages)
        }
    
    def _extract_student_insights(self, state: ArchMentorState, current_message: str) -> Dict[str, Any]:
        """Extract key insights from student's responses"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        # Use AI to extract insights
        prompt = f"""
        Analyze these architecture student messages and extract key insights about their understanding and approach:
        
        MESSAGES: {user_messages}
        CURRENT MESSAGE: "{current_message}"
        
        Extract:
        1. Key insights about their design thinking
        2. Areas where they show understanding
        3. Potential misconceptions or gaps
        4. Their design priorities and values
        5. Learning style indicators
        
        Return as a structured analysis.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            insights_analysis = response.choices[0].message.content.strip()
            
            return {
                "key_insights": insights_analysis,
                "message_count": len(user_messages),
                "current_focus": self._identify_current_focus(current_message)
            }
            
        except Exception as e:
            print(f"⚠️ Insight extraction failed: {e}")
            return {
                "key_insights": "Unable to extract insights",
                "message_count": len(user_messages),
                "current_focus": "general inquiry"
            }
    
    def _determine_response_strategy(self, student_analysis: Dict, conversation_progression: Dict) -> str:
        """Enhanced response strategy determination with cognitive protection focus"""
        
        # COGNITIVE OFFLOADING PROTECTION
        if student_analysis.get("shows_overconfidence") and student_analysis.get("engagement_level") == "low":
            return "assumption_challenge"  # Challenge superficial confidence
        
        if student_analysis.get("question_complexity") == "simple" and conversation_progression.get("stage") == "deepening":
            return "depth_promotion"  # Push for deeper thinking
        
        if student_analysis.get("shows_confusion"):
            return "clarifying_guidance"  # Build understanding
        
        # STANDARD SOCRATIC STRATEGIES
        if student_analysis.get("confidence_level") == "uncertain":
            return "supportive_guidance"  # Build confidence
        
        if student_analysis.get("engagement_level") == "high":
            return "exploratory_question"  # Leverage engagement
        
        if conversation_progression.get("stage") == "initial":
            return "foundational_question"  # Start with basics
        
        return "adaptive_question"  # Default adaptive approach
    
    async def _generate_clarifying_guidance(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate clarifying guidance that builds understanding without giving answers"""
        
        building_type = self._extract_building_type_from_context(state)
        
        # Get the user's last message to understand what they're asking about
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        # Extract the main topic the user is asking about
        main_topic = self._extract_main_topic(last_message)
        
        # Check if user has already specified a focus area within that topic
        user_specified_focus = self._extract_user_specified_focus(last_message)
        
        # If user has already specified a focus, move to the next level of exploration
        if user_specified_focus:
            response_text = self._generate_focused_exploration_question(user_specified_focus, building_type, main_topic)
        else:
            # Generate dynamic topic-specific guidance
            response_text = self._generate_dynamic_topic_guidance(main_topic, building_type, last_message)
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "clarifying_guidance",
            "educational_intent": "build_understanding",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }
    
    async def _generate_supportive_guidance(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate supportive guidance for students with low understanding"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        The student has low understanding and needs supportive guidance. Provide encouraging, educational guidance.
        
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Provide supportive guidance that:
        1. Encourages their learning journey
        2. Provides foundational knowledge
        3. Builds their confidence
        4. Guides them to the next step
        5. Is encouraging and educational
        
        Give supportive guidance:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.4
            )
            
            supportive_response = response.choices[0].message.content.strip()
            
            return {
                "response_text": supportive_response,
                "response_type": "supportive_guidance",
                "user_input_addressed": "learning_support"
            }
            
        except Exception as e:
            print(f"⚠️ Supportive guidance generation failed: {e}")
            return {
                "response_text": "Great question! Let's build on this step by step. What aspect would you like to explore first?",
                "response_type": "supportive_guidance",
                "user_input_addressed": "learning_support"
            }
    
    async def _generate_challenging_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate challenging questions for confident students"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        The student shows confidence and understanding. Generate a challenging question that pushes their thinking deeper.
        
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Generate a challenging question that:
        1. Challenges their assumptions
        2. Forces them to consider trade-offs
        3. Pushes them to justify their choices
        4. Makes them think about implications
        5. Is direct and thought-provoking
        
        Ask ONE challenging question:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.3
            )
            
            challenging_question = response.choices[0].message.content.strip()
            
            if not challenging_question.endswith('?'):
                challenging_question += '?'
            
            return {
                "response_text": challenging_question,
                "response_type": "challenging_question",
                "user_input_addressed": "critical_thinking"
            }
            
        except Exception as e:
            print(f"⚠️ Challenging question generation failed: {e}")
            return {
                "response_text": "What assumptions are you making about this design decision that might need to be questioned?",
                "response_type": "challenging_question",
                "user_input_addressed": "critical_thinking"
            }
    
    async def _generate_exploratory_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate exploratory questions for students in exploration stage"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        The student is in exploration stage. Generate an exploratory question that opens up new avenues of thinking.
        
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Generate an exploratory question that:
        1. Opens up new possibilities
        2. Encourages creative thinking
        3. Explores different approaches
        4. Guides discovery
        5. Is open-ended and inspiring
        
        Ask ONE exploratory question:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.4
            )
            
            exploratory_question = response.choices[0].message.content.strip()
            
            if not exploratory_question.endswith('?'):
                exploratory_question += '?'
            
            return {
                "response_text": exploratory_question,
                "response_type": "exploratory_question",
                "user_input_addressed": "exploration"
            }
            
        except Exception as e:
            print(f"⚠️ Exploratory question generation failed: {e}")
            return {
                "response_text": "What other approaches could you consider for this aspect of your design?",
                "response_type": "exploratory_question",
                "user_input_addressed": "exploration"
            }
    
    async def _generate_adaptive_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict, strategy: str) -> Dict[str, Any]:
        """Generate adaptive questions based on specific strategy"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        Generate an adaptive question based on the specific strategy and student analysis.
        
        STRATEGY: {strategy}
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Generate a question that adapts to the student's current needs and learning stage.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.3
            )
            
            adaptive_question = response.choices[0].message.content.strip()
            
            if not adaptive_question.endswith('?'):
                adaptive_question += '?'
            
            return {
                "response_text": adaptive_question,
                "response_type": "adaptive_question",
                "user_input_addressed": "adaptive_guidance"
            }
            
        except Exception as e:
            print(f"⚠️ Adaptive question generation failed: {e}")
            return {
                "response_text": "How does this relate to your overall design goals?",
                "response_type": "adaptive_question",
                "user_input_addressed": "adaptive_guidance"
            }
    
    async def _generate_assumption_challenge(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Challenge assumptions to prevent superficial confidence"""
        
        building_type = self._extract_building_type_from_context(state)
        
        response_text = f"""
**🧠 Let's examine your assumptions**

I notice you're expressing confidence, but let's make sure it's built on solid reasoning.

**Let's challenge your thinking:**

1. **What evidence supports your current approach?** (Not just opinions, but concrete reasons)

2. **What are the potential weaknesses in your reasoning?** (Every design has trade-offs - what are yours?)

3. **How would you defend this to a skeptical critic?** (Imagine someone questioning every decision)

4. **What alternatives have you considered and rejected?** (Why did you choose this path over others?)

**The goal isn't to undermine your confidence, but to strengthen it through rigorous thinking.**

*Which of these questions feels most challenging to answer?*
"""
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "assumption_challenge",
            "educational_intent": "challenge_assumptions",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }
    
    async def _generate_depth_promotion(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Promote deeper thinking when responses are too superficial"""
        
        building_type = self._extract_building_type_from_context(state)
        
        response_text = f"""
**🔍 Let's go deeper**

I sense you might be scratching the surface of this problem. Let's explore the layers beneath.

**Let's dive deeper:**

1. **What's the underlying principle driving your design decisions?** (Not just "it looks good" but the fundamental reasoning)

2. **How does your design respond to the specific context?** (What makes this solution right for this particular situation?)

3. **What are the long-term implications of your choices?** (How will this design perform over time?)

4. **What would happen if you took the opposite approach?** (Sometimes the best way to understand your choice is to consider its opposite)

**Deep thinking creates lasting understanding. Let's build that together.**

*Which of these deeper questions resonates most with your current thinking?*
"""
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "depth_promotion",
            "educational_intent": "promote_deep_thinking",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }
    
    def _assess_learning_progression(self, state: ArchMentorState) -> str:
        """Assess the student's learning progression"""
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) <= 2:
            return "beginning"
        elif len(user_messages) <= 5:
            return "developing"
        elif len(user_messages) <= 8:
            return "intermediate"
        else:
            return "advanced"
    
    def _analyze_topic_evolution(self, user_messages: List[str]) -> Dict[str, Any]:
        """Analyze how topics have evolved in the conversation"""
        if len(user_messages) < 2:
            return {"evolution": "single_topic", "topics": ["initial"]}
        
        # Simple topic analysis
        topics = []
        for msg in user_messages:
            if any(word in msg.lower() for word in ["light", "window", "glazing"]):
                topics.append("environmental")
            elif any(word in msg.lower() for word in ["circulation", "flow", "movement"]):
                topics.append("circulation")
            elif any(word in msg.lower() for word in ["material", "construction", "structure"]):
                topics.append("materials")
            else:
                topics.append("general")
        
        return {
            "evolution": "topic_progression" if len(set(topics)) > 1 else "focused_discussion",
            "topics": topics,
            "topic_count": len(set(topics))
        }
    
    def _identify_current_focus(self, current_message: str) -> str:
        """Identify the current focus of the student's message"""
        if any(word in current_message.lower() for word in ["light", "window", "glazing"]):
            return "environmental_design"
        elif any(word in current_message.lower() for word in ["circulation", "flow", "movement"]):
            return "circulation_design"
        elif any(word in current_message.lower() for word in ["material", "construction", "structure"]):
            return "materials_and_construction"
        else:
            return "general_design"
    
    def _get_educational_intent(self, strategy: str, student_analysis: Dict) -> str:
        """Get the educational intent of the response strategy"""
        intents = {
            "clarifying_guidance": "Clarify confusion and build understanding",
            "supportive_guidance": "Support learning and build confidence",
            "challenging_question": "Challenge assumptions and promote critical thinking",
            "exploratory_question": "Encourage exploration and creative thinking",
            "adaptive_question": "Adapt to student's current learning needs"
        }
        return intents.get(strategy, "Guide student learning")
    
    def _generate_fallback_response(self, user_input: str = "", building_type: str = "project") -> Dict[str, Any]:
        """Generate a fallback Socratic question when AI fails"""
        
        if not user_input:
            return {
                "agent": self.name,
                "response_text": "What specific aspect of your design would you like to explore further?",
                "response_type": "fallback_socratic",
                "educational_intent": "Encourage specific exploration",
                "user_input_addressed": "general inquiry"
            }
        
        # Simple template-based fallback
        fallback_questions = [
            f"What specific challenges do you anticipate with {user_input.lower()} in your {building_type}?",
            f"How do you think {user_input.lower()} will impact the overall design of your {building_type}?",
            f"What factors would you consider when implementing {user_input.lower()} in your {building_type}?",
            f"How might {user_input.lower()} affect the user experience in your {building_type}?"
        ]
        
        return {
            "agent": self.name,
            "response_text": random.choice(fallback_questions),
            "response_type": "fallback_socratic",
            "educational_intent": "Guide exploration of specific design aspect",
            "user_input_addressed": user_input[:50] + "..." if len(user_input) > 50 else user_input
        }
    #3107-FULL DEFITINIO ADDED FOR EXAMPLE BASED QUESTION  
    async def _generate_example_based_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict, domain_expert_result: Dict) -> Dict[str, Any]:
        """Generate Socratic questions specifically about the examples that were just provided - Enhanced for deeper probing"""
        
        building_type = self._extract_building_type_from_context(state)
        examples_text = domain_expert_result.get("response_text", "")
        
        # Extract the specific topic being discussed
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_user_message = user_messages[-1] if user_messages else ""
        
        # Determine the level of probing needed based on student state
        confidence_level = student_analysis.get("confidence_level", "confident")
        understanding_level = student_analysis.get("understanding_level", "medium")
        
        if confidence_level == "overconfident":
            question_strategy = "challenge_assumptions"
        elif confidence_level == "uncertain":
            question_strategy = "build_confidence"
        elif understanding_level == "low":
            question_strategy = "clarify_understanding"
        else:
            question_strategy = "deepen_analysis"
        
        prompt = f"""
        The Domain Expert just provided these examples to the student:
        
        {examples_text}
        
        STUDENT'S LAST MESSAGE: "{last_user_message}"
        BUILDING TYPE: {building_type}
        STUDENT CONFIDENCE: {confidence_level}
        STUDENT UNDERSTANDING: {understanding_level}
        QUESTION STRATEGY: {question_strategy}
        
        Generate ONE specific Socratic question that:
        1. References the specific examples that were just provided
        2. Uses the {question_strategy} approach to probe deeper thinking
        3. Encourages critical analysis of those examples
        4. Prompts them to consider how principles apply to their own design
        5. Is specific to the examples provided, not generic
        6. Builds on their current understanding level
        
        QUESTION STRATEGIES:
        - challenge_assumptions: "What assumptions underlie [specific example]? How might those assumptions not apply to your context?"
        - build_confidence: "What aspects of [specific example] do you find most compelling for your project? Why?"
        - clarify_understanding: "Can you explain how [specific example] addresses [specific challenge]? What makes it effective?"
        - deepen_analysis: "Looking at [specific example], what underlying principles do you see that could inform your approach?"
        
        Generate ONE targeted question using the {question_strategy} approach:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.3
            )
            
            example_question = response.choices[0].message.content.strip()
            
            if not example_question.endswith('?'):
                example_question += '?'
            
            return {
                "response_text": example_question,
                "response_type": "example_based_question",
                "user_input_addressed": "critical_analysis_of_examples",
                "examples_referenced": True,
                "question_strategy": question_strategy,
                "probing_depth": "deep"
            }
            
        except Exception as e:
            print(f"⚠️ Example-based question generation failed: {e}")
            return {
                "response_text": "Looking at these examples, what specific aspects do you think would be most relevant to your own design approach, and why?",
                "response_type": "example_based_question",
                "user_input_addressed": "critical_analysis_of_examples",
                "examples_referenced": True,
                "question_strategy": "deepen_analysis",
                "probing_depth": "deep"
            }

    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type from the current design brief"""
        if not state.current_design_brief:
            return "project"
        
        # Simple extraction - look for building type in the brief
        brief_words = state.current_design_brief.lower().split()
        building_types = ["museum", "library", "school", "hospital", "office", "residential", "commercial", "community", "center"]
        
        for word in brief_words:
            if word in building_types:
                return word
        
        return "project"
    
    def _extract_main_topic(self, last_message: str) -> str:
        """Extract the main architectural topic the user is asking about"""
        message_lower = last_message.lower()
        
        # Common architectural topics - this is just for context, not hardcoding responses
        architectural_topics = [
            "adaptive reuse", "sustainability", "lighting", "acoustics", "circulation", 
            "materials", "structure", "accessibility", "energy efficiency", "ventilation",
            "thermal comfort", "daylighting", "spatial organization", "programming",
            "site planning", "landscape", "interior design", "facade design", "construction",
            "building codes", "fire safety", "mechanical systems", "electrical systems",
            "plumbing", "roofing", "foundations", "seismic design", "wind loads",
            "architectural history", "urban design", "placemaking", "community engagement"
        ]
        
        # Find the most relevant topic mentioned
        for topic in architectural_topics:
            if topic in message_lower:
                return topic
        
        # If no specific topic found, extract from context
        words = message_lower.split()
        if "principles" in words:
            # Look for the word before "principles"
            for i, word in enumerate(words):
                if word == "principles" and i > 0:
                    return words[i-1]
        
        # Default to a general architectural inquiry
        return "architectural design"
    
    def _extract_user_specified_focus(self, last_message: str) -> str:
        """Extract what focus area the user has already specified within a topic"""
        message_lower = last_message.lower()
        
        # Generic focus areas that apply to any architectural topic
        focus_indicators = {
            "principles": "principles",
            "examples": "examples", 
            "process": "process",
            "technical": "technical_details",
            "challenges": "challenges",
            "strategies": "strategies",
            "considerations": "considerations",
            "requirements": "requirements",
            "standards": "standards",
            "best practices": "best_practices",
            "approaches": "approaches",
            "methods": "methods",
            "techniques": "techniques",
            "solutions": "solutions",
            "applications": "applications"
        }
        
        # Check for focus indicators
        for indicator, focus_type in focus_indicators.items():
            if indicator in message_lower:
                return focus_type
        
        return ""
    
    def _generate_focused_exploration_question(self, focus_area: str, building_type: str, main_topic: str) -> str:
        """Generate a focused exploration question based on user's specified focus and topic"""
        
        # Dynamic focus questions that work for any architectural topic
        focus_questions = {
            "principles": f"""
**🏗️ {main_topic.title()} Principles - Deep Dive**

Excellent choice! Understanding the principles of {main_topic} is crucial for successful {building_type} projects. Let's explore this systematically:

**What specific aspect of {main_topic} principles would you like to explore first?**

1. **Core concepts** - The fundamental ideas that guide {main_topic} decisions
2. **Application strategies** - How to apply {main_topic} principles in practice
3. **Design integration** - How {main_topic} principles relate to overall design
4. **Performance considerations** - How {main_topic} principles affect building performance
5. **User experience impact** - How {main_topic} principles influence occupant experience

**Or is there a particular challenge you're facing with {main_topic} in your {building_type} project?**

*What aspect of {main_topic} principles feels most relevant to your current design stage?*
""",
            "examples": f"""
**🏗️ {main_topic.title()} Examples - Deep Dive**

Great focus! Learning from real examples of {main_topic} can provide valuable insights for your {building_type} project. Let's explore this systematically:

**What type of {main_topic} examples would be most helpful?**

1. **Successful case studies** - Projects that demonstrate excellent {main_topic} implementation
2. **Innovative approaches** - Creative and unique {main_topic} solutions
3. **Problem-solving examples** - How {main_topic} challenges were overcome
4. **Similar project types** - {main_topic} examples from {building_type} projects
5. **Contemporary applications** - Modern approaches to {main_topic}

**Or is there a specific {main_topic} challenge you're trying to solve in your project?**

*What type of {main_topic} examples would be most relevant to your current design stage?*
""",
            "process": f"""
**🏗️ {main_topic.title()} Process - Deep Dive**

Excellent choice! Understanding the process of implementing {main_topic} is essential for your {building_type} project. Let's explore this systematically:

**What aspect of the {main_topic} process would you like to explore first?**

1. **Planning phase** - How to approach {main_topic} from the beginning
2. **Design integration** - How to incorporate {main_topic} into your design process
3. **Implementation steps** - The practical steps for {main_topic} execution
4. **Evaluation methods** - How to assess {main_topic} effectiveness
5. **Iteration and refinement** - How to improve {main_topic} solutions over time

**Or is there a particular stage in the {main_topic} process where you need guidance?**

*What aspect of the {main_topic} process feels most relevant to your current design stage?*
""",
            "technical_details": f"""
**🏗️ {main_topic.title()} Technical Details - Deep Dive**

Great focus! Technical understanding of {main_topic} is crucial for successful {building_type} projects. Let's explore this systematically:

**What specific technical aspect of {main_topic} would you like to explore first?**

1. **Specifications and standards** - Technical requirements for {main_topic}
2. **Material and system selection** - Choosing appropriate {main_topic} solutions
3. **Integration with other systems** - How {main_topic} works with building systems
4. **Performance metrics** - How to measure {main_topic} effectiveness
5. **Code compliance** - Regulatory requirements for {main_topic}

**Or is there a particular technical challenge you're facing with {main_topic} in your project?**

*What technical aspect of {main_topic} feels most relevant to your current design stage?*
""",
            "challenges": f"""
**🏗️ {main_topic.title()} Challenges - Deep Dive**

Excellent choice! Understanding the challenges of {main_topic} will help you prepare for your {building_type} project. Let's explore this systematically:

**What type of {main_topic} challenges would you like to explore first?**

1. **Common obstacles** - Typical challenges encountered in {main_topic} implementation
2. **Site-specific challenges** - How {main_topic} challenges vary by context
3. **Budget and resource constraints** - Financial and practical limitations
4. **Integration challenges** - How {main_topic} conflicts with other design goals
5. **Maintenance and long-term issues** - Ongoing challenges with {main_topic}

**Or is there a specific {main_topic} challenge you're currently facing in your project?**

*What type of {main_topic} challenge feels most relevant to your current design stage?*
"""
        }
        
        return focus_questions.get(focus_area, f"""
**🏗️ {main_topic.title()} - Let's Explore Your Focus**

Great! You've identified an important aspect of {main_topic} for your {building_type} project. Let's dive deeper:

**What specific {main_topic} question or challenge are you wrestling with right now?**

*This will help me provide the most relevant guidance for your current design stage.*
""")
    
    def _generate_dynamic_topic_guidance(self, main_topic: str, building_type: str, last_message: str) -> str:
        """Generate dynamic topic-specific guidance for any architectural topic"""
        
        # Check if user is asking about a specific topic
        if main_topic != "architectural design":
            return f"""
**🏗️ {main_topic.title()} - Let's Focus Your Thinking**

Great topic! {main_topic.title()} is an important aspect of {building_type} projects. Before we dive into examples, let's clarify your specific interests:

**What aspect of {main_topic} interests you most?**

1. **Principles and concepts** - The fundamental ideas behind {main_topic}
2. **Practical applications** - How to implement {main_topic} in real projects
3. **Technical requirements** - Specific standards and specifications for {main_topic}
4. **Design strategies** - Creative approaches to {main_topic}
5. **Problem-solving** - How to address {main_topic} challenges

**Or is there a specific challenge you're facing with {main_topic} in your {building_type} project?**

*Tell me which direction feels most relevant to your current design thinking.*
"""
        else:
            # Generic guidance for general architectural inquiries
            return f"""
**🤔 Let's Clarify Your Focus**

I want to make sure I provide the most helpful guidance for your {building_type} project.

**What would be most valuable for you right now?**

1. **Specific examples** - Real projects that demonstrate best practices
2. **Design principles** - The underlying concepts and approaches
3. **Process guidance** - How to approach this type of project step-by-step
4. **Technical details** - Specific requirements, codes, or standards
5. **Creative inspiration** - Different ways to think about the problem

**Or is there a particular challenge or question you're wrestling with?**

*What would help you move forward most effectively?*
"""