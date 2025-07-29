"""
MEGA Architectural Mentor - Linkography Types and Data Models
Types and interfaces for Gabriela Goldschmidt's Linkography methodology
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Literal
from datetime import datetime
import numpy as np


# Phase types based on the three-phase design process
DesignPhase = Literal['ideation', 'visualization', 'materialization']

# Move types based on cognitive actions
MoveType = Literal['analysis', 'synthesis', 'evaluation', 'transformation', 'reflection']

# Modality types for multimodal interaction
Modality = Literal['text', 'sketch', 'gesture', 'verbal']

# Link types
LinkType = Literal['backward', 'forward', 'lateral']


@dataclass
class DesignMove:
    """Represents a single design move in the linkography"""
    id: str
    timestamp: float
    session_id: str
    user_id: str
    phase: DesignPhase
    content: str
    move_type: MoveType
    modality: Modality
    embedding: Optional[np.ndarray] = None
    cognitive_load: Optional[float] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure timestamp is float"""
        self.timestamp = float(self.timestamp)


@dataclass
class LinkographLink:
    """Represents a link between two design moves"""
    id: str
    source_move: str
    target_move: str
    strength: float  # 0-1 for fuzzy linkography
    confidence: float
    link_type: LinkType
    temporal_distance: int
    semantic_similarity: float
    automated: bool = True
    
    def __post_init__(self):
        """Validate link strength and confidence"""
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class LinkographMetrics:
    """Metrics calculated from a linkograph"""
    link_density: float  # Total link strength / number of moves
    critical_move_ratio: float  # Ratio of critical moves
    entropy: float  # Information entropy of the linkograph
    phase_balance: Dict[str, float]  # Time distribution across phases
    cognitive_indicators: Dict[str, float]  # Mapped cognitive metrics
    
    # Additional metrics
    avg_link_strength: float = 0.0
    max_link_range: int = 0
    orphan_move_ratio: float = 0.0
    chunk_count: int = 0
    web_count: int = 0
    sawtooth_count: int = 0


@dataclass
class Linkograph:
    """Complete linkograph representation"""
    id: str
    session_id: str
    moves: List[DesignMove]
    links: List[LinkographLink]
    metrics: LinkographMetrics
    phase: DesignPhase
    generated_at: float
    
    def get_move_by_id(self, move_id: str) -> Optional[DesignMove]:
        """Get a move by its ID"""
        for move in self.moves:
            if move.id == move_id:
                return move
        return None
    
    def get_links_for_move(self, move_id: str) -> Tuple[List[LinkographLink], List[LinkographLink]]:
        """Get all links where move is source or target"""
        source_links = [link for link in self.links if link.source_move == move_id]
        target_links = [link for link in self.links if link.target_move == move_id]
        return source_links, target_links
    
    def get_critical_moves(self, threshold: float = 0.1) -> List[DesignMove]:
        """Get moves that are critical (high forelinks and backlinks)"""
        critical_moves = []
        total_moves = len(self.moves)
        
        for move in self.moves:
            source_links, target_links = self.get_links_for_move(move.id)
            link_ratio = (len(source_links) + len(target_links)) / (2 * total_moves)
            
            if link_ratio >= threshold:
                critical_moves.append(move)
        
        return critical_moves


@dataclass
class LinkographPattern:
    """Represents a pattern detected in the linkograph"""
    pattern_type: str  # 'chunk', 'web', 'sawtooth', 'orphan'
    moves: List[str]  # Move IDs involved in the pattern
    strength: float  # Pattern strength/confidence
    description: str
    cognitive_implications: Dict[str, float]


@dataclass
class CognitiveLinkographMapping:
    """Maps linkography metrics to cognitive assessment framework"""
    deep_thinking_engagement: float
    cognitive_offloading_prevention: float
    scaffolding_effectiveness: float
    knowledge_integration: float
    learning_progression: float
    metacognitive_awareness: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format"""
        return {
            'deep_thinking_engagement': self.deep_thinking_engagement,
            'cognitive_offloading_prevention': self.cognitive_offloading_prevention,
            'scaffolding_effectiveness': self.scaffolding_effectiveness,
            'knowledge_integration': self.knowledge_integration,
            'learning_progression': self.learning_progression,
            'metacognitive_awareness': self.metacognitive_awareness
        }


@dataclass
class LinkographSession:
    """Extended session data including linkography analysis"""
    session_id: str
    user_id: str
    start_time: float
    end_time: Optional[float]
    linkographs: List[Linkograph]  # Multiple linkographs per session (by phase)
    overall_metrics: LinkographMetrics
    cognitive_mapping: CognitiveLinkographMapping
    patterns_detected: List[LinkographPattern]
    
    def get_phase_linkograph(self, phase: DesignPhase) -> Optional[Linkograph]:
        """Get linkograph for a specific phase"""
        for lg in self.linkographs:
            if lg.phase == phase:
                return lg
        return None
    
    def get_duration_minutes(self) -> float:
        """Get session duration in minutes"""
        if self.end_time:
            return (self.end_time - self.start_time) / 60.0
        return 0.0