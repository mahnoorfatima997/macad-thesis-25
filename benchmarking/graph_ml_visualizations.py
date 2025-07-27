"""
Advanced Graph ML Visualizations for Cognitive Benchmarking
Based on thesis requirements for interactive graph analysis
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path
from sklearn.cluster import SpectralClustering
from sklearn.manifold import TSNE
try:
    import torch
    import torch_geometric
    from torch_geometric.nn import GCNConv, global_mean_pool
    from torch_geometric.data import Data, Batch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import community  # python-louvain for community detection
    COMMUNITY_AVAILABLE = True
except ImportError:
    COMMUNITY_AVAILABLE = False
from datetime import datetime
import colorsys


class GraphMLVisualizer:
    """Advanced Graph ML visualizations for cognitive benchmarking"""
    
    def __init__(self, results_path: str = "benchmarking/results"):
        self.results_path = Path(results_path)
        self.load_data()
        
        # Color scheme from thesis
        self.colors = {
            'clusters': {
                'beginner': '#FF6B6B',
                'intermediate': '#4ECDC4',
                'advanced': '#45B7D1', 
                'expert': '#96CEB4'
            },
            'nodes': {
                'user': '#E8743B',
                'concept': '#19A979',
                'interaction': '#945ECF',
                'knowledge': '#13A4B4',
                'skill': '#525252'
            },
            'edges': {
                'temporal': '#CCCCCC',
                'conceptual': '#FFA500',
                'cognitive': '#7B68EE',
                'learning': '#32CD32'
            }
        }
    
    def load_data(self):
        """Load benchmarking results for visualization"""
        try:
            # Load benchmark report
            with open(self.results_path / "benchmark_report.json", 'r') as f:
                self.benchmark_report = json.load(f)
            
            # Load evaluation reports
            self.evaluation_reports = {}
            eval_dir = self.results_path / "evaluation_reports"
            for eval_file in eval_dir.glob("*.json"):
                with open(eval_file, 'r') as f:
                    session_data = json.load(f)
                    session_id = session_data['session_metrics']['session_id']
                    self.evaluation_reports[session_id] = session_data
                    
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.benchmark_report = {}
            self.evaluation_reports = {}
    
    def create_expanded_knowledge_graph(self):
        """Create expanded knowledge graph showing architecture, cognition & AI relationships"""
        
        # Build the knowledge graph
        G = nx.Graph()
        
        # Central nodes
        central_nodes = {
            'Design Process': {'type': 'process', 'size': 40, 'color': self.colors['nodes']['interaction']},
            'Spatial Reasoning': {'type': 'cognitive', 'size': 35, 'color': self.colors['nodes']['skill']},
            'AI Feedback': {'type': 'ai', 'size': 35, 'color': self.colors['nodes']['knowledge']},
            'Critical Thinking': {'type': 'cognitive', 'size': 30, 'color': self.colors['nodes']['skill']},
            'Visual Analysis': {'type': 'process', 'size': 30, 'color': self.colors['nodes']['interaction']}
        }
        
        # Add central nodes
        for node, attrs in central_nodes.items():
            G.add_node(node, **attrs)
        
        # Cognitive concepts
        cognitive_concepts = [
            'Pattern Recognition', 'Problem Solving', 'Metacognition',
            'Knowledge Transfer', 'Conceptual Understanding', 'Reflection'
        ]
        
        # Architectural concepts
        arch_concepts = [
            'Form Generation', 'Spatial Composition', 'Material Systems',
            'Structural Logic', 'Environmental Design', 'Context Analysis'
        ]
        
        # AI/Learning concepts
        ai_concepts = [
            'Socratic Method', 'Scaffolding', 'Cognitive Load',
            'Feedback Loops', 'Adaptive Learning', 'Knowledge Graphs'
        ]
        
        # Add concept nodes and edges
        for concept in cognitive_concepts:
            G.add_node(concept, type='cognitive', size=20, color=self.colors['nodes']['skill'])
            G.add_edge('Critical Thinking', concept, weight=np.random.uniform(0.5, 1.0))
            
        for concept in arch_concepts:
            G.add_node(concept, type='architecture', size=20, color=self.colors['nodes']['concept'])
            G.add_edge('Design Process', concept, weight=np.random.uniform(0.5, 1.0))
            G.add_edge('Spatial Reasoning', concept, weight=np.random.uniform(0.3, 0.8))
            
        for concept in ai_concepts:
            G.add_node(concept, type='ai', size=20, color=self.colors['nodes']['knowledge'])
            G.add_edge('AI Feedback', concept, weight=np.random.uniform(0.5, 1.0))
        
        # Add cross-domain connections
        G.add_edge('Pattern Recognition', 'Form Generation', weight=0.8)
        G.add_edge('Problem Solving', 'Structural Logic', weight=0.7)
        G.add_edge('Metacognition', 'Socratic Method', weight=0.9)
        G.add_edge('Visual Analysis', 'Pattern Recognition', weight=0.8)
        G.add_edge('Knowledge Transfer', 'Adaptive Learning', weight=0.7)
        
        # User proficiency connections
        if 'proficiency_clusters' in self.benchmark_report:
            for cluster_id, cluster_data in self.benchmark_report['proficiency_clusters'].items():
                prof_level = cluster_data['proficiency_level']
                node_name = f"{prof_level.capitalize()} Users"
                G.add_node(node_name, type='user_cluster', size=25, 
                          color=self.colors['clusters'][prof_level])
                
                # Connect to relevant concepts based on proficiency
                if prof_level == 'expert':
                    G.add_edge(node_name, 'Metacognition', weight=0.9)
                    G.add_edge(node_name, 'Knowledge Transfer', weight=0.8)
                elif prof_level == 'advanced':
                    G.add_edge(node_name, 'Critical Thinking', weight=0.8)
                    G.add_edge(node_name, 'Problem Solving', weight=0.7)
                elif prof_level == 'intermediate':
                    G.add_edge(node_name, 'Pattern Recognition', weight=0.7)
                    G.add_edge(node_name, 'Spatial Reasoning', weight=0.6)
                else:  # beginner
                    G.add_edge(node_name, 'Scaffolding', weight=0.9)
                    G.add_edge(node_name, 'Form Generation', weight=0.5)
        
        # Create interactive visualization
        return self._create_interactive_graph_viz(
            G, 
            "Expanded Knowledge Graph - Architecture, Cognition & AI",
            layout='spring'
        )
    
    def create_cognitive_benchmark_network(self):
        """Create cognitive benchmark network showing user clusters and interactions"""
        
        G = nx.DiGraph()
        
        # Add user nodes from sessions
        session_nodes = []
        for i, (session_id, report) in enumerate(self.evaluation_reports.items()):
            metrics = report['session_metrics']
            
            # Determine user cluster based on skill level
            skill_level = metrics['skill_progression']['final_level']
            improvement = metrics['improvement_over_baseline']['overall_improvement']
            
            node_id = f"User_{i+1}"
            session_nodes.append(node_id)
            
            G.add_node(node_id, 
                      type='user',
                      skill_level=skill_level,
                      improvement=improvement,
                      size=20 + improvement/10,
                      color=self.colors['clusters'][skill_level])
        
        # Add test/question nodes
        test_types = ['Design Task', 'Spatial Analysis', 'Concept Integration', 
                     'Critical Reflection', 'Problem Solving']
        
        for test in test_types:
            G.add_node(test, type='test', size=30, color=self.colors['nodes']['concept'])
        
        # Add response quality nodes
        response_types = ['Deep Thinking', 'Surface Level', 'Scaffolded', 
                         'Independent', 'Collaborative']
        
        for resp in response_types:
            G.add_node(resp, type='response', size=25, color=self.colors['nodes']['interaction'])
        
        # Connect users to tests and responses based on their patterns
        for i, node in enumerate(session_nodes):
            # Random connections for demonstration (in real implementation, 
            # these would be based on actual interaction data)
            skill_level = G.nodes[node]['skill_level']
            
            # Connect to tests
            if skill_level in ['advanced', 'expert']:
                G.add_edge(node, 'Critical Reflection', weight=0.8)
                G.add_edge(node, 'Problem Solving', weight=0.7)
            else:
                G.add_edge(node, 'Design Task', weight=0.8)
                G.add_edge(node, 'Spatial Analysis', weight=0.6)
            
            # Connect tests to responses
            if skill_level == 'expert':
                G.add_edge('Critical Reflection', 'Deep Thinking', weight=0.9)
                G.add_edge('Problem Solving', 'Independent', weight=0.8)
            elif skill_level == 'beginner':
                G.add_edge('Design Task', 'Scaffolded', weight=0.9)
                G.add_edge('Spatial Analysis', 'Surface Level', weight=0.6)
        
        # Add cluster nodes
        clusters = self._detect_communities(G)
        for cluster_id, nodes in clusters.items():
            cluster_node = f"Cluster_{cluster_id}"
            G.add_node(cluster_node, type='cluster', size=40, 
                      color=self._get_cluster_color(cluster_id))
            
            # Connect cluster to its members
            for node in nodes:
                if node in session_nodes:
                    G.add_edge(cluster_node, node, weight=0.3)
        
        return self._create_interactive_graph_viz(
            G,
            "Cognitive Benchmark Network - User Clusters & Interactions",
            layout='hierarchical'
        )
    
    def create_learning_trajectory_graph(self):
        """Create learning trajectory graph showing progression paths"""
        
        G = nx.DiGraph()
        
        # Create skill progression nodes
        skills = ['Spatial Awareness', 'Design Principles', 'Critical Analysis', 
                 'System Thinking', 'Creative Synthesis']
        
        levels = ['Novice', 'Developing', 'Proficient', 'Advanced', 'Expert']
        
        # Add skill nodes at different levels
        pos = {}
        for i, skill in enumerate(skills):
            for j, level in enumerate(levels):
                node_id = f"{skill}_{level}"
                G.add_node(node_id, 
                          skill=skill,
                          level=j,
                          type='skill_node',
                          size=15 + j*5,
                          color=self._get_gradient_color(j/4))
                pos[node_id] = (i * 2, j * 2)
        
        # Add progression edges
        for i, skill in enumerate(skills):
            for j in range(len(levels) - 1):
                from_node = f"{skill}_{levels[j]}"
                to_node = f"{skill}_{levels[j+1]}"
                G.add_edge(from_node, to_node, 
                          type='progression',
                          weight=0.8)
        
        # Add cross-skill dependencies
        dependencies = [
            ('Spatial Awareness_Proficient', 'Design Principles_Developing'),
            ('Design Principles_Proficient', 'Critical Analysis_Developing'),
            ('Critical Analysis_Advanced', 'System Thinking_Proficient'),
            ('System Thinking_Advanced', 'Creative Synthesis_Proficient')
        ]
        
        for from_node, to_node in dependencies:
            if from_node in G and to_node in G:
                G.add_edge(from_node, to_node, 
                          type='dependency',
                          weight=0.6)
        
        # Add actual user trajectories
        if self.evaluation_reports:
            trajectory_nodes = []
            for i, (session_id, report) in enumerate(self.evaluation_reports.items()):
                metrics = report['session_metrics']
                skill_level = metrics['skill_progression']['final_level']
                
                # Map user to trajectory
                user_node = f"User_Path_{i+1}"
                G.add_node(user_node,
                          type='user_trajectory',
                          skill_level=skill_level,
                          size=25,
                          color=self.colors['clusters'][skill_level])
                trajectory_nodes.append(user_node)
                
                # Connect to relevant skill nodes
                if skill_level == 'expert':
                    G.add_edge(user_node, 'Creative Synthesis_Expert', weight=0.9)
                elif skill_level == 'advanced':
                    G.add_edge(user_node, 'System Thinking_Advanced', weight=0.8)
                elif skill_level == 'intermediate':
                    G.add_edge(user_node, 'Critical Analysis_Proficient', weight=0.7)
                else:
                    G.add_edge(user_node, 'Spatial Awareness_Developing', weight=0.6)
        
        return self._create_interactive_graph_viz(
            G,
            "Learning Trajectory Graph - Skill Progression Paths",
            layout='custom',
            pos=pos
        )
    
    def create_multi_scale_pattern_graph(self):
        """Create multi-scale pattern analysis graph"""
        
        # Create hierarchical graph
        G = nx.DiGraph()
        
        # Global level - Overall system performance
        G.add_node('System Performance', type='global', level=0, size=50,
                  color='#2C3E50')
        
        # Cluster level - User proficiency clusters
        clusters = ['Beginner Cluster', 'Intermediate Cluster', 
                   'Advanced Cluster', 'Expert Cluster']
        
        for cluster in clusters:
            prof_level = cluster.split()[0].lower()
            G.add_node(cluster, type='cluster', level=1, size=40,
                      color=self.colors['clusters'].get(prof_level, '#888888'))
            G.add_edge('System Performance', cluster)
        
        # Pattern level - Cognitive patterns
        patterns = {
            'Beginner Cluster': ['Scaffolding Dependent', 'Linear Thinking', 'Surface Learning'],
            'Intermediate Cluster': ['Pattern Recognition', 'Guided Exploration', 'Conceptual Links'],
            'Advanced Cluster': ['Independent Analysis', 'System Thinking', 'Deep Integration'],
            'Expert Cluster': ['Creative Synthesis', 'Metacognitive Control', 'Knowledge Transfer']
        }
        
        for cluster, pattern_list in patterns.items():
            for pattern in pattern_list:
                G.add_node(pattern, type='pattern', level=2, size=30,
                          color='#9B59B6')
                G.add_edge(cluster, pattern)
        
        # Individual level - Specific behaviors
        behaviors = {
            'Scaffolding Dependent': ['Frequent Help Requests', 'Step-by-Step Following'],
            'Pattern Recognition': ['Visual Comparisons', 'Similarity Detection'],
            'Independent Analysis': ['Self-Directed Exploration', 'Hypothesis Testing'],
            'Creative Synthesis': ['Novel Combinations', 'Cross-Domain Transfer']
        }
        
        for pattern, behavior_list in behaviors.items():
            if pattern in G:
                for behavior in behavior_list:
                    G.add_node(behavior, type='behavior', level=3, size=20,
                              color='#E74C3C')
                    G.add_edge(pattern, behavior)
        
        # Add metrics to behaviors
        metric_values = {
            'Frequent Help Requests': 0.85,
            'Visual Comparisons': 0.72,
            'Self-Directed Exploration': 0.91,
            'Novel Combinations': 0.88
        }
        
        for behavior, value in metric_values.items():
            if behavior in G:
                G.nodes[behavior]['metric_value'] = value
                G.nodes[behavior]['size'] = 15 + value * 20
        
        return self._create_interactive_graph_viz(
            G,
            "Multi-Scale Pattern Analysis - From System to Individual Behaviors",
            layout='hierarchical'
        )
    
    def create_gnn_embedding_visualization(self):
        """Create visualization of GNN embeddings and predictions"""
        
        # Generate sample GNN embeddings (in real implementation, 
        # these would come from the trained GNN model)
        n_nodes = len(self.evaluation_reports) * 5  # 5 nodes per session
        embeddings = np.random.randn(n_nodes, 128)  # 128-dim embeddings
        
        # Reduce to 2D using t-SNE
        tsne = TSNE(n_components=2, random_state=42)
        embeddings_2d = tsne.fit_transform(embeddings)
        
        # Create traces for different node types
        node_types = ['User State', 'Design Action', 'Cognitive Load', 
                     'Learning Outcome', 'Feedback Response']
        
        traces = []
        
        for i, node_type in enumerate(node_types):
            # Get nodes of this type
            type_indices = list(range(i, n_nodes, len(node_types)))
            x_coords = embeddings_2d[type_indices, 0]
            y_coords = embeddings_2d[type_indices, 1]
            
            # Assign proficiency levels randomly for visualization
            proficiency_levels = np.random.choice(['beginner', 'intermediate', 
                                                 'advanced', 'expert'], 
                                                size=len(type_indices))
            
            colors = [self.colors['clusters'][level] for level in proficiency_levels]
            
            trace = go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                name=node_type,
                marker=dict(
                    size=10,
                    color=colors,
                    line=dict(width=1, color='white')
                ),
                text=[f"{node_type}<br>Proficiency: {level}" 
                     for level in proficiency_levels],
                hoverinfo='text'
            )
            traces.append(trace)
        
        # Add cluster boundaries
        n_clusters = 4
        clustering = SpectralClustering(n_clusters=n_clusters, 
                                      affinity='nearest_neighbors',
                                      random_state=42)
        cluster_labels = clustering.fit_predict(embeddings_2d)
        
        # Draw cluster boundaries
        for i in range(n_clusters):
            cluster_points = embeddings_2d[cluster_labels == i]
            if len(cluster_points) > 2:
                # Create convex hull
                from scipy.spatial import ConvexHull
                hull = ConvexHull(cluster_points)
                
                # Add hull as a trace
                hull_points = cluster_points[hull.vertices]
                hull_points = np.vstack([hull_points, hull_points[0]])  # Close the shape
                
                trace = go.Scatter(
                    x=hull_points[:, 0],
                    y=hull_points[:, 1],
                    mode='lines',
                    name=f'Cluster {i+1}',
                    line=dict(color='rgba(0,0,0,0.3)', width=2, dash='dash'),
                    showlegend=False,
                    hoverinfo='skip'
                )
                traces.append(trace)
        
        # Create figure
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title="GNN Embedding Space - Cognitive State Representations",
            xaxis_title="Embedding Dimension 1",
            yaxis_title="Embedding Dimension 2",
            hovermode='closest',
            width=900,
            height=700,
            template='plotly_white'
        )
        
        return fig
    
    def _create_interactive_graph_viz(self, G, title, layout='spring', pos=None):
        """Create interactive graph visualization using Plotly"""
        
        # Calculate layout
        if pos is None:
            if layout == 'spring':
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            elif layout == 'hierarchical':
                pos = self._hierarchical_layout(G)
            elif layout == 'circular':
                pos = nx.circular_layout(G)
            else:  # custom
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Create edge traces
        edge_traces = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_type = edge[2].get('type', 'default')
            weight = edge[2].get('weight', 0.5)
            
            edge_color = self.colors['edges'].get(edge_type, '#CCCCCC')
            
            # Create edge trace
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=weight*3, color=edge_color),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node attributes
            node_data = G.nodes[node]
            size = node_data.get('size', 20)
            color = node_data.get('color', '#888888')
            
            node_size.append(size)
            node_color.append(color)
            
            # Create hover text
            hover_text = f"<b>{node}</b><br>"
            hover_text += f"Type: {node_data.get('type', 'unknown')}<br>"
            
            # Add additional attributes
            for key, value in node_data.items():
                if key not in ['size', 'color', 'type', 'pos']:
                    hover_text += f"{key}: {value}<br>"
            
            node_text.append(hover_text)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=[str(node) for node in G.nodes()],
            textposition="top center",
            textfont=dict(size=10),
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            width=1000,
            height=800
        )
        
        # Add annotations for important nodes
        annotations = []
        important_nodes = [node for node in G.nodes() 
                          if G.nodes[node].get('size', 20) > 30]
        
        for node in important_nodes[:5]:  # Limit to 5 annotations
            x, y = pos[node]
            annotations.append(
                dict(
                    x=x,
                    y=y + 0.1,
                    text=node,
                    showarrow=False,
                    font=dict(size=12, color='black', family='Arial Black')
                )
            )
        
        fig.update_layout(annotations=annotations)
        
        return fig
    
    def _hierarchical_layout(self, G):
        """Create hierarchical layout for directed graphs"""
        
        pos = {}
        
        # Find nodes by level if available
        levels = {}
        for node in G.nodes():
            level = G.nodes[node].get('level', None)
            if level is not None:
                if level not in levels:
                    levels[level] = []
                levels[level].append(node)
        
        if levels:
            # Use specified levels
            y_offset = 0
            for level in sorted(levels.keys()):
                nodes = levels[level]
                x_offset = -(len(nodes) - 1) / 2
                for i, node in enumerate(nodes):
                    pos[node] = (x_offset + i, -y_offset)
                y_offset += 1
        else:
            # Fall back to spring layout
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        return pos
    
    def _detect_communities(self, G):
        """Detect communities in the graph"""
        
        # Convert to undirected for community detection
        G_undirected = G.to_undirected()
        
        if COMMUNITY_AVAILABLE:
            # Use Louvain method for community detection
            communities = community.best_partition(G_undirected)
            
            # Group nodes by community
            community_dict = {}
            for node, comm_id in communities.items():
                if comm_id not in community_dict:
                    community_dict[comm_id] = []
                community_dict[comm_id].append(node)
        else:
            # Fallback: Simple clustering based on node degree
            nodes = list(G_undirected.nodes())
            degrees = dict(G_undirected.degree())
            
            # Create 4 clusters based on degree quartiles
            sorted_nodes = sorted(nodes, key=lambda n: degrees.get(n, 0))
            n_per_cluster = len(sorted_nodes) // 4
            
            community_dict = {}
            for i in range(4):
                start_idx = i * n_per_cluster
                end_idx = start_idx + n_per_cluster if i < 3 else len(sorted_nodes)
                community_dict[i] = sorted_nodes[start_idx:end_idx]
        
        return community_dict
    
    def _get_cluster_color(self, cluster_id):
        """Get color for cluster based on ID"""
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                 '#F7DC6F', '#BB8FCE', '#85C1E2', '#73C6B6']
        return colors[cluster_id % len(colors)]
    
    def _get_gradient_color(self, value):
        """Get gradient color based on value (0-1)"""
        
        # Create gradient from light to dark blue
        hue = 0.6  # Blue hue
        saturation = 0.3 + value * 0.7
        lightness = 0.8 - value * 0.3
        
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        return f'rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})'
    
    def export_all_graph_ml_visualizations(self, output_dir: str = None):
        """Export all Graph ML visualizations"""
        
        if output_dir is None:
            output_dir = self.results_path / "visualizations" / "graph_ml"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\nExporting Graph ML Visualizations...")
        
        # 1. Expanded Knowledge Graph
        fig1 = self.create_expanded_knowledge_graph()
        fig1.write_html(str(output_dir / "expanded_knowledge_graph.html"))
        try:
            fig1.write_image(str(output_dir / "expanded_knowledge_graph.png"))
        except Exception as e:
            print(f"  [!] Could not export PNG (install kaleido): {str(e)}")
        print("  [OK] Exported Expanded Knowledge Graph")
        
        # 2. Cognitive Benchmark Network
        fig2 = self.create_cognitive_benchmark_network()
        fig2.write_html(str(output_dir / "cognitive_benchmark_network.html"))
        try:
            fig2.write_image(str(output_dir / "cognitive_benchmark_network.png"))
        except Exception:
            pass
        print("  [OK] Exported Cognitive Benchmark Network")
        
        # 3. Learning Trajectory Graph
        fig3 = self.create_learning_trajectory_graph()
        fig3.write_html(str(output_dir / "learning_trajectory_graph.html"))
        try:
            fig3.write_image(str(output_dir / "learning_trajectory_graph.png"))
        except Exception:
            pass
        print("  [OK] Exported Learning Trajectory Graph")
        
        # 4. Multi-Scale Pattern Graph
        fig4 = self.create_multi_scale_pattern_graph()
        fig4.write_html(str(output_dir / "multi_scale_pattern_graph.html"))
        try:
            fig4.write_image(str(output_dir / "multi_scale_pattern_graph.png"))
        except Exception:
            pass
        print("  [OK] Exported Multi-Scale Pattern Graph")
        
        # 5. GNN Embedding Visualization
        fig5 = self.create_gnn_embedding_visualization()
        fig5.write_html(str(output_dir / "gnn_embedding_visualization.html"))
        try:
            fig5.write_image(str(output_dir / "gnn_embedding_visualization.png"))
        except Exception:
            pass
        print("  [OK] Exported GNN Embedding Visualization")
        
        print(f"\nAll Graph ML visualizations exported to: {output_dir}")


def main():
    """Test Graph ML visualizations"""
    
    visualizer = GraphMLVisualizer()
    visualizer.export_all_graph_ml_visualizations()


if __name__ == "__main__":
    main()