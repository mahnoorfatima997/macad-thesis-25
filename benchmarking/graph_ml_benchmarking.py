# Graph ML Benchmarking Framework for Cognitive Assessment
# This module implements Graph Neural Networks for analyzing user interaction patterns
# and generating cognitive benchmarks based on the thesis requirements

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import GCNConv, GATConv, SAGEConv, global_mean_pool
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
from thesis_colors import (
    THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS, 
    PLOTLY_COLORSCALES, CHART_COLORS, UI_COLORS,
    get_color_palette, get_metric_color, get_proficiency_color, get_agent_color
)

class InteractionGraph:
    """Constructs and manages interaction graphs from user data"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_features = {}
        self.edge_features = {}
        self.temporal_edges = []
        self.conceptual_edges = []
        
    def add_interaction_node(self, 
                           interaction_id: str,
                           interaction_data: Dict[str, Any]):
        """Add an interaction as a node in the graph"""
        
        # Extract node features
        node_attrs = {
            'timestamp': interaction_data['timestamp'],
            'interaction_type': interaction_data['input_type'],
            'agents_used': interaction_data['agents_used'],
            'response_type': interaction_data['response_type'],
            'cognitive_load': self._calculate_cognitive_load(interaction_data),
            'learning_indicator': self._calculate_learning_indicator(interaction_data),
            'engagement_score': self._calculate_engagement_score(interaction_data),
            'skill_level': interaction_data['student_skill_level'],
            'prevents_offloading': interaction_data['prevents_cognitive_offloading'],
            'encourages_thinking': interaction_data['encourages_deep_thinking'],
            'provides_scaffolding': interaction_data['provides_scaffolding']
        }
        
        self.graph.add_node(interaction_id, **node_attrs)
        self.node_features[interaction_id] = self._encode_node_features(node_attrs)
        
    def add_temporal_edge(self, source_id: str, target_id: str):
        """Add temporal edge between consecutive interactions"""
        
        edge_attrs = {
            'edge_type': 'temporal',
            'weight': 1.0
        }
        
        self.graph.add_edge(source_id, target_id, **edge_attrs)
        self.temporal_edges.append((source_id, target_id))
        
    def add_conceptual_edge(self, source_id: str, target_id: str, similarity: float):
        """Add conceptual edge based on content similarity"""
        
        if similarity > 0.5:  # Threshold for conceptual connection
            edge_attrs = {
                'edge_type': 'conceptual',
                'weight': similarity
            }
            
            self.graph.add_edge(source_id, target_id, **edge_attrs)
            self.conceptual_edges.append((source_id, target_id))
    
    def _calculate_cognitive_load(self, interaction: Dict) -> float:
        """Calculate cognitive load from interaction metrics"""
        
        # Factors that increase cognitive load
        input_complexity = len(interaction['student_input'].split()) / 50.0
        response_complexity = len(interaction['agent_response'].split()) / 100.0
        multi_agent = 1.0 if interaction['multi_agent_coordination'] else 0.5
        
        # Normalize to 0-1 scale
        cognitive_load = min((input_complexity + response_complexity) * multi_agent, 1.0)
        
        return cognitive_load
    
    def _calculate_learning_indicator(self, interaction: Dict) -> float:
        """Calculate learning effectiveness indicator"""
        
        factors = [
            interaction['prevents_cognitive_offloading'],
            interaction['encourages_deep_thinking'],
            interaction['provides_scaffolding'],
            interaction['maintains_engagement'],
            interaction['adapts_to_skill_level']
        ]
        
        return sum(factors) / len(factors)
    
    def _calculate_engagement_score(self, interaction: Dict) -> float:
        """Calculate user engagement score"""
        
        # Based on input characteristics and response patterns
        question_asked = 1.0 if '?' in interaction['student_input'] else 0.5
        elaborative_input = 1.0 if interaction['input_length'] > 10 else 0.3
        maintained_engagement = 1.0 if interaction['maintains_engagement'] else 0.5
        
        return (question_asked + elaborative_input + maintained_engagement) / 3.0
    
    def _encode_node_features(self, attrs: Dict) -> np.ndarray:
        """Encode node attributes as feature vector"""
        
        # Categorical encodings
        skill_encoding = {
            'beginner': [1, 0, 0],
            'intermediate': [0, 1, 0],
            'advanced': [0, 0, 1]
        }
        
        input_type_encoding = {
            'feedback_request': [1, 0, 0, 0, 0],
            'improvement_seeking': [0, 1, 0, 0, 0],
            'knowledge_seeking': [0, 0, 1, 0, 0],
            'confusion_expression': [0, 0, 0, 1, 0],
            'general_statement': [0, 0, 0, 0, 1]
        }
        
        # Combine features
        features = []
        
        # Numerical features
        features.extend([
            attrs['cognitive_load'],
            attrs['learning_indicator'],
            attrs['engagement_score'],
            float(attrs['prevents_offloading']),
            float(attrs['encourages_thinking']),
            float(attrs['provides_scaffolding'])
        ])
        
        # Categorical features
        features.extend(skill_encoding.get(attrs['skill_level'], [0, 0, 0]))
        
        # Agent usage (binary encoding for each agent type)
        agent_types = ['socratic', 'cognitive', 'knowledge', 'context']
        agent_encoding = [1.0 if agent in str(attrs['agents_used']) else 0.0 for agent in agent_types]
        features.extend(agent_encoding)
        
        return np.array(features, dtype=np.float32)
    
    def to_pytorch_geometric(self) -> Data:
        """Convert NetworkX graph to PyTorch Geometric format"""
        
        # Get node features
        node_ids = list(self.graph.nodes())
        x = torch.tensor([self.node_features[nid] for nid in node_ids], dtype=torch.float)
        
        # Get edge indices
        edge_index = []
        edge_attr = []
        
        for source, target in self.graph.edges():
            source_idx = node_ids.index(source)
            target_idx = node_ids.index(target)
            edge_index.append([source_idx, target_idx])
            
            # Edge features
            edge_data = self.graph[source][target]
            edge_attr.append([edge_data['weight']])
        
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor(edge_attr, dtype=torch.float)
        
        return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)


class CognitiveGNN(nn.Module):
    """Graph Neural Network for cognitive pattern analysis"""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_heads: int = 4):
        super(CognitiveGNN, self).__init__()
        
        # Multi-layer GNN architecture
        self.conv1 = GATConv(input_dim, hidden_dim, heads=num_heads, concat=True)
        self.conv2 = SAGEConv(hidden_dim * num_heads, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, output_dim)
        )
        
    def forward(self, x, edge_index, batch=None):
        # First GAT layer with multi-head attention
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        
        # GraphSAGE layer for neighborhood aggregation
        x = F.relu(self.conv2(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        
        # GCN layer for final feature extraction
        x = self.conv3(x, edge_index)
        
        # Global pooling for graph-level representation
        if batch is not None:
            x = global_mean_pool(x, batch)
        
        # Classification
        return self.classifier(x)


class CognitiveBenchmarkGenerator:
    """Generates cognitive benchmarks from analyzed interaction patterns"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.interaction_graphs = []
        self.gnn_model = None
        self.scaler = StandardScaler()
        self.proficiency_clusters = None
        self.benchmark_profiles = {}
        self.n_clusters = 3  # Default value, will be updated during clustering
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def process_session_data(self, session_file: str) -> InteractionGraph:
        """Process session data into interaction graph"""
        
        # Load interaction data
        df = pd.read_csv(session_file)
        
        # Create interaction graph
        graph = InteractionGraph()
        
        # Add nodes for each interaction
        for idx, row in df.iterrows():
            interaction_id = f"{row['session_id']}_{row['interaction_number']}"
            graph.add_interaction_node(interaction_id, row.to_dict())
        
        # Add temporal edges
        for i in range(len(df) - 1):
            source_id = f"{df.iloc[i]['session_id']}_{df.iloc[i]['interaction_number']}"
            target_id = f"{df.iloc[i+1]['session_id']}_{df.iloc[i+1]['interaction_number']}"
            graph.add_temporal_edge(source_id, target_id)
        
        # Add conceptual edges based on similarity
        # (Simplified - in practice, use embeddings for semantic similarity)
        for i in range(len(df)):
            for j in range(i + 1, min(i + 5, len(df))):  # Look ahead 5 interactions
                source_row = df.iloc[i]
                target_row = df.iloc[j]
                
                # Calculate simple similarity based on shared cognitive flags
                source_flags = set(eval(source_row['cognitive_flags']) if isinstance(source_row['cognitive_flags'], str) else [])
                target_flags = set(eval(target_row['cognitive_flags']) if isinstance(target_row['cognitive_flags'], str) else [])
                
                if source_flags and target_flags:
                    similarity = len(source_flags.intersection(target_flags)) / len(source_flags.union(target_flags))
                    
                    source_id = f"{source_row['session_id']}_{source_row['interaction_number']}"
                    target_id = f"{target_row['session_id']}_{target_row['interaction_number']}"
                    graph.add_conceptual_edge(source_id, target_id, similarity)
        
        return graph
    
    def train_gnn_model(self, graphs: List[InteractionGraph], epochs: int = 100):
        """Train GNN model on interaction graphs"""
        
        # Convert graphs to PyTorch format
        data_list = [g.to_pytorch_geometric() for g in graphs]
        
        # Create data loader
        loader = DataLoader(data_list, batch_size=32, shuffle=True)
        
        # Initialize model
        input_dim = data_list[0].x.shape[1]
        hidden_dim = 64
        output_dim = 3  # Beginner, Intermediate, Advanced proficiency levels
        
        self.gnn_model = CognitiveGNN(input_dim, hidden_dim, output_dim)
        optimizer = torch.optim.Adam(self.gnn_model.parameters(), lr=0.001)
        
        # Training loop
        self.gnn_model.train()
        for epoch in range(epochs):
            total_loss = 0
            
            for batch in loader:
                optimizer.zero_grad()
                
                # Forward pass
                out = self.gnn_model(batch.x, batch.edge_index, batch.batch)
                
                # Create pseudo-labels based on learning indicators
                # (In practice, use actual labeled data)
                labels = self._generate_pseudo_labels(batch)
                
                # Calculate loss
                loss = F.cross_entropy(out, labels)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if epoch % 20 == 0:
                print(f"Epoch {epoch}, Loss: {total_loss / len(loader):.4f}")
    
    def _generate_pseudo_labels(self, batch) -> torch.Tensor:
        """Generate pseudo-labels for training (placeholder for actual labels)"""
        
        # Extract average learning indicators per graph
        learning_indicators = []
        
        for i in range(batch.num_graphs):
            mask = batch.batch == i
            graph_features = batch.x[mask]
            
            # Learning indicator is at index 1 in feature vector
            avg_learning = graph_features[:, 1].mean().item()
            
            # Map to proficiency level
            if avg_learning < 0.4:
                label = 0  # Beginner
            elif avg_learning < 0.7:
                label = 1  # Intermediate
            else:
                label = 2  # Advanced
            
            learning_indicators.append(label)
        
        return torch.tensor(learning_indicators, dtype=torch.long)
    
    def generate_proficiency_clusters(self, graphs: List[InteractionGraph]) -> Dict[str, Any]:
        """Cluster users by cognitive proficiency patterns"""
        
        # Extract graph-level features
        graph_features = []
        
        for graph in graphs:
            features = self._extract_graph_features(graph)
            graph_features.append(features)
        
        # Normalize features
        graph_features = np.array(graph_features)
        graph_features_scaled = self.scaler.fit_transform(graph_features)
        
        # Handle cases with insufficient data
        if len(graphs) < 3:
            # For very small datasets, assign proficiency based on metrics
            cluster_labels = []
            for i, features in enumerate(graph_features):
                # Simple rule-based assignment
                avg_learning = features[1]  # learning effectiveness
                avg_offload_prevention = features[3]  # cognitive offloading prevention
                
                if avg_learning > 0.7 and avg_offload_prevention > 0.7:
                    cluster_labels.append(2)  # Advanced
                elif avg_learning > 0.5 or avg_offload_prevention > 0.5:
                    cluster_labels.append(1)  # Intermediate
                else:
                    cluster_labels.append(0)  # Beginner
            
            cluster_labels = np.array(cluster_labels)
            optimal_clusters = len(np.unique(cluster_labels))
            self.n_clusters = optimal_clusters  # Store for visualization
            
            # Create mock clustering for consistency
            self.proficiency_clusters = KMeans(n_clusters=optimal_clusters, random_state=42)
            self.proficiency_clusters.fit(graph_features_scaled)
            self.proficiency_clusters.labels_ = cluster_labels
        else:
            # Find optimal number of clusters for larger datasets
            silhouette_scores = []
            for n_clusters in range(2, min(10, len(graphs))):
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                labels = kmeans.fit_predict(graph_features_scaled)
                score = silhouette_score(graph_features_scaled, labels)
                silhouette_scores.append(score)
            
            # Use best number of clusters
            optimal_clusters = silhouette_scores.index(max(silhouette_scores)) + 2
            self.n_clusters = optimal_clusters  # Store for visualization
            self.proficiency_clusters = KMeans(n_clusters=optimal_clusters, random_state=42)
            cluster_labels = self.proficiency_clusters.fit_predict(graph_features_scaled)
        
        # Analyze cluster characteristics
        cluster_profiles = {}
        for cluster_id in range(optimal_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_features = graph_features[cluster_mask]
            
            profile = {
                'cluster_id': cluster_id,
                'size': np.sum(cluster_mask),
                'avg_cognitive_load': np.mean(cluster_features[:, 0]),
                'avg_learning_effectiveness': np.mean(cluster_features[:, 1]),
                'avg_engagement': np.mean(cluster_features[:, 2]),
                'cognitive_offloading_prevention': np.mean(cluster_features[:, 3]),
                'deep_thinking_rate': np.mean(cluster_features[:, 4]),
                'scaffolding_effectiveness': np.mean(cluster_features[:, 5])
            }
            
            # Assign proficiency level based on metrics
            if profile['avg_learning_effectiveness'] > 0.7 and profile['deep_thinking_rate'] > 0.6:
                profile['proficiency_level'] = 'advanced'
            elif profile['avg_learning_effectiveness'] > 0.5:
                profile['proficiency_level'] = 'intermediate'
            else:
                profile['proficiency_level'] = 'beginner'
            
            cluster_profiles[cluster_id] = profile
        
        return {
            'n_clusters': optimal_clusters,
            'cluster_profiles': cluster_profiles,
            'cluster_labels': cluster_labels.tolist()
        }
    
    def _extract_graph_features(self, graph: InteractionGraph) -> np.ndarray:
        """Extract graph-level features for clustering"""
        
        nodes = list(graph.graph.nodes())
        
        if not nodes:
            return np.zeros(10)
        
        # Aggregate node features
        cognitive_loads = [graph.graph.nodes[n]['cognitive_load'] for n in nodes]
        learning_indicators = [graph.graph.nodes[n]['learning_indicator'] for n in nodes]
        engagement_scores = [graph.graph.nodes[n]['engagement_score'] for n in nodes]
        prevents_offloading = [graph.graph.nodes[n]['prevents_offloading'] for n in nodes]
        encourages_thinking = [graph.graph.nodes[n]['encourages_thinking'] for n in nodes]
        provides_scaffolding = [graph.graph.nodes[n]['provides_scaffolding'] for n in nodes]
        
        # Graph structural features
        density = nx.density(graph.graph)
        avg_degree = np.mean([d for n, d in graph.graph.degree()])
        
        # Temporal progression features
        temporal_coherence = len(graph.temporal_edges) / max(len(nodes) - 1, 1)
        conceptual_connectivity = len(graph.conceptual_edges) / max(len(nodes), 1)
        
        features = [
            np.mean(cognitive_loads),
            np.mean(learning_indicators),
            np.mean(engagement_scores),
            np.mean(prevents_offloading),
            np.mean(encourages_thinking),
            np.mean(provides_scaffolding),
            density,
            avg_degree,
            temporal_coherence,
            conceptual_connectivity
        ]
        
        return np.array(features)
    
    def create_benchmark_profiles(self, cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create benchmark profiles for each proficiency level"""
        
        benchmarks = {}
        
        for cluster_id, profile in cluster_analysis['cluster_profiles'].items():
            proficiency = profile['proficiency_level']
            
            benchmark = {
                'proficiency_level': proficiency,
                'target_metrics': {
                    'cognitive_load_range': self._get_range(profile['avg_cognitive_load']),
                    'learning_effectiveness_min': max(profile['avg_learning_effectiveness'] - 0.1, 0),
                    'engagement_min': max(profile['avg_engagement'] - 0.1, 0),
                    'cognitive_offloading_prevention_min': max(profile['cognitive_offloading_prevention'] - 0.1, 0),
                    'deep_thinking_rate_min': max(profile['deep_thinking_rate'] - 0.1, 0),
                    'scaffolding_effectiveness_min': max(profile['scaffolding_effectiveness'] - 0.1, 0)
                },
                'recommended_strategies': self._get_recommended_strategies(profile),
                'progression_indicators': self._get_progression_indicators(proficiency)
            }
            
            benchmarks[proficiency] = benchmark
        
        self.benchmark_profiles = benchmarks
        return benchmarks
    
    def _get_range(self, value: float, margin: float = 0.15) -> Tuple[float, float]:
        """Get acceptable range around a value"""
        return (max(value - margin, 0), min(value + margin, 1))
    
    def _get_recommended_strategies(self, profile: Dict) -> List[str]:
        """Get recommended teaching strategies based on profile"""
        
        strategies = []
        
        if profile['cognitive_offloading_prevention'] < 0.5:
            strategies.append("Increase Socratic questioning to prevent direct answer seeking")
        
        if profile['deep_thinking_rate'] < 0.6:
            strategies.append("Incorporate more 'why' and 'how' questions to encourage reflection")
        
        if profile['scaffolding_effectiveness'] < 0.5:
            strategies.append("Provide more structured guidance with progressive complexity")
        
        if profile['avg_engagement'] < 0.6:
            strategies.append("Use more interactive elements and personalized challenges")
        
        return strategies
    
    def _get_progression_indicators(self, proficiency: str) -> Dict[str, Any]:
        """Define indicators for progression to next level"""
        
        progression_map = {
            'beginner': {
                'next_level': 'intermediate',
                'requirements': {
                    'sustained_deep_thinking': 0.6,
                    'reduced_cognitive_offloading': 0.7,
                    'independent_problem_solving': 0.5,
                    'conceptual_connections': 0.4
                }
            },
            'intermediate': {
                'next_level': 'advanced',
                'requirements': {
                    'sustained_deep_thinking': 0.8,
                    'reduced_cognitive_offloading': 0.85,
                    'independent_problem_solving': 0.7,
                    'conceptual_connections': 0.7
                }
            },
            'advanced': {
                'next_level': 'expert',
                'requirements': {
                    'sustained_deep_thinking': 0.9,
                    'reduced_cognitive_offloading': 0.95,
                    'independent_problem_solving': 0.85,
                    'conceptual_connections': 0.85
                }
            }
        }
        
        return progression_map.get(proficiency, {})
    
    def visualize_cognitive_patterns(self, graphs: List[InteractionGraph], save_path: str = "./benchmarking/visualizations"):
        """Generate visualizations of cognitive patterns"""
        
        Path(save_path).mkdir(parents=True, exist_ok=True)
        
        # 1. Cognitive Load Distribution
        plt.figure(figsize=(10, 6))
        cognitive_loads = []
        for graph in graphs:
            for node in graph.graph.nodes():
                cognitive_loads.append(graph.graph.nodes[node]['cognitive_load'])
        
        plt.hist(cognitive_loads, bins=30, alpha=0.7, color=THESIS_COLORS['primary_purple'], edgecolor=THESIS_COLORS['primary_dark'])
        plt.xlabel('Cognitive Load')
        plt.ylabel('Frequency')
        plt.title('Distribution of Cognitive Load Across All Interactions')
        plt.savefig(f"{save_path}/cognitive_load_distribution.png")
        plt.close()
        
        # 2. Learning Effectiveness Over Time
        plt.figure(figsize=(12, 6))
        for i, graph in enumerate(graphs[:5]):  # First 5 sessions
            nodes = list(graph.graph.nodes())
            learning_indicators = [graph.graph.nodes[n]['learning_indicator'] for n in nodes]
            plt.plot(learning_indicators, label=f'Session {i+1}', alpha=0.7)
        
        plt.xlabel('Interaction Number')
        plt.ylabel('Learning Effectiveness')
        plt.title('Learning Effectiveness Progression Across Sessions')
        plt.legend()
        plt.savefig(f"{save_path}/learning_progression.png")
        plt.close()
        
        # 3. Agent Usage Patterns
        agent_usage = {'socratic': 0, 'cognitive': 0, 'knowledge': 0, 'context': 0}
        for graph in graphs:
            for node in graph.graph.nodes():
                agents = graph.graph.nodes[node]['agents_used']
                for agent_type in agent_usage:
                    if agent_type in str(agents).lower():
                        agent_usage[agent_type] += 1
        
        plt.figure(figsize=(8, 8))
        plt.pie(agent_usage.values(), labels=agent_usage.keys(), autopct='%1.1f%%')
        plt.title('Distribution of Agent Usage')
        plt.savefig(f"{save_path}/agent_usage_distribution.png")
        plt.close()
        
        # 4. Proficiency Cluster Visualization
        if hasattr(self, 'proficiency_clusters') and self.proficiency_clusters and len(graphs) > 1:
            try:
                graph_features = [self._extract_graph_features(g) for g in graphs]
                graph_features = np.array(graph_features)
                
                # Check if we have enough variance for PCA
                if len(graphs) >= 2:
                    graph_features_scaled = self.scaler.transform(graph_features)
                    
                    # Reduce to 2D for visualization
                    from sklearn.decomposition import PCA
                    # Use min of 2 or number of samples for PCA components
                    n_components = min(2, len(graphs))
                    pca = PCA(n_components=n_components)
                    features_2d = pca.fit_transform(graph_features_scaled)
                    
                    plt.figure(figsize=(10, 8))
                    
                    if hasattr(self.proficiency_clusters, 'labels_'):
                        labels = self.proficiency_clusters.labels_
                    else:
                        labels = self.proficiency_clusters.predict(graph_features_scaled)
                    
                    # Create custom colormap from thesis colors
                    from matplotlib.colors import LinearSegmentedColormap, hex2color
                    thesis_colors_rgb = [
                        hex2color(get_proficiency_color('beginner')),
                        hex2color(get_proficiency_color('intermediate')),
                        hex2color(get_proficiency_color('advanced')),
                        hex2color(get_proficiency_color('expert'))
                    ]
                    thesis_cmap = LinearSegmentedColormap.from_list('thesis_prof', thesis_colors_rgb[:self.n_clusters])
                    
                    if n_components == 2:
                        scatter = plt.scatter(features_2d[:, 0], features_2d[:, 1], c=labels, cmap=thesis_cmap, alpha=0.7)
                    else:
                        # For 1D case, create artificial y-axis
                        scatter = plt.scatter(features_2d[:, 0], np.zeros_like(features_2d[:, 0]), c=labels, cmap=thesis_cmap, alpha=0.7)
                    
                    plt.colorbar(scatter)
                    plt.xlabel('First Principal Component')
                    plt.ylabel('Second Principal Component' if n_components == 2 else 'Sessions')
                    plt.title('User Proficiency Clusters')
                    
                    # Add cluster centers only if we have real clustering
                    if hasattr(self.proficiency_clusters, 'cluster_centers_') and len(graphs) >= 3:
                        centers_scaled = self.proficiency_clusters.cluster_centers_
                        centers_2d = pca.transform(centers_scaled)
                        if n_components == 2:
                            plt.scatter(centers_2d[:, 0], centers_2d[:, 1], c='red', marker='x', s=200, linewidths=3)
                        else:
                            plt.scatter(centers_2d[:, 0], np.zeros_like(centers_2d[:, 0]), c='red', marker='x', s=200, linewidths=3)
                    
                    plt.savefig(f"{save_path}/proficiency_clusters.png")
                    plt.close()
            except Exception as e:
                print(f"Warning: Could not generate proficiency cluster visualization: {str(e)}")
    
    def generate_benchmark_report(self, output_path: str = "./benchmarking/benchmark_report.json"):
        """Generate comprehensive benchmark report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'benchmark_profiles': self.benchmark_profiles,
            'cluster_analysis': {
                'n_clusters': len(self.benchmark_profiles),
                'proficiency_distribution': {}
            },
            'recommendations': {
                'system_improvements': [],
                'pedagogical_strategies': [],
                'future_research': []
            }
        }
        
        # Add proficiency distribution
        for profile in self.benchmark_profiles.values():
            level = profile['proficiency_level']
            report['cluster_analysis']['proficiency_distribution'][level] = \
                report['cluster_analysis']['proficiency_distribution'].get(level, 0) + 1
        
        # System improvement recommendations
        avg_prevention = np.mean([p['target_metrics']['cognitive_offloading_prevention_min'] 
                                 for p in self.benchmark_profiles.values()])
        
        if avg_prevention < 0.7:
            report['recommendations']['system_improvements'].append(
                "Strengthen Socratic agent to better prevent cognitive offloading"
            )
        
        avg_thinking = np.mean([p['target_metrics']['deep_thinking_rate_min'] 
                               for p in self.benchmark_profiles.values()])
        
        if avg_thinking < 0.6:
            report['recommendations']['system_improvements'].append(
                "Enhance question generation to promote deeper critical thinking"
            )
        
        # Pedagogical strategy recommendations
        report['recommendations']['pedagogical_strategies'] = [
            "Implement adaptive difficulty based on proficiency level",
            "Provide phase-specific scaffolding (Ideation → Visualization → Materialization)",
            "Use multi-agent coordination for complex design challenges",
            "Track metacognitive development through reflection prompts"
        ]
        
        # Future research directions
        report['recommendations']['future_research'] = [
            "Investigate long-term retention of spatial reasoning skills",
            "Compare cognitive load patterns across different design domains",
            "Analyze the impact of AI mentorship on creative confidence",
            "Study the transfer of learned skills to professional practice"
        ]
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[REPORT] Benchmark report generated: {output_path}")
        
        return report
    
    def save_model(self, path: str):
        """Save trained model and benchmarks"""
        
        model_data = {
            'gnn_model_state': self.gnn_model.state_dict() if self.gnn_model else None,
            'scaler': self.scaler,
            'proficiency_clusters': self.proficiency_clusters,
            'benchmark_profiles': self.benchmark_profiles
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model and benchmarks"""
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.scaler = model_data['scaler']
        self.proficiency_clusters = model_data['proficiency_clusters']
        self.benchmark_profiles = model_data['benchmark_profiles']
        
        # Reconstruct GNN model if state dict exists
        if model_data['gnn_model_state']:
            # You'll need to know the model dimensions
            # This is a simplified version
            self.gnn_model = CognitiveGNN(input_dim=16, hidden_dim=64, output_dim=3)
            self.gnn_model.load_state_dict(model_data['gnn_model_state'])
        
        print(f"Model loaded from {path}")


def main():
    """Example usage of the benchmarking system"""
    
    # Initialize benchmark generator
    generator = CognitiveBenchmarkGenerator()
    
    # Process session data
    data_dir = Path("./thesis_data")
    session_files = list(data_dir.glob("interactions_*.csv"))
    
    if not session_files:
        print("No interaction data found. Please run some sessions first.")
        return
    
    print(f"Found {len(session_files)} session files")
    
    # Convert sessions to graphs
    graphs = []
    for session_file in session_files:
        graph = generator.process_session_data(str(session_file))
        graphs.append(graph)
    
    # Train GNN model
    print("\nTraining GNN model...")
    generator.train_gnn_model(graphs, epochs=50)
    
    # Generate proficiency clusters
    print("\nGenerating proficiency clusters...")
    cluster_analysis = generator.generate_proficiency_clusters(graphs)
    
    print(f"\nFound {cluster_analysis['n_clusters']} proficiency clusters:")
    for cluster_id, profile in cluster_analysis['cluster_profiles'].items():
        print(f"  Cluster {cluster_id}: {profile['proficiency_level']} "
              f"(n={profile['size']}, learning_eff={profile['avg_learning_effectiveness']:.2f})")
    
    # Create benchmarks
    print("\nCreating benchmark profiles...")
    benchmarks = generator.create_benchmark_profiles(cluster_analysis)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generator.visualize_cognitive_patterns(graphs)
    
    # Generate final report
    print("\nGenerating benchmark report...")
    report = generator.generate_benchmark_report()
    
    # Save model
    generator.save_model("./benchmarking/cognitive_benchmark_model.pkl")
    
    print("\n[OK] Benchmarking complete!")
    print(f"   - Analyzed {len(graphs)} sessions")
    print(f"   - Created {len(benchmarks)} proficiency benchmarks")
    print("   - Visualizations saved to ./benchmarking/visualizations/")
    print("   - Report saved to ./benchmarking/benchmark_report.json")


if __name__ == "__main__":
    main()