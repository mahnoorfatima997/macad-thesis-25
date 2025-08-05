"""
MEGA Architectural Mentor - Advanced Graph ML Integration with Linkography
Integrates temporal graph neural networks, anomaly detection, and pattern discovery
with linkography data for enhanced cognitive assessment
"""

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.data import Data, TemporalData, HeteroData
    from torch_geometric.nn import GCNConv, GATConv, TransformerConv, global_mean_pool
    from torch_geometric.nn.conv import MessagePassing
    from torch_geometric.utils import negative_sampling
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create dummy classes for when PyTorch is not available
    class nn:
        class Module: pass
        class Linear: pass
        class Dropout: pass
        class MultiheadAttention: pass
    class F:
        relu = lambda x: x
        softmax = lambda x, dim: x
    class torch:
        tensor = lambda x, dtype=None: np.array(x)
        no_grad = lambda: None
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
import pickle

from linkography_types import (
    Linkograph, DesignMove, LinkographLink, LinkographPattern,
    LinkographSession, CognitiveLinkographMapping
)


class LinkographToTemporalGraph:
    """Converts linkography data to temporal graph format for Graph ML analysis"""
    
    def __init__(self):
        self.node_features_dim = 32
        self.edge_features_dim = 8
        
    def convert_to_temporal_graph(self, linkograph_session: LinkographSession) -> TemporalData:
        """Convert a linkography session to PyTorch Geometric TemporalData format"""
        
        # Aggregate all moves from all linkographs in session
        all_moves = []
        all_links = []
        
        for linkograph in linkograph_session.linkographs:
            all_moves.extend(linkograph.moves)
            all_links.extend(linkograph.links)
        
        # Create node features from design moves
        node_features = self._extract_node_features(all_moves)
        
        # Create edge indices and features from links
        edge_index, edge_attr, edge_time = self._extract_edge_data(all_links, all_moves)
        
        # Create temporal data object
        temporal_data = TemporalData(
            x=node_features,
            edge_index=edge_index,
            edge_attr=edge_attr,
            edge_time=edge_time,
            num_nodes=len(all_moves)
        )
        
        return temporal_data
    
    def _extract_node_features(self, moves: List[DesignMove]) -> torch.Tensor:
        """Extract feature vectors from design moves"""
        features = []
        
        for move in moves:
            # Basic features
            phase_encoding = self._encode_phase(move.phase)
            move_type_encoding = self._encode_move_type(move.move_type)
            modality_encoding = self._encode_modality(move.modality)
            
            # Cognitive features
            cognitive_load = move.cognitive_load if move.cognitive_load else 0.5
            
            # Temporal features
            normalized_time = move.timestamp / max([m.timestamp for m in moves])
            
            # Combine features
            feature_vector = np.concatenate([
                phase_encoding,
                move_type_encoding,
                modality_encoding,
                [cognitive_load, normalized_time]
            ])
            
            features.append(feature_vector)
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _extract_edge_data(self, links: List[LinkographLink], moves: List[DesignMove]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Extract edge indices, attributes, and timestamps"""
        edge_indices = []
        edge_attrs = []
        edge_times = []
        
        # Create move ID to index mapping
        move_id_to_idx = {move.id: idx for idx, move in enumerate(moves)}
        
        for link in links:
            if link.source_move in move_id_to_idx and link.target_move in move_id_to_idx:
                source_idx = move_id_to_idx[link.source_move]
                target_idx = move_id_to_idx[link.target_move]
                
                edge_indices.append([source_idx, target_idx])
                
                # Edge attributes
                edge_attr = [
                    link.strength,
                    link.confidence,
                    link.semantic_similarity,
                    float(link.temporal_distance),
                    self._encode_link_type(link.link_type)
                ]
                edge_attrs.append(edge_attr)
                
                # Edge time (use target move's timestamp)
                edge_times.append(moves[target_idx].timestamp)
        
        edge_index = torch.tensor(edge_indices, dtype=torch.long).t()
        edge_attr = torch.tensor(edge_attrs, dtype=torch.float32)
        edge_time = torch.tensor(edge_times, dtype=torch.float32)
        
        return edge_index, edge_attr, edge_time
    
    def _encode_phase(self, phase: str) -> np.ndarray:
        """One-hot encode design phase"""
        phases = ['ideation', 'visualization', 'materialization']
        encoding = np.zeros(len(phases))
        if phase in phases:
            encoding[phases.index(phase)] = 1.0
        return encoding
    
    def _encode_move_type(self, move_type: str) -> np.ndarray:
        """One-hot encode move type"""
        types = ['analysis', 'synthesis', 'evaluation', 'transformation', 'reflection']
        encoding = np.zeros(len(types))
        if move_type in types:
            encoding[types.index(move_type)] = 1.0
        return encoding
    
    def _encode_modality(self, modality: str) -> np.ndarray:
        """One-hot encode modality"""
        modalities = ['text', 'sketch', 'gesture', 'verbal']
        encoding = np.zeros(len(modalities))
        if modality in modalities:
            encoding[modalities.index(modality)] = 1.0
        return encoding
    
    def _encode_link_type(self, link_type: str) -> float:
        """Encode link type as scalar"""
        types = {'backward': -1.0, 'forward': 1.0, 'lateral': 0.0}
        return types.get(link_type, 0.0)


class TemporalLinkographGNN(nn.Module):
    """Temporal Graph Neural Network for linkography analysis"""
    
    def __init__(self, node_features_dim: int, edge_features_dim: int, hidden_dim: int = 64):
        super().__init__()
        
        # Temporal convolution layers
        self.conv1 = TransformerConv(node_features_dim, hidden_dim, edge_dim=edge_features_dim)
        self.conv2 = TransformerConv(hidden_dim, hidden_dim, edge_dim=edge_features_dim)
        self.conv3 = TransformerConv(hidden_dim, hidden_dim, edge_dim=edge_features_dim)
        
        # Temporal attention mechanism
        self.temporal_attention = nn.MultiheadAttention(hidden_dim, num_heads=4)
        
        # Output layers for different tasks
        self.pattern_classifier = nn.Linear(hidden_dim, 4)  # chunk, web, sawtooth, orphan
        self.cognitive_predictor = nn.Linear(hidden_dim, 6)  # 6 cognitive metrics
        self.anomaly_detector = nn.Linear(hidden_dim, 1)  # anomaly score
        
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x, edge_index, edge_attr, batch=None):
        # First GNN layer
        x = self.conv1(x, edge_index, edge_attr)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Second GNN layer
        x = self.conv2(x, edge_index, edge_attr)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Third GNN layer
        x = self.conv3(x, edge_index, edge_attr)
        
        # Apply temporal attention
        x_reshaped = x.unsqueeze(0)  # Add sequence dimension
        x_attended, _ = self.temporal_attention(x_reshaped, x_reshaped, x_reshaped)
        x = x_attended.squeeze(0)
        
        # Global pooling for graph-level representation
        if batch is not None:
            graph_embedding = global_mean_pool(x, batch)
        else:
            graph_embedding = x.mean(dim=0, keepdim=True)
        
        # Task-specific outputs
        pattern_logits = self.pattern_classifier(graph_embedding)
        cognitive_scores = torch.sigmoid(self.cognitive_predictor(graph_embedding))
        anomaly_score = torch.sigmoid(self.anomaly_detector(graph_embedding))
        
        return {
            'node_embeddings': x,
            'graph_embedding': graph_embedding,
            'pattern_logits': pattern_logits,
            'cognitive_scores': cognitive_scores,
            'anomaly_score': anomaly_score
        }


class LinkographAnomalyDetector:
    """Detects anomalies in design process using graph-based methods"""
    
    def __init__(self, model: TemporalLinkographGNN):
        self.model = model
        self.anomaly_threshold = 0.7
        
    def detect_learning_struggles(self, temporal_graph: TemporalData) -> Dict[str, Any]:
        """Detect learning struggles through graph anomaly detection"""
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(
                temporal_graph.x,
                temporal_graph.edge_index,
                temporal_graph.edge_attr
            )
        
        anomaly_score = outputs['anomaly_score'].item()
        node_embeddings = outputs['node_embeddings']
        
        # Identify specific struggle patterns
        struggles = {
            'overall_anomaly_score': anomaly_score,
            'is_struggling': anomaly_score > self.anomaly_threshold,
            'struggle_nodes': [],
            'recommendations': []
        }
        
        if struggles['is_struggling']:
            # Find nodes with high reconstruction error
            node_anomalies = self._compute_node_anomalies(node_embeddings, temporal_graph)
            
            # Identify top anomalous nodes
            top_anomalies = torch.topk(node_anomalies, k=min(5, len(node_anomalies)))
            struggles['struggle_nodes'] = top_anomalies.indices.tolist()
            
            # Generate recommendations based on anomaly patterns
            struggles['recommendations'] = self._generate_recommendations(
                node_anomalies, temporal_graph
            )
        
        return struggles
    
    def _compute_node_anomalies(self, embeddings: torch.Tensor, graph: TemporalData) -> torch.Tensor:
        """Compute anomaly scores for individual nodes"""
        # Simple approach: distance from mean embedding
        mean_embedding = embeddings.mean(dim=0)
        distances = torch.norm(embeddings - mean_embedding, dim=1)
        
        # Normalize to 0-1 range
        normalized_distances = (distances - distances.min()) / (distances.max() - distances.min() + 1e-8)
        
        return normalized_distances
    
    def _generate_recommendations(self, node_anomalies: torch.Tensor, graph: TemporalData) -> List[str]:
        """Generate educational recommendations based on anomaly patterns"""
        recommendations = []
        
        # Check for orphan moves (nodes with no connections)
        degrees = torch.zeros(graph.num_nodes)
        for i in range(graph.edge_index.size(1)):
            degrees[graph.edge_index[0, i]] += 1
            degrees[graph.edge_index[1, i]] += 1
        
        orphan_ratio = (degrees == 0).sum().item() / graph.num_nodes
        
        if orphan_ratio > 0.3:
            recommendations.append(
                "High number of unconnected design moves detected. "
                "Consider encouraging more iterative exploration and connection-making."
            )
        
        # Check for phase imbalance
        phase_features = graph.x[:, :3]  # First 3 features are phase encoding
        phase_distribution = phase_features.sum(dim=0)
        phase_imbalance = phase_distribution.std() / phase_distribution.mean()
        
        if phase_imbalance > 0.5:
            recommendations.append(
                "Imbalanced design phases detected. "
                "Ensure adequate time is spent on ideation, visualization, and materialization."
            )
        
        return recommendations


class GraphMLLinkographyAnalyzer:
    """Main analyzer combining all Graph ML methods for linkography"""
    
    def __init__(self):
        self.converter = LinkographToTemporalGraph()
        self.model = TemporalLinkographGNN(
            node_features_dim=20,  # Adjusted based on feature extraction
            edge_features_dim=5,
            hidden_dim=64
        )
        self.anomaly_detector = LinkographAnomalyDetector(self.model)
        
    def analyze_session(self, linkograph_session: LinkographSession) -> Dict[str, Any]:
        """Perform comprehensive Graph ML analysis on a linkography session"""
        
        # Convert to temporal graph
        temporal_graph = self.converter.convert_to_temporal_graph(linkograph_session)
        
        # Run model inference
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(
                temporal_graph.x,
                temporal_graph.edge_index,
                temporal_graph.edge_attr
            )
        
        # Extract insights
        analysis = {
            'session_id': linkograph_session.session_id,
            'temporal_graph_metrics': self._compute_graph_metrics(temporal_graph),
            'pattern_predictions': self._interpret_patterns(outputs['pattern_logits']),
            'cognitive_assessment': self._interpret_cognitive_scores(outputs['cognitive_scores']),
            'anomaly_detection': self.anomaly_detector.detect_learning_struggles(temporal_graph),
            'embeddings': {
                'node_embeddings': outputs['node_embeddings'].numpy(),
                'graph_embedding': outputs['graph_embedding'].numpy()
            }
        }
        
        return analysis
    
    def _compute_graph_metrics(self, graph: TemporalData) -> Dict[str, float]:
        """Compute temporal graph metrics"""
        # Convert to NetworkX for metric computation
        G = nx.DiGraph()
        edge_list = graph.edge_index.t().numpy()
        for i in range(edge_list.shape[0]):
            G.add_edge(
                edge_list[i, 0],
                edge_list[i, 1],
                weight=graph.edge_attr[i, 0].item()  # Use strength as weight
            )
        
        metrics = {
            'num_nodes': graph.num_nodes,
            'num_edges': graph.edge_index.size(1),
            'density': nx.density(G),
            'avg_clustering': nx.average_clustering(G.to_undirected()),
            'connectivity': 1.0 if nx.is_weakly_connected(G) else 0.0
        }
        
        # Temporal metrics
        if hasattr(graph, 'edge_time'):
            time_diffs = torch.diff(torch.sort(graph.edge_time)[0])
            metrics['temporal_regularity'] = 1.0 / (time_diffs.std().item() + 1e-8)
            metrics['temporal_span'] = (graph.edge_time.max() - graph.edge_time.min()).item()
        
        return metrics
    
    def _interpret_patterns(self, pattern_logits: torch.Tensor) -> Dict[str, float]:
        """Interpret pattern classification results"""
        pattern_probs = F.softmax(pattern_logits, dim=-1).squeeze()
        patterns = ['chunk', 'web', 'sawtooth', 'orphan']
        
        return {
            pattern: prob.item()
            for pattern, prob in zip(patterns, pattern_probs)
        }
    
    def _interpret_cognitive_scores(self, cognitive_scores: torch.Tensor) -> Dict[str, float]:
        """Interpret cognitive assessment scores"""
        scores = cognitive_scores.squeeze().numpy()
        metrics = [
            'deep_thinking_engagement',
            'cognitive_offloading_prevention',
            'scaffolding_effectiveness',
            'knowledge_integration',
            'learning_progression',
            'metacognitive_awareness'
        ]
        
        return {
            metric: float(score)
            for metric, score in zip(metrics, scores)
        }
    
    def create_evolution_graph(self, sessions: List[LinkographSession]) -> nx.DiGraph:
        """Create a graph showing evolution of design thinking across sessions"""
        evolution_graph = nx.DiGraph()
        
        for i, session in enumerate(sessions):
            # Add session node
            session_analysis = self.analyze_session(session)
            evolution_graph.add_node(
                f"session_{i}",
                **session_analysis['temporal_graph_metrics'],
                **session_analysis['cognitive_assessment']
            )
            
            # Add edges between consecutive sessions
            if i > 0:
                evolution_graph.add_edge(
                    f"session_{i-1}",
                    f"session_{i}",
                    weight=self._compute_session_similarity(sessions[i-1], sessions[i])
                )
        
        return evolution_graph
    
    def _compute_session_similarity(self, session1: LinkographSession, session2: LinkographSession) -> float:
        """Compute similarity between two sessions"""
        # Simple approach: compare cognitive mappings
        mapping1 = session1.cognitive_mapping.to_dict()
        mapping2 = session2.cognitive_mapping.to_dict()
        
        similarities = []
        for key in mapping1:
            if key in mapping2:
                diff = abs(mapping1[key] - mapping2[key])
                similarities.append(1.0 - diff)
        
        return np.mean(similarities) if similarities else 0.0


# Export the main analyzer class
__all__ = ['GraphMLLinkographyAnalyzer', 'LinkographToTemporalGraph', 'TemporalLinkographGNN']