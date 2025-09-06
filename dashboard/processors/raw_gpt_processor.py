"""
Raw GPT processor - completely unfiltered GPT responses like ChatGPT app.
No conditioning, no socratic elements, no phase awareness, no architectural focus.
Provides pure, direct GPT responses for research comparison purposes.
Uses unified phase progression system for consistent phase tracking across all modes.
"""

import os
import sys
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from processors.phase_calculator import phase_calculator
from phase_progression_system import PhaseProgressionSystem


class PureRawGPTProcessor:
    """
    Raw GPT processor that provides completely unfiltered responses like ChatGPT app.
    No conditioning, no socratic elements, no phase awareness - pure conversational AI.
    Uses unified phase progression system for consistent phase tracking.
    """

    def __init__(self):
        self.conversation_history = {}  # Track conversations per session
        # Initialize unified phase progression system for consistent tracking
        self.phase_system = PhaseProgressionSystem()
        print("🔄 RAW_GPT: Initialized with unified phase progression system")

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
                           session_id: str = None, image_path: str = None) -> Dict[str, Any]:
        """
        Process user input with pure, unfiltered GPT response - completely raw like ChatGPT.

        Args:
            user_input: The user's input
            messages: Conversation history for context only
            session_id: Session identifier
            image_path: Optional path to uploaded image

        Returns:
            Dict containing pure GPT response and metadata
        """

        # Use unified phase progression system for consistent tracking
        if session_id:
            # Ensure session exists in phase system
            if session_id not in self.phase_system.sessions:
                self.phase_system.start_session(session_id)

            # Get phase info from unified system
            phase_summary = self.phase_system.get_session_summary(session_id)
            current_phase = phase_summary.get('current_phase', 'ideation')
            phase_info = {
                "current_phase": current_phase,
                "phase_completion": phase_summary.get('phase_summaries', {}).get(current_phase, {}).get('completion_percent', 0.0)
            }
        else:
            # Fallback to phase calculator for metadata only
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

            # Add current user input with image if provided
            if image_path:
                # For raw GPT, we include the image directly without analysis - just like ChatGPT
                import base64

                try:
                    with open(image_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

                    messages_for_api.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_input},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    })
                    print(f"📷 RAW_GPT: Added image to raw GPT request")
                except Exception as e:
                    print(f"⚠️ RAW_GPT: Failed to process image, using text only: {e}")
                    messages_for_api.append({"role": "user", "content": user_input})
            else:
                messages_for_api.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages_for_api,
                max_tokens=1500,  # Increased for image responses
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
                              session_id: str = None, image_path: str = None) -> Dict[str, Any]:
    """
    Get a completely unfiltered Raw GPT response like ChatGPT app.

    Args:
        user_input: The user's input
        messages: Conversation history for context only
        session_id: Session identifier
        image_path: Optional path to uploaded image

    Returns:
        Dict containing raw GPT response and metadata
    """

    # Use default empty messages if none provided
    if messages is None:
        messages = []

    # Use the pure processor
    return await pure_raw_gpt_processor.process_input(user_input, messages, session_id, image_path)