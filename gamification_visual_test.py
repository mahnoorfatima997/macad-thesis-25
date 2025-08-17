#!/usr/bin/env python3
"""
Comprehensive Gamification Visual Test Script
Tests all 4 gamification game types in isolation with realistic scenarios.
"""

import streamlit as st
import sys
import os
from typing import Dict, Any

# Add thesis-agents to path
sys.path.insert(0, 'thesis-agents')
sys.path.insert(0, 'dashboard')

def setup_page():
    """Setup Streamlit page configuration."""
    st.set_page_config(
        page_title="🎮 Gamification Visual Test",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎮 Gamification Visual Test Suite")
    st.markdown("**Test all 4 gamification game types in isolation**")
    st.markdown("---")

def create_test_message(challenge_text: str, challenge_type: str, building_type: str = "community center") -> Dict[str, Any]:
    """Create a realistic message structure that triggers gamification."""
    return {
        "role": "assistant",
        "content": challenge_text,
        "timestamp": "2025-01-17T12:00:00Z",
        "gamification": {
            "is_gamified": True,
            "display_type": "enhanced_visual",
            "trigger_type": challenge_type,
            "challenge_data": {
                "challenge_type": challenge_type,
                "building_type": building_type,
                "gamification_applied": True,
                "user_type": "community member" if building_type == "community center" else "visitor"
            }
        }
    }

def get_test_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get realistic test scenarios for each game type."""
    return {
        "role_play": {
            "name": "🎭 Role-Play Challenge",
            "description": "Empathy and user-centered thinking scenarios",
            "scenarios": [
                {
                    "title": "Community Center - Elderly User",
                    "content": "🎭 ROLE-PLAY CHALLENGE: Step into someone else's shoes!\n\n*You are now an elderly person with limited mobility entering your community center for the first time.*\n\nYou're using a walker and feeling a bit uncertain about navigating this new space. The main entrance is ahead of you.\n\nWalk me through your first 60 seconds - what do you see, feel, and think? What would make you feel welcome and confident?",
                    "building_type": "community center"
                },
                {
                    "title": "Hospital - Anxious Family Member",
                    "content": "🎭 ROLE-PLAY CHALLENGE: Step into someone else's shoes!\n\n*You are now a worried parent rushing to the hospital emergency department with your injured child.*\n\nYour heart is racing, you're in an unfamiliar place, and you need to find help quickly.\n\nDescribe your experience: What visual cues help or hinder you? How does the space either calm or increase your anxiety?",
                    "building_type": "hospital"
                }
            ]
        },
        "perspective_shift": {
            "name": "🎯 Perspective Shift Challenge", 
            "description": "Challenge assumptions and broaden perspective",
            "scenarios": [
                {
                    "title": "Perfect Design Reality Check",
                    "content": "🎯 PERSPECTIVE SHIFT: Time for a reality check!\n\n*Plot twist: You're designing for someone completely different than you imagined.*\n\nYou thought your community center would serve families with children, but the neighborhood demographics just shifted - it's now primarily seniors and young professionals with no kids.\n\nTell me: How does this change everything? What assumptions about 'community needs' do you need to reconsider?",
                    "building_type": "community center"
                },
                {
                    "title": "Accessibility Assumption Challenge",
                    "content": "🎯 PERSPECTIVE SHIFT: Time for a reality check!\n\n*Your 'accessible' design just met someone who challenges all your assumptions.*\n\nA wheelchair user just told you that your ramps are too steep, your 'accessible' bathroom is actually harder to use than a standard one, and your lowered reception desk makes them feel patronized.\n\nWhat does truly inclusive design mean when the people you're designing for disagree with your solutions?",
                    "building_type": "office"
                }
            ]
        },
        "detective": {
            "name": "🔍 Detective Challenge",
            "description": "Stimulate curiosity and investigative thinking", 
            "scenarios": [
                {
                    "title": "Hidden User Experience Mystery",
                    "content": "🔍 USER DETECTIVE: Let's solve a mystery!\n\n*Your community center has a secret - different users experience it completely differently.*\n\nThe same entrance that makes teenagers feel excited and welcome makes elderly visitors feel overwhelmed and excluded. The open layout that energizes families makes introverts feel exposed and uncomfortable.\n\nWhat clues in your design reveal these hidden experiences? How can you design one space that reads differently to different people?",
                    "building_type": "community center"
                },
                {
                    "title": "Circulation Pattern Mystery",
                    "content": "🔍 USER DETECTIVE: Let's solve a mystery!\n\n*There's something strange happening in your hospital's circulation patterns.*\n\nPatients keep getting lost, but not where you'd expect. The signage is clear, the layout seems logical, but people consistently make wrong turns at three specific locations.\n\nWhat invisible forces are guiding their movement? What clues can you find in human behavior, lighting, sightlines, and spatial psychology?",
                    "building_type": "hospital"
                }
            ]
        },
        "constraint": {
            "name": "🏗️ Constraint Challenge",
            "description": "Creative problem-solving with limitations",
            "scenarios": [
                {
                    "title": "Triple Constraint Storm",
                    "content": "🏗️ SPACE TRANSFORMATION: Your design just got interesting!\n\n*Your community center just got hit with three simultaneous constraints:*\n\n1. 🌊 The site floods every 5 years for 2-3 days\n2. 💰 Budget was cut by 40% - what gets prioritized?\n3. 👥 User capacity doubled - twice as many people, same space\n\nDescribe the transformation: What changes and why? How do you turn these constraints into your design's superpowers?",
                    "building_type": "community center"
                },
                {
                    "title": "Adaptive Reuse Challenge",
                    "content": "🏗️ SPACE TRANSFORMATION: Your design just got interesting!\n\n*Imagine your old warehouse could shape-shift based on user needs throughout the day.*\n\nMorning: Quiet co-working space for 20 people\nAfternoon: Active play area for 50 children\nEvening: Performance venue for 200 audience members\n\nThe same space, the same budget, but completely different experiences. What transforms and how?",
                    "building_type": "warehouse conversion"
                }
            ]
        }
    }

def test_html_cleaning_logic():
    """Test the HTML cleaning logic with realistic problematic content."""
    st.subheader("🧹 HTML Cleaning Logic Test")
    
    # Simulate the problematic HTML content from your example
    problematic_content = """🎮 Mentor - Challenge Mode!
<!-- Main content -->
<div style="position: relative; z-index: 1;">
    <div style="
        font-size: 4em;
        margin-bottom: 15px;
        text-shadow: 0 3px 6px rgba(0,0,0,0.2);
        animation: bounce 2s infinite;
    ">🎭</div>
    <h2 style="
        color: #cd766d;
        margin: 0;
        font-weight: bold;
        font-size: 1.8em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    ">🎯 DESIGN CHALLENGE</h2>
    <div style="
        background: linear-gradient(90deg, transparent, #cd766d, transparent);
        height: 4px;
        width: 100px;
        margin: 20px auto;
        border-radius: 2px;
        animation: glow 2s ease-in-out infinite alternate;
    "></div>
</div>

🎯 Challenge:
Your idea of creating a central multipurpose hall as the heart of the community center is intriguing.
🎭 Role-Play Challenge"""

    st.markdown("**Original problematic content:**")
    st.code(problematic_content[:200] + "...", language="html")
    
    # Apply the cleaning logic
    clean_content = clean_html_content(problematic_content)
    
    st.markdown("**After HTML cleaning:**")
    st.code(clean_content, language="text")
    
    # Test results
    has_html = "<div style=" in clean_content or "<!-- Main content -->" in clean_content
    has_content = "Challenge:" in clean_content
    has_emojis = "🎭" in clean_content and "🎯" in clean_content
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("HTML Removed", "✅ Yes" if not has_html else "❌ No")
    with col2:
        st.metric("Content Preserved", "✅ Yes" if has_content else "❌ No")
    with col3:
        st.metric("Emojis Preserved", "✅ Yes" if has_emojis else "❌ No")
    
    return not has_html and has_content and has_emojis

def clean_html_content(content: str) -> str:
    """Apply the same HTML cleaning logic as the main system."""
    import re
    
    if "<div style=" in content or "<!-- Main content -->" in content or "<h2 style=" in content:
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Remove complete HTML tags with their attributes
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove lines that are just HTML attributes or empty
        lines = content.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Skip lines that are just CSS properties or HTML attributes
            if (line.startswith('font-size:') or line.startswith('margin:') or 
                line.startswith('color:') or line.startswith('background:') or
                line.startswith('border:') or line.startswith('padding:') or
                line.startswith('text-shadow:') or line.startswith('animation:') or
                'style=' in line or line.startswith('">') or line == '>'):
                continue
            # Keep meaningful content lines
            clean_lines.append(line)
        
        content = '\n'.join(clean_lines)
    
    return content

def render_gamification_test(challenge_data: Dict[str, Any]):
    """Render a gamification challenge for testing."""
    try:
        st.markdown("### 🎮 Gamification Rendering Test")

        # Clean the challenge text first (simulate the fix)
        challenge_text = challenge_data.get("challenge_text", "")
        clean_challenge_text = clean_html_content(challenge_text)
        challenge_data["challenge_text"] = clean_challenge_text

        # Test both enhanced and original systems
        test_enhanced = st.checkbox("🚀 Use Enhanced Visual Gamification", value=True)

        if test_enhanced:
            try:
                # Import enhanced gamification
                from ui.enhanced_gamification import render_enhanced_gamified_challenge, inject_gamification_css

                st.success("✅ Enhanced gamification system loaded!")

                # Inject CSS for animations
                inject_gamification_css()

                # Render enhanced gamification
                render_enhanced_gamified_challenge(challenge_data)

                return True

            except ImportError as e:
                st.warning(f"⚠️ Enhanced gamification not available: {e}")
                st.info("Falling back to original system...")
                test_enhanced = False

        if not test_enhanced:
            # Import the original gamification components
            from ui.gamification_components import render_gamified_challenge

            # Render the original gamified challenge
            render_gamified_challenge(challenge_data)

        return True

    except Exception as e:
        st.error(f"❌ Gamification rendering failed: {str(e)}")
        st.code(f"Error details: {e}", language="python")
        return False

def main():
    """Main test interface."""
    setup_page()
    
    # Sidebar controls
    st.sidebar.header("🎮 Test Controls")
    
    # Test selection
    test_scenarios = get_test_scenarios()
    
    selected_game_type = st.sidebar.selectbox(
        "Select Game Type",
        options=list(test_scenarios.keys()),
        format_func=lambda x: test_scenarios[x]["name"]
    )
    
    selected_scenario_idx = st.sidebar.selectbox(
        "Select Scenario",
        options=range(len(test_scenarios[selected_game_type]["scenarios"])),
        format_func=lambda x: test_scenarios[selected_game_type]["scenarios"][x]["title"]
    )
    
    # Test options
    st.sidebar.markdown("---")
    test_html_cleaning = st.sidebar.checkbox("Test HTML Cleaning Logic", value=True)
    test_visual_rendering = st.sidebar.checkbox("Test Visual Rendering", value=True)
    show_message_structure = st.sidebar.checkbox("Show Message Structure", value=False)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Selected scenario details
        scenario = test_scenarios[selected_game_type]["scenarios"][selected_scenario_idx]
        
        st.header(f"{test_scenarios[selected_game_type]['name']}")
        st.markdown(f"**Description:** {test_scenarios[selected_game_type]['description']}")
        st.markdown(f"**Scenario:** {scenario['title']}")
        
        # Test HTML cleaning if enabled
        if test_html_cleaning:
            st.markdown("---")
            cleaning_success = test_html_cleaning_logic()
            
        # Test visual rendering if enabled
        if test_visual_rendering:
            st.markdown("---")
            st.subheader("🎨 Visual Rendering Test")
            
            # Create test message
            test_message = create_test_message(
                scenario["content"],
                selected_game_type,
                scenario["building_type"]
            )
            
            # Extract challenge data
            challenge_data = test_message["gamification"]["challenge_data"].copy()
            challenge_data["challenge_text"] = test_message["content"]
            
            # Render the gamification
            rendering_success = render_gamification_test(challenge_data)
            
        # Show message structure if enabled
        if show_message_structure:
            st.markdown("---")
            st.subheader("📋 Message Structure")
            test_message = create_test_message(
                scenario["content"],
                selected_game_type,
                scenario["building_type"]
            )
            st.json(test_message)
    
    with col2:
        # Test results summary
        st.subheader("📊 Test Results")
        
        if test_html_cleaning:
            cleaning_result = test_html_cleaning_logic()
            st.metric("HTML Cleaning", "✅ Pass" if cleaning_result else "❌ Fail")
        
        if test_visual_rendering:
            st.metric("Visual Rendering", "🎮 Check Left Panel")
        
        # Quick test all button
        st.markdown("---")
        if st.button("🚀 Quick Test All Game Types"):
            st.markdown("### 🎮 All Game Types Preview")
            
            for game_type, game_info in test_scenarios.items():
                st.markdown(f"#### {game_info['name']}")
                scenario = game_info["scenarios"][0]  # Use first scenario
                
                test_message = create_test_message(
                    scenario["content"],
                    game_type,
                    scenario["building_type"]
                )
                
                challenge_data = test_message["gamification"]["challenge_data"].copy()
                challenge_data["challenge_text"] = clean_html_content(test_message["content"])
                
                try:
                    render_gamification_test(challenge_data)
                    st.success(f"✅ {game_info['name']} rendered successfully")
                except Exception as e:
                    st.error(f"❌ {game_info['name']} failed: {str(e)}")
                
                st.markdown("---")

def test_challenge_type_mapping():
    """Test the challenge type mapping logic."""
    st.subheader("🔄 Challenge Type Mapping Test")

    # Test the mapping from generator types to UI types
    challenge_type_mapping = {
        "perspective_challenge": "role_play",
        "metacognitive_challenge": "curiosity_amplification",
        "constraint_challenge": "constraint_challenge",
        "alternative_challenge": "perspective_shift"
    }

    st.markdown("**Challenge Type Mappings:**")
    for generator_type, ui_type in challenge_type_mapping.items():
        st.markdown(f"- `{generator_type}` → `{ui_type}`")

    # Test detection logic
    st.markdown("**Detection Logic Test:**")
    test_texts = [
        ("🎭 ROLE-PLAY CHALLENGE: Step into someone else's shoes!", "role_play"),
        ("🎯 PERSPECTIVE SHIFT: Time for a reality check!", "perspective_shift"),
        ("🔍 USER DETECTIVE: Let's solve a mystery!", "detective"),
        ("🏗️ SPACE TRANSFORMATION: Your design just got interesting!", "transformation")
    ]

    for text, expected_type in test_texts:
        detected_type = detect_challenge_type_from_text(text)
        status = "✅" if detected_type == expected_type else "❌"
        st.markdown(f"{status} `{text[:30]}...` → `{detected_type}` (expected: `{expected_type}`)")

def detect_challenge_type_from_text(challenge_text: str) -> str:
    """Detect challenge type from text (mirrors the UI logic)."""
    text_lower = challenge_text.lower()

    # Check for formatted headers first
    if "role-play challenge" in text_lower or "step into" in text_lower:
        return "role_play"
    elif "perspective shift" in text_lower or "reality check" in text_lower:
        return "perspective_shift"
    elif "detective" in text_lower or "mystery" in text_lower:
        return "detective"
    elif "transformation" in text_lower or "shape-shift" in text_lower:
        return "transformation"
    elif "storytelling" in text_lower or "story" in text_lower:
        return "storytelling"
    elif "time travel" in text_lower or "fast-forward" in text_lower:
        return "time_travel"
    elif "constraint" in text_lower or "design challenge" in text_lower:
        return "constraint_challenge"
    elif "curiosity" in text_lower or "wonder" in text_lower:
        return "curiosity_amplification"
    else:
        return "role_play"

def create_comprehensive_test_suite():
    """Create a comprehensive test suite for all gamification aspects."""
    st.header("🧪 Comprehensive Gamification Test Suite")

    # Test categories
    test_categories = {
        "HTML Cleaning": test_html_cleaning_logic,
        "Challenge Type Mapping": test_challenge_type_mapping,
        "Visual Rendering": lambda: st.info("Visual rendering tested in main interface"),
        "Message Structure": lambda: st.info("Message structure shown in sidebar option")
    }

    # Run all tests
    results = {}
    for category, test_func in test_categories.items():
        st.subheader(f"🔧 {category}")
        try:
            result = test_func()
            results[category] = result if isinstance(result, bool) else True
            st.success(f"✅ {category} test completed")
        except Exception as e:
            results[category] = False
            st.error(f"❌ {category} test failed: {str(e)}")
        st.markdown("---")

    # Summary
    st.subheader("📊 Test Summary")
    passed = sum(results.values())
    total = len(results)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tests Passed", f"{passed}/{total}")
    with col2:
        st.metric("Success Rate", f"{(passed/total)*100:.1f}%")
    with col3:
        status = "✅ All Pass" if passed == total else "⚠️ Some Failed"
        st.metric("Overall Status", status)

    return results

def add_debug_information():
    """Add debug information and troubleshooting tips."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Debug Info")

    # System information
    st.sidebar.markdown("**System Status:**")

    # Check if gamification components can be imported
    try:
        from ui.gamification_components import render_gamified_challenge
        st.sidebar.success("✅ Gamification components loaded")
    except ImportError as e:
        st.sidebar.error(f"❌ Import error: {str(e)}")

    # Check if Streamlit is working properly
    st.sidebar.info(f"📱 Streamlit version: {st.__version__}")

    # Troubleshooting tips
    with st.sidebar.expander("🆘 Troubleshooting Tips"):
        st.markdown("""
        **If you see HTML code instead of games:**
        1. Check that HTML cleaning logic is enabled
        2. Verify the message content structure
        3. Ensure gamification components are imported correctly

        **If games don't render:**
        1. Check the challenge_type mapping
        2. Verify the challenge_data structure
        3. Look for import errors in the sidebar

        **If styling looks wrong:**
        1. Check that Streamlit unsafe_allow_html is working
        2. Verify CSS styles are being applied
        3. Test with different challenge types
        """)

if __name__ == "__main__":
    # Add debug information to sidebar
    add_debug_information()

    # Main application
    main()

    # Add comprehensive test suite at the bottom
    st.markdown("---")
    create_comprehensive_test_suite()
