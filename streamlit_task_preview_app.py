#!/usr/bin/env python3
"""
STREAMLIT APP: Task UI Preview
Shows exactly how tasks appear in the actual Streamlit interface
Run with: streamlit run streamlit_task_preview_app.py
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

from dashboard.processors.dynamic_task_manager import DynamicTaskManager, TaskType, ActiveTask
from dashboard.processors.task_guidance_system import TaskGuidanceSystem
from dashboard.ui.task_ui_renderer import TaskUIRenderer

# Page configuration
st.set_page_config(
    page_title="Task UI Preview",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state for task preview"""
    if 'dashboard_mode' not in st.session_state:
        st.session_state.dashboard_mode = 'Test Mode'
    if 'test_group' not in st.session_state:
        st.session_state.test_group = 'MENTOR'
    if 'test_current_phase' not in st.session_state:
        st.session_state.test_current_phase = 'Ideation'
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = 'preview_session_123'

def create_mock_task(task_type: TaskType, test_group: str) -> ActiveTask:
    """Create a mock active task for preview"""
    phase_mapping = {
        'architectural_concept': 'ideation',
        'spatial_program': 'ideation', 
        'visual_conceptualization': 'visualization',
        'visual_analysis_2d': 'visualization',
        'environmental_contextual': 'visualization',
        'spatial_analysis_3d': 'materialization',
        'realization_implementation': 'materialization',
        'design_evolution': 'reflection',
        'knowledge_transfer': 'reflection'
    }
    
    current_phase = phase_mapping.get(task_type.value, 'ideation')
    
    return ActiveTask(
        task_type=task_type,
        start_time=datetime.now(),
        test_group=test_group,
        current_phase=current_phase,
        trigger_reason="UI Preview",
        completion_criteria=[],
        task_specific_data={},
        trigger_phase_completion=25.0
    )

def render_task_preview(task_type: TaskType, test_group: str):
    """Render a task preview in the actual Streamlit UI"""
    
    # Initialize systems
    guidance_system = TaskGuidanceSystem()
    ui_renderer = TaskUIRenderer()
    
    # Create mock task
    task = create_mock_task(task_type, test_group)
    
    # Get task content
    if test_group == "MENTOR":
        task_data = guidance_system.mentor_tasks.get(task_type, {})
    elif test_group == "GENERIC_AI":
        task_data = guidance_system.generic_ai_tasks.get(task_type, {})
    elif test_group == "CONTROL":
        task_data = guidance_system.control_tasks.get(task_type, {})
    else:
        task_data = {}
    
    if not task_data:
        st.error(f"❌ No task data found for {task_type.value} in {test_group} mode")
        return
    
    task_content = task_data.get("task_assignment", f"🎯 TASK {task_type.value}: Complete the design challenge")
    guidance_type = "socratic" if test_group == "MENTOR" else "direct" if test_group == "GENERIC_AI" else "minimal"
    
    # Render the actual UI component
    try:
        ui_renderer.render_task_component(task, task_content, guidance_type)
        
        # Show additional details in an expander
        with st.expander("📋 Task Details", expanded=False):
            st.write(f"**Task Type:** {task_type.value}")
            st.write(f"**Test Group:** {test_group}")
            st.write(f"**Guidance Type:** {guidance_type}")
            st.write(f"**Phase:** {task.current_phase}")
            st.write(f"**Content Length:** {len(task_content)} characters")
            
            # Show mode-specific content
            if test_group == "MENTOR":
                socratic_questions = task_data.get("socratic_questions", [])
                if socratic_questions:
                    st.write(f"**Socratic Questions:** {len(socratic_questions)} questions")
                    for i, question in enumerate(socratic_questions, 1):
                        st.write(f"{i}. {question}")
            
            elif test_group == "GENERIC_AI":
                direct_info = task_data.get("direct_information", [])
                if direct_info:
                    st.write(f"**Direct Information:** {len(direct_info)} points")
                    for i, info in enumerate(direct_info, 1):
                        st.write(f"{i}. {info}")
            
            elif test_group == "CONTROL":
                minimal_prompt = task_data.get("minimal_prompt", "")
                if minimal_prompt:
                    st.write(f"**Minimal Prompt:** {minimal_prompt}")
        
    except Exception as e:
        st.error(f"❌ Failed to render task: {e}")
        st.exception(e)

def main():
    """Main Streamlit app"""
    
    # Initialize session state
    initialize_session_state()
    
    # App header
    st.title("🎯 Task UI Preview")
    st.markdown("**See exactly how tasks appear in the actual Streamlit interface**")
    
    # Sidebar controls
    st.sidebar.header("🎮 Task Selection")
    
    # Test group selection
    test_group = st.sidebar.selectbox(
        "Select Test Group:",
        ["MENTOR", "GENERIC_AI", "CONTROL"],
        help="Choose which test group's tasks to preview"
    )
    
    # Task type selection
    all_tasks = list(TaskType)
    task_names = [task.value.replace('_', ' ').title() for task in all_tasks]
    
    selected_task_name = st.sidebar.selectbox(
        "Select Task:",
        task_names,
        help="Choose which task to preview"
    )
    
    # Convert back to TaskType
    selected_task = all_tasks[task_names.index(selected_task_name)]
    
    # Preview mode selection
    preview_mode = st.sidebar.radio(
        "Preview Mode:",
        ["Single Task", "All Tasks for Group", "Compare Across Groups"],
        help="Choose how to display the tasks"
    )
    
    # Main content area
    if preview_mode == "Single Task":
        st.header(f"🎯 {selected_task_name} - {test_group} Mode")
        render_task_preview(selected_task, test_group)
        
    elif preview_mode == "All Tasks for Group":
        st.header(f"🎯 All Tasks - {test_group} Mode")
        
        for task_type in all_tasks:
            task_name = task_type.value.replace('_', ' ').title()
            st.subheader(f"📋 {task_name}")
            render_task_preview(task_type, test_group)
            st.markdown("---")
            
    elif preview_mode == "Compare Across Groups":
        st.header(f"🎯 {selected_task_name} - All Groups Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🟣 MENTOR")
            render_task_preview(selected_task, "MENTOR")
            
        with col2:
            st.subheader("🔵 GENERIC_AI")
            render_task_preview(selected_task, "GENERIC_AI")
            
        with col3:
            st.subheader("🟤 CONTROL")
            render_task_preview(selected_task, "CONTROL")
    
    # Footer information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Status")
    st.sidebar.success("✅ Task UI Renderer: Active")
    st.sidebar.success("✅ Task Guidance System: Active")
    st.sidebar.success("✅ Dynamic Task Manager: Active")
    
    st.sidebar.markdown("### 🎨 Theme Information")
    st.sidebar.markdown("- **MENTOR**: 🟣 Purple gradient + ◈ Diamond")
    st.sidebar.markdown("- **GENERIC_AI**: 🔵 Blue gradient + ◉ Circle")
    st.sidebar.markdown("- **CONTROL**: 🟤 Brown gradient + ◐ Half-circle")
    
    # Debug information
    with st.expander("🔧 Debug Information", expanded=False):
        st.write("**Session State:**")
        st.json({
            "dashboard_mode": st.session_state.dashboard_mode,
            "test_group": test_group,
            "selected_task": selected_task.value,
            "preview_mode": preview_mode
        })

if __name__ == "__main__":
    main()
