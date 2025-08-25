"""
Standalone Phase Calculator
Independent phase progression logic that can be used by any mode (Raw GPT, No AI, etc.)
without dependency on the multi-agent system.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class DesignPhase(Enum):
    """Design phases for the architectural design process."""
    IDEATION = "ideation"
    VISUALIZATION = "visualization" 
    MATERIALIZATION = "materialization"


class PhaseCalculator:
    """
    Standalone phase calculator that determines current design phase
    based on conversation content and message count.
    """
    
    def __init__(self):
        self.phase_keywords = self._initialize_phase_keywords()
        self.phase_thresholds = self._initialize_phase_thresholds()
    
    def _initialize_phase_keywords(self) -> Dict[DesignPhase, List[str]]:
        """Initialize keywords that indicate each phase."""
        return {
            DesignPhase.IDEATION: [
                "concept", "idea", "program", "function", "user", "need", "requirement",
                "community", "purpose", "goal", "vision", "brief", "context", "site",
                "analysis", "research", "precedent", "inspiration", "brainstorm"
            ],
            DesignPhase.VISUALIZATION: [
                "plan", "section", "elevation", "sketch", "drawing", "layout", "space",
                "room", "circulation", "flow", "arrangement", "organization", "zoning",
                "diagram", "visual", "form", "shape", "geometry", "massing", "volume"
            ],
            DesignPhase.MATERIALIZATION: [
                "material", "construction", "structure", "detail", "technical", "system",
                "building", "concrete", "steel", "wood", "glass", "facade", "wall",
                "foundation", "roof", "mechanical", "electrical", "plumbing", "hvac"
            ]
        }
    
    def _initialize_phase_thresholds(self) -> Dict[str, int]:
        """Initialize message count thresholds for phase transitions."""
        return {
            "min_messages_for_visualization": 8,
            "min_messages_for_materialization": 15,
            "ideation_keyword_threshold": 2,
            "visualization_keyword_threshold": 3,
            "materialization_keyword_threshold": 3
        }
    
    def calculate_current_phase(self, messages: List[Dict[str, Any]], 
                              session_id: str = None) -> Dict[str, Any]:
        """
        Calculate the current design phase based on conversation content.
        
        Args:
            messages: List of conversation messages
            session_id: Optional session identifier
            
        Returns:
            Dict containing phase information and analysis
        """
        if not messages:
            return {
                "current_phase": DesignPhase.IDEATION.value,
                "phase_confidence": 1.0,
                "message_count": 0,
                "keyword_analysis": {},
                "phase_progression": 0.0,
                "next_phase": DesignPhase.VISUALIZATION.value,
                "transition_ready": False
            }
        
        # Analyze recent messages (last 10 for phase detection)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        total_messages = len(messages)
        
        # Count keywords for each phase
        keyword_counts = self._count_phase_keywords(recent_messages)
        
        # Determine current phase based on content and message count
        current_phase = self._determine_phase_from_analysis(keyword_counts, total_messages)
        
        # Calculate phase progression and confidence
        phase_progression = self._calculate_phase_progression(current_phase, total_messages)
        phase_confidence = self._calculate_phase_confidence(keyword_counts, current_phase)
        
        # Determine next phase and transition readiness
        next_phase = self._get_next_phase(current_phase)
        transition_ready = self._assess_transition_readiness(current_phase, keyword_counts, total_messages)
        
        return {
            "current_phase": current_phase.value,
            "phase_confidence": phase_confidence,
            "message_count": total_messages,
            "keyword_analysis": {
                "ideation_count": keyword_counts[DesignPhase.IDEATION],
                "visualization_count": keyword_counts[DesignPhase.VISUALIZATION],
                "materialization_count": keyword_counts[DesignPhase.MATERIALIZATION]
            },
            "phase_progression": phase_progression,
            "next_phase": next_phase.value if next_phase else None,
            "transition_ready": transition_ready,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _count_phase_keywords(self, messages: List[Dict[str, Any]]) -> Dict[DesignPhase, int]:
        """Count keywords for each phase in the messages."""
        keyword_counts = {phase: 0 for phase in DesignPhase}
        
        # Combine all message content
        all_content = " ".join([
            msg.get("content", "").lower() 
            for msg in messages 
            if msg.get("role") == "user"
        ])
        
        # Count keywords for each phase
        for phase, keywords in self.phase_keywords.items():
            for keyword in keywords:
                keyword_counts[phase] += all_content.count(keyword)
        
        return keyword_counts
    
    def _determine_phase_from_analysis(self, keyword_counts: Dict[DesignPhase, int], 
                                     total_messages: int) -> DesignPhase:
        """Determine the current phase based on keyword analysis and message count."""
        
        # Get thresholds
        min_viz = self.phase_thresholds["min_messages_for_visualization"]
        min_mat = self.phase_thresholds["min_messages_for_materialization"]
        viz_threshold = self.phase_thresholds["visualization_keyword_threshold"]
        mat_threshold = self.phase_thresholds["materialization_keyword_threshold"]
        
        viz_count = keyword_counts[DesignPhase.VISUALIZATION]
        mat_count = keyword_counts[DesignPhase.MATERIALIZATION]
        
        # Phase determination logic (conservative approach)
        if (total_messages >= min_mat and 
            mat_count >= mat_threshold and
            mat_count > viz_count):
            return DesignPhase.MATERIALIZATION
        elif (total_messages >= min_viz and 
              viz_count >= viz_threshold):
            return DesignPhase.VISUALIZATION
        else:
            return DesignPhase.IDEATION
    
    def _calculate_phase_progression(self, current_phase: DesignPhase, 
                                   total_messages: int) -> float:
        """Calculate how far through the current phase the user is (0.0 to 1.0)."""
        
        if current_phase == DesignPhase.IDEATION:
            # Progress through ideation based on message count
            max_ideation_messages = self.phase_thresholds["min_messages_for_visualization"]
            return min(1.0, total_messages / max_ideation_messages)
        
        elif current_phase == DesignPhase.VISUALIZATION:
            # Progress through visualization
            viz_start = self.phase_thresholds["min_messages_for_visualization"]
            viz_duration = self.phase_thresholds["min_messages_for_materialization"] - viz_start
            viz_progress = max(0, total_messages - viz_start)
            return min(1.0, viz_progress / viz_duration)
        
        elif current_phase == DesignPhase.MATERIALIZATION:
            # Progress through materialization (open-ended)
            mat_start = self.phase_thresholds["min_messages_for_materialization"]
            mat_progress = max(0, total_messages - mat_start)
            # Assume 15 messages for full materialization
            return min(1.0, mat_progress / 15)
        
        return 0.0
    
    def _calculate_phase_confidence(self, keyword_counts: Dict[DesignPhase, int], 
                                  current_phase: DesignPhase) -> float:
        """Calculate confidence in the current phase determination."""
        
        total_keywords = sum(keyword_counts.values())
        if total_keywords == 0:
            return 0.5  # Neutral confidence when no keywords
        
        current_phase_keywords = keyword_counts[current_phase]
        confidence = current_phase_keywords / total_keywords
        
        # Boost confidence if current phase has significantly more keywords
        other_phases_max = max([
            count for phase, count in keyword_counts.items() 
            if phase != current_phase
        ], default=0)
        
        if current_phase_keywords > other_phases_max * 1.5:
            confidence = min(1.0, confidence * 1.2)
        
        return confidence
    
    def _get_next_phase(self, current_phase: DesignPhase) -> Optional[DesignPhase]:
        """Get the next phase in the sequence."""
        phase_order = [DesignPhase.IDEATION, DesignPhase.VISUALIZATION, DesignPhase.MATERIALIZATION]
        
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _assess_transition_readiness(self, current_phase: DesignPhase, 
                                   keyword_counts: Dict[DesignPhase, int],
                                   total_messages: int) -> bool:
        """Assess if the user is ready to transition to the next phase."""
        
        if current_phase == DesignPhase.IDEATION:
            # Ready for visualization if enough messages and some spatial thinking
            return (total_messages >= self.phase_thresholds["min_messages_for_visualization"] and
                    keyword_counts[DesignPhase.VISUALIZATION] >= 2)
        
        elif current_phase == DesignPhase.VISUALIZATION:
            # Ready for materialization if enough messages and technical thinking
            return (total_messages >= self.phase_thresholds["min_messages_for_materialization"] and
                    keyword_counts[DesignPhase.MATERIALIZATION] >= 2)
        
        elif current_phase == DesignPhase.MATERIALIZATION:
            # Materialization is the final phase
            return False
        
        return False
    
    def get_phase_description(self, phase: str) -> str:
        """Get a description of what the phase involves."""
        descriptions = {
            "ideation": "Exploring concepts, understanding requirements, and developing initial ideas",
            "visualization": "Creating spatial arrangements, sketches, and visual representations",
            "materialization": "Developing technical details, materials, and construction strategies"
        }
        return descriptions.get(phase, "Design development phase")


# Global instance for use across the application
phase_calculator = PhaseCalculator()
