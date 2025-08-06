# utils/agent_response.py - Standardized Agent Response Format
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class ResponseType(Enum):
    """Standard response types for agents"""
    ANALYSIS = "analysis"
    KNOWLEDGE = "knowledge"
    SOCRATIC = "socratic"
    COGNITIVE_ENHANCEMENT = "cognitive_enhancement"
    CONTEXT_CLASSIFICATION = "context_classification"
    SYNTHESIS = "synthesis"
    ERROR = "error"
    FALLBACK = "fallback"

class CognitiveFlag(Enum):
    """Standard cognitive flags for tracking"""
    COGNITIVE_OFFLOADING_DETECTED = "cognitive_offloading_detected"
    DEEP_THINKING_ENCOURAGED = "deep_thinking_encouraged"
    SCAFFOLDING_PROVIDED = "scaffolding_provided"
    ENGAGEMENT_MAINTAINED = "engagement_maintained"
    SKILL_ADAPTATION = "skill_adaptation"
    KNOWLEDGE_INTEGRATION = "knowledge_integration"
    METACOGNITIVE_AWARENESS = "metacognitive_awareness"
    LEARNING_PROGRESSION = "learning_progression"

@dataclass
class JourneyAlignment:
    """Journey-specific alignment metrics"""
    current_phase: str = "ideation"
    phase_progress: float = 0.0
    milestone_progress: Dict[str, float] = field(default_factory=dict)
    next_milestone: Optional[str] = None
    journey_progress: float = 0.0
    phase_confidence: float = 0.5
    milestone_questions_asked: List[str] = field(default_factory=list)

@dataclass
class ProgressUpdate:
    """Progress tracking for the design journey"""
    phase_progress: Dict[str, float] = field(default_factory=dict)
    milestone_progress: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    cognitive_state: Dict[str, Any] = field(default_factory=dict)
    learning_progression: Dict[str, Any] = field(default_factory=dict)
    skill_level_update: Optional[str] = None
    engagement_level_update: Optional[str] = None

@dataclass
class EnhancementMetrics:
    """Cognitive enhancement metrics"""
    cognitive_offloading_prevention_score: float = 0.0
    deep_thinking_engagement_score: float = 0.0
    knowledge_integration_score: float = 0.0
    scaffolding_effectiveness_score: float = 0.0
    learning_progression_score: float = 0.0
    metacognitive_awareness_score: float = 0.0
    overall_cognitive_score: float = 0.0
    scientific_confidence: float = 0.0

@dataclass
class AgentResponse:
    """Standardized response format for all agents"""
    
    # Core response content
    response_text: str
    response_type: ResponseType
    
    # Cognitive enhancement tracking
    cognitive_flags: List[CognitiveFlag] = field(default_factory=list)
    enhancement_metrics: EnhancementMetrics = field(default_factory=EnhancementMetrics)
    
    # Progress tracking
    progress_update: ProgressUpdate = field(default_factory=ProgressUpdate)
    journey_alignment: JourneyAlignment = field(default_factory=JourneyAlignment)
    
    # Response metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.5
    confidence_score: float = 0.5
    
    # Agent-specific data
    agent_name: str = ""
    processing_time: float = 0.0
    sources_used: List[str] = field(default_factory=list)
    
    # Error handling
    error_message: Optional[str] = None
    fallback_used: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        return {
            "response_text": self.response_text,
            "response_type": self.response_type.value,
            "cognitive_flags": [flag.value for flag in self.cognitive_flags],
            "enhancement_metrics": {
                "cognitive_offloading_prevention_score": self.enhancement_metrics.cognitive_offloading_prevention_score,
                "deep_thinking_engagement_score": self.enhancement_metrics.deep_thinking_engagement_score,
                "knowledge_integration_score": self.enhancement_metrics.knowledge_integration_score,
                "scaffolding_effectiveness_score": self.enhancement_metrics.scaffolding_effectiveness_score,
                "learning_progression_score": self.enhancement_metrics.learning_progression_score,
                "metacognitive_awareness_score": self.enhancement_metrics.metacognitive_awareness_score,
                "overall_cognitive_score": self.enhancement_metrics.overall_cognitive_score,
                "scientific_confidence": self.enhancement_metrics.scientific_confidence
            },
            "progress_update": {
                "phase_progress": self.progress_update.phase_progress,
                "milestone_progress": self.progress_update.milestone_progress,
                "cognitive_state": self.progress_update.cognitive_state,
                "learning_progression": self.progress_update.learning_progression,
                "skill_level_update": self.progress_update.skill_level_update,
                "engagement_level_update": self.progress_update.engagement_level_update
            },
            "journey_alignment": {
                "current_phase": self.journey_alignment.current_phase,
                "phase_progress": self.journey_alignment.phase_progress,
                "milestone_progress": self.journey_alignment.milestone_progress,
                "next_milestone": self.journey_alignment.next_milestone,
                "journey_progress": self.journey_alignment.journey_progress,
                "phase_confidence": self.journey_alignment.phase_confidence,
                "milestone_questions_asked": self.journey_alignment.milestone_questions_asked
            },
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score,
            "agent_name": self.agent_name,
            "processing_time": self.processing_time,
            "sources_used": self.sources_used,
            "error_message": self.error_message,
            "fallback_used": self.fallback_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResponse':
        """Create response from dictionary format"""
        return cls(
            response_text=data.get("response_text", ""),
            response_type=ResponseType(data.get("response_type", "fallback")),
            cognitive_flags=[CognitiveFlag(flag) for flag in data.get("cognitive_flags", [])],
            enhancement_metrics=EnhancementMetrics(**data.get("enhancement_metrics", {})),
            progress_update=ProgressUpdate(**data.get("progress_update", {})),
            journey_alignment=JourneyAlignment(**data.get("journey_alignment", {})),
            metadata=data.get("metadata", {}),
            quality_score=data.get("quality_score", 0.5),
            confidence_score=data.get("confidence_score", 0.5),
            agent_name=data.get("agent_name", ""),
            processing_time=data.get("processing_time", 0.0),
            sources_used=data.get("sources_used", []),
            error_message=data.get("error_message"),
            fallback_used=data.get("fallback_used", False)
        )
    
    def is_successful(self) -> bool:
        """Check if response was successful"""
        return self.error_message is None and not self.fallback_used
    
    def has_cognitive_enhancement(self) -> bool:
        """Check if response includes cognitive enhancement"""
        return len(self.cognitive_flags) > 0
    
    def get_primary_cognitive_flag(self) -> Optional[CognitiveFlag]:
        """Get the primary cognitive flag"""
        return self.cognitive_flags[0] if self.cognitive_flags else None

class ResponseBuilder:
    """Helper class for building standardized responses"""
    
    @staticmethod
    def create_analysis_response(
        response_text: str,
        cognitive_flags: List[CognitiveFlag] = None,
        enhancement_metrics: EnhancementMetrics = None,
        **kwargs
    ) -> AgentResponse:
        """Create an analysis response"""
        return AgentResponse(
            response_text=response_text,
            response_type=ResponseType.ANALYSIS,
            cognitive_flags=cognitive_flags or [],
            enhancement_metrics=enhancement_metrics or EnhancementMetrics(),
            agent_name="analysis_agent",
            **kwargs
        )
    
    @staticmethod
    def create_knowledge_response(
        response_text: str,
        sources_used: List[str] = None,
        **kwargs
    ) -> AgentResponse:
        """Create a knowledge response"""
        return AgentResponse(
            response_text=response_text,
            response_type=ResponseType.KNOWLEDGE,
            sources_used=sources_used or [],
            agent_name="domain_expert",
            **kwargs
        )
    
    @staticmethod
    def create_socratic_response(
        response_text: str,
        cognitive_flags: List[CognitiveFlag] = None,
        **kwargs
    ) -> AgentResponse:
        """Create a Socratic response"""
        return AgentResponse(
            response_text=response_text,
            response_type=ResponseType.SOCRATIC,
            cognitive_flags=cognitive_flags or [],
            agent_name="socratic_tutor",
            **kwargs
        )
    
    @staticmethod
    def create_cognitive_enhancement_response(
        response_text: str,
        cognitive_flags: List[CognitiveFlag] = None,
        enhancement_metrics: EnhancementMetrics = None,
        **kwargs
    ) -> AgentResponse:
        """Create a cognitive enhancement response"""
        return AgentResponse(
            response_text=response_text,
            response_type=ResponseType.COGNITIVE_ENHANCEMENT,
            cognitive_flags=cognitive_flags or [],
            enhancement_metrics=enhancement_metrics or EnhancementMetrics(),
            agent_name="cognitive_enhancement",
            **kwargs
        )
    
    @staticmethod
    def create_error_response(
        error_message: str,
        agent_name: str = "",
        **kwargs
    ) -> AgentResponse:
        """Create an error response"""
        return AgentResponse(
            response_text=f"Error: {error_message}",
            response_type=ResponseType.ERROR,
            error_message=error_message,
            agent_name=agent_name,
            **kwargs
        )
    
    @staticmethod
    def create_fallback_response(
        response_text: str,
        agent_name: str = "",
        **kwargs
    ) -> AgentResponse:
        """Create a fallback response"""
        return AgentResponse(
            response_text=response_text,
            response_type=ResponseType.FALLBACK,
            fallback_used=True,
            agent_name=agent_name,
            **kwargs
        )

# Utility functions for response validation
def validate_response(response: AgentResponse) -> bool:
    """Validate that a response meets minimum requirements"""
    if not response.response_text:
        return False
    
    if response.response_type == ResponseType.ERROR and not response.error_message:
        return False
    
    if response.quality_score < 0.0 or response.quality_score > 1.0:
        return False
    
    return True

def merge_responses(responses: List[AgentResponse]) -> AgentResponse:
    """Merge multiple agent responses into a single response"""
    if not responses:
        return ResponseBuilder.create_error_response("No responses to merge")
    
    # Use the first response as base
    base_response = responses[0]
    
    # Merge cognitive flags
    all_flags = []
    for response in responses:
        all_flags.extend(response.cognitive_flags)
    
    # Merge enhancement metrics (average)
    total_metrics = EnhancementMetrics()
    metric_count = 0
    for response in responses:
        if response.enhancement_metrics:
            total_metrics.cognitive_offloading_prevention_score += response.enhancement_metrics.cognitive_offloading_prevention_score
            total_metrics.deep_thinking_engagement_score += response.enhancement_metrics.deep_thinking_engagement_score
            total_metrics.knowledge_integration_score += response.enhancement_metrics.knowledge_integration_score
            total_metrics.scaffolding_effectiveness_score += response.enhancement_metrics.scaffolding_effectiveness_score
            total_metrics.learning_progression_score += response.enhancement_metrics.learning_progression_score
            total_metrics.metacognitive_awareness_score += response.enhancement_metrics.metacognitive_awareness_score
            total_metrics.overall_cognitive_score += response.enhancement_metrics.overall_cognitive_score
            total_metrics.scientific_confidence += response.enhancement_metrics.scientific_confidence
            metric_count += 1
    
    if metric_count > 0:
        total_metrics.cognitive_offloading_prevention_score /= metric_count
        total_metrics.deep_thinking_engagement_score /= metric_count
        total_metrics.knowledge_integration_score /= metric_count
        total_metrics.scaffolding_effectiveness_score /= metric_count
        total_metrics.learning_progression_score /= metric_count
        total_metrics.metacognitive_awareness_score /= metric_count
        total_metrics.overall_cognitive_score /= metric_count
        total_metrics.scientific_confidence /= metric_count
    
    # Create merged response
    merged_response = AgentResponse(
        response_text=base_response.response_text,
        response_type=ResponseType.SYNTHESIS,
        cognitive_flags=list(set(all_flags)),  # Remove duplicates
        enhancement_metrics=total_metrics,
        progress_update=base_response.progress_update,
        journey_alignment=base_response.journey_alignment,
        metadata=base_response.metadata,
        quality_score=sum(r.quality_score for r in responses) / len(responses),
        confidence_score=sum(r.confidence_score for r in responses) / len(responses),
        agent_name="synthesizer",
        sources_used=list(set([s for r in responses for s in r.sources_used]))
    )
    
    return merged_response 