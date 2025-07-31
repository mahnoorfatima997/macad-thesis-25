#!/usr/bin/env python3
"""
Pattern Recognition Module for Linkography Analysis
Detects cognitive patterns like overload, design fixation, and creative breakthroughs
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime, timedelta
from thesis_colors import (
    THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS, 
    PLOTLY_COLORSCALES, CHART_COLORS, UI_COLORS,
    get_color_palette, get_metric_color, get_proficiency_color, get_agent_color
)


class CognitivePatternDetector:
    """Detects cognitive patterns in design thinking processes"""
    
    def __init__(self):
        """Initialize the cognitive pattern detector"""
        
        # Thresholds for pattern detection
        self.cognitive_overload_threshold = 0.7
        self.fixation_threshold = 0.4  # Percentage of moves of same type
        self.breakthrough_threshold = 0.8  # High cognitive load + phase transition
        self.temporal_cluster_threshold = 3  # Minimum moves in temporal cluster
        
        print("Cognitive Pattern Detector initialized")
    
    def detect_cognitive_overload(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect cognitive overload patterns"""
        
        if not moves:
            return {"overload_detected": False, "overload_moves": [], "overload_score": 0.0}
        
        # Extract cognitive loads
        cognitive_loads = [move.get('cognitive_load', 0.0) for move in moves]
        
        # Calculate overload statistics
        avg_load = np.mean(cognitive_loads)
        max_load = np.max(cognitive_loads)
        overload_moves = [move for move in moves if move.get('cognitive_load', 0.0) > self.cognitive_overload_threshold]
        
        # Detect overload periods (consecutive high-load moves)
        overload_periods = self._detect_overload_periods(moves)
        
        # Calculate overload score
        overload_score = len(overload_moves) / len(moves) if moves else 0.0
        
        return {
            "overload_detected": overload_score > 0.2,  # More than 20% of moves are overloaded
            "overload_moves": overload_moves,
            "overload_periods": overload_periods,
            "overload_score": overload_score,
            "average_cognitive_load": avg_load,
            "max_cognitive_load": max_load,
            "overload_threshold": self.cognitive_overload_threshold,
            "overload_percentage": overload_score * 100
        }
    
    def _detect_overload_periods(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect periods of consecutive cognitive overload"""
        
        overload_periods = []
        current_period = []
        
        for i, move in enumerate(moves):
            if move.get('cognitive_load', 0.0) > self.cognitive_overload_threshold:
                current_period.append(move)
            else:
                if len(current_period) >= 2:  # At least 2 consecutive overload moves
                    period_info = {
                        "start_index": i - len(current_period),
                        "end_index": i - 1,
                        "duration": len(current_period),
                        "moves": current_period,
                        "average_load": np.mean([m.get('cognitive_load', 0.0) for m in current_period])
                    }
                    overload_periods.append(period_info)
                current_period = []
        
        # Check for period at the end
        if len(current_period) >= 2:
            period_info = {
                "start_index": len(moves) - len(current_period),
                "end_index": len(moves) - 1,
                "duration": len(current_period),
                "moves": current_period,
                "average_load": np.mean([m.get('cognitive_load', 0.0) for m in current_period])
            }
            overload_periods.append(period_info)
        
        return overload_periods
    
    def detect_design_fixation(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect design fixation patterns"""
        
        if not moves:
            return {"fixation_detected": False, "fixation_patterns": [], "fixation_score": 0.0}
        
        # Analyze move type distribution
        move_types = [move.get('move_type', 'unknown') for move in moves]
        type_counts = {}
        for move_type in move_types:
            type_counts[move_type] = type_counts.get(move_type, 0) + 1
        
        # Detect dominant move types
        total_moves = len(moves)
        dominant_types = {t: c for t, c in type_counts.items() if c / total_moves > self.fixation_threshold}
        
        # Detect temporal clustering of same move types
        temporal_clusters = self._detect_temporal_clusters(moves)
        
        # Detect repetitive content patterns
        content_patterns = self._detect_repetitive_content(moves)
        
        # Calculate fixation score
        fixation_score = len(dominant_types) / len(set(move_types)) if move_types else 0.0
        
        return {
            "fixation_detected": fixation_score < 0.5,  # Low diversity indicates fixation
            "dominant_move_types": dominant_types,
            "temporal_clusters": temporal_clusters,
            "content_patterns": content_patterns,
            "fixation_score": fixation_score,
            "move_type_diversity": len(set(move_types)),
            "fixation_threshold": self.fixation_threshold
        }
    
    def _detect_temporal_clusters(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect temporal clusters of same move types"""
        
        temporal_clusters = []
        current_cluster = []
        
        for i, move in enumerate(moves):
            if not current_cluster or move.get('move_type') == current_cluster[-1].get('move_type'):
                current_cluster.append(move)
            else:
                if len(current_cluster) >= self.temporal_cluster_threshold:
                    cluster_info = {
                        "start_index": i - len(current_cluster),
                        "end_index": i - 1,
                        "duration": len(current_cluster),
                        "move_type": current_cluster[0].get('move_type'),
                        "moves": current_cluster
                    }
                    temporal_clusters.append(cluster_info)
                current_cluster = [move]
        
        # Check for cluster at the end
        if len(current_cluster) >= self.temporal_cluster_threshold:
            cluster_info = {
                "start_index": len(moves) - len(current_cluster),
                "end_index": len(moves) - 1,
                "duration": len(current_cluster),
                "move_type": current_cluster[0].get('move_type'),
                "moves": current_cluster
            }
            temporal_clusters.append(cluster_info)
        
        return temporal_clusters
    
    def _detect_repetitive_content(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect repetitive content patterns"""
        
        content_patterns = []
        
        # Look for repeated phrases or concepts
        contents = [move.get('content', '').lower() for move in moves]
        
        # Simple keyword repetition detection
        keywords = {}
        for content in contents:
            words = content.split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    keywords[word] = keywords.get(word, 0) + 1
        
        # Find frequently repeated keywords
        repeated_keywords = {word: count for word, count in keywords.items() if count >= 3}
        
        if repeated_keywords:
            content_patterns.append({
                "pattern_type": "keyword_repetition",
                "keywords": repeated_keywords,
                "description": f"Repeated keywords: {list(repeated_keywords.keys())}"
            })
        
        return content_patterns
    
    def detect_creative_breakthroughs(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect potential creative breakthroughs"""
        
        if len(moves) < 2:
            return []
        
        breakthroughs = []
        
        # Look for phase transitions with high cognitive load
        for i in range(1, len(moves)):
            current_move = moves[i]
            previous_move = moves[i-1]
            
            current_phase = current_move.get('phase', 'unknown')
            previous_phase = previous_move.get('phase', 'unknown')
            current_load = current_move.get('cognitive_load', 0.0)
            
            # Phase transition with high cognitive load
            if (current_phase != previous_phase and 
                current_load > self.breakthrough_threshold):
                
                breakthrough = {
                    "move_index": i,
                    "move": current_move,
                    "breakthrough_type": "phase_transition",
                    "phase_transition": f"{previous_phase} → {current_phase}",
                    "cognitive_load": current_load,
                    "confidence": self._calculate_breakthrough_confidence(current_move, moves, i)
                }
                breakthroughs.append(breakthrough)
        
        # Look for high-connectivity moves (many semantic links)
        connectivity_breakthroughs = self._detect_connectivity_breakthroughs(moves)
        breakthroughs.extend(connectivity_breakthroughs)
        
        # Look for novel move types
        novelty_breakthroughs = self._detect_novelty_breakthroughs(moves)
        breakthroughs.extend(novelty_breakthroughs)
        
        return breakthroughs
    
    def _calculate_breakthrough_confidence(self, move: Dict[str, Any], 
                                         all_moves: List[Dict[str, Any]], 
                                         move_index: int) -> float:
        """Calculate confidence score for a breakthrough"""
        
        confidence = 0.0
        
        # High cognitive load increases confidence
        cognitive_load = move.get('cognitive_load', 0.0)
        confidence += cognitive_load * 0.4
        
        # Novel move type increases confidence
        move_type = move.get('move_type', 'unknown')
        previous_types = [m.get('move_type', 'unknown') for m in all_moves[:move_index]]
        if move_type not in previous_types:
            confidence += 0.3
        
        # Phase transition increases confidence
        if move_index > 0:
            current_phase = move.get('phase', 'unknown')
            previous_phase = all_moves[move_index-1].get('phase', 'unknown')
            if current_phase != previous_phase:
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _detect_connectivity_breakthroughs(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect breakthroughs based on connectivity patterns"""
        
        # This would require semantic similarity analysis
        # For now, return empty list - will be implemented with linkography data
        return []
    
    def _detect_novelty_breakthroughs(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect breakthroughs based on novelty of move types"""
        
        breakthroughs = []
        
        for i, move in enumerate(moves):
            move_type = move.get('move_type', 'unknown')
            previous_types = [m.get('move_type', 'unknown') for m in moves[:i]]
            
            # Novel move type that hasn't appeared before
            if move_type not in previous_types and i > 0:
                breakthrough = {
                    "move_index": i,
                    "move": move,
                    "breakthrough_type": "novel_move_type",
                    "novel_type": move_type,
                    "confidence": 0.6
                }
                breakthroughs.append(breakthrough)
        
        return breakthroughs
    
    def analyze_cognitive_flow(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall cognitive flow of the design process"""
        
        if not moves:
            return {"flow_analysis": {}, "flow_patterns": []}
        
        # Analyze cognitive load progression
        cognitive_loads = [move.get('cognitive_load', 0.0) for move in moves]
        load_progression = self._analyze_load_progression(cognitive_loads)
        
        # Analyze phase progression
        phase_progression = self._analyze_phase_progression(moves)
        
        # Analyze move type patterns
        move_type_patterns = self._analyze_move_type_patterns(moves)
        
        # Detect flow patterns
        flow_patterns = self._detect_flow_patterns(moves)
        
        return {
            "flow_analysis": {
                "load_progression": load_progression,
                "phase_progression": phase_progression,
                "move_type_patterns": move_type_patterns
            },
            "flow_patterns": flow_patterns,
            "total_moves": len(moves),
            "average_load": np.mean(cognitive_loads),
            "load_variability": np.std(cognitive_loads)
        }
    
    def _analyze_load_progression(self, cognitive_loads: List[float]) -> Dict[str, Any]:
        """Analyze progression of cognitive load over time"""
        
        if len(cognitive_loads) < 2:
            return {"trend": "insufficient_data", "peaks": [], "valleys": []}
        
        # Calculate trend
        x = np.arange(len(cognitive_loads))
        slope = np.polyfit(x, cognitive_loads, 1)[0]
        
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Find peaks and valleys
        peaks = []
        valleys = []
        
        for i in range(1, len(cognitive_loads) - 1):
            if cognitive_loads[i] > cognitive_loads[i-1] and cognitive_loads[i] > cognitive_loads[i+1]:
                peaks.append({"index": i, "value": cognitive_loads[i]})
            elif cognitive_loads[i] < cognitive_loads[i-1] and cognitive_loads[i] < cognitive_loads[i+1]:
                valleys.append({"index": i, "value": cognitive_loads[i]})
        
        return {
            "trend": trend,
            "slope": slope,
            "peaks": peaks,
            "valleys": valleys,
            "peak_count": len(peaks),
            "valley_count": len(valleys)
        }
    
    def _analyze_phase_progression(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze progression through design phases"""
        
        phases = [move.get('phase', 'unknown') for move in moves]
        unique_phases = list(set(phases))
        
        # Count phase transitions
        transitions = []
        for i in range(1, len(phases)):
            if phases[i] != phases[i-1]:
                transitions.append({
                    "from_phase": phases[i-1],
                    "to_phase": phases[i],
                    "index": i
                })
        
        # Calculate phase distribution
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        return {
            "unique_phases": unique_phases,
            "phase_transitions": transitions,
            "transition_count": len(transitions),
            "phase_distribution": phase_counts,
            "phase_balance": len(unique_phases) / 3  # 3 phases: ideation, visualization, materialization
        }
    
    def _analyze_move_type_patterns(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in move types"""
        
        move_types = [move.get('move_type', 'unknown') for move in moves]
        unique_types = list(set(move_types))
        
        # Calculate type distribution
        type_counts = {}
        for move_type in move_types:
            type_counts[move_type] = type_counts.get(move_type, 0) + 1
        
        # Find most common type
        most_common = max(type_counts.items(), key=lambda x: x[1]) if type_counts else None
        
        return {
            "unique_types": unique_types,
            "type_distribution": type_counts,
            "most_common_type": most_common,
            "type_diversity": len(unique_types),
            "type_balance": len(unique_types) / 5  # 5 move types: analysis, synthesis, evaluation, transformation, reflection
        }
    
    def _detect_flow_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect specific flow patterns in the design process"""
        
        patterns = []
        
        # Detect iterative patterns
        iterative_patterns = self._detect_iterative_patterns(moves)
        patterns.extend(iterative_patterns)
        
        # Detect linear progression
        linear_patterns = self._detect_linear_patterns(moves)
        patterns.extend(linear_patterns)
        
        # Detect circular patterns
        circular_patterns = self._detect_circular_patterns(moves)
        patterns.extend(circular_patterns)
        
        return patterns
    
    def _detect_iterative_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect iterative patterns in the design process"""
        
        patterns = []
        
        # Look for repeated phase sequences
        phases = [move.get('phase', 'unknown') for move in moves]
        
        # Simple iteration detection: same phase appears multiple times
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        iterative_phases = [phase for phase, count in phase_counts.items() if count > 1]
        
        if iterative_phases:
            patterns.append({
                "pattern_type": "iteration",
                "description": f"Iterative phases: {iterative_phases}",
                "iterative_phases": iterative_phases,
                "confidence": 0.7
            })
        
        return patterns
    
    def _detect_linear_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect linear progression patterns"""
        
        patterns = []
        
        # Check if phases follow a linear progression
        phases = [move.get('phase', 'unknown') for move in moves]
        unique_phases = list(dict.fromkeys(phases))  # Preserve order
        
        # Expected linear progression: ideation -> visualization -> materialization
        expected_progression = ['ideation', 'visualization', 'materialization']
        
        # Check if phases follow expected progression
        linear_score = 0
        for i, phase in enumerate(unique_phases):
            if phase in expected_progression:
                expected_index = expected_progression.index(phase)
                if i == expected_index:
                    linear_score += 1
        
        linear_confidence = linear_score / len(expected_progression) if expected_progression else 0
        
        if linear_confidence > 0.6:
            patterns.append({
                "pattern_type": "linear_progression",
                "description": "Linear progression through design phases",
                "linear_confidence": linear_confidence,
                "confidence": linear_confidence
            })
        
        return patterns
    
    def _detect_circular_patterns(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect circular patterns in the design process"""
        
        patterns = []
        
        # Look for cycles in move types
        move_types = [move.get('move_type', 'unknown') for move in moves]
        
        # Simple cycle detection: same move type appears at beginning and end
        if len(move_types) >= 3:
            first_type = move_types[0]
            last_type = move_types[-1]
            
            if first_type == last_type:
                patterns.append({
                    "pattern_type": "circular",
                    "description": f"Circular pattern: starts and ends with {first_type}",
                    "cycle_type": first_type,
                    "confidence": 0.6
                })
        
        return patterns
    
    def generate_pattern_report(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive pattern analysis report"""
        
        # Detect all patterns
        overload_analysis = self.detect_cognitive_overload(moves)
        fixation_analysis = self.detect_design_fixation(moves)
        breakthroughs = self.detect_creative_breakthroughs(moves)
        flow_analysis = self.analyze_cognitive_flow(moves)
        
        # Generate summary
        pattern_summary = {
            "cognitive_overload": overload_analysis["overload_detected"],
            "design_fixation": fixation_analysis["fixation_detected"],
            "creative_breakthroughs": len(breakthroughs),
            "flow_patterns": len(flow_analysis["flow_patterns"])
        }
        
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_moves": len(moves),
                "analysis_parameters": {
                    "overload_threshold": self.cognitive_overload_threshold,
                    "fixation_threshold": self.fixation_threshold,
                    "breakthrough_threshold": self.breakthrough_threshold
                }
            },
            "pattern_summary": pattern_summary,
            "cognitive_overload": overload_analysis,
            "design_fixation": fixation_analysis,
            "creative_breakthroughs": breakthroughs,
            "cognitive_flow": flow_analysis
        }


def test_pattern_recognition():
    """Test the pattern recognition module"""
    
    print("🧪 Testing Cognitive Pattern Detector...")
    
    # Sample design moves with various patterns
    sample_moves = [
        {"content": "I want to design a sustainable building", "phase": "ideation", "move_type": "synthesis", "cognitive_load": 0.6},
        {"content": "Let me consider solar orientation", "phase": "ideation", "move_type": "analysis", "cognitive_load": 0.7},
        {"content": "I'll sketch the south-facing facade", "phase": "visualization", "move_type": "transformation", "cognitive_load": 0.8},
        {"content": "This needs better structural support", "phase": "materialization", "move_type": "analysis", "cognitive_load": 0.9},
        {"content": "Let me go back to the concept", "phase": "ideation", "move_type": "synthesis", "cognitive_load": 0.7},
        {"content": "I think the form is perfect", "phase": "ideation", "move_type": "evaluation", "cognitive_load": 0.5},
        {"content": "Actually, let me reconsider", "phase": "ideation", "move_type": "reflection", "cognitive_load": 0.8}
    ]
    
    # Initialize detector
    detector = CognitivePatternDetector()
    
    # Generate pattern report
    report = detector.generate_pattern_report(sample_moves)
    
    print(f"\n📊 Pattern Recognition Results:")
    print(f"   Cognitive Overload: {report['pattern_summary']['cognitive_overload']}")
    print(f"   Design Fixation: {report['pattern_summary']['design_fixation']}")
    print(f"   Creative Breakthroughs: {report['pattern_summary']['creative_breakthroughs']}")
    print(f"   Flow Patterns: {report['pattern_summary']['flow_patterns']}")
    
    print(f"\n🧠 Cognitive Overload Analysis:")
    print(f"   Overload Score: {report['cognitive_overload']['overload_score']:.3f}")
    print(f"   Overload Percentage: {report['cognitive_overload']['overload_percentage']:.1f}%")
    
    print(f"\n🔒 Design Fixation Analysis:")
    print(f"   Fixation Score: {report['design_fixation']['fixation_score']:.3f}")
    print(f"   Dominant Types: {list(report['design_fixation']['dominant_move_types'].keys())}")
    
    print(f"\n💡 Creative Breakthroughs:")
    for breakthrough in report['creative_breakthroughs']:
        print(f"   - {breakthrough['breakthrough_type']}: {breakthrough['move']['content'][:50]}...")
    
    print(f"\n✅ Cognitive Pattern Detector working!")


if __name__ == "__main__":
    test_pattern_recognition() 