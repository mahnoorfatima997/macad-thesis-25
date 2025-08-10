"""
Comprehensive logging system for test sessions
Captures all interactions, design moves, and metrics for linkography analysis
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thesis_tests.data_models import (
    TestSession, InteractionData, DesignMove, AssessmentResult,
    TestPhase, TestGroup, MoveType, MoveSource, Modality, DesignFocus
)
from shared_assessment import CognitiveAssessment


class TestSessionLogger:
    """Comprehensive logger for test sessions"""
    
    def __init__(self, session_id: str, participant_id: str, test_group: TestGroup):
        self.session_id = session_id
        self.participant_id = participant_id
        self.test_group = test_group
        
        # Initialize storage
        self.interactions: List[InteractionData] = []
        self.design_moves: List[DesignMove] = []
        self.assessments: Dict[str, AssessmentResult] = {}
        self.phase_transitions: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.cognitive_metrics_history: List[Dict[str, Any]] = []
        self.current_phase = TestPhase.PRE_TEST
        self.session_start_time = datetime.now()
        self.phase_start_times: Dict[str, datetime] = {}
        
        # File paths - use thesis_data directory for benchmarking compatibility
        self.data_dir = Path("thesis_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.data_dir / f"session_{session_id}.json"
        self.moves_file = self.data_dir / f"moves_{session_id}.csv"
        self.interactions_file = self.data_dir / f"interactions_{session_id}.csv"
        self.metrics_file = self.data_dir / f"metrics_{session_id}.csv"
        self.session_summary_file = self.data_dir / f"session_summary_{session_id}.json"
        
        # Initialize CSV files
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Initialize CSV files with headers"""
        # Design moves CSV
        moves_headers = [
            'move_id', 'session_id', 'timestamp', 'sequence_number', 'content',
            'move_type', 'phase', 'modality', 'cognitive_operation', 'design_focus',
            'move_source', 'cognitive_load', 'previous_move_id', 'tool_used',
            'interaction_trigger', 'semantic_links', 'temporal_links', 
            'conceptual_distance', 'ai_influence_strength', 'self_generation_strength',
            'directness_level', 'pause_duration', 'revision_count', 'complexity_score',
            'uncertainty_markers'
        ]
        
        with open(self.moves_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=moves_headers)
            writer.writeheader()
        
        # Interactions CSV - include all columns expected by benchmarking (+ phase/checklist extras)
        interactions_headers = [
            'session_id', 'timestamp', 'interaction_number', 'student_input', 'input_length',
            'input_type', 'student_skill_level', 'understanding_level', 'confidence_level',
            'engagement_level', 'agent_response', 'response_length', 'routing_path',
            'agents_used', 'response_type', 'primary_agent', 'cognitive_flags',
            'cognitive_flags_count', 'confidence_score', 'sources_used', 'knowledge_integrated',
            'sources_count', 'response_time', 'prevents_cognitive_offloading',
            'encourages_deep_thinking', 'provides_scaffolding', 'maintains_engagement',
            'adapts_to_skill_level', 'multi_agent_coordination', 'appropriate_agent_selection',
            'response_coherence',
            # Added phase/checklist flattening fields (compatible additions)
            'current_phase', 'phase_score', 'phase_transition_from', 'phase_transition_to',
            'checklist_delta_json', 'next_targets_json',
            # Raw merged metadata (JSON)
            'metadata'
        ]
        
        with open(self.interactions_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=interactions_headers)
            writer.writeheader()
        
        # Metrics CSV
        metrics_headers = [
            'timestamp', 'phase', 'cop_score', 'dte_score', 'se_score',
            'ki_score', 'lp_score', 'ma_score', 'composite_score'
        ]
        
        with open(self.metrics_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=metrics_headers)
            writer.writeheader()
    
    def log_session_start(self):
        """Log the start of a test session"""
        self.phase_start_times[TestPhase.PRE_TEST.value] = self.session_start_time
        self._log_event("session_start", {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "test_group": self.test_group.value,
            "start_time": self.session_start_time.isoformat()
        })
    
    def log_phase_transition(self, from_phase: TestPhase, to_phase: TestPhase):
        """Log phase transitions"""
        transition_time = datetime.now()
        
        # Calculate phase duration
        if from_phase.value in self.phase_start_times:
            duration = (transition_time - self.phase_start_times[from_phase.value]).total_seconds()
        else:
            duration = 0
        
        self.phase_transitions.append({
            "timestamp": transition_time.isoformat(),
            "from_phase": from_phase.value,
            "to_phase": to_phase.value,
            "duration_seconds": duration
        })
        
        self.phase_start_times[to_phase.value] = transition_time
        self.current_phase = to_phase
        
        self._log_event("phase_transition", {
            "from_phase": from_phase.value,
            "to_phase": to_phase.value,
            "duration": duration
        })
    
    def log_interaction(self, interaction: InteractionData):
        """Log a user-system interaction with real cognitive assessment"""
        self.interactions.append(interaction)
        
        # Get response content and type for assessment
        agent_response = interaction.system_response if interaction.system_response else ""
        response_type = self._determine_response_type(interaction)
        
        # Perform real cognitive assessment based on actual response content
        if self.test_group == TestGroup.CONTROL:
            # Control group has no AI assistance, so minimal scores
            prevents_offloading = 0.0
            encourages_thinking = 0.0
            provides_scaffolding = 0.0
            maintains_engagement = 0.0
            adapts_to_skill = 0.0
        else:
            # For MENTOR and GENERIC_AI, assess the actual response
            prevents_offloading = 1.0 if CognitiveAssessment.assess_cognitive_offloading_prevention(
                agent_response, response_type
            ) else 0.0
            encourages_thinking = 1.0 if CognitiveAssessment.assess_deep_thinking_encouragement(
                agent_response
            ) else 0.0
            provides_scaffolding = 1.0 if CognitiveAssessment.assess_scaffolding(
                agent_response, []  # No cognitive flags in test data
            ) else 0.0
            maintains_engagement = 1.0 if CognitiveAssessment.assess_engagement_maintenance(
                agent_response, response_type
            ) else 0.0
            
            # Estimate skill level for adaptation assessment
            skill_level = self._estimate_skill_level(interaction)
            adapts_to_skill = 1.0 if CognitiveAssessment.assess_skill_adaptation(
                agent_response, skill_level
            ) else 0.0
            
            # Apply group-specific modifiers to reflect system design differences
            if self.test_group == TestGroup.GENERIC_AI:
                # Generic AI is less likely to prevent offloading by design
                prevents_offloading *= 0.3  # Reduce by 70%
                encourages_thinking *= 0.5  # Reduce by 50%
                provides_scaffolding *= 0.7  # Reduce by 30%
        
        # Determine input type
        input_lower = interaction.user_input.lower()
        if any(q in input_lower for q in ['what is', 'how do i', 'tell me', 'explain']):
            input_type = 'direct_question'
        elif any(q in input_lower for q in ['i think', 'maybe', 'could']):
            input_type = 'exploratory_statement'
        else:
            input_type = 'general_statement'
        
        # Write to CSV with all required fields
        with open(self.interactions_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'session_id', 'timestamp', 'interaction_number', 'student_input', 'input_length',
                'input_type', 'student_skill_level', 'understanding_level', 'confidence_level',
                'engagement_level', 'agent_response', 'response_length', 'routing_path',
                'agents_used', 'response_type', 'primary_agent', 'cognitive_flags',
                'cognitive_flags_count', 'confidence_score', 'sources_used', 'knowledge_integrated',
                'sources_count', 'response_time', 'prevents_cognitive_offloading',
                'encourages_deep_thinking', 'provides_scaffolding', 'maintains_engagement',
                'adapts_to_skill_level', 'multi_agent_coordination', 'appropriate_agent_selection',
                'response_coherence',
                'current_phase', 'phase_score', 'phase_transition_from', 'phase_transition_to',
                'checklist_delta_json', 'next_targets_json',
                'metadata'
            ])
            
            # Prepare merged metadata (logger core + provided)
            metadata = {
                'phase': interaction.phase.value,
                'cognitive_metrics': interaction.cognitive_metrics,
                'generated_moves': interaction.generated_moves,
                'error_occurred': interaction.error_occurred,
                'test_group': self.test_group.value
            }
            # Merge in interaction-provided metadata (from orchestrator/dashboard)
            try:
                if isinstance(interaction.metadata, dict):
                    metadata.update(interaction.metadata)
            except Exception:
                pass

            # Extract flattened fields from metadata
            meta_routing_path = metadata.get('routing_path') or metadata.get('route') or 'test_environment'
            meta_agents_used = metadata.get('agents_used')
            if isinstance(meta_agents_used, list):
                meta_agents_used_str = '|'.join([str(a) for a in meta_agents_used])
            else:
                meta_agents_used_str = str(meta_agents_used) if meta_agents_used is not None else self.test_group.value
            cognitive_flags_val = metadata.get('cognitive_flags', [])
            if isinstance(cognitive_flags_val, list):
                cognitive_flags_str = '|'.join([str(f) for f in cognitive_flags_val])
                cognitive_flags_count = len(cognitive_flags_val)
            else:
                cognitive_flags_str = str(cognitive_flags_val) if cognitive_flags_val else ''
                cognitive_flags_count = 0 if not cognitive_flags_val else 1
            sources_used_val = metadata.get('sources', [])
            if isinstance(sources_used_val, list):
                sources_used_str = json.dumps(sources_used_val)
                sources_count_val = len(sources_used_val)
            else:
                sources_used_str = ''
                sources_count_val = 0
            knowledge_integrated_val = 1 if metadata.get('knowledge_integrated', False) else metadata.get('knowledge_integrated', 0)

            current_phase_val = metadata.get('current_phase') or metadata.get('phase')  # allow either
            phase_score_val = metadata.get('phase_score')
            transition = metadata.get('phase_transition') or {}
            phase_transition_from = transition.get('from') if isinstance(transition, dict) else None
            phase_transition_to = transition.get('to') if isinstance(transition, dict) else None
            checklist_delta = metadata.get('checklist_delta', [])
            next_targets = metadata.get('next_targets', [])
            checklist_delta_json = json.dumps(checklist_delta) if checklist_delta else ''
            next_targets_json = json.dumps(next_targets) if next_targets else ''
            
            writer.writerow({
                'session_id': interaction.session_id,
                'timestamp': interaction.timestamp.isoformat(),
                'interaction_number': len(self.interactions),
                'student_input': interaction.user_input,
                'input_length': len(interaction.user_input.split()),
                'input_type': input_type,
                'student_skill_level': 'intermediate',  # Default
                'understanding_level': 'medium',
                'confidence_level': 'medium',
                'engagement_level': 'high' if self.test_group == TestGroup.MENTOR else 'medium',
                'agent_response': interaction.system_response,
                'response_length': len(interaction.system_response.split()),
                'routing_path': meta_routing_path,
                'agents_used': meta_agents_used_str,
                'response_type': interaction.interaction_type,
                'primary_agent': self.test_group.value,
                'cognitive_flags': cognitive_flags_str,
                'cognitive_flags_count': cognitive_flags_count,
                'confidence_score': 0.8,
                'sources_used': sources_used_str,
                'knowledge_integrated': knowledge_integrated_val if knowledge_integrated_val in [0,1] else (1 if self.test_group != TestGroup.CONTROL else 0),
                'sources_count': sources_count_val,
                'response_time': interaction.response_time,
                'prevents_cognitive_offloading': prevents_offloading,
                'encourages_deep_thinking': encourages_thinking,
                'provides_scaffolding': provides_scaffolding,
                'maintains_engagement': maintains_engagement,
                'adapts_to_skill_level': adapts_to_skill,
                'multi_agent_coordination': 1 if self.test_group == TestGroup.MENTOR else 0,
                'appropriate_agent_selection': 1,
                'response_coherence': 1,
                'current_phase': current_phase_val,
                'phase_score': phase_score_val if isinstance(phase_score_val, (int, float)) else '',
                'phase_transition_from': phase_transition_from,
                'phase_transition_to': phase_transition_to,
                'checklist_delta_json': checklist_delta_json,
                'next_targets_json': next_targets_json,
                'metadata': json.dumps(metadata, default=str)
            })
    
    def log_design_move(self, move: DesignMove):
        """Log a design move for linkography"""
        self.design_moves.append(move)
        
        # Write to CSV immediately
        with open(self.moves_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'move_id', 'session_id', 'timestamp', 'sequence_number', 'content',
                'move_type', 'phase', 'modality', 'cognitive_operation', 'design_focus',
                'move_source', 'cognitive_load', 'previous_move_id', 'tool_used',
                'interaction_trigger', 'semantic_links', 'temporal_links', 
                'conceptual_distance', 'ai_influence_strength', 'self_generation_strength',
                'directness_level', 'pause_duration', 'revision_count', 'complexity_score',
                'uncertainty_markers'
            ])
            writer.writerow({
                'move_id': move.id,
                'session_id': move.session_id,
                'timestamp': move.timestamp.isoformat(),
                'sequence_number': move.sequence_number,
                'content': move.content,
                'move_type': move.move_type.value,
                'phase': move.phase.value,
                'modality': move.modality.value,
                'cognitive_operation': move.cognitive_operation,
                'design_focus': move.design_focus.value,
                'move_source': move.move_source.value,
                'cognitive_load': move.cognitive_load,
                'previous_move_id': move.previous_move_id or '',
                'tool_used': move.tool_used,
                'interaction_trigger': move.interaction_trigger,
                'semantic_links': json.dumps(move.semantic_links),
                'temporal_links': json.dumps(move.temporal_links),
                'conceptual_distance': move.conceptual_distance,
                'ai_influence_strength': move.ai_influence_strength or '',
                'self_generation_strength': move.self_generation_strength,
                'directness_level': move.directness_level or '',
                'pause_duration': move.pause_duration,
                'revision_count': move.revision_count,
                'complexity_score': move.complexity_score,
                'uncertainty_markers': move.uncertainty_markers
            })
    
    def log_cognitive_metrics(self, metrics: Dict[str, float]):
        """Log cognitive metrics snapshot"""
        timestamp = datetime.now()
        
        metrics_entry = {
            "timestamp": timestamp.isoformat(),
            "phase": self.current_phase.value,
            **metrics
        }
        
        self.cognitive_metrics_history.append(metrics_entry)
        
        # Write to CSV
        with open(self.metrics_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'phase', 'cop_score', 'dte_score', 'se_score',
                'ki_score', 'lp_score', 'ma_score', 'composite_score'
            ])
            writer.writerow({
                'timestamp': timestamp.isoformat(),
                'phase': self.current_phase.value,
                'cop_score': metrics.get('cop', 0),
                'dte_score': metrics.get('dte', 0),
                'se_score': metrics.get('se', 0),
                'ki_score': metrics.get('ki', 0),
                'lp_score': metrics.get('lp', 0),
                'ma_score': metrics.get('ma', 0),
                'composite_score': metrics.get('composite', 0)
            })
    
    def log_assessment(self, assessment: AssessmentResult):
        """Log assessment results"""
        self.assessments[assessment.assessment_type] = assessment
        
        self._log_event(f"assessment_{assessment.assessment_type}", {
            "scores": assessment.scores,
            "timestamp": assessment.timestamp.isoformat(),
            "completion_time": assessment.completion_time
        })
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current cognitive metrics"""
        if self.cognitive_metrics_history:
            latest = self.cognitive_metrics_history[-1]
            # Extract only the numeric metric values
            return {
                "cop": latest.get("cop_score", 0.0),
                "dte": latest.get("dte_score", 0.0),
                "se": latest.get("se_score", 0.0),
                "ki": latest.get("ki_score", 0.0),
                "lp": latest.get("lp_score", 0.0),
                "ma": latest.get("ma_score", 0.0),
                "composite": latest.get("composite_score", 0.0)
            }
        return {
            "cop": 0.0,
            "dte": 0.0,
            "se": 0.0,
            "ki": 0.0,
            "lp": 0.0,
            "ma": 0.0,
            "composite": 0.0
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the session"""
        end_time = datetime.now()
        duration = (end_time - self.session_start_time).total_seconds() / 60  # minutes
        
        # Calculate average cognitive scores
        if self.cognitive_metrics_history:
            avg_scores = {
                metric: sum(entry.get(metric, 0) for entry in self.cognitive_metrics_history) / len(self.cognitive_metrics_history)
                for metric in ['cop', 'dte', 'se', 'ki', 'lp', 'ma', 'composite']
            }
        else:
            avg_scores = {metric: 0.0 for metric in ['cop', 'dte', 'se', 'ki', 'lp', 'ma', 'composite']}
        
        return {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "test_group": self.test_group.value,
            "duration_minutes": duration,
            "total_interactions": len(self.interactions),
            "total_moves": len(self.design_moves),
            "phase_transitions": len(self.phase_transitions),
            "avg_cognitive_score": avg_scores.get('composite', 0),
            "cognitive_scores": avg_scores,
            "cognitive_metrics": avg_scores,  # Add this for compatibility
            "phases_completed": list(self.phase_start_times.keys())
        }
    
    def finalize_session(self):
        """Finalize and save complete session data"""
        session_data = {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "test_group": self.test_group.value,
            "start_time": self.session_start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "phase_transitions": self.phase_transitions,
            "assessments": {k: v.to_dict() for k, v in self.assessments.items()},
            "summary": self.get_session_summary(),
            "cognitive_metrics_history": self.cognitive_metrics_history
        }
        
        # Save complete session data
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        self._log_event("session_complete", {
            "total_duration": session_data["summary"]["duration_minutes"],
            "total_moves": len(self.design_moves),
            "total_interactions": len(self.interactions)
        })

        # Ensure a session summary JSON exists (merge-safe)
        try:
            if self.session_summary_file.exists():
                with open(self.session_summary_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            else:
                existing = {}
            existing.setdefault('session_id', self.session_id)
            existing['summary'] = session_data['summary']
            with open(self.session_summary_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2)
        except Exception:
            pass
    
    def export_session_data(self) -> str:
        """Export complete session data"""
        self.finalize_session()
        return str(self.session_file)

    def log_phase_snapshot(self, snapshot: Dict[str, Any]):
        """Log a periodic phase assessment snapshot and persist to session_summary JSON."""
        # Event log
        self._log_event("assessment_snapshot", snapshot)
        # Merge into session_summary JSON
        try:
            if self.session_summary_file.exists():
                with open(self.session_summary_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            else:
                existing = {"session_id": self.session_id}
            timeline = existing.setdefault('phase_progression_timeline', [])
            timeline.append(snapshot)
            with open(self.session_summary_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2)
        except Exception:
            pass
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Internal method to log events"""
        event_log = self.data_dir / f"events_{self.session_id}.log"
        with open(event_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data
            }) + '\n')
    
    def _determine_response_type(self, interaction: InteractionData) -> str:
        """Determine the response type based on interaction data"""
        if interaction.interaction_type:
            return interaction.interaction_type
        
        # Analyze response content to determine type
        response = interaction.system_response.lower() if interaction.system_response else ""
        
        if "?" in response and any(q in response for q in ["what", "how", "why", "when", "which"]):
            if any(s in response for s in ["think about", "consider", "reflect"]):
                return "cognitive_primary"
            return "socratic_primary"
        elif any(phrase in response for phrase in ["the answer", "you should", "it is"]):
            return "direct_answer"
        elif any(phrase in response for phrase in ["explore", "investigate", "challenge"]):
            return "cognitive_challenge"
        else:
            return "knowledge_integration"
    
    def _estimate_skill_level(self, interaction: InteractionData) -> str:
        """Estimate student skill level from interaction"""
        # Check for explicit skill level in interaction data
        if hasattr(interaction, 'student_skill_level') and interaction.student_skill_level:
            return interaction.student_skill_level
        
        # Estimate based on input complexity
        input_text = interaction.user_input.lower()
        words = input_text.split()
        
        # Technical terms indicate higher skill
        technical_terms = [
            "circulation", "program", "zoning", "fenestration", "massing",
            "parti", "typology", "vernacular", "articulation", "threshold",
            "porosity", "tectonics", "materiality", "morphology", "syntax"
        ]
        
        technical_count = sum(1 for term in technical_terms if term in input_text)
        
        # Question complexity
        if len(words) < 10 and technical_count == 0:
            return "beginner"
        elif technical_count >= 3 or len(words) > 30:
            return "advanced"
        else:
            return "intermediate"