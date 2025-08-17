"""
Raw GPT processor - completely unfiltered GPT responses like ChatGPT app.
No conditioning, no socratic elements, no phase awareness, no architectural focus.
Provides pure, direct GPT responses for research comparison purposes.
"""

import os
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime
from .phase_calculator import phase_calculator


class PureRawGPTProcessor:
    """
    Raw GPT processor that provides completely unfiltered responses like ChatGPT app.
    No conditioning, no socratic elements, no phase awareness - pure conversational AI.
    """

    def __init__(self):
        self.conversation_history = {}  # Track conversations per session

    def get_minimal_context(self, messages: List[Dict[str, Any]]) -> str:
        """Create minimal context for pure GPT response - no conditioning or phase awareness."""

        # Only provide basic conversation context if available
        if len(messages) > 1:
            context = "Previous conversation:\n"
            for msg in messages[-3:]:  # Last 3 messages for context only
                if msg.get("role") == "user":
                    context += f"User: {msg.get('content', '')}\n"
                elif msg.get("role") == "assistant":
                    context += f"Assistant: {msg.get('content', '')}\n"
            return context

        return ""

    async def process_input(self, user_input: str, messages: List[Dict[str, Any]],
                           session_id: str = None) -> Dict[str, Any]:
        """
        Process user input with pure, unfiltered GPT response - completely raw like ChatGPT.

        Args:
            user_input: The user's input
            messages: Conversation history for context only
            session_id: Session identifier

        Returns:
            Dict containing pure GPT response and metadata
        """

        # Calculate current phase for metadata only (not used in response generation)
        phase_info = phase_calculator.calculate_current_phase(messages, session_id)
        current_phase = phase_info["current_phase"]

        # Get minimal conversation context only
        context = self.get_minimal_context(messages)

        # Create completely raw prompt - no conditioning, no phase awareness, no architectural focus
        if context:
            prompt = f"""{context}

User: {user_input}"""
        else:
            prompt = user_input

        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Use conversation format for better context handling
            messages_for_api = []

            # Add conversation history if available
            if len(messages) > 1:
                for msg in messages[-5:]:  # Last 5 messages for context
                    role = "user" if msg.get("role") == "user" else "assistant"
                    content = msg.get("content", "")
                    if content:
                        messages_for_api.append({"role": role, "content": content})

            # Add current user input
            messages_for_api.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages_for_api,
                max_tokens=1000,
                temperature=0.7  # Higher temperature for more natural responses
            )

            raw_response = response.choices[0].message.content.strip()

            return {
                "response": raw_response,
                "metadata": {
                    "response_type": "raw_gpt_unfiltered",
                    "agents_used": ["gpt-4o"],
                    "interaction_type": "raw_conversation",
                    "confidence_level": "high",
                    "understanding_level": "high",
                    "engagement_level": "medium",
                    "sources": [],
                    "response_time": 0,
                    "routing_path": "raw_gpt_unfiltered",
                    "current_phase": current_phase,
                    "phase_info": phase_info,
                    "no_conditioning": True,
                    "no_socratic_elements": True,
                    "no_phase_awareness": True,
                    "pure_chatgpt_style": True
                },
                "routing_path": "raw_gpt_unfiltered",
                "classification": {
                    "interaction_type": "raw_conversation",
                    "confidence_level": "high",
                    "understanding_level": "high",
                    "engagement_level": "medium"
                },
                "phase_info": phase_info
            }

        except Exception as e:
            print(f"❌ Raw GPT response failed: {e}")
            return {
                "response": "I apologize, but I'm unable to provide a response at the moment. Please try again.",
                "metadata": {
                    "response_type": "error",
                    "agents_used": [],
                    "error": str(e),
                    "routing_path": "error",
                    "current_phase": current_phase,
                    "phase_info": phase_info,
                    "no_conditioning": True,
                    "no_socratic_elements": True,
                    "no_phase_awareness": True,
                    "pure_chatgpt_style": True
                },
                "routing_path": "error",
                "classification": {},
                "phase_info": phase_info
            }


# Global instance
pure_raw_gpt_processor = PureRawGPTProcessor()


async def get_raw_gpt_response(user_input: str, messages: List[Dict[str, Any]] = None,
                              session_id: str = None) -> Dict[str, Any]:
    """
    Get a completely unfiltered Raw GPT response like ChatGPT app.

    Args:
        user_input: The user's input
        messages: Conversation history for context only
        session_id: Session identifier

    Returns:
        Dict containing raw GPT response and metadata
    """

    # Use default empty messages if none provided
    if messages is None:
        messages = []

    # Use the pure processor
    return await pure_raw_gpt_processor.process_input(user_input, messages, session_id)