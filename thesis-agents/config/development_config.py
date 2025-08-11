#!/usr/bin/env python3
"""
Development configuration for cost-efficient testing
"""

import os
from typing import Dict, Any

class DevelopmentConfig:
    """Configuration for cheap development testing"""
    
    def __init__(self):
        # Development mode flag
        self.DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
        
        # Model configurations for cost efficiency
        self.models = {
            "expensive": "gpt-4o",           # Production model
            "cheap": "gpt-3.5-turbo",       # Development model  
            "mini": "gpt-4o-mini"           # Ultra cheap model
        }
        
        # Token limits for development - Increased for generous responses
        self.token_limits = {
            "analysis": 1200,     # Generous for detailed analysis
            "socratic": 800,      # Generous for thoughtful questions
            "domain": 1000,       # Generous for comprehensive knowledge
            "synthesis": 1500,    # Generous for complete synthesis
            "classification": 400 # Generous for detailed classification
        }
        
        # Enable/disable expensive features
        self.features = {
            "web_search": False,              # Disable expensive web searches
            "multi_agent_synthesis": False,   # Use single agent responses
            "context_classification": True,   # Keep basic classification
            "visual_analysis": False,         # Disable GPT-4V calls
            "flexible_prompts": False         # Use cached/simple prompts
        }
        
        # Mock responses for testing
        self.mock_responses = {
            "analysis": {
                "cognitive_flags": ["needs_brief_development"],
                "skill_assessment": {"level": "intermediate"},
                "confidence": 0.8
            },
            "socratic": {
                "response_text": "What aspects of this design challenge you most?",
                "response_type": "mock_socratic"
            },
            "domain": {
                "knowledge_response": {
                    "response": "Here are some key principles for this topic...",
                    "has_knowledge": True,
                    "source": "mock_knowledge"
                }
            }
        }
    
    def get_model(self, use_case: str = "cheap") -> str:
        """Get appropriate model for development"""
        if self.DEV_MODE:
            return self.models.get("cheap", "gpt-3.5-turbo")
        return self.models.get("expensive", "gpt-4o")
    
    def get_token_limit(self, component: str) -> int:
        """Get token limit for component"""
        return self.token_limits.get(component, 100)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if expensive feature is enabled"""
        if not self.DEV_MODE:
            return True  # All features enabled in production
        return self.features.get(feature, False)
    
    def get_mock_response(self, component: str) -> Dict[str, Any]:
        """Get mock response for component"""
        return self.mock_responses.get(component, {})

# Global config instance
dev_config = DevelopmentConfig()

def use_cheap_model() -> str:
    """Quick helper to get cheap model"""
    return dev_config.get_model("cheap")

def should_skip_expensive_call(feature: str) -> bool:
    """Quick helper to check if expensive call should be skipped"""
    return not dev_config.is_feature_enabled(feature)

def get_dev_token_limit(component: str) -> int:
    """Quick helper to get development token limit"""
    return dev_config.get_token_limit(component)