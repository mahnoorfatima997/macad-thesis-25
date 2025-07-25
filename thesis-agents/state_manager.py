# state_manager.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class DesignPhase(Enum):
    IDEATION = "ideation"
    DEVELOPMENT = "development"
    REFINEMENT = "refinement"
    EVALUATION = "evaluation"

@dataclass
class VisualArtifact:
    id: str
    type: str  # "sketch", "plan", "section", "detail"
    image_path: str
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    annotations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class StudentProfile:
    skill_level: str = "intermediate"  # "beginner", "intermediate", "advanced"
    learning_style: str = "visual"
    cognitive_load: float = 0.3  # 0-1 scale
    engagement_level: float = 0.7
    knowledge_gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

@dataclass
class ArchMentorState:
    # Core conversation
    messages: List[Dict[str, str]] = field(default_factory=list)
    current_design_brief: str = ""
    design_phase: DesignPhase = DesignPhase.IDEATION
    
    # Visual artifacts
    visual_artifacts: List[VisualArtifact] = field(default_factory=list)
    current_sketch: Optional[VisualArtifact] = None
    
    # Student modeling
    student_profile: StudentProfile = field(default_factory=StudentProfile)
    session_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Agent coordination
    last_agent: str = ""
    next_agent: str = "analysis"
    agent_context: Dict[str, Any] = field(default_factory=dict)
    
    # Domain configuration
    domain: str = "architecture"
    domain_config: Dict[str, Any] = field(default_factory=dict)