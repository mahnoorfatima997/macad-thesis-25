"""
Domain Expert Agent Package

Modular domain expert agent for architectural knowledge retrieval and synthesis.
Maintains backward compatibility with the original DomainExpertAgent class.
"""

from .adapter import DomainExpertAgent

# Maintain backward compatibility
__all__ = ['DomainExpertAgent'] 