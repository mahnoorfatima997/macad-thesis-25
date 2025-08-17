#!/usr/bin/env python3
"""
Enhanced Gamification Demo
Showcases the new visual, interactive gamification system.
"""

import streamlit as st
import sys
import os

# Add paths
sys.path.insert(0, 'thesis-agents')
sys.path.insert(0, 'dashboard')

def setup_demo_page():
    """Setup the demo page."""
    st.set_page_config(
        page_title="🎮 Enhanced Gamification Demo",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎮 Enhanced Gamification System Demo")
    st.markdown("**Experience the new visual, interactive gamification!**")
    
    # Comparison section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ❌ Old System (Text-Based)")
        st.markdown("""
        - Plain text challenges
        - Non-functional buttons
        - Boring presentation
        - Low engagement
        """)
    
    with col2:
        st.markdown("### ✅ New System (Visual & Interactive)")
        st.markdown("""
        - **Visual card interfaces**
        - **Interactive games & puzzles**
        - **Animated elements**
        - **High engagement**
        """)
    
    st.markdown("---")

def create_demo_scenarios():
    """Create demo scenarios for each game type."""
    return {
        "🎭 Persona Card Game": {
            "type": "role_play",
            "content": "🎭 ROLE-PLAY CHALLENGE: Step into someone else's shoes!\n\n*You are now an elderly person with limited mobility entering your community center for the first time.*\n\nYou're using a walker and feeling uncertain about this new space. Walk me through your experience.",
            "building_type": "community center",
            "description": "Interactive persona selection with visual cards and immersive scenarios"
        },
        "🎯 Perspective Wheel": {
            "type": "perspective_shift", 
            "content": "🎯 PERSPECTIVE SHIFT: Time for a reality check!\n\n*Plot twist: You're designing for someone completely different than you imagined.*\n\nYour assumptions about users just got challenged. How does this change everything?",
            "building_type": "community center",
            "description": "Spin-the-wheel game with colorful perspective cards and point system"
        },
        "🔍 Mystery Investigation": {
            "type": "detective",
            "content": "🔍 USER DETECTIVE: Let's solve a mystery!\n\n*Your community center has a secret - different users experience it completely differently.*\n\nWhat clues in your design reveal these hidden experiences?",
            "building_type": "community center", 
            "description": "Interactive clue investigation with progress tracking and detective points"
        },
        "🏗️ Constraint Puzzle": {
            "type": "constraint",
            "content": "🏗️ SPACE TRANSFORMATION: Your design just got interesting!\n\n*Your community center just got hit with multiple constraints.*\n\nHow do you turn these limitations into design superpowers?",
            "building_type": "community center",
            "description": "Interactive constraint selection with creativity scoring and bonus challenges"
        }
    }

def main():
    """Main demo interface."""
    setup_demo_page()
    
    # Import enhanced gamification
    try:
        from ui.enhanced_gamification import render_enhanced_gamified_challenge, inject_gamification_css
        
        # Inject CSS for animations
        inject_gamification_css()
        
        st.success("✅ Enhanced Gamification System Loaded!")
        
    except ImportError as e:
        st.error(f"❌ Could not load enhanced gamification: {e}")
        st.info("Make sure you're running from the correct directory with all files present.")
        return
    
    # Demo scenarios
    scenarios = create_demo_scenarios()
    
    # Sidebar controls
    st.sidebar.header("🎮 Demo Controls")
    
    selected_demo = st.sidebar.selectbox(
        "Choose Demo Game:",
        options=list(scenarios.keys())
    )
    
    scenario = scenarios[selected_demo]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Game Info")
    st.sidebar.markdown(f"**Type:** {scenario['type']}")
    st.sidebar.markdown(f"**Building:** {scenario['building_type']}")
    st.sidebar.markdown(f"**Features:** {scenario['description']}")
    
    # Auto-play option
    auto_play = st.sidebar.checkbox("🔄 Auto-cycle through all games", value=False)
    
    if auto_play:
        st.sidebar.info("🎮 Showing all game types automatically")
    
    # Main demo area
    st.header(f"🎮 {selected_demo}")
    st.markdown(f"**{scenario['description']}**")
    
    # Create challenge data
    challenge_data = {
        "challenge_type": scenario["type"],
        "challenge_text": scenario["content"],
        "building_type": scenario["building_type"],
        "gamification_applied": True
    }
    
    # Render the enhanced gamification
    try:
        render_enhanced_gamified_challenge(challenge_data)
        
        # Success feedback
        st.sidebar.success("✅ Game rendered successfully!")
        
    except Exception as e:
        st.error(f"❌ Demo failed: {str(e)}")
        st.code(f"Error: {e}", language="python")
    
    # Auto-cycle through all games
    if auto_play:
        st.markdown("---")
        st.markdown("## 🎮 All Game Types Preview")
        
        for game_name, game_scenario in scenarios.items():
            if game_name != selected_demo:  # Don't repeat the selected one
                st.markdown(f"### {game_name}")
                
                game_challenge_data = {
                    "challenge_type": game_scenario["type"],
                    "challenge_text": game_scenario["content"],
                    "building_type": game_scenario["building_type"],
                    "gamification_applied": True
                }
                
                try:
                    render_enhanced_gamified_challenge(game_challenge_data)
                except Exception as e:
                    st.error(f"❌ {game_name} failed: {str(e)}")
                
                st.markdown("---")
    
    # Feature highlights
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✨ New Features")
    st.sidebar.markdown("""
    - 🎨 **Visual Cards** - Beautiful, colorful interfaces
    - 🎮 **Interactive Games** - Click, select, and play
    - 📊 **Progress Tracking** - Points and achievements
    - 🎯 **Smart Challenges** - Context-aware scenarios
    - 🎭 **Immersive Personas** - Step into user shoes
    - 🔍 **Mystery Games** - Investigate and solve
    - 🧩 **Puzzle Challenges** - Creative problem-solving
    - ⚡ **Animations** - Smooth, engaging transitions
    """)
    
    # Comparison with old system
    st.markdown("---")
    st.markdown("## 📊 System Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Visual Appeal", "🔥 High", delta="vs. Low (old)")
    
    with col2:
        st.metric("Interactivity", "🎮 Full", delta="vs. None (old)")
    
    with col3:
        st.metric("Engagement", "⭐ Excellent", delta="vs. Poor (old)")
    
    # Instructions
    st.markdown("---")
    st.markdown("## 🚀 How to Use")
    st.markdown("""
    1. **Select a game type** from the sidebar
    2. **Interact with the visual elements** - click cards, buttons, and options
    3. **Follow the game prompts** - each game has unique mechanics
    4. **Earn points and achievements** - track your progress
    5. **Try all game types** - each offers different experiences
    
    **🎯 Pro Tip:** Enable "Auto-cycle" to see all games at once!
    """)

if __name__ == "__main__":
    main()
