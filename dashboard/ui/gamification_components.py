"""
Enhanced Gamification UI Components
Creates engaging, interactive gamification elements for the architecture mentor system.
"""

import streamlit as st
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

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
        """Render an enhanced gamified challenge with visual elements."""
        
        challenge_text = challenge_data.get("challenge_text", "")
        challenge_type = self._detect_challenge_type(challenge_text)
        
        # Get visual theme
        theme = self.challenge_types.get(challenge_type, self.challenge_types["role_play"])
        
        # Extract challenge components
        title, scenario, main_challenge, question = self._parse_challenge_text(challenge_text)
        
        # Render the enhanced challenge
        self._render_challenge_header(title, theme)
        self._render_scenario_box(scenario, theme)
        self._render_main_challenge(main_challenge, theme)
        self._render_interactive_question(question, theme)
        self._render_challenge_footer(challenge_type)
    
    def _detect_challenge_type(self, challenge_text: str) -> str:
        """Detect the type of challenge from the text."""
        text_lower = challenge_text.lower()
        
        if "role-play" in text_lower or "step into" in text_lower:
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
        else:
            return "role_play"
    
    def _parse_challenge_text(self, challenge_text: str) -> tuple:
        """Parse challenge text into components."""
        lines = challenge_text.split('\n')
        
        title = ""
        scenario = ""
        main_challenge = ""
        question = ""
        
        current_section = "title"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
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
        
        return title.strip(), scenario.strip(), main_challenge.strip(), question.strip()
    
    def _render_challenge_header(self, title: str, theme: Dict) -> None:
        """Render an animated challenge header."""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {theme['bg_color']} 0%, {theme['color']}20 100%);
            border: 3px solid {theme['border']};
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            animation: pulse 2s infinite;
        ">
            <div style="font-size: 3em; margin-bottom: 10px;">{theme['icon']}</div>
            <h2 style="
                color: {theme['color']};
                margin: 0;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            ">{title}</h2>
        </div>
        
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
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
        st.markdown("### 🛠️ Challenge Tools")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💡 Get a Hint", key=f"hint_{random.randint(1000, 9999)}"):
                hints = [
                    "Think about the user's emotional journey",
                    "Consider the sensory experience",
                    "What would surprise or delight them?",
                    "How does the space make them feel safe?",
                    "What draws their attention first?"
                ]
                st.info(f"💡 **Hint:** {random.choice(hints)}")
        
        with col2:
            if st.button("🎲 Random Perspective", key=f"perspective_{random.randint(1000, 9999)}"):
                perspectives = [
                    "A child seeing this space for the first time",
                    "An elderly person with mobility challenges", 
                    "Someone who's never been in a community center",
                    "A person from a different cultural background",
                    "Someone having a difficult day"
                ]
                st.success(f"🎭 **Try this perspective:** {random.choice(perspectives)}")
        
        with col3:
            if st.button("⭐ Inspiration", key=f"inspiration_{random.randint(1000, 9999)}"):
                inspirations = [
                    "Think of your favorite childhood place",
                    "Imagine a space that feels like a warm hug",
                    "Consider how light changes throughout the day",
                    "Think about sounds, smells, and textures",
                    "Imagine the space during different seasons"
                ]
                st.warning(f"✨ **Inspiration:** {inspirations[random.randint(0, len(inspirations)-1)]}")
    
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
        """Render gamification progress in sidebar."""
        stats = st.session_state.gamification_stats

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎮 Your Progress")

        # Level and XP
        st.sidebar.markdown(f"**Level:** {stats['level']} 🏆")
        xp_to_next = 100 - (stats['total_xp'] % 100)
        st.sidebar.progress((stats['total_xp'] % 100) / 100)
        st.sidebar.markdown(f"**XP:** {stats['total_xp']} ({xp_to_next} to next level)")

        # Stats
        st.sidebar.markdown(f"**Challenges:** {stats['challenges_completed']} ✅")
        st.sidebar.markdown(f"**Current Streak:** {stats['current_streak']} 🔥")
        st.sidebar.markdown(f"**Best Streak:** {stats['best_streak']} ⭐")

        # Achievements
        if stats['achievements']:
            st.sidebar.markdown("**Achievements:**")
            for achievement in stats['achievements']:
                if achievement == 'first_challenge':
                    st.sidebar.markdown("🏅 Challenge Accepted")
                elif achievement == 'perspective_master':
                    st.sidebar.markdown("🎭 Perspective Master")

# Convenience functions for easy integration
def render_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Render a gamified challenge with enhanced visuals."""
    try:
        print(f"🎮 GAMIFICATION: Starting render with data: {list(challenge_data.keys())}")
        display = GamificationDisplay()
        display.render_gamified_challenge(challenge_data)
        print(f"🎮 GAMIFICATION: Render completed successfully")

        # Track the challenge
        tracker = GamificationTracker()
        # Note: In real implementation, call add_challenge_completion when user responds

    except Exception as e:
        print(f"🎮 GAMIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Fallback to simple gamification display
        _render_simple_gamified_challenge(challenge_data)

def _render_simple_gamified_challenge(challenge_data: Dict[str, Any]) -> None:
    """Simple fallback gamification display."""
    import streamlit as st

    challenge_text = challenge_data.get("challenge_text", "")
    challenge_type = challenge_data.get("challenge_type", "challenge")
    difficulty = challenge_data.get("difficulty_level", "medium")

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

def render_gamification_sidebar() -> None:
    """Render gamification progress in sidebar."""
    tracker = GamificationTracker()
    tracker.render_progress_sidebar()
