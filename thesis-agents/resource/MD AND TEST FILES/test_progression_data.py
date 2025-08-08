#!/usr/bin/env python3
"""
Test script to verify conversation progression data flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

sys.path.append('thesis-agents')
from conversation_progression import ConversationProgressionManager, ConversationPhase
from state_manager import ArchMentorState, StudentProfile

def test_conversation_progression():
    """Test the conversation progression data generation"""
    
    print("🧪 Testing Conversation Progression Data Flow")
    print("=" * 50)
    
    # Initialize progression manager
    progression_manager = ConversationProgressionManager(domain="architecture")
    
    # Create a test state
    student_profile = StudentProfile(
        skill_level="intermediate",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.7,
        knowledge_gaps=["site analysis", "sustainability principles"],
        strengths=["design thinking", "spatial awareness"]
    )
    
    state = ArchMentorState(
        student_profile=student_profile,
        messages=[
            {
                "role": "user",
                "content": "I'm working on a community center design and need help with site analysis."
            },
            {
                "role": "assistant", 
                "content": "Great! Let's start by analyzing your site. What are the key characteristics of your location?"
            },
            {
                "role": "user",
                "content": "The site is in an urban area with good public transportation access."
            }
        ],
        current_design_brief="Design a sustainable community center for an urban neighborhood"
    )
    
    # Test first message analysis
    print("\n1. Testing first message analysis...")
    first_analysis = progression_manager.analyze_first_message(
        "I'm working on a community center design and need help with site analysis.", 
        state
    )
    
    print(f"✅ First message analysis:")
    print(f"   - Conversation phase: {first_analysis.get('conversation_phase', 'unknown')}")
    print(f"   - Current phase: {first_analysis.get('current_phase', 'unknown')}")
    print(f"   - User profile: {first_analysis.get('user_profile', {}).get('knowledge_level', 'unknown')}")
    
    # Test conversation progression
    print("\n2. Testing conversation progression...")
    progression_analysis = progression_manager.progress_conversation(
        "The site is in an urban area with good public transportation access.",
        "Great! Let's start by analyzing your site. What are the key characteristics of your location?",
        state
    )
    
    print(f"✅ Conversation progression:")
    print(f"   - Current phase: {progression_analysis.get('current_phase', 'unknown')}")
    print(f"   - Phase transition: {progression_analysis.get('phase_transition', False)}")
    print(f"   - New milestone: {progression_analysis.get('new_milestone')}")
    
    # Test conversation summary
    conversation_summary = progression_analysis.get('conversation_summary', {})
    print(f"   - Conversation summary keys: {list(conversation_summary.keys())}")
    
    # Test learning progress
    learning_progress = conversation_summary.get('learning_progress', {})
    print(f"   - Learning progress: {learning_progress}")
    
    # Test milestone guidance
    print("\n3. Testing milestone guidance...")
    milestone_guidance = progression_manager.get_milestone_driven_agent_guidance(
        "The site is in an urban area with good public transportation access.",
        state
    )
    
    print(f"✅ Milestone guidance:")
    print(f"   - Current milestone: {milestone_guidance.get('current_milestone')}")
    print(f"   - Agent focus: {milestone_guidance.get('agent_focus', 'unknown')}")
    print(f"   - Milestone progress: {milestone_guidance.get('milestone_progress', 0)}%")
    
    # Test milestone assessment
    print("\n4. Testing milestone assessment...")
    milestone_assessment = progression_manager.assess_milestone_completion(
        "The site is in an urban area with good public transportation access.",
        "Great! Let's start by analyzing your site. What are the key characteristics of your location?",
        state
    )
    
    print(f"✅ Milestone assessment:")
    print(f"   - Milestone complete: {milestone_assessment.get('milestone_complete', False)}")
    print(f"   - Completion percentage: {milestone_assessment.get('completion_percentage', 0)}%")
    print(f"   - Phase transition: {milestone_assessment.get('phase_transition', False)}")
    
    # Test current milestone
    current_milestone = progression_manager.get_current_milestone()
    print(f"\n5. Current milestone:")
    if current_milestone:
        print(f"   - Milestone type: {current_milestone.milestone_type.value}")
        print(f"   - Phase: {current_milestone.phase.value}")
        print(f"   - Progress percentage: {current_milestone.progress_percentage}%")
        print(f"   - Required actions: {current_milestone.required_actions}")
    else:
        print("   - No current milestone")
    
    print("\n✅ Conversation progression test completed!")

if __name__ == "__main__":
    test_conversation_progression()
