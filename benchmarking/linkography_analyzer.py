"""
MEGA Architectural Mentor - Linkography Session Analyzer
Analyzes interaction sessions to generate linkographs and cognitive mappings
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
import numpy as np
from datetime import datetime

from benchmarking.linkography_types import (
    DesignMove, Linkograph, LinkographSession, DesignPhase,
    MoveType, Modality, LinkographPattern, LinkographLink, LinkographMetrics
)
from benchmarking.linkography_engine import LinkographyEngine
from benchmarking.linkography_cognitive_mapping import CognitiveMappingService
import time


class LinkographySessionAnalyzer:
    """
    Analyzes interaction sessions to extract design moves and generate linkographs.
    Integrates with the existing benchmarking data structure.
    """
    
    def __init__(self):
        self.engine = LinkographyEngine()
        self.cognitive_mapper = CognitiveMappingService()
        # Fix path to work from both root and benchmarking directory
        if Path("results").exists():
            self.results_path = Path("results")
        elif Path("benchmarking/results").exists():
            self.results_path = Path("benchmarking/results")
        else:
            self.results_path = Path(__file__).parent / "results"
        
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
            patterns_detected=patterns,
            raw_data=session_data  # Include raw data for concept extraction
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
            patterns_detected=[],
            raw_data={}  # Empty raw data for empty sessions
        )
    
    def analyze_all_sessions(self) -> Dict[str, LinkographSession]:
        """Analyze all available sessions in the benchmarking results"""
        sessions = {}
        
        # First try to load from evaluation reports
        eval_dir = self.results_path / "evaluation_reports"
        if eval_dir.exists():
            for eval_file in eval_dir.glob("*.json"):
                with open(eval_file, 'r') as f:
                    session_data = json.load(f)
                
                # Analyze session
                linkograph_session = self.analyze_session(session_data)
                sessions[linkograph_session.session_id] = linkograph_session
        
        # Also load directly from linkography files if available
        # Fix path to work from both root and benchmarking directory
        if Path("../thesis_data/linkography").exists():
            linkography_dir = Path("../thesis_data/linkography")
        elif Path("thesis_data/linkography").exists():
            linkography_dir = Path("thesis_data/linkography")
        else:
            linkography_dir = Path(__file__).parent.parent / "thesis_data/linkography"
        if linkography_dir.exists():
            for linkography_file in linkography_dir.glob("linkography_*.json"):
                # Skip moves files
                if "moves" in linkography_file.name:
                    continue
                    
                try:
                    with open(linkography_file, 'r') as f:
                        linkograph_data = json.load(f)
                    
                    session_id = linkograph_data.get('session_id', '')
                    
                    # Skip if already loaded from evaluation
                    if session_id in sessions:
                        continue
                    
                    # Create a LinkographSession from the linkography data
                    session = self._create_session_from_linkography(linkograph_data)
                    if session:
                        sessions[session.session_id] = session
                        
                except Exception as e:
                    print(f"Error loading linkography file {linkography_file}: {e}")
        
        return sessions
    
    def _create_session_from_linkography(self, linkograph_data: Dict[str, Any]) -> Optional[LinkographSession]:
        """Create a LinkographSession from linkography JSON data"""
        try:
            session_id = linkograph_data.get('session_id', '')
            
            # Reconstruct linkograph
            linkograph_dict = linkograph_data.get('linkograph', {})
            
            # Create moves
            moves = []
            for move_data in linkograph_dict.get('moves', []):
                move = DesignMove(
                    id=move_data['id'],
                    timestamp=move_data['timestamp'],
                    session_id=session_id,
                    user_id='participant',
                    phase=move_data.get('phase', 'ideation'),
                    content=move_data.get('content', ''),
                    move_type=move_data.get('move_type', 'analysis'),
                    modality=move_data.get('modality', 'text')
                )
                moves.append(move)
            
            # Create links
            links = []
            for link_data in linkograph_dict.get('links', []):
                link = LinkographLink(
                    id=link_data['id'],
                    source_move=link_data['source_move'],
                    target_move=link_data['target_move'],
                    strength=link_data.get('strength', 0.5),
                    confidence=0.8,
                    link_type=link_data.get('link_type', 'forward'),
                    temporal_distance=1,
                    semantic_similarity=link_data.get('strength', 0.5)
                )
                links.append(link)
            
            # Create metrics
            metrics_data = linkograph_data.get('metrics', {})
            metrics = LinkographMetrics(
                link_density=metrics_data.get('link_density', 0.0),
                critical_move_ratio=metrics_data.get('critical_move_ratio', 0.0),
                entropy=metrics_data.get('entropy', 0.0),
                phase_balance=metrics_data.get('phase_balance', {}),
                cognitive_indicators=metrics_data.get('cognitive_indicators', {}),
                avg_link_strength=metrics_data.get('avg_link_strength', 0.0),
                orphan_move_ratio=metrics_data.get('orphan_move_ratio', 0.0)
            )
            
            # Create linkograph
            linkograph = Linkograph(
                id=linkograph_dict.get('id', session_id),
                session_id=session_id,
                moves=moves,
                links=links,
                metrics=metrics,
                phase=linkograph_dict.get('phase', 'ideation'),
                generated_at=linkograph_dict.get('generated_at', time.time())
            )
            
            # Create session
            session = LinkographSession(
                session_id=session_id,
                user_id='participant',
                start_time=linkograph_data.get('timestamp', ''),
                end_time=None,
                linkographs=[linkograph],
                overall_metrics=metrics,
                cognitive_mapping=self.cognitive_mapper.map_linkography_to_cognitive(linkograph),
                patterns_detected=self._extract_patterns_from_linkograph(linkograph),
                raw_data=linkograph_data  # Include original data
            )
            
            return session
            
        except Exception as e:
            print(f"Error creating session from linkography: {e}")
            return None
    
    def _extract_patterns_from_linkograph(self, linkograph: Linkograph) -> List[LinkographPattern]:
        """Extract patterns from a single linkograph"""
        patterns = []
        
        try:
            # Use engine's pattern detection if available
            if hasattr(self.engine, '_detect_patterns'):
                engine_patterns = self.engine._detect_patterns(linkograph)
                patterns.extend(engine_patterns)
            
            # Basic pattern detection based on link structure
            if len(linkograph.links) > 0:
                # Check for high connectivity (web pattern)
                avg_links_per_move = len(linkograph.links) / len(linkograph.moves) if linkograph.moves else 0
                if avg_links_per_move > 2:
                    patterns.append(LinkographPattern(
                        pattern_type='web',
                        moves=[m.id for m in linkograph.moves],
                        strength=min(avg_links_per_move / 3, 1.0),
                        description="High connectivity pattern indicating intensive development",
                        cognitive_implications={'deep_thinking': 0.8, 'integration': 0.9}
                    ))
                
                # Check for sequential patterns
                sequential_links = sum(1 for link in linkograph.links if link.link_type == 'forward')
                if sequential_links / len(linkograph.links) > 0.7:
                    patterns.append(LinkographPattern(
                        pattern_type='sawtooth',
                        moves=[m.id for m in linkograph.moves],
                        strength=0.7,
                        description="Sequential development pattern",
                        cognitive_implications={'systematic_thinking': 0.8}
                    ))
        except Exception as e:
            print(f"Error extracting patterns: {e}")
        
        return patterns
    
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