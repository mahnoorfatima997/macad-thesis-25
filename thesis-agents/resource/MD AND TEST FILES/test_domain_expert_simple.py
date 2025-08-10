#!/usr/bin/env python3
"""
Simple test script for updated DomainExpertAgent to verify structure without API calls
"""

import asyncio
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from agents.domain_expert import DomainExpertAgent
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import AgentResponse, ResponseType

async def test_domain_expert_structure():
    """Test the DomainExpertAgent structure without API calls"""
    
    print("🧪 Testing DomainExpertAgent Structure...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people"
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Create agent
    agent = DomainExpertAgent("architecture")
    
    print(f"✅ Agent created successfully: {agent.name}")
    print(f"✅ Agent domain: {agent.domain}")
    
    # Test that the provide_knowledge method exists and has correct signature
    import inspect
    sig = inspect.signature(agent.provide_knowledge)
    print(f"✅ Method signature: {sig}")
    
    # Test that return type annotation is AgentResponse
    return_type = sig.return_annotation
    print(f"✅ Return type: {return_type}")
    
    if return_type == AgentResponse:
        print("✅ Return type is correctly AgentResponse")
    else:
        print("❌ Return type should be AgentResponse")
    
    # Test that helper methods exist
    helper_methods = [
        "_convert_to_agent_response",
        "_calculate_enhancement_metrics", 
        "_extract_cognitive_flags",
        "_convert_cognitive_flags"
    ]
    
    for method in helper_methods:
        if hasattr(agent, method):
            print(f"✅ Helper method exists: {method}")
        else:
            print(f"❌ Missing helper method: {method}")
    
    print("\n✅ DomainExpertAgent structure test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_domain_expert_structure()) 