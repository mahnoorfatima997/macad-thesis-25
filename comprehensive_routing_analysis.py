#!/usr/bin/env python3
"""
COMPREHENSIVE ROUTING SYSTEM ANALYSIS & TEST SUITE
==================================================

This script provides:
1. Complete routing analysis (routes → agents → interaction types → responses)
2. Comprehensive test suite for all routes and scenarios
3. Response quality analysis
4. Performance metrics

Usage: python comprehensive_routing_analysis.py
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the thesis-agents directory to the path
sys.path.append('thesis-agents')

# ============================================================================
# ROUTING SYSTEM ANALYSIS
# ============================================================================

ROUTING_ANALYSIS = {
    "routes_to_agents": {
        "progressive_opening": "synthesizer",
        "topic_transition": "synthesizer", 
        "cognitive_intervention": "cognitive_enhancement",
        "socratic_exploration": "socratic_tutor",
        "design_guidance": "analysis_agent",  # Updated to analysis_agent
        "multi_agent_comprehensive": "analysis_agent",
        "knowledge_with_challenge": "domain_expert",
        "socratic_clarification": "socratic_tutor",
        "supportive_scaffolding": "socratic_tutor",
        "cognitive_challenge": "cognitive_enhancement",
        "foundational_building": "socratic_tutor",
        "balanced_guidance": "analysis_agent",
        "knowledge_only": "domain_expert",
        "socratic_focus": "analysis_agent",
        "default": "analysis_agent"
    },
    
    "interaction_types_to_routes": {
        "cognitive_offloading": "cognitive_intervention",
        "overconfident_statement": "cognitive_challenge", 
        "topic_transition": "topic_transition",
        "improvement_seeking": "balanced_guidance",  # Updated from socratic_exploration
        "creative_exploration": "socratic_exploration",
        "knowledge_request": "knowledge_only",
        "example_request": "knowledge_only",
        "evaluation_request": "multi_agent_comprehensive",
        "feedback_request": "multi_agent_comprehensive",
        "design_problem": "balanced_guidance",
        "confusion_expression": "socratic_clarification",
        "general_statement": "balanced_guidance"
    },
    
    "gamified_behaviors": {
        "visual_choice_reasoning": ["improvement_seeking", "creative_exploration"],
        "constraint_storm_challenge": ["cognitive_challenge"],
        "progressive_revelation": ["knowledge_with_challenge"],
        "adaptive_scaffolding": ["supportive_scaffolding"],
        "metacognitive_reflection": ["cognitive_intervention"]
    },
    
    "expected_response_types": {
        "knowledge_only": "Direct knowledge delivery with examples",
        "socratic_exploration": "Questions and guided discovery",
        "cognitive_challenge": "Challenging questions and constraints",
        "multi_agent_comprehensive": "Multi-perspective analysis",
        "balanced_guidance": "Balanced advice with gentle exploration",
        "cognitive_intervention": "Metacognitive reflection prompts",
        "supportive_scaffolding": "Supportive guidance with encouragement"
    }
}

# ============================================================================
# TEST SCENARIOS
# ============================================================================

TEST_SCENARIOS = [
    {
        "name": "Kindergarten Spatial Organization",
        "user_input": "what else can I do to decide about the spatial organization of this building?",
        "design_brief": "I am designing a kindergarten and learning center for children in Copenhagen",
        "expected_intent": "improvement_seeking",
        "expected_route": "balanced_guidance",
        "expected_agent": "analysis_agent",
        "expected_gamified_behavior": "visual_choice_reasoning",
        "building_type": "kindergarten"
    },
    {
        "name": "Pure Knowledge Request",
        "user_input": "What are the standard dimensions for classroom spaces?",
        "design_brief": "I am designing a school building",
        "expected_intent": "knowledge_request",
        "expected_route": "knowledge_only",
        "expected_agent": "domain_expert",
        "expected_gamified_behavior": "",
        "building_type": "school"
    },
    {
        "name": "Creative Exploration",
        "user_input": "What if I create a flowing, organic layout instead of traditional rooms?",
        "design_brief": "I am designing a community center",
        "expected_intent": "creative_exploration",
        "expected_route": "socratic_exploration", 
        "expected_agent": "socratic_tutor",
        "expected_gamified_behavior": "visual_choice_reasoning",
        "building_type": "community_center"
    },
    {
        "name": "Overconfident Statement",
        "user_input": "I will just place all the rooms randomly, it doesn't matter much",
        "design_brief": "I am designing an office building",
        "expected_intent": "overconfident_statement",
        "expected_route": "cognitive_challenge",
        "expected_agent": "cognitive_enhancement",
        "expected_gamified_behavior": "constraint_storm_challenge",
        "building_type": "office"
    },
    {
        "name": "Cognitive Offloading",
        "user_input": "Just tell me exactly what to do for the layout",
        "design_brief": "I am designing a residential building",
        "expected_intent": "cognitive_offloading",
        "expected_route": "cognitive_intervention",
        "expected_agent": "cognitive_enhancement",
        "expected_gamified_behavior": "metacognitive_reflection", 
        "building_type": "residential"
    },
    {
        "name": "Evaluation Request",
        "user_input": "Can you evaluate my design approach and give me feedback?",
        "design_brief": "I am designing a library",
        "expected_intent": "evaluation_request",
        "expected_route": "multi_agent_comprehensive",
        "expected_agent": "analysis_agent",
        "expected_gamified_behavior": "",
        "building_type": "library"
    },
    {
        "name": "Confusion Expression",
        "user_input": "I'm confused about how to organize the circulation paths",
        "design_brief": "I am designing a hospital",
        "expected_intent": "confusion_expression",
        "expected_route": "socratic_clarification",
        "expected_agent": "socratic_tutor",
        "expected_gamified_behavior": "adaptive_scaffolding",
        "building_type": "hospital"
    },
    {
        "name": "Design Problem Statement",
        "user_input": "I'm designing the entrance area and considering multiple access points",
        "design_brief": "I am designing a museum",
        "expected_intent": "design_problem",
        "expected_route": "balanced_guidance",
        "expected_agent": "analysis_agent",
        "expected_gamified_behavior": "visual_choice_reasoning",
        "building_type": "museum"
    }
]

# ============================================================================
# COMPREHENSIVE TEST FUNCTIONS
# ============================================================================

async def test_building_type_detection():
    """Test building type detection for all scenarios."""
    print("🏗️ TESTING BUILDING TYPE DETECTION")
    print("=" * 60)
    
    try:
        from state_manager import ArchMentorState
        
        results = []
        for scenario in TEST_SCENARIOS:
            state = ArchMentorState()
            state.current_design_brief = scenario["design_brief"]
            
            detected_type = state.extract_building_type_from_brief_only()
            expected_type = scenario["building_type"]
            
            success = detected_type == expected_type
            results.append({
                "scenario": scenario["name"],
                "expected": expected_type,
                "detected": detected_type,
                "success": success
            })
            
            status = "✅" if success else "❌"
            print(f"{status} {scenario['name']}: {detected_type} (expected: {expected_type})")
        
        success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
        print(f"\n📊 Building Type Detection Success Rate: {success_rate:.1f}%")
        return results
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_intent_classification():
    """Test user intent classification for all scenarios."""
    print("\n🎯 TESTING INTENT CLASSIFICATION")
    print("=" * 60)
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        from state_manager import ArchMentorState
        
        router = AdvancedRoutingDecisionTree()
        results = []
        
        for scenario in TEST_SCENARIOS:
            # Create state
            state = ArchMentorState()
            state.current_design_brief = scenario["design_brief"]
            state.building_type = scenario["building_type"]
            
            # Create routing context
            context = RoutingContext(
                classification={"user_input": scenario["user_input"]},
                context_analysis={},
                routing_suggestions={},
                conversation_history=[],
                user_intent=""
            )
            
            # Test intent classification
            detected_intent = router.classify_user_intent(scenario["user_input"], context)
            expected_intent = scenario["expected_intent"]
            
            success = detected_intent == expected_intent
            results.append({
                "scenario": scenario["name"],
                "expected": expected_intent,
                "detected": detected_intent,
                "success": success
            })
            
            status = "✅" if success else "❌"
            print(f"{status} {scenario['name']}: {detected_intent} (expected: {expected_intent})")
        
        success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
        print(f"\n📊 Intent Classification Success Rate: {success_rate:.1f}%")
        return results

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_routing_decisions():
    """Test routing decisions for all scenarios."""
    print("\n🛤️ TESTING ROUTING DECISIONS")
    print("=" * 60)

    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        from state_manager import ArchMentorState

        router = AdvancedRoutingDecisionTree()
        results = []

        for scenario in TEST_SCENARIOS:
            # Create state
            state = ArchMentorState()
            state.current_design_brief = scenario["design_brief"]
            state.building_type = scenario["building_type"]

            # Create routing context
            context = RoutingContext(
                classification={
                    "user_input": scenario["user_input"],
                    "interaction_type": scenario["expected_intent"],
                    "engagement_level": "high",
                    "confidence_level": "confident"
                },
                context_analysis={},
                routing_suggestions={},
                conversation_history=[],
                user_intent=scenario["expected_intent"]
            )

            # Test routing decision
            decision = router.decide_route(context)
            detected_route = str(decision.route).split('.')[-1].lower()
            expected_route = scenario["expected_route"]

            success = expected_route in detected_route
            results.append({
                "scenario": scenario["name"],
                "expected": expected_route,
                "detected": detected_route,
                "success": success,
                "reason": decision.reason
            })

            status = "✅" if success else "❌"
            print(f"{status} {scenario['name']}: {detected_route} (expected: {expected_route})")
            print(f"   Reason: {decision.reason}")

        success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
        print(f"\n📊 Routing Decision Success Rate: {success_rate:.1f}%")
        return results

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_agent_responses():
    """Test actual agent responses for key scenarios."""
    print("\n🤖 TESTING AGENT RESPONSES")
    print("=" * 60)

    results = []

    # Test key scenarios with different agents
    key_scenarios = [
        TEST_SCENARIOS[0],  # Kindergarten - balanced_guidance
        TEST_SCENARIOS[1],  # Knowledge request - knowledge_only
        TEST_SCENARIOS[2],  # Creative exploration - socratic_exploration
        TEST_SCENARIOS[4],  # Cognitive offloading - cognitive_intervention
    ]

    for scenario in key_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print("-" * 40)

        try:
            # Create state
            from state_manager import ArchMentorState
            state = ArchMentorState()
            state.current_design_brief = scenario["design_brief"]
            state.building_type = scenario["building_type"]
            state.messages = [
                {"role": "user", "content": scenario["design_brief"]},
                {"role": "user", "content": scenario["user_input"]}
            ]

            # Test based on expected agent
            expected_agent = scenario["expected_agent"]
            response = None

            if expected_agent == "domain_expert":
                from agents.domain_expert.adapter import DomainExpertAgent
                agent = DomainExpertAgent()

                context_classification = {
                    "interaction_type": scenario["expected_intent"],
                    "primary_gap": "knowledge_request",
                    "engagement_level": "high"
                }

                analysis_result = {
                    "building_type": scenario["building_type"],
                    "user_intent": scenario["expected_intent"]
                }

                routing_decision = {
                    "route": scenario["expected_route"],
                    "reason": f"Test scenario for {scenario['name']}"
                }

                response = await agent.provide_knowledge(
                    state, context_classification, analysis_result, routing_decision
                )

            elif expected_agent == "socratic_tutor":
                from agents.socratic_tutor.adapter import SocraticTutorAgent
                agent = SocraticTutorAgent()

                context_classification = {
                    "interaction_type": scenario["expected_intent"],
                    "primary_gap": "creative_exploration",
                    "engagement_level": "high",
                    "confidence_level": "confident",
                    "gamified_behavior": scenario.get("expected_gamified_behavior", "")
                }

                analysis_result = {
                    "building_type": scenario["building_type"],
                    "user_intent": scenario["expected_intent"]
                }

                response = await agent.provide_guidance(
                    state, context_classification, analysis_result, scenario["expected_route"]
                )

            elif expected_agent == "cognitive_enhancement":
                from agents.cognitive_enhancement.adapter import CognitiveEnhancementAgent
                agent = CognitiveEnhancementAgent()

                context_classification = {
                    "interaction_type": scenario["expected_intent"],
                    "cognitive_offloading_detected": True,
                    "engagement_level": "high"
                }

                analysis_result = {
                    "building_type": scenario["building_type"],
                    "user_intent": scenario["expected_intent"]
                }

                response = await agent.provide_challenge(
                    state, context_classification, analysis_result, {}
                )

            elif expected_agent == "analysis_agent":
                from agents.analysis_agent.adapter import AnalysisAgent
                agent = AnalysisAgent()

                # Analysis agent uses process method
                response = await agent.process(state)

            # Analyze response
            if response:
                response_text = response.response_text
                response_length = len(response_text)

                # Check for expected response characteristics
                expected_type = ROUTING_ANALYSIS["expected_response_types"].get(scenario["expected_route"], "")

                quality_indicators = {
                    "has_questions": "?" in response_text,
                    "has_choices": any(choice in response_text.lower() for choice in ["a)", "b)", "c)", "option", "choice"]),
                    "building_specific": scenario["building_type"] in response_text.lower(),
                    "contextual": any(word in response_text.lower() for word in ["spatial", "organization", "design", "layout"]),
                    "appropriate_length": 100 < response_length < 1000
                }

                quality_score = sum(quality_indicators.values()) / len(quality_indicators) * 100

                results.append({
                    "scenario": scenario["name"],
                    "agent": expected_agent,
                    "route": scenario["expected_route"],
                    "response_length": response_length,
                    "quality_score": quality_score,
                    "quality_indicators": quality_indicators,
                    "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                })

                print(f"✅ Agent: {expected_agent}")
                print(f"📏 Response length: {response_length} chars")
                print(f"⭐ Quality score: {quality_score:.1f}%")
                print(f"📝 Preview: {response_text[:100]}...")

            else:
                print(f"❌ No response generated")
                results.append({
                    "scenario": scenario["name"],
                    "agent": expected_agent,
                    "route": scenario["expected_route"],
                    "response_length": 0,
                    "quality_score": 0,
                    "error": "No response generated"
                })

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "scenario": scenario["name"],
                "agent": scenario["expected_agent"],
                "route": scenario["expected_route"],
                "error": str(e)
            })

    # Calculate overall metrics
    successful_responses = [r for r in results if "error" not in r and r.get("quality_score", 0) > 0]
    if successful_responses:
        avg_quality = sum(r["quality_score"] for r in successful_responses) / len(successful_responses)
        avg_length = sum(r["response_length"] for r in successful_responses) / len(successful_responses)
        print(f"\n📊 Response Quality Metrics:")
        print(f"   Average Quality Score: {avg_quality:.1f}%")
        print(f"   Average Response Length: {avg_length:.0f} chars")
        print(f"   Success Rate: {len(successful_responses)}/{len(results)} ({len(successful_responses)/len(results)*100:.1f}%)")

    return results

async def generate_comprehensive_report():
    """Generate comprehensive routing analysis report."""
    print("\n📋 GENERATING COMPREHENSIVE ROUTING REPORT")
    print("=" * 70)

    # Print routing analysis
    print("\n🗺️ ROUTING SYSTEM MAPPING")
    print("-" * 40)
    print("Route → Agent Mapping:")
    for route, agent in ROUTING_ANALYSIS["routes_to_agents"].items():
        print(f"  {route} → {agent}")

    print("\nInteraction Type → Route Mapping:")
    for interaction, route in ROUTING_ANALYSIS["interaction_types_to_routes"].items():
        print(f"  {interaction} → {route}")

    print("\nGamified Behaviors:")
    for behavior, interactions in ROUTING_ANALYSIS["gamified_behaviors"].items():
        print(f"  {behavior}: {', '.join(interactions)}")

    # Run all tests
    building_results = await test_building_type_detection()
    intent_results = await test_intent_classification()
    routing_results = await test_routing_decisions()
    response_results = await test_agent_responses()

    # Generate summary report
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)

    total_tests = len(TEST_SCENARIOS)

    if building_results:
        building_success = sum(1 for r in building_results if r["success"]) / len(building_results) * 100
        print(f"🏗️ Building Type Detection: {building_success:.1f}% ({sum(1 for r in building_results if r['success'])}/{len(building_results)})")

    if intent_results:
        intent_success = sum(1 for r in intent_results if r["success"]) / len(intent_results) * 100
        print(f"🎯 Intent Classification: {intent_success:.1f}% ({sum(1 for r in intent_results if r['success'])}/{len(intent_results)})")

    if routing_results:
        routing_success = sum(1 for r in routing_results if r["success"]) / len(routing_results) * 100
        print(f"🛤️ Routing Decisions: {routing_success:.1f}% ({sum(1 for r in routing_results if r['success'])}/{len(routing_results)})")

    if response_results:
        response_success = len([r for r in response_results if "error" not in r]) / len(response_results) * 100
        print(f"🤖 Agent Responses: {response_success:.1f}% ({len([r for r in response_results if 'error' not in r])}/{len(response_results)})")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_data = {
        "timestamp": timestamp,
        "routing_analysis": ROUTING_ANALYSIS,
        "test_scenarios": TEST_SCENARIOS,
        "results": {
            "building_type_detection": building_results,
            "intent_classification": intent_results,
            "routing_decisions": routing_results,
            "agent_responses": response_results
        }
    }

    report_filename = f"routing_analysis_report_{timestamp}.json"
    with open(report_filename, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)

    print(f"\n💾 Detailed report saved to: {report_filename}")

    # Overall system health
    all_success_rates = []
    if building_results:
        all_success_rates.append(sum(1 for r in building_results if r["success"]) / len(building_results) * 100)
    if intent_results:
        all_success_rates.append(sum(1 for r in intent_results if r["success"]) / len(intent_results) * 100)
    if routing_results:
        all_success_rates.append(sum(1 for r in routing_results if r["success"]) / len(routing_results) * 100)
    if response_results:
        all_success_rates.append(len([r for r in response_results if "error" not in r]) / len(response_results) * 100)

    if all_success_rates:
        overall_health = sum(all_success_rates) / len(all_success_rates)
        print(f"\n🎯 OVERALL SYSTEM HEALTH: {overall_health:.1f}%")

        if overall_health >= 90:
            print("🎉 EXCELLENT - System is performing very well!")
        elif overall_health >= 75:
            print("✅ GOOD - System is performing well with minor issues")
        elif overall_health >= 60:
            print("⚠️ FAIR - System needs attention in some areas")
        else:
            print("❌ POOR - System requires significant improvements")

    return report_data

async def main():
    """Run comprehensive routing analysis and testing."""
    print("🚀 COMPREHENSIVE ROUTING SYSTEM ANALYSIS & TEST SUITE")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Test scenarios: {len(TEST_SCENARIOS)}")
    print(f"🛤️ Routes analyzed: {len(ROUTING_ANALYSIS['routes_to_agents'])}")
    print(f"🎯 Interaction types: {len(ROUTING_ANALYSIS['interaction_types_to_routes'])}")

    try:
        report_data = await generate_comprehensive_report()
        return report_data
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(main())
