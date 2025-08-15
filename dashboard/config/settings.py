"""
Dashboard configuration settings and constants.
"""

import os
import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Centralized secrets manager that handles both Streamlit secrets and environment variables.
    Prioritizes st.secrets for Streamlit deployment, falls back to environment variables for local development.
    """

    @staticmethod
    def get_secret(key: str, default: str = "") -> str:
        """
        Get a secret value from Streamlit secrets or environment variables.

        Args:
            key: The secret key to retrieve
            default: Default value if key is not found

        Returns:
            The secret value or default
        """
        # First try Streamlit secrets (for deployment)
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                value = st.secrets[key]
                if value:  # Only return non-empty values
                    logger.debug(f"✅ Secret '{key}' loaded from st.secrets")
                    return str(value)
        except Exception as e:
            logger.debug(f"Could not access st.secrets for '{key}': {e}")

        # Fallback to environment variables (for local development)
        try:
            # Try to load from .env if not already loaded
            from dotenv import load_dotenv
            load_dotenv(override=False)  # Don't override existing env vars

            # Also try project root .env
            root_env = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
            if os.path.exists(root_env):
                load_dotenv(root_env, override=False)
        except ImportError:
            pass  # python-dotenv not available
        except Exception as e:
            logger.debug(f"Could not load .env files: {e}")

        # Get from environment
        value = os.getenv(key, default)
        if value and value != default:
            logger.debug(f"✅ Secret '{key}' loaded from environment variables")
        elif not value:
            logger.warning(f"⚠️ Secret '{key}' not found in st.secrets or environment variables")

        return value

    @staticmethod
    def get_bool_secret(key: str, default: bool = False) -> bool:
        """Get a boolean secret value."""
        value = SecretsManager.get_secret(key, str(default).lower())
        return value.lower() in ('true', '1', 'yes', 'on')

    @staticmethod
    def get_int_secret(key: str, default: int = 0) -> int:
        """Get an integer secret value."""
        try:
            return int(SecretsManager.get_secret(key, str(default)))
        except (ValueError, TypeError):
            return default

# Global secrets manager instance
secrets = SecretsManager()

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "Unified Architectural Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Input mode options
INPUT_MODES = ["Text Only", "Image + Text", "Image Only"]

# Mentor type options for research comparison
MENTOR_TYPES = ["Socratic Agent", "Raw GPT"]

# Template design prompts
TEMPLATE_PROMPTS = {
    "Select a template...": "",
    "🏢 Sustainable Office Building": "I'm designing a sustainable office building for a tech company. The building should accommodate 200 employees with flexible workspaces, meeting rooms, and common areas. I want to focus on energy efficiency, natural lighting, and creating a collaborative environment. The site is in an urban area with limited green space.",
    "🏫 Community Learning Center": "I'm creating a community learning center that will serve as a hub for education, workshops, and community events. The building needs to include classrooms, a library, multipurpose spaces, and outdoor learning areas. I want it to be welcoming to all ages and accessible to everyone in the community.",
    "🏠 Residential Complex": "I'm designing a residential complex that combines modern living with community spaces. The project includes apartments, shared amenities, and green spaces. I want to create a sense of community while maintaining privacy and sustainability.",
    "🏛️ Cultural Center": "I'm designing a cultural center that will showcase local arts and provide performance spaces. The building needs to include galleries, theaters, workshops, and public gathering areas. I want it to be both functional and inspiring."
}

# Mode options
TESTING_MODES = ["MENTOR", "RAW_GPT", "GENERIC_AI", "CONTROL"]

# Skill levels
SKILL_LEVELS = ["beginner", "intermediate", "advanced"]

# Project types for phase progression
PROJECT_TYPES = [
    "Community Center", 
    "Office Building", 
    "Residential Complex", 
    "Cultural Center", 
    "Educational Facility", 
    "Custom Project"
]

# Assessment modes
ASSESSMENT_MODES = [
    "Phase-Based Socratic", 
    "Agentic Mentor", 
    "Combined Mode"
]

# Export formats
EXPORT_FORMATS = ["JSON", "CSV", "Excel"]

def get_api_key() -> str:
    """Get API key from Streamlit secrets or environment variables"""
    return secrets.get_secret('OPENAI_API_KEY')

def get_tavily_api_key() -> str:
    """Get Tavily API key from Streamlit secrets or environment variables"""
    return secrets.get_secret('TAVILY_API_KEY')

def get_replicate_api_token() -> str:
    """Get Replicate API token from Streamlit secrets or environment variables"""
    return secrets.get_secret('REPLICATE_API_TOKEN')

def get_langsmith_api_key() -> str:
    """Get LangSmith API key from Streamlit secrets or environment variables"""
    return secrets.get_secret('LANGSMITH_API_KEY')

def get_langsmith_config() -> dict:
    """Get LangSmith configuration from Streamlit secrets or environment variables"""
    return {
        'api_key': secrets.get_secret('LANGSMITH_API_KEY'),
        'endpoint': secrets.get_secret('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com'),
        'project': secrets.get_secret('LANGSMITH_PROJECT', 'mentor'),
        'tracing': secrets.get_bool_secret('LANGSMITH_TRACING', True)
    }