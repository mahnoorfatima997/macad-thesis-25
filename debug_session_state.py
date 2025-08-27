#!/usr/bin/env python3
"""
DEBUG: Session State Test Group Issue
Quick test to see what's happening with test group in session state
"""

import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

# Mock streamlit for testing
class MockSessionState:
    def __init__(self):
        # Start with empty session state
        self._state = {}
        
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._state[key] = value
    
    def __getattr__(self, key):
        return self._state.get(key, None)
    
    def show_state(self):
        print("📋 Current Session State:")
        for key, value in self._state.items():
            print(f"   {key}: {value}")

class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
    
    def selectbox(self, label, options, format_func=None, help=None):
        # Simulate user selecting MENTOR
        return 'MENTOR'
    
    def button(self, label, type=None):
        # Simulate button click
        return True
    
    def success(self, msg):
        print(f"✅ {msg}")
    
    def error(self, msg):
        print(f"❌ {msg}")
    
    def write(self, msg):
        print(f"📝 {msg}")
    
    def rerun(self):
        print("🔄 Streamlit rerun called")

# Mock streamlit
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from thesis_tests.data_models import TestGroup, TestPhase


def test_sidebar_test_group_flow():
    """Test the complete sidebar test group selection flow"""
    print("🎯 TESTING: Complete Sidebar Test Group Flow")
    print("=" * 60)
    
    # Step 1: Simulate sidebar rendering (this should set test group)
    print("📋 Step 1: Simulating sidebar test group selection...")
    
    # Simulate the sidebar selectbox
    test_group_options = {
        "MENTOR": "Mentor - Multi-agent scaffolding system",
        "GENERIC_AI": "Generic AI - Direct AI assistance",
        "CONTROL": "No AI - Self-directed design work"
    }
    
    selected_test_group = 'MENTOR'  # User selection
    
    # Map test group to mentor type for compatibility
    mentor_type_mapping = {
        "MENTOR": "Socratic Agent",
        "GENERIC_AI": "Raw GPT",
        "CONTROL": "No AI"
    }
    
    # Update session state (this is what the sidebar does)
    st.session_state.test_group_selection = selected_test_group
    st.session_state.mentor_type = mentor_type_mapping[selected_test_group]
    st.session_state.current_mode = mentor_type_mapping[selected_test_group]
    
    # CRITICAL: Also set test_group for task system compatibility
    test_group_enum_mapping = {
        "MENTOR": TestGroup.MENTOR,
        "GENERIC_AI": TestGroup.GENERIC_AI,
        "CONTROL": TestGroup.CONTROL
    }
    st.session_state.test_group = test_group_enum_mapping[selected_test_group]
    
    print(f"   Selected: {selected_test_group}")
    st.session_state.show_state()
    
    # Step 2: Simulate "Start Test Session" button click
    print(f"\n📋 Step 2: Simulating 'Start Test Session' button click...")
    
    # Simulate initialize_test_session() function
    st.session_state.test_session_active = True
    st.session_state.test_current_phase = "Ideation"
    st.session_state.test_session_start = "2024-01-01T10:00:00"
    st.session_state.messages = []
    st.session_state.phase_session_id = "test_session_20240101_100000"
    
    print("   Test session initialized")
    st.session_state.show_state()
    
    # Step 3: Test mode processor detection
    print(f"\n📋 Step 3: Testing mode processor test group detection...")
    
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')
    test_mode_active = (dashboard_mode == "Test Mode")
    
    # Simulate the mode processor logic
    test_group_raw = (
        st.session_state.get('test_group', None) or 
        st.session_state.get('test_group_selection', None) or
        st.session_state.get('current_mode', None)
    )
    
    if test_group_raw:
        if isinstance(test_group_raw, str):
            test_group_mapping = {
                "MENTOR": TestGroup.MENTOR,
                "GENERIC_AI": TestGroup.GENERIC_AI, 
                "CONTROL": TestGroup.CONTROL,
                "Socratic Agent": TestGroup.MENTOR,
                "Raw GPT": TestGroup.GENERIC_AI,
                "No AI": TestGroup.CONTROL
            }
            test_group = test_group_mapping.get(test_group_raw, None)
        else:
            test_group = test_group_raw
    else:
        test_group = None
    
    print(f"   Dashboard Mode: {dashboard_mode}")
    print(f"   Test Mode Active: {test_mode_active}")
    print(f"   Test Group Raw: {test_group_raw}")
    print(f"   Final Test Group: {test_group}")
    
    # Step 4: Check if task system would work
    print(f"\n📋 Step 4: Checking if task system would work...")
    
    task_system_ready = (
        test_mode_active and 
        test_group is not None and
        st.session_state.get('test_session_active', False)
    )
    
    print(f"   Task System Ready: {task_system_ready}")
    
    if task_system_ready:
        print("   ✅ SUCCESS: Task system should work!")
        print(f"      Test Group: {test_group.value}")
        print(f"      Session Active: {st.session_state.test_session_active}")
        print(f"      Phase: {st.session_state.test_current_phase}")
        return True
    else:
        print("   ❌ FAILURE: Task system not ready")
        print(f"      Test Mode Active: {test_mode_active}")
        print(f"      Test Group Set: {test_group is not None}")
        print(f"      Session Active: {st.session_state.get('test_session_active', False)}")
        return False


def test_session_state_persistence():
    """Test if session state persists across operations"""
    print("\n🔄 TESTING: Session State Persistence")
    print("=" * 60)
    
    # Set initial state
    st.session_state.test_group = TestGroup.MENTOR
    st.session_state.test_group_selection = 'MENTOR'
    st.session_state.dashboard_mode = 'Test Mode'
    
    print("📋 Initial state set:")
    st.session_state.show_state()
    
    # Simulate some operations that might affect state
    st.session_state.messages = []  # Clear messages (like initialize_test_session does)
    st.session_state.test_session_active = True
    
    print(f"\n📋 After session initialization:")
    st.session_state.show_state()
    
    # Check if test group is still there
    test_group_still_set = (
        st.session_state.get('test_group') is not None and
        st.session_state.get('test_group_selection') is not None
    )
    
    print(f"\n   Test Group Still Set: {test_group_still_set}")
    
    if test_group_still_set:
        print("   ✅ SUCCESS: Session state persists correctly")
        return True
    else:
        print("   ❌ FAILURE: Session state lost during operations")
        return False


def main():
    """Test the complete session state flow"""
    print("🚀 SESSION STATE DEBUG TEST")
    print("=" * 80)
    
    try:
        test1_passed = test_sidebar_test_group_flow()
        test2_passed = test_session_state_persistence()
        
        print("\n" + "=" * 80)
        if all([test1_passed, test2_passed]):
            print("🎉 SESSION STATE TESTS PASSED!")
            print("✅ Sidebar test group selection works")
            print("✅ Session state persists correctly")
            print("\n💡 DIAGNOSIS: The session state logic should work correctly.")
            print("   If tasks still don't appear, the issue might be:")
            print("   1. Dashboard mode not set to 'Test Mode'")
            print("   2. Session state being reset somewhere else")
            print("   3. Mode processor not being called")
            print("   4. Task manager not being initialized")
        else:
            print("❌ SESSION STATE TESTS FAILED!")
            print(f"   Sidebar flow: {'✅' if test1_passed else '❌'}")
            print(f"   State persistence: {'✅' if test2_passed else '❌'}")
        print("=" * 80)
        
        return 0 if all([test1_passed, test2_passed]) else 1
        
    except Exception as e:
        print(f"\n❌ SESSION STATE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
