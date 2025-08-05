"""
Simplified Graph ML Integration with Linkography - Works without PyTorch
Provides graph-based analysis using NetworkX and scikit-learn only
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import pandas as pd

from linkography_types import (
    Linkograph, DesignMove, LinkographLink, LinkographPattern,
    LinkographSession, CognitiveLinkographMapping
)


class SimpleLinkographToGraph:
    """Converts linkography data to NetworkX graph format for analysis"""
    
    def __init__(self):
        self.node_features_dim = 20
        self.edge_features_dim = 5
        
    def convert_to_networkx(self, linkograph_session: LinkographSession) -> nx.DiGraph:
        """Convert a linkography session to NetworkX directed graph"""
        
        G = nx.DiGraph()
        
        # Aggregate all moves from all linkographs in session
        all_moves = []
        all_links = []
        
        for linkograph in linkograph_session.linkographs:
            all_moves.extend(linkograph.moves)
            all_links.extend(linkograph.links)
        
        # Add nodes with features
        for i, move in enumerate(all_moves):
            node_features = self._extract_node_features(move, i, len(all_moves))
            G.add_node(i, **node_features, move=move)
        
        # Add edges with features
        move_id_to_idx = {move.id: idx for idx, move in enumerate(all_moves)}
        
        for link in all_links:
            if link.source_move in move_id_to_idx and link.target_move in move_id_to_idx:
                source_idx = move_id_to_idx[link.source_move]
                target_idx = move_id_to_idx[link.target_move]
                
                edge_features = self._extract_edge_features(link)
                G.add_edge(source_idx, target_idx, **edge_features, link=link)
        
        return G
    
    def _extract_node_features(self, move: DesignMove, idx: int, total_moves: int) -> Dict[str, Any]:
        """Extract features from a design move"""
        return {
            'phase': move.phase,
            'move_type': move.move_type,
            'modality': move.modality,
            'cognitive_load': move.cognitive_load if move.cognitive_load else 0.5,
            'normalized_time': move.timestamp / max(1, total_moves),
            'position': idx / max(1, total_moves - 1),
            'content_length': len(move.content),
            'id': move.id
        }
    
    def _extract_edge_features(self, link: LinkographLink) -> Dict[str, Any]:
        """Extract features from a link"""
        return {
            'strength': link.strength,
            'confidence': link.confidence,
            'semantic_similarity': link.semantic_similarity,
            'temporal_distance': link.temporal_distance,
            'link_type': link.link_type
        }


class SimpleGraphMLAnalyzer:
    """Simplified Graph ML analyzer using NetworkX and scikit-learn"""
    
    def __init__(self):
        self.converter = SimpleLinkographToGraph()
        self.scaler = StandardScaler()
        
    def analyze_session(self, linkograph_session: LinkographSession) -> Dict[str, Any]:
        """Perform graph-based analysis on a linkography session"""
        
        # Convert to graph
        G = self.converter.convert_to_networkx(linkograph_session)
        
        # Compute graph metrics
        metrics = self._compute_graph_metrics(G)
        
        # Detect patterns
        patterns = self._detect_graph_patterns(G)
        
        # Analyze cognitive flow
        cognitive_flow = self._analyze_cognitive_flow(G)
        
        # Create node embeddings
        embeddings = self._create_node_embeddings(G)
        
        return {
            'session_id': linkograph_session.session_id,
            'graph_metrics': metrics,
            'patterns': patterns,
            'cognitive_flow': cognitive_flow,
            'embeddings': embeddings,
            'anomalies': self._detect_anomalies(G, embeddings)
        }
    
    def _compute_graph_metrics(self, G: nx.DiGraph) -> Dict[str, float]:
        """Compute various graph metrics"""
        
        metrics = {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': nx.density(G),
            'avg_degree': np.mean([d for n, d in G.degree()]) if G.number_of_nodes() > 0 else 0
        }
        
        # Connectivity metrics
        if G.number_of_nodes() > 0:
            metrics['connectivity'] = 1.0 if nx.is_weakly_connected(G) else 0.0
            
            # Clustering coefficient (on undirected version)
            G_undirected = G.to_undirected()
            metrics['avg_clustering'] = nx.average_clustering(G_undirected)
            
            # Path-based metrics
            if nx.is_weakly_connected(G):
                metrics['avg_path_length'] = nx.average_shortest_path_length(G.to_undirected())
            else:
                # Compute for largest component
                largest_cc = max(nx.weakly_connected_components(G), key=len)
                G_sub = G.subgraph(largest_cc).to_undirected()
                if len(G_sub) > 1:
                    metrics['avg_path_length'] = nx.average_shortest_path_length(G_sub)
                else:
                    metrics['avg_path_length'] = 0
        
        return metrics
    
    def _detect_graph_patterns(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Detect structural patterns in the graph"""
        
        patterns = {
            'hubs': [],
            'clusters': [],
            'bridges': [],
            'isolated_nodes': []
        }
        
        if G.number_of_nodes() == 0:
            return patterns
        
        # Detect hubs (high-degree nodes)
        degrees = dict(G.degree())
        if degrees:
            avg_degree = np.mean(list(degrees.values()))
            std_degree = np.std(list(degrees.values()))
            hub_threshold = avg_degree + 2 * std_degree
            
            patterns['hubs'] = [
                node for node, degree in degrees.items()
                if degree > hub_threshold
            ]
        
        # Detect isolated nodes
        patterns['isolated_nodes'] = list(nx.isolates(G))
        
        # Detect communities (on undirected version)
        G_undirected = G.to_undirected()
        if G_undirected.number_of_edges() > 0:
            import community.community_louvain as community_louvain
            try:
                communities = community_louvain.best_partition(G_undirected)
                # Group nodes by community
                community_groups = {}
                for node, comm in communities.items():
                    if comm not in community_groups:
                        community_groups[comm] = []
                    community_groups[comm].append(node)
                patterns['clusters'] = list(community_groups.values())
            except:
                # Fallback if community detection fails
                patterns['clusters'] = []
        
        # Detect bridges (edges whose removal increases components)
        if G.number_of_edges() > 0:
            bridges = list(nx.bridges(G_undirected))
            patterns['bridges'] = bridges[:5]  # Limit to top 5
        
        return patterns
    
    def _analyze_cognitive_flow(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Analyze the cognitive flow through the graph"""
        
        if G.number_of_nodes() == 0:
            return {'phases': {}, 'transitions': {}, 'flow_score': 0}
        
        # Track phase transitions
        phase_transitions = {}
        phase_counts = {'ideation': 0, 'visualization': 0, 'materialization': 0}
        
        for node in G.nodes():
            phase = G.nodes[node].get('phase', 'unknown')
            if phase in phase_counts:
                phase_counts[phase] += 1
            
            # Check transitions
            for successor in G.successors(node):
                succ_phase = G.nodes[successor].get('phase', 'unknown')
                transition = f"{phase}->{succ_phase}"
                phase_transitions[transition] = phase_transitions.get(transition, 0) + 1
        
        # Calculate flow score (based on phase balance and transitions)
        total_nodes = G.number_of_nodes()
        phase_balance = 1.0 - np.std(list(phase_counts.values())) / (np.mean(list(phase_counts.values())) + 1e-8)
        
        # Smooth transitions score
        forward_transitions = sum(
            count for trans, count in phase_transitions.items()
            if trans in ['ideation->visualization', 'visualization->materialization']
        )
        total_transitions = sum(phase_transitions.values())
        transition_score = forward_transitions / (total_transitions + 1) if total_transitions > 0 else 0
        
        flow_score = (phase_balance + transition_score) / 2
        
        return {
            'phases': phase_counts,
            'transitions': phase_transitions,
            'flow_score': flow_score,
            'phase_balance': phase_balance,
            'transition_smoothness': transition_score
        }
    
    def _create_node_embeddings(self, G: nx.DiGraph) -> np.ndarray:
        """Create node embeddings using graph structure"""
        
        if G.number_of_nodes() == 0:
            return np.array([])
        
        # Create feature matrix
        features = []
        for node in G.nodes():
            node_data = G.nodes[node]
            feature_vec = [
                node_data.get('cognitive_load', 0.5),
                node_data.get('normalized_time', 0.5),
                node_data.get('position', 0.5),
                G.in_degree(node),
                G.out_degree(node),
                nx.clustering(G.to_undirected(), node) if G.number_of_edges() > 0 else 0
            ]
            features.append(feature_vec)
        
        features_array = np.array(features)
        
        # Apply PCA for dimensionality reduction
        if features_array.shape[0] > 2:
            pca = PCA(n_components=min(2, features_array.shape[0]))
            embeddings = pca.fit_transform(features_array)
        else:
            embeddings = features_array
        
        return embeddings
    
    def _detect_anomalies(self, G: nx.DiGraph, embeddings: np.ndarray) -> Dict[str, Any]:
        """Detect anomalous nodes and patterns"""
        
        anomalies = {
            'anomalous_nodes': [],
            'anomaly_score': 0,
            'issues': []
        }
        
        if G.number_of_nodes() == 0 or len(embeddings) == 0:
            return anomalies
        
        # Check for orphan nodes
        orphans = list(nx.isolates(G))
        orphan_ratio = len(orphans) / G.number_of_nodes()
        
        if orphan_ratio > 0.3:
            anomalies['issues'].append({
                'type': 'high_orphan_ratio',
                'severity': 'high',
                'description': f"{orphan_ratio:.1%} of design moves are unconnected",
                'recommendation': "Encourage more iterative thinking and connection-making"
            })
        
        # Check for phase imbalance
        phase_counts = {}
        for node in G.nodes():
            phase = G.nodes[node].get('phase', 'unknown')
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        if len(phase_counts) > 1:
            phase_values = list(phase_counts.values())
            phase_std = np.std(phase_values)
            phase_mean = np.mean(phase_values)
            if phase_std / (phase_mean + 1e-8) > 0.5:
                anomalies['issues'].append({
                    'type': 'phase_imbalance',
                    'severity': 'medium',
                    'description': "Uneven distribution across design phases",
                    'recommendation': "Balance time between ideation, visualization, and materialization"
                })
        
        # Detect outliers in embeddings
        if len(embeddings) > 3:
            # Use distance from centroid
            centroid = np.mean(embeddings, axis=0)
            distances = np.linalg.norm(embeddings - centroid, axis=1)
            
            # Outliers are > 2 std deviations away
            outlier_threshold = np.mean(distances) + 2 * np.std(distances)
            outlier_nodes = [i for i, d in enumerate(distances) if d > outlier_threshold]
            
            anomalies['anomalous_nodes'] = outlier_nodes
            anomalies['anomaly_score'] = len(outlier_nodes) / len(embeddings)
        
        return anomalies
    
    def create_evolution_graph(self, sessions: List[LinkographSession]) -> nx.DiGraph:
        """Create a graph showing evolution across sessions"""
        
        evolution_graph = nx.DiGraph()
        
        for i, session in enumerate(sessions):
            # Analyze session
            analysis = self.analyze_session(session)
            
            # Add session node
            evolution_graph.add_node(
                f"session_{i}",
                session_id=session.session_id[:8],
                **analysis['graph_metrics'],
                **analysis['cognitive_flow'],
                anomaly_score=analysis['anomalies']['anomaly_score']
            )
            
            # Add edges between consecutive sessions
            if i > 0:
                similarity = self._compute_session_similarity(sessions[i-1], sessions[i])
                evolution_graph.add_edge(
                    f"session_{i-1}",
                    f"session_{i}",
                    weight=similarity
                )
        
        return evolution_graph
    
    def _compute_session_similarity(self, session1: LinkographSession, session2: LinkographSession) -> float:
        """Compute similarity between two sessions"""
        # Compare cognitive mappings
        mapping1 = session1.cognitive_mapping.to_dict()
        mapping2 = session2.cognitive_mapping.to_dict()
        
        similarities = []
        for key in mapping1:
            if key in mapping2:
                diff = abs(mapping1[key] - mapping2[key])
                similarities.append(1.0 - diff)
        
        return np.mean(similarities) if similarities else 0.0


# Export classes
__all__ = ['SimpleLinkographToGraph', 'SimpleGraphMLAnalyzer']