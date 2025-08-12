"""
Phase-Based Assessment System

Implements the structured Socratic Assessment Framework with automatic phase detection,
Socratic questioning patterns, and progression tracking as described in phase_based.txt.
"""

from .phase_manager import (
    PhaseAssessmentManager,
    DesignPhase,
    SocraticStep,
    PhaseAssessment,
    SocraticQuestion
)

__all__ = [
    'PhaseAssessmentManager',
    'DesignPhase', 
    'SocraticStep',
    'PhaseAssessment',
    'SocraticQuestion'
]
