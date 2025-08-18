"""
Enhanced Visual Gamification System
Creates engaging, interactive, visual game experiences with improved UI elements.
Maintains Streamlit compatibility while adding creative visual enhancements.
"""

import streamlit as st
import random
from typing import Dict, List, Any
import json
import time

# Enhanced visual themes with thesis colors
ENHANCED_THEMES = {
    "role_play": {
        "primary": "#4f3a3e",      # Dark burgundy
        "secondary": "#5c4f73",    # Deep purple
        "accent": "#e0ceb5",       # Light beige
        "gradient": "linear-gradient(135deg, #4f3a3e 0%, #5c4f73 50%, #e0ceb5 100%)",
        "icon": "◉",
        "animation": "bounce",
        "symbol": "▲"
    },
    "perspective_shift": {
        "primary": "#784c80",      # Rich violet
        "secondary": "#b87189",    # Dusty rose
        "accent": "#cda29a",       # Soft pink
        "gradient": "linear-gradient(135deg, #784c80 0%, #b87189 50%, #cda29a 100%)",
        "icon": "◈",
        "animation": "pulse",
        "symbol": "◆"
    },
    "detective": {
        "primary": "#cd766d",      # Coral red
        "secondary": "#d99c66",    # Soft orange
        "accent": "#dcc188",       # Warm sand
        "gradient": "linear-gradient(135deg, #cd766d 0%, #d99c66 50%, #dcc188 100%)",
        "icon": "◎",
        "animation": "shake",
        "symbol": "●"
    },
    "constraint": {
        "primary": "#5c4f73",      # Deep purple
        "secondary": "#784c80",    # Rich violet
        "accent": "#b87189",       # Dusty rose
        "gradient": "linear-gradient(135deg, #5c4f73 0%, #784c80 50%, #b87189 100%)",
        "icon": "◐",
        "animation": "rotate",
        "symbol": "■"
    }
}

class EnhancedGamificationRenderer:
    """Enhanced visual gamification with creative interactive elements."""
    
    def __init__(self):
        self.themes = ENHANCED_THEMES

    def _get_personas_for_building(self, building_type: str) -> Dict[str, Dict[str, Any]]:
        """Return personas for a given building type."""
        # Example personas for demonstration
        personas_data = {
            "community center": {
                "Parent": {
                    "description": "A parent seeking a safe, engaging space for their children.",
                    "mission": "Find activities and spaces that foster learning and play.",
                    "insights": ["Parents value safety and visibility.", "Flexible spaces are appreciated."]
                },
                "Teen": {
                    "description": "A teenager looking for a place to hang out and express themselves.",
                    "mission": "Discover creative zones and social areas.",
                    "insights": ["Teens want autonomy and creative outlets.", "Social spaces are important."]
                },
                "Senior": {
                    "description": "An older adult seeking community and accessibility.",
                    "mission": "Locate accessible paths and welcoming gathering spots.",
                    "insights": ["Accessibility is crucial.", "Quiet, comfortable areas are valued."]
                }
            },
            "hospital": {
                "Patient": {
                    "description": "A patient navigating the hospital for treatment.",
                    "mission": "Find clear directions and comfortable waiting areas.",
                    "insights": ["Wayfinding is essential.", "Comfort reduces stress."]
                },
                "Visitor": {
                    "description": "A visitor supporting a loved one.",
                    "mission": "Locate patient rooms and amenities easily.",
                    "insights": ["Clear signage helps visitors.", "Amenities improve experience."]
                },
                "Staff": {
                    "description": "A staff member working long shifts.",
                    "mission": "Access efficient workspaces and rest areas.",
                    "insights": ["Efficiency and rest spaces matter.", "Staff need quick access to resources."]
                }
            }
        }
        return personas_data.get(building_type, personas_data["community center"])
        
    def render_enhanced_challenge(self, challenge_data: Dict[str, Any]) -> None:
        """Render an enhanced visual challenge experience."""
        challenge_type = challenge_data.get("challenge_type", "role_play")
        challenge_text = challenge_data.get("challenge_text", "")
        building_type = challenge_data.get("building_type", "community center")
        
        # Map challenge types to enhanced versions
        type_mapping = {
            "perspective_challenge": "role_play",
            "metacognitive_challenge": "detective", 
            "constraint_challenge": "constraint",
            "alternative_challenge": "perspective_shift"
        }
        
        enhanced_type = type_mapping.get(challenge_type, challenge_type) or "role_play"
        theme = self.themes.get(enhanced_type, self.themes["role_play"])
        
        # Inject enhanced CSS
        self._inject_enhanced_css()
        
        # Render based on enhanced type
        if enhanced_type == "role_play":
            self._render_enhanced_persona_game(challenge_text, theme, building_type)
        elif enhanced_type == "perspective_shift":
            self._render_spinning_wheel_game(challenge_text, theme, building_type)
        elif enhanced_type == "detective":
            self._render_animated_mystery_game(challenge_text, theme, building_type)
        elif enhanced_type == "constraint":
            self._render_interactive_constraint_game(challenge_text, theme, building_type)
    
    def _inject_enhanced_css(self):
        """Inject compact CSS with thesis colors only."""
        st.markdown("""
        <style>
        /* Compact Animations */
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-8px); }
            60% { transform: translateY(-4px); }
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(120, 76, 128, 0.4);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 0 0 15px rgba(120, 76, 128, 0.1);
            }
            100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(120, 76, 128, 0);
            }
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0) rotate(0deg); }
            10% { transform: translateX(-3px) rotate(-1deg); }
            20% { transform: translateX(3px) rotate(1deg); }
            30% { transform: translateX(-3px) rotate(-1deg); }
            40% { transform: translateX(3px) rotate(1deg); }
            50% { transform: translateX(-2px) rotate(-0.5deg); }
            60% { transform: translateX(2px) rotate(0.5deg); }
            70% { transform: translateX(-2px) rotate(-0.5deg); }
            80% { transform: translateX(2px) rotate(0.5deg); }
            90% { transform: translateX(-1px) rotate(-0.5deg); }
        }

        @keyframes rotate {
            0% { transform: rotate(0deg) scale(1); }
            25% { transform: rotate(90deg) scale(1.1); }
            50% { transform: rotate(180deg) scale(1); }
            75% { transform: rotate(270deg) scale(1.1); }
            100% { transform: rotate(360deg) scale(1); }
        }

        @keyframes wheelSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(1800deg); }
        }

        @keyframes cardFlip {
            0% { transform: rotateY(0deg); }
            50% { transform: rotateY(90deg); }
            100% { transform: rotateY(0deg); }
        }

        @keyframes slideInScale {
            0% {
                opacity: 0;
                transform: translateY(30px) scale(0.8);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes glow {
            0% {
                box-shadow: 0 0 15px rgba(79, 58, 62, 0.3), 0 0 30px rgba(79, 58, 62, 0.2);
                transform: scale(1);
            }
            50% {
                box-shadow: 0 0 25px rgba(79, 58, 62, 0.6), 0 0 50px rgba(79, 58, 62, 0.4);
                transform: scale(1.02);
            }
            100% {
                box-shadow: 0 0 15px rgba(79, 58, 62, 0.3), 0 0 30px rgba(79, 58, 62, 0.2);
                transform: scale(1);
            }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(180deg); }
        }

        /* Enhanced Button Styles */
        .stButton > button {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 20px;
            white-space: normal !important;
            height: auto !important;
            min-height: 80px;
            padding: 20px 25px !important;
            text-align: center !important;
            line-height: 1.6 !important;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 3px solid transparent;
            position: relative;
            overflow: hidden;
            font-weight: 600 !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }

        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.6s;
        }

        .stButton > button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            border-color: rgba(79, 58, 62, 0.5);
            background: linear-gradient(135deg, rgba(79, 58, 62, 0.1), rgba(92, 79, 115, 0.1));
        }

        .stButton > button:hover::before {
            left: 100%;
        }

        .stButton > button:active {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        }

        /* Wheel Animation */
        .spinning-wheel {
            animation: wheelSpin 3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        /* Card Flip Animation */
        .card-flip {
            animation: cardFlip 0.6s ease-in-out;
        }

        /* Glowing Elements */
        .glow-effect {
            animation: glow 2s ease-in-out infinite;
        }

        /* Progressive Loading Bar */
        .progress-bar {
            width: 100%;
            height: 15px;
            background: rgba(224, 206, 181, 0.3);
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4f3a3e, #5c4f73, #784c80);
            border-radius: 10px;
            transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 10px rgba(79, 58, 62, 0.3);
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        /* Interactive Cards */
        .interactive-card {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .interactive-card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        }

        .interactive-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.6s;
        }

        .interactive-card:hover::before {
            left: 100%;
        }

        /* Floating Elements */
        .floating-element {
            animation: float 6s ease-in-out infinite;
        }

        /* Text Area Enhancements */
        .stTextArea > div > div > textarea {
            border-radius: 15px !important;
            border: 2px solid #e0ceb5 !important;
            transition: all 0.3s ease !important;
            font-size: 1.1em !important;
            line-height: 1.6 !important;
            padding: 20px !important;
        }

        .stTextArea > div > div > textarea:focus {
            border-color: #4f3a3e !important;
            box-shadow: 0 0 15px rgba(79, 58, 62, 0.2) !important;
        }
        </style>
        """, unsafe_allow_html=True)

    def _render_enhanced_persona_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact persona game."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Persona Challenge
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Get personas for building type
        personas = self._get_personas_for_building(building_type)

        # Initialize persona state
        persona_key = f"persona_{building_type}_{hash(challenge_text)}"
        if persona_key not in st.session_state:
            st.session_state[persona_key] = {
                'selected_persona': None,
                'persona_data': None,
                'response_given': False,
                'persona_points': 0
            }

        persona_state = st.session_state[persona_key]

        # Compact persona selection
        for i, (persona_name, persona_data) in enumerate(personas.items()):
            is_selected = persona_state['selected_persona'] == persona_name

            # Compact persona card with click interaction
            if st.button(
                f"{theme['symbol']} {persona_name}: {persona_data['description'][:60]}...",
                key=f"select_persona_{i}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                persona_state['selected_persona'] = persona_name
                persona_state['persona_data'] = persona_data
                persona_state['response_given'] = False
                st.rerun()

        # Show selected persona experience
        if persona_state['selected_persona'] and persona_state['persona_data']:
            persona_data = persona_state['persona_data']
            persona_name = persona_state['selected_persona']

            # Compact experience section
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} {persona_name}:</strong>
                <span style="color: #2c2328;">{persona_data['mission']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Compact response area
            user_response = st.text_area(
                "Your experience:",
                placeholder=f"As {persona_name}, I feel...",
                height=100,
                key=f"response_{persona_key}",
                help="Describe your thoughts, feelings, and observations from this persona's perspective"
            )

            if st.button(f"{theme['symbol']} Submit Experience", key=f"submit_{persona_key}", type="primary"):
                if user_response.strip():
                    persona_state['response_given'] = True
                    persona_state['persona_points'] += 30

        # Show insights after submission
        if persona_state.get('response_given', False):
            # Compact insights display
            insights = persona_data.get('insights', ["Great thinking!"])
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div style="
                    background: {theme['accent']};
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    border-left: 3px solid {theme['primary']};
                ">
                    <strong style="color: {theme['primary']};">{theme['symbol']} Insight {i+1}:</strong>
                    <span style="color: #2c2328; line-height: 1.5;">{insight}</span>
                </div>
                """, unsafe_allow_html=True)

            # Show only contextual progress (no success message)
            self._show_contextual_progress("Persona Challenge", persona_state['persona_points'], 30)

    def _render_spinning_wheel_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact perspective wheel game."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Perspective Wheel
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Initialize wheel state
        wheel_key = f"wheel_{building_type}_{hash(challenge_text)}"
        if wheel_key not in st.session_state:
            st.session_state[wheel_key] = {
                'spun_perspective': None,
                'response_given': False,
                'perspective_points': 0,
                'spins_count': 0,
                'is_spinning': False
            }

        wheel_state = st.session_state[wheel_key]

        # Perspectives with thesis colors and geometric icons
        perspectives = [
            {"name": "Child's View", "icon": "●", "color": theme['primary'], "challenge": "Everything looks huge! What feels safe versus intimidating?"},
            {"name": "Elder's View", "icon": "■", "color": theme['secondary'], "challenge": "Comfort and accessibility are key. What helps versus hinders movement?"},
            {"name": "Athlete's View", "icon": "▲", "color": theme['accent'], "challenge": "Movement and energy! What inspires versus restricts physical activity?"},
            {"name": "Artist's View", "icon": "◆", "color": theme['primary'], "challenge": "Beauty and inspiration! What sparks versus dulls creative thinking?"},
            {"name": "Professional's View", "icon": "◉", "color": theme['secondary'], "challenge": "Efficiency and image! What impresses versus disappoints clients?"},
            {"name": "Visitor's View", "icon": "◈", "color": theme['accent'], "challenge": "First impressions! What welcomes versus confuses newcomers?"}
        ]

        # Compact spin button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                f"{theme['icon']} SPIN WHEEL",
                key=f"spin_{wheel_key}",
                type="primary",
                use_container_width=True
            ):
                selected_perspective = random.choice(perspectives)
                wheel_state['spun_perspective'] = selected_perspective
                wheel_state['response_given'] = False
                wheel_state['spins_count'] += 1
                st.rerun()

        # Show spun perspective
        if wheel_state['spun_perspective']:
            perspective = wheel_state['spun_perspective']

            # Compact perspective display
            st.markdown(f"""
            <div style="
                background: {perspective['color']};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
            ">
                <div style="font-size: 1.5em; margin-bottom: 8px; color: white;">{perspective['icon']}</div>
                <h4 style="margin: 8px 0; color: white;">{perspective['name']}</h4>
                <p style="margin: 8px 0; color: white; font-size: 0.9em;">{perspective['challenge']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Compact response area
            response = st.text_area(
                "Your insight:",
                placeholder=f"From this perspective, I see...",
                height=100,
                key=f"perspective_response_{wheel_key}"
            )

            if st.button(f"{theme['symbol']} Submit Perspective", key=f"submit_perspective_{wheel_key}", type="primary"):
                if response.strip():
                    wheel_state['response_given'] = True
                    wheel_state['perspective_points'] += 20

        # Show progress after submission
        if wheel_state.get('response_given', False):
            # Show only contextual progress (no success message)
            self._show_contextual_progress("Perspective Challenge", wheel_state['perspective_points'], 20)



    def _render_animated_mystery_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact mystery investigation game with user input."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Mystery Investigation
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Mystery setup
        mysteries = {
            "community center": {
                "case": "People keep avoiding the main entrance",
                "clues": ["Heavy door mechanism", "Dim entrance lighting", "No clear sightlines inside", "Echo-prone acoustics"],
                "red_herrings": ["Wall paint color", "WiFi signal strength"],
                "solution": "The entrance doesn't feel welcoming or safe"
            },
            "hospital": {
                "case": "Patients keep getting lost in the same corridor",
                "clues": ["Inconsistent lighting levels", "No clear landmarks", "Varying ceiling heights", "Fast-paced foot traffic"],
                "red_herrings": ["Background music volume", "Temperature variations"],
                "solution": "Visual cues are inconsistent and confusing"
            }
        }

        mystery = mysteries.get(building_type, mysteries["community center"])

        # Compact case presentation
        st.markdown(f"""
        <div style="
            background: {theme['accent']};
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid {theme['primary']};
        ">
            <strong style="color: {theme['primary']};">{theme['symbol']} The Mystery:</strong>
            <span style="color: #2c2328;">{mystery['case']}</span>
        </div>
        """, unsafe_allow_html=True)

        # Initialize investigation state
        investigation_key = f"investigation_{building_type}_{hash(mystery['case'])}"
        if investigation_key not in st.session_state:
            st.session_state[investigation_key] = {
                'investigated_clues': [],
                'detective_points': 0,
                'mystery_solved': False
            }

        investigation_state = st.session_state[investigation_key]

        # Compact clue investigation
        all_clues = mystery['clues'] + mystery['red_herrings']

        # Display clues as compact buttons
        for i, clue in enumerate(all_clues):
            is_investigated = clue in investigation_state['investigated_clues']
            is_important = clue in mystery['clues']

            if is_investigated:
                if is_important:
                    button_type = "primary"
                    prefix = f"{theme['symbol']} ✓"
                else:
                    button_type = "secondary"
                    prefix = f"{theme['symbol']} ✗"
            else:
                button_type = "secondary"
                prefix = f"{theme['symbol']}"

            if st.button(f"{prefix} {clue}", key=f"clue_{i}_{investigation_key}", type=button_type):
                if not is_investigated:
                    investigation_state['investigated_clues'].append(clue)
                    if is_important:
                        investigation_state['detective_points'] += 10
                    st.rerun()

        # Add user input for hypothesis
        if len(investigation_state['investigated_clues']) >= 2:
            st.markdown("### Your Investigation")

            hypothesis = st.text_area(
                "What do you think is causing the problem?",
                placeholder="Based on the evidence, I believe the issue is...",
                height=100,
                key=f"hypothesis_{investigation_key}"
            )

            if st.button(f"{theme['symbol']} Submit Solution", key=f"solve_{investigation_key}", type="primary"):
                if hypothesis.strip():
                    investigation_state['mystery_solved'] = True
                    investigation_state['detective_points'] += 20

        # Show solution after mystery is solved
        if investigation_state.get('mystery_solved', False):
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} Solution:</strong>
                <span style="color: #2c2328;">{mystery['solution']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Show only contextual progress (no success message)
            self._show_contextual_progress("Mystery Investigation", investigation_state['detective_points'], 20)






    def _render_interactive_constraint_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render compact constraint puzzle game."""
        # Compact header
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                width: 50px;
                height: 50px;
                background: {theme['accent']};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-size: 1.5em;
                color: {theme['primary']};
            ">
                {theme['icon']}
            </div>
            <h3 style="color: white; margin: 0; font-weight: 400;">
                {theme['icon']} Constraint Puzzle
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Constraint definitions with thesis colors and geometric icons
        constraints = {
            "Budget Cut": {"impact": "40% less money", "color": theme['primary'], "challenge": "What gets prioritized?", "icon": theme['symbol']},
            "Time Crunch": {"impact": "Half the timeline", "color": theme['secondary'], "challenge": "What can be done quickly?", "icon": "■"},
            "Site Issues": {"impact": "Floods every 5 years", "color": theme['accent'], "challenge": "How to design for water?", "icon": "▲"},
            "Double Users": {"impact": "Twice as many people", "color": theme['primary'], "challenge": "How to fit everyone?", "icon": "◆"},
            "Material Limits": {"impact": "Only local materials", "color": theme['secondary'], "challenge": "What's available nearby?", "icon": "◉"},
            "Accessibility": {"impact": "Full universal design", "color": theme['accent'], "challenge": "How to include everyone?", "icon": "◈"}
        }

        # Initialize constraint selection
        constraint_key = f"constraints_{building_type}_{hash(challenge_text)}"
        if constraint_key not in st.session_state:
            st.session_state[constraint_key] = {
                'selected_constraints': [],
                'solution': '',
                'points': 0,
                'completed': False
            }

        constraint_state = st.session_state[constraint_key]

        # Compact constraint selection
        for constraint_name, constraint_data in constraints.items():
            is_selected = constraint_name in constraint_state['selected_constraints']

            if st.button(
                f"{constraint_data['icon']} {constraint_name}: {constraint_data['impact']}",
                key=f"constraint_{constraint_name}_{constraint_key}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                if is_selected:
                    constraint_state['selected_constraints'].remove(constraint_name)
                else:
                    if len(constraint_state['selected_constraints']) < 3:
                        constraint_state['selected_constraints'].append(constraint_name)
                st.rerun()

        # Show solution area when constraints are selected
        if constraint_state['selected_constraints']:
            # Compact challenge display
            st.markdown(f"""
            <div style="
                background: {theme['accent']};
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">{theme['symbol']} Active Constraints:</strong>
                <span style="color: #2c2328;">{', '.join(constraint_state['selected_constraints'])}</span>
            </div>
            """, unsafe_allow_html=True)

            # Compact solution area
            solution = st.text_area(
                "Your creative solution:",
                placeholder="With these constraints, I would...",
                height=120,
                key=f"solution_{constraint_key}"
            )

            if st.button(f"{theme['symbol']} Submit Solution", key=f"submit_{constraint_key}", type="primary"):
                if solution.strip():
                    constraint_state['completed'] = True
                    constraint_state['solution'] = solution
                    constraint_state['points'] += len(constraint_state['selected_constraints']) * 15

        # Show progress after completion
        if constraint_state.get('completed', False):
            # Show only contextual progress (no success message)
            self._show_contextual_progress("Constraint Challenge", constraint_state['points'], 15)