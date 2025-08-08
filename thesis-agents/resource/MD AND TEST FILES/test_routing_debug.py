#!/usr/bin/env python3
"""
Test script to debug routing issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('thesis-agents')

from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
from state_manager import ArchMentorState, StudentProfile

def test_routing_with_actual_data():
    """Test routing with the actual classification data from context agent"""
    
    print("🧪 Testing Routing Decision Tree with Actual Data")
    print("=" * 60)
    
    # Initialize the routing decision tree
    routing_tree = AdvancedRoutingDecisionTree()
    
    # Create a test state
    student_profile = StudentProfile(
        skill_level="intermediate",
        learning_style="visual",
        cognitive_load=0.3,
        engagement_level=0.7,
        knowledge_gaps=["site analysis", "sustainability principles"],
        strengths=["design thinking", "spatial awareness"]
    )
    
    state = ArchMentorState(
        student_profile=student_profile,
        messages=[
            {
                "role": "user",
                "content": "I'm working on a community center design and need help with site analysis."
            },
            {
                "role": "assistant", 
                "content": "Great! Let's start by analyzing your site. What are the key characteristics of your location?"
            },
            {
                "role": "user",
                "content": "Hi there, thank you — I'm excited to start this journey too. To begin, the primary purpose of my design is to create a vibrant and inclusive community hub that serves as a shared space for learning, recreation, celebration, and support..."
            }
        ],
        current_design_brief="Design a sustainable community center for an urban neighborhood"
    )
    
    # Test case 1: feedback_request (from terminal logs)
    print("\n1. Testing with feedback_request (from terminal logs)...")
    
    classification_1 = {
        "interaction_type": "feedback_request",
        "understanding_level": "high",
        "confidence_level": "confident",
        "engagement_level": "high",
        "user_input": "Hi there, thank you — I'm excited to start this journey too...",
        "last_message": "Hi there, thank you — I'm excited to start this journey too..."
    }
    
    context_analysis_1 = {
        "complexity_score": 0.8,
        "specificity_score": 0.7,
        "technical_terms": ["community hub", "inclusive", "sustainable"]
    }
    
    routing_suggestions_1 = {
        "primary_route": "balanced_guidance",
        "confidence": 0.6,
        "alternative_routes": ["socratic_exploration", "multi_agent_comprehensive"]
    }
    
    routing_context_1 = RoutingContext(
        classification=classification_1,
        context_analysis=context_analysis_1,
        routing_suggestions=routing_suggestions_1,
        student_state=state.__dict__,
        conversation_history=state.messages,
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_1 = routing_tree.decide_route(routing_context_1)
    
    print(f"✅ Input: feedback_request")
    print(f"   Route: {decision_1.route.value}")
    print(f"   Reason: {decision_1.reason}")
    print(f"   Rule Applied: {decision_1.rule_applied}")
    print(f"   User Intent: {decision_1.user_intent}")
    
    # Test case 2: example_request
    print("\n2. Testing with example_request...")
    
    classification_2 = {
        "interaction_type": "example_request",
        "understanding_level": "medium",
        "confidence_level": "confident",
        "engagement_level": "high",
        "user_input": "Can you give me examples of sustainable community centers?",
        "last_message": "Can you give me examples of sustainable community centers?"
    }
    
    routing_context_2 = RoutingContext(
        classification=classification_2,
        context_analysis=context_analysis_1,
        routing_suggestions=routing_suggestions_1,
        student_state=state.__dict__,
        conversation_history=state.messages,
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_2 = routing_tree.decide_route(routing_context_2)
    
    print(f"✅ Input: example_request")
    print(f"   Route: {decision_2.route.value}")
    print(f"   Reason: {decision_2.reason}")
    print(f"   Rule Applied: {decision_2.rule_applied}")
    print(f"   User Intent: {decision_2.user_intent}")
    
    # Test case 3: knowledge_request
    print("\n3. Testing with knowledge_request...")
    
    classification_3 = {
        "interaction_type": "knowledge_request",
        "understanding_level": "low",
        "confidence_level": "uncertain",
        "engagement_level": "medium",
        "user_input": "What is adaptive reuse?",
        "last_message": "What is adaptive reuse?"
    }
    
    routing_context_3 = RoutingContext(
        classification=classification_3,
        context_analysis=context_analysis_1,
        routing_suggestions=routing_suggestions_1,
        student_state=state.__dict__,
        conversation_history=state.messages,
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_3 = routing_tree.decide_route(routing_context_3)
    
    print(f"✅ Input: knowledge_request")
    print(f"   Route: {decision_3.route.value}")
    print(f"   Reason: {decision_3.reason}")
    print(f"   Rule Applied: {decision_3.rule_applied}")
    print(f"   User Intent: {decision_3.user_intent}")
    
    # Test case 4: technical_question
    print("\n4. Testing with technical_question...")
    
    classification_4 = {
        "interaction_type": "technical_question",
        "understanding_level": "high",
        "confidence_level": "confident",
        "engagement_level": "high",
        "user_input": "What are the technical requirements for a community center?",
        "last_message": "What are the technical requirements for a community center?"
    }
    
    routing_context_4 = RoutingContext(
        classification=classification_4,
        context_analysis=context_analysis_1,
        routing_suggestions=routing_suggestions_1,
        student_state=state.__dict__,
        conversation_history=state.messages,
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_4 = routing_tree.decide_route(routing_context_4)
    
    print(f"✅ Input: technical_question")
    print(f"   Route: {decision_4.route.value}")
    print(f"   Reason: {decision_4.reason}")
    print(f"   Rule Applied: {decision_4.rule_applied}")
    print(f"   User Intent: {decision_4.user_intent}")
    
    # Test case 5: direct_answer_request
    print("\n5. Testing with direct_answer_request...")
    
    classification_5 = {
        "interaction_type": "direct_answer_request",
        "understanding_level": "low",
        "confidence_level": "uncertain",
        "engagement_level": "low",
        "user_input": "Can you design this for me?",
        "last_message": "Can you design this for me?"
    }
    
    routing_context_5 = RoutingContext(
        classification=classification_5,
        context_analysis=context_analysis_1,
        routing_suggestions=routing_suggestions_1,
        student_state=state.__dict__,
        conversation_history=state.messages,
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_5 = routing_tree.decide_route(routing_context_5)
    
    print(f"✅ Input: direct_answer_request")
    print(f"   Route: {decision_5.route.value}")
    print(f"   Reason: {decision_5.reason}")
    print(f"   Rule Applied: {decision_5.rule_applied}")
    print(f"   User Intent: {decision_5.user_intent}")
    
    # Test case 6: question_response
    print("\n6. Testing with question_response...")
    
    classification_6 = {
        "interaction_type": "question_response",
        "understanding_level": "medium",
        "confidence_level": "confident",
        "engagement_level": "high",
        "user_input": "The site is in an urban area with good public transportation access.",
        "last_message": "The site is in an urban area with good public transportation access."
    }
    
    routing_context_6 = RoutingContext(
        classification=classification_6,
        context_analysis=context_analysis_1,
        routing_suggestions=routing_suggestions_1,
        student_state=state.__dict__,
        conversation_history=state.messages,
        current_phase="discovery",
        phase_progress=0.3
    )
    
    decision_6 = routing_tree.decide_route(routing_context_6)
    
    print(f"✅ Input: question_response")
    print(f"   Route: {decision_6.route.value}")
    print(f"   Reason: {decision_6.reason}")
    print(f"   Rule Applied: {decision_6.rule_applied}")
    print(f"   User Intent: {decision_6.user_intent}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"   feedback_request → {decision_1.route.value}")
    print(f"   example_request → {decision_2.route.value}")
    print(f"   knowledge_request → {decision_3.route.value}")
    print(f"   technical_question → {decision_4.route.value}")
    print(f"   direct_answer_request → {decision_5.route.value}")
    print(f"   question_response → {decision_6.route.value}")
    
    # Check if all routes are balanced_guidance
    routes = [decision_1.route.value, decision_2.route.value, decision_3.route.value, 
              decision_4.route.value, decision_5.route.value, decision_6.route.value]
    
    if all(route == "balanced_guidance" for route in routes):
        print("\n❌ PROBLEM: All routes are defaulting to balanced_guidance!")
        print("   This indicates the routing rules are not matching the interaction types.")
    else:
        print(f"\n✅ SUCCESS: Routing is working! Found {len(set(routes))} different routes.")
    
    print("\n✅ Routing debug test completed!")

if __name__ == "__main__":
    test_routing_with_actual_data()
