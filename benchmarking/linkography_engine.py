"""
MEGA Architectural Mentor - Fuzzy Linkography Engine
Automated linkography generation using semantic similarity
Based on Gabriela Goldschmidt's methodology with AI enhancement
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import uuid
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from .linkography_types import (
    DesignMove, LinkographLink, Linkograph, LinkographMetrics,
    LinkographPattern, CognitiveLinkographMapping, LinkType
)


class LinkographyEngine:
    """
    Fuzzy linkography engine for automated design process analysis.
    Uses semantic embeddings to automatically detect links between design moves.
    """
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 similarity_threshold: float = 0.35,
                 max_link_range: int = 15):
        """
        Initialize the linkography engine.
        
        Args:
            model_name: Sentence transformer model for embeddings
            similarity_threshold: Minimum similarity for link creation (0-1)
            max_link_range: Maximum temporal distance for links
        """
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.max_link_range = max_link_range
        self.logger = logging.getLogger(__name__)
        
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate semantic embedding for design move content"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def calculate_similarity(self, move1: DesignMove, move2: DesignMove) -> float:
        """Calculate cosine similarity between two design moves"""
        if move1.embedding is None:
            move1.embedding = self.generate_embedding(move1.content)
        if move2.embedding is None:
            move2.embedding = self.generate_embedding(move2.content)
            
        similarity = cosine_similarity(
            move1.embedding.reshape(1, -1),
            move2.embedding.reshape(1, -1)
        )[0, 0]
        
        return float(similarity)
    
    def generate_links(self, moves: List[DesignMove]) -> List[LinkographLink]:
        """
        Generate links between design moves using fuzzy linkography.
        
        Args:
            moves: List of design moves in temporal order
            
        Returns:
            List of linkograph links
        """
        links = []
        
        # Ensure all moves have embeddings
        for move in moves:
            if move.embedding is None:
                move.embedding = self.generate_embedding(move.content)
        
        # Calculate pairwise similarities
        for i, source_move in enumerate(moves):
            for j, target_move in enumerate(moves):
                if i == j:
                    continue
                    
                # Check temporal distance
                temporal_distance = abs(j - i)
                if temporal_distance > self.max_link_range:
                    continue
                
                # Calculate similarity
                similarity = self.calculate_similarity(source_move, target_move)
                
                # Create link if above threshold
                if similarity >= self.similarity_threshold:
                    link_type: LinkType = 'forward' if j > i else 'backward'
                    if abs(temporal_distance) <= 3 and similarity > 0.7:
                        link_type = 'lateral'  # Strong nearby connections
                    
                    link = LinkographLink(
                        id=str(uuid.uuid4()),
                        source_move=source_move.id,
                        target_move=target_move.id,
                        strength=similarity,
                        confidence=self._calculate_confidence(similarity, temporal_distance),
                        link_type=link_type,
                        temporal_distance=temporal_distance,
                        semantic_similarity=similarity,
                        automated=True
                    )
                    links.append(link)
        
        return links
    
    def _calculate_confidence(self, similarity: float, temporal_distance: int) -> float:
        """Calculate confidence score for a link"""
        # Confidence decreases with temporal distance
        distance_factor = 1.0 - (temporal_distance / self.max_link_range) * 0.3
        # Confidence increases with similarity
        similarity_factor = similarity
        
        confidence = distance_factor * similarity_factor
        return max(0.0, min(1.0, confidence))
    
    def calculate_metrics(self, linkograph: Linkograph) -> LinkographMetrics:
        """Calculate comprehensive linkography metrics"""
        moves = linkograph.moves
        links = linkograph.links
        
        if not moves:
            return LinkographMetrics(
                link_density=0.0,
                critical_move_ratio=0.0,
                entropy=0.0,
                phase_balance={},
                cognitive_indicators={}
            )
        
        # Link density
        total_link_strength = sum(link.strength for link in links)
        link_density = total_link_strength / len(moves) if moves else 0.0
        
        # Critical moves ratio
        critical_moves = linkograph.get_critical_moves()
        critical_move_ratio = len(critical_moves) / len(moves)
        
        # Entropy calculation
        entropy = self._calculate_entropy(linkograph)
        
        # Phase balance
        phase_balance = self._calculate_phase_balance(moves)
        
        # Cognitive indicators (will be mapped later)
        cognitive_indicators = {
            'deep_thinking': 0.0,
            'offloading_prevention': 0.0,
            'knowledge_integration': 0.0,
            'learning_progression': 0.0,
            'metacognitive_awareness': 0.0
        }
        
        # Additional metrics
        avg_link_strength = total_link_strength / len(links) if links else 0.0
        max_link_range = max((link.temporal_distance for link in links), default=0)
        
        # Count orphan moves
        linked_moves = set()
        for link in links:
            linked_moves.add(link.source_move)
            linked_moves.add(link.target_move)
        orphan_count = len([m for m in moves if m.id not in linked_moves])
        orphan_move_ratio = orphan_count / len(moves)
        
        # Pattern counts
        patterns = self._detect_patterns(linkograph)
        chunk_count = len([p for p in patterns if p.pattern_type == 'chunk'])
        web_count = len([p for p in patterns if p.pattern_type == 'web'])
        sawtooth_count = len([p for p in patterns if p.pattern_type == 'sawtooth'])
        
        return LinkographMetrics(
            link_density=link_density,
            critical_move_ratio=critical_move_ratio,
            entropy=entropy,
            phase_balance=phase_balance,
            cognitive_indicators=cognitive_indicators,
            avg_link_strength=avg_link_strength,
            max_link_range=max_link_range,
            orphan_move_ratio=orphan_move_ratio,
            chunk_count=chunk_count,
            web_count=web_count,
            sawtooth_count=sawtooth_count
        )
    
    def _calculate_entropy(self, linkograph: Linkograph) -> float:
        """Calculate Shannon entropy of the linkograph"""
        if not linkograph.links:
            return 0.0
            
        # Create link strength distribution
        strengths = [link.strength for link in linkograph.links]
        total_strength = sum(strengths)
        
        if total_strength == 0:
            return 0.0
            
        # Calculate probabilities
        probabilities = [s / total_strength for s in strengths]
        
        # Shannon entropy
        entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probabilities)
        
        # Normalize by max possible entropy
        max_entropy = np.log2(len(linkograph.links))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return normalized_entropy
    
    def _calculate_phase_balance(self, moves: List[DesignMove]) -> Dict[str, float]:
        """Calculate time distribution across design phases"""
        phase_counts = {'ideation': 0, 'visualization': 0, 'materialization': 0}
        
        for move in moves:
            if move.phase in phase_counts:
                phase_counts[move.phase] += 1
        
        total_moves = len(moves)
        phase_balance = {
            phase: count / total_moves if total_moves > 0 else 0.0
            for phase, count in phase_counts.items()
        }
        
        return phase_balance
    
    def _detect_patterns(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Detect common linkographic patterns"""
        patterns = []
        
        # Detect chunks (dense local connections)
        chunks = self._detect_chunks(linkograph)
        patterns.extend(chunks)
        
        # Detect webs (highly interconnected regions)
        webs = self._detect_webs(linkograph)
        patterns.extend(webs)
        
        # Detect sawtooth patterns (sequential development)
        sawteeth = self._detect_sawteeth(linkograph)
        patterns.extend(sawteeth)
        
        return patterns
    
    def _detect_chunks(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Detect chunk patterns (focused exploration)"""
        chunks = []
        moves = linkograph.moves
        
        # Look for groups of moves with high local connectivity
        window_size = 5
        for i in range(len(moves) - window_size + 1):
            window_moves = moves[i:i + window_size]
            window_ids = [m.id for m in window_moves]
            
            # Count links within window
            internal_links = [
                link for link in linkograph.links
                if link.source_move in window_ids and link.target_move in window_ids
            ]
            
            # High density indicates a chunk
            density = len(internal_links) / (window_size * (window_size - 1))
            if density > 0.3:  # Threshold for chunk detection
                chunk = LinkographPattern(
                    pattern_type='chunk',
                    moves=window_ids,
                    strength=density,
                    description=f"Focused exploration chunk at moves {i}-{i+window_size-1}",
                    cognitive_implications={
                        'deep_thinking': 0.8,
                        'knowledge_integration': 0.6
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _detect_webs(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Detect web patterns (intensive development)"""
        webs = []
        
        # Find highly connected components
        # Simple approach: find moves with many connections
        connection_threshold = 5
        
        for move in linkograph.moves:
            source_links, target_links = linkograph.get_links_for_move(move.id)
            total_connections = len(source_links) + len(target_links)
            
            if total_connections >= connection_threshold:
                # Find all connected moves
                connected_moves = set([move.id])
                for link in source_links + target_links:
                    connected_moves.add(link.source_move)
                    connected_moves.add(link.target_move)
                
                web = LinkographPattern(
                    pattern_type='web',
                    moves=list(connected_moves),
                    strength=total_connections / len(linkograph.moves),
                    description=f"Web pattern centered on move {move.id[:8]}",
                    cognitive_implications={
                        'deep_thinking': 0.9,
                        'knowledge_integration': 0.8,
                        'metacognitive_awareness': 0.7
                    }
                )
                webs.append(web)
        
        return webs
    
    def _detect_sawteeth(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Detect sawtooth patterns (sequential development)"""
        sawteeth = []
        
        # Look for sequential forward links
        sequence_threshold = 3
        current_sequence = []
        
        for i in range(len(linkograph.moves) - 1):
            current_id = linkograph.moves[i].id
            next_id = linkograph.moves[i + 1].id
            
            # Check if there's a forward link
            has_forward_link = any(
                link.source_move == current_id and link.target_move == next_id
                for link in linkograph.links
            )
            
            if has_forward_link:
                if not current_sequence:
                    current_sequence = [current_id]
                current_sequence.append(next_id)
            else:
                if len(current_sequence) >= sequence_threshold:
                    sawtooth = LinkographPattern(
                        pattern_type='sawtooth',
                        moves=current_sequence,
                        strength=len(current_sequence) / len(linkograph.moves),
                        description=f"Sequential development pattern of {len(current_sequence)} moves",
                        cognitive_implications={
                            'learning_progression': 0.8,
                            'scaffolding_effectiveness': 0.7
                        }
                    )
                    sawteeth.append(sawtooth)
                current_sequence = []
        
        return sawteeth
    
    def update_linkograph_realtime(self, 
                                  current_linkograph: Linkograph,
                                  new_move: DesignMove) -> Linkograph:
        """Update linkograph incrementally with a new design move"""
        # Add embedding to new move
        if new_move.embedding is None:
            new_move.embedding = self.generate_embedding(new_move.content)
        
        # Add new move
        updated_moves = current_linkograph.moves + [new_move]
        
        # Generate links for new move
        new_links = []
        for existing_move in current_linkograph.moves[-self.max_link_range:]:
            similarity = self.calculate_similarity(existing_move, new_move)
            
            if similarity >= self.similarity_threshold:
                temporal_distance = len(current_linkograph.moves) - current_linkograph.moves.index(existing_move)
                
                # Create backward link from new move to existing
                link = LinkographLink(
                    id=str(uuid.uuid4()),
                    source_move=new_move.id,
                    target_move=existing_move.id,
                    strength=similarity,
                    confidence=self._calculate_confidence(similarity, temporal_distance),
                    link_type='backward',
                    temporal_distance=temporal_distance,
                    semantic_similarity=similarity,
                    automated=True
                )
                new_links.append(link)
                
                # Create forward link from existing to new
                forward_link = LinkographLink(
                    id=str(uuid.uuid4()),
                    source_move=existing_move.id,
                    target_move=new_move.id,
                    strength=similarity,
                    confidence=self._calculate_confidence(similarity, temporal_distance),
                    link_type='forward',
                    temporal_distance=temporal_distance,
                    semantic_similarity=similarity,
                    automated=True
                )
                new_links.append(forward_link)
        
        # Update linkograph
        updated_links = current_linkograph.links + new_links
        
        # Create new linkograph instance
        updated_linkograph = Linkograph(
            id=current_linkograph.id,
            session_id=current_linkograph.session_id,
            moves=updated_moves,
            links=updated_links,
            metrics=self.calculate_metrics(current_linkograph),  # Will recalculate
            phase=new_move.phase,
            generated_at=datetime.now().timestamp()
        )
        
        # Recalculate metrics
        updated_linkograph.metrics = self.calculate_metrics(updated_linkograph)
        
        return updated_linkograph
    
    def generate_linkograph(self, 
                          moves: List[DesignMove],
                          session_id: str) -> Linkograph:
        """Generate a complete linkograph from a list of design moves"""
        # Generate embeddings for all moves
        for move in moves:
            if move.embedding is None:
                move.embedding = self.generate_embedding(move.content)
        
        # Generate links
        links = self.generate_links(moves)
        
        # Determine overall phase (most common)
        phase_counts = {}
        for move in moves:
            phase_counts[move.phase] = phase_counts.get(move.phase, 0) + 1
        overall_phase = max(phase_counts, key=phase_counts.get) if phase_counts else 'ideation'
        
        # Create linkograph
        linkograph = Linkograph(
            id=str(uuid.uuid4()),
            session_id=session_id,
            moves=moves,
            links=links,
            metrics=LinkographMetrics(
                link_density=0.0,
                critical_move_ratio=0.0,
                entropy=0.0,
                phase_balance={},
                cognitive_indicators={}
            ),
            phase=overall_phase,
            generated_at=datetime.now().timestamp()
        )
        
        # Calculate metrics
        linkograph.metrics = self.calculate_metrics(linkograph)
        
        return linkograph