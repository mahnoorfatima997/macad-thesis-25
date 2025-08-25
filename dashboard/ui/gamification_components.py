"""
Enhanced Gamification UI Components
Creates engaging, interactive gamification elements for the architecture mentor system.
Integrates advanced features: progress tracking, achievements, interactive diagrams,
3D visualization, adaptive difficulty, and storytelling.
"""

import streamlit as st
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import advanced gamification systems
try:
    from .progress_tracking import progress_tracker
    from .achievement_system import achievement_system
    from .interactive_diagrams import interactive_diagrams
    from .spatial_3d import spatial_3d
    from .adaptive_difficulty import adaptive_difficulty
    from .storytelling_framework import storytelling_framework
except ImportError:
    # Fallback if advanced systems aren't available
    progress_tracker = None
    achievement_system = None
    interactive_diagrams = None
    spatial_3d = None
    adaptive_difficulty = None
    storytelling_framework = None

# Import thesis colors for consistent styling
try:
    from benchmarking.thesis_colors import THESIS_COLORS, UI_COLORS, METRIC_COLORS
except ImportError:
    # Fallback colors if import fails
    THESIS_COLORS = {
        'primary_dark': '#4f3a3e',
        'primary_purple': '#5c4f73',
        'primary_violet': '#784c80',
        'primary_rose': '#b87189',
        'primary_pink': '#cda29a',
        'neutral_warm': '#dcc188',
        'neutral_orange': '#d99c66',
        'accent_coral': '#cd766d',
        'accent_magenta': '#cf436f',
    }
    UI_COLORS = {
        'background': '#faf8f5',
        'text_primary': '#2c2328',
        'border': '#e0ceb5',
    }
    METRIC_COLORS = {
        'cognitive_enhancement': '#b87189',
    }

class GamificationDisplay:
    """Enhanced gamification display with visual elements and interactivity."""
    
    def __init__(self):
        self.challenge_types = {
            "role_play": {
                "icon": "🎭",
                "color": THESIS_COLORS['accent_coral'],
                "bg_color": UI_COLORS['background'],
                "border": THESIS_COLORS['accent_coral']
            },
            "perspective_shift": {
                "icon": "🎯",
                "color": THESIS_COLORS['primary_violet'],
                "bg_color": UI_COLORS['background'],
                "border": THESIS_COLORS['primary_violet']
            },
            "detective": {
                "icon": "🔍",
                "color": THESIS_COLORS['primary_purple'],
                "bg_color": UI_COLORS['background'],
                "border": THESIS_COLORS['primary_purple']
            },
            "transformation": {
                "icon": "🏗️",
                "color": THESIS_COLORS['neutral_warm'],
                "bg_color": UI_COLORS['background'],
                "border": THESIS_COLORS['neutral_warm']
            },
            "storytelling": {
                "icon": "🎨",
                "color": THESIS_COLORS['primary_rose'],
                "bg_color": UI_COLORS['background'],
                "border": THESIS_COLORS['primary_rose']
            },
            "time_travel": {
                "icon": "⏰",
                "color": THESIS_COLORS['primary_dark'],
                "bg_color": UI_COLORS['background'],
                "border": THESIS_COLORS['primary_dark']
            }
        }
    
    def render_gamified_challenge(self, challenge_data: Dict[str, Any]) -> None:
        """Render an enhanced gamified challenge with truly interactive elements."""

        challenge_text = challenge_data.get("challenge_text", "")
        # Use provided challenge_type if available, otherwise detect from text
        challenge_type = challenge_data.get("challenge_type", self._detect_challenge_type(challenge_text))

        # Map challenge types from generator to UI types
        challenge_type_mapping = {
            "perspective_challenge": "role_play",
            "metacognitive_challenge": "curiosity_amplification",
            "constraint_challenge": "constraint_challenge",
            "alternative_challenge": "perspective_shift"
        }
        challenge_type = challenge_type_mapping.get(challenge_type, challenge_type)

        # Get visual theme
        theme = self.challenge_types.get(challenge_type, self.challenge_types["role_play"])

        # Check if challenge text already has formatting (like "🎭 ROLE-PLAY CHALLENGE:")
        has_existing_formatting = any(header in challenge_text for header in [
            "🎭 ROLE-PLAY CHALLENGE:", "🎯 PERSPECTIVE SHIFT:", "🔍 USER DETECTIVE:",
            "🏗️ SPACE TRANSFORMATION:", "⏰ TIME TRAVEL CHALLENGE:", "🎨 SPATIAL STORYTELLING:",
            "⚡ DESIGN CHALLENGE:", "🔄 LIFECYCLE ADVENTURE:", "🌅 DAILY RHYTHM CHALLENGE:"
        ])

        if has_existing_formatting:
            # Challenge text already has nice formatting, just display it directly
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {theme['bg_color']} 0%, {theme['color']}15 50%, {theme['color']}25 100%);
                border: 3px solid {theme['border']};
                border-radius: 20px;
                padding: 30px;
                margin: 25px 0;
                box-shadow: 0 12px 40px rgba(0,0,0,0.15);
                font-size: 1.1em;
                line-height: 1.6;
            ">
                {challenge_text.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Extract challenge components and render with UI headers
            title, scenario, main_challenge, question = self._parse_challenge_text(challenge_text)

            # Render the enhanced challenge with interactive elements
            self._render_challenge_header(title, theme)
            self._render_scenario_box(scenario, theme)
            self._render_main_challenge(main_challenge, theme)

        # Add interactive game mechanics based on challenge type
        if has_existing_formatting:
            # For formatted challenges, extract the question from the text
            lines = challenge_text.split('\n')
            question_line = ""
            for line in lines:
                if '?' in line:
                    question_line = line.strip()
                    break
            if not question_line:
                question_line = "What are your thoughts on this challenge?"
        else:
            # Use parsed question from unformatted text
            question_line = question

        if challenge_type == "curiosity_amplification":
            self._render_curiosity_game(question_line, theme)
        elif challenge_type == "constraint_challenge":
            self._render_constraint_game(question_line, theme)
        elif challenge_type == "perspective_shift":
            self._render_perspective_game(question_line, theme)
        elif challenge_type == "role_play":
            self._render_roleplay_game(question_line, theme)
        else:
            self._render_interactive_question(question_line, theme)

        self._render_challenge_footer(challenge_type)
    
    def _detect_challenge_type(self, challenge_text: str) -> str:
        """Detect the type of challenge from the text (works with formatted and plain text)."""
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
    
    def _parse_challenge_text(self, challenge_text: str) -> tuple:
        """Parse challenge text into components."""
        lines = challenge_text.split('\n')

        title = "Challenge"  # Default title
        scenario = ""
        main_challenge = ""
        question = ""

        # Filter out routing metadata lines
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip routing metadata lines
            if ("— Intent:" in line or "INTENT:" in line or
                "Route:" in line or "ROUTE:" in line or
                "Agents:" in line or "AGENTS:" in line or
                "Type:" in line and ("balanced_guidance" in line or "knowledge_with_challenge" in line)):
                continue
            clean_lines.append(line)

        current_section = "title"

        for line in clean_lines:
            if line.startswith('*') and line.endswith('*'):
                current_section = "scenario"
                scenario += line[1:-1] + " "
            elif '?' in line and current_section != "title":
                current_section = "question"
                question += line + " "
            elif current_section == "title" and any(keyword in line.upper() for keyword in ["CHALLENGE", "SHIFT", "DETECTIVE", "TRANSFORMATION"]):
                title = line
                current_section = "main"
            elif current_section == "main":
                main_challenge += line + " "

        # If no proper structure found, use all clean content as main challenge
        if not main_challenge and not scenario and not question:
            main_challenge = ' '.join(clean_lines)

        return title.strip(), scenario.strip(), main_challenge.strip(), question.strip()

    def _get_challenge_title(self, title: str, theme: Dict) -> str:
        """Generate an appropriate challenge title based on theme."""
        if title and title != "Challenge":
            return f"🎯 {title.upper()}"

        # Generate title based on challenge type
        challenge_titles = {
            "role_play": "🎭 ROLE-PLAY CHALLENGE",
            "perspective_shift": "👁️ PERSPECTIVE SHIFT CHALLENGE",
            "detective": "🔍 DETECTIVE CHALLENGE",
            "transformation": "✨ TRANSFORMATION CHALLENGE",
            "storytelling": "📚 STORYTELLING CHALLENGE",
            "time_travel": "⏰ TIME TRAVEL CHALLENGE",
            "curiosity_amplification": "🔍 CURIOSITY CHALLENGE",
            "constraint_challenge": "⚡ CONSTRAINT CHALLENGE"
        }

        # Find the challenge type from theme
        for challenge_type, challenge_title in challenge_titles.items():
            if theme.get('name', '').lower().replace(' ', '_') == challenge_type:
                return challenge_title

        return "🎯 DESIGN CHALLENGE"

    def _render_challenge_header(self, title: str, theme: Dict) -> None:
        """Render an animated challenge header."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {theme['bg_color']} 0%, {theme['color']}15 50%, {theme['color']}25 100%);
            border: 3px solid {theme['border']};
            border-radius: 20px;
            padding: 30px;
            margin: 25px 0;
            text-align: center;
            box-shadow: 0 12px 40px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2);
            position: relative;
            overflow: hidden;
            animation: pulse 3s ease-in-out infinite;
        ">
            <!-- Animated background pattern -->
            <div style="
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, {theme['color']}08 1px, transparent 1px);
                background-size: 25px 25px;
                animation: float 25s infinite linear;
                pointer-events: none;
            "></div>

            <!-- Main content -->
            <div style="position: relative; z-index: 1;">
                <div style="
                    font-size: 4em;
                    margin-bottom: 15px;
                    text-shadow: 0 3px 6px rgba(0,0,0,0.2);
                    animation: bounce 2s infinite;
                ">{theme['icon']}</div>
                <h2 style="
                    color: {theme['color']};
                    margin: 0;
                    font-weight: bold;
                    font-size: 1.8em;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    letter-spacing: 1px;
                ">{self._get_challenge_title(title, theme)}</h2>
                <div style="
                    background: linear-gradient(90deg, transparent, {theme['color']}, transparent);
                    height: 4px;
                    width: 100px;
                    margin: 20px auto;
                    border-radius: 2px;
                    animation: glow 2s ease-in-out infinite alternate;
                "></div>
            </div>
        </div>

        <style>
        @keyframes float {{
            0% {{ transform: translate(0, 0) rotate(0deg); }}
            100% {{ transform: translate(-25px, -25px) rotate(360deg); }}
        }}
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-12px); }}
            60% {{ transform: translateY(-6px); }}
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); box-shadow: 0 12px 40px rgba(0,0,0,0.15); }}
            50% {{ transform: scale(1.02); box-shadow: 0 16px 50px rgba(0,0,0,0.2); }}
            100% {{ transform: scale(1); box-shadow: 0 12px 40px rgba(0,0,0,0.15); }}
        }}
        @keyframes glow {{
            from {{ box-shadow: 0 0 8px {theme['color']}40; }}
            to {{ box-shadow: 0 0 25px {theme['color']}80, 0 0 35px {theme['color']}40; }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def _render_scenario_box(self, scenario: str, theme: Dict) -> None:
        """Render the scenario in an engaging box."""
        if not scenario:
            return
            
        st.markdown(f"""
        <div style="
            background: {theme['bg_color']};
            border-left: 5px solid {theme['color']};
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 0 10px 10px 0;
            font-style: italic;
            font-size: 1.1em;
            color: {UI_COLORS['text_primary']};
            box-shadow: 0 4px 15px rgba(79, 58, 62, 0.1);
        ">
            <strong>🎬 Scenario:</strong><br>
            {scenario}
        </div>
        """, unsafe_allow_html=True)
    
    def _render_main_challenge(self, main_challenge: str, theme: Dict) -> None:
        """Render the main challenge text."""
        if not main_challenge:
            return
            
        st.markdown(f"""
        <div style="
            background: white;
            border: 2px dashed {theme['color']};
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            font-size: 1.05em;
            line-height: 1.6;
            color: {UI_COLORS['text_primary']};
        ">
            <strong>🎯 Challenge:</strong><br>
            {main_challenge}
        </div>
        """, unsafe_allow_html=True)
    
    def _render_interactive_question(self, question: str, theme: Dict) -> None:
        """Render an interactive question section."""
        if not question:
            return
            
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['color']}10, {theme['color']}20);
            border: 2px solid {theme['color']};
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        ">
            <div style="font-size: 1.5em; margin-bottom: 10px;">💭</div>
            <strong style="color: {theme['color']}; font-size: 1.2em;">Your Mission:</strong><br>
            <div style="margin-top: 10px; font-size: 1.1em; color: {UI_COLORS['text_primary']};">
                {question}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add interactive elements
        self._render_challenge_tools(theme)
    
    def _render_challenge_tools(self, theme: Dict) -> None:
        """Render interactive tools to help with the challenge."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {theme['color']}08, {theme['color']}15);
            border: 2px solid {theme['color']}40;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        ">
            <h3 style="
                color: {theme['color']};
                text-align: center;
                margin-bottom: 20px;
                font-weight: bold;
            ">🛠️ Challenge Tools</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        # Initialize session state for tool responses
        if 'tool_responses' not in st.session_state:
            st.session_state.tool_responses = {}

        with col1:
            hint_key = f"hint_{id(theme)}"
            if st.button("💡 Get a Hint", key=hint_key):
                # Get contextual hints based on building type and challenge
                building_type = st.session_state.get('building_type', 'building')
                hints = self._get_contextual_hints(building_type, theme)
                selected_hint = random.choice(hints)
                st.session_state.tool_responses[hint_key] = selected_hint
                st.rerun()

            # Display hint if available
            if hint_key in st.session_state.tool_responses:
                st.info(f"💡 **Hint:** {st.session_state.tool_responses[hint_key]}")

        with col2:
            perspective_key = f"perspective_{id(theme)}"
            if st.button("🎲 Random Perspective", key=perspective_key):
                building_type = st.session_state.get('building_type', 'building')
                perspectives = self._get_contextual_perspectives(building_type, theme)
                selected_perspective = random.choice(perspectives)
                st.session_state.tool_responses[perspective_key] = selected_perspective
                st.rerun()

            # Display perspective if available
            if perspective_key in st.session_state.tool_responses:
                st.success(f"🎭 **Try this perspective:** {st.session_state.tool_responses[perspective_key]}")

        with col3:
            inspiration_key = f"inspiration_{id(theme)}"
            if st.button("⭐ Inspiration", key=inspiration_key):
                building_type = st.session_state.get('building_type', 'building')
                inspirations = self._get_contextual_inspirations(building_type, theme)
                selected_inspiration = random.choice(inspirations)
                st.session_state.tool_responses[inspiration_key] = selected_inspiration
                st.rerun()

            # Display inspiration if available
            if inspiration_key in st.session_state.tool_responses:
                st.warning(f"✨ **Inspiration:** {st.session_state.tool_responses[inspiration_key]}")
    
    def _get_contextual_hints(self, building_type: str, theme: Dict) -> List[str]:
        """Get contextual hints based on building type and challenge theme."""
        base_hints = [
            "Think about the user's emotional journey",
            "Consider the sensory experience",
            "What would surprise or delight them?",
            "How does the space make them feel safe?",
            "What draws their attention first?"
        ]

        # Add building-specific hints
        if building_type == "community center":
            base_hints.extend([
                "How do different age groups use this space?",
                "What makes people feel welcome and included?",
                "How can the space adapt to different activities?"
            ])
        elif building_type == "hospital":
            base_hints.extend([
                "How does this space support healing?",
                "What reduces stress and anxiety?",
                "How do staff and patients interact here?"
            ])
        elif building_type == "school":
            base_hints.extend([
                "How does this encourage learning?",
                "What makes students feel safe and engaged?",
                "How do different learning styles work here?"
            ])

        return base_hints

    def _get_contextual_perspectives(self, building_type: str, theme: Dict) -> List[str]:
        """Get contextual perspectives based on building type."""
        base_perspectives = [
            "A child seeing this space for the first time",
            "An elderly person with mobility challenges",
            "Someone from a different cultural background",
            "Someone having a difficult day"
        ]

        # Add building-specific perspectives
        if building_type == "community center":
            base_perspectives.extend([
                "A parent with young children",
                "A teenager looking for belonging",
                "A community leader organizing events"
            ])
        elif building_type == "hospital":
            base_perspectives.extend([
                "A patient feeling anxious about treatment",
                "A family member waiting for news",
                "A healthcare worker during a busy shift"
            ])
        elif building_type == "school":
            base_perspectives.extend([
                "A shy student on their first day",
                "A teacher managing a large class",
                "A parent visiting for the first time"
            ])

        return base_perspectives

    def _get_contextual_inspirations(self, building_type: str, theme: Dict) -> List[str]:
        """Get contextual inspirations based on building type."""
        base_inspirations = [
            "Think of your favorite childhood place",
            "Imagine a space that feels like a warm hug",
            "Consider how light changes throughout the day",
            "Think about sounds, smells, and textures"
        ]

        # Add building-specific inspirations
        if building_type == "community center":
            base_inspirations.extend([
                "Village squares where people naturally gather",
                "Living rooms where families feel comfortable",
                "Markets where diverse communities meet"
            ])
        elif building_type == "hospital":
            base_inspirations.extend([
                "Gardens that promote healing",
                "Homes that feel safe and nurturing",
                "Spas that reduce stress and anxiety"
            ])
        elif building_type == "school":
            base_inspirations.extend([
                "Libraries that inspire curiosity",
                "Workshops where creativity flows",
                "Playgrounds where learning is fun"
            ])

        return base_inspirations

    def _render_curiosity_game(self, question: str, theme: Dict) -> None:
        """Render an interactive curiosity amplification game."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['color']}10, {theme['color']}20);
            border: 2px solid {theme['color']};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        ">
            <h3 style="color: {theme['color']}; text-align: center; margin-bottom: 20px;">
                🔍 Discovery Challenge
            </h3>
            <p style="font-size: 1.1em; text-align: center; margin-bottom: 20px;">
                {question}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Interactive discovery elements
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🎯 Explore This", key=f"explore_{id(theme)}"):
                discoveries = [
                    "What if this space could transform throughout the day?",
                    "How might natural elements change the atmosphere?",
                    "What sounds would make this space feel alive?",
                    "How could lighting create different moods?",
                    "What textures would invite people to touch and explore?"
                ]
                st.success(f"💡 **Discovery:** {random.choice(discoveries)}")

        with col2:
            if st.button("🌟 What If...", key=f"whatif_{id(theme)}"):
                scenarios = [
                    "What if this space was used by children vs. adults?",
                    "What if the weather was different?",
                    "What if people had different cultural backgrounds?",
                    "What if this was someone's first visit?",
                    "What if this space needed to serve multiple purposes?"
                ]
                st.info(f"🤔 **Scenario:** {random.choice(scenarios)}")

        with col3:
            if st.button("🚀 Push Further", key=f"push_{id(theme)}"):
                challenges = [
                    "How could this space surprise and delight users?",
                    "What would make this space memorable?",
                    "How could this space tell a story?",
                    "What would make people want to return?",
                    "How could this space create community?"
                ]
                st.warning(f"⚡ **Challenge:** {random.choice(challenges)}")

    def _render_constraint_game(self, question: str, theme: Dict) -> None:
        """Render an interactive constraint challenge game."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['color']}15, {theme['color']}25);
            border: 3px solid {theme['color']};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            position: relative;
        ">
            <h3 style="color: {theme['color']}; text-align: center; margin-bottom: 20px;">
                ⚡ Constraint Challenge
            </h3>
            <p style="font-size: 1.1em; text-align: center; margin-bottom: 20px;">
                {question}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Initialize constraint game state
        if 'constraint_game' not in st.session_state:
            st.session_state.constraint_game = {
                'active_constraints': [],
                'solutions': [],
                'score': 0
            }

        # Constraint selection
        st.markdown("**Choose your constraints:**")
        constraints = [
            "🏗️ Budget cut by 50%",
            "⏰ Timeline reduced by 30%",
            "🌧️ Must work in all weather",
            "♿ Full accessibility required",
            "🌱 Zero environmental impact",
            "👥 Must serve 3x more people"
        ]

        selected_constraints = st.multiselect(
            "Select constraints to apply:",
            constraints,
            key="constraint_selector"
        )

        if selected_constraints:
            if st.button("🎯 Apply Constraints", key="apply_constraints"):
                st.session_state.constraint_game['active_constraints'] = selected_constraints
                st.success(f"Applied {len(selected_constraints)} constraints! Now solve the challenge.")

        # Solution input
        if st.session_state.constraint_game['active_constraints']:
            solution = st.text_area(
                "Your creative solution:",
                placeholder="How would you adapt your design to work with these constraints?",
                key="constraint_solution"
            )

            if st.button("💡 Submit Solution", key="submit_solution") and solution:
                st.session_state.constraint_game['solutions'].append(solution)
                st.session_state.constraint_game['score'] += len(selected_constraints) * 10
                st.balloons()
                st.success(f"Great solution! +{len(selected_constraints) * 10} points")

    def _render_perspective_game(self, question: str, theme: Dict) -> None:
        """Render an interactive perspective shift game."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['color']}12, {theme['color']}22);
            border: 2px solid {theme['color']};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        ">
            <h3 style="color: {theme['color']}; text-align: center; margin-bottom: 20px;">
                🎭 Perspective Shift Game
            </h3>
            <p style="font-size: 1.1em; text-align: center; margin-bottom: 20px;">
                {question}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Perspective selection
        perspectives = {
            "👶 Child (Age 5)": "Low eye level, curious, playful, needs safety",
            "👵 Elder (Age 75)": "Mobility concerns, experience, wisdom, comfort needs",
            "🏃 Athlete": "Physical activity, performance, energy, movement",
            "🎨 Artist": "Creativity, inspiration, aesthetics, expression",
            "👔 Business Person": "Efficiency, professionalism, networking, productivity",
            "🌍 Tourist": "First impression, navigation, cultural interest, memorable experience"
        }

        selected_perspective = st.selectbox(
            "Choose a perspective to explore:",
            list(perspectives.keys()),
            key="perspective_selector"
        )

        if selected_perspective:
            st.info(f"**{selected_perspective}:** {perspectives[selected_perspective]}")

            # Interactive perspective questions
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🤔 What would they notice first?", key="notice_first"):
                    building_type = st.session_state.get('building_type', 'space')
                    responses = {
                        "👶 Child (Age 5)": f"Bright colors, fun shapes, things at their height level in the {building_type}",
                        "👵 Elder (Age 75)": f"Clear signage, comfortable seating, accessible pathways in the {building_type}",
                        "🏃 Athlete": f"Open spaces for movement, equipment storage, changing areas in the {building_type}",
                        "🎨 Artist": f"Natural light quality, inspiring views, creative potential of the {building_type}",
                        "👔 Business Person": f"Professional atmosphere, meeting spaces, technology access in the {building_type}",
                        "🌍 Tourist": f"Unique architectural features, photo opportunities, cultural elements of the {building_type}"
                    }
                    st.success(f"👀 **They'd notice:** {responses.get(selected_perspective, 'The overall atmosphere')}")

            with col2:
                if st.button("😊 What would make them happy?", key="make_happy"):
                    building_type = st.session_state.get('building_type', 'space')
                    responses = {
                        "👶 Child (Age 5)": f"Interactive elements, safe play areas, colorful details in the {building_type}",
                        "👵 Elder (Age 75)": f"Comfortable seating, good lighting, social gathering spots in the {building_type}",
                        "🏃 Athlete": f"Functional equipment, good ventilation, motivating environment in the {building_type}",
                        "🎨 Artist": f"Inspiring spaces, natural materials, creative atmosphere in the {building_type}",
                        "👔 Business Person": f"Efficient layout, quiet work areas, professional amenities in the {building_type}",
                        "🌍 Tourist": f"Authentic local character, memorable experiences, photo-worthy moments in the {building_type}"
                    }
                    st.success(f"😊 **They'd love:** {responses.get(selected_perspective, 'A welcoming atmosphere')}")

    def _render_roleplay_game(self, question: str, theme: Dict) -> None:
        """Render an interactive roleplay game."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['color']}10, {theme['color']}20);
            border: 2px solid {theme['color']};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        ">
            <h3 style="color: {theme['color']}; text-align: center; margin-bottom: 20px;">
                🎭 Role-Play Challenge
            </h3>
            <p style="font-size: 1.1em; text-align: center; margin-bottom: 20px;">
                {question}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Role selection and scenario
        roles = [
            "🏛️ City Planning Committee Member",
            "💰 Budget-Conscious Client",
            "🌱 Environmental Advocate",
            "♿ Accessibility Consultant",
            "👥 Community Representative",
            "🏗️ Construction Manager"
        ]

        selected_role = st.selectbox("Choose your role:", roles, key="role_selector")

        if selected_role:
            # Role-specific challenges
            if st.button("🎯 Start Role-Play", key="start_roleplay"):
                building_type = st.session_state.get('building_type', 'project')
                scenarios = {
                    "🏛️ City Planning Committee Member": f"Present your {building_type} design to the planning committee. Address zoning concerns and community impact.",
                    "💰 Budget-Conscious Client": f"Justify the costs of your {building_type} design. Show value and return on investment.",
                    "🌱 Environmental Advocate": f"Defend the environmental sustainability of your {building_type}. Address carbon footprint and resource use.",
                    "♿ Accessibility Consultant": f"Review your {building_type} for accessibility compliance. Identify potential barriers.",
                    "👥 Community Representative": f"Explain how your {building_type} serves diverse community needs and cultural values.",
                    "🏗️ Construction Manager": f"Assess the buildability of your {building_type}. Address construction challenges and timeline."
                }

                scenario = scenarios.get(selected_role, f"Evaluate your {building_type} from this perspective.")
                st.info(f"**Your Mission:** {scenario}")

                # Response input
                response = st.text_area(
                    "Your response as this role:",
                    placeholder="How would you respond to this challenge?",
                    key="roleplay_response"
                )

                if st.button("📝 Submit Response", key="submit_roleplay") and response:
                    st.success("Excellent role-play! You've considered multiple stakeholder perspectives.")
                    st.balloons()

    def _render_challenge_footer(self, challenge_type: str) -> None:
        """Render challenge footer with progress and encouragement."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown("🏆 **Challenge Level:** Architect")
        
        with col2:
            # Progress bar (simulated)
            progress = random.randint(60, 90)
            st.progress(progress / 100)
            st.markdown(f"<center><small>Design Thinking Progress: {progress}%</small></center>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("⚡ **XP Earned:** +25")

    def render_achievement_popup(self, achievement_type: str) -> None:
        """Render achievement popup when user completes challenges."""
        achievements = {
            "first_challenge": {
                "title": "🎯 Challenge Accepted!",
                "description": "Completed your first design challenge",
                "badge": "🏅",
                "color": THESIS_COLORS['neutral_orange']
            },
            "perspective_master": {
                "title": "👁️ Perspective Master",
                "description": "Explored multiple user perspectives",
                "badge": "🎭",
                "color": THESIS_COLORS['primary_violet']
            },
            "creative_thinker": {
                "title": "💡 Creative Thinker",
                "description": "Found innovative design solutions",
                "badge": "⚡",
                "color": THESIS_COLORS['accent_coral']
            },
            "empathy_expert": {
                "title": "❤️ Empathy Expert",
                "description": "Demonstrated deep user understanding",
                "badge": "🤝",
                "color": THESIS_COLORS['primary_rose']
            }
        }

        achievement = achievements.get(achievement_type, achievements["first_challenge"])

        st.balloons()  # Celebration animation

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {achievement['color']}20 0%, {achievement['color']}40 100%);
            border: 3px solid {achievement['color']};
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: bounce 1s ease-in-out;
        ">
            <div style="font-size: 4em; margin-bottom: 15px;">{achievement['badge']}</div>
            <h2 style="color: {achievement['color']}; margin: 10px 0; font-weight: bold;">
                {achievement['title']}
            </h2>
            <p style="font-size: 1.2em; color: {UI_COLORS['text_primary']}; margin: 0;">
                {achievement['description']}
            </p>
            <div style="margin-top: 15px; font-size: 1.1em; color: {achievement['color']};">
                <strong>+50 XP Earned! 🌟</strong>
            </div>
        </div>

        <style>
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        </style>
        """, unsafe_allow_html=True)

class GamificationTracker:
    """Track user progress and achievements in gamification."""

    def __init__(self):
        if 'gamification_stats' not in st.session_state:
            st.session_state.gamification_stats = {
                'challenges_completed': 0,
                'total_xp': 0,
                'achievements': [],
                'current_streak': 0,
                'best_streak': 0,
                'level': 1
            }

    def add_challenge_completion(self, challenge_type: str, xp_earned: int = 25) -> None:
        """Add a completed challenge to user stats."""
        stats = st.session_state.gamification_stats
        stats['challenges_completed'] += 1
        stats['total_xp'] += xp_earned
        stats['current_streak'] += 1

        if stats['current_streak'] > stats['best_streak']:
            stats['best_streak'] = stats['current_streak']

        # Level up logic
        new_level = (stats['total_xp'] // 100) + 1
        if new_level > stats['level']:
            stats['level'] = new_level
            self._show_level_up(new_level)

        # Check for achievements
        self._check_achievements(challenge_type)

    def _show_level_up(self, new_level: int) -> None:
        """Show level up animation."""
        st.balloons()
        st.success(f"🎉 **LEVEL UP!** You're now Level {new_level}! 🎉")

    def _check_achievements(self, challenge_type: str) -> None:
        """Check and award achievements."""
        stats = st.session_state.gamification_stats

        # First challenge achievement
        if stats['challenges_completed'] == 1 and 'first_challenge' not in stats['achievements']:
            stats['achievements'].append('first_challenge')
            display = GamificationDisplay()
            display.render_achievement_popup('first_challenge')

        # Perspective master (5 perspective challenges)
        if challenge_type == 'perspective_shift' and stats['challenges_completed'] >= 5:
            if 'perspective_master' not in stats['achievements']:
                stats['achievements'].append('perspective_master')
                display = GamificationDisplay()
                display.render_achievement_popup('perspective_master')

    def render_progress_sidebar(self) -> None:
        """Render gamification progress in sidebar - DISABLED."""
        # Progress display has been moved to contextual inline display
        # FIXED: Remove unreachable code that references undefined 'stats'
        pass

# Convenience functions for easy integration
def render_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Render a gamified challenge with enhanced visuals."""
    try:
        print(f"🎮 GAMIFICATION: Starting render with data: {list(challenge_data.keys())}")

        # Validate required data fields
        required_fields = ["challenge_text", "challenge_type"]
        missing_fields = [field for field in required_fields if field not in challenge_data]

        if missing_fields:
            print(f"🎮 GAMIFICATION WARNING: Missing fields {missing_fields}, using fallback")
            _render_simple_gamified_challenge(challenge_data)
            return

        display = GamificationDisplay()
        display.render_gamified_challenge(challenge_data)
        print(f"🎮 GAMIFICATION: Render completed successfully")

        # Track the challenge
        try:
            tracker = GamificationTracker()
            # Note: In real implementation, call add_challenge_completion when user responds
        except Exception as tracker_error:
            print(f"🎮 GAMIFICATION: Tracker error (non-critical): {tracker_error}")

    except Exception as e:
        print(f"🎮 GAMIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Fallback to simple gamification display
        _render_simple_gamified_challenge(challenge_data)

def _render_simple_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Simple fallback gamification display with robust error handling."""
    try:
        import streamlit as st

        # Safe data extraction with fallbacks
        challenge_text = challenge_data.get("challenge_text", "Let's explore your design challenge!")
        challenge_type = challenge_data.get("challenge_type", "challenge")
        difficulty = challenge_data.get("difficulty_level", "medium")

        # Ensure we have some content to display
        if not challenge_text or challenge_text.strip() == "":
            challenge_text = "Continue exploring your design ideas!"

    except Exception as e:
        print(f"🎮 SIMPLE GAMIFICATION ERROR: {e}")
        # Ultra-safe fallback
        import streamlit as st
        challenge_text = "Continue with your design exploration!"
        challenge_type = "challenge"
        difficulty = "medium"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #faf8f5 0%, #cd766d20 100%);
        border: 3px solid #cd766d;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <div style="text-align: center; margin-bottom: 15px;">
            <div style="font-size: 2em;">🎯</div>
            <div style="font-size: 1.2em; font-weight: bold; color: #cd766d;">
                GAMIFIED CHALLENGE - {difficulty.upper()}
            </div>
        </div>
        <div style="
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #cd766d;
            margin: 10px 0;
        ">
            <div style="font-weight: bold; color: #4f3a3e; margin-bottom: 10px;">
                🧠 {challenge_type.replace('_', ' ').title()}
            </div>
            <div style="line-height: 1.6; color: #2c2328;">
                {challenge_text}
            </div>
        </div>
        <div style="text-align: center; margin-top: 15px; color: #888; font-size: 0.9em;">
            💡 Take a moment to reflect on this challenge
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_advanced_gamification_dashboard():
    """Render the advanced gamification dashboard with all systems."""
    st.markdown("## 🎮 Advanced Gamification Dashboard")

    # Create tabs for different advanced features
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Progress", "🏅 Achievements", "🏗️ Interactive Diagrams",
        "🎯 3D Challenges", "⚡ Adaptive Learning", "📚 Story Mode"
    ])

    with tab1:
        if progress_tracker:
            progress_tracker.render_progress_dashboard()
        else:
            st.info("Progress tracking system not available.")

    with tab2:
        if achievement_system:
            achievement_system.render_badge_showcase()
        else:
            st.info("Achievement system not available.")

    with tab3:
        if interactive_diagrams:
            st.markdown("### 🏗️ Interactive Spatial Challenges")
            challenge_type = st.selectbox(
                "Choose challenge type:",
                ["space_organization", "circulation_flow", "zoning_analysis", "site_planning"]
            )
            building_type = st.session_state.get('building_type', 'community_center')
            interactive_diagrams.render_spatial_challenge(challenge_type, building_type)
        else:
            st.info("Interactive diagrams system not available.")

    with tab4:
        if spatial_3d:
            st.markdown("### 🎯 3D Spatial Reasoning")
            challenge_type = st.selectbox(
                "Choose 3D challenge:",
                ["massing_study", "interior_experience", "daylighting", "site_integration"]
            )
            building_type = st.session_state.get('building_type', 'community_center')
            spatial_3d.render_3d_challenge(challenge_type, building_type)
        else:
            st.info("3D visualization system not available.")

    with tab5:
        if adaptive_difficulty:
            adaptive_difficulty.render_difficulty_dashboard()
        else:
            st.info("Adaptive difficulty system not available.")

    with tab6:
        if storytelling_framework:
            # Check if user is in a story or needs to select one
            story_state = st.session_state.get('storytelling_state', {})
            if story_state.get('current_story'):
                storytelling_framework.render_story_chapter()
            else:
                storytelling_framework.render_story_selection()
        else:
            st.info("Storytelling framework not available.")

def integrate_advanced_gamification(challenge_data: Dict[str, Any]) -> None:
    """Integrate advanced gamification features into challenges."""
    challenge_text = challenge_data.get("challenge_text", "")

    # Map challenge to skill area
    skill_mapping = {
        "curiosity_amplification": "creative_thinking",
        "constraint_challenge": "technical_systems",
        "perspective_shift": "user_experience",
        "role_play": "cultural_context"
    }

    # Detect challenge type (simplified)
    challenge_type = "curiosity_amplification"  # Default
    for ctype in skill_mapping.keys():
        if ctype.replace('_', ' ') in challenge_text.lower():
            challenge_type = ctype
            break

    skill_area = skill_mapping.get(challenge_type, "spatial_reasoning")

    # Get adaptive challenge configuration if available
    if adaptive_difficulty:
        building_type = st.session_state.get('building_type', 'community_center')
        adaptive_config = adaptive_difficulty.get_adaptive_challenge(challenge_type, skill_area)

        # Show difficulty level
        difficulty_name = adaptive_config.get('difficulty_name', 'Standard')
        st.info(f"🎯 **Difficulty Level:** {difficulty_name}")

    # Check for new achievements
    if achievement_system and progress_tracker:
        progress_data = st.session_state.get('progress_data', {})
        new_badges = achievement_system.check_badge_requirements(progress_data)

        for badge_id in new_badges:
            achievement_system.award_badge(badge_id)

def complete_advanced_challenge(challenge_type: str, success: bool, time_spent: float = 300.0):
    """Complete a challenge and update all advanced systems."""
    skill_mapping = {
        "curiosity_amplification": "creative_thinking",
        "constraint_challenge": "technical_systems",
        "perspective_shift": "user_experience",
        "role_play": "cultural_context"
    }

    skill_area = skill_mapping.get(challenge_type, "spatial_reasoning")

    # Update progress tracking
    if progress_tracker:
        progress_tracker.complete_challenge(challenge_type, [skill_area])

    # Record performance for adaptive difficulty
    if adaptive_difficulty:
        engagement_indicators = {
            'engagement_score': 0.8 if success else 0.4,
            'completion_time': time_spent
        }
        adaptive_difficulty.record_challenge_performance(
            challenge_type, skill_area, success, time_spent, engagement_indicators
        )

    # Check for new achievements
    if achievement_system and progress_tracker:
        progress_data = st.session_state.get('progress_data', {})
        new_badges = achievement_system.check_badge_requirements(progress_data)

        for badge_id in new_badges:
            achievement_system.award_badge(badge_id)

    # Show completion feedback
    if success:
        st.success("🎉 Challenge completed successfully!")
        if time_spent < 180:  # Under 3 minutes
            st.info("⚡ Lightning fast! You're getting good at this.")
        elif time_spent > 600:  # Over 10 minutes
            st.info("🤔 Thoughtful approach! Deep thinking leads to better solutions.")
    else:
        st.info("📚 Learning opportunity! Every challenge teaches us something new.")

def render_gamification_sidebar() -> None:
    """Render gamification progress in sidebar - simplified for test mode."""
    tracker = GamificationTracker()
    tracker.render_progress_sidebar()

    # Advanced gamification button removed for test mode focus
