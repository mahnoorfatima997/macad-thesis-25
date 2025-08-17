#!/usr/bin/env python3
"""
Test script to verify routing and response fixes
"""

import sys
import os
sys.path.insert(0, 'thesis-agents')

from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext

def test_routing_fixes():
    """Test the routing fixes"""
    print("🧪 TESTING ROUTING FIXES")
    print("=" * 80)
    
    router = AdvancedRoutingDecisionTree()
    
    # Test cases from routing_test_user_inputs.md
    test_cases = [
        # Design guidance cases - should go to balanced_guidance
        {
            'input': 'I need help organizing spaces for different age groups in my community center.',
            'expected': 'balanced_guidance',
            'category': 'Design Guidance'
        },
        {
            'input': 'How should I handle circulation patterns in a large community space?',
            'expected': 'balanced_guidance',
            'category': 'Design Guidance'
        },
        {
            'input': 'I want to create flexible spaces that can change function throughout the day.',
            'expected': 'balanced_guidance',
            'category': 'Design Guidance'
        },
        {
            'input': 'help',
            'expected': 'balanced_guidance',
            'category': 'Design Guidance'
        },
        
        # Knowledge only cases - should go to knowledge_only
        {
            'input': 'What are some examples of successful community centers in hot climates?',
            'expected': 'knowledge_only',
            'category': 'Knowledge Only'
        },
        {
            'input': 'Can you tell me about passive cooling strategies for large buildings?',
            'expected': 'knowledge_only',
            'category': 'Knowledge Only'
        },
        {
            'input': 'Can you show me some examples of warehouse-to-community center conversions?',
            'expected': 'knowledge_only',
            'category': 'Knowledge Only'
        },
        
        # Confusion cases - should go to socratic_clarification
        {
            'input': 'I don\'t understand what you mean by spatial hierarchy.',
            'expected': 'socratic_clarification',
            'category': 'Confusion'
        },
        {
            'input': 'Can you explain that differently? I\'m not following.',
            'expected': 'socratic_clarification',
            'category': 'Confusion'
        },
    ]
    
    results = {'correct': 0, 'total': len(test_cases), 'details': []}
    
    for test_case in test_cases:
        test_input = test_case['input']
        expected_route = test_case['expected']
        category = test_case['category']
        
        # Test routing
        classification = {'user_input': test_input}
        context = RoutingContext(classification=classification, context_analysis={}, routing_suggestions={})
        decision = router.decide_route(context)
        
        actual_route = decision.route.value
        is_correct = actual_route == expected_route
        
        if is_correct:
            results['correct'] += 1
        
        result_detail = {
            'input': test_input,
            'category': category,
            'expected': expected_route,
            'actual': actual_route,
            'correct': is_correct,
            'rule': decision.rule_applied,
            'intent': decision.user_intent
        }
        results['details'].append(result_detail)
        
        status = '✅' if is_correct else '❌'
        print(f"{status} [{category}] {test_input[:50]}...")
        print(f"    Expected: {expected_route} | Got: {actual_route}")
        if not is_correct:
            print(f"    Rule: {decision.rule_applied} | Intent: {decision.user_intent}")
        print()
    
    # Summary
    accuracy = (results['correct'] / results['total']) * 100
    print(f"📊 RESULTS: {results['correct']}/{results['total']} correct ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("🎉 ROUTING FIXES SUCCESSFUL!")
    else:
        print("⚠️  Some routing issues remain")
        
    return results

def test_synthesis_template():
    """Test that synthesis template is working"""
    print("\n🧪 TESTING SYNTHESIS TEMPLATE")
    print("=" * 80)
    
    try:
        from thesis_agents.orchestration.synthesis import shape_by_route
        print("✅ Synthesis module imported successfully")
        
        # Test basic synthesis template
        test_text = "This is a test response"
        test_classification = {"user_input": "How should I organize spaces?"}
        test_context = {}
        test_results = {}
        
        shaped_response = shape_by_route(
            text=test_text,
            path="balanced_guidance",
            classification=test_classification,
            context_analysis=test_context,
            ordered_results=test_results
        )
        
        if "Synthesis:" in shaped_response:
            print("✅ Synthesis template is working")
            print(f"   Response preview: {shaped_response[:100]}...")
        else:
            print("❌ Synthesis template not working properly")
            
    except Exception as e:
        print(f"❌ Synthesis test failed: {e}")

if __name__ == "__main__":
    # Test routing fixes
    routing_results = test_routing_fixes()
    
    # Test synthesis template
    test_synthesis_template()
    
    print(f"\n🏁 TESTING COMPLETE")
    print("=" * 80)
