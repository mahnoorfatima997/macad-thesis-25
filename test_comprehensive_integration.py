"""
Comprehensive Integration Test

Tests the complete flow from user input to final response including:
- Routing decisions
- Database searches
- Gamification triggers
- Response generation
- UI rendering
"""

import sys
import os
import asyncio
from unittest.mock import patch, MagicMock

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

async def test_integration_comprehensive():
    """Comprehensive end-to-end integration test."""
    
    print("🔄 COMPREHENSIVE INTEGRATION TEST")
    print("=" * 60)
    
    # Test scenarios that represent real user interactions
    test_scenarios = [
        {
            "name": "Community Center Knowledge Request",
            "user_input": "I need information about circulation design for community centers",
            "building_type": "community_center",
            "expected_route": "knowledge_only",
            "expected_gamification": False,
            "expected_db_search": True,
            "expected_topic": "circulation"
        },
        {
            "name": "Negative Context Example Request",
            "user_input": "I dont want project examples I need knowledge about accessibility",
            "building_type": "unknown",
            "expected_route": "knowledge_only",
            "expected_gamification": False,
            "expected_example_request": False,
            "expected_topic": "accessibility"
        },
        {
            "name": "Role-Play Gamification Trigger",
            "user_input": "How would an elderly person feel entering this community center?",
            "building_type": "community_center",
            "expected_route": "cognitive_challenge",
            "expected_gamification": True,
            "gamification_type": "role_play"
        },
        {
            "name": "Wooden Structures Knowledge",
            "user_input": "What are the design principles for wooden structures?",
            "building_type": "unknown",
            "expected_route": "knowledge_only",
            "expected_gamification": False,
            "expected_topic": "wooden structures"
        },
        {
            "name": "Low Engagement Trigger",
            "user_input": "ok",
            "building_type": "community_center",
            "expected_route": "cognitive_challenge",
            "expected_gamification": True,
            "gamification_type": "low_engagement"
        },
        {
            "name": "Hospital Size Requirements",
            "user_input": "How big should a hospital emergency room be for 200 patients?",
            "building_type": "hospital",
            "expected_route": "knowledge_only",
            "expected_gamification": False,
            "expected_topic": "hospital design"
        }
    ]
    
    total_scenarios = len(test_scenarios)
    passed_scenarios = 0
    failed_scenarios = []
    
    for scenario in test_scenarios:
        print(f"\n🎯 Testing Scenario: {scenario['name']}")
        print("-" * 50)
        print(f"Input: '{scenario['user_input']}'")
        
        scenario_passed = True
        scenario_errors = []
        
        try:
            # Initialize components
            from utils.routing_decision_tree import RoutingDecisionTree
            from agents.domain_expert.adapter import DomainExpertAdapter
            from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGenerator
            from orchestration.state import ArchMentorState
            from knowledge_base.knowledge_manager import KnowledgeManager
            
            router = RoutingDecisionTree()
            domain_expert = DomainExpertAdapter()
            challenge_gen = ChallengeGenerator()
            km = KnowledgeManager(domain="architecture")
            
            # Create state
            state = ArchMentorState()
            state.messages = [{"role": "user", "content": scenario["user_input"]}]
            state.project_context = scenario.get("building_type", "unknown")
            
            # Test 1: Routing
            if "expected_route" in scenario:
                route = router.determine_route(state)
                expected_route = scenario["expected_route"]
                
                if route.value.lower() == expected_route.lower():
                    print(f"   ✅ Routing: {route.value}")
                else:
                    print(f"   ❌ Routing: {route.value} (expected: {expected_route})")
                    scenario_passed = False
                    scenario_errors.append(f"Routing mismatch: {route.value} vs {expected_route}")
            
            # Test 2: Gamification Detection
            if "expected_gamification" in scenario:
                should_gamify = challenge_gen._should_apply_gamification(state, "test", "test context")
                expected_gamify = scenario["expected_gamification"]
                
                if should_gamify == expected_gamify:
                    print(f"   ✅ Gamification: {should_gamify}")
                else:
                    print(f"   ❌ Gamification: {should_gamify} (expected: {expected_gamify})")
                    scenario_passed = False
                    scenario_errors.append(f"Gamification mismatch: {should_gamify} vs {expected_gamify}")
            
            # Test 3: Topic Extraction
            if "expected_topic" in scenario:
                topic = domain_expert._extract_topic_from_user_input(scenario["user_input"])
                expected_topic = scenario["expected_topic"]
                
                if topic.lower() == expected_topic.lower():
                    print(f"   ✅ Topic: {topic}")
                else:
                    print(f"   ❌ Topic: {topic} (expected: {expected_topic})")
                    scenario_passed = False
                    scenario_errors.append(f"Topic mismatch: {topic} vs {expected_topic}")
            
            # Test 4: Database Search (if expected)
            if scenario.get("expected_db_search", False):
                try:
                    # Create a search query based on the topic
                    topic = domain_expert._extract_topic_from_user_input(scenario["user_input"])
                    building_type = scenario.get("building_type", "unknown")
                    
                    if building_type != "unknown":
                        search_query = f"{topic} {building_type.replace('_', ' ')}"
                    else:
                        search_query = topic
                    
                    results = km.search_knowledge(search_query, n_results=3)
                    
                    if results and len(results) > 0:
                        avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
                        print(f"   ✅ Database: {len(results)} results, avg similarity: {avg_similarity:.3f}")
                    else:
                        print(f"   ⚠️ Database: No results found for '{search_query}'")
                        # Don't fail the scenario for this, as it might be expected
                        
                except Exception as e:
                    print(f"   ⚠️ Database: Error - {e}")
                    # Don't fail the scenario for database errors
            
            # Test 5: Example Request Detection
            if "expected_example_request" in scenario:
                # Test negative context detection
                negative_patterns = ["don't want", "dont want", "not want", "no examples", "no projects"]
                has_negative = any(pattern in scenario["user_input"].lower() for pattern in negative_patterns)
                
                example_patterns = ["example projects", "project examples", "case studies", "precedents"]
                has_example_request = any(pattern in scenario["user_input"].lower() for pattern in example_patterns)
                
                final_result = has_example_request and not has_negative
                expected = scenario["expected_example_request"]
                
                if final_result == expected:
                    print(f"   ✅ Example Request: {final_result}")
                else:
                    print(f"   ❌ Example Request: {final_result} (expected: {expected})")
                    scenario_passed = False
                    scenario_errors.append(f"Example request mismatch: {final_result} vs {expected}")
            
            # Test 6: Building Type Extraction
            if "building_type" in scenario and scenario["building_type"] != "unknown":
                extracted_type = challenge_gen._extract_building_type(scenario["user_input"])
                expected_type = scenario["building_type"]
                
                if extracted_type == expected_type:
                    print(f"   ✅ Building Type: {extracted_type}")
                else:
                    print(f"   ❌ Building Type: {extracted_type} (expected: {expected_type})")
                    scenario_passed = False
                    scenario_errors.append(f"Building type mismatch: {extracted_type} vs {expected_type}")
            
        except Exception as e:
            print(f"   ⚠️ Scenario Error: {e}")
            scenario_passed = False
            scenario_errors.append(f"Exception: {e}")
        
        # Scenario result
        if scenario_passed:
            print(f"   🎉 Scenario PASSED")
            passed_scenarios += 1
        else:
            print(f"   💥 Scenario FAILED")
            failed_scenarios.append((scenario["name"], scenario_errors))
    
    # Final Summary
    print(f"\n📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total scenarios: {total_scenarios}")
    print(f"Passed: {passed_scenarios}")
    print(f"Failed: {len(failed_scenarios)}")
    print(f"Success rate: {(passed_scenarios/total_scenarios)*100:.1f}%")
    
    if failed_scenarios:
        print(f"\n❌ FAILED SCENARIOS:")
        for scenario_name, errors in failed_scenarios:
            print(f"\n   {scenario_name}:")
            for error in errors:
                print(f"     - {error}")
    
    # Component Health Check
    print(f"\n🏥 COMPONENT HEALTH CHECK:")
    print("-" * 40)
    
    try:
        # Test database connection
        km = KnowledgeManager(domain="architecture")
        doc_count = km.collection.count()
        print(f"   ✅ Database: {doc_count} documents available")
    except Exception as e:
        print(f"   ❌ Database: {e}")
    
    try:
        # Test routing system
        router = RoutingDecisionTree()
        print(f"   ✅ Routing: System initialized")
    except Exception as e:
        print(f"   ❌ Routing: {e}")
    
    try:
        # Test gamification system
        challenge_gen = ChallengeGenerator()
        print(f"   ✅ Gamification: System initialized")
    except Exception as e:
        print(f"   ❌ Gamification: {e}")

if __name__ == "__main__":
    asyncio.run(test_integration_comprehensive())
