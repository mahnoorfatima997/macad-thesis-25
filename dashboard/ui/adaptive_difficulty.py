"""
Adaptive Difficulty Engine for Personalized Learning
Adjusts challenge difficulty based on user performance, learning patterns, and engagement.
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
import numpy as np
from dataclasses import dataclass

@dataclass
class LearningMetrics:
    """Metrics for tracking learning performance."""
    success_rate: float
    average_time: float
    engagement_score: float
    skill_progression: Dict[str, float]
    challenge_preferences: Dict[str, int]
    difficulty_comfort: float

class AdaptiveDifficultyEngine:
    """Engine that adapts challenge difficulty based on user performance."""
    
    def __init__(self):
        self.difficulty_levels = {
            1: {
                "name": "Beginner",
                "description": "Basic concepts with guided support",
                "complexity_multiplier": 0.5,
                "support_level": "high",
                "time_pressure": "none"
            },
            2: {
                "name": "Developing",
                "description": "Intermediate concepts with some guidance",
                "complexity_multiplier": 0.7,
                "support_level": "medium",
                "time_pressure": "low"
            },
            3: {
                "name": "Proficient",
                "description": "Standard architectural challenges",
                "complexity_multiplier": 1.0,
                "support_level": "low",
                "time_pressure": "medium"
            },
            4: {
                "name": "Advanced",
                "description": "Complex multi-layered problems",
                "complexity_multiplier": 1.3,
                "support_level": "minimal",
                "time_pressure": "medium"
            },
            5: {
                "name": "Expert",
                "description": "Professional-level challenges",
                "complexity_multiplier": 1.6,
                "support_level": "none",
                "time_pressure": "high"
            }
        }
        
        self.skill_areas = [
            "spatial_reasoning", "sustainability", "user_experience",
            "technical_systems", "cultural_context", "creative_thinking"
        ]
        
        self.challenge_types = [
            "curiosity_amplification", "constraint_challenge", "perspective_shift",
            "role_play", "spatial_reasoning", "technical_challenge"
        ]
        
        self._initialize_adaptive_state()
    
    def _initialize_adaptive_state(self):
        """Initialize adaptive difficulty tracking."""
        if 'adaptive_difficulty' not in st.session_state:
            st.session_state.adaptive_difficulty = {
                'current_difficulty': 2,  # Start at developing level
                'performance_history': [],
                'skill_assessments': {skill: 2.0 for skill in self.skill_areas},
                'learning_velocity': 1.0,
                'engagement_patterns': {},
                'challenge_success_rates': {},
                'time_spent_patterns': {},
                'preferred_challenge_types': {},
                'last_assessment': datetime.now().isoformat(),
                'adaptation_triggers': []
            }
    
    def get_adaptive_challenge(self, challenge_type: str, skill_area: str) -> Dict[str, Any]:
        """Generate an adaptive challenge based on current user performance."""
        adaptive_data = st.session_state.adaptive_difficulty
        
        # Assess current performance
        current_metrics = self._calculate_current_metrics()
        
        # Determine optimal difficulty
        optimal_difficulty = self._calculate_optimal_difficulty(skill_area, current_metrics)
        
        # Generate challenge with adaptive parameters
        challenge_config = self._generate_challenge_config(
            challenge_type, skill_area, optimal_difficulty
        )
        
        # Log the adaptation decision
        self._log_adaptation_decision(challenge_type, skill_area, optimal_difficulty)
        
        return challenge_config
    
    def _calculate_current_metrics(self) -> LearningMetrics:
        """Calculate current learning metrics from session data."""
        adaptive_data = st.session_state.adaptive_difficulty
        progress_data = st.session_state.get('progress_data', {})
        
        # Calculate success rate from recent performance
        recent_performance = adaptive_data['performance_history'][-10:]  # Last 10 challenges
        success_rate = np.mean([p['success'] for p in recent_performance]) if recent_performance else 0.5
        
        # Calculate average completion time
        recent_times = [p['time_spent'] for p in recent_performance if 'time_spent' in p]
        average_time = np.mean(recent_times) if recent_times else 300  # Default 5 minutes
        
        # Calculate engagement score based on various factors
        engagement_score = self._calculate_engagement_score()
        
        # Get skill progression
        skill_progression = adaptive_data['skill_assessments'].copy()
        
        # Get challenge preferences
        challenge_preferences = adaptive_data['preferred_challenge_types'].copy()
        
        # Calculate difficulty comfort level
        difficulty_comfort = self._calculate_difficulty_comfort()
        
        return LearningMetrics(
            success_rate=success_rate,
            average_time=average_time,
            engagement_score=engagement_score,
            skill_progression=skill_progression,
            challenge_preferences=challenge_preferences,
            difficulty_comfort=difficulty_comfort
        )
    
    def _calculate_engagement_score(self) -> float:
        """Calculate user engagement score based on interaction patterns."""
        adaptive_data = st.session_state.adaptive_difficulty
        
        # Factors that indicate engagement
        factors = []
        
        # Time spent on challenges (not too fast, not too slow)
        recent_times = [p.get('time_spent', 300) for p in adaptive_data['performance_history'][-5:]]
        if recent_times:
            avg_time = np.mean(recent_times)
            # Optimal time range is 2-8 minutes
            time_score = 1.0 - abs(avg_time - 300) / 300  # Normalize around 5 minutes
            factors.append(max(0, min(1, time_score)))
        
        # Variety in challenge types attempted
        challenge_variety = len(adaptive_data['preferred_challenge_types'])
        variety_score = min(challenge_variety / len(self.challenge_types), 1.0)
        factors.append(variety_score)
        
        # Consistency of participation
        performance_history = adaptive_data['performance_history']
        if len(performance_history) > 1:
            # Check if user is consistently engaging
            recent_activity = len([p for p in performance_history[-7:] if p])  # Last week
            consistency_score = min(recent_activity / 7, 1.0)
            factors.append(consistency_score)
        
        # Return average of all factors
        return np.mean(factors) if factors else 0.5
    
    def _calculate_difficulty_comfort(self) -> float:
        """Calculate how comfortable the user is with current difficulty."""
        adaptive_data = st.session_state.adaptive_difficulty
        current_difficulty = adaptive_data['current_difficulty']
        
        # Look at recent performance at current difficulty
        recent_performance = adaptive_data['performance_history'][-5:]
        
        if not recent_performance:
            return 0.5  # Neutral if no data
        
        # Calculate success rate and time efficiency at current level
        success_rate = np.mean([p['success'] for p in recent_performance])
        
        # If success rate is too high (>0.8), user might be ready for harder challenges
        # If success rate is too low (<0.4), user might need easier challenges
        if success_rate > 0.8:
            return min(1.0, success_rate + 0.2)  # Ready for harder
        elif success_rate < 0.4:
            return max(0.0, success_rate - 0.2)  # Needs easier
        else:
            return success_rate  # Current level is appropriate
    
    def _calculate_optimal_difficulty(self, skill_area: str, metrics: LearningMetrics) -> int:
        """Calculate the optimal difficulty level for the user."""
        adaptive_data = st.session_state.adaptive_difficulty
        current_difficulty = adaptive_data['current_difficulty']
        
        # Factors that influence difficulty adjustment
        adjustment_factors = []
        
        # Success rate factor
        if metrics.success_rate > 0.85:
            adjustment_factors.append(0.3)  # Increase difficulty
        elif metrics.success_rate < 0.4:
            adjustment_factors.append(-0.4)  # Decrease difficulty
        else:
            adjustment_factors.append(0)  # Maintain
        
        # Skill-specific performance
        skill_level = metrics.skill_progression.get(skill_area, 2.0)
        if skill_level > current_difficulty + 0.5:
            adjustment_factors.append(0.2)  # User has grown beyond current level
        elif skill_level < current_difficulty - 0.5:
            adjustment_factors.append(-0.2)  # User needs more support
        
        # Engagement factor
        if metrics.engagement_score > 0.8:
            adjustment_factors.append(0.1)  # High engagement, can handle more challenge
        elif metrics.engagement_score < 0.4:
            adjustment_factors.append(-0.2)  # Low engagement, reduce pressure
        
        # Time efficiency factor
        if metrics.average_time < 120:  # Very fast completion
            adjustment_factors.append(0.2)  # Increase challenge
        elif metrics.average_time > 600:  # Very slow completion
            adjustment_factors.append(-0.1)  # Slight reduction
        
        # Calculate adjustment
        total_adjustment = sum(adjustment_factors)
        new_difficulty = current_difficulty + total_adjustment
        
        # Clamp to valid range and round
        optimal_difficulty = max(1, min(5, round(new_difficulty)))
        
        return optimal_difficulty
    
    def _generate_challenge_config(self, challenge_type: str, skill_area: str, difficulty: int) -> Dict[str, Any]:
        """Generate challenge configuration based on adaptive parameters."""
        difficulty_config = self.difficulty_levels[difficulty]
        
        # Base challenge configuration
        config = {
            "challenge_type": challenge_type,
            "skill_area": skill_area,
            "difficulty_level": difficulty,
            "difficulty_name": difficulty_config["name"],
            "complexity_multiplier": difficulty_config["complexity_multiplier"],
            "support_level": difficulty_config["support_level"],
            "time_pressure": difficulty_config["time_pressure"]
        }
        
        # Adaptive modifications based on difficulty
        if difficulty <= 2:  # Beginner/Developing
            config.update({
                "provide_hints": True,
                "show_examples": True,
                "step_by_step_guidance": True,
                "allow_multiple_attempts": True,
                "feedback_frequency": "immediate"
            })
        elif difficulty == 3:  # Proficient
            config.update({
                "provide_hints": True,
                "show_examples": False,
                "step_by_step_guidance": False,
                "allow_multiple_attempts": True,
                "feedback_frequency": "after_completion"
            })
        else:  # Advanced/Expert
            config.update({
                "provide_hints": False,
                "show_examples": False,
                "step_by_step_guidance": False,
                "allow_multiple_attempts": False,
                "feedback_frequency": "minimal"
            })
        
        # Skill-specific adaptations
        config["skill_focus"] = self._get_skill_focus(skill_area, difficulty)
        
        # Challenge-type specific adaptations
        config["challenge_parameters"] = self._get_challenge_parameters(challenge_type, difficulty)
        
        return config
    
    def _get_skill_focus(self, skill_area: str, difficulty: int) -> Dict[str, Any]:
        """Get skill-specific focus areas based on difficulty."""
        skill_focuses = {
            "spatial_reasoning": {
                1: ["basic_2d_relationships", "simple_proportions"],
                2: ["3d_visualization", "scale_understanding"],
                3: ["complex_spatial_relationships", "circulation_planning"],
                4: ["multi_level_coordination", "advanced_geometry"],
                5: ["parametric_relationships", "complex_site_integration"]
            },
            "sustainability": {
                1: ["basic_energy_concepts", "material_awareness"],
                2: ["passive_design_strategies", "water_management"],
                3: ["integrated_systems", "lifecycle_thinking"],
                4: ["advanced_performance", "regenerative_design"],
                5: ["carbon_neutral_design", "circular_economy"]
            },
            "user_experience": {
                1: ["basic_accessibility", "comfort_factors"],
                2: ["wayfinding", "social_spaces"],
                3: ["inclusive_design", "behavioral_patterns"],
                4: ["cultural_sensitivity", "adaptive_environments"],
                5: ["universal_design", "community_engagement"]
            }
        }
        
        return {
            "focus_areas": skill_focuses.get(skill_area, {}).get(difficulty, ["general_concepts"]),
            "depth_level": difficulty,
            "integration_required": difficulty >= 3
        }
    
    def _get_challenge_parameters(self, challenge_type: str, difficulty: int) -> Dict[str, Any]:
        """Get challenge-type specific parameters based on difficulty."""
        base_parameters = {
            "curiosity_amplification": {
                "exploration_depth": difficulty,
                "question_complexity": difficulty * 0.2,
                "connection_requirements": max(1, difficulty - 1)
            },
            "constraint_challenge": {
                "number_of_constraints": min(difficulty + 1, 6),
                "constraint_complexity": difficulty * 0.3,
                "solution_requirements": difficulty
            },
            "perspective_shift": {
                "number_of_perspectives": min(difficulty + 2, 8),
                "perspective_complexity": difficulty * 0.25,
                "synthesis_required": difficulty >= 3
            },
            "role_play": {
                "number_of_stakeholders": min(difficulty + 1, 7),
                "conflict_complexity": difficulty * 0.2,
                "negotiation_required": difficulty >= 4
            }
        }
        
        return base_parameters.get(challenge_type, {"complexity": difficulty * 0.2})
    
    def _log_adaptation_decision(self, challenge_type: str, skill_area: str, difficulty: int):
        """Log the adaptation decision for analysis."""
        adaptive_data = st.session_state.adaptive_difficulty
        
        adaptation_log = {
            "timestamp": datetime.now().isoformat(),
            "challenge_type": challenge_type,
            "skill_area": skill_area,
            "difficulty_assigned": difficulty,
            "previous_difficulty": adaptive_data['current_difficulty'],
            "reason": self._get_adaptation_reason(difficulty, adaptive_data['current_difficulty'])
        }
        
        adaptive_data['adaptation_triggers'].append(adaptation_log)
        
        # Keep only last 20 adaptation decisions
        adaptive_data['adaptation_triggers'] = adaptive_data['adaptation_triggers'][-20:]
        
        # Update current difficulty
        adaptive_data['current_difficulty'] = difficulty
    
    def _get_adaptation_reason(self, new_difficulty: int, old_difficulty: int) -> str:
        """Get human-readable reason for difficulty adaptation."""
        if new_difficulty > old_difficulty:
            return f"Increased difficulty due to strong performance (success rate > 85%)"
        elif new_difficulty < old_difficulty:
            return f"Decreased difficulty due to challenges with current level (success rate < 40%)"
        else:
            return "Maintained difficulty level - performance is appropriate"
    
    def record_challenge_performance(self, challenge_type: str, skill_area: str, 
                                   success: bool, time_spent: float, 
                                   engagement_indicators: Dict[str, Any] = None):
        """Record performance data for adaptive learning."""
        adaptive_data = st.session_state.adaptive_difficulty
        
        performance_record = {
            "timestamp": datetime.now().isoformat(),
            "challenge_type": challenge_type,
            "skill_area": skill_area,
            "difficulty_level": adaptive_data['current_difficulty'],
            "success": success,
            "time_spent": time_spent,
            "engagement_indicators": engagement_indicators or {}
        }
        
        adaptive_data['performance_history'].append(performance_record)
        
        # Keep only last 50 performance records
        adaptive_data['performance_history'] = adaptive_data['performance_history'][-50:]
        
        # Update skill assessment
        self._update_skill_assessment(skill_area, success, time_spent)
        
        # Update challenge preferences
        self._update_challenge_preferences(challenge_type, success, engagement_indicators)
    
    def _update_skill_assessment(self, skill_area: str, success: bool, time_spent: float):
        """Update skill level assessment based on performance."""
        adaptive_data = st.session_state.adaptive_difficulty
        current_level = adaptive_data['skill_assessments'][skill_area]
        
        # Calculate performance score (0-1)
        success_score = 1.0 if success else 0.0
        
        # Time efficiency score (optimal time is around 300 seconds)
        time_score = max(0, 1 - abs(time_spent - 300) / 300)
        
        # Combined performance score
        performance_score = (success_score * 0.7) + (time_score * 0.3)
        
        # Update skill level with exponential moving average
        learning_rate = 0.1
        new_level = current_level + learning_rate * (performance_score * 5 - current_level)
        
        # Clamp to valid range
        adaptive_data['skill_assessments'][skill_area] = max(1.0, min(5.0, new_level))
    
    def _update_challenge_preferences(self, challenge_type: str, success: bool, 
                                    engagement_indicators: Dict[str, Any]):
        """Update challenge type preferences based on performance and engagement."""
        adaptive_data = st.session_state.adaptive_difficulty
        
        if challenge_type not in adaptive_data['preferred_challenge_types']:
            adaptive_data['preferred_challenge_types'][challenge_type] = 0
        
        # Increase preference for successful and engaging challenges
        preference_change = 0
        if success:
            preference_change += 1
        
        # Add engagement bonus
        if engagement_indicators:
            engagement_score = engagement_indicators.get('engagement_score', 0.5)
            if engagement_score > 0.7:
                preference_change += 1
        
        adaptive_data['preferred_challenge_types'][challenge_type] += preference_change
    
    def render_difficulty_dashboard(self):
        """Render the adaptive difficulty dashboard."""
        st.markdown("## 🎯 Adaptive Learning Dashboard")
        
        adaptive_data = st.session_state.adaptive_difficulty
        current_difficulty = adaptive_data['current_difficulty']
        difficulty_info = self.difficulty_levels[current_difficulty]
        
        # Current difficulty display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #3498db20, #3498db40);
                border: 3px solid #3498db;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
            ">
                <h3 style="color: #3498db; margin: 0;">Current Level</h3>
                <h2 style="color: #3498db; margin: 5px 0;">{difficulty_info['name']}</h2>
                <p style="margin: 0;">{difficulty_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Performance metrics
            metrics = self._calculate_current_metrics()
            st.metric("Success Rate", f"{metrics.success_rate:.1%}")
            st.metric("Engagement", f"{metrics.engagement_score:.1%}")
        
        with col3:
            # Learning velocity
            learning_velocity = adaptive_data.get('learning_velocity', 1.0)
            st.metric("Learning Velocity", f"{learning_velocity:.1f}x")
            
            # Next adaptation prediction
            next_difficulty = self._calculate_optimal_difficulty("general", metrics)
            if next_difficulty > current_difficulty:
                st.success("📈 Ready for harder challenges")
            elif next_difficulty < current_difficulty:
                st.info("📉 May benefit from easier challenges")
            else:
                st.success("✅ Current level is optimal")
        
        # Skill progression radar
        self._render_skill_progression_radar()
        
        # Recent adaptations
        self._render_recent_adaptations()
    
    def _render_skill_progression_radar(self):
        """Render skill progression radar chart."""
        st.markdown("### 📊 Skill Progression")
        
        adaptive_data = st.session_state.adaptive_difficulty
        skill_levels = adaptive_data['skill_assessments']
        
        # Create radar chart data
        skills = list(skill_levels.keys())
        values = list(skill_levels.values())
        
        # Simple text-based display for now (could be enhanced with plotly)
        for skill, level in skill_levels.items():
            progress = level / 5.0  # Normalize to 0-1
            skill_name = skill.replace('_', ' ').title()
            
            st.markdown(f"**{skill_name}**")
            st.progress(progress)
            st.caption(f"Level {level:.1f}/5.0")
    
    def _render_recent_adaptations(self):
        """Render recent difficulty adaptations."""
        st.markdown("### 📈 Recent Adaptations")
        
        adaptive_data = st.session_state.adaptive_difficulty
        recent_adaptations = adaptive_data['adaptation_triggers'][-5:]  # Last 5
        
        if recent_adaptations:
            for adaptation in reversed(recent_adaptations):  # Most recent first
                timestamp = datetime.fromisoformat(adaptation['timestamp'])
                time_ago = datetime.now() - timestamp
                
                if time_ago.days > 0:
                    time_str = f"{time_ago.days} days ago"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600} hours ago"
                else:
                    time_str = f"{time_ago.seconds // 60} minutes ago"
                
                difficulty_change = adaptation['difficulty_assigned'] - adaptation['previous_difficulty']
                
                if difficulty_change > 0:
                    icon = "📈"
                    color = "success"
                elif difficulty_change < 0:
                    icon = "📉"
                    color = "info"
                else:
                    icon = "➡️"
                    color = "secondary"
                
                st.markdown(f"""
                {icon} **{adaptation['challenge_type'].replace('_', ' ').title()}** 
                ({adaptation['skill_area'].replace('_', ' ').title()}) - {time_str}
                
                *{adaptation['reason']}*
                """)
        else:
            st.info("No recent adaptations to display.")

# Global instance
adaptive_difficulty = AdaptiveDifficultyEngine()
