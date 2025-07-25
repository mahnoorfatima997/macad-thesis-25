# agents/socratic_tutor.py - COMPLETE REWRITE implementing Section 5 Logic
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
        
        # Initialize question templates based on Section 5 logic
        self.question_templates = self._initialize_question_templates()
        
        print(f"🤔 {self.name} initialized for domain: {domain}")
    
    def generate_choice_question(self, improvement_areas: List[str], state: ArchMentorState) -> str:
        """Generate question to help student choose improvement focus"""
        
        building_type = state.current_design_brief.split()[2] if len(state.current_design_brief.split()) > 2 else "project"
        
        choice_questions = [
            f"Which of these improvement areas feels most important for your {building_type} right now?",
            f"Looking at these opportunities, which aspect would you like to explore first?", 
            f"What draws your attention most among these improvement areas?",
            f"Which area do you think would have the biggest impact on your design?"
        ]
        
        import random
        return random.choice(choice_questions)

    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any], context_classification: Optional[Dict] = None) -> Dict[str, Any]:
        """Enhanced to handle improvement area selection"""
        
        # Check if this is an improvement overview situation
        domain_result = getattr(state, '_temp_domain_result', None)
        if (domain_result and 
            domain_result.get("knowledge_response", {}).get("response_type") == "improvement_overview"):
            
            areas = domain_result["knowledge_response"]["areas_identified"]
            choice_question = self.generate_choice_question(areas, state)
            
            return {
                "agent": self.name,
                "response_text": choice_question,
                "response_type": "choice_facilitation",
                "primary_gap_addressed": "area_selection",
                "educational_intent": "Guide student to choose their learning focus"
            }

    
    def _initialize_question_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize question templates based on Section 5 logic"""
        
        return {
            # UNDERSTANDING LEVEL BASED QUESTIONS (Section 5)
            "understanding_level": {
                "low": [
                    "What do you mean by {topic}?",
                    "Can you help me understand your thinking about {topic}?",
                    "What's your current understanding of {topic}?",
                    "How would you describe {topic} in your own words?",
                    "What aspects of {topic} are you most familiar with?"
                ],
                "medium": [
                    "What possibilities do you see for {topic}?",
                    "How might you approach {topic}?",
                    "What factors should we consider for {topic}?",
                    "What alternatives have you considered for {topic}?",
                    "How does {topic} relate to your overall design goals?"
                ],
                "high": [
                    "Why do you think this approach to {topic} would work?",
                    "What are the implications of your {topic} decisions?",
                    "How does {topic} connect to other aspects of your design?",
                    "What evidence supports your {topic} strategy?",
                    "How might you evaluate the success of your {topic} approach?"
                ]
            },
            
            # CONFIDENCE LEVEL ADAPTATIONS (Section 5)
            "confidence_level": {
                "uncertain": [
                    "Let's explore this step by step. What feels most familiar to you about {topic}?",
                    "What aspects of {topic} do you feel confident about?",
                    "If you had to start somewhere with {topic}, where would that be?",
                    "What similar situations have you encountered that might help with {topic}?",
                    "What would help you feel more confident about {topic}?"
                ],
                "confident": [
                    "That's a solid foundation. How might you build on that {topic} approach?",
                    "What deeper aspects of {topic} could we explore?",
                    "How would you explain your {topic} reasoning to someone else?",
                    "What additional considerations might strengthen your {topic} approach?",
                    "Where do you see the most potential for development in {topic}?"
                ],
                "overconfident": [
                    "What if your assumptions about {topic} are incomplete?",
                    "How might someone disagree with your {topic} approach?",
                    "What could go wrong with this {topic} strategy?",
                    "What evidence might challenge your {topic} conclusions?",
                    "How would your {topic} approach perform under different constraints?"
                ]
            },
            
            # QUESTION TYPES BY LEARNING GOAL (Section 5)
            "learning_goals": {
                "exploration": [
                    "What possibilities do you see for {topic}?",
                    "How might you approach {topic}?",
                    "What different directions could {topic} take?",
                    "What would happen if you tried {alternative} for {topic}?",
                    "How else might you think about {topic}?"
                ],
                "clarification": [
                    "What do you mean by {topic}?",
                    "Can you be more specific about {topic}?",
                    "How would you define {topic} in this context?",
                    "What exactly are you trying to achieve with {topic}?",
                    "Can you give me an example of {topic}?"
                ],
                "analysis": [
                    "Why do you think this {topic} approach works?",
                    "What are the implications of this {topic} decision?",
                    "How does {topic} affect other parts of your design?",
                    "What are the strengths and weaknesses of this {topic} approach?",
                    "What patterns do you notice in successful {topic} examples?"
                ],
                "synthesis": [
                    "How does {topic} connect to {related_topic}?",
                    "What patterns do you notice across different aspects of {topic}?",
                    "How might you integrate {topic} with your overall design vision?",
                    "What overarching principles guide your {topic} decisions?",
                    "How do all these {topic} considerations work together?"
                ]
            }
        }
    
    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any], context_classification: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate Socratic response implementing Section 5 logic"""
        
        print(f"\n🤔 {self.name} generating Socratic response...")
        
        cognitive_flags = analysis_result.get('cognitive_flags', [])
        
        # Determine primary cognitive gap
        primary_gap = self._determine_primary_gap(cognitive_flags)
        print(f"📋 Processing {len(cognitive_flags)} cognitive flags")
        print(f"🎯 Primary cognitive gap: {primary_gap}")
        
        # Analyze student state for adaptive questioning
        student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
        
        # Determine response strategy: questions vs guidance
        response_strategy = self._determine_response_strategy(student_analysis, primary_gap)
        
        # Generate appropriate response
        if response_strategy == "provide_supportive_guidance":
            response_result = await self._generate_supportive_guidance(state, primary_gap, student_analysis)
        elif response_strategy == "provide_clarifying_guidance":
            response_result = await self._generate_clarifying_guidance(state, primary_gap, student_analysis)
        else:  # Various question strategies
            response_result = await self._generate_adaptive_question(state, primary_gap, student_analysis, response_strategy)
        
        response_result.update({
            "agent": self.name,
            "primary_gap_addressed": primary_gap,
            "response_strategy": response_strategy,
            "student_analysis": student_analysis,
            "educational_intent": self._get_educational_intent(response_strategy, primary_gap)
        })
        
        print(f"✅ Generated {response_strategy} response")
        print(f"🎯 Intent: {response_result['educational_intent']}")
        
        return response_result
    
    def _analyze_student_state(self, state: ArchMentorState, analysis_result: Dict, context_classification: Optional[Dict]) -> Dict[str, Any]:
        """Analyze student state for adaptive Socratic method implementation"""
        
        # Get understanding level from analysis
        understanding_level = self._assess_understanding_level(state, analysis_result, context_classification)
        
        # Get confidence level from context or analysis
        confidence_level = self._assess_confidence_level(state, context_classification)
        
        # Assess engagement level
        engagement_level = self._assess_engagement_level(state, context_classification)
        
        # Check for confusion signals
        confusion_score = self._assess_confusion_level(state)
        
        return {
            "understanding_level": understanding_level,
            "confidence_level": confidence_level,
            "engagement_level": engagement_level,
            "confusion_score": confusion_score,
            "conversation_length": len(state.messages),
            "recent_patterns": self._analyze_recent_patterns(state)
        }
    
    def _assess_understanding_level(self, state: ArchMentorState, analysis_result: Dict, context_classification: Optional[Dict]) -> str:
        """Assess student understanding level (Section 5 logic)"""
        
        # Use detected skill level as baseline
        skill_level = state.student_profile.skill_level
        
        # Adjust based on context classification if available
        if context_classification:
            understanding_from_context = context_classification.get("understanding_level", "medium")
            
            # Combine skill level with contextual understanding
            if skill_level == "beginner" and understanding_from_context in ["medium", "high"]:
                return "medium"  # Beginner showing progress
            elif skill_level == "advanced" and understanding_from_context == "low":
                return "medium"  # Advanced student struggling with this topic
            else:
                return understanding_from_context
        
        # Map skill level to understanding level
        skill_to_understanding = {
            "beginner": "low",
            "intermediate": "medium", 
            "advanced": "high"
        }
        
        return skill_to_understanding.get(skill_level, "medium")
    
    def _assess_confidence_level(self, state: ArchMentorState, context_classification: Optional[Dict]) -> str:
        """Assess student confidence level (Section 5 logic)"""
        
        if context_classification:
            return context_classification.get("confidence_level", "confident")
        
        # Analyze recent messages for confidence indicators
        recent_messages = [msg['content'] for msg in state.messages[-3:] if msg.get('role') == 'user']
        recent_text = ' '.join(recent_messages).lower()
        
        # Overconfident indicators
        overconfident_words = ["obviously", "clearly", "definitely", "perfect", "optimal", "best"]
        if any(word in recent_text for word in overconfident_words):
            return "overconfident"
        
        # Uncertain indicators
        uncertain_words = ["maybe", "i think", "not sure", "confused", "unclear"]
        if any(word in recent_text for word in uncertain_words):
            return "uncertain"
        
        return "confident"  # Default
    
    def _assess_engagement_level(self, state: ArchMentorState, context_classification: Optional[Dict]) -> str:
        """Assess student engagement level"""
        
        if context_classification:
            return context_classification.get("engagement_level", "medium")
        
        # Analyze message patterns
        user_messages = [msg for msg in state.messages if msg.get('role') == 'user']
        
        if not user_messages:
            return "medium"
        
        # Recent message analysis
        recent_messages = user_messages[-2:]
        avg_length = sum(len(msg['content'].split()) for msg in recent_messages) / len(recent_messages)
        has_questions = any("?" in msg['content'] for msg in recent_messages)
        
        if avg_length > 20 and has_questions:
            return "high"
        elif avg_length < 5:
            return "low"
        else:
            return "medium"
    
    def _assess_confusion_level(self, state: ArchMentorState) -> float:
        """Assess level of confusion from recent messages"""
        
        user_messages = [msg['content'] for msg in state.messages[-3:] if msg.get('role') == 'user']
        recent_text = ' '.join(user_messages).lower()
        
        confusion_indicators = ["confused", "don't understand", "unclear", "lost", "help"]
        confusion_count = sum(1 for indicator in confusion_indicators if indicator in recent_text)
        
        return min(confusion_count / 3.0, 1.0)  # Normalize to 0-1
    
    def _analyze_recent_patterns(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze recent conversation patterns"""
        
        user_messages = [msg['content'] for msg in state.messages[-5:] if msg.get('role') == 'user']
        
        return {
            "repetitive_topics": self._detect_repetitive_topics(user_messages),
            "question_frequency": sum(1 for msg in user_messages if "?" in msg) / max(len(user_messages), 1),
            "shows_progression": len(set(user_messages)) > len(user_messages) * 0.7  # Diverse responses
        }
    
    def _detect_repetitive_topics(self, messages: List[str]) -> bool:
        """Detect if student is stuck on same topics"""
        
        if len(messages) < 3:
            return False
        
        # Simple keyword overlap detection
        keywords = []
        for msg in messages:
            words = [word.lower() for word in msg.split() if len(word) > 4]
            keywords.extend(words)
        
        # If too much overlap, might be repetitive
        unique_ratio = len(set(keywords)) / max(len(keywords), 1)
        return unique_ratio < 0.6
    
    def _determine_response_strategy(self, student_analysis: Dict, primary_gap: str) -> str:
        """Determine whether to ask questions or provide guidance (Section 5 logic)"""
        
        understanding = student_analysis["understanding_level"]
        confidence = student_analysis["confidence_level"]
        engagement = student_analysis["engagement_level"]
        confusion = student_analysis["confusion_score"]
        
        # High confusion = provide guidance first
        if confusion > 0.7:
            return "provide_clarifying_guidance"
        
        # Uncertain + low understanding = provide supportive guidance
        if confidence == "uncertain" and understanding == "low":
            return "provide_supportive_guidance"
        
        # Low engagement = try to re-engage with exploration
        if engagement == "low":
            return "ask_exploratory_questions"
        
        # Overconfident = challenge assumptions
        if confidence == "overconfident":
            return "ask_challenging_questions"
        
        # High understanding + confident = analytical questions
        if understanding == "high" and confidence == "confident":
            return "ask_analytical_questions"
        
        # Medium understanding = discovery questions
        if understanding == "medium":
            return "ask_discovery_questions"
        
        # Default: clarifying questions for low understanding
        return "ask_clarifying_questions"
    
    async def _generate_supportive_guidance(self, state: ArchMentorState, primary_gap: str, student_analysis: Dict) -> Dict[str, Any]:
        """Generate supportive guidance for uncertain/struggling students"""
        
        topic = self._gap_to_topic(primary_gap)
        
        guidance_prompt = f"""
        Provide gentle, supportive guidance for an uncertain architecture student.
        
        CONTEXT:
        - Student is feeling uncertain about: {primary_gap.replace('_', ' ')}
        - Project: {state.current_design_brief}
        - Understanding level: {student_analysis['understanding_level']}
        - Confidence: {student_analysis['confidence_level']}
        
        Provide supportive guidance that:
        1. Acknowledges their uncertainty without judgment
        2. Offers a small, manageable starting point
        3. Builds confidence through encouragement
        4. Provides helpful direction without solving the problem
        5. Ends with a gentle, supportive question
        
        Tone: Encouraging, patient, supportive
        Length: 50-80 words
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": guidance_prompt}],
                max_tokens=120,
                temperature=0.6
            )
            
            guidance_text = response.choices[0].message.content.strip()
            
            return {
                "response_text": guidance_text,
                "response_type": "supportive_guidance",
                "has_question": "?" in guidance_text
            }
            
        except Exception as e:
            # Fallback supportive guidance
            fallback = f"I understand {topic} can feel overwhelming. Let's start with what you already know. What aspects of {topic} feel most familiar to you?"
            
            return {
                "response_text": fallback,
                "response_type": "supportive_guidance_fallback",
                "has_question": True,
                "error": str(e)
            }
    



    async def generate_dynamic_socratic_question(self, primary_gap: str, confidence_level: str, understanding_level: str, engagement_level: str, state: ArchMentorState, user_input: str) -> str:
        """Generate Socratic questions for ANY topic the student mentions - no templates"""
        
        prompt = f"""
        Generate a Socratic question for an architecture student based on their learning state:
        
        STUDENT'S INPUT: "{user_input}"
        LEARNING GAP: {primary_gap.replace('_', ' ')}
        PROJECT: {state.current_design_brief}
        SKILL LEVEL: {state.student_profile.skill_level}
        
        LEARNING STATE:
        - Confidence: {confidence_level}
        - Understanding: {understanding_level}  
        - Engagement: {engagement_level}
        
        Generate a Socratic question based on their learning state:
        
        IF OVERCONFIDENT:
        - Challenge assumptions: "What if your assumptions about X are incomplete?"
        - Test boundaries: "How might this approach fail in different conditions?"
        - Explore alternatives: "How might someone disagree with this approach?"
        
        IF UNCERTAIN/LOW UNDERSTANDING:
        - Build confidence: "What aspects of X feel most familiar to you?"
        - Start simple: "Let's begin with what you already know about X"
        - Provide direction: "What would help you feel more confident about X?"
        
        IF CONFIDENT + GOOD UNDERSTANDING:
        - Deepen analysis: "Why do you think this X approach would work?"
        - Explore connections: "How does X relate to other aspects of your design?"
        - Encourage evaluation: "What evidence supports your X strategy?"
        
        IF LOW ENGAGEMENT:
        - Re-engage: "What possibilities do you see for X?"
        - Spark curiosity: "What if you approached X completely differently?"
        - Make it personal: "How would X affect your own experience of the space?"
        
        The question should:
        1. Address what they ACTUALLY mentioned in their input
        2. Match their learning state and skill level
        3. Guide discovery rather than test knowledge
        4. Be specific to their project context
        5. Encourage thinking rather than seeking answers
        
        Generate ONE appropriate Socratic question (under 25 words).
        Focus on THEIR topic, not generic architectural concepts.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.6
            )
            
            question = response.choices[0].message.content.strip()
            
            # Ensure it's a question
            if not question.endswith('?'):
                question += '?'
            
            print(f"🤔 Generated dynamic Socratic question: {question}")
            return question
            
        except Exception as e:
            print(f"⚠️ Dynamic question generation failed: {e}")
            return self._fallback_socratic_question(primary_gap, confidence_level, user_input)

    def _fallback_socratic_question(self, primary_gap: str, confidence_level: str, user_input: str) -> str:
        """Simple fallback questions when AI fails"""
        
        topic = primary_gap.replace('_', ' ')
        
        if confidence_level == "overconfident":
            return f"What assumptions are you making about {topic} that might need questioning?"
        elif confidence_level == "uncertain":
            return f"What aspects of {topic} feel most familiar to you right now?"
        else:
            return f"What possibilities do you see for developing {topic} further?"

    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any], context_classification: Optional[Dict] = None) -> Dict[str, Any]:
        """Updated generate_response to use dynamic question generation"""
        
        print(f"\n🤔 {self.name} generating Socratic response...")
        
        # Get user's last input
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        # Get learning state from context classification
        if context_classification:
            confidence_level = context_classification.get("confidence_level", "confident")
            understanding_level = context_classification.get("understanding_level", "medium")
            engagement_level = context_classification.get("engagement_level", "medium")
            
            # Get primary gap to address
            cognitive_flags = analysis_result.get('cognitive_flags', [])
            primary_gap = self._determine_primary_gap(cognitive_flags)
            
            # Generate dynamic question based on what they actually said
            dynamic_question = await self.generate_dynamic_socratic_question(
                primary_gap, confidence_level, understanding_level, engagement_level, state, last_message
            )
            
            return {
                "agent": self.name,
                "response_text": dynamic_question,
                "response_type": "dynamic_socratic",
                "primary_gap_addressed": primary_gap,
                "educational_intent": f"Guide exploration based on {confidence_level} confidence",
                "question_approach": f"Adapted to {understanding_level} understanding",
                "user_input_addressed": last_message[:50] + "..." if len(last_message) > 50 else last_message
            }
        
        # Fallback to existing logic if no context classification
        cognitive_flags = analysis_result.get('cognitive_flags', [])
        primary_gap = self._determine_primary_gap(cognitive_flags)
        
        # Use existing methods as fallback
        student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
        response_strategy = self._determine_response_strategy(student_analysis, primary_gap)
        
        if response_strategy == "provide_supportive_guidance":
            response_result = await self._generate_supportive_guidance(state, primary_gap, student_analysis)
        elif response_strategy == "provide_clarifying_guidance":
            response_result = await self._generate_clarifying_guidance(state, primary_gap, student_analysis)
        else:
            response_result = await self._generate_adaptive_question(state, primary_gap, student_analysis, response_strategy)
        
        response_result.update({
            "agent": self.name,
            "primary_gap_addressed": primary_gap,
            "educational_intent": f"Guide learning for {primary_gap}"
        })
        
        return response_result






    async def _generate_clarifying_guidance(self, state: ArchMentorState, primary_gap: str, student_analysis: Dict) -> Dict[str, Any]:
        """Generate clarifying guidance for confused students"""
        
        topic = self._gap_to_topic(primary_gap)
        
        clarification_prompt = f"""
        Provide clear, clarifying guidance for a confused architecture student.
        
        CONTEXT:
        - Student is confused about: {primary_gap.replace('_', ' ')}
        - Project: {state.current_design_brief}
        - Confusion level: {student_analysis['confusion_score']:.1f}
        
        Provide clarifying guidance that:
        1. Breaks down the complex topic into simpler parts
        2. Explains one key concept clearly
        3. Uses concrete examples when helpful
        4. Reduces cognitive load
        5. Ends with a simple, focusing question
        
        Tone: Clear, patient, explanatory
        Length: 60-100 words
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": clarification_prompt}],
                max_tokens=150,
                temperature=0.4
            )
            
            clarification_text = response.choices[0].message.content.strip()
            
            return {
                "response_text": clarification_text,
                "response_type": "clarifying_guidance",
                "has_question": "?" in clarification_text
            }
            
        except Exception as e:
            # Fallback clarifying guidance
            fallback = f"Let me help clarify {topic}. The key thing to understand is that it's about creating solutions that work for your users. What specific part would you like me to explain first?"
            
            return {
                "response_text": fallback,
                "response_type": "clarifying_guidance_fallback", 
                "has_question": True,
                "error": str(e)
            }
    
    async def _generate_adaptive_question(self, state: ArchMentorState, primary_gap: str, student_analysis: Dict, strategy: str) -> Dict[str, Any]:
        """Generate adaptive questions based on strategy (Section 5 logic)"""
        
        understanding = student_analysis["understanding_level"]
        confidence = student_analysis["confidence_level"]
        topic = self._gap_to_topic(primary_gap)
        
        # Select appropriate question type
        if strategy == "ask_challenging_questions":
            question_type = "confidence_level"
            question_category = "overconfident"
        elif strategy == "ask_analytical_questions":
            question_type = "learning_goals"
            question_category = "analysis"
        elif strategy == "ask_discovery_questions":
            question_type = "learning_goals"
            question_category = "exploration"
        elif strategy == "ask_clarifying_questions":
            question_type = "learning_goals"
            question_category = "clarification"
        else:  # ask_exploratory_questions
            question_type = "understanding_level"
            question_category = understanding
        
        # Get question template
        question_templates = self.question_templates[question_type][question_category]
        base_question = random.choice(question_templates)
        
        # Contextualize the question
        contextualized_question = await self._contextualize_question(
            base_question, topic, state, primary_gap, student_analysis
        )
        
        return {
            "response_text": contextualized_question,
            "response_type": f"socratic_{strategy}",
            "question_type": question_type,
            "question_category": question_category,
            "has_question": True
        }
    
    async def _contextualize_question(self, base_question: str, topic: str, state: ArchMentorState, primary_gap: str, student_analysis: Dict) -> str:
        """Contextualize question to student's specific project"""
        
        contextualization_prompt = f"""
        Adapt this Socratic question to be specific to the student's architectural project:
        
        BASE QUESTION: {base_question}
        TOPIC: {topic}
        STUDENT PROJECT: {state.current_design_brief}
        LEARNING GAP: {primary_gap.replace('_', ' ')}
        UNDERSTANDING LEVEL: {student_analysis['understanding_level']}
        
        Create a contextualized question that:
        1. Maintains the Socratic questioning approach
        2. Relates directly to their specific project
        3. Addresses the learning gap
        4. Matches their understanding level
        5. Encourages discovery and thinking
        
        Return only the contextualized question.
        Length: One sentence, under 25 words.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": contextualization_prompt}],
                max_tokens=60,
                temperature=0.5
            )
            
            contextualized = response.choices[0].message.content.strip()
            
            # Ensure it's a question
            if not contextualized.endswith('?'):
                contextualized += '?'
            
            return contextualized
            
        except Exception as e:
            # Fallback to simple template substitution
            return base_question.format(topic=topic)
    
    def _determine_primary_gap(self, cognitive_flags: List[str]) -> str:
        """Determine primary cognitive gap to address"""
        
        if not cognitive_flags:
            return "general_exploration"
        
        # Priority order for gap addressing
        gap_priority = [
            "needs_accessibility_guidance",
            "needs_brief_clarification", 
            "needs_spatial_thinking_support",
            "needs_basic_guidance",
            "needs_public_space_consideration",
            "needs_program_clarification"
        ]
        
        for priority_gap in gap_priority:
            if priority_gap in cognitive_flags:
                return priority_gap.replace('needs_', '').replace('_guidance', '')
        
        # Return first flag if no priority match
        return cognitive_flags[0].replace('needs_', '').replace('_guidance', '')
    
    def _gap_to_topic(self, gap: str) -> str:
        """Convert cognitive gap to conversational topic - EXPANDED"""
        
        gap_to_topic_map = {
            "accessibility": "accessibility and universal design",
            "spatial_design": "spatial organization and central space design",  # NEW
            "lighting_design": "lighting and natural illumination",  # NEW  
            "circulation_design": "circulation and movement patterns",  # NEW
            "brief_clarification": "project requirements and goals",
            "spatial_thinking_support": "spatial organization and flow",
            "basic": "fundamental design principles",
            "public_space_consideration": "community and public space design",
            "program_clarification": "program requirements and user needs"
        }
        
        return gap_to_topic_map.get(gap, gap.replace('_', ' '))
    
    def _get_educational_intent(self, strategy: str, primary_gap: str) -> str:
        """Get educational intent for logging/analysis"""
        
        intent_map = {
            "provide_supportive_guidance": "Build confidence and provide direction",
            "provide_clarifying_guidance": "Reduce confusion and clarify concepts", 
            "ask_challenging_questions": "Challenge assumptions and deepen thinking",
            "ask_analytical_questions": "Promote analytical thinking and evaluation",
            "ask_discovery_questions": "Guide discovery and exploration",
            "ask_clarifying_questions": "Clarify understanding and concepts",
            "ask_exploratory_questions": "Re-engage and explore possibilities"
        }
        
        base_intent = intent_map.get(strategy, "Guide learning")
        return f"{base_intent} for {primary_gap.replace('_', ' ')}"

# Test function
async def test_complete_socratic_agent():
    print("🧪 Testing Complete Socratic Agent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for elderly people with accessibility considerations"
    state.student_profile.skill_level = "intermediate"
    
    # Add some conversation history
    state.messages = [
        {"role": "user", "content": "I think my design is obviously perfect for accessibility"},
        {"role": "assistant", "content": "Let's explore that further"},
        {"role": "user", "content": "Maybe I'm not sure about the door widths though"}
    ]
    
    # Mock analysis result
    analysis_result = {
        "cognitive_flags": ["needs_accessibility_guidance", "needs_spatial_thinking_support"],
        "confidence_score": 0.6
    }
    
    # Mock context classification
    context_classification = {
        "confidence_level": "overconfident",
        "understanding_level": "medium",
        "engagement_level": "high"
    }
    
    # Test Socratic agent
    agent = SocraticTutorAgent("architecture")
    result = await agent.generate_response(state, analysis_result, context_classification)
    
    print(f"\n🤔 Socratic Agent Results:")
    print(f"   Strategy: {result['response_strategy']}")
    print(f"   Primary Gap: {result['primary_gap_addressed']}")
    print(f"   Educational Intent: {result['educational_intent']}")
    print(f"   Response Type: {result['response_type']}")
    print(f"   Has Question: {result.get('has_question', False)}")
    
    print(f"\n💬 Generated Response:")
    print(f"   {result['response_text']}")
    
    print(f"\n📊 Student Analysis Used:")
    for key, value in result['student_analysis'].items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Complete Socratic Agent working!")
    
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_complete_socratic_agent())