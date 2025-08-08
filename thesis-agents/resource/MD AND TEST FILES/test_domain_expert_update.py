#!/usr/bin/env python3
"""
Test script for updated DomainExpertAgent to verify:
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

from agents.domain_expert import DomainExpertAgent
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import AgentResponse, ResponseType

async def test_domain_expert_update():
    """Test the updated DomainExpertAgent"""
    
    print("🧪 Testing Updated DomainExpertAgent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with accessible entrances, flexible meeting spaces, and a commercial kitchen for community events"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Add some user messages for conversation context
    state.messages.extend([
        {"role": "user", "content": "Can you show me examples of sustainable materials for my community center?"},
        {"role": "user", "content": "I want to use environmentally friendly options"}
    ])
    
    # Create mock analysis result
    analysis_result = {
        "agent": "analysis_agent",
        "domain": "architecture",
        "visual_analysis": {},
        "text_analysis": {"building_type": "community center"},
        "synthesis": {"cognitive_challenges": ["sustainability"], "learning_opportunities": ["material selection"]},
        "confidence_score": 0.7,
        "cognitive_flags": ["needs_sustainability_guidance"],
        "phase_analysis": {"phase": "ideation", "confidence": 0.6},
        "skill_assessment": {"detected_level": "intermediate", "confidence": 0.7}
    }
    
    # Create agent
    agent = DomainExpertAgent("architecture")
    
    # Test knowledge provision
    result = await agent.provide_knowledge(state, analysis_result, "sustainability_materials")
    
    print(f"\n📊 Test Results:")
    print(f"   Response type: {type(result)}")
    print(f"   Is AgentResponse: {isinstance(result, AgentResponse)}")
    print(f"   Response type: {result.response_type}")
    print(f"   Agent name: {result.agent_name}")
    print(f"   Response text: {result.response_text[:100]}...")
    print(f"   Cognitive flags count: {len(result.cognitive_flags)}")
    print(f"   Enhancement metrics: {result.enhancement_metrics.overall_cognitive_score:.2f}")
    print(f"   Sources used: {len(result.sources_used)}")
    
    # Test backward compatibility - check if original data is preserved
    original_data = result.metadata.get("original_response_result", {})
    print(f"\n🔍 Backward Compatibility Check:")
    print(f"   Original response result preserved: {bool(original_data)}")
    print(f"   Knowledge gap addressed preserved: {bool(result.metadata.get('knowledge_gap_addressed'))}")
    print(f"   Building type preserved: {bool(result.metadata.get('building_type'))}")
    print(f"   User input addressed preserved: {bool(result.metadata.get('user_input_addressed'))}")
    print(f"   Knowledge pattern preserved: {bool(result.metadata.get('knowledge_pattern'))}")
    print(f"   Analysis result preserved: {bool(result.metadata.get('analysis_result'))}")
    print(f"   Gap type preserved: {bool(result.metadata.get('gap_type'))}")
    print(f"   Cognitive flags preserved: {bool(result.metadata.get('cognitive_flags'))}")
    
    # Test interaction_logger compatibility
    print(f"\n📝 Interaction Logger Compatibility:")
    print(f"   Can extract agent name: {result.agent_name}")
    print(f"   Can extract response text: {bool(result.response_text)}")
    print(f"   Can extract cognitive flags: {len(result.cognitive_flags)}")
    print(f"   Can extract enhancement metrics: {result.enhancement_metrics.overall_cognitive_score > 0}")
    print(f"   Can extract sources: {len(result.sources_used)}")
    
    # Test that all required fields for interaction_logger are available
    required_fields = [
        "agent", "response_text", "response_type", "knowledge_gap_addressed", 
        "building_type", "user_input_addressed", "knowledge_pattern", "cognitive_flags"
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
    asyncio.run(test_domain_expert_update()) 