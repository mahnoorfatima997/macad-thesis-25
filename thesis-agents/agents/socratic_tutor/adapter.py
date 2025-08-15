"""
Socratic Tutor Agent Adapter - streamlined modular version.

This adapter maintains backward compatibility while delegating to processor modules.
"""

import sys
import os
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from phase_assessment import PhaseAssessmentManager, DesignPhase, SocraticStep

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
    
    def __init__(self, domain: str = "architecture") -> None:
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
            from phase_assessment import PhaseAssessmentManager
            self.phase_manager: Optional['PhaseAssessmentManager'] = PhaseAssessmentManager()
            print(f"   📋 Phase-based assessment system enabled")
        else:
            self.phase_manager: Optional['PhaseAssessmentManager'] = None
            print(f"   ⚠️ Phase-based assessment system disabled")

        self.telemetry.log_agent_end("__init__")
        print(f"🤔 {self.name} initialized for domain: {domain}")

    # ENHANCEMENT: Technical detection methods ported from FROMOLDREPO
    def _looks_technical(self, text: str) -> bool:
        """Heuristic to detect technical questions from user text.

        Ported from FROMOLDREPO lines 618-627.
        """
        if not text:
            return False
        t = text.lower()
        indicators = [
            "requirement", "requirements", "code", "codes", "ada", "standard", "standards",
            "regulation", "slope", "width", "landing", "clearance", "egress",
        ]
        return any(k in t for k in indicators)

    def _looks_design_guidance(self, text: str) -> bool:
        """Heuristic to detect design-guidance phrasing.

        Ported from FROMOLDREPO lines 629-638.
        """
        if not text:
            return False
        t = text.lower()
        patterns = [
            "how should", "how can i", "how do i", "how to", "how might",
            "what direction", "which direction", "where should", "design direction",
        ]
        return any(p in t for p in patterns)

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
        print(f"🔍 DEBUG: Socratic tutor received state.building_type: {getattr(state, 'building_type', 'NOT_SET')}")
        print(f"🔍 DEBUG: Socratic tutor received state.messages count: {len(getattr(state, 'messages', []))}")
        print(f"🔍 DEBUG: Socratic tutor received state.current_design_brief: {getattr(state, 'current_design_brief', 'NOT_SET')}")
        
        # Check if we have routing information to determine response type
        routing_path = context_classification.get("routing_path", "unknown")
        print(f"🔍 DEBUG: Routing path detected: {routing_path}")
        
        self.telemetry.log_agent_start("provide_guidance")
        
        try:
            print(f"\n🤔 {self.name} generating sophisticated Socratic response...")

            # Get user's last input
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            user_input = user_messages[-1] if user_messages else ""

            if not user_input:
                return await self._generate_fallback_response(state, analysis_result, gap_type)

            # AGENT COORDINATION: Check for other agents' responses to build upon
            coordination_context = context_classification.get("agent_coordination", {})
            other_responses = coordination_context.get("other_responses", {})

            if other_responses:
                print(f"🤝 Coordination: Building Socratic questions upon {list(other_responses.keys())} responses")
                # Extract domain knowledge to create questions about
                domain_knowledge = other_responses.get("domain_expert", {}).get("response_text", "")
                if domain_knowledge:
                    print(f"   📚 Domain knowledge available: {len(domain_knowledge)} chars")
                    # Store for use in question generation
                    context_classification["domain_knowledge_context"] = domain_knowledge[:500]  # First 500 chars

            # ENHANCED ROUTE-AWARE RESPONSE GENERATION WITH GAMIFICATION
            if routing_path == "supportive_scaffolding":
                print(f"   🆘 Using SUPPORTIVE SCAFFOLDING approach")
                response_result = await self._generate_supportive_scaffolding_response(state, context_classification, analysis_result, gap_type)
            elif routing_path == "knowledge_only":
                print(f"   📚 Using KNOWLEDGE ONLY approach")
                response_result = await self._generate_knowledge_only_response(state, context_classification, analysis_result, gap_type)
            elif routing_path == "balanced_guidance":
                print(f"   ⚖️ Using BALANCED GUIDANCE approach")
                response_result = await self._generate_balanced_guidance_response(state, context_classification, analysis_result, gap_type)
            elif routing_path == "socratic_exploration":
                print(f"   ❓ Using SOCRATIC EXPLORATION approach")
                # Check for gamified behavior enhancement
                gamified_behavior = context_classification.get("gamified_behavior", "")
                if gamified_behavior == "visual_choice_reasoning":
                    print(f"   🎮 Using GAMIFIED visual choice reasoning")
                    response_result = await self._generate_visual_choice_response(state, context_classification, analysis_result, gap_type)
                elif self.phase_manager and self._should_use_phase_based_approach(state, context_classification):
                    print(f"   🎯 Using phase-based Socratic assessment")
                    response_result = await self._generate_phase_based_response(state, context_classification, analysis_result, gap_type)
                else:
                    print(f"   🔄 Using default adaptive approach for route: {routing_path}")
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
            elif routing_path == "cognitive_challenge":
                print(f"   ⚡ Using COGNITIVE CHALLENGE approach")
                gamified_behavior = context_classification.get("gamified_behavior", "")
                if gamified_behavior == "constraint_storm_challenge":
                    print(f"   🌩️ Using CONSTRAINT STORM challenge")
                    response_result = await self._generate_constraint_challenge_response(state, context_classification, analysis_result, gap_type)
                else:
                    response_result = await self._generate_cognitive_challenge_response(state, context_classification, analysis_result, gap_type)
            else:
                print(f"   🔄 Using default adaptive approach for route: {routing_path}")
                response_result = await self._generate_adaptive_socratic_response(state, context_classification, analysis_result, gap_type)

            # Add cognitive flags
            cognitive_flags = self._extract_cognitive_flags(response_result, state)

            # Handle both Dict and AgentResponse types for adding cognitive flags
            if isinstance(response_result, AgentResponse):
                # If it's already an AgentResponse, we don't need to add flags here
                # They will be handled in the conversion process
                pass
            elif isinstance(response_result, dict):
                response_result["cognitive_flags"] = cognitive_flags
            else:
                # Convert to dict if it's neither
                response_result = {"response_text": str(response_result), "cognitive_flags": cognitive_flags}

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

    # GAMIFIED RESPONSE GENERATION METHODS

    async def _generate_visual_choice_response(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate gamified visual choice response for Socratic exploration."""
        try:
            user_input = context_classification.get("user_input", "")
            building_type = self._extract_building_type_from_context(state)

            # Extract topic from user input
            topic = self._extract_main_topic(user_input)

            # Generate enhanced visual choice prompt for spatial organization
            prompt = f"""
            Create an engaging Socratic exploration response using visual choices for a {building_type} design project.

            User's input: "{user_input}"
            Main topic: {topic}
            Building type: {building_type}

            SPECIFIC GUIDANCE FOR SPATIAL ORGANIZATION:
            - Focus on spatial relationships, circulation patterns, and functional zones
            - Present 3 distinct organizational approaches with clear visual metaphors
            - Connect choices to the specific needs of a {building_type}
            - Use architectural terminology appropriately

            Follow this structure:
            1. Acknowledge their spatial thinking with enthusiasm
            2. Present 3 spatial organization approaches:
               🌿 A) [Organic/flowing approach with description]
               🏛️ B) [Structured/zoned approach with description]
               🌟 C) [Hybrid/flexible approach with description]
            3. Ask them to choose and explain their reasoning
            4. Follow up with deeper questions about their choice

            Make it engaging and gamified but educationally meaningful.
            Keep the tone collaborative and curious, not childish.
            Focus on spatial design principles and user experience.
            """

            response = await self._generate_llm_response(prompt, state, analysis_result)

            return {
                "response_text": response,
                "response_strategy": "visual_choice_reasoning",
                "educational_intent": "spatial_reasoning_development",
                "gamified_behavior": "visual_choice_reasoning",
                "cognitive_flags": ["choice_based_learning", "visual_thinking", "reasoning_development"]
            }

        except Exception as e:
            self.telemetry.log_error(f"Visual choice response generation failed: {str(e)}")
            return await self._generate_fallback_response(state, analysis_result, gap_type)

    async def _generate_constraint_challenge_response(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate gamified constraint storm challenge response."""
        try:
            user_input = context_classification.get("user_input", "")
            building_type = self._extract_building_type_from_context(state)

            # Generate constraint challenge
            prompt = f"""
            Create an engaging constraint challenge for a {building_type} design project.

            User's input: "{user_input}"

            Follow this structure:
            1. Acknowledge their current thinking positively
            2. Introduce a surprising but realistic constraint (budget cut, site change, new requirement)
            3. Present 3-4 creative response options (A, B, C, D format with emojis)
            4. Ask for their gut reaction and reasoning
            5. Set up exploration of the implications

            Make the constraint challenging but not discouraging. Focus on creative problem-solving.
            Use emojis for visual appeal but keep the tone professional and engaging.
            """

            response = await self._generate_llm_response(prompt, state, analysis_result)

            return {
                "response_text": response,
                "response_strategy": "constraint_storm_challenge",
                "educational_intent": "adaptive_thinking_development",
                "gamified_behavior": "constraint_storm_challenge",
                "cognitive_flags": ["constraint_thinking", "creative_problem_solving", "adaptive_reasoning"]
            }

        except Exception as e:
            self.telemetry.log_error(f"Constraint challenge response generation failed: {str(e)}")
            return self._generate_fallback_dict_response(state, gap_type)

    async def _generate_cognitive_challenge_response(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate cognitive challenge response for low engagement."""
        try:
            user_input = context_classification.get("user_input", "")
            building_type = self._extract_building_type_from_context(state)

            prompt = f"""
            Create a cognitive challenge response for a student showing low engagement or overconfidence.

            User's input: "{user_input}"
            Building type: {building_type}

            The student needs intellectual stimulation. Create a response that:
            1. Acknowledges their current position
            2. Introduces a thought-provoking challenge or perspective shift
            3. Engages them with choices or scenarios
            4. Pushes them to think more deeply

            Make it challenging but supportive. Use engaging language and strategic emojis.
            """

            response = await self._generate_llm_response(prompt, state, analysis_result)

            return {
                "response_text": response,
                "response_strategy": "cognitive_challenge",
                "educational_intent": "engagement_stimulation",
                "cognitive_flags": ["challenge_thinking", "engagement_boost", "depth_development"]
            }

        except Exception as e:
            self.telemetry.log_error(f"Cognitive challenge response generation failed: {str(e)}")
            return self._generate_fallback_dict_response(state, gap_type)

    def _extract_main_topic(self, user_input: str) -> str:
        """Extract main architectural topic from user input."""
        user_input_lower = user_input.lower()

        # Topic patterns for architecture
        topic_patterns = {
            "circulation": ["circulation", "movement", "flow", "wayfinding", "navigation"],
            "lighting": ["lighting", "daylight", "natural light", "illumination"],
            "materials": ["materials", "material", "concrete", "steel", "wood", "glass"],
            "sustainability": ["sustainability", "sustainable", "green", "environmental", "energy"],
            "community": ["community", "social", "gathering", "interaction", "public"],
            "healing": ["healing", "therapeutic", "wellness", "health", "recovery"],
            "structure": ["structure", "structural", "columns", "beams", "foundation"],
            "space": ["space", "spatial", "room", "area", "zone", "layout"],
            "courtyards": ["courtyard", "outdoor", "garden", "landscape", "nature"],
            "accessibility": ["accessibility", "accessible", "universal", "inclusive"]
        }

        for topic, keywords in topic_patterns.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return topic

        return "design"  # Default topic
    
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
        """Generate response based on the determined strategy.

        ENHANCED: Now includes technical and design guidance detection from FROMOLDREPO.
        """

        # Get user's last message for enhanced detection
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # ENHANCEMENT: Check for technical questions first
        if self._looks_technical(last_message):
            # If we have domain expert results, generate technical followup
            domain_expert_result = getattr(state, "domain_expert_result", {})
            if domain_expert_result and domain_expert_result.get("response_text", ""):
                return await self._generate_technical_followup(state, domain_expert_result)

        # ENHANCEMENT: Check for design guidance requests - DISABLED to prevent hardcoded fallback override
        # The hardcoded synthesis was overriding proper LLM responses, so we let the normal flow handle design guidance
        # if self._looks_design_guidance(last_message):
        #     domain_expert_result = getattr(state, "domain_expert_result", {})
        #     return await self._generate_design_guidance_synthesis(state, analysis_result, domain_expert_result)

        # Original strategy-based routing
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

        metadata = {
            "response_type": "clarifying_guidance",
            "response_strategy": "clarifying_guidance",
            "educational_intent": "build_understanding",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

        return {
            "response_text": response_text,
            "response_type": "challenging_question",
            "response_strategy": "challenging_question",
            "educational_intent": "Challenge overconfident thinking",
            "building_type": building_type,
            "cognitive_flags": ["deep_thinking_encouraged", "overconfidence_addressed"]
        }

    async def _generate_challenging_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate challenging questions for overconfident students."""

        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # Use AI to generate challenging question
        response_text = await self._generate_ai_challenging_question(last_message, building_type, state)

        metadata = {
            "response_type": "challenging_question",
            "response_strategy": "challenging_question",
            "educational_intent": "challenge_assumptions",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

        return {
            "response_text": response_text,
            "response_type": "challenging_question",
            "response_strategy": "challenging_question",
            "educational_intent": "Challenge and deepen thinking",
            "building_type": building_type,
            "cognitive_flags": ["deep_thinking_encouraged", "challenge_presented"]
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

        metadata = {
            "response_type": "exploratory_question",
            "response_strategy": "exploratory_question",
            "educational_intent": "encourage_exploration",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

        return {
            "response_text": response_text,
            "response_type": "exploratory_question",
            "response_strategy": "exploratory_question",
            "educational_intent": "Encourage exploration and investigation",
            "building_type": building_type,
            "cognitive_flags": ["exploration_encouraged", "curiosity_stimulated"]
        }

    async def _generate_adaptive_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate adaptive questions based on current context."""

        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_message = user_messages[-1] if user_messages else ""

        # Use AI to generate adaptive question
        response_text = await self._generate_ai_adaptive_question(last_message, building_type, state)

        metadata = {
            "response_type": "adaptive_question",
            "response_strategy": "adaptive_question",
            "educational_intent": "adaptive_guidance",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }

        return {
            "response_text": response_text,
            "response_type": "adaptive_question",
            "response_strategy": "adaptive_question",
            "educational_intent": "Adapt to current context and needs",
            "building_type": building_type,
            "cognitive_flags": ["adaptive_guidance", "context_responsive"]
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

    def _extract_building_type_from_context(self, state) -> str:
        """
        Get building type from state - NO MORE DETECTION, just retrieval.
        Building type is now centrally managed in conversation_progression.py
        """
        # PRIORITY 1: Use conversation continuity context (highest confidence)
        if hasattr(state, 'student_state') and hasattr(state.student_state, 'conversation_context'):
            context = state.student_state.conversation_context
            if context.detected_building_type and context.building_type_confidence > 0.7:
                return context.detected_building_type

        # PRIORITY 2: Use state.building_type if available
        if hasattr(state, 'building_type') and state.building_type and state.building_type != "unknown":
            return state.building_type
        
        # PRIORITY 2: Use state.building_type from student_state if available
        if hasattr(state, 'student_state') and hasattr(state.student_state, 'building_type'):
            if state.student_state.building_type and state.student_state.building_type != "unknown":
                return state.student_state.building_type
        
        # PRIORITY 3: Use building_type from context_analysis if available
        if hasattr(state, 'context_analysis') and state.context_analysis:
            context_analysis = state.context_analysis
            if isinstance(context_analysis, dict) and context_analysis.get('building_type'):
                building_type = context_analysis['building_type']
                if building_type != "unknown":
                    return building_type

        # PRIORITY 4: Extract from current_design_brief if available
        if hasattr(state, 'student_state') and hasattr(state.student_state, 'current_design_brief'):
            brief = state.student_state.current_design_brief
            if brief and "community_center" in brief.lower():
                return "community_center"
            elif brief and "community center" in brief.lower():
                return "community_center"

        # PRIORITY 5: Extract from current_design_brief directly on state
        if hasattr(state, 'current_design_brief') and state.current_design_brief:
            brief = state.current_design_brief
            if brief and "community_center" in brief.lower():
                return "community_center"
            elif brief and "community center" in brief.lower():
                return "community_center"

        # FALLBACK: Return unknown instead of mixed_use
        return "unknown"

    async def _generate_contextual_followup(self, user_response: str, base_question: 'SocraticQuestion',
                                    current_phase: 'DesignPhase', building_type: str) -> str:
        """Generate a contextual follow-up using LLM instead of hardcoded templates."""

        print(f"🔍 DEBUG: Generating contextual followup for building_type: {building_type}")
        print(f"🔍 DEBUG: User response: {user_response[:100]}...")
        print(f"🔍 DEBUG: Current phase: {current_phase.value}")

        try:
            # Build context for AI generation
            context = f"""
You are an expert architectural mentor using the Socratic method to guide a student through their design project.

STUDENT'S RESPONSE: "{user_response}"

CURRENT PHASE: {current_phase.value}
BUILDING TYPE: {building_type}
BASE QUESTION: {base_question.question_text}

YOUR TASK:
Generate a thoughtful, contextual response that:
1. ACKNOWLEDGES what the student just said (be specific about their points)
2. BUILDS ON their specific response (reference their exact words and ideas)
3. CONNECTS to their {building_type} project context
4. ENCOURAGES deeper thinking about what they've shared
5. RELATES to the current design phase

IMPORTANT: 
- Reference specific details from their response (age range, specific needs, challenges mentioned)
- Build on their exact ideas (e.g., "Your focus on Copenhagen's wind and rain protection...")
- Don't ask generic questions - engage with what they said
- Make it relevant to their {building_type} project
- Keep it conversational and encouraging
- Make it 2-3 sentences that show you understand their input

Generate a contextual response that builds on their input:
"""
            
            print(f"🔍 DEBUG: Attempting LLM generation with context length: {len(context)}")
            
            # Generate response using AI
            response = await self.client.generate_completion([
                {"role": "user", "content": context}
            ], max_tokens=150, temperature=0.7)
            
            print(f"🔍 DEBUG: LLM response received: {response}")
            
            ai_generated_response = response.get("content", "").strip()
            if not ai_generated_response or len(ai_generated_response) < 20:
                print(f"🔍 DEBUG: LLM response too short, using fallback")
                # Fallback to a generic but building-type-appropriate question
                return self._generate_fallback_contextual_followup(user_response, building_type, current_phase)
            
            print(f"🔍 DEBUG: Using LLM-generated response: {ai_generated_response}")
            return ai_generated_response
            
        except Exception as e:
            print(f"🔍 DEBUG: AI generation failed in contextual followup: {e}")
            print(f"🔍 DEBUG: Exception type: {type(e)}")
            # Fallback to generic but appropriate response
            return self._generate_fallback_contextual_followup(user_response, building_type, current_phase)
    
    def _generate_fallback_contextual_followup(self, user_response: str, building_type: str, current_phase: 'DesignPhase') -> str:
        """Generate a fallback contextual followup that's truly generic and flexible."""
        
        # Truly generic fallback that works for any building type and any user response
        # No hardcoded assumptions about specific content, age ranges, locations, etc.
        return f"Your response shows thoughtful consideration of your {building_type} project. I can see you've thought through important aspects of your design. What specific element from what you've described would you like to explore further or develop in more detail?"

    def _get_next_step(self, current_step: Any) -> Any:
        """Get the next Socratic step in sequence."""
        try:
            from phase_assessment.phase_manager import SocraticStep

            step_order = [
                SocraticStep.INITIAL_CONTEXT_REASONING,
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
                SocraticStep.SOCRATIC_QUESTIONING,
                SocraticStep.METACOGNITIVE_PROMPT
            ]

            try:
                current_index = step_order.index(current_step)
                if current_index < len(step_order) - 1:
                    return step_order[current_index + 1]
            except ValueError:
                pass

            return current_step  # Stay at current step if can't advance
        except ImportError:
            return current_step

    def _extract_cognitive_flags(self, response_result: Union[Dict, AgentResponse], state: ArchMentorState) -> List[str]:
        """Extract cognitive flags from the response and student state."""

        flags = []

        # Handle both Dict and AgentResponse types
        if isinstance(response_result, AgentResponse):
            response_strategy = response_result.metadata.get("response_strategy", "")
            response_text = response_result.response_text
        elif isinstance(response_result, dict):
            response_strategy = response_result.get("response_strategy", "")
            response_text = response_result.get("response_text", "")
        else:
            response_strategy = ""
            response_text = str(response_result)

        # Add flags based on strategy
        if response_strategy == "challenging_question":
            flags.append("deep_thinking_encouraged")
        elif response_strategy == "clarifying_guidance":
            flags.append("scaffolding_provided")
        elif response_strategy == "exploratory_question":
            flags.append("exploration_encouraged")

        # Check if response contains questions
        if "?" in response_text:
            flags.append("questioning_promoted")

        # Check conversation length for engagement
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if len(user_messages) > 1:
            flags.append("engagement_maintained")

        return flags

    def _convert_to_agent_response(self, response_result: Union[Dict, AgentResponse], state: ArchMentorState,
                                 analysis_result: Dict, context_classification: Dict, gap_type: str) -> AgentResponse:
        """Convert the response result to AgentResponse format."""

        # If already an AgentResponse, return it
        if isinstance(response_result, AgentResponse):
            return response_result

        # Ensure response_result is a dict
        if not isinstance(response_result, dict):
            response_result = {"response_text": str(response_result), "response_type": "fallback"}

        # Handle both dict and AgentResponse types
        if isinstance(response_result, AgentResponse):
            # If already an AgentResponse, return it directly
            return response_result

        # Ensure response_result is a dictionary
        if not isinstance(response_result, dict):
            response_result = {"response_text": str(response_result), "response_type": "fallback"}

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
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=200, temperature=0.7)
            
            ai_generated_response = response.get("content", "").strip()

            # Ensure response ends naturally (not mid-sentence)
            if ai_generated_response and not ai_generated_response.endswith(('.', '?', '!')):
                # Find the last complete sentence
                sentences = ai_generated_response.split('.')
                if len(sentences) > 1:
                    ai_generated_response = '.'.join(sentences[:-1]) + '.'

            return ai_generated_response
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            self.telemetry.log_error(f"AI challenging question generation failed: {str(e)}")
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
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=200, temperature=0.7)
            
            ai_generated_response = response.get("content", "").strip()

            # Ensure response ends naturally (not mid-sentence)
            if ai_generated_response and not ai_generated_response.endswith(('.', '?', '!')):
                # Find the last complete sentence
                sentences = ai_generated_response.split('.')
                if len(sentences) > 1:
                    ai_generated_response = '.'.join(sentences[:-1]) + '.'

            return ai_generated_response
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            self.telemetry.log_error(f"AI exploratory question generation failed: {str(e)}")
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
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=150, temperature=0.7)
            return response.get("content", "").strip()
        except Exception as e:
            # Generate LLM-based fallback question instead of hardcoded
            self.telemetry.log_error(f"AI adaptive question generation failed: {str(e)}")
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
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=150, temperature=0.7)
            return response.get("content", "").strip()
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
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=100, temperature=0.7)

            fallback_question = response.get("content", "").strip()

            if not fallback_question.endswith('?'):
                fallback_question += '?'

            return fallback_question

        except Exception as e:
            print(f"⚠️ LLM fallback question generation failed: {e}")
            # Only as last resort, use a contextual template
            return f"What specific aspect of {user_input.lower() if user_input else 'your design'} would be most important to consider for your {building_type}?"

    async def _generate_fallback_response(self, state: ArchMentorState, 
                                  analysis_result: Dict, gap_type: str) -> AgentResponse:
        """Generate fallback response when no user input is available using LLM instead of hardcoded template."""

        building_type = self._extract_building_type_from_context(state)

        try:
            # Generate dynamic fallback response using LLM
            prompt = f"""
            You are an expert architectural mentor helping a student with their {building_type} project.
            
            CONTEXT:
            - Building type: {building_type}
            - Gap type: {gap_type}
            - This is a fallback response when no specific user input is available
            
            TASK: Generate an engaging, encouraging opening message that:
            1. Welcomes the student to explore their {building_type} project
            2. Asks thoughtful, open-ended questions to get them thinking
            3. Shows enthusiasm for their architectural journey
            4. Encourages them to share their thoughts and challenges
            5. Sounds natural and conversational, not like a template
            
            RESPONSE: Write a welcoming message with 2-3 thoughtful questions (2-3 sentences total).
            """
            
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=200, temperature=0.7)
            
            ai_generated_response = response.get("content", "").strip()
            
            # Fallback to template if LLM fails
            if not ai_generated_response or len(ai_generated_response) < 30:
                response_text = f"Let's explore your {building_type} project. What would you like to focus on next?"
            else:
                response_text = ai_generated_response
                
        except Exception as e:
            # Fallback to template if LLM fails
            response_text = f"Let's explore your {building_type} project. What would you like to focus on next?"

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

        # ENHANCED: More flexible conditions for phase-based approach
        has_design_brief = bool(state.current_design_brief)
        sufficient_conversation = len(user_messages) >= 1
        design_focused = any(keyword in " ".join(user_messages).lower()
                           for keyword in ["design", "building", "space", "architecture", "project", "museum", "library", "school", "hospital", "office", "residential", "commercial", "community", "center"])

        # Use phase-based approach if we have design focus OR a design brief (not both required)
        return (has_design_brief or design_focused) and sufficient_conversation

    async def _generate_phase_based_response(self, state: ArchMentorState, context_classification: Dict,
                                           analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate response using phase-based Socratic assessment."""

        # ENHANCED: Use phase info from orchestrator if available, otherwise detect
        if hasattr(state, 'phase_info') and state.phase_info:
            # Use phase information from dashboard's phase progression system
            dashboard_phase_info = state.phase_info
            current_phase_name = dashboard_phase_info.get("current_phase", "ideation")
            current_step_name = dashboard_phase_info.get("step", "initial_context_reasoning")

            # Convert string names to enum values
            try:
                current_phase = DesignPhase(current_phase_name)
                current_step = SocraticStep(current_step_name)
                print(f"🎯 SOCRATIC: Using dashboard phase info: {current_phase_name} - {current_step_name}")
            except (ValueError, NameError):
                # Fallback if enum conversion fails or enums not available
                current_phase = DesignPhase.IDEATION if 'DesignPhase' in globals() else None
                current_step = SocraticStep.INITIAL_CONTEXT_REASONING if 'SocraticStep' in globals() else None
                if current_phase is None or current_step is None:
                    # If enums not available, use fallback detection
                    if not self.phase_manager:
                        raise ValueError("Phase manager not available")
                    current_phase, current_step = self.phase_manager.detect_current_phase(state)
                print(f"⚠️ SOCRATIC: Failed to convert phase info, using fallback")
        else:
            # Fallback to phase detection if no dashboard info available
            if not self.phase_manager:
                raise ValueError("Phase manager not available")
            current_phase, current_step = self.phase_manager.detect_current_phase(state)
            print(f"🔍 SOCRATIC: Using phase detection: {current_phase.value} - {current_step.value}")

        # Extract building type
        building_type = self._extract_building_type_from_context(state)

        print(f"🔍 DEBUG: Building type extracted: {building_type}")
        print(f"🔍 DEBUG: State building_type: {getattr(state, 'building_type', 'NOT_SET')}")
        print(f"🔍 DEBUG: State current_design_brief: {getattr(state, 'current_design_brief', 'NOT_SET')}")
        print(f"🔍 DEBUG: State messages count: {len(getattr(state, 'messages', []))}")

        print(f"   📋 Current phase: {current_phase.value}")
        print(f"   📋 Current step: {current_step.value}")
        print(f"   🏗️ Building type: {building_type}")

        # Generate Socratic question for current phase and step
        context = {
            "building_type": building_type,
            "context_element": "character",  # Could be extracted from conversation
            "difficulty_level": context_classification.get("understanding_level", "moderate")
        }

        socratic_question = await self.phase_manager.generate_socratic_question(
            current_phase, current_step, building_type, context
        )

        # ENHANCED: Actually respond to what the user said instead of ignoring it
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if len(user_messages) > 1:
            # User has provided a response - acknowledge it and build on it
            user_response = user_messages[-1]

            # Check if user provided substantial response (indicates step completion)
            if len(user_response.split()) > 15:  # Detailed response
                print(f"   🔍 User provided substantial response, focusing on building on their input")
                # Generate a contextual response that builds on their specific input
                response_text = await self._generate_contextual_followup(
                    user_response, socratic_question, current_phase, building_type
                )
            else:
                # Shorter response - use phase-based question but make it contextual
                response_text = await self._generate_contextual_followup(
                    user_response, socratic_question, current_phase, building_type
                )
        else:
            # First question in the phase
            response_text = socratic_question.question_text

        # Return dictionary for consistency with other response generation methods
        return {
            "response_text": response_text,
            "response_type": "phase_based_socratic",
            "response_strategy": f"phase_{current_phase.value}_step_{current_step.value}",
            "educational_intent": f"Guide through {current_phase.value} phase using Socratic method",
            "phase_info": {
                "current_phase": current_phase.value,
                "current_step": current_step.value,
                "expected_elements": socratic_question.expected_elements
            },
            "building_type": building_type,
            "socratic_question": socratic_question.__dict__,
            "cognitive_flags": ["phase_based_learning", "socratic_questioning", "guided_exploration"]
        }

    # ENHANCEMENT: Technical followup generation ported from FROMOLDREPO
    async def _generate_technical_followup(self, state: ArchMentorState, domain_expert_result: Dict[str, Any]) -> Dict[str, Any]:
        """Produce 1–2 concise application probes referencing DomainExpert key points.

        Ported from FROMOLDREPO lines 640-672.
        """
        building_type = self._extract_building_type_from_context(state)
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break

        # Try to extract short labels from DomainExpert response
        text = (domain_expert_result or {}).get("response_text", "").strip()
        labels = []
        if text:
            import re
            bullets = re.findall(r"^\s*[-•]\s*(.+)$", text, flags=re.MULTILINE)
            for b in bullets[:3]:
                # Use first 4 words as a short label
                words = b.split()
                labels.append(" ".join(words[:4]))

        topic = self._extract_main_topic(last_message) if last_message else "your focus"
        if not labels:
            labels = [f"{topic} detail", f"{topic} compliance"]

        q1 = f"Given {labels[0]}, where in your {building_type} does this most affect the layout or user flow?"
        q2 = f"How will you verify {labels[1]} meets your project's constraints?"

        response_text = f"Apply these points in context:\n{q1}\n{q2}"

        return {
            "response_text": response_text,
            "response_type": "technical_followup",
        }

    async def _generate_design_guidance_synthesis(self, state: ArchMentorState, analysis_result: Dict[str, Any], domain_expert_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate design guidance synthesis with Insight/Direction/Watch format.

        Ported from FROMOLDREPO lines 673-715.
        """
        building_type = self._extract_building_type_from_context(state)
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break

        topic = self._extract_main_topic(last_message) if last_message else "design approach"

        items = []

        # Insight from domain expert or analysis - ENHANCED: Use multiple sentences
        domain_text = (domain_expert_result or {}).get("response_text", "")
        if domain_text:
            # Extract first 2-3 meaningful sentences for richer insight
            sentences = [s.strip() for s in domain_text.split('.') if s.strip()]
            if len(sentences) >= 3:
                insight = '. '.join(sentences[:3]) + '.'
            elif len(sentences) >= 2:
                insight = '. '.join(sentences[:2]) + '.'
            elif sentences:
                insight = sentences[0] + '.'
            else:
                insight = domain_text[:200]

            # Limit length but preserve complete sentences
            if len(insight) > 600:
                insight = insight[:600].rstrip()
                last_period = insight.rfind('.')
                if last_period > 400:  # Keep if we have substantial content
                    insight = insight[:last_period + 1]

            items.append(f"- Insight: {insight}")

        # Direction question
        direction_q = f"Which approach to {topic} best supports your {building_type} goals?"
        items.append(f"- Direction: {direction_q}")

        # Watch line
        watch_line = f"- Watch: Check implications for circulation/daylight/acoustics."
        items.append(watch_line)

        header = "Synthesis:"
        next_probe = "Next: test one concrete change and tell me what you notice. What will you try first?"
        response_text = header + "\n" + "\n".join(items) + "\n\n" + next_probe

        return {
            "response_text": response_text,
            "response_type": "design_guidance",
        }

    def _extract_main_topic(self, text: str) -> str:
        """Extract main topic from user text."""
        if not text:
            return "design"

        # Simple keyword extraction
        keywords = ["circulation", "lighting", "structure", "materials", "layout", "space", "design"]
        text_lower = text.lower()

        for keyword in keywords:
            if keyword in text_lower:
                return keyword

        return "design approach"



    # Route-specific response generation methods
    
    async def _generate_supportive_scaffolding_response(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate supportive scaffolding response - provides guidance and explanations instead of questions."""
        
        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        user_input = user_messages[-1] if user_messages else ""
        
        print(f"🔍 DEBUG: Generating supportive scaffolding for building_type: {building_type}")
        print(f"🔍 DEBUG: User input: {user_input[:100]}...")
        
        try:
            # Build context for supportive guidance generation
            context = f"""
You are an expert architectural mentor providing SUPPORTIVE GUIDANCE to help a student understand concepts they're struggling with.

STUDENT'S INPUT: "{user_input}"
BUILDING TYPE: {building_type}
GAP TYPE: {gap_type}

YOUR TASK: Provide SUPPORTIVE GUIDANCE that:
1. ACKNOWLEDGES their confusion/struggle
2. EXPLAINS the concepts they're unclear about
3. GIVES SPECIFIC EXAMPLES relevant to their {building_type} project
4. BREAKS DOWN complex ideas into understandable parts
5. PROVIDES PRACTICAL GUIDANCE for moving forward

IMPORTANT: 
- DO NOT ask more questions (they're already confused!)
- DO provide clear explanations and examples
- DO give specific guidance for their {building_type} project
- DO help them understand what they're struggling with
- Keep it encouraging and supportive

Generate supportive guidance (2-3 sentences):
"""
            
            print(f"🔍 DEBUG: Attempting LLM generation for supportive guidance")
            
            # Generate supportive guidance using AI
            response = await self.client.generate_completion([
                {"role": "user", "content": context}
            ], max_tokens=200, temperature=0.7)
            
            print(f"🔍 DEBUG: LLM response received: {response}")
            
            ai_generated_response = response.get("content", "").strip()
            if not ai_generated_response or len(ai_generated_response) < 30:
                print(f"🔍 DEBUG: LLM response too short, using fallback")
                # Fallback to supportive guidance
                return self._generate_fallback_supportive_response(user_input, building_type, gap_type)
            
            print(f"🔍 DEBUG: Using LLM-generated supportive guidance: {ai_generated_response}")
            
            return {
                "response_text": ai_generated_response,
                "response_type": "supportive_scaffolding",
                "response_strategy": "supportive_guidance",
                "educational_intent": "Provide supportive guidance and explanations",
                "metadata": {
                    "building_type": building_type,
                    "gap_type": gap_type,
                    "response_approach": "supportive_guidance"
                }
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: AI generation failed in supportive scaffolding: {e}")
            return self._generate_fallback_supportive_response(user_input, building_type, gap_type)
    
    def _generate_fallback_supportive_response(self, user_input: str, building_type: str, gap_type: str) -> Dict[str, Any]:
        """Generate fallback supportive response when LLM fails."""
        
        # Generic but supportive fallback
        if "seasonal" in user_input.lower() or "winter" in user_input.lower():
            return {
                "response_text": f"Let me help you understand seasonal design for your {building_type}. Seasonal changes can be challenging, but they're also opportunities to create year-round appeal. For winter gardens, consider elements like evergreen plants, sheltered seating areas, and warm materials that make the space inviting even in cold weather. The key is creating a sense of warmth and protection while maintaining the connection to nature.",
                "response_type": "supportive_scaffolding",
                "response_strategy": "supportive_guidance",
                "educational_intent": "Explain seasonal design concepts",
                "metadata": {
                    "building_type": building_type,
                    "gap_type": gap_type,
                    "response_approach": "fallback_supportive"
                }
            }
        else:
            return {
                "response_text": f"I understand this can be challenging! Let me help you with your {building_type} project. The key is to break down complex concepts into manageable parts. Start with what you do understand, and we can build from there. What specific aspect would you like me to explain first?",
                "response_type": "supportive_scaffolding",
                "response_strategy": "supportive_guidance",
                "educational_intent": "Provide general supportive guidance",
                "metadata": {
                    "building_type": building_type,
                    "gap_type": gap_type,
                    "response_approach": "fallback_supportive"
                }
            }
    
    async def _generate_knowledge_only_response(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate knowledge-only response - provides direct answers without follow-up questions."""
        
        building_type = self._extract_building_type_from_context(state)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        user_input = user_messages[-1] if user_messages else ""
        
        print(f"🔍 DEBUG: Generating knowledge-only response for building_type: {building_type}")
        
        try:
            # Build context for knowledge generation
            context = f"""
You are an expert architectural mentor providing DIRECT KNOWLEDGE to answer a student's question.

STUDENT'S QUESTION: "{user_input}"
BUILDING TYPE: {building_type}

YOUR TASK: Provide a COMPREHENSIVE ANSWER that:
1. Directly answers their question
2. Gives specific examples relevant to {building_type}
3. Explains the concepts clearly
4. Provides practical information they can use
5. Does NOT ask follow-up questions

IMPORTANT: 
- Give a complete, helpful answer
- Include relevant examples for {building_type}
- Be specific and actionable
- Don't ask questions back

Generate a comprehensive answer (3-4 sentences):
"""
            
            # Generate knowledge response using AI
            response = await self.client.generate_completion([
                {"role": "user", "content": context}
            ], max_tokens=250, temperature=0.7)
            
            ai_generated_response = response.get("content", "").strip()
            if not ai_generated_response or len(ai_generated_response) < 50:
                return self._generate_fallback_knowledge_response(user_input, building_type)
            
            return {
                "response_text": ai_generated_response,
                "response_type": "knowledge_only",
                "response_strategy": "direct_knowledge",
                "educational_intent": "Provide comprehensive knowledge and answers",
                "metadata": {
                    "building_type": building_type,
                    "response_approach": "knowledge_provision"
                }
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: AI generation failed in knowledge-only: {e}")
            return self._generate_fallback_knowledge_response(user_input, building_type)
    
    def _generate_fallback_knowledge_response(self, user_input: str, building_type: str) -> Dict[str, Any]:
        """Generate fallback knowledge response when LLM fails."""
        
        return {
            "response_text": f"I'd be happy to help you with your {building_type} project. Your question touches on important architectural concepts. Let me provide you with some key information that should help clarify things for you.",
            "response_type": "knowledge_only",
            "response_strategy": "fallback_knowledge",
            "educational_intent": "Provide basic knowledge guidance",
            "metadata": {
                "building_type": building_type,
                "response_approach": "fallback_knowledge"
            }
        }
    
    async def _generate_adaptive_socratic_response(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, gap_type: str) -> Dict[str, Any]:
        """Generate adaptive Socratic response - the original adaptive approach."""
        
        # Analyze student state and conversation progression
        student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        user_input = user_messages[-1] if user_messages else ""
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
        
        return response_result

    async def _generate_balanced_guidance_response(
        self, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict, 
        gap_type: str
    ) -> Dict[str, Any]:
        """
        Generate balanced guidance response that combines helpful advice with gentle exploration.
        This is for design_guidance_request routes where users want guidance but also benefit from thinking.
        """
        try:
            # Extract building type and context
            building_type = self._extract_building_type_from_context(state)
            user_input = context_classification.get("user_input", "")
            
            # Get comprehensive context for better responses
            design_brief = getattr(state, 'current_design_brief', '') or ''

            # Get full conversation context to understand references
            all_messages = [msg['content'] for msg in state.messages if msg.get('role') in ['user', 'assistant']]
            conversation_context = ' | '.join(all_messages[-8:]) if all_messages else ''

            # Extract key project details from conversation history
            project_details = self._extract_project_details_from_conversation(state)

            # Generate contextual guidance using LLM
            prompt = f"""
            You are an architectural mentor helping with a {building_type} project.

            PROJECT CONTEXT: {design_brief}
            PROJECT DETAILS FROM CONVERSATION: {project_details}
            RECENT CONVERSATION: {conversation_context}
            CURRENT USER REQUEST: "{user_input}"

            IMPORTANT: The user's current message may refer to previous conversation context.
            Look for references like "this", "that", "it", "forgot about" that connect to earlier discussion.
            If the user mentions something was "forgotten", identify what specific aspect from the conversation history they're referring to.

            Provide a BALANCED response that includes:
            1. HELPFUL GUIDANCE: Give specific, actionable advice related to their {building_type} project
            2. CONTEXTUAL RELEVANCE: Reference their specific project context and previous discussion
            3. GENTLE EXPLORATION: Ask ONE thoughtful question that builds on your guidance
            4. ENCOURAGEMENT: Support their design thinking process

            Focus on being helpful and practical while encouraging their own thinking.
            Make sure your response is specific to their {building_type} project, not generic.
            Keep the response conversational and supportive.
            """
            
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=200, temperature=0.7)
            
            if response and response.get("content"):
                return {
                    "response_text": response["content"],
                    "response_type": "balanced_guidance",
                    "guidance_type": "design_guidance",
                    "building_type": building_type,
                    "confidence": 0.9
                }
            else:
                # Fallback to generic but helpful guidance
                return self._generate_fallback_balanced_guidance(building_type, user_input)
                
        except Exception as e:
            print(f"🔍 DEBUG: LLM generation failed for balanced_guidance: {e}")
            # Fallback to generic but helpful guidance
            building_type = self._extract_building_type_from_context(state)
            user_input = context_classification.get("user_input", "")
            return self._generate_fallback_balanced_guidance(building_type, user_input)
    
    def _generate_fallback_balanced_guidance(self, building_type: str, user_input: str) -> Dict[str, Any]:
        """Generate fallback balanced guidance when LLM fails."""
        building_type = building_type if building_type != "unknown" else "architectural"
        
        # Provide helpful guidance with gentle exploration
        guidance_text = f"""
        Based on your {building_type} project, here's some helpful guidance for organizing your spaces:

        **Practical Approach:**
        • Start by mapping the flow between indoor and outdoor areas
        • Consider how different age groups will use each space
        • Think about seasonal changes and weather protection
        • Plan for flexible, adaptable spaces that can serve multiple purposes

        **Design Strategy:**
        • Create clear visual connections between classrooms and outdoor areas
        • Use materials and colors that complement the natural environment
        • Design circulation paths that encourage exploration
        • Include both active and quiet outdoor spaces

        **Next Steps:**
        • Sketch a basic layout showing the relationship between indoor and outdoor areas
        • Consider how the spaces will change throughout the day and seasons
        • Think about what specific activities each space will support

        What aspect of this organization strategy feels most important to you right now?
        """
        
        return {
            "response_text": guidance_text.strip(),
            "response_type": "balanced_guidance",
            "guidance_type": "design_guidance",
            "building_type": building_type,
            "confidence": 0.8
        }

    async def _generate_llm_response(self, prompt: str, state: ArchMentorState, analysis_result: Dict) -> str:
        """Generate LLM response using the client."""
        try:
            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=300, temperature=0.7)

            return response.get("content", "").strip()
        except Exception as e:
            # Fallback response
            building_type = self._extract_building_type_from_context(state)
            return f"Let's explore your {building_type} project further. What specific aspect would you like to focus on?"

    def _generate_fallback_dict_response(self, state: ArchMentorState, gap_type: str) -> Dict[str, Any]:
        """Generate fallback response as dictionary for gamified methods."""
        building_type = self._extract_building_type_from_context(state)
        return {
            "response_text": f"Let's explore your {building_type} project further. What specific aspect would you like to focus on?",
            "response_type": "fallback",
            "response_strategy": "fallback_guidance",
            "educational_intent": "continued_exploration",
            "gap_type": gap_type,
            "building_type": building_type,
            "cognitive_flags": ["continued_engagement"]
        }

    def _extract_project_details_from_conversation(self, state: ArchMentorState) -> str:
        """Extract key project details from conversation history to understand context."""
        try:
            all_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            conversation_text = ' '.join(all_messages).lower()

            details = []

            # Check conversation context first for project details
            if hasattr(state, 'conversation_context'):
                ctx = state.conversation_context
                if ctx.project_type:
                    details.append(f"{ctx.project_type} project")
                if ctx.existing_building_type and ctx.target_building_type:
                    details.append(f"converting {ctx.existing_building_type} to {ctx.target_building_type}")
                elif ctx.existing_building_type:
                    details.append(f"existing {ctx.existing_building_type} building")
                elif ctx.target_building_type:
                    details.append(f"{ctx.target_building_type} program")
                if ctx.project_details:
                    details.extend(ctx.project_details)

            # Fallback to text analysis if no conversation context
            if not details:
                # Check for building types and project types
                if 'warehouse' in conversation_text:
                    details.append("existing warehouse building")
                if 'adaptive reuse' in conversation_text or 'conversion' in conversation_text:
                    details.append("adaptive reuse project")
                if 'community center' in conversation_text:
                    details.append("community center program")
                if 'elder' in conversation_text or 'senior' in conversation_text:
                    details.append("serving elder/senior population")
                if 'construction' in conversation_text:
                    details.append("construction approach considerations")

            # Check for specific architectural elements mentioned
            if 'circulation' in conversation_text:
                details.append("circulation design")
            if 'material' in conversation_text:
                details.append("material considerations")
            if 'structure' in conversation_text:
                details.append("structural considerations")

            return '; '.join(details) if details else "general architectural project"

        except Exception as e:
            print(f"⚠️ Error extracting project details: {e}")
            return "architectural project"

    # Cleanup
    def __del__(self) -> None:
        """Cleanup method."""
        try:
            self.telemetry.log_agent_end("cleanup")
        except:
            pass