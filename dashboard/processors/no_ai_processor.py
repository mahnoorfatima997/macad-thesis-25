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
            return "Please describe your current design thinking."
        
        # Initialize counter for this session and phase if needed
        counter_key = f"{session_id}_{phase_key}"
        if counter_key not in self.question_counters:
            self.question_counters[counter_key] = 0
        
        # Get questions for this phase
        questions = self.phase_questions[phase_key]
        current_index = self.question_counters[counter_key]
        
        # If we've asked all questions in this phase, provide a generic prompt
        # The phase transition logic will handle moving to the next phase
        if current_index >= len(questions):
            if phase_key == "materialization":
                return "What other aspects of your final design would you like to explore or refine?"
            else:
                return "What other aspects of your design would you like to explore further?"
        
        # Get the current question and increment counter
        question = questions[current_index]
        self.question_counters[counter_key] += 1
        
        return question
    
    def get_response_to_user_input(self, user_input: str, messages: List[Dict[str, Any]],
                                  session_id: str) -> Dict[str, Any]:
        """
        Process user input and return the next hardcoded question.
        Uses simple question-count based phase progression for no AI mode.
        This simulates the control group experience with no AI assistance.
        """

        # For No AI mode, use simple question-count based phase progression
        current_phase = self._determine_current_phase_by_questions(session_id)

        # Get the next hardcoded question for this phase
        next_question = self.get_next_question(current_phase, session_id)

        # Create phase info compatible with existing dashboard systems
        phase_completion = self._calculate_phase_completion(current_phase, session_id)
        phase_info = {
            "current_phase": current_phase,
            "phase_completion": phase_completion,
            "phase_progression": phase_completion / 100.0  # Convert to 0-1 scale for compatibility
        }

        # Update session state for dashboard integration
        import streamlit as st
        if hasattr(st, 'session_state'):
            st.session_state.test_current_phase = current_phase.title()  # Ideation, Visualization, Materialization
            st.session_state.phase_completion_percent = phase_completion
            # Store phase info for dashboard to access
            st.session_state.no_ai_phase_info = phase_info
            print(f"🔄 NO_AI: Stored phase info in session state: {phase_info}")

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
    
    def _determine_current_phase_by_questions(self, session_id: str) -> str:
        """Determine current phase based on question count progression."""
        # Get current question counts for each phase
        ideation_count = self.question_counters.get(f"{session_id}_ideation", 0)
        visualization_count = self.question_counters.get(f"{session_id}_visualization", 0)
        materialization_count = self.question_counters.get(f"{session_id}_materialization", 0)

        # Phase progression logic: move to next phase after asking all questions in current phase
        ideation_total = len(self.phase_questions["ideation"])
        visualization_total = len(self.phase_questions["visualization"])

        if ideation_count < ideation_total:
            return "ideation"
        elif visualization_count < visualization_total:
            return "visualization"
        else:
            return "materialization"

    def _calculate_phase_completion(self, phase: str, session_id: str) -> float:
        """Calculate phase completion percentage based on questions asked."""
        counter_key = f"{session_id}_{phase.lower()}"
        questions_asked = self.question_counters.get(counter_key, 0)
        total_questions = len(self.phase_questions.get(phase.lower(), []))

        if total_questions == 0:
            return 0.0

        # Cap at 100% completion
        completion = min((questions_asked / total_questions) * 100, 100.0)
        return completion

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
    Simple: just get the next question from the hardcoded list.
    """
    if not session_id:
        session_id = st.session_state.get("session_id", "default_session")

    if messages is None:
        messages = []

    # Use the basic no AI processor - it already has the question cycling logic
    response = no_ai_processor.get_response_to_user_input(user_input, messages, session_id)

    # Add image acknowledgment if image was provided
    if image_path:
        original_response = response.get("response", "")
        image_acknowledgment = "Thank you for sharing the image. "
        response["response"] = image_acknowledgment + original_response

    return response
