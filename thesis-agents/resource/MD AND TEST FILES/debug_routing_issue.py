#!/usr/bin/env python3
"""
Debug script to identify why routing is always returning balanced_guidance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thesis_agents.utils.routing_decision_tree import (
    AdvancedRoutingDecisionTree, 
    RoutingContext, 
    RouteType,
    InputType,
    UnderstandingLevel,
    ConfidenceLevel,
    EngagementLevel
)

def test_routing_decisions():
    """Test various routing scenarios to identify the issue"""
    
    routing_tree = AdvancedRoutingDecisionTree()
    
    # Test cases with different interaction types
    test_cases = [
        {
            "name": "Knowledge Request",
            "user_input": "What are the key principles of sustainable architecture?",
            "interaction_type": "knowledge_request",
            "understanding_level": "medium",
            "confidence_level": "confident",
            "engagement_level": "medium"
        },
        {
            "name": "Cognitive Offloading",
            "user_input": "Can you design this building for me?",
            "interaction_type": "direct_answer_request",
            "understanding_level": "low",
            "confidence_level": "uncertain",
            "engagement_level": "low"
        },
        {
            "name": "Design Problem",
            "user_input": "I'm struggling with the layout of my community center",
            "interaction_type": "design_problem",
            "understanding_level": "medium",
            "confidence_level": "uncertain",
            "engagement_level": "high"
        },
        {
            "name": "Implementation Request",
            "user_input": "How do I implement passive solar design?",
            "interaction_type": "implementation_request",
            "understanding_level": "high",
            "confidence_level": "confident",
            "engagement_level": "high"
        },
        {
            "name": "First Message",
            "user_input": "Hello, I want to design a building",
            "interaction_type": "first_message",
            "understanding_level": "medium",
            "confidence_level": "confident",
            "engagement_level": "medium"
        }
    ]
    
    print("🔍 Testing Routing Decision Tree")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"   Input: {test_case['user_input']}")
        print(f"   Interaction Type: {test_case['interaction_type']}")
        
        # Create classification
        classification = {
            "user_input": test_case['user_input'],
            "last_message": test_case['user_input'],
            "interaction_type": test_case['interaction_type'],
            "understanding_level": test_case['understanding_level'],
            "confidence_level": test_case['confidence_level'],
            "engagement_level": test_case['engagement_level'],
            "is_first_message": test_case['interaction_type'] == "first_message"
        }
        
        # Create routing context
        context = RoutingContext(
            classification=classification,
            context_analysis={},
            routing_suggestions={},
            user_intent="unknown"
        )
        
        # Get routing decision
        decision = routing_tree.decide_route(context)
        
        print(f"   🎯 Route: {decision.route.value}")
        print(f"   📝 Reason: {decision.reason}")
        print(f"   🎚️ Confidence: {decision.confidence:.2f}")
        print(f"   ⚙️ Rule Applied: {decision.rule_applied}")
        print(f"   🧠 User Intent: {decision.user_intent}")
        
        # Check if it's balanced_guidance
        if decision.route.value == "balanced_guidance":
            print("   ⚠️ WARNING: Defaulting to balanced_guidance!")
            
            # Debug why no other rules matched
            print("   🔍 Debugging rule evaluation:")
            for rule_name, rule in sorted(routing_tree.decision_rules.items(), key=lambda x: x[1]["priority"]):
                conditions = rule.get("conditions", [])
                print(f"      Rule '{rule_name}' (priority {rule['priority']}):")
                for condition in conditions:
                    result = routing_tree._evaluate_condition(condition, classification, context)
                    print(f"        Condition '{condition}': {result}")
                rule_matches = routing_tree._evaluate_rule(rule, classification, context)
                print(f"        Rule matches: {rule_matches}")
                if rule_matches:
                    print(f"        ✅ This rule would have been selected!")
                    break
        else:
            print("   ✅ Non-default route selected")
        
        print("-" * 50)

def test_condition_evaluation():
    """Test specific condition evaluation"""
    
    routing_tree = AdvancedRoutingDecisionTree()
    
    print("\n🔍 Testing Condition Evaluation")
    print("=" * 50)
    
    # Test different conditions
    test_conditions = [
        "is_first_message == True",
        "user_intent == 'knowledge_request'",
        "cognitive_offloading_detected == True",
        "engagement_level == 'high'",
        "understanding_level == 'high'",
        "confidence_level == 'overconfident'"
    ]
    
    classification = {
        "user_input": "Test message",
        "last_message": "Test message",
        "interaction_type": "knowledge_request",
        "understanding_level": "high",
        "confidence_level": "confident",
        "engagement_level": "high",
        "is_first_message": False,
        "cognitive_offloading_detected": False,
        "user_intent": "knowledge_request"
    }
    
    context = RoutingContext(
        classification=classification,
        context_analysis={},
        routing_suggestions={},
        user_intent="knowledge_request"
    )
    
    for condition in test_conditions:
        result = routing_tree._evaluate_condition(condition, classification, context)
        print(f"Condition '{condition}': {result}")

if __name__ == "__main__":
    test_routing_decisions()
    test_condition_evaluation() 