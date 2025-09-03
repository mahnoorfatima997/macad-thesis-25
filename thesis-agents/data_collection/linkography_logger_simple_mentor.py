"""
Simplified Linkography Logger for Mentor.py Application
Adapted from thesis_tests/linkography_logger_simple.py to work without external dependencies
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid


class SimpleMentorLinkographyLogger:
    """Simplified linkography logger for mentor.py application without external dependencies"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        
        # Storage
        self.moves: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        
        # File paths - use thesis_data directory for consistency
        self.data_dir = Path("thesis_data/linkography")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.linkography_file = self.data_dir / f"linkography_{session_id}.json"
        self.moves_log = self.data_dir / f"linkography_moves_{session_id}.jsonl"
        
        # Initialize files
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize linkography files"""
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
            "timestamp": datetime.now().isoformat(),
            "sequence_number": len(self.moves) + 1,
            "content": content,
            "move_type": move_type_map.get(move_type, "analysis"),
            "phase": phase_map.get(phase, "ideation"),
            "modality": modality_map.get(modality, "text"),
            "cognitive_operation": move_type,
            "design_focus": design_focus,
            "move_source": move_source,
            "cognitive_load": "medium",
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
        # Add to moves list
        self.moves.append(move_dict)
        
        # Log to JSONL file
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
            'phase_distribution': self._calculate_phase_distribution(),
            'patterns': {'chunks': 0, 'webs': 0, 'sawteeth': 0},  # Simple fallback
            'benchmarking_available': False
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

    def get_linkograph_for_visualization(self) -> Optional[Dict[str, Any]]:
        """Get linkograph data formatted for visualization"""
        if not self.moves:
            return None

        # Format for visualization tools
        nodes = []
        for i, move in enumerate(self.moves):
            nodes.append({
                'id': move['id'],
                'label': f"M{i+1}",
                'title': move['content'][:100] + "..." if len(move['content']) > 100 else move['content'],
                'group': move['phase'],
                'value': 1
            })

        edges = []
        for link in self.links:
            edges.append({
                'from': link['source_move'],
                'to': link['target_move'],
                'value': link['strength'],
                'title': f"Strength: {link['strength']:.2f}",
                'arrows': 'to'
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': self.get_linkography_metrics()
        }
