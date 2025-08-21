"""
Simple Gamification Trigger Test
Tests the trigger patterns directly without Streamlit
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'thesis-agents'))

from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
from state_manager import ArchMentorState

def create_test_state(user_message: str) -> ArchMentorState:
    """Create a test state with a user message."""
    state = ArchMentorState()
    state.messages = [
        {"role": "user", "content": user_message}
    ]
    state.current_design_brief = "Design a community center"
    return state

def test_trigger_patterns():
    """Test the trigger patterns with real user examples."""
    
    processor = ChallengeGeneratorProcessor()
    
    # Test cases from user's examples
    test_cases = [
        {
            "message": "I think I should start with thinking about how a community member feel in this building",
            "expected": True,
            "type": "Role-play"
        },
        {
            "message": "How does my design feel from a teenager's perspective",
            "expected": True,
            "type": "Perspective"
        },
        {
            "message": "I need fresh ideas for my design",
            "expected": True,
            "type": "Creative constraint"
        },
        {
            "message": "help me see this from a different angle",
            "expected": True,
            "type": "Perspective shift"
        },
        {
            "message": "how would a visitor feel when they enter my community center?",
            "expected": True,
            "type": "Role-play"
        },
        {
            "message": "The building should have good lighting",
            "expected": False,
            "type": "Normal statement"
        }
    ]
    
    print("🎮 GAMIFICATION TRIGGER TEST RESULTS")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['type']}")
        print(f"Message: \"{test_case['message']}\"")
        
        # Create test state
        state = create_test_state(test_case['message'])
        
        # Test the trigger
        result = processor._should_apply_gamification(state, "user_perspective", "perspective_challenge")
        
        # Check result
        if result == test_case['expected']:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"Expected: {test_case['expected']}, Got: {result} - {status}")
        
        if not result and test_case['expected']:
            print("  🚨 SHOULD HAVE TRIGGERED BUT DIDN'T!")
        elif result and not test_case['expected']:
            print("  🚨 TRIGGERED WHEN IT SHOULDN'T HAVE!")

def test_individual_patterns():
    """Test individual pattern matching."""
    
    print("\n\n🔍 INDIVIDUAL PATTERN ANALYSIS")
    print("=" * 50)
    
    # Test messages
    messages = [
        "I think I should start with thinking about how a community member feel in this building",
        "How does my design feel from a teenager's perspective", 
        "I need fresh ideas for my design",
        "help me see this from a different angle"
    ]
    
    # Pattern sets
    role_play_patterns = [
        'how would a visitor feel', 'how would', 'what would', 'from the perspective of',
        'how do users feel', 'what would an elderly person', 'what would a child',
        'how a', 'feel in this', 'feel when they', 'feel in the', 'experience in',
        'member feel', 'user feel', 'visitor feel', 'person feel',
        'from a', 'as a', 'like a', 'perspective', "'s perspective",
        'teenager\'s perspective', 'child\'s perspective', 'user\'s perspective'
    ]
    
    perspective_shift_patterns = [
        'help me see this from a different angle', 'different angle', 'see this differently',
        'think about this differently', 'different perspective', 'another way to think',
        'alternative viewpoint', 'fresh perspective',
        'different angle', 'differently', 'another way', 'alternative', 
        'fresh perspective', 'new perspective', 'see this', 'think about this'
    ]
    
    constraint_patterns = [
        'i\'m stuck on', 'stuck on', 'having trouble', 'not sure how',
        'i need fresh ideas', 'need fresh ideas', 'fresh ideas', 'new ideas',
        'creative ideas', 'need ideas', 'ideas for', 'inspire', 'inspiration',
        'stuck', 'help me think', 'new approach', 'different approach'
    ]
    
    for message in messages:
        print(f"\nAnalyzing: \"{message}\"")
        message_lower = message.lower()
        
        # Check role-play patterns
        role_matches = [p for p in role_play_patterns if p in message_lower]
        if role_matches:
            print(f"  ✅ Role-play matches: {role_matches}")
        else:
            print(f"  ❌ No role-play matches")
        
        # Check perspective shift patterns
        perspective_matches = [p for p in perspective_shift_patterns if p in message_lower]
        if perspective_matches:
            print(f"  ✅ Perspective shift matches: {perspective_matches}")
        else:
            print(f"  ❌ No perspective shift matches")
        
        # Check constraint patterns
        constraint_matches = [p for p in constraint_patterns if p in message_lower]
        if constraint_matches:
            print(f"  ✅ Constraint matches: {constraint_matches}")
        else:
            print(f"  ❌ No constraint matches")
        
        # Overall result
        any_match = role_matches or perspective_matches or constraint_matches
        print(f"  🎯 OVERALL: {'SHOULD TRIGGER' if any_match else 'NO TRIGGER'}")

if __name__ == "__main__":
    print("Starting gamification trigger tests...\n")
    
    try:
        test_trigger_patterns()
        test_individual_patterns()
        
        print("\n\n🎯 SUMMARY")
        print("=" * 50)
        print("If tests are failing, the trigger patterns need to be updated")
        print("to match the actual language users are using.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
