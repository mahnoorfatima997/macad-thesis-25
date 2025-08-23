"""
Advanced Progress Tracking System for Gamified Learning
Tracks user progress across different architectural thinking areas with visual indicators.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import json
from datetime import datetime, timedelta
import random

class ProgressTracker:
    """Comprehensive progress tracking for architectural learning."""
    
    def __init__(self):
        self.skill_areas = {
            "spatial_reasoning": {
                "name": "Spatial Reasoning",
                "icon": "🏗️",
                "color": "#3498db",
                "description": "Understanding 3D relationships and spatial organization"
            },
            "sustainability": {
                "name": "Sustainability",
                "icon": "🌱",
                "color": "#27ae60",
                "description": "Environmental design and sustainable practices"
            },
            "user_experience": {
                "name": "User Experience",
                "icon": "👥",
                "color": "#e74c3c",
                "description": "Human-centered design and accessibility"
            },
            "technical_systems": {
                "name": "Technical Systems",
                "icon": "⚙️",
                "color": "#f39c12",
                "description": "Building systems and construction methods"
            },
            "cultural_context": {
                "name": "Cultural Context",
                "icon": "🌍",
                "color": "#9b59b6",
                "description": "Cultural sensitivity and contextual design"
            },
            "creative_thinking": {
                "name": "Creative Thinking",
                "icon": "🎨",
                "color": "#e67e22",
                "description": "Innovation and creative problem-solving"
            }
        }
        
        self.milestone_levels = {
            1: {"name": "Explorer", "xp_required": 0, "color": "#95a5a6"},
            2: {"name": "Apprentice", "xp_required": 100, "color": "#3498db"},
            3: {"name": "Designer", "xp_required": 300, "color": "#27ae60"},
            4: {"name": "Architect", "xp_required": 600, "color": "#f39c12"},
            5: {"name": "Master", "xp_required": 1000, "color": "#e74c3c"},
            6: {"name": "Visionary", "xp_required": 1500, "color": "#9b59b6"}
        }
        
        self._initialize_progress_state()
    
    def _initialize_progress_state(self):
        """Initialize progress tracking in session state."""
        if 'progress_data' not in st.session_state:
            st.session_state.progress_data = {
                'total_xp': 0,
                'current_level': 1,
                'skill_progress': {skill: 0 for skill in self.skill_areas.keys()},
                'challenges_completed': 0,
                'streak_days': 0,
                'last_activity': datetime.now().isoformat(),
                'daily_goals': {
                    'challenges': 3,
                    'xp': 50,
                    'skills_practiced': 2
                },
                'weekly_stats': [],
                'achievement_history': []
            }
    
    def render_progress_dashboard(self):
        """Render the main progress dashboard."""
        st.markdown("## 📊 Your Learning Progress")
        
        # Overall progress overview
        self._render_overall_progress()
        
        # Skill area breakdown
        self._render_skill_breakdown()
        
        # Daily goals and streaks
        self._render_daily_goals()
        
        # Weekly progress chart
        self._render_weekly_progress()
    
    def _render_overall_progress(self):
        """Render overall progress indicators."""
        progress_data = st.session_state.progress_data
        current_level = progress_data['current_level']
        total_xp = progress_data['total_xp']
        
        # Current level info
        level_info = self.milestone_levels[current_level]
        next_level = current_level + 1 if current_level < 6 else 6
        next_level_info = self.milestone_levels[next_level]
        
        # Calculate progress to next level
        if current_level < 6:
            current_level_xp = level_info['xp_required']
            next_level_xp = next_level_info['xp_required']
            progress_to_next = (total_xp - current_level_xp) / (next_level_xp - current_level_xp)
            progress_to_next = max(0, min(1, progress_to_next))
        else:
            progress_to_next = 1.0
        
        # Level display
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {level_info['color']}20, {level_info['color']}40);
                border: 3px solid {level_info['color']};
                border-radius: 20px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
            ">
                <h2 style="color: {level_info['color']}; margin: 0;">
                    Level {current_level}
                </h2>
                <h3 style="color: {level_info['color']}; margin: 5px 0;">
                    {level_info['name']}
                </h3>
                <p style="margin: 0; font-size: 1.2em;">
                    {total_xp} XP
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Progress bar to next level
            if current_level < 6:
                st.markdown(f"**Progress to {next_level_info['name']} (Level {next_level})**")
                st.progress(progress_to_next)
                xp_needed = next_level_xp - total_xp
                st.caption(f"{xp_needed} XP needed for next level")
            else:
                st.markdown("**🏆 Maximum Level Achieved!**")
                st.success("You've reached the highest level!")
        
        with col3:
            # Quick stats
            st.metric("Challenges Completed", progress_data['challenges_completed'])
            st.metric("Current Streak", f"{progress_data['streak_days']} days")
    
    def _render_skill_breakdown(self):
        """Render skill area progress breakdown."""
        st.markdown("### 🎯 Skill Development")
        
        progress_data = st.session_state.progress_data
        skill_progress = progress_data['skill_progress']
        
        # Create skill progress visualization
        skills = list(self.skill_areas.keys())
        values = [skill_progress.get(skill, 0) for skill in skills]
        colors = [self.skill_areas[skill]['color'] for skill in skills]
        
        # Radar chart for skills
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[self.skill_areas[skill]['name'] for skill in skills],
            fill='toself',
            name='Current Level',
            line_color='rgba(52, 152, 219, 0.8)',
            fillcolor='rgba(52, 152, 219, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Skill Development Radar",
            height=400
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Skill details
            for skill_key, skill_info in self.skill_areas.items():
                current_value = skill_progress.get(skill_key, 0)
                st.markdown(f"""
                <div style="
                    background: {skill_info['color']}15;
                    border-left: 4px solid {skill_info['color']};
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                ">
                    <strong>{skill_info['icon']} {skill_info['name']}</strong><br>
                    <small>{skill_info['description']}</small><br>
                    <div style="
                        background: #f0f0f0;
                        border-radius: 10px;
                        height: 8px;
                        margin: 5px 0;
                    ">
                        <div style="
                            background: {skill_info['color']};
                            height: 8px;
                            border-radius: 10px;
                            width: {current_value}%;
                        "></div>
                    </div>
                    <small>{current_value}/100</small>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_daily_goals(self):
        """Render daily goals and achievements."""
        st.markdown("### 🎯 Daily Goals")
        
        progress_data = st.session_state.progress_data
        daily_goals = progress_data['daily_goals']
        
        # Calculate today's progress
        today_challenges = min(progress_data['challenges_completed'], daily_goals['challenges'])
        today_xp = min(progress_data['total_xp'], daily_goals['xp'])
        skills_practiced = len([s for s in progress_data['skill_progress'].values() if s > 0])
        skills_practiced = min(skills_practiced, daily_goals['skills_practiced'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self._render_goal_card(
                "🎯 Challenges",
                today_challenges,
                daily_goals['challenges'],
                "#3498db"
            )
        
        with col2:
            self._render_goal_card(
                "⭐ Experience",
                today_xp,
                daily_goals['xp'],
                "#f39c12"
            )
        
        with col3:
            self._render_goal_card(
                "🧠 Skills",
                skills_practiced,
                daily_goals['skills_practiced'],
                "#27ae60"
            )
    
    def _render_goal_card(self, title: str, current: int, target: int, color: str):
        """Render individual goal card."""
        progress = min(current / target, 1.0) if target > 0 else 0
        
        st.markdown(f"""
        <div style="
            background: {color}15;
            border: 2px solid {color};
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            margin: 5px 0;
        ">
            <h4 style="color: {color}; margin: 0 0 10px 0;">{title}</h4>
            <div style="
                background: #f0f0f0;
                border-radius: 10px;
                height: 12px;
                margin: 10px 0;
            ">
                <div style="
                    background: {color};
                    height: 12px;
                    border-radius: 10px;
                    width: {progress * 100}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <p style="margin: 0; font-weight: bold;">
                {current}/{target}
            </p>
            {'✅ Complete!' if progress >= 1.0 else f'{target - current} to go'}
        </div>
        """, unsafe_allow_html=True)
    
    def _render_weekly_progress(self):
        """Render weekly progress chart."""
        st.markdown("### 📈 Weekly Progress")
        
        # Generate sample weekly data (in real implementation, this would come from stored data)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        xp_data = [random.randint(20, 80) for _ in days]
        challenges_data = [random.randint(1, 5) for _ in days]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=days,
            y=xp_data,
            name='XP Earned',
            marker_color='#3498db',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=days,
            y=challenges_data,
            mode='lines+markers',
            name='Challenges Completed',
            line=dict(color='#e74c3c', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Weekly Learning Activity',
            xaxis_title='Day',
            yaxis=dict(title='XP Earned', side='left'),
            yaxis2=dict(title='Challenges', side='right', overlaying='y'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def add_xp(self, amount: int, skill_area: str = None):
        """Add XP and update progress."""
        progress_data = st.session_state.progress_data
        progress_data['total_xp'] += amount
        
        # Update skill-specific progress
        if skill_area and skill_area in self.skill_areas:
            progress_data['skill_progress'][skill_area] = min(
                progress_data['skill_progress'][skill_area] + amount // 2,
                100
            )
        
        # Check for level up
        self._check_level_up()
        
        # Update last activity
        progress_data['last_activity'] = datetime.now().isoformat()
    
    def complete_challenge(self, challenge_type: str, skill_areas: List[str] = None):
        """Mark a challenge as completed and award XP."""
        progress_data = st.session_state.progress_data
        progress_data['challenges_completed'] += 1
        
        # Award XP based on challenge type
        xp_rewards = {
            'curiosity_amplification': 25,
            'constraint_challenge': 35,
            'perspective_shift': 30,
            'role_play': 40,
            'spatial_reasoning': 45,
            'technical_challenge': 50
        }
        
        xp_earned = xp_rewards.get(challenge_type, 25)
        
        # Bonus XP for skill diversity
        if skill_areas:
            for skill in skill_areas:
                self.add_xp(xp_earned // len(skill_areas), skill)
        else:
            self.add_xp(xp_earned)
        
        # Show completion feedback
        st.success(f"🎉 Challenge completed! +{xp_earned} XP earned!")
        
        # Check for achievements
        self._check_achievements()
    
    def _check_level_up(self):
        """Check if user has leveled up."""
        progress_data = st.session_state.progress_data
        current_level = progress_data['current_level']
        total_xp = progress_data['total_xp']
        
        for level, info in self.milestone_levels.items():
            if total_xp >= info['xp_required'] and level > current_level:
                progress_data['current_level'] = level
                st.balloons()
                st.success(f"🎉 LEVEL UP! You're now a {info['name']} (Level {level})!")
                break
    
    def _check_achievements(self):
        """Check for new achievements."""
        progress_data = st.session_state.progress_data
        
        # Example achievements
        achievements = []
        
        if progress_data['challenges_completed'] == 1:
            achievements.append("🌟 First Steps - Completed your first challenge!")
        
        if progress_data['challenges_completed'] == 10:
            achievements.append("🏆 Challenge Master - Completed 10 challenges!")
        
        if progress_data['total_xp'] >= 100:
            achievements.append("⭐ XP Collector - Earned 100 XP!")
        
        # Show new achievements
        for achievement in achievements:
            if achievement not in progress_data['achievement_history']:
                progress_data['achievement_history'].append(achievement)
                st.success(f"🏅 Achievement Unlocked: {achievement}")

# Global instance
progress_tracker = ProgressTracker()
