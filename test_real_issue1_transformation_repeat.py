#!/usr/bin/env python3
"""
Test the REAL Issue 1: Transformation challenge triggering repeatedly when user responds to transformation challenge
The issue is NOT about example requests - it's about responses to transformation games triggering the same game again.
"""

import sys
import os
sys.path.append('.')
sys.path.append('thesis-agents')

from dotenv import load_dotenv
load_dotenv()

def test_transformation_response_repetition():
    """Test that responses to transformation challenges don't trigger another transformation challenge"""
    print("🧪 TESTING REAL ISSUE 1: Transformation challenge repetition prevention")
    print("=" * 70)
    
    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        from state_manager import ArchMentorState
        
        processor = ChallengeGeneratorProcessor()
        
        # Simulate the actual scenario from the terminal:
        # 1. User mentions warehouse conversion
        # 2. System triggers transformation challenge
        # 3. User responds to the transformation challenge (mentioning "converting" again)
        # 4. System should NOT trigger another transformation challenge
        
        state = ArchMentorState()
        state.messages = [
            {'role': 'user', 'content': 'I am converting a warehouse to a community center'},
            {'role': 'assistant', 'content': 'Interesting transformation project! Let me present you with a creative challenge...'},
            {'role': 'assistant', 'content': 'TRANSFORMATION CHALLENGE: Imagine you are converting this warehouse in three different time periods...'},
            {'role': 'user', 'content': 'For converting the warehouse, I think the 1920s approach would focus on maintaining the industrial character while adding community spaces'}
        ]
        
        print("Conversation scenario:")
        print("1. User: 'I am converting a warehouse to a community center'")
        print("2. Assistant: [Triggers transformation challenge]")
        print("3. User responds: 'For converting the warehouse, I think the 1920s approach...'")
        print("4. Should the system trigger another transformation challenge?")
        print()
        
        # Test if gamification should be applied to the user's response
        user_response = "For converting the warehouse, I think the 1920s approach would focus on maintaining the industrial character while adding community spaces"
        should_trigger = processor._should_apply_gamification(state, 'test_challenge', user_response)
        
        print(f"User response contains 'converting': {'converting' in user_response}")
        print(f"Recent assistant messages contain transformation content: {any('transformation' in msg['content'].lower() for msg in state.messages if msg.get('role') == 'assistant')}")
        print(f"Should trigger gamification: {should_trigger}")
        print(f"Expected: False (should NOT trigger another transformation challenge)")
        print()
        
        if not should_trigger:
            print("✅ REAL ISSUE 1 FIXED: User responses to transformation challenges don't trigger repetition")
            return True
        else:
            print("❌ REAL ISSUE 1 NOT FIXED: User responses still trigger repeated transformation challenges")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_challenge_types_still_work():
    """Test that different challenge types can still be triggered after a transformation challenge"""
    print("\n🧪 TESTING: Different challenge types still work after transformation")
    print("=" * 70)
    
    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        from state_manager import ArchMentorState
        
        processor = ChallengeGeneratorProcessor()
        
        # Scenario: After a transformation challenge, user asks a role-play question
        state = ArchMentorState()
        state.messages = [
            {'role': 'user', 'content': 'I am converting a warehouse to a community center'},
            {'role': 'assistant', 'content': 'TRANSFORMATION CHALLENGE: Imagine converting this in different eras...'},
            {'role': 'user', 'content': 'That was helpful for the conversion approach'},
            {'role': 'user', 'content': 'How would a visitor feel entering this space?'}  # Role-play trigger
        ]
        
        print("Scenario: After transformation challenge, user asks role-play question")
        print("User: 'How would a visitor feel entering this space?'")
        print("Should trigger role-play challenge (different from transformation)?")
        print()
        
        # Test if role-play gamification should be applied
        user_question = "How would a visitor feel entering this space?"
        should_trigger = processor._should_apply_gamification(state, 'test_challenge', user_question)
        
        print(f"Should trigger gamification: {should_trigger}")
        print(f"Expected: True (should trigger role-play challenge)")
        print()
        
        if should_trigger:
            print("✅ Different challenge types still work after transformation")
            return True
        else:
            print("⚠️ Different challenge types might be blocked (check frequency control)")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_transformation_after_gap():
    """Test that transformation challenges can be triggered again after a gap"""
    print("\n🧪 TESTING: Transformation challenges work again after conversation gap")
    print("=" * 70)
    
    try:
        from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGeneratorProcessor
        from state_manager import ArchMentorState
        
        processor = ChallengeGeneratorProcessor()
        
        # Scenario: Transformation challenge, then several other messages, then another transformation topic
        state = ArchMentorState()
        state.messages = [
            {'role': 'user', 'content': 'I am converting a warehouse to a community center'},
            {'role': 'assistant', 'content': 'TRANSFORMATION CHALLENGE: Different eras...'},
            {'role': 'user', 'content': 'That was helpful'},
            {'role': 'assistant', 'content': 'Great! What else would you like to explore?'},
            {'role': 'user', 'content': 'I need help with the layout'},
            {'role': 'assistant', 'content': 'Let me help with layout considerations...'},
            {'role': 'user', 'content': 'Now I am also converting the adjacent factory building'}  # New transformation topic
        ]
        
        print("Scenario: After gap in conversation, user mentions new transformation")
        print("User: 'Now I am also converting the adjacent factory building'")
        print("Should trigger transformation challenge (enough gap from previous)?")
        print()
        
        # Test if transformation gamification should be applied again
        user_message = "Now I am also converting the adjacent factory building"
        should_trigger = processor._should_apply_gamification(state, 'test_challenge', user_message)
        
        print(f"Should trigger gamification: {should_trigger}")
        print(f"Expected: True (should trigger transformation challenge after gap)")
        print()
        
        if should_trigger:
            print("✅ Transformation challenges work again after conversation gap")
            return True
        else:
            print("⚠️ Transformation challenges might be over-blocked (check gap detection)")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests for the real Issue 1"""
    print("🚀 TESTING REAL ISSUE 1: TRANSFORMATION CHALLENGE REPETITION")
    print("The issue: When users respond to transformation challenges, the system")
    print("detects transformation keywords in their response and triggers another")
    print("transformation challenge, creating an annoying loop.")
    print("=" * 80)
    
    # Run tests
    test1_passed = test_transformation_response_repetition()
    test2_passed = test_different_challenge_types_still_work()
    test3_passed = test_transformation_after_gap()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 REAL ISSUE 1 TEST RESULTS")
    print("=" * 80)
    
    tests = [
        ("🔄 Transformation Response Repetition Prevention", test1_passed),
        ("🎭 Different Challenge Types Still Work", test2_passed),
        ("⏰ Transformation Works After Gap", test3_passed)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 REAL ISSUE 1 COMPLETELY FIXED!")
        print("✅ Transformation challenges won't repeat on user responses")
        print("✅ Other challenge types still work properly")
        print("✅ Transformation challenges can be used again after gaps")
    else:
        print("⚠️ REAL ISSUE 1 NEEDS MORE WORK - Check failed tests above")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
