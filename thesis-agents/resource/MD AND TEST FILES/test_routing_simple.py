#!/usr/bin/env python3
"""
Simple test script to verify routing fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('thesis-agents')

from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext

def test_routing_fix():
    """Test the routing fix with simple cases"""
    
    print("🧪 Testing Routing Fix")
    print("=" * 40)
    
    # Initialize the routing decision tree
    routing_tree = AdvancedRoutingDecisionTree()
    
    # Test case 1: knowledge_request (should NOT be cognitive offloading)
    print("\n1. Testing knowledge_request...")
    
    classification_1 = {
        "interaction_type": "knowledge_request",
        "understanding_level": "low",
        "confidence_level": "uncertain",
        "engagement_level": "medium",
        "user_input": "What is adaptive reuse?",
        "last_message": "What is adaptive reuse?"
    }
    
    routing_context_1 = RoutingContext(
        classification=classification_1,
        context_analysis={},
        routing_suggestions={},
        student_state=None,
        conversation_history=[],
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_1 = routing_tree.decide_route(routing_context_1)
    
    print(f"   Route: {decision_1.route.value}")
    print(f"   Rule: {decision_1.rule_applied}")
    print(f"   Cognitive Offloading: {decision_1.cognitive_offloading_detected}")
    
    # Test case 2: example_request (should NOT be cognitive offloading)
    print("\n2. Testing example_request...")
    
    classification_2 = {
        "interaction_type": "example_request",
        "understanding_level": "medium",
        "confidence_level": "confident",
        "engagement_level": "high",
        "user_input": "Can you give me examples of sustainable community centers?",
        "last_message": "Can you give me examples of sustainable community centers?"
    }
    
    routing_context_2 = RoutingContext(
        classification=classification_2,
        context_analysis={},
        routing_suggestions={},
        student_state=None,
        conversation_history=[],
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_2 = routing_tree.decide_route(routing_context_2)
    
    print(f"   Route: {decision_2.route.value}")
    print(f"   Rule: {decision_2.rule_applied}")
    print(f"   Cognitive Offloading: {decision_2.cognitive_offloading_detected}")
    
    # Test case 3: direct_answer_request (SHOULD be cognitive offloading)
    print("\n3. Testing direct_answer_request...")
    
    classification_3 = {
        "interaction_type": "direct_answer_request",
        "understanding_level": "low",
        "confidence_level": "uncertain",
        "engagement_level": "low",
        "user_input": "Can you design this for me?",
        "last_message": "Can you design this for me?"
    }
    
    routing_context_3 = RoutingContext(
        classification=classification_3,
        context_analysis={},
        routing_suggestions={},
        student_state=None,
        conversation_history=[],
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_3 = routing_tree.decide_route(routing_context_3)
    
    print(f"   Route: {decision_3.route.value}")
    print(f"   Rule: {decision_3.rule_applied}")
    print(f"   Cognitive Offloading: {decision_3.cognitive_offloading_detected}")
    
    print("\n" + "=" * 40)
    print("📊 RESULTS:")
    print(f"   knowledge_request → {decision_1.route.value} (cognitive offloading: {decision_1.cognitive_offloading_detected})")
    print(f"   example_request → {decision_2.route.value} (cognitive offloading: {decision_2.cognitive_offloading_detected})")
    print(f"   direct_answer_request → {decision_3.route.value} (cognitive offloading: {decision_3.cognitive_offloading_detected})")
    
    # Check if the fix worked
    if not decision_1.cognitive_offloading_detected and not decision_2.cognitive_offloading_detected and decision_3.cognitive_offloading_detected:
        print("\n✅ SUCCESS: Routing fix worked!")
        print("   - knowledge_request and example_request are NOT flagged as cognitive offloading")
        print("   - direct_answer_request IS flagged as cognitive offloading")
    else:
        print("\n❌ ISSUE: Routing fix may not have worked completely")
    
    print("\n✅ Simple routing test completed!")

if __name__ == "__main__":
    test_routing_fix()
