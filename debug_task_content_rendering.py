#!/usr/bin/env python3
"""
DEBUG: Task Content Rendering
Debug what content is actually being rendered in the task UI
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
        self.active_task = None
        
    def get(self, key, default=None):
        return getattr(self, key, default)

class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
        self._markdown_content = []
    
    def markdown(self, content, unsafe_allow_html=False):
        self._markdown_content.append(content)
        # Print first 200 chars of each markdown call for debugging
        print(f"MARKDOWN CALL: {content[:200]}...")
        print("---")
    
    def get_markdown_content(self):
        return self._markdown_content
    
    def clear_markdown_content(self):
        self._markdown_content = []

# Mock streamlit
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from dashboard.ui.task_ui_renderer import TaskUIRenderer
from dashboard.processors.dynamic_task_manager import ActiveTask, TaskType
from dashboard.processors.task_guidance_system import TaskGuidanceSystem
from thesis_tests.data_models import TestGroup, TestPhase
from datetime import datetime


def debug_task_content_flow():
    """Debug the complete task content flow"""
    print("🔍 DEBUGGING: Task Content Flow")
    print("=" * 80)
    
    # Step 1: Get actual task content from guidance system
    print("📋 STEP 1: Getting task content from guidance system")
    guidance_system = TaskGuidanceSystem()
    task_data = guidance_system.mentor_tasks.get(TaskType.ARCHITECTURAL_CONCEPT, {})
    
    original_assignment = task_data.get("task_assignment", "")
    original_questions = task_data.get("socratic_questions", [])
    
    print(f"   Original assignment length: {len(original_assignment)}")
    print(f"   Original assignment preview: {original_assignment[:150]}...")
    print(f"   Original questions count: {len(original_questions)}")
    if original_questions:
        print(f"   First question: {original_questions[0]}")
    
    # Step 2: Simulate chat_components.py content creation
    print(f"\n📋 STEP 2: Simulating chat_components.py content creation")
    task_content = original_assignment
    if original_questions:
        task_content += f"\n\n**Guided Exploration Question:**\n{original_questions[0]}"
    
    print(f"   Combined content length: {len(task_content)}")
    print(f"   Combined content preview: {task_content[:200]}...")
    
    # Step 3: Test extraction methods
    print(f"\n📋 STEP 3: Testing extraction methods")
    renderer = TaskUIRenderer()
    
    extracted_title = renderer._extract_clean_task_title(task_content)
    extracted_assignment = renderer._extract_clean_assignment(task_content)
    extracted_question = renderer._extract_socratic_question(task_content)

    print(f"   Extracted title: '{extracted_title}'")
    print(f"   Extracted assignment length: {len(extracted_assignment)}")
    print(f"   Extracted assignment: {extracted_assignment[:150]}...")
    print(f"   Extracted question: {extracted_question}")

    # Debug the question extraction in detail
    print(f"\n   QUESTION EXTRACTION DEBUG:")
    lines = task_content.split('\n')
    for i, line in enumerate(lines):
        if 'Guided Exploration Question' in line or line.strip().endswith('?'):
            print(f"      Line {i}: {line}")
            if i + 1 < len(lines):
                print(f"      Next line: {lines[i + 1]}")
    
    # Step 4: Test rendering
    print(f"\n📋 STEP 4: Testing rendering with debug output")
    
    task = ActiveTask(
        task_type=TaskType.ARCHITECTURAL_CONCEPT,
        start_time=datetime.now(),
        test_group="MENTOR",
        current_phase="ideation",
        trigger_reason="Test trigger",
        completion_criteria={},
        task_specific_data={},
        trigger_phase_completion=15.0
    )
    
    st.clear_markdown_content()
    
    print(f"\n   RENDERING TASK COMPONENT:")
    print(f"   Task: {task.task_type.value}")
    print(f"   Content length: {len(task_content)}")
    print(f"   Guidance type: socratic")
    
    renderer.render_task_component(task, task_content, "socratic")
    
    # Step 5: Analyze rendered content
    print(f"\n📋 STEP 5: Analyzing rendered content")
    markdown_content = st.get_markdown_content()
    
    print(f"   Total markdown calls: {len(markdown_content)}")
    
    for i, content in enumerate(markdown_content):
        print(f"\n   MARKDOWN CALL {i+1}:")
        if 'Architectural Concept Development' in content:
            print(f"      ✅ Contains specific title")
        if 'community center for a diverse urban' in content:
            print(f"      ✅ Contains specific assignment")
        if 'community social patterns' in content or 'most important questions' in content:
            print(f"      ✅ Contains specific question")
        if 'Complete the design challenge assignment' in content:
            print(f"      ❌ Contains generic assignment")
        if 'Explore this challenge through thoughtful' in content:
            print(f"      ❌ Contains generic guidance")

        # Show first 300 chars of guidance call (call 4)
        if i == 3:  # Guidance call
            print(f"      GUIDANCE CONTENT: {content[:300]}...")
    
    # Check full content
    full_content = ' '.join(markdown_content)
    
    print(f"\n   FULL CONTENT ANALYSIS:")
    print(f"   ✅ Specific title present: {'Architectural Concept Development' in full_content}")
    print(f"   ✅ Specific assignment present: {'community center for a diverse urban' in full_content}")
    print(f"   ✅ Specific question present: {'community social patterns' in full_content}")
    print(f"   ❌ Generic assignment present: {'Complete the design challenge assignment' in full_content}")
    print(f"   ❌ Generic guidance present: {'Explore this challenge through thoughtful' in full_content}")


def main():
    """Debug task content rendering"""
    print("🚀 TASK CONTENT RENDERING DEBUG")
    print("=" * 80)
    
    try:
        debug_task_content_flow()
        
        print("\n" + "=" * 80)
        print("🔍 DEBUG COMPLETE")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
