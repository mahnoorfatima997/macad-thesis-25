"""
MEGA Architectural Mentor - Linkography to Cognitive Metrics Mapping
Maps linkography patterns to the existing cognitive assessment framework
"""

import numpy as np
from typing import Dict, List, Optional
from benchmarking.linkography_types import (
    Linkograph, LinkographPattern, CognitiveLinkographMapping,
    DesignMove, LinkographLink
)


class CognitiveMappingService:
    """
    Service to map linkography metrics to cognitive assessment dimensions.
    Based on the research correlations between linkographic patterns and cognitive processes.
    """
    
    def __init__(self):
        # Weights for different linkography features in cognitive calculations
        self.feature_weights = {
            'deep_thinking': {
                'link_density': 0.3,
                'web_structures': 0.25,
                'critical_moves': 0.25,
                'chunk_formations': 0.2
            },
            'offloading_prevention': {
                'orphan_ratio': -0.4,  # Negative correlation
                'link_range': 0.3,
                'link_density': 0.3
            },
            'scaffolding': {
                'sawtooth_patterns': 0.35,
                'phase_transitions': 0.35,
                'progressive_linking': 0.3
            },
            'knowledge_integration': {
                'backlink_critical': 0.3,
                'long_range_links': 0.3,
                'web_formations': 0.2,
                'cross_phase_links': 0.2
            },
            'learning_progression': {
                'link_strengthening': 0.3,
                'expanding_range': 0.25,
                'pattern_evolution': 0.25,
                'phase_balance': 0.2
            },
            'metacognitive': {
                'self_referential': 0.35,
                'evaluation_moves': 0.35,
                'pattern_adaptation': 0.3
            }
        }
    
    def map_linkography_to_cognitive(self, linkograph: Linkograph) -> CognitiveLinkographMapping:
        """
        Map linkography metrics to cognitive assessment dimensions.
        
        Args:
            linkograph: The linkograph to analyze
            
        Returns:
            CognitiveLinkographMapping with scores for each cognitive dimension
        """
        # Extract features from linkograph
        features = self._extract_linkography_features(linkograph)
        
        # Calculate cognitive scores
        dte = self.calculate_deep_thinking_engagement(linkograph, features)
        cop = self.calculate_cognitive_offloading_prevention(linkograph, features)
        se = self.calculate_scaffolding_effectiveness(linkograph, features)
        ki = self.calculate_knowledge_integration(linkograph, features)
        lp = self.calculate_learning_progression(linkograph, features)
        ma = self.calculate_metacognitive_awareness(linkograph, features)
        
        return CognitiveLinkographMapping(
            deep_thinking_engagement=dte,
            cognitive_offloading_prevention=cop,
            scaffolding_effectiveness=se,
            knowledge_integration=ki,
            learning_progression=lp,
            metacognitive_awareness=ma
        )
    
    def _extract_linkography_features(self, linkograph: Linkograph) -> Dict[str, float]:
        """Extract relevant features from linkograph for cognitive mapping"""
        features = {}
        
        # Basic metrics from linkograph
        features['link_density'] = linkograph.metrics.link_density
        features['critical_move_ratio'] = linkograph.metrics.critical_move_ratio
        features['entropy'] = linkograph.metrics.entropy
        features['orphan_ratio'] = linkograph.metrics.orphan_move_ratio
        
        # Pattern-based features
        features['chunk_count'] = linkograph.metrics.chunk_count
        features['web_count'] = linkograph.metrics.web_count
        features['sawtooth_count'] = linkograph.metrics.sawtooth_count
        
        # Calculate additional features
        features['avg_link_range'] = self._calculate_average_link_range(linkograph)
        features['long_range_ratio'] = self._calculate_long_range_ratio(linkograph)
        features['backlink_ratio'] = self._calculate_backlink_ratio(linkograph)
        features['phase_transition_count'] = self._count_phase_transitions(linkograph)
        features['cross_phase_links'] = self._count_cross_phase_links(linkograph)
        features['self_referential_ratio'] = self._calculate_self_referential_ratio(linkograph)
        
        return features
    
    def calculate_deep_thinking_engagement(self, 
                                         linkograph: Linkograph,
                                         features: Dict[str, float]) -> float:
        """
        Calculate Deep Thinking Engagement (DTE) score.
        
        High link density = sustained cognitive engagement
        Web structures = intensive exploration
        Critical moves with high forelinks = generative thinking
        Chunk formations = focused examination
        """
        # Normalize features
        link_density_score = min(features['link_density'] / 2.0, 1.0)  # Normalize to 0-1
        web_score = min(features['web_count'] / max(len(linkograph.moves) * 0.1, 1), 1.0)
        critical_score = features['critical_move_ratio']
        chunk_score = min(features['chunk_count'] / max(len(linkograph.moves) * 0.2, 1), 1.0)
        
        # Calculate weighted score
        weights = self.feature_weights['deep_thinking']
        dte_score = (
            weights['link_density'] * link_density_score +
            weights['web_structures'] * web_score +
            weights['critical_moves'] * critical_score +
            weights['chunk_formations'] * chunk_score
        )
        
        return max(0.0, min(1.0, dte_score))
    
    def calculate_cognitive_offloading_prevention(self,
                                                linkograph: Linkograph,
                                                features: Dict[str, float]) -> float:
        """
        Calculate Cognitive Offloading Prevention (COP) score.
        
        Sparse linkographs = potential cognitive overload
        Orphan moves = cognitive capacity limitations
        Short link ranges = working memory constraints
        """
        # Invert orphan ratio (fewer orphans = better)
        orphan_prevention = 1.0 - features['orphan_ratio']
        
        # Normalize link range (longer = better)
        link_range_score = min(features['avg_link_range'] / 10.0, 1.0)
        
        # Link density (moderate is best, too high or too low indicates issues)
        link_density_score = 1.0 - abs(features['link_density'] - 0.5) * 2
        
        # Calculate weighted score
        cop_score = (
            0.4 * orphan_prevention +
            0.3 * link_range_score +
            0.3 * link_density_score
        )
        
        return max(0.0, min(1.0, cop_score))
    
    def calculate_scaffolding_effectiveness(self,
                                          linkograph: Linkograph,
                                          features: Dict[str, float]) -> float:
        """
        Calculate Scaffolding Effectiveness (SE) score.
        
        Sawtooth patterns = sequential development with support
        Phase transitions = structured progression
        Progressive linking = building on previous ideas
        """
        # Normalize sawtooth patterns
        sawtooth_score = min(features['sawtooth_count'] / max(len(linkograph.moves) * 0.15, 1), 1.0)
        
        # Phase transition score
        expected_transitions = len(linkograph.moves) * 0.1  # Expect ~10% transitions
        transition_score = min(features['phase_transition_count'] / max(expected_transitions, 1), 1.0)
        
        # Progressive linking (forward links ratio)
        forward_links = [l for l in linkograph.links if l.link_type == 'forward']
        progressive_score = len(forward_links) / max(len(linkograph.links), 1)
        
        # Calculate weighted score
        se_score = (
            0.35 * sawtooth_score +
            0.35 * transition_score +
            0.3 * progressive_score
        )
        
        return max(0.0, min(1.0, se_score))
    
    def calculate_knowledge_integration(self,
                                      linkograph: Linkograph,
                                      features: Dict[str, float]) -> float:
        """
        Calculate Knowledge Integration (KI) score.
        
        Backlink critical moves = synthesis of concepts
        Long-range links = distant idea connections
        Web formations = integration of related concepts
        Cross-phase links = holistic design thinking
        """
        # Backlink ratio (more backlinks = more integration)
        backlink_score = features['backlink_ratio']
        
        # Long-range link ratio
        long_range_score = features['long_range_ratio']
        
        # Web formations normalized
        web_score = min(features['web_count'] / max(len(linkograph.moves) * 0.1, 1), 1.0)
        
        # Cross-phase links normalized
        total_links = len(linkograph.links)
        cross_phase_score = features['cross_phase_links'] / max(total_links, 1)
        
        # Calculate weighted score
        weights = self.feature_weights['knowledge_integration']
        ki_score = (
            weights['backlink_critical'] * backlink_score +
            weights['long_range_links'] * long_range_score +
            weights['web_formations'] * web_score +
            weights['cross_phase_links'] * cross_phase_score
        )
        
        return max(0.0, min(1.0, ki_score))
    
    def calculate_learning_progression(self,
                                     linkograph: Linkograph,
                                     features: Dict[str, float]) -> float:
        """
        Calculate Learning Progression (LP) score.
        
        Progressive link strengthening over time
        Increasing link range = expanding connections
        Evolution from chunks to webs = growing expertise
        Phase balance = comprehensive skill development
        """
        # Link strengthening trend
        strengthening_score = self._calculate_link_strengthening_trend(linkograph)
        
        # Range expansion
        range_expansion_score = self._calculate_range_expansion(linkograph)
        
        # Pattern evolution (chunks to webs)
        pattern_evolution = min(features['web_count'] / max(features['chunk_count'], 1), 1.0) * 0.5 + 0.5
        
        # Phase balance score
        phase_balance = linkograph.metrics.phase_balance
        balance_values = list(phase_balance.values())
        balance_score = 1.0 - (np.std(balance_values) * 3 if len(balance_values) > 1 else 0.0)  # Penalize imbalance
        
        # Calculate weighted score
        weights = self.feature_weights['learning_progression']
        lp_score = (
            weights['link_strengthening'] * strengthening_score +
            weights['expanding_range'] * range_expansion_score +
            weights['pattern_evolution'] * pattern_evolution +
            weights['phase_balance'] * max(0, balance_score)
        )
        
        return max(0.0, min(1.0, lp_score))
    
    def calculate_metacognitive_awareness(self,
                                        linkograph: Linkograph,
                                        features: Dict[str, float]) -> float:
        """
        Calculate Metacognitive Awareness (MA) score.
        
        Self-referential links = building on own ideas
        Evaluation moves = critical reflection
        Strategic pattern changes = adaptive regulation
        """
        # Self-referential ratio
        self_ref_score = features['self_referential_ratio']
        
        # Evaluation moves ratio
        eval_moves = [m for m in linkograph.moves if m.move_type == 'evaluation']
        eval_score = len(eval_moves) / max(len(linkograph.moves), 1)
        
        # Pattern adaptation (entropy indicates variety)
        adaptation_score = features['entropy']
        
        # Calculate weighted score
        weights = self.feature_weights['metacognitive']
        ma_score = (
            weights['self_referential'] * self_ref_score +
            weights['evaluation_moves'] * eval_score +
            weights['pattern_adaptation'] * adaptation_score
        )
        
        return max(0.0, min(1.0, ma_score))
    
    # Helper methods for feature calculation
    def _calculate_average_link_range(self, linkograph: Linkograph) -> float:
        """Calculate average temporal distance of links"""
        if not linkograph.links:
            return 0.0
        
        total_range = sum(link.temporal_distance for link in linkograph.links)
        return total_range / len(linkograph.links)
    
    def _calculate_long_range_ratio(self, linkograph: Linkograph) -> float:
        """Calculate ratio of long-range links (>5 moves apart)"""
        if not linkograph.links:
            return 0.0
        
        long_range = [l for l in linkograph.links if l.temporal_distance > 5]
        return len(long_range) / len(linkograph.links)
    
    def _calculate_backlink_ratio(self, linkograph: Linkograph) -> float:
        """Calculate ratio of backward links"""
        if not linkograph.links:
            return 0.0
        
        backlinks = [l for l in linkograph.links if l.link_type == 'backward']
        return len(backlinks) / len(linkograph.links)
    
    def _count_phase_transitions(self, linkograph: Linkograph) -> int:
        """Count number of phase transitions"""
        if len(linkograph.moves) < 2:
            return 0
        
        transitions = 0
        for i in range(1, len(linkograph.moves)):
            if linkograph.moves[i].phase != linkograph.moves[i-1].phase:
                transitions += 1
        
        return transitions
    
    def _count_cross_phase_links(self, linkograph: Linkograph) -> int:
        """Count links between different phases"""
        cross_phase = 0
        
        for link in linkograph.links:
            source_move = linkograph.get_move_by_id(link.source_move)
            target_move = linkograph.get_move_by_id(link.target_move)
            
            if source_move and target_move and source_move.phase != target_move.phase:
                cross_phase += 1
        
        return cross_phase
    
    def _calculate_self_referential_ratio(self, linkograph: Linkograph) -> float:
        """Calculate ratio of links that connect to nearby moves (self-referential)"""
        if not linkograph.links:
            return 0.0
        
        self_ref = [l for l in linkograph.links if l.temporal_distance <= 3]
        return len(self_ref) / len(linkograph.links)
    
    def _calculate_link_strengthening_trend(self, linkograph: Linkograph) -> float:
        """Calculate if link strength increases over time"""
        if len(linkograph.links) < 2:
            return 0.5
        
        # Split links into early and late
        sorted_links = sorted(linkograph.links, key=lambda l: l.temporal_distance)
        mid_point = len(sorted_links) // 2
        
        early_strength = np.mean([l.strength for l in sorted_links[:mid_point]])
        late_strength = np.mean([l.strength for l in sorted_links[mid_point:]])
        
        # Normalize difference to 0-1
        trend = (late_strength - early_strength + 1) / 2
        return max(0.0, min(1.0, trend))
    
    def _calculate_range_expansion(self, linkograph: Linkograph) -> float:
        """Calculate if link range expands over time"""
        if len(linkograph.moves) < 10:
            return 0.5
        
        # Compare early vs late link ranges
        move_count = len(linkograph.moves)
        early_moves = linkograph.moves[:move_count//2]
        late_moves = linkograph.moves[move_count//2:]
        
        early_ids = [m.id for m in early_moves]
        late_ids = [m.id for m in late_moves]
        
        early_links = [l for l in linkograph.links if l.source_move in early_ids]
        late_links = [l for l in linkograph.links if l.source_move in late_ids]
        
        if not early_links or not late_links:
            return 0.5
        
        early_range = np.mean([l.temporal_distance for l in early_links])
        late_range = np.mean([l.temporal_distance for l in late_links])
        
        # Normalize expansion to 0-1
        expansion = (late_range - early_range) / max(early_range, 1) * 0.5 + 0.5
        return max(0.0, min(1.0, expansion))