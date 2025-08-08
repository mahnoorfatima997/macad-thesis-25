#!/usr/bin/env python3
"""
Test script to verify routing is working correctly in the actual app context
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thesis-agents'))

from state_manager import ArchMentorState, StudentProfile
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
import asyncio

async def test_routing_in_app():
    """Test routing with actual app components"""
    
    print("🔍 Testing Routing in App Context")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator("architecture")
    
    # Create test state
    student_state = ArchMentorState()
    student_state.student_profile = StudentProfile(
        skill_level="intermediate",
        learning_style="visual"
    )
    student_state.current_design_brief = "Design a sustainable community center"
    
    # Add the design brief as the first message
    student_state.messages = [
        {
            "role": "brief",
            "content": "Design a sustainable community center"
        }
    ]
    
    # Test different user inputs
    test_inputs = [
        "What are the key principles of sustainable architecture?",
        "Can you design this building for me?",
        "I'm struggling with the layout of my community center",
        "How do I implement passive solar design?",
        "Hello, I want to design a building"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n📋 Test {i}: {user_input}")
        
        # Add the user message to the state
        student_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Process the input
        result = await orchestrator.process_student_input(student_state)
        
        # Extract routing information
        routing_path = result.get("routing_path", "unknown")
        classification = result.get("student_classification", {})
        interaction_type = classification.get("interaction_type", "unknown")
        
        print(f"   🎯 Routing Path: {routing_path}")
        print(f"   📝 Interaction Type: {interaction_type}")
        
        # Check if it's balanced_guidance
        if routing_path == "balanced_guidance":
            print("   ⚠️ WARNING: Defaulting to balanced_guidance!")
        else:
            print("   ✅ Non-default route selected")
        
        print("-" * 50)
        
        # Remove the user message for the next test to simulate fresh conversation
        student_state.messages.pop()

if __name__ == "__main__":
    asyncio.run(test_routing_in_app()) 