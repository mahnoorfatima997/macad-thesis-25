"""
Sidebar components for the dashboard.
"""

import streamlit as st
import json
import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.config.settings import get_api_key
from dashboard.core.session_manager import get_session_info, reset_session
from dashboard.core.dropbox_integration import dropbox_exporter


def render_api_status():
    """Render API key status."""
    api_key = get_api_key()
    if api_key:
        st.success("API Key: Configured")
    else:
        st.error("API Key: Missing")
    return bool(api_key)


def render_dropbox_status():
    """Render Dropbox connection status."""
    status = dropbox_exporter.get_connection_status()

    if status["connected"]:
        st.success(f"☁️ Dropbox: Connected ({status.get('account_email', 'Unknown')})")
    elif status["dropbox_available"]:
        st.warning("☁️ Dropbox: Not connected")
        if status.get("error"):
            st.caption(f"Error: {status['error']}")
    else:
        st.error("☁️ Dropbox: Package not installed")

    return status["connected"]


def render_participant_info():
    """Render participant information section."""
    st.markdown("### Participant")
    
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
    st.markdown("### Session")
    
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
    st.markdown("### System Status")
    st.info("**Vision**: GPT Vision Available")
    st.info("**Agents**: Multi-Agent System Ready")

    # Routing metadata toggle
    st.checkbox("Show route/agents meta in replies", key="show_routing_meta")

def render_system_status_simplified():
    """Render simplified system status for test mode."""
    st.markdown("### System Status")
    st.info("**Research System**: Ready")

    # Routing metadata toggle (for research purposes)
    st.checkbox("Show routing metadata", key="show_routing_meta",
                help="Display technical routing information for research analysis")


def render_current_session_status():
    """Render current session status if analysis is complete."""
    if st.session_state.get('analysis_complete', False):
        st.markdown("### Current Session")
        current_mode = st.session_state.get('current_mode', 'MENTOR')
        
        if current_mode == "MENTOR":
            st.success(f"**Mode**: {current_mode}")
        elif current_mode == "GENERIC_AI":
            st.warning(f"**Mode**: {current_mode}")
        else:
            st.info(f"**Mode**: {current_mode}")


def render_session_management(data_collector=None):
    """Render session management section."""
    st.markdown("### Session Management")
    
    # Reset session button
    if st.button("Reset Session"):
        reset_session()
        st.success("Session reset successfully!")
        st.rerun()
    
    # Reset data collector button
    if data_collector and st.button("Reset Data Collector"):
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../thesis-agents'))
        from data_collection.interaction_logger import InteractionLogger
        st.session_state.data_collector = InteractionLogger(session_id="unified_dashboard_session")
        st.success("Data collector reset!")
        st.rerun()
    
    # Export data button - ONLY in Test Mode
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')
    if dashboard_mode == "Test Mode":
        if st.button("💾 Export Data"):
            export_session_data(data_collector)
    else:
        st.info("📊 Export functionality is only available in Test Mode for research data collection.")


def render_mode_selection():
    """Render mode selection - Test Mode vs Flexible Mode."""

    st.markdown("### Dashboard Mode")

    mode_options = {
        "Test Mode": "🔬 Research testing with fixed community center challenge",
        "Flexible Mode": "⚙️ Original mentor.py with templates and flexible options"
    }

    selected_mode = st.selectbox(
        "Select Mode:",
        list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        help="Choose between research test mode or flexible mentor mode"
    )

    # Update session state
    st.session_state.dashboard_mode = selected_mode

    return selected_mode

def render_test_mode_primary():
    """Render test mode as the primary interface."""

    # Test group selection (replaces mentor type)
    st.markdown("### Test Group Assignment")

    test_group_options = {
        "MENTOR": "Mentor - Multi-agent scaffolding system",
        "GENERIC_AI": "Generic AI - Direct AI assistance",
        "CONTROL": "No AI - Self-directed design work"
    }

    selected_test_group = st.selectbox(
        "Test Condition:",
        list(test_group_options.keys()),
        format_func=lambda x: test_group_options[x],
        help="Select the experimental condition for this session"
    )

    # Map test group to mentor type for compatibility
    mentor_type_mapping = {
        "MENTOR": "Socratic Agent",
        "GENERIC_AI": "Raw GPT",
        "CONTROL": "No AI"
    }

    # Update session state
    st.session_state.test_group_selection = selected_test_group
    st.session_state.mentor_type = mentor_type_mapping[selected_test_group]
    st.session_state.current_mode = mentor_type_mapping[selected_test_group]

    # CRITICAL: Also set test_group for task system compatibility
    from thesis_tests.data_models import TestGroup
    test_group_enum_mapping = {
        "MENTOR": TestGroup.MENTOR,
        "GENERIC_AI": TestGroup.GENERIC_AI,
        "CONTROL": TestGroup.CONTROL
    }
    st.session_state.test_group = test_group_enum_mapping[selected_test_group]

    # Test session status
    if st.session_state.get('test_session_active', False):
        participant_id = st.session_state.get('participant_id', 'unified_user')
        st.success(f"**Active Test Session**")
        st.write(f"Participant: {participant_id}")
        st.write(f"Condition: {test_group_options[selected_test_group]}")

        # Phase information
        current_phase = st.session_state.get('test_current_phase', 'Ideation')
        st.write(f"Phase: {current_phase}")

        # REMOVED: Duplicate phase control buttons
        # Phase progression is handled automatically by the phase progression system
        # Manual phase controls would interfere with research validity
    else:
        # Start test session
        if st.button("Start Test Session", type="primary"):
            initialize_test_session()

    # DEBUG: Task System Status
    #debug_task_system_status()

    return selected_test_group

def render_flexible_mode_options():
    """Render flexible mode options (original mentor.py functionality)."""

    st.markdown("### Flexible Mode Options")

    # Import here to avoid circular imports
    from dashboard.config.settings import MENTOR_TYPES

    # Original mentor type selection
    mentor_type = st.selectbox(
        "Mentor Type:",
        MENTOR_TYPES,
        index=0,
        help="Mentor: Multi-agent system that challenges and guides thinking\n"
             "Generic AI: Direct GPT responses for comparison\n"
             "No AI: Hardcoded questions only, no AI assistance (control group)"
    )

    # Update session state
    st.session_state.mentor_type = mentor_type
    st.session_state.current_mode = mentor_type

    return mentor_type

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
    """Export session data functionality with enhanced research metrics - ONLY in Test Mode."""

    # MODE RESTRICTION: Only allow export in Test Mode
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')
    if dashboard_mode != "Test Mode":
        st.error("🚫 Export functionality is only available in Test Mode for research data collection.")
        return

    if not st.session_state.get('messages', []):
        st.warning("No data to export")
        return
    
    # Export comprehensive data using InteractionLogger with Dropbox integration
    if data_collector and hasattr(data_collector, 'interactions') and len(data_collector.interactions) > 0:
        try:
            # Export to local and Dropbox
            export_results = dropbox_exporter.export_comprehensive_data(data_collector)

            if export_results["success"]:
                st.success("✅ Session data exported to local thesis_data/ and Dropbox!")

                # Show local files
                if export_results["local_files"]:
                    st.info("📁 **Local files created:**")
                    for file_path in export_results["local_files"]:
                        st.write(f"  • {file_path}")

                # Show Dropbox files
                if export_results["dropbox_files"]:
                    st.info("☁️ **Dropbox files uploaded:**")
                    for dropbox_path in export_results["dropbox_files"]:
                        st.write(f"  • {dropbox_path}")

                # Show any errors
                if export_results["errors"]:
                    st.warning("⚠️ **Some issues occurred:**")
                    for error in export_results["errors"]:
                        st.write(f"  • {error}")
            else:
                st.error("❌ Export failed")
                if export_results["errors"]:
                    for error in export_results["errors"]:
                        st.write(f"  • {error}")

            # Show key research metrics
            summary = data_collector.get_session_summary() if hasattr(data_collector, 'get_session_summary') else None
            if summary:
                st.metric("Total Interactions", len(data_collector.interactions))
                if 'cognitive_offloading_prevention_rate' in summary:
                    st.metric("Cognitive Offloading Prevention", f"{summary.get('cognitive_offloading_prevention_rate', 0):.1%}")
                if 'deep_thinking_encouragement_rate' in summary:
                    st.metric("Deep Thinking Engagement", f"{summary.get('deep_thinking_encouragement_rate', 0):.1%}")

        except Exception as e:
            st.error(f"❌ Export failed: {e}")
            # Fallback to local export only
            try:
                summary = data_collector.export_for_thesis_analysis()
                st.warning("⚠️ Exported to local only (Dropbox failed)")
            except Exception as e2:
                st.error(f"❌ Local export also failed: {e2}")
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

    # Also export to Dropbox
    try:
        session_id = st.session_state.get('session_id', 'unknown')
        dropbox_result = dropbox_exporter.export_session_data(export_data, session_id)

        if dropbox_result["success"]:
            st.success(f"☁️ Also saved to Dropbox: {dropbox_result['dropbox_path']}")
        else:
            st.warning("⚠️ Dropbox upload failed (local download still available)")
    except Exception as e:
        st.warning(f"⚠️ Dropbox upload failed: {e}")


def render_complete_sidebar(data_collector=None) -> str:
    """Render the complete sidebar with mode selection."""
    with st.sidebar:
        # Mode selection first
        selected_mode = render_mode_selection()

        st.markdown("---")

        # Render appropriate mode interface
        if selected_mode == "Test Mode":
            render_test_mode_primary()
        else:  # Flexible Mode
            render_flexible_mode_options()

        st.markdown("---")
        st.subheader("⚙️ System Configuration")

        # Pre-test section (available in both modes)
        render_pretest_section()

        # API Key status
        render_api_status()

        # Dropbox status
        render_dropbox_status()

        # Participant info
        render_participant_info()

        # Session info
        render_session_info()

        # System status (simplified)
        render_system_status_simplified()

        # Session management
        render_session_management(data_collector)

        # Dynamic task status (if in test mode)
        dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')
        if dashboard_mode == "Test Mode" and data_collector:
            try:
                # Get mode processor from session state if available
                mode_processor = st.session_state.get('mode_processor')
                if mode_processor and hasattr(mode_processor, 'render_active_tasks_ui'):
                    print(f"🔍 SIDEBAR_DEBUG: About to render task UI from sidebar")
                    # Ensure task system is initialized before rendering
                    mode_processor._ensure_task_system_initialized()
                    print(f"🔍 SIDEBAR_DEBUG: Task system initialized: {mode_processor.task_manager is not None}")
                    mode_processor.render_active_tasks_ui()
                else:
                    print(f"🔍 SIDEBAR_DEBUG: Mode processor not available or missing render method")
            except Exception as e:
                print(f"⚠️ Error rendering task UI: {e}")
                import traceback
                traceback.print_exc()

    return "Main"  # Single-flow: no page selector


def initialize_test_session():
    """Initialize a new test session."""
    try:
        # Set test session as active
        st.session_state.test_session_active = True
        st.session_state.test_current_phase = "Ideation"
        st.session_state.test_session_start = datetime.now()

        # Clear previous messages to start fresh
        st.session_state.messages = []

        # Initialize phase system for test mode
        if 'phase_session_id' not in st.session_state:
            st.session_state.phase_session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        st.success("✅ Test session initialized!")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Failed to initialize test session: {e}")


def debug_task_system_status():
    """Debug function to check task system status in the sidebar"""

    st.markdown("---")
    st.markdown("### 🔍 DEBUG: Task System Status")

    # Check 1: Dashboard Mode
    dashboard_mode = st.session_state.get('dashboard_mode', 'NOT_SET')
    test_mode_active = (dashboard_mode == "Test Mode")

    st.write(f"**Dashboard Mode**: {dashboard_mode}")
    st.write(f"**Test Mode Active**: {'✅' if test_mode_active else '❌'}")

    # Check 2: Test Group Settings
    test_group = st.session_state.get('test_group', 'NOT_SET')
    test_group_selection = st.session_state.get('test_group_selection', 'NOT_SET')
    mentor_type = st.session_state.get('mentor_type', 'NOT_SET')
    current_mode = st.session_state.get('current_mode', 'NOT_SET')

    st.write(f"**test_group**: {test_group}")
    st.write(f"**test_group_selection**: {test_group_selection}")
    st.write(f"**mentor_type**: {mentor_type}")
    st.write(f"**current_mode**: {current_mode}")

    # Check 3: Test Session Status
    test_session_active = st.session_state.get('test_session_active', False)
    test_current_phase = st.session_state.get('test_current_phase', 'NOT_SET')
    phase_session_id = st.session_state.get('phase_session_id', 'NOT_SET')

    st.write(f"**test_session_active**: {'✅' if test_session_active else '❌'}")
    st.write(f"**test_current_phase**: {test_current_phase}")
    st.write(f"**phase_session_id**: {phase_session_id}")

    # Check 4: Messages and Interaction Count
    messages = st.session_state.get('messages', [])
    message_count = len(messages)

    st.write(f"**Message Count**: {message_count}")

    # Check 5: Task System Readiness
    task_system_ready = (
        test_mode_active and
        test_group != 'NOT_SET' and
        test_group is not None and
        test_session_active
    )

    st.write(f"**Task System Ready**: {'✅' if task_system_ready else '❌'}")

    # Summary
    if task_system_ready:
        st.success("✅ Task system should be working!")
        if message_count == 0:
            st.info("💡 Start a conversation to trigger tasks")
    else:
        st.error("❌ Task system not ready")

        # Specific recommendations
        if not test_mode_active:
            st.warning("🔧 Set Dashboard Mode to 'Test Mode'")
        if test_group == 'NOT_SET' or test_group is None:
            st.warning("🔧 Select a test group (MENTOR/GENERIC_AI/CONTROL)")
        if not test_session_active:
            st.warning("🔧 Click 'Start Test Session' button")

    # Quick Fix Button
    if st.button("🔧 Quick Fix: Force Set MENTOR Group"):
        from thesis_tests.data_models import TestGroup
        st.session_state.dashboard_mode = 'Test Mode'
        st.session_state.test_group_selection = 'MENTOR'
        st.session_state.mentor_type = 'Socratic Agent'
        st.session_state.current_mode = 'Socratic Agent'
        st.session_state.test_group = TestGroup.MENTOR
        st.session_state.test_session_active = True
        st.session_state.test_current_phase = 'Ideation'
        if 'phase_session_id' not in st.session_state:
            from datetime import datetime
            st.session_state.phase_session_id = f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.success("✅ MENTOR group and Test Mode force-enabled!")
        st.rerun()


# REMOVED: Manual phase control functions
# Phase progression is handled automatically by the phase progression system
# Manual phase controls would interfere with research validity and data collection