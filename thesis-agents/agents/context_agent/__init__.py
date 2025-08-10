"""
Context Agent Package

Modular context agent for conversation analysis and routing decisions.
Maintains backward compatibility with the original ContextAgent class.
"""

from .adapter import ContextAgent

# Maintain backward compatibility
__all__ = ['ContextAgent'] 