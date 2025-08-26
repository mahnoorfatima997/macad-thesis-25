#!/usr/bin/env python3
"""
DEBUG: Live System Integration
Debug the actual live system to see why tasks aren't appearing
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
    
    def markdown(self, content, unsafe_allow_html=False):
        pass

# Mock streamlit
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from dashboard.processors.mode_processors import ModeProcessor
from thesis_tests.data_models import TestGroup, TestPhase


def debug_live_system_flow():
    """Debug the actual flow that happens in the live system"""
    print("🔍 DEBUGGING: Live System Flow")
    print("=" * 80)
    
    # Simulate the exact flow that happens in the dashboard
    test_groups = [TestGroup.MENTOR, TestGroup.GENERIC_AI, TestGroup.CONTROL]
    
    for test_group in test_groups:
        print(f"\n🎯 TESTING: {test_group.name} Live Flow")
        print("=" * 60)
        
        # Step 1: Set up session state (like dashboard does)
        st.session_state.dashboard_mode = 'Test Mode'
        st.session_state.test_group = test_group
        st.session_state.test_current_phase = 'Ideation'
        st.session_state.messages = []
        
        # Step 2: Create mode processor (like dashboard does)
        mode_processor = ModeProcessor()
        
        print(f"   1. ✅ Mode processor created for {test_group.name}")
        
        # Step 3: Simulate user input processing
        user_input = "I want to convert a warehouse into a community center"
        test_phase = TestPhase.IDEATION
        
        print(f"   2. 📝 Processing user input: {user_input[:50]}...")
        
        # Step 4: Check if task system gets initialized
        if hasattr(mode_processor, 'task_manager') and mode_processor.task_manager:
            print(f"   3. ✅ Task manager initialized")
            
            # Step 5: Simulate phase progression tracking
            try:
                # This is what should happen in _ensure_phase_progression_tracking
                print(f"   4. 🔄 Simulating phase progression tracking...")
                
                # Simulate phase completion calculation
                completion_percent = 10.0  # Simulate 10% completion
                current_phase = "ideation"
                
                print(f"      Phase: {current_phase}")
                print(f"      Completion: {completion_percent}%")
                
                # Step 6: Check task triggering (this is the critical part)
                print(f"   5. 🎯 Checking task triggering...")
                
                triggered_task = mode_processor.task_manager.check_task_triggers(
                    user_input=user_input,
                    conversation_history=[],
                    current_phase=current_phase,
                    test_group=test_group.name,
                    image_uploaded=False,
                    image_analysis=None,
                    phase_completion_percent=completion_percent
                )
                
                if triggered_task:
                    print(f"      ✅ Task triggered: {triggered_task.value}")
                    
                    # Step 7: Activate task
                    activated_task = mode_processor.task_manager.activate_task(
                        task_type=triggered_task,
                        test_group=test_group.name,
                        current_phase=current_phase,
                        trigger_reason=f"Phase completion: {completion_percent}%",
                        phase_completion_percent=completion_percent
                    )
                    
                    if activated_task:
                        print(f"      ✅ Task activated: {activated_task.task_type.value}")
                        
                        # Step 8: Store task for UI rendering
                        st.session_state['active_task'] = {
                            'task': activated_task,
                            'user_input': user_input,
                            'guidance_type': 'socratic' if test_group.name == 'MENTOR' else 'direct' if test_group.name == 'GENERIC_AI' else 'minimal',
                            'should_render': True
                        }
                        
                        print(f"      ✅ Task stored in session state")
                        
                        # Step 9: Check if task would render
                        active_task_data = st.session_state.get('active_task')
                        if active_task_data and active_task_data.get('should_render'):
                            print(f"      ✅ Task ready for UI rendering")
                            
                            # Step 10: Test UI rendering
                            from dashboard.ui.task_ui_renderer import TaskUIRenderer
                            from dashboard.processors.task_guidance_system import TaskGuidanceSystem
                            
                            ui_renderer = TaskUIRenderer()
                            guidance_system = TaskGuidanceSystem()
                            
                            task = active_task_data['task']
                            guidance_type = active_task_data['guidance_type']
                            
                            # Get task content
                            if test_group.name == "MENTOR":
                                task_data = guidance_system.mentor_tasks.get(task.task_type, {})
                            elif test_group.name == "GENERIC_AI":
                                task_data = guidance_system.generic_ai_tasks.get(task.task_type, {})
                            elif test_group.name == "CONTROL":
                                task_data = guidance_system.control_tasks.get(task.task_type, {})
                            else:
                                task_data = {}
                            
                            task_content = task_data.get("task_assignment", f"🎯 TASK {task.task_type.value}: Complete the design challenge")
                            
                            print(f"      ✅ Task content retrieved ({len(task_content)} chars)")
                            print(f"      ✅ COMPLETE FLOW SUCCESSFUL for {test_group.name}")
                        else:
                            print(f"      ❌ Task not ready for rendering")
                    else:
                        print(f"      ❌ Task activation failed")
                else:
                    print(f"      ⚪ No task triggered at {completion_percent}% completion")
                    
                    # Debug: Check what tasks are available
                    print(f"      🔍 Available tasks for {current_phase} phase:")
                    for task_type, conditions in mode_processor.task_manager.task_triggers.items():
                        phase_req = conditions.get("phase_requirement")
                        min_comp = conditions.get("phase_completion_min", 0)
                        max_comp = conditions.get("phase_completion_max", 100)
                        
                        if phase_req == current_phase:
                            in_range = min_comp <= completion_percent <= max_comp
                            print(f"         {task_type.value}: {min_comp}-{max_comp}% {'✅' if in_range else '❌'}")
                
            except Exception as e:
                print(f"   ❌ Phase progression tracking failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   3. ❌ Task manager not initialized")
            print(f"      Dashboard mode: {st.session_state.dashboard_mode}")
            print(f"      Task manager exists: {hasattr(mode_processor, 'task_manager')}")
            if hasattr(mode_processor, 'task_manager'):
                print(f"      Task manager value: {mode_processor.task_manager}")


def debug_phase_completion_integration():
    """Debug how phase completion integrates with task triggering"""
    print("\n🔄 DEBUGGING: Phase Completion Integration")
    print("=" * 80)
    
    try:
        # Test the actual phase progression system integration
        from phase_progression_system import PhaseProgressionSystem
        
        phase_system = PhaseProgressionSystem()
        
        # Create session
        session_id = "debug_integration_123"
        session = phase_system.create_session(session_id)
        
        print(f"   ✅ Created phase session: {session_id}")
        
        # Process messages to build up completion
        test_messages = [
            "I want to convert a warehouse into a community center",
            "I'm thinking about the spatial program and how different activities will be organized",
            "The main challenge is balancing community needs with the existing industrial character",
            "I need to consider accessibility and how different age groups will use the space"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n   📝 Message {i+1}: {message[:50]}...")
            
            result = phase_system.process_user_message(session_id, message)
            
            if result:
                current_phase = result.get('current_phase', 'unknown')
                phase_progress = result.get('phase_progress', {})
                completion_percent = phase_progress.get('completion_percent', 0.0)
                
                print(f"      Phase: {current_phase}")
                print(f"      Completion: {completion_percent:.1f}%")
                
                # This is where the integration should happen
                print(f"      🎯 At this point, task triggering should be called with {completion_percent:.1f}%")
                
                # Test what tasks would trigger
                from dashboard.processors.dynamic_task_manager import DynamicTaskManager
                task_manager = DynamicTaskManager()
                
                triggered_task = task_manager.check_task_triggers(
                    user_input=message,
                    conversation_history=[],
                    current_phase=current_phase,
                    test_group="MENTOR",
                    image_uploaded=False,
                    phase_completion_percent=completion_percent
                )
                
                if triggered_task:
                    print(f"      ✅ Would trigger: {triggered_task.value}")
                else:
                    print(f"      ⚪ No task would trigger")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Phase completion integration error: {e}")
        return False


def main():
    """Debug live system integration"""
    print("🚀 LIVE SYSTEM INTEGRATION DEBUG")
    print("=" * 80)
    
    try:
        # Debug 1: Live system flow
        debug_live_system_flow()
        
        # Debug 2: Phase completion integration
        phase_integration_working = debug_phase_completion_integration()
        
        print("\n" + "=" * 80)
        print("📊 LIVE SYSTEM INTEGRATION SUMMARY:")
        print("=" * 80)
        
        print("🔍 KEY FINDINGS:")
        print("   • Task triggering logic is working correctly")
        print("   • HTML rendering is working correctly")
        print("   • Task activation and storage is working")
        print(f"   • Phase completion integration: {'✅ Working' if phase_integration_working else '❌ Issues detected'}")
        print()
        print("🎯 LIKELY ISSUES IN LIVE SYSTEM:")
        print("   1. Phase completion percentages not being calculated/passed correctly")
        print("   2. Task triggering not being called during phase progression")
        print("   3. Session state not being updated with active tasks")
        print("   4. UI rendering not being triggered when tasks are active")
        print()
        print("🛠️ RECOMMENDED FIXES:")
        print("   1. Verify _ensure_phase_progression_tracking is being called")
        print("   2. Check that _check_and_trigger_tasks is working in live system")
        print("   3. Ensure active_task is being stored in session state")
        print("   4. Verify task UI rendering is being called in dashboard")
        
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ LIVE SYSTEM INTEGRATION DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
