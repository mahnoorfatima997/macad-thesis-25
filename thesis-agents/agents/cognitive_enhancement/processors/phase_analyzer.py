"""
Phase analysis processing module for design phase-specific cognitive support.
"""
from typing import Dict, Any, List
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class PhaseAnalyzerProcessor:
    """
    Processes phase-specific analysis and recommendations for design phases.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("phase_analyzer")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def get_phase_focus(self, phase: str) -> str:
        """Get the primary focus for a design phase."""
        phase_focuses = {
            "ideation": "Concept generation and exploration",
            "visualization": "Spatial and formal development", 
            "materialization": "Technical resolution and implementation",
            "design_development": "Integrated design refinement",
            "analysis": "Problem understanding and research",
            "synthesis": "Solution integration and refinement",
            "evaluation": "Assessment and iteration"
        }
        return phase_focuses.get(phase, "Design development")
    
    def get_phase_demands(self, phase: str) -> str:
        """Get the cognitive demands for a design phase."""
        phase_demands = {
            "ideation": "Divergent thinking, creativity, research synthesis",
            "visualization": "Spatial reasoning, form exploration, integration",
            "materialization": "Technical analysis, detail resolution, specification",
            "design_development": "Balanced integration of all design aspects",
            "analysis": "Critical thinking, research skills, problem decomposition",
            "synthesis": "Systems thinking, integration, holistic reasoning",
            "evaluation": "Assessment skills, criteria development, judgment"
        }
        return phase_demands.get(phase, "Integrated design thinking")
    
    def get_phase_duration(self, phase: str) -> str:
        """Get expected duration for a design phase."""
        phase_durations = {
            "ideation": "2-4 weeks",
            "visualization": "4-6 weeks",
            "materialization": "6-8 weeks",
            "design_development": "3-5 weeks",
            "analysis": "1-3 weeks",
            "synthesis": "2-4 weeks",
            "evaluation": "1-2 weeks"
        }
        return phase_durations.get(phase, "3-5 weeks")
    
    def get_phase_indicators(self, phase: str) -> List[str]:
        """Get key indicators for a design phase."""
        phase_indicators = {
            "ideation": ["Research depth", "Concept variety", "Problem understanding", "Creative exploration"],
            "visualization": ["Spatial clarity", "Form development", "Design integration", "Visual communication"],
            "materialization": ["Technical accuracy", "Detail resolution", "Specification quality", "Constructability"],
            "design_development": ["Design coherence", "System integration", "Resolution quality", "Refinement"],
            "analysis": ["Research quality", "Problem clarity", "Context understanding", "Requirements definition"],
            "synthesis": ["Solution integration", "System coherence", "Holistic thinking", "Creative synthesis"],
            "evaluation": ["Assessment criteria", "Critical judgment", "Iteration quality", "Decision making"]
        }
        return phase_indicators.get(phase, ["Design progress", "Problem solving", "Creative development"])
    
    def get_engagement_recommendation(self, score: float) -> str:
        """Get engagement improvement recommendation."""
        if score < 0.4:
            return "Try asking more questions and exploring topics that intrigue you."
        elif score < 0.7:
            return "Consider diving deeper into aspects that spark your curiosity."
        else:
            return "Maintain your high level of engagement and continue exploring."
    
    def get_complexity_recommendation(self, score: float) -> str:
        """Get complexity engagement recommendation."""
        if score < 0.4:
            return "Challenge yourself with 'what if' scenarios and alternative approaches."
        elif score < 0.7:
            return "Explore more complex relationships and system interactions."
        else:
            return "Continue engaging with complex design challenges effectively."
    
    def get_reflection_recommendation(self, score: float) -> str:
        """Get reflection improvement recommendation."""
        if score < 0.4:
            return "Pause regularly to consider your design decisions and reasoning."
        elif score < 0.7:
            return "Develop deeper awareness of your design thinking process."
        else:
            return "Maintain your strong reflective practice and metacognitive awareness."
    
    def analyze_phase_alignment(self, current_phase: str, cognitive_state: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze alignment between cognitive state and phase requirements."""
        self.telemetry.log_agent_start("analyze_phase_alignment")
        
        try:
            phase_requirements = self._get_phase_requirements(current_phase)
            cognitive_capabilities = self._assess_cognitive_capabilities(cognitive_state, state)
            
            # Calculate alignment scores
            alignment_scores = {}
            for requirement, importance in phase_requirements.items():
                capability = cognitive_capabilities.get(requirement, 0.5)
                alignment_scores[requirement] = capability * importance
            
            overall_alignment = sum(alignment_scores.values()) / len(alignment_scores)
            
            # Generate recommendations
            recommendations = self._generate_phase_recommendations(current_phase, alignment_scores, cognitive_state)
            
            # Identify gaps and strengths
            gaps = {req: score for req, score in alignment_scores.items() if score < 0.5}
            strengths = {req: score for req, score in alignment_scores.items() if score > 0.7}
            
            return {
                "phase": current_phase,
                "overall_alignment": overall_alignment,
                "alignment_scores": alignment_scores,
                "phase_requirements": phase_requirements,
                "cognitive_capabilities": cognitive_capabilities,
                "recommendations": recommendations,
                "identified_gaps": gaps,
                "identified_strengths": strengths,
                "analysis_timestamp": self.telemetry.get_timestamp()
            }
            
        except Exception as e:
            self.telemetry.log_error("analyze_phase_alignment", str(e))
            return self._get_fallback_phase_alignment(current_phase)
    
    def generate_phase_specific_challenges(self, phase: str, cognitive_state: Dict, alignment_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate phase-specific cognitive challenges."""
        self.telemetry.log_agent_start("generate_phase_specific_challenges")
        
        try:
            challenges = []
            gaps = alignment_analysis.get("identified_gaps", {})
            
            # Generate challenges based on phase and gaps
            if phase == "ideation":
                challenges.extend(self._generate_ideation_challenges(gaps, cognitive_state))
            elif phase == "visualization":
                challenges.extend(self._generate_visualization_challenges(gaps, cognitive_state))
            elif phase == "materialization":
                challenges.extend(self._generate_materialization_challenges(gaps, cognitive_state))
            else:
                challenges.extend(self._generate_general_phase_challenges(phase, gaps, cognitive_state))
            
            # Add phase-specific metadata
            for challenge in challenges:
                challenge.update({
                    "target_phase": phase,
                    "phase_specific": True,
                    "generation_method": "phase_aligned"
                })
            
            return challenges
            
        except Exception as e:
            self.telemetry.log_error("generate_phase_specific_challenges", str(e))
            return self._get_fallback_challenges(phase)
    
    def assess_phase_transition_readiness(self, current_phase: str, next_phase: str, cognitive_state: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Assess readiness to transition to the next design phase."""
        self.telemetry.log_agent_start("assess_phase_transition_readiness")
        
        try:
            # Current phase completion assessment
            current_completion = self._assess_phase_completion(current_phase, cognitive_state, state)
            
            # Next phase readiness assessment
            next_phase_readiness = self._assess_next_phase_readiness(next_phase, cognitive_state, state)
            
            # Transition barriers
            barriers = self._identify_transition_barriers(current_phase, next_phase, cognitive_state)
            
            # Overall readiness score
            readiness_score = (current_completion + next_phase_readiness) / 2
            
            # Recommendations for transition
            transition_recommendations = self._generate_transition_recommendations(
                current_phase, next_phase, readiness_score, barriers
            )
            
            return {
                "current_phase": current_phase,
                "next_phase": next_phase,
                "readiness_score": readiness_score,
                "current_completion": current_completion,
                "next_phase_readiness": next_phase_readiness,
                "transition_barriers": barriers,
                "recommendations": transition_recommendations,
                "transition_advised": readiness_score > 0.6,
                "assessment_timestamp": self.telemetry.get_timestamp()
            }
            
        except Exception as e:
            self.telemetry.log_error("assess_phase_transition_readiness", str(e))
            return self._get_fallback_transition_assessment(current_phase, next_phase)
    
    def _get_phase_requirements(self, phase: str) -> Dict[str, float]:
        """Get cognitive requirements for a specific phase with importance weights."""
        requirements = {
            "ideation": {
                "creativity": 0.9,
                "research_skills": 0.8,
                "divergent_thinking": 0.9,
                "curiosity": 0.8,
                "openness": 0.7
            },
            "visualization": {
                "spatial_reasoning": 0.9,
                "integration_skills": 0.8,
                "visual_thinking": 0.9,
                "iteration_comfort": 0.7,
                "form_sensitivity": 0.8
            },
            "materialization": {
                "technical_thinking": 0.9,
                "detail_orientation": 0.9,
                "systematic_approach": 0.8,
                "precision": 0.8,
                "implementation_focus": 0.7
            },
            "design_development": {
                "integration_skills": 0.9,
                "balance_thinking": 0.8,
                "refinement_skills": 0.8,
                "holistic_view": 0.7,
                "iteration_comfort": 0.7
            }
        }
        
        return requirements.get(phase, {
            "general_thinking": 0.8,
            "problem_solving": 0.8,
            "creativity": 0.7,
            "reflection": 0.7
        })
    
    def _assess_cognitive_capabilities(self, cognitive_state: Dict, state: ArchMentorState) -> Dict[str, float]:
        """Assess current cognitive capabilities."""
        # Map cognitive state to capabilities
        engagement = cognitive_state.get("engagement_level", "moderate")
        metacognitive = cognitive_state.get("metacognitive_awareness", "moderate")
        complexity_handling = cognitive_state.get("cognitive_load", "optimal")
        
        # Simple mapping (could be more sophisticated)
        capabilities = {
            "creativity": 0.8 if engagement == "high" else 0.5,
            "research_skills": 0.7 if metacognitive == "high" else 0.5,
            "divergent_thinking": 0.8 if engagement == "high" else 0.5,
            "spatial_reasoning": 0.6,  # Would need specific assessment
            "integration_skills": 0.7 if metacognitive == "high" else 0.5,
            "technical_thinking": 0.6,  # Would need specific assessment
            "detail_orientation": 0.7 if complexity_handling == "optimal" else 0.5,
            "systematic_approach": 0.7 if metacognitive == "high" else 0.5,
            "holistic_view": 0.6 if metacognitive == "high" else 0.4,
            "iteration_comfort": 0.7 if engagement == "high" else 0.5
        }
        
        return capabilities
    
    def _generate_phase_recommendations(self, phase: str, alignment_scores: Dict, cognitive_state: Dict) -> List[str]:
        """Generate phase-specific recommendations."""
        recommendations = []
        
        # Phase-specific base recommendations
        phase_recs = {
            "ideation": [
                "Explore multiple conceptual approaches",
                "Research relevant precedents and case studies",
                "Question assumptions about the problem"
            ],
            "visualization": [
                "Develop spatial relationships systematically",
                "Create multiple design iterations",
                "Focus on form and space integration"
            ],
            "materialization": [
                "Develop technical details methodically",
                "Consider constructability and feasibility",
                "Specify materials and systems precisely"
            ]
        }
        
        recommendations.extend(phase_recs.get(phase, ["Continue developing your design approach"]))
        
        # Add gap-specific recommendations
        for requirement, score in alignment_scores.items():
            if score < 0.5:
                if requirement == "creativity":
                    recommendations.append("Try brainstorming alternative approaches")
                elif requirement == "technical_thinking":
                    recommendations.append("Focus on technical feasibility and details")
                elif requirement == "integration_skills":
                    recommendations.append("Work on connecting different design aspects")
        
        return recommendations[:5]  # Limit to top 5
    
    def _generate_ideation_challenges(self, gaps: Dict, cognitive_state: Dict) -> List[Dict[str, Any]]:
        """Generate challenges specific to ideation phase."""
        challenges = []
        
        if "creativity" in gaps:
            challenges.append({
                "challenge_text": "Generate 5 completely different approaches to solving this design problem.",
                "cognitive_target": "creativity",
                "difficulty": "medium"
            })
        
        if "research_skills" in gaps:
            challenges.append({
                "challenge_text": "Find 3 precedent projects that address similar challenges and analyze their approaches.",
                "cognitive_target": "research_skills",
                "difficulty": "medium"
            })
        
        if "divergent_thinking" in gaps:
            challenges.append({
                "challenge_text": "What would this project look like if it were designed for a completely different context?",
                "cognitive_target": "divergent_thinking",
                "difficulty": "high"
            })
        
        return challenges
    
    def _generate_visualization_challenges(self, gaps: Dict, cognitive_state: Dict) -> List[Dict[str, Any]]:
        """Generate challenges specific to visualization phase."""
        challenges = []
        
        if "spatial_reasoning" in gaps:
            challenges.append({
                "challenge_text": "Describe how someone would move through your spaces and what they would experience.",
                "cognitive_target": "spatial_reasoning",
                "difficulty": "medium"
            })
        
        if "integration_skills" in gaps:
            challenges.append({
                "challenge_text": "How do the different parts of your design work together as a unified whole?",
                "cognitive_target": "integration_skills",
                "difficulty": "medium"
            })
        
        return challenges
    
    def _generate_materialization_challenges(self, gaps: Dict, cognitive_state: Dict) -> List[Dict[str, Any]]:
        """Generate challenges specific to materialization phase."""
        challenges = []
        
        if "technical_thinking" in gaps:
            challenges.append({
                "challenge_text": "Explain how your design would actually be constructed, step by step.",
                "cognitive_target": "technical_thinking",
                "difficulty": "high"
            })
        
        if "detail_orientation" in gaps:
            challenges.append({
                "challenge_text": "Identify 5 specific technical details that need to be resolved for your design to work.",
                "cognitive_target": "detail_orientation",
                "difficulty": "medium"
            })
        
        return challenges
    
    def _generate_general_phase_challenges(self, phase: str, gaps: Dict, cognitive_state: Dict) -> List[Dict[str, Any]]:
        """Generate general challenges for any phase."""
        return [{
            "challenge_text": f"What is the most important aspect to focus on in the {phase} phase of your project?",
            "cognitive_target": "phase_awareness",
            "difficulty": "medium"
        }]
    
    def _assess_phase_completion(self, phase: str, cognitive_state: Dict, state: ArchMentorState) -> float:
        """Assess how complete the current phase is."""
        # Simple assessment based on conversation depth and engagement
        message_count = len(state.messages) if hasattr(state, 'messages') else 0
        engagement = cognitive_state.get("engagement_level", "moderate")
        
        base_completion = min(message_count / 15.0, 1.0)
        
        if engagement == "high":
            base_completion *= 1.2
        elif engagement == "low":
            base_completion *= 0.8
        
        return min(base_completion, 1.0)
    
    def _assess_next_phase_readiness(self, next_phase: str, cognitive_state: Dict, state: ArchMentorState) -> float:
        """Assess readiness for the next phase."""
        # Simple readiness assessment
        metacognitive = cognitive_state.get("metacognitive_awareness", "moderate")
        complexity_handling = cognitive_state.get("cognitive_load", "optimal")
        
        readiness = 0.5
        
        if metacognitive == "high":
            readiness += 0.2
        if complexity_handling == "optimal":
            readiness += 0.2
        
        return min(readiness, 1.0)
    
    def _identify_transition_barriers(self, current_phase: str, next_phase: str, cognitive_state: Dict) -> List[str]:
        """Identify barriers to phase transition."""
        barriers = []
        
        if cognitive_state.get("cognitive_load") == "overload":
            barriers.append("High cognitive load may impede transition")
        
        if cognitive_state.get("engagement_level") == "low":
            barriers.append("Low engagement may affect phase transition readiness")
        
        if cognitive_state.get("metacognitive_awareness") == "low":
            barriers.append("Limited self-awareness may hinder phase progression")
        
        return barriers
    
    def _generate_transition_recommendations(self, current_phase: str, next_phase: str, readiness_score: float, barriers: List[str]) -> List[str]:
        """Generate recommendations for phase transition."""
        recommendations = []
        
        if readiness_score < 0.4:
            recommendations.append(f"Focus on completing {current_phase} phase before transitioning")
            recommendations.append("Build confidence and competence in current phase activities")
        elif readiness_score < 0.6:
            recommendations.append(f"Consider gradual transition to {next_phase} phase")
            recommendations.append("Address identified barriers before full transition")
        else:
            recommendations.append(f"Ready to transition to {next_phase} phase")
            recommendations.append(f"Begin preparing for {next_phase} phase requirements")
        
        # Address specific barriers
        for barrier in barriers:
            if "cognitive load" in barrier:
                recommendations.append("Reduce complexity or provide additional support")
            elif "engagement" in barrier:
                recommendations.append("Increase engagement through more interesting challenges")
        
        return recommendations
    
    def _get_fallback_phase_alignment(self, phase: str) -> Dict[str, Any]:
        """Return fallback phase alignment analysis."""
        return {
            "phase": phase,
            "overall_alignment": 0.6,
            "alignment_scores": {"general_capability": 0.6},
            "recommendations": [f"Continue developing {phase} phase skills"],
            "identified_gaps": {},
            "identified_strengths": {"general_capability": 0.6},
            "analysis_timestamp": self.telemetry.get_timestamp()
        }
    
    def _get_fallback_challenges(self, phase: str) -> List[Dict[str, Any]]:
        """Return fallback challenges for a phase."""
        return [{
            "challenge_text": f"Continue exploring the key aspects of {phase} phase.",
            "cognitive_target": "phase_engagement",
            "difficulty": "medium",
            "target_phase": phase,
            "phase_specific": True
        }]
    
    def _get_fallback_transition_assessment(self, current_phase: str, next_phase: str) -> Dict[str, Any]:
        """Return fallback transition assessment."""
        return {
            "current_phase": current_phase,
            "next_phase": next_phase,
            "readiness_score": 0.5,
            "current_completion": 0.5,
            "next_phase_readiness": 0.5,
            "transition_barriers": [],
            "recommendations": ["Continue current phase development"],
            "transition_advised": False,
            "assessment_timestamp": self.telemetry.get_timestamp()
        } 