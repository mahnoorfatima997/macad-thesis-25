"""
Cognitive Enhancement Agent Package

Modular cognitive enhancement agent for challenging assumptions and preventing cognitive offloading.
Maintains backward compatibility with the original CognitiveEnhancementAgent class.
"""

from .adapter import CognitiveEnhancementAgent

# Maintain backward compatibility
__all__ = ['CognitiveEnhancementAgent'] 