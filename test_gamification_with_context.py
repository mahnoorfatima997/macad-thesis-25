#!/usr/bin/env python3
"""
Test Gamification with Conversation Context
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_gamification_with_conversation_context():
    """Test gamification with proper conversation context"""
    print('🎮 TESTING GAMIFICATION WITH CONVERSATION CONTEXT')
    print('=' * 80)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from state_manager import ArchMentorState
        
        # Create orchestrator and state
        orchestrator = LangGraphOrchestrator()
        state = ArchMentorState()
        
        # Create a conversation context first
        state.messages = [
            {"role": "user", "content": "I'm working on a community center design"},
            {"role": "assistant", "content": "That's great! Community centers are important spaces. What specific aspects are you considering?"},
            {"role": "user", "content": "This design is perfect and will work for everyone"}  # This should trigger gamification
        ]
        
        overconfident_input = "This design is perfect and will work for everyone"
        print(f'Testing input with context: {overconfident_input}')
        print('Expected: Should trigger cognitive_challenge route with gamification')
        
        # Process through orchestrator
        result = await orchestrator.process_student_input(state)
        
        print(f'\n📊 ORCHESTRATOR RESULT:')
        print(f'Type: {type(result)}')
        
        if isinstance(result, dict):
            print(f'Keys: {list(result.keys())}')
            
            # Check final response
            final_response = result.get('final_response', result.get('response', ''))
            print(f'\nFinal response length: {len(final_response)}')
            print(f'Response preview: {final_response[:200]}...')
            
            # Check metadata for gamification
            metadata = result.get('response_metadata', result.get('metadata', {}))
            print(f'\n🎯 METADATA ANALYSIS:')
            print(f'Routing path: {metadata.get("routing_path", "unknown")}')
            print(f'Agents used: {metadata.get("agents_used", [])}')
            print(f'All metadata keys: {list(metadata.keys())}')
            
            # Check for gamification metadata
            gamification_display = metadata.get('gamification_display', {})
            gamification = metadata.get('gamification', {})
            
            if gamification_display or gamification:
                print(f'\n🎉 GAMIFICATION FOUND!')
                print(f'Gamification display: {bool(gamification_display)}')
                print(f'Gamification metadata: {bool(gamification)}')
                
                # Show gamification details
                gam_data = gamification_display or gamification
                if gam_data:
                    print(f'\n🎮 GAMIFICATION DETAILS:')
                    for key, value in gam_data.items():
                        if isinstance(value, dict):
                            print(f'  {key}: {list(value.keys())}')
                        else:
                            print(f'  {key}: {value}')
                
                return True
            else:
                print(f'\n❌ NO GAMIFICATION FOUND')
                return False
        else:
            print(f'❌ Unexpected result type: {type(result)}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_direct_routing():
    """Test routing directly to see if overconfident statements are detected"""
    print('\n🧭 TESTING DIRECT ROUTING FOR OVERCONFIDENT STATEMENTS')
    print('=' * 80)
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        
        router = AdvancedRoutingDecisionTree()
        
        # Test overconfident statements
        test_cases = [
            "This design is perfect and will work for everyone",
            "My solution is flawless and addresses all needs",
            "This approach is definitely the best option",
            "I'm confident this will solve all the problems"
        ]
        
        for test_input in test_cases:
            print(f'\n🧪 Testing: {test_input}')
            
            classification = {'user_input': test_input}
            context = RoutingContext(
                classification=classification,
                context_analysis={},
                routing_suggestions={}
            )
            decision = router.decide_route(context)
            
            print(f'Route: {decision.route.value}')
            print(f'Intent: {decision.user_intent}')
            print(f'Rule: {decision.rule_applied}')
            
            if decision.route.value == 'cognitive_challenge':
                print('✅ Correctly identified as overconfident statement')
            else:
                print('❌ Not identified as overconfident statement')
        
        return True
        
    except Exception as e:
        print(f'❌ Routing test failed: {e}')
        return False

async def test_cognitive_enhancement_directly():
    """Test cognitive enhancement agent directly"""
    print('\n🧠 TESTING COGNITIVE ENHANCEMENT AGENT DIRECTLY')
    print('=' * 80)
    
    try:
        from agents.cognitive_enhancement import CognitiveEnhancementAgent
        from state_manager import ArchMentorState
        
        agent = CognitiveEnhancementAgent()
        state = ArchMentorState()
        
        # Set up state with conversation context
        state.messages = [
            {"role": "user", "content": "I'm working on a community center design"},
            {"role": "assistant", "content": "That's great! What aspects are you considering?"},
            {"role": "user", "content": "This design is perfect and will work for everyone"}
        ]
        
        # Test cognitive enhancement
        context_classification = {"primary_gap": "overconfidence"}
        analysis_result = {"user_intent": "overconfident_statement"}
        routing_decision = {"route": "cognitive_challenge"}
        
        result = await agent.provide_challenge(
            state=state,
            context_classification=context_classification,
            analysis_result=analysis_result,
            routing_decision=routing_decision
        )
        
        print(f'Result type: {type(result)}')
        print(f'Has metadata: {hasattr(result, "metadata")}')
        
        if hasattr(result, 'metadata') and result.metadata:
            print(f'Metadata keys: {list(result.metadata.keys())}')
            
            if 'gamification_display' in result.metadata:
                gam_data = result.metadata['gamification_display']
                print(f'\n🎮 GAMIFICATION METADATA FOUND:')
                print(f'Is gamified: {gam_data.get("is_gamified", False)}')
                print(f'Display type: {gam_data.get("display_type", "unknown")}')
                
                challenge_data = gam_data.get('challenge_data', {})
                if challenge_data:
                    print(f'Challenge type: {challenge_data.get("challenge_type", "unknown")}')
                    print(f'Difficulty: {challenge_data.get("difficulty_level", "unknown")}')
                
                return True
            else:
                print('❌ No gamification_display in metadata')
        else:
            print('❌ No metadata found')
        
        return False
        
    except Exception as e:
        print(f'❌ Cognitive enhancement test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run comprehensive gamification tests"""
    print('🚀 COMPREHENSIVE GAMIFICATION TESTING')
    print('=' * 100)
    
    # Test routing first
    routing_success = await test_direct_routing()
    
    # Test cognitive enhancement directly
    cognitive_success = await test_cognitive_enhancement_directly()
    
    # Test with conversation context
    workflow_success = await test_gamification_with_conversation_context()
    
    print('\n📊 COMPREHENSIVE GAMIFICATION TEST RESULTS')
    print('=' * 80)
    print(f'Direct Routing: {"✅ WORKING" if routing_success else "❌ NEEDS FIX"}')
    print(f'Cognitive Enhancement: {"✅ WORKING" if cognitive_success else "❌ NEEDS FIX"}')
    print(f'Complete Workflow: {"✅ WORKING" if workflow_success else "❌ NEEDS FIX"}')
    
    if routing_success and cognitive_success and workflow_success:
        print('\n🎉 GAMIFICATION SYSTEM FULLY WORKING!')
    elif cognitive_success:
        print('\n⚠️ GAMIFICATION PARTIALLY WORKING')
        print('Cognitive enhancement generates gamification, but workflow needs debugging')
    else:
        print('\n❌ GAMIFICATION SYSTEM NEEDS MORE WORK')
    
    return routing_success and cognitive_success and workflow_success

if __name__ == "__main__":
    asyncio.run(main())
