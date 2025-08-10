"""
Base agent protocol for shared interface patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.agent_response import AgentResponse
from state_manager import ArchMentorState


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Provides common interface patterns and shared initialization logic
    while allowing each agent to implement its specific behavior.
    """
    
    def __init__(self, domain: str = "architecture"):
        self.domain = domain
        self.name = self.__class__.__name__.lower().replace('agent', '_agent')
    
    @abstractmethod
    async def process(self, state: ArchMentorState, context_package: Optional[Dict] = None) -> AgentResponse:
        """
        Main processing method that all agents must implement.
        
        Args:
            state: Current system state with conversation history
            context_package: Optional context from other agents
            
        Returns:
            AgentResponse with processed results
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get basic agent information."""
        return {
            "name": self.name,
            "domain": self.domain,
            "class": self.__class__.__name__
        } 