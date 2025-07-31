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
    
    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any], context_classification: Optional[Dict] = None) -> Dict[str, Any]:
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
        
        # Advanced analysis of student state
        student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
        conversation_progression = self._analyze_conversation_progression(state, last_message)
        student_insights = self._extract_student_insights(state, last_message)
        
        # Determine response strategy based on analysis
        response_strategy = self._determine_response_strategy(student_analysis, conversation_progression)
        
        print(f"📊 Student Analysis: {student_analysis}")
        print(f"🔄 Conversation Stage: {conversation_progression['stage']}")
        print(f"💡 Student Insights: {student_insights['key_insights']}")
        print(f"🎯 Response Strategy: {response_strategy}")
        
        # Generate appropriate response based on strategy
        if response_strategy == "clarifying_guidance":
            response_result = await self._generate_clarifying_guidance(state, student_analysis, conversation_progression)
        elif response_strategy == "supportive_guidance":
            response_result = await self._generate_supportive_guidance(state, student_analysis, conversation_progression)
        elif response_strategy == "challenging_question":
            response_result = await self._generate_challenging_question(state, student_analysis, conversation_progression)
        elif response_strategy == "exploratory_question":
            response_result = await self._generate_exploratory_question(state, student_analysis, conversation_progression)
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
                max_tokens=600,  # Increased from 200 to prevent cut-off responses
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
        """Determine the best response strategy based on analysis"""
        
        confidence = student_analysis["confidence_level"]
        understanding = student_analysis["understanding_level"]
        shows_confusion = student_analysis["shows_confusion"]
        shows_overconfidence = student_analysis["shows_overconfidence"]
        stage = conversation_progression["stage"]
        
        # Strategy determination logic
        if shows_confusion or confidence == "uncertain":
            return "clarifying_guidance"
        elif shows_overconfidence or confidence == "overconfident":
            return "challenging_question"
        elif understanding == "low" or stage == "initial":
            return "supportive_guidance"
        elif stage == "exploration":
            return "exploratory_question"
        elif stage == "deepening":
            return "challenging_question"
        elif stage == "advanced":
            return "challenging_question"
        else:
            return "adaptive_question"
    
    async def _generate_clarifying_guidance(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate clarifying guidance for confused students"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        The student seems confused or uncertain. Provide clarifying guidance that helps them understand the concept better.
        
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Provide a clarifying response that:
        1. Acknowledges their confusion
        2. Breaks down the concept into simpler terms
        3. Provides a clear, step-by-step explanation
        4. Encourages them to ask follow-up questions
        5. Is supportive and patient
        
        Give a helpful clarifying response:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Increased from 150 to prevent cut-off responses
                temperature=0.4
            )
            
            clarifying_response = response.choices[0].message.content.strip()
            
            return {
                "response_text": clarifying_response,
                "response_type": "clarifying_guidance",
                "user_input_addressed": "confusion_expression"
            }
            
        except Exception as e:
            print(f"⚠️ Clarifying guidance generation failed: {e}")
            return {
                "response_text": "I understand this might be confusing. Let me break this down step by step. What specific part would you like me to clarify?",
                "response_type": "clarifying_guidance",
                "user_input_addressed": "confusion_expression"
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
                max_tokens=400,  # Increased from 150 to prevent cut-off responses
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