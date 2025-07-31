"""
Linkography-specific logging system
Captures design moves and links for automated linkography generation
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarking.linkography_engine import LinkographyEngine
from benchmarking.linkography_types import (
    DesignMove as LinkographyMove,
    Linkograph,
    LinkographLink
)
from thesis_tests.data_models import DesignMove, MoveType, TestPhase


class LinkographyLogger:
    """Logger specifically for linkography data"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.linkography_engine = LinkographyEngine()
        
        # Storage
        self.moves: List[LinkographyMove] = []
        self.current_linkograph: Optional[Linkograph] = None
        
        # File paths - use thesis_data directory for benchmarking compatibility
        self.data_dir = Path("thesis_data/linkography")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.linkography_file = self.data_dir / f"linkography_{session_id}.json"
        self.moves_log = self.data_dir / f"linkography_moves_{session_id}.jsonl"
        
        # Initialize files
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize linkography files"""
        # Create empty moves log
        with open(self.moves_log, 'w') as f:
            pass
    
    def convert_to_linkography_move(self, design_move: DesignMove) -> LinkographyMove:
        """Convert test design move to linkography move"""
        # Map move types
        move_type_map = {
            MoveType.ANALYSIS: 'analysis',
            MoveType.SYNTHESIS: 'synthesis',
            MoveType.EVALUATION: 'evaluation',
            MoveType.TRANSFORMATION: 'transformation',
            MoveType.REFLECTION: 'reflection'
        }
        
        # Map phases
        phase_map = {
            TestPhase.IDEATION: 'ideation',
            TestPhase.VISUALIZATION: 'visualization',
            TestPhase.MATERIALIZATION: 'materialization'
        }
        
        # Map modality
        modality_map = {
            'text': 'text',
            'sketch': 'sketch',
            'image': 'sketch',  # Map image to sketch
            'voice': 'verbal',  # Map voice to verbal
            'upload': 'sketch',  # Map upload to sketch
            'diagram': 'sketch',
            'gesture': 'gesture'
        }
        
        linkography_move = LinkographyMove(
            id=design_move.id,
            timestamp=design_move.timestamp.timestamp(),
            session_id=design_move.session_id,
            user_id='participant',  # Default user ID
            phase=phase_map.get(design_move.phase, 'ideation'),
            content=design_move.content,
            move_type=move_type_map.get(design_move.move_type, 'analysis'),
            modality=modality_map.get(design_move.modality.value, 'text'),
            cognitive_load=design_move.complexity_score if hasattr(design_move, 'complexity_score') else 0.5,
            metadata={
                'sequence_number': design_move.sequence_number,
                'design_focus': design_move.design_focus.value,
                'move_source': design_move.move_source.value,
                'cognitive_operation': design_move.cognitive_operation,
                'pause_duration': design_move.pause_duration,
                'revision_count': design_move.revision_count,
                'complexity_score': design_move.complexity_score,
                'ai_influence_strength': design_move.ai_influence_strength,
                'directness_level': design_move.directness_level,
                'cognitive_load_level': design_move.cognitive_load
            }
        )
        
        return linkography_move
    
    def log_design_move(self, design_move: DesignMove):
        """Log a design move and update linkography in real-time"""
        # Convert to linkography move
        linkography_move = self.convert_to_linkography_move(design_move)
        
        # Add to moves list
        self.moves.append(linkography_move)
        
        # Log to file
        with open(self.moves_log, 'a') as f:
            move_dict = {
                'id': linkography_move.id,
                'timestamp': linkography_move.timestamp,
                'session_id': linkography_move.session_id,
                'user_id': linkography_move.user_id,
                'phase': linkography_move.phase,
                'content': linkography_move.content,
                'move_type': linkography_move.move_type,
                'modality': linkography_move.modality,
                'cognitive_load': linkography_move.cognitive_load,
                'metadata': linkography_move.metadata
            }
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'move': move_dict
            }) + '\n')
        
        # Update linkograph
        if self.current_linkograph is None:
            # Create initial linkograph
            self.current_linkograph = self.linkography_engine.generate_linkograph(
                [linkography_move],
                self.session_id
            )
        else:
            # Update existing linkograph
            self.current_linkograph = self.linkography_engine.update_linkograph_realtime(
                self.current_linkograph,
                linkography_move
            )
        
        # Save current state
        self._save_current_linkograph()
    
    def _save_current_linkograph(self):
        """Save current linkograph state"""
        if self.current_linkograph:
            # Convert linkograph to dictionary format
            linkograph_dict = {
                'id': self.current_linkograph.id,
                'session_id': self.current_linkograph.session_id,
                'phase': self.current_linkograph.phase,
                'generated_at': self.current_linkograph.generated_at,
                'move_count': len(self.current_linkograph.moves),
                'link_count': len(self.current_linkograph.links),
                'moves': [
                    {
                        'id': m.id,
                        'timestamp': m.timestamp,
                        'content': m.content,
                        'move_type': m.move_type,
                        'phase': m.phase,
                        'modality': m.modality
                    } for m in self.current_linkograph.moves
                ],
                'links': [
                    {
                        'id': l.id,
                        'source_move': l.source_move,
                        'target_move': l.target_move,
                        'strength': l.strength,
                        'link_type': l.link_type
                    } for l in self.current_linkograph.links
                ]
            }
            
            linkograph_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'linkograph': linkograph_dict,
                'metrics': self.current_linkograph.metrics.__dict__ if self.current_linkograph.metrics else {},
                'move_count': len(self.moves),
                'link_count': len(self.current_linkograph.links) if self.current_linkograph else 0
            }
            
            with open(self.linkography_file, 'w') as f:
                json.dump(linkograph_data, f, indent=2)
    
    def get_current_linkograph(self) -> Optional[Linkograph]:
        """Get current linkograph"""
        return self.current_linkograph
    
    def get_linkography_metrics(self) -> Dict[str, float]:
        """Get current linkography metrics"""
        # Base metrics with defaults
        metrics = {
            'total_moves': len(self.moves),
            'total_links': 0,
            'link_density': 0.0,
            'move_diversity': 0.0,
            'critical_move_ratio': 0.0,
            'entropy': 0.0,
            'orphan_move_ratio': 0.0,
            'avg_link_strength': 0.0,
            'chunk_count': 0,
            'web_count': 0,
            'sawtooth_count': 0
        }
        
        # Update with actual metrics if available
        if self.current_linkograph:
            metrics['total_links'] = len(self.current_linkograph.links)
            
            if self.current_linkograph.metrics:
                metrics.update({
                    'link_density': self.current_linkograph.metrics.link_density,
                    'critical_move_ratio': self.current_linkograph.metrics.critical_move_ratio,
                    'entropy': self.current_linkograph.metrics.entropy,
                    'orphan_move_ratio': self.current_linkograph.metrics.orphan_move_ratio,
                    'avg_link_strength': self.current_linkograph.metrics.avg_link_strength,
                    'chunk_count': self.current_linkograph.metrics.chunk_count,
                    'web_count': self.current_linkograph.metrics.web_count,
                    'sawtooth_count': self.current_linkograph.metrics.sawtooth_count
                })
            
            # Calculate move diversity
            if len(self.moves) > 0:
                move_types = [m.move_type for m in self.moves]
                unique_types = len(set(move_types))
                metrics['move_diversity'] = unique_types / len(move_types) if len(move_types) > 0 else 0.0
        
        return metrics
    
    def get_cognitive_indicators(self) -> Dict[str, float]:
        """Get cognitive indicators from linkography"""
        if self.current_linkograph and self.current_linkograph.metrics:
            return self.current_linkograph.metrics.cognitive_indicators
        return {}
    
    def finalize(self):
        """Finalize linkography logging"""
        if self.current_linkograph:
            # Regenerate complete linkograph with all moves
            self.current_linkograph = self.linkography_engine.generate_linkograph(
                self.moves,
                self.session_id
            )
            
            # Save final linkograph
            # Convert linkograph to dictionary
            linkograph_dict = {
                'id': self.current_linkograph.id,
                'session_id': self.current_linkograph.session_id,
                'phase': self.current_linkograph.phase,
                'generated_at': self.current_linkograph.generated_at,
                'move_count': len(self.current_linkograph.moves),
                'link_count': len(self.current_linkograph.links),
                'moves': [
                    {
                        'id': m.id,
                        'timestamp': m.timestamp,
                        'content': m.content,
                        'move_type': m.move_type,
                        'phase': m.phase,
                        'modality': m.modality
                    } for m in self.current_linkograph.moves
                ],
                'links': [
                    {
                        'id': l.id,
                        'source_move': l.source_move,
                        'target_move': l.target_move,
                        'strength': l.strength,
                        'link_type': l.link_type
                    } for l in self.current_linkograph.links
                ]
            }
            
            final_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'linkograph': linkograph_dict,
                'metrics': self.current_linkograph.metrics.__dict__ if self.current_linkograph.metrics else {},
                'move_count': len(self.moves),
                'link_count': len(self.current_linkograph.links),
                'critical_moves': [m.id for m in self.current_linkograph.get_critical_moves()],
                'patterns': self._extract_patterns(),
                'phase_distribution': self._calculate_phase_distribution()
            }
            
            with open(self.linkography_file, 'w') as f:
                json.dump(final_data, f, indent=2)
    
    def _extract_patterns(self) -> Dict[str, Any]:
        """Extract linkographic patterns"""
        if not self.current_linkograph:
            return {}
        
        # Pattern detection would be implemented here
        # For now, return basic pattern counts from metrics
        return {
            'chunks': self.current_linkograph.metrics.chunk_count if self.current_linkograph.metrics else 0,
            'webs': self.current_linkograph.metrics.web_count if self.current_linkograph.metrics else 0,
            'sawteeth': self.current_linkograph.metrics.sawtooth_count if self.current_linkograph.metrics else 0
        }
    
    def _calculate_phase_distribution(self) -> Dict[str, float]:
        """Calculate distribution of moves across phases"""
        phase_counts = {'ideation': 0, 'visualization': 0, 'materialization': 0}
        
        for move in self.moves:
            if move.phase in phase_counts:
                phase_counts[move.phase] += 1
        
        total = sum(phase_counts.values())
        if total > 0:
            return {phase: count/total for phase, count in phase_counts.items()}
        return phase_counts
    
    def export_linkography_data(self) -> str:
        """Export linkography data"""
        self.finalize()
        return str(self.linkography_file)
    
    def get_linkograph_for_visualization(self) -> Optional[Dict[str, Any]]:
        """Get linkograph data formatted for visualization"""
        if not self.current_linkograph:
            return None
        
        # Format for visualization tools
        nodes = []
        for move in self.moves:
            nodes.append({
                'id': move.id,
                'label': f"M{move.sequence_number}",
                'title': move.content[:100] + "..." if len(move.content) > 100 else move.content,
                'group': move.phase,
                'value': len([l for l in self.current_linkograph.links 
                             if l.source_move == move.id or l.target_move == move.id])
            })
        
        edges = []
        for link in self.current_linkograph.links:
            edges.append({
                'from': link.source_move,
                'to': link.target_move,
                'value': link.strength,
                'title': f"Strength: {link.strength:.2f}",
                'arrows': 'to'
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': self.get_linkography_metrics()
        }