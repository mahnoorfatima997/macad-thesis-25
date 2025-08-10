"""
Sidebar components for the dashboard.
"""

import streamlit as st
from datetime import datetime
from typing import Optional

from ..config.settings import get_api_key
from ..core.session_manager import get_session_info, reset_session


def render_api_status():
    """Render API key status."""
    api_key = get_api_key()
    if api_key:
        st.success("✅ API Key: Configured")
    else:
        st.error("❌ API Key: Missing")
    return bool(api_key)


def render_participant_info():
    """Render participant information section."""
    st.markdown("### 👤 Participant")
    
    # Get current values
    current_pid = st.session_state.get('participant_id', 'unified_user')
    current_name = st.session_state.get('participant_name', '')
    
    # Input fields
    pid = st.text_input("Participant ID", value=current_pid)
    pname = st.text_input("Name (optional)", value=current_name)
    
    # Update session state
    st.session_state.participant_id = pid or "unified_user"
    st.session_state.participant_name = pname or ""


def render_session_info():
    """Render session information section."""
    st.markdown("### 🕒 Session")
    
    session_info = get_session_info()
    
    # Display session ID
    st.caption(f"ID: {session_info['session_id'] or '—'}")
    
    # Display start time and elapsed time
    if session_info['start_time']:
        st.caption(f"Started: {session_info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        if session_info['elapsed_minutes'] > 0:
            st.caption(f"Elapsed: {session_info['elapsed_minutes']:.1f} min")


def render_system_status():
    """Render system status section."""
    st.markdown("### 🔧 System Status")
    st.info("**Vision**: GPT Vision Available")
    st.info("**Agents**: Multi-Agent System Ready")
    
    # Routing metadata toggle
    st.checkbox("Show route/agents meta in replies", key="show_routing_meta")


def render_current_session_status():
    """Render current session status if analysis is complete."""
    if st.session_state.get('analysis_complete', False):
        st.markdown("### 📊 Current Session")
        current_mode = st.session_state.get('current_mode', 'MENTOR')
        
        if current_mode == "MENTOR":
            st.success(f"**Mode**: {current_mode} 🤖")
        elif current_mode == "GENERIC_AI":
            st.warning(f"**Mode**: {current_mode} 🤖")
        else:
            st.info(f"**Mode**: {current_mode} 🎯")


def render_session_management(data_collector=None):
    """Render session management section."""
    st.markdown("### 📊 Session Management")
    
    # Reset session button
    if st.button("🔄 Reset Session"):
        reset_session()
        st.success("Session reset successfully!")
        st.rerun()
    
    # Reset data collector button
    if data_collector and st.button("🔄 Reset Data Collector"):
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../thesis-agents'))
        from data_collection.interaction_logger import InteractionLogger
        st.session_state.data_collector = InteractionLogger(session_id="unified_dashboard_session")
        st.success("Data collector reset!")
        st.rerun()
    
    # Export data button
    if st.button("💾 Export Data"):
        export_session_data(data_collector)


def render_pretest_section():
    """Render pre-test visibility toggle in the sidebar."""
    # Initialize the toggle if missing
    if 'show_pre_test' not in st.session_state:
        st.session_state.show_pre_test = False

    st.markdown("### 🧪 Pre-Test (optional)")
    st.checkbox(
        "Show Pre-Test before chat",
        key="show_pre_test",
        help="When checked, the pre-test appears above the mentor chat in the main area."
    )


def export_session_data(data_collector=None):
    """Export session data functionality with enhanced research metrics."""
    if not st.session_state.get('messages', []):
        st.warning("No data to export")
        return
    
    # Export comprehensive data using InteractionLogger
    if data_collector and hasattr(data_collector, 'interactions') and len(data_collector.interactions) > 0:
        try:
            summary = data_collector.export_for_thesis_analysis()
            st.success("✅ Session data exported to thesis_data/")
            st.info(f"Files created: interactions_{data_collector.session_id}.csv, "
                   f"design_moves_{data_collector.session_id}.csv, "
                   f"session_summary_{data_collector.session_id}.json, "
                   f"full_log_{data_collector.session_id}.json")
            
            # Show key research metrics
            if summary:
                st.metric("Total Interactions", len(data_collector.interactions))
                if 'cognitive_offloading_prevention_rate' in summary:
                    st.metric("Cognitive Offloading Prevention", f"{summary.get('cognitive_offloading_prevention_rate', 0):.1%}")
                if 'deep_thinking_encouragement_rate' in summary:
                    st.metric("Deep Thinking Engagement", f"{summary.get('deep_thinking_encouragement_rate', 0):.1%}")
                    
        except Exception as e:
            st.warning(f"Data export warning: {e}")
    else:
        st.info("No interaction data to export yet. Start a conversation to generate research data.")
    
    # Prepare enhanced data for download
    import json
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "session_metadata": {
            "session_id": st.session_state.get('session_id'),
            "participant_id": st.session_state.get('participant_id', 'unified_user'),
            "participant_name": st.session_state.get('participant_name', ''),
            "input_mode": st.session_state.get('input_mode', 'Text Only'),
            "mentor_type": st.session_state.get('mentor_type', 'Socratic Agent'),
            "mode": st.session_state.get('current_mode', 'MENTOR'),
            "session_start_time": str(st.session_state.get('session_start_time', '')),
            "has_uploaded_image": bool(st.session_state.get('uploaded_image_path'))
        },
        "messages": st.session_state.get('messages', []),
        "analysis_results": st.session_state.get('analysis_results'),
        "test_results": st.session_state.get('test_results', {}),
        "scientific_metrics": {
            "total_interactions": len(st.session_state.get('messages', [])) // 2,
            "mentor_type_used": st.session_state.get('mentor_type', 'Socratic Agent'),
            "input_mode_used": st.session_state.get('input_mode', 'Text Only'),
            "analysis_complete": st.session_state.get('analysis_complete', False)
        }
    }
    
    # Convert to JSON
    json_str = json.dumps(export_data, indent=2, default=str)
    
    # Create download button
    st.download_button(
        label="📥 Download Session Data",
        data=json_str,
        file_name=f"session_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def render_complete_sidebar(data_collector=None) -> str:
    """Render the complete sidebar with all components."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key status
        render_api_status()
        
        # Pre-test section (placed near top)
        render_pretest_section()
        
        # Participant info
        render_participant_info()
        
        # Session info
        render_session_info()
        
        # System status
        render_system_status()
        
        # Current session status
        render_current_session_status()
        
        # Session management
        render_session_management(data_collector)
        
    return "Main"  # Single-flow: no page selector 