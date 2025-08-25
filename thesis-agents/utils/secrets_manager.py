"""
Centralized secrets manager for the MEGA Architectural Mentor system.
Handles both Streamlit secrets and environment variables with proper fallback.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Centralized secrets manager that handles both Streamlit secrets and environment variables.
    Prioritizes st.secrets for Streamlit deployment, falls back to environment variables for local development.
    """
    
    def __init__(self):
        self._env_loaded = False
        self._load_env_files()
    
    def _load_env_files(self):
        """Load environment files if available and not already loaded."""
        if self._env_loaded:
            return
            
        try:
            from dotenv import load_dotenv
            
            # Load from current directory
            load_dotenv(override=False)
            
            # Try to load from project root (relative to this file)
            project_root_env = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "..", "..", ".env")
            )
            if os.path.exists(project_root_env):
                load_dotenv(project_root_env, override=False)
                logger.debug(f"Loaded .env from: {project_root_env}")
            
            self._env_loaded = True
            
        except ImportError:
            logger.debug("python-dotenv not available, skipping .env file loading")
        except Exception as e:
            logger.debug(f"Could not load .env files: {e}")
    
    def get_secret(self, key: str, default: str = "") -> str:
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
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                value = st.secrets[key]
                if value:  # Only return non-empty values
                    logger.debug(f"✅ Secret '{key}' loaded from st.secrets")
                    return str(value)
        except ImportError:
            # Streamlit not available (e.g., in standalone scripts)
            pass
        except Exception as e:
            logger.debug(f"Could not access st.secrets for '{key}': {e}")
        
        # Fallback to environment variables (for local development)
        self._load_env_files()
        value = os.getenv(key, default)
        
        if value and value != default:
            logger.debug(f"✅ Secret '{key}' loaded from environment variables")
        elif not value:
            logger.warning(f"⚠️ Secret '{key}' not found in st.secrets or environment variables")
        
        return value
    
    def get_bool_secret(self, key: str, default: bool = False) -> bool:
        """Get a boolean secret value."""
        value = self.get_secret(key, str(default).lower())
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int_secret(self, key: str, default: int = 0) -> int:
        """Get an integer secret value."""
        try:
            return int(self.get_secret(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    def get_float_secret(self, key: str, default: float = 0.0) -> float:
        """Get a float secret value."""
        try:
            return float(self.get_secret(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    def get_all_secrets(self) -> Dict[str, str]:
        """Get all available secrets (for debugging purposes)."""
        secrets_dict = {}
        
        # Try Streamlit secrets first
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                for key in st.secrets:
                    secrets_dict[key] = "***HIDDEN***"  # Don't expose actual values
        except ImportError:
            pass
        except Exception:
            pass
        
        # Add environment variables (common API keys only)
        common_keys = [
            'OPENAI_API_KEY', 'TAVILY_API_KEY', 'REPLICATE_API_TOKEN',
            'LANGSMITH_API_KEY', 'LANGSMITH_ENDPOINT', 'LANGSMITH_PROJECT',
            'LANGSMITH_TRACING'
        ]
        
        for key in common_keys:
            if os.getenv(key):
                secrets_dict[key] = "***HIDDEN***"
        
        return secrets_dict

# Global secrets manager instance
secrets_manager = SecretsManager()

# Convenience functions for common API keys
def get_openai_api_key() -> str:
    """Get OpenAI API key."""
    return secrets_manager.get_secret('OPENAI_API_KEY')

def get_tavily_api_key() -> str:
    """Get Tavily API key."""
    return secrets_manager.get_secret('TAVILY_API_KEY')

def get_replicate_api_token() -> str:
    """Get Replicate API token."""
    return secrets_manager.get_secret('REPLICATE_API_TOKEN')

def get_langsmith_config() -> Dict[str, Any]:
    """Get LangSmith configuration."""
    return {
        'api_key': secrets_manager.get_secret('LANGSMITH_API_KEY'),
        'endpoint': secrets_manager.get_secret('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com'),
        'project': secrets_manager.get_secret('LANGSMITH_PROJECT', 'mentor'),
        'tracing': secrets_manager.get_bool_secret('LANGSMITH_TRACING', True)
    }

# For backward compatibility
def get_secret(key: str, default: str = "") -> str:
    """Backward compatibility function."""
    return secrets_manager.get_secret(key, default)
