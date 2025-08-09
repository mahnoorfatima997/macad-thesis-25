"""
Session state management for the dashboard.
"""

import streamlit as st
from datetime import datetime
from typing import Any, Dict


def initialize_session_state():
    """Initialize Streamlit session state with default values."""
    
    # Core session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "MENTOR"
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Test-related state
    if 'test_active' not in st.session_state:
        st.session_state.test_active = False
    
    if 'test_paused' not in st.session_state:
        st.session_state.test_paused = False
    
    if 'test_config' not in st.session_state:
        st.session_state.test_config = None
    
    # Phase progression state
    if 'phase_system' not in st.session_state:
        st.session_state.phase_system = None
    
    if 'phase_session_id' not in st.session_state:
        st.session_state.phase_session_id = None
    
    # Participant/session metadata
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = "unified_user"
    
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = ""
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    
    # UI preferences
    if 'show_routing_meta' not in st.session_state:
        st.session_state.show_routing_meta = False
    
    # Input mode and mentor type for research
    if 'input_mode' not in st.session_state:
        st.session_state.input_mode = "Text Only"
    
    if 'mentor_type' not in st.session_state:
        st.session_state.mentor_type = "Socratic Agent"
    
    if 'uploaded_image_path' not in st.session_state:
        st.session_state.uploaded_image_path = None
    
    # Socratic dialogue control flags
    if 'awaiting_socratic_response' not in st.session_state:
        st.session_state.awaiting_socratic_response = False
    
    if 'current_question_id' not in st.session_state:
        st.session_state.current_question_id = None


def reset_session():
    """Reset the current session state."""
    st.session_state.messages = []
    st.session_state.analysis_results = None
    st.session_state.test_results = {}
    st.session_state.session_id = None
    st.session_state.analysis_complete = False
    st.session_state.awaiting_socratic_response = False
    st.session_state.current_question_id = None
    st.session_state.input_mode = "Text Only"
    st.session_state.mentor_type = "Socratic Agent"
    st.session_state.uploaded_image_path = None


def get_session_info() -> Dict[str, Any]:
    """Get current session information."""
    session_info = {
        'session_id': st.session_state.get('session_id'),
        'participant_id': st.session_state.get('participant_id', 'unified_user'),
        'participant_name': st.session_state.get('participant_name', ''),
        'start_time': st.session_state.get('session_start_time'),
        'current_mode': st.session_state.get('current_mode', 'MENTOR'),
        'analysis_complete': st.session_state.get('analysis_complete', False),
        'message_count': len(st.session_state.get('messages', [])),
        'test_active': st.session_state.get('test_active', False)
    }
    
    # Calculate elapsed time if session has started
    if session_info['start_time']:
        try:
            elapsed = datetime.now() - session_info['start_time']
            session_info['elapsed_minutes'] = elapsed.total_seconds() / 60.0
        except Exception:
            session_info['elapsed_minutes'] = 0.0
    else:
        session_info['elapsed_minutes'] = 0.0
    
    return session_info


def ensure_session_started():
    """Ensure a session is started and set start time if needed."""
    if not st.session_state.session_id:
        st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if st.session_state.session_id and not st.session_state.session_start_time:
        st.session_state.session_start_time = datetime.now()


def update_participant_info(participant_id: str, participant_name: str = ""):
    """Update participant information in session state."""
    st.session_state.participant_id = participant_id or "unified_user"
    st.session_state.participant_name = participant_name or "" 