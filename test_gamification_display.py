#!/usr/bin/env python3
"""
Test Gamification Display Issue
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_gamification_display():
    print('🎮 TESTING GAMIFICATION DISPLAY ISSUE')
    print('=' * 60)
    
    try:
        from agents.cognitive_enhancement import CognitiveEnhancementAgent
        from state_manager import ArchMentorState
        
        agent = CognitiveEnhancementAgent()
        state = ArchMentorState()
        
        # Test gamification trigger
        test_input = 'This design is perfect and will work for everyone'
        print(f'Testing input: {test_input}')
        
        result = await agent.analyze_and_enhance(
            user_input=test_input,
            context={'conversation_history': []}
        )
        
        print('\nRaw result from cognitive enhancement:')
        print(f'Type: {type(result)}')
        if isinstance(result, dict):
            print(f'Keys: {list(result.keys())}')
        else:
            print('Result is not a dict')
        print(f'Full result: {result}')
        
        # Check for gamification data
        if isinstance(result, dict) and 'gamification' in result:
            gam_data = result['gamification']
            print('\n🎯 Gamification data found:')
            print(f'  Type: {gam_data.get("type", "unknown")}')
            print(f'  Message: {gam_data.get("message", "No message")}')
            print(f'  Visual Effect: {gam_data.get("visual_effect", "none")}')
            print(f'  Points: {gam_data.get("points_awarded", 0)}')
        else:
            print('❌ No gamification data found in result')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

async def test_routing_with_gamification():
    print('\n🧭 TESTING ROUTING WITH GAMIFICATION OUTPUT')
    print('=' * 60)
    
    try:
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree, RoutingContext
        
        router = AdvancedRoutingDecisionTree()
        
        # Test overconfident statement
        test_input = 'This design is perfect and will work for everyone'
        print(f'Testing routing for: {test_input}')
        
        classification = {'user_input': test_input}
        context = RoutingContext(
            classification=classification,
            context_analysis={},
            routing_suggestions={}
        )
        decision = router.decide_route(context)
        
        print(f'Route: {decision.route.value}')
        print(f'Rule: {decision.rule_applied}')
        print(f'Intent: {decision.user_intent}')
        print(f'Metadata: {decision.metadata}')
        
        # Check if gamification metadata is in routing decision
        if 'gamification' in decision.metadata:
            print('\n🎯 Gamification in routing metadata:')
            gam_data = decision.metadata['gamification']
            print(f'  {gam_data}')
        else:
            print('\n❌ No gamification in routing metadata')
            
    except Exception as e:
        print(f'❌ Routing test error: {e}')
        import traceback
        traceback.print_exc()

async def test_complete_workflow_gamification():
    print('\n🔄 TESTING COMPLETE WORKFLOW GAMIFICATION')
    print('=' * 60)
    
    try:
        # Test through the mentor app workflow
        from mentor import process_user_input
        
        test_input = 'This design is perfect and will work for everyone'
        print(f'Testing complete workflow: {test_input}')
        
        # This should trigger the complete workflow including gamification
        response = await process_user_input(test_input)
        
        print(f'\nComplete workflow response:')
        print(f'Type: {type(response)}')
        print(f'Response: {response}')
        
        # Check if response contains gamification elements
        if isinstance(response, dict):
            if 'gamification' in response:
                print('\n🎯 Gamification found in response:')
                print(f'  {response["gamification"]}')
            else:
                print('\n❌ No gamification in response')
                
            if 'metadata' in response and 'gamification' in response['metadata']:
                print('\n🎯 Gamification found in metadata:')
                print(f'  {response["metadata"]["gamification"]}')
        
    except Exception as e:
        print(f'❌ Complete workflow test error: {e}')
        import traceback
        traceback.print_exc()

async def test_streamlit_gamification_display():
    print('\n🖥️ TESTING STREAMLIT GAMIFICATION DISPLAY')
    print('=' * 60)
    
    try:
        # Check if there's a gamification display function in the UI
        import streamlit as st
        
        # Simulate gamification data
        gamification_data = {
            'type': 'overconfidence_challenge',
            'message': '🚨 Hold on! While confidence is great, every design has trade-offs. What potential challenges might this design face?',
            'visual_effect': 'warning_border',
            'points_awarded': 0
        }
        
        print('Simulated gamification data:')
        print(f'  Type: {gamification_data["type"]}')
        print(f'  Message: {gamification_data["message"]}')
        print(f'  Visual Effect: {gamification_data["visual_effect"]}')
        print(f'  Points: {gamification_data["points_awarded"]}')
        
        # Check if there's a display function
        # This would normally be called in the Streamlit app
        print('\n📱 This gamification should appear in the UI as:')
        print(f'   🚨 WARNING BORDER')
        print(f'   Message: {gamification_data["message"]}')
        print(f'   Points: +{gamification_data["points_awarded"]} (no points for challenges)')
        
    except Exception as e:
        print(f'❌ Streamlit test error: {e}')

async def main():
    await test_gamification_display()
    await test_routing_with_gamification()
    await test_complete_workflow_gamification()
    await test_streamlit_gamification_display()
    
    print('\n📊 GAMIFICATION DISPLAY ANALYSIS COMPLETE')
    print('=' * 60)
    print('If gamification is not showing in the UI, check:')
    print('1. Gamification metadata is being passed to the UI')
    print('2. UI has gamification display components')
    print('3. CSS/styling for gamification elements')
    print('4. Streamlit components are rendering gamification')

if __name__ == "__main__":
    asyncio.run(main())
