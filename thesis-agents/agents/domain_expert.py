"""
Domain Expert Agent - Backward Compatibility Wrapper

This file maintains backward compatibility by importing the refactored DomainExpertAgent
from the new modular structure.
"""

# Import the refactored DomainExpertAgent from the modular package
from .domain_expert import DomainExpertAgent

# Import utility functions for backward compatibility
from .domain_expert.adapter import is_building_request, is_landscape_request

# Re-export for backward compatibility
__all__ = ['DomainExpertAgent', 'is_building_request', 'is_landscape_request']