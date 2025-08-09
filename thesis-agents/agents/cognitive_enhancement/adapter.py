"""
Cognitive Enhancement Agent Adapter - streamlined modular version.

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
from .processors import (
    CognitiveAssessmentProcessor, 
    InterventionGeneratorProcessor,
    ChallengeGeneratorProcessor,
    ScientificMetricsProcessor,
    PhaseAnalyzerProcessor
)
from ..common import LLMClient, AgentTelemetry, MetricsCalculator, TextProcessor, SafetyValidator


class CognitiveEnhancementAgent:
    """
    Cognitive Enhancement Agent for challenging assumptions and preventing cognitive offloading.
    
    This streamlined adapter delegates to specialized processor modules.
    """
    
    def __init__(self, domain="architecture"):
        """Initialize the Cognitive Enhancement Agent with modular processors."""
        self.telemetry = AgentTelemetry("cognitive_enhancement")
        self.telemetry.log_agent_start("__init__", domain=domain)
        
        # Core properties
        self.domain = domain
        self.name = "cognitive_enhancement"
        
        # Initialize LLM client
        self.client = LLMClient(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        
        # Initialize shared utilities
        self.text_processor = TextProcessor()
        self.safety_validator = SafetyValidator()
        self.metrics_calculator = MetricsCalculator()
        
        # Initialize modular processors
        self.assessment_processor = CognitiveAssessmentProcessor()
        self.intervention_processor = InterventionGeneratorProcessor()
        self.challenge_processor = ChallengeGeneratorProcessor()
        self.metrics_processor = ScientificMetricsProcessor()
        self.phase_processor = PhaseAnalyzerProcessor()
        
        # Initialize cognitive metrics and templates (maintain compatibility)
        self.cognitive_metrics = COGNITIVE_THRESHOLDS
        self.challenge_templates = CHALLENGE_TEMPLATES
        
        self.telemetry.log_agent_end("__init__")
        print(f"🧠 {self.name} initialized for domain: {domain}")
    
    async def provide_challenge(self, state: ArchMentorState, context_classification: Dict, 
                              analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """
        Main processing method - provides cognitive challenges and interventions.
        """
        self.telemetry.log_agent_start("provide_challenge")
        
        try:
            # Step 1: Assess cognitive state
            cognitive_state = self.assessment_processor.assess_cognitive_state(
                state, context_classification, analysis_result
            )
            
            # Step 2: Detect cognitive offloading patterns
            offloading_detection = self.intervention_processor.detect_cognitive_offloading_patterns(
                context_classification, state
            )
            
            # Step 3: Generate cognitive intervention if needed
            intervention_result = await self.intervention_processor.generate_cognitive_intervention(
                offloading_detection, state, analysis_result
            )
            
            # Step 4: Select enhancement strategy
            strategy = self.challenge_processor.select_enhancement_strategy(
                cognitive_state, analysis_result, state
            )
            
            # Step 5: Generate cognitive challenge
            challenge_result = await self.challenge_processor.generate_cognitive_challenge(
                strategy, cognitive_state, state, analysis_result
            )
            
            # Step 6: Calculate scientific metrics
            scientific_metrics = self.metrics_processor.calculate_scientific_metrics(
                cognitive_state, state, analysis_result
            )
            
            # Step 7: Enhance with scientific context
            enhanced_result = self._enhance_response_with_scientific_context(
                challenge_result, scientific_metrics, cognitive_state, state
            )
            
            # Step 8: Convert to AgentResponse
            response = self._convert_to_agent_response(
                enhanced_result, state, context_classification, analysis_result, routing_decision
            )
            
            self.telemetry.log_agent_end("provide_challenge")
            return response
            
        except Exception as e:
            self.telemetry.log_error(f"Challenge provision failed: {str(e)}")
            return ResponseBuilder.create_error_response(
                f"Challenge provision failed: {str(e)}",
                agent_name=self.name
            )
    
    # Delegation methods for backward compatibility
    
    def assess_cognitive_state(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict) -> Dict[str, Any]:
        """Assess cognitive state (delegates to processor)."""
        return self.assessment_processor.assess_cognitive_state(state, context_classification, analysis_result)
    
    def select_enhancement_strategy(self, cognitive_state: Dict, analysis_result: Dict, state: ArchMentorState) -> str:
        """Select enhancement strategy (delegates to processor)."""
        return self.challenge_processor.select_enhancement_strategy(cognitive_state, analysis_result, state)
    
    async def generate_cognitive_challenge(self, strategy: str, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate cognitive challenge (delegates to processor)."""
        return await self.challenge_processor.generate_cognitive_challenge(strategy, cognitive_state, state, analysis_result)
    
    def calculate_scientific_metrics(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Calculate scientific metrics (delegates to processor)."""
        return self.metrics_processor.calculate_scientific_metrics(cognitive_state, state, analysis_result)
    
    def validate_thesis_metrics(self, scientific_metrics: Dict) -> Dict[str, Any]:
        """Validate thesis metrics (delegates to processor)."""
        return self.metrics_processor.validate_thesis_metrics(scientific_metrics)
    
    def create_cognitive_assessment_summary(self, scientific_metrics: Dict, cognitive_state: Dict, analysis_result: Dict) -> str:
        """Create cognitive assessment summary (delegates to processor)."""
        return self.assessment_processor.create_cognitive_assessment_summary(scientific_metrics, cognitive_state, analysis_result)
    
    # Phase-related delegation methods
    
    def _get_phase_focus(self, phase: str) -> str:
        """Get phase focus (delegates to processor)."""
        return self.phase_processor.get_phase_focus(phase)
    
    def _get_phase_demands(self, phase: str) -> str:
        """Get phase demands (delegates to processor)."""
        return self.phase_processor.get_phase_demands(phase)
    
    def _get_phase_duration(self, phase: str) -> str:
        """Get phase duration (delegates to processor)."""
        return self.phase_processor.get_phase_duration(phase)
    
    def _get_phase_indicators(self, phase: str) -> List[str]:
        """Get phase indicators (delegates to processor)."""
        return self.phase_processor.get_phase_indicators(phase)
    
    def _get_engagement_recommendation(self, score: float) -> str:
        """Get engagement recommendation (delegates to processor)."""
        return self.phase_processor.get_engagement_recommendation(score)
    
    def _get_complexity_recommendation(self, score: float) -> str:
        """Get complexity recommendation (delegates to processor)."""
        return self.phase_processor.get_complexity_recommendation(score)
    
    def _get_reflection_recommendation(self, score: float) -> str:
        """Get reflection recommendation (delegates to processor)."""
        return self.phase_processor.get_reflection_recommendation(score)
    
    # Support methods that remain in adapter
    
    def _enhance_response_with_scientific_context(self, challenge_result: Dict, scientific_metrics: Dict,
                                                 cognitive_state: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Enhance response with scientific context."""
        challenge_result["scientific_metrics"] = scientific_metrics
        challenge_result["cognitive_state"] = cognitive_state
        challenge_result["enhancement_timestamp"] = self.telemetry.get_timestamp()
        return challenge_result
    
    def _convert_to_agent_response(self, challenge_result: Dict, state: ArchMentorState, 
                                 context_classification: Dict, analysis_result: Dict, 
                                 routing_decision: Dict) -> AgentResponse:
        """Convert challenge result to AgentResponse format."""
        # Calculate enhancement metrics
        enhancement_metrics = self._calculate_enhancement_metrics(challenge_result, state, analysis_result)
        
        # Extract cognitive flags
        cognitive_flags = self._extract_cognitive_flags(challenge_result, state, context_classification)
        converted_flags = self._convert_cognitive_flags(cognitive_flags)
        
        # Build response
        response_text = challenge_result.get("challenge_text", "Continue exploring your design approach.")
        
        return ResponseBuilder.create_cognitive_enhancement_response(
            response_text,
            cognitive_flags=converted_flags,
            enhancement_metrics=enhancement_metrics,
            metadata={}
        )
    
    def _calculate_enhancement_metrics(self, challenge_result: Dict, state: ArchMentorState, analysis_result: Dict) -> EnhancementMetrics:
        """Calculate enhancement metrics for the response."""
        complexity_score = challenge_result.get("difficulty_level", "medium")
        complexity_value = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(complexity_score, 0.6)
        
        engagement_score = 0.7  # Simplified
        learning_velocity = 0.6  # Simplified
        cognitive_load = complexity_value
        
        return EnhancementMetrics()
    
    def _extract_cognitive_flags(self, challenge_result: Dict, state: ArchMentorState, context_classification: Dict) -> List[str]:
        """Extract cognitive flags from the challenge result."""
        flags = []
        
        challenge_type = challenge_result.get("challenge_type", "general")
        difficulty = challenge_result.get("difficulty_level", "medium")
        
        if challenge_type == "constraint_challenge":
            flags.append("assumption_challenged")
        elif challenge_type == "metacognitive_challenge":
            flags.append("reflection_prompted")
        elif challenge_type == "perspective_challenge":
            flags.append("perspective_expanded")
        
        if difficulty == "high":
            flags.append("high_challenge_provided")
        
        return flags
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Convert string flags to CognitiveFlag enums."""
        flag_mapping = {
            "assumption_challenged": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
            "reflection_prompted": CognitiveFlag.METACOGNITIVE_AWARENESS,
            "engagement_increased": CognitiveFlag.ENGAGEMENT_MAINTAINED,
            "perspective_expanded": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
            "high_challenge_provided": CognitiveFlag.CHALLENGE_APPROPRIATE
        }
        
        return [flag_mapping.get(flag, CognitiveFlag.NEEDS_ENCOURAGEMENT) for flag in cognitive_flags]
    
    # Additional backward compatibility methods
    
    def enhance_response_with_scientific_context(self, challenge_result: Dict, scientific_metrics: Dict,
                                               cognitive_state: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Public method for backward compatibility."""
        return self._enhance_response_with_scientific_context(challenge_result, scientific_metrics, cognitive_state, state)
    
    # Initialization methods for backward compatibility
    
    def _initialize_cognitive_metrics(self) -> Dict[str, Dict[str, float]]:
        """Initialize cognitive metrics (for backward compatibility)."""
        return COGNITIVE_THRESHOLDS
    
    def _initialize_challenge_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize challenge templates (for backward compatibility)."""
        return CHALLENGE_TEMPLATES 