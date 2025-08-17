#!/usr/bin/env python3
"""
Quick routing classification test without full orchestrator.
Tests the routing fixes we implemented.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add thesis-agents to path
sys.path.insert(0, 'thesis-agents')

from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext

def test_routing_fixes():
    """Test the specific routing fixes we implemented."""
    print("🧪 QUICK ROUTING CLASSIFICATION TEST")
    print("=" * 60)
    
    router = AdvancedRoutingDecisionTree()
    
    # Test cases based on the issues you reported
    test_cases = [
        {
            "input": "I'm picturing it as a kind of 'all-day hangout' for the neighborhood",
            "expected": "design_exploration",
            "description": "User describing their vision (should NOT be design_problem)"
        },
        {
            "input": "it is for everyone. Families need play and learning areas, younger folks might want co-working",
            "expected": "design_exploration", 
            "description": "User continuing design thinking (should NOT be design_problem)"
        },
        {
            "input": "what if I need to create a hearth of this community center, one central space",
            "expected": "design_exploration",
            "description": "User exploring design ideas (should NOT be design_problem)"
        },
        {
            "input": "what are some strategies for organizing spaces in a community center?",
            "expected": "knowledge_request",
            "description": "Direct knowledge request"
        },
        {
            "input": "show me examples of flexible community spaces",
            "expected": "example_request",
            "description": "Example request"
        },
        {
            "input": "I'm confused about what you mean by spatial hierarchy",
            "expected": "confusion_expression",
            "description": "Confusion expression"
        },
        {
            "input": "I'm stuck on how to fit all the spaces in this small site",
            "expected": "design_exploration",  # design_problem removed, should route to exploration
            "description": "Explicit design problem (now routes to design_exploration)"
        },
        {
            "input": "What are the ADA requirements for door widths?",
            "expected": "technical_question",
            "description": "Technical question"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        user_input = test_case["input"]
        expected = test_case["expected"]
        description = test_case["description"]
        
        # Test intent classification
        classification = {'user_input': user_input}
        context = RoutingContext(
            classification=classification,
            context_analysis={},
            routing_suggestions={}
        )
        
        intent = router.classify_user_intent(user_input, context)
        
        success = intent == expected
        results.append(success)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{i}. {status}")
        print(f"   Description: {description}")
        print(f"   Input: '{user_input}'")
        print(f"   Expected: {expected}")
        print(f"   Got: {intent}")
        
        if not success:
            print(f"   ⚠️  ISSUE: Expected {expected} but got {intent}")
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All routing tests passed! The fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. The routing logic may need further adjustment.")
    
    return passed == total

def test_gamification_triggers():
    """Test gamification trigger detection."""
    print(f"\n{'='*60}")
    print("🎮 GAMIFICATION TRIGGER TEST")
    print(f"{'='*60}")
    
    router = AdvancedRoutingDecisionTree()
    
    # Test cases that should trigger gamification
    gamification_cases = [
        {
            "input": "Tell me about accessibility requirements",
            "should_gamify": True,
            "description": "Knowledge request that could benefit from challenge"
        },
        {
            "input": "This design is perfect and will work for everyone",
            "should_gamify": True,
            "description": "Overconfident statement should trigger challenge"
        },
        {
            "input": "What are some strategies for organizing spaces?",
            "should_gamify": False,
            "description": "Simple knowledge request shouldn't always gamify"
        }
    ]
    
    for i, test_case in enumerate(gamification_cases, 1):
        user_input = test_case["input"]
        should_gamify = test_case["should_gamify"]
        description = test_case["description"]
        
        # Test gamification detection (simplified)
        classification = {'user_input': user_input}
        context = RoutingContext(
            classification=classification,
            context_analysis={},
            routing_suggestions={}
        )
        
        # This is a simplified test - the actual gamification logic is more complex
        intent = router.classify_user_intent(user_input, context)
        
        print(f"\n{i}. {description}")
        print(f"   Input: '{user_input}'")
        print(f"   Intent: {intent}")
        print(f"   Should gamify: {should_gamify}")
        print(f"   Status: ℹ️  (Gamification logic is complex and context-dependent)")

if __name__ == "__main__":
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please check your .env file")
    else:
        print(f"✅ API Key found: {api_key[:10]}...")
    
    print()
    
    # Run tests
    routing_success = test_routing_fixes()
    test_gamification_triggers()
    
    print(f"\n{'='*60}")
    print("🎯 OVERALL RESULT")
    print(f"{'='*60}")
    
    if routing_success:
        print("✅ Routing fixes are working correctly!")
        print("   - design_problem no longer overrides other intents")
        print("   - design_exploration is properly classified")
        print("   - knowledge_request and example_request work correctly")
    else:
        print("❌ Some routing issues remain. Check the failed tests above.")
