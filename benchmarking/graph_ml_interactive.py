"""
Enhanced Interactive Graph ML Visualizations for Cognitive Benchmarking
Using Plotly's advanced network graph capabilities for interactive exploration
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
from datetime import datetime
import colorsys


class InteractiveGraphMLVisualizer:
    """Interactive Graph ML visualizations with enhanced interactivity"""
    
    def __init__(self, results_path: str = "benchmarking/results"):
        self.results_path = Path(results_path)
        self.load_data()
        
        # Custom color scheme for thesis
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
                'skill': '#525252',
                'ai': '#FFA500',
                'architecture': '#2E86AB'
            },
            'edges': {
                'temporal': '#CCCCCC',
                'conceptual': '#FFA500',
                'cognitive': '#7B68EE',
                'learning': '#32CD32',
                'dependency': '#FF6B6B'
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
            if eval_dir.exists():
                for eval_file in eval_dir.glob("*.json"):
                    with open(eval_file, 'r') as f:
                        session_data = json.load(f)
                        session_id = session_data['session_metrics']['session_id']
                        self.evaluation_reports[session_id] = session_data
                        
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.benchmark_report = {}
            self.evaluation_reports = {}
    
    def create_interactive_knowledge_graph(self):
        """Create highly interactive knowledge graph with physics simulation"""
        
        # Build the knowledge graph
        G = nx.Graph()
        
        # Core concept nodes
        core_concepts = {
            'Architectural Design': {'type': 'architecture', 'group': 1, 'size': 40},
            'Cognitive Process': {'type': 'cognitive', 'group': 2, 'size': 40},
            'AI System': {'type': 'ai', 'group': 3, 'size': 40},
            'Learning Outcome': {'type': 'knowledge', 'group': 4, 'size': 35}
        }
        
        # Add core nodes
        for concept, attrs in core_concepts.items():
            G.add_node(concept, **attrs)
        
        # Architecture concepts
        arch_concepts = {
            'Spatial Reasoning': {'connects': ['Architectural Design', 'Cognitive Process'], 'size': 30},
            'Form Generation': {'connects': ['Architectural Design'], 'size': 25},
            'Material Systems': {'connects': ['Architectural Design'], 'size': 25},
            'Environmental Design': {'connects': ['Architectural Design'], 'size': 25},
            'Structural Logic': {'connects': ['Architectural Design'], 'size': 25}
        }
        
        # Cognitive concepts
        cognitive_concepts = {
            'Critical Thinking': {'connects': ['Cognitive Process', 'Learning Outcome'], 'size': 30},
            'Pattern Recognition': {'connects': ['Cognitive Process', 'AI System'], 'size': 28},
            'Problem Solving': {'connects': ['Cognitive Process'], 'size': 25},
            'Metacognition': {'connects': ['Cognitive Process', 'Learning Outcome'], 'size': 28},
            'Visual Analysis': {'connects': ['Cognitive Process', 'Architectural Design'], 'size': 28}
        }
        
        # AI concepts
        ai_concepts = {
            'Socratic Method': {'connects': ['AI System', 'Learning Outcome'], 'size': 30},
            'Cognitive Scaffolding': {'connects': ['AI System', 'Cognitive Process'], 'size': 28},
            'Multi-Agent System': {'connects': ['AI System'], 'size': 25},
            'Knowledge Graphs': {'connects': ['AI System', 'Learning Outcome'], 'size': 25},
            'Adaptive Feedback': {'connects': ['AI System', 'Cognitive Process'], 'size': 28}
        }
        
        # Add all concept nodes and edges
        all_concepts = {**arch_concepts, **cognitive_concepts, **ai_concepts}
        
        for concept, data in all_concepts.items():
            # Determine node type based on connections
            if 'Architectural Design' in data['connects']:
                node_type = 'architecture'
            elif 'Cognitive Process' in data['connects']:
                node_type = 'cognitive'
            elif 'AI System' in data['connects']:
                node_type = 'ai'
            else:
                node_type = 'knowledge'
            
            G.add_node(concept, type=node_type, size=data['size'])
            
            # Add edges
            for target in data['connects']:
                G.add_edge(concept, target, weight=0.8)
        
        # Add user proficiency nodes if available
        if 'proficiency_clusters' in self.benchmark_report:
            for cluster_id, cluster_data in self.benchmark_report['proficiency_clusters'].items():
                prof_level = cluster_data['proficiency_level']
                node_name = f"{prof_level.capitalize()} Learners"
                G.add_node(node_name, 
                          type='user', 
                          size=30,
                          proficiency=prof_level)
                
                # Connect to relevant concepts
                if prof_level == 'expert':
                    G.add_edge(node_name, 'Metacognition', weight=0.9)
                    G.add_edge(node_name, 'Critical Thinking', weight=0.9)
                elif prof_level == 'advanced':
                    G.add_edge(node_name, 'Problem Solving', weight=0.8)
                    G.add_edge(node_name, 'Spatial Reasoning', weight=0.8)
                elif prof_level == 'intermediate':
                    G.add_edge(node_name, 'Pattern Recognition', weight=0.7)
                    G.add_edge(node_name, 'Visual Analysis', weight=0.7)
                else:  # beginner
                    G.add_edge(node_name, 'Cognitive Scaffolding', weight=0.9)
                    G.add_edge(node_name, 'Form Generation', weight=0.6)
        
        # Create interactive visualization
        return self._create_enhanced_interactive_viz(
            G, 
            "Interactive Knowledge Graph - Architecture, Cognition & AI Integration",
            physics_enabled=True
        )
    
    def create_interactive_learning_network(self):
        """Create interactive learning trajectory network"""
        
        G = nx.DiGraph()
        
        # Skill progression levels
        skills = ['Spatial Awareness', 'Design Principles', 'Critical Analysis', 
                 'System Thinking', 'Creative Synthesis']
        levels = ['Foundation', 'Developing', 'Proficient', 'Advanced', 'Expert']
        
        # Create skill nodes at different levels
        pos_map = {}
        for i, skill in enumerate(skills):
            for j, level in enumerate(levels):
                node_id = f"{skill}_{level}"
                G.add_node(node_id, 
                          skill=skill,
                          level=level,
                          level_num=j,
                          type='skill_node',
                          size=15 + j*3)
                pos_map[node_id] = (i * 2, j * 2)
                
                # Add progression edges
                if j > 0:
                    prev_node = f"{skill}_{levels[j-1]}"
                    G.add_edge(prev_node, node_id, 
                              type='progression',
                              weight=0.8)
        
        # Add cross-skill dependencies
        dependencies = [
            ('Spatial Awareness_Proficient', 'Design Principles_Developing', 'prerequisite'),
            ('Design Principles_Proficient', 'Critical Analysis_Developing', 'prerequisite'),
            ('Critical Analysis_Advanced', 'System Thinking_Proficient', 'enables'),
            ('System Thinking_Advanced', 'Creative Synthesis_Proficient', 'enables'),
            ('Spatial Awareness_Advanced', 'Creative Synthesis_Developing', 'supports')
        ]
        
        for from_node, to_node, rel_type in dependencies:
            if from_node in G and to_node in G:
                G.add_edge(from_node, to_node, 
                          type='dependency',
                          relationship=rel_type,
                          weight=0.6)
        
        # Add actual user trajectories if available
        if self.evaluation_reports:
            for i, (session_id, report) in enumerate(list(self.evaluation_reports.items())[:10]):
                metrics = report['session_metrics']
                skill_level = metrics['skill_progression']['final_level']
                
                user_node = f"Learner_{i+1}"
                G.add_node(user_node,
                          type='user',
                          skill_level=skill_level,
                          size=20)
                
                # Connect to skill nodes based on proficiency
                if skill_level == 'expert':
                    target_nodes = ['Creative Synthesis_Expert', 'System Thinking_Expert']
                elif skill_level == 'advanced':
                    target_nodes = ['System Thinking_Advanced', 'Critical Analysis_Advanced']
                elif skill_level == 'intermediate':
                    target_nodes = ['Critical Analysis_Proficient', 'Design Principles_Proficient']
                else:
                    target_nodes = ['Spatial Awareness_Developing', 'Design Principles_Foundation']
                
                for target in target_nodes:
                    if target in G:
                        G.add_edge(user_node, target, 
                                  type='achievement',
                                  weight=0.7)
        
        return self._create_enhanced_interactive_viz(
            G,
            "Interactive Learning Trajectory Network",
            layout_type='hierarchical',
            pos=pos_map
        )
    
    def create_interactive_cognitive_network(self):
        """Create interactive cognitive pattern network"""
        
        G = nx.Graph()
        
        # Cognitive pattern nodes
        patterns = {
            'Deep Thinking': {'centrality': 0.9, 'frequency': 0.8},
            'Surface Learning': {'centrality': 0.3, 'frequency': 0.4},
            'Scaffolded Progress': {'centrality': 0.7, 'frequency': 0.9},
            'Independent Exploration': {'centrality': 0.8, 'frequency': 0.6},
            'Collaborative Learning': {'centrality': 0.6, 'frequency': 0.7},
            'Reflective Practice': {'centrality': 0.85, 'frequency': 0.7},
            'Creative Problem Solving': {'centrality': 0.9, 'frequency': 0.5}
        }
        
        # Add pattern nodes
        for pattern, metrics in patterns.items():
            G.add_node(pattern,
                      type='pattern',
                      centrality=metrics['centrality'],
                      frequency=metrics['frequency'],
                      size=20 + metrics['centrality']*30)
        
        # Add connections based on co-occurrence
        connections = [
            ('Deep Thinking', 'Reflective Practice', 0.9),
            ('Deep Thinking', 'Creative Problem Solving', 0.8),
            ('Scaffolded Progress', 'Deep Thinking', 0.7),
            ('Independent Exploration', 'Creative Problem Solving', 0.8),
            ('Collaborative Learning', 'Scaffolded Progress', 0.6),
            ('Reflective Practice', 'Independent Exploration', 0.7),
            ('Surface Learning', 'Scaffolded Progress', 0.5)
        ]
        
        for source, target, weight in connections:
            G.add_edge(source, target, weight=weight)
        
        # Add user behavior nodes
        behaviors = {
            'Question Asking': ['Deep Thinking', 'Scaffolded Progress'],
            'Hypothesis Testing': ['Independent Exploration', 'Creative Problem Solving'],
            'Pattern Comparison': ['Deep Thinking', 'Reflective Practice'],
            'Concept Integration': ['Collaborative Learning', 'Deep Thinking'],
            'Solution Iteration': ['Creative Problem Solving', 'Reflective Practice']
        }
        
        for behavior, connected_patterns in behaviors.items():
            G.add_node(behavior, type='behavior', size=15)
            for pattern in connected_patterns:
                G.add_edge(behavior, pattern, weight=0.6, type='exhibits')
        
        return self._create_enhanced_interactive_viz(
            G,
            "Interactive Cognitive Pattern Network",
            physics_enabled=True,
            clustering=True
        )
    
    def create_interactive_agent_network(self):
        """Create interactive multi-agent system network"""
        
        G = nx.DiGraph()
        
        # Agent nodes
        agents = {
            'Orchestrator': {'role': 'coordinator', 'interactions': 150, 'centrality': 1.0},
            'Socratic Tutor': {'role': 'educator', 'interactions': 120, 'centrality': 0.9},
            'Domain Expert': {'role': 'knowledge', 'interactions': 80, 'centrality': 0.7},
            'Cognitive Enhancement': {'role': 'support', 'interactions': 60, 'centrality': 0.6},
            'Visual Analyzer': {'role': 'perception', 'interactions': 90, 'centrality': 0.75},
            'Context Manager': {'role': 'memory', 'interactions': 70, 'centrality': 0.65}
        }
        
        # Add agent nodes
        for agent, data in agents.items():
            G.add_node(agent,
                      type='agent',
                      role=data['role'],
                      interactions=data['interactions'],
                      size=20 + data['centrality']*30)
        
        # Agent interactions
        interactions = [
            ('Orchestrator', 'Socratic Tutor', 0.9, 'delegates'),
            ('Orchestrator', 'Domain Expert', 0.8, 'consults'),
            ('Orchestrator', 'Visual Analyzer', 0.85, 'requests'),
            ('Socratic Tutor', 'Cognitive Enhancement', 0.7, 'collaborates'),
            ('Domain Expert', 'Context Manager', 0.6, 'queries'),
            ('Visual Analyzer', 'Domain Expert', 0.7, 'informs'),
            ('Context Manager', 'Socratic Tutor', 0.65, 'updates'),
            ('Cognitive Enhancement', 'Context Manager', 0.6, 'monitors')
        ]
        
        for source, target, weight, interaction_type in interactions:
            G.add_edge(source, target, 
                      weight=weight,
                      interaction_type=interaction_type)
        
        # Add task nodes
        tasks = {
            'Question Generation': ['Socratic Tutor', 'Context Manager'],
            'Visual Analysis': ['Visual Analyzer', 'Domain Expert'],
            'Scaffolding Decision': ['Cognitive Enhancement', 'Orchestrator'],
            'Knowledge Retrieval': ['Domain Expert', 'Context Manager'],
            'Response Synthesis': ['Orchestrator', 'Socratic Tutor']
        }
        
        for task, connected_agents in tasks.items():
            G.add_node(task, type='task', size=15)
            for agent in connected_agents:
                G.add_edge(agent, task, weight=0.5, type='performs')
        
        return self._create_enhanced_interactive_viz(
            G,
            "Interactive Multi-Agent System Network",
            layout_type='circular',
            show_arrows=True
        )
    
    def create_interactive_embedding_space(self):
        """Create interactive GNN embedding visualization"""
        
        # Generate or load embeddings
        n_points = 200
        n_clusters = 4
        
        # Generate clustered data for visualization
        embeddings_2d = []
        labels = []
        proficiency_levels = []
        
        for cluster in range(n_clusters):
            # Generate cluster center
            center_x = np.cos(2 * np.pi * cluster / n_clusters) * 10
            center_y = np.sin(2 * np.pi * cluster / n_clusters) * 10
            
            # Generate points around center
            cluster_size = n_points // n_clusters
            x = np.random.normal(center_x, 2, cluster_size)
            y = np.random.normal(center_y, 2, cluster_size)
            
            embeddings_2d.extend(list(zip(x, y)))
            labels.extend([cluster] * cluster_size)
            
            # Assign proficiency levels
            prof_map = {0: 'beginner', 1: 'intermediate', 2: 'advanced', 3: 'expert'}
            proficiency_levels.extend([prof_map[cluster]] * cluster_size)
        
        embeddings_2d = np.array(embeddings_2d)
        
        # Create traces for each proficiency level
        traces = []
        
        for prof_level in ['beginner', 'intermediate', 'advanced', 'expert']:
            mask = np.array(proficiency_levels) == prof_level
            
            trace = go.Scatter(
                x=embeddings_2d[mask, 0],
                y=embeddings_2d[mask, 1],
                mode='markers',
                name=prof_level.capitalize(),
                marker=dict(
                    size=8,
                    color=self.colors['clusters'][prof_level],
                    line=dict(width=1, color='white'),
                    opacity=0.8
                ),
                text=[f"{prof_level.capitalize()}<br>Point {i}" 
                     for i in range(sum(mask))],
                hoverinfo='text'
            )
            traces.append(trace)
        
        # Add cluster boundaries using convex hulls
        from scipy.spatial import ConvexHull
        
        for cluster in range(n_clusters):
            mask = np.array(labels) == cluster
            cluster_points = embeddings_2d[mask]
            
            if len(cluster_points) > 3:
                hull = ConvexHull(cluster_points)
                hull_points = cluster_points[hull.vertices]
                hull_points = np.vstack([hull_points, hull_points[0]])
                
                trace = go.Scatter(
                    x=hull_points[:, 0],
                    y=hull_points[:, 1],
                    mode='lines',
                    name=f'Cluster {cluster+1}',
                    line=dict(color='rgba(0,0,0,0.2)', width=2, dash='dash'),
                    showlegend=False,
                    hoverinfo='skip'
                )
                traces.append(trace)
        
        # Add transition zones
        for i in range(n_clusters):
            for j in range(i+1, n_clusters):
                # Draw connection between cluster centers
                center_i = embeddings_2d[np.array(labels) == i].mean(axis=0)
                center_j = embeddings_2d[np.array(labels) == j].mean(axis=0)
                
                trace = go.Scatter(
                    x=[center_i[0], center_j[0]],
                    y=[center_i[1], center_j[1]],
                    mode='lines',
                    line=dict(color='rgba(128,128,128,0.3)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                )
                traces.append(trace)
        
        # Create figure
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title="Interactive GNN Embedding Space - Cognitive State Representations",
            xaxis_title="Latent Dimension 1",
            yaxis_title="Latent Dimension 2",
            hovermode='closest',
            width=900,
            height=700,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                zeroline=True,
                zerolinecolor='rgba(200,200,200,0.5)'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                zeroline=True,
                zerolinecolor='rgba(200,200,200,0.5)'
            )
        )
        
        # Add annotations
        fig.add_annotation(
            text="Transition zones indicate learning opportunities",
            xref="paper", yref="paper",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=12, color="gray")
        )
        
        return fig
    
    def _create_enhanced_interactive_viz(self, G, title, layout_type='spring', 
                                       physics_enabled=False, clustering=False,
                                       show_arrows=False, pos=None):
        """Create enhanced interactive visualization with advanced features"""
        
        # Calculate layout
        if pos is None:
            if layout_type == 'spring':
                pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
            elif layout_type == 'circular':
                pos = nx.circular_layout(G)
            elif layout_type == 'hierarchical':
                # Custom hierarchical layout
                pos = self._hierarchical_layout(G)
            else:
                pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Create edge traces with different styles
        edge_traces = []
        edge_types = set([G[u][v].get('type', 'default') for u, v in G.edges()])
        
        for edge_type in edge_types:
            edge_x = []
            edge_y = []
            edge_text = []
            
            for edge in G.edges(data=True):
                if edge[2].get('type', 'default') == edge_type:
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    
                    # Add edge text
                    mid_x = (x0 + x1) / 2
                    mid_y = (y0 + y1) / 2
                    weight = edge[2].get('weight', 0.5)
                    edge_text.append(f"{edge[0]} → {edge[1]}<br>Weight: {weight:.2f}")
            
            edge_color = self.colors['edges'].get(edge_type, '#CCCCCC')
            edge_width = 2 if edge_type in ['cognitive', 'learning'] else 1
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=edge_width, color=edge_color),
                hoverinfo='none',
                showlegend=False,
                opacity=0.6
            )
            edge_traces.append(edge_trace)
        
        # Create node trace with enhanced interactivity
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        node_symbols = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node attributes
            node_data = G.nodes[node]
            size = node_data.get('size', 20)
            node_type = node_data.get('type', 'default')
            
            # Assign color based on type
            if node_type in self.colors['nodes']:
                color = self.colors['nodes'][node_type]
            elif 'proficiency' in node_data:
                color = self.colors['clusters'][node_data['proficiency']]
            else:
                color = '#888888'
            
            node_size.append(size)
            node_color.append(color)
            
            # Create detailed hover text
            hover_text = f"<b>{node}</b><br>"
            hover_text += f"Type: {node_type}<br>"
            
            # Add node degree
            degree = G.degree(node)
            hover_text += f"Connections: {degree}<br>"
            
            # Add additional attributes
            for key, value in node_data.items():
                if key not in ['size', 'color', 'type', 'pos']:
                    if isinstance(value, float):
                        hover_text += f"{key}: {value:.2f}<br>"
                    else:
                        hover_text += f"{key}: {value}<br>"
            
            # Add connected nodes
            neighbors = list(G.neighbors(node))
            if neighbors:
                hover_text += f"Connected to: {', '.join(neighbors[:5])}"
                if len(neighbors) > 5:
                    hover_text += f" (+{len(neighbors)-5} more)"
            
            node_text.append(hover_text)
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[str(node) for node in G.nodes()],
            textposition="top center",
            textfont=dict(size=10, color='black'),
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white'),
                symbol='circle'
            )
        )
        
        # Combine all traces
        all_traces = edge_traces + [node_trace]
        
        # Create figure with enhanced layout
        fig = go.Figure(data=all_traces)
        
        # Update layout with white background and interactive features
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, color='black')),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                showspikes=True,
                spikemode='across',
                spikethickness=1,
                spikecolor='gray'
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                showspikes=True,
                spikemode='across',
                spikethickness=1,
                spikecolor='gray'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=1000,
            height=800,
            clickmode='event+select',
            dragmode='pan'
        )
        
        # Add physics simulation effect using updatemenus
        if physics_enabled:
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=list([
                            dict(
                                args=[{"marker.size": node_size}],
                                label="Reset Size",
                                method="update"
                            ),
                            dict(
                                args=[{"marker.size": [[s*1.5 for s in node_size]]}],
                                label="Expand",
                                method="update"
                            )
                        ]),
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.11,
                        xanchor="left",
                        y=1.1,
                        yanchor="top"
                    ),
                ]
            )
        
        # Add graph statistics annotation
        stats_text = f"Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}"
        if nx.is_connected(G.to_undirected()):
            avg_path_length = nx.average_shortest_path_length(G.to_undirected())
            stats_text += f" | Avg Path Length: {avg_path_length:.2f}"
        
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.99, y=0.01,
            showarrow=False,
            font=dict(size=10, color="gray"),
            xanchor='right'
        )
        
        return fig
    
    def _hierarchical_layout(self, G):
        """Create hierarchical layout for directed graphs"""
        pos = {}
        
        # Get nodes by level if available
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
                    pos[node] = (x_offset + i * 1.5, -y_offset * 2)
                y_offset += 1
        else:
            # Fall back to spring layout
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Add any remaining nodes
        for node in G.nodes():
            if node not in pos:
                pos[node] = (np.random.uniform(-5, 5), np.random.uniform(-5, 5))
        
        return pos
    
    def export_all_interactive_visualizations(self, output_dir: str = None):
        """Export all interactive visualizations"""
        
        if output_dir is None:
            output_dir = self.results_path / "visualizations" / "interactive_graph_ml"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\nExporting Interactive Graph ML Visualizations...")
        
        # Export all visualizations
        visualizations = [
            ("interactive_knowledge_graph", self.create_interactive_knowledge_graph),
            ("interactive_learning_network", self.create_interactive_learning_network),
            ("interactive_cognitive_network", self.create_interactive_cognitive_network),
            ("interactive_agent_network", self.create_interactive_agent_network),
            ("interactive_embedding_space", self.create_interactive_embedding_space)
        ]
        
        for name, create_func in visualizations:
            try:
                fig = create_func()
                fig.write_html(str(output_dir / f"{name}.html"))
                print(f"  [OK] Exported {name}")
            except Exception as e:
                print(f"  [!] Error exporting {name}: {str(e)}")
        
        print(f"\nAll interactive visualizations exported to: {output_dir}")


def main():
    """Test interactive visualizations"""
    visualizer = InteractiveGraphMLVisualizer()
    visualizer.export_all_interactive_visualizations()


if __name__ == "__main__":
    main()