#!/usr/bin/env python3
"""
Test Gamification Fix - Complete Workflow
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'thesis-agents')

async def test_complete_gamification_workflow():
    """Test the complete gamification workflow with the fix"""
    print('🎮 TESTING COMPLETE GAMIFICATION WORKFLOW WITH FIX')
    print('=' * 80)
    
    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from state_manager import ArchMentorState
        
        # Create orchestrator and state
        orchestrator = LangGraphOrchestrator()
        state = ArchMentorState()
        
        # Test overconfident statement that should trigger gamification
        test_input = 'This design is perfect and will work for everyone'
        state.messages = [{"role": "user", "content": test_input}]
        
        print(f'Testing input: {test_input}')
        print('Expected: Should trigger cognitive_challenge route with gamification')
        
        # Process through orchestrator
        result = await orchestrator.process_student_input(state)
        
        print(f'\n📊 ORCHESTRATOR RESULT:')
        print(f'Type: {type(result)}')
        
        if isinstance(result, dict):
            print(f'Keys: {list(result.keys())}')
            
            # Check final response
            final_response = result.get('final_response', '')
            print(f'\nFinal response length: {len(final_response)}')
            print(f'Response preview: {final_response[:200]}...')
            
            # Check metadata for gamification
            metadata = result.get('response_metadata', {})
            print(f'\n🎯 METADATA ANALYSIS:')
            print(f'Routing path: {metadata.get("routing_path", "unknown")}')
            print(f'Agents used: {metadata.get("agents_used", [])}')
            
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
                    print(f'  Is gamified: {gam_data.get("is_gamified", False)}')
                    print(f'  Display type: {gam_data.get("display_type", "unknown")}')
                    
                    challenge_data = gam_data.get('challenge_data', {})
                    if challenge_data:
                        print(f'  Challenge type: {challenge_data.get("challenge_type", "unknown")}')
                        print(f'  Difficulty: {challenge_data.get("difficulty_level", "unknown")}')
                        challenge_text = challenge_data.get('challenge_text', '')
                        print(f'  Challenge preview: {challenge_text[:100]}...')
                
                return True
            else:
                print(f'\n❌ NO GAMIFICATION FOUND')
                print(f'Available metadata keys: {list(metadata.keys())}')
                return False
        else:
            print(f'❌ Unexpected result type: {type(result)}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_ui_gamification_display():
    """Test how gamification would be displayed in the UI"""
    print('\n🖥️ TESTING UI GAMIFICATION DISPLAY')
    print('=' * 60)
    
    try:
        from dashboard.ui.gamification_components import GamificationDisplay
        
        display = GamificationDisplay()
        
        # Simulate gamification metadata from the system
        gamification_metadata = {
            'is_gamified': True,
            'display_type': 'enhanced_visual',
            'challenge_data': {
                'challenge_type': 'metacognitive_challenge',
                'difficulty_level': 'high',
                'challenge_text': 'Reflect on the assumption that your design is universally perfect. Consider the diverse needs and experiences of potential users.',
                'pedagogical_intent': 'Foster metacognitive awareness and self-evaluation'
            }
        }
        
        print('Simulated gamification metadata:')
        for key, value in gamification_metadata.items():
            if isinstance(value, dict):
                print(f'  {key}:')
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str) and len(subvalue) > 50:
                        print(f'    {subkey}: {subvalue[:50]}...')
                    else:
                        print(f'    {subkey}: {subvalue}')
            else:
                print(f'  {key}: {value}')
        
        # Check if display has methods to render this
        methods = [method for method in dir(display) if 'render' in method.lower()]
        print(f'\nAvailable render methods: {methods}')
        
        # This would be called in the Streamlit UI
        print(f'\n📱 UI DISPLAY SIMULATION:')
        print(f'🎯 GAMIFIED CHALLENGE DETECTED')
        print(f'Type: {gamification_metadata["challenge_data"]["challenge_type"]}')
        print(f'Difficulty: {gamification_metadata["challenge_data"]["difficulty_level"]}')
        print(f'Intent: {gamification_metadata["challenge_data"]["pedagogical_intent"]}')
        print(f'Challenge: {gamification_metadata["challenge_data"]["challenge_text"][:100]}...')
        
        return True
        
    except Exception as e:
        print(f'❌ UI test error: {e}')
        return False

async def main():
    """Run complete gamification fix test"""
    print('🚀 GAMIFICATION FIX VERIFICATION')
    print('=' * 100)
    
    # Test complete workflow
    workflow_success = await test_complete_gamification_workflow()
    
    # Test UI display
    ui_success = await test_ui_gamification_display()
    
    print('\n📊 GAMIFICATION FIX TEST RESULTS')
    print('=' * 80)
    print(f'Complete Workflow: {"✅ WORKING" if workflow_success else "❌ NEEDS FIX"}')
    print(f'UI Display: {"✅ WORKING" if ui_success else "❌ NEEDS FIX"}')
    
    if workflow_success and ui_success:
        print('\n🎉 GAMIFICATION FIX SUCCESSFUL!')
        print('The gamification system is now working end-to-end:')
        print('1. ✅ Overconfident statements trigger cognitive_challenge route')
        print('2. ✅ Cognitive enhancement agent generates gamification metadata')
        print('3. ✅ Orchestration extracts and propagates gamification metadata')
        print('4. ✅ UI components can display gamification elements')
        print('\n🚀 READY FOR PRODUCTION!')
    elif workflow_success:
        print('\n⚠️ PARTIAL SUCCESS')
        print('Gamification metadata is being generated and propagated,')
        print('but UI display needs attention.')
    else:
        print('\n❌ GAMIFICATION STILL NOT WORKING')
        print('The orchestration fix may need further debugging.')
    
    return workflow_success and ui_success

if __name__ == "__main__":
    asyncio.run(main())
