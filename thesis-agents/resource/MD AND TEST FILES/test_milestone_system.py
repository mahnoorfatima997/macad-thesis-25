#!/usr/bin/env python3
"""
Test script for milestone-driven conversation system
"""

import asyncio
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from conversation_progression import ConversationProgressionManager, MilestoneType, ConversationPhase
from state_manager import ArchMentorState
from datetime import datetime

async def test_milestone_system():
    """Test the milestone-driven conversation system"""
    
    print("🧪 Testing Milestone-Driven Conversation System")
    print("=" * 50)
    
    # Initialize the progression manager
    progression_manager = ConversationProgressionManager("architecture")
    
    # Create a mock student state
    student_state = ArchMentorState(
        messages=[
            {"role": "user", "content": "I want to design a community center", "timestamp": datetime.now()},
            {"role": "assistant", "content": "Great! Let's explore your community center design. What specific aspects are you most interested in?", "timestamp": datetime.now()},
            {"role": "user", "content": "I'm thinking about the site analysis and how to organize the spaces", "timestamp": datetime.now()}
        ],
        current_design_brief="Design a community center"
    )
    
    # Test milestone guidance
    print("\n🎯 Testing Milestone Guidance...")
    milestone_guidance = progression_manager.get_milestone_driven_agent_guidance(
        "I'm thinking about the site analysis and how to organize the spaces", 
        student_state
    )
    
    current_milestone = milestone_guidance.get("current_milestone")
    agent_focus = milestone_guidance.get("agent_focus")
    agent_guidance = milestone_guidance.get("agent_guidance", {})
    
    print(f"✅ Current Milestone: {current_milestone.milestone_type.value if current_milestone else 'None'}")
    print(f"✅ Agent Focus: {agent_focus}")
    print(f"✅ Milestone Progress: {milestone_guidance.get('milestone_progress', 0)}%")
    print(f"✅ Phase: {milestone_guidance.get('phase', 'unknown')}")
    print(f"✅ Agent Guidance: {agent_guidance.get('guidance', 'No guidance')}")
    
    # Test milestone completion assessment
    print("\n🎯 Testing Milestone Completion Assessment...")
    completion_assessment = progression_manager.assess_milestone_completion(
        "I understand the site analysis concepts and want to apply them to my design",
        "Great understanding! Let's explore how to apply these concepts.",
        student_state
    )
    
    print(f"✅ Milestone Complete: {completion_assessment.get('milestone_complete', False)}")
    print(f"✅ Next Milestone: {completion_assessment.get('next_milestone', 'None')}")
    print(f"✅ Guidance: {completion_assessment.get('guidance', 'No guidance')}")
    
    # Test milestone creation
    print("\n🎯 Testing Milestone Creation...")
    new_milestone = progression_manager._create_milestone(
        MilestoneType.KNOWLEDGE_ACQUISITION,
        "I want to learn more about spatial organization",
        student_state
    )
    
    print(f"✅ Created Milestone: {new_milestone.milestone_type.value}")
    print(f"✅ Phase: {new_milestone.phase.value}")
    print(f"✅ Progress: {new_milestone.progress_percentage}%")
    print(f"✅ Required Actions: {new_milestone.required_actions}")
    print(f"✅ Success Criteria: {new_milestone.success_criteria}")
    
    # Test progression sequence
    print("\n🎯 Testing Progression Sequence...")
    for phase in ConversationPhase:
        sequence = progression_manager.progression_sequence.get(phase, [])
        print(f"✅ {phase.value.title()} Phase: {[m.value for m in sequence]}")
    
    print("\n🎉 Milestone System Test Completed Successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_milestone_system())
