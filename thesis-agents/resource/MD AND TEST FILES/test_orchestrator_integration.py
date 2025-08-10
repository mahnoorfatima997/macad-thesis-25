#!/usr/bin/env python3
"""
Test script for orchestrator integration with AdvancedRoutingDecisionTree
"""

import sys
import os
from dotenv import load_dotenv

# Add the thesis-agents directory to the path
thesis_agents_path = os.path.join(os.path.dirname(__file__), 'thesis-agents')
sys.path.append(thesis_agents_path)

# Load environment variables
load_dotenv('.env')

from orchestration.langgraph_orchestrator import LangGraphOrchestrator
from state_manager import ArchMentorState, StudentProfile, DesignPhase
from utils.routing_decision_tree import RoutingContext, RouteType

def test_orchestrator_integration():
    """Test the orchestrator integration with AdvancedRoutingDecisionTree"""
    
    print("🧪 Testing Orchestrator Integration with AdvancedRoutingDecisionTree")
    print("=" * 70)
    
    try:
        # Initialize the orchestrator
        print("1. Initializing orchestrator...")
        orchestrator = LangGraphOrchestrator(domain="architecture")
        print("✅ Orchestrator initialized successfully")
        
        # Test that the routing decision tree is properly initialized
        print("\n2. Testing routing decision tree initialization...")
        if hasattr(orchestrator, 'routing_decision_tree'):
            print("✅ AdvancedRoutingDecisionTree is initialized")
        else:
            print("❌ AdvancedRoutingDecisionTree not found")
            return False
        
        # Test routing decision tree functionality
        print("\n3. Testing routing decision tree functionality...")
        routing_tree = orchestrator.routing_decision_tree
        
        # Create a test routing context
        test_classification = {
            "interaction_type": "example_request",
            "confidence_level": "confident",
            "understanding_level": "medium",
            "engagement_level": "high",
            "last_message": "Can you show me some examples of sustainable architecture?"
        }
        
        test_context_analysis = {
            "conversation_patterns": {
                "recent_messages": ["Hello", "I'm working on a project"],
                "repetitive_topics": False
            }
        }
        
        test_routing_suggestions = {
            "primary_route": "knowledge_only",
            "confidence": 0.8,
            "reasoning": ["User requested examples", "Clear knowledge request"]
        }
        
        test_context = RoutingContext(
            classification=test_classification,
            context_analysis=test_context_analysis,
            routing_suggestions=test_routing_suggestions,
            student_state=None,
            conversation_history=[],
            current_phase="ideation",
            phase_progress=0.0
        )
        
        # Test the routing decision
        decision = routing_tree.decide_route(test_context)
        print(f"✅ Routing decision made: {decision.route.value}")
        print(f"   Reason: {decision.reason}")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Rule Applied: {decision.rule_applied}")
        
        # Test the orchestrator's route_decision method
        print("\n4. Testing orchestrator's route_decision method...")
        
        # Create a mock WorkflowState
        mock_student_state = ArchMentorState(
            student_profile=StudentProfile(
                skill_level="beginner",
                learning_style="visual",
                cognitive_load=0.3,
                engagement_level=0.7
            ),
            messages=[],
            current_design_brief="Community Center Project",
            design_phase=DesignPhase.IDEATION,
            visual_artifacts=[],
            domain="architecture"
        )
        
        mock_state = {
            "student_state": mock_student_state,
            "last_message": "Can you show me some examples of sustainable architecture?",
            "student_classification": test_classification,
            "context_analysis": test_context_analysis,
            "routing_suggestions": test_routing_suggestions,
            "routing_decision": {}
        }
        
        # Test the route_decision method
        route_result = orchestrator.route_decision(mock_state)
        print(f"✅ Route decision result: {route_result}")
        
        # Check if detailed routing decision was stored
        if "detailed_routing_decision" in mock_state:
            detailed_decision = mock_state["detailed_routing_decision"]
            print(f"✅ Detailed routing decision stored:")
            print(f"   Route: {detailed_decision['route']}")
            print(f"   Reason: {detailed_decision['reason']}")
            print(f"   Confidence: {detailed_decision['confidence']:.2f}")
            print(f"   Rule Applied: {detailed_decision['rule_applied']}")
        else:
            print("❌ Detailed routing decision not stored")
            return False
        
        # Test the reasoning method
        print("\n5. Testing routing reasoning method...")
        reasoning = orchestrator._generate_routing_reasoning(
            route_result, 
            test_routing_suggestions, 
            test_classification
        )
        print(f"✅ Routing reasoning: {reasoning}")
        
        # Test different routing scenarios
        print("\n6. Testing different routing scenarios...")
        
        # Test cognitive intervention scenario
        cognitive_classification = {
            "interaction_type": "feedback_request",
            "confidence_level": "overconfident",
            "understanding_level": "low",
            "engagement_level": "low",
            "last_message": "Just tell me the answer"
        }
        
        cognitive_context = RoutingContext(
            classification=cognitive_classification,
            context_analysis=test_context_analysis,
            routing_suggestions={},
            student_state=None,
            conversation_history=[],
            current_phase="ideation",
            phase_progress=0.0
        )
        
        cognitive_decision = routing_tree.decide_route(cognitive_context)
        print(f"✅ Cognitive intervention scenario: {cognitive_decision.route.value}")
        print(f"   Reason: {cognitive_decision.reason}")
        
        # Test progressive conversation scenario
        progressive_classification = {
            "interaction_type": "first_message",
            "confidence_level": "uncertain",
            "understanding_level": "low",
            "engagement_level": "medium",
            "last_message": "Hello, I'm starting a new project",
            "is_first_message": True
        }
        
        progressive_context = RoutingContext(
            classification=progressive_classification,
            context_analysis=test_context_analysis,
            routing_suggestions={},
            student_state=None,
            conversation_history=[],
            current_phase="ideation",
            phase_progress=0.0
        )
        
        progressive_decision = routing_tree.decide_route(progressive_context)
        print(f"✅ Progressive conversation scenario: {progressive_decision.route.value}")
        print(f"   Reason: {progressive_decision.reason}")
        
        print("\n🎉 All tests passed! Orchestrator integration successful.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_orchestrator_integration()
    if success:
        print("\n✅ Orchestrator integration test completed successfully!")
    else:
        print("\n❌ Orchestrator integration test failed!")
        sys.exit(1) 