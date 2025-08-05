"""
Data models for the MEGA Architectural Mentor test system
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


class TestGroup(Enum):
    """Test group assignments"""
    MENTOR = "MENTOR"
    GENERIC_AI = "GENERIC_AI"
    CONTROL = "CONTROL"


class TestPhase(Enum):
    """Test phases"""
    PRE_TEST = "PRE_TEST"
    IDEATION = "IDEATION"
    VISUALIZATION = "VISUALIZATION"
    MATERIALIZATION = "MATERIALIZATION"
    POST_TEST = "POST_TEST"
    COMPLETED = "COMPLETED"


class MoveType(Enum):
    """Design move types based on cognitive operation"""
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    TRANSFORMATION = "transformation"
    REFLECTION = "reflection"


class DesignFocus(Enum):
    """Design focus areas"""
    FUNCTION = "function"
    FORM = "form"
    STRUCTURE = "structure"
    MATERIAL = "material"
    ENVIRONMENT = "environment"
    CULTURE = "culture"


class Modality(Enum):
    """Interaction modalities"""
    TEXT = "text"
    SKETCH = "sketch"
    IMAGE = "image"
    VOICE = "voice"
    UPLOAD = "upload"


class MoveSource(Enum):
    """Source of design moves"""
    USER_GENERATED = "user_generated"
    AI_PROVIDED = "ai_provided"
    AI_PROMPTED = "ai_prompted"
    RESOURCE_REFERENCED = "resource_referenced"
    PLATFORM_PROMPTED = "platform_prompted"
    SELF_GENERATED = "self_generated"


@dataclass
class TestParticipant:
    """Test participant information"""
    id: str
    test_group: TestGroup
    session_id: str
    proficiency_level: Optional[str] = None
    pre_test_scores: Dict[str, float] = field(default_factory=dict)
    post_test_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DesignMove:
    """Represents a single design move in the linkography"""
    id: str
    session_id: str
    timestamp: datetime
    sequence_number: int
    content: str
    move_type: MoveType
    phase: TestPhase
    modality: Modality
    cognitive_operation: str
    design_focus: DesignFocus
    move_source: MoveSource
    cognitive_load: str  # high, medium, low
    
    # Linkography context
    previous_move_id: Optional[str] = None
    tool_used: str = ""
    interaction_trigger: str = ""
    semantic_links: List[str] = field(default_factory=list)
    temporal_links: List[str] = field(default_factory=list)
    conceptual_distance: float = 0.0
    
    # Group-specific fields
    ai_influence_strength: Optional[float] = None  # For AI groups
    self_generation_strength: float = 1.0  # For control group
    directness_level: Optional[str] = None  # For generic AI
    
    # Additional metadata
    pause_duration: float = 0.0
    revision_count: int = 0
    complexity_score: float = 0.0
    uncertainty_markers: int = 0
    
    # Multimodal context
    concurrent_sketch: Optional[str] = None
    image_annotations: Optional[Dict[str, Any]] = None
    spatial_coordinates: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'sequence_number': self.sequence_number,
            'content': self.content,
            'move_type': self.move_type.value,
            'phase': self.phase.value,
            'modality': self.modality.value,
            'cognitive_operation': self.cognitive_operation,
            'design_focus': self.design_focus.value,
            'move_source': self.move_source.value,
            'cognitive_load': self.cognitive_load,
            'previous_move_id': self.previous_move_id,
            'tool_used': self.tool_used,
            'interaction_trigger': self.interaction_trigger,
            'semantic_links': self.semantic_links,
            'temporal_links': self.temporal_links,
            'conceptual_distance': self.conceptual_distance,
            'ai_influence_strength': self.ai_influence_strength,
            'self_generation_strength': self.self_generation_strength,
            'directness_level': self.directness_level,
            'pause_duration': self.pause_duration,
            'revision_count': self.revision_count,
            'complexity_score': self.complexity_score,
            'uncertainty_markers': self.uncertainty_markers,
            'concurrent_sketch': self.concurrent_sketch,
            'image_annotations': self.image_annotations,
            'spatial_coordinates': self.spatial_coordinates
        }


@dataclass
class InteractionData:
    """Represents a single interaction in the test"""
    id: str
    session_id: str
    timestamp: datetime
    phase: TestPhase
    interaction_type: str
    user_input: str
    system_response: str
    response_time: float
    
    # Cognitive metrics
    cognitive_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Design moves generated from this interaction
    generated_moves: List[str] = field(default_factory=list)
    
    # Additional context
    error_occurred: bool = False
    error_details: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'phase': self.phase.value,
            'interaction_type': self.interaction_type,
            'user_input': self.user_input,
            'system_response': self.system_response,
            'response_time': self.response_time,
            'cognitive_metrics': self.cognitive_metrics,
            'generated_moves': self.generated_moves,
            'error_occurred': self.error_occurred,
            'error_details': self.error_details,
            'metadata': self.metadata
        }


@dataclass
class AssessmentResult:
    """Assessment results for pre/post tests"""
    assessment_type: str  # pre_test, post_test
    scores: Dict[str, float]
    timestamp: datetime
    completion_time: Optional[float] = None
    responses: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'assessment_type': self.assessment_type,
            'scores': self.scores,
            'timestamp': self.timestamp.isoformat(),
            'completion_time': self.completion_time,
            'responses': self.responses
        }


@dataclass
class TestSession:
    """Complete test session data"""
    id: str
    participant_id: str
    test_group: TestGroup
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Phase timing
    phase_durations: Dict[str, float] = field(default_factory=dict)
    
    # Data collections
    interactions: List[InteractionData] = field(default_factory=list)
    design_moves: List[DesignMove] = field(default_factory=list)
    assessments: Dict[str, AssessmentResult] = field(default_factory=dict)
    
    # Metrics
    cognitive_metrics: Dict[str, float] = field(default_factory=dict)
    design_quality_scores: Dict[str, float] = field(default_factory=dict)
    
    # Status
    completed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'test_group': self.test_group.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'phase_durations': self.phase_durations,
            'interactions': [i.to_dict() for i in self.interactions],
            'design_moves': [m.to_dict() for m in self.design_moves],
            'assessments': {k: v.to_dict() for k, v in self.assessments.items()},
            'cognitive_metrics': self.cognitive_metrics,
            'design_quality_scores': self.design_quality_scores,
            'completed': self.completed,
            'metadata': self.metadata
        }