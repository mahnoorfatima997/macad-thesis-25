"""
Analysis Agent - Backward Compatibility Wrapper

This file maintains backward compatibility by importing the refactored AnalysisAgent
from the new modular structure.
"""

# Import the refactored AnalysisAgent from the modular package
from .analysis_agent.adapter import AnalysisAgent

# Re-export for backward compatibility
__all__ = ['AnalysisAgent']