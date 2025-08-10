"""
Socratic Tutor Agent Package

Modular socratic tutor agent for guided questioning and learning facilitation.
Maintains backward compatibility with the original SocraticTutorAgent class.
"""

from .adapter import SocraticTutorAgent

# Maintain backward compatibility
__all__ = ['SocraticTutorAgent'] 