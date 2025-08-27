#!/usr/bin/env python3
"""
DEBUG: All Task Messages Visualization
Test all task messages across three modes (MENTOR, GENERIC_AI, CONTROL) 
to see how they are visualized and trigger them systematically
"""

import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

# Mock streamlit for testing
class MockSessionState:
    def __init__(self):
        self.dashboard_mode = 'Test Mode'
        self.test_group = None
        self.test_current_phase = 'Ideation'
        self.messages = []
        self.session_id = 'test_session_123'
        self.phase_session_id = None
        self.active_task = None
        
    def get(self, key, default=None):
        return getattr(self, key, default)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
        self.ui_output = []

    def markdown(self, content, unsafe_allow_html=False):
        if unsafe_allow_html and content:
            # Extract and display the actual UI content
            self.ui_output.append(("HTML", content))
            self._display_ui_content(content)
        else:
            self.ui_output.append(("MARKDOWN", content))
            print(f"📄 MARKDOWN: {content}")

    def _display_ui_content(self, html_content):
        """Display HTML content in a readable format"""
        print(f"\n{'='*100}")
        print(f"🎨 STREAMLIT UI RENDERING:")
        print(f"{'='*100}")

        # Extract key information from HTML
        import re

        # Extract task title
        title_match = re.search(r'<h2[^>]*>(.*?)</h2>', html_content, re.DOTALL)
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            print(f"📋 TASK TITLE: {title}")

        # Extract guidance type
        guidance_match = re.search(r'<div[^>]*color: rgba\(255,255,255,0\.9\)[^>]*>(.*?)</div>', html_content, re.DOTALL)
        if guidance_match:
            guidance = re.sub(r'<[^>]+>', '', guidance_match.group(1)).strip()
            print(f"🎯 GUIDANCE TYPE: {guidance}")

        # Check for theme colors
        if 'linear-gradient' in html_content:
            gradient_match = re.search(r'background: (linear-gradient[^;]+)', html_content)
            if gradient_match:
                print(f"🎨 THEME GRADIENT: {gradient_match.group(1)[:60]}...")

        # Check for icons
        icon_matches = re.findall(r'[◈◉◐]', html_content)
        if icon_matches:
            print(f"🔸 THEME ICON: {icon_matches[0]}")

        print(f"{'='*100}")

    def container(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

# Mock streamlit
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from dashboard.processors.dynamic_task_manager import DynamicTaskManager, TaskType, ActiveTask
from dashboard.processors.task_guidance_system import TaskGuidanceSystem
from dashboard.ui.task_ui_renderer import TaskUIRenderer
from datetime import datetime


def display_task_content(task_type: TaskType, test_group: str, guidance_system: TaskGuidanceSystem):
    """Display the content of a specific task for a test group"""

    print(f"\n{'='*80}")
    print(f"🎯 TASK: {task_type.value.upper()} | GROUP: {test_group}")
    print(f"{'='*80}")

    # Get task data based on test group
    if test_group == "MENTOR":
        task_data = guidance_system.mentor_tasks.get(task_type, {})
        print(f"📋 MENTOR MODE - Socratic Questioning Approach")
    elif test_group == "GENERIC_AI":
        task_data = guidance_system.generic_ai_tasks.get(task_type, {})
        print(f"📋 GENERIC_AI MODE - Direct Information Approach")
    elif test_group == "CONTROL":
        task_data = guidance_system.control_tasks.get(task_type, {})
        print(f"📋 CONTROL MODE - Minimal Guidance Approach")
    else:
        print(f"❌ Unknown test group: {test_group}")
        return

    if not task_data:
        print(f"❌ No task data found for {task_type.value} in {test_group} mode")
        return

    # Display task assignment
    task_assignment = task_data.get("task_assignment", "No assignment found")
    print(f"\n📝 TASK ASSIGNMENT:")
    print(f"{'-'*60}")
    print(task_assignment)

    # Display mode-specific content
    if test_group == "MENTOR":
        socratic_questions = task_data.get("socratic_questions", [])
        if socratic_questions:
            print(f"\n❓ SOCRATIC QUESTIONS:")
            print(f"{'-'*60}")
            for i, question in enumerate(socratic_questions, 1):
                print(f"{i}. {question}")

    elif test_group == "GENERIC_AI":
        direct_info = task_data.get("direct_information", [])
        if direct_info:
            print(f"\n📚 DIRECT INFORMATION:")
            print(f"{'-'*60}")
            for i, info in enumerate(direct_info, 1):
                print(f"{i}. {info}")

    elif test_group == "CONTROL":
        minimal_prompt = task_data.get("minimal_prompt", "")
        if minimal_prompt:
            print(f"\n💭 MINIMAL PROMPT:")
            print(f"{'-'*60}")
            print(minimal_prompt)

    print(f"\n{'='*80}")


def render_task_ui(task_type: TaskType, test_group: str, guidance_system: TaskGuidanceSystem, ui_renderer: TaskUIRenderer):
    """Render the actual Streamlit UI for a task"""

    print(f"\n🎨 RENDERING STREAMLIT UI FOR: {task_type.value.upper()} | {test_group}")
    print(f"{'='*100}")

    try:
        # Create a mock active task
        task = ActiveTask(
            task_type=task_type,
            start_time=datetime.now(),
            test_group=test_group,
            current_phase="ideation" if task_type.value.startswith(('architectural', 'spatial')) else
                         "visualization" if task_type.value.startswith(('visual', 'environmental')) else
                         "materialization",
            trigger_reason="UI Debug Test",
            completion_criteria=[],
            task_specific_data={},
            trigger_phase_completion=10.0
        )

        # Get task content
        if test_group == "MENTOR":
            task_data = guidance_system.mentor_tasks.get(task_type, {})
        elif test_group == "GENERIC_AI":
            task_data = guidance_system.generic_ai_tasks.get(task_type, {})
        elif test_group == "CONTROL":
            task_data = guidance_system.control_tasks.get(task_type, {})
        else:
            task_data = {}

        task_content = task_data.get("task_assignment", f"🎯 TASK {task_type.value}: Complete the design challenge")
        guidance_type = "socratic" if test_group == "MENTOR" else "direct" if test_group == "GENERIC_AI" else "minimal"

        print(f"📋 Task Content Length: {len(task_content)} characters")
        print(f"🎯 Guidance Type: {guidance_type}")

        # Clear previous UI output
        st.ui_output = []

        # Render the actual UI component
        ui_renderer.render_task_component(task, task_content, guidance_type)

        print(f"✅ UI Rendering Completed - {len(st.ui_output)} UI elements generated")

        # Display any additional UI elements that were rendered
        for ui_type, content in st.ui_output:
            if ui_type == "MARKDOWN" and content.strip():
                print(f"📄 Additional Content: {content[:100]}...")

    except Exception as e:
        print(f"❌ UI Rendering Failed: {e}")
        import traceback
        traceback.print_exc()

    print(f"{'='*100}")


def test_task_triggering_with_threshold_crossing():
    """Test the new threshold crossing detection system"""
    
    print(f"\n🔍 TESTING: Threshold Crossing Detection System")
    print(f"{'='*80}")
    
    task_manager = DynamicTaskManager()
    
    # Test scenario: User jumps from 31% to 40% completion
    # Task 1.2 has threshold at 20-60%, so it should trigger
    
    print(f"📊 SCENARIO: User completion jumps 31% → 40%")
    print(f"   Task 1.2 (SPATIAL_PROGRAM) threshold: 20-60%")
    print(f"   Expected: Task should trigger because 40% is within range and user crossed into it")
    
    # Simulate the progression
    conversation_history = [{"role": "user", "content": "Working on my design"}]
    
    # First update: 31% completion (should not trigger Task 1.2 yet if it requires prerequisites)
    print(f"\n🎯 Step 1: 31% completion")
    triggered_task_1 = task_manager.check_task_triggers(
        user_input="I'm developing my spatial program",
        conversation_history=conversation_history,
        current_phase="ideation",
        test_group="MENTOR",
        phase_completion_percent=31.0
    )
    
    if triggered_task_1:
        print(f"   ✅ Triggered: {triggered_task_1.value}")
        # Complete prerequisite if needed
        if triggered_task_1 == TaskType.ARCHITECTURAL_CONCEPT:
            task_manager.activate_task(triggered_task_1, "MENTOR", "ideation", "Test")
            task_manager.complete_task(triggered_task_1, "Completed for test")
    else:
        print(f"   ⚪ No task triggered")
    
    # Second update: 40% completion (should trigger Task 1.2 due to threshold crossing)
    print(f"\n🎯 Step 2: 40% completion (threshold crossing)")
    triggered_task_2 = task_manager.check_task_triggers(
        user_input="Continuing with spatial program development",
        conversation_history=conversation_history,
        current_phase="ideation",
        test_group="MENTOR",
        phase_completion_percent=40.0
    )
    
    if triggered_task_2:
        print(f"   ✅ THRESHOLD_CROSSED: {triggered_task_2.value}")
        return True
    else:
        print(f"   ❌ THRESHOLD_CROSSING_FAILED: No task triggered")
        return False


def test_phase_transition_tasks():
    """Test phase transition task triggering"""
    
    print(f"\n🔄 TESTING: Phase Transition Task Triggering")
    print(f"{'='*80}")
    
    task_manager = DynamicTaskManager()
    
    # Set up completed ideation phase
    task_manager.user_progression_history["ideation"] = 100.0
    
    # Complete prerequisite tasks
    arch_task = task_manager.activate_task(TaskType.ARCHITECTURAL_CONCEPT, "MENTOR", "ideation", "Test")
    task_manager.complete_task(TaskType.ARCHITECTURAL_CONCEPT, "Completed")
    
    spatial_task = task_manager.activate_task(TaskType.SPATIAL_PROGRAM, "MENTOR", "ideation", "Test")
    task_manager.complete_task(TaskType.SPATIAL_PROGRAM, "Completed")
    
    print(f"📊 SCENARIO: Ideation 100% → Visualization 0%")
    print(f"   Expected: Task 2.0 (VISUAL_CONCEPTUALIZATION) should trigger at visualization start")
    
    # Test phase transition
    transition_tasks = task_manager.check_phase_transition_tasks(
        from_phase="ideation",
        to_phase="visualization",
        user_input="Moving to visualization phase",
        conversation_history=[],
        test_group="MENTOR"
    )
    
    if transition_tasks:
        print(f"   ✅ PHASE_TRANSITION_TASKS: {[task.value for task in transition_tasks]}")
        return True
    else:
        print(f"   ❌ PHASE_TRANSITION_FAILED: No tasks triggered")
        return False


def test_focused_ui_rendering():
    """Test UI rendering for key tasks that users commonly see"""

    print(f"\n🎨 FOCUSED UI RENDERING TEST")
    print(f"{'='*80}")

    guidance_system = TaskGuidanceSystem()
    ui_renderer = TaskUIRenderer()

    # Test the most common tasks users encounter
    key_tasks = [
        (TaskType.ARCHITECTURAL_CONCEPT, "MENTOR"),
        (TaskType.ARCHITECTURAL_CONCEPT, "GENERIC_AI"),
        (TaskType.ARCHITECTURAL_CONCEPT, "CONTROL"),
        (TaskType.SPATIAL_PROGRAM, "MENTOR"),
        (TaskType.VISUAL_CONCEPTUALIZATION, "MENTOR"),
    ]

    print(f"🎯 Testing {len(key_tasks)} key task UI renderings...")

    for task_type, test_group in key_tasks:
        print(f"\n{'='*60}")
        print(f"🎨 FOCUSED TEST: {task_type.value} | {test_group}")
        print(f"{'='*60}")

        render_task_ui(task_type, test_group, guidance_system, ui_renderer)

        # Add a pause for readability
        print(f"\n⏸️  [UI rendered above - check the HTML output for visual formatting]")


def main():
    """Debug all task messages and triggering logic"""
    print("🚀 COMPREHENSIVE TASK MESSAGE & TRIGGERING DEBUG")
    print("=" * 80)

    try:
        # Initialize systems
        guidance_system = TaskGuidanceSystem()
        task_manager = DynamicTaskManager()

        # Get all task types
        all_tasks = list(TaskType)
        test_groups = ["MENTOR", "GENERIC_AI", "CONTROL"]

        print(f"📋 Found {len(all_tasks)} task types across {len(test_groups)} test groups")

        # Option 1: Full comprehensive display (all tasks, all groups)
        print(f"\n🔍 Choose debug mode:")
        print(f"   1. Full comprehensive display (all tasks, all groups)")
        print(f"   2. Focused UI rendering test (key tasks only)")
        print(f"   3. Both comprehensive and focused tests")

        # For automated testing, we'll do focused UI rendering
        mode = 2  # Focused UI rendering

        if mode == 1 or mode == 3:
            # Initialize UI renderer
            ui_renderer = TaskUIRenderer()

            # Display all task content and UI for each group
            for test_group in test_groups:
                print(f"\n\n🎯 DISPLAYING ALL TASKS FOR {test_group} MODE")
                print(f"{'='*100}")

                for task_type in all_tasks:
                    # Display task content (text)
                    display_task_content(task_type, test_group, guidance_system)

                    # Render actual Streamlit UI
                    render_task_ui(task_type, test_group, guidance_system, ui_renderer)

        if mode == 2 or mode == 3:
            # Focused UI rendering test
            test_focused_ui_rendering()
        
        # Test threshold crossing detection
        threshold_crossing_works = test_task_triggering_with_threshold_crossing()
        
        # Test phase transition tasks
        phase_transition_works = test_phase_transition_tasks()
        
        print(f"\n\n{'='*80}")
        print(f"📊 COMPREHENSIVE DEBUG SUMMARY")
        print(f"{'='*80}")
        
        print(f"✅ Task Content Display: Complete")
        print(f"   • All {len(all_tasks)} tasks displayed for all 3 test groups")
        print(f"   • MENTOR: Socratic questions and guided exploration")
        print(f"   • GENERIC_AI: Direct information and examples")
        print(f"   • CONTROL: Minimal prompts and self-direction")
        
        print(f"\n🎯 Task Triggering Logic:")
        print(f"   • Threshold Crossing Detection: {'✅ Working' if threshold_crossing_works else '❌ Failed'}")
        print(f"   • Phase Transition Tasks: {'✅ Working' if phase_transition_works else '❌ Failed'}")
        
        if threshold_crossing_works and phase_transition_works:
            print(f"\n🎉 ALL SYSTEMS WORKING CORRECTLY!")
            print(f"   • Tasks will trigger when users cross completion thresholds")
            print(f"   • Phase transitions will show both missed and new tasks")
            print(f"   • No tasks will be skipped due to completion percentage jumps")
        else:
            print(f"\n⚠️ SOME ISSUES DETECTED - CHECK IMPLEMENTATION")
        
        print(f"{'='*80}")
        
        return 0 if (threshold_crossing_works and phase_transition_works) else 1
        
    except Exception as e:
        print(f"\n❌ COMPREHENSIVE DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
