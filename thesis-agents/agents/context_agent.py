"""
Context Agent - Backward Compatibility Wrapper

This file maintains backward compatibility by importing the refactored ContextAgent
from the new modular structure.
"""

# Import the refactored ContextAgent from the modular package
from .context_agent import ContextAgent

# Re-export for backward compatibility
__all__ = ['ContextAgent']