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
    "🔗 Integration Test",
    "🎯 Live Game Testing",
    "🎨 Rich Content Testing"
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

    # ADDED: Comprehensive conflict testing
    st.subheader("🔍 Conflict Analysis Test")

    if st.button("🧪 Run Gamification Conflict Analysis", type="primary"):
        with st.spinner("Running comprehensive conflict analysis..."):
            try:
                import subprocess
                result = subprocess.run(
                    ["python", "task1_gamification_conflict_analysis.py"],
                    capture_output=True,
                    text=True,
                    cwd="."
                )

                if result.returncode == 0:
                    st.success("✅ Conflict analysis completed successfully")
                    with st.expander("📊 Analysis Results", expanded=True):
                        st.code(result.stdout, language="text")
                else:
                    st.error("❌ Conflict analysis failed")
                    st.code(result.stderr, language="text")

            except Exception as e:
                st.error(f"❌ Failed to run conflict analysis: {e}")

elif selected_test_mode == "🎯 Live Game Testing":
    st.header("🎯 Live Game Testing with Rich Content")
    st.markdown("Test all gamification types with real user messages and see the rich, contextual content generation in action.")

    # Enhanced test scenarios with rich content validation
    test_scenarios = {
        "🎯 Perspective Wheel": {
            "message": "What if I place the workshops in the brighter central hall and move the market activities into the side wings? Would that create a more engaging flow for people moving through the center?",
            "expected_game": "alternative_challenge",
            "expected_ui": "_render_spinning_wheel_game",
            "building_type": "community center",
            "context": "warehouse conversion with workshop and market spaces"
        },
        "👤 Role-Play Game": {
            "message": "How would a young visitor feel inside this building since I have been only considered elder people?",
            "expected_game": "perspective_challenge",
            "expected_ui": "_render_enhanced_persona_game",
            "building_type": "community center",
            "context": "elder-focused design with intergenerational considerations"
        },
        "🔍 Detective Mystery": {
            "message": "Users seem to avoid the main entrance but I can't identify why - something feels off about the space",
            "expected_game": "metacognitive_challenge",
            "expected_ui": "_render_animated_mystery_game",
            "building_type": "community center",
            "context": "entrance design problem investigation"
        },
        "🧩 Constraint Puzzle": {
            "message": "I'm completely stuck on this design problem and need fresh ideas for my approach",
            "expected_game": "constraint_challenge",
            "expected_ui": "_render_interactive_constraint_game",
            "building_type": "community center",
            "context": "general design problem with creative constraints"
        },
        "🏗️ Transformation Game": {
            "message": "I'm converting this warehouse into a community center with spaces for cultural activities, flexible workshops, and a small market hall. The challenge I'm facing is how to transform the industrial scale into something that feels human and welcoming for daily use mostly for elder people.",
            "expected_game": "space_transformation",
            "expected_ui": "_render_transformation_game",
            "building_type": "community center",
            "context": "warehouse to community center conversion with elder focus"
        },
        "⏰ Time Travel": {
            "message": "How will this building evolve over time as the community's needs change in the future?",
            "expected_game": "time_travel_challenge",
            "expected_ui": "_render_time_travel_game",
            "building_type": "community center",
            "context": "temporal evolution and future adaptability"
        },
        "📚 Storytelling": {
            "message": "I would like to create a user journey through the central hub — almost like a story that guides people from arrival, into moments of pause, and then out toward workshops or market spaces. How do I design that narrative flow so it feels natural and not forced?",
            "expected_game": "spatial_storytelling",
            "expected_ui": "_render_storytelling_game",
            "building_type": "community center",
            "context": "narrative flow design with central hub and activity zones"
        }
    }

    selected_scenario = st.selectbox(
        "🎮 Select Test Scenario:",
        list(test_scenarios.keys()),
        help="Choose a scenario to test rich content generation"
    )

    scenario = test_scenarios[selected_scenario]

    # Enhanced scenario display
    st.markdown("### 📋 Scenario Details")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**User Message:**")
        st.markdown(f'*"{scenario["message"]}"*')

        st.markdown("**Context:**")
        st.info(f"🏢 {scenario['building_type']} | 🎯 {scenario['context']}")

    with col2:
        st.markdown("**Expected Game:**")
        st.code(scenario['expected_game'])

        st.markdown("**UI Method:**")
        st.code(scenario['expected_ui'])

    # Test button with rich content validation
    if st.button(f"🎮 Test {selected_scenario} with Rich Content", type="primary"):
        st.markdown("---")
        st.markdown(f"**🎮 {selected_scenario} Live Test with Rich Content Generation:**")

        # Create enhanced challenge data with user message context
        challenge_data = create_sample_challenge_data(scenario['expected_game'], scenario['building_type'])
        challenge_data['user_message'] = scenario['message']
        challenge_data['building_type'] = scenario['building_type']
        challenge_data['context'] = scenario['context']

        try:
            # Show content generation preview first
            with st.expander("🔍 Rich Content Generation Preview", expanded=True):
                st.markdown("**Testing rich content generation for this scenario...**")

                # Test content generation based on game type
                content_gen = st.session_state.renderer.content_generator

                if scenario['expected_game'] == 'space_transformation':
                    st.markdown("**🏗️ Transformation Content:**")
                    transformations = content_gen.generate_transformations_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    for name, desc in transformations.items():
                        content_type = "RICH" if len(desc) > 80 else "SHALLOW"
                        st.markdown(f"• **{name}**: {content_type} ({len(desc)} chars)")
                        st.markdown(f"  *{desc[:100]}...*")

                elif scenario['expected_game'] == 'perspective_challenge':
                    st.markdown("**👤 Persona Content:**")
                    personas = content_gen.generate_personas_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    for name, data in personas.items():
                        desc = data.get('description', '')
                        content_type = "RICH" if len(desc) > 50 else "SHALLOW"
                        st.markdown(f"• **{name}**: {content_type} ({len(desc)} chars)")
                        st.markdown(f"  *{desc[:80]}...*")

                elif scenario['expected_game'] == 'metacognitive_challenge':
                    st.markdown("**🔍 Mystery Content:**")
                    mystery = content_gen.generate_mystery_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    st.markdown(f"• **Mystery**: {mystery['mystery_description']}")
                    st.markdown("• **Clues:**")
                    for clue in mystery['clues']:
                        content_type = "RICH" if len(clue) > 50 else "SHALLOW"
                        st.markdown(f"  - {content_type}: *{clue[:60]}...*")

                elif scenario['expected_game'] == 'constraint_challenge':
                    st.markdown("**🧩 Constraint Content:**")
                    constraints = content_gen.generate_constraints_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    for name, data in constraints.items():
                        impact = data.get('impact', '')
                        content_type = "RICH" if len(impact) > 50 else "SHALLOW"
                        st.markdown(f"• **{name}**: {content_type} ({len(impact)} chars)")
                        st.markdown(f"  *{impact[:80]}...*")

                elif scenario['expected_game'] == 'spatial_storytelling':
                    st.markdown("**📚 Story Chapter Content:**")
                    chapters = content_gen.generate_story_chapters_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    for name, desc in chapters.items():
                        content_type = "RICH" if len(desc) > 80 else "SHALLOW"
                        st.markdown(f"• **{name}**: {content_type} ({len(desc)} chars)")
                        st.markdown(f"  *{desc[:100]}...*")

                elif scenario['expected_game'] == 'time_travel_challenge':
                    st.markdown("**⏰ Time Period Content:**")
                    periods = content_gen.generate_time_periods_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    for name, desc in periods.items():
                        content_type = "RICH" if len(desc) > 80 else "SHALLOW"
                        st.markdown(f"• **{name}**: {content_type} ({len(desc)} chars)")
                        st.markdown(f"  *{desc[:100]}...*")

                elif scenario['expected_game'] == 'alternative_challenge':
                    st.markdown("**🎯 Perspective Content:**")
                    perspectives = content_gen.generate_perspectives_from_context(
                        scenario['building_type'],
                        scenario['message']
                    )
                    for perspective in perspectives:
                        st.markdown(f"• **{perspective}'s View**")

            # Render the actual game
            st.markdown("### 🎮 Live Game Rendering:")
            st.session_state.renderer.render_enhanced_challenge(challenge_data)
            st.success(f"✅ {selected_scenario} rendered successfully with rich content!")

        except Exception as e:
            st.error(f"❌ Error rendering {selected_scenario}: {e}")
            st.exception(e)

    # Rich Content Validation Test
    st.subheader("🎨 Rich Content Validation Test")
    st.markdown("Test all games to verify they generate rich, contextual content instead of shallow descriptions.")

    # Warehouse conversion test message (rich context)
    warehouse_message = "I'm converting this warehouse into a community center with spaces for cultural activities, flexible workshops, and a small market hall. The challenge I'm facing is how to transform the industrial scale into something that feels human and welcoming for daily use mostly for elder people."

    if st.button("🎨 Test All Games with Rich Content", type="primary"):
        st.markdown("**Testing rich content generation across all games...**")

        content_gen = st.session_state.renderer.content_generator

        # Test each game type for rich content
        game_tests = [
            ("🏗️ Transformations", "space_transformation", "generate_transformations_from_context"),
            ("👤 Personas", "perspective_challenge", "generate_personas_from_context"),
            ("🔍 Mystery", "metacognitive_challenge", "generate_mystery_from_context"),
            ("🧩 Constraints", "constraint_challenge", "generate_constraints_from_context"),
            ("📚 Story Chapters", "spatial_storytelling", "generate_story_chapters_from_context"),
            ("⏰ Time Periods", "time_travel_challenge", "generate_time_periods_from_context"),
            ("🎯 Perspectives", "alternative_challenge", "generate_perspectives_from_context")
        ]

        for game_name, game_type, method_name in game_tests:
            with st.expander(f"{game_name} Rich Content Test", expanded=False):
                try:
                    method = getattr(content_gen, method_name)
                    result = method("community center", warehouse_message)

                    if isinstance(result, dict):
                        rich_count = 0
                        total_count = len(result)

                        for key, value in result.items():
                            if isinstance(value, dict):
                                # For personas/constraints with nested data
                                desc = value.get('description', '') or value.get('impact', '') or str(value)
                                char_count = len(desc)
                            else:
                                # For simple string values
                                char_count = len(str(value))

                            if char_count > 80:
                                rich_count += 1
                                content_type = "✅ RICH"
                            else:
                                content_type = "⚠️ SHALLOW"

                            st.markdown(f"**{key}**: {content_type} ({char_count} chars)")

                            # Show preview
                            if isinstance(value, dict):
                                preview = str(value.get('description', '') or value.get('impact', '') or str(value))[:100]
                            else:
                                preview = str(value)[:100]
                            st.markdown(f"*{preview}...*")

                        # Summary
                        richness_ratio = rich_count / total_count if total_count > 0 else 0
                        if richness_ratio >= 0.7:
                            st.success(f"✅ {game_name}: {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")
                        else:
                            st.warning(f"⚠️ {game_name}: Only {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")

                    elif isinstance(result, list):
                        st.success(f"✅ {game_name}: Generated {len(result)} items")
                        for item in result[:3]:  # Show first 3
                            st.markdown(f"• {item}")

                    else:
                        st.info(f"ℹ️ {game_name}: Generated content of type {type(result)}")

                except Exception as e:
                    st.error(f"❌ {game_name}: Error - {e}")

        st.success("🎉 Rich content validation completed!")

    # Test all game types (data creation only)
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

    if st.button("🚀 Test All Game Types (Data Creation)", type="secondary"):
        st.markdown("**Testing all game types for data creation...**")

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

elif selected_test_mode == "🎨 Rich Content Testing":
    st.header("🎨 Rich Content Testing Laboratory")
    st.markdown("Comprehensive testing of rich content generation across all games with different user scenarios and contexts.")

    # Test scenario selector
    test_scenarios = {
        "🏭 Warehouse to Community Center": {
            "building_type": "community center",
            "user_message": "I'm converting this warehouse into a community center with spaces for cultural activities, flexible workshops, and a small market hall. The challenge I'm facing is how to transform the industrial scale into something that feels human and welcoming for daily use mostly for elder people.",
            "context": "Industrial adaptive reuse with elder focus",
            "expected_themes": ["industrial heritage", "community", "accessibility", "cultural activities"]
        },
        "👴 Elder-Focused Design": {
            "building_type": "community center",
            "user_message": "How do I design spaces that are welcoming and accessible for elderly users in my community center? I want to create areas where they feel comfortable socializing and participating in activities.",
            "context": "Accessibility and intergenerational design",
            "expected_themes": ["accessibility", "comfort", "social interaction", "aging in place"]
        },
        "🌍 Climate-Responsive Design": {
            "building_type": "school",
            "user_message": "My school design needs to respond to the hot, dry climate while creating comfortable learning environments. How do I balance natural ventilation with acoustic privacy?",
            "context": "Environmental design challenges",
            "expected_themes": ["climate response", "natural ventilation", "thermal comfort", "learning environments"]
        },
        "🏙️ Urban Density Challenge": {
            "building_type": "residential complex",
            "user_message": "I'm designing a high-density residential complex in the city center. How do I create private outdoor spaces and community areas when land is so limited?",
            "context": "Urban density and community building",
            "expected_themes": ["density", "privacy", "community spaces", "urban context"]
        },
        "🎭 Cultural Heritage Integration": {
            "building_type": "museum",
            "user_message": "My museum design needs to showcase local cultural heritage while being accessible to international visitors. How do I balance authenticity with universal understanding?",
            "context": "Cultural sensitivity and accessibility",
            "expected_themes": ["cultural heritage", "authenticity", "accessibility", "storytelling"]
        }
    }

    selected_scenario = st.selectbox(
        "🎯 Select Test Scenario:",
        list(test_scenarios.keys()),
        help="Choose a scenario to test rich content generation"
    )

    scenario = test_scenarios[selected_scenario]

    # Display scenario details
    st.markdown("### 📋 Scenario Details")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**User Message:**")
        st.markdown(f'*"{scenario["user_message"]}"*')

        st.markdown("**Context:**")
        st.info(f"🏢 {scenario['building_type']} | 🎯 {scenario['context']}")

    with col2:
        st.markdown("**Expected Themes:**")
        for theme in scenario['expected_themes']:
            st.markdown(f"• {theme}")

    # Test all games with this scenario
    if st.button("🎨 Test All Games with This Scenario", type="primary"):
        st.markdown("---")
        st.markdown(f"**🎨 Rich Content Generation Test for: {selected_scenario}**")

        content_gen = st.session_state.renderer.content_generator

        # Test each game type
        game_tests = [
            ("🏗️ Transformation Game", "generate_transformations_from_context", "dict", 80),
            ("👤 Persona Game", "generate_personas_from_context", "dict_nested", 50),
            ("🔍 Mystery Game", "generate_mystery_from_context", "mystery", 50),
            ("🧩 Constraint Game", "generate_constraints_from_context", "dict_nested", 50),
            ("📚 Storytelling Game", "generate_story_chapters_from_context", "dict", 80),
            ("⏰ Time Travel Game", "generate_time_periods_from_context", "dict", 80),
            ("🎯 Perspective Game", "generate_perspectives_from_context", "list", 0)
        ]

        for game_name, method_name, result_type, min_chars in game_tests:
            with st.expander(f"{game_name} - Rich Content Analysis", expanded=True):
                try:
                    method = getattr(content_gen, method_name)
                    result = method(scenario['building_type'], scenario['user_message'])

                    if result_type == "dict":
                        # Simple dictionary with string values
                        rich_count = 0
                        total_count = len(result)

                        st.markdown("**Generated Content:**")
                        for key, value in result.items():
                            char_count = len(str(value))
                            is_rich = char_count >= min_chars

                            if is_rich:
                                rich_count += 1
                                status = "✅ RICH"
                                color = "green"
                            else:
                                status = "⚠️ SHALLOW"
                                color = "orange"

                            st.markdown(f"**{key}**: {status} ({char_count} chars)")
                            st.markdown(f"<div style='color: {color}; font-style: italic; margin-left: 20px;'>{str(value)[:120]}...</div>", unsafe_allow_html=True)

                        # Summary
                        richness_ratio = rich_count / total_count if total_count > 0 else 0
                        if richness_ratio >= 0.8:
                            st.success(f"🎉 EXCELLENT: {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")
                        elif richness_ratio >= 0.6:
                            st.warning(f"⚠️ GOOD: {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")
                        else:
                            st.error(f"❌ NEEDS WORK: Only {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")

                    elif result_type == "dict_nested":
                        # Dictionary with nested data (personas, constraints)
                        rich_count = 0
                        total_count = len(result)

                        st.markdown("**Generated Content:**")
                        for key, value in result.items():
                            if isinstance(value, dict):
                                desc = value.get('description', '') or value.get('impact', '') or str(value)
                            else:
                                desc = str(value)

                            char_count = len(desc)
                            is_rich = char_count >= min_chars

                            if is_rich:
                                rich_count += 1
                                status = "✅ RICH"
                                color = "green"
                            else:
                                status = "⚠️ SHALLOW"
                                color = "orange"

                            st.markdown(f"**{key}**: {status} ({char_count} chars)")
                            st.markdown(f"<div style='color: {color}; font-style: italic; margin-left: 20px;'>{desc[:120]}...</div>", unsafe_allow_html=True)

                        # Summary
                        richness_ratio = rich_count / total_count if total_count > 0 else 0
                        if richness_ratio >= 0.8:
                            st.success(f"🎉 EXCELLENT: {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")
                        elif richness_ratio >= 0.6:
                            st.warning(f"⚠️ GOOD: {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")
                        else:
                            st.error(f"❌ NEEDS WORK: Only {rich_count}/{total_count} items are rich ({richness_ratio:.1%})")

                    elif result_type == "mystery":
                        # Special handling for mystery data
                        st.markdown("**Generated Mystery:**")

                        mystery_desc = result.get('mystery_description', '')
                        st.markdown(f"**Mystery**: {mystery_desc}")

                        clues = result.get('clues', [])
                        st.markdown("**Clues:**")
                        rich_clues = 0
                        for clue in clues:
                            char_count = len(clue)
                            is_rich = char_count >= min_chars
                            if is_rich:
                                rich_clues += 1
                                status = "✅ RICH"
                                color = "green"
                            else:
                                status = "⚠️ SHALLOW"
                                color = "orange"

                            st.markdown(f"• {status} ({char_count} chars)")
                            st.markdown(f"<div style='color: {color}; font-style: italic; margin-left: 20px;'>{clue}</div>", unsafe_allow_html=True)

                        # Summary
                        total_clues = len(clues)
                        richness_ratio = rich_clues / total_clues if total_clues > 0 else 0
                        if richness_ratio >= 0.8:
                            st.success(f"🎉 EXCELLENT: {rich_clues}/{total_clues} clues are rich ({richness_ratio:.1%})")
                        elif richness_ratio >= 0.6:
                            st.warning(f"⚠️ GOOD: {rich_clues}/{total_clues} clues are rich ({richness_ratio:.1%})")
                        else:
                            st.error(f"❌ NEEDS WORK: Only {rich_clues}/{total_clues} clues are rich ({richness_ratio:.1%})")

                    elif result_type == "list":
                        # Simple list (perspectives)
                        st.markdown("**Generated Perspectives:**")
                        for item in result:
                            st.markdown(f"• {item}")
                        st.success(f"✅ Generated {len(result)} perspectives")

                except Exception as e:
                    st.error(f"❌ Error testing {game_name}: {e}")
                    st.exception(e)

    # Comparative analysis
    st.markdown("---")
    st.subheader("📊 Comparative Rich Content Analysis")

    if st.button("📊 Compare All Scenarios", type="secondary"):
        st.markdown("**Comparing rich content generation across all scenarios...**")

        content_gen = st.session_state.renderer.content_generator

        # Test transformation game across all scenarios (as example)
        comparison_results = {}

        for scenario_name, scenario_data in test_scenarios.items():
            try:
                transformations = content_gen.generate_transformations_from_context(
                    scenario_data['building_type'],
                    scenario_data['user_message']
                )

                rich_count = sum(1 for desc in transformations.values() if len(desc) >= 80)
                total_count = len(transformations)
                richness_ratio = rich_count / total_count if total_count > 0 else 0

                comparison_results[scenario_name] = {
                    'rich_count': rich_count,
                    'total_count': total_count,
                    'richness_ratio': richness_ratio,
                    'sample': list(transformations.values())[0] if transformations else "No content"
                }

            except Exception as e:
                comparison_results[scenario_name] = {
                    'error': str(e)
                }

        # Display comparison
        st.markdown("**🏗️ Transformation Game - Cross-Scenario Comparison:**")

        for scenario_name, results in comparison_results.items():
            if 'error' in results:
                st.error(f"❌ {scenario_name}: {results['error']}")
            else:
                ratio = results['richness_ratio']
                if ratio >= 0.8:
                    status = "🎉 EXCELLENT"
                    color = "green"
                elif ratio >= 0.6:
                    status = "⚠️ GOOD"
                    color = "orange"
                else:
                    status = "❌ NEEDS WORK"
                    color = "red"

                st.markdown(f"**{scenario_name}**: {status} ({results['rich_count']}/{results['total_count']} rich - {ratio:.1%})")
                st.markdown(f"<div style='color: {color}; font-style: italic; margin-left: 20px;'>Sample: {results['sample'][:100]}...</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎮 Enhanced Gamification Visualizer | Built for thesis-agents mentor system</p>
    <p><small>Use this tool to visualize, test, and enhance gamification components before deploying to mentor.py</small></p>
    <p><strong>🎯 Pro Tip:</strong> Use the trigger examples to test games in mentor.py conversations!</p>
</div>
""", unsafe_allow_html=True)
