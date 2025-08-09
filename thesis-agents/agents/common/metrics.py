"""
Shared metrics calculation utilities for agents.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from ..utils.agent_response import EnhancementMetrics


class MetricsCalculator:
    """
    Shared metrics calculation utilities for cognitive and performance metrics.
    """
    
    @staticmethod
    def calculate_confidence_score(indicators: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calculate weighted confidence score from multiple indicators.
        
        Args:
            indicators: Dictionary of indicator scores
            weights: Dictionary of weights for each indicator
            
        Returns:
            Weighted confidence score (0.0 to 1.0)
        """
        if not indicators or not weights:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for indicator, score in indicators.items():
            weight = weights.get(indicator, 1.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(max(total_weighted_score / total_weight, 0.0), 1.0)
    
    @staticmethod
    def calculate_skill_confidence(message_count: int, total_words: int, technical_terms: int) -> float:
        """
        Calculate confidence in skill level assessment.
        
        Args:
            message_count: Number of messages from user
            total_words: Total word count
            technical_terms: Count of technical terms used
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # More messages = higher confidence
        message_confidence = min(message_count / 5, 1.0)
        
        # More words = higher confidence
        length_confidence = min(total_words / 100, 1.0)
        
        # Technical terms indicate clearer skill level
        technical_confidence = min(technical_terms / 10, 1.0) if technical_terms > 0 else 0.0
        
        return (message_confidence + length_confidence + technical_confidence) / 3
    
    @staticmethod
    def calculate_phase_confidence(phase_scores: Dict[str, float], threshold: float = 0.6) -> float:
        """
        Calculate confidence in phase detection.
        
        Args:
            phase_scores: Dictionary of phase scores
            threshold: Minimum threshold for confidence
            
        Returns:
            Confidence score
        """
        if not phase_scores:
            return 0.0
        
        max_score = max(phase_scores.values())
        scores = list(phase_scores.values())
        scores.sort(reverse=True)
        
        # High confidence if top score is well above others
        if len(scores) > 1:
            separation = scores[0] - scores[1]
            confidence = max_score * (1 + separation)
        else:
            confidence = max_score
        
        return min(confidence, 1.0)
    
    @staticmethod
    def calculate_enhancement_metrics(
        analysis_result: Dict[str, Any],
        cognitive_flags: List[str],
        phase_confidence: float
    ) -> EnhancementMetrics:
        """
        Calculate comprehensive enhancement metrics.
        
        Args:
            analysis_result: Analysis results dictionary
            cognitive_flags: List of cognitive flags
            phase_confidence: Phase detection confidence
            
        Returns:
            EnhancementMetrics object
        """
        # Extract relevant metrics from analysis
        synthesis = analysis_result.get('synthesis', {})
        cognitive_challenges = len(synthesis.get('cognitive_challenges', []))
        learning_opportunities = len(synthesis.get('learning_opportunities', []))
        
        # Calculate individual metrics
        cop_score = MetricsCalculator._calculate_cop_score(cognitive_flags, cognitive_challenges)
        dte_score = MetricsCalculator._calculate_dte_score(learning_opportunities, analysis_result)
        ki_score = MetricsCalculator._calculate_ki_score(analysis_result)
        scaffolding_score = MetricsCalculator._calculate_scaffolding_score(analysis_result)
        learning_progression_score = phase_confidence
        metacognitive_score = MetricsCalculator._calculate_metacognitive_score(cognitive_flags)
        
        # Calculate overall score
        overall_score = (cop_score + dte_score + ki_score + scaffolding_score + 
                        learning_progression_score + metacognitive_score) / 6
        
        return EnhancementMetrics(
            cognitive_offloading_prevention_score=cop_score,
            deep_thinking_engagement_score=dte_score,
            knowledge_integration_score=ki_score,
            scaffolding_effectiveness_score=scaffolding_score,
            learning_progression_score=learning_progression_score,
            metacognitive_awareness_score=metacognitive_score,
            overall_cognitive_score=overall_score,
            scientific_confidence=min(phase_confidence + 0.2, 1.0)  # Boost confidence slightly
        )
    
    @staticmethod
    def _calculate_cop_score(cognitive_flags: List[str], cognitive_challenges: int) -> float:
        """Calculate Cognitive Offloading Prevention score."""
        # Higher score if we're identifying challenges (preventing offloading)
        flag_score = len([f for f in cognitive_flags if 'challenge' in f.lower()]) * 0.2
        challenge_score = min(cognitive_challenges * 0.1, 0.6)
        return min(flag_score + challenge_score + 0.3, 1.0)  # Base score of 0.3
    
    @staticmethod
    def _calculate_dte_score(learning_opportunities: int, analysis_result: Dict) -> float:
        """Calculate Deep Thinking Engagement score."""
        # Higher score if we're providing learning opportunities
        opportunity_score = min(learning_opportunities * 0.15, 0.7)
        
        # Bonus for complex analysis
        if analysis_result.get('phase_analysis', {}).get('confidence', 0) > 0.7:
            complexity_bonus = 0.2
        else:
            complexity_bonus = 0.0
        
        return min(opportunity_score + complexity_bonus + 0.2, 1.0)  # Base score of 0.2
    
    @staticmethod
    def _calculate_ki_score(analysis_result: Dict) -> float:
        """Calculate Knowledge Integration score."""
        # Score based on synthesis quality
        synthesis = analysis_result.get('synthesis', {})
        next_focus_areas = len(synthesis.get('next_focus_areas', []))
        missing_considerations = len(synthesis.get('missing_considerations', []))
        
        integration_score = min((next_focus_areas + missing_considerations) * 0.1, 0.8)
        return integration_score + 0.2  # Base score of 0.2
    
    @staticmethod
    def _calculate_scaffolding_score(analysis_result: Dict) -> float:
        """Calculate Scaffolding Effectiveness score."""
        # Score based on appropriate guidance level
        phase_analysis = analysis_result.get('phase_analysis', {})
        recommendations = len(phase_analysis.get('phase_recommendations', []))
        
        scaffolding_score = min(recommendations * 0.2, 0.8)
        return scaffolding_score + 0.2  # Base score of 0.2
    
    @staticmethod
    def _calculate_metacognitive_score(cognitive_flags: List[str]) -> float:
        """Calculate Metacognitive Awareness score."""
        # Score based on metacognitive flags
        metacognitive_flags = [f for f in cognitive_flags if any(
            term in f.lower() for term in ['reflection', 'awareness', 'thinking', 'consider']
        )]
        
        score = min(len(metacognitive_flags) * 0.25, 0.8)
        return score + 0.2  # Base score of 0.2 