"""
Typed data models and schemas for the Context Agent.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class InteractionType(Enum):
    """Types of student interactions."""
    QUESTION = "question"
    STATEMENT = "statement"
    EXPLORATION = "exploration"
    FEEDBACK_REQUEST = "feedback_request"
    CONFUSION = "confusion"
    PROGRESS_UPDATE = "progress_update"
    REFLECTION = "reflection"


class UnderstandingLevel(Enum):
    """Student understanding levels."""
    NOVICE = "novice"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"


class ConfidenceLevel(Enum):
    """Student confidence levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    OVERCONFIDENT = "overconfident"


class EngagementLevel(Enum):
    """Student engagement levels."""
    DISENGAGED = "disengaged"
    PASSIVE = "passive"
    ACTIVE = "active"
    HIGHLY_ENGAGED = "highly_engaged"


class DesignPhase(Enum):
    """Design phases."""
    IDEATION = "ideation"
    DEVELOPMENT = "development"
    RESOLUTION = "resolution"


@dataclass
class CoreClassification:
    """Core classification of student input."""
    interaction_type: InteractionType
    understanding_level: UnderstandingLevel
    confidence_level: ConfidenceLevel
    engagement_level: EngagementLevel
    is_response_to_question: bool = False
    is_technical_question: bool = False
    is_feedback_request: bool = False
    confidence_score: float = 0.0


@dataclass
class ContentAnalysis:
    """Analysis of content characteristics.

    Extended to align with processor outputs and downstream usage
    (e.g., context generation). Existing fields are preserved for
    backward compatibility.
    """
    # Existing fields
    technical_terms: List[str] = field(default_factory=list)
    emotional_indicators: Dict[str, int] = field(default_factory=dict)
    complexity_score: float = 0.0
    specificity_score: float = 0.0
    word_count: int = 0
    sentence_count: int = 0

    # New fields expected by processors/context generation
    key_topics: List[str] = field(default_factory=list)
    content_structure: Dict[str, Any] = field(default_factory=dict)
    content_quality: str = "medium"
    domain_concepts: List[str] = field(default_factory=list)
    information_density: float = 0.0
    analysis_confidence: float = 0.0


@dataclass
class ConversationPatterns:
    """Analysis of conversation patterns."""
    has_repetitive_topics: bool = False
    has_topic_jumping: bool = False
    engagement_trend: str = "stable"
    understanding_progression: str = "stable"
    recent_focus: List[str] = field(default_factory=list)
    conversation_depth: Dict[str, Any] = field(default_factory=dict)
    question_patterns: Dict[str, Any] = field(default_factory=dict)
    response_patterns: Dict[str, Any] = field(default_factory=dict)
    conversation_metrics: Dict[str, Any] = field(default_factory=dict)
    pattern_confidence: float = 0.0


@dataclass
class ContextualMetadata:
    """Contextual metadata about the interaction."""
    complexity_appropriateness: str = "appropriate"
    response_urgency: str = "normal"
    pedagogical_opportunity: str = "none"
    continuation_cues: List[str] = field(default_factory=list)
    difficulty_adjustment: str = "maintain"
    learning_context: Dict[str, Any] = field(default_factory=dict)
    challenge_readiness: str = "moderate"
    explanation_need: str = "moderate"
    information_gaps: List[str] = field(default_factory=list)
    analysis_focus_areas: List[str] = field(default_factory=list)
    engagement_recommendations: List[str] = field(default_factory=list)
    metadata_confidence: float = 0.5
    generation_timestamp: str = ""
    timestamp: str = ""  # Keep for backward compatibility


@dataclass
class RoutingSuggestions:
    """Suggestions for routing to appropriate agents."""
    primary_agent: str = ""
    secondary_agents: List[str] = field(default_factory=list)
    routing_confidence: float = 0.0
    routing_reasoning: str = ""
    agent_priorities: Dict[str, float] = field(default_factory=dict)


@dataclass
class AgentContexts:
    """Context information for different agents."""
    socratic_context: Dict[str, Any] = field(default_factory=dict)
    domain_context: Dict[str, Any] = field(default_factory=dict)
    analysis_context: Dict[str, Any] = field(default_factory=dict)
    cognitive_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextPackage:
    """Complete context analysis package."""
    core_classification: CoreClassification
    content_analysis: ContentAnalysis
    conversation_patterns: ConversationPatterns
    contextual_metadata: ContextualMetadata
    routing_suggestions: RoutingSuggestions
    agent_contexts: AgentContexts
    context_quality: float = 0.0
    analysis_timestamp: str = ""
    package_timestamp: str = ""  # Added missing field
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            "core_classification": {
                "interaction_type": self.core_classification.interaction_type.value,
                "understanding_level": self.core_classification.understanding_level.value,
                "confidence_level": self.core_classification.confidence_level.value,
                "engagement_level": self.core_classification.engagement_level.value,
                "is_response_to_question": self.core_classification.is_response_to_question,
                "is_technical_question": self.core_classification.is_technical_question,
                "is_feedback_request": self.core_classification.is_feedback_request,
                "confidence_score": self.core_classification.confidence_score
            },
            "content_analysis": {
                "technical_terms": self.content_analysis.technical_terms,
                "emotional_indicators": self.content_analysis.emotional_indicators,
                "complexity_score": self.content_analysis.complexity_score,
                "specificity_score": self.content_analysis.specificity_score,
                "word_count": self.content_analysis.word_count,
                "sentence_count": self.content_analysis.sentence_count
            },
            "conversation_patterns": {
                "has_repetitive_topics": self.conversation_patterns.has_repetitive_topics,
                "has_topic_jumping": self.conversation_patterns.has_topic_jumping,
                "engagement_trend": self.conversation_patterns.engagement_trend,
                "understanding_progression": self.conversation_patterns.understanding_progression,
                "recent_focus": self.conversation_patterns.recent_focus,
                "conversation_depth": self.conversation_patterns.conversation_depth,
                "question_patterns": self.conversation_patterns.question_patterns,
                "response_patterns": self.conversation_patterns.response_patterns,
                "conversation_metrics": self.conversation_patterns.conversation_metrics,
                "pattern_confidence": self.conversation_patterns.pattern_confidence
            },
            "contextual_metadata": {
                "complexity_appropriateness": self.contextual_metadata.complexity_appropriateness,
                "response_urgency": self.contextual_metadata.response_urgency,
                "pedagogical_opportunity": self.contextual_metadata.pedagogical_opportunity,
                "continuation_cues": self.contextual_metadata.continuation_cues,
                "difficulty_adjustment": self.contextual_metadata.difficulty_adjustment,
                "learning_context": self.contextual_metadata.learning_context,
                "challenge_readiness": self.contextual_metadata.challenge_readiness,
                "explanation_need": self.contextual_metadata.explanation_need,
                "information_gaps": self.contextual_metadata.information_gaps,
                "analysis_focus_areas": self.contextual_metadata.analysis_focus_areas,
                "engagement_recommendations": self.contextual_metadata.engagement_recommendations,
                "metadata_confidence": self.contextual_metadata.metadata_confidence,
                "generation_timestamp": self.contextual_metadata.generation_timestamp,
                "timestamp": self.contextual_metadata.timestamp
            },
            "routing_suggestions": {
                "primary_agent": self.routing_suggestions.primary_agent,
                "secondary_agents": self.routing_suggestions.secondary_agents,
                "routing_confidence": self.routing_suggestions.routing_confidence,
                "routing_reasoning": self.routing_suggestions.routing_reasoning,
                "agent_priorities": self.routing_suggestions.agent_priorities
            },
            "agent_contexts": {
                "socratic_context": self.agent_contexts.socratic_context,
                "domain_context": self.agent_contexts.domain_context,
                "analysis_context": self.agent_contexts.analysis_context,
                "cognitive_context": self.agent_contexts.cognitive_context
            },
            "context_quality": self.context_quality,
            "analysis_timestamp": self.analysis_timestamp
        } 