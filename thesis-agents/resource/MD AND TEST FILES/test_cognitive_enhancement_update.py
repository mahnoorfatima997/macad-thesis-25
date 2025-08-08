#!/usr/bin/env python3
"""
Test script for updated CognitiveEnhancementAgent to verify:
1. It returns AgentResponse format
2. It preserves all original data for interaction_logger.py
3. It maintains backward compatibility
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the thesis-agents directory to the path
thesis_agents_path = os.path.join(os.path.dirname(__file__), 'thesis-agents')
sys.path.append(thesis_agents_path)

# Load .env file from root directory
load_dotenv('.env')

from agents.cognitive_enhancement import CognitiveEnhancementAgent
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import AgentResponse, ResponseType

async def test_cognitive_enhancement_update():
    """Test the updated CognitiveEnhancementAgent"""
    
    print("🧪 Testing Updated CognitiveEnhancementAgent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with accessible entrances, flexible meeting spaces, and a commercial kitchen for community events"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Add some user messages for conversation context
    state.messages.extend([
        {"role": "user", "content": "Can you give me the answer to this design problem?"},
        {"role": "user", "content": "I need the solution right away"}
    ])
    
    # Create mock analysis result
    analysis_result = {
        "agent": "analysis_agent",
        "domain": "architecture",
        "visual_analysis": {},
        "text_analysis": {"building_type": "community center"},
        "synthesis": {"cognitive_challenges": ["cognitive_offloading"], "learning_opportunities": ["deep_thinking"]},
        "confidence_score": 0.7,
        "cognitive_flags": ["cognitive_offloading_detected"],
        "phase_analysis": {"phase": "ideation", "confidence": 0.6},
        "skill_assessment": {"detected_level": "intermediate", "confidence": 0.7}
    }
    
    # Create mock context classification
    context_classification = {
        "confidence_level": "overconfident",
        "understanding_level": "low",
        "engagement_level": "low",
        "interaction_type": "example_request"
    }
    
    # Create mock routing decision
    routing_decision = {
        "selected_agent": "cognitive_enhancement",
        "reason": "cognitive_offloading_detected"
    }
    
    # Create agent
    agent = CognitiveEnhancementAgent("architecture")
    
    # Test cognitive enhancement
    result = await agent.provide_challenge(state, context_classification, analysis_result, routing_decision)
    
    print(f"\n📊 Test Results:")
    print(f"   Response type: {type(result)}")
    print(f"   Is AgentResponse: {isinstance(result, AgentResponse)}")
    print(f"   Response type: {result.response_type}")
    print(f"   Agent name: {result.agent_name}")
    print(f"   Response text: {result.response_text[:100]}...")
    print(f"   Cognitive flags count: {len(result.cognitive_flags)}")
    print(f"   Enhancement metrics: {result.enhancement_metrics.overall_cognitive_score:.2f}")
    
    # Test backward compatibility - check if original data is preserved
    original_data = result.metadata.get("original_challenge_result", {})
    print(f"\n🔍 Backward Compatibility Check:")
    print(f"   Original challenge result preserved: {bool(original_data)}")
    print(f"   Cognitive state preserved: {bool(result.metadata.get('cognitive_state'))}")
    print(f"   Scientific metrics preserved: {bool(result.metadata.get('scientific_metrics'))}")
    print(f"   Enhancement strategy preserved: {bool(result.metadata.get('enhancement_strategy'))}")
    print(f"   Context used preserved: {bool(result.metadata.get('context_used'))}")
    print(f"   Pedagogical intent preserved: {bool(result.metadata.get('pedagogical_intent'))}")
    print(f"   Cognitive summary preserved: {bool(result.metadata.get('cognitive_summary'))}")
    print(f"   Offloading detection preserved: {bool(result.metadata.get('offloading_detection'))}")
    print(f"   Analysis result preserved: {bool(result.metadata.get('analysis_result'))}")
    print(f"   Routing decision preserved: {bool(result.metadata.get('routing_decision'))}")
    print(f"   Cognitive flags preserved: {bool(result.metadata.get('cognitive_flags'))}")
    
    # Test interaction_logger compatibility
    print(f"\n📝 Interaction Logger Compatibility:")
    print(f"   Can extract agent name: {result.agent_name}")
    print(f"   Can extract response text: {bool(result.response_text)}")
    print(f"   Can extract cognitive flags: {len(result.cognitive_flags)}")
    print(f"   Can extract enhancement metrics: {result.enhancement_metrics.overall_cognitive_score > 0}")
    
    # Test that all required fields for interaction_logger are available
    required_fields = [
        "agent", "response_text", "cognitive_state", "scientific_metrics", 
        "enhancement_strategy", "pedagogical_intent", "cognitive_flags"
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
    asyncio.run(test_cognitive_enhancement_update()) 