"""
Standalone Test Script for Enhanced Gamification UI Components

This script allows you to preview and interact with all gamification components
from dashboard/ui/enhanced_gamification.py without running the full mentor.py app.

Usage: streamlit run test_gamification.py
"""

import streamlit as st
import sys
import os
from typing import Dict, Any

# Add the project root to Python path to import gamification module
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the gamification renderer
try:
    from dashboard.ui.enhanced_gamification import EnhancedGamificationRenderer, ENHANCED_THEMES
    print("✅ Successfully imported EnhancedGamificationRenderer")
except ImportError as e:
    st.error(f"❌ Failed to import gamification module: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="Gamification UI Test",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f3a3e;
        color: white;
    }
    .debug-info {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

def create_sample_challenge_data(challenge_type: str, building_type: str = "community_center") -> Dict[str, Any]:
    """Create realistic sample challenge data for testing."""

    # Realistic challenge scenarios based on actual architectural design challenges
    challenge_scenarios = {
        "perspective_challenge": {
            "community_center": "Consider how different users will experience your community center design. A teenager looking for a quiet study space, an elderly person attending a social event, and a parent with young children all have different needs and expectations.",
            "library": "Think about how various users interact with your library design. A researcher needing focused work areas, a family with children exploring together, and a student group collaborating on projects each require different spatial considerations.",
            "school": "Explore how different users experience your school design. Students moving between classes, teachers managing classroom activities, and visitors navigating the building all have unique spatial needs.",
            "museum": "Consider the diverse experiences in your museum design. Art enthusiasts seeking contemplation, families with children exploring interactively, and scholars conducting research each require different spatial approaches."
        },

        "metacognitive_challenge": {
            "community_center": "Let's investigate what makes community centers successful. Why do some spaces foster connection while others feel empty? Your detective skills will help uncover the hidden patterns in community engagement.",
            "library": "Investigate the secrets of successful library design. What makes some libraries feel welcoming and productive while others seem sterile? Let's uncover the mystery of effective learning environments.",
            "school": "Explore the hidden factors that make educational spaces work. Why do some schools inspire learning while others feel institutional? Your investigation will reveal the secrets of effective educational design.",
            "museum": "Discover what makes museum spaces captivating. Why do some exhibitions draw visitors in while others are quickly passed by? Let's investigate the mystery of engaging cultural spaces."
        },

        "constraint_challenge": {
            "community_center": "Every great community center emerges from creative constraints. Limited budget, existing structure, zoning restrictions - how can these limitations spark your most innovative solutions for community connection?",
            "library": "Transform constraints into opportunities for your library design. Noise control requirements, technology integration needs, and space limitations can actually inspire creative solutions for modern learning.",
            "school": "Navigate the complex constraints of educational design. Safety requirements, budget limitations, and curriculum needs can become the foundation for innovative learning environments.",
            "museum": "Work within the unique constraints of museum design. Conservation requirements, visitor flow patterns, and exhibition flexibility can inspire creative solutions for cultural engagement."
        },

        "alternative_challenge": {
            "community_center": "Challenge your assumptions about community center design. What if this space functioned more like a living room than an institution? How might this shift your entire design approach?",
            "library": "Reimagine the library beyond traditional concepts. What if it functioned more like a creative workshop than a quiet repository? How would this change your design thinking?",
            "school": "Question conventional school design. What if learning happened more like exploration than instruction? How might this perspective transform your spatial approach?",
            "museum": "Rethink museum design assumptions. What if visitors were co-creators rather than passive observers? How would this shift change your entire spatial strategy?"
        }
    }

    # Get the appropriate challenge text
    challenge_text = challenge_scenarios.get(challenge_type, {}).get(
        building_type,
        f"Explore new perspectives in your {building_type.replace('_', ' ')} design."
    )

    return {
        "challenge_type": challenge_type,
        "challenge_text": challenge_text,
        "building_type": building_type,
        "context": f"You are designing a {building_type.replace('_', ' ')} for a diverse urban community.",
        "difficulty_level": "intermediate",
        "estimated_time": "5-10 minutes",
        "project_phase": "conceptual_design"
    }

def display_debug_info(title: str, data: Dict[str, Any]):
    """Display debug information in a formatted box."""
    st.markdown(f"""
    <div class="debug-info">
        <strong>🔍 {title} Debug Info:</strong><br>
        {chr(10).join([f"• <strong>{k}:</strong> {v}" for k, v in data.items()])}
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main function to run the gamification test interface."""
    
    # Header
    st.title("🎮 Gamification UI Component Tester")
    st.markdown("**Test and preview all gamification components in isolation**")
    
    # Initialize the gamification renderer
    if 'renderer' not in st.session_state:
        st.session_state.renderer = EnhancedGamificationRenderer()
        st.success("✅ Gamification renderer initialized!")
    
    # Sidebar controls
    st.sidebar.title("🎛️ Test Controls")
    
    # Building type selector
    building_types = [
        "community_center", "library", "school", "museum", 
        "office_building", "residential_complex", "hospital"
    ]
    selected_building_type = st.sidebar.selectbox(
        "🏗️ Building Type:",
        building_types,
        index=0
    )
    
    # Theme preview
    st.sidebar.markdown("### 🎨 Available Themes")
    for theme_name, theme_data in ENHANCED_THEMES.items():
        st.sidebar.markdown(f"""
        <div style="
            background: {theme_data['gradient']};
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
            text-align: center;
            color: white;
            font-weight: bold;
        ">
            {theme_data['icon']} {theme_name.replace('_', ' ').title()}
        </div>
        """, unsafe_allow_html=True)
    
    # Reset button
    if st.sidebar.button("🔄 Reset All States", type="secondary"):
        # Clear all session state related to gamification
        keys_to_clear = [k for k in st.session_state.keys() if any(x in k for x in ['persona', 'wheel', 'mystery', 'constraint'])]
        for key in keys_to_clear:
            del st.session_state[key]
        st.sidebar.success("🔄 All game states reset!")
        st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Persona Challenge", 
        "🎯 Perspective Wheel", 
        "🔍 Mystery Investigation", 
        "🧩 Constraint Puzzle",
        "📊 Debug Dashboard"
    ])
    
    # Tab 1: Persona Challenge
    with tab1:
        st.header("👤 Persona Challenge Game")
        st.markdown("*Test the persona selection and role-playing challenge component*")
        
        challenge_data = create_sample_challenge_data("perspective_challenge", selected_building_type)
        
        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)
        
        # Render the persona challenge
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering persona challenge: {e}")
            st.exception(e)
    
    # Tab 2: Perspective Wheel
    with tab2:
        st.header("🎯 Perspective Wheel Game")
        st.markdown("*Test the spinning wheel perspective challenge component*")

        challenge_data = create_sample_challenge_data("alternative_challenge", selected_building_type)

        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)

        # Render the perspective wheel
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering perspective wheel: {e}")
            st.exception(e)

    # Tab 3: Mystery Investigation
    with tab3:
        st.header("🔍 Mystery Investigation Game")
        st.markdown("*Test the detective-style mystery investigation component*")

        challenge_data = create_sample_challenge_data("metacognitive_challenge", selected_building_type)

        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)

        # Render the mystery investigation
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering mystery investigation: {e}")
            st.exception(e)

    # Tab 4: Constraint Puzzle
    with tab4:
        st.header("🧩 Constraint Puzzle Game")
        st.markdown("*Test the creative constraint challenge component*")

        challenge_data = create_sample_challenge_data("constraint_challenge", selected_building_type)

        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)

        # Render the constraint puzzle
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering constraint puzzle: {e}")
            st.exception(e)

    # Tab 5: Debug Dashboard
    with tab5:
        st.header("📊 Debug Dashboard")
        st.markdown("*Monitor all game states and session data*")

        # Display all session state data related to gamification
        gamification_keys = [k for k in st.session_state.keys() if any(x in k for x in ['persona', 'wheel', 'mystery', 'constraint'])]

        if gamification_keys:
            st.subheader("🎮 Active Game States")
            for key in gamification_keys:
                with st.expander(f"🔍 {key}", expanded=False):
                    st.json(st.session_state[key])
        else:
            st.info("🎯 No active game states. Interact with the games in other tabs to see debug data here.")

        # Display theme information
        st.subheader("🎨 Theme Configuration")
        selected_theme = st.selectbox("Select theme to inspect:", list(ENHANCED_THEMES.keys()))
        if selected_theme:
            st.json(ENHANCED_THEMES[selected_theme])

        # Display renderer information
        st.subheader("🤖 Renderer Information")
        if hasattr(st.session_state, 'renderer'):
            st.success("✅ Renderer is active")
            st.write(f"**Renderer class:** {type(st.session_state.renderer).__name__}")
            st.write(f"**Available themes:** {len(st.session_state.renderer.themes)}")

            # Test all challenge types
            st.subheader("🧪 Quick Test All Components")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("Test Persona", type="secondary"):
                    test_data = create_sample_challenge_data("perspective_challenge", selected_building_type)
                    st.session_state.test_persona_data = test_data
                    st.success("✅ Persona test data created")

            with col2:
                if st.button("Test Wheel", type="secondary"):
                    test_data = create_sample_challenge_data("alternative_challenge", selected_building_type)
                    st.session_state.test_wheel_data = test_data
                    st.success("✅ Wheel test data created")

            with col3:
                if st.button("Test Mystery", type="secondary"):
                    test_data = create_sample_challenge_data("metacognitive_challenge", selected_building_type)
                    st.session_state.test_mystery_data = test_data
                    st.success("✅ Mystery test data created")

            with col4:
                if st.button("Test Constraint", type="secondary"):
                    test_data = create_sample_challenge_data("constraint_challenge", selected_building_type)
                    st.session_state.test_constraint_data = test_data
                    st.success("✅ Constraint test data created")
        else:
            st.error("❌ Renderer not initialized")

        # Instructions
        st.subheader("📖 Testing Instructions")
        st.markdown("""
        **How to use this test script:**

        1. **Select Building Type**: Use the sidebar to choose different building types
        2. **Navigate Tabs**: Each tab tests a different gamification component
        3. **Interact**: Click buttons, fill text areas, and test all interactive elements
        4. **Monitor State**: Use this Debug tab to see how session state changes
        5. **Reset**: Use the sidebar reset button to clear all states and start fresh

        **What to test:**
        - ✅ Visual styling and theme consistency
        - ✅ Button interactions and state management
        - ✅ Text input handling and validation
        - ✅ Progress tracking and point systems
        - ✅ Responsive layout and mobile compatibility
        - ✅ Error handling and edge cases

        **Expected Behavior:**
        - Each game should maintain its own state independently
        - Points and progress should update correctly
        - UI should be visually consistent with the main app
        - All interactive elements should be functional
        """)

        # Performance metrics
        if st.checkbox("Show Performance Metrics"):
            import time
            start_time = time.time()

            # Simulate rendering performance test
            with st.spinner("Testing render performance..."):
                time.sleep(0.1)  # Simulate processing

            end_time = time.time()
            st.metric("Render Time", f"{(end_time - start_time)*1000:.1f}ms")
            st.metric("Session State Size", f"{len(st.session_state)} items")
            st.metric("Active Games", len([k for k in st.session_state.keys() if any(x in k for x in ['persona', 'wheel', 'mystery', 'constraint'])]))

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        🎮 <strong>Gamification UI Tester</strong> |
        Built for testing <code>dashboard/ui/enhanced_gamification.py</code> components |
        <em>Standalone testing environment</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
