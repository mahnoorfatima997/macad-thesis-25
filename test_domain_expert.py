#!/usr/bin/env python3
"""
Test Domain Expert Knowledge Retrieval
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_domain_expert_knowledge():
    print('🧪 TESTING DOMAIN EXPERT KNOWLEDGE RETRIEVAL')
    print('=' * 60)
    
    try:
        from agents.domain_expert import DomainExpertAgent
        
        agent = DomainExpertAgent()
        print('✅ Domain expert initialized')
        
        # Test knowledge retrieval
        test_queries = [
            'passive cooling strategies',
            'community center design principles', 
            'examples of sustainable architecture'
        ]
        
        successful_queries = 0
        
        for query in test_queries:
            print(f'\n🔍 Testing query: {query}')
            try:
                # Test the knowledge retrieval method
                result = await agent.get_knowledge(query)
                
                if result and 'content' in result:
                    content_length = len(result['content'])
                    source = result.get('source', 'unknown')
                    print(f'✅ Retrieved {content_length} chars from {source}')
                    preview = result['content'][:150].replace('\n', ' ')
                    print(f'Preview: {preview}...')
                    successful_queries += 1
                else:
                    print('❌ No content returned')
                    
            except Exception as e:
                print(f'❌ Query failed: {e}')
        
        success_rate = (successful_queries / len(test_queries)) * 100
        print(f'\n📊 Domain Expert Success Rate: {success_rate:.1f}%')
        
        return success_rate
        
    except Exception as e:
        print(f'❌ Domain expert test failed: {e}')
        return 0

async def test_gamification_system():
    print('\n🎮 TESTING GAMIFICATION SYSTEM')
    print('=' * 60)
    
    try:
        from agents.cognitive_enhancement import CognitiveEnhancementAgent
        
        agent = CognitiveEnhancementAgent()
        print('✅ Cognitive enhancement agent initialized')
        
        # Test gamification triggers
        test_cases = [
            {
                'input': 'This design is perfect and will work for everyone',
                'expected_trigger': 'overconfidence_challenge'
            },
            {
                'input': 'Just tell me what to do',
                'expected_trigger': 'cognitive_offloading_prevention'
            },
            {
                'input': 'What are some good examples of community centers?',
                'expected_trigger': 'encouragement_boost'
            }
        ]
        
        gamification_working = 0
        
        for test_case in test_cases:
            print(f'\n🎯 Testing: {test_case["input"][:40]}...')
            try:
                # Test gamification detection
                result = await agent.analyze_and_enhance(
                    user_input=test_case['input'],
                    context={'conversation_history': []}
                )
                
                if result and 'gamification' in result:
                    gam_data = result['gamification']
                    print(f'✅ Gamification triggered: {gam_data.get("type", "unknown")}')
                    print(f'Message: {gam_data.get("message", "No message")[:50]}...')
                    gamification_working += 1
                else:
                    print('❌ No gamification triggered')
                    
            except Exception as e:
                print(f'❌ Gamification test failed: {e}')
        
        gam_success_rate = (gamification_working / len(test_cases)) * 100
        print(f'\n📊 Gamification Success Rate: {gam_success_rate:.1f}%')
        
        return gam_success_rate
        
    except Exception as e:
        print(f'❌ Gamification system test failed: {e}')
        return 0

async def test_complete_system():
    print('\n🔄 TESTING COMPLETE SYSTEM INTEGRATION')
    print('=' * 60)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        
        orchestrator = LangGraphOrchestrator()
        print('✅ Orchestrator initialized')
        
        # Test complete workflow
        test_inputs = [
            'What are some examples of community centers in hot climates?',
            'I need help organizing spaces for different age groups',
            'I don\'t understand what you mean by spatial hierarchy'
        ]
        
        successful_workflows = 0
        
        for test_input in test_inputs:
            print(f'\n🧪 Testing workflow: {test_input[:40]}...')
            try:
                # Create a simple state for testing
                from orchestration.types import WorkflowState
                
                state = WorkflowState(
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
                result = await orchestrator.process_workflow(state)
                
                if result and result.get('final_response'):
                    response_length = len(result['final_response'])
                    print(f'✅ Workflow completed: {response_length} char response')
                    successful_workflows += 1
                else:
                    print('❌ Workflow failed to produce response')
                    
            except Exception as e:
                print(f'❌ Workflow failed: {e}')
        
        workflow_success_rate = (successful_workflows / len(test_inputs)) * 100
        print(f'\n📊 Complete Workflow Success Rate: {workflow_success_rate:.1f}%')
        
        return workflow_success_rate
        
    except Exception as e:
        print(f'❌ Complete system test failed: {e}')
        return 0

async def main():
    print('🚀 COMPREHENSIVE SYSTEM FUNCTIONALITY TEST')
    print('=' * 80)
    
    # Test individual components
    domain_expert_score = await test_domain_expert_knowledge()
    gamification_score = await test_gamification_system()
    workflow_score = await test_complete_system()
    
    # Calculate overall score
    overall_score = (domain_expert_score + gamification_score + workflow_score) / 3
    
    print('\n📊 FINAL SYSTEM HEALTH REPORT')
    print('=' * 80)
    print(f'🎯 Overall System Health: {overall_score:.1f}%')
    print(f'  - Domain Expert: {domain_expert_score:.1f}%')
    print(f'  - Gamification: {gamification_score:.1f}%')
    print(f'  - Complete Workflows: {workflow_score:.1f}%')
    
    if overall_score >= 75:
        print('\n🎉 System is in excellent condition!')
    elif overall_score >= 50:
        print('\n✅ System is functional with minor issues')
    else:
        print('\n⚠️ System needs attention before production use')
    
    return overall_score

if __name__ == "__main__":
    asyncio.run(main())
