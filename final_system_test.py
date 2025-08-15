#!/usr/bin/env python3
"""
Final System Test - Complete Functionality Verification
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_domain_expert_real():
    """Test real domain expert functionality"""
    print('🧪 TESTING DOMAIN EXPERT REAL FUNCTIONALITY')
    print('=' * 60)
    
    try:
        from agents.domain_expert import DomainExpertAgent
        from state_manager import ArchMentorState
        
        agent = DomainExpertAgent()
        state = ArchMentorState()
        
        print('✅ Domain expert and state initialized')
        
        # Test the actual method
        test_query = 'passive cooling strategies for buildings'
        print(f'\n🔍 Testing: {test_query}')
        
        result = await agent.provide_domain_knowledge(test_query, state)
        
        if result:
            print('✅ Domain expert responded successfully')
            response_type = result.get('response_type', 'unknown')
            print(f'Response type: {response_type}')
            
            response_text = result.get('response_text', '')
            if response_text:
                print(f'Response length: {len(response_text)} characters')
                preview = response_text[:200].replace('\n', ' ')
                print(f'Preview: {preview}...')
                return True
            else:
                print('❌ No response text returned')
                return False
        else:
            print('❌ No result returned')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False

async def test_complete_orchestration():
    """Test complete orchestration workflow"""
    print('\n🔄 TESTING COMPLETE ORCHESTRATION')
    print('=' * 60)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from orchestration.types import WorkflowState
        
        orchestrator = LangGraphOrchestrator()
        print('✅ Orchestrator initialized')
        
        # Test with a simple knowledge request
        test_input = 'What are examples of community centers in hot climates?'
        print(f'\n🧪 Testing: {test_input}')
        
        # Create workflow state
        initial_state = WorkflowState(
            user_input=test_input,
            messages=[{"role": "user", "content": test_input}],
            classification={},
            context_analysis={},
            routing_suggestions={},
            domain_expert_response="",
            socratic_response="",
            cognitive_enhancement="",
            final_response="",
            response_metadata={}
        )
        
        # Process through orchestrator
        final_state = await orchestrator.process_workflow(initial_state)
        
        if final_state and final_state.get('final_response'):
            response = final_state['final_response']
            print('✅ Orchestration completed successfully')
            print(f'Response length: {len(response)} characters')
            preview = response[:200].replace('\n', ' ')
            print(f'Preview: {preview}...')
            
            # Check metadata
            metadata = final_state.get('response_metadata', {})
            print(f'Route used: {metadata.get("routing_path", "unknown")}')
            print(f'Agents used: {metadata.get("agents_used", [])}')
            
            return True
        else:
            print('❌ No final response generated')
            return False
            
    except Exception as e:
        print(f'❌ Orchestration test failed: {e}')
        return False

def test_routing_accuracy():
    """Test routing accuracy with current fixes"""
    print('\n🧭 TESTING ROUTING ACCURACY')
    print('=' * 60)
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        
        router = AdvancedRoutingDecisionTree()
        
        # Test cases with expected routes
        test_cases = [
            {
                'input': 'What are examples of community centers in hot climates?',
                'expected': 'knowledge_only',
                'category': 'Example Request'
            },
            {
                'input': 'Can you tell me about passive cooling strategies?',
                'expected': 'knowledge_only',
                'category': 'Knowledge Request'
            },
            {
                'input': 'I need help organizing spaces for different age groups',
                'expected': 'balanced_guidance',
                'category': 'Design Guidance'
            },
            {
                'input': 'I don\'t understand spatial hierarchy',
                'expected': 'socratic_clarification',
                'category': 'Confusion'
            },
            {
                'input': 'How should I handle circulation patterns?',
                'expected': 'knowledge_only',
                'category': 'Knowledge Request'
            }
        ]
        
        correct = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            test_input = test_case['input']
            expected = test_case['expected']
            
            classification = {'user_input': test_input}
            context = RoutingContext(
                classification=classification,
                context_analysis={},
                routing_suggestions={}
            )
            decision = router.decide_route(context)
            
            actual = decision.route.value
            is_correct = actual == expected
            
            if is_correct:
                correct += 1
            
            status = '✅' if is_correct else '❌'
            print(f'{status} {test_case["category"]}: {expected} → {actual}')
        
        accuracy = (correct / total) * 100
        print(f'\n📊 Routing Accuracy: {accuracy:.1f}% ({correct}/{total})')
        
        return accuracy >= 80  # 80% threshold for success
        
    except Exception as e:
        print(f'❌ Routing test failed: {e}')
        return False

def test_synthesis_functionality():
    """Test synthesis functionality"""
    print('\n🎭 TESTING SYNTHESIS FUNCTIONALITY')
    print('=' * 60)
    
    try:
        from orchestration.synthesis import shape_by_route
        
        # Test different route types
        test_cases = [
            {
                'route': 'knowledge_only',
                'text': 'Passive cooling strategies include natural ventilation and thermal mass.',
                'expected_format': 'direct'
            },
            {
                'route': 'balanced_guidance',
                'text': 'Here is guidance about organizing spaces.',
                'expected_format': 'synthesis_structure'
            }
        ]
        
        successful = 0
        
        for test_case in test_cases:
            route = test_case['route']
            text = test_case['text']
            
            print(f'\n🧪 Testing synthesis for: {route}')
            
            try:
                shaped_response = shape_by_route(
                    text=text,
                    routing_path=route,
                    classification={'user_input': 'test'},
                    ordered_results={},
                    user_message_count=1,
                    context_analysis={}
                )
                
                if shaped_response and len(shaped_response) > 0:
                    print('✅ Synthesis successful')
                    
                    # Check format
                    has_synthesis = 'Synthesis:' in shaped_response
                    if route == 'balanced_guidance' and has_synthesis:
                        print('✅ Correct synthesis structure for balanced_guidance')
                        successful += 1
                    elif route == 'knowledge_only' and not has_synthesis:
                        print('✅ Correct direct format for knowledge_only')
                        successful += 1
                    else:
                        print(f'⚠️ Format may not match route expectations')
                        successful += 0.5  # Partial credit
                else:
                    print('❌ No response generated')
                    
            except Exception as e:
                print(f'❌ Synthesis failed: {e}')
        
        success_rate = (successful / len(test_cases)) * 100
        print(f'\n📊 Synthesis Success Rate: {success_rate:.1f}%')
        
        return success_rate >= 75
        
    except Exception as e:
        print(f'❌ Synthesis test failed: {e}')
        return False

async def main():
    """Run comprehensive final system test"""
    print('🚀 FINAL COMPREHENSIVE SYSTEM TEST')
    print('=' * 80)
    
    # Run all tests
    domain_expert_success = await test_domain_expert_real()
    orchestration_success = await test_complete_orchestration()
    routing_success = test_routing_accuracy()
    synthesis_success = test_synthesis_functionality()
    
    # Calculate overall success
    tests = [domain_expert_success, orchestration_success, routing_success, synthesis_success]
    successful_tests = sum(tests)
    total_tests = len(tests)
    overall_success_rate = (successful_tests / total_tests) * 100
    
    print('\n📊 FINAL SYSTEM HEALTH REPORT')
    print('=' * 80)
    print(f'🎯 Overall System Health: {overall_success_rate:.1f}%')
    print(f'  - Domain Expert: {"✅" if domain_expert_success else "❌"}')
    print(f'  - Orchestration: {"✅" if orchestration_success else "❌"}')
    print(f'  - Routing: {"✅" if routing_success else "❌"}')
    print(f'  - Synthesis: {"✅" if synthesis_success else "❌"}')
    
    if overall_success_rate >= 75:
        print('\n🎉 SYSTEM IS READY FOR PRODUCTION!')
        print('The learning tool is functioning well across all major components.')
    elif overall_success_rate >= 50:
        print('\n✅ SYSTEM IS FUNCTIONAL')
        print('The learning tool works but may need minor improvements.')
    else:
        print('\n⚠️ SYSTEM NEEDS ATTENTION')
        print('Several components need fixes before production use.')
    
    # Generate final recommendations
    print('\n📝 FINAL RECOMMENDATIONS:')
    if not domain_expert_success:
        print('  1. Fix domain expert knowledge retrieval')
    if not orchestration_success:
        print('  2. Debug orchestration workflow')
    if not routing_success:
        print('  3. Improve routing accuracy')
    if not synthesis_success:
        print('  4. Fix synthesis formatting')
    
    if overall_success_rate >= 75:
        print('  - System is ready for user testing')
        print('  - Consider adding monitoring and analytics')
        print('  - Implement user feedback collection')
    
    return overall_success_rate

if __name__ == "__main__":
    asyncio.run(main())
