"""
Scientific metrics processing module for thesis research measurements.
"""
from typing import Dict, Any, List, Tuple
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class ScientificMetricsProcessor:
    """
    Processes scientific metrics calculation and validation for thesis research.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("scientific_metrics")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def calculate_scientific_metrics(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive scientific metrics for thesis research.
        """
        self.telemetry.log_agent_start("calculate_scientific_metrics")
        
        try:
            # Calculate individual metric categories
            engagement_metrics = self._calculate_engagement_metrics(cognitive_state, state)
            complexity_metrics = self._calculate_complexity_metrics(state, analysis_result)
            reflection_metrics = self._calculate_reflection_metrics(state, cognitive_state)
            progression_metrics = self._calculate_progression_metrics(state, analysis_result)
            
            # Calculate composite metrics
            improvement_score = self._calculate_improvement_over_baseline(
                engagement_metrics, complexity_metrics, reflection_metrics, progression_metrics
            )
            
            overall_cognitive_score = self._calculate_overall_cognitive_score(
                engagement_metrics, complexity_metrics, reflection_metrics, progression_metrics
            )
            
            # Phase-specific metrics
            current_phase = analysis_result.get("current_phase", "design_development")
            phase_metrics = self._calculate_phase_specific_metrics(current_phase, cognitive_state, state)
            
            # Calculate scientific confidence
            scientific_confidence = self._calculate_scientific_confidence(
                phase_metrics.get("phase_alignment_score", 0.7), cognitive_state, state
            )
            
            # Additional specialized metrics
            offloading_prevention = self._calculate_cognitive_offloading_prevention(cognitive_state, state)
            scaffolding_effectiveness = self._calculate_scaffolding_effectiveness(cognitive_state, analysis_result)
            knowledge_integration = self._calculate_knowledge_integration(state, analysis_result)
            
            return {
                "engagement_metrics": engagement_metrics,
                "complexity_metrics": complexity_metrics,
                "reflection_metrics": reflection_metrics,
                "progression_metrics": progression_metrics,
                "improvement_over_baseline": improvement_score,
                "overall_cognitive_score": overall_cognitive_score,
                "phase_specific_metrics": phase_metrics,
                "scientific_confidence": scientific_confidence,
                "cognitive_offloading_prevention": offloading_prevention,
                "scaffolding_effectiveness": scaffolding_effectiveness,
                "knowledge_integration": knowledge_integration,
                "calculation_timestamp": self.telemetry.get_timestamp()
            }
            
        except Exception as e:
            self.telemetry.log_error("calculate_scientific_metrics", str(e))
            return self._get_fallback_metrics()
    
    def _calculate_engagement_metrics(self, cognitive_state: Dict, state: ArchMentorState) -> Dict[str, float]:
        """Calculate detailed engagement metrics."""
        try:
            base_score = 0.7 if cognitive_state.get("engagement_level") == "high" else 0.5
            
            # Message frequency analysis
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            interaction_frequency = min(message_count / 10.0, 1.0)
            
            # Question quality analysis
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            question_indicators = ["why", "how", "what if", "could", "might", "would"]
            question_quality = 0.5
            
            if user_messages:
                recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
                question_count = sum(
                    1 for msg in recent_messages
                    for indicator in question_indicators
                    if indicator.lower() in msg.lower()
                )
                question_quality = min(question_count / 3.0, 1.0)
            
            # Exploration depth analysis
            exploration_depth = base_score * 0.9  # Simplified
            
            return {
                "overall_score": base_score,
                "interaction_frequency": interaction_frequency,
                "question_quality": question_quality,
                "exploration_depth": exploration_depth,
                "engagement_consistency": self._calculate_engagement_consistency(user_messages)
            }
            
        except Exception as e:
            self.telemetry.log_error("_calculate_engagement_metrics", str(e))
            return {"overall_score": 0.5, "interaction_frequency": 0.5, "question_quality": 0.5, "exploration_depth": 0.5}
    
    def _calculate_complexity_metrics(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, float]:
        """Calculate detailed complexity metrics."""
        try:
            # Message complexity assessment
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            complexity_score = min(message_count / 15.0, 1.0)
            
            # Problem complexity from analysis
            problem_complexity = analysis_result.get("complexity_score", 0.5)
            
            # Solution sophistication
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            solution_sophistication = 0.5
            
            if user_messages:
                # Assess vocabulary sophistication
                sophisticated_terms = [
                    "integration", "synthesis", "relationship", "system", "context",
                    "implications", "consequences", "alternatives", "optimization"
                ]
                recent_text = " ".join(user_messages[-3:]).lower()
                sophistication_count = sum(1 for term in sophisticated_terms if term in recent_text)
                solution_sophistication = min(sophistication_count / 5.0, 1.0)
            
            # Integration level
            integration_level = complexity_score * 1.1  # Slightly higher weight
            
            return {
                "overall_score": complexity_score,
                "problem_complexity": problem_complexity,
                "solution_sophistication": solution_sophistication,
                "integration_level": min(integration_level, 1.0),
                "complexity_progression": self._calculate_complexity_progression(user_messages)
            }
            
        except Exception as e:
            self.telemetry.log_error("_calculate_complexity_metrics", str(e))
            return {"overall_score": 0.5, "problem_complexity": 0.5, "solution_sophistication": 0.5, "integration_level": 0.5}
    
    def _calculate_reflection_metrics(self, state: ArchMentorState, cognitive_state: Dict) -> Dict[str, float]:
        """Calculate detailed reflection metrics."""
        try:
            base_score = 0.8 if cognitive_state.get("metacognitive_awareness") == "high" else 0.5
            
            # Self-assessment indicators
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            self_assessment_indicators = [
                "i think", "i believe", "i realize", "i notice", "i understand",
                "i'm not sure", "i wonder", "it seems", "i feel"
            ]
            
            self_assessment = 0.5
            if user_messages:
                recent_text = " ".join(user_messages[-3:]).lower()
                assessment_count = sum(1 for indicator in self_assessment_indicators if indicator in recent_text)
                self_assessment = min(assessment_count / 3.0, 1.0)
            
            # Process awareness
            process_awareness = base_score
            
            # Decision justification
            justification_indicators = [
                "because", "since", "therefore", "thus", "as a result",
                "due to", "given that", "considering", "based on"
            ]
            
            decision_justification = 0.5
            if user_messages:
                recent_text = " ".join(user_messages[-3:]).lower()
                justification_count = sum(1 for indicator in justification_indicators if indicator in recent_text)
                decision_justification = min(justification_count / 2.0, 1.0)
            
            return {
                "overall_score": base_score,
                "self_assessment": self_assessment,
                "process_awareness": process_awareness,
                "decision_justification": decision_justification,
                "reflection_depth": self._calculate_reflection_depth(user_messages)
            }
            
        except Exception as e:
            self.telemetry.log_error("_calculate_reflection_metrics", str(e))
            return {"overall_score": 0.5, "self_assessment": 0.5, "process_awareness": 0.5, "decision_justification": 0.5}
    
    def _calculate_progression_metrics(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, float]:
        """Calculate detailed progression metrics."""
        try:
            # Simple progression assessment based on conversation length
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            progression_score = min(message_count / 20.0, 1.0)
            
            # Skill development indicators
            skill_development = progression_score
            
            # Knowledge acquisition
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            knowledge_indicators = [
                "learned", "discovered", "understand now", "makes sense",
                "i see", "ah", "interesting", "didn't know"
            ]
            
            knowledge_acquisition = 0.5
            if user_messages:
                recent_text = " ".join(user_messages).lower()
                knowledge_count = sum(1 for indicator in knowledge_indicators if indicator in recent_text)
                knowledge_acquisition = min(knowledge_count / 5.0, 1.0)
            
            # Competency growth
            competency_growth = progression_score * 1.1
            
            return {
                "overall_score": progression_score,
                "skill_development": skill_development,
                "knowledge_acquisition": knowledge_acquisition,
                "competency_growth": min(competency_growth, 1.0),
                "learning_velocity": self._calculate_learning_velocity(user_messages)
            }
            
        except Exception as e:
            self.telemetry.log_error("_calculate_progression_metrics", str(e))
            return {"overall_score": 0.5, "skill_development": 0.5, "knowledge_acquisition": 0.5, "competency_growth": 0.5}
    
    def _calculate_improvement_over_baseline(self, engagement_metrics: Dict, complexity_metrics: Dict, 
                                           reflection_metrics: Dict, progression_metrics: Dict) -> float:
        """Calculate improvement over baseline performance."""
        try:
            all_scores = []
            
            for metrics in [engagement_metrics, complexity_metrics, reflection_metrics, progression_metrics]:
                if isinstance(metrics, dict) and "overall_score" in metrics:
                    all_scores.append(metrics["overall_score"])
            
            if not all_scores:
                return 0.5
            
            # Weighted average with emphasis on progression
            weights = [0.25, 0.25, 0.25, 0.25]  # Equal weights for now
            weighted_score = sum(score * weight for score, weight in zip(all_scores, weights))
            
            return min(weighted_score, 1.0)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_improvement_over_baseline", str(e))
            return 0.5
    
    def _calculate_phase_specific_metrics(self, current_phase: str, cognitive_state: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Calculate phase-specific cognitive metrics."""
        try:
            phase_characteristics = {
                "ideation": {
                    "focus": "Concept generation and exploration",
                    "demands": "Divergent thinking, creativity, research synthesis",
                    "duration": "2-4 weeks",
                    "indicators": ["Research depth", "Concept variety", "Problem understanding"]
                },
                "visualization": {
                    "focus": "Spatial and formal development",
                    "demands": "Spatial reasoning, form exploration, integration",
                    "duration": "4-6 weeks",
                    "indicators": ["Spatial clarity", "Form development", "Design integration"]
                },
                "materialization": {
                    "focus": "Technical resolution and implementation",
                    "demands": "Technical analysis, detail resolution, specification",
                    "duration": "6-8 weeks",
                    "indicators": ["Technical accuracy", "Detail resolution", "Specification quality"]
                },
                "design_development": {
                    "focus": "Integrated design refinement",
                    "demands": "Balanced integration of all design aspects",
                    "duration": "3-5 weeks",
                    "indicators": ["Design coherence", "System integration", "Resolution quality"]
                }
            }
            
            phase_info = phase_characteristics.get(current_phase, phase_characteristics["design_development"])
            
            # Calculate phase alignment score
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            phase_alignment_score = min(message_count / 10.0, 1.0) * 0.7  # Simplified
            
            return {
                "phase": current_phase,
                "focus": phase_info["focus"],
                "demands": phase_info["demands"],
                "expected_duration": phase_info["duration"],
                "key_indicators": phase_info["indicators"],
                "phase_alignment_score": phase_alignment_score,
                "phase_appropriateness": self._assess_phase_appropriateness(current_phase, cognitive_state)
            }
            
        except Exception as e:
            self.telemetry.log_error("_calculate_phase_specific_metrics", str(e))
            return {
                "phase": current_phase,
                "phase_alignment_score": 0.5,
                "phase_appropriateness": "moderate"
            }
    
    def _calculate_overall_cognitive_score(self, engagement_metrics: Dict, complexity_metrics: Dict,
                                         reflection_metrics: Dict, progression_metrics: Dict) -> float:
        """Calculate overall cognitive development score."""
        try:
            scores = []
            
            for metrics in [engagement_metrics, complexity_metrics, reflection_metrics, progression_metrics]:
                if isinstance(metrics, dict) and "overall_score" in metrics:
                    scores.append(metrics["overall_score"])
            
            if not scores:
                return 0.5
            
            # Weighted average with higher weight on reflection and progression
            weights = [0.2, 0.25, 0.3, 0.25]  # Emphasis on reflection
            if len(scores) == len(weights):
                weighted_score = sum(score * weight for score, weight in zip(scores, weights))
            else:
                weighted_score = sum(scores) / len(scores)
            
            return min(weighted_score, 1.0)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_overall_cognitive_score", str(e))
            return 0.5
    
    def _calculate_scientific_confidence(self, phase_confidence: float, cognitive_state: Dict, state: ArchMentorState) -> float:
        """Calculate confidence in scientific measurements."""
        try:
            confidence_factors = []
            
            # Data richness
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            data_richness = min(message_count / 10.0, 1.0)
            confidence_factors.append(data_richness)
            
            # Assessment consistency
            assessment_confidence = cognitive_state.get("assessment_confidence", 0.5)
            confidence_factors.append(assessment_confidence)
            
            # Phase confidence
            confidence_factors.append(phase_confidence)
            
            # Measurement reliability (simplified)
            confidence_factors.append(0.7)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_scientific_confidence", str(e))
            return 0.5
    
    def _calculate_cognitive_offloading_prevention(self, cognitive_state: Dict, state: ArchMentorState) -> float:
        """Calculate cognitive offloading prevention score."""
        try:
            # Simple calculation based on engagement and metacognitive awareness
            engagement_score = 0.7 if cognitive_state.get("engagement_level") == "high" else 0.5
            metacognitive_score = 0.8 if cognitive_state.get("metacognitive_awareness") == "high" else 0.5
            
            # Independence indicators
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            independence_indicators = [
                "i will", "i think", "my approach", "i plan", "i want to try",
                "let me", "i could", "i would", "my idea"
            ]
            
            independence_score = 0.5
            if user_messages:
                recent_text = " ".join(user_messages[-3:]).lower()
                independence_count = sum(1 for indicator in independence_indicators if indicator in recent_text)
                independence_score = min(independence_count / 3.0, 1.0)
            
            return (engagement_score + metacognitive_score + independence_score) / 3
            
        except Exception as e:
            self.telemetry.log_error("_calculate_cognitive_offloading_prevention", str(e))
            return 0.5
    
    def _calculate_scaffolding_effectiveness(self, cognitive_state: Dict, analysis_result: Dict) -> float:
        """Calculate scaffolding effectiveness score."""
        try:
            # Simple calculation based on cognitive load and learning progression
            cognitive_load = cognitive_state.get("cognitive_load", "optimal")
            learning_progression = cognitive_state.get("learning_progression", "stable")
            
            load_score = {
                "optimal": 0.9,
                "underload": 0.6,
                "overload": 0.4
            }.get(cognitive_load, 0.5)
            
            progression_score = {
                "progressing": 0.9,
                "stable": 0.7,
                "regressing": 0.3
            }.get(learning_progression, 0.5)
            
            return (load_score + progression_score) / 2
            
        except Exception as e:
            self.telemetry.log_error("_calculate_scaffolding_effectiveness", str(e))
            return 0.5
    
    def _calculate_knowledge_integration(self, state: ArchMentorState, analysis_result: Dict) -> float:
        """Calculate knowledge integration score."""
        try:
            # Simple calculation based on conversation depth and complexity
            conversation_depth = len(state.messages) if hasattr(state, 'messages') else 0
            depth_score = min(conversation_depth / 10.0, 1.0)
            
            # Integration indicators in user messages
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            integration_indicators = [
                "connects to", "relates to", "builds on", "combines", "integrates",
                "brings together", "synthesizes", "links", "ties together"
            ]
            
            integration_score = 0.5
            if user_messages:
                recent_text = " ".join(user_messages).lower()
                integration_count = sum(1 for indicator in integration_indicators if indicator in recent_text)
                integration_score = min(integration_count / 3.0, 1.0)
            
            return (depth_score + integration_score) / 2
            
        except Exception as e:
            self.telemetry.log_error("_calculate_knowledge_integration", str(e))
            return 0.5
    
    def validate_thesis_metrics(self, scientific_metrics: Dict) -> Dict[str, Any]:
        """Validate scientific metrics for thesis research."""
        try:
            validation_result = {
                "valid": True,
                "issues": [],
                "recommendations": [],
                "quality_score": 0.0
            }
            
            # Check required metrics
            required_metrics = [
                "engagement_metrics", "complexity_metrics", "reflection_metrics",
                "progression_metrics", "overall_cognitive_score", "scientific_confidence"
            ]
            
            missing_metrics = []
            for metric in required_metrics:
                if metric not in scientific_metrics:
                    missing_metrics.append(metric)
                    validation_result["valid"] = False
            
            if missing_metrics:
                validation_result["issues"].append(f"Missing metrics: {', '.join(missing_metrics)}")
                validation_result["recommendations"].append("Ensure all required metrics are calculated")
            
            # Check metric ranges
            range_issues = []
            for metric_name, metric_data in scientific_metrics.items():
                if isinstance(metric_data, dict):
                    for sub_metric, value in metric_data.items():
                        if isinstance(value, (int, float)) and not 0 <= value <= 1:
                            range_issues.append(f"{metric_name}.{sub_metric}: {value}")
                elif isinstance(metric_data, (int, float)) and not 0 <= metric_data <= 1:
                    range_issues.append(f"{metric_name}: {metric_data}")
            
            if range_issues:
                validation_result["valid"] = False
                validation_result["issues"].extend([f"Value out of range: {issue}" for issue in range_issues])
                validation_result["recommendations"].append("Ensure all metric values are between 0 and 1")
            
            # Calculate quality score
            if validation_result["valid"]:
                validation_result["quality_score"] = self._calculate_metrics_quality_score(scientific_metrics)
            
            return validation_result
            
        except Exception as e:
            self.telemetry.log_error("validate_thesis_metrics", str(e))
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "recommendations": ["Review metrics calculation process"],
                "quality_score": 0.0
            }
    
    # Helper methods for detailed calculations
    
    def _calculate_engagement_consistency(self, user_messages: List[str]) -> float:
        """Calculate consistency of engagement over time."""
        if len(user_messages) < 3:
            return 0.5
        
        # Simple consistency measure based on message length variation
        message_lengths = [len(msg.split()) for msg in user_messages[-5:]]
        if not message_lengths:
            return 0.5
        
        avg_length = sum(message_lengths) / len(message_lengths)
        variance = sum((length - avg_length) ** 2 for length in message_lengths) / len(message_lengths)
        consistency = max(0, 1 - (variance / max(avg_length, 1)))
        
        return min(consistency, 1.0)
    
    def _calculate_complexity_progression(self, user_messages: List[str]) -> float:
        """Calculate progression in complexity handling."""
        if len(user_messages) < 2:
            return 0.5
        
        # Compare early vs recent message complexity
        early_messages = user_messages[:2]
        recent_messages = user_messages[-2:]
        
        early_complexity = sum(len(msg.split()) for msg in early_messages) / len(early_messages)
        recent_complexity = sum(len(msg.split()) for msg in recent_messages) / len(recent_messages)
        
        if early_complexity == 0:
            return 0.5
        
        progression = recent_complexity / early_complexity
        return min(progression / 2.0, 1.0)  # Normalize
    
    def _calculate_reflection_depth(self, user_messages: List[str]) -> float:
        """Calculate depth of reflective thinking."""
        if not user_messages:
            return 0.5
        
        depth_indicators = [
            "because", "therefore", "however", "although", "considering",
            "implications", "consequences", "reflects", "suggests", "indicates"
        ]
        
        recent_text = " ".join(user_messages[-3:]).lower()
        depth_count = sum(1 for indicator in depth_indicators if indicator in recent_text)
        
        return min(depth_count / 3.0, 1.0)
    
    def _calculate_learning_velocity(self, user_messages: List[str]) -> float:
        """Calculate velocity of learning progression."""
        if len(user_messages) < 3:
            return 0.5
        
        # Simple velocity based on increasing sophistication
        sophistication_scores = []
        for msg in user_messages[-5:]:
            sophisticated_terms = [
                "relationship", "system", "integration", "synthesis", "optimization",
                "implications", "consequences", "alternatives", "complexity"
            ]
            score = sum(1 for term in sophisticated_terms if term.lower() in msg.lower())
            sophistication_scores.append(score)
        
        if len(sophistication_scores) < 2:
            return 0.5
        
        # Calculate trend
        early_avg = sum(sophistication_scores[:2]) / 2
        recent_avg = sum(sophistication_scores[-2:]) / 2
        
        if early_avg == 0:
            return min(recent_avg / 3.0, 1.0)
        
        velocity = recent_avg / early_avg
        return min(velocity / 2.0, 1.0)
    
    def _assess_phase_appropriateness(self, current_phase: str, cognitive_state: Dict) -> str:
        """Assess if cognitive state is appropriate for current phase."""
        engagement = cognitive_state.get("engagement_level", "moderate")
        complexity = cognitive_state.get("cognitive_load", "optimal")
        
        if engagement == "high" and complexity == "optimal":
            return "highly_appropriate"
        elif engagement in ["moderate", "high"] and complexity in ["optimal", "underload"]:
            return "appropriate"
        elif engagement == "low" or complexity == "overload":
            return "needs_adjustment"
        else:
            return "moderate"
    
    def _calculate_metrics_quality_score(self, scientific_metrics: Dict) -> float:
        """Calculate overall quality score for metrics."""
        quality_factors = []
        
        # Completeness
        expected_metrics = ["engagement_metrics", "complexity_metrics", "reflection_metrics", "progression_metrics"]
        completeness = sum(1 for metric in expected_metrics if metric in scientific_metrics) / len(expected_metrics)
        quality_factors.append(completeness)
        
        # Consistency (simplified)
        consistency = 0.8  # Placeholder
        quality_factors.append(consistency)
        
        # Confidence
        confidence = scientific_metrics.get("scientific_confidence", 0.5)
        quality_factors.append(confidence)
        
        return sum(quality_factors) / len(quality_factors)
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Return fallback metrics when calculation fails."""
        return {
            "engagement_metrics": {"overall_score": 0.5},
            "complexity_metrics": {"overall_score": 0.5},
            "reflection_metrics": {"overall_score": 0.5},
            "progression_metrics": {"overall_score": 0.5},
            "improvement_over_baseline": 0.5,
            "overall_cognitive_score": 0.5,
            "phase_specific_metrics": {"phase_alignment_score": 0.5},
            "scientific_confidence": 0.4,
            "cognitive_offloading_prevention": 0.5,
            "scaffolding_effectiveness": 0.5,
            "knowledge_integration": 0.5,
            "calculation_timestamp": self.telemetry.get_timestamp(),
            "fallback": True
        } 