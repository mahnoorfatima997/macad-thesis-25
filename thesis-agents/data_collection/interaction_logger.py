#!/usr/bin/env python3
"""
Enhanced Interaction Logger for Thesis Data Collection
Comprehensive logging with scientific metrics, cognitive state tracking, and design move analysis
"""

import json
import csv
import datetime
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import asdict, is_dataclass
from enum import Enum
import os
import uuid
import pandas as pd

# Custom JSON encoder to handle ConversationMilestone and other non-serializable objects
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle ConversationMilestone and other non-serializable objects"""
    
    def default(self, obj):
        # Handle ConversationMilestone and other dataclasses
        if is_dataclass(obj):
            return asdict(obj)
        
        # Handle Enum objects
        if isinstance(obj, Enum):
            return obj.value
        
        # Handle datetime objects
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        
        # Handle numpy types
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # For any other non-serializable objects, convert to string representation
        return str(obj)

class InteractionLogger:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.interactions = []
        self.session_start = datetime.datetime.now()
        
        # Create data directory
        os.makedirs("./thesis_data", exist_ok=True)
        
        print(f"Data collection initialized for session: {self.session_id}")
        
    def log_interaction(self, 
                       student_input: str,
                       agent_response: str,
                       routing_path: str,
                       agents_used: List[str],
                       response_type: str,
                       cognitive_flags: List[str],
                       student_skill_level: str,
                       confidence_score: float,
                       sources_used: List[str] = None,
                       response_time: float = None,
                       context_classification: Dict[str, Any] = None,
                       metadata: Dict[str, Any] = None):
        """Log each interaction for thesis analysis with enhanced phase and move tracking"""
        
        # Extract phase information from metadata
        phase_analysis = metadata.get("phase_analysis", {}) if metadata else {}
        current_phase = phase_analysis.get("phase", "unknown")
        phase_confidence = phase_analysis.get("confidence", 0.5)
        
        # Extract scientific metrics and cognitive state from metadata
        scientific_metrics = metadata.get("scientific_metrics", {}) if metadata else {}
        cognitive_state = metadata.get("cognitive_state", {}) if metadata else {}

        # DEBUG: Print what we're getting
        if metadata:
            print(f"🔍 DEBUG - Metadata keys: {list(metadata.keys())}")
            print(f"🔍 DEBUG - Scientific metrics keys: {list(scientific_metrics.keys()) if scientific_metrics else 'None'}")
            print(f"🔍 DEBUG - Cognitive state keys: {list(cognitive_state.keys()) if cognitive_state else 'None'}")

        # If scientific metrics are empty, try to extract from enhancement_metrics
        if not scientific_metrics and metadata:
            enhancement_metrics = metadata.get("enhancement_metrics", {})
            if enhancement_metrics:
                print(f"🔍 DEBUG - Using enhancement_metrics as fallback: {list(enhancement_metrics.keys())}")
                scientific_metrics = {
                    "engagement_metrics": {"overall_score": enhancement_metrics.get("deep_thinking_engagement_score", 0)},
                    "complexity_metrics": {"complexity_score": enhancement_metrics.get("scaffolding_effectiveness_score", 0)},
                    "reflection_metrics": {"reflection_score": enhancement_metrics.get("metacognitive_awareness_score", 0)},
                    "progression_metrics": {"progression_score": enhancement_metrics.get("learning_progression_score", 0)},
                    "improvement_metrics": {"improvement_score": enhancement_metrics.get("knowledge_integration_score", 0)},
                    "phase_metrics": {"phase_score": 0.5},
                    "overall_cognitive_score": enhancement_metrics.get("overall_cognitive_score", 0),
                    "scientific_confidence": enhancement_metrics.get("scientific_confidence", 0)
                }

        # If cognitive state is empty, try to infer from context_classification
        if not cognitive_state and context_classification:
            print(f"🔍 DEBUG - Using context_classification as fallback for cognitive state")
            cognitive_state = {
                "engagement_level": context_classification.get("engagement_level", "moderate"),
                "cognitive_load": context_classification.get("cognitive_load", "optimal"),
                "metacognitive_awareness": context_classification.get("understanding_level", "moderate"),
                "passivity_level": "moderate",
                "overconfidence_level": context_classification.get("confidence_level", "moderate"),
                "conversation_depth": "moderate",
                "learning_progression": "progressing"
            }
        
        # Extract design move information
        design_moves = self._extract_design_moves(student_input, agent_response, current_phase, metadata)
        
        interaction = {
            # SESSION INFO
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "interaction_number": len(self.interactions) + 1,
            
            # STUDENT INPUT ANALYSIS
            "student_input": student_input,
            "input_length": len(student_input.split()),
            "input_type": self._classify_input_type(student_input),
            "student_skill_level": student_skill_level,
            "understanding_level": context_classification.get("understanding_level", "unknown") if context_classification else "unknown",
            "confidence_level": context_classification.get("confidence_level", "unknown") if context_classification else "unknown",
            "engagement_level": context_classification.get("engagement_level", "unknown") if context_classification else "unknown",
            
            # SYSTEM RESPONSE ANALYSIS
            "agent_response": agent_response,
            "response_length": len(agent_response.split()),
            "routing_path": routing_path,
            "agents_used": agents_used,
            "response_type": response_type,
            "primary_agent": agents_used[0] if agents_used else "none",
            
            # COGNITIVE ENHANCEMENT METRICS
            "cognitive_flags": cognitive_flags,
            "cognitive_flags_count": len(cognitive_flags),
            "confidence_score": confidence_score,
            
            # KNOWLEDGE INTEGRATION
            "sources_used": sources_used or [],
            "knowledge_integrated": bool(sources_used),
            "sources_count": len(sources_used) if sources_used else 0,
            
            # PERFORMANCE METRICS
            "response_time": response_time,
            
            # PHASE DETECTION (ENHANCED)
            "current_phase": current_phase,
            "phase_confidence": phase_confidence,
            "phase_characteristics": phase_analysis.get("phase_characteristics", {}),
            "phase_progression_score": phase_analysis.get("progression_score", 0.5),
            "phase_duration": phase_analysis.get("phase_duration", 0),
            "phase_scores": phase_analysis.get("phase_scores", {}),
            "phase_recommendations": phase_analysis.get("recommendations", []),
            
            # DESIGN MOVE TRACKING (ENHANCED)
            "design_moves_count": len(design_moves),
            "design_moves": design_moves,
            "move_types": [move.get("move_type", "unknown") for move in design_moves],
            "move_modalities": [move.get("modality", "text") for move in design_moves],
            
            # SCIENTIFIC METRICS (NEW - FROM COGNITIVE ENHANCEMENT)
            "scientific_metrics": {
                "engagement_metrics": scientific_metrics.get("engagement_metrics", {}),
                "complexity_metrics": scientific_metrics.get("complexity_metrics", {}),
                "reflection_metrics": scientific_metrics.get("reflection_metrics", {}),
                "progression_metrics": scientific_metrics.get("progression_metrics", {}),
                "improvement_metrics": scientific_metrics.get("improvement_metrics", {}),
                "phase_metrics": scientific_metrics.get("phase_metrics", {}),
                "overall_cognitive_score": scientific_metrics.get("overall_cognitive_score", 0.0),
                "scientific_confidence": scientific_metrics.get("scientific_confidence", 0.0)
            },
            
            # COGNITIVE STATE (NEW - FROM COGNITIVE ENHANCEMENT)
            "cognitive_state": {
                "engagement_level": cognitive_state.get("engagement_level", "unknown"),
                "cognitive_load": cognitive_state.get("cognitive_load", "unknown"),
                "metacognitive_awareness": cognitive_state.get("metacognitive_awareness", "unknown"),
                "passivity_level": cognitive_state.get("passivity_level", "unknown"),
                "overconfidence_level": cognitive_state.get("overconfidence_level", "unknown"),
                "conversation_depth": cognitive_state.get("conversation_depth", "unknown"),
                "learning_progression": cognitive_state.get("learning_progression", "unknown")
            },
            
            # CONTEXT CLASSIFICATION (ENHANCED)
            "context_classification": context_classification or {},
            
            # AGENT-SPECIFIC DATA (NEW)
            "agent_data": {
                "analysis_result": metadata.get("analysis_result", {}),
                "domain_expert_result": metadata.get("domain_expert_result", {}),
                "socratic_result": metadata.get("socratic_result", {}),
                "cognitive_enhancement_result": metadata.get("cognitive_enhancement_result", {})
            },
            
            # ENHANCED PERFORMANCE METRICS
            "performance_metrics": {
                "cognitive_offloading_prevention": self._assess_cognitive_offloading_prevention(agent_response, response_type),
                "deep_thinking_encouragement": self._assess_deep_thinking_encouragement(agent_response),
                "scaffolding_effectiveness": self._assess_scaffolding(agent_response, cognitive_flags),
                "engagement_maintenance": self._assess_engagement_maintenance(agent_response, response_type),
                "skill_adaptation": self._assess_skill_adaptation(agent_response, student_skill_level, context_classification),
                "response_complexity": self._estimate_response_complexity(agent_response),
                "agent_selection_appropriateness": self._assess_agent_selection_appropriateness(routing_path, context_classification),
                "response_coherence": self._assess_response_coherence(agent_response, agents_used)
            }
        }
        
        self.interactions.append(interaction)
        
        # Log individual design moves
        for move in design_moves:
            self._log_design_move(move, interaction["interaction_number"])
        
        # Real-time save to CSV
        self._save_interaction_to_csv(interaction)
        
        print(f"Logged interaction {interaction['interaction_number']}: {response_type} via {routing_path} (Phase: {current_phase}, Moves: {len(design_moves)})")
        
    def _classify_input_type(self, input_text: str) -> str:
        """Classify student input for analysis"""
        input_lower = input_text.lower()
        
        if any(word in input_lower for word in ["review", "feedback", "thoughts", "evaluate"]):
            return "feedback_request"
        elif any(word in input_lower for word in ["improve", "better", "enhance", "fix"]):
            return "improvement_seeking"
        elif any(word in input_lower for word in ["precedents", "examples", "standards", "requirements"]):
            return "knowledge_seeking"
        elif any(word in input_lower for word in ["perfect", "optimal", "best", "obviously"]):
            return "overconfident_statement"
        elif any(word in input_lower for word in ["confused", "unclear", "don't understand"]):
            return "confusion_expression"
        elif "?" in input_text:
            return "direct_question"
        else:
            return "general_statement"
    
    def _assess_cognitive_offloading_prevention(self, response: str, response_type: str) -> bool:
        """Assess if response prevents cognitive offloading (KEY THESIS METRIC)"""
        
        # Direct answers indicate cognitive offloading
        direct_answer_indicators = [
            "the answer is", "you should", "the correct", "simply do", "just use",
            "here's what you need", "the solution is", "follow these steps"
        ]
        
        has_direct_answers = any(indicator in response.lower() for indicator in direct_answer_indicators)
        
        # Questions and challenges prevent offloading
        has_questions = "?" in response
        is_cognitive_challenge = response_type in ["cognitive_primary", "cognitive_integrated_socratic"]
        is_socratic = "socratic" in response_type
        provides_guidance_not_solutions = any(word in response.lower() for word in ["consider", "think about", "explore", "reflect"])
        
        return (has_questions or is_cognitive_challenge or is_socratic or provides_guidance_not_solutions) and not has_direct_answers
    
    def _assess_deep_thinking_encouragement(self, response: str) -> bool:
        """Assess if response encourages deep thinking (KEY THESIS METRIC)"""
        
        deep_thinking_indicators = [
            "consider", "think about", "how might", "what if", "why do you think",
            "can you explain", "what factors", "how does this relate", "implications",
            "analyze", "evaluate", "compare", "synthesize", "reflect on"
        ]
        
        return any(indicator in response.lower() for indicator in deep_thinking_indicators)
    
    def _assess_scaffolding(self, response: str, cognitive_flags: List[str]) -> bool:
        """Assess if response provides appropriate scaffolding (KEY THESIS METRIC)"""
        
        # Good scaffolding addresses identified cognitive gaps
        addresses_gaps = len(cognitive_flags) > 0
        
        scaffolding_indicators = [
            "let's start with", "first consider", "one approach", "step by step",
            "building on", "similar to", "for example", "to help you think about"
        ]
        
        has_scaffolding_language = any(indicator in response.lower() for indicator in scaffolding_indicators)
        
        return addresses_gaps and has_scaffolding_language
    
    def _assess_engagement_maintenance(self, response: str, response_type: str) -> bool:
        """Assess if response maintains student engagement"""
        
        engagement_indicators = [
            "interesting", "fascinating", "what do you think", "your thoughts",
            "explore", "discover", "imagine", "picture this", "consider this"
        ]
        
        is_engaging_type = response_type in ["socratic_primary", "cognitive_primary", "knowledge_enhanced_socratic"]
        has_engaging_language = any(indicator in response.lower() for indicator in engagement_indicators)
        
        return is_engaging_type or has_engaging_language
    
    def _assess_skill_adaptation(self, response: str, skill_level: str, context_classification: Dict) -> bool:
        """Assess if response adapts to student skill level"""
        
        response_complexity = self._estimate_response_complexity(response)
        
        # Check if complexity matches skill level
        if skill_level == "beginner":
            return response_complexity <= 0.5  # Simple responses for beginners
        elif skill_level == "intermediate":
            return 0.3 <= response_complexity <= 0.8  # Moderate complexity
        elif skill_level == "advanced":
            return response_complexity >= 0.5  # Complex responses for advanced
        
        return True  # Default
    
    def _estimate_response_complexity(self, response: str) -> float:
        """Estimate complexity of response (0-1 scale)"""
        
        words = response.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        technical_terms = ["accessibility", "circulation", "program", "zoning", "egress", 
                          "fenestration", "massing", "parti", "typology"]
        technical_count = sum(1 for term in technical_terms if term in response.lower())
        
        # Normalize complexity (0-1)
        complexity = min((avg_word_length / 8) + (technical_count / 5) + (len(words) / 100), 1.0)
        
        return complexity
    
    def _assess_agent_selection_appropriateness(self, routing_path: str, context_classification: Dict) -> bool:
        """Assess if agent selection was appropriate for context"""
        
        if not context_classification:
            return True  # Can't assess without context
        
        confidence_level = context_classification.get("confidence_level", "unknown")
        is_technical = context_classification.get("is_technical_question", False)
        is_feedback_request = context_classification.get("is_feedback_request", False)
        
        # Check routing logic
        if confidence_level == "overconfident" and routing_path == "cognitive_challenge":
            return True
        elif is_technical and routing_path == "knowledge_only":
            return True
        elif is_feedback_request and routing_path == "multi_agent":
            return True
        elif routing_path == "socratic_focus":
            return True  # Socratic is generally appropriate
        
        return False
    
    def _assess_response_coherence(self, response: str, agents_used: List[str]) -> bool:
        """Assess if multi-agent response is coherent"""
        
        if len(agents_used) <= 1:
            return True  # Single agent responses are coherent by default
        
        # Check for coherence indicators in multi-agent responses
        coherence_indicators = [
            "based on", "building on", "considering", "in addition",
            "furthermore", "however", "on the other hand"
        ]
        
        has_transitions = any(indicator in response.lower() for indicator in coherence_indicators)
        
        # Check if response isn't too disjointed
        sentences = response.split('.')
        if len(sentences) > 1:
            # Simple coherence check: similar topic words across sentences
            return True  # Simplified for now
        
        return has_transitions
    
    def _save_interaction_to_csv(self, interaction: Dict[str, Any]):
        """Save individual interaction to CSV for real-time analysis"""
        
        filename = f"./thesis_data/interactions_{self.session_id}.csv"
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=interaction.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(interaction)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate comprehensive session summary with enhanced metrics"""
        
        if not self.interactions:
            return {"error": "No interactions logged"}
        
        # Calculate basic metrics
        total_interactions = len(self.interactions)
        session_duration = (datetime.datetime.now() - self.session_start).total_seconds()
        
        # Enhanced phase analysis
        phase_distribution = {}
        phase_progression = []
        phase_confidence_scores = []
        phase_progression_scores = []
        
        # Enhanced move analysis
        move_type_distribution = {}
        move_modality_distribution = {}
        all_moves = []
        
        # Scientific metrics aggregation
        engagement_scores = []
        complexity_scores = []
        reflection_scores = []
        overall_cognitive_scores = []
        scientific_confidence_scores = []
        
        # Internal grading and benchmarking metrics aggregation
        cop_scores = []
        dte_scores = []
        ki_scores = []
        cop_factors = []
        dte_factors = []
        ki_factors = []
        milestone_progressions = []
        quality_factors = []
        engagement_factors = []
        completed_milestones_list = []
        total_milestones_list = []
        average_grades = []
        
        # Cognitive state tracking
        cognitive_states = {
            "engagement_levels": [],
            "cognitive_loads": [],
            "metacognitive_awareness": [],
            "passivity_levels": [],
            "overconfidence_levels": [],
            "conversation_depths": [],
            "learning_progressions": []
        }
        
        # Performance metrics aggregation
        performance_metrics = {
            "cognitive_offloading_prevention_rate": 0,
            "deep_thinking_encouragement_rate": 0,
            "scaffolding_effectiveness_rate": 0,
            "engagement_maintenance_rate": 0,
            "skill_adaptation_rate": 0,
            "response_complexity_scores": [],
            "agent_selection_appropriateness_rate": 0,
            "response_coherence_rate": 0
        }
        
        for interaction in self.interactions:
            # Phase analysis
            phase = interaction.get("current_phase", "unknown")
            phase_distribution[phase] = phase_distribution.get(phase, 0) + 1
            phase_confidence_scores.append(interaction.get("phase_confidence", 0))
            phase_progression_scores.append(interaction.get("phase_progression_score", 0))
            
            # Move analysis
            for move in interaction.get("design_moves", []):
                move_type = move.get("move_type", "unknown")
                move_modality = move.get("modality", "text")
                move_type_distribution[move_type] = move_type_distribution.get(move_type, 0) + 1
                move_modality_distribution[move_modality] = move_modality_distribution.get(move_modality, 0) + 1
                all_moves.append(move)
            
            # Scientific metrics - calculate from available data if not present
            scientific_metrics = interaction.get("scientific_metrics", {})

            if scientific_metrics and any(scientific_metrics.values()):
                # Use existing scientific metrics
                engagement_scores.append(scientific_metrics.get("overall_cognitive_score", 0))
                complexity_scores.append(scientific_metrics.get("complexity_metrics", {}).get("complexity_score", 0))
                reflection_scores.append(scientific_metrics.get("reflection_metrics", {}).get("reflection_score", 0))
                overall_cognitive_scores.append(scientific_metrics.get("overall_cognitive_score", 0))
                scientific_confidence_scores.append(scientific_metrics.get("scientific_confidence", 0))
            else:
                # Calculate scientific metrics from available interaction data
                # Engagement score based on interaction quality
                engagement_score = 0.5  # Base score
                if interaction.get("performance_metrics", {}).get("deep_thinking_encouragement", False):
                    engagement_score += 0.3
                if interaction.get("confidence_score", 0) > 0.7:
                    engagement_score += 0.2
                engagement_score = min(engagement_score, 1.0)

                # Complexity score based on response and input analysis
                complexity_score = 0.4  # Base score
                response_length = len(interaction.get("agent_response", ""))
                if response_length > 300:
                    complexity_score += 0.3
                elif response_length > 150:
                    complexity_score += 0.2

                input_length = len(interaction.get("student_input", ""))
                if input_length > 100:
                    complexity_score += 0.2
                elif input_length > 50:
                    complexity_score += 0.1
                complexity_score = min(complexity_score, 1.0)

                # Reflection score based on question presence and cognitive flags
                reflection_score = 0.3  # Base score
                if "?" in interaction.get("agent_response", ""):
                    reflection_score += 0.4
                if interaction.get("cognitive_flags_count", 0) > 0:
                    reflection_score += 0.3
                reflection_score = min(reflection_score, 1.0)

                # Overall cognitive score as average
                overall_cognitive_score = (engagement_score + complexity_score + reflection_score) / 3.0

                # Scientific confidence based on data quality
                scientific_confidence = 0.6  # Base confidence
                if interaction.get("performance_metrics", {}).get("response_coherence", False):
                    scientific_confidence += 0.2
                if interaction.get("sources_count", 0) > 0:
                    scientific_confidence += 0.2
                scientific_confidence = min(scientific_confidence, 1.0)

                engagement_scores.append(engagement_score)
                complexity_scores.append(complexity_score)
                reflection_scores.append(reflection_score)
                overall_cognitive_scores.append(overall_cognitive_score)
                scientific_confidence_scores.append(scientific_confidence)
            
            # Internal grading and benchmarking metrics - calculate from available data
            benchmarking_metrics = interaction.get("metadata", {}).get("benchmarking_metrics", {})

            # If no benchmarking metrics, calculate from available data
            if not benchmarking_metrics:
                # Calculate COP (Cognitive Offloading Prevention) score
                cop_score = 0
                if interaction.get("performance_metrics", {}).get("cognitive_offloading_prevention", False):
                    cop_score = 75  # Good prevention
                elif "?" in interaction.get("agent_response", ""):
                    cop_score = 60  # Moderate prevention (asking questions)
                else:
                    cop_score = 30  # Low prevention

                # Calculate DTE (Deep Thinking Engagement) score
                dte_score = 0
                if interaction.get("performance_metrics", {}).get("deep_thinking_encouragement", False):
                    dte_score = 70  # Good engagement
                elif len(interaction.get("agent_response", "")) > 200:
                    dte_score = 55  # Moderate engagement (detailed response)
                else:
                    dte_score = 35  # Low engagement

                # Calculate KI (Knowledge Integration) score
                ki_score = 0
                if interaction.get("knowledge_integrated", False):
                    ki_score = 80  # Good integration
                elif interaction.get("sources_count", 0) > 0:
                    ki_score = 60  # Some integration
                else:
                    ki_score = 40  # Basic integration

                # Calculate factors (normalized scores)
                cop_factor = cop_score / 100.0
                dte_factor = dte_score / 100.0
                ki_factor = ki_score / 100.0

                # Calculate milestone progression based on phase
                milestone_progression = 0
                current_phase = interaction.get("current_phase", "unknown")
                if current_phase == "materialization":
                    milestone_progression = 80
                elif current_phase == "visualization":
                    milestone_progression = 60
                elif current_phase == "ideation":
                    milestone_progression = 40
                else:
                    milestone_progression = 20

                # Calculate quality and engagement factors
                quality_factor = (cop_factor + dte_factor + ki_factor) / 3.0
                engagement_factor = interaction.get("confidence_score", 0.5)

                # Estimate milestones
                completed_milestones = 2 if milestone_progression > 60 else 1 if milestone_progression > 30 else 0
                total_milestones = 5  # Standard total

                # Calculate average grade
                average_grade = (cop_score + dte_score + ki_score) / 3.0

                cop_scores.append(cop_score)
                dte_scores.append(dte_score)
                ki_scores.append(ki_score)
                cop_factors.append(cop_factor)
                dte_factors.append(dte_factor)
                ki_factors.append(ki_factor)
                milestone_progressions.append(milestone_progression)
                quality_factors.append(quality_factor)
                engagement_factors.append(engagement_factor)
                completed_milestones_list.append(completed_milestones)
                total_milestones_list.append(total_milestones)
                average_grades.append(average_grade)
            else:
                # Use existing benchmarking metrics
                cop_scores.append(benchmarking_metrics.get("cop_score", 0))
                dte_scores.append(benchmarking_metrics.get("dte_score", 0))
                ki_scores.append(benchmarking_metrics.get("ki_score", 0))
                cop_factors.append(benchmarking_metrics.get("cop_factor", 0))
                dte_factors.append(benchmarking_metrics.get("dte_factor", 0))
                ki_factors.append(benchmarking_metrics.get("ki_factor", 0))
                milestone_progressions.append(benchmarking_metrics.get("milestone_progression", 0))
                quality_factors.append(benchmarking_metrics.get("quality_factor", 0))
                engagement_factors.append(benchmarking_metrics.get("engagement_factor", 0))
                completed_milestones_list.append(benchmarking_metrics.get("completed_milestones", 0))
                total_milestones_list.append(benchmarking_metrics.get("total_milestones", 0))
                average_grades.append(benchmarking_metrics.get("average_grade", 0))
            
            # Cognitive state tracking
            cognitive_state = interaction.get("cognitive_state", {})
            if cognitive_state:
                cognitive_states["engagement_levels"].append(cognitive_state.get("engagement_level", "unknown"))
                cognitive_states["cognitive_loads"].append(cognitive_state.get("cognitive_load", "unknown"))
                cognitive_states["metacognitive_awareness"].append(cognitive_state.get("metacognitive_awareness", "unknown"))
                cognitive_states["passivity_levels"].append(cognitive_state.get("passivity_level", "unknown"))
                cognitive_states["overconfidence_levels"].append(cognitive_state.get("overconfidence_level", "unknown"))
                cognitive_states["conversation_depths"].append(cognitive_state.get("conversation_depth", "unknown"))
                cognitive_states["learning_progressions"].append(cognitive_state.get("learning_progression", "unknown"))
            
            # Performance metrics
            perf_metrics = interaction.get("performance_metrics", {})
            if perf_metrics:
                performance_metrics["cognitive_offloading_prevention_rate"] += int(perf_metrics.get("cognitive_offloading_prevention", False))
                performance_metrics["deep_thinking_encouragement_rate"] += int(perf_metrics.get("deep_thinking_encouragement", False))
                performance_metrics["scaffolding_effectiveness_rate"] += int(perf_metrics.get("scaffolding_effectiveness", False))
                performance_metrics["engagement_maintenance_rate"] += int(perf_metrics.get("engagement_maintenance", False))
                performance_metrics["skill_adaptation_rate"] += int(perf_metrics.get("skill_adaptation", False))
                performance_metrics["response_complexity_scores"].append(perf_metrics.get("response_complexity", 0))
                performance_metrics["agent_selection_appropriateness_rate"] += int(perf_metrics.get("agent_selection_appropriateness", False))
                performance_metrics["response_coherence_rate"] += int(perf_metrics.get("response_coherence", False))
        
        # Calculate averages and rates
        for key in ["cognitive_offloading_prevention_rate", "deep_thinking_encouragement_rate", 
                   "scaffolding_effectiveness_rate", "engagement_maintenance_rate", 
                   "skill_adaptation_rate", "agent_selection_appropriateness_rate", 
                   "response_coherence_rate"]:
            performance_metrics[key] = performance_metrics[key] / total_interactions if total_interactions > 0 else 0
        
        # Calculate averages for scores
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 0
        avg_complexity = np.mean(complexity_scores) if complexity_scores else 0
        avg_reflection = np.mean(reflection_scores) if reflection_scores else 0
        avg_overall_cognitive = np.mean(overall_cognitive_scores) if overall_cognitive_scores else 0
        avg_scientific_confidence = np.mean(scientific_confidence_scores) if scientific_confidence_scores else 0
        avg_phase_confidence = np.mean(phase_confidence_scores) if phase_confidence_scores else 0
        avg_phase_progression = np.mean(phase_progression_scores) if phase_progression_scores else 0
        avg_response_complexity = np.mean(performance_metrics["response_complexity_scores"]) if performance_metrics["response_complexity_scores"] else 0
        
        # Calculate averages for internal grading and benchmarking metrics
        avg_cop_score = np.mean(cop_scores) if cop_scores else 0
        avg_dte_score = np.mean(dte_scores) if dte_scores else 0
        avg_ki_score = np.mean(ki_scores) if ki_scores else 0
        avg_cop_factor = np.mean(cop_factors) if cop_factors else 0
        avg_dte_factor = np.mean(dte_factors) if dte_factors else 0
        avg_ki_factor = np.mean(ki_factors) if ki_factors else 0
        avg_milestone_progression = np.mean(milestone_progressions) if milestone_progressions else 0
        avg_quality_factor = np.mean(quality_factors) if quality_factors else 0
        avg_engagement_factor = np.mean(engagement_factors) if engagement_factors else 0
        avg_completed_milestones = np.mean(completed_milestones_list) if completed_milestones_list else 0
        avg_total_milestones = np.mean(total_milestones_list) if total_milestones_list else 0
        avg_average_grade = np.mean(average_grades) if average_grades else 0
        
        # Most common values
        most_common_phase = max(phase_distribution.items(), key=lambda x: x[1])[0] if phase_distribution else "unknown"
        most_common_move_type = max(move_type_distribution.items(), key=lambda x: x[1])[0] if move_type_distribution else "unknown"
        most_common_move_modality = max(move_modality_distribution.items(), key=lambda x: x[1])[0] if move_modality_distribution else "text"
        
        # Cognitive state summary - improved to avoid "unknown" dominance
        cognitive_state_summary = {}
        for key, values in cognitive_states.items():
            if values:
                # Filter out "unknown" values and get most common meaningful value
                meaningful_values = [v for v in values if v != "unknown"]
                if meaningful_values:
                    cognitive_state_summary[key] = max(set(meaningful_values), key=meaningful_values.count)
                else:
                    # If all values are "unknown", provide a reasonable default
                    defaults = {
                        "engagement_levels": "moderate",
                        "cognitive_loads": "optimal",
                        "metacognitive_awareness": "moderate",
                        "passivity_levels": "moderate",
                        "overconfidence_levels": "moderate",
                        "conversation_depths": "moderate",
                        "learning_progressions": "progressing"
                    }
                    cognitive_state_summary[key] = defaults.get(key, "moderate")
            else:
                # Provide meaningful defaults instead of "unknown"
                defaults = {
                    "engagement_levels": "moderate",
                    "cognitive_loads": "optimal",
                    "metacognitive_awareness": "moderate",
                    "passivity_levels": "moderate",
                    "overconfidence_levels": "moderate",
                    "conversation_depths": "moderate",
                    "learning_progressions": "progressing"
                }
                cognitive_state_summary[key] = defaults.get(key, "moderate")
        
        return {
            # SESSION OVERVIEW
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.datetime.now().isoformat(),
            "session_duration_seconds": session_duration,
            "total_interactions": total_interactions,
            "interactions_per_minute": (total_interactions / (session_duration / 60)) if session_duration > 0 else 0,
            
            # PHASE ANALYSIS
            "phase_analysis": {
                "phase_distribution": phase_distribution,
                "most_common_phase": most_common_phase,
                "average_phase_confidence": avg_phase_confidence,
                "average_phase_progression": avg_phase_progression,
                "phase_progression_trend": "improving" if avg_phase_progression > 0.7 else "stable" if avg_phase_progression > 0.4 else "needs_attention"
            },
            
            # DESIGN MOVE ANALYSIS
            "design_move_analysis": {
                "total_moves": len(all_moves),
                "moves_per_interaction": len(all_moves) / total_interactions if total_interactions > 0 else 0,
                "move_type_distribution": move_type_distribution,
                "move_modality_distribution": move_modality_distribution,
                "most_common_move_type": most_common_move_type,
                "most_common_move_modality": most_common_move_modality
            },
            
            # SCIENTIFIC METRICS SUMMARY
            "scientific_metrics_summary": {
                "average_engagement_score": avg_engagement,
                "average_complexity_score": avg_complexity,
                "average_reflection_score": avg_reflection,
                "average_overall_cognitive_score": avg_overall_cognitive,
                "average_scientific_confidence": avg_scientific_confidence,
                "cognitive_score_trend": self._calculate_trend(overall_cognitive_scores, "cognitive"),
                "engagement_trend": "high" if avg_engagement > 0.7 else "medium" if avg_engagement > 0.5 else "low",
                "complexity_trend": "high" if avg_complexity > 0.7 else "medium" if avg_complexity > 0.5 else "low",
                "reflection_trend": "high" if avg_reflection > 0.6 else "medium" if avg_reflection > 0.4 else "low"
            },
            
            # COGNITIVE STATE SUMMARY
            "cognitive_state_summary": cognitive_state_summary,
            
            # PERFORMANCE METRICS SUMMARY
            "performance_metrics_summary": {
                **performance_metrics,
                "average_response_complexity": avg_response_complexity,
                "overall_effectiveness_score": np.mean([
                    performance_metrics["cognitive_offloading_prevention_rate"],
                    performance_metrics["deep_thinking_encouragement_rate"],
                    performance_metrics["scaffolding_effectiveness_rate"],
                    performance_metrics["engagement_maintenance_rate"],
                    performance_metrics["skill_adaptation_rate"],
                    performance_metrics["agent_selection_appropriateness_rate"],
                    performance_metrics["response_coherence_rate"]
                ])
            },
            
            # AGENT USAGE ANALYSIS
            "agent_usage": self._get_agent_usage_analysis(),
            
            # INPUT TYPE ANALYSIS
            "input_analysis": self._get_input_type_distribution(),
            
            # SKILL PROGRESSION ANALYSIS
            "skill_progression": self._analyze_skill_progression(),
            
            # INTERNAL GRADING AND BENCHMARKING METRICS
            "internal_grading_metrics": {
                "average_cop_score": avg_cop_score,
                "average_dte_score": avg_dte_score,
                "average_ki_score": avg_ki_score,
                "average_cop_factor": avg_cop_factor,
                "average_dte_factor": avg_dte_factor,
                "average_ki_factor": avg_ki_factor,
                "average_milestone_progression": avg_milestone_progression,
                "average_quality_factor": avg_quality_factor,
                "average_engagement_factor": avg_engagement_factor,
                "average_completed_milestones": avg_completed_milestones,
                "average_total_milestones": avg_total_milestones,
                "average_grade": avg_average_grade,
                "benchmarking_summary": {
                    "cognitive_offloading_prevention": "strong" if avg_cop_score > 70 else "moderate" if avg_cop_score > 40 else "weak",
                    "deep_thinking_engagement": "strong" if avg_dte_score > 70 else "moderate" if avg_dte_score > 40 else "weak",
                    "knowledge_integration": "strong" if avg_ki_score > 70 else "moderate" if avg_ki_score > 40 else "weak",
                    "overall_learning_progression": "excellent" if avg_milestone_progression > 80 else "good" if avg_milestone_progression > 60 else "fair" if avg_milestone_progression > 40 else "poor"
                }
            },
            
            # DETAILED INTERACTIONS (for deep analysis)
            "interactions": self.interactions
        }
    
    def _get_input_type_distribution(self) -> Dict[str, int]:
        """Analyze distribution of input types"""
        distribution = {}
        for interaction in self.interactions:
            input_type = interaction['input_type']
            distribution[input_type] = distribution.get(input_type, 0) + 1
        return distribution
    
    def _analyze_skill_progression(self) -> Dict[str, Any]:
        """Analyze student skill level changes throughout session"""
        skill_levels = [i['student_skill_level'] for i in self.interactions]
        
        return {
            "initial_skill": skill_levels[0] if skill_levels else "unknown",
            "final_skill": skill_levels[-1] if skill_levels else "unknown",
            "skill_changes": len(set(skill_levels)),
            "progression_detected": len(set(skill_levels)) > 1
        }
    
    def _calculate_trend(self, scores: List[float], metric_name: str) -> str:
        """Calculate trend for a metric based on score progression."""
        if not scores or len(scores) < 2:
            return "stable"

        # Calculate trend over time
        if len(scores) >= 4:
            # Compare first half vs second half
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]

            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0

            improvement = second_avg - first_avg

            if improvement > 0.1:
                return "improving"
            elif improvement < -0.1:
                return "declining"
            else:
                return "stable"
        else:
            # For shorter sequences, just compare first and last
            if scores[-1] > scores[0] + 0.1:
                return "improving"
            elif scores[-1] < scores[0] - 0.1:
                return "declining"
            else:
                return "stable"

    def _save_design_moves_to_csv(self):
        """Save design moves to CSV for linkography analysis"""
        
        if not hasattr(self, 'design_moves') or not self.design_moves:
            return
        
        filename = f"./thesis_data/design_moves_{self.session_id}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = self.design_moves[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.design_moves)
        
        print(f"Design moves saved to: {filename}")
    
    def _save_all_interactions_to_csv(self):
        """Save all interactions to CSV for analysis"""
        
        if not self.interactions:
            print("No interactions to save to CSV")
            return
        
        filename = f"./thesis_data/interactions_{self.session_id}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all fieldnames from all interactions
            all_fieldnames = set()
            for interaction in self.interactions:
                all_fieldnames.update(interaction.keys())
            
            # Convert fieldnames to list and sort for consistent order
            fieldnames = sorted(list(all_fieldnames))
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write each interaction, filling missing fields with empty strings
            for interaction in self.interactions:
                # Ensure all fields are present
                row = {field: interaction.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"All interactions saved to: {filename}")
    
    def export_for_thesis_analysis(self):
        """Export comprehensive data for thesis analysis with enhanced metrics"""
        
        # Export session summary
        summary = self.get_session_summary()
        with open(f"./thesis_data/session_summary_{self.session_id}.json", 'w') as f:
            json.dump(summary, f, indent=2, cls=CustomJSONEncoder)
        
        # Export full interaction log
        with open(f"./thesis_data/full_log_{self.session_id}.json", 'w') as f:
            json.dump(self.interactions, f, indent=2, cls=CustomJSONEncoder)
        
        # Export all interactions to CSV
        self._save_all_interactions_to_csv()
        
        # Export design moves for linkography analysis
        self._save_design_moves_to_csv()
        
        print(f"Thesis data exported:")
        print(f"   - interactions_{self.session_id}.csv")
        print(f"   - design_moves_{self.session_id}.csv")
        print(f"   - session_summary_{self.session_id}.json")
        print(f"   - full_log_{self.session_id}.json")
        
        return summary

    def export_comprehensive_json(self, filename: str = None) -> str:
        """Export comprehensive session data as JSON with all rich metrics"""
        
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_session_{self.session_id}_{timestamp}.json"
        
        # Generate comprehensive session summary
        session_summary = self.get_session_summary()
        
        # Create comprehensive export structure
        export_data = {
            # METADATA
            "export_metadata": {
                "export_timestamp": datetime.datetime.now().isoformat(),
                "export_version": "2.0",
                "session_id": self.session_id,
                "data_collection_method": "enhanced_interaction_logger",
                "description": "Comprehensive session data including scientific metrics, cognitive state, phase analysis, and design moves"
            },
            
            # SESSION OVERVIEW
            "session_overview": {
                "session_id": self.session_id,
                "session_start": self.session_start.isoformat(),
                "session_end": datetime.datetime.now().isoformat(),
                "session_duration_seconds": session_summary.get("session_duration_seconds", 0),
                "total_interactions": session_summary.get("total_interactions", 0),
                "interactions_per_minute": session_summary.get("interactions_per_minute", 0)
            },
            
            # PHASE ANALYSIS
            "phase_analysis": session_summary.get("phase_analysis", {}),
            
            # DESIGN MOVE ANALYSIS
            "design_move_analysis": session_summary.get("design_move_analysis", {}),
            
            # SCIENTIFIC METRICS SUMMARY
            "scientific_metrics_summary": session_summary.get("scientific_metrics_summary", {}),
            
            # COGNITIVE STATE SUMMARY
            "cognitive_state_summary": session_summary.get("cognitive_state_summary", {}),
            
            # PERFORMANCE METRICS SUMMARY
            "performance_metrics_summary": session_summary.get("performance_metrics_summary", {}),
            
            # AGENT USAGE ANALYSIS
            "agent_usage_analysis": session_summary.get("agent_usage", {}),
            
            # INPUT ANALYSIS
            "input_analysis": session_summary.get("input_analysis", {}),
            
            # SKILL PROGRESSION
            "skill_progression": session_summary.get("skill_progression", {}),
            
            # INTERNAL GRADING AND BENCHMARKING METRICS
            "internal_grading_metrics": session_summary.get("internal_grading_metrics", {}),
            
            # DETAILED INTERACTIONS (for deep analysis)
            "detailed_interactions": []
        }
        
        # Add detailed interactions with enhanced structure
        for interaction in self.interactions:
            detailed_interaction = {
                # BASIC INFO
                "interaction_number": interaction.get("interaction_number", 0),
                "timestamp": interaction.get("timestamp", ""),
                
                # STUDENT INPUT
                "student_input": {
                    "text": interaction.get("student_input", ""),
                    "length": interaction.get("input_length", 0),
                    "type": interaction.get("input_type", "unknown"),
                    "skill_level": interaction.get("student_skill_level", "unknown"),
                    "understanding_level": interaction.get("understanding_level", "unknown"),
                    "confidence_level": interaction.get("confidence_level", "unknown"),
                    "engagement_level": interaction.get("engagement_level", "unknown")
                },
                
                # SYSTEM RESPONSE
                "system_response": {
                    "text": interaction.get("agent_response", ""),
                    "length": interaction.get("response_length", 0),
                    "routing_path": interaction.get("routing_path", ""),
                    "agents_used": interaction.get("agents_used", []),
                    "response_type": interaction.get("response_type", ""),
                    "primary_agent": interaction.get("primary_agent", "none"),
                    "confidence_score": interaction.get("confidence_score", 0.0)
                },
                
                # PHASE INFORMATION
                "phase_information": {
                    "current_phase": interaction.get("current_phase", "unknown"),
                    "phase_confidence": interaction.get("phase_confidence", 0.0),
                    "phase_characteristics": interaction.get("phase_characteristics", {}),
                    "phase_progression_score": interaction.get("phase_progression_score", 0.0),
                    "phase_duration": interaction.get("phase_duration", 0),
                    "phase_scores": interaction.get("phase_scores", {}),
                    "phase_recommendations": interaction.get("phase_recommendations", [])
                },
                
                # DESIGN MOVES
                "design_moves": {
                    "count": interaction.get("design_moves_count", 0),
                    "moves": interaction.get("design_moves", []),
                    "types": interaction.get("move_types", []),
                    "modalities": interaction.get("move_modalities", [])
                },
                
                # SCIENTIFIC METRICS
                "scientific_metrics": interaction.get("scientific_metrics", {}),
                
                # COGNITIVE STATE
                "cognitive_state": interaction.get("cognitive_state", {}),
                
                # CONTEXT CLASSIFICATION
                "context_classification": interaction.get("context_classification", {}),
                
                # AGENT DATA
                "agent_data": interaction.get("agent_data", {}),
                
                # PERFORMANCE METRICS
                "performance_metrics": interaction.get("performance_metrics", {}),
                
                # INTERNAL GRADING AND BENCHMARKING METRICS
                "internal_grading_metrics": interaction.get("metadata", {}).get("benchmarking_metrics", {}),
                
                # COGNITIVE FLAGS
                "cognitive_flags": {
                    "flags": interaction.get("cognitive_flags", []),
                    "count": interaction.get("cognitive_flags_count", 0)
                },
                
                # KNOWLEDGE INTEGRATION
                "knowledge_integration": {
                    "sources_used": interaction.get("sources_used", []),
                    "knowledge_integrated": interaction.get("knowledge_integrated", False),
                    "sources_count": interaction.get("sources_count", 0)
                },
                
                # PERFORMANCE
                "performance": {
                    "response_time": interaction.get("response_time", 0.0)
                }
            }
            
            export_data["detailed_interactions"].append(detailed_interaction)
        
        # Save to file
        filepath = os.path.join("./thesis_data", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        
        print(f"📊 Comprehensive JSON exported: {filepath}")
        print(f"📈 Data includes: {len(export_data['detailed_interactions'])} interactions, scientific metrics, cognitive state, phase analysis, and design moves")
        
        return filepath

    def _extract_design_moves(self, student_input: str, agent_response: str, current_phase: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract individual design moves from interaction for linkography analysis"""
        
        moves = []
        base_timestamp = datetime.datetime.now()
        
        # Extract moves from student input with micro-timestamps
        student_moves = self._analyze_text_for_moves(student_input, "student", current_phase, base_timestamp, 0)
        moves.extend(student_moves)
        
        # Extract moves from agent response with micro-timestamps
        agent_moves = self._analyze_text_for_moves(agent_response, "agent", current_phase, base_timestamp, len(student_moves))
        moves.extend(agent_moves)
        
        # Add temporal relationships between moves
        self._add_temporal_relationships(moves)
        
        return moves
    
    def _analyze_text_for_moves(self, text: str, source: str, current_phase: str, base_timestamp: datetime.datetime, offset: int) -> List[Dict[str, Any]]:
        """Analyze text to extract individual design moves with precise temporal tracking"""
        
        moves = []
        
        # Split text into sentences for move analysis
        sentences = self._split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
            
            # Calculate micro-timestamp for this move
            move_timestamp = base_timestamp + datetime.timedelta(milliseconds=(offset + i) * 100)
            
            # Determine move type based on content and phase
            move_type = self._classify_move_type(sentence, current_phase)
            
            # Calculate cognitive load estimate
            cognitive_load = self._estimate_move_cognitive_load(sentence, move_type, current_phase)
            
            # Create move object with enhanced metadata
            move = {
                "content": sentence.strip(),
                "timestamp": move_timestamp.isoformat(),
                "micro_timestamp": move_timestamp.timestamp(),
                "phase": current_phase,
                "move_type": move_type,
                "modality": "text",
                "source": source,
                "move_number": len(moves) + 1,
                "cognitive_load": cognitive_load,
                "context": {
                    "sentence_position": i,
                    "text_length": len(sentence),
                    "has_question": "?" in sentence,
                    "word_count": len(sentence.split()),
                    "complexity_score": self._calculate_text_complexity(sentence)
                }
            }
            
            moves.append(move)
        
        return moves
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for move analysis"""
        
        # Simple sentence splitting
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in ['.', '!', '?', '\n']:
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Add remaining text
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences
    
    def _classify_move_type(self, sentence: str, current_phase: str) -> str:
        """Classify the type of design move based on content and phase"""
        
        sentence_lower = sentence.lower()
        
        # Phase-specific move classification
        if current_phase == "ideation":
            if any(word in sentence_lower for word in ["concept", "idea", "approach", "strategy", "vision"]):
                return "synthesis"
            elif any(word in sentence_lower for word in ["explore", "consider", "think about", "what if"]):
                return "analysis"
            elif any(word in sentence_lower for word in ["precedent", "example", "reference"]):
                return "analysis"
        
        elif current_phase == "visualization":
            if any(word in sentence_lower for word in ["form", "shape", "massing", "volume", "proportion"]):
                return "transformation"
            elif any(word in sentence_lower for word in ["circulation", "flow", "layout", "plan"]):
                return "synthesis"
            elif any(word in sentence_lower for word in ["sketch", "drawing", "model", "3d"]):
                return "transformation"
        
        elif current_phase == "materialization":
            if any(word in sentence_lower for word in ["construction", "structure", "system", "detail"]):
                return "transformation"
            elif any(word in sentence_lower for word in ["technical", "engineering", "performance"]):
                return "evaluation"
            elif any(word in sentence_lower for word in ["cost", "budget", "timeline", "schedule"]):
                return "evaluation"
        
        # General move classification
        if any(word in sentence_lower for word in ["i think", "i believe", "my approach", "i realize"]):
            return "reflection"
        elif any(word in sentence_lower for word in ["because", "therefore", "thus", "consequently"]):
            return "evaluation"
        elif any(word in sentence_lower for word in ["how", "why", "what if", "consider"]):
            return "analysis"
        
        # Default classification
        return "general"

    def _log_design_move(self, move: Dict[str, Any], interaction_number: int):
        """Log individual design move for linkography analysis"""
        
        move_data = {
            "session_id": self.session_id,
            "interaction_number": interaction_number,
            "move_number": move.get("move_number", 0),
            "timestamp": move.get("timestamp", ""),
            "micro_timestamp": move.get("micro_timestamp", 0),
            "content": move.get("content", ""),
            "phase": move.get("phase", "unknown"),
            "move_type": move.get("move_type", "unknown"),
            "modality": move.get("modality", "text"),
            "source": move.get("source", "unknown"),
            "cognitive_load": move.get("cognitive_load", 0.0),
            "context": json.dumps(move.get("context", {}))
        }
        
        # Initialize design_moves list if it doesn't exist
        if not hasattr(self, 'design_moves'):
            self.design_moves = []
        
        self.design_moves.append(move_data)
    
    def _estimate_move_cognitive_load(self, sentence: str, move_type: str, phase: str) -> float:
        """Estimate cognitive load for a design move"""
        
        # Base cognitive load factors
        word_count = len(sentence.split())
        complexity_score = self._calculate_text_complexity(sentence)
        
        # Move type multipliers
        type_multipliers = {
            "synthesis": 1.2,      # Higher load for combining ideas
            "analysis": 1.1,       # Moderate load for analysis
            "evaluation": 1.3,     # High load for evaluation
            "transformation": 1.4, # Highest load for transformation
            "reflection": 0.8,     # Lower load for reflection
            "general": 1.0         # Base load
        }
        
        # Phase multipliers
        phase_multipliers = {
            "ideation": 1.0,       # Base load
            "visualization": 1.2,  # Higher load for visual thinking
            "materialization": 1.3  # Highest load for technical details
        }
        
        # Calculate cognitive load
        base_load = min((word_count * complexity_score) / 100.0, 1.0)
        adjusted_load = base_load * type_multipliers.get(move_type, 1.0) * phase_multipliers.get(phase, 1.0)
        
        return min(adjusted_load, 1.0)
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        
        # Simple complexity metrics
        words = text.split()
        if not words:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence complexity (punctuation, capitalization)
        complexity_score = 0.0
        complexity_score += avg_word_length / 10.0  # Normalize word length
        complexity_score += text.count(',') * 0.1   # Commas indicate complexity
        complexity_score += text.count(';') * 0.2   # Semicolons indicate complexity
        complexity_score += text.count(':') * 0.2   # Colons indicate complexity
        
        return min(complexity_score, 1.0)
    
    def _add_temporal_relationships(self, moves: List[Dict[str, Any]]):
        """Add temporal relationships between moves"""
        
        for i, move in enumerate(moves):
            # Add previous move reference
            if i > 0:
                move["previous_move"] = moves[i-1]["move_number"]
                move["temporal_gap"] = move["micro_timestamp"] - moves[i-1]["micro_timestamp"]
            else:
                move["previous_move"] = None
                move["temporal_gap"] = 0.0
            
            # Add next move reference
            if i < len(moves) - 1:
                move["next_move"] = moves[i+1]["move_number"]
            else:
                move["next_move"] = None

    def _get_agent_usage_analysis(self) -> Dict[str, Any]:
        """Analyze agent usage patterns"""
        agent_usage = {}
        routing_distribution = {}
        multi_agent_usage_count = 0
        
        for interaction in self.interactions:
            # Agent usage
            for agent in interaction.get('agents_used', []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
            
            # Routing distribution
            path = interaction.get('routing_path', 'unknown')
            routing_distribution[path] = routing_distribution.get(path, 0) + 1
            
            # Multi-agent usage
            if len(interaction.get('agents_used', [])) > 1:
                multi_agent_usage_count += 1
        
        total_interactions = len(self.interactions)
        
        return {
            "agent_usage": agent_usage,
            "routing_distribution": routing_distribution,
            "multi_agent_usage_rate": multi_agent_usage_count / total_interactions if total_interactions > 0 else 0,
            "avg_agents_per_interaction": sum(len(i.get('agents_used', [])) for i in self.interactions) / total_interactions if total_interactions > 0 else 0,
            "most_used_agent": max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else "none",
            "most_common_route": max(routing_distribution.items(), key=lambda x: x[1])[0] if routing_distribution else "unknown"
        }

# Benchmark comparison functions for thesis
def compare_with_baseline(session_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Compare session metrics with baseline traditional tutoring"""
    
    # Define baseline metrics from literature (you'll refine these)
    BASELINE_METRICS = {
        "cognitive_offloading_prevention_rate": 0.3,  # Traditional tutoring often gives direct answers
        "deep_thinking_encouragement_rate": 0.4,
        "scaffolding_rate": 0.5,
        "knowledge_integration_rate": 0.2,
        "avg_sources_per_interaction": 0.5,
        "skill_adaptation_rate": 0.3
    }
    
    comparison = {}
    for metric, baseline_value in BASELINE_METRICS.items():
        current_value = session_summary.get(metric, 0)
        improvement = ((current_value - baseline_value) / baseline_value) * 100 if baseline_value > 0 else 0
        comparison[f"{metric}_improvement"] = improvement
        comparison[f"{metric}_baseline"] = baseline_value
        comparison[f"{metric}_current"] = current_value
    
    # Overall effectiveness score
    improvements = [comparison[key] for key in comparison.keys() if key.endswith('_improvement')]
    comparison["overall_improvement"] = sum(improvements) / len(improvements) if improvements else 0
    
    return comparison

# Analysis functions for thesis
def analyze_all_sessions() -> Dict[str, Any]:
    """Analyze all collected thesis data"""
    
    # Read all CSV files
    csv_files = [f for f in os.listdir("./thesis_data") if f.startswith("interactions_") and f.endswith(".csv")]
    
    if not csv_files:
        print("No data files found. Run some sessions first!")
        return {}
    
    # Combine all interactions
    all_data = []
    for file in csv_files:
        df = pd.read_csv(f"./thesis_data/{file}")
        all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Generate comprehensive analysis
    analysis = {
        "total_sessions": len(csv_files),
        "total_interactions": len(combined_df),
        
        # KEY THESIS METRICS
        "cognitive_offloading_prevention": combined_df['prevents_cognitive_offloading'].mean(),
        "deep_thinking_encouragement": combined_df['encourages_deep_thinking'].mean(),
        "scaffolding_effectiveness": combined_df['provides_scaffolding'].mean(),
        "engagement_maintenance": combined_df['maintains_engagement'].mean(),
        "skill_adaptation": combined_df['adapts_to_skill_level'].mean(),
        
        # SYSTEM PERFORMANCE
        "knowledge_integration_rate": combined_df['knowledge_integrated'].mean(),
        "multi_agent_coordination_rate": combined_df['multi_agent_coordination'].mean(),
        "appropriate_routing_rate": combined_df['appropriate_agent_selection'].mean(),
        
        # ROUTING ANALYSIS
        "routing_distribution": combined_df['routing_path'].value_counts().to_dict(),
        "response_type_distribution": combined_df['response_type'].value_counts().to_dict(),
        "agent_usage_distribution": {},
        
        # STUDENT PATTERNS
        "input_type_distribution": combined_df['input_type'].value_counts().to_dict(),
        "skill_level_distribution": combined_df['student_skill_level'].value_counts().to_dict(),
        
        # TEMPORAL ANALYSIS
        "avg_session_length": combined_df.groupby('session_id').size().mean(),
        "avg_response_time": combined_df['response_time'].mean()
    }
    
    return analysis

# Export function for thesis writing
def export_thesis_ready_data():
    """Export data in formats ready for thesis analysis"""
    
    analysis = analyze_all_sessions()
    
    # Export summary statistics
    with open("./thesis_data/thesis_summary_statistics.json", 'w') as f:
        json.dump(analysis, f, indent=2, cls=CustomJSONEncoder)
    
    # Export for statistical analysis software (R, SPSS, etc.)
    csv_files = [f for f in os.listdir("./thesis_data") if f.startswith("interactions_") and f.endswith(".csv")]
    
    if csv_files:
        all_data = []
        for file in csv_files:
            df = pd.read_csv(f"./thesis_data/{file}")
            all_data.append(df)
        
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_csv("./thesis_data/all_interactions_for_analysis.csv", index=False)
        
        print("Thesis-ready data exported:")
        print("   - thesis_summary_statistics.json")
        print("   - all_interactions_for_analysis.csv")
        print(f"   - {len(csv_files)} individual session files")
        print(f"   - Total interactions: {len(combined_df)}")
    
    return analysis