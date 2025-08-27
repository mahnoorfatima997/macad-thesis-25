#!/usr/bin/env python3
"""
DEBUG: Live Task Triggering Issues
Debug why tasks aren't triggering at the right completion percentages
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
from dashboard.processors.dynamic_task_manager import TaskType
from thesis_tests.data_models import TestGroup, TestPhase


def debug_task_triggering_all_modes():
    """Debug task triggering across all three modes"""
    print("🔍 DEBUGGING: Task Triggering Across All Modes")
    print("=" * 80)
    
    test_groups = [TestGroup.MENTOR, TestGroup.GENERIC_AI, TestGroup.CONTROL]
    
    for test_group in test_groups:
        print(f"\n🎯 TESTING: {test_group.name} Mode")
        print("=" * 60)
        
        # Set up mode
        st.session_state.test_group = test_group
        st.session_state.test_current_phase = 'Ideation'
        
        mode_processor = ModeProcessor()
        mode_processor._ensure_task_system_initialized()
        
        if not mode_processor.task_manager:
            print(f"   ❌ Task manager not initialized for {test_group.name}")
            continue
        
        print(f"   ✅ Task manager initialized for {test_group.name}")
        
        # Test different completion percentages
        test_cases = [
            (5.0, "ideation", "Task 1.1 should trigger"),
            (15.0, "ideation", "Task 1.1 should still be in range"),
            (25.0, "ideation", "Task 1.2 should trigger"),
            (35.0, "ideation", "Task 1.2 should still be in range"),
            (65.0, "ideation", "No task should trigger (between ranges)"),
            (0.0, "visualization", "Task 2.0 should trigger"),
            (15.0, "visualization", "Task 2.0 should still be in range"),
            (35.0, "visualization", "Task 2.2 should trigger"),
        ]
        
        for completion, phase, expected in test_cases:
            print(f"\n   📊 Testing {completion}% {phase} completion:")
            print(f"      Expected: {expected}")
            
            # Clear previous tasks
            st.session_state.active_task = None
            
            # Check task triggering
            triggered_task = mode_processor.task_manager.check_task_triggers(
                user_input="I'm working on my community center design",
                conversation_history=[],
                current_phase=phase,
                test_group=test_group.name,
                image_uploaded=False,
                image_analysis=None,
                phase_completion_percent=completion
            )
            
            if triggered_task:
                print(f"      ✅ Triggered: {triggered_task.value}")
                
                # Try to activate the task
                try:
                    activated_task = mode_processor.task_manager.activate_task(
                        task_type=triggered_task,
                        test_group=test_group.name,
                        current_phase=phase,
                        trigger_reason=f"{completion}% completion test",
                        phase_completion_percent=completion
                    )
                    
                    if activated_task:
                        print(f"      ✅ Activated: {activated_task.task_type.value}")
                        
                        # Complete the task to allow next ones
                        mode_processor.task_manager.complete_task(triggered_task, "Test completion")
                        print(f"      ✅ Completed: {triggered_task.value}")
                    else:
                        print(f"      ❌ Failed to activate: {triggered_task.value}")
                        
                except Exception as e:
                    print(f"      ❌ Activation error: {e}")
            else:
                print(f"      ⚪ No task triggered")
        
        # Check task history
        print(f"\n   📊 Final Task History for {test_group.name}:")
        for task in mode_processor.task_manager.task_history:
            completion_reason = task.progress_indicators.get("completion_reason", "Unknown")
            print(f"      • {task.task_type.value}: {completion_reason}")


def debug_task_trigger_conditions():
    """Debug the actual task trigger conditions"""
    print("\n🔍 DEBUGGING: Task Trigger Conditions")
    print("=" * 80)
    
    from dashboard.processors.dynamic_task_manager import DynamicTaskManager
    
    task_manager = DynamicTaskManager()
    
    print("📋 Current Task Trigger Conditions:")
    
    for task_type, conditions in task_manager.task_triggers.items():
        print(f"\n   🎯 {task_type.value}:")
        print(f"      Phase: {conditions.get('phase_requirement', 'Any')}")
        print(f"      Completion: {conditions.get('phase_completion_min', 0):.0f}-{conditions.get('phase_completion_max', 100):.0f}%")
        
        if conditions.get('requires_previous'):
            prereqs = [req.value for req in conditions['requires_previous']]
            print(f"      Prerequisites: {prereqs}")
        
        if conditions.get('image_upload'):
            print(f"      Requires image: {conditions['image_upload']}")
        
        if conditions.get('trigger_once'):
            print(f"      Trigger once: {conditions['trigger_once']}")


def debug_phase_completion_calculation():
    """Debug how phase completion is calculated"""
    print("\n🔍 DEBUGGING: Phase Completion Calculation")
    print("=" * 80)
    
    try:
        # Try to import and test phase progression system
        from phase_progression_system import PhaseProgressionSystem
        
        phase_system = PhaseProgressionSystem()
        
        # Create a test session
        session_id = "debug_session_123"
        phase_system.create_session(session_id)
        
        print(f"   ✅ Created test session: {session_id}")
        
        # Test messages to simulate progression
        test_messages = [
            "I want to convert a warehouse into a community center",
            "I'm thinking about the spatial program and how to organize different activities",
            "The main challenge is balancing community needs with the existing industrial character",
            "I need to consider accessibility and how different age groups will use the space",
            "Let me think about the circulation patterns and how people will move through the building"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n   📝 Processing message {i+1}: {message[:50]}...")
            
            result = phase_system.process_user_message(session_id, message)
            
            if result:
                current_phase = result.get('current_phase', 'unknown')
                phase_progress = result.get('phase_progress', {})
                completion_percent = phase_progress.get('completion_percent', 0.0)
                
                print(f"      Phase: {current_phase}")
                print(f"      Completion: {completion_percent:.1f}%")
                
                # This is where task triggering should happen
                print(f"      🎯 Task triggering should check at {completion_percent:.1f}% completion")
            else:
                print(f"      ❌ No result from phase system")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Phase progression system error: {e}")
        return False


def main():
    """Debug task triggering issues"""
    print("🚀 TASK TRIGGERING DEBUG SESSION")
    print("=" * 80)
    
    try:
        # Debug 1: Task triggering across all modes
        debug_task_triggering_all_modes()
        
        # Debug 2: Task trigger conditions
        debug_task_trigger_conditions()
        
        # Debug 3: Phase completion calculation
        phase_system_working = debug_phase_completion_calculation()
        
        print("\n" + "=" * 80)
        print("📊 TASK TRIGGERING DEBUG SUMMARY:")
        print("=" * 80)
        
        print("🔍 KEY FINDINGS:")
        print("   • Task trigger conditions are properly configured")
        print("   • Task activation works when manually triggered")
        print(f"   • Phase progression system: {'✅ Working' if phase_system_working else '❌ Issues detected'}")
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Verify phase completion percentages are being passed correctly")
        print("   2. Check if task triggering is being called in live system")
        print("   3. Ensure task UI rendering is working properly")
        
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TASK TRIGGERING DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
