"""
Pure Raw GPT processor - completely independent of multi-agent system.
Provides direct GPT responses with phase-aware context but no socratic training.
Used for research comparison purposes.
"""

import os
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime
from .phase_calculator import phase_calculator


class PureRawGPTProcessor:
    """
    Pure Raw GPT processor that is completely independent of the multi-agent system.
    Uses only direct GPT calls with phase-aware context.
    """

    def __init__(self):
        self.conversation_history = {}  # Track conversations per session

    def get_phase_aware_context(self, messages: List[Dict[str, Any]],
                               current_phase: str) -> str:
        """Create phase-aware context for GPT without any socratic elements."""

        phase_contexts = {
            "ideation": """You are an architectural expert helping with the IDEATION phase of design.
            Focus on: concept development, program analysis, user needs, site context, and initial ideas.
            Provide direct, comprehensive answers about architectural concepts and design thinking.""",

            "visualization": """You are an architectural expert helping with the VISUALIZATION phase of design.
            Focus on: spatial arrangements, sketching techniques, plans/sections/elevations, circulation, and form development.
            Provide direct, comprehensive answers about architectural visualization and spatial design.""",

            "materialization": """You are an architectural expert helping with the MATERIALIZATION phase of design.
            Focus on: materials, construction systems, technical details, building systems, and implementation strategies.
            Provide direct, comprehensive answers about architectural technology and construction."""
        }

        base_context = phase_contexts.get(current_phase, phase_contexts["ideation"])

        # Add conversation context if available
        if len(messages) > 1:
            recent_context = "\n\nRecent conversation context:\n"
            for msg in messages[-3:]:  # Last 3 messages for context
                if msg.get("role") == "user":
                    recent_context += f"Student: {msg.get('content', '')[:100]}...\n"
                elif msg.get("role") == "assistant":
                    recent_context += f"You previously: {msg.get('content', '')[:100]}...\n"
            base_context += recent_context

        return base_context

    async def process_input(self, user_input: str, messages: List[Dict[str, Any]],
                           session_id: str = None) -> Dict[str, Any]:
        """
        Process user input with pure GPT response - no multi-agent system involvement.

        Args:
            user_input: The user's input
            messages: Conversation history for context
            session_id: Session identifier

        Returns:
            Dict containing GPT response and metadata
        """

        # Calculate current phase using standalone calculator
        phase_info = phase_calculator.calculate_current_phase(messages, session_id)
        current_phase = phase_info["current_phase"]

        # Get phase-aware context
        context = self.get_phase_aware_context(messages, current_phase)

        # Create the prompt for direct GPT response
        prompt = f"""{context}

STUDENT QUESTION: "{user_input}"

CURRENT DESIGN PHASE: {current_phase.upper()}
PHASE DESCRIPTION: {phase_calculator.get_phase_description(current_phase)}

Provide a detailed, informative answer that directly addresses their question.
Give specific architectural advice, examples, and technical information appropriate for the {current_phase} phase.
Be comprehensive and educational, but avoid asking socratic questions - give direct answers and guidance."""

        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )

            raw_response = response.choices[0].message.content.strip()

            return {
                "response": raw_response,
                "metadata": {
                    "response_type": "pure_raw_gpt",
                    "agents_used": ["gpt-4o"],
                    "interaction_type": "direct_answer",
                    "confidence_level": "high",
                    "understanding_level": "high",
                    "engagement_level": "medium",
                    "sources": [],
                    "response_time": 0,
                    "routing_path": "pure_raw_gpt",
                    "current_phase": current_phase,
                    "phase_info": phase_info,
                    "no_socratic_elements": True,
                    "pure_gpt": True
                },
                "routing_path": "pure_raw_gpt",
                "classification": {
                    "interaction_type": "direct_answer",
                    "confidence_level": "high",
                    "understanding_level": "high",
                    "engagement_level": "medium"
                },
                "phase_info": phase_info
            }

        except Exception as e:
            print(f"❌ Pure Raw GPT response failed: {e}")
            return {
                "response": "I apologize, but I'm unable to provide a response at the moment. Please try again.",
                "metadata": {
                    "response_type": "error",
                    "agents_used": [],
                    "error": str(e),
                    "routing_path": "error",
                    "current_phase": current_phase,
                    "phase_info": phase_info,
                    "no_socratic_elements": True,
                    "pure_gpt": True
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
    Get a pure Raw GPT response completely independent of multi-agent system.

    Args:
        user_input: The user's input
        messages: Conversation history for phase calculation and context
        session_id: Session identifier

    Returns:
        Dict containing pure GPT response and metadata
    """

    # Use default empty messages if none provided
    if messages is None:
        messages = []

    # Use the pure processor
    return await pure_raw_gpt_processor.process_input(user_input, messages, session_id)