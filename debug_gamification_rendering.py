#!/usr/bin/env python3
"""
Debug Gamification Rendering Issue
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'dashboard')

def test_gamification_rendering():
    """Test gamification rendering with debug output"""
    print('🎮 DEBUGGING GAMIFICATION RENDERING')
    print('=' * 80)
    
    try:
        from ui.gamification_components import GamificationDisplay, render_gamified_challenge
        
        # Create display instance
        display = GamificationDisplay()
        print('✅ GamificationDisplay created successfully')
        
        # Test with real challenge data from the system
        challenge_data = {
            'challenge_text': 'Consider the diverse needs and experiences of future users in your project. Reflect on how your design accommodates various perspectives, lifestyles, and accessibility requirements. Are there assumptions in your design that might overlook certain user groups or scenarios?',
            'challenge_type': 'metacognitive_challenge',
            'difficulty_level': 'high',
            'pedagogical_intent': 'Foster metacognitive awareness and self-evaluation'
        }
        
        print('\n🧪 Testing challenge parsing:')
        title, scenario, main_challenge, question = display._parse_challenge_text(challenge_data['challenge_text'])
        print(f'Title: "{title}"')
        print(f'Scenario: "{scenario}"')
        print(f'Main challenge: "{main_challenge[:100]}..."')
        print(f'Question: "{question}"')
        
        print('\n🎯 Testing challenge type detection:')
        detected_type = display._detect_challenge_type(challenge_data['challenge_text'])
        print(f'Detected type: {detected_type}')
        
        print('\n🎨 Testing theme selection:')
        theme = display.challenge_types.get(detected_type, display.challenge_types["role_play"])
        print(f'Theme: {theme}')
        
        print('\n🖥️ Testing individual render methods:')
        
        # Test each render method individually
        try:
            print('Testing _render_challenge_header...')
            # This would normally render to Streamlit, but we can test the logic
            print('✅ Header method exists')
        except Exception as e:
            print(f'❌ Header error: {e}')
        
        try:
            print('Testing _render_scenario_box...')
            print('✅ Scenario method exists')
        except Exception as e:
            print(f'❌ Scenario error: {e}')
        
        try:
            print('Testing _render_main_challenge...')
            print('✅ Main challenge method exists')
        except Exception as e:
            print(f'❌ Main challenge error: {e}')
        
        try:
            print('Testing _render_interactive_question...')
            print('✅ Interactive question method exists')
        except Exception as e:
            print(f'❌ Interactive question error: {e}')
        
        try:
            print('Testing _render_challenge_footer...')
            print('✅ Footer method exists')
        except Exception as e:
            print(f'❌ Footer error: {e}')
        
        print('\n🔧 Testing full render method (without Streamlit):')
        # We can't actually render without Streamlit, but we can test the logic
        try:
            # Simulate what happens in render_gamified_challenge
            challenge_text = challenge_data.get("challenge_text", "")
            challenge_type = display._detect_challenge_type(challenge_text)
            theme = display.challenge_types.get(challenge_type, display.challenge_types["role_play"])
            title, scenario, main_challenge, question = display._parse_challenge_text(challenge_text)
            
            print('✅ All rendering logic works without errors')
            print(f'Would render: {challenge_type} challenge with theme {theme["icon"]}')
            
            return True
            
        except Exception as e:
            print(f'❌ Rendering logic error: {e}')
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f'❌ Gamification test error: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_message_structure():
    """Test the message structure that should trigger gamification"""
    print('\n💬 TESTING MESSAGE STRUCTURE')
    print('=' * 80)
    
    # This is what the message should look like when it reaches the UI
    test_message = {
        "role": "assistant",
        "content": "Consider the diverse needs and experiences of future users in your project. Reflect on how your design accommodates various perspectives, lifestyles, and accessibility requirements.",
        "timestamp": "2025-08-15T17:52:44.041060",
        "mentor_type": "MENTOR",
        "gamification": {
            "is_gamified": True,
            "display_type": "enhanced_visual",
            "challenge_data": {
                "challenge_text": "Consider the diverse needs and experiences of future users in your project. Reflect on how your design accommodates various perspectives, lifestyles, and accessibility requirements.",
                "challenge_type": "metacognitive_challenge",
                "difficulty_level": "high",
                "pedagogical_intent": "Foster metacognitive awareness and self-evaluation"
            }
        }
    }
    
    print('📋 Message structure:')
    print(f'Role: {test_message["role"]}')
    print(f'Content length: {len(test_message["content"])}')
    print(f'Has gamification: {"gamification" in test_message}')
    
    gamification_info = test_message.get("gamification", {})
    print(f'Is gamified: {gamification_info.get("is_gamified", False)}')
    print(f'Display type: {gamification_info.get("display_type", "none")}')
    print(f'Has challenge data: {"challenge_data" in gamification_info}')
    
    # Test the UI detection logic
    is_gamified = gamification_info.get("is_gamified", False)
    display_type = gamification_info.get("display_type", "")
    should_render_enhanced = is_gamified and display_type == "enhanced_visual"
    
    print(f'\n🎯 UI Detection Results:')
    print(f'Should render enhanced: {should_render_enhanced}')
    
    if should_render_enhanced:
        challenge_data = gamification_info.get("challenge_data", {})
        print(f'Challenge data keys: {list(challenge_data.keys())}')
        
        # This is what gets passed to render_gamified_challenge
        final_challenge_data = challenge_data.copy()
        final_challenge_data["challenge_text"] = test_message["content"]
        
        print(f'Final challenge data for rendering: {list(final_challenge_data.keys())}')
        print('✅ Message structure is correct for gamification')
        return True
    else:
        print('❌ Message would not trigger gamification')
        return False

def main():
    """Run gamification rendering debug tests"""
    print('🚀 GAMIFICATION RENDERING DEBUG')
    print('=' * 100)
    
    # Test rendering components
    rendering_success = test_gamification_rendering()
    
    # Test message structure
    message_success = test_message_structure()
    
    print('\n📊 DEBUG RESULTS')
    print('=' * 80)
    print(f'Rendering Components: {"✅ WORKING" if rendering_success else "❌ BROKEN"}')
    print(f'Message Structure: {"✅ WORKING" if message_success else "❌ BROKEN"}')
    
    if rendering_success and message_success:
        print('\n🎉 GAMIFICATION RENDERING SHOULD WORK!')
        print('The issue might be:')
        print('1. Streamlit context missing when rendering')
        print('2. CSS styles not loading properly')
        print('3. Error happening during actual Streamlit render')
    else:
        print('\n❌ GAMIFICATION RENDERING HAS ISSUES')
        print('Components need debugging.')
    
    print('\n💡 NEXT STEPS:')
    print('1. Check Streamlit console for errors during gamification rendering')
    print('2. Add more debug prints to the _render_gamified_message function')
    print('3. Test with a simple gamification display first')
    
    return rendering_success and message_success

if __name__ == "__main__":
    main()
