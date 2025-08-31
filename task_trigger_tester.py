#!/usr/bin/env python3
"""
Working Task Trigger Test App - No OpenAI API Required
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add dashboard to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

try:
    from processors.mode_processors import ModeProcessor, TestGroup
    from processors.dynamic_task_manager import TaskType
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

def main():
    st.set_page_config(
        page_title="Task Trigger Tester",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Task Trigger Testing App")
    st.markdown("**Test all 8 tasks across 3 phases - No OpenAI API required**")
    
    if not IMPORTS_OK:
        st.error(f"❌ Import Error: {IMPORT_ERROR}")
        st.info("Make sure you're running this from the project root directory")
        return
    
    # Initialize session state
    if 'initialized' not in st.session_state:
        initialize_app()
    
    # Sidebar controls
    render_sidebar()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_main_interface()
    
    with col2:
        render_task_status()

def initialize_app():
    """Initialize the app"""
    st.session_state.initialized = True
    st.session_state.current_phase = 'ideation'
    st.session_state.completion = 0.0
    st.session_state.test_results = []
    st.session_state.task_manager = None
    
    try:
        # Initialize task system
        st.session_state.dashboard_mode = 'Test Mode'
        st.session_state.test_group = TestGroup.MENTOR
        
        mode_processor = ModeProcessor()
        mode_processor._ensure_task_system_initialized()
        
        st.session_state.mode_processor = mode_processor
        st.session_state.task_manager = mode_processor.task_manager
        
        st.success("✅ Task system initialized successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        st.session_state.mode_processor = None
        st.session_state.task_manager = None

def render_sidebar():
    """Render sidebar controls"""
    st.sidebar.header("🎯 Test Controls")
    
    # Phase selection
    phase = st.sidebar.selectbox(
        "Phase:",
        ['ideation', 'visualization', 'materialization'],
        index=['ideation', 'visualization', 'materialization'].index(st.session_state.current_phase)
    )
    
    # Completion slider
    completion = st.sidebar.slider(
        "Completion %:",
        0.0, 100.0, st.session_state.completion, 5.0
    )
    
    # Update session state
    st.session_state.current_phase = phase
    st.session_state.completion = completion
    
    st.sidebar.markdown("---")
    
    # Quick test buttons
    st.sidebar.subheader("🚀 Quick Tests")
    
    if st.sidebar.button("Test Task 2.1 (Main Issue)", type="primary"):
        test_specific_task('visualization', 0.0, 'Task 2.1 - Visual Analysis 2D')
    
    if st.sidebar.button("Test All Ideation Tasks"):
        test_phase_tasks('ideation')
    
    if st.sidebar.button("Test All Visualization Tasks"):
        test_phase_tasks('visualization')
    
    if st.sidebar.button("Test All Materialization Tasks"):
        test_phase_tasks('materialization')
    
    if st.sidebar.button("🔄 Reset System"):
        reset_system()

def render_main_interface():
    """Render main testing interface"""
    st.subheader(f"🔍 Current Test: {st.session_state.current_phase.title()} at {st.session_state.completion}%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Test Current Settings", type="primary"):
            test_current_settings()
    
    with col2:
        if st.button("🔄 Test Phase Transition"):
            test_phase_transition()
    
    # Display expected tasks
    st.subheader("📋 Expected Tasks for Current Settings")
    expected = get_expected_tasks(st.session_state.current_phase, st.session_state.completion)
    
    if expected:
        for task_id, description in expected:
            st.write(f"• **{description}** (`{task_id}`)")
    else:
        st.info("No tasks expected at this threshold")
    
    # Test results
    if st.session_state.test_results:
        st.subheader("📊 Recent Test Results")
        
        for i, result in enumerate(reversed(st.session_state.test_results[-5:])):
            with st.expander(f"Test {len(st.session_state.test_results)-i}: {result['description']}"):
                st.write(f"**Phase:** {result['phase']}")
                st.write(f"**Completion:** {result['completion']}%")
                st.write(f"**Expected:** {result['expected']}")
                st.write(f"**Triggered:** {result['triggered']}")
                st.write(f"**Status:** {'✅ PASS' if result['success'] else '❌ FAIL'}")
                st.write(f"**Time:** {result['timestamp']}")

def render_task_status():
    """Render current task manager status"""
    st.subheader("📊 Task Manager Status")
    
    if not st.session_state.task_manager:
        st.error("❌ Task manager not available")
        return
    
    try:
        task_manager = st.session_state.task_manager
        
        # Active tasks
        active_tasks = list(task_manager.active_tasks.keys())
        st.metric("Active Tasks", len(active_tasks))
        
        if active_tasks:
            st.write("**Active:**")
            for task in active_tasks:
                st.write(f"• {task}")
        
        # Completed tasks
        completed_tasks = [t.task_type.value for t in task_manager.task_history]
        st.metric("Completed Tasks", len(completed_tasks))
        
        if completed_tasks:
            st.write("**Completed:**")
            for task in completed_tasks[-3:]:  # Show last 3
                st.write(f"• {task}")
        
        # Instance info
        st.write(f"**Instance ID:** {hex(id(task_manager))}")
        
    except Exception as e:
        st.error(f"❌ Error displaying status: {str(e)}")

def test_current_settings():
    """Test task triggers with current settings"""
    phase = st.session_state.current_phase
    completion = st.session_state.completion
    
    test_specific_task(phase, completion, f"{phase.title()} at {completion}%")

def test_specific_task(phase, completion, description):
    """Test specific task trigger"""
    if not st.session_state.task_manager:
        st.error("❌ Task manager not available")
        return
    
    try:
        with st.spinner(f"Testing {description}..."):
            triggered_task = st.session_state.task_manager.check_task_triggers(
                user_input=f"Testing {phase} at {completion}%",
                conversation_history=[
                    {"role": "user", "content": f"Working on {phase}"},
                    {"role": "assistant", "content": "Great progress!"}
                ],
                current_phase=phase,
                test_group="MENTOR",
                image_uploaded=False,
                phase_completion_percent=completion
            )
        
        # Process results
        if triggered_task:
            if isinstance(triggered_task, list):
                triggered_names = [t.value for t in triggered_task]
            else:
                triggered_names = [triggered_task.value]
        else:
            triggered_names = []
        
        # Get expected tasks
        expected = [task_id for task_id, _ in get_expected_tasks(phase, completion)]
        
        # Check success
        success = set(triggered_names) == set(expected)
        
        # Display results
        if success:
            st.success(f"✅ SUCCESS: {description}")
            st.write(f"Triggered: {triggered_names}")
        else:
            st.error(f"❌ FAILED: {description}")
            st.write(f"Expected: {expected}")
            st.write(f"Triggered: {triggered_names}")
        
        # Save result
        st.session_state.test_results.append({
            'phase': phase,
            'completion': completion,
            'expected': expected,
            'triggered': triggered_names,
            'success': success,
            'description': description,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        st.error(f"❌ Error testing {description}: {str(e)}")

def test_phase_tasks(phase):
    """Test all tasks for a specific phase"""
    phase_tests = {
        'ideation': [(5.0, 'Task 1.1'), (35.0, 'Task 1.2')],
        'visualization': [(0.0, 'Task 2.1'), (45.0, 'Task 2.2')],
        'materialization': [(0.0, 'Task 3.1'), (45.0, 'Task 3.2'), (55.0, 'Task 4.1'), (65.0, 'Task 4.2')]
    }
    
    tests = phase_tests.get(phase, [])
    
    for completion, task_name in tests:
        test_specific_task(phase, completion, f"{task_name} ({phase} {completion}%)")

def test_phase_transition():
    """Test phase transition task triggering"""
    if not hasattr(st.session_state.mode_processor, '_handle_phase_transition'):
        st.error("❌ Phase transition method not available")
        return
    
    try:
        with st.spinner("Testing phase transition..."):
            # Test ideation → visualization transition
            st.session_state.mode_processor._handle_phase_transition(
                from_phase="ideation",
                to_phase="visualization",
                test_group=TestGroup.MENTOR,
                user_input="Testing phase transition"
            )
        
        st.success("✅ Phase transition test completed")
        st.info("Check task status to see if Task 2.1 was activated")
        
    except Exception as e:
        st.error(f"❌ Phase transition test failed: {str(e)}")

def get_expected_tasks(phase, completion):
    """Get expected tasks for phase and completion"""
    task_map = {
        'ideation': [
            (5.0, 'architectural_concept', 'Task 1.1: Architectural Concept'),
            (35.0, 'spatial_program', 'Task 1.2: Spatial Program')
        ],
        'visualization': [
            (0.0, 'visual_analysis_2d', 'Task 2.1: Visual Analysis 2D ⭐'),
            (45.0, 'environmental_contextual', 'Task 2.2: Environmental Contextual')
        ],
        'materialization': [
            (0.0, 'spatial_analysis_3d', 'Task 3.1: Spatial Analysis 3D'),
            (45.0, 'realization_implementation', 'Task 3.2: Realization Implementation'),
            (55.0, 'design_evolution', 'Task 4.1: Design Evolution'),
            (65.0, 'knowledge_transfer', 'Task 4.2: Knowledge Transfer')
        ]
    }
    
    expected = []
    for trigger_completion, task_id, description in task_map.get(phase, []):
        if completion >= trigger_completion:
            # Check if this is the exact trigger point
            if completion == trigger_completion:
                expected.append((task_id, description))
    
    return expected

def reset_system():
    """Reset the task system"""
    try:
        # Clear session state
        for key in ['mode_processor', 'task_manager', 'test_results']:
            if key in st.session_state:
                del st.session_state[key]
        
        # Reinitialize
        initialize_app()
        st.success("✅ System reset successfully!")
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"❌ Reset failed: {str(e)}")

if __name__ == "__main__":
    main()
