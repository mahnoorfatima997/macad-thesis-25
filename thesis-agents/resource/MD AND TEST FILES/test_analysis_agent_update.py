#!/usr/bin/env python3
"""
Test script for updated AnalysisAgent to verify:
1. It returns AgentResponse format
2. It preserves all original data for interaction_logger.py
3. It maintains backward compatibility
"""

import asyncio
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.analysis_agent import AnalysisAgent
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import AgentResponse, ResponseType

async def test_analysis_agent_update():
    """Test the updated AnalysisAgent"""
    
    print("🧪 Testing Updated AnalysisAgent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with accessible entrances, flexible meeting spaces, and a commercial kitchen for community events"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Add some user messages for skill detection
    state.messages.extend([
        {"role": "user", "content": "How do I design accessibility into my building?"},
        {"role": "user", "content": "I want to create spaces that everyone can use"}
    ])
    
    # Create agent
    agent = AnalysisAgent("architecture")
    
    # Test analysis
    result = await agent.process(state)
    
    print(f"\n📊 Test Results:")
    print(f"   Response type: {type(result)}")
    print(f"   Is AgentResponse: {isinstance(result, AgentResponse)}")
    print(f"   Response type: {result.response_type}")
    print(f"   Agent name: {result.agent_name}")
    print(f"   Response text: {result.response_text[:100]}...")
    print(f"   Cognitive flags count: {len(result.cognitive_flags)}")
    print(f"   Enhancement metrics: {result.enhancement_metrics.overall_cognitive_score:.2f}")
    
    # Test backward compatibility - check if original data is preserved
    original_data = result.metadata.get("original_analysis_result", {})
    print(f"\n🔍 Backward Compatibility Check:")
    print(f"   Original analysis result preserved: {bool(original_data)}")
    print(f"   Phase analysis preserved: {bool(result.metadata.get('phase_analysis'))}")
    print(f"   Skill assessment preserved: {bool(result.metadata.get('skill_assessment'))}")
    print(f"   Visual analysis preserved: {bool(result.metadata.get('visual_analysis'))}")
    print(f"   Text analysis preserved: {bool(result.metadata.get('text_analysis'))}")
    print(f"   Synthesis preserved: {bool(result.metadata.get('synthesis'))}")
    print(f"   Cognitive flags preserved: {bool(result.metadata.get('cognitive_flags'))}")
    
    # Test interaction_logger compatibility
    print(f"\n📝 Interaction Logger Compatibility:")
    print(f"   Can extract agent name: {result.agent_name}")
    print(f"   Can extract response text: {bool(result.response_text)}")
    print(f"   Can extract cognitive flags: {len(result.cognitive_flags)}")
    print(f"   Can extract enhancement metrics: {result.enhancement_metrics.overall_cognitive_score > 0}")
    
    # Test that all required fields for interaction_logger are available
    required_fields = [
        "agent", "domain", "visual_analysis", "text_analysis", 
        "synthesis", "confidence_score", "cognitive_flags", "phase_analysis", "skill_assessment"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in original_data:
            missing_fields.append(field)
    
    print(f"   Missing fields for interaction_logger: {missing_fields}")
    
    if not missing_fields:
        print("✅ All required fields preserved for interaction_logger")
    else:
        print("❌ Some required fields missing")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_analysis_agent_update()) 