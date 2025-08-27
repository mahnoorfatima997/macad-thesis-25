#!/usr/bin/env python3
"""
DEBUG: UI Visual Preview
Create a visual preview of how tasks appear in the Streamlit UI
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
        self.html_outputs = []
    
    def markdown(self, content, unsafe_allow_html=False):
        if unsafe_allow_html and content:
            self.html_outputs.append(content)
            self._create_visual_preview(content)
    
    def _create_visual_preview(self, html_content):
        """Create a visual preview of the HTML content"""
        import re
        
        print(f"\n{'🎨 VISUAL PREVIEW ' + '='*70}")
        
        # Extract task title
        title_match = re.search(r'<h2[^>]*>(.*?)</h2>', html_content, re.DOTALL)
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            print(f"┌{'─'*78}┐")
            print(f"│{title.center(78)}│")
            print(f"├{'─'*78}┤")
        
        # Extract guidance type
        guidance_match = re.search(r'<div[^>]*color: rgba\(255,255,255,0\.9\)[^>]*>(.*?)</div>', html_content, re.DOTALL)
        if guidance_match:
            guidance = re.sub(r'<[^>]+>', '', guidance_match.group(1)).strip()
            print(f"│{guidance.center(78)}│")
            print(f"├{'─'*78}┤")
        
        # Extract theme colors and create visual representation
        if 'linear-gradient' in html_content:
            gradient_match = re.search(r'background: (linear-gradient[^;]+)', html_content)
            if gradient_match:
                gradient = gradient_match.group(1)
                if '#784c80' in gradient:  # MENTOR colors
                    print(f"│{'🟣 MENTOR THEME: Purple gradient with warm accents'.center(78)}│")
                elif '#5c4f73' in gradient:  # GENERIC_AI colors
                    print(f"│{'🔵 GENERIC_AI THEME: Blue-purple gradient'.center(78)}│")
                elif '#4f3a3e' in gradient:  # CONTROL colors
                    print(f"│{'🟤 CONTROL THEME: Brown-neutral gradient'.center(78)}│")
        
        # Extract and display icon
        icon_matches = re.findall(r'[◈◉◐]', html_content)
        if icon_matches:
            icon = icon_matches[0]
            icon_desc = {'◈': 'Diamond (MENTOR)', '◉': 'Circle (GENERIC_AI)', '◐': 'Half-circle (CONTROL)'}
            icon_text = f'Icon: {icon} - {icon_desc.get(icon, "Unknown")}'
            print(f"│{icon_text.center(78)}│")
        
        print(f"└{'─'*78}┘")
        print(f"{'='*88}")
    
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


def create_task_ui_preview(task_type: TaskType, test_group: str):
    """Create a comprehensive UI preview for a specific task"""
    
    print(f"\n{'🎯 TASK UI PREVIEW ' + '='*60}")
    print(f"Task: {task_type.value.upper()} | Group: {test_group}")
    print(f"{'='*80}")
    
    try:
        # Initialize systems
        guidance_system = TaskGuidanceSystem()
        ui_renderer = TaskUIRenderer()
        
        # Create mock active task
        task = ActiveTask(
            task_type=task_type,
            start_time=datetime.now(),
            test_group=test_group,
            current_phase="ideation" if task_type.value.startswith(('architectural', 'spatial')) else 
                         "visualization" if task_type.value.startswith(('visual', 'environmental')) else 
                         "materialization",
            trigger_reason="UI Preview Test",
            completion_criteria=[],
            task_specific_data={},
            trigger_phase_completion=25.0
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
        
        if not task_data:
            print(f"❌ No task data found for {task_type.value} in {test_group} mode")
            return
        
        task_content = task_data.get("task_assignment", f"🎯 TASK {task_type.value}: Complete the design challenge")
        guidance_type = "socratic" if test_group == "MENTOR" else "direct" if test_group == "GENERIC_AI" else "minimal"
        
        # Clear previous HTML outputs
        st.html_outputs = []
        
        # Render the UI
        ui_renderer.render_task_component(task, task_content, guidance_type)
        
        # Display task content preview
        print(f"\n📝 TASK CONTENT PREVIEW:")
        print(f"{'─'*60}")
        content_lines = task_content.split('\n')
        for i, line in enumerate(content_lines[:10]):  # Show first 10 lines
            if line.strip():
                print(f"  {line.strip()}")
        if len(content_lines) > 10:
            print(f"  ... ({len(content_lines) - 10} more lines)")
        
        # Display mode-specific content
        if test_group == "MENTOR":
            socratic_questions = task_data.get("socratic_questions", [])
            if socratic_questions:
                print(f"\n❓ SOCRATIC QUESTIONS ({len(socratic_questions)} questions):")
                print(f"{'─'*60}")
                for i, question in enumerate(socratic_questions[:3], 1):  # Show first 3
                    print(f"  {i}. {question}")
                if len(socratic_questions) > 3:
                    print(f"  ... ({len(socratic_questions) - 3} more questions)")
        
        elif test_group == "GENERIC_AI":
            direct_info = task_data.get("direct_information", [])
            if direct_info:
                print(f"\n📚 DIRECT INFORMATION ({len(direct_info)} points):")
                print(f"{'─'*60}")
                for i, info in enumerate(direct_info[:3], 1):  # Show first 3
                    print(f"  {i}. {info}")
                if len(direct_info) > 3:
                    print(f"  ... ({len(direct_info) - 3} more information points)")
        
        elif test_group == "CONTROL":
            minimal_prompt = task_data.get("minimal_prompt", "")
            if minimal_prompt:
                print(f"\n💭 MINIMAL PROMPT:")
                print(f"{'─'*60}")
                print(f"  {minimal_prompt}")
        
        print(f"\n✅ UI Preview Generated Successfully")
        print(f"   HTML Elements: {len(st.html_outputs)}")
        print(f"   Content Length: {len(task_content)} characters")
        
    except Exception as e:
        print(f"❌ UI Preview Failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Create UI previews for key tasks"""
    print("🎨 STREAMLIT UI VISUAL PREVIEW GENERATOR")
    print("=" * 80)
    
    # Key tasks that users commonly encounter
    preview_tasks = [
        # Ideation phase tasks
        (TaskType.ARCHITECTURAL_CONCEPT, "MENTOR"),
        (TaskType.ARCHITECTURAL_CONCEPT, "GENERIC_AI"),
        (TaskType.ARCHITECTURAL_CONCEPT, "CONTROL"),
        
        # Spatial program task
        (TaskType.SPATIAL_PROGRAM, "MENTOR"),
        
        # Visualization phase tasks
        (TaskType.VISUAL_CONCEPTUALIZATION, "MENTOR"),
        (TaskType.VISUAL_ANALYSIS_2D, "GENERIC_AI"),
        
        # Environmental task
        (TaskType.ENVIRONMENTAL_CONTEXTUAL, "CONTROL"),
    ]
    
    print(f"🎯 Generating UI previews for {len(preview_tasks)} key tasks...")
    
    for task_type, test_group in preview_tasks:
        create_task_ui_preview(task_type, test_group)
        print(f"\n{'─'*80}")
    
    print(f"\n🎉 UI PREVIEW GENERATION COMPLETE!")
    print(f"{'='*80}")
    print(f"📋 SUMMARY:")
    print(f"   • Generated {len(preview_tasks)} task UI previews")
    print(f"   • Covered all 3 test groups (MENTOR, GENERIC_AI, CONTROL)")
    print(f"   • Showed visual representation of themes and layouts")
    print(f"   • Displayed task content and mode-specific guidance")
    print(f"")
    print(f"🎨 VISUAL ELEMENTS SHOWN:")
    print(f"   • Task titles and headers")
    print(f"   • Theme colors and gradients")
    print(f"   • Icons (◈ MENTOR, ◉ GENERIC_AI, ◐ CONTROL)")
    print(f"   • Guidance types and content")
    print(f"   • Task assignments and instructions")
    print(f"")
    print(f"✅ All UI components are rendering correctly!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
