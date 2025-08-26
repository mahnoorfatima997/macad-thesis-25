"""
Achievement Badge System for Gamified Architectural Learning
Comprehensive badge system with visual rewards and progression tracking.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

class AchievementBadgeSystem:
    """Comprehensive achievement and badge system for architectural learning."""
    
    def __init__(self):
        self.badge_categories = {
            "thinking_skills": {
                "name": "Thinking Skills",
                "icon": "🧠",
                "color": "#3498db",
                "description": "Badges for developing different types of architectural thinking"
            },
            "design_process": {
                "name": "Design Process",
                "icon": "🎨",
                "color": "#e74c3c",
                "description": "Badges for mastering design methodology and process"
            },
            "technical_mastery": {
                "name": "Technical Mastery",
                "icon": "⚙️",
                "color": "#f39c12",
                "description": "Badges for technical knowledge and building systems"
            },
            "sustainability": {
                "name": "Sustainability",
                "icon": "🌱",
                "color": "#27ae60",
                "description": "Badges for environmental and sustainable design"
            },
            "social_impact": {
                "name": "Social Impact",
                "icon": "👥",
                "color": "#9b59b6",
                "description": "Badges for community-focused and inclusive design"
            },
            "innovation": {
                "name": "Innovation",
                "icon": "💡",
                "color": "#e67e22",
                "description": "Badges for creative and innovative thinking"
            },
            "milestones": {
                "name": "Milestones",
                "icon": "🏆",
                "color": "#34495e",
                "description": "Special badges for major achievements and milestones"
            }
        }
        
        self.badges = {
            # Thinking Skills Badges
            "spatial_explorer": {
                "name": "Spatial Explorer",
                "icon": "🏗️",
                "category": "thinking_skills",
                "description": "Completed 5 spatial reasoning challenges",
                "requirement": {"type": "skill_challenges", "skill": "spatial_reasoning", "count": 5},
                "rarity": "common",
                "xp_reward": 50
            },
            "spatial_master": {
                "name": "Spatial Master",
                "icon": "🏛️",
                "category": "thinking_skills", 
                "description": "Achieved 80+ in spatial reasoning skill",
                "requirement": {"type": "skill_level", "skill": "spatial_reasoning", "level": 80},
                "rarity": "rare",
                "xp_reward": 100
            },
            "perspective_shifter": {
                "name": "Perspective Shifter",
                "icon": "🎭",
                "category": "thinking_skills",
                "description": "Completed 10 perspective-based challenges",
                "requirement": {"type": "challenge_type", "challenge": "perspective_shift", "count": 10},
                "rarity": "uncommon",
                "xp_reward": 75
            },
            
            # Design Process Badges
            "design_thinker": {
                "name": "Design Thinker",
                "icon": "💭",
                "category": "design_process",
                "description": "Completed first design exploration challenge",
                "requirement": {"type": "first_challenge", "challenge": "design_exploration"},
                "rarity": "common",
                "xp_reward": 25
            },
            "iteration_master": {
                "name": "Iteration Master",
                "icon": "🔄",
                "category": "design_process",
                "description": "Revised and improved a design 5 times",
                "requirement": {"type": "iterations", "count": 5},
                "rarity": "uncommon",
                "xp_reward": 60
            },
            "holistic_designer": {
                "name": "Holistic Designer",
                "icon": "🌐",
                "category": "design_process",
                "description": "Achieved 60+ in all skill areas",
                "requirement": {"type": "all_skills", "level": 60},
                "rarity": "epic",
                "xp_reward": 200
            },
            
            # Technical Mastery Badges
            "systems_thinker": {
                "name": "Systems Thinker",
                "icon": "⚡",
                "category": "technical_mastery",
                "description": "Completed 5 technical system challenges",
                "requirement": {"type": "skill_challenges", "skill": "technical_systems", "count": 5},
                "rarity": "common",
                "xp_reward": 50
            },
            "building_expert": {
                "name": "Building Expert",
                "icon": "🏢",
                "category": "technical_mastery",
                "description": "Achieved 90+ in technical systems skill",
                "requirement": {"type": "skill_level", "skill": "technical_systems", "level": 90},
                "rarity": "legendary",
                "xp_reward": 250
            },
            
            # Sustainability Badges
            "eco_warrior": {
                "name": "Eco Warrior",
                "icon": "🌿",
                "category": "sustainability",
                "description": "Completed 5 sustainability challenges",
                "requirement": {"type": "skill_challenges", "skill": "sustainability", "count": 5},
                "rarity": "common",
                "xp_reward": 50
            },
            "green_architect": {
                "name": "Green Architect",
                "icon": "🌳",
                "category": "sustainability",
                "description": "Achieved 85+ in sustainability skill",
                "requirement": {"type": "skill_level", "skill": "sustainability", "level": 85},
                "rarity": "rare",
                "xp_reward": 120
            },
            
            # Social Impact Badges
            "community_advocate": {
                "name": "Community Advocate",
                "icon": "🤝",
                "category": "social_impact",
                "description": "Completed 5 user experience challenges",
                "requirement": {"type": "skill_challenges", "skill": "user_experience", "count": 5},
                "rarity": "common",
                "xp_reward": 50
            },
            "inclusive_designer": {
                "name": "Inclusive Designer",
                "icon": "♿",
                "category": "social_impact",
                "description": "Completed 3 accessibility-focused challenges",
                "requirement": {"type": "challenge_theme", "theme": "accessibility", "count": 3},
                "rarity": "uncommon",
                "xp_reward": 80
            },
            
            # Innovation Badges
            "creative_spark": {
                "name": "Creative Spark",
                "icon": "✨",
                "category": "innovation",
                "description": "Completed first creative challenge",
                "requirement": {"type": "first_challenge", "challenge": "creative_thinking"},
                "rarity": "common",
                "xp_reward": 30
            },
            "innovation_champion": {
                "name": "Innovation Champion",
                "icon": "🚀",
                "category": "innovation",
                "description": "Achieved 95+ in creative thinking skill",
                "requirement": {"type": "skill_level", "skill": "creative_thinking", "level": 95},
                "rarity": "legendary",
                "xp_reward": 300
            },
            
            # Milestone Badges
            "first_steps": {
                "name": "First Steps",
                "icon": "👶",
                "category": "milestones",
                "description": "Completed your very first challenge",
                "requirement": {"type": "total_challenges", "count": 1},
                "rarity": "common",
                "xp_reward": 25
            },
            "dedicated_learner": {
                "name": "Dedicated Learner",
                "icon": "📚",
                "category": "milestones",
                "description": "Completed 25 challenges",
                "requirement": {"type": "total_challenges", "count": 25},
                "rarity": "uncommon",
                "xp_reward": 100
            },
            "architecture_master": {
                "name": "Architecture Master",
                "icon": "🏆",
                "category": "milestones",
                "description": "Completed 100 challenges",
                "requirement": {"type": "total_challenges", "count": 100},
                "rarity": "legendary",
                "xp_reward": 500
            },
            "streak_warrior": {
                "name": "Streak Warrior",
                "icon": "🔥",
                "category": "milestones",
                "description": "Maintained a 7-day learning streak",
                "requirement": {"type": "streak", "days": 7},
                "rarity": "rare",
                "xp_reward": 150
            }
        }
        
        self.rarity_styles = {
            "common": {"color": "#95a5a6", "glow": "0 0 10px #95a5a6"},
            "uncommon": {"color": "#27ae60", "glow": "0 0 15px #27ae60"},
            "rare": {"color": "#3498db", "glow": "0 0 20px #3498db"},
            "epic": {"color": "#9b59b6", "glow": "0 0 25px #9b59b6"},
            "legendary": {"color": "#f39c12", "glow": "0 0 30px #f39c12"}
        }
        
        self._initialize_badge_state()
    
    def _initialize_badge_state(self):
        """Initialize badge system in session state."""
        if 'badge_data' not in st.session_state:
            st.session_state.badge_data = {
                'earned_badges': [],
                'badge_progress': {},
                'recent_badges': [],
                'total_badge_xp': 0,
                'badge_showcase': []  # Featured badges to display
            }
    
    def render_badge_showcase(self):
        """Render the main badge showcase."""
        st.markdown("## 🏅 Achievement Badges")
        
        # Recent badges earned
        self._render_recent_badges()
        
        # Badge categories
        self._render_badge_categories()
        
        # Badge collection overview
        self._render_badge_collection()
    
    def _render_recent_badges(self):
        """Render recently earned badges."""
        badge_data = st.session_state.badge_data
        recent_badges = badge_data.get('recent_badges', [])
        
        if recent_badges:
            st.markdown("### 🌟 Recently Earned")
            
            cols = st.columns(min(len(recent_badges), 4))
            for i, badge_id in enumerate(recent_badges[-4:]):  # Show last 4
                badge = self.badges[badge_id]
                rarity_style = self.rarity_styles[badge['rarity']]
                
                with cols[i]:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, {rarity_style['color']}20, {rarity_style['color']}40);
                        border: 2px solid {rarity_style['color']};
                        border-radius: 15px;
                        padding: 15px;
                        text-align: center;
                        margin: 5px;
                        box-shadow: {rarity_style['glow']};
                        animation: pulse 2s infinite;
                    ">
                        <div style="font-size: 2.5em; margin-bottom: 10px;">
                            {badge['icon']}
                        </div>
                        <h4 style="color: {rarity_style['color']}; margin: 5px 0;">
                            {badge['name']}
                        </h4>
                        <p style="font-size: 0.8em; margin: 0;">
                            {badge['rarity'].title()}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_badge_categories(self):
        """Render badge categories with progress."""
        st.markdown("### 📂 Badge Categories")
        
        badge_data = st.session_state.badge_data
        earned_badges = badge_data.get('earned_badges', [])
        
        for category_id, category_info in self.badge_categories.items():
            # Count badges in this category
            category_badges = [b for b in self.badges.values() if b['category'] == category_id]
            earned_in_category = [b for b in earned_badges if self.badges[b]['category'] == category_id]
            
            progress = len(earned_in_category) / len(category_badges) if category_badges else 0
            
            with st.expander(f"{category_info['icon']} {category_info['name']} ({len(earned_in_category)}/{len(category_badges)})"):
                st.markdown(f"*{category_info['description']}*")
                
                # Progress bar
                st.progress(progress)
                
                # Badge grid
                badge_cols = st.columns(4)
                col_idx = 0
                
                for badge_id, badge in self.badges.items():
                    if badge['category'] == category_id:
                        is_earned = badge_id in earned_badges
                        rarity_style = self.rarity_styles[badge['rarity']]
                        
                        with badge_cols[col_idx % 4]:
                            opacity = "1.0" if is_earned else "0.3"
                            
                            st.markdown(f"""
                            <div style="
                                background: {'linear-gradient(135deg, ' + rarity_style['color'] + '20, ' + rarity_style['color'] + '40)' if is_earned else '#f8f9fa'};
                                border: 2px solid {rarity_style['color'] if is_earned else '#dee2e6'};
                                border-radius: 10px;
                                padding: 10px;
                                text-align: center;
                                margin: 5px 0;
                                opacity: {opacity};
                                {'box-shadow: ' + rarity_style['glow'] + ';' if is_earned else ''}
                            ">
                                <div style="font-size: 2em; margin-bottom: 5px;">
                                    {badge['icon']}
                                </div>
                                <h5 style="margin: 5px 0; font-size: 0.9em;">
                                    {badge['name']}
                                </h5>
                                <p style="font-size: 0.7em; margin: 0;">
                                    {badge['description']}
                                </p>
                                <p style="font-size: 0.6em; margin: 2px 0; color: {rarity_style['color']};">
                                    {badge['rarity'].title()}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        col_idx += 1
    
    def _render_badge_collection(self):
        """Render overall badge collection statistics."""
        st.markdown("### 📊 Collection Statistics")
        
        badge_data = st.session_state.badge_data
        earned_badges = badge_data.get('earned_badges', [])
        total_badges = len(self.badges)
        
        # Calculate rarity distribution
        rarity_counts = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0}
        for badge_id in earned_badges:
            rarity = self.badges[badge_id]['rarity']
            rarity_counts[rarity] += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completion_rate = len(earned_badges) / total_badges if total_badges > 0 else 0
            st.metric("Collection Progress", f"{len(earned_badges)}/{total_badges}", f"{completion_rate:.1%}")
        
        with col2:
            total_badge_xp = sum(self.badges[badge_id]['xp_reward'] for badge_id in earned_badges)
            st.metric("Badge XP Earned", total_badge_xp)
        
        with col3:
            rarest_badge = max(earned_badges, key=lambda x: ["common", "uncommon", "rare", "epic", "legendary"].index(self.badges[x]['rarity'])) if earned_badges else None
            rarest_rarity = self.badges[rarest_badge]['rarity'].title() if rarest_badge else "None"
            st.metric("Rarest Badge", rarest_rarity)
        
        # Rarity distribution chart
        if any(rarity_counts.values()):
            st.markdown("**Badge Rarity Distribution**")
            rarity_cols = st.columns(5)
            
            for i, (rarity, count) in enumerate(rarity_counts.items()):
                style = self.rarity_styles[rarity]
                with rarity_cols[i]:
                    st.markdown(f"""
                    <div style="
                        background: {style['color']}20;
                        border: 2px solid {style['color']};
                        border-radius: 10px;
                        padding: 10px;
                        text-align: center;
                        margin: 2px;
                    ">
                        <h3 style="color: {style['color']}; margin: 0;">{count}</h3>
                        <p style="margin: 0; font-size: 0.8em;">{rarity.title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def check_badge_requirements(self, progress_data: Dict[str, Any]) -> List[str]:
        """Check if any new badges should be awarded."""
        badge_data = st.session_state.badge_data
        earned_badges = badge_data.get('earned_badges', [])
        new_badges = []
        
        for badge_id, badge in self.badges.items():
            if badge_id not in earned_badges:
                if self._meets_requirement(badge['requirement'], progress_data):
                    new_badges.append(badge_id)
        
        return new_badges
    
    def _meets_requirement(self, requirement: Dict[str, Any], progress_data: Dict[str, Any]) -> bool:
        """Check if a specific requirement is met."""
        req_type = requirement['type']
        
        if req_type == 'total_challenges':
            return progress_data.get('challenges_completed', 0) >= requirement['count']
        
        elif req_type == 'skill_level':
            skill = requirement['skill']
            return progress_data.get('skill_progress', {}).get(skill, 0) >= requirement['level']
        
        elif req_type == 'skill_challenges':
            # This would need to be tracked separately in a real implementation
            skill = requirement['skill']
            return progress_data.get('skill_progress', {}).get(skill, 0) >= requirement['count'] * 10
        
        elif req_type == 'challenge_type':
            # This would need challenge type tracking
            return progress_data.get('challenges_completed', 0) >= requirement['count']
        
        elif req_type == 'streak':
            return progress_data.get('streak_days', 0) >= requirement['days']
        
        elif req_type == 'all_skills':
            skill_progress = progress_data.get('skill_progress', {})
            return all(level >= requirement['level'] for level in skill_progress.values())
        
        elif req_type == 'first_challenge':
            return progress_data.get('challenges_completed', 0) >= 1
        
        return False
    
    def award_badge(self, badge_id: str) -> bool:
        """Award a badge to the user."""
        badge_data = st.session_state.badge_data
        
        if badge_id not in badge_data['earned_badges']:
            badge_data['earned_badges'].append(badge_id)
            badge_data['recent_badges'].append(badge_id)
            
            # Keep only last 10 recent badges
            badge_data['recent_badges'] = badge_data['recent_badges'][-10:]
            
            badge = self.badges[badge_id]
            badge_data['total_badge_xp'] += badge['xp_reward']
            
            # Show award notification
            rarity_style = self.rarity_styles[badge['rarity']]
            st.success(f"🏅 **Badge Earned!** {badge['icon']} {badge['name']} (+{badge['xp_reward']} XP)")
            
            if badge['rarity'] in ['epic', 'legendary']:
                st.balloons()
            
            return True
        
        return False

# Global instance
achievement_system = AchievementBadgeSystem()
