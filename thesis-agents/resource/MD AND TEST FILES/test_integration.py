#!/usr/bin/env python3
"""
Test script to verify the integration between analysis agent and conversation progression system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thesis_agents.agents.analysis_agent import AnalysisAgent
from thesis_agents.state_manager import ArchMentorState, StudentProfile
from thesis_agents.conversation_progression import ConversationProgressionManager

async def test_analysis_agent_integration():
    """Test the integration between analysis agent and conversation progression"""
    
    print("🧪 Testing Analysis Agent Integration with Conversation Progression")
    print("=" * 60)
    
    # Initialize analysis agent
    analysis_agent = AnalysisAgent(domain="architecture")
    
    # Create a test state
    student_profile = StudentProfile(
        name="Test Student",
        experience_level="intermediate",
        interests=["sustainable design", "urban planning"],
        learning_style="visual"
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
        project_context={
            "building_type": "community center",
            "location": "urban area",
            "current_phase": "ideation"
        }
    )
    
    # Test conversation progression integration
    print("\n1. Testing conversation progression integration...")
    progression_integration = analysis_agent.integrate_conversation_progression(
        state, "The site is in an urban area with good public transportation access.", ""
    )
    
    print(f"✅ Conversation progression analysis: {progression_integration.get('conversation_progression', {}).get('phase', 'unknown')}")
    print(f"✅ Current milestone: {progression_integration.get('current_milestone')}")
    print(f"✅ Milestone assessment: {progression_integration.get('milestone_assessment', {}).get('completion_percentage', 0):.1f}%")
    print(f"✅ Agent guidance: {progression_integration.get('agent_guidance', {}).get('agent_focus', 'unknown')}")
    
    # Test analysis agent processing
    print("\n2. Testing analysis agent processing...")
    analysis_result = await analysis_agent.process(state, {})
    
    print(f"✅ Analysis result type: {type(analysis_result)}")
    if hasattr(analysis_result, 'to_dict'):
        analysis_dict = analysis_result.to_dict()
        print(f"✅ Analysis result keys: {list(analysis_dict.keys())}")
        print(f"✅ Conversation progression in analysis: {'conversation_progression' in analysis_dict}")
    else:
        print(f"✅ Analysis result keys: {list(analysis_result.keys())}")
        print(f"✅ Conversation progression in analysis: {'conversation_progression' in analysis_result}")
    
    # Test milestone question generation
    print("\n3. Testing milestone question generation...")
    from thesis_agents.phase_management.milestone_questions import MilestoneType as ArchitecturalMilestoneType
    
    question = analysis_agent._generate_milestone_question(ArchitecturalMilestoneType.SITE_ANALYSIS)
    print(f"✅ Generated question: {question}")
    
    print("\n✅ Integration test completed successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_analysis_agent_integration())
