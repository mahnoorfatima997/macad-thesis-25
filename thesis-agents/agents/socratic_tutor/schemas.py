"""
Typed data models and schemas for the Socratic Tutor Agent.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class QuestionType(Enum):
    """Types of Socratic questions."""
    CLARIFYING = "clarifying"
    ASSUMPTION_CHALLENGING = "assumption_challenging"
    EVIDENCE = "evidence"
    PERSPECTIVE = "perspective"
    IMPLICATION = "implication"
    SOCRATIC = "socratic"
    FALLBACK = "fallback"


class PedagogicalIntent(Enum):
    """Pedagogical intents for different student states."""
    CHALLENGE_ASSUMPTIONS = "Challenge assumptions and encourage critical thinking"
    BUILD_CONFIDENCE = "Build confidence through guided discovery"
    CLARIFY_UNDERSTANDING = "Clarify understanding through structured questioning"
    GUIDE_INQUIRY = "Guide learning through thoughtful inquiry"


class ConfidenceLevel(Enum):
    """Student confidence levels."""
    OVERCONFIDENT = "overconfident"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    LOW = "low"


class UnderstandingLevel(Enum):
    """Student understanding levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    PARTIAL = "partial"


@dataclass
class QuestionContext:
    """Context information for question generation."""
    user_input: str
    project_context: str
    interaction_type: str
    understanding_level: str
    confidence_level: str
    gap_type: str


@dataclass
class QuestionResult:
    """Result of Socratic question generation."""
    question_text: str
    question_type: str
    interaction_type: str = ""
    understanding_level: str = ""
    confidence_level: str = ""
    pedagogical_intent: str = ""
    generation_confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "question_text": self.question_text,
            "question_type": self.question_type,
            "interaction_type": self.interaction_type,
            "understanding_level": self.understanding_level,
            "confidence_level": self.confidence_level,
            "pedagogical_intent": self.pedagogical_intent,
            "generation_confidence": self.generation_confidence
        }


@dataclass
class GuidanceContext:
    """Context for providing Socratic guidance."""
    state: Any  # ArchMentorState
    context_classification: Dict[str, Any]
    analysis_result: Dict[str, Any]
    gap_type: str
    current_input: str = ""
    
    def extract_classification_data(self) -> Dict[str, str]:
        """Extract classification data from context."""
        core_classification = self.context_classification.get('core_classification', {})
        return {
            'interaction_type': core_classification.get('interaction_type', 'general'),
            'understanding_level': core_classification.get('understanding_level', 'medium'),
            'confidence_level': core_classification.get('confidence_level', 'confident')
        }


@dataclass
class SocraticResponse:
    """Complete Socratic response with question and metadata."""
    question_result: QuestionResult
    enhancement_metrics: Any  # EnhancementMetrics
    cognitive_flags: List[str]
    agent_name: str = "socratic_tutor"
    response_confidence: float = 0.8
    
    def to_agent_response(self) -> Any:
        """Convert to AgentResponse format."""
        # This will be implemented in the response builder
        pass 