"""
MEGA Architectural Mentor - Graph ML Visualizations for Linkography
Advanced visualizations for temporal graph analysis and pattern discovery
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import torch
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False

from thesis_colors import THESIS_COLORS, METRIC_COLORS
from linkography_graph_ml_integration import GraphMLLinkographyAnalyzer, TemporalData


class LinkographyGraphMLVisualizer:
    """Creates advanced Graph ML visualizations for linkography analysis"""
    
    def __init__(self):
        self.colors = THESIS_COLORS
        self.metric_colors = METRIC_COLORS
        
    def create_temporal_evolution_graph(self, evolution_graph: nx.DiGraph) -> go.Figure:
        """Visualize the evolution of design thinking across sessions"""
        
        # Use spring layout for positioning
        pos = nx.spring_layout(evolution_graph, k=2, iterations=50)
        
        # Extract edge traces
        edge_trace = []
        for edge in evolution_graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    width=evolution_graph[edge[0]][edge[1]]['weight'] * 3,
                    color=self.colors['neutral_warm']
                ),
                hoverinfo='none',
                showlegend=False
            ))
        
        # Extract node traces
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in evolution_graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node attributes
            attrs = evolution_graph.nodes[node]
            
            # Create hover text
            text = f"<b>{node}</b><br>"
            text += f"Nodes: {attrs.get('num_nodes', 0)}<br>"
            text += f"Edges: {attrs.get('num_edges', 0)}<br>"
            text += f"Density: {attrs.get('density', 0):.3f}<br>"
            text += f"Deep Thinking: {attrs.get('deep_thinking_engagement', 0):.3f}<br>"
            text += f"Learning Progress: {attrs.get('learning_progression', 0):.3f}"
            node_text.append(text)
            
            # Color by learning progression
            progress = attrs.get('learning_progression', 0.5)
            node_color.append(progress)
            
            # Size by graph complexity
            complexity = attrs.get('num_nodes', 20) + attrs.get('num_edges', 20)
            node_size.append(10 + complexity / 5)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=[n.replace('session_', 'S') for n in evolution_graph.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale=[[0, self.colors['accent_coral']], 
                           [0.5, self.colors['neutral_orange']], 
                           [1, self.colors['primary_violet']]],
                colorbar=dict(
                    title="Learning<br>Progress",
                    thickness=15,
                    x=1.02
                ),
                line=dict(width=2, color=self.colors['primary_dark'])
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title="Design Thinking Evolution Across Sessions",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=600
        )
        
        return fig
    
    def create_embedding_visualization(self, embeddings: np.ndarray, labels: List[str], 
                                     method: str = 'tsne') -> go.Figure:
        """Visualize high-dimensional embeddings in 2D/3D space"""
        
        # Reduce dimensionality
        if method == 'tsne':
            reducer = TSNE(n_components=3, perplexity=min(30, len(embeddings)-1))
        elif method == 'pca':
            reducer = PCA(n_components=3)
        elif method == 'umap':
            if UMAP_AVAILABLE:
                reducer = umap.UMAP(n_components=3, n_neighbors=min(15, len(embeddings)-1))
            else:
                # Fallback to t-SNE if UMAP not available
                reducer = TSNE(n_components=3, perplexity=min(30, len(embeddings)-1))
        else:
            raise ValueError(f"Unknown reduction method: {method}")
        
        coords = reducer.fit_transform(embeddings)
        
        # Create 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='markers+text',
            text=labels,
            textposition='top center',
            marker=dict(
                size=8,
                color=np.arange(len(embeddings)),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Temporal<br>Order")
            ),
            hovertext=[f"Move {i}: {label}" for i, label in enumerate(labels)],
            hoverinfo='text'
        )])
        
        fig.update_layout(
            title=f"Design Move Embeddings ({method.upper()})",
            scene=dict(
                xaxis_title="Dimension 1",
                yaxis_title="Dimension 2",
                zaxis_title="Dimension 3",
                bgcolor='rgba(250, 248, 245, 0.5)'
            ),
            height=700
        )
        
        return fig
    
    def create_anomaly_heatmap(self, node_anomalies: np.ndarray, 
                              move_labels: List[str]) -> go.Figure:
        """Create heatmap showing anomaly scores across design moves"""
        
        # Reshape for heatmap (create time windows)
        window_size = 10
        num_windows = len(node_anomalies) // window_size + 1
        
        # Pad array to fit windows
        padded_length = num_windows * window_size
        padded_anomalies = np.pad(node_anomalies, 
                                  (0, padded_length - len(node_anomalies)), 
                                  mode='constant', 
                                  constant_values=0)
        
        # Reshape to 2D
        heatmap_data = padded_anomalies.reshape(num_windows, window_size)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            colorscale=[[0, 'white'], 
                       [0.5, self.colors['neutral_orange']], 
                       [1, self.colors['accent_coral']]],
            text=[[f"Move {i*window_size + j}" for j in range(window_size)] 
                  for i in range(num_windows)],
            hovertemplate="Window: %{y}<br>Position: %{x}<br>Anomaly Score: %{z:.3f}<br>%{text}<extra></extra>",
            colorbar=dict(title="Anomaly<br>Score")
        ))
        
        fig.update_layout(
            title="Design Process Anomaly Detection Heatmap",
            xaxis_title="Move Position in Window",
            yaxis_title="Time Window",
            height=500
        )
        
        return fig
    
    def create_cognitive_trajectory_radar(self, cognitive_trajectories: List[Dict[str, float]]) -> go.Figure:
        """Create animated radar chart showing cognitive metric evolution"""
        
        categories = list(cognitive_trajectories[0].keys())
        
        fig = go.Figure()
        
        # Add traces for each time point
        for i, trajectory in enumerate(cognitive_trajectories):
            values = list(trajectory.values())
            values.append(values[0])  # Complete the circle
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=f'Stage {i+1}',
                line_color=self.colors['primary_violet'],
                fillcolor=f'rgba(120,76,128,{0.1 + i*0.15/len(cognitive_trajectories)})'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Cognitive Development Trajectory",
            height=600
        )
        
        return fig
    
    def create_pattern_emergence_timeline(self, pattern_data: List[Dict[str, Any]]) -> go.Figure:
        """Visualize how patterns emerge and evolve over time"""
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(pattern_data)
        
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            subplot_titles=['Chunk Patterns', 'Web Patterns', 'Sawtooth Patterns', 'Orphan Patterns'],
            vertical_spacing=0.05
        )
        
        patterns = ['chunk', 'web', 'sawtooth', 'orphan']
        colors = [self.colors['primary_purple'], self.colors['primary_violet'], 
                 self.colors['neutral_warm'], self.colors['accent_coral']]
        
        for i, (pattern, color) in enumerate(zip(patterns, colors)):
            if pattern in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[pattern],
                        mode='lines+markers',
                        name=pattern.capitalize(),
                        line=dict(color=color, width=2),
                        fill='tozeroy',
                        fillcolor=color.replace(')', ',0.2)').replace('rgb', 'rgba')
                    ),
                    row=i+1, col=1
                )
                
                # Add threshold line
                fig.add_hline(
                    y=0.5, 
                    line_dash="dash", 
                    line_color="gray",
                    annotation_text="Detection Threshold",
                    row=i+1, col=1
                )
        
        fig.update_xaxes(title_text="Time Step", row=4, col=1)
        fig.update_yaxes(title_text="Probability", range=[0, 1])
        
        fig.update_layout(
            title="Pattern Emergence Timeline",
            height=800,
            showlegend=True
        )
        
        return fig
    
    def create_graph_metric_comparison(self, sessions: List[Dict[str, Any]]) -> go.Figure:
        """Create parallel coordinates plot comparing graph metrics across sessions"""
        
        # Extract metrics for comparison
        metrics_data = []
        for i, session in enumerate(sessions):
            metrics = session['temporal_graph_metrics']
            metrics['session'] = i
            metrics['anomaly_score'] = session['anomaly_detection']['overall_anomaly_score']
            metrics_data.append(metrics)
        
        df = pd.DataFrame(metrics_data)
        
        # Normalize metrics to 0-1 scale for comparison
        for col in df.columns:
            if col != 'session':
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min() + 1e-8)
        
        fig = go.Figure(data=
            go.Parcoords(
                line=dict(
                    color=df['anomaly_score'],
                    colorscale=[[0, self.colors['primary_violet']], 
                               [0.5, self.colors['neutral_orange']], 
                               [1, self.colors['accent_coral']]],
                    showscale=True,
                    colorbar=dict(title="Anomaly<br>Score")
                ),
                dimensions=[
                    dict(label='Session', values=df['session']),
                    dict(label='Nodes', values=df['num_nodes']),
                    dict(label='Edges', values=df['num_edges']),
                    dict(label='Density', values=df['density']),
                    dict(label='Clustering', values=df['avg_clustering']),
                    dict(label='Connectivity', values=df['connectivity']),
                    dict(label='Temporal Reg.', values=df.get('temporal_regularity', 0)),
                    dict(label='Anomaly', values=df['anomaly_score'])
                ]
            )
        )
        
        fig.update_layout(
            title="Graph Metrics Comparison Across Sessions",
            height=600
        )
        
        return fig
    
    def create_learning_struggle_dashboard(self, struggle_analysis: Dict[str, Any]) -> go.Figure:
        """Create comprehensive dashboard for learning struggle analysis"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Anomaly Score Timeline', 'Struggle Node Distribution',
                           'Recommendation Impact', 'Cognitive Metric Changes'),
            specs=[[{'type': 'scatter'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'scatter'}]]
        )
        
        # Anomaly score timeline
        if 'timeline' in struggle_analysis:
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(struggle_analysis['timeline']))),
                    y=struggle_analysis['timeline'],
                    mode='lines+markers',
                    line=dict(color=self.colors['accent_coral'], width=3),
                    marker=dict(size=8),
                    name='Anomaly Score'
                ),
                row=1, col=1
            )
            
            # Add threshold line
            fig.add_hline(
                y=0.7, 
                line_dash="dash",
                line_color="gray",
                annotation_text="Struggle Threshold",
                row=1, col=1
            )
        
        # Struggle node distribution
        if 'node_types' in struggle_analysis:
            fig.add_trace(
                go.Bar(
                    x=list(struggle_analysis['node_types'].keys()),
                    y=list(struggle_analysis['node_types'].values()),
                    marker_color=[self.colors['primary_purple'], 
                                 self.colors['primary_violet'],
                                 self.colors['neutral_warm']],
                    name='Node Types'
                ),
                row=1, col=2
            )
        
        # Recommendation categories
        if 'recommendation_categories' in struggle_analysis:
            fig.add_trace(
                go.Pie(
                    labels=list(struggle_analysis['recommendation_categories'].keys()),
                    values=list(struggle_analysis['recommendation_categories'].values()),
                    hole=0.3,
                    marker_colors=[self.colors['neutral_orange'], 
                                  self.colors['primary_rose'],
                                  self.colors['primary_pink']],
                    name='Recommendations'
                ),
                row=2, col=1
            )
        
        # Cognitive metric changes
        if 'cognitive_changes' in struggle_analysis:
            metrics = list(struggle_analysis['cognitive_changes'].keys())
            before = [v['before'] for v in struggle_analysis['cognitive_changes'].values()]
            after = [v['after'] for v in struggle_analysis['cognitive_changes'].values()]
            
            fig.add_trace(
                go.Scatter(
                    x=metrics,
                    y=before,
                    mode='lines+markers',
                    name='Before',
                    line=dict(color=self.colors['neutral_warm'], width=2)
                ),
                row=2, col=2
            )
            
            fig.add_trace(
                go.Scatter(
                    x=metrics,
                    y=after,
                    mode='lines+markers',
                    name='After',
                    line=dict(color=self.colors['primary_violet'], width=2)
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Learning Struggle Analysis Dashboard",
            height=800,
            showlegend=True
        )
        
        return fig


# Export visualizer
__all__ = ['LinkographyGraphMLVisualizer']