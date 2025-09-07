"""
MEGA Personality Dashboard Integration
Personality analysis section for the benchmarking dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
import json
from datetime import datetime

from personality_models import PersonalityProfile, HEXACOModel, load_personality_profile
from personality_analyzer import PersonalityAnalyzer, create_analyzer_with_fallback
from personality_processor import PersonalityProcessor, run_personality_analysis
from personality_visualizer import PersonalityVisualizer, render_personality_overview, render_personality_comparison
from thesis_colors import THESIS_COLORS, get_color_palette

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalityDashboard:
    """
    Main personality analysis dashboard section
    Integrates with existing benchmarking dashboard
    """
    
    def __init__(self):
        """Initialize personality dashboard components"""
        self.visualizer = PersonalityVisualizer()
        self.processor = PersonalityProcessor()
        self.colors = THESIS_COLORS
        
        # Paths for personality data
        self.results_dir = Path("benchmarking/results/personality_reports")
        self.viz_dir = Path("benchmarking/results/personality_visualizations")
        
        # Create directories if they don't exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir.mkdir(parents=True, exist_ok=True)
    
    def check_personality_data_availability(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if personality analysis data is available
        
        Returns:
            (data_available, status_info)
        """
        status = {
            'has_profiles': False,
            'num_profiles': 0,
            'has_summary': False,
            'analyzer_available': False,
            'last_analysis': None,
            'issues': []
        }
        
        # Check if personality profiles exist
        if self.results_dir.exists():
            profile_files = list(self.results_dir.glob("session_*_personality.json"))
            status['num_profiles'] = len(profile_files)
            status['has_profiles'] = len(profile_files) > 0
            
            # Check for summary file
            summary_file = self.results_dir / "personality_summary_all_sessions.json"
            status['has_summary'] = summary_file.exists()
            
            if status['has_summary']:
                try:
                    with open(summary_file, 'r') as f:
                        summary_data = json.load(f)
                    status['last_analysis'] = summary_data.get('analysis_timestamp')
                except Exception as e:
                    status['issues'].append(f"Could not read summary file: {e}")
        
        # Check if analyzer is available
        try:
            analyzer = create_analyzer_with_fallback()
            status['analyzer_available'] = analyzer.is_available or analyzer.use_fallback
        except Exception as e:
            status['issues'].append(f"Analyzer initialization failed: {e}")
        
        data_available = status['has_profiles'] and status['num_profiles'] > 0
        return data_available, status
    
    def load_personality_profiles(self) -> List[PersonalityProfile]:
        """Load all available personality profiles"""
        profiles = []
        
        if not self.results_dir.exists():
            logger.warning("Personality results directory not found")
            return profiles
        
        profile_files = list(self.results_dir.glob("session_*_personality.json"))
        
        for file_path in profile_files:
            try:
                profile = load_personality_profile(file_path)
                if profile:
                    profiles.append(profile)
            except Exception as e:
                logger.error(f"Failed to load profile {file_path}: {e}")
        
        # Sort by session ID
        profiles.sort(key=lambda p: p.session_id)
        
        logger.info(f"Loaded {len(profiles)} personality profiles")
        return profiles
    
    def render_personality_analysis_section(self):
        """Main rendering function for personality analysis section"""
        st.markdown("# Personality Analysis")
        st.markdown("---")
        
        # Check data availability
        data_available, status = self.check_personality_data_availability()
        
        # Status information
        st.markdown("### Analysis Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_text = "Available" if data_available else "Not Available"
            st.metric("Data Available", f"{status_text}: {status['num_profiles']} profiles")
        
        with col2:
            analyzer_text = "Available" if status['analyzer_available'] else "Not Available"
            st.metric("Analyzer Status", analyzer_text)
        
        with col3:
            if status['last_analysis']:
                last_analysis = datetime.fromisoformat(status['last_analysis'])
                days_ago = (datetime.now() - last_analysis).days
                st.metric("Last Analysis", f"{days_ago} days ago")
            else:
                st.metric("Last Analysis", "Never")
        
        # Run analysis section
        st.markdown("### Run Personality Analysis")
        st.markdown("Generate personality analysis for all available sessions.")
        
        if st.button("Run Personality Analysis", type="primary"):
            self._run_personality_analysis_with_progress()
        
        # Main analysis display
        if data_available:
            self._render_personality_dashboard_tabs()
        else:
            st.info("No personality analysis data available. Run the analysis above to generate insights.")
    
    def _run_personality_analysis_with_progress(self):
        """Run personality analysis with progress tracking"""
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing personality analysis...")
            progress_bar.progress(10)
            
            # Find sessions
            session_files = self.processor.find_session_files()
            total_sessions = len(session_files)
            
            if total_sessions == 0:
                st.error("No session files found in thesis_data directory")
                return
            
            status_text.text(f"Found {total_sessions} sessions to analyze...")
            progress_bar.progress(20)
            
            # Process sessions
            profiles = []
            for i, (session_id, files) in enumerate(session_files.items()):
                status_text.text(f"Analyzing session {session_id} ({i+1}/{total_sessions})...")
                progress = 20 + int((i / total_sessions) * 60)
                progress_bar.progress(progress)
                
                profile = self.processor.process_single_session(session_id, files)
                if profile:
                    profiles.append(profile)
                    self.processor.save_personality_profile(profile)
            
            status_text.text("Generating summary and correlations...")
            progress_bar.progress(85)
            
            # Save batch summary
            if profiles:
                self.processor.save_batch_summary(profiles)
                self.processor.correlate_with_cognitive_metrics(profiles)
                self.processor.validate_data_quality(profiles)
            
            status_text.text("Analysis complete!")
            progress_bar.progress(100)
            
            # Success message
            if profiles:
                st.success(f"Successfully analyzed {len(profiles)} sessions!")
                
                # Show quick summary
                dominant_traits = {}
                for profile in profiles:
                    for trait in profile.dominant_traits[:2]:
                        dominant_traits[trait] = dominant_traits.get(trait, 0) + 1
                
                if dominant_traits:
                    most_common = max(dominant_traits.items(), key=lambda x: x[1])
                    st.info(f"Most common dominant trait: **{most_common[0].replace('_', ' ').title()}** ({most_common[1]} sessions)")
            else:
                st.warning("Analysis completed but no valid profiles were generated. Check data quality.")
            
            # Force refresh
            st.rerun()
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            logger.error(f"Personality analysis failed: {e}")
    
    def _render_personality_dashboard_tabs(self):
        """Render the complete personality analysis dashboard in a single scrollable view"""
        profiles = self.load_personality_profiles()
        
        if not profiles:
            st.warning("No personality profiles found")
            return
        
        # Render all content in a single scrollable view
        self._render_personality_overview_tab(profiles)
        self._render_trait_evolution_tab(profiles)
        self._render_combined_preferences_and_correlations_tab(profiles)
    
    def _render_personality_overview_tab(self, profiles: List[PersonalityProfile]):
        """Render personality overview tab"""
        st.markdown("### Overall Personality Analysis Summary")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", len(profiles))
        
        with col2:
            avg_reliability = np.mean([p.reliability_score for p in profiles])
            st.metric("Avg Reliability", f"{avg_reliability:.2f}")
        
        with col3:
            total_text = sum(p.text_length for p in profiles)
            st.metric("Total Text Analyzed", f"{total_text:,} chars")
        
        with col4:
            high_confidence = sum(1 for p in profiles if p.reliability_score > 0.7)
            st.metric("High Confidence", f"{high_confidence}/{len(profiles)}")
        
        st.markdown("---")
        
        # Overview charts and visualizations - 3 Column Layout
        st.markdown("### Personality Analysis Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Average HEXACO Profile")
            avg_profile = self._calculate_average_profile(profiles)
            radar_chart = self.visualizer.create_hexaco_radar_chart(avg_profile)
            st.plotly_chart(radar_chart, use_container_width=True, key="personality_overview_radar")
        
        with col2:
            st.markdown("#### Trait Distribution Across Sessions")
            distribution_chart = self._create_trait_distribution_chart(profiles)
            st.plotly_chart(distribution_chart, use_container_width=True, key="personality_overview_distribution")
        
        with col3:
            st.markdown("#### Session Reliability Overview")
            reliability_chart = self._create_reliability_overview_chart(profiles)
            st.plotly_chart(reliability_chart, use_container_width=True, key="personality_overview_reliability")
        
        # Trait correlation heatmap (full width below)
        if len(profiles) >= 3:
            st.markdown("---")
            st.markdown("#### Trait Correlation Heatmap")
            correlation_chart = self.visualizer.create_trait_correlation_heatmap(profiles)
            st.plotly_chart(correlation_chart, use_container_width=True, key="personality_overview_heatmap")
        
        st.markdown("---")
        
        # Session selector for detailed view
        st.markdown("### Individual User Personality Profile")
        st.markdown("Select a session to view detailed personality analysis for system improvement and user-specific adaptation.")
        
        # Create session options with clear session ID and timestamp
        session_options = []
        for p in profiles:
            # Try to get original session timestamp, not analysis timestamp
            original_timestamp = None
            
            # Method 1: Extract from session_id if it contains timestamp (YYYYMMDD_HHMMSS)
            import re
            timestamp_match = re.search(r'(\d{8}_\d{6})', p.session_id)
            if timestamp_match:
                try:
                    from datetime import datetime
                    timestamp_str = timestamp_match.group(1)
                    original_timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except:
                    pass
            
            # Method 2: Look for corresponding session file in thesis_data
            if not original_timestamp:
                session_file_patterns = [
                    f"thesis_data/session_{p.session_id}.json",
                    f"thesis_data/session_unified_session_{p.session_id}.json"
                ]
                for pattern in session_file_patterns:
                    session_file = Path(pattern)
                    if session_file.exists():
                        try:
                            import json
                            with open(session_file, 'r') as f:
                                session_data = json.load(f)
                            if 'start_time' in session_data:
                                original_timestamp = datetime.fromisoformat(session_data['start_time'].replace('Z', '+00:00'))
                                break
                        except:
                            continue
            
            # Method 3: Fallback to analysis timestamp
            if not original_timestamp and hasattr(p, 'timestamp') and p.timestamp:
                try:
                    if isinstance(p.timestamp, str):
                        original_timestamp = datetime.fromisoformat(p.timestamp.replace('Z', '+00:00'))
                    else:
                        original_timestamp = p.timestamp
                except:
                    pass
            
            # Format the display - clean and confident
            if original_timestamp:
                formatted_time = original_timestamp.strftime("%Y-%m-%d %H:%M")
                session_display = f"{p.session_id} | {formatted_time}"
            else:
                session_display = p.session_id
            
            session_options.append(session_display)
        
        selected_option = st.selectbox("Select session for detailed analysis:", session_options)
        
        if selected_option:
            # Parse session_id from the new format: "session_id | timestamp | Reliability: label"
            session_id = selected_option.split(" | ")[0] if " | " in selected_option else selected_option.split(" (")[0]
            selected_profile = next((p for p in profiles if p.session_id == session_id), None)
            
            if selected_profile:
                self._render_detailed_personality_profile(selected_profile)
    
    def _calculate_average_profile(self, profiles: List[PersonalityProfile]) -> PersonalityProfile:
        """Calculate average personality profile across all sessions"""
        if not profiles:
            return None
        
        # Calculate average traits
        avg_traits = {}
        trait_names = list(profiles[0].traits.keys())
        
        for trait in trait_names:
            trait_scores = [p.traits.get(trait, 0.5) for p in profiles if trait in p.traits]
            if trait_scores:
                avg_traits[trait] = np.mean(trait_scores)
            else:
                avg_traits[trait] = 0.5
        
        # Calculate average levels
        avg_levels = {}
        for trait, score in avg_traits.items():
            if score > 0.6:
                avg_levels[trait] = 'high'
            elif score > 0.4:
                avg_levels[trait] = 'medium'
            else:
                avg_levels[trait] = 'low'
        
        # Create average profile
        avg_profile = PersonalityProfile(
            session_id="Average_All_Sessions",
            traits=avg_traits,
            levels=avg_levels,
            confidence={trait: 1.0 for trait in trait_names},
            text_length=sum(p.text_length for p in profiles),
            analysis_method="Aggregate",
            reliability_score=np.mean([p.reliability_score for p in profiles])
        )
        
        return avg_profile
    
    def _render_detailed_personality_profile(self, profile: PersonalityProfile):
        """Render detailed personality profile for individual user"""
        st.markdown("---")
        st.markdown(f"## User Profile: {profile.session_id}")
        
        # Basic profile info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Analysis Reliability", f"{profile.reliability_score:.2f}")
        
        with col2:
            st.metric("Text Length", f"{profile.text_length:,} chars")
        
        with col3:
            st.metric("Analysis Method", profile.analysis_method)
        
        # Personality analysis results
        st.markdown("### HEXACO Personality Traits Analysis")
        
        # Display traits in two columns
        col1, col2 = st.columns(2)
        
        trait_details = {
            'honesty_humility': {
                'name': 'Honesty-Humility',
                'description': 'Measures sincerity, fairness, greed-avoidance, and modesty in interactions.',
                'low': 'Tends to be manipulative, greedy, entitled, and boastful in approach.',
                'medium': 'Shows balanced fairness and moderate modesty in interactions.',
                'high': 'Demonstrates sincerity, fairness, modesty, and genuine altruistic behavior.'
            },
            'emotionality': {
                'name': 'Emotionality', 
                'description': 'Assesses fearfulness, anxiety, dependence, and sentimentality.',
                'low': 'Appears fearless, independent, tough, and emotionally detached.',
                'medium': 'Displays balanced emotional responses with moderate sensitivity.',
                'high': 'Shows sensitivity, anxiety, sentimentality, dependence, and fearfulness.'
            },
            'extraversion': {
                'name': 'Extraversion',
                'description': 'Evaluates social self-esteem, boldness, sociability, and liveliness.',
                'low': 'Tends to be shy, quiet, reserved, and prefers solitude.',
                'medium': 'Socially balanced, comfortable in small group interactions.',
                'high': 'Demonstrates outgoing, confident, sociable, energetic, and bold behavior.'
            },
            'agreeableness': {
                'name': 'Agreeableness',
                'description': 'Measures forgiveness, gentleness, flexibility, and patience.',
                'low': 'Tends to be critical, stubborn, demanding, and quick to anger.',
                'medium': 'Shows reasonable cooperation with selective forgiveness.',
                'high': 'Displays forgiving, gentle, flexible, patient, and cooperative nature.'
            },
            'conscientiousness': {
                'name': 'Conscientiousness',
                'description': 'Assesses organization, diligence, perfectionism, and prudence.',
                'low': 'Appears disorganized, impulsive, careless, and procrastinating.',
                'medium': 'Shows moderate organization and general reliability.',
                'high': 'Demonstrates high organization, diligence, perfectionism, and discipline.'
            },
            'openness': {
                'name': 'Openness to Experience',
                'description': 'Evaluates aesthetic appreciation, inquisitiveness, creativity, and unconventionality.',
                'low': 'Prefers conventional, practical, traditional approaches and routine.',
                'medium': 'Shows moderate curiosity with selective creativity.',
                'high': 'Displays creativity, imagination, curiosity, unconventional and artistic thinking.'
            }
        }
        
        traits_left = ['honesty_humility', 'emotionality', 'extraversion']
        traits_right = ['agreeableness', 'conscientiousness', 'openness']
        
        with col1:
            for trait in traits_left:
                if trait in profile.traits:
                    self._display_trait_analysis(profile, trait, trait_details[trait])
        
        with col2:
            for trait in traits_right:
                if trait in profile.traits:
                    self._display_trait_analysis(profile, trait, trait_details[trait])
        
        # Session Analysis Charts - 3 Column Layout
        st.markdown("### Comprehensive Session Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### HEXACO Radar Chart")
            radar_chart = self._create_individual_hexaco_radar(profile)
            st.plotly_chart(radar_chart, use_container_width=True, key=f"individual_radar_{profile.session_id}")
        
        with col2:
            st.markdown("#### Trait Confidence Levels")
            confidence_chart = self._create_confidence_bar_chart(profile)
            st.plotly_chart(confidence_chart, use_container_width=True, key=f"confidence_{profile.session_id}")
        
        with col3:
            st.markdown("#### Personality Balance")
            balance_chart = self._create_personality_balance_chart(profile)
            st.plotly_chart(balance_chart, use_container_width=True, key=f"balance_{profile.session_id}")
        
        # System improvement recommendations
        st.markdown("### System Adaptation Recommendations")
        self._generate_adaptation_recommendations(profile)
    
    def _display_trait_analysis(self, profile: PersonalityProfile, trait: str, trait_info: dict):
        """Display detailed analysis for a single trait"""
        score = profile.traits.get(trait, 0.5)
        level = profile.levels.get(trait, 'medium')
        confidence = profile.confidence.get(trait, 0.5)
        
        # Trait header
        st.markdown(f"#### {trait_info['name']}")
        
        # Score and level
        st.markdown(f"**Score**: {score:.3f} | **Level**: {level.title()} | **Confidence**: {confidence:.2f}")
        
        # Visual asset display
        asset_path = self._get_trait_asset_path(trait, level)
        if asset_path and asset_path.exists():
            st.image(str(asset_path), use_container_width=True, caption=f"{trait_info['name']} - {level.title()}")
        
        # Description
        st.markdown(f"**Description**: {trait_info['description']}")
        
        # Level-specific explanation
        level_desc = trait_info.get(level, 'No description available')
        st.markdown(f"**Analysis**: {level_desc}")
        
        st.markdown("---")
    
    def _generate_adaptation_recommendations(self, profile: PersonalityProfile):
        """Generate system adaptation recommendations based on personality profile"""
        recommendations = []
        
        # Analyze dominant traits for recommendations
        for trait in profile.dominant_traits[:3]:
            level = profile.levels.get(trait, 'medium')
            
            if trait == 'openness':
                if level == 'high':
                    recommendations.append("Provide more creative and unconventional design challenges.")
                    recommendations.append("Introduce experimental materials and innovative approaches.")
                elif level == 'low':
                    recommendations.append("Focus on practical, proven design methodologies.")
                    recommendations.append("Provide clear, structured design processes.")
            
            elif trait == 'conscientiousness':
                if level == 'high':
                    recommendations.append("Offer detailed, systematic design frameworks.")
                    recommendations.append("Provide comprehensive planning tools and checklists.")
                elif level == 'low':
                    recommendations.append("Break complex tasks into smaller, manageable steps.")
                    recommendations.append("Provide additional organization and planning support.")
            
            elif trait == 'extraversion':
                if level == 'high':
                    recommendations.append("Encourage collaborative design sessions and group work.")
                    recommendations.append("Provide social learning opportunities and peer interaction.")
                elif level == 'low':
                    recommendations.append("Offer individual work options and quiet reflection time.")
                    recommendations.append("Provide self-paced learning with minimal social pressure.")
            
            elif trait == 'agreeableness':
                if level == 'high':
                    recommendations.append("Emphasize collaborative and community-serving design approaches.")
                    recommendations.append("Focus on sustainable and ethically responsible design solutions.")
                elif level == 'low':
                    recommendations.append("Provide clear justification for design decisions and requirements.")
                    recommendations.append("Allow for critical analysis and questioning of design approaches.")
            
            elif trait == 'emotionality':
                if level == 'high':
                    recommendations.append("Provide supportive, low-stress learning environment.")
                    recommendations.append("Offer additional guidance and reassurance during complex tasks.")
                elif level == 'low':
                    recommendations.append("Present challenging, high-stakes design problems.")
                    recommendations.append("Encourage independent problem-solving with minimal guidance.")
        
        # Display recommendations
        if recommendations:
            st.markdown("**Recommended System Adaptations:**")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        else:
            st.markdown("**Balanced personality profile** - standard system configuration recommended.")
    
    def _create_individual_hexaco_radar(self, profile: PersonalityProfile):
        """Create a HEXACO radar chart for individual personality profile"""
        import plotly.graph_objects as go
        import numpy as np
        
        # HEXACO traits in order for radar chart
        traits = ['honesty_humility', 'emotionality', 'extraversion', 'agreeableness', 'conscientiousness', 'openness']
        trait_labels = ['Honesty-Humility', 'Emotionality', 'eXtraversion', 'Agreeableness', 'Conscientiousness', 'Openness']
        
        # Get scores for each trait
        scores = []
        for trait in traits:
            score = profile.traits.get(trait, 0.5)
            scores.append(score * 100)  # Convert to percentage for better visualization
        
        # Close the radar chart by repeating the first value
        scores.append(scores[0])
        trait_labels.append(trait_labels[0])
        
        # Create figure
        fig = go.Figure()
        
        # Add the personality profile trace
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=trait_labels,
            fill='toself',
            fillcolor=f'rgba({int(self.colors["primary_violet"][1:3], 16)}, {int(self.colors["primary_violet"][3:5], 16)}, {int(self.colors["primary_violet"][5:7], 16)}, 0.3)',
            line=dict(color=self.colors["primary_violet"], width=2),
            marker=dict(color=self.colors["primary_violet"], size=8),
            name=f'Profile {profile.session_id[:8]}...',
            hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}%<extra></extra>'
        ))
        
        # Update layout to match the example style
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(255, 255, 255, 0)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showline=False,
                    gridcolor=self.colors['neutral_light'],
                    gridwidth=1,
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    tickfont=dict(size=10, color=self.colors['primary_dark'])
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color=self.colors['primary_dark'], family='Arial'),
                    linecolor=self.colors['neutral_light'],
                    gridcolor=self.colors['neutral_light']
                )
            ),
            showlegend=False,
            title=dict(
                text=f"<b>HEXACO Personality Profile</b><br><sub>Session: {profile.session_id[:12]}...</sub>",
                font=dict(size=16, color=self.colors['primary_dark'], family='Arial'),
                x=0.5,
                xanchor='center'
            ),
            font=dict(family='Arial'),
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            width=500,
            height=500
        )
        
        return fig
    
    def _create_confidence_bar_chart(self, profile: PersonalityProfile):
        """Create a horizontal bar chart showing confidence levels for each trait"""
        import plotly.graph_objects as go
        
        # Get traits and confidence scores
        traits = ['honesty_humility', 'emotionality', 'extraversion', 'agreeableness', 'conscientiousness', 'openness']
        trait_labels = ['Honesty-Humility', 'Emotionality', 'eXtraversion', 'Agreeableness', 'Conscientiousness', 'Openness']
        
        confidences = []
        colors = []
        for trait in traits:
            confidence = profile.confidence.get(trait, 0.5) * 100
            confidences.append(confidence)
            
            # Color code by confidence level
            if confidence >= 70:
                colors.append(self.colors['primary_violet'])  # High confidence
            elif confidence >= 50:
                colors.append(self.colors['primary_rose'])    # Medium confidence  
            else:
                colors.append(self.colors['neutral_orange'])  # Low confidence
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=trait_labels,
            x=confidences,
            orientation='h',
            marker=dict(color=colors, line=dict(color=self.colors['primary_dark'], width=1)),
            text=[f'{c:.1f}%' for c in confidences],
            textposition='inside',
            textfont=dict(color='white', size=10, family='Arial'),
            hovertemplate='<b>%{y}</b><br>Confidence: %{x:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Analysis Confidence</b>",
                font=dict(size=14, color=self.colors['primary_dark'], family='Arial'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Confidence Level (%)",
                range=[0, 100],
                showgrid=True,
                gridcolor=self.colors['neutral_light'],
                tickfont=dict(size=10, color=self.colors['primary_dark'])
            ),
            yaxis=dict(
                tickfont=dict(size=10, color=self.colors['primary_dark'])
            ),
            showlegend=False,
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            font=dict(family='Arial'),
            height=400,
            margin=dict(l=20, r=20, t=60, b=40)
        )
        
        return fig
    
    def _create_personality_balance_chart(self, profile: PersonalityProfile):
        """Create a donut chart showing personality balance (high vs medium vs low traits)"""
        import plotly.graph_objects as go
        
        # Count traits by level
        level_counts = {'high': 0, 'medium': 0, 'low': 0}
        for level in profile.levels.values():
            level_counts[level] += 1
        
        # Create data for donut chart
        labels = []
        values = []
        colors = []
        
        if level_counts['high'] > 0:
            labels.append(f'High Traits ({level_counts["high"]})')
            values.append(level_counts['high'])
            colors.append(self.colors['primary_violet'])
        
        if level_counts['medium'] > 0:
            labels.append(f'Medium Traits ({level_counts["medium"]})')
            values.append(level_counts['medium'])
            colors.append(self.colors['primary_rose'])
        
        if level_counts['low'] > 0:
            labels.append(f'Low Traits ({level_counts["low"]})')
            values.append(level_counts['low'])
            colors.append(self.colors['neutral_orange'])
        
        # Calculate reliability score color
        reliability = profile.reliability_score
        if reliability >= 0.7:
            reliability_color = self.colors['primary_violet']
            reliability_text = "High"
        elif reliability >= 0.5:
            reliability_color = self.colors['primary_rose']
            reliability_text = "Medium"
        else:
            reliability_color = self.colors['neutral_orange']
            reliability_text = "Low"
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color=self.colors['primary_dark'], width=1)),
            textinfo='label+percent',
            textfont=dict(size=10, color=self.colors['primary_dark'], family='Arial'),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        ))
        
        # Add center text showing reliability
        fig.add_annotation(
            text=f"<b>Reliability</b><br>{reliability_text}<br>({reliability:.2f})",
            x=0.5, y=0.5,
            font=dict(size=12, color=reliability_color, family='Arial'),
            showarrow=False,
            align='center'
        )
        
        fig.update_layout(
            title=dict(
                text="<b>Trait Distribution</b>",
                font=dict(size=14, color=self.colors['primary_dark'], family='Arial'),
                x=0.5,
                xanchor='center'
            ),
            showlegend=False,
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            font=dict(family='Arial'),
            height=400,
            margin=dict(l=20, r=20, t=60, b=40)
        )
        
        return fig
    
    def _create_trait_distribution_chart(self, profiles: List[PersonalityProfile]):
        """Create a stacked bar chart showing distribution of trait levels across all sessions"""
        import plotly.graph_objects as go
        import numpy as np
        
        # HEXACO traits
        traits = ['honesty_humility', 'emotionality', 'extraversion', 'agreeableness', 'conscientiousness', 'openness']
        trait_labels = ['Honesty-Humility', 'Emotionality', 'eXtraversion', 'Agreeableness', 'Conscientiousness', 'Openness']
        
        # Count levels for each trait across all sessions
        level_counts = {trait: {'low': 0, 'medium': 0, 'high': 0} for trait in traits}
        
        for profile in profiles:
            for trait in traits:
                level = profile.levels.get(trait, 'low')
                level_counts[trait][level] += 1
        
        # Create stacked bar chart
        fig = go.Figure()
        
        # Add bars for each level
        fig.add_trace(go.Bar(
            name='High',
            x=trait_labels,
            y=[level_counts[trait]['high'] for trait in traits],
            marker_color=self.colors['primary_violet'],
            hovertemplate='<b>%{x}</b><br>High: %{y} sessions<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name='Medium',
            x=trait_labels,
            y=[level_counts[trait]['medium'] for trait in traits],
            marker_color=self.colors['primary_rose'],
            hovertemplate='<b>%{x}</b><br>Medium: %{y} sessions<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name='Low',
            x=trait_labels,
            y=[level_counts[trait]['low'] for trait in traits],
            marker_color=self.colors['neutral_orange'],
            hovertemplate='<b>%{x}</b><br>Low: %{y} sessions<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Trait Level Distribution</b>",
                font=dict(size=14, color=self.colors['primary_dark'], family='Arial'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=10, color=self.colors['primary_dark'])
            ),
            yaxis=dict(
                title="Number of Sessions",
                tickfont=dict(size=10, color=self.colors['primary_dark'])
            ),
            barmode='stack',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10, color=self.colors['primary_dark'])
            ),
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            font=dict(family='Arial'),
            height=400,
            margin=dict(l=40, r=20, t=80, b=100)
        )
        
        return fig
    
    def _create_reliability_overview_chart(self, profiles: List[PersonalityProfile]):
        """Create a scatter plot showing reliability scores and text lengths for all sessions"""
        import plotly.graph_objects as go
        
        # Extract data for plotting
        reliability_scores = [p.reliability_score for p in profiles]
        text_lengths = [p.text_length for p in profiles]
        session_labels = [f"Session {p.session_id[:8]}..." for p in profiles]
        
        # Color code by reliability level
        colors = []
        for score in reliability_scores:
            if score >= 0.7:
                colors.append(self.colors['primary_violet'])
            elif score >= 0.5:
                colors.append(self.colors['primary_rose'])
            else:
                colors.append(self.colors['neutral_orange'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=text_lengths,
            y=reliability_scores,
            mode='markers',
            marker=dict(
                size=10,
                color=colors,
                line=dict(color=self.colors['primary_dark'], width=1),
                opacity=0.8
            ),
            text=session_labels,
            hovertemplate='<b>%{text}</b><br>Text Length: %{x} chars<br>Reliability: %{y:.3f}<extra></extra>',
            showlegend=False
        ))
        
        # Add reliability thresholds
        fig.add_hline(y=0.7, line_dash="dash", line_color=self.colors['primary_violet'], 
                      annotation_text="High Reliability", annotation_position="bottom right")
        fig.add_hline(y=0.5, line_dash="dash", line_color=self.colors['primary_rose'],
                      annotation_text="Medium Reliability", annotation_position="bottom right")
        
        fig.update_layout(
            title=dict(
                text="<b>Session Quality Overview</b>",
                font=dict(size=14, color=self.colors['primary_dark'], family='Arial'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Text Length (characters)",
                tickfont=dict(size=10, color=self.colors['primary_dark']),
                showgrid=True,
                gridcolor=self.colors['neutral_light']
            ),
            yaxis=dict(
                title="Reliability Score",
                range=[0, 1],
                tickfont=dict(size=10, color=self.colors['primary_dark']),
                showgrid=True,
                gridcolor=self.colors['neutral_light']
            ),
            paper_bgcolor='rgba(255, 255, 255, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            font=dict(family='Arial'),
            height=400,
            margin=dict(l=60, r=20, t=60, b=60)
        )
        
        return fig
    
    def _get_trait_asset_path(self, trait: str, level: str) -> Optional[Path]:
        """
        Get the correct asset path for a trait and level combination
        Maps trait names to the actual file naming convention
        """
        # Asset directory
        assets_dir = Path("assets/personality_features")
        
        # Map internal trait names to file naming convention
        trait_file_mapping = {
            'honesty_humility': 'honesty_humility',
            'emotionality': 'emotionality', 
            'extraversion': 'extraversion',
            'agreeableness': 'agreeableness',
            'conscientiousness': 'conscientiousness',
            'openness': 'openness'
        }
        
        # Get the file name component for the trait
        file_trait_name = trait_file_mapping.get(trait, trait)
        
        # Construct filename: hexaco_{trait}_{level}.png
        filename = f"hexaco_{file_trait_name}_{level}.png"
        asset_path = assets_dir / filename
        
        return asset_path if asset_path.exists() else None
    
    def _render_trait_evolution_tab(self, profiles: List[PersonalityProfile]):
        """Render trait evolution over sessions tab"""
        st.markdown("### Personality Trait Evolution")
        
        if len(profiles) < 2:
            st.info("Need at least 2 sessions to show evolution")
            return
        
        # Evolution comparison chart
        st.plotly_chart(self.visualizer.create_personality_comparison(profiles), use_container_width=True, key="trait_evolution_comparison")
        
        # Trait statistics table
        st.markdown("### Trait Statistics Across Sessions")
        
        trait_stats = []
        trait_names = list(self.visualizer.trait_display_names.keys())
        
        for trait in trait_names:
            scores = [p.traits.get(trait, 0.5) for p in profiles if trait in p.traits]
            if scores:
                trait_stats.append({
                    'Trait': self.visualizer.trait_display_names[trait],
                    'Mean': f"{np.mean(scores):.3f}",
                    'Std Dev': f"{np.std(scores):.3f}",
                    'Min': f"{np.min(scores):.3f}",
                    'Max': f"{np.max(scores):.3f}",
                    'Sessions': len(scores)
                })
        
        if trait_stats:
            df_stats = pd.DataFrame(trait_stats)
            st.dataframe(df_stats, use_container_width=True)
    
    def _render_visual_correlations_tab(self, profiles: List[PersonalityProfile]):
        """Render visual correlations tab with PNG assets"""
        st.markdown("### Personality Visual Representations")
        
        # Session selector
        session_options = [f"Session {p.session_id}" for p in profiles]
        selected_session = st.selectbox("Select session:", session_options, key="visual_session")
        
        if selected_session:
            session_id = selected_session.replace("Session ", "")
            selected_profile = next((p for p in profiles if p.session_id == session_id), None)
            
            if selected_profile:
                # Display visual assets
                self.visualizer.display_personality_assets(selected_profile)
        
        # Trait correlations heatmap
        if len(profiles) >= 3:
            st.markdown("### Trait Correlation Heatmap")
            st.plotly_chart(self.visualizer.create_trait_correlation_heatmap(profiles), use_container_width=True, key="visual_correlations_heatmap")
    
    def _render_architectural_preferences_tab(self, profiles: List[PersonalityProfile]):
        """Render architectural preferences analysis tab"""
        st.markdown("### Architectural Design Preferences")
        
        # This would correlate personality traits with design patterns
        # For now, show conceptual analysis
        
        st.markdown("""
        #### Personality-Design Correlations (Conceptual)
        
        Based on personality psychology research, different personality traits 
        are associated with different design preferences:
        """)
        
        # Show trait-preference associations
        trait_preferences = {
            'Openness to Experience': [
                'Innovative and unconventional designs',
                'Experimental materials and forms',
                'Abstract and artistic elements'
            ],
            'Conscientiousness': [
                'Systematic and organized layouts', 
                'Functional and efficient designs',
                'Detail-oriented planning approaches'
            ],
            'eXtraversion': [
                'Public and social spaces emphasis',
                'Bold and attention-grabbing features',
                'Community-centered design thinking'
            ],
            'Agreeableness': [
                'Collaborative design processes',
                'Sustainable and ethical considerations',
                'Universal accessibility focus'
            ],
            'Emotionality': [
                'Comfort and safety prioritization',
                'Natural and calming environments',
                'Personal and intimate spaces'
            ],
            'Honesty-Humility': [
                'Modest and community-serving designs',
                'Resource-efficient solutions',
                'Environmentally responsible choices'
            ]
        }
        
        # Display preferences for each trait
        for trait_name, preferences in trait_preferences.items():
            st.markdown(f"#### {trait_name} Design Preferences")
            for pref in preferences:
                st.markdown(f"• {pref}")
            st.markdown("")  # Add spacing
        
        # Show session-specific insights
        if profiles:
            st.markdown("### Session-Specific Design Insights")
            
            for profile in profiles[:3]:  # Show first 3 sessions
                st.markdown(f"#### Session {profile.session_id} Design Profile")
                dominant = profile.dominant_traits[:2] if profile.dominant_traits else []
                
                if dominant:
                    st.markdown("**Predicted Design Preferences:**")
                    for trait in dominant:
                        trait_name = self.visualizer.trait_display_names.get(trait, trait)
                        if trait_name in trait_preferences:
                            for pref in trait_preferences[trait_name]:
                                st.markdown(f"• {pref}")
                else:
                    st.markdown("*Balanced personality profile - flexible design approach*")
                st.markdown("")  # Add spacing between sessions
    
    def _render_cognitive_correlations_tab(self, profiles: List[PersonalityProfile]):
        """Render cognitive correlations analysis tab"""
        st.markdown("### Personality-Cognitive Correlations")
        
        # Load correlation data if available
        corr_file = self.results_dir / "personality_cognitive_correlations.json"
        
        if corr_file.exists():
            try:
                with open(corr_file, 'r') as f:
                    corr_data = json.load(f)
                
                st.markdown(f"**Last Analysis:** {corr_data.get('timestamp', 'Unknown')}")
                
                if 'insights' in corr_data and corr_data['insights']:
                    st.markdown("#### Key Insights")
                    for insight in corr_data['insights']:
                        st.markdown(f"• {insight}")
                
            except Exception as e:
                logger.error(f"Failed to load correlation data: {e}")
                st.error("Could not load correlation analysis")
        else:
            st.info("Correlation analysis not yet available. Run personality analysis to generate.")
        
        # Conceptual correlations display
        st.markdown("#### Expected Personality-Cognitive Correlations")
        
        expected_correlations = {
            'Cognitive Offloading Prevention': [
                'High Conscientiousness → Better self-regulation',
                'High Openness → More independent exploration',
                'High Agreeableness → May rely more on guidance'
            ],
            'Deep Thinking Engagement': [
                'High Openness → Greater curiosity and exploration',
                'High Conscientiousness → Systematic analysis',
                'High Emotionality → May affect focus under pressure'
            ],
            'Scaffolding Effectiveness': [
                'High Agreeableness → Better response to guidance',
                'Low Extraversion → May prefer structured support',
                'High Openness → May want less constraining scaffolds'
            ],
            'Knowledge Integration': [
                'High Conscientiousness → Better systematic integration',
                'High Openness → More creative connections',
                'Low Honesty-Humility → May overconfident in integration'
            ]
        }
        
        for metric, correlations in expected_correlations.items():
            st.markdown(f"##### {metric}")
            for corr in correlations:
                st.markdown(f"• {corr}")
            st.markdown("")  # Add spacing
        
        # Scatter plot for trait relationships
        if len(profiles) >= 5:
            st.markdown("#### Trait Relationship Analysis")
            
            # Create DataFrame for analysis
            data = []
            for profile in profiles:
                row = {'session_id': profile.session_id}
                row.update(profile.traits)
                row['reliability'] = profile.reliability_score
                data.append(row)
            
            df = pd.DataFrame(data)
            
            if not df.empty:
                fig = self.visualizer.create_proficiency_personality_scatter(df)
                st.plotly_chart(fig, use_container_width=True, key="cognitive_correlations_scatter")
    
    def _render_combined_preferences_and_correlations_tab(self, profiles: List[PersonalityProfile]):
        """Render architectural preferences, design insights, and cognitive correlations in three columns"""
        st.markdown("### Design Preferences and Cognitive Correlations Analysis")
        
        # Create three columns for side-by-side display with animated headers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Title first
            st.markdown("#### Architectural Design Preferences")
            # Add animated GIF header
            gif_path = Path("assets/Design_Preferences_and_Cognitive_Correlations_Analysis/Architectural_Design_Preferences.gif")
            if gif_path.exists():
                st.image(str(gif_path), use_container_width=True)
            # Content after GIF
            self._render_architectural_preferences_content(profiles)
        
        with col2:
            # Title first
            st.markdown("#### Session-Specific Design Insights")
            # Add animated GIF header
            gif_path = Path("assets/Design_Preferences_and_Cognitive_Correlations_Analysis/Session_Specific_Design_Insights.gif")
            if gif_path.exists():
                st.image(str(gif_path), use_container_width=True)
            # Content after GIF
            self._render_session_design_insights_content(profiles)
        
        with col3:
            # Title first
            st.markdown("#### Personality-Cognitive Correlations")
            # Add animated GIF header
            gif_path = Path("assets/Design_Preferences_and_Cognitive_Correlations_Analysis/Personality_Cognitive_Correlations.gif")
            if gif_path.exists():
                st.image(str(gif_path), use_container_width=True)
            # Content after GIF
            self._render_cognitive_correlations_content(profiles)
    
    def _render_architectural_preferences_content(self, profiles: List[PersonalityProfile]):
        """Render architectural preferences content only (without title)"""
        
        # Trait-preference associations
        trait_preferences = {
            'Openness to Experience': [
                'Innovative and unconventional designs',
                'Experimental materials and forms',
                'Abstract and artistic elements'
            ],
            'Conscientiousness': [
                'Systematic and organized layouts', 
                'Functional and efficient designs',
                'Detail-oriented planning approaches'
            ],
            'eXtraversion': [
                'Public and social spaces emphasis',
                'Bold and attention-grabbing features',
                'Community-centered design thinking'
            ],
            'Agreeableness': [
                'Collaborative design processes',
                'Sustainable and ethical considerations',
                'Universal accessibility focus'
            ],
            'Emotionality': [
                'Comfort and safety prioritization',
                'Natural and calming environments',
                'Personal and intimate spaces'
            ],
            'Honesty-Humility': [
                'Modest and community-serving designs',
                'Resource-efficient solutions',
                'Environmentally responsible choices'
            ]
        }
        
        # Display preferences for each trait
        for trait_name, preferences in trait_preferences.items():
            st.markdown(f"**{trait_name}**")
            for pref in preferences:
                st.markdown(f"• {pref}")
            st.markdown("")  # Add spacing
    
    def _render_session_design_insights_content(self, profiles: List[PersonalityProfile]):
        """Render session-specific design insights content only (without title)"""
        
        if profiles:
            for profile in profiles[:3]:  # Show first 3 sessions
                st.markdown(f"**Session {profile.session_id[:8]}...**")
                dominant = profile.dominant_traits[:2] if profile.dominant_traits else []
                
                if dominant:
                    st.markdown("*Predicted Design Preferences:*")
                    for trait in dominant:
                        trait_name = self.visualizer.trait_display_names.get(trait, trait)
                        # Get preferences based on trait
                        trait_preferences = {
                            'Openness to Experience': ['Innovative designs', 'Experimental materials'],
                            'Conscientiousness': ['Systematic layouts', 'Functional designs'],
                            'eXtraversion': ['Social spaces', 'Bold features'],
                            'Agreeableness': ['Collaborative processes', 'Sustainable solutions'],
                            'Emotionality': ['Comfort prioritization', 'Calming environments'],
                            'Honesty-Humility': ['Modest designs', 'Resource-efficient solutions']
                        }
                        if trait_name in trait_preferences:
                            for pref in trait_preferences[trait_name]:
                                st.markdown(f"• {pref}")
                else:
                    st.markdown("*Balanced profile - flexible approach*")
                st.markdown("")  # Add spacing between sessions
        else:
            st.markdown("No session data available")
    
    def _render_cognitive_correlations_content(self, profiles: List[PersonalityProfile]):
        """Render cognitive correlations content only (without title)"""
        
        # Load correlation data if available
        corr_file = self.results_dir / "personality_cognitive_correlations.json"
        
        if corr_file.exists():
            try:
                with open(corr_file, 'r') as f:
                    corr_data = json.load(f)
                
                st.markdown(f"**Last Analysis:** {corr_data.get('timestamp', 'Unknown')}")
                
                if 'insights' in corr_data and corr_data['insights']:
                    st.markdown("**Key Insights**")
                    for insight in corr_data['insights']:
                        st.markdown(f"• {insight}")
                
            except Exception as e:
                logger.error(f"Failed to load correlation data: {e}")
                st.error("Could not load correlation analysis")
        else:
            st.info("Correlation analysis not yet available.")
        
        # Expected correlations display (condensed)
        st.markdown("**Expected Correlations**")
        
        expected_correlations = {
            'Cognitive Offloading': [
                'High Conscientiousness → Better self-regulation',
                'High Openness → Independent exploration'
            ],
            'Deep Thinking': [
                'High Openness → Greater curiosity',
                'High Conscientiousness → Systematic analysis'
            ],
            'Scaffolding': [
                'High Agreeableness → Better guidance response',
                'Low Extraversion → Prefers structured support'
            ],
            'Integration': [
                'High Conscientiousness → Systematic integration',
                'High Openness → Creative connections'
            ]
        }
        
        for metric, correlations in expected_correlations.items():
            st.markdown(f"**{metric}**")
            for corr in correlations:
                st.markdown(f"• {corr}")
            st.markdown("")  # Add spacing

def render_personality_analysis():
    """
    Main function to render personality analysis section
    This function is called from the main dashboard
    """
    try:
        dashboard = PersonalityDashboard()
        dashboard.render_personality_analysis_section()
    except Exception as e:
        st.error(f"Failed to render personality analysis: {str(e)}")
        logger.error(f"Dashboard rendering error: {e}")
        
        # Provide fallback information
        st.markdown("""
        ### Personality Analysis Unavailable
        
        The personality analysis feature encountered an error. This might be due to:
        
        • Missing personality analysis dependencies
        • No interaction data available for analysis
        • Configuration or file system issues
        
        Please check the analysis status above and try running the personality analysis.
        """)

# Export main functions
__all__ = [
    'PersonalityDashboard',
    'render_personality_analysis'
]