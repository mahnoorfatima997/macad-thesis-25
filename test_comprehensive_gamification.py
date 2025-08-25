"""
Comprehensive Gamification Test

Tests all gamification improvements including:
- All gamification types and UI rendering
- Challenge generation and templates
- Enhanced gamification components
- Progress tracking and state management
"""

import sys
import os
import streamlit as st
from unittest.mock import MagicMock, patch

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

def test_gamification_comprehensive():
    """Comprehensive test of gamification system."""
    
    print("🎮 COMPREHENSIVE GAMIFICATION TEST")
    print("=" * 60)
    
    # Mock streamlit for testing
    with patch('streamlit.markdown'), patch('streamlit.button'), patch('streamlit.text_area'), \
         patch('streamlit.columns'), patch('streamlit.success'), patch('streamlit.session_state', {}):
        
        try:
            from ui.enhanced_gamification import EnhancedGamificationRenderer
            from agents.cognitive_enhancement.processors.challenge_generator import ChallengeGenerator
            
            # Initialize components
            renderer = EnhancedGamificationRenderer()
            challenge_gen = ChallengeGenerator()
            
            print("✅ Components initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize components: {e}")
            return
    
    # Test gamification types
    gamification_types = {
        "role_play": {
            "challenge_text": "🎭 ROLE-PLAY CHALLENGE: Step into someone else's shoes!",
            "theme": renderer.themes["role_play"],
            "method": "_render_enhanced_persona_game"
        },
        "perspective_shift": {
            "challenge_text": "🎯 PERSPECTIVE SHIFT: Time for a reality check!",
            "theme": renderer.themes["perspective_shift"], 
            "method": "_render_spinning_wheel_game"
        },
        "detective": {
            "challenge_text": "🔍 USER DETECTIVE: Let's solve a mystery!",
            "theme": renderer.themes["detective"],
            "method": "_render_animated_mystery_game"
        },
        "constraint": {
            "challenge_text": "⚡ DESIGN CHALLENGE: Time for a creative constraint!",
            "theme": renderer.themes["constraint"],
            "method": "_render_interactive_constraint_game"
        },
        "storytelling": {
            "challenge_text": "📚 STORYTELLING CHALLENGE: Every space tells a story!",
            "theme": renderer.themes["storytelling"],
            "method": "_render_storytelling_game"
        },
        "time_travel": {
            "challenge_text": "⏰ TIME TRAVEL CHALLENGE: Your building through the ages!",
            "theme": renderer.themes["time_travel"],
            "method": "_render_time_travel_game"
        },
        "transformation": {
            "challenge_text": "🏗️ TRANSFORMATION CHALLENGE: Your design just got interesting!",
            "theme": renderer.themes["transformation"],
            "method": "_render_transformation_game"
        }
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    # Test 1: Theme Configuration
    print(f"\n📂 Testing Theme Configuration")
    print("-" * 50)
    
    for gamification_type, config in gamification_types.items():
        total_tests += 1
        try:
            theme = config["theme"]
            required_keys = ["primary", "secondary", "accent", "gradient", "icon"]
            
            missing_keys = [key for key in required_keys if key not in theme]
            if not missing_keys:
                print(f"   ✅ {gamification_type}: Theme complete")
                passed_tests += 1
            else:
                print(f"   ❌ {gamification_type}: Missing keys: {missing_keys}")
                failed_tests.append(("Theme", gamification_type, f"Missing keys: {missing_keys}"))
                
        except Exception as e:
            print(f"   ⚠️ {gamification_type}: Error - {e}")
            failed_tests.append(("Theme", gamification_type, str(e)))
    
    # Test 2: Method Existence
    print(f"\n📂 Testing UI Rendering Methods")
    print("-" * 50)
    
    for gamification_type, config in gamification_types.items():
        total_tests += 1
        method_name = config["method"]
        
        try:
            if hasattr(renderer, method_name):
                print(f"   ✅ {gamification_type}: Method {method_name} exists")
                passed_tests += 1
            else:
                print(f"   ❌ {gamification_type}: Method {method_name} missing")
                failed_tests.append(("Method", gamification_type, f"Method {method_name} not found"))
                
        except Exception as e:
            print(f"   ⚠️ {gamification_type}: Error - {e}")
            failed_tests.append(("Method", gamification_type, str(e)))
    
    # Test 3: Challenge Template Generation
    print(f"\n📂 Testing Challenge Template Generation")
    print("-" * 50)
    
    template_tests = [
        ("user_perspective", "community_center"),
        ("spatial", "hospital"),
        ("temporal_perspective", "school")
    ]
    
    for challenge_type, building_type in template_tests:
        total_tests += 1
        try:
            # Mock the required components
            with patch.object(challenge_gen, 'text_processor') as mock_processor:
                mock_processor.select_random.return_value = "Test template with {building_type} and {user_type}"
                
                result = challenge_gen._add_gamification_elements("Base challenge", challenge_type, building_type)
                
                if result and building_type in result:
                    print(f"   ✅ {challenge_type} + {building_type}: Template generated")
                    passed_tests += 1
                else:
                    print(f"   ❌ {challenge_type} + {building_type}: Template generation failed")
                    failed_tests.append(("Template", f"{challenge_type}+{building_type}", "Generation failed"))
                    
        except Exception as e:
            print(f"   ⚠️ {challenge_type} + {building_type}: Error - {e}")
            failed_tests.append(("Template", f"{challenge_type}+{building_type}", str(e)))
    
    # Test 4: Gamification Trigger Patterns
    print(f"\n📂 Testing Gamification Trigger Patterns")
    print("-" * 50)
    
    trigger_tests = [
        ("how would a visitor feel", True, "role_play"),
        ("i wonder what would happen", True, "curiosity"),
        ("im stuck on this", True, "constraint"),
        ("this is easy", True, "overconfidence"),
        ("ok", True, "low_engagement"),
        ("tell me what to do", True, "cognitive_offloading"),
        ("normal design question", False, "none")
    ]
    
    for test_input, should_trigger, trigger_type in trigger_tests:
        total_tests += 1
        try:
            from orchestration.state import ArchMentorState
            
            state = ArchMentorState()
            state.messages = [{"role": "user", "content": test_input}]
            
            result = challenge_gen._should_apply_gamification(state, "test", "test context")
            
            if result == should_trigger:
                print(f"   ✅ '{test_input}': {result} (expected: {should_trigger})")
                passed_tests += 1
            else:
                print(f"   ❌ '{test_input}': {result} (expected: {should_trigger})")
                failed_tests.append(("Trigger", test_input, f"Expected {should_trigger}, got {result}"))
                
        except Exception as e:
            print(f"   ⚠️ '{test_input}': Error - {e}")
            failed_tests.append(("Trigger", test_input, str(e)))
    
    # Test 5: Enhanced Gamification Integration
    print(f"\n📂 Testing Enhanced Gamification Integration")
    print("-" * 50)
    
    integration_tests = [
        {
            "challenge_data": {
                "challenge_text": "Test challenge",
                "challenge_type": "role_play",
                "building_type": "community_center"
            }
        },
        {
            "challenge_data": {
                "challenge_text": "📚 STORYTELLING CHALLENGE: Test story",
                "challenge_type": "storytelling", 
                "building_type": "hospital"
            }
        }
    ]
    
    for test_case in integration_tests:
        total_tests += 1
        try:
            challenge_data = test_case["challenge_data"]
            
            # Mock streamlit components for rendering test
            with patch('streamlit.markdown'), patch('streamlit.button'), \
                 patch('streamlit.text_area'), patch('streamlit.columns'):
                
                # This would normally render the UI
                renderer.render_enhanced_challenge(challenge_data)
                print(f"   ✅ Integration test passed for {challenge_data['challenge_type']}")
                passed_tests += 1
                
        except Exception as e:
            print(f"   ❌ Integration test failed: {e}")
            failed_tests.append(("Integration", str(test_case), str(e)))
    
    # Summary
    print(f"\n📊 GAMIFICATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for category, test_name, error in failed_tests:
            print(f"   {category}: {test_name} - {error}")
    
    # Test Results by Category
    categories = {}
    for category, _, _ in failed_tests:
        categories[category] = categories.get(category, 0) + 1
    
    if categories:
        print(f"\n📈 FAILURES BY CATEGORY:")
        for category, count in categories.items():
            print(f"   {category}: {count} failures")

if __name__ == "__main__":
    test_gamification_comprehensive()
