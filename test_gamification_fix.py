#!/usr/bin/env python3
"""
Test the gamification fix for design exploration questions
"""

import os
import sys
import asyncio

# Add project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
THESIS_AGENTS_DIR = os.path.join(PROJECT_ROOT, 'thesis-agents')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, THESIS_AGENTS_DIR)

from dotenv import load_dotenv
load_dotenv()

try:
    from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
    from state_manager import ArchMentorState
    print("✅ Successfully imported modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_gamification_triggers():
    """Test gamification triggers with user's specific examples"""
    
    challenge_gen = ChallengeGeneratorProcessor()
    
    # Test cases - user's actual messages that should NOT trigger gamification
    test_cases = [
        {
            "name": "User's Transitional Nooks Question",
            "message": "I am thinking about creating nooks around the building that will serve as a transitional space between inside and outside to create very open and welcoming atmosphere. how should I aproach this considering spatial organization?",
            "should_trigger": False,
            "reason": "Thoughtful design exploration question - should get direct guidance"
        },
        {
            "name": "Design Approach Question",
            "message": "How should I approach designing flexible learning spaces?",
            "should_trigger": False,
            "reason": "Design approach question - should get direct guidance"
        },
        {
            "name": "Spatial Organization Question", 
            "message": "What would be the best way to organize spaces considering user flow?",
            "should_trigger": False,
            "reason": "Spatial organization question - should get direct guidance"
        },
        {
            "name": "Actually Stuck (should trigger)",
            "message": "I'm completely stuck on this circulation problem and need fresh ideas",
            "should_trigger": True,
            "reason": "Actually stuck and asking for ideas - should trigger gamification"
        },
        {
            "name": "Role-play Question (should trigger)",
            "message": "How would an elderly visitor feel entering this space?",
            "should_trigger": True,
            "reason": "Role-play question - should trigger gamification"
        },
        {
            "name": "Low Engagement (should trigger)",
            "message": "ok",
            "should_trigger": True,
            "reason": "Low engagement - should trigger gamification"
        }
    ]
    
    print("🧪 TESTING GAMIFICATION TRIGGER LOGIC")
    print("=" * 60)
    
    for test_case in test_cases:
        # Create test state
        state = ArchMentorState()
        state.messages = [{"role": "user", "content": test_case["message"]}]
        
        # Test the trigger logic
        result = challenge_gen._should_apply_gamification(state, "test", "test context")
        
        # Check if result matches expectation
        passed = result == test_case["should_trigger"]
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"\n{status} {test_case['name']}")
        print(f"   Message: \"{test_case['message'][:80]}{'...' if len(test_case['message']) > 80 else ''}\"")
        print(f"   Expected: {test_case['should_trigger']} | Actual: {result}")
        print(f"   Reason: {test_case['reason']}")
        
        if not passed:
            print(f"   ❌ MISMATCH: Expected {test_case['should_trigger']}, got {result}")
    
    print(f"\n🎯 SUMMARY")
    print("=" * 30)
    
    # Count results
    total_tests = len(test_cases)
    passed_tests = 0
    
    for test_case in test_cases:
        state = ArchMentorState()
        state.messages = [{"role": "user", "content": test_case["message"]}]
        result = challenge_gen._should_apply_gamification(state, "test", "test context")
        if result == test_case["should_trigger"]:
            passed_tests += 1
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Gamification triggers fixed!")
    else:
        print("⚠️ Some tests failed - needs more work")

if __name__ == "__main__":
    test_gamification_triggers()
