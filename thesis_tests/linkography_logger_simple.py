"""
Simplified Linkography Logger
Works without external benchmarking dependencies
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid

from thesis_tests.data_models import DesignMove, MoveType, TestPhase


class SimpleLinkographyLogger:
    """Simplified logger for linkography data without external dependencies"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        
        # Storage
        self.moves: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        
        # File paths
        self.data_dir = Path("thesis_tests/linkography_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.linkography_file = self.data_dir / f"linkography_{session_id}.json"
        self.moves_log = self.data_dir / f"linkography_moves_{session_id}.jsonl"
        
        # Initialize files
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize linkography files"""
        with open(self.moves_log, 'w') as f:
            pass
    
    def log_design_move(self, design_move: DesignMove):
        """Log a design move"""
        # Convert to dictionary
        move_dict = {
            'id': design_move.id,
            'session_id': design_move.session_id,
            'timestamp': design_move.timestamp.isoformat(),
            'sequence_number': design_move.sequence_number,
            'content': design_move.content,
            'move_type': design_move.move_type.value,
            'phase': design_move.phase.value,
            'modality': design_move.modality.value,
            'cognitive_operation': design_move.cognitive_operation,
            'design_focus': design_move.design_focus.value,
            'move_source': design_move.move_source.value,
            'cognitive_load': design_move.cognitive_load,
            'metadata': {
                'pause_duration': design_move.pause_duration,
                'revision_count': design_move.revision_count,
                'complexity_score': design_move.complexity_score,
                'ai_influence_strength': design_move.ai_influence_strength,
                'directness_level': design_move.directness_level
            }
        }
        
        # Add to moves list
        self.moves.append(move_dict)
        
        # Log to file
        with open(self.moves_log, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'move': move_dict
            }) + '\n')
        
        # Create simple links based on sequence
        if len(self.moves) > 1:
            # Link to previous move
            link = {
                'id': str(uuid.uuid4()),
                'source_move': self.moves[-2]['id'],
                'target_move': move_dict['id'],
                'strength': 0.5,  # Default strength
                'link_type': 'temporal'
            }
            self.links.append(link)
        
        # Save current state
        self._save_current_linkograph()
    
    def _save_current_linkograph(self):
        """Save current linkograph state"""
        linkograph_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'moves': self.moves,
            'links': self.links,
            'move_count': len(self.moves),
            'link_count': len(self.links),
            'metrics': self._calculate_simple_metrics()
        }
        
        with open(self.linkography_file, 'w') as f:
            json.dump(linkograph_data, f, indent=2)
    
    def _calculate_simple_metrics(self) -> Dict[str, float]:
        """Calculate simple linkography metrics"""
        if not self.moves:
            return {
                'link_density': 0.0,
                'move_diversity': 0.0,
                'phase_balance': {}
            }
        
        # Link density
        link_density = len(self.links) / len(self.moves) if self.moves else 0.0
        
        # Move type diversity
        move_types = set(m['move_type'] for m in self.moves)
        move_diversity = len(move_types) / 5  # 5 possible move types
        
        # Phase balance
        phase_counts = {}
        for move in self.moves:
            phase = move['phase']
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        total_moves = len(self.moves)
        phase_balance = {
            phase: count / total_moves 
            for phase, count in phase_counts.items()
        }
        
        return {
            'link_density': link_density,
            'move_diversity': move_diversity,
            'phase_balance': phase_balance
        }
    
    def get_linkography_metrics(self) -> Dict[str, float]:
        """Get current linkography metrics"""
        metrics = self._calculate_simple_metrics()
        return {
            'link_density': metrics['link_density'],
            'move_diversity': metrics['move_diversity'],
            'total_moves': len(self.moves),
            'total_links': len(self.links)
        }
    
    def get_cognitive_indicators(self) -> Dict[str, float]:
        """Get simplified cognitive indicators"""
        # Simple calculations based on move patterns
        if not self.moves:
            return {
                'deep_thinking': 0.0,
                'offloading_prevention': 0.0,
                'knowledge_integration': 0.0,
                'learning_progression': 0.0,
                'metacognitive_awareness': 0.0
            }
        
        # Count different move types
        move_type_counts = {}
        for move in self.moves:
            mt = move['move_type']
            move_type_counts[mt] = move_type_counts.get(mt, 0) + 1
        
        total_moves = len(self.moves)
        
        # Simple cognitive indicators based on move types
        return {
            'deep_thinking': move_type_counts.get('evaluation', 0) / total_moves,
            'offloading_prevention': 1.0 - (move_type_counts.get('analysis', 0) / total_moves),
            'knowledge_integration': move_type_counts.get('synthesis', 0) / total_moves,
            'learning_progression': min(total_moves / 50, 1.0),  # Progress indicator
            'metacognitive_awareness': move_type_counts.get('reflection', 0) / total_moves
        }
    
    def finalize(self):
        """Finalize linkography logging"""
        final_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'moves': self.moves,
            'links': self.links,
            'move_count': len(self.moves),
            'link_count': len(self.links),
            'metrics': self._calculate_simple_metrics(),
            'phase_distribution': self._calculate_phase_distribution()
        }
        
        with open(self.linkography_file, 'w') as f:
            json.dump(final_data, f, indent=2)
    
    def _calculate_phase_distribution(self) -> Dict[str, float]:
        """Calculate distribution of moves across phases"""
        phase_counts = {}
        
        for move in self.moves:
            phase = move['phase']
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        total = sum(phase_counts.values())
        if total > 0:
            return {phase: count/total for phase, count in phase_counts.items()}
        return phase_counts
    
    def export_linkography_data(self) -> str:
        """Export linkography data"""
        self.finalize()
        return str(self.linkography_file)