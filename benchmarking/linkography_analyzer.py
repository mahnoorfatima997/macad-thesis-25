"""
MEGA Architectural Mentor - Linkography Session Analyzer
Analyzes interaction sessions to generate linkographs and cognitive mappings
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from linkography_types import (
    DesignMove, Linkograph, LinkographSession, DesignPhase,
    MoveType, Modality, LinkographPattern
)
from linkography_engine import LinkographyEngine
from linkography_cognitive_mapping import CognitiveMappingService


class LinkographySessionAnalyzer:
    """
    Analyzes interaction sessions to extract design moves and generate linkographs.
    Integrates with the existing benchmarking data structure.
    """
    
    def __init__(self):
        self.engine = LinkographyEngine()
        self.cognitive_mapper = CognitiveMappingService()
        self.results_path = Path("benchmarking/results")
        
    def analyze_session(self, session_data: Dict) -> LinkographSession:
        """
        Analyze a complete session and generate linkography data.
        
        Args:
            session_data: Session data from evaluation reports
            
        Returns:
            LinkographSession with complete analysis
        """
        session_id = session_data['session_metrics']['session_id']
        user_id = session_data['session_metrics'].get('user_id', 'unknown')
        
        # Extract design moves from interactions
        design_moves = self._extract_design_moves(session_data)
        
        if not design_moves:
            # Return empty session if no moves found
            return self._create_empty_session(session_id, user_id)
        
        # Group moves by phase
        phase_moves = self._group_moves_by_phase(design_moves)
        
        # Generate linkographs for each phase
        linkographs = []
        for phase, moves in phase_moves.items():
            if moves:
                linkograph = self.engine.generate_linkograph(moves, session_id)
                linkographs.append(linkograph)
        
        # Generate overall linkograph
        overall_linkograph = self.engine.generate_linkograph(design_moves, session_id)
        
        # Map to cognitive metrics
        cognitive_mapping = self.cognitive_mapper.map_linkography_to_cognitive(overall_linkograph)
        
        # Detect patterns
        patterns = self._detect_all_patterns(overall_linkograph)
        
        # Create session object
        session = LinkographSession(
            session_id=session_id,
            user_id=user_id,
            start_time=session_data['session_metrics']['timestamp'],
            end_time=session_data['session_metrics']['timestamp'] + 
                     session_data['session_metrics']['duration_minutes'] * 60,
            linkographs=linkographs,
            overall_metrics=overall_linkograph.metrics,
            cognitive_mapping=cognitive_mapping,
            patterns_detected=patterns
        )
        
        return session
    
    def _extract_design_moves(self, session_data: Dict) -> List[DesignMove]:
        """Extract design moves from session interactions"""
        moves = []
        
        # Get interactions from session data
        interactions = session_data.get('interaction_analysis', {}).get('interactions', [])
        
        for idx, interaction in enumerate(interactions):
            # Determine phase based on interaction context
            phase = self._determine_phase(interaction, idx, len(interactions))
            
            # Determine move type based on interaction
            move_type = self._determine_move_type(interaction)
            
            # Create design move
            move = DesignMove(
                id=str(uuid.uuid4()),
                timestamp=interaction.get('timestamp', idx),
                session_id=session_data['session_metrics']['session_id'],
                user_id=session_data['session_metrics'].get('user_id', 'unknown'),
                phase=phase,
                content=interaction.get('user_message', '') + ' ' + interaction.get('ai_response', ''),
                move_type=move_type,
                modality='text',  # Default to text for now
                cognitive_load=interaction.get('cognitive_load', 0.5),
                metadata={
                    'interaction_type': interaction.get('interaction_type', 'unknown'),
                    'agent': interaction.get('agent', 'unknown'),
                    'cognitive_metrics': interaction.get('cognitive_metrics', {})
                }
            )
            
            moves.append(move)
        
        return moves
    
    def _determine_phase(self, interaction: Dict, idx: int, total: int) -> DesignPhase:
        """Determine design phase based on interaction content and position"""
        # Simple heuristic: divide session into three parts
        position_ratio = idx / max(total - 1, 1)
        
        # Check for phase keywords in content
        content = (interaction.get('user_message', '') + ' ' + 
                  interaction.get('ai_response', '')).lower()
        
        if any(word in content for word in ['idea', 'concept', 'explore', 'brainstorm']):
            return 'ideation'
        elif any(word in content for word in ['sketch', 'draw', 'visualize', 'represent']):
            return 'visualization'
        elif any(word in content for word in ['build', 'construct', 'material', 'detail']):
            return 'materialization'
        
        # Default based on position
        if position_ratio < 0.33:
            return 'ideation'
        elif position_ratio < 0.67:
            return 'visualization'
        else:
            return 'materialization'
    
    def _determine_move_type(self, interaction: Dict) -> MoveType:
        """Determine cognitive move type from interaction"""
        content = (interaction.get('user_message', '') + ' ' + 
                  interaction.get('ai_response', '')).lower()
        
        # Simple keyword-based classification
        if any(word in content for word in ['analyze', 'examine', 'study', 'investigate']):
            return 'analysis'
        elif any(word in content for word in ['combine', 'integrate', 'merge', 'synthesize']):
            return 'synthesis'
        elif any(word in content for word in ['evaluate', 'assess', 'judge', 'critique']):
            return 'evaluation'
        elif any(word in content for word in ['transform', 'change', 'modify', 'adapt']):
            return 'transformation'
        elif any(word in content for word in ['reflect', 'think', 'consider', 'ponder']):
            return 'reflection'
        
        # Default to analysis
        return 'analysis'
    
    def _group_moves_by_phase(self, moves: List[DesignMove]) -> Dict[DesignPhase, List[DesignMove]]:
        """Group design moves by phase"""
        phase_groups = {
            'ideation': [],
            'visualization': [],
            'materialization': []
        }
        
        for move in moves:
            if move.phase in phase_groups:
                phase_groups[move.phase].append(move)
        
        return phase_groups
    
    def _detect_all_patterns(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Detect all patterns in the linkograph"""
        patterns = []
        
        # Use engine's pattern detection
        engine_patterns = self.engine._detect_patterns(linkograph)
        patterns.extend(engine_patterns)
        
        # Add custom pattern detection for educational context
        educational_patterns = self._detect_educational_patterns(linkograph)
        patterns.extend(educational_patterns)
        
        return patterns
    
    def _detect_educational_patterns(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Detect patterns specific to educational context"""
        patterns = []
        
        # Detect struggle patterns (many orphan moves in sequence)
        orphan_sequences = self._find_orphan_sequences(linkograph)
        for seq in orphan_sequences:
            pattern = LinkographPattern(
                pattern_type='struggle',
                moves=seq,
                strength=len(seq) / len(linkograph.moves),
                description=f"Student struggling with concept (sequence of {len(seq)} unconnected moves)",
                cognitive_implications={
                    'cognitive_offloading': -0.8,
                    'deep_thinking': -0.6,
                    'scaffolding_needed': 0.9
                }
            )
            patterns.append(pattern)
        
        # Detect breakthrough patterns (sudden increase in connectivity)
        breakthroughs = self._find_breakthrough_moments(linkograph)
        for breakthrough in breakthroughs:
            pattern = LinkographPattern(
                pattern_type='breakthrough',
                moves=breakthrough,
                strength=0.8,
                description="Conceptual breakthrough moment",
                cognitive_implications={
                    'deep_thinking': 0.9,
                    'knowledge_integration': 0.8,
                    'learning_progression': 0.9
                }
            )
            patterns.append(pattern)
        
        return patterns
    
    def _find_orphan_sequences(self, linkograph: Linkograph) -> List[List[str]]:
        """Find sequences of orphan moves indicating struggle"""
        orphan_sequences = []
        current_sequence = []
        
        for move in linkograph.moves:
            source_links, target_links = linkograph.get_links_for_move(move.id)
            is_orphan = len(source_links) + len(target_links) == 0
            
            if is_orphan:
                current_sequence.append(move.id)
            else:
                if len(current_sequence) >= 3:  # Sequence of 3+ orphans
                    orphan_sequences.append(current_sequence)
                current_sequence = []
        
        if len(current_sequence) >= 3:
            orphan_sequences.append(current_sequence)
        
        return orphan_sequences
    
    def _find_breakthrough_moments(self, linkograph: Linkograph) -> List[List[str]]:
        """Find moments of sudden increased connectivity"""
        breakthroughs = []
        moves = linkograph.moves
        
        for i in range(2, len(moves) - 2):
            # Compare connectivity before and after
            before_moves = moves[max(0, i-3):i]
            current_move = moves[i]
            after_moves = moves[i:min(len(moves), i+3)]
            
            before_connectivity = sum(
                len(linkograph.get_links_for_move(m.id)[0]) + 
                len(linkograph.get_links_for_move(m.id)[1])
                for m in before_moves
            ) / len(before_moves)
            
            current_connectivity = (
                len(linkograph.get_links_for_move(current_move.id)[0]) +
                len(linkograph.get_links_for_move(current_move.id)[1])
            )
            
            # Breakthrough if current connectivity is much higher
            if current_connectivity > before_connectivity * 2 and current_connectivity >= 4:
                breakthrough_moves = [m.id for m in before_moves + [current_move] + after_moves[:1]]
                breakthroughs.append(breakthrough_moves)
        
        return breakthroughs
    
    def _create_empty_session(self, session_id: str, user_id: str) -> LinkographSession:
        """Create an empty session when no moves are found"""
        empty_linkograph = Linkograph(
            id=str(uuid.uuid4()),
            session_id=session_id,
            moves=[],
            links=[],
            metrics=self.engine.calculate_metrics(Linkograph(
                id='temp', session_id=session_id, moves=[], links=[],
                metrics=None, phase='ideation', generated_at=0
            )),
            phase='ideation',
            generated_at=datetime.now().timestamp()
        )
        
        return LinkographSession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp(),
            linkographs=[empty_linkograph],
            overall_metrics=empty_linkograph.metrics,
            cognitive_mapping=self.cognitive_mapper.map_linkography_to_cognitive(empty_linkograph),
            patterns_detected=[]
        )
    
    def analyze_all_sessions(self) -> Dict[str, LinkographSession]:
        """Analyze all available sessions in the benchmarking results"""
        sessions = {}
        
        # Load evaluation reports
        eval_dir = self.results_path / "evaluation_reports"
        if not eval_dir.exists():
            return sessions
        
        for eval_file in eval_dir.glob("*.json"):
            with open(eval_file, 'r') as f:
                session_data = json.load(f)
            
            # Analyze session
            linkograph_session = self.analyze_session(session_data)
            sessions[linkograph_session.session_id] = linkograph_session
        
        return sessions
    
    def save_linkography_results(self, sessions: Dict[str, LinkographSession]):
        """Save linkography analysis results"""
        output_dir = self.results_path / "linkography_analysis"
        output_dir.mkdir(exist_ok=True)
        
        for session_id, session in sessions.items():
            # Save session data
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'duration_minutes': session.get_duration_minutes(),
                'total_moves': sum(len(lg.moves) for lg in session.linkographs),
                'total_links': sum(len(lg.links) for lg in session.linkographs),
                'overall_metrics': {
                    'link_density': session.overall_metrics.link_density,
                    'critical_move_ratio': session.overall_metrics.critical_move_ratio,
                    'entropy': session.overall_metrics.entropy,
                    'phase_balance': session.overall_metrics.phase_balance
                },
                'cognitive_mapping': session.cognitive_mapping.to_dict(),
                'patterns': [
                    {
                        'type': p.pattern_type,
                        'strength': p.strength,
                        'description': p.description
                    }
                    for p in session.patterns_detected
                ]
            }
            
            output_file = output_dir / f"linkography_{session_id}.json"
            with open(output_file, 'w') as f:
                json.dump(session_data, f, indent=2)