#!/usr/bin/env python3
"""
COMPREHENSIVE ROUTING SYSTEM TEST
Tests all routing issues identified by the user.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add thesis-agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))

# Load environment variables
load_dotenv()

def test_routing_system():
    """Test the routing system comprehensively"""
    print("🧪 COMPREHENSIVE ROUTING SYSTEM TEST")
    print("=" * 60)
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        from agents.context_agent import ContextAgent
        from agents.analysis_agent import AnalysisAgent
        from state_manager import ArchMentorState
        
        # Initialize components
        routing_tree = AdvancedRoutingDecisionTree()
        context_agent = ContextAgent("architecture")
        analysis_agent = AnalysisAgent("architecture")
        
        print("✅ Components initialized successfully")
        
        # Test cases from user's problems
        test_cases = [
            {
                "name": "PROBLEM 4: Knowledge Request - Circulation",
                "message": "can you guide me about how to create a good circulation inside the building?",
                "expected_route": "knowledge_only",
                "expected_intent": "knowledge_seeking"
            },
            {
                "name": "PROBLEM 5: Best Practices Knowledge",
                "message": "what are the best practices for circulation design in a community center?",
                "expected_route": "knowledge_only",
                "expected_intent": "knowledge_seeking"
            },
            {
                "name": "Technical Question Test",
                "message": "What are ADA door width requirements?",
                "expected_route": "knowledge_only",
                "expected_intent": "technical_question"
            },
            {
                "name": "Confusion Expression Test",
                "message": "looking through someone else's lens is very helpful to consider all user groups with wide range of ages. but I am not sure how to provide a good inner garden strategy for this building. what would be the best idea?",
                "expected_route": "socratic_clarification",
                "expected_intent": "confusion_expression"
            },
            {
                "name": "Design Exploration Test",
                "message": "I'm thinking about how courtyards might create different social dynamics in my hospital design",
                "expected_route": "socratic_exploration",
                "expected_intent": "design_exploration"
            }
        ]
        
        print(f"\n🧪 Testing {len(test_cases)} routing scenarios...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- TEST {i}: {test_case['name']} ---")
            print(f"📝 Message: {test_case['message']}")
            
            # Create mock student state
            student_state = ArchMentorState()
            student_state.messages.append({
                "role": "user",
                "content": test_case['message']
            })
            
            # Test context analysis
            try:
                context_result = asyncio.run(context_agent.analyze_student_input(
                    student_state, test_case['message']
                ))
                print(f"🧠 Context Analysis: {context_result.metadata.get('core_classification', {}).get('interaction_type', 'unknown')}")

                # Create routing context
                routing_context = RoutingContext(
                    classification=context_result.metadata.get('core_classification', {}),
                    context_analysis=context_result.metadata,
                    routing_suggestions=context_result.metadata.get('routing_suggestions', {}),
                    student_state=student_state.__dict__,
                    conversation_history=student_state.messages,
                    current_phase="ideation",
                    phase_progress=0.0
                )
                
                # Test routing decision
                decision = routing_tree.decide_route(routing_context)
                
                print(f"🛣️  Actual Route: {decision.route.value}")
                print(f"🎯 Expected Route: {test_case['expected_route']}")
                print(f"📋 Reason: {decision.reason}")
                print(f"🔍 User Intent: {decision.classification.get('user_intent', 'unknown')}")
                print(f"⚡ Confidence: {decision.confidence:.2f}")
                
                # Check if routing is correct
                route_correct = decision.route.value == test_case['expected_route']
                intent_correct = decision.classification.get('user_intent') == test_case['expected_intent']
                
                if route_correct and intent_correct:
                    print("✅ ROUTING CORRECT")
                else:
                    print("❌ ROUTING FAILED")
                    if not route_correct:
                        print(f"   Route mismatch: got {decision.route.value}, expected {test_case['expected_route']}")
                    if not intent_correct:
                        print(f"   Intent mismatch: got {decision.classification.get('user_intent')}, expected {test_case['expected_intent']}")
                
            except Exception as e:
                print(f"❌ ERROR in test: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🔍 ROUTING RULES ANALYSIS")
        print("=" * 40)
        
        # Analyze routing rules
        rules = routing_tree.decision_rules
        print(f"📊 Total routing rules: {len(rules)}")
        
        # Check knowledge request rules
        knowledge_rules = [name for name, rule in rules.items() if 'knowledge' in name.lower()]
        print(f"🧠 Knowledge-related rules: {knowledge_rules}")
        
        for rule_name in knowledge_rules:
            rule = rules[rule_name]
            print(f"   {rule_name}: priority={rule['priority']}, route={rule['route'].value if rule['route'] else 'None'}")
        
        # Check fallback rules
        fallback_rules = [name for name, rule in rules.items() if 'fallback' in name.lower() or rule['priority'] > 90]
        print(f"🔄 Fallback rules: {fallback_rules}")
        
        for rule_name in fallback_rules:
            rule = rules[rule_name]
            print(f"   {rule_name}: priority={rule['priority']}, route={rule['route'].value if rule['route'] else 'None'}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routing_system()
