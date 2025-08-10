#!/usr/bin/env python3
"""
Test script for updated SocraticTutorAgent to verify:
1. It returns AgentResponse format
2. It preserves all original data for interaction_logger.py
3. It maintains backward compatibility
"""

import asyncio
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.socratic_tutor import SocraticTutorAgent
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import AgentResponse, ResponseType

async def test_socratic_tutor_update():
    """Test the updated SocraticTutorAgent"""
    
    print("🧪 Testing Updated SocraticTutorAgent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with accessible entrances, flexible meeting spaces, and a commercial kitchen for community events"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Add some user messages for conversation context
    state.messages.extend([
        {"role": "user", "content": "How do I design accessibility into my building?"},
        {"role": "user", "content": "I want to create spaces that everyone can use"}
    ])
    
    # Create mock analysis result
    analysis_result = {
        "agent": "analysis_agent",
        "domain": "architecture",
        "visual_analysis": {},
        "text_analysis": {"building_type": "community center"},
        "synthesis": {"cognitive_challenges": ["accessibility"], "learning_opportunities": ["universal design"]},
        "confidence_score": 0.7,
        "cognitive_flags": ["needs_accessibility_guidance"],
        "phase_analysis": {"phase": "ideation", "confidence": 0.6},
        "skill_assessment": {"detected_level": "intermediate", "confidence": 0.7}
    }
    
    # Create mock context classification
    context_classification = {
        "confidence_level": "medium",
        "understanding_level": "medium",
        "engagement_level": "high"
    }
    
    # Create agent
    agent = SocraticTutorAgent("architecture")
    
    # Test Socratic response generation
    result = await agent.generate_response(state, analysis_result, context_classification)
    
    print(f"\n📊 Test Results:")
    print(f"   Response type: {type(result)}")
    print(f"   Is AgentResponse: {isinstance(result, AgentResponse)}")
    print(f"   Response type: {result.response_type}")
    print(f"   Agent name: {result.agent_name}")
    print(f"   Response text: {result.response_text[:100]}...")
    print(f"   Cognitive flags count: {len(result.cognitive_flags)}")
    print(f"   Enhancement metrics: {result.enhancement_metrics.overall_cognitive_score:.2f}")
    
    # Test backward compatibility - check if original data is preserved
    original_data = result.metadata.get("original_response_result", {})
    print(f"\n🔍 Backward Compatibility Check:")
    print(f"   Original response result preserved: {bool(original_data)}")
    print(f"   Student analysis preserved: {bool(result.metadata.get('student_analysis'))}")
    print(f"   Conversation progression preserved: {bool(result.metadata.get('conversation_progression'))}")
    print(f"   Student insights preserved: {bool(result.metadata.get('student_insights'))}")
    print(f"   Response strategy preserved: {bool(result.metadata.get('response_strategy'))}")
    print(f"   Educational intent preserved: {bool(result.metadata.get('educational_intent'))}")
    print(f"   Analysis result preserved: {bool(result.metadata.get('analysis_result'))}")
    print(f"   Context classification preserved: {bool(result.metadata.get('context_classification'))}")
    print(f"   Cognitive flags preserved: {bool(result.metadata.get('cognitive_flags'))}")
    
    # Test interaction_logger compatibility
    print(f"\n📝 Interaction Logger Compatibility:")
    print(f"   Can extract agent name: {result.agent_name}")
    print(f"   Can extract response text: {bool(result.response_text)}")
    print(f"   Can extract cognitive flags: {len(result.cognitive_flags)}")
    print(f"   Can extract enhancement metrics: {result.enhancement_metrics.overall_cognitive_score > 0}")
    
    # Test that all required fields for interaction_logger are available
    required_fields = [
        "agent", "response_text", "response_type", "educational_intent", 
        "student_analysis", "conversation_progression", "cognitive_flags"
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
    asyncio.run(test_socratic_tutor_update()) 