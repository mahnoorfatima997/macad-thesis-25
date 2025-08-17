"""
Enhanced Visual Gamification System
Creates engaging, interactive, visual game experiences instead of text-based challenges.
"""

import streamlit as st
import random
from typing import Dict, List, Any
import json

# Enhanced visual themes with gradients and animations
ENHANCED_THEMES = {
    "role_play": {
        "primary": "#cd766d",
        "secondary": "#e8a598",
        "accent": "#f4d4c7",
        "gradient": "linear-gradient(135deg, #cd766d 0%, #e8a598 50%, #f4d4c7 100%)",
        "icon": "◉",
        "animation": "bounce",
        "symbol": "▲"
    },
    "perspective_shift": {
        "primary": "#8B5CF6",
        "secondary": "#A78BFA",
        "accent": "#C4B5FD",
        "gradient": "linear-gradient(135deg, #8B5CF6 0%, #A78BFA 50%, #C4B5FD 100%)",
        "icon": "◈",
        "animation": "pulse",
        "symbol": "◆"
    },
    "detective": {
        "primary": "#7C3AED",
        "secondary": "#8B5CF6",
        "accent": "#A78BFA",
        "gradient": "linear-gradient(135deg, #7C3AED 0%, #8B5CF6 50%, #A78BFA 100%)",
        "icon": "◎",
        "animation": "shake",
        "symbol": "●"
    },
    "constraint": {
        "primary": "#6B7280",
        "secondary": "#9CA3AF",
        "accent": "#D1D5DB",
        "gradient": "linear-gradient(135deg, #6B7280 0%, #9CA3AF 50%, #D1D5DB 100%)",
        "icon": "◐",
        "animation": "rotate",
        "symbol": "■"
    }
}

class EnhancedGamificationRenderer:
    """Enhanced visual gamification with interactive elements."""
    
    def __init__(self):
        self.themes = ENHANCED_THEMES
        
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
        
        enhanced_type = type_mapping.get(challenge_type, challenge_type)
        theme = self.themes.get(enhanced_type, self.themes["role_play"])
        
        # Render based on enhanced type
        if enhanced_type == "role_play":
            self._render_persona_card_game(challenge_text, theme, building_type)
        elif enhanced_type == "perspective_shift":
            self._render_perspective_wheel_game(challenge_text, theme, building_type)
        elif enhanced_type == "detective":
            self._render_mystery_investigation_game(challenge_text, theme, building_type)
        elif enhanced_type == "constraint":
            self._render_constraint_puzzle_game(challenge_text, theme, building_type)
    
    def _render_persona_card_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render an interactive persona card selection game."""
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 15px 40px rgba(0,0,0,0.25);
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: {theme['animation']} 3s infinite;
            "></div>
            <div style="
                width: 80px;
                height: 80px;
                background: linear-gradient(45deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                font-size: 2.5em;
                color: {theme['primary']};
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                position: relative;
                z-index: 2;
            ">
                {theme['icon']}
            </div>
            <h2 style="
                color: white;
                margin: 0;
                text-shadow: 0 3px 6px rgba(0,0,0,0.4);
                font-size: 2.2em;
                font-weight: 300;
                letter-spacing: 2px;
                position: relative;
                z-index: 2;
            ">
                PERSONA EXPERIENCE
            </h2>
            <div style="
                width: 60px;
                height: 3px;
                background: rgba(255,255,255,0.8);
                margin: 15px auto 0;
                border-radius: 2px;
                position: relative;
                z-index: 2;
            "></div>
        </div>
        """, unsafe_allow_html=True)

        # Create persona cards
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

        # Display persona cards with minimal text
        st.markdown("**Choose Your Perspective:**")

        for i, (persona_name, persona_data) in enumerate(personas.items()):
            # Create persona card with better text handling
            is_selected = persona_state['selected_persona'] == persona_name

            card_style = f"""
            background: {'linear-gradient(45deg, ' + theme['primary'] + ', white)' if is_selected else theme['primary'] + '20'};
            border: {'3px solid ' + theme['primary'] if is_selected else '2px solid ' + theme['primary'] + '60'};
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            text-align: left;
            cursor: pointer;
            transition: all 0.3s ease;
            """

            # Create compact persona card
            with st.expander(f"**{persona_name}**", expanded=is_selected):
                st.markdown(f"*{persona_data['description'][:80]}...*")

                if st.button(
                    f"Experience as {persona_name}",
                    key=f"select_persona_{i}",
                    type="primary" if not is_selected else "secondary"
                ):
                    persona_state['selected_persona'] = persona_name
                    persona_state['persona_data'] = persona_data
                    persona_state['response_given'] = False
                    st.rerun()

        # Show selected persona experience
        if persona_state['selected_persona'] and persona_state['persona_data']:
            persona_data = persona_state['persona_data']
            persona_name = persona_state['selected_persona']

            st.markdown("---")
            st.markdown(f"**You are: {persona_name}**")

            # Interactive scenario with better styling
            st.markdown(f"""
            <div style="
                background: linear-gradient(45deg, {theme['secondary']}, {theme['accent']});
                padding: 20px;
                border-radius: 15px;
                margin: 15px 0;
                border-left: 5px solid {theme['primary']};
            ">
                <strong style="color: {theme['primary']};">Mission:</strong><br>
                <span style="color: #333;">{persona_data['mission']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Interactive response area
            user_response = st.text_area(
                "Your experience:",
                placeholder=f"As {persona_name}, I feel...",
                height=100,
                key=f"response_{persona_key}"
            )

            if st.button("Submit Experience", key=f"submit_{persona_key}"):
                if user_response.strip():
                    persona_state['response_given'] = True
                    persona_state['persona_points'] += 30

        # Show success and insights AFTER the button interaction
        if persona_state.get('response_given', False):
            # Cool success effect that stays visible
            st.markdown(f"""
            <div style="
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 25px;
                border-radius: 20px;
                text-align: center;
                margin: 25px 0;
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
                border: 2px solid rgba(255,255,255,0.3);
            ">
                <div style="font-size: 2.5em; margin-bottom: 10px;">{theme['symbol']}</div>
                <h2 style="margin: 10px 0; font-weight: 300;">EXCELLENT INSIGHT!</h2>
                <p style="font-size: 1.2em; margin: 0;">You're thinking like a real user! +30 Points</p>
            </div>
            """, unsafe_allow_html=True)

            # Show insights in a cleaner way
            st.markdown("**Key Design Insights:**")
            insights = persona_data.get('insights', ["Great thinking!"])
            for i, insight in enumerate(insights):
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, {theme['accent']}, rgba(255,255,255,0.9));
                    padding: 20px;
                    border-radius: 15px;
                    margin: 15px 0;
                    border-left: 5px solid {theme['primary']};
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 1.5em; color: {theme['primary']}; margin-bottom: 8px;">{theme['symbol']}</div>
                    <strong style="color: {theme['primary']};">Insight {i+1}:</strong><br>
                    <span style="color: #333; line-height: 1.6;">{insight}</span>
                </div>
                """, unsafe_allow_html=True)

            # Show completion
            self._show_challenge_completion("persona_completed", persona_state['persona_points'])
    
    def _render_perspective_wheel_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render an interactive perspective wheel game."""
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 25px;
            padding: 40px;
            margin: 20px 0;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: repeating-conic-gradient(from 0deg, transparent 0deg, rgba(255,255,255,0.05) 30deg, transparent 60deg);
                animation: {theme['animation']} 4s linear infinite;
            "></div>
            <div style="
                width: 100px;
                height: 100px;
                background: linear-gradient(45deg, rgba(255,255,255,0.95), rgba(255,255,255,0.8));
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 25px;
                font-size: 3em;
                color: {theme['primary']};
                box-shadow: 0 12px 35px rgba(0,0,0,0.25);
                position: relative;
                z-index: 2;
                border: 3px solid rgba(255,255,255,0.6);
            ">
                {theme['icon']}
            </div>
            <h2 style="
                color: white;
                margin: 0;
                text-shadow: 0 4px 8px rgba(0,0,0,0.5);
                font-size: 2.5em;
                font-weight: 200;
                letter-spacing: 3px;
                position: relative;
                z-index: 2;
            ">
                PERSPECTIVE WHEEL
            </h2>
            <div style="
                width: 80px;
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent);
                margin: 20px auto 0;
                position: relative;
                z-index: 2;
            "></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Spin for a new perspective:**")

        # Create perspective wheel
        perspectives = [
            {"name": "Child's View", "icon": "◉", "color": "#FFB6C1", "challenge": "Everything looks huge! What feels safe versus intimidating?"},
            {"name": "Elder's View", "icon": "◈", "color": "#DDA0DD", "challenge": "Comfort and accessibility are key. What helps versus hinders movement?"},
            {"name": "Athlete's View", "icon": "◆", "color": "#98FB98", "challenge": "Movement and energy! What inspires versus restricts physical activity?"},
            {"name": "Artist's View", "icon": "◎", "color": "#F0E68C", "challenge": "Beauty and inspiration! What sparks versus dulls creative thinking?"},
            {"name": "Professional's View", "icon": "◐", "color": "#87CEEB", "challenge": "Efficiency and image! What impresses versus disappoints clients?"},
            {"name": "Visitor's View", "icon": "●", "color": "#FFA07A", "challenge": "First impressions! What welcomes versus confuses newcomers?"}
        ]

        # Initialize wheel state
        wheel_key = f"wheel_{building_type}_{hash(challenge_text)}"
        if wheel_key not in st.session_state:
            st.session_state[wheel_key] = {
                'spun_perspective': None,
                'response_given': False,
                'perspective_points': 0,
                'spins_count': 0
            }

        wheel_state = st.session_state[wheel_key]

        # Spin button with better styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "SPIN THE WHEEL!",
                key=f"spin_{wheel_key}",
                type="primary",
                help="Click to get a random perspective challenge"
            ):
                selected_perspective = random.choice(perspectives)
                wheel_state['spun_perspective'] = selected_perspective
                wheel_state['response_given'] = False
                wheel_state['spins_count'] += 1

                # Cool spinning effect instead of balloons
                st.markdown("""
                <div style="
                    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                    color: white;
                    padding: 15px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 15px 0;
                    animation: pulse 1s ease-in-out;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                ">
                    <h4>Wheel Spinning...</h4>
                    <p>New perspective incoming!</p>
                </div>
                """, unsafe_allow_html=True)

                st.rerun()

        # Show spun perspective
        if wheel_state['spun_perspective']:
            perspective = wheel_state['spun_perspective']

            st.markdown("---")
            st.markdown(f"""
            <div style="
                background: linear-gradient(45deg, {perspective['color']}, white);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                border: 3px solid {perspective['color']};
            ">
                <div style="font-size: 2em; margin-bottom: 10px;">{perspective['icon']}</div>
                <h3 style="margin: 10px 0; color: #333;">{perspective['name']}</h3>
                <p style="margin: 15px 0; color: #555; font-size: 1.1em; line-height: 1.5;">{perspective['challenge']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Interactive challenge response
            response = st.text_area(
                "Your insight:",
                placeholder=f"From this perspective, I see...",
                height=100,
                key=f"perspective_response_{wheel_key}"
            )

            if st.button("Submit Perspective", key=f"submit_perspective_{wheel_key}"):
                if response.strip():
                    wheel_state['response_given'] = True
                    wheel_state['perspective_points'] += 20

        # Show success and metrics AFTER the button interaction
        if wheel_state.get('response_given', False):
            # Cool success effect that stays visible
            st.markdown(f"""
            <div style="
                background: linear-gradient(45deg, #8B5CF6, #A78BFA);
                color: white;
                padding: 25px;
                border-radius: 20px;
                text-align: center;
                margin: 25px 0;
                box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
                border: 2px solid rgba(255,255,255,0.3);
            ">
                <div style="font-size: 2.5em; margin-bottom: 10px;">{theme['symbol']}</div>
                <h2 style="margin: 10px 0; font-weight: 300;">PERSPECTIVE EXPANDED!</h2>
                <p style="font-size: 1.2em; margin: 0;">You're seeing with new eyes! +20 Points</p>
            </div>
            """, unsafe_allow_html=True)

            # Show metrics in a cool way
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, {theme['primary']}, {theme['secondary']});
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 10px 0;
                ">
                    <h3 style="margin: 0; font-size: 2em;">{wheel_state['perspective_points']}</h3>
                    <p style="margin: 5px 0;">Perspective Points</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, {theme['secondary']}, {theme['accent']});
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 10px 0;
                ">
                    <h3 style="margin: 0; font-size: 2em;">{wheel_state['spins_count']}</h3>
                    <p style="margin: 5px 0;">Total Spins</p>
                </div>
                """, unsafe_allow_html=True)

            # Show completion
            self._show_challenge_completion("perspective_shifted", wheel_state['perspective_points'])
    
    def _render_mystery_investigation_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render an interactive mystery investigation game."""
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 20px;
            padding: 35px;
            margin: 20px 0;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.03) 50%, transparent 70%);
                animation: {theme['animation']} 3s infinite;
            "></div>
            <div style="
                width: 90px;
                height: 90px;
                background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                font-size: 3em;
                color: {theme['primary']};
                box-shadow: 0 10px 30px rgba(0,0,0,0.25);
                position: relative;
                z-index: 2;
                border: 2px solid rgba(255,255,255,0.5);
            ">
                {theme['icon']}
            </div>
            <h2 style="
                color: white;
                margin: 0;
                text-shadow: 0 3px 6px rgba(0,0,0,0.4);
                font-size: 2.3em;
                font-weight: 300;
                letter-spacing: 2px;
                position: relative;
                z-index: 2;
            ">
                MYSTERY INVESTIGATION
            </h2>
            <div style="
                width: 100px;
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
                margin: 18px auto 0;
                position: relative;
                z-index: 2;
            "></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### The Case of the Confusing Space")

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

        st.markdown(f"**The Mystery:** {mystery['case']}")

        # Initialize investigation state with unique key
        investigation_key = f"investigation_{building_type}_{hash(mystery['case'])}"
        if investigation_key not in st.session_state:
            st.session_state[investigation_key] = {
                'investigated_clues': [],
                'detective_points': 0,
                'mystery_solved': False
            }

        investigation_state = st.session_state[investigation_key]

        # Clue investigation
        st.markdown("### Investigate the Evidence")
        st.markdown("*Click on evidence to examine it:*")

        # Display clues as interactive buttons with better styling
        all_clues = mystery['clues'] + mystery['red_herrings']

        # Create clue buttons with proper text handling
        for i, clue in enumerate(all_clues):
            # Create unique key for each clue
            clue_key = f"clue_{investigation_key}_{i}"

            # Check if already investigated
            is_investigated = clue in investigation_state['investigated_clues']

            # Style based on investigation status
            button_style = "🔍 " if not is_investigated else "✓ "
            button_text = f"{button_style}{clue}"

            if st.button(
                button_text,
                key=clue_key,
                disabled=is_investigated,
                help=f"Click to investigate: {clue}"
            ):
                # Add to investigated clues
                investigation_state['investigated_clues'].append(clue)

                # Provide feedback
                if clue in mystery['clues']:
                    st.success(f"Important evidence found: {clue}")
                    investigation_state['detective_points'] += 10
                else:
                    st.info(f"Interesting but not crucial: {clue}")
                    investigation_state['detective_points'] += 5

                # Cool effect instead of balloons
                st.markdown("""
                <div style="
                    background: linear-gradient(45deg, #4CAF50, #45a049);
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 10px 0;
                    animation: slideIn 0.5s ease-out;
                ">
                    Evidence Collected! +{} Points
                </div>
                """.format(10 if clue in mystery['clues'] else 5), unsafe_allow_html=True)

                st.rerun()

        # Show investigation progress
        if investigation_state['investigated_clues']:
            important_clues_found = len([c for c in investigation_state['investigated_clues'] if c in mystery['clues']])
            progress = important_clues_found / len(mystery['clues'])

            st.progress(progress)
            st.markdown(f"**Investigation Progress:** {progress:.0%} ({important_clues_found}/{len(mystery['clues'])} key evidence found)")
            st.metric("Detective Points", investigation_state['detective_points'])

            # Solve the mystery
            if progress >= 0.75 and not investigation_state['mystery_solved']:
                st.markdown("### Ready to Solve the Mystery?")

                solution_guess = st.text_area(
                    "What's your theory about what's really happening?",
                    placeholder="Based on the evidence, I believe the problem is...",
                    height=100,
                    key=f"solution_{investigation_key}"
                )

                if st.button("Submit Solution", key=f"submit_{investigation_key}"):
                    if solution_guess.strip():
                        investigation_state['mystery_solved'] = True
                        investigation_state['detective_points'] += 50

                        # Cool success effect
                        st.markdown("""
                        <div style="
                            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                            color: white;
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                            margin: 20px 0;
                            animation: pulse 1s ease-in-out;
                            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                        ">
                            <h3>Mystery Solved!</h3>
                            <p>Excellent detective work! +50 Bonus Points</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"**The Real Solution:** {mystery['solution']}")
                        st.markdown(f"**Your Theory:** {solution_guess}")

                        # Show what happens next
                        self._show_challenge_completion("mystery_solved", investigation_state['detective_points'])

                        st.rerun()

    def _show_challenge_completion(self, challenge_type: str, points: int) -> None:
        """Show what happens when user completes a challenge."""
        st.markdown("### What Happens Next?")

        completion_responses = {
            "mystery_solved": [
                "Your detective skills reveal hidden user experience issues in your design.",
                "You now understand how spatial psychology affects user behavior.",
                "This investigation approach can be applied to any design problem."
            ],
            "persona_completed": [
                "You've developed deeper empathy for your users' real experiences.",
                "This perspective will inform every design decision you make.",
                "User-centered thinking is now part of your design process."
            ],
            "perspective_shifted": [
                "Your design thinking has expanded beyond your initial assumptions.",
                "You can now see your project through multiple lenses simultaneously.",
                "This multi-perspective approach leads to more inclusive design."
            ],
            "constraints_mastered": [
                "You've learned to turn limitations into creative opportunities.",
                "Constraint-based thinking enhances rather than limits creativity.",
                "These problem-solving skills apply to any design challenge."
            ]
        }

        responses = completion_responses.get(challenge_type, ["Great work! You've completed the challenge."])

        for i, response in enumerate(responses):
            st.markdown(f"**{i+1}.** {response}")

        # Show learning progression
        st.markdown("### Your Learning Journey")

        learning_stages = {
            "mystery_solved": ["Observation", "Investigation", "Analysis", "Solution"],
            "persona_completed": ["Empathy", "Understanding", "Application", "Integration"],
            "perspective_shifted": ["Awareness", "Exploration", "Comparison", "Synthesis"],
            "constraints_mastered": ["Challenge", "Creativity", "Innovation", "Mastery"]
        }

        stages = learning_stages.get(challenge_type, ["Start", "Progress", "Develop", "Complete"])

        cols = st.columns(len(stages))
        for i, stage in enumerate(stages):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #4CAF50, #45a049);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 5px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                ">
                    <strong>{stage}</strong><br>
                    ✓ Complete
                </div>
                """, unsafe_allow_html=True)

        # Next steps
        st.markdown("### Continue Your Design Journey")

        next_steps = {
            "mystery_solved": "Apply this investigative approach to other aspects of your design",
            "persona_completed": "Use this persona perspective in your next design decisions",
            "perspective_shifted": "Challenge more assumptions in your design thinking",
            "constraints_mastered": "Seek out creative constraints to enhance your next project"
        }

        next_step = next_steps.get(challenge_type, "Continue exploring and learning")
        st.info(f"**Next Step:** {next_step}")

        # Achievement badge
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #333;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        ">
            <h3>Achievement Unlocked!</h3>
            <p><strong>{challenge_type.replace('_', ' ').title()}</strong></p>
            <p>Total Points: {points}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _get_personas_for_building(self, building_type: str) -> Dict[str, Dict]:
        """Get personas specific to building type."""
        base_personas = {
            "Anxious First-Timer": {
                "icon": "👤",
                "description": "Nervous about navigating this new space, needs clear guidance and reassurance to feel comfortable",
                "scenario": f"You're visiting this {building_type} for the first time and feeling overwhelmed by the unfamiliar environment",
                "mission": "Find what you need without getting lost or feeling embarrassed about asking for help",
                "thoughts": ["Where exactly do I go?", "Is this the right place for me?", "Will staff be available to help?", "What if I look lost?"],
                "insights": [
                    "Clear, visible signage reduces anxiety and builds confidence",
                    "Friendly, approachable staff visibility helps newcomers feel welcome",
                    "Open sightlines allow people to orient themselves and feel in control"
                ]
            },
            "Busy Parent": {
                "icon": "👥",
                "description": "Juggling multiple responsibilities, needs efficiency and child-friendly features throughout the space",
                "scenario": f"You're rushing to the {building_type} with two young children in tow, trying to accomplish your goals quickly",
                "mission": "Get what you need efficiently while keeping kids safe, engaged, and well-behaved",
                "thoughts": ["Is this environment safe for children?", "How long will this take?", "Where can I manage stroller and bags?", "Will my kids get bored or disruptive?"],
                "insights": [
                    "Child-height features and sightlines matter for both safety and engagement",
                    "Clear, direct circulation paths help families move efficiently",
                    "Visual supervision opportunities are essential for parent peace of mind"
                ]
            },
            "Mobility-Challenged Elder": {
                "icon": "♿",
                "description": "Uses mobility aids, values comfort and accessibility over speed, seeks dignity in all interactions",
                "scenario": f"You're using a walker to navigate the {building_type}, taking your time and being careful with each step",
                "mission": "Access all services comfortably without physical barriers or social embarrassment",
                "thoughts": ["Can I reach everything I need?", "Are there places to rest when I get tired?", "Will I feel included and valued?", "Can I maintain my independence?"],
                "insights": [
                    "Universal design principles benefit everyone, not just those with disabilities",
                    "Strategic rest areas are essential for longer visits and social interaction",
                    "Dignity in accessibility means avoiding segregated or obviously 'special' accommodations"
                ]
            }
        }

        # Add building-specific personas
        if building_type == "community center":
            base_personas["Shy Teenager"] = {
                "icon": "👤",
                "description": "Wants to belong and find their social group but feels self-conscious about fitting in with existing communities",
                "scenario": "You're checking out programs and activities but worried about whether you'll fit in with the other participants",
                "mission": "Find activities and potential friends without standing out awkwardly or being forced into uncomfortable social situations",
                "thoughts": ["Will I look stupid or out of place?", "Are there people my age who share my interests?", "Is this place cool or will I be judged?", "Can I observe before committing?"],
                "insights": [
                    "Casual observation spaces help teens assess social dynamics before participating",
                    "Peer visibility and activity transparency matter for social comfort",
                    "Multiple entry points and participation levels reduce social pressure"
                ]
            }
        elif building_type == "hospital":
            base_personas["Worried Family Member"] = {
                "icon": "👥",
                "description": "Emotionally stressed about a loved one's health, needs clear information and comfortable waiting areas",
                "scenario": "You're spending long hours at the hospital while a family member receives treatment, feeling anxious and uncertain",
                "mission": "Stay informed about your loved one's condition while managing your own emotional and physical needs",
                "thoughts": ["How is my family member doing?", "Where can I get updates?", "Is there somewhere comfortable to wait?", "What if there's an emergency?"],
                "insights": [
                    "Clear communication pathways reduce family anxiety and improve satisfaction",
                    "Comfortable, well-equipped waiting areas support extended stays",
                    "Privacy options for difficult conversations are essential"
                ]
            }

        return base_personas

    def _render_constraint_puzzle_game(self, challenge_text: str, theme: Dict, building_type: str) -> None:
        """Render an interactive constraint puzzle game."""
        st.markdown(f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 25px;
            padding: 40px;
            margin: 20px 0;
            box-shadow: 0 20px 50px rgba(0,0,0,0.35);
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -20px;
                left: -20px;
                right: -20px;
                bottom: -20px;
                background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.05), transparent);
                animation: {theme['animation']} 6s linear infinite;
            "></div>
            <div style="
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.8));
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 25px;
                font-size: 3.5em;
                color: {theme['primary']};
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                position: relative;
                z-index: 2;
                border: 3px solid rgba(255,255,255,0.6);
                transform: rotate(45deg);
            ">
                <div style="transform: rotate(-45deg);">{theme['icon']}</div>
            </div>
            <h2 style="
                color: white;
                margin: 0;
                text-shadow: 0 4px 8px rgba(0,0,0,0.5);
                font-size: 2.4em;
                font-weight: 200;
                letter-spacing: 3px;
                position: relative;
                z-index: 2;
            ">
                CONSTRAINT PUZZLE
            </h2>
            <div style="
                width: 120px;
                height: 3px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent);
                margin: 20px auto 0;
                position: relative;
                z-index: 2;
                border-radius: 2px;
            "></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🧩 Design Challenge Puzzle")

        # Constraint cards
        constraints = {
            "◉ Budget Cut": {"impact": "40% less money", "color": "#FF6B6B", "challenge": "What gets prioritized?"},
            "◈ Time Crunch": {"impact": "Half the timeline", "color": "#4ECDC4", "challenge": "What can be done quickly?"},
            "◆ Site Issues": {"impact": "Floods every 5 years", "color": "#45B7D1", "challenge": "How to design for water?"},
            "◎ Double Users": {"impact": "Twice as many people", "color": "#96CEB4", "challenge": "How to fit everyone?"},
            "◐ Material Limits": {"impact": "Only local materials", "color": "#FFEAA7", "challenge": "What's available nearby?"},
            "● Accessibility": {"impact": "Full universal design", "color": "#DDA0DD", "challenge": "How to include everyone?"}
        }

        st.markdown("**🎲 Pick Your Constraints** (Choose 2-3 for maximum challenge!):")

        # Initialize constraint selection
        if 'selected_constraints' not in st.session_state:
            st.session_state.selected_constraints = []

        # Display constraint cards
        cols = st.columns(3)
        for i, (constraint_name, constraint_data) in enumerate(constraints.items()):
            with cols[i % 3]:
                is_selected = constraint_name in st.session_state.selected_constraints

                # Create interactive constraint card
                card_style = f"""
                background: {'linear-gradient(45deg, ' + constraint_data['color'] + ', white)' if is_selected else constraint_data['color'] + '40'};
                border: {'3px solid ' + constraint_data['color'] if is_selected else '2px solid ' + constraint_data['color'] + '80'};
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                """

                if st.button(
                    f"{constraint_name}\n{constraint_data['impact']}\n{constraint_data['challenge']}",
                    key=f"constraint_{i}",
                    help=f"Click to {'remove' if is_selected else 'add'} this constraint"
                ):
                    if is_selected:
                        st.session_state.selected_constraints.remove(constraint_name)
                    else:
                        st.session_state.selected_constraints.append(constraint_name)
                    st.rerun()

        # Show selected constraints and puzzle
        if st.session_state.selected_constraints:
            st.markdown("---")
            st.markdown("### 🎯 Your Design Challenge")

            # Display selected constraints
            st.markdown("**Active Constraints:**")
            for constraint in st.session_state.selected_constraints:
                constraint_data = constraints[constraint]
                st.markdown(f"""
                <div style="
                    background: {constraint_data['color']}20;
                    border-left: 4px solid {constraint_data['color']};
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                ">
                    <strong>{constraint}</strong>: {constraint_data['impact']} - {constraint_data['challenge']}
                </div>
                """, unsafe_allow_html=True)

            # Creative solution area
            st.markdown("### 💡 Your Creative Solution")

            # Solution templates based on constraints
            solution_prompts = {
                1: "With this constraint, I would...",
                2: "To handle both constraints, my strategy is...",
                3: "With these three challenges, I'd create a design that..."
            }

            num_constraints = len(st.session_state.selected_constraints)
            prompt = solution_prompts.get(num_constraints, "My innovative solution is...")

            solution = st.text_area(
                "Describe your creative solution:",
                placeholder=prompt,
                height=120
            )

            if solution:
                # Calculate creativity score based on solution length and constraint difficulty
                creativity_score = min(100, len(solution.split()) * 2 + num_constraints * 10)

                st.success(f"🎨 Creative Solution Submitted!")
                st.metric("🏆 Creativity Score", f"{creativity_score}/100")

                if creativity_score > 80:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(45deg, #FFD700, #FFA500);
                        color: #333;
                        padding: 20px;
                        border-radius: 15px;
                        text-align: center;
                        margin: 20px 0;
                        animation: glow 2s ease-in-out infinite;
                        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
                    ">
                        <h3>Exceptional Creativity!</h3>
                        <p>You've turned constraints into opportunities!</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif creativity_score > 60:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(45deg, #4CAF50, #45a049);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 15px 0;
                        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
                    ">
                        <strong>Great thinking!</strong> You're finding innovative solutions!
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(45deg, #2196F3, #1976D2);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 15px 0;
                        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
                    ">
                        <strong>Good start!</strong> Keep exploring creative possibilities!
                    </div>
                    """, unsafe_allow_html=True)

                # Bonus challenge
                if st.button("🚀 Add Another Constraint!", key="bonus_constraint"):
                    remaining_constraints = [c for c in constraints.keys() if c not in st.session_state.selected_constraints]
                    if remaining_constraints:
                        bonus_constraint = random.choice(remaining_constraints)
                        st.session_state.selected_constraints.append(bonus_constraint)
                        st.rerun()


def render_enhanced_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Main function to render enhanced gamified challenges."""
    renderer = EnhancedGamificationRenderer()
    renderer.render_enhanced_challenge(challenge_data)


# CSS for animations
def inject_gamification_css():
    """Inject CSS for gamification animations."""
    st.markdown("""
    <style>
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0) scale(1);
            filter: brightness(1);
        }
        40% {
            transform: translateY(-8px) scale(1.02);
            filter: brightness(1.1);
        }
        60% {
            transform: translateY(-4px) scale(1.01);
            filter: brightness(1.05);
        }
    }

    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
        }
        50% {
            transform: scale(1.03);
            box-shadow: 0 0 0 10px rgba(139, 92, 246, 0.1);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
        }
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0) rotate(0deg); }
        10% { transform: translateX(-2px) rotate(-1deg); }
        20% { transform: translateX(2px) rotate(1deg); }
        30% { transform: translateX(-2px) rotate(-1deg); }
        40% { transform: translateX(2px) rotate(1deg); }
        50% { transform: translateX(-1px) rotate(-0.5deg); }
        60% { transform: translateX(1px) rotate(0.5deg); }
        70% { transform: translateX(-1px) rotate(-0.5deg); }
        80% { transform: translateX(1px) rotate(0.5deg); }
        90% { transform: translateX(-1px) rotate(-0.5deg); }
    }

    @keyframes rotate {
        0% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(90deg) scale(1.05); }
        50% { transform: rotate(180deg) scale(1); }
        75% { transform: rotate(270deg) scale(1.05); }
        100% { transform: rotate(360deg) scale(1); }
    }

    @keyframes slideIn {
        0% {
            opacity: 0;
            transform: translateY(-20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes glow {
        0% {
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5), 0 0 20px rgba(76, 175, 80, 0.3);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 25px rgba(76, 175, 80, 0.8), 0 0 40px rgba(76, 175, 80, 0.5);
            transform: scale(1.02);
        }
        100% {
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5), 0 0 20px rgba(76, 175, 80, 0.3);
            transform: scale(1);
        }
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(30px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stButton > button {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 15px;
        white-space: normal !important;
        height: auto !important;
        min-height: 70px;
        padding: 15px 20px !important;
        text-align: left !important;
        line-height: 1.5 !important;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: rgba(205, 118, 109, 0.3);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .stExpander > div > div > div > div {
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
