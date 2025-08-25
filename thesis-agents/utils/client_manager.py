"""
Shared OpenAI client manager to avoid multiple client instances per agent.
"""

from typing import Optional
import os
import threading
from openai import OpenAI

try:
    from .secrets_manager import get_openai_api_key
except ImportError:
    # Fallback if secrets_manager is not available
    def get_openai_api_key() -> str:
        return os.getenv("OPENAI_API_KEY", "")

_client_lock = threading.Lock()
_shared_client: Optional[OpenAI] = None


def get_shared_client() -> OpenAI:
    """Return a singleton OpenAI client configured from secrets manager.

    Ensures all agents reuse the same client to reduce memory usage and
    maintain consistent configuration. Uses secrets manager for API key.
    """
    global _shared_client
    if _shared_client is None:
        with _client_lock:
            if _shared_client is None:
                api_key = get_openai_api_key()
                _shared_client = OpenAI(api_key=api_key)
    return _shared_client


