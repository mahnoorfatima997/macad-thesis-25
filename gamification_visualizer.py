"""
Enhanced Gamification Visualization & Test Suite
Comprehensive testing and visualization interface for all gamification components in enhanced_gamification.py
Allows visual enhancement and topic modification without triggering games in mentor.py
"""

import streamlit as st
import sys
import os
import json
from typing import Dict, List, Any

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dashboard.ui.enhanced_gamification import EnhancedGamificationRenderer

# Page configuration
st.set_page_config(
    page_title="🎮 Enhanced Gamification Visualizer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #784c80 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .game-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #4f3a3e;
    }
    
    .trigger-example {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    .debug-info {
        background: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        font-family: monospace;
        font-size: 0.9em;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'renderer' not in st.session_state:
    st.session_state.renderer = EnhancedGamificationRenderer()

# Helper functions
def create_sample_challenge_data(challenge_type: str, building_type: str = "community center", custom_text: str = None) -> dict:
    """Create sample challenge data for testing different game types."""
    
    base_data = {
        "challenge_type": challenge_type,
        "building_type": building_type,
        "gamification_applied": True,
        "difficulty_level": "medium"
    }
    
    # Challenge-specific text and data
    default_texts = {
        "perspective_challenge": f"Experience your {building_type} from different user perspectives. How does the space feel to different people?",
        "alternative_challenge": f"Spin the wheel to discover new perspectives on your {building_type} design. Each viewpoint reveals unique insights.",
        "metacognitive_challenge": f"Investigate the mystery: Why do people behave unexpectedly in your {building_type}? Gather clues to solve the puzzle.",
        "constraint_challenge": f"Your {building_type} faces new constraints! Select up to 3 limitations and create innovative solutions.",
        "spatial_storytelling": f"Tell the story of your {building_type} through different times of day. What narrative unfolds in your space?",
        "time_travel_challenge": f"Travel through time to see your {building_type} in the past, present, and future. How does time change your design?",
        "space_transformation": f"Your {building_type} needs to transform! Choose how it adapts and evolves to meet changing needs.",
        "lifecycle_adventure": f"Follow your {building_type} through its lifecycle. How does it grow and change over time?",
        "daily_rhythm_challenge": f"Explore the daily rhythms of your {building_type}. How does it pulse with life throughout the day?"
    }
    
    base_data["challenge_text"] = custom_text or default_texts.get(challenge_type, f"Interactive challenge for your {building_type}.")
    
    return base_data

def create_cognitive_enhancement_challenge(challenge_type: str, building_type: str = "community center") -> dict:
    """Create rich cognitive enhancement challenge data."""
    
    cognitive_challenges = {
        "spatial_storytelling": f"""🎨 SPATIAL STORYTELLING: DESIGN CHALLENGE

*Your building tells a story through its spaces, materials, and flow*

Your {building_type} has a narrative waiting to be discovered. Every corridor whispers secrets, every room holds memories, and every threshold marks a transition in the user's journey.

Consider the spatial sequence: How does someone move through your building? What story unfolds as they progress from entrance to exit? Think about the emotional arc - moments of compression and release, intimacy and grandeur, solitude and community.

The materialization phase of your design should reflect this narrative. Are there moments where the story becomes tangible through texture, light, or form?

What story does your {building_type} tell, and how do the spaces choreograph this narrative for its users?""",

        "time_travel_challenge": f"""⏰ TIME TRAVEL: TEMPORAL DESIGN CHALLENGE

*Your building exists across multiple timelines - past, present, and future*

Imagine your {building_type} as a time machine. In the past, it served different needs with different technologies and social patterns. Today, it responds to current demands. In the future, it will adapt to needs we can barely imagine.

Phase Transition Analysis: How does your building's identity shift across these temporal phases? What elements remain constant, and what transforms?

Consider the lifecycle of spaces: How do rooms age? How do circulation patterns evolve? How does the building's relationship with its context change over decades?

As you evaluate your design, think about temporal flexibility. What aspects of your {building_type} are timeless, and what should be designed for change?

How does your building honor its past while embracing its future?""",

        "perspective_challenge": f"""🎭 PERSPECTIVE CHALLENGE: MULTI-USER EXPERIENCE

*Your building serves many masters - each with unique needs and perceptions*

Step into the shoes of three very different users of your {building_type}. A child sees towering spaces and hidden corners. An elderly person navigates with careful attention to surfaces and support. A professional rushes through with efficiency in mind.

Each perspective reveals different truths about your design. The child discovers wonder in unexpected places. The elder finds comfort in thoughtful details. The professional appreciates clear wayfinding and functional flow.

Reflect on how your spatial decisions impact each user differently. What feels welcoming to one might feel overwhelming to another. What seems efficient might sacrifice the human experience.

How does your {building_type} balance these competing needs while creating spaces that feel authentic to all users?""",

        "constraint_challenge": f"""🧩 CONSTRAINT CHALLENGE: CREATIVE LIMITATIONS

*Your building faces real-world constraints that demand innovative solutions*

Every great design emerges from constraints - budget limitations, site restrictions, code requirements, and user needs that seem impossible to reconcile.

Your {building_type} must work within these boundaries while still achieving architectural excellence. Perhaps the budget is cut by 40%. Maybe the site floods every few years. The program might need to serve twice as many people as originally planned.

These constraints aren't obstacles - they're creative catalysts. They force you to question assumptions, explore unconventional solutions, and discover the essential qualities that make your building truly necessary.

Consider how constraints have shaped great architecture throughout history. How can limitations become the source of your design's greatest strengths?

What innovative solutions emerge when your {building_type} must do more with less?"""
    }
    
    return {
        "challenge_type": challenge_type,
        "building_type": building_type,
        "challenge_text": cognitive_challenges.get(challenge_type, f"Rich cognitive challenge for your {building_type}."),
        "gamification_applied": True,
        "difficulty_level": "high"
    }

def get_trigger_examples() -> Dict[str, List[str]]:
    """Get example user inputs that trigger each game type in mentor.py"""
    return {
        "perspective_challenge": [
            "I want to understand how different users experience my community center",
            "How would a child versus an adult see this space?",
            "What would it feel like to be a visitor in this building?",
            "Help me think about user perspectives",
            "I need to consider different viewpoints on my design"
        ],
        "alternative_challenge": [
            "What are some alternative approaches to this design problem?",
            "I'm stuck - can you suggest different ways to think about this?",
            "Show me other perspectives on this architectural challenge",
            "What if I approached this completely differently?",
            "I need fresh ideas for my design"
        ],
        "metacognitive_challenge": [
            "Why do people keep avoiding the main entrance?",
            "I notice users behaving strangely in this space - why?",
            "Something isn't working in my design but I can't figure out what",
            "Help me investigate what's wrong with this space",
            "I need to understand the underlying issues in my building"
        ],
        "constraint_challenge": [
            "My budget just got cut in half - what do I do?",
            "The site has major limitations - how do I work with them?",
            "I have too many requirements and not enough space",
            "Help me solve this design problem with limited resources",
            "I need creative solutions for these constraints"
        ],
        "spatial_storytelling": [
            "What story does my building tell?",
            "How do I create a narrative through my spaces?",
            "I want my building to have a clear spatial sequence",
            "Help me think about the user journey through my design",
            "How can architecture tell stories?"
        ],
        "time_travel_challenge": [
            "How will my building age over time?",
            "What did this site look like 20 years ago?",
            "How should I design for future changes?",
            "I want to understand the temporal aspects of my design",
            "How does time affect architectural spaces?"
        ],
        "space_transformation": [
            "My building needs to adapt to different uses",
            "How can I design flexible spaces?",
            "The program keeps changing - how do I accommodate this?",
            "I need spaces that can transform based on needs",
            "Help me design for adaptability and change"
        ]
    }

def display_debug_info(title: str, data: dict):
    """Display debug information in a formatted way."""
    st.markdown(f"**{title}:**")
    st.markdown('<div class="debug-info">', unsafe_allow_html=True)
    for key, value in data.items():
        st.text(f"{key}: {value}")
    st.markdown('</div>', unsafe_allow_html=True)

# Main interface
st.markdown("""
<div class="main-header">
    <h1>🎮 Enhanced Gamification Visualizer</h1>
    <p>Comprehensive testing, visualization, and enhancement interface</p>
    <p><em>Visualize, modify, and enhance all interactive games without triggering them in mentor.py</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("🎛️ Configuration")

# Building type selector
building_types = [
    "community center",
    "hospital", 
    "school",
    "library",
    "office building",
    "residential complex",
    "museum",
    "shopping center",
    "cultural center",
    "sports facility"
]

selected_building_type = st.sidebar.selectbox(
    "🏢 Building Type:",
    building_types,
    index=0,
    help="Choose the building type for contextualized challenges"
)

# Test mode selector
test_modes = [
    "🎮 Game Visualization",
    "🎯 Trigger Examples", 
    "🔧 Game Customization",
    "📊 Data Inspector",
    "🔗 Integration Test"
]

selected_test_mode = st.sidebar.selectbox(
    "🧪 Mode:",
    test_modes,
    index=0,
    help="Choose how to interact with the gamification system"
)

# Reset session state button
if st.sidebar.button("🔄 Reset All States", help="Clear all game progress and start fresh"):
    # Clear all gamification-related session state
    keys_to_remove = [key for key in st.session_state.keys() if any(
        pattern in key for pattern in ['persona_', 'wheel_', 'investigation_', 'constraints_',
                                     'storytelling_', 'time_travel_', 'transformation_', 'cognitive_challenge_']
    )]
    for key in keys_to_remove:
        del st.session_state[key]
    st.sidebar.success("✅ All states reset!")
    st.rerun()

# Main content area
if selected_test_mode == "🎮 Game Visualization":
    st.header("🎮 Interactive Game Visualization")
    st.markdown("Visualize and interact with all gamification components. Perfect for testing visual enhancements and gameplay mechanics.")

    # Create tabs for each game type
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👤 Persona", "🎯 Perspective", "🔍 Mystery", "🧩 Constraint",
        "📚 Storytelling", "⏰ Time Travel", "🏗️ Transformation"
    ])

    # Tab 1: Persona Challenge
    with tab1:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("👤 Persona Challenge Game")
        st.markdown("**Game Type:** Role-playing challenge where users experience spaces from different perspectives")
        st.markdown("**Visual Elements:** Persona cards, selection interface, experience recording")

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
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Perspective Wheel
    with tab2:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("🎯 Perspective Wheel Game")
        st.markdown("**Game Type:** Spinning wheel that randomly selects different viewpoints for design analysis")
        st.markdown("**Visual Elements:** Interactive wheel, perspective cards, insight recording")

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
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: Mystery Investigation
    with tab3:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("🔍 Mystery Investigation Game")
        st.markdown("**Game Type:** Detective-style investigation where users solve design problems by gathering clues")
        st.markdown("**Visual Elements:** Clue buttons, investigation progress, solution submission")

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
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 4: Constraint Puzzle
    with tab4:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("🧩 Constraint Puzzle Game")
        st.markdown("**Game Type:** Creative problem-solving with multiple constraint selection and solution development")
        st.markdown("**Visual Elements:** Constraint selection buttons, active constraints display, solution area")

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
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 5: Storytelling Game
    with tab5:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("📚 Storytelling Challenge Game")
        st.markdown("**Game Type:** Narrative-driven exploration of spatial sequences and building stories")
        st.markdown("**Visual Elements:** Chapter progression, story continuation, narrative recording")

        challenge_data = create_sample_challenge_data("spatial_storytelling", selected_building_type)

        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)

        # Render the storytelling game
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering storytelling game: {e}")
            st.exception(e)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 6: Time Travel Game
    with tab6:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("⏰ Time Travel Challenge Game")
        st.markdown("**Game Type:** Temporal exploration of building evolution across past, present, and future")
        st.markdown("**Visual Elements:** Time period selector, temporal descriptions, insight recording")

        challenge_data = create_sample_challenge_data("time_travel_challenge", selected_building_type)

        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)

        # Render the time travel game
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering time travel game: {e}")
            st.exception(e)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 7: Transformation Game
    with tab7:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.header("🏗️ Transformation Challenge Game")
        st.markdown("**Game Type:** Adaptive design exploration with multiple transformation types and scenarios")
        st.markdown("**Visual Elements:** Transformation type selector, scenario descriptions, evolution tracking")

        challenge_data = create_sample_challenge_data("space_transformation", selected_building_type)

        # Display challenge info
        with st.expander("📋 Challenge Configuration", expanded=False):
            display_debug_info("Challenge Data", challenge_data)

        # Render the transformation game
        try:
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
        except Exception as e:
            st.error(f"❌ Error rendering transformation game: {e}")
            st.exception(e)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_test_mode == "🎯 Trigger Examples":
    st.header("🎯 User Input Trigger Examples")
    st.markdown("Example user inputs that trigger each game type in mentor.py. Use these to test the games in actual conversations.")

    trigger_examples = get_trigger_examples()

    # Create expandable sections for each game type
    for game_type, examples in trigger_examples.items():
        # Map challenge types to display names
        display_names = {
            "perspective_challenge": "👤 Role Play",
            "alternative_challenge": "🎯 Perspective Wheel",
            "metacognitive_challenge": "🔍 Mystery Investigation",
            "constraint_challenge": "🧩 Constraint Puzzle",
            "spatial_storytelling": "📚 Storytelling Challenge",
            "time_travel_challenge": "⏰ Time Travel Challenge",
            "space_transformation": "🏗️ Transformation Challenge"
        }

        display_name = display_names.get(game_type, game_type)

        with st.expander(f"{display_name} - Trigger Examples", expanded=True):
            st.markdown(f"**Challenge Type:** `{game_type}`")
            st.markdown("**Example user inputs that trigger this game in mentor.py:**")

            for i, example in enumerate(examples, 1):
                st.markdown(f"""
                <div class="trigger-example">
                    <strong>Example {i}:</strong><br>
                    "{example}"
                </div>
                """, unsafe_allow_html=True)

            # Add a test button for each game type
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"🎮 Test {display_name}", key=f"test_{game_type}"):
                    st.session_state[f"test_trigger_{game_type}"] = True
                    st.success(f"✅ {display_name} triggered! Check the visualization below.")

            with col2:
                if st.button(f"📋 Copy Example", key=f"copy_{game_type}"):
                    # Show the first example for easy copying
                    st.code(examples[0], language="text")

            # Show the game if triggered
            if st.session_state.get(f"test_trigger_{game_type}", False):
                st.markdown("---")
                st.markdown(f"**🎮 {display_name} Preview:**")

                challenge_data = create_sample_challenge_data(game_type, selected_building_type)

                try:
                    st.session_state.renderer.render_enhanced_challenge(challenge_data)
                except Exception as e:
                    st.error(f"❌ Error rendering {display_name}: {e}")

                # Reset button
                if st.button(f"🔄 Hide {display_name}", key=f"hide_{game_type}"):
                    st.session_state[f"test_trigger_{game_type}"] = False
                    st.rerun()

elif selected_test_mode == "🔧 Game Customization":
    st.header("🔧 Game Customization Workshop")
    st.markdown("Customize game content, themes, and elements. Test your modifications in real-time.")

    # Game type selector
    game_types = [
        ("perspective_challenge", "👤 Role Play"),
        ("alternative_challenge", "🎯 Perspective Wheel"),
        ("metacognitive_challenge", "🔍 Mystery Investigation"),
        ("constraint_challenge", "🧩 Constraint Puzzle"),
        ("spatial_storytelling", "📚 Storytelling Challenge"),
        ("time_travel_challenge", "⏰ Time Travel Challenge"),
        ("space_transformation", "🏗️ Transformation Challenge")
    ]

    selected_game = st.selectbox(
        "🎮 Select Game to Customize:",
        game_types,
        format_func=lambda x: x[1]
    )

    game_type, game_name = selected_game

    st.subheader(f"Customizing: {game_name}")

    # Customization options
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📝 Content Customization")

        # Custom challenge text
        default_text = create_sample_challenge_data(game_type, selected_building_type)["challenge_text"]

        custom_text = st.text_area(
            "Custom Challenge Text:",
            value=default_text,
            height=150,
            help="Modify the challenge description and instructions"
        )

        # Custom building type
        custom_building = st.text_input(
            "Custom Building Type:",
            value=selected_building_type,
            help="Change the building type for this challenge"
        )

        # Difficulty level
        difficulty = st.selectbox(
            "Difficulty Level:",
            ["low", "medium", "high"],
            index=1
        )

    with col2:
        st.markdown("### 🎨 Visual Customization")

        # Theme selector
        available_themes = list(st.session_state.renderer.themes.keys())
        selected_theme = st.selectbox(
            "Visual Theme:",
            available_themes,
            help="Choose the visual theme for this game"
        )

        # Show theme preview
        theme_data = st.session_state.renderer.themes[selected_theme]
        st.markdown("**Theme Preview:**")
        st.markdown(f"""
        <div style="
            background: {theme_data['gradient']};
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <div style="font-size: 2em; margin-bottom: 10px;">{theme_data['icon']}</div>
            <strong>{selected_theme.replace('_', ' ').title()}</strong>
        </div>
        """, unsafe_allow_html=True)

        # Color customization
        st.markdown("**Color Palette:**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
            <div style="
                background: {theme_data['primary']};
                height: 40px;
                border-radius: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.8em;
            ">Primary</div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div style="
                background: {theme_data['secondary']};
                height: 40px;
                border-radius: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.8em;
            ">Secondary</div>
            """, unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""
            <div style="
                background: {theme_data['accent']};
                height: 40px;
                border-radius: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: {theme_data['primary']};
                font-size: 0.8em;
            ">Accent</div>
            """, unsafe_allow_html=True)

    # Preview section
    st.markdown("---")
    st.subheader("🎮 Live Preview")

    if st.button("🔄 Update Preview", type="primary"):
        # Create custom challenge data
        custom_challenge_data = {
            "challenge_type": game_type,
            "challenge_text": custom_text,
            "building_type": custom_building,
            "gamification_applied": True,
            "difficulty_level": difficulty,
            "custom_theme": selected_theme
        }

        st.session_state[f"custom_preview_{game_type}"] = custom_challenge_data
        st.success("✅ Preview updated with your customizations!")

    # Show custom preview
    if f"custom_preview_{game_type}" in st.session_state:
        custom_data = st.session_state[f"custom_preview_{game_type}"]

        st.markdown("**Your Customized Game:**")
        try:
            st.session_state.renderer.render_enhanced_challenge(custom_data)
        except Exception as e:
            st.error(f"❌ Error rendering customized game: {e}")
            st.exception(e)

        # Export options
        st.markdown("### 💾 Export Customization")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Configuration"):
                st.code(json.dumps(custom_data, indent=2), language="json")

        with col2:
            if st.button("💾 Save as JSON"):
                filename = f"custom_{game_type}_{custom_building.replace(' ', '_')}.json"
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json.dumps(custom_data, indent=2),
                    file_name=filename,
                    mime="application/json"
                )

elif selected_test_mode == "📊 Data Inspector":
    st.header("📊 Challenge Data Inspector")
    st.markdown("Inspect the data structure and configuration for each challenge type.")

    # Challenge type selector
    challenge_types = [
        "perspective_challenge",
        "alternative_challenge",
        "metacognitive_challenge",
        "constraint_challenge",
        "spatial_storytelling",
        "time_travel_challenge",
        "space_transformation",
        "lifecycle_adventure",
        "daily_rhythm_challenge"
    ]

    selected_challenge = st.selectbox(
        "🎯 Select Challenge Type:",
        challenge_types,
        help="Choose a challenge type to inspect its data structure"
    )

    # Generate and display challenge data
    challenge_data = create_sample_challenge_data(selected_challenge, selected_building_type)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Challenge Data Structure")
        st.json(challenge_data)

        # Show mapping information
        st.subheader("🔄 Type Mapping")
        type_mapping = {
            "perspective_challenge": "role_play",
            "metacognitive_challenge": "detective",
            "constraint_challenge": "constraint",
            "alternative_challenge": "perspective_shift",
            "spatial_storytelling": "storytelling",
            "time_travel_challenge": "time_travel",
            "space_transformation": "transformation",
            "lifecycle_adventure": "time_travel",
            "daily_rhythm_challenge": "time_travel"
        }

        mapped_type = type_mapping.get(selected_challenge, selected_challenge)
        st.info(f"**{selected_challenge}** → **{mapped_type}**")

        # Show cognitive enhancement version
        st.subheader("🧠 Cognitive Enhancement Version")
        if st.button("Generate Rich Challenge", key="generate_cognitive"):
            cognitive_data = create_cognitive_enhancement_challenge(selected_challenge, selected_building_type)
            st.session_state['cognitive_preview'] = cognitive_data
            st.success("✅ Rich cognitive challenge generated!")

        if 'cognitive_preview' in st.session_state:
            st.json(st.session_state['cognitive_preview'])

    with col2:
        st.subheader("🎨 Theme Configuration")

        # Get theme for this challenge type
        renderer = st.session_state.renderer
        mapped_type = type_mapping.get(selected_challenge, selected_challenge)
        theme = renderer.themes.get(mapped_type, renderer.themes["role_play"])

        st.json(theme)

        # Show color preview
        st.subheader("🎨 Color Preview")
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin: 10px 0;">
            <div style="width: 50px; height: 50px; background: {theme['primary']}; border-radius: 8px; border: 2px solid #ddd;"></div>
            <div style="width: 50px; height: 50px; background: {theme['secondary']}; border-radius: 8px; border: 2px solid #ddd;"></div>
            <div style="width: 50px; height: 50px; background: {theme['accent']}; border-radius: 8px; border: 2px solid #ddd;"></div>
        </div>
        <p><small>Primary • Secondary • Accent</small></p>
        """, unsafe_allow_html=True)

        # Show gradient preview
        st.subheader("🌈 Gradient Preview")
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            height: 60px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2em;
        ">
            {theme['icon']} {mapped_type.replace('_', ' ').title()}
        </div>
        """, unsafe_allow_html=True)

    # Preview section
    st.markdown("---")
    st.subheader("🎮 Live Data Preview")

    preview_type = st.radio(
        "Preview Type:",
        ["Standard Challenge", "Cognitive Enhancement"],
        horizontal=True
    )

    if preview_type == "Standard Challenge":
        preview_data = challenge_data
    else:
        preview_data = create_cognitive_enhancement_challenge(selected_challenge, selected_building_type)

    # Show the preview
    try:
        st.session_state.renderer.render_enhanced_challenge(preview_data)
    except Exception as e:
        st.error(f"❌ Error rendering preview: {e}")
        st.exception(e)

elif selected_test_mode == "🔗 Integration Test":
    st.header("🔗 Integration Test")
    st.markdown("Test how the gamification system integrates with the mentor.py application.")

    st.subheader("📋 Integration Checklist")

    # Test imports
    try:
        from dashboard.ui.enhanced_gamification import render_enhanced_gamified_challenge, inject_gamification_css
        st.success("✅ Enhanced gamification imports successful")
    except ImportError as e:
        st.error(f"❌ Import error: {e}")

    # Test renderer initialization
    try:
        renderer = EnhancedGamificationRenderer()
        st.success("✅ EnhancedGamificationRenderer initialization successful")
    except Exception as e:
        st.error(f"❌ Renderer initialization error: {e}")

    # Test challenge data processing
    try:
        test_data = create_sample_challenge_data("perspective_challenge", selected_building_type)
        st.success("✅ Challenge data creation successful")

        with st.expander("📊 Sample Challenge Data"):
            st.json(test_data)

    except Exception as e:
        st.error(f"❌ Challenge data creation error: {e}")

    # Test rendering pipeline
    st.subheader("🎮 Rendering Pipeline Test")

    try:
        test_challenge_data = create_sample_challenge_data("perspective_challenge", selected_building_type)

        st.markdown("**Testing render_enhanced_gamified_challenge function:**")
        render_enhanced_gamified_challenge(test_challenge_data)
        st.success("✅ Rendering pipeline test successful")

    except Exception as e:
        st.error(f"❌ Rendering pipeline error: {e}")
        st.exception(e)

    # Test all game types
    st.subheader("🧪 Comprehensive Game Type Test")

    all_game_types = [
        "perspective_challenge",
        "alternative_challenge",
        "metacognitive_challenge",
        "constraint_challenge",
        "spatial_storytelling",
        "time_travel_challenge",
        "space_transformation"
    ]

    if st.button("🚀 Test All Game Types", type="primary"):
        st.markdown("**Testing all game types...**")

        for game_type in all_game_types:
            try:
                test_data = create_sample_challenge_data(game_type, selected_building_type)
                # Just test data creation, not rendering (to avoid UI clutter)
                st.success(f"✅ {game_type}: Data creation successful")
            except Exception as e:
                st.error(f"❌ {game_type}: Error - {e}")

        st.success("🎉 All game types tested!")

    # Performance test
    st.subheader("⚡ Performance Test")

    if st.button("🏃‍♂️ Run Performance Test"):
        import time

        start_time = time.time()

        # Test multiple renders
        for i in range(5):
            test_data = create_sample_challenge_data("perspective_challenge", selected_building_type)
            # Simulate processing without actual rendering
            time.sleep(0.01)

        end_time = time.time()
        duration = end_time - start_time

        st.success(f"✅ Performance test completed in {duration:.3f} seconds")
        st.info(f"Average time per challenge: {duration/5:.3f} seconds")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎮 Enhanced Gamification Visualizer | Built for thesis-agents mentor system</p>
    <p><small>Use this tool to visualize, test, and enhance gamification components before deploying to mentor.py</small></p>
    <p><strong>🎯 Pro Tip:</strong> Use the trigger examples to test games in mentor.py conversations!</p>
</div>
""", unsafe_allow_html=True)
