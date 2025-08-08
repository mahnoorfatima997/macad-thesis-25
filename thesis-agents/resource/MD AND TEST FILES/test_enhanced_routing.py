#!/usr/bin/env python3
"""
Test script for enhanced routing decision tree functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext, RoutingDecision
from state_manager import ArchMentorState, StudentProfile, VisualArtifact, DesignPhase

def test_enhanced_routing():
    """Test the enhanced routing decision tree with better intent classification"""
    
    print("🧪 Testing Enhanced Routing Decision Tree")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Create routing decision tree
    routing_tree = AdvancedRoutingDecisionTree()
    
    # Test cases with different user intents
    test_cases = [
        {
            "name": "Cognitive Offloading Detection",
            "user_input": "Just tell me exactly what to design for my community center",
            "expected_intent": "cognitive_offloading",
            "expected_route": "cognitive_intervention"
        },
        {
            "name": "Knowledge Request",
            "user_input": "What are the key principles for designing accessible spaces?",
            "expected_intent": "knowledge_request",
            "expected_route": "knowledge_only"
        },
        {
            "name": "Design Problem",
            "user_input": "I'm having trouble with the circulation flow in my community center",
            "expected_intent": "design_problem",
            "expected_route": "socratic_exploration"
        },
        {
            "name": "Implementation Request",
            "user_input": "How do I calculate the required square footage for my project?",
            "expected_intent": "implementation_request",
            "expected_route": "knowledge_with_challenge"
        },
        {
            "name": "Evaluation Request",
            "user_input": "Is this layout good for a community center?",
            "expected_intent": "evaluation_request",
            "expected_route": "multi_agent_comprehensive"
        },
        {
            "name": "Creative Exploration",
            "user_input": "What if I try a different approach to the entrance design?",
            "expected_intent": "creative_exploration",
            "expected_route": "socratic_exploration"
        }
    ]
    
    # Create a test context
    student_profile = StudentProfile(
        skill_level="beginner",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.8
    )
    
    visual_artifacts = []
    
    state = ArchMentorState(
        student_profile=student_profile,
        visual_artifacts=visual_artifacts,
        design_phase=DesignPhase.IDEATION,
        messages=[
            {"role": "user", "content": "I want to design a community center for adaptive reuse"},
            {"role": "assistant", "content": "Great! Adaptive reuse is an excellent approach."}
        ]
    )
    
    print("\n🔍 Test 1: Intent Classification")
    print("-" * 30)
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Input: {test_case['user_input']}")
        
        # Create routing context
        context = RoutingContext(
            classification={
                "user_input": test_case['user_input'],
                "interaction_type": "general_question",
                "understanding_level": "medium",
                "confidence_level": "confident",
                "engagement_level": "high"
            },
            context_analysis={
                "cognitive_state": "engaged",
                "learning_progression": "active"
            },
            routing_suggestions={
                "confidence": 0.7,
                "primary_route": "balanced_guidance"
            },
            project_context={
                "building_type": "community",
                "project_scope": "adaptive reuse"
            }
        )
        
        # Test intent classification
        user_intent = routing_tree.classify_user_intent(test_case['user_input'], context)
        print(f"   Expected Intent: {test_case['expected_intent']}")
        print(f"   Actual Intent: {user_intent}")
        print(f"   ✅ Intent Match: {user_intent == test_case['expected_intent']}")
        
        # Test routing decision
        decision = routing_tree.decide_route(context)
        print(f"   Expected Route: {test_case['expected_route']}")
        print(f"   Actual Route: {decision.route.value}")
        print(f"   ✅ Route Match: {decision.route.value == test_case['expected_route']}")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Rule Applied: {decision.rule_applied}")
    
    # Test 2: Context Keyword Extraction
    print("\n🔍 Test 2: Context Keyword Extraction")
    print("-" * 30)
    
    test_input = "I need help with the structural design and lighting for my adaptive reuse community center"
    keywords = routing_tree._extract_context_keywords(test_input)
    
    print(f"Input: {test_input}")
    print(f"Extracted Keywords: {keywords}")
    
    expected_categories = ["architectural_elements", "technical_aspects", "project_types"]
    found_categories = list(keywords.keys())
    
    print(f"Expected Categories: {expected_categories}")
    print(f"Found Categories: {found_categories}")
    print(f"✅ Keyword Extraction: {len(keywords) > 0}")
    
    # Test 3: Pure Knowledge Request Detection
    print("\n🔍 Test 3: Pure Knowledge Request Detection")
    print("-" * 30)
    
    pure_knowledge_tests = [
        {
            "input": "What are the best practices for sustainable design?",
            "expected": True,
            "description": "Pure knowledge request"
        },
        {
            "input": "How should I approach the lighting design for my project?",
            "expected": False,
            "description": "Knowledge with guidance request"
        },
        {
            "input": "Can you show me examples of community centers?",
            "expected": True,
            "description": "Pure example request"
        }
    ]
    
    for test in pure_knowledge_tests:
        classification = {"user_input": test["input"]}
        is_pure = routing_tree._is_pure_knowledge_request(classification, context)
        
        print(f"Input: {test['input']}")
        print(f"Expected: {test['expected']}")
        print(f"Actual: {is_pure}")
        print(f"✅ Match: {is_pure == test['expected']}")
        print(f"Description: {test['description']}")
        print()
    
    print("\n🎉 Enhanced Routing Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_enhanced_routing() 