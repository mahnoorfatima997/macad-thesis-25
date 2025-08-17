#!/usr/bin/env python3
"""
Comprehensive Routing Test Script
Tests each route type to identify where the override is happening.
"""

import os
import asyncio
import json
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Add the thesis-agents folder to the Python path
sys.path.append('thesis-agents')

# Load environment variables
load_dotenv()

# Test cases for each route type
TEST_CASES = {
    "knowledge_only": [
        "can you provide examples of sustainable building materials?",
        "show me case studies of modern office buildings",
        "give me examples of passive solar design",
        "what are some precedents for green roofs?",
        "can you show me projects using bamboo construction?"
    ],
    
    "supportive_scaffolding": [
        "I'm not sure how to start my residential project",
        "I feel confused about the zoning requirements",
        "I need help understanding building codes",
        "I'm stuck on the floor plan layout",
        "I don't know how to approach the site analysis"
    ],
    
    "socratic_exploration": [
        "How might I integrate natural light into my design?",
        "What factors should I consider for the building orientation?",
        "How can I make the space more accessible?",
        "What would be the best approach for the circulation?",
        "How might the local climate influence my material choices?"
    ],
    
    "progressive_opening": [
        "I want to design a hospital",
        "I'm starting a new commercial project",
        "I need to create a museum design",
        "I want to build a sustainable home",
        "I'm designing a school building"
    ]
}

async def test_routing_decision_tree():
    """Test the routing decision tree directly."""
    print("🔍 Testing Routing Decision Tree Directly...")
    
    try:
        # Import the routing decision tree
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree
        
        print("✅ Successfully imported AdvancedRoutingDecisionTree")
        
        # Create instance
        router = AdvancedRoutingDecisionTree()
        
        # Test each route type
        for route_type, test_cases in TEST_CASES.items():
            print(f"\n📋 Testing {route_type.upper()} route:")
            
            for i, test_input in enumerate(test_cases, 1):
                print(f"  {i}. Input: {test_input[:60]}...")
                
                # Mock context for testing
                mock_context = type('MockContext', (), {
                    "building_type": "mixed_use",
                    "complexity_level": "intermediate",
                    "user_level": "intermediate",
                    "user_input": test_input,
                    "classification": {
                        "interaction_type": "example_request" if "example" in test_input.lower() else "general_question",
                        "user_input": test_input,
                        "understanding_level": "intermediate",
                        "confidence_level": "confident",
                        "engagement_level": "high"
                    },
                    "context_analysis": {},
                    "routing_suggestions": {},
                    "student_state": {},
                    "conversation_history": [],
                    "current_phase": "ideation",
                    "phase_progress": 0.0,
                    "project_context": {},
                    "user_intent": "unknown",
                    "cognitive_state": {}
                })()
                
                try:
                    # Call the routing decision tree directly
                    route_decision = router.decide_route(mock_context)
                    
                    print(f"     Route: {route_decision.route.value if hasattr(route_decision, 'route') else 'UNKNOWN'}")
                    print(f"     Reasoning: {route_decision.reason if hasattr(route_decision, 'reason') else 'NO REASONING'}")
                    
                    # Check if routing is correct
                    expected_route = route_type
                    actual_route = route_decision.route.value if hasattr(route_decision, 'route') else 'UNKNOWN'
                    
                    if actual_route == expected_route:
                        print(f"     ✅ CORRECT ROUTING")
                    else:
                        print(f"     ❌ WRONG ROUTING - Expected: {expected_route}, Got: {actual_route}")
                        
                except Exception as e:
                    print(f"     ❌ ERROR: {e}")
                    
    except ImportError as e:
        print(f"❌ Could not import RoutingDecisionTree: {e}")
        return False
    
    return True

async def test_context_agent_classification():
    """Test the context agent's input classification."""
    print("\n🔍 Testing Context Agent Input Classification...")
    
    try:
        # Import the context agent
        from agents.context_agent.processors.input_classification import InputClassificationProcessor
        
        print("✅ Successfully imported InputClassificationProcessor")
        
        processor = InputClassificationProcessor()
        
        # Test each route type
        for route_type, test_cases in TEST_CASES.items():
            print(f"\n📋 Testing {route_type.upper()} classification:")
            
            for i, test_input in enumerate(test_cases, 1):
                print(f"  {i}. Input: {test_input[:60]}...")
                
                try:
                    # Call the classification directly
                    classification = processor._classify_interaction_type(test_input)
                    
                    print(f"     Classification: {classification}")
                    
                    # Check if classification makes sense for the route
                    if route_type == "knowledge_only" and "example" in test_input.lower():
                        if "example_request" in classification:
                            print(f"     ✅ CORRECT CLASSIFICATION")
                        else:
                            print(f"     ❌ WRONG CLASSIFICATION - Expected example_request")
                            
                except Exception as e:
                    print(f"     ❌ ERROR: {e}")
                    
    except ImportError as e:
        print(f"❌ Could not import InputClassificationProcessor: {e}")
        return False
    
    return True

async def test_socratic_tutor_routing():
    """Test the Socratic tutor's routing logic."""
    print("\n🔍 Testing Socratic Tutor Routing Logic...")
    
    try:
        # Import the Socratic tutor
        from agents.socratic_tutor.adapter import SocraticTutorAgent
        
        print("✅ Successfully imported SocraticTutorAgent")
        
        # Test with different routing paths
        test_routing_paths = [
            "knowledge_only",
            "supportive_scaffolding", 
            "socratic_exploration",
            "progressive_opening"
        ]
        
        for routing_path in test_routing_paths:
            print(f"\n📋 Testing routing_path: {routing_path}")
            
            # Mock state and context
            mock_state = type('MockState', (), {
                'building_type': 'mixed_use',
                'messages': [],
                'current_design_brief': 'test project'
            })()
            
            mock_context = {
                'interaction_type': 'design_guidance_request',
                'understanding_level': 'intermediate',
                'routing_path': routing_path
            }
            
            mock_analysis = {}
            mock_gap_type = 'knowledge_gap'
            
            try:
                # Create agent instance
                agent = SocraticTutorAgent()
                
                # Test the routing logic
                if routing_path == "knowledge_only":
                    print(f"  Should call: _generate_knowledge_only_response")
                elif routing_path == "supportive_scaffolding":
                    print(f"  Should call: _generate_supportive_scaffolding_response")
                elif routing_path == "socratic_exploration":
                    print(f"  Should call: _generate_adaptive_socratic_response")
                else:
                    print(f"  Should call: _generate_adaptive_socratic_response (default)")
                    
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                
    except ImportError as e:
        print(f"❌ Could not import SocraticTutorAgent: {e}")
        return False
    
    return True

async def test_orchestrator_routing():
    """Test the orchestrator's routing logic."""
    print("\n🔍 Testing Orchestrator Routing Logic...")
    
    try:
        # Import the orchestrator
        from orchestration.orchestrator import LangGraphOrchestrator
        
        print("✅ Successfully imported LangGraphOrchestrator")
        
        # Test routing decision flow
        print("📋 Testing routing decision flow:")
        
        # Mock workflow state
        mock_state = {
            "student_classification": {
                "interaction_type": "example_request",
                "routing_path": "knowledge_only"
            },
            "routing_decision": {
                "path": "knowledge_only",
                "reasoning": "Pure example request"
            }
        }
        
        print(f"  Mock state routing_path: {mock_state['student_classification'].get('routing_path')}")
        print(f"  Mock routing_decision path: {mock_state['routing_decision'].get('path')}")
        
        # Check if they match
        if mock_state['student_classification'].get('routing_path') == mock_state['routing_decision'].get('path'):
            print("  ✅ Routing paths match")
        else:
            print("  ❌ Routing paths don't match")
            
    except ImportError as e:
        print(f"❌ Could not import LangGraphOrchestrator: {e}")
        return False
    
    return True

async def test_actual_routing_flow():
    """Test the actual routing flow to see where the override happens."""
    print("\n🔍 Testing Actual Routing Flow...")
    
    try:
        # Import the routing decision tree
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree
        from agents.context_agent.processors.input_classification import InputClassificationProcessor
        
        print("✅ Successfully imported routing components")
        
        # Create instances
        router = AdvancedRoutingDecisionTree()
        classifier = InputClassificationProcessor()
        
        # Test a specific problematic case
        test_input = "can you provide examples for the use of outdoor spaces in learning centers?"
        print(f"\n📋 Testing problematic input: {test_input}")
        
        # Step 1: Classify the input
        classification = classifier._classify_interaction_type(test_input)
        print(f"  Step 1 - Classification: {classification}")
        
        # Step 2: Create routing context
        mock_context = type('MockContext', (), {
            "building_type": "mixed_use",
            "complexity_level": "intermediate",
            "user_level": "intermediate",
            "user_input": test_input,
            "classification": {
                "interaction_type": classification,
                "user_input": test_input,
                "understanding_level": "intermediate",
                "confidence_level": "confident",
                "engagement_level": "high"
            },
            "context_analysis": {},
            "routing_suggestions": {},
            "student_state": {},
            "conversation_history": [],
            "current_phase": "ideation",
            "phase_progress": 0.0,
            "project_context": {},
            "user_intent": "unknown",
            "cognitive_state": {}
        })()
        
        # Step 3: Get routing decision
        try:
            route_decision = router.decide_route(mock_context)
            print(f"  Step 2 - Route Decision: {route_decision.route.value if hasattr(route_decision, 'route') else 'UNKNOWN'}")
            print(f"  Step 2 - Reasoning: {route_decision.reason if hasattr(route_decision, 'reason') else 'NO REASONING'}")
        except Exception as e:
            print(f"  Step 2 - ERROR: {e}")
            
    except ImportError as e:
        print(f"❌ Could not import routing components: {e}")
        return False
    
    return True

async def main():
    """Run all routing tests."""
    print("🚀 Starting Comprehensive Routing Tests...")
    print("=" * 60)
    
    # Test 1: Routing Decision Tree
    await test_routing_decision_tree()
    
    # Test 2: Context Agent Classification
    await test_context_agent_classification()
    
    # Test 3: Socratic Tutor Routing
    await test_socratic_tutor_routing()
    
    # Test 4: Orchestrator Routing
    await test_orchestrator_routing()
    
    # Test 5: Actual Routing Flow (Most Important!)
    await test_actual_routing_flow()
    
    print("\n" + "=" * 60)
    print("🏁 Routing Tests Completed!")
    print("\n📊 Next Steps:")
    print("1. Check the test results above")
    print("2. Identify which component is overriding the routing")
    print("3. Fix the routing logic in the identified component")
    print("4. Re-run tests to verify fixes")

if __name__ == "__main__":
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file")
        exit(1)
    
    # Run the tests
    asyncio.run(main())
