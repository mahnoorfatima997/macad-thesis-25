#!/usr/bin/env python3
"""
Test to check why the problematic input is being routed incorrectly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the thesis-agents folder to the Python path
sys.path.append('thesis-agents')

from utils.routing_decision_tree import AdvancedRoutingDecisionTree
from agents.context_agent.processors.input_classification import InputClassificationProcessor

def test_problematic_input():
    """Test the problematic input from the user's conversation."""
    print("🔍 Testing Problematic Input...")
    
    # Create instances
    router = AdvancedRoutingDecisionTree()
    classifier = InputClassificationProcessor()
    
    # Test the problematic input from your conversation
    test_input = "I am curious how I should organize my spaces around those courtyards and gardens. What should be my approach?"
    print(f"\n📋 Testing input: {test_input}")
    
    # Step 1: Classify the input
    classification = classifier._classify_interaction_type(test_input)
    print(f"  Step 1 - Classification: {classification}")
    
    # Step 2: Create routing context
    mock_context = type('MockContext', (), {
        "building_type": "mixed_use",
        "complexity_level": "intermediate",
        "user_level": "intermediate",
        "user_input": test_input,
        "classification": {
            "interaction_type": classification,
            "user_input": test_input,
            "understanding_level": "intermediate",
            "confidence_level": "confident",
            "engagement_level": "high"
        },
        "context_analysis": {},
        "routing_suggestions": {},
        "student_state": {},
        "conversation_history": [],
        "current_phase": "ideation",
        "phase_progress": 0.0,
        "project_context": {},
        "user_intent": "unknown",
        "cognitive_state": {}
    })()
    
    # Step 3: Get routing decision
    try:
        route_decision = router.decide_route(mock_context)
        print(f"  Step 2 - Route Decision: {route_decision.route.value}")
        print(f"  Step 2 - Reasoning: {route_decision.reason}")
        
        # Check if this is the correct route
        if route_decision.route.value == "supportive_scaffolding":
            print("  ✅ CORRECT ROUTING - Guidance request → supportive_scaffolding")
        else:
            print(f"  ❌ WRONG ROUTING - Expected: supportive_scaffolding, Got: {route_decision.route.value}")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    print("\n🎯 This test shows why the routing is still broken.")
    print("🎯 The input classification or routing decision tree logic needs fixing.")

if __name__ == "__main__":
    test_problematic_input()
