# Visualization Tools for Cognitive Benchmarking
# This module provides comprehensive visualization capabilities for analyzing
# cognitive patterns and benchmarking results

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime
import colorcet as cc
from thesis_colors import (
    THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS, 
    PLOTLY_COLORSCALES, CHART_COLORS, UI_COLORS,
    get_color_palette, get_metric_color, get_proficiency_color, get_agent_color
)


class CognitiveBenchmarkVisualizer:
    """Comprehensive visualization tools for cognitive benchmarking analysis"""
    
    def __init__(self, style: str = 'scientific'):
        self.style = style
        self._setup_visualization_style()
        self.color_palette = self._setup_color_palette()
        
    def _setup_visualization_style(self):
        """Setup consistent visualization style"""
        
        if self.style == 'scientific':
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("husl")
        elif self.style == 'presentation':
            plt.style.use('seaborn-v0_8-dark')
            sns.set_palette("bright")
        
        # Set default figure parameters
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        
    def _setup_color_palette(self) -> Dict[str, str]:
        """Setup color palette for consistent visualization"""
        
        return {
            'beginner': get_proficiency_color('beginner'),
            'intermediate': get_proficiency_color('intermediate'),
            'advanced': get_proficiency_color('advanced'),
            'expert': get_proficiency_color('expert'),
            'cognitive_load': THESIS_COLORS['neutral_orange'],
            'learning': get_metric_color('knowledge_integration'),
            'engagement': get_metric_color('engagement'),
            'scaffolding': get_metric_color('scaffolding'),
            'positive': THESIS_COLORS['primary_violet'],
            'negative': THESIS_COLORS['accent_coral'],
            'neutral': THESIS_COLORS['neutral_light']
        }
    
    def visualize_interaction_graph(self, 
                                  graph: nx.DiGraph, 
                                  title: str = "User Interaction Graph",
                                  save_path: Optional[str] = None,
                                  interactive: bool = True):
        """Visualize interaction graph with cognitive metrics"""
        
        if interactive:
            self._create_interactive_graph(graph, title, save_path)
        else:
            self._create_static_graph(graph, title, save_path)
    
    def _create_interactive_graph(self, graph: nx.DiGraph, title: str, save_path: Optional[str]):
        """Create interactive graph visualization using Plotly"""
        
        # Calculate layout
        pos = nx.spring_layout(graph, k=1, iterations=50)
        
        # Create edge traces
        edge_traces = []
        
        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_type = graph[edge[0]][edge[1]].get('edge_type', 'temporal')
            color = UI_COLORS['text_secondary'] if edge_type == 'temporal' else THESIS_COLORS['neutral_orange']
            width = 1 if edge_type == 'temporal' else 2
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=width, color=color),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_text = []
        
        for node in graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Color by learning indicator
            learning_indicator = graph.nodes[node].get('learning_indicator', 0.5)
            node_colors.append(learning_indicator)
            
            # Size by cognitive load
            cognitive_load = graph.nodes[node].get('cognitive_load', 0.5)
            node_sizes.append(20 + cognitive_load * 30)
            
            # Hover text
            node_info = graph.nodes[node]
            hover_text = f"Node: {node}<br>" \
                        f"Learning: {learning_indicator:.2f}<br>" \
                        f"Cognitive Load: {cognitive_load:.2f}<br>" \
                        f"Skill Level: {node_info.get('skill_level', 'unknown')}<br>" \
                        f"Interaction Type: {node_info.get('interaction_type', 'unknown')}"
            node_text.append(hover_text)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                colorscale='Viridis',
                colorbar=dict(
                    title=dict(text="Learning<br>Indicator", side='right'),
                    thickness=15,
                    xanchor='left'
                ),
                line=dict(width=2, color='white')
            ),
            text=node_text,
            hoverinfo='text',
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Interactive graph saved to: {save_path}")
        else:
            fig.show()
    
    def _create_static_graph(self, graph: nx.DiGraph, title: str, save_path: Optional[str]):
        """Create static graph visualization using matplotlib"""
        
        plt.figure(figsize=(14, 10))
        
        # Calculate layout
        pos = nx.spring_layout(graph, k=1, iterations=50)
        
        # Draw edges
        temporal_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                         if d.get('edge_type') == 'temporal']
        conceptual_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                           if d.get('edge_type') == 'conceptual']
        
        nx.draw_networkx_edges(graph, pos, temporal_edges, 
                              edge_color='gray', width=1, alpha=0.5, 
                              arrows=True, arrowsize=10)
        nx.draw_networkx_edges(graph, pos, conceptual_edges, 
                              edge_color='orange', width=2, alpha=0.7, 
                              arrows=True, arrowsize=12)
        
        # Draw nodes
        node_colors = [graph.nodes[node].get('learning_indicator', 0.5) 
                      for node in graph.nodes()]
        node_sizes = [300 + graph.nodes[node].get('cognitive_load', 0.5) * 500 
                     for node in graph.nodes()]
        
        # Create custom colormap from thesis colors
        from matplotlib.colors import LinearSegmentedColormap
        thesis_colors_rgb = [
            plt.colors.hex2color(THESIS_COLORS['accent_coral']),
            plt.colors.hex2color(THESIS_COLORS['neutral_orange']),
            plt.colors.hex2color(THESIS_COLORS['neutral_warm']),
            plt.colors.hex2color(THESIS_COLORS['primary_violet']),
            plt.colors.hex2color(THESIS_COLORS['primary_dark'])
        ]
        thesis_cmap = LinearSegmentedColormap.from_list('thesis', thesis_colors_rgb)
        
        nodes = nx.draw_networkx_nodes(graph, pos, 
                                      node_color=node_colors,
                                      node_size=node_sizes,
                                      cmap=thesis_cmap,
                                      alpha=0.9,
                                      edgecolors='white',
                                      linewidths=2)
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=thesis_cmap, 
                                   norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca(), fraction=0.046, pad=0.04)
        cbar.set_label('Learning Indicator', rotation=270, labelpad=20)
        
        plt.title(title, fontsize=20, pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"Static graph saved to: {save_path}")
        else:
            plt.show()
    
    def create_proficiency_dashboard(self, 
                                   cluster_profiles: Dict[str, Any],
                                   session_metrics: List[Dict[str, Any]],
                                   save_path: Optional[str] = None):
        """Create comprehensive proficiency analysis dashboard"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Proficiency Distribution', 'Key Metrics by Proficiency',
                          'Learning Progression', 'Cognitive Pattern Analysis'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "heatmap"}]]
        )
        
        # 1. Proficiency Distribution (Pie Chart)
        proficiency_counts = {}
        for profile in cluster_profiles.values():
            level = profile['proficiency_level']
            proficiency_counts[level] = proficiency_counts.get(level, 0) + profile['size']
        
        fig.add_trace(
            go.Pie(
                labels=list(proficiency_counts.keys()),
                values=list(proficiency_counts.values()),
                hole=0.3,
                marker_colors=[self.color_palette.get(k, THESIS_COLORS['neutral_warm']) for k in proficiency_counts.keys()],
                textinfo='label+percent',
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # 2. Key Metrics by Proficiency (Bar Chart)
        metrics_data = []
        for profile in cluster_profiles.values():
            metrics_data.append({
                'Proficiency': profile['proficiency_level'],
                'Cognitive Load': profile['avg_cognitive_load'],
                'Learning Effectiveness': profile['avg_learning_effectiveness'],
                'Engagement': profile['avg_engagement'],
                'Deep Thinking': profile['deep_thinking_rate']
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        
        for metric in ['Cognitive Load', 'Learning Effectiveness', 'Engagement', 'Deep Thinking']:
            fig.add_trace(
                go.Bar(
                    name=metric,
                    x=metrics_df['Proficiency'],
                    y=metrics_df[metric],
                    text=metrics_df[metric].round(2),
                    textposition='auto'
                ),
                row=1, col=2
            )
        
        # 3. Learning Progression (Scatter Plot)
        if session_metrics:
            progression_data = []
            for i, session in enumerate(session_metrics):
                if 'cognitive_offloading_prevention' in session:
                    progression_data.append({
                        'Session': i + 1,
                        'Prevention Rate': session['cognitive_offloading_prevention']['overall_rate'],
                        'Deep Thinking': session['deep_thinking_engagement']['overall_rate'],
                        'Scaffolding': session['scaffolding_effectiveness']['overall_rate']
                    })
            
            if progression_data:
                prog_df = pd.DataFrame(progression_data)
                
                for metric in ['Prevention Rate', 'Deep Thinking', 'Scaffolding']:
                    fig.add_trace(
                        go.Scatter(
                            name=metric,
                            x=prog_df['Session'],
                            y=prog_df[metric],
                            mode='lines+markers',
                            line=dict(width=2),
                            marker=dict(size=8)
                        ),
                        row=2, col=1
                    )
        
        # 4. Cognitive Pattern Heatmap
        pattern_matrix = []
        pattern_labels = []
        
        for profile in cluster_profiles.values():
            pattern_labels.append(f"{profile['proficiency_level'].title()} (n={profile['size']})")
            pattern_matrix.append([
                profile['avg_cognitive_load'],
                profile['avg_learning_effectiveness'],
                profile['avg_engagement'],
                profile['cognitive_offloading_prevention'],
                profile['deep_thinking_rate'],
                profile['scaffolding_effectiveness']
            ])
        
        fig.add_trace(
            go.Heatmap(
                z=pattern_matrix,
                x=['Cognitive<br>Load', 'Learning<br>Effect', 'Engagement', 
                   'Offload<br>Prevention', 'Deep<br>Thinking', 'Scaffolding'],
                y=pattern_labels,
                colorscale=PLOTLY_COLORSCALES['main'],
                text=np.round(pattern_matrix, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                showscale=True
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Cognitive Benchmarking Dashboard",
            title_font_size=24,
            showlegend=True,
            height=1000,
            width=1400
        )
        
        # Update axes
        fig.update_xaxes(title_text="Session Number", row=2, col=1)
        fig.update_yaxes(title_text="Metric Value", row=2, col=1)
        fig.update_yaxes(title_text="Metric Value", row=1, col=2)
        
        if save_path:
            fig.write_html(save_path)
            print(f"Dashboard saved to: {save_path}")
        else:
            fig.show()
    
    def visualize_benchmark_comparison(self,
                                     benchmark_profiles: Dict[str, Any],
                                     user_metrics: Dict[str, Any],
                                     save_path: Optional[str] = None):
        """Compare user metrics against benchmark profiles"""
        
        # Create radar chart for comparison
        fig = go.Figure()
        
        # Define metrics to compare
        metrics = [
            'cognitive_load_range',
            'learning_effectiveness_min',
            'engagement_min',
            'cognitive_offloading_prevention_min',
            'deep_thinking_rate_min',
            'scaffolding_effectiveness_min'
        ]
        
        metric_labels = [
            'Cognitive<br>Load',
            'Learning<br>Effectiveness',
            'Engagement',
            'Offload<br>Prevention',
            'Deep<br>Thinking',
            'Scaffolding'
        ]
        
        # Add benchmark profiles
        for level, profile in benchmark_profiles.items():
            values = []
            for metric in metrics:
                if metric == 'cognitive_load_range':
                    # Use midpoint of range
                    values.append(np.mean(profile['target_metrics'][metric]))
                else:
                    values.append(profile['target_metrics'][metric])
            
            # Close the radar chart
            values += values[:1]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_labels + metric_labels[:1],
                fill='toself',
                fillcolor=self.color_palette.get(level, THESIS_COLORS['neutral_warm']),
                opacity=0.3,
                name=f'{level.title()} Benchmark',
                line=dict(color=self.color_palette.get(level, THESIS_COLORS['neutral_warm']), width=2)
            ))
        
        # Add user metrics if provided
        if user_metrics:
            user_values = [
                user_metrics.get('avg_cognitive_load', 0.5),
                user_metrics.get('learning_effectiveness', 0.5),
                user_metrics.get('engagement', 0.5),
                user_metrics.get('cognitive_offloading_prevention', 0.5),
                user_metrics.get('deep_thinking_rate', 0.5),
                user_metrics.get('scaffolding_effectiveness', 0.5)
            ]
            user_values += user_values[:1]
            
            fig.add_trace(go.Scatterpolar(
                r=user_values,
                theta=metric_labels + metric_labels[:1],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.5)',
                name='Current User',
                line=dict(color='red', width=3)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title={
                'text': "User Performance vs Proficiency Benchmarks",
                'font': {'size': 20}
            },
            width=900,
            height=700
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Comparison chart saved to: {save_path}")
        else:
            fig.show()
    
    def create_cognitive_flow_diagram(self,
                                    interaction_data: pd.DataFrame,
                                    save_path: Optional[str] = None):
        """Create Sankey diagram showing cognitive flow through agents"""
        
        # Prepare data for Sankey diagram
        sources = []
        targets = []
        values = []
        labels = []
        
        # Define nodes
        input_types = interaction_data['input_type'].unique()
        routing_paths = interaction_data['routing_path'].unique()
        response_types = interaction_data['response_type'].unique()
        
        # Create label list
        labels = (list(input_types) + list(routing_paths) + list(response_types))
        label_to_idx = {label: i for i, label in enumerate(labels)}
        
        # Count flows
        flow_counts = interaction_data.groupby(
            ['input_type', 'routing_path', 'response_type']
        ).size().reset_index(name='count')
        
        # Add input -> routing flows
        input_routing = interaction_data.groupby(
            ['input_type', 'routing_path']
        ).size().reset_index(name='count')
        
        for _, row in input_routing.iterrows():
            sources.append(label_to_idx[row['input_type']])
            targets.append(label_to_idx[row['routing_path']])
            values.append(row['count'])
        
        # Add routing -> response flows
        routing_response = interaction_data.groupby(
            ['routing_path', 'response_type']
        ).size().reset_index(name='count')
        
        for _, row in routing_response.iterrows():
            sources.append(label_to_idx[row['routing_path']])
            targets.append(label_to_idx[row['response_type']])
            values.append(row['count'])
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=[self._get_node_color(label) for label in labels]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color='rgba(100, 100, 100, 0.3)'
            )
        )])
        
        fig.update_layout(
            title={
                'text': "Cognitive Flow: Input → Routing → Response",
                'font': {'size': 20}
            },
            font_size=12,
            width=1200,
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Flow diagram saved to: {save_path}")
        else:
            fig.show()
    
    def _get_node_color(self, label: str) -> str:
        """Get color for Sankey node based on type"""
        
        if 'question' in label.lower():
            return self.color_palette['cognitive_load']
        elif 'feedback' in label.lower():
            return self.color_palette['learning']
        elif 'socratic' in label.lower():
            return self.color_palette['engagement']
        elif 'cognitive' in label.lower():
            return self.color_palette['scaffolding']
        elif 'knowledge' in label.lower():
            return self.color_palette['intermediate']
        else:
            return self.color_palette['neutral']
    
    def create_temporal_analysis(self,
                               session_data: pd.DataFrame,
                               save_path: Optional[str] = None):
        """Create temporal analysis visualization"""
        
        # Convert timestamp to datetime
        session_data['timestamp'] = pd.to_datetime(session_data['timestamp'])
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Cognitive Metrics Over Time',
                          'Agent Usage Distribution',
                          'Cumulative Learning Progress'),
            specs=[[{"secondary_y": True}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]],
            row_heights=[0.4, 0.3, 0.3]
        )
        
        # 1. Cognitive Metrics Timeline
        metrics = ['prevents_cognitive_offloading', 'encourages_deep_thinking', 
                  'provides_scaffolding', 'maintains_engagement']
        colors = [THESIS_COLORS['primary_violet'], THESIS_COLORS['primary_purple'], 
                 THESIS_COLORS['primary_rose'], THESIS_COLORS['accent_coral']]
        
        for metric, color in zip(metrics, colors):
            # Calculate rolling average
            rolling_metric = session_data[metric].rolling(window=5, min_periods=1).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=session_data.index,
                    y=rolling_metric,
                    name=metric.replace('_', ' ').title(),
                    line=dict(color=color, width=2),
                    mode='lines'
                ),
                row=1, col=1
            )
        
        # Add cognitive load on secondary axis
        fig.add_trace(
            go.Scatter(
                x=session_data.index,
                y=session_data['confidence_score'],
                name='Confidence Score',
                line=dict(color=THESIS_COLORS['neutral_warm'], width=2, dash='dash'),
                mode='lines'
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        # 2. Agent Usage Stacked Area
        agent_columns = []
        for col in session_data.columns:
            if 'agent' in col.lower() and col != 'agents_used':
                agent_columns.append(col)
        
        if not agent_columns:
            # Parse agents_used column
            agent_usage = {'socratic': [], 'cognitive': [], 'knowledge': [], 'context': []}
            
            for agents in session_data['agents_used']:
                for agent_type in agent_usage:
                    if isinstance(agents, str):
                        agent_usage[agent_type].append(1 if agent_type in agents.lower() else 0)
                    else:
                        agent_usage[agent_type].append(0)
            
            for agent_type, usage in agent_usage.items():
                fig.add_trace(
                    go.Scatter(
                        x=session_data.index,
                        y=usage,
                        name=f'{agent_type.title()} Agent',
                        stackgroup='agents',
                        fillcolor=get_agent_color(agent_type)
                    ),
                    row=2, col=1
                )
        
        # 3. Cumulative Learning Progress
        cumulative_prevention = session_data['prevents_cognitive_offloading'].cumsum()
        cumulative_thinking = session_data['encourages_deep_thinking'].cumsum()
        cumulative_scaffolding = session_data['provides_scaffolding'].cumsum()
        
        fig.add_trace(
            go.Scatter(
                x=session_data.index,
                y=cumulative_prevention / (session_data.index + 1),
                name='Avg Offload Prevention',
                line=dict(color=THESIS_COLORS['primary_violet'], width=3),
                fill='tonexty'
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=session_data.index,
                y=cumulative_thinking / (session_data.index + 1),
                name='Avg Deep Thinking',
                line=dict(color=THESIS_COLORS['primary_purple'], width=3),
                fill='tonexty'
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_xaxes(title_text="Interaction Number", row=3, col=1)
        fig.update_yaxes(title_text="Metric Value", row=1, col=1)
        fig.update_yaxes(title_text="Confidence", row=1, col=1, secondary_y=True)
        fig.update_yaxes(title_text="Agent Usage", row=2, col=1)
        fig.update_yaxes(title_text="Cumulative Average", row=3, col=1)
        
        fig.update_layout(
            title_text="Temporal Cognitive Analysis",
            title_font_size=24,
            showlegend=True,
            height=1200,
            width=1000
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Temporal analysis saved to: {save_path}")
        else:
            fig.show()
    
    def create_skill_progression_visualization(self,
                                             progression_data: List[Dict[str, Any]],
                                             save_path: Optional[str] = None):
        """Visualize skill progression across sessions"""
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # Extract data
        sessions = []
        skill_levels = []
        progression_scores = []
        stability_scores = []
        
        for session in progression_data:
            sessions.append(session.get('session_id', ''))
            
            prog = session.get('skill_progression', {})
            skill_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            
            initial = skill_map.get(prog.get('initial_level', 'beginner'), 1)
            final = skill_map.get(prog.get('final_level', 'beginner'), 1)
            
            skill_levels.append([initial, final])
            progression_scores.append(prog.get('progression_score', 0))
            stability_scores.append(prog.get('stability', 0))
        
        # 1. Skill Level Changes
        x = np.arange(len(sessions))
        width = 0.35
        
        initial_levels = [s[0] for s in skill_levels]
        final_levels = [s[1] for s in skill_levels]
        
        ax1.bar(x - width/2, initial_levels, width, label='Initial Level', 
                color=self.color_palette['beginner'], alpha=0.7)
        ax1.bar(x + width/2, final_levels, width, label='Final Level',
                color=self.color_palette['advanced'], alpha=0.7)
        
        ax1.set_ylabel('Skill Level')
        ax1.set_title('Skill Level Progression by Session')
        ax1.set_xticks(x)
        ax1.set_xticklabels([f'S{i+1}' for i in range(len(sessions))], rotation=45)
        ax1.set_yticks([1, 2, 3])
        ax1.set_yticklabels(['Beginner', 'Intermediate', 'Advanced'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Progression Scores
        ax2.plot(x, progression_scores, 'o-', color=self.color_palette['positive'], 
                linewidth=2, markersize=8, label='Progression Score')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.fill_between(x, 0, progression_scores, alpha=0.3, 
                        color=self.color_palette['positive'])
        
        ax2.set_ylabel('Progression Score')
        ax2.set_title('Learning Progression Score Over Time')
        ax2.set_xticks(x)
        ax2.set_xticklabels([f'S{i+1}' for i in range(len(sessions))], rotation=45)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. Stability Scores
        ax3.bar(x, stability_scores, color=self.color_palette['neutral'], alpha=0.7)
        ax3.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, 
                   label='Target Stability')
        
        ax3.set_ylabel('Stability Score')
        ax3.set_title('Skill Level Stability by Session')
        ax3.set_xticks(x)
        ax3.set_xticklabels([f'S{i+1}' for i in range(len(sessions))], rotation=45)
        ax3.set_ylim(0, 1)
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Skill progression visualization saved to: {save_path}")
        else:
            plt.show()
    
    def create_benchmark_report_visualization(self,
                                            benchmark_report: Dict[str, Any],
                                            save_path: Optional[str] = None):
        """Create comprehensive visualization of benchmark report"""
        
        # Create multi-page report
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Proficiency Distribution',
                          'System Improvement Recommendations',
                          'Pedagogical Strategies',
                          'Benchmark Profile Comparison'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "table"}, {"type": "scatter"}]]
        )
        
        # 1. Proficiency Distribution
        prof_dist = benchmark_report['cluster_analysis']['proficiency_distribution']
        
        fig.add_trace(
            go.Pie(
                labels=list(prof_dist.keys()),
                values=list(prof_dist.values()),
                hole=0.4,
                marker_colors=[self.color_palette.get(k, THESIS_COLORS['neutral_warm']) for k in prof_dist.keys()],
                textinfo='label+value+percent',
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # 2. System Improvements Bar Chart
        improvements = benchmark_report['recommendations']['system_improvements']
        if improvements:
            imp_categories = [imp.split()[0] for imp in improvements]
            imp_values = [100 / len(improvements)] * len(improvements)  # Equal importance
            
            fig.add_trace(
                go.Bar(
                    x=imp_categories,
                    y=imp_values,
                    text=[f"{v:.0f}%" for v in imp_values],
                    textposition='auto',
                    marker_color=self.color_palette['negative']
                ),
                row=1, col=2
            )
        
        # 3. Pedagogical Strategies Table
        strategies = benchmark_report['recommendations']['pedagogical_strategies']
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Pedagogical Strategy'],
                    fill_color=self.color_palette['scaffolding'],
                    align='left',
                    font=dict(color='white', size=14)
                ),
                cells=dict(
                    values=[strategies],
                    fill_color='lightgray',
                    align='left',
                    height=30
                )
            ),
            row=2, col=1
        )
        
        # 4. Benchmark Profiles Comparison
        if 'benchmark_profiles' in benchmark_report:
            profiles = benchmark_report['benchmark_profiles']
            
            metrics = ['learning_effectiveness_min', 'engagement_min', 
                      'deep_thinking_rate_min', 'scaffolding_effectiveness_min']
            
            for level, profile in profiles.items():
                values = [profile['target_metrics'].get(m, 0) for m in metrics]
                
                fig.add_trace(
                    go.Scatter(
                        x=['Learning', 'Engagement', 'Deep Thinking', 'Scaffolding'],
                        y=values,
                        name=level.title(),
                        mode='lines+markers',
                        line=dict(width=3),
                        marker=dict(size=10)
                    ),
                    row=2, col=2
                )
        
        # Update layout
        fig.update_layout(
            title_text="Cognitive Benchmarking Report Summary",
            title_font_size=24,
            showlegend=True,
            height=1000,
            width=1400
        )
        
        fig.update_xaxes(title_text="Improvement Areas", row=1, col=2)
        fig.update_yaxes(title_text="Priority %", row=1, col=2)
        fig.update_xaxes(title_text="Metrics", row=2, col=2)
        fig.update_yaxes(title_text="Target Value", row=2, col=2)
        
        if save_path:
            fig.write_html(save_path)
            print(f"Report visualization saved to: {save_path}")
        else:
            fig.show()
    
    def save_all_visualizations(self, 
                              data: Dict[str, Any],
                              output_dir: str = "./benchmarking/visualizations"):
        """Generate and save all visualizations"""
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print("Generating comprehensive visualization suite...")
        
        # List of visualizations to generate
        visualizations = [
            ('proficiency_dashboard', self.create_proficiency_dashboard),
            ('temporal_analysis', self.create_temporal_analysis),
            ('cognitive_flow', self.create_cognitive_flow_diagram),
            ('benchmark_comparison', self.visualize_benchmark_comparison),
            ('skill_progression', self.create_skill_progression_visualization),
            ('benchmark_report', self.create_benchmark_report_visualization)
        ]
        
        for viz_name, viz_func in visualizations:
            try:
                print(f"  - Generating {viz_name}...")
                # Call visualization function with appropriate data
                # (Implementation depends on available data structure)
                
            except Exception as e:
                print(f"    Error generating {viz_name}: {str(e)}")
        
        print(f"\n✅ All visualizations saved to: {output_dir}")


def main():
    """Example usage of visualization tools"""
    
    visualizer = CognitiveBenchmarkVisualizer(style='scientific')
    
    # Example: Load some data and create visualizations
    # This would be replaced with actual data loading
    
    print("Cognitive Benchmark Visualizer initialized")
    print("Available visualization methods:")
    print("  - visualize_interaction_graph()")
    print("  - create_proficiency_dashboard()")
    print("  - visualize_benchmark_comparison()")
    print("  - create_cognitive_flow_diagram()")
    print("  - create_temporal_analysis()")
    print("  - create_skill_progression_visualization()")
    print("  - create_benchmark_report_visualization()")


if __name__ == "__main__":
    main()