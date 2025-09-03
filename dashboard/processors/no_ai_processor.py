"""
No AI processor for control group - provides hardcoded questions without AI assistance.
Used for research comparison purposes.
Uses unified phase progression system for consistent phase tracking across all modes.
"""

import streamlit as st
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from processors.phase_calculator import phase_calculator
from phase_progression_system import PhaseProgressionSystem


class NoAIProcessor:
    """Provides hardcoded questions for each phase without any AI assistance.
    Uses unified phase progression system for consistent phase tracking."""

    def __init__(self):
        self.phase_questions = self._initialize_phase_questions()
        self.question_counters = {}  # Track which question to ask next for each phase
        # Initialize unified phase progression system for consistent tracking
        self.phase_system = PhaseProgressionSystem()
        print("🔄 NO_AI: Initialized with unified phase progression system")
    
    def _initialize_phase_questions(self) -> Dict[str, List[str]]:
        """Initialize hardcoded questions for each phase."""
        return {
            "ideation": [
                "What are the main functions this community center should serve?",
                "Who are the primary users you expect to use this space?",
                "What are the key spatial requirements for your program?",
                "How might the existing warehouse structure influence your design approach?",
                "What are the most important adjacencies between different program areas?",
                "How do you envision people moving through the space?",
                "What kind of atmosphere do you want to create in this community center?",
                "How might you address accessibility requirements in your design?",
                "What outdoor connections or extensions might be important?",
                "How could the design reflect the local community's identity?"
            ],
            "visualization": [
                "How would you organize the main spaces in plan view?",
                "What would be the primary circulation route through the building?",
                "How might you show the relationship between indoor and outdoor spaces?",
                "What drawing type would best communicate your spatial concept?",
                "How would you represent the scale and proportion of your spaces?",
                "What sectional relationships are most important to show?",
                "How might you illustrate the connection between different floor levels?",
                "What views or perspectives would best explain your design?",
                "How would you show the integration of new and existing elements?",
                "What details are most important to communicate at this stage?"
            ],
            "materialization": [
                "What structural system would be most appropriate for this project?",
                "How might you integrate new structure with the existing warehouse frame?",
                "What materials would best support your design concept?",
                "How would you address thermal comfort and energy efficiency?",
                "What lighting strategy would work best for your program mix?",
                "How might you detail the connection between old and new construction?",
                "What building systems require the most careful integration?",
                "How would you approach acoustic separation between different uses?",
                "What sustainable strategies are most relevant to this project?",
                "How might construction phasing affect your design decisions?"
            ]
        }
    
    def get_next_question(self, phase: str, session_id: str) -> str:
        """Get the next hardcoded question for the specified phase."""
        # Normalize phase name
        phase_key = phase.lower()
        if phase_key not in self.phase_questions:
            print(f"🚨 NO_AI: Unknown phase '{phase_key}', available phases: {list(self.phase_questions.keys())}")
            return "Please describe your current design thinking."

        # Initialize counter for this session and phase if needed
        counter_key = f"{session_id}_{phase_key}"
        if counter_key not in self.question_counters:
            self.question_counters[counter_key] = 0
            print(f"🔄 NO_AI: Initialized counter for {counter_key} = 0")

        # Get questions for this phase
        questions = self.phase_questions[phase_key]
        current_index = self.question_counters[counter_key]

        print(f"📊 NO_AI: Phase={phase_key}, Question {current_index + 1}/{len(questions)}")
        print(f"🔢 NO_AI: Counter key={counter_key}, Current index={current_index}")

        # If we've asked all questions, cycle back or provide a generic prompt
        if current_index >= len(questions):
            print(f"🔄 NO_AI: All {len(questions)} questions asked for {phase_key}, providing generic prompt")
            return "What other aspects of your design would you like to explore further?"

        # Get the current question and increment counter
        question = questions[current_index]
        self.question_counters[counter_key] += 1

        print(f"❓ NO_AI: Asking question {current_index + 1}: {question[:50]}...")
        print(f"🔢 NO_AI: Incremented counter to {self.question_counters[counter_key]}")

        return question
    
    def get_response_to_user_input(self, user_input: str, messages: List[Dict[str, Any]],
                                  session_id: str) -> Dict[str, Any]:
        """
        Process user input and return the next hardcoded question.
        Uses unified phase progression system for consistent phase tracking.
        This simulates the control group experience with no AI assistance.
        """

        # Use unified phase progression system for consistent tracking
        if session_id:
            # Ensure session exists in phase system
            if session_id not in self.phase_system.sessions:
                self.phase_system.start_session(session_id)

            # Process the user message to update phase progression
            # Note: For No AI mode, we don't use the returned question, just track progression
            self.phase_system.process_user_message(session_id, user_input)

            # Get phase info from unified system
            phase_summary = self.phase_system.get_session_summary(session_id)
            current_phase = phase_summary.get('current_phase', 'ideation')
            phase_info = {
                "current_phase": current_phase,
                "phase_completion": phase_summary.get('phase_summaries', {}).get(current_phase, {}).get('completion_percent', 0.0)
            }
        else:
            # Fallback to phase calculator
            phase_info = phase_calculator.calculate_current_phase(messages, session_id)
            current_phase = phase_info["current_phase"]

        # Get the next hardcoded question for this phase
        next_question = self.get_next_question(current_phase, session_id)

        # Create a simple acknowledgment + next question response
        response = f"Thank you for sharing your thoughts. {next_question}"

        return {
            "response": response,
            "metadata": {
                "response_type": "no_ai",
                "agents_used": ["hardcoded_questions"],
                "interaction_type": "control_group",
                "confidence_level": "n/a",
                "understanding_level": "n/a",
                "engagement_level": "n/a",
                "sources": [],
                "response_time": 0,
                "routing_path": "no_ai",
                "current_phase": current_phase,
                "phase_info": phase_info,
                "question_number": self.question_counters.get(f"{session_id}_{current_phase.lower()}", 1)
            },
            "routing_path": "no_ai",
            "classification": {
                "interaction_type": "control_group",
                "confidence_level": "n/a",
                "understanding_level": "n/a",
                "engagement_level": "n/a"
            },
            "phase_info": phase_info
        }
    
    def reset_session_counters(self, session_id: str):
        """Reset question counters for a specific session."""
        keys_to_remove = [key for key in self.question_counters.keys() if key.startswith(session_id)]
        for key in keys_to_remove:
            del self.question_counters[key]
    
    def get_session_progress(self, session_id: str) -> Dict[str, int]:
        """Get the current question progress for each phase in a session."""
        progress = {}
        for phase in self.phase_questions.keys():
            counter_key = f"{session_id}_{phase}"
            progress[phase] = self.question_counters.get(counter_key, 0)
        return progress


# Global instance for use across the application
no_ai_processor = NoAIProcessor()


async def get_no_ai_response(user_input: str, messages: List[Dict[str, Any]] = None,
                            session_id: str = None, image_path: str = None) -> Dict[str, Any]:
    """
    Get a hardcoded response for the no AI control group.

    Args:
        user_input: The user's input (acknowledged but not processed)
        messages: Conversation history for phase calculation
        session_id: Session identifier for tracking question progression
        image_path: Optional path to uploaded image (acknowledged but not analyzed)

    Returns:
        Dict containing the hardcoded response and metadata
    """
    if not session_id:
        session_id = st.session_state.get("session_id", "default_session")

    if messages is None:
        messages = []

    # For No AI mode, we acknowledge the image but don't analyze it
    response = no_ai_processor.get_response_to_user_input(user_input, messages, session_id)

    # Add image acknowledgment if image was provided
    if image_path:
        original_response = response.get("response", "")
        image_acknowledgment = "Thank you for sharing the image. "
        response["response"] = image_acknowledgment + original_response
        print(f"📷 NO_AI: Acknowledged image upload without analysis")

    return response
