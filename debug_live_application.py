#!/usr/bin/env python3
"""
DEBUG: Live Application Task System
Add this code to your application to debug why tasks aren't appearing
"""

import streamlit as st
from datetime import datetime

def debug_task_system():
    """Debug function to check task system status - ADD THIS TO YOUR SIDEBAR"""
    
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
    
    # Check 6: Phase Completion (if available)
    try:
        if hasattr(st.session_state, 'phase_session_id') and st.session_state.phase_session_id:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from phase_progression_system import PhaseProgressionSystem
            
            phase_system = PhaseProgressionSystem()
            session = phase_system.sessions.get(st.session_state.phase_session_id)
            if session and session.current_phase:
                current_progress = session.phase_progress.get(session.current_phase)
                if current_progress:
                    phase_completion_percent = current_progress.completion_percent
                    st.write(f"**Phase Completion**: {phase_completion_percent:.1f}%")
                else:
                    st.write(f"**Phase Completion**: No progress data")
            else:
                st.write(f"**Phase Completion**: No session found")
    except Exception as e:
        st.write(f"**Phase Completion**: Error - {e}")
    
    # Summary
    if task_system_ready:
        st.success("✅ Task system should be working!")
        if message_count == 0:
            st.info("💡 Start a conversation to trigger tasks at appropriate completion percentages")
    else:
        st.error("❌ Task system not ready - check the issues above")
        
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
            st.session_state.phase_session_id = f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.success("✅ MENTOR group and Test Mode force-enabled!")
        st.rerun()


# INSTRUCTIONS FOR USER:
# 1. Add this to your sidebar by importing this file and calling debug_task_system()
# 2. Or copy the debug_task_system() function into your sidebar_components.py
# 3. Add this line in your sidebar: debug_task_system()

def add_debug_to_sidebar():
    """
    COPY THIS CODE INTO YOUR dashboard/ui/sidebar_components.py file
    Add this call at the end of render_test_mode_primary() function:
    
    # DEBUG: Add task system debugging
    debug_task_system()
    """
    pass

if __name__ == "__main__":
    print("🔍 DEBUG SCRIPT FOR LIVE APPLICATION")
    print("=" * 50)
    print("INSTRUCTIONS:")
    print("1. Copy the debug_task_system() function above")
    print("2. Add it to your dashboard/ui/sidebar_components.py")
    print("3. Call debug_task_system() at the end of render_test_mode_primary()")
    print("4. Run your application and check the debug output in the sidebar")
    print("5. Use the 'Quick Fix' button if needed")
    print("=" * 50)
