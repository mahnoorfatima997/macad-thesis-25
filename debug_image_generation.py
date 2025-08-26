"""
Debug Image Generation System
Diagnose why images aren't appearing at phase completion.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add thesis-agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))

def test_replicate_connection():
    """Test Replicate API connection."""
    print("🔍 Testing Replicate API Connection")
    print("=" * 40)
    
    try:
        from vision.image_generator import ReplicateImageGenerator
        
        generator = ReplicateImageGenerator()
        
        # Test connection
        connection_ok = generator.test_connection()
        
        if connection_ok:
            print("✅ Replicate API connection successful")
            return True
        else:
            print("❌ Replicate API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Replicate connection: {e}")
        return False

def test_phase_progression_system():
    """Test the phase progression system initialization."""
    print("\n🔍 Testing Phase Progression System")
    print("=" * 40)
    
    try:
        from phase_progression_system import PhaseProgressionSystem
        
        # Initialize the system
        phase_system = PhaseProgressionSystem()
        
        # Check if image generation is enabled
        print(f"Image generation enabled: {phase_system.image_generation_enabled}")
        print(f"Image generator available: {phase_system.image_generator is not None}")
        print(f"Prompt generator available: {phase_system.prompt_generator is not None}")
        
        if phase_system.image_generation_enabled:
            print("✅ Phase progression system has image generation enabled")
            return True
        else:
            print("❌ Phase progression system does not have image generation enabled")
            return False
            
    except Exception as e:
        print(f"❌ Error testing phase progression system: {e}")
        return False

def test_image_generation_flow():
    """Test the complete image generation flow."""
    print("\n🔍 Testing Image Generation Flow")
    print("=" * 40)
    
    try:
        from vision.image_generator import ReplicateImageGenerator, DesignPromptGenerator
        
        # Initialize components
        image_generator = ReplicateImageGenerator()
        prompt_generator = DesignPromptGenerator()
        
        print("✅ Image generation components initialized")
        
        # Test prompt generation
        test_conversation = [
            {"role": "user", "content": "I want to design a community center"},
            {"role": "assistant", "content": "What kind of activities should it support?"},
            {"role": "user", "content": "It should have a library, meeting rooms, and a cafe"},
            {"role": "assistant", "content": "How do you envision the spatial organization?"},
            {"role": "user", "content": "I think an open central space with wings for different functions"}
        ]
        
        print("🤖 Testing prompt generation...")
        design_prompt = prompt_generator.generate_image_prompt_from_conversation(
            test_conversation,
            "ideation",
            "community center"
        )
        
        print(f"✅ Generated prompt: {design_prompt[:100]}...")
        
        # Test image generation (but don't actually generate to save API costs)
        print("🎨 Testing image generation setup...")
        
        if not image_generator.api_token:
            print("❌ No Replicate API token found")
            return False
        
        print("✅ Image generation setup complete")
        print("⚠️ Skipping actual image generation to save API costs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing image generation flow: {e}")
        return False

def test_phase_transition_detection():
    """Test phase transition detection and image generation trigger."""
    print("\n🔍 Testing Phase Transition Detection")
    print("=" * 40)

    try:
        from phase_progression_system import PhaseProgressionSystem, DesignPhase

        # Initialize system
        phase_system = PhaseProgressionSystem()

        # Create a test session using the correct method
        session_id = "test_debug_session"
        session = phase_system.start_session(session_id)

        print(f"✅ Test session created: {session_id}")
        print(f"Current phase: {session.current_phase.value}")
        print(f"Session initialized: {session is not None}")

        # Test phase completion check
        print("🔍 Testing phase completion logic...")

        # Simulate more detailed interactions to build up phase progress
        test_messages = [
            "I want to design a community center that serves multiple functions for our neighborhood",
            "The building should have a library with quiet reading areas, meeting rooms for community groups, and a cafe for social interaction",
            "I'm thinking about an open central atrium that connects all the different wings and creates a sense of community",
            "The library should be acoustically separated from the cafe to maintain quiet study areas",
            "Meeting rooms need flexible configurations with movable walls to accommodate different group sizes",
            "I want the building to feel welcoming and accessible to people of all ages and abilities",
            "The cafe should have both indoor and outdoor seating to create different social environments",
            "I'm considering how natural light can flow through the central atrium to all the different spaces",
            "The entrance should be clearly visible and create a strong sense of arrival",
            "I want to incorporate sustainable design features like solar panels and rainwater collection"
        ]

        for i, message in enumerate(test_messages):
            print(f"Processing message {i+1}: {message[:50]}...")
            result = phase_system.process_user_message(session_id, message)

            # Check current progress after each message
            summary = phase_system.get_session_summary(session_id)
            current_phase_data = summary.get('phase_summaries', {}).get('ideation', {})
            completion_percent = current_phase_data.get('completion_percent', 0)
            print(f"   Current completion: {completion_percent:.1f}%")

            if result.get('phase_transition'):
                print(f"🎉 Phase transition detected!")
                print(f"   Previous phase: {result.get('previous_phase')}")
                print(f"   New phase: {result.get('new_phase')}")
                print(f"   Generated image: {result.get('generated_image') is not None}")

                if result.get('generated_image'):
                    img_data = result['generated_image']
                    print(f"   Image URL: {img_data.get('url', 'No URL')}")
                    print(f"   Image phase: {img_data.get('phase', 'No phase')}")
                    print(f"   Image style: {img_data.get('style', 'No style')}")

                return True

        print("⚠️ No phase transition detected with test messages")

        # Check final phase progress
        summary = phase_system.get_session_summary(session_id)
        current_phase_data = summary.get('phase_summaries', {}).get('ideation', {})
        completion_percent = current_phase_data.get('completion_percent', 0)

        print(f"Final ideation phase completion: {completion_percent}%")

        # Try to manually trigger a phase transition to test image generation
        print("🔧 Attempting manual phase transition...")
        try:
            transition_result = phase_system.transition_to_next_phase(session_id)
            if transition_result.get('success'):
                print(f"✅ Manual transition successful!")
                print(f"   New phase: {transition_result.get('new_phase')}")
                print(f"   Generated image: {transition_result.get('generated_image') is not None}")

                if transition_result.get('generated_image'):
                    img_data = transition_result['generated_image']
                    print(f"   Image URL: {img_data.get('url', 'No URL')}")
                    print(f"   Image phase: {img_data.get('phase', 'No phase')}")
                    print(f"   Image style: {img_data.get('style', 'No style')}")
                    return True
            else:
                print(f"❌ Manual transition failed: {transition_result}")
        except Exception as e:
            print(f"❌ Error in manual transition: {e}")

        return False

    except Exception as e:
        print(f"❌ Error testing phase transition detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_integration():
    """Test how the dashboard handles generated images."""
    print("\n🔍 Testing Dashboard Integration")
    print("=" * 40)
    
    try:
        # Test the image display function
        print("Testing image display components...")
        
        # Mock generated image data
        test_image_data = {
            "url": "https://example.com/test_image.png",
            "prompt": "Modern community center design, architectural ideation phase",
            "style": "rough_sketch",
            "phase": "ideation"
        }
        
        print("✅ Mock image data created")
        print(f"   URL: {test_image_data['url']}")
        print(f"   Phase: {test_image_data['phase']}")
        print(f"   Style: {test_image_data['style']}")
        
        # Test if the chat components can handle image display
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard'))
            from ui.chat_components import _render_generated_image_in_chat
            print("✅ Image rendering function available")
        except ImportError as e:
            print(f"⚠️ Could not import image rendering function: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard integration: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("🚀 Image Generation Diagnostic Tool")
    print("=" * 60)
    
    tests = [
        ("Replicate API Connection", test_replicate_connection),
        ("Phase Progression System", test_phase_progression_system),
        ("Image Generation Flow", test_image_generation_flow),
        ("Phase Transition Detection", test_phase_transition_detection),
        ("Dashboard Integration", test_dashboard_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 Diagnostic Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n🔧 Potential Issues Identified:")
        for test_name, result in results:
            if not result:
                print(f"   • {test_name} failed - check the detailed output above")
        
        print("\n💡 Common Solutions:")
        print("   • Ensure REPLICATE_API_TOKEN is set in secrets.toml")
        print("   • Check that phase progression thresholds are reasonable")
        print("   • Verify image generation is enabled in phase system")
        print("   • Test with more detailed conversation to trigger phase transition")
    else:
        print("\n🎉 All tests passed! Image generation should be working.")
        print("If images still don't appear, the issue might be:")
        print("   • Phase transition thresholds too high")
        print("   • Not enough conversation to trigger transitions")
        print("   • UI display issues in the dashboard")

if __name__ == "__main__":
    main()
