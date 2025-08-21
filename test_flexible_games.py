"""
Flexible Games Test Suite
Demonstrates how all games now adapt to user messages and project context
"""

import streamlit as st
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dashboard.ui.enhanced_gamification import EnhancedGamificationRenderer, inject_gamification_css

# Page configuration
st.set_page_config(
    page_title="🎯 Flexible Games Test",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Flexible Games Test Suite")
st.markdown("**All games now adapt dynamically to user messages and project context!**")

# Initialize renderer
if 'renderer' not in st.session_state:
    st.session_state.renderer = EnhancedGamificationRenderer()

# Inject CSS
inject_gamification_css()

def create_flexible_challenge_data(challenge_type: str, building_type: str, user_message: str) -> dict:
    """Create challenge data that will trigger flexible content generation."""
    return {
        "challenge_type": challenge_type,
        "challenge_text": user_message,
        "building_type": building_type,
        "gamification_applied": True,
        "difficulty_level": "medium"
    }

# Test Configuration
st.sidebar.header("🎯 Flexible Content Test")
building_type = st.sidebar.selectbox(
    "Building Type:",
    ["community center", "library", "school", "museum", "hospital"]
)

# Demonstration of Flexible Content
st.header("🎮 All Games Are Now Flexible!")

st.markdown("""
**✅ What's New:**
- **Role Play**: Generates personas based on user mentions (child, elderly, parent, etc.)
- **Perspective Wheel**: Creates contextual viewpoints based on building type and message
- **Mystery Investigation**: Analyzes problem keywords to generate relevant clues
- **Constraint Puzzle**: Detects constraint types (budget, site, time) from user message
- **Storytelling**: Creates story chapters based on temporal and thematic keywords
- **Time Travel**: Adapts time periods based on context (historical, future-focused, etc.)
- **Transformation**: Generates transformation types based on flexibility needs mentioned
""")

# Test Examples
st.header("🧪 Test Examples")

test_scenarios = [
    {
        "name": "👶 Child & Elderly Focus",
        "message": "How would a child versus an elderly person experience my community center?",
        "game": "perspective_challenge",
        "expected": "Generates Child, Elderly, Parent personas + contextual perspectives"
    },
    {
        "name": "💰 Budget Constraints",
        "message": "My budget just got cut in half and the site floods regularly",
        "game": "constraint_challenge", 
        "expected": "Generates Budget Cut, Site Issues, Flood Zone constraints"
    },
    {
        "name": "🚪 Entrance Mystery",
        "message": "People keep avoiding the main entrance - it's confusing",
        "game": "metacognitive_challenge",
        "expected": "Generates entrance-specific clues and navigation problems"
    },
    {
        "name": "📚 Library Story",
        "message": "What story does my library tell to different visitors throughout the day?",
        "game": "spatial_storytelling",
        "expected": "Generates library-specific story chapters with visitor focus"
    },
    {
        "name": "🏥 Hospital Adaptation",
        "message": "How can my hospital adapt to serve more patients in the future?",
        "game": "space_transformation",
        "expected": "Generates healthcare-specific transformation types"
    },
    {
        "name": "🏛️ Museum Heritage",
        "message": "How has this museum site changed throughout history?",
        "game": "time_travel_challenge",
        "expected": "Generates Historical, Present, Legacy time periods"
    }
]

selected_scenario = st.selectbox(
    "Select test scenario:",
    test_scenarios,
    format_func=lambda x: x["name"]
)

if st.button("🎮 Test Flexible Content Generation", type="primary"):
    scenario = selected_scenario
    
    st.markdown(f"**Testing:** {scenario['name']}")
    st.markdown(f"**User Message:** \"{scenario['message']}\"")
    st.markdown(f"**Expected:** {scenario['expected']}")
    
    # Create challenge data
    challenge_data = create_flexible_challenge_data(
        scenario["game"], 
        building_type, 
        scenario["message"]
    )
    
    st.markdown("---")
    st.markdown("**🎯 Generated Game:**")
    
    try:
        # Render the flexible game
        st.session_state.renderer.render_enhanced_challenge(challenge_data)
        st.success("✅ Flexible content generated successfully!")
        
        # Show what was generated behind the scenes
        with st.expander("🔍 Behind the Scenes - Generated Content"):
            content_gen = st.session_state.renderer.content_generator
            
            if scenario["game"] == "perspective_challenge":
                personas = content_gen.generate_personas_from_context(building_type, scenario["message"])
                st.markdown("**Generated Personas:**")
                for persona, data in personas.items():
                    st.text(f"• {persona}: {data['description']}")
                
                perspectives = content_gen.generate_perspectives_from_context(building_type, scenario["message"])
                st.markdown("**Generated Perspectives:**")
                for perspective in perspectives:
                    st.text(f"• {perspective}'s View")
            
            elif scenario["game"] == "constraint_challenge":
                constraints = content_gen.generate_constraints_from_context(building_type, scenario["message"])
                st.markdown("**Generated Constraints:**")
                for constraint, data in constraints.items():
                    st.text(f"• {constraint}: {data['impact']}")
            
            elif scenario["game"] == "metacognitive_challenge":
                mystery = content_gen.generate_mystery_from_context(building_type, scenario["message"])
                st.markdown("**Generated Mystery:**")
                st.text(f"Problem: {mystery['mystery_description']}")
                st.text(f"Clues: {', '.join(mystery['clues'])}")
                st.text(f"Red Herrings: {', '.join(mystery['red_herrings'])}")
            
            elif scenario["game"] == "spatial_storytelling":
                chapters = content_gen.generate_story_chapters_from_context(building_type, scenario["message"])
                st.markdown("**Generated Story Chapters:**")
                for chapter_name, chapter_desc in chapters.items():
                    st.text(f"• {chapter_name}: {chapter_desc}")
            
            elif scenario["game"] == "time_travel_challenge":
                periods = content_gen.generate_time_periods_from_context(building_type, scenario["message"])
                st.markdown("**Generated Time Periods:**")
                for period_name, period_desc in periods.items():
                    st.text(f"• {period_name}: {period_desc}")
            
            elif scenario["game"] == "space_transformation":
                transformations = content_gen.generate_transformations_from_context(building_type, scenario["message"])
                st.markdown("**Generated Transformations:**")
                for transform_name, transform_desc in transformations.items():
                    st.text(f"• {transform_name}: {transform_desc}")
        
    except Exception as e:
        st.error(f"❌ Error generating flexible content: {e}")
        st.exception(e)

# Custom Test
st.header("🎨 Custom Test")
st.markdown("**Create your own test with custom user message:**")

custom_message = st.text_area(
    "Enter your custom user message:",
    placeholder="e.g., 'My school needs to accommodate wheelchair users and has limited budget'",
    height=100
)

custom_game = st.selectbox(
    "Select game type:",
    [
        ("perspective_challenge", "👤 Role Play"),
        ("alternative_challenge", "🎯 Perspective Wheel"),
        ("metacognitive_challenge", "🔍 Mystery Investigation"),
        ("constraint_challenge", "🧩 Constraint Puzzle"),
        ("spatial_storytelling", "📚 Storytelling"),
        ("time_travel_challenge", "⏰ Time Travel"),
        ("space_transformation", "🏗️ Transformation")
    ],
    format_func=lambda x: x[1]
)

if custom_message and st.button("🚀 Test Custom Message"):
    challenge_data = create_flexible_challenge_data(
        custom_game[0],
        building_type,
        custom_message
    )
    
    st.markdown("**Your Custom Game:**")
    try:
        st.session_state.renderer.render_enhanced_challenge(challenge_data)
        st.success("✅ Custom flexible content generated!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Summary
st.header("📋 Flexibility Summary")

flexibility_features = [
    ("👤 Role Play", "✅ Generates personas from user keywords (child, elderly, parent, etc.)"),
    ("🎯 Perspective Wheel", "✅ Creates contextual viewpoints based on building type and message"),
    ("🔍 Mystery Investigation", "✅ Analyzes problem keywords to generate relevant clues"),
    ("🧩 Constraint Puzzle", "✅ Detects constraint types (budget, site, time) from message"),
    ("📚 Storytelling", "✅ Creates story chapters based on temporal and thematic keywords"),
    ("⏰ Time Travel", "✅ Adapts time periods based on context (historical, future, etc.)"),
    ("🏗️ Transformation", "✅ Generates transformation types based on flexibility needs")
]

for game, feature in flexibility_features:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{game}**")
    with col2:
        st.markdown(feature)

st.success("🎉 All 7 games are now fully flexible and context-aware!")

# Technical Details
with st.expander("🔧 Technical Implementation"):
    st.markdown("""
    **FlexibleContentGenerator Class:**
    - Analyzes user messages for keywords and context
    - Generates dynamic content based on building type and user intent
    - Maintains thesis color scheme and visual consistency
    - Uses minimal tokens by focusing on keyword detection rather than AI generation
    
    **Keyword Detection Examples:**
    - "child", "elderly" → Generates Child, Senior Citizen personas
    - "budget", "cost" → Generates Budget Cut, Value Engineering constraints
    - "avoiding", "confusing" → Generates navigation and entrance clues
    - "history", "heritage" → Generates Historical, Present, Legacy time periods
    - "flexible", "multi-use" → Generates Adaptive, Functional transformations
    
    **Benefits:**
    - ✅ No additional AI tokens required
    - ✅ Fast, deterministic content generation
    - ✅ Contextually relevant to user's actual problem
    - ✅ Maintains visual consistency and thesis colors
    - ✅ Scales to any building type or user scenario
    """)

st.markdown("---")
st.markdown("**🎯 Enhanced Gamification System - Now 100% Flexible and Context-Aware!**")
