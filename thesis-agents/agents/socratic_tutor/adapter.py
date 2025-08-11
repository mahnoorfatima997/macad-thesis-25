"""
Socratic Tutor Agent Adapter - streamlined modular version.

This adapter maintains backward compatibility while delegating to processor modules.
"""

import sys
import os
from typing import Dict, Any, List, Optional

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics

# Import modular components
from .config import *
from .schemas import QuestionContext, QuestionResult, GuidanceContext, SocraticResponse
from .processors import QuestionGeneratorProcessor, SocraticResponseBuilderProcessor
from ..common import LLMClient, AgentTelemetry, MetricsCalculator, TextProcessor, SafetyValidator

# Import phase assessment system
try:
    from phase_assessment import PhaseAssessmentManager, DesignPhase, SocraticStep
    PHASE_ASSESSMENT_AVAILABLE = True
except ImportError:
    PHASE_ASSESSMENT_AVAILABLE = False
    print("⚠️ Phase assessment system not available")


class SocraticTutorAgent:
    """
    Socratic Tutor Agent for guided questioning and learning facilitation.
    
    This streamlined adapter delegates to specialized processor modules.
    """
    
    def __init__(self, domain="architecture"):
        """Initialize the Socratic Tutor Agent with modular processors."""
        self.telemetry = AgentTelemetry("socratic_tutor")
        self.telemetry.log_agent_start("__init__", domain=domain)
        
        # Core properties
        self.domain = domain
        self.name = "socratic_tutor"
        
        # Initialize LLM client
        self.client = LLMClient(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        
        # Initialize shared utilities
        self.text_processor = TextProcessor()
        self.safety_validator = SafetyValidator()
        self.metrics_calculator = MetricsCalculator()
        
        # Initialize modular processors
        self.question_processor = QuestionGeneratorProcessor()
        self.response_processor = SocraticResponseBuilderProcessor()

        # Initialize phase assessment system if available
        if PHASE_ASSESSMENT_AVAILABLE:
            self.phase_manager = PhaseAssessmentManager()
            print(f"   📋 Phase-based assessment system enabled")
        else:
            self.phase_manager = None
            print(f"   ⚠️ Phase-based assessment system disabled")

        self.telemetry.log_agent_end("__init__")
        print(f"🤔 {self.name} initialized for domain: {domain}")
    
    async def provide_guidance(
        self, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict, 
        gap_type: str
    ) -> AgentResponse:
        """
        Main guidance provision method - maintains exact same signature as original.
        
        Args:
            state: Current system state
            context_classification: Context analysis from context agent
            analysis_result: Analysis results from analysis agent
            gap_type: Type of knowledge gap to address
            
        Returns:
            AgentResponse with Socratic question and guidance
        """
        self.telemetry.log_agent_start("provide_guidance")
        
        try:
            print(f"\n🤔 {self.name} generating sophisticated Socratic response...")

            # Get user's last input
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            user_input = user_messages[-1] if user_messages else ""

            if not user_input:
                return self._generate_fallback_response(state, context_classification, analysis_result, gap_type)

            # Check if phase-based assessment is available and should be used
            if self.phase_manager and self._should_use_phase_based_approach(state, context_classification):
                print(f"   🎯 Using phase-based Socratic assessment")
                response_result = await self._generate_phase_based_response(state, context_classification, analysis_result, gap_type)
            else:
                print(f"   🔄 Using adaptive Socratic approach")
                # Analyze student state and conversation progression
                student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
                conversation_progression = self._analyze_conversation_progression(state, user_input)

                # Determine response strategy
                response_strategy = self._determine_response_strategy(student_analysis, conversation_progression)

                print(f"   Strategy: {response_strategy}")
                print(f"   Student confidence: {student_analysis.get('confidence_level', 'unknown')}")
                print(f"   Conversation stage: {conversation_progression.get('stage', 'unknown')}")

                # Generate response based on strategy
                response_result = await self._generate_response_by_strategy(
                    response_strategy, state, student_analysis, conversation_progression, analysis_result
                )

            # Add cognitive flags
            cognitive_flags = self._extract_cognitive_flags(response_result, state)
            response_result["cognitive_flags"] = cognitive_flags

            # Convert to AgentResponse
            agent_response = self._convert_to_agent_response(
                response_result, state, analysis_result, context_classification, gap_type
            )

            self.telemetry.log_agent_end("provide_guidance")
            return agent_response

        except Exception as e:
            self.telemetry.log_error(f"Guidance provision failed: {str(e)}")
            return ResponseBuilder.create_error_response(
                f"Guidance provision failed: {str(e)}",
                agent_name=self.name
            )
    
    # Delegation methods for backward compatibility
    
    async def generate_socratic_question(
        self, 
        user_input: str, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict, 
        gap_type: str
    ) -> QuestionResult:
        """Generate Socratic question (delegates to processor)."""
        return await self.question_processor.generate_socratic_question(
            user_input, state, context_classification, analysis_result, gap_type
        )
    
    def convert_to_agent_response(
        self, 
        question_result: QuestionResult, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict
    ) -> AgentResponse:
        """Convert to agent response (delegates to processor)."""
        return self.response_processor.convert_to_agent_response(
            question_result, state, context_classification, analysis_result
        )
    
    def calculate_enhancement_metrics(self, question_result: QuestionResult, state: ArchMentorState) -> EnhancementMetrics:
        """Calculate enhancement metrics (delegates to processor)."""
        return self.response_processor._calculate_enhancement_metrics(question_result, state)
    
    def extract_cognitive_flags(self, question_result: QuestionResult, context_classification: Dict) -> List[str]:
        """Extract cognitive flags (delegates to processor)."""
        return self.response_processor._extract_cognitive_flags(question_result, context_classification)
    
    def get_pedagogical_intent(self, interaction_type: str, confidence_level: str) -> str:
        """Get pedagogical intent (delegates to processor)."""
        return self.question_processor._get_pedagogical_intent(interaction_type, confidence_level)
    
    def validate_question(self, question_text: str) -> bool:
        """Validate question quality (delegates to processor)."""
        return self.question_processor.validate_question(question_text)
    
    def get_question_statistics(self, question_text: str) -> Dict[str, Any]:
        """Get question statistics (delegates to processor)."""
        return self.question_processor.get_question_statistics(question_text)
    
    def validate_response_quality(self, agent_response: AgentResponse) -> bool:
        """Validate response quality (delegates to processor)."""
        return self.response_processor.validate_response_quality(agent_response)
    
    # Private methods for internal processing (maintain compatibility)
    
    async def _generate_socratic_question(
        self, 
        user_input: str, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict, 
        gap_type: str
    ) -> Dict[str, Any]:
        """
        Internal question generation method (maintains original signature).
        Converts QuestionResult to Dict for backward compatibility.
        """
        try:
            question_result = await self.question_processor.generate_socratic_question(
                user_input, state, context_classification, analysis_result, gap_type
            )
            return question_result.to_dict()
            
        except Exception as e:
            self.telemetry.log_error("_generate_socratic_question", str(e))
            return {
                "question_text": FALLBACK_QUESTION,
                "question_type": "fallback",
                "pedagogical_intent": "Encourage exploration and curiosity"
            }
    
    def _get_pedagogical_intent(self, interaction_type: str, confidence_level: str) -> str:
        """Internal pedagogical intent method (delegates to processor)."""
        return self.question_processor._get_pedagogical_intent(interaction_type, confidence_level)
    
    def _convert_to_agent_response(
        self, 
        question_result: Dict, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict
    ) -> AgentResponse:
        """
        Internal response conversion method (maintains original signature).
        Converts Dict to QuestionResult for processor compatibility.
        """
        try:
            # Convert dict back to QuestionResult for processor
            if isinstance(question_result, dict):
                question_obj = QuestionResult(
                    question_text=question_result.get("question_text", ""),
                    question_type=question_result.get("question_type", "socratic"),
                    interaction_type=question_result.get("interaction_type", ""),
                    understanding_level=question_result.get("understanding_level", ""),
                    confidence_level=question_result.get("confidence_level", ""),
                    pedagogical_intent=question_result.get("pedagogical_intent", ""),
                    generation_confidence=question_result.get("generation_confidence", 0.8)
                )
            else:
                question_obj = question_result
            
            return self.response_processor.convert_to_agent_response(
                question_obj, state, context_classification, analysis_result
            )
            
        except Exception as e:
            self.telemetry.log_error("_convert_to_agent_response", str(e))
            return ResponseBuilder.create_error_response(
                f"Response conversion failed: {str(e)}",
                agent_name=self.name
            )
    
    def _calculate_enhancement_metrics(self, question_result: Dict, state: ArchMentorState) -> EnhancementMetrics:
        """Internal enhancement metrics calculation (delegates to processor)."""
        try:
            # Convert dict to QuestionResult if needed
            if isinstance(question_result, dict):
                question_obj = QuestionResult(
                    question_text=question_result.get("question_text", ""),
                    question_type=question_result.get("question_type", "socratic")
                )
            else:
                question_obj = question_result
            
            return self.response_processor._calculate_enhancement_metrics(question_obj, state)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_enhancement_metrics", str(e))
            return EnhancementMetrics(
                cognitive_offloading_prevention_score=0.6,
                deep_thinking_engagement_score=0.7,
                knowledge_integration_score=0.6,
                scaffolding_effectiveness_score=0.7,
                learning_progression_score=0.6,
                metacognitive_awareness_score=0.6,
                overall_cognitive_score=0.63,
                scientific_confidence=0.8
            )
    
    def _extract_cognitive_flags(self, question_result: Dict, context_classification: Dict) -> List[str]:
        """Internal cognitive flags extraction (delegates to processor)."""
        try:
            # Convert dict to QuestionResult if needed
            if isinstance(question_result, dict):
                question_obj = QuestionResult(
                    question_text=question_result.get("question_text", ""),
                    question_type=question_result.get("question_type", "socratic"),
                    confidence_level=question_result.get("confidence_level", "")
                )
            else:
                question_obj = question_result
            
            return self.response_processor._extract_cognitive_flags(question_obj, context_classification)
            
        except Exception as e:
            self.telemetry.log_error("_extract_cognitive_flags", str(e))
            return ["deep_thinking_encouraged"]
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Internal cognitive flags conversion (delegates to processor)."""
        return self.response_processor._convert_cognitive_flags(cognitive_flags)
    
    # Utility methods
    
    def create_guidance_context(
        self, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict, 
        gap_type: str
    ) -> GuidanceContext:
        """Create guidance context object."""
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        current_input = user_messages[-1] if user_messages else ""
        
        return GuidanceContext(
            state=state,
            context_classification=context_classification,
            analysis_result=analysis_result,
            gap_type=gap_type,
            current_input=current_input
        )
    
    def get_response_summary(self, agent_response: AgentResponse) -> str:
        """Get response summary (delegates to processor)."""
        return self.response_processor.get_response_summary(agent_response)
    
    def calculate_response_effectiveness(self, agent_response: AgentResponse, 
                                       context_classification: Dict) -> float:
        """Calculate response effectiveness (delegates to processor)."""
        return self.response_processor.calculate_response_effectiveness(agent_response, context_classification)
    
    def suggest_question_improvements(self, question_text: str, context: QuestionContext) -> List[str]:
        """Suggest question improvements (delegates to processor)."""
        return self.question_processor.suggest_question_improvements(question_text, context)
    
    def get_question_complexity(self, question_text: str) -> str:
        """Get question complexity (delegates to processor)."""
        return self.question_processor.get_question_complexity(question_text)

    # Enhanced AI-powered methods for sophisticated Socratic questioning

    def _analyze_student_state(self, state: ArchMentorState, analysis_result: Dict, context_classification: Dict) -> Dict[str, Any]:
        """Analyze student's current learning state and confidence."""

        # Get confidence and understanding from context classification
        confidence_level = context_classification.get("confidence_level", "confident") if context_classification else "confident"
        understanding_level = context_classification.get("understanding_level", "medium") if context_classification else "medium"

        # Analyze question complexity from recent messages
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        question_complexity = "basic"
        if user_messages:
            last_message = user_messages[-1]
            if len(last_message.split()) > 20:
                question_complexity = "complex"
            elif len(last_message.split()) > 10:
                question_complexity = "moderate"

        return {
            "confidence_level": confidence_level,
            "understanding_level": understanding_level,
            "question_complexity": question_complexity,
            "total_messages": len(user_messages),
            "learning_progression": self._assess_learning_progression(state)
        }

    def _analyze_conversation_progression(self, state: ArchMentorState, current_message: str) -> Dict[str, Any]:
        """Analyze the progression of the conversation."""

        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']

        if len(user_messages) <= 1:
            stage = "initial"
        elif len(user_messages) <= 3:
            stage = "exploration"
        elif len(user_messages) <= 6:
            stage = "development"
        else:
            stage = "refinement"

        # Analyze topic evolution
        topic_evolution = self._analyze_topic_evolution(user_messages)

        # Identify patterns
        patterns = []
        if len(user_messages) > 2:
            recent_lengths = [len(msg.split()) for msg in user_messages[-3:]]
            if all(length > 15 for length in recent_lengths):
                patterns.append("detailed_responses")
            elif all(length < 8 for length in recent_lengths):
                patterns.append("brief_responses")

        return {
            "stage": stage,
            "topic_evolution": topic_evolution,
            "patterns": patterns,
            "message_count": len(user_messages)
        }

    def _determine_response_strategy(self, student_analysis: Dict, conversation_progression: Dict) -> str:
        """Determine the best response strategy based on student state."""

        confidence_level = student_analysis.get("confidence_level", "confident")
        stage = conversation_progression.get("stage", "initial")

        # Strategy selection logic
        if confidence_level == "confused" or confidence_level == "uncertain":
            return "clarifying_guidance"
        elif confidence_level == "overconfident":
            return "challenging_question"
        elif stage == "initial":
            return "foundational_question"
        elif stage == "exploration":
            return "exploratory_question"
        else:
            return "adaptive_question"

    async def _generate_response_by_strategy(self, strategy: str, state: ArchMentorState,
                                           student_analysis: Dict, conversation_progression: Dict,
                                           analysis_result: Dict) -> Dict[str, Any]:
        """Generate response based on the determined strategy."""

        if strategy == "clarifying_guidance":
            return await self._generate_clarifying_guidance(state, student_analysis, conversation_progression)
        elif strategy == "challenging_question":
            return await self._generate_challenging_question(state, student_analysis, conversation_progression)
        elif strategy == "foundational_question":
            return await self._generate_foundational_question(state, student_analysis, conversation_progression)
        elif strategy == "exploratory_question":
            return await self._generate_exploratory_question(state, student_analysis, conversation_progression)
        else:
            return await self._generate_adaptive_question(state, student_analysis, conversation_progression)

    async def _generate_clarifying_guidance(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate clarifying guidance for confused students."""

        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # Use AI to generate contextual clarifying guidance
        response_text = await self._generate_ai_clarifying_response(last_message, building_type, state)

        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "clarifying_guidance",
            "response_strategy": "clarifying_guidance",
            "educational_intent": "build_understanding",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

    async def _generate_challenging_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate challenging questions for overconfident students."""

        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # Use AI to generate challenging question
        response_text = await self._generate_ai_challenging_question(last_message, building_type, state)

        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "challenging_question",
            "response_strategy": "challenging_question",
            "educational_intent": "challenge_assumptions",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

    async def _generate_foundational_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate foundational questions for initial exploration."""

        building_type = self._extract_building_type_from_context(state)

        response_text = f"""Let's start by exploring the fundamentals of your {building_type} project.

What do you think are the most important questions we should ask about this project before we begin designing?

Consider: Who will use this space? What activities need to happen here? What makes this site unique?"""

        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "foundational_question",
            "response_strategy": "foundational_question",
            "educational_intent": "establish_foundation",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

    async def _generate_exploratory_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate exploratory questions for deeper investigation."""

        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # Use AI to generate exploratory question
        response_text = await self._generate_ai_exploratory_question(last_message, building_type, state)

        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "exploratory_question",
            "response_strategy": "exploratory_question",
            "educational_intent": "encourage_exploration",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

    async def _generate_adaptive_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate adaptive questions based on current context."""

        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # Use AI to generate adaptive question
        response_text = await self._generate_ai_adaptive_question(last_message, building_type, state)

        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "adaptive_question",
            "response_strategy": "adaptive_question",
            "educational_intent": "adaptive_guidance",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

    # Utility methods

    def _assess_learning_progression(self, state: ArchMentorState) -> str:
        """Assess the student's learning progression."""
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
        """Analyze how topics have evolved in the conversation."""
        if len(user_messages) < 2:
            return {"evolution": "single_topic", "topics": ["initial"]}

        # Simple topic analysis
        topics = []
        for msg in user_messages:
            if "material" in msg.lower():
                topics.append("materials")
            elif "space" in msg.lower() or "layout" in msg.lower():
                topics.append("spatial")
            elif "light" in msg.lower() or "window" in msg.lower():
                topics.append("environmental")
            else:
                topics.append("general")

        return {
            "evolution": "topic_progression" if len(set(topics)) > 1 else "focused_discussion",
            "topics": topics,
            "topic_count": len(set(topics))
        }

    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type from the current design brief."""
        if not state.current_design_brief:
            return "project"

        # Simple extraction - look for building type in the brief
        brief_lower = state.current_design_brief.lower()
        building_types = ["community center", "office", "house", "school", "hospital", "warehouse", "retail"]

        for building_type in building_types:
            if building_type in brief_lower:
                return building_type

        return "project"

    def _extract_cognitive_flags(self, response_result: Dict, state: ArchMentorState) -> List[str]:
        """Extract cognitive flags from the response and student state."""

        flags = []
        response_strategy = response_result.get("response_strategy", "")

        # Add flags based on strategy
        if response_strategy == "challenging_question":
            flags.append("deep_thinking_encouraged")
        elif response_strategy == "clarifying_guidance":
            flags.append("scaffolding_provided")
        elif response_strategy == "exploratory_question":
            flags.append("exploration_encouraged")

        # Check if response contains questions
        response_text = response_result.get("response_text", "")
        if "?" in response_text:
            flags.append("questioning_promoted")

        # Check conversation length for engagement
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if len(user_messages) > 1:
            flags.append("engagement_maintained")

        return flags

    def _convert_to_agent_response(self, response_result: Dict, state: ArchMentorState,
                                 analysis_result: Dict, context_classification: Dict, gap_type: str) -> AgentResponse:
        """Convert the response result to AgentResponse format."""

        # Calculate enhancement metrics
        enhancement_metrics = self._calculate_enhancement_metrics(response_result, state, analysis_result)

        # Convert cognitive flags
        cognitive_flags = self._convert_cognitive_flags(response_result.get("cognitive_flags", []))

        # Create Socratic response using the correct method
        agent_response = ResponseBuilder.create_socratic_response(
            response_text=response_result.get("response_text", ""),
            cognitive_flags=cognitive_flags,
            metadata={
                "response_strategy": response_result.get("response_strategy", ""),
                "educational_intent": response_result.get("educational_intent", ""),
                "gap_type": gap_type,
                "building_type": self._extract_building_type_from_context(state)
            }
        )

        # Add enhancement metrics manually
        agent_response.enhancement_metrics = enhancement_metrics

        return agent_response

    def _calculate_enhancement_metrics(self, response_result: Dict, state: ArchMentorState, analysis_result: Dict) -> EnhancementMetrics:
        """Calculate cognitive enhancement metrics for Socratic tutoring."""

        response_strategy = response_result.get("response_strategy", "")

        # Calculate scores based on strategy
        if response_strategy == "challenging_question":
            deep_thinking_score = 0.9
            scaffolding_score = 0.6
            engagement_score = 0.8
            metacognitive_score = 0.8
        elif response_strategy == "clarifying_guidance":
            deep_thinking_score = 0.6
            scaffolding_score = 0.9
            engagement_score = 0.7
            metacognitive_score = 0.6
        else:
            deep_thinking_score = 0.7
            scaffolding_score = 0.7
            engagement_score = 0.8
            metacognitive_score = 0.7

        overall_score = (deep_thinking_score + scaffolding_score + engagement_score + metacognitive_score) / 4.0
        scientific_confidence = 0.85  # High confidence in Socratic method

        return EnhancementMetrics(
            cognitive_offloading_prevention_score=0.8,  # Socratic method prevents cognitive offloading
            deep_thinking_engagement_score=deep_thinking_score,
            knowledge_integration_score=0.7,  # Socratic method promotes integration
            scaffolding_effectiveness_score=scaffolding_score,
            learning_progression_score=engagement_score,
            metacognitive_awareness_score=metacognitive_score,
            overall_cognitive_score=overall_score,
            scientific_confidence=scientific_confidence
        )

    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Convert cognitive flags to standardized format."""

        flag_mapping = {
            "deep_thinking_encouraged": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
            "scaffolding_provided": CognitiveFlag.SCAFFOLDING_PROVIDED,
            "exploration_encouraged": CognitiveFlag.EXPLORATION_ENCOURAGED,
            "questioning_promoted": CognitiveFlag.QUESTIONING_PROMOTED,
            "engagement_maintained": CognitiveFlag.ENGAGEMENT_MAINTAINED
        }

        converted_flags = []
        for flag in cognitive_flags:
            if flag in flag_mapping:
                converted_flags.append(flag_mapping[flag])
            else:
                # Default to scaffolding for unknown flags
                converted_flags.append(CognitiveFlag.SCAFFOLDING_PROVIDED)

        return converted_flags

    # AI-powered response generation methods

    async def _generate_ai_clarifying_response(self, last_message: str, building_type: str, state: ArchMentorState) -> str:
        """Generate AI-powered clarifying response."""

        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
        You are a distinguished architectural educator employing the Socratic method to guide student learning through structured inquiry. Your approach is grounded in pedagogical theory and architectural scholarship.

        STUDENT'S EXPRESSION: "{last_message}"
        BUILDING TYPOLOGY: {building_type}

        Craft a complete scholarly response that:
        1. PROVIDES SUPPORTIVE GUIDANCE: Acknowledge their thinking and offer concrete direction
        2. DECONSTRUCTS THE PROBLEM: Break down the complex architectural challenge into manageable parts
        3. OFFERS METHODOLOGICAL INSIGHT: Provide specific design thinking frameworks or approaches they can use
        4. CONNECTS TO THEORY: Reference relevant architectural principles or precedents where helpful
        5. BUILDS CONFIDENCE: Show them how their thinking connects to broader design discourse
        6. ENDS NATURALLY: Ensure the response concludes with a complete thought

        RESPONSE STRUCTURE:
        - Start by acknowledging their specific concern or question
        - Provide 2-3 concrete approaches or frameworks they can use
        - Explain how these connect to their building type and design goals
        - End with a complete synthesis of the guidance
        - THEN ask ONE specific, actionable question that builds directly on the guidance

        Write a complete response (200-250 words) that provides real value and ends naturally before asking your question.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Increased for complete responses
                temperature=0.3
            )

            ai_response = response.choices[0].message.content.strip()

            # Ensure response ends naturally (not mid-sentence)
            if ai_response and not ai_response.endswith(('.', '?', '!')):
                # Find the last complete sentence
                sentences = ai_response.split('.')
                if len(sentences) > 1:
                    ai_response = '.'.join(sentences[:-1]) + '.'

            return ai_response
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            return await self._generate_llm_fallback_question(last_message, building_type, state)

    async def _generate_ai_challenging_question(self, last_message: str, building_type: str, state: ArchMentorState) -> str:
        """Generate AI-powered challenging question."""

        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
        You are a distinguished architectural educator using the Socratic method to challenge and deepen student thinking.

        STUDENT'S MESSAGE: "{last_message}"
        BUILDING TYPE: {building_type}

        Craft a complete scholarly response that:
        1. ACKNOWLEDGES THEIR THINKING: Recognize the validity of their approach while identifying areas for deeper consideration
        2. INTRODUCES COMPLEXITY: Present 2-3 additional factors or constraints they should consider
        3. PROVIDES THEORETICAL CONTEXT: Reference relevant design principles or architectural theory
        4. CHALLENGES ASSUMPTIONS: Question underlying assumptions in a constructive way
        5. OFFERS ALTERNATIVE PERSPECTIVES: Show different ways to approach the same problem
        6. ENDS NATURALLY: Conclude with a complete synthesis before asking your question

        RESPONSE STRUCTURE:
        - Acknowledge their approach and its merits
        - Introduce additional complexity or considerations specific to their building type
        - Provide theoretical grounding or precedent examples
        - End with a complete thought that synthesizes the challenges
        - THEN ask ONE specific, challenging question that requires them to defend or refine their reasoning

        Write a complete response (200-250 words) that challenges them constructively while providing educational value.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Increased for complete responses
                temperature=0.4
            )

            ai_response = response.choices[0].message.content.strip()

            # Ensure response ends naturally (not mid-sentence)
            if ai_response and not ai_response.endswith(('.', '?', '!')):
                # Find the last complete sentence
                sentences = ai_response.split('.')
                if len(sentences) > 1:
                    ai_response = '.'.join(sentences[:-1]) + '.'

            return ai_response
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            return await self._generate_llm_fallback_question(last_message, building_type, state)

    async def _generate_ai_exploratory_question(self, last_message: str, building_type: str, state: ArchMentorState) -> str:
        """Generate AI-powered exploratory question."""

        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
        You are a Socratic tutor encouraging exploration in architecture.

        STUDENT'S MESSAGE: "{last_message}"
        BUILDING TYPE: {building_type}

        Generate an exploratory question that:
        1. Opens up new avenues of thinking
        2. Encourages creative exploration
        3. Connects to broader design principles
        4. Invites them to consider alternatives

        Keep it under 100 words and be inspiring.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            return await self._generate_llm_fallback_question(last_message, building_type, state)

    async def _generate_ai_adaptive_question(self, last_message: str, building_type: str, state: ArchMentorState) -> str:
        """Generate AI-powered adaptive question."""

        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
        You are an accomplished architectural educator employing adaptive Socratic pedagogy to advance student learning through strategic inquiry.

        STUDENT'S CONTRIBUTION: "{last_message}"
        BUILDING TYPOLOGY: {building_type}

        Generate a sophisticated adaptive question that:
        1. Builds substantively upon their demonstrated understanding and insights
        2. Propels their design thinking toward greater complexity and nuance
        3. Connects explicitly to established architectural theory, principles, or methodologies
        4. Challenges them to synthesize concepts and develop more rigorous design reasoning
        5. Encourages critical examination of assumptions and design implications

        Frame your inquiry within appropriate architectural discourse while maintaining accessibility. Be intellectually challenging yet supportive.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            return await self._generate_llm_fallback_question(last_message, building_type, state)

    async def _generate_llm_fallback_question(self, user_input: str, building_type: str, state: ArchMentorState) -> str:
        """Generate LLM-based fallback question instead of hardcoded responses."""

        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Get recent context from conversation
        recent_context = ""
        if hasattr(state, 'messages') and state.messages:
            recent_messages = state.messages[-3:]  # Last 3 messages
            recent_context = " | ".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}" for msg in recent_messages])

        prompt = f"""
        You are a Socratic tutor helping an architecture student. The LLM generation failed, so you need to create a thoughtful fallback question.

        STUDENT'S INPUT: "{user_input}"
        BUILDING TYPE: {building_type}
        RECENT CONTEXT: {recent_context}

        Generate a thoughtful Socratic question that:
        1. Directly relates to their specific input and building type
        2. Encourages deeper thinking about their design challenge
        3. Builds on the conversation context if available
        4. Avoids generic templates - be specific to their situation
        5. Helps them explore the implications or considerations they might have missed

        Keep it under 50 words and make it genuinely helpful for their specific situation.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.6
            )

            fallback_question = response.choices[0].message.content.strip()

            if not fallback_question.endswith('?'):
                fallback_question += '?'

            return fallback_question

        except Exception as e:
            print(f"⚠️ LLM fallback question generation failed: {e}")
            # Only as last resort, use a contextual template
            return f"What specific aspect of {user_input.lower() if user_input else 'your design'} would be most important to consider for your {building_type}?"

    def _generate_fallback_response(self, state: ArchMentorState, context_classification: Dict,
                                  analysis_result: Dict, gap_type: str) -> AgentResponse:
        """Generate fallback response when no user input is available."""

        building_type = self._extract_building_type_from_context(state)

        response_text = f"""Let's explore your {building_type} project together through some thoughtful questions.

What aspects of your design are you most excited about? What challenges are you anticipating?

I'm here to help you think through the complexities and discover insights through questioning."""

        return ResponseBuilder.create_socratic_response(
            response_text=response_text,
            cognitive_flags=[],
            metadata={"response_type": "fallback_prompt", "building_type": building_type}
        )

    # Backward compatibility method
    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any],
                              context_classification: Optional[Dict] = None, domain_expert_result: Optional[Dict] = None) -> AgentResponse:
        """Backward compatibility method for original API."""

        # Convert to new API format
        gap_type = "general"
        if analysis_result and "cognitive_flags" in analysis_result:
            cognitive_flags = analysis_result["cognitive_flags"]
            if cognitive_flags:
                gap_type = cognitive_flags[0].replace("needs_", "").replace("_guidance", "")

        return await self.provide_guidance(state, context_classification or {}, analysis_result, gap_type)

    # Phase-based assessment methods

    def _should_use_phase_based_approach(self, state: ArchMentorState, context_classification: Dict) -> bool:
        """Determine if phase-based assessment should be used."""

        if not self.phase_manager:
            return False

        # Use phase-based approach for structured learning sessions
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']

        # Enable phase-based approach if:
        # 1. There's a clear design brief
        # 2. The conversation has progressed beyond initial greetings
        # 3. The student seems engaged in design thinking

        has_design_brief = bool(state.current_design_brief)
        sufficient_conversation = len(user_messages) >= 1
        design_focused = any(keyword in " ".join(user_messages).lower()
                           for keyword in ["design", "building", "space", "architecture", "project"])

        return has_design_brief and sufficient_conversation and design_focused

    async def _generate_phase_based_response(self, state: ArchMentorState, context_classification: Dict,
                                           analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate response using phase-based Socratic assessment."""

        # Detect current phase and step
        current_phase, current_step = self.phase_manager.detect_current_phase(state)

        # Extract building type
        building_type = self._extract_building_type_from_context(state)

        print(f"   📋 Current phase: {current_phase.value}")
        print(f"   📋 Current step: {current_step.value}")
        print(f"   🏗️ Building type: {building_type}")

        # Generate Socratic question for current phase and step
        context = {
            "building_type": building_type,
            "context_element": "character",  # Could be extracted from conversation
            "difficulty_level": context_classification.get("understanding_level", "moderate")
        }

        socratic_question = self.phase_manager.generate_socratic_question(
            current_phase, current_step, building_type, context
        )

        # Check if this is a response to a previous question (for assessment)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if len(user_messages) > 1:
            # This might be a response to assess
            previous_response = user_messages[-1]

            # For now, we'll generate the next question
            # In a full implementation, we'd assess the previous response first
            response_text = socratic_question.question_text
        else:
            # First question in the phase
            response_text = socratic_question.question_text

        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "phase_based_socratic",
            "response_strategy": f"phase_{current_phase.value}_step_{current_step.value}",
            "educational_intent": f"Guide through {current_phase.value} phase using Socratic method",
            "phase_info": {
                "current_phase": current_phase.value,
                "current_step": current_step.value,
                "assessment_criteria": socratic_question.assessment_criteria,
                "expected_elements": socratic_question.expected_elements
            },
            "building_type": building_type,
            "socratic_question": socratic_question.__dict__
        }

    # Cleanup
    def __del__(self):
        """Cleanup method."""
        try:
            self.telemetry.log_agent_end("cleanup")
        except:
            pass 