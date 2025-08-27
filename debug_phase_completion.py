#!/usr/bin/env python3
"""
DEBUG: Phase Completion System Integration
Diagnose why dynamic tasks are not triggering during conversations
"""

import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

from phase_progression_system import PhaseProgressionSystem
from dashboard.processors.dynamic_task_manager import DynamicTaskManager, TaskType


def test_phase_progression_integration():
    """Test the complete phase progression to task triggering flow"""
    print("🔍 DEBUGGING: Phase Progression System Integration")
    print("=" * 60)
    
    # Initialize systems
    phase_system = PhaseProgressionSystem()
    task_manager = DynamicTaskManager()
    
    # Create a session
    session_id = f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n📋 Creating session: {session_id}")
    
    session = phase_system.start_session(session_id)
    print(f"✅ Session created: {session.session_id}")
    print(f"   Current phase: {session.current_phase.value}")
    print(f"   Phase progress keys: {list(session.phase_progress.keys())}")
    
    # Check initial phase progress
    current_progress = session.phase_progress.get(session.current_phase)
    if current_progress:
        print(f"   Initial completion: {current_progress.completion_percent:.1f}%")
    else:
        print("   ❌ No progress found for current phase")
        return
    
    # Simulate user messages to build up phase completion
    test_messages = [
        "I'm working on a community center design project",
        "I want to create a space that brings people together through adaptive reuse",
        "The concept focuses on transforming an old warehouse into a vibrant community hub",
        "I'm thinking about how different spaces can support various community activities",
        "The spatial program should include meeting rooms, recreational areas, and flexible spaces"
    ]
    
    print(f"\n📝 Processing {len(test_messages)} messages to build phase completion:")
    
    for i, message in enumerate(test_messages):
        print(f"\n   Message {i+1}: {message[:50]}...")
        
        # Process message through phase system
        result = phase_system.process_user_message(session_id, message)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            continue
            
        # Get updated session state
        session = phase_system.sessions.get(session_id)
        if not session:
            print(f"   ❌ Session not found")
            continue
            
        current_progress = session.phase_progress.get(session.current_phase)
        if current_progress:
            completion_percent = current_progress.completion_percent
            print(f"   📊 Phase: {session.current_phase.value}")
            print(f"   📈 Completion: {completion_percent:.1f}%")
            
            # Test task triggering at this completion level
            conversation_history = [{"role": "user", "content": msg} for msg in test_messages[:i+1]]
            
            triggered_task = task_manager.check_task_triggers(
                user_input=message,
                conversation_history=conversation_history,
                current_phase=session.current_phase.value.lower(),
                test_group="MENTOR",
                image_uploaded=False,
                phase_completion_percent=completion_percent
            )
            
            if triggered_task:
                print(f"   🎯 TASK TRIGGERED: {triggered_task.value}")
                # Complete the task to allow next ones to trigger
                task = task_manager.activate_task(
                    task_type=triggered_task,
                    test_group="MENTOR",
                    current_phase=session.current_phase.value.lower(),
                    trigger_reason=f"Debug test at {completion_percent:.1f}%",
                    phase_completion_percent=completion_percent
                )
                task_manager.complete_task(triggered_task, "Debug completion")
            else:
                print(f"   ⚪ No task triggered at {completion_percent:.1f}%")
        else:
            print(f"   ❌ No progress found for phase: {session.current_phase.value}")
    
    print(f"\n📊 Final Session State:")
    session = phase_system.sessions.get(session_id)
    if session:
        print(f"   Current phase: {session.current_phase.value}")
        for phase, progress in session.phase_progress.items():
            print(f"   {phase.value}: {progress.completion_percent:.1f}% complete")
    
    print(f"\n🎯 Task History:")
    for task in task_manager.task_history:
        print(f"   {task.task_type.value}: {task.trigger_reason}")


def test_manual_phase_completion_triggering():
    """Test task triggering with manually set phase completion percentages"""
    print("\n🔍 DEBUGGING: Manual Phase Completion Triggering")
    print("=" * 60)
    
    task_manager = DynamicTaskManager()
    
    conversation_history = [
        {"role": "user", "content": "I'm working on a community center design"},
        {"role": "assistant", "content": "Great! Tell me about your concept."},
        {"role": "user", "content": "I want to create a space for community activities"}
    ]
    
    # Test each task at its expected trigger percentage
    test_cases = [
        (TaskType.ARCHITECTURAL_CONCEPT, "ideation", 5.0, "I want to create a community space through adaptive reuse"),
        (TaskType.SPATIAL_PROGRAM, "ideation", 25.0, "Now I need to develop spatial relationships and circulation patterns"),
        (TaskType.VISUAL_ANALYSIS_2D, "visualization", 10.0, "Here's my floor plan sketch"),
        (TaskType.ENVIRONMENTAL_CONTEXTUAL, "visualization", 40.0, "I need to integrate environmental factors and site context"),
        (TaskType.SPATIAL_ANALYSIS_3D, "materialization", 15.0, "Let me develop 3D spatial organization and material systems"),
        (TaskType.REALIZATION_IMPLEMENTATION, "materialization", 50.0, "Now I need construction strategy and implementation"),
        (TaskType.DESIGN_EVOLUTION, "materialization", 80.0, "I want to reflect on design evolution and development progress"),
        (TaskType.KNOWLEDGE_TRANSFER, "materialization", 90.0, "Let me think about sharing these design insights and knowledge")
    ]
    
    print(f"\n📋 Testing {len(test_cases)} tasks with manual completion percentages:")
    
    for task_type, phase, completion, user_input in test_cases:
        print(f"\n   {task_type.value.replace('_', ' ').title()}:")
        print(f"      Phase: {phase} at {completion}%")
        print(f"      Input: {user_input[:50]}...")
        
        # Special handling for image upload task
        image_uploaded = (task_type == TaskType.VISUAL_ANALYSIS_2D)
        image_analysis = {"image_type": "floor_plan"} if image_uploaded else None
        
        triggered_task = task_manager.check_task_triggers(
            user_input=user_input,
            conversation_history=conversation_history,
            current_phase=phase,
            test_group="MENTOR",
            image_uploaded=image_uploaded,
            image_analysis=image_analysis,
            phase_completion_percent=completion
        )
        
        if triggered_task == task_type:
            print(f"      ✅ TRIGGERED correctly")
            # Complete task for next test
            task = task_manager.activate_task(
                task_type=triggered_task,
                test_group="MENTOR",
                current_phase=phase,
                trigger_reason=f"Manual test at {completion}%",
                phase_completion_percent=completion
            )
            task_manager.complete_task(triggered_task, "Manual completion")
        elif triggered_task:
            print(f"      ❌ WRONG TASK: {triggered_task.value} (expected {task_type.value})")
        else:
            print(f"      ❌ NO TASK triggered")


def test_phase_system_completion_calculation():
    """Test how the phase system calculates completion percentages"""
    print("\n🔍 DEBUGGING: Phase System Completion Calculation")
    print("=" * 60)
    
    phase_system = PhaseProgressionSystem()
    session_id = f"completion_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    session = phase_system.start_session(session_id)
    print(f"\n📋 Testing completion calculation for session: {session_id}")
    
    # Test messages that should increase completion
    test_messages = [
        "I'm designing a community center",
        "The concept is adaptive reuse of a warehouse",
        "I want to create flexible spaces for community activities",
        "The spatial program includes meeting rooms and recreational areas",
        "I'm considering circulation patterns and adjacency requirements"
    ]
    
    print(f"\n📝 Processing messages and tracking completion:")
    
    for i, message in enumerate(test_messages):
        print(f"\n   Message {i+1}: {message}")
        
        # Process message
        result = phase_system.process_user_message(session_id, message)
        
        # Get completion percentage
        session = phase_system.sessions.get(session_id)
        if session:
            current_progress = session.phase_progress.get(session.current_phase)
            if current_progress:
                print(f"      Completion: {current_progress.completion_percent:.1f}%")
                print(f"      Completed steps: {len(current_progress.completed_steps)}")
                print(f"      Average score: {current_progress.average_score:.2f}")
            else:
                print(f"      ❌ No progress found")
        else:
            print(f"      ❌ Session not found")


def main():
    """Run all diagnostic tests"""
    print("🚀 PHASE COMPLETION SYSTEM DIAGNOSTICS")
    print("=" * 80)
    
    try:
        test_phase_progression_integration()
        test_manual_phase_completion_triggering()
        test_phase_system_completion_calculation()
        
        print("\n" + "=" * 80)
        print("🎉 DIAGNOSTICS COMPLETE!")
        print("Check the output above to identify integration issues.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
