"""
Typed data models and schemas for the Analysis Agent.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class SkillLevel(Enum):
    """Student skill levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DesignPhase(Enum):
    """Design phases in architectural process."""
    IDEATION = "ideation"
    VISUALIZATION = "visualization"
    MATERIALIZATION = "materialization"
    COMPLETION = "completion"


class BuildingType(Enum):
    """Building types for classification."""
    OFFICE = "office"
    RESIDENTIAL = "residential"
    EDUCATIONAL = "educational"
    CULTURAL = "cultural"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MIXED_USE = "mixed_use"
    COMMUNITY = "community"
    UNKNOWN = "unknown"


@dataclass
class SkillAssessment:
    """Results of student skill level assessment."""
    skill_level: SkillLevel
    confidence: float
    indicators: Dict[str, int] = field(default_factory=dict)
    complexity_metrics: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class PhaseDetection:
    """Results of design phase detection."""
    current_phase: DesignPhase
    confidence: float
    phase_scores: Dict[str, float] = field(default_factory=dict)
    progression_ready: bool = False
    next_phase: Optional[DesignPhase] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TextAnalysis:
    """Results of design brief text analysis."""
    building_type: BuildingType
    key_themes: List[str] = field(default_factory=list)
    program_requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    design_goals: List[str] = field(default_factory=list)
    complexity_level: str = "moderate"
    detail_level: str = "medium"


@dataclass
class VisualAnalysis:
    """Results of visual artifact analysis."""
    has_visual: bool = False
    visual_type: str = ""
    spatial_elements: List[str] = field(default_factory=list)
    design_elements: List[str] = field(default_factory=list)
    technical_elements: List[str] = field(default_factory=list)
    phase_indicators: List[str] = field(default_factory=list)


@dataclass
class CognitiveState:
    """Assessment of student cognitive state."""
    engagement_level: float = 0.5
    confidence_level: float = 0.5
    understanding_level: float = 0.5
    cognitive_load: float = 0.5
    flags: List[str] = field(default_factory=list)
    needs_support: bool = False


@dataclass
class Synthesis:
    """Synthesis of all analysis results."""
    cognitive_challenges: List[str] = field(default_factory=list)
    learning_opportunities: List[str] = field(default_factory=list)
    missing_considerations: List[str] = field(default_factory=list)
    next_focus_areas: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PhaseProgression:
    """Phase progression analysis results."""
    current_phase: str
    phase_progress: float
    completed_milestones: int = 0
    total_milestones: int = 0
    next_milestone: Optional[str] = None
    progression_score: float = 0.0
    milestone_completion: float = 0.0
    phase_recommendations: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis results."""
    skill_assessment: SkillAssessment
    phase_detection: PhaseDetection
    text_analysis: TextAnalysis
    visual_analysis: VisualAnalysis
    cognitive_state: CognitiveState
    synthesis: Synthesis
    phase_analysis: PhaseProgression
    conversation_progression: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            "skill_assessment": {
                "skill_level": self.skill_assessment.skill_level.value,
                "confidence": self.skill_assessment.confidence,
                "indicators": self.skill_assessment.indicators,
                "complexity_metrics": self.skill_assessment.complexity_metrics,
                "reasoning": self.skill_assessment.reasoning
            },
            "phase_analysis": {
                "phase": self.phase_detection.current_phase.value,
                "confidence": self.phase_detection.confidence,
                "phase_scores": self.phase_detection.phase_scores,
                "progression_ready": self.phase_detection.progression_ready,
                "next_phase": self.phase_detection.next_phase.value if self.phase_detection.next_phase else None,
                "phase_recommendations": self.phase_detection.recommendations,
                "progression_score": self.phase_analysis.progression_score,
                "completed_milestones": self.phase_analysis.completed_milestones,
                "total_milestones": self.phase_analysis.total_milestones,
                "next_milestone": self.phase_analysis.next_milestone,
                "milestone_completion": self.phase_analysis.milestone_completion
            },
            "text_analysis": {
                "building_type": self.text_analysis.building_type.value,
                "key_themes": self.text_analysis.key_themes,
                "program_requirements": self.text_analysis.program_requirements,
                "constraints": self.text_analysis.constraints,
                "design_goals": self.text_analysis.design_goals,
                "complexity_level": self.text_analysis.complexity_level,
                "detail_level": self.text_analysis.detail_level
            },
            "visual_analysis": {
                "has_visual": self.visual_analysis.has_visual,
                "visual_type": self.visual_analysis.visual_type,
                "spatial_elements": self.visual_analysis.spatial_elements,
                "design_elements": self.visual_analysis.design_elements,
                "technical_elements": self.visual_analysis.technical_elements,
                "phase_indicators": self.visual_analysis.phase_indicators
            },
            "cognitive_state": {
                "engagement_level": self.cognitive_state.engagement_level,
                "confidence_level": self.cognitive_state.confidence_level,
                "understanding_level": self.cognitive_state.understanding_level,
                "cognitive_load": self.cognitive_state.cognitive_load,
                "flags": self.cognitive_state.flags,
                "needs_support": self.cognitive_state.needs_support
            },
            "synthesis": {
                "cognitive_challenges": self.synthesis.cognitive_challenges,
                "learning_opportunities": self.synthesis.learning_opportunities,
                "missing_considerations": self.synthesis.missing_considerations,
                "next_focus_areas": self.synthesis.next_focus_areas,
                "recommendations": self.synthesis.recommendations
            },
            "conversation_progression": self.conversation_progression
        } 