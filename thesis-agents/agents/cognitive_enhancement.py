"""
Cognitive Enhancement Agent - Backward Compatibility Wrapper

This file maintains backward compatibility by importing the refactored CognitiveEnhancementAgent
from the new modular structure.
"""

# Import the refactored CognitiveEnhancementAgent from the modular package
from .cognitive_enhancement import CognitiveEnhancementAgent

# Re-export for backward compatibility
__all__ = ['CognitiveEnhancementAgent']