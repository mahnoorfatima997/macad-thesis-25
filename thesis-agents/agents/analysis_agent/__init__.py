"""
Analysis Agent Package

Modular analysis agent for architectural design assessment and cognitive enhancement.
Maintains backward compatibility with the original AnalysisAgent class.
"""

from .adapter import AnalysisAgent

# Maintain backward compatibility
__all__ = ['AnalysisAgent'] 