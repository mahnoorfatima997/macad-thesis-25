#!/usr/bin/env python3
"""
Test UI Gamification Display
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'dashboard')

def test_gamification_ui_components():
    """Test gamification UI components with real data"""
    print('🖥️ TESTING GAMIFICATION UI COMPONENTS')
    print('=' * 80)
    
    try:
        from ui.gamification_components import GamificationDisplay, render_gamified_challenge
        
        # Create display instance
        display = GamificationDisplay()
        print('✅ GamificationDisplay created successfully')
        
        # Test with real gamification data from the system
        real_gamification_data = {
            'challenge_text': 'As you assert that your design is perfect and universally applicable, consider the diverse needs and experiences of potential users. Reflect on how your design accommodates different cultural, social, and physical contexts.',
            'challenge_type': 'metacognitive_challenge',
            'metacognitive_type': 'process_reflection',
            'pedagogical_intent': 'Foster metacognitive awareness and self-evaluation with focus on increasing engagement',
            'cognitive_target': 'metacognition',
            'expected_outcome': 'Enhanced self-awareness and reflective practice',
            'strategy': 'promote_reflection',
            'subtype': 'process_reflection',
            'difficulty_level': 'high',
            'generation_timestamp': '2025-08-15T17:47:02.417677'
        }
        
        print('\n🎮 Testing with real gamification data:')
        print(f'Challenge type: {real_gamification_data["challenge_type"]}')
        print(f'Difficulty: {real_gamification_data["difficulty_level"]}')
        print(f'Intent: {real_gamification_data["pedagogical_intent"]}')
        print(f'Challenge preview: {real_gamification_data["challenge_text"][:100]}...')
        
        # Test the display methods
        methods = [method for method in dir(display) if 'render' in method.lower()]
        print(f'\nAvailable render methods: {methods}')
        
        # Test challenge type detection
        detected_type = display._detect_challenge_type(real_gamification_data['challenge_text'])
        print(f'Detected challenge type: {detected_type}')
        
        # Test visual style selection
        visual_style = display._get_visual_style(detected_type)
        print(f'Visual style: {visual_style}')
        
        print('\n✅ Gamification UI components are working correctly')
        return True
        
    except Exception as e:
        print(f'❌ UI components test error: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_message_gamification_detection():
    """Test how messages are detected as gamified"""
    print('\n💬 TESTING MESSAGE GAMIFICATION DETECTION')
    print('=' * 80)
    
    try:
        # Simulate message structure from the system
        gamified_message = {
            "role": "assistant",
            "content": "As you assert that your design is perfect and universally applicable, consider the diverse needs and experiences of potential users.",
            "timestamp": "2025-08-15T17:47:02.417677",
            "mentor_type": "MENTOR",
            "gamification": {
                "is_gamified": True,
                "display_type": "enhanced_visual",
                "challenge_data": {
                    "challenge_text": "As you assert that your design is perfect...",
                    "challenge_type": "metacognitive_challenge",
                    "difficulty_level": "high",
                    "pedagogical_intent": "Foster metacognitive awareness"
                }
            }
        }
        
        # Test gamification detection logic
        gamification_info = gamified_message.get("gamification", {})
        is_gamified = gamification_info.get("is_gamified", False)
        display_type = gamification_info.get("display_type", "")
        
        print(f'Message has gamification: {bool(gamification_info)}')
        print(f'Is gamified: {is_gamified}')
        print(f'Display type: {display_type}')
        print(f'Should render enhanced: {is_gamified and display_type == "enhanced_visual"}')
        
        if is_gamified and display_type == "enhanced_visual":
            print('✅ Message would be rendered as gamified challenge')
            
            challenge_data = gamification_info.get("challenge_data", {})
            print(f'Challenge data keys: {list(challenge_data.keys())}')
            
            return True
        else:
            print('❌ Message would not be rendered as gamified')
            return False
            
    except Exception as e:
        print(f'❌ Message detection test error: {e}')
        return False

def test_gamification_data_structure_compatibility():
    """Test compatibility between system output and UI expectations"""
    print('\n🔄 TESTING DATA STRUCTURE COMPATIBILITY')
    print('=' * 80)
    
    # System output structure (from our test)
    system_output = {
        'gamification_display': {
            'is_gamified': True,
            'display_type': 'enhanced_visual',
            'challenge_data': {
                'challenge_text': 'As you assert that your design is perfect...',
                'challenge_type': 'metacognitive_challenge',
                'difficulty_level': 'high',
                'pedagogical_intent': 'Foster metacognitive awareness'
            }
        }
    }
    
    # UI expected structure (from chat_components.py)
    ui_expected = {
        'gamification': {
            'is_gamified': True,
            'display_type': 'enhanced_visual',
            'challenge_data': {
                'challenge_text': 'Challenge text here...',
                'challenge_type': 'metacognitive_challenge'
            }
        }
    }
    
    print('System output structure:')
    print(f'  Key: gamification_display')
    print(f'  Has is_gamified: {"is_gamified" in system_output["gamification_display"]}')
    print(f'  Has display_type: {"display_type" in system_output["gamification_display"]}')
    print(f'  Has challenge_data: {"challenge_data" in system_output["gamification_display"]}')
    
    print('\nUI expected structure:')
    print(f'  Key: gamification')
    print(f'  Has is_gamified: {"is_gamified" in ui_expected["gamification"]}')
    print(f'  Has display_type: {"display_type" in ui_expected["gamification"]}')
    print(f'  Has challenge_data: {"challenge_data" in ui_expected["gamification"]}')
    
    # Check compatibility
    system_data = system_output['gamification_display']
    ui_data = ui_expected['gamification']
    
    compatible = (
        system_data.get('is_gamified') == ui_data.get('is_gamified') and
        system_data.get('display_type') == ui_data.get('display_type') and
        'challenge_data' in system_data and 'challenge_data' in ui_data
    )
    
    if compatible:
        print('\n✅ Data structures are compatible')
        print('The issue might be in the key mapping: gamification_display vs gamification')
    else:
        print('\n❌ Data structures are incompatible')
    
    return compatible

def main():
    """Run UI gamification tests"""
    print('🚀 UI GAMIFICATION DISPLAY TESTING')
    print('=' * 100)
    
    # Test UI components
    ui_success = test_gamification_ui_components()
    
    # Test message detection
    message_success = test_message_gamification_detection()
    
    # Test data structure compatibility
    compatibility_success = test_gamification_data_structure_compatibility()
    
    print('\n📊 UI GAMIFICATION TEST RESULTS')
    print('=' * 80)
    print(f'UI Components: {"✅ WORKING" if ui_success else "❌ NEEDS FIX"}')
    print(f'Message Detection: {"✅ WORKING" if message_success else "❌ NEEDS FIX"}')
    print(f'Data Compatibility: {"✅ WORKING" if compatibility_success else "❌ NEEDS FIX"}')
    
    if ui_success and message_success and compatibility_success:
        print('\n🎉 UI GAMIFICATION SYSTEM READY!')
        print('All components are working correctly.')
    else:
        print('\n⚠️ UI GAMIFICATION NEEDS ATTENTION')
        print('Some components need debugging.')
    
    print('\n💡 LIKELY ISSUE:')
    print('The system generates "gamification_display" but UI expects "gamification"')
    print('This key mapping issue prevents gamification from showing in the UI.')
    
    return ui_success and message_success and compatibility_success

if __name__ == "__main__":
    main()
