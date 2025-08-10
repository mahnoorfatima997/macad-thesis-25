#!/usr/bin/env python3
"""
Test the classification fix for example requests
"""

import sys
import os
sys.path.append('./thesis-agents')

from agents.context_agent import ContextAgent
from state_manager import ArchMentorState, StudentProfile

def test_classification():
    """Test the classification fix"""
    
    print("🔍 Testing Classification Fix...")
    
    # Initialize context agent
    context_agent = ContextAgent("architecture")
    
    # Create test state
    state = ArchMentorState()
    state.student_profile = StudentProfile(skill_level="intermediate")
    
    # Test cases
    test_cases = [
        "can you provide some precedent projects for community centers that are used to be industrial buildings and turned into community centers?",
        "show me examples of sustainable design",
        "I need some references for adaptive reuse",
        "can you give me case studies of community centers",
        "what is adaptive reuse?"  # This should NOT be example_request
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test_input}")
        print(f"{'='*60}")
        
        # Test manual classification
        interaction_type = context_agent._classify_interaction_type(test_input, state)
        print(f"Manual Classification: {interaction_type}")
        
        # Test if it would trigger manual override
        manual_override_types = [
            "question_response", "confusion_expression", "direct_answer_request", 
            "knowledge_request", "implementation_request", "example_request",
            "feedback_request", "technical_question", "improvement_seeking",
            "general_question", "general_statement"
        ]
        
        if interaction_type in manual_override_types:
            print(f"✅ Would trigger manual override: {interaction_type}")
        else:
            print(f"❌ Would NOT trigger manual override: {interaction_type}")
    
    print(f"\n{'='*60}")
    print("🎯 Expected Results:")
    print("✅ Test 1: example_request (your message)")
    print("✅ Test 2: example_request")
    print("✅ Test 3: example_request") 
    print("✅ Test 4: example_request")
    print("❌ Test 5: knowledge_request (not example_request)")

if __name__ == "__main__":
    test_classification()
