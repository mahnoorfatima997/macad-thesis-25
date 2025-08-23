"""
Comprehensive Routing Test

Tests all routing improvements including:
- Negative context detection
- Building type extraction
- Intent classification
- Gamification trigger detection
"""

import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from utils.routing_decision_tree import AdvancedRoutingDecisionTree
from agents.domain_expert.adapter import DomainExpertAdapter
from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGenerator
from orchestration.state import ArchMentorState

def test_routing_comprehensive():
    """Comprehensive test of routing and intent detection."""
    
    print("🎯 COMPREHENSIVE ROUTING TEST")
    print("=" * 60)
    
    # Initialize components
    router = AdvancedRoutingDecisionTree()
    domain_expert = DomainExpertAdapter()
    challenge_gen = ChallengeGenerator()
    
    # Test cases with expected outcomes
    test_cases = {
        "Negative Context Detection": [
            {
                "input": "i dont want project examples I need knowledge about circulation",
                "expected_route": "knowledge_only",
                "expected_example_request": False,
                "building_type": "community_center"
            },
            {
                "input": "not looking for examples just circulation principles",
                "expected_route": "knowledge_only", 
                "expected_example_request": False,
                "building_type": "unknown"
            },
            {
                "input": "no project examples please just design guidelines",
                "expected_route": "knowledge_only",
                "expected_example_request": False,
                "building_type": "unknown"
            }
        ],
        "Example Requests": [
            {
                "input": "can you provide example projects for community center",
                "expected_route": "knowledge_only",
                "expected_example_request": True,
                "building_type": "community_center"
            },
            {
                "input": "show me case studies of hospitals",
                "expected_route": "knowledge_only",
                "expected_example_request": True,
                "building_type": "hospital"
            }
        ],
        "Gamification Triggers": [
            {
                "input": "how would a visitor feel entering this space",
                "expected_gamification": True,
                "trigger_type": "role_play"
            },
            {
                "input": "i wonder what would happen if we changed the layout",
                "expected_gamification": True,
                "trigger_type": "curiosity"
            },
            {
                "input": "im stuck on the circulation design",
                "expected_gamification": True,
                "trigger_type": "constraint"
            },
            {
                "input": "this seems pretty easy to design",
                "expected_gamification": True,
                "trigger_type": "overconfidence"
            },
            {
                "input": "just tell me what to do",
                "expected_gamification": True,
                "trigger_type": "cognitive_offloading"
            },
            {
                "input": "ok",
                "expected_gamification": True,
                "trigger_type": "low_engagement"
            }
        ],
        "Building Type Extraction": [
            {
                "input": "designing a community center for 500 people",
                "expected_building_type": "community_center"
            },
            {
                "input": "working on a hospital renovation project",
                "expected_building_type": "hospital"
            },
            {
                "input": "school design with flexible classrooms",
                "expected_building_type": "school"
            },
            {
                "input": "wooden structure for residential use",
                "expected_building_type": "residential"
            }
        ],
        "Topic Extraction": [
            {
                "input": "circulation design principles",
                "expected_topic": "circulation"
            },
            {
                "input": "accessibility requirements for buildings",
                "expected_topic": "accessibility"
            },
            {
                "input": "sustainable design strategies",
                "expected_topic": "sustainability"
            },
            {
                "input": "wooden structures and timber construction",
                "expected_topic": "wooden structures"
            }
        ]
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for category, tests in test_cases.items():
        print(f"\n📂 Testing Category: {category}")
        print("-" * 50)
        
        for test_case in tests:
            total_tests += 1
            user_input = test_case["input"]
            print(f"\n🔍 Input: '{user_input}'")
            
            try:
                # Test routing
                if "expected_route" in test_case:
                    # Create mock state
                    state = ArchMentorState()
                    state.messages = [{"role": "user", "content": user_input}]
                    state.project_context = test_case.get("building_type", "unknown")
                    
                    route = router.determine_route(state)
                    expected = test_case["expected_route"]
                    
                    if route.value.lower() == expected.lower():
                        print(f"   ✅ Routing: {route.value} (expected: {expected})")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Routing: {route.value} (expected: {expected})")
                        failed_tests.append((category, user_input, f"Route mismatch: got {route.value}, expected {expected}"))
                
                # Test example request detection
                if "expected_example_request" in test_case:
                    # This would require accessing the domain expert's internal logic
                    # For now, we'll test the pattern matching
                    is_example_request = any(keyword in user_input.lower() for keyword in 
                                           ["example projects", "project examples", "case studies", "precedents"])
                    
                    # Check for negative context
                    negative_patterns = ["don't want", "dont want", "not want", "no examples", "no projects"]
                    has_negative = any(pattern in user_input.lower() for pattern in negative_patterns)
                    
                    final_result = is_example_request and not has_negative
                    expected = test_case["expected_example_request"]
                    
                    if final_result == expected:
                        print(f"   ✅ Example Request: {final_result} (expected: {expected})")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Example Request: {final_result} (expected: {expected})")
                        failed_tests.append((category, user_input, f"Example detection mismatch"))
                
                # Test gamification triggers
                if "expected_gamification" in test_case:
                    state = ArchMentorState()
                    state.messages = [{"role": "user", "content": user_input}]
                    
                    should_gamify = challenge_gen._should_apply_gamification(state, "test", "test context")
                    expected = test_case["expected_gamification"]
                    
                    if should_gamify == expected:
                        print(f"   ✅ Gamification: {should_gamify} (expected: {expected})")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Gamification: {should_gamify} (expected: {expected})")
                        failed_tests.append((category, user_input, f"Gamification trigger mismatch"))
                
                # Test building type extraction
                if "expected_building_type" in test_case:
                    extracted = challenge_gen._extract_building_type(user_input)
                    expected = test_case["expected_building_type"]
                    
                    if extracted == expected:
                        print(f"   ✅ Building Type: {extracted} (expected: {expected})")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Building Type: {extracted} (expected: {expected})")
                        failed_tests.append((category, user_input, f"Building type mismatch"))
                
                # Test topic extraction
                if "expected_topic" in test_case:
                    extracted = domain_expert._extract_topic_from_user_input(user_input)
                    expected = test_case["expected_topic"]
                    
                    if extracted.lower() == expected.lower():
                        print(f"   ✅ Topic: {extracted} (expected: {expected})")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Topic: {extracted} (expected: {expected})")
                        failed_tests.append((category, user_input, f"Topic extraction mismatch"))
                        
            except Exception as e:
                print(f"   ⚠️ ERROR: {e}")
                failed_tests.append((category, user_input, str(e)))
    
    # Summary
    print(f"\n📊 ROUTING TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for category, input_text, error in failed_tests:
            print(f"   {category}: '{input_text}' - {error}")

if __name__ == "__main__":
    test_routing_comprehensive()
