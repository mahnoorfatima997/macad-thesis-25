#!/usr/bin/env python3
"""
Test script to verify conversation progression data flow and UI metrics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('thesis-agents')

from conversation_progression import ConversationProgressionManager, ConversationPhase
from state_manager import ArchMentorState, StudentProfile

def test_conversation_progression_data_flow():
    """Test the conversation progression data generation and UI display"""
    
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
    
    # Test conversation progression
    print("\n1. Testing conversation progression...")
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
    
    # Test project context
    project_context = conversation_summary.get('project_context', {})
    print(f"   - Project context: {project_context}")
    
    # Test challenges and opportunities
    challenges = conversation_summary.get('challenges', [])
    opportunities = conversation_summary.get('opportunities', [])
    print(f"   - Challenges: {challenges}")
    print(f"   - Opportunities: {opportunities}")
    
    # Test UI calculation function
    print("\n2. Testing UI calculation function...")
    
    # Import the UI calculation function
    import mega_architectural_mentor
    phase_progress = mega_architectural_mentor._calculate_phase_progress(progression_analysis)
    
    print(f"✅ UI Phase Progress Calculation:")
    print(f"   - Calculated progress: {phase_progress}%")
    print(f"   - Current phase: {progression_analysis.get('current_phase', 'unknown')}")
    
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
    
    # Test the complete data structure that would be passed to UI
    print("\n4. Testing complete data structure...")
    
    # Simulate the orchestrator result structure
    orchestrator_result = {
        "response": "Test response",
        "metadata": {},
        "routing_path": "test_path",
        "classification": {},
        "conversation_progression": progression_analysis,
        "milestone_guidance": milestone_guidance
    }
    
    print(f"✅ Orchestrator result structure:")
    print(f"   - Has conversation_progression: {'conversation_progression' in orchestrator_result}")
    print(f"   - Has milestone_guidance: {'milestone_guidance' in orchestrator_result}")
    print(f"   - Conversation progression keys: {list(orchestrator_result['conversation_progression'].keys())}")
    
    # Test UI data extraction
    print("\n5. Testing UI data extraction...")
    
    # Simulate how the UI extracts data
    conversation_progression = orchestrator_result.get('conversation_progression', {})
    current_phase = conversation_progression.get('current_phase', 'unknown')
    conversation_summary = conversation_progression.get('conversation_summary', {})
    project_context = conversation_summary.get('project_context', {})
    challenges = conversation_summary.get('challenges', [])
    opportunities = conversation_summary.get('opportunities', [])
    
    print(f"✅ UI Data Extraction:")
    print(f"   - Current phase: {current_phase}")
    print(f"   - Project context: {project_context}")
    print(f"   - Challenges count: {len(challenges)}")
    print(f"   - Opportunities count: {len(opportunities)}")
    print(f"   - Phase progress: {phase_progress}%")
    
    print("\n✅ Conversation progression test completed!")

if __name__ == "__main__":
    test_conversation_progression_data_flow()
