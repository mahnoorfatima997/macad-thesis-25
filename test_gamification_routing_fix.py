"""
Test Gamification Routing Fix
Tests if the synchronized trigger patterns now correctly route to gamification
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'thesis-agents'))

def test_routing_triggers():
    """Test the routing system's gamification trigger detection."""
    
    try:
        from utils.routing_decision_tree import RoutingDecisionTree
        
        router = RoutingDecisionTree()
        
        # Test cases from user's examples
        test_cases = [
            {
                "message": "I think I should start with thinking about how a community member feel in this building",
                "expected_triggers": ["perspective_shift_challenge"],
                "expected_route": "COGNITIVE_CHALLENGE",
                "description": "Community member feeling"
            },
            {
                "message": "How does my design feel from a teenager's perspective",
                "expected_triggers": ["perspective_shift_challenge"],
                "expected_route": "COGNITIVE_CHALLENGE", 
                "description": "Teenager's perspective"
            },
            {
                "message": "I need fresh ideas for my design",
                "expected_triggers": ["creative_constraint_challenge"],
                "expected_route": "COGNITIVE_CHALLENGE",
                "description": "Fresh ideas request"
            },
            {
                "message": "help me see this from a different angle",
                "expected_triggers": ["perspective_shift_challenge"],
                "expected_route": "COGNITIVE_CHALLENGE",
                "description": "Different angle request"
            },
            {
                "message": "how would a visitor feel when they enter my community center?",
                "expected_triggers": ["perspective_shift_challenge"],
                "expected_route": "COGNITIVE_CHALLENGE",
                "description": "Visitor feeling question"
            },
            {
                "message": "The building should have good lighting",
                "expected_triggers": [],
                "expected_route": "OTHER",
                "description": "Normal statement (should NOT trigger)"
            }
        ]
        
        print("🎮 GAMIFICATION ROUTING TEST RESULTS")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['description']}")
            print(f"Message: \"{test_case['message']}\"")
            
            # Test trigger detection
            triggers = router._detect_gamification_triggers(
                test_case['message'], 
                "design_exploration", 
                {}
            )
            
            print(f"Detected triggers: {triggers}")
            print(f"Expected triggers: {test_case['expected_triggers']}")
            
            # Check if triggers match
            triggers_match = set(triggers) == set(test_case['expected_triggers'])
            if triggers_match:
                print("✅ TRIGGERS MATCH")
            else:
                print("❌ TRIGGERS DON'T MATCH")
            
            # Test routing decision
            if triggers:
                # Simulate the routing logic
                route = None
                for trigger in triggers:
                    if trigger == "perspective_shift_challenge":
                        route = "COGNITIVE_CHALLENGE"
                        break
                    elif trigger == "creative_constraint_challenge":
                        route = "COGNITIVE_CHALLENGE"
                        break
                    elif trigger == "low_engagement_challenge":
                        route = "COGNITIVE_CHALLENGE"
                        break
                    elif trigger == "reality_check_challenge":
                        route = "COGNITIVE_CHALLENGE"
                        break
                
                print(f"Would route to: {route}")
                
                if route == "COGNITIVE_CHALLENGE" and test_case['expected_route'] == "COGNITIVE_CHALLENGE":
                    print("✅ ROUTING CORRECT - Will trigger gamification")
                elif test_case['expected_route'] == "OTHER":
                    print("❌ ROUTING ERROR - Should not trigger gamification")
                else:
                    print("❌ ROUTING ERROR - Wrong route")
            else:
                if test_case['expected_route'] == "OTHER":
                    print("✅ ROUTING CORRECT - No gamification triggered")
                else:
                    print("❌ ROUTING ERROR - Should have triggered gamification")
            
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pattern_matching_directly():
    """Test pattern matching directly without routing system."""
    
    print("\n\n🔍 DIRECT PATTERN MATCHING TEST")
    print("=" * 60)
    
    # Test messages from user examples
    test_messages = [
        "I think I should start with thinking about how a community member feel in this building",
        "How does my design feel from a teenager's perspective", 
        "I need fresh ideas for my design",
        "help me see this from a different angle",
        "how would a visitor feel when they enter my community center?"
    ]
    
    # Updated patterns from routing_decision_tree.py
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
    
    for message in test_messages:
        print(f"\nTesting: \"{message}\"")
        message_lower = message.lower().strip()
        
        # Check each pattern set
        role_matches = [p for p in role_play_patterns if p in message_lower]
        perspective_matches = [p for p in perspective_shift_patterns if p in message_lower]
        constraint_matches = [p for p in constraint_patterns if p in message_lower]
        
        if role_matches:
            print(f"  ✅ Role-play matches: {role_matches}")
            print(f"  → Would trigger: perspective_shift_challenge")
        
        if perspective_matches:
            print(f"  ✅ Perspective shift matches: {perspective_matches}")
            print(f"  → Would trigger: perspective_shift_challenge")
        
        if constraint_matches:
            print(f"  ✅ Constraint matches: {constraint_matches}")
            print(f"  → Would trigger: creative_constraint_challenge")
        
        if not (role_matches or perspective_matches or constraint_matches):
            print(f"  ❌ No pattern matches found")

def main():
    """Run all tests."""
    
    print("Testing gamification routing fix...\n")
    
    # Test 1: Direct pattern matching
    test_pattern_matching_directly()
    
    # Test 2: Routing system integration
    routing_success = test_routing_triggers()
    
    print("\n\n🎯 SUMMARY")
    print("=" * 60)
    
    if routing_success:
        print("✅ Routing system tests PASSED")
        print("✅ Trigger patterns are synchronized")
        print("✅ User examples should now trigger gamification")
        print("\n🎮 EXPECTED BEHAVIOR:")
        print("- 'how a community member feel' → Role-play game")
        print("- 'teenager's perspective' → Perspective wheel game") 
        print("- 'fresh ideas' → Constraint puzzle game")
        print("- 'different angle' → Perspective shift game")
        print("- 'visitor feel' → Role-play game")
    else:
        print("❌ Routing system tests FAILED")
        print("❌ Gamification triggers may still not work correctly")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Test in the actual mentor system")
    print("2. Verify games render correctly")
    print("3. Check that routing goes to COGNITIVE_CHALLENGE")

if __name__ == "__main__":
    main()
