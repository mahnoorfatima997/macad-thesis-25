#!/usr/bin/env python3
"""
Test script to debug ongoing conversation routing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thesis-agents'))

from state_manager import ArchMentorState, StudentProfile
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
import asyncio

async def test_ongoing_routing():
    """Test ongoing conversation routing"""
    
    print("🔍 Testing Ongoing Conversation Routing")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator("architecture")
    
    # Create test state with existing conversation
    student_state = ArchMentorState()
    student_state.student_profile = StudentProfile(
        skill_level="intermediate",
        learning_style="visual"
    )
    student_state.current_design_brief = "Design a sustainable community center"
    
    # Add existing conversation
    student_state.messages = [
        {
            "role": "brief",
            "content": "Design a sustainable community center"
        },
        {
            "role": "user",
            "content": "Hello, I want to design a building"
        },
        {
            "role": "assistant",
            "content": "Hello there! I'm thrilled to see your interest in the functional aspect of architecture..."
        }
    ]
    
    # Test different ongoing conversation inputs
    test_inputs = [
        {
            "input": "I'm confused about the layout",
            "expected_type": "confusion_expression"
        },
        {
            "input": "Can you design this for me?",
            "expected_type": "direct_answer_request"
        },
        {
            "input": "What are sustainable materials?",
            "expected_type": "knowledge_request"
        },
        {
            "input": "How do I implement this?",
            "expected_type": "implementation_request"
        }
    ]
    
    for i, test_case in enumerate(test_inputs, 1):
        print(f"\n📋 Test {i}: {test_case['input']}")
        print(f"   Expected Type: {test_case['expected_type']}")
        
        # Add the user message to the state
        student_state.messages.append({
            "role": "user",
            "content": test_case['input']
        })
        
        # Process the input
        result = await orchestrator.process_student_input(student_state)
        
        # Extract routing information
        routing_path = result.get("routing_path", "unknown")
        classification = result.get("student_classification", {})
        interaction_type = classification.get("interaction_type", "unknown")
        
        print(f"   🎯 Routing Path: {routing_path}")
        print(f"   📝 Interaction Type: {interaction_type}")
        print(f"   🧠 Understanding Level: {classification.get('understanding_level', 'unknown')}")
        print(f"   🎚️ Confidence Level: {classification.get('confidence_level', 'unknown')}")
        print(f"   🔥 Engagement Level: {classification.get('engagement_level', 'unknown')}")
        
        # Check if it's balanced_guidance
        if routing_path == "balanced_guidance":
            print("   ⚠️ WARNING: Defaulting to balanced_guidance!")
        else:
            print("   ✅ Non-default route selected")
        
        print("-" * 50)
        
        # Remove the user message for the next test
        student_state.messages.pop()

if __name__ == "__main__":
    asyncio.run(test_ongoing_routing()) 