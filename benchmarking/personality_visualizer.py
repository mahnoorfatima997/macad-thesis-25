"""
MEGA Personality Visualizer
Visualization components for personality analysis using thesis colors
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
import logging

from personality_models import (
    PersonalityProfile, 
    HEXACOModel, 
    PersonalityColorMapper,
    PersonalityAssetMapper
)
from thesis_colors import THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS, CHART_COLORS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalityVisualizer:
    """
    Visualization components for personality analysis
    Follows thesis color scheme and design patterns
    """
    
    def __init__(self):
        """Initialize visualizer with thesis color scheme"""
        self.colors = THESIS_COLORS
        self.metric_colors = METRIC_COLORS
        self.color_mapper = PersonalityColorMapper()
        self.asset_mapper = PersonalityAssetMapper()
        
        # HEXACO trait display names and colors
        self.trait_display_names = {
            'honesty_humility': 'Honesty-Humility',
            'emotionality': 'Emotionality', 
            'extraversion': 'eXtraversion',
            'agreeableness': 'Agreeableness',
            'conscientiousness': 'Conscientiousness',
            'openness': 'Openness to Experience'
        }
        
    def create_hexaco_radar_chart(self, profile: PersonalityProfile) -> go.Figure:
        """
        Create HEXACO radar chart for personality traits
        
        Args:
            profile: PersonalityProfile to visualize
            
        Returns:
            Plotly figure with radar chart
        """
        if not profile.traits:
            logger.warning("No traits data available for radar chart")
            return go.Figure()
        
        # Prepare data for radar chart
        traits = []
        values = []
        colors = []
        
        for trait, score in profile.traits.items():
            traits.append(self.trait_display_names.get(trait, trait.title()))
            values.append(score)
            colors.append(self.color_mapper.get_trait_color(trait))
        
        # Close the radar chart by adding first point at the end
        traits.append(traits[0])
        values.append(values[0])
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=traits,
            fill='toself',
            fillcolor=self.colors['primary_violet'],
            line=dict(color=self.colors['primary_dark'], width=3),
            marker=dict(color=self.colors['primary_dark'], size=8),
            opacity=0.7,
            name=f"Session {profile.session_id}",
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>"
        ))
        
        # Update layout with thesis styling
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickmode='array',
                    tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                    ticktext=['0.2', '0.4', '0.6', '0.8', '1.0'],
                    gridcolor=self.colors['neutral_light'],
                    linecolor=self.colors['neutral_light']
                ),
                angularaxis=dict(
                    gridcolor=self.colors['neutral_light'],
                    linecolor=self.colors['primary_dark'],
                    tickfont=dict(size=12, color=self.colors['primary_dark'])
                )
            ),
            title=dict(
                text=f"HEXACO Personality Profile - Session {profile.session_id}",
                x=0.5,
                font=dict(size=16, color=self.colors['primary_dark'])
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial", color=self.colors['primary_dark']),
            width=500,
            height=500
        )
        
        return fig
    
    def create_trait_bars_chart(self, profile: PersonalityProfile) -> go.Figure:
        """
        Create horizontal bar chart showing trait levels with confidence
        
        Args:
            profile: PersonalityProfile to visualize
            
        Returns:
            Plotly figure with bar chart
        """
        if not profile.traits:
            return go.Figure()
        
        # Prepare data
        traits = []
        scores = []
        levels = []
        confidences = []
        colors = []
        
        for trait, score in profile.traits.items():
            traits.append(self.trait_display_names.get(trait, trait.title()))
            scores.append(score)
            levels.append(profile.levels.get(trait, 'medium'))
            confidences.append(profile.confidence.get(trait, 0.5))
            colors.append(self.color_mapper.get_trait_color(trait))
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=traits,
            x=scores,
            orientation='h',
            marker=dict(
                color=colors,
                opacity=0.8,
                line=dict(color=self.colors['primary_dark'], width=1)
            ),
            text=[f"{level.title()}" for level in levels],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial Bold"),
            hovertemplate="<b>%{y}</b><br>Score: %{x:.3f}<br>Level: %{text}<br>Confidence: %{customdata:.2f}<extra></extra>",
            customdata=confidences,
            name="Personality Traits"
        ))
        
        # Add reference lines for level boundaries
        for threshold in [0.33, 0.66]:
            fig.add_vline(
                x=threshold, 
                line_dash="dash", 
                line_color=self.colors['neutral_warm'],
                opacity=0.5
            )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Personality Trait Levels - Session {profile.session_id}",
                x=0.5,
                font=dict(size=16, color=self.colors['primary_dark'])
            ),
            xaxis=dict(
                title="Trait Score",
                range=[0, 1],
                gridcolor=self.colors['neutral_light'],
                tickfont=dict(color=self.colors['primary_dark'])
            ),
            yaxis=dict(
                title="",
                tickfont=dict(color=self.colors['primary_dark'])
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial", color=self.colors['primary_dark']),
            height=400,
            margin=dict(l=200)
        )
        
        return fig
    
    def create_personality_comparison(self, profiles: List[PersonalityProfile]) -> go.Figure:
        """
        Create comparison chart across multiple sessions
        
        Args:
            profiles: List of PersonalityProfiles to compare
            
        Returns:
            Plotly figure with comparison visualization
        """
        if not profiles:
            return go.Figure()
        
        # Prepare data for comparison - truncate session IDs for readability
        session_ids = [p.session_id[:10] + "..." if len(p.session_id) > 10 else p.session_id for p in profiles]
        trait_names = list(self.trait_display_names.keys())
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[self.trait_display_names[trait] for trait in trait_names],
            specs=[[{"type": "scatter"}] * 3] * 2,
            vertical_spacing=0.35,
            horizontal_spacing=0.08
        )
        
        positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]
        
        for i, trait in enumerate(trait_names):
            if i >= len(positions):
                break
                
            row, col = positions[i]
            
            # Get scores for this trait
            scores = [p.traits.get(trait, 0.5) for p in profiles]
            
            fig.add_trace(
                go.Scatter(
                    x=session_ids,
                    y=scores,
                    mode='lines+markers',
                    line=dict(color=self.color_mapper.get_trait_color(trait), width=3),
                    marker=dict(size=8, color=self.color_mapper.get_trait_color(trait)),
                    name=self.trait_display_names[trait],
                    showlegend=False,
                    hovertemplate="<b>Session %{fullData.customdata[%{pointIndex}]}</b><br>Score: %{y:.3f}<extra></extra>",
                    customdata=[p.session_id for p in profiles]
                ),
                row=row, col=col
            )
            
            # Add level reference lines
            fig.add_hline(y=0.33, line_dash="dash", line_color=self.colors['neutral_warm'], 
                         opacity=0.5, row=row, col=col)
            fig.add_hline(y=0.66, line_dash="dash", line_color=self.colors['neutral_warm'], 
                         opacity=0.5, row=row, col=col)
        
        fig.update_layout(
            title=dict(
                text="Personality Trait Evolution Across Sessions",
                x=0.5,
                font=dict(size=18, color=self.colors['primary_dark'])
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial", color=self.colors['primary_dark']),
            height=800,
            margin=dict(t=80, b=80, l=60, r=60)
        )
        
        # Update all y-axes to same range
        fig.update_yaxes(range=[0, 1])
        
        return fig
    
    def create_trait_correlation_heatmap(self, profiles: List[PersonalityProfile]) -> go.Figure:
        """
        Create heatmap showing correlations between personality traits
        
        Args:
            profiles: List of PersonalityProfiles for correlation analysis
            
        Returns:
            Plotly figure with correlation heatmap
        """
        if len(profiles) < 3:
            logger.warning("Need at least 3 profiles for meaningful correlations")
            return go.Figure()
        
        # Create DataFrame with trait scores
        data = []
        for profile in profiles:
            data.append(profile.traits)
        
        df = pd.DataFrame(data)
        
        if df.empty:
            return go.Figure()
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        # Prepare display names
        display_names = [self.trait_display_names.get(trait, trait) for trait in corr_matrix.columns]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=display_names,
            y=display_names,
            colorscale=[
                [0.0, self.colors['accent_coral']],      # Strong negative
                [0.25, self.colors['primary_pink']],     # Weak negative
                [0.5, self.colors['neutral_light']],     # No correlation
                [0.75, self.colors['primary_violet']],   # Weak positive
                [1.0, self.colors['primary_dark']]       # Strong positive
            ],
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=10),
            hoverongaps=False,
            hovertemplate="<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text="Personality Trait Correlations",
                x=0.5,
                font=dict(size=16, color=self.colors['primary_dark'])
            ),
            paper_bgcolor='white',
            font=dict(family="Arial", color=self.colors['primary_dark']),
            width=600,
            height=500
        )
        
        return fig
    
    def display_personality_assets(self, profile: PersonalityProfile):
        """
        Display PNG assets corresponding to personality levels
        
        Args:
            profile: PersonalityProfile with trait levels
        """
        if not profile.levels:
            st.warning("No personality level data available for asset display")
            return
        
        st.markdown("### 🎨 Personality Visual Representations")
        
        # Get assets for all traits
        assets = self.asset_mapper.get_all_assets_for_profile(profile)
        
        # Display in a grid
        cols = st.columns(3)
        
        trait_list = list(self.trait_display_names.keys())
        
        for i, trait in enumerate(trait_list):
            col_idx = i % 3
            
            with cols[col_idx]:
                trait_name = self.trait_display_names[trait]
                level = profile.levels.get(trait, 'medium')
                score = profile.traits.get(trait, 0.5)
                
                st.markdown(f"**{trait_name}**")
                st.markdown(f"Level: {level.title()} ({score:.2f})")
                
                # Try to display asset
                asset_path = assets.get(trait)
                if asset_path and asset_path.exists():
                    try:
                        st.image(str(asset_path), width=200)
                    except Exception as e:
                        st.error(f"Could not display asset: {e}")
                        st.markdown(f"*{trait_name}: {level.title()}*")
                else:
                    st.markdown(f"*{trait_name}: {level.title()}*")
                    st.markdown(f"*(Asset not found)*")
                
                st.markdown("---")
    
    def create_personality_summary_text(self, profile: PersonalityProfile) -> str:
        """
        Create formatted text summary of personality analysis
        
        Args:
            profile: PersonalityProfile to summarize
            
        Returns:
            Formatted string summary
        """
        if not profile.traits:
            return "No personality data available for analysis."
        
        summary_parts = []
        
        # Header
        summary_parts.append(f"## Personality Analysis Summary - Session {profile.session_id}")
        summary_parts.append("")
        
        # Overall reliability
        reliability_emoji = "🟢" if profile.reliability_score > 0.7 else "🟡" if profile.reliability_score > 0.5 else "🔴"
        summary_parts.append(f"**Analysis Reliability:** {reliability_emoji} {profile.reliability_score:.2f}")
        summary_parts.append(f"**Text Analyzed:** {profile.text_length:,} characters")
        summary_parts.append("")
        
        # Dominant traits
        if profile.dominant_traits:
            dominant_names = [self.trait_display_names.get(trait, trait) for trait in profile.dominant_traits[:3]]
            summary_parts.append(f"**Dominant Traits:** {', '.join(dominant_names)}")
            summary_parts.append("")
        
        # Trait breakdown
        summary_parts.append("### HEXACO Trait Breakdown")
        summary_parts.append("")
        
        for trait, score in profile.traits.items():
            trait_name = self.trait_display_names.get(trait, trait)
            level = profile.levels.get(trait, 'medium')
            confidence = profile.confidence.get(trait, 0.5)
            
            level_emoji = "🔴" if level == "low" else "🟡" if level == "medium" else "🟢"
            
            summary_parts.append(f"**{trait_name}:** {level_emoji} {level.title()} ({score:.2f})")
            summary_parts.append(f"  - *Confidence: {confidence:.2f}*")
            
            # Add trait description
            trait_info = HEXACOModel.get_trait_info(trait)
            if trait_info:
                description = trait_info.get(f"{level}_desc", "")
                if description:
                    summary_parts.append(f"  - *{description}*")
            
            summary_parts.append("")
        
        # Generated summary
        if profile.personality_summary:
            summary_parts.append("### Personality Interpretation")
            summary_parts.append("")
            summary_parts.append(profile.personality_summary)
            summary_parts.append("")
        
        # Analysis metadata
        summary_parts.append("---")
        summary_parts.append(f"*Analysis Method: {profile.analysis_method}*")
        summary_parts.append(f"*Analysis Date: {profile.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(summary_parts)
    
    def create_proficiency_personality_scatter(self, personality_data: pd.DataFrame, 
                                             cognitive_data: Optional[pd.DataFrame] = None) -> go.Figure:
        """
        Create scatter plot correlating personality traits with cognitive proficiency
        
        Args:
            personality_data: DataFrame with personality scores
            cognitive_data: Optional DataFrame with cognitive metrics
            
        Returns:
            Plotly figure with scatter plot
        """
        if personality_data.empty:
            return go.Figure()
        
        # Use openness vs conscientiousness as example
        if 'openness' not in personality_data.columns or 'conscientiousness' not in personality_data.columns:
            return go.Figure()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=personality_data['openness'],
            y=personality_data['conscientiousness'],
            mode='markers',
            marker=dict(
                size=12,
                color=self.colors['primary_violet'],
                opacity=0.7,
                line=dict(color=self.colors['primary_dark'], width=1)
            ),
            text=personality_data.index,
            hovertemplate="<b>Session %{text}</b><br>Openness: %{x:.3f}<br>Conscientiousness: %{y:.3f}<extra></extra>",
            name="Sessions"
        ))
        
        # Add quadrant reference lines
        fig.add_hline(y=0.5, line_dash="dash", line_color=self.colors['neutral_warm'], opacity=0.5)
        fig.add_vline(x=0.5, line_dash="dash", line_color=self.colors['neutral_warm'], opacity=0.5)
        
        fig.update_layout(
            title=dict(
                text="Personality Trait Relationship: Openness vs Conscientiousness",
                x=0.5,
                font=dict(size=16, color=self.colors['primary_dark'])
            ),
            xaxis=dict(
                title="Openness to Experience",
                range=[0, 1],
                gridcolor=self.colors['neutral_light']
            ),
            yaxis=dict(
                title="Conscientiousness", 
                range=[0, 1],
                gridcolor=self.colors['neutral_light']
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial", color=self.colors['primary_dark']),
            width=600,
            height=500
        )
        
        return fig

# Utility functions for Streamlit integration
def render_personality_overview(profile: PersonalityProfile):
    """Render personality overview in Streamlit"""
    visualizer = PersonalityVisualizer()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.plotly_chart(visualizer.create_hexaco_radar_chart(profile), use_container_width=True)
    
    with col2:
        st.plotly_chart(visualizer.create_trait_bars_chart(profile), use_container_width=True)
    
    # Display personality assets
    visualizer.display_personality_assets(profile)
    
    # Text summary
    summary_text = visualizer.create_personality_summary_text(profile)
    st.markdown(summary_text)

def render_personality_comparison(profiles: List[PersonalityProfile]):
    """Render personality comparison in Streamlit"""
    visualizer = PersonalityVisualizer()
    
    if len(profiles) > 1:
        st.plotly_chart(visualizer.create_personality_comparison(profiles), use_container_width=True)
        
        if len(profiles) >= 3:
            st.plotly_chart(visualizer.create_trait_correlation_heatmap(profiles), use_container_width=True)
    else:
        st.info("Need multiple sessions for comparison analysis")

# Export main classes
__all__ = [
    'PersonalityVisualizer',
    'render_personality_overview',
    'render_personality_comparison'
]