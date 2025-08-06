"""
MEGA Architectural Mentor - Linkography Visualization
Interactive visualization components for linkography analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import streamlit as st

from benchmarking.linkography_types import Linkograph, DesignMove, LinkographLink, LinkographPattern
from benchmarking.thesis_colors import (
    THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS, 
    PLOTLY_COLORSCALES, get_color_palette, get_metric_color
)


class LinkographVisualizer:
    """Create interactive visualizations for linkography analysis"""
    
    def __init__(self):
        self.colors = THESIS_COLORS
        self.metric_colors = METRIC_COLORS
        
    def create_triangular_linkograph(self, 
                                   linkograph: Linkograph,
                                   highlight_patterns: Optional[List[LinkographPattern]] = None,
                                   interactive: bool = True) -> go.Figure:
        """
        Create the traditional triangular linkograph visualization.
        
        Args:
            linkograph: The linkograph to visualize
            highlight_patterns: Optional patterns to highlight
            interactive: Whether to enable interactivity
            
        Returns:
            Plotly figure object
        """
        moves = linkograph.moves
        links = linkograph.links
        n_moves = len(moves)
        
        # Create figure
        fig = go.Figure()
        
        # Calculate positions for triangular layout
        move_positions = []
        for i, move in enumerate(moves):
            x = i
            y = 0
            move_positions.append((x, y))
        
        # Add links as lines below the moves
        for link in links:
            source_idx = next(i for i, m in enumerate(moves) if m.id == link.source_move)
            target_idx = next(i for i, m in enumerate(moves) if m.id == link.target_move)
            
            if source_idx == target_idx:
                continue
                
            # Calculate arc for the link
            mid_x = (source_idx + target_idx) / 2
            mid_y = -abs(target_idx - source_idx) * 0.5  # Arc depth based on distance
            
            # Color based on link strength
            link_color = self._get_link_color(link.strength)
            
            # Add link arc
            fig.add_trace(go.Scatter(
                x=[source_idx, mid_x, target_idx],
                y=[0, mid_y, 0],
                mode='lines',
                line=dict(
                    color=link_color,
                    width=max(1, link.strength * 3),
                    shape='spline'
                ),
                hovertemplate=f'Link: {link.source_move[:8]} → {link.target_move[:8]}<br>' +
                             f'Strength: {link.strength:.2f}<br>' +
                             f'Type: {link.link_type}<br>' +
                             f'Distance: {link.temporal_distance}<extra></extra>',
                showlegend=False,
                opacity=0.7
            ))
        
        # Add moves as dots
        move_colors = [self._get_phase_color(move.phase) for move in moves]
        move_sizes = []
        move_texts = []
        
        for move in moves:
            # Size based on connectivity
            source_links, target_links = linkograph.get_links_for_move(move.id)
            connectivity = len(source_links) + len(target_links)
            size = 8 + connectivity * 2
            move_sizes.append(size)
            
            # Hover text
            move_texts.append(
                f'Move {move.id[:8]}<br>' +
                f'Phase: {move.phase}<br>' +
                f'Type: {move.move_type}<br>' +
                f'Connections: {connectivity}<br>' +
                f'Content: {move.content[:50]}...'
            )
        
        fig.add_trace(go.Scatter(
            x=[pos[0] for pos in move_positions],
            y=[pos[1] for pos in move_positions],
            mode='markers+text',
            marker=dict(
                size=move_sizes,
                color=move_colors,
                line=dict(color=self.colors['primary_dark'], width=1)
            ),
            text=[f'{i}' for i in range(n_moves)],
            textposition='top center',
            hovertext=move_texts,
            hoverinfo='text',
            showlegend=False
        ))
        
        # Highlight patterns if provided
        if highlight_patterns:
            for pattern in highlight_patterns:
                self._highlight_pattern(fig, pattern, moves)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="Linkograph: Design Process Visualization",
                font=dict(size=20, color=self.colors['primary_dark'])
            ),
            xaxis=dict(
                title="Design Moves (Temporal Sequence)",
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                title="Link Depth",
                showgrid=False,
                zeroline=True,
                autorange='reversed'  # Links go down
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest' if interactive else False,
            height=600,
            dragmode='pan' if interactive else False,
            template='plotly_white'  # Force white theme
        )
        
        # Add phase annotations
        self._add_phase_annotations(fig, moves)
        
        return fig
    
    def create_link_density_heatmap(self, linkograph: Linkograph) -> go.Figure:
        """Create a heatmap showing link density across the design process"""
        moves = linkograph.moves
        n_moves = len(moves)
        
        # Handle edge case for small linkographs
        if n_moves < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="Not enough moves for density analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=300)
            return fig
        
        window_size = max(2, min(5, n_moves // 10))  # Adaptive window size with better bounds
        
        # Calculate link density for windows
        densities = []
        positions = []
        
        # Ensure we have at least one window
        if n_moves < window_size:
            window_size = n_moves
        
        for i in range(0, n_moves - window_size + 1):
            window_moves = moves[i:i + window_size]
            window_ids = [m.id for m in window_moves]
            
            # Count links in window
            window_links = [
                link for link in linkograph.links
                if link.source_move in window_ids or link.target_move in window_ids
            ]
            
            density = len(window_links) / window_size
            densities.append(density)
            positions.append(i + window_size // 2)
        
        # Create heatmap data
        if not densities:
            # If no densities calculated, create a simple visualization
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for density heatmap",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            fig.update_layout(height=300)
            return fig
        
        heatmap_data = []
        for i, density in enumerate(densities):
            heatmap_data.append([density] * 10)  # Make it wider for visibility
        
        fig = go.Figure(data=go.Heatmap(
            z=np.array(heatmap_data).T,
            x=positions,
            y=list(range(10)),
            colorscale=PLOTLY_COLORSCALES['main'],
            showscale=True,
            colorbar=dict(
                title="Link<br>Density"
            ),
            hovertemplate='Move Position: %{x}<br>Link Density: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Link Density Throughout Design Process",
            xaxis_title="Design Move Position",
            yaxis=dict(showticklabels=False, title=""),
            height=300
        )
        
        return fig
    
    def create_phase_transition_sankey(self, linkograph: Linkograph) -> go.Figure:
        """Create a Sankey diagram showing phase transitions"""
        moves = linkograph.moves
        
        # Track phase transitions
        transitions = {'ideation': {}, 'visualization': {}, 'materialization': {}}
        
        for i in range(len(moves) - 1):
            current_phase = moves[i].phase
            next_phase = moves[i + 1].phase
            
            if current_phase in transitions:
                if next_phase not in transitions[current_phase]:
                    transitions[current_phase][next_phase] = 0
                transitions[current_phase][next_phase] += 1
        
        # Build Sankey data
        labels = ['Ideation (Start)', 'Visualization (Start)', 'Materialization (Start)',
                  'Ideation (End)', 'Visualization (End)', 'Materialization (End)']
        
        source = []
        target = []
        value = []
        colors = []
        
        phase_map = {
            'ideation': (0, 3),
            'visualization': (1, 4),
            'materialization': (2, 5)
        }
        
        for from_phase, to_dict in transitions.items():
            for to_phase, count in to_dict.items():
                if count > 0:
                    source.append(phase_map[from_phase][0])
                    target.append(phase_map[to_phase][1])
                    value.append(count)
                    colors.append(self._get_phase_color(from_phase))
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color=self.colors['primary_dark'], width=0.5),
                label=labels,
                color=[
                    self._get_phase_color('ideation'),
                    self._get_phase_color('visualization'),
                    self._get_phase_color('materialization'),
                    self._get_phase_color('ideation'),
                    self._get_phase_color('visualization'),
                    self._get_phase_color('materialization')
                ]
            ),
            textfont=dict(color="black", size=14, family="Arial"),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=[self._hex_to_rgba(c, 0.25) for c in colors]  # Add transparency
            )
        )])
        
        fig.update_layout(
            title="Design Phase Transitions",
            height=400
        )
        
        return fig
    
    def create_critical_moves_timeline(self, linkograph: Linkograph) -> go.Figure:
        """Create a timeline highlighting critical moves"""
        moves = linkograph.moves
        critical_moves = linkograph.get_critical_moves(threshold=0.1)
        critical_ids = [m.id for m in critical_moves]
        
        # Create timeline data
        timeline_data = []
        
        for i, move in enumerate(moves):
            source_links, target_links = linkograph.get_links_for_move(move.id)
            connectivity = len(source_links) + len(target_links)
            
            timeline_data.append({
                'position': i,
                'phase': move.phase,
                'type': move.move_type,
                'connectivity': connectivity,
                'is_critical': move.id in critical_ids,
                'content': move.content[:50] + '...'
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Create figure
        fig = go.Figure()
        
        # Check if dataframe is empty
        if df.empty:
            fig.add_annotation(
                text="No design moves to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # USE THE EXACT SAME COLORS AS BACKGROUND REGIONS
        # From _get_phase_color method:
        phase_colors = {
            'ideation': self.colors['accent_coral'],      # Coral
            'visualization': self.colors['neutral_orange'], # Orange
            'materialization': self.colors['primary_violet'] # Violet
        }
        
        # Add regular moves grouped by phase for legend
        for phase in ['ideation', 'visualization', 'materialization']:
            phase_regular = df[(df['phase'] == phase) & (df['is_critical'] == False)]
            if not phase_regular.empty:
                fig.add_trace(go.Scatter(
                    x=phase_regular['position'],
                    y=phase_regular['connectivity'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=phase_colors[phase],  # Use exact phase color
                        line=dict(width=1, color='white')
                    ),
                    text=phase_regular['content'],
                    hovertemplate='Move %{x}<br>Connections: %{y}<br>%{text}<extra></extra>',
                    name=f'{phase.capitalize()} - Regular',
                    legendgroup=phase
                ))
        
        # Add critical moves grouped by phase  
        for phase in ['ideation', 'visualization', 'materialization']:
            phase_critical = df[(df['phase'] == phase) & (df['is_critical'] == True)]
            if not phase_critical.empty:
                fig.add_trace(go.Scatter(
                    x=phase_critical['position'],
                    y=phase_critical['connectivity'],
                    mode='markers',
                    marker=dict(
                        size=16,
                        color=phase_colors[phase],  # SAME color as regular but bigger
                        symbol='circle',
                        line=dict(width=2, color=self.colors['primary_dark'])
                    ),
                    text=phase_critical['content'],
                    hovertemplate='CRITICAL MOVE %{x}<br>Connections: %{y}<br>%{text}<extra></extra>',
                    name=f'{phase.capitalize()} - Critical',
                    legendgroup=phase
                ))
        
        # Add phase regions with labels
        self._add_phase_regions_with_labels(fig, moves)
        
        fig.update_layout(
            title="Critical Moves and Connectivity Timeline",
            xaxis_title="Design Move Sequence",
            yaxis_title="Number of Connections",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_pattern_analysis_chart(self, patterns: List[LinkographPattern]) -> go.Figure:
        """Create a chart showing detected patterns and their implications"""
        if not patterns:
            return go.Figure().add_annotation(
                text="No patterns detected",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Aggregate patterns by type
        pattern_counts = {}
        pattern_strengths = {}
        
        for pattern in patterns:
            ptype = pattern.pattern_type
            if ptype not in pattern_counts:
                pattern_counts[ptype] = 0
                pattern_strengths[ptype] = []
            pattern_counts[ptype] += 1
            pattern_strengths[ptype].append(pattern.strength)
        
        # Create subplot figure
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Pattern Distribution", "Average Pattern Strength"),
            specs=[[{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Pie chart for pattern distribution
        labels = list(pattern_counts.keys())
        values = list(pattern_counts.values())
        colors = [self._get_pattern_color(label) for label in labels]
        
        fig.add_trace(
            go.Pie(
                labels=[l.capitalize() for l in labels],
                values=values,
                hole=0.3,
                marker_colors=colors,
                textinfo='label+percent'
            ),
            row=1, col=1
        )
        
        # Bar chart for average strengths
        avg_strengths = [np.mean(strengths) for strengths in pattern_strengths.values()]
        
        fig.add_trace(
            go.Bar(
                x=[l.capitalize() for l in labels],
                y=avg_strengths,
                marker_color=colors,
                text=[f'{s:.2f}' for s in avg_strengths],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Linkographic Pattern Analysis",
            showlegend=False,
            height=400
        )
        
        fig.update_yaxes(title_text="Average Strength", row=1, col=2)
        
        return fig
    
    def create_cognitive_mapping_radar(self, 
                                     cognitive_mapping: Dict[str, float],
                                     baseline: Optional[Dict[str, float]] = None) -> go.Figure:
        """Create a radar chart showing cognitive metric mappings"""
        categories = [
            'Deep Thinking\nEngagement',
            'Cognitive Offloading\nPrevention',
            'Scaffolding\nEffectiveness',
            'Knowledge\nIntegration',
            'Learning\nProgression',
            'Metacognitive\nAwareness'
        ]
        
        fig = go.Figure()
        
        # Add linkography-based metrics
        values = [
            cognitive_mapping.get('deep_thinking_engagement', 0),
            cognitive_mapping.get('cognitive_offloading_prevention', 0),
            cognitive_mapping.get('scaffolding_effectiveness', 0),
            cognitive_mapping.get('knowledge_integration', 0),
            cognitive_mapping.get('learning_progression', 0),
            cognitive_mapping.get('metacognitive_awareness', 0)
        ]
        
        # Convert hex color to rgba for fillcolor
        violet_color = self.colors['primary_violet']
        # Extract RGB values from hex
        r = int(violet_color[1:3], 16)
        g = int(violet_color[3:5], 16)
        b = int(violet_color[5:7], 16)
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Linkography Analysis',
            line_color=self.colors['primary_violet'],
            fillcolor=f'rgba({r},{g},{b},0.25)'
        ))
        
        # Add baseline if provided
        if baseline:
            baseline_values = [
                baseline.get('deep_thinking_engagement', 0),
                baseline.get('cognitive_offloading_prevention', 0),
                baseline.get('scaffolding_effectiveness', 0),
                baseline.get('knowledge_integration', 0),
                baseline.get('learning_progression', 0),
                baseline.get('metacognitive_awareness', 0)
            ]
            
            # Convert hex color to rgba for baseline fillcolor
            orange_color = self.colors['neutral_orange']
            # Extract RGB values from hex
            r_base = int(orange_color[1:3], 16)
            g_base = int(orange_color[3:5], 16)
            b_base = int(orange_color[5:7], 16)
            
            fig.add_trace(go.Scatterpolar(
                r=baseline_values,
                theta=categories,
                fill='toself',
                name='Baseline',
                line_color=self.colors['neutral_orange'],
                fillcolor=f'rgba({r_base},{g_base},{b_base},0.25)'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0]
                )
            ),
            showlegend=True,
            title="Cognitive Metrics from Linkography",
            height=500
        )
        
        return fig
    
    def create_move_embeddings_scatter(self, linkograph: Linkograph) -> go.Figure:
        """Create a 2D scatter plot of move embeddings using PCA/TSNE"""
        from sklearn.decomposition import PCA
        
        moves = linkograph.moves
        embeddings = [move.embedding for move in moves if move.embedding is not None]
        
        if len(embeddings) < 2:
            return go.Figure().add_annotation(
                text="Not enough embeddings for visualization",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Reduce dimensions
        embeddings_array = np.array(embeddings)
        pca = PCA(n_components=2)
        coords = pca.fit_transform(embeddings_array)
        
        # Create scatter plot
        fig = go.Figure()
        
        # Group by phase
        phase_groups = {}
        for i, move in enumerate(moves[:len(embeddings)]):
            if move.phase not in phase_groups:
                phase_groups[move.phase] = {'x': [], 'y': [], 'text': []}
            phase_groups[move.phase]['x'].append(coords[i, 0])
            phase_groups[move.phase]['y'].append(coords[i, 1])
            phase_groups[move.phase]['text'].append(f"{move.content[:30]}...")
        
        # Add traces for each phase
        for phase, data in phase_groups.items():
            fig.add_trace(go.Scatter(
                x=data['x'],
                y=data['y'],
                mode='markers',
                name=phase.capitalize(),
                marker=dict(
                    size=10,
                    color=self._get_phase_color(phase),
                    line=dict(width=1, color=self.colors['primary_dark'])
                ),
                text=data['text'],
                hovertemplate='%{text}<extra></extra>'
            ))
        
        # Add links as lines
        for link in linkograph.links:
            if link.strength > 0.5:  # Only show strong links
                source_idx = next((i for i, m in enumerate(moves) if m.id == link.source_move), None)
                target_idx = next((i for i, m in enumerate(moves) if m.id == link.target_move), None)
                
                if source_idx is not None and target_idx is not None and source_idx < len(coords) and target_idx < len(coords):
                    fig.add_trace(go.Scatter(
                        x=[coords[source_idx, 0], coords[target_idx, 0]],
                        y=[coords[source_idx, 1], coords[target_idx, 1]],
                        mode='lines',
                        line=dict(
                            color=self.colors['neutral_light'],
                            width=link.strength * 2
                        ),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
        fig.update_layout(
            title="Design Move Embeddings (Semantic Space)",
            xaxis_title=f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)",
            yaxis_title=f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)",
            height=500
        )
        
        return fig
    
    # Helper methods
    def _get_link_color(self, strength: float) -> str:
        """Get color for link based on strength"""
        if strength > 0.8:
            return self.colors['primary_dark']
        elif strength > 0.6:
            return self.colors['primary_purple']
        elif strength > 0.4:
            return self.colors['primary_violet']
        else:
            return self.colors['neutral_light']
    
    def _get_phase_color(self, phase: str) -> str:
        """Get color for design phase"""
        phase_colors = {
            'ideation': self.colors['accent_coral'],
            'visualization': self.colors['neutral_orange'],
            'materialization': self.colors['primary_violet']
        }
        return phase_colors.get(phase, self.colors['neutral_warm'])
    
    def _get_pattern_color(self, pattern_type: str) -> str:
        """Get color for pattern type"""
        pattern_colors = {
            'chunk': self.colors['primary_purple'],
            'web': self.colors['primary_violet'],
            'sawtooth': self.colors['neutral_warm'],
            'orphan': self.colors['accent_coral']
        }
        return pattern_colors.get(pattern_type, self.colors['neutral_light'])
    
    def _hex_to_rgba(self, hex_color: str, alpha: float = 0.2) -> str:
        """Convert hex color to rgba format with specified alpha"""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'
    
    def _add_phase_annotations(self, fig: go.Figure, moves: List[DesignMove]):
        """Add phase region annotations to figure"""
        if not moves:
            return
            
        current_phase = moves[0].phase
        phase_start = 0
        
        for i, move in enumerate(moves + [None]):
            if move is None or move.phase != current_phase:
                # Add annotation for completed phase
                fig.add_annotation(
                    x=(phase_start + i - 1) / 2,
                    y=0.5,
                    text=current_phase.capitalize(),
                    showarrow=False,
                    font=dict(color=self._get_phase_color(current_phase), size=14, weight='bold')
                )
                
                if move is not None:
                    current_phase = move.phase
                    phase_start = i
    
    def _add_phase_regions(self, fig: go.Figure, moves: List[DesignMove]):
        """Add colored background regions for phases"""
        if not moves:
            return
            
        current_phase = moves[0].phase
        phase_start = 0
        
        for i, move in enumerate(moves + [None]):
            if move is None or move.phase != current_phase:
                # Add shape for phase region
                fig.add_shape(
                    type="rect",
                    x0=phase_start - 0.5,
                    x1=i - 0.5,
                    y0=0,
                    y1=1,
                    yref="paper",
                    fillcolor=self._get_phase_color(current_phase),
                    opacity=0.1,
                    layer="below",
                    line_width=0
                )
                
                if move is not None:
                    current_phase = move.phase
                    phase_start = i
    
    def _add_phase_regions_with_labels(self, fig: go.Figure, moves: List[DesignMove]):
        """Add colored background regions for phases"""
        if not moves:
            return
            
        current_phase = moves[0].phase
        phase_start = 0
        
        for i, move in enumerate(moves + [None]):
            if move is None or move.phase != current_phase:
                # Add shape for phase region
                fig.add_shape(
                    type="rect",
                    x0=phase_start - 0.5,
                    x1=i - 0.5,
                    y0=0,
                    y1=1,
                    yref="paper",
                    fillcolor=self._get_phase_color(current_phase),
                    opacity=0.1,
                    layer="below",
                    line_width=0
                )
                
                if move is not None:
                    current_phase = move.phase
                    phase_start = i
    
    def _highlight_pattern(self, fig: go.Figure, pattern: LinkographPattern, moves: List[DesignMove]):
        """Highlight a specific pattern in the linkograph"""
        # Find indices of moves in pattern
        pattern_indices = []
        for move_id in pattern.moves:
            idx = next((i for i, m in enumerate(moves) if m.id == move_id), None)
            if idx is not None:
                pattern_indices.append(idx)
        
        if pattern_indices:
            # Add highlighting shape
            fig.add_shape(
                type="rect",
                x0=min(pattern_indices) - 0.5,
                x1=max(pattern_indices) + 0.5,
                y0=-10,
                y1=1,
                fillcolor=self._get_pattern_color(pattern.pattern_type),
                opacity=0.2,
                layer="below",
                line=dict(
                    color=self._get_pattern_color(pattern.pattern_type),
                    width=2,
                    dash="dash"
                )
            )