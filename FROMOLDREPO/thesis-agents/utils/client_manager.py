"""
Shared OpenAI client manager to avoid multiple client instances per agent.
"""

from typing import Optional
import os
import threading
from openai import OpenAI

_client_lock = threading.Lock()
_shared_client: Optional[OpenAI] = None


def get_shared_client() -> OpenAI:
    """Return a singleton OpenAI client configured from environment.

    Ensures all agents reuse the same client to reduce memory usage and
    maintain consistent configuration.
    """
    global _shared_client
    if _shared_client is None:
        with _client_lock:
            if _shared_client is None:
                api_key = os.getenv("OPENAI_API_KEY")
                _shared_client = OpenAI(api_key=api_key)
    return _shared_client


