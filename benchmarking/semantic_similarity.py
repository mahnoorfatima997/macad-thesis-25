#!/usr/bin/env python3
"""
Semantic Similarity Module for Linkography Analysis
Provides advanced text similarity detection using sentence transformers
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import torch
from thesis_colors import (
    THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS, 
    PLOTLY_COLORSCALES, CHART_COLORS, UI_COLORS,
    get_color_palette, get_metric_color, get_proficiency_color, get_agent_color
)


class SemanticSimilarityAnalyzer:
    """Advanced semantic similarity analysis for design moves"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with specified sentence transformer model"""
        
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        
        print(f"🧠 Semantic Similarity Analyzer initialized with {model_name}")
    
    def encode_texts(self, texts: List[str], cache_key: Optional[str] = None) -> np.ndarray:
        """Encode texts to embeddings with optional caching"""
        
        if cache_key and cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
        
        # Encode texts
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
        # Cache if key provided
        if cache_key:
            self.embeddings_cache[cache_key] = embeddings
        
        return embeddings
    
    def calculate_similarity_matrix(self, texts: List[str], cache_key: Optional[str] = None) -> np.ndarray:
        """Calculate pairwise similarity matrix for texts"""
        
        embeddings = self.encode_texts(texts, cache_key)
        similarity_matrix = cosine_similarity(embeddings)
        
        return similarity_matrix
    
    def find_similar_pairs(self, texts: List[str], threshold: float = 0.6, 
                          cache_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find pairs of texts with similarity above threshold"""
        
        similarity_matrix = self.calculate_similarity_matrix(texts, cache_key)
        similar_pairs = []
        
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                similarity = similarity_matrix[i][j]
                
                if similarity >= threshold:
                    pair = {
                        "text1": texts[i],
                        "text2": texts[j],
                        "index1": i,
                        "index2": j,
                        "similarity": float(similarity)
                    }
                    similar_pairs.append(pair)
        
        # Sort by similarity (highest first)
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_pairs
    
    def analyze_design_move_similarity(self, moves: List[Dict[str, Any]], 
                                     threshold: float = 0.6) -> Dict[str, Any]:
        """Analyze similarity between design moves"""
        
        if len(moves) < 2:
            return {"similar_pairs": [], "similarity_matrix": None}
        
        # Extract move contents
        contents = [move.get('content', '') for move in moves]
        
        # Calculate similarity matrix
        similarity_matrix = self.calculate_similarity_matrix(contents)
        
        # Find similar pairs
        similar_pairs = self.find_similar_pairs(contents, threshold)
        
        # Analyze similarity patterns
        analysis = {
            "similarity_matrix": similarity_matrix.tolist(),
            "similar_pairs": similar_pairs,
            "average_similarity": float(np.mean(similarity_matrix)),
            "max_similarity": float(np.max(similarity_matrix)),
            "min_similarity": float(np.min(similarity_matrix)),
            "similarity_std": float(np.std(similarity_matrix)),
            "high_similarity_pairs": len(similar_pairs),
            "similarity_distribution": self._analyze_similarity_distribution(similarity_matrix)
        }
        
        return analysis
    
    def _analyze_similarity_distribution(self, similarity_matrix: np.ndarray) -> Dict[str, Any]:
        """Analyze the distribution of similarity scores"""
        
        # Flatten matrix (excluding diagonal)
        similarities = []
        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                similarities.append(similarity_matrix[i][j])
        
        if not similarities:
            return {}
        
        similarities = np.array(similarities)
        
        return {
            "mean": float(np.mean(similarities)),
            "median": float(np.median(similarities)),
            "std": float(np.std(similarities)),
            "q25": float(np.percentile(similarities, 25)),
            "q75": float(np.percentile(similarities, 75)),
            "min": float(np.min(similarities)),
            "max": float(np.max(similarities))
        }
    
    def detect_conceptual_clusters(self, moves: List[Dict[str, Any]], 
                                 similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Detect conceptual clusters of similar design moves"""
        
        if len(moves) < 2:
            return []
        
        contents = [move.get('content', '') for move in moves]
        similarity_matrix = self.calculate_similarity_matrix(contents)
        
        # Use hierarchical clustering to find conceptual groups
        clusters = self._hierarchical_clustering(similarity_matrix, similarity_threshold)
        
        # Convert clusters to move groups
        conceptual_clusters = []
        for cluster_indices in clusters:
            cluster_moves = [moves[i] for i in cluster_indices]
            cluster_contents = [moves[i].get('content', '') for i in cluster_indices]
            
            # Calculate cluster characteristics
            cluster_similarity = np.mean([
                similarity_matrix[i][j] 
                for i in cluster_indices 
                for j in cluster_indices 
                if i != j
            ])
            
            conceptual_cluster = {
                "cluster_id": len(conceptual_clusters),
                "moves": cluster_moves,
                "contents": cluster_contents,
                "size": len(cluster_indices),
                "average_similarity": float(cluster_similarity),
                "phases": list(set(move.get('phase', 'unknown') for move in cluster_moves)),
                "move_types": list(set(move.get('move_type', 'unknown') for move in cluster_moves))
            }
            
            conceptual_clusters.append(conceptual_cluster)
        
        return conceptual_clusters
    
    def _hierarchical_clustering(self, similarity_matrix: np.ndarray, 
                               threshold: float) -> List[List[int]]:
        """Simple hierarchical clustering based on similarity matrix"""
        
        n = len(similarity_matrix)
        clusters = [[i] for i in range(n)]
        
        # Merge clusters based on similarity
        merged = True
        while merged and len(clusters) > 1:
            merged = False
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    # Check if clusters should be merged
                    should_merge = False
                    
                    for idx1 in clusters[i]:
                        for idx2 in clusters[j]:
                            if similarity_matrix[idx1][idx2] >= threshold:
                                should_merge = True
                                break
                        if should_merge:
                            break
                    
                    if should_merge:
                        # Merge clusters
                        clusters[i].extend(clusters[j])
                        clusters.pop(j)
                        merged = True
                        break
                
                if merged:
                    break
        
        return clusters
    
    def analyze_phase_similarity(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze similarity patterns within and between design phases"""
        
        if len(moves) < 2:
            return {}
        
        # Group moves by phase
        phase_groups = {}
        for i, move in enumerate(moves):
            phase = move.get('phase', 'unknown')
            if phase not in phase_groups:
                phase_groups[phase] = []
            phase_groups[phase].append(i)
        
        contents = [move.get('content', '') for move in moves]
        similarity_matrix = self.calculate_similarity_matrix(contents)
        
        phase_analysis = {
            "within_phase_similarities": {},
            "between_phase_similarities": {},
            "phase_coherence": {}
        }
        
        # Analyze within-phase similarities
        for phase, indices in phase_groups.items():
            if len(indices) > 1:
                within_similarities = []
                for i in indices:
                    for j in indices:
                        if i != j:
                            within_similarities.append(similarity_matrix[i][j])
                
                phase_analysis["within_phase_similarities"][phase] = {
                    "mean": float(np.mean(within_similarities)),
                    "std": float(np.std(within_similarities)),
                    "count": len(within_similarities)
                }
        
        # Analyze between-phase similarities
        phase_list = list(phase_groups.keys())
        for i, phase1 in enumerate(phase_list):
            for j, phase2 in enumerate(phase_list):
                if i < j:  # Avoid duplicate pairs
                    between_similarities = []
                    for idx1 in phase_groups[phase1]:
                        for idx2 in phase_groups[phase2]:
                            between_similarities.append(similarity_matrix[idx1][idx2])
                    
                    if between_similarities:
                        key = f"{phase1}_to_{phase2}"
                        phase_analysis["between_phase_similarities"][key] = {
                            "mean": float(np.mean(between_similarities)),
                            "std": float(np.std(between_similarities)),
                            "count": len(between_similarities)
                        }
        
        # Calculate phase coherence (how similar moves are within each phase)
        for phase, indices in phase_groups.items():
            if len(indices) > 1:
                within_similarities = []
                for i in indices:
                    for j in indices:
                        if i != j:
                            within_similarities.append(similarity_matrix[i][j])
                
                phase_analysis["phase_coherence"][phase] = {
                    "coherence_score": float(np.mean(within_similarities)),
                    "move_count": len(indices)
                }
        
        return phase_analysis
    
    def detect_semantic_links(self, moves: List[Dict[str, Any]], 
                            threshold: float = 0.6,
                            max_distance: int = 5) -> List[Dict[str, Any]]:
        """Detect semantic links between design moves"""
        
        if len(moves) < 2:
            return []
        
        contents = [move.get('content', '') for move in moves]
        similarity_matrix = self.calculate_similarity_matrix(contents)
        
        semantic_links = []
        
        for i in range(len(moves)):
            for j in range(i + 1, len(moves)):
                similarity = similarity_matrix[i][j]
                distance = j - i
                
                if similarity >= threshold and distance <= max_distance:
                    link = {
                        "source_move": moves[i],
                        "target_move": moves[j],
                        "source_index": i,
                        "target_index": j,
                        "similarity": float(similarity),
                        "distance": distance,
                        "link_type": "semantic"
                    }
                    semantic_links.append(link)
        
        # Sort by similarity (highest first)
        semantic_links.sort(key=lambda x: x['similarity'], reverse=True)
        
        return semantic_links
    
    def clear_cache(self):
        """Clear the embeddings cache"""
        self.embeddings_cache.clear()
        print("🗑️ Embeddings cache cleared")


def test_semantic_similarity():
    """Test the semantic similarity analyzer"""
    
    print("🧪 Testing Semantic Similarity Analyzer...")
    
    # Sample design moves
    sample_moves = [
        {
            "content": "I want to design a sustainable building",
            "phase": "ideation",
            "move_type": "synthesis"
        },
        {
            "content": "Let me consider solar orientation for energy efficiency",
            "phase": "ideation",
            "move_type": "analysis"
        },
        {
            "content": "I'll sketch the south-facing facade",
            "phase": "visualization",
            "move_type": "transformation"
        },
        {
            "content": "The building should have good natural lighting",
            "phase": "ideation",
            "move_type": "synthesis"
        },
        {
            "content": "I need to think about the structural system",
            "phase": "materialization",
            "move_type": "analysis"
        }
    ]
    
    # Initialize analyzer
    analyzer = SemanticSimilarityAnalyzer()
    
    # Test similarity analysis
    similarity_analysis = analyzer.analyze_design_move_similarity(sample_moves)
    
    print(f"\n📊 Similarity Analysis Results:")
    print(f"   Average Similarity: {similarity_analysis['average_similarity']:.3f}")
    print(f"   High Similarity Pairs: {similarity_analysis['high_similarity_pairs']}")
    print(f"   Similarity Range: {similarity_analysis['min_similarity']:.3f} - {similarity_analysis['max_similarity']:.3f}")
    
    # Test conceptual clustering
    clusters = analyzer.detect_conceptual_clusters(sample_moves)
    print(f"\n🔗 Conceptual Clusters: {len(clusters)}")
    for i, cluster in enumerate(clusters):
        print(f"   Cluster {i}: {cluster['size']} moves, avg similarity: {cluster['average_similarity']:.3f}")
    
    # Test phase similarity analysis
    phase_analysis = analyzer.analyze_phase_similarity(sample_moves)
    print(f"\n🏗️ Phase Analysis:")
    for phase, coherence in phase_analysis['phase_coherence'].items():
        print(f"   {phase}: coherence {coherence['coherence_score']:.3f}")
    
    # Test semantic link detection
    semantic_links = analyzer.detect_semantic_links(sample_moves)
    print(f"\n🔗 Semantic Links: {len(semantic_links)}")
    
    print(f"\n✅ Semantic Similarity Analyzer working!")


if __name__ == "__main__":
    test_semantic_similarity() 