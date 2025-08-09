"""
Socratic Tutor Agent - Backward Compatibility Wrapper

This file maintains backward compatibility by importing the refactored SocraticTutorAgent
from the new modular structure.
"""

# Import the refactored SocraticTutorAgent from the modular package
from .socratic_tutor import SocraticTutorAgent

# Re-export for backward compatibility
__all__ = ['SocraticTutorAgent']