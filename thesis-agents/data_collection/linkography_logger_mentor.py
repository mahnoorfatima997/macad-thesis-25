"""
Linkography Logger for Mentor.py Application
Adapted from thesis_tests/linkography_logger.py to work with mentor.py architecture
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid

# Try to import benchmarking dependencies
BENCHMARKING_AVAILABLE = False
try:
    # Add project root to path for benchmarking imports
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from benchmarking.linkography_engine import LinkographyEngine
    from benchmarking.linkography_types import (
        DesignMove as LinkographyMove,
        Linkograph,
        LinkographLink
    )
    BENCHMARKING_AVAILABLE = True
    print("✅ Benchmarking linkography engine available")
except ImportError as e:
    print(f"⚠️ Benchmarking linkography engine not available: {e}")
    # Define minimal classes for fallback
    class LinkographyMove:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Linkograph:
        def __init__(self):
            self.moves = []
            self.links = []
            self.metrics = None
    
    class LinkographyEngine:
        def generate_linkograph(self, moves, session_id):
            return Linkograph()
        
        def update_linkograph_realtime(self, linkograph, move):
            return linkograph


class MentorLinkographyLogger:
    """Linkography logger adapted for mentor.py application"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.benchmarking_available = BENCHMARKING_AVAILABLE
        
        if self.benchmarking_available:
            self.linkography_engine = LinkographyEngine()
        else:
            self.linkography_engine = LinkographyEngine()  # Fallback version
        
        # Storage
        self.moves: List[LinkographyMove] = []
        self.current_linkograph: Optional[Linkograph] = None
        
        # File paths - use thesis_data directory for consistency
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
    
    def create_design_move_from_interaction(self, content: str, move_type: str, 
                                          move_source: str, phase: str = "ideation",
                                          modality: str = "text", design_focus: str = "function") -> Dict[str, Any]:
        """Create a design move from interaction data (compatible with mentor.py)"""
        
        # Map move types to standard categories
        move_type_map = {
            "analysis": "analysis",
            "synthesis": "synthesis", 
            "evaluation": "evaluation",
            "transformation": "transformation",
            "reflection": "reflection",
            "question": "analysis",
            "response": "synthesis",
            "clarification": "evaluation",
            "suggestion": "transformation",
            "feedback": "reflection"
        }
        
        # Map phases
        phase_map = {
            "ideation": "ideation",
            "visualization": "visualization", 
            "materialization": "materialization",
            "pre_test": "ideation",
            "post_test": "materialization"
        }
        
        # Map modalities
        modality_map = {
            "text": "text",
            "sketch": "sketch",
            "image": "sketch",
            "voice": "verbal",
            "upload": "sketch",
            "diagram": "sketch"
        }
        
        move_dict = {
            "id": str(uuid.uuid4()),
            "session_id": self.session_id,
            "timestamp": datetime.now().timestamp(),
            "sequence_number": len(self.moves) + 1,
            "content": content,
            "move_type": move_type_map.get(move_type, "analysis"),
            "phase": phase_map.get(phase, "ideation"),
            "modality": modality_map.get(modality, "text"),
            "cognitive_operation": move_type,
            "design_focus": design_focus,
            "move_source": move_source,
            "cognitive_load": 0.5,  # Default cognitive load
            "metadata": {
                "original_move_type": move_type,
                "original_phase": phase,
                "original_modality": modality,
                "timestamp_iso": datetime.now().isoformat()
            }
        }
        
        return move_dict

    def log_design_move_from_dict(self, move_dict: Dict[str, Any]):
        """Log a design move from dictionary data"""
        # Convert to LinkographyMove object
        if self.benchmarking_available:
            linkography_move = LinkographyMove(
                id=move_dict["id"],
                timestamp=move_dict["timestamp"],
                session_id=move_dict["session_id"],
                user_id='participant',
                phase=move_dict["phase"],
                content=move_dict["content"],
                move_type=move_dict["move_type"],
                modality=move_dict["modality"],
                cognitive_load=move_dict["cognitive_load"],
                metadata=move_dict["metadata"]
            )
        else:
            # Fallback: create simple object
            linkography_move = LinkographyMove(**move_dict)

        # Add to moves list
        self.moves.append(linkography_move)

        # Log to JSONL file
        with open(self.moves_log, 'a') as f:
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
            if self.benchmarking_available:
                self.current_linkograph = self.linkography_engine.update_linkograph_realtime(
                    self.current_linkograph,
                    linkography_move
                )
            else:
                # Simple fallback: just add to moves
                self.current_linkograph.moves.append(linkography_move)

        # Save current state
        self._save_current_linkograph()

    def log_interaction_as_moves(self, user_input: str, ai_response: str,
                               phase: str = "ideation", modality: str = "text"):
        """Log an interaction as design moves (user input + AI response)"""

        # Log user input as a move
        user_move = self.create_design_move_from_interaction(
            content=user_input,
            move_type="question",
            move_source="user_generated",
            phase=phase,
            modality=modality
        )
        self.log_design_move_from_dict(user_move)

        # Log AI response as a move
        ai_move = self.create_design_move_from_interaction(
            content=ai_response,
            move_type="response",
            move_source="ai_provided",
            phase=phase,
            modality="text"
        )
        self.log_design_move_from_dict(ai_move)

    def _save_current_linkograph(self):
        """Save current linkograph state"""
        if self.current_linkograph:
            # Convert linkograph to dictionary format
            if self.benchmarking_available and hasattr(self.current_linkograph, 'moves'):
                moves_data = [
                    {
                        'id': getattr(m, 'id', str(uuid.uuid4())),
                        'timestamp': getattr(m, 'timestamp', datetime.now().timestamp()),
                        'content': getattr(m, 'content', ''),
                        'move_type': getattr(m, 'move_type', 'analysis'),
                        'phase': getattr(m, 'phase', 'ideation'),
                        'modality': getattr(m, 'modality', 'text')
                    } for m in self.current_linkograph.moves
                ]

                links_data = []
                if hasattr(self.current_linkograph, 'links'):
                    links_data = [
                        {
                            'id': getattr(l, 'id', str(uuid.uuid4())),
                            'source_move': getattr(l, 'source_move', ''),
                            'target_move': getattr(l, 'target_move', ''),
                            'strength': getattr(l, 'strength', 0.5),
                            'link_type': getattr(l, 'link_type', 'temporal')
                        } for l in self.current_linkograph.links
                    ]
            else:
                # Fallback: use simple move data
                moves_data = [
                    {
                        'id': getattr(m, 'id', str(uuid.uuid4())),
                        'timestamp': getattr(m, 'timestamp', datetime.now().timestamp()),
                        'content': getattr(m, 'content', ''),
                        'move_type': getattr(m, 'move_type', 'analysis'),
                        'phase': getattr(m, 'phase', 'ideation'),
                        'modality': getattr(m, 'modality', 'text')
                    } for m in self.moves
                ]
                links_data = []

            linkograph_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'linkograph': {
                    'id': getattr(self.current_linkograph, 'id', str(uuid.uuid4())),
                    'session_id': self.session_id,
                    'phase': 'mixed',
                    'generated_at': datetime.now().isoformat(),
                    'move_count': len(moves_data),
                    'link_count': len(links_data),
                    'moves': moves_data,
                    'links': links_data
                },
                'metrics': self._get_metrics_dict(),
                'move_count': len(self.moves),
                'link_count': len(links_data)
            }

            with open(self.linkography_file, 'w') as f:
                json.dump(linkograph_data, f, indent=2)

    def _get_metrics_dict(self) -> Dict[str, float]:
        """Get metrics dictionary"""
        if self.benchmarking_available and self.current_linkograph and hasattr(self.current_linkograph, 'metrics') and self.current_linkograph.metrics:
            return {
                'link_density': getattr(self.current_linkograph.metrics, 'link_density', 0.0),
                'critical_move_ratio': getattr(self.current_linkograph.metrics, 'critical_move_ratio', 0.0),
                'entropy': getattr(self.current_linkograph.metrics, 'entropy', 0.0),
                'orphan_move_ratio': getattr(self.current_linkograph.metrics, 'orphan_move_ratio', 0.0),
                'avg_link_strength': getattr(self.current_linkograph.metrics, 'avg_link_strength', 0.0),
                'chunk_count': getattr(self.current_linkograph.metrics, 'chunk_count', 0),
                'web_count': getattr(self.current_linkograph.metrics, 'web_count', 0),
                'sawtooth_count': getattr(self.current_linkograph.metrics, 'sawtooth_count', 0)
            }
        else:
            # Fallback metrics
            return {
                'total_moves': len(self.moves),
                'total_links': 0,
                'link_density': 0.0,
                'move_diversity': len(set(getattr(m, 'move_type', 'analysis') for m in self.moves)) / max(len(self.moves), 1),
                'critical_move_ratio': 0.0,
                'entropy': 0.0,
                'orphan_move_ratio': 0.0,
                'avg_link_strength': 0.0,
                'chunk_count': 0,
                'web_count': 0,
                'sawtooth_count': 0
            }

    def get_linkography_metrics(self) -> Dict[str, float]:
        """Get current linkography metrics"""
        return self._get_metrics_dict()

    def get_cognitive_indicators(self) -> Dict[str, float]:
        """Get cognitive indicators from linkography"""
        if self.benchmarking_available and self.current_linkograph and hasattr(self.current_linkograph, 'metrics') and self.current_linkograph.metrics:
            return getattr(self.current_linkograph.metrics, 'cognitive_indicators', {})

        # Fallback cognitive indicators
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
            mt = getattr(move, 'move_type', 'analysis')
            move_type_counts[mt] = move_type_counts.get(mt, 0) + 1

        total_moves = len(self.moves)

        return {
            'deep_thinking': move_type_counts.get('evaluation', 0) / total_moves,
            'offloading_prevention': 1.0 - (move_type_counts.get('analysis', 0) / total_moves),
            'knowledge_integration': move_type_counts.get('synthesis', 0) / total_moves,
            'learning_progression': min(total_moves / 50, 1.0),
            'metacognitive_awareness': move_type_counts.get('reflection', 0) / total_moves
        }

    def finalize(self):
        """Finalize linkography logging"""
        if self.current_linkograph and self.benchmarking_available:
            # Regenerate complete linkograph with all moves
            self.current_linkograph = self.linkography_engine.generate_linkograph(
                self.moves,
                self.session_id
            )

        # Save final linkograph with additional analysis
        final_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'linkograph': self._get_linkograph_dict(),
            'metrics': self._get_metrics_dict(),
            'move_count': len(self.moves),
            'link_count': len(getattr(self.current_linkograph, 'links', [])) if self.current_linkograph else 0,
            'patterns': self._extract_patterns(),
            'phase_distribution': self._calculate_phase_distribution(),
            'benchmarking_available': self.benchmarking_available
        }

        with open(self.linkography_file, 'w') as f:
            json.dump(final_data, f, indent=2)

    def _get_linkograph_dict(self) -> Dict[str, Any]:
        """Get linkograph as dictionary"""
        if self.current_linkograph:
            moves_data = []
            for m in getattr(self.current_linkograph, 'moves', self.moves):
                moves_data.append({
                    'id': getattr(m, 'id', str(uuid.uuid4())),
                    'timestamp': getattr(m, 'timestamp', datetime.now().timestamp()),
                    'content': getattr(m, 'content', ''),
                    'move_type': getattr(m, 'move_type', 'analysis'),
                    'phase': getattr(m, 'phase', 'ideation'),
                    'modality': getattr(m, 'modality', 'text')
                })

            links_data = []
            if hasattr(self.current_linkograph, 'links'):
                for l in self.current_linkograph.links:
                    links_data.append({
                        'id': getattr(l, 'id', str(uuid.uuid4())),
                        'source_move': getattr(l, 'source_move', ''),
                        'target_move': getattr(l, 'target_move', ''),
                        'strength': getattr(l, 'strength', 0.5),
                        'link_type': getattr(l, 'link_type', 'temporal')
                    })

            return {
                'id': getattr(self.current_linkograph, 'id', str(uuid.uuid4())),
                'session_id': self.session_id,
                'phase': 'mixed',
                'generated_at': datetime.now().isoformat(),
                'move_count': len(moves_data),
                'link_count': len(links_data),
                'moves': moves_data,
                'links': links_data
            }
        return {}

    def _extract_patterns(self) -> Dict[str, Any]:
        """Extract linkographic patterns"""
        if self.benchmarking_available and self.current_linkograph and hasattr(self.current_linkograph, 'metrics') and self.current_linkograph.metrics:
            return {
                'chunks': getattr(self.current_linkograph.metrics, 'chunk_count', 0),
                'webs': getattr(self.current_linkograph.metrics, 'web_count', 0),
                'sawteeth': getattr(self.current_linkograph.metrics, 'sawtooth_count', 0)
            }
        return {'chunks': 0, 'webs': 0, 'sawteeth': 0}

    def _calculate_phase_distribution(self) -> Dict[str, float]:
        """Calculate distribution of moves across phases"""
        phase_counts = {'ideation': 0, 'visualization': 0, 'materialization': 0}

        for move in self.moves:
            phase = getattr(move, 'phase', 'ideation')
            if phase in phase_counts:
                phase_counts[phase] += 1

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
        for i, move in enumerate(self.moves):
            nodes.append({
                'id': getattr(move, 'id', str(uuid.uuid4())),
                'label': f"M{i+1}",
                'title': getattr(move, 'content', '')[:100] + "..." if len(getattr(move, 'content', '')) > 100 else getattr(move, 'content', ''),
                'group': getattr(move, 'phase', 'ideation'),
                'value': 1  # Default value
            })

        edges = []
        if hasattr(self.current_linkograph, 'links'):
            for link in self.current_linkograph.links:
                edges.append({
                    'from': getattr(link, 'source_move', ''),
                    'to': getattr(link, 'target_move', ''),
                    'value': getattr(link, 'strength', 0.5),
                    'title': f"Strength: {getattr(link, 'strength', 0.5):.2f}",
                    'arrows': 'to'
                })

        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': self.get_linkography_metrics()
        }
