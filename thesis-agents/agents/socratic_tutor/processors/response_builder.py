"""
Response building processing module for creating AgentResponse objects from Socratic questions.
"""
from typing import Dict, Any, List, Optional
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics
from ..schemas import QuestionResult, SocraticResponse
from ..config import ENHANCEMENT_METRICS, COGNITIVE_FLAGS_MAPPING
from ...common import AgentTelemetry, MetricsCalculator
from state_manager import ArchMentorState


class SocraticResponseBuilderProcessor:
    """
    Processes response building for Socratic tutor agent.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("socratic_response_builder")
        self.metrics_calculator = MetricsCalculator()
        
    def convert_to_agent_response(
        self, 
        question_result: QuestionResult, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict
    ) -> AgentResponse:
        """
        Convert question result to AgentResponse format.
        This is the exact logic from the original adapter.
        """
        self.telemetry.log_agent_start("convert_to_agent_response")
        
        try:
            # Calculate enhancement metrics
            enhancement_metrics = self._calculate_enhancement_metrics(question_result, state)
            
            # Extract cognitive flags
            cognitive_flags = self._extract_cognitive_flags(question_result, context_classification)
            
            # Build response using ResponseBuilder
            response = ResponseBuilder.build_guidance_response(
                response_text=question_result.question_text,
                question_type=question_result.question_type,
                pedagogical_intent=question_result.pedagogical_intent,
                cognitive_flags=self._convert_cognitive_flags(cognitive_flags),
                enhancement_metrics=enhancement_metrics,
                agent_name="socratic_tutor"
            )
            
            self.telemetry.log_agent_end("convert_to_agent_response")
            return response
            
        except Exception as e:
            self.telemetry.log_error("convert_to_agent_response", str(e))
            return ResponseBuilder.build_error_response(
                f"Socratic response conversion failed: {str(e)}",
                agent_name="socratic_tutor"
            )
    
    def _calculate_enhancement_metrics(self, question_result: QuestionResult, state: ArchMentorState) -> EnhancementMetrics:
        """
        Calculate enhancement metrics for Socratic guidance.
        This is the exact logic from the original adapter.
        """
        self.telemetry.log_agent_start("_calculate_enhancement_metrics")
        
        try:
            # Get metrics configuration based on question type
            question_type = question_result.question_type
            metrics_config = ENHANCEMENT_METRICS.get(question_type, ENHANCEMENT_METRICS['fallback_question'])
            
            # Extract individual scores
            cop_score = metrics_config['cognitive_offloading_prevention_score']
            dte_score = metrics_config['deep_thinking_engagement_score']
            ki_score = metrics_config['knowledge_integration_score']
            scaffolding_score = metrics_config['scaffolding_effectiveness_score']
            lp_score = metrics_config['learning_progression_score']
            metacognitive_score = metrics_config['metacognitive_awareness_score']
            scientific_confidence = metrics_config['scientific_confidence']
            
            # Calculate overall score
            overall_score = (cop_score + dte_score + ki_score + scaffolding_score + lp_score + metacognitive_score) / 6
            
            # Create EnhancementMetrics object
            enhancement_metrics = EnhancementMetrics(
                cognitive_offloading_prevention_score=cop_score,
                deep_thinking_engagement_score=dte_score,
                knowledge_integration_score=ki_score,
                scaffolding_effectiveness_score=scaffolding_score,
                learning_progression_score=lp_score,
                metacognitive_awareness_score=metacognitive_score,
                overall_cognitive_score=overall_score,
                scientific_confidence=scientific_confidence
            )
            
            self.telemetry.log_agent_end("_calculate_enhancement_metrics")
            return enhancement_metrics
            
        except Exception as e:
            self.telemetry.log_error("_calculate_enhancement_metrics", str(e))
            # Return default metrics
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
    
    def _extract_cognitive_flags(self, question_result: QuestionResult, context_classification: Dict) -> List[str]:
        """
        Extract cognitive flags from question result.
        This is the exact logic from the original adapter.
        """
        self.telemetry.log_agent_start("_extract_cognitive_flags")
        
        try:
            flags = []
            
            # Always encourage deep thinking with Socratic questions
            flags.append("deep_thinking_encouraged")
            
            # Add specific flags based on context
            confidence_level = question_result.confidence_level
            if confidence_level == "overconfident":
                flags.append("assumption_challenged")
            elif confidence_level == "uncertain":
                flags.append("scaffolding_provided")
            
            # Socratic method promotes metacognitive awareness
            flags.append("metacognitive_awareness")
            
            self.telemetry.log_agent_end("_extract_cognitive_flags")
            return flags
            
        except Exception as e:
            self.telemetry.log_error("_extract_cognitive_flags", str(e))
            return ["deep_thinking_encouraged"]
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """
        Convert string flags to CognitiveFlag enums.
        This is the exact logic from the original adapter.
        """
        try:
            flag_mapping = {
                "deep_thinking_encouraged": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
                "assumption_challenged": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
                "scaffolding_provided": CognitiveFlag.SCAFFOLDING_PROVIDED,
                "metacognitive_awareness": CognitiveFlag.METACOGNITIVE_AWARENESS
            }
            
            return [flag_mapping.get(flag, CognitiveFlag.DEEP_THINKING_ENCOURAGED) for flag in cognitive_flags]
            
        except Exception as e:
            self.telemetry.log_error("_convert_cognitive_flags", str(e))
            return [CognitiveFlag.DEEP_THINKING_ENCOURAGED]
    
    def create_socratic_response(
        self,
        question_result: QuestionResult,
        enhancement_metrics: EnhancementMetrics,
        cognitive_flags: List[str]
    ) -> SocraticResponse:
        """Create a complete Socratic response object."""
        try:
            return SocraticResponse(
                question_result=question_result,
                enhancement_metrics=enhancement_metrics,
                cognitive_flags=cognitive_flags,
                agent_name="socratic_tutor",
                response_confidence=question_result.generation_confidence
            )
            
        except Exception as e:
            self.telemetry.log_error("create_socratic_response", str(e))
            # Return basic response
            return SocraticResponse(
                question_result=question_result,
                enhancement_metrics=enhancement_metrics,
                cognitive_flags=["deep_thinking_encouraged"],
                agent_name="socratic_tutor",
                response_confidence=0.6
            )
    
    def validate_response_quality(self, agent_response: AgentResponse) -> bool:
        """Validate the quality of the generated response."""
        try:
            # Check required fields
            if not hasattr(agent_response, 'response_text') or not agent_response.response_text:
                return False
            
            if not hasattr(agent_response, 'enhancement_metrics'):
                return False
            
            if not hasattr(agent_response, 'cognitive_flags'):
                return False
            
            # Check response text quality
            response_text = agent_response.response_text.strip()
            if len(response_text) < 10:
                return False
            
            # Should be a question
            if not response_text.endswith('?'):
                return False
            
            # Check enhancement metrics
            metrics = agent_response.enhancement_metrics
            if not (0 <= metrics.overall_cognitive_score <= 1):
                return False
            
            return True
            
        except Exception as e:
            self.telemetry.log_error("validate_response_quality", str(e))
            return False
    
    def get_response_summary(self, agent_response: AgentResponse) -> str:
        """Generate a summary of the response."""
        try:
            metrics = agent_response.enhancement_metrics
            flags = [flag.name for flag in agent_response.cognitive_flags]
            
            summary = f"Socratic Response Summary:\n"
            summary += f"• Question: {agent_response.response_text[:50]}...\n"
            summary += f"• Cognitive Score: {metrics.overall_cognitive_score:.2f}\n"
            summary += f"• Deep Thinking: {metrics.deep_thinking_engagement_score:.2f}\n"
            summary += f"• Scaffolding: {metrics.scaffolding_effectiveness_score:.2f}\n"
            summary += f"• Cognitive Flags: {', '.join(flags)}\n"
            
            return summary
            
        except Exception as e:
            self.telemetry.log_error("get_response_summary", str(e))
            return "Response summary unavailable."
    
    def calculate_response_effectiveness(self, agent_response: AgentResponse, 
                                       context_classification: Dict) -> float:
        """Calculate the effectiveness of the response based on context."""
        try:
            effectiveness_factors = []
            
            # Base effectiveness from overall cognitive score
            base_score = agent_response.enhancement_metrics.overall_cognitive_score
            effectiveness_factors.append(base_score)
            
            # Bonus for appropriate cognitive flags
            expected_flags = self._get_expected_flags(context_classification)
            actual_flags = [flag.name for flag in agent_response.cognitive_flags]
            
            flag_match_ratio = len(set(expected_flags) & set(actual_flags)) / len(expected_flags) if expected_flags else 0
            effectiveness_factors.append(flag_match_ratio)
            
            # Question quality factor
            question_text = agent_response.response_text
            if len(question_text.split()) <= 30 and question_text.endswith('?'):
                effectiveness_factors.append(0.8)
            else:
                effectiveness_factors.append(0.6)
            
            return sum(effectiveness_factors) / len(effectiveness_factors)
            
        except Exception as e:
            self.telemetry.log_error("calculate_response_effectiveness", str(e))
            return 0.7
    
    def _get_expected_flags(self, context_classification: Dict) -> List[str]:
        """Get expected cognitive flags based on context."""
        try:
            expected_flags = ["DEEP_THINKING_ENCOURAGED"]
            
            core_classification = context_classification.get('core_classification', {})
            confidence_level = core_classification.get('confidence_level', 'confident')
            understanding_level = core_classification.get('understanding_level', 'medium')
            
            if confidence_level == 'overconfident':
                expected_flags.append("DEEP_THINKING_ENCOURAGED")  # For assumption challenging
            elif confidence_level == 'uncertain' or understanding_level == 'low':
                expected_flags.append("SCAFFOLDING_PROVIDED")
            
            expected_flags.append("METACOGNITIVE_AWARENESS")
            
            return expected_flags
            
        except Exception as e:
            self.telemetry.log_error("_get_expected_flags", str(e))
            return ["DEEP_THINKING_ENCOURAGED"] 