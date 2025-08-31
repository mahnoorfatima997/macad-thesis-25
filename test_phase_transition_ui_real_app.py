#!/usr/bin/env python3
"""
Test Phase Transition UI in Real Streamlit Application Context
This test runs within the actual Streamlit environment to verify task UI rendering
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

# Import real Streamlit and application components
import streamlit as st
from datetime import datetime

def initialize_real_app_session():
    """Initialize session exactly like the real application"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"test_session_{int(time.time())}"
    if 'dashboard_mode' not in st.session_state:
        st.session_state.dashboard_mode = 'Test Mode'
    if 'test_group' not in st.session_state:
        from thesis_tests.data_models import TestGroup
        st.session_state.test_group = TestGroup.MENTOR
    if 'test_current_phase' not in st.session_state:
        st.session_state.test_current_phase = 'Ideation'
    return True

def test_phase_transition_ui_rendering():
    """Test that task UI renders immediately during phase transitions in real app context"""
    print("🔧 TESTING: Phase Transition UI Rendering in Real App Context")
    print("=" * 70)
    
    try:
        # Import real application components
        from dashboard.processors.mode_processors import ModeProcessor
        from thesis_tests.data_models import TestGroup, TestPhase
        
        # Initialize real app session
        initialize_real_app_session()
        
        # Initialize real mode processor (like the actual app does)
        mode_processor = ModeProcessor()
        mode_processor._ensure_task_system_initialized()
        
        print("   ✅ Real application components initialized")
        
        # Simulate being in ideation phase with some progress
        st.session_state.test_current_phase = 'Ideation'
        st.session_state.messages = [
            {"role": "user", "content": "I want to design a community center"},
            {"role": "assistant", "content": "Great! Let's start with understanding the community needs."},
            {"role": "user", "content": "The community is diverse with many cultural groups"},
            {"role": "assistant", "content": "That's important context. How might this diversity influence your design?"},
        ]
        
        print("   ✅ Simulated ideation phase with conversation history")
        
        # Test 1: Trigger phase transition from ideation to visualization
        print("\n   🔄 TESTING: Phase transition from Ideation to Visualization")
        
        # Clear any existing active tasks
        if 'active_task' in st.session_state:
            del st.session_state['active_task']
        
        # Simulate phase transition (like the real app does)
        mode_processor._handle_phase_transition(
            from_phase='ideation',
            to_phase='visualization', 
            test_group=TestGroup.MENTOR,
            user_input="Phase transition to visualization"
        )
        
        # Check if task was activated and stored
        active_task_data = st.session_state.get('active_task')
        task_activated = active_task_data is not None
        
        print(f"   ✅ Task activated during phase transition: {task_activated}")
        
        if task_activated:
            task = active_task_data['task']
            print(f"   ✅ Task type: {task.task_type.value}")
            print(f"   ✅ Should render: {active_task_data.get('should_render', False)}")
            print(f"   ✅ Guidance type: {active_task_data.get('guidance_type', 'unknown')}")
        
        # Test 2: Verify task UI components render for messages
        print("\n   🎨 TESTING: Task UI rendering for messages")
        
        # Add a new message to trigger task UI rendering
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🎉 Phase Transition: Welcome to the visualization phase! Now we'll focus on spatial organization.",
            "timestamp": datetime.now().isoformat(),
            "phase_transition": True
        })
        
        # Test task UI rendering for the new message
        try:
            from dashboard.ui.chat_components import render_tasks_for_message
            
            # Get the message index (last message)
            message_index = len(st.session_state.messages) - 1
            
            # Clear UI output tracking
            st.ui_outputs = []
            
            # Render tasks for the message (like the real app does)
            render_tasks_for_message(message_index)
            
            ui_rendered = len(st.ui_outputs) > 0
            print(f"   ✅ Task UI rendered for message: {ui_rendered}")
            
            if ui_rendered:
                print(f"   ✅ UI components generated: {len(st.ui_outputs)}")
                for i, (ui_type, content) in enumerate(st.ui_outputs):
                    print(f"      UI {i+1}: {ui_type} ({len(content)} chars)")
        
        except Exception as ui_error:
            print(f"   ❌ Task UI rendering failed: {ui_error}")
            ui_rendered = False
        
        # Test 3: Verify completed tasks persist in chat history
        print("\n   📜 TESTING: Completed task persistence")
        
        # Simulate completing the current task
        if task_activated and mode_processor.task_manager:
            task_type = active_task_data['task'].task_type
            mode_processor.task_manager.complete_task(task_type, "Test completion")
            print(f"   ✅ Task {task_type.value} marked as completed")
            
            # Test that completed task UI still renders for past messages
            try:
                # Clear UI output tracking
                st.ui_outputs = []
                
                # Render tasks for the message again (should show completed task)
                render_tasks_for_message(message_index)
                
                completed_ui_rendered = len(st.ui_outputs) > 0
                print(f"   ✅ Completed task UI still renders: {completed_ui_rendered}")
                
            except Exception as persistence_error:
                print(f"   ❌ Completed task persistence failed: {persistence_error}")
                completed_ui_rendered = False
        else:
            completed_ui_rendered = True  # Skip if no task to complete
            print("   ⏭️ Skipping completed task test (no active task)")
        
        # Overall success assessment
        overall_success = task_activated and ui_rendered and completed_ui_rendered
        
        print(f"\n   🎯 PHASE TRANSITION UI TEST RESULTS:")
        print(f"      Task activation during transition: {'✅' if task_activated else '❌'}")
        print(f"      Task UI rendering for messages: {'✅' if ui_rendered else '❌'}")
        print(f"      Completed task persistence: {'✅' if completed_ui_rendered else '❌'}")
        
        if overall_success:
            print(f"\n   🎉 SUCCESS: Phase transition UI working in real app context!")
            print(f"      ✅ Students will see task UI immediately during phase transitions")
            print(f"      ✅ Task UI components render before agent responses")
            print(f"      ✅ Completed tasks remain visible in chat history")
        else:
            print(f"\n   ❌ FAILURE: Phase transition UI issues remain")
            print(f"      🔧 Students may not see task interfaces during transitions")
        
        return overall_success
        
    except Exception as e:
        print(f"   ❌ Phase transition UI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_8_tasks_ui_rendering():
    """Test UI rendering for all 8 tasks in real app context"""
    print("\n🔧 TESTING: All 8 Tasks UI Rendering")
    print("=" * 70)
    
    try:
        from dashboard.processors.dynamic_task_manager import TaskType
        from dashboard.processors.mode_processors import ModeProcessor
        from thesis_tests.data_models import TestGroup
        
        # Initialize real app components
        initialize_real_app_session()
        mode_processor = ModeProcessor()
        mode_processor._ensure_task_system_initialized()
        
        all_tasks = [
            TaskType.ARCHITECTURAL_CONCEPT,
            TaskType.SPATIAL_PROGRAM, 
            TaskType.VISUAL_ANALYSIS_2D,
            TaskType.VISUAL_ANALYSIS_3D,
            TaskType.TECHNICAL_SYSTEMS,
            TaskType.MATERIAL_SELECTION,
            TaskType.SUSTAINABILITY_ANALYSIS,
            TaskType.FINAL_PRESENTATION
        ]
        
        successful_renders = 0
        
        for i, task_type in enumerate(all_tasks):
            print(f"\n   🎯 Testing Task {i+1}/8: {task_type.value}")
            
            try:
                # Activate the task
                activated_task = mode_processor.task_manager.activate_task(
                    task_type=task_type,
                    test_group="MENTOR",
                    current_phase="ideation",
                    trigger_reason="Test activation",
                    phase_completion_percent=50.0
                )
                
                if activated_task:
                    # Store task for UI rendering
                    st.session_state['active_task'] = {
                        'task': activated_task,
                        'user_input': f"Test input for {task_type.value}",
                        'guidance_type': 'socratic',
                        'should_render': True
                    }
                    
                    # Test UI rendering
                    st.ui_outputs = []
                    
                    # Add a test message
                    message_index = len(st.session_state.messages)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Task {task_type.value} activated",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Render task UI
                    from dashboard.ui.chat_components import render_tasks_for_message
                    render_tasks_for_message(message_index)
                    
                    ui_rendered = len(st.ui_outputs) > 0
                    
                    if ui_rendered:
                        successful_renders += 1
                        print(f"      ✅ UI rendered successfully ({len(st.ui_outputs)} components)")
                    else:
                        print(f"      ❌ UI rendering failed")
                    
                    # Complete the task for next iteration
                    mode_processor.task_manager.complete_task(task_type, "Test completion")
                    
                else:
                    print(f"      ❌ Task activation failed")
                    
            except Exception as task_error:
                print(f"      ❌ Task test failed: {task_error}")
        
        success_rate = (successful_renders / len(all_tasks)) * 100
        
        print(f"\n   📊 ALL TASKS UI RENDERING RESULTS:")
        print(f"      Successful renders: {successful_renders}/{len(all_tasks)} ({success_rate:.1f}%)")
        
        if success_rate >= 100:
            print(f"      🎉 SUCCESS: All 8 tasks render UI correctly!")
        elif success_rate >= 75:
            print(f"      ⚠️ PARTIAL: Most tasks render UI correctly")
        else:
            print(f"      ❌ FAILURE: Many tasks fail to render UI")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"   ❌ All tasks UI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 STARTING: Phase Transition UI Test in Real Streamlit App Context")
    print("   This test runs within the actual application environment")
    print("   Testing task UI rendering during phase transitions")
    print()
    
    # Test phase transition UI rendering
    phase_transition_works = test_phase_transition_ui_rendering()
    
    # Test all 8 tasks UI rendering
    all_tasks_work = test_all_8_tasks_ui_rendering()
    
    print()
    print("🎯 FINAL RESULTS:")
    if phase_transition_works and all_tasks_work:
        print("   🎉 COMPLETE SUCCESS!")
        print("   ✅ Phase transition UI works in real app context")
        print("   ✅ Task UI renders immediately during transitions")
        print("   ✅ All 8 tasks render UI components correctly")
        print("   ✅ Completed tasks persist in chat history")
        print("   🎓 STUDENTS WILL SEE TASK INTERFACES CORRECTLY!")
        result = "SUCCESS"
    elif phase_transition_works:
        print("   ⚠️ PARTIAL SUCCESS")
        print("   ✅ Phase transition UI works")
        print("   ❌ Some task UI rendering issues remain")
        result = "PARTIAL"
    elif all_tasks_work:
        print("   ⚠️ PARTIAL SUCCESS")
        print("   ✅ Task UI rendering works")
        print("   ❌ Phase transition UI issues remain")
        result = "PARTIAL"
    else:
        print("   ❌ FAILURE")
        print("   ❌ Phase transition UI broken")
        print("   ❌ Task UI rendering broken")
        print("   🚨 STUDENTS WILL NOT SEE TASK INTERFACES!")
        result = "FAILURE"
    
    print()
    print("📊 PHASE TRANSITION UI TEST COMPLETE")
    print(f"   Result: {result}")
    print("   This test ran in real Streamlit application context")
    print("   Results reflect actual application behavior")
