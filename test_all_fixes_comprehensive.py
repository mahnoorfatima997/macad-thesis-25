#!/usr/bin/env python3
"""
COMPREHENSIVE TEST FOR ALL ROUTING AND MENTOR FIXES
Tests all the issues identified by the user and verifies fixes.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add thesis-agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))

# Load environment variables
load_dotenv()

def test_all_fixes():
    """Test all routing and mentor fixes comprehensively"""
    print("🧪 COMPREHENSIVE SYSTEM FIXES TEST")
    print("=" * 60)
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        from agents.context_agent import ContextAgent
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from state_manager import ArchMentorState
        
        # Initialize components
        routing_tree = AdvancedRoutingDecisionTree()
        context_agent = ContextAgent("architecture")
        orchestrator = LangGraphOrchestrator()
        
        print("✅ All components initialized successfully")
        
        # Test cases covering all user problems
        test_cases = [
            {
                "name": "PROBLEM 1: Knowledge Request - Circulation",
                "message": "can you guide me about how to create a good circulation inside the building?",
                "expected_route": "knowledge_only",
                "expected_intent": "knowledge_seeking",
                "test_type": "routing"
            },
            {
                "name": "PROBLEM 2: Best Practices Knowledge", 
                "message": "what are the best practices for circulation design in a community center?",
                "expected_route": "knowledge_only",
                "expected_intent": "knowledge_seeking", 
                "test_type": "routing"
            },
            {
                "name": "PROBLEM 3: Technical Question",
                "message": "What are ADA door width requirements?",
                "expected_route": "knowledge_only",
                "expected_intent": "technical_question",
                "test_type": "routing"
            },
            {
                "name": "PROBLEM 4: Confusion Expression with Context",
                "message": "looking through someone else's lens is very helpful to consider all user groups with wide range of ages. but I am not sure how to provide a good inner garden strategy for this building. what would be the best idea?",
                "expected_route": "socratic_clarification",
                "expected_intent": "confusion_expression",
                "test_type": "mentor_continuity",
                "context": [
                    {"role": "user", "content": "I'm designing a community center in a cold climate"},
                    {"role": "assistant", "content": "That's an interesting project! Cold climate design requires special considerations."}
                ]
            },
            {
                "name": "PROBLEM 5: Design Exploration",
                "message": "I'm thinking about how courtyards might create different social dynamics in my hospital design",
                "expected_route": "socratic_exploration", 
                "expected_intent": "design_exploration",
                "test_type": "routing"
            }
        ]
        
        print(f"\n🧪 Testing {len(test_cases)} comprehensive scenarios...")
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- TEST {i}: {test_case['name']} ---")
            print(f"📝 Message: {test_case['message']}")
            
            try:
                if test_case['test_type'] == 'routing':
                    # Test routing only
                    student_state = ArchMentorState()
                    student_state.messages.append({
                        "role": "user",
                        "content": test_case['message']
                    })
                    
                    # Test context analysis
                    context_result = asyncio.run(context_agent.analyze_student_input(
                        student_state, test_case['message']
                    ))
                    
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
                    print(f"🔍 User Intent: {decision.classification.get('user_intent', 'unknown')}")
                    
                    # Check if routing is correct
                    route_correct = decision.route.value == test_case['expected_route']
                    intent_correct = decision.classification.get('user_intent') == test_case['expected_intent']
                    
                    if route_correct:
                        print("✅ ROUTING CORRECT")
                        success_count += 1
                    else:
                        print("❌ ROUTING FAILED")
                        print(f"   Route mismatch: got {decision.route.value}, expected {test_case['expected_route']}")
                        
                elif test_case['test_type'] == 'mentor_continuity':
                    # Test full mentor continuity
                    student_state = ArchMentorState()
                    
                    # Add context if provided
                    if 'context' in test_case:
                        student_state.messages.extend(test_case['context'])
                    
                    # Add current message
                    student_state.messages.append({
                        "role": "user",
                        "content": test_case['message']
                    })
                    
                    # Test full orchestrator
                    result = asyncio.run(orchestrator.process_student_input(student_state))
                    
                    print(f"🛣️  Actual Route: {result.get('routing_path', 'unknown')}")
                    print(f"🎯 Expected Route: {test_case['expected_route']}")
                    
                    # Check context understanding
                    response_text = result.get('response', '').lower()
                    context_indicators = ['community center', 'cold climate', 'inner garden', 'user groups']
                    context_understood = sum(1 for indicator in context_indicators if indicator in response_text)
                    
                    print(f"🧠 Context Understanding: {context_understood}/{len(context_indicators)} indicators found")
                    
                    route_correct = result.get('routing_path') == test_case['expected_route']
                    context_good = context_understood >= 2
                    
                    if route_correct and context_good:
                        print("✅ MENTOR CONTINUITY CORRECT")
                        success_count += 1
                    else:
                        print("❌ MENTOR CONTINUITY FAILED")
                        if not route_correct:
                            print(f"   Route mismatch: got {result.get('routing_path')}, expected {test_case['expected_route']}")
                        if not context_good:
                            print(f"   Poor context understanding: {context_understood}/{len(context_indicators)}")
                            
            except Exception as e:
                print(f"❌ ERROR in test: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎯 FINAL RESULTS")
        print("=" * 40)
        print(f"✅ Tests passed: {success_count}/{len(test_cases)}")
        print(f"📊 Success rate: {(success_count/len(test_cases)*100):.1f}%")
        
        if success_count == len(test_cases):
            print("🎉 ALL TESTS PASSED - SYSTEM FULLY FIXED!")
        elif success_count >= len(test_cases) * 0.8:
            print("✅ MOST TESTS PASSED - SYSTEM MOSTLY FIXED")
        else:
            print("⚠️ SOME TESTS FAILED - NEEDS MORE WORK")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_fixes()
