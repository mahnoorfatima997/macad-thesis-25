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
            # Extract user input
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            current_input = user_messages[-1] if user_messages else ""
            
            # Generate Socratic question using processor
            question_result = await self.question_processor.generate_socratic_question(
                current_input, state, context_classification, analysis_result, gap_type
            )
            
            # Convert to AgentResponse using processor
            response = self.response_processor.convert_to_agent_response(
                question_result, state, context_classification, analysis_result
            )
            
            self.telemetry.log_agent_end("provide_guidance")
            return response
            
        except Exception as e:
            self.telemetry.log_error(f"Guidance provision failed: {str(e)}")
            return ResponseBuilder.build_error_response(
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
            return ResponseBuilder.build_error_response(
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
    
    # Cleanup
    def __del__(self):
        """Cleanup method."""
        try:
            self.telemetry.log_agent_end("cleanup")
        except:
            pass 