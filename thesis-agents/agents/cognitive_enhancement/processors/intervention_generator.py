"""
Intervention generation processing module for cognitive offloading detection and intervention.
"""
from typing import Dict, Any, List
from ..config import OFFLOADING_PATTERNS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class InterventionGeneratorProcessor:
    """
    Processes cognitive intervention generation and offloading detection.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("intervention_generator")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def detect_cognitive_offloading_patterns(self, context_classification: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """
        Detect cognitive offloading patterns in student behavior.
        """
        self.telemetry.log_agent_start("detect_cognitive_offloading_patterns")
        
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return {"detected": False}
            
            recent_message = user_messages[-1].lower()
            
            # Check for offloading patterns
            for pattern_name, pattern_config in OFFLOADING_PATTERNS.items():
                for indicator in pattern_config["indicators"]:
                    if indicator in recent_message:
                        return {
                            "detected": True,
                            "type": pattern_name,
                            "intervention": pattern_config["intervention"],
                            "confidence": 0.8,
                            "message_analyzed": recent_message[:100] + "..." if len(recent_message) > 100 else recent_message
                        }
            
            # Additional pattern detection
            additional_patterns = self._detect_additional_offloading_patterns(user_messages)
            if additional_patterns["detected"]:
                return additional_patterns
            
            return {"detected": False}
            
        except Exception as e:
            self.telemetry.log_error("detect_cognitive_offloading_patterns", str(e))
            return {"detected": False, "error": str(e)}
    
    async def generate_cognitive_intervention(self, offloading_detection: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """
        Generate cognitive intervention based on offloading detection.
        """
        self.telemetry.log_agent_start("generate_cognitive_intervention")
        
        try:
            if not offloading_detection.get("detected", False):
                return {
                    "intervention_type": "none",
                    "challenge": "Continue exploring your design approach.",
                    "rationale": "No cognitive offloading detected.",
                    "confidence": 0.5
                }
            
            offloading_type = offloading_detection.get("type", "general")
            intervention_config = offloading_detection.get("intervention", {})
            
            # Generate intervention based on type
            if offloading_type == "solution_seeking":
                intervention = await self._generate_solution_seeking_intervention(state, analysis_result)
            elif offloading_type == "confirmation_bias":
                intervention = await self._generate_confirmation_bias_intervention(state, analysis_result)
            elif offloading_type == "complexity_avoidance":
                intervention = await self._generate_complexity_avoidance_intervention(state, analysis_result)
            elif offloading_type == "dependency_seeking":
                intervention = await self._generate_dependency_seeking_intervention(state, analysis_result)
            elif offloading_type == "validation_seeking":
                intervention = await self._generate_validation_seeking_intervention(state, analysis_result)
            else:
                intervention = await self._generate_general_intervention(state, analysis_result)
            
            # Add meta-information
            intervention.update({
                "offloading_type": offloading_type,
                "detection_confidence": offloading_detection.get("confidence", 0.5),
                "intervention_timestamp": self.telemetry.get_timestamp()
            })
            
            return intervention
            
        except Exception as e:
            self.telemetry.log_error("generate_cognitive_intervention", str(e))
            return {
                "intervention_type": "error",
                "challenge": "Let's continue exploring your design.",
                "rationale": "Error in intervention generation.",
                "confidence": 0.3
            }
    
    async def _generate_solution_seeking_intervention(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate intervention for solution-seeking behavior."""
        challenges = [
            "Before looking for solutions, what specific problem are you trying to solve?",
            "What would happen if you explored the problem space more deeply first?",
            "How might different users experience this challenge differently?",
            "What assumptions about the problem might you be making?",
            "What questions haven't you asked yet about this design challenge?"
        ]
        
        return {
            "intervention_type": "problem_exploration",
            "challenge": self.text_processor.select_random(challenges),
            "rationale": "Encouraging deeper problem exploration before solution-seeking.",
            "pedagogical_intent": "Develop problem analysis skills",
            "confidence": 0.8
        }
    
    async def _generate_confirmation_bias_intervention(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate intervention for confirmation bias."""
        challenges = [
            "What evidence might contradict your current approach?",
            "How would someone with a different background approach this problem?",
            "What are the strongest arguments against your current design direction?",
            "What would you need to see to change your mind about this approach?",
            "Which of your assumptions might be worth questioning?"
        ]
        
        return {
            "intervention_type": "perspective_challenge",
            "challenge": self.text_processor.select_random(challenges),
            "rationale": "Challenging confirmation bias by encouraging alternative perspectives.",
            "pedagogical_intent": "Promote critical thinking and perspective-taking",
            "confidence": 0.8
        }
    
    async def _generate_complexity_avoidance_intervention(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate intervention for complexity avoidance."""
        challenges = [
            "What aspects of this problem feel most complex or uncertain?",
            "How might embracing this complexity lead to better solutions?",
            "What would you gain by working through the difficult parts?",
            "How could you break down this complexity into manageable pieces?",
            "What's the most challenging aspect you're avoiding, and why?"
        ]
        
        return {
            "intervention_type": "complexity_engagement",
            "challenge": self.text_processor.select_random(challenges),
            "rationale": "Encouraging engagement with complexity rather than avoidance.",
            "pedagogical_intent": "Build tolerance for ambiguity and complex problem-solving",
            "confidence": 0.8
        }
    
    async def _generate_dependency_seeking_intervention(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate intervention for dependency-seeking behavior."""
        challenges = [
            "What would you try if you had to solve this completely on your own?",
            "What resources or knowledge do you already have that could help?",
            "How might you test your ideas before seeking external validation?",
            "What's your instinct telling you about the right direction?",
            "What would happen if you trusted your design judgment more?"
        ]
        
        return {
            "intervention_type": "independence_building",
            "challenge": self.text_processor.select_random(challenges),
            "rationale": "Building independence and self-reliance in design thinking.",
            "pedagogical_intent": "Develop autonomous problem-solving skills",
            "confidence": 0.7
        }
    
    async def _generate_validation_seeking_intervention(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate intervention for validation-seeking behavior."""
        challenges = [
            "What criteria would you use to evaluate this design yourself?",
            "How confident do you feel about your approach, and why?",
            "What aspects of your design do you feel most certain about?",
            "How might you validate your ideas through testing or research?",
            "What would make you more confident in your design decisions?"
        ]
        
        return {
            "intervention_type": "self_validation",
            "challenge": self.text_processor.select_random(challenges),
            "rationale": "Encouraging self-validation and confidence building.",
            "pedagogical_intent": "Build self-assessment and evaluation skills",
            "confidence": 0.7
        }
    
    async def _generate_general_intervention(self, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate general cognitive intervention."""
        challenges = [
            "What's driving your design decisions in this moment?",
            "How confident are you in your current approach, and why?",
            "What would you want to understand better about this problem?",
            "How might you test or validate your current thinking?",
            "What's your next step in developing this design?"
        ]
        
        return {
            "intervention_type": "metacognitive_reflection",
            "challenge": self.text_processor.select_random(challenges),
            "rationale": "Promoting general metacognitive awareness.",
            "pedagogical_intent": "Enhance reflective thinking and self-awareness",
            "confidence": 0.6
        }
    
    def _detect_additional_offloading_patterns(self, user_messages: List[str]) -> Dict[str, Any]:
        """Detect additional cognitive offloading patterns."""
        try:
            if not user_messages:
                return {"detected": False}
            
            recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
            combined_text = " ".join(recent_messages).lower()
            
            # Pattern: Excessive help-seeking
            help_seeking_indicators = [
                "help me", "tell me what to do", "what should i do", "i don't know how",
                "can you solve this", "give me the answer", "show me the way"
            ]
            
            help_seeking_count = sum(1 for indicator in help_seeking_indicators if indicator in combined_text)
            if help_seeking_count >= 2:
                return {
                    "detected": True,
                    "type": "excessive_help_seeking",
                    "intervention": {
                        "type": "independence_building",
                        "priority": "high"
                    },
                    "confidence": 0.7
                }
            
            # Pattern: Decision avoidance
            avoidance_indicators = [
                "i can't decide", "too many options", "don't know which", "all seem good",
                "you choose", "what do you think is best", "i'm stuck"
            ]
            
            avoidance_count = sum(1 for indicator in avoidance_indicators if indicator in combined_text)
            if avoidance_count >= 1:
                return {
                    "detected": True,
                    "type": "decision_avoidance",
                    "intervention": {
                        "type": "decision_making_support",
                        "priority": "medium"
                    },
                    "confidence": 0.6
                }
            
            # Pattern: Perfectionism paralysis
            perfectionism_indicators = [
                "has to be perfect", "not good enough", "needs to be better", "afraid of mistakes",
                "what if it's wrong", "need the best solution", "can't move forward"
            ]
            
            perfectionism_count = sum(1 for indicator in perfectionism_indicators if indicator in combined_text)
            if perfectionism_count >= 1:
                return {
                    "detected": True,
                    "type": "perfectionism_paralysis",
                    "intervention": {
                        "type": "iteration_encouragement",
                        "priority": "medium"
                    },
                    "confidence": 0.6
                }
            
            return {"detected": False}
            
        except Exception as e:
            self.telemetry.log_error("_detect_additional_offloading_patterns", str(e))
            return {"detected": False}
    
    def assess_intervention_effectiveness(self, intervention_history: List[Dict], state: ArchMentorState) -> Dict[str, Any]:
        """Assess the effectiveness of previous interventions."""
        try:
            if not intervention_history:
                return {
                    "effectiveness_score": 0.5,
                    "patterns": [],
                    "recommendations": ["Continue monitoring cognitive patterns"]
                }
            
            # Simple effectiveness assessment
            recent_interventions = intervention_history[-3:] if len(intervention_history) >= 3 else intervention_history
            
            # Count intervention types
            intervention_types = {}
            for intervention in recent_interventions:
                int_type = intervention.get("intervention_type", "unknown")
                intervention_types[int_type] = intervention_types.get(int_type, 0) + 1
            
            # Assess message progression after interventions
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if len(user_messages) >= 2:
                recent_length = len(user_messages[-1].split())
                earlier_length = len(user_messages[-2].split())
                length_improvement = recent_length / max(earlier_length, 1)
            else:
                length_improvement = 1.0
            
            # Calculate effectiveness score
            effectiveness_score = min(length_improvement * 0.5 + 0.3, 1.0)
            
            return {
                "effectiveness_score": effectiveness_score,
                "intervention_types": intervention_types,
                "length_improvement": length_improvement,
                "recommendations": self._generate_intervention_recommendations(effectiveness_score, intervention_types)
            }
            
        except Exception as e:
            self.telemetry.log_error("assess_intervention_effectiveness", str(e))
            return {
                "effectiveness_score": 0.5,
                "error": str(e),
                "recommendations": ["Continue standard intervention approach"]
            }
    
    def _generate_intervention_recommendations(self, effectiveness_score: float, intervention_types: Dict[str, int]) -> List[str]:
        """Generate recommendations based on intervention effectiveness."""
        recommendations = []
        
        if effectiveness_score < 0.4:
            recommendations.append("Consider changing intervention approach")
            recommendations.append("Assess if cognitive load is too high")
        elif effectiveness_score > 0.8:
            recommendations.append("Current intervention approach is working well")
            recommendations.append("Consider increasing challenge level")
        else:
            recommendations.append("Continue current intervention approach with minor adjustments")
        
        # Type-specific recommendations
        if intervention_types.get("problem_exploration", 0) > 2:
            recommendations.append("Student may need more structured problem-solving support")
        
        if intervention_types.get("complexity_engagement", 0) > 2:
            recommendations.append("Consider breaking down complexity into smaller steps")
        
        return recommendations
    
    def generate_intervention_summary(self, interventions: List[Dict]) -> str:
        """Generate a summary of interventions for analysis."""
        try:
            if not interventions:
                return "No interventions generated in this session."
            
            intervention_count = len(interventions)
            intervention_types = {}
            
            for intervention in interventions:
                int_type = intervention.get("intervention_type", "unknown")
                intervention_types[int_type] = intervention_types.get(int_type, 0) + 1
            
            most_common_type = max(intervention_types.items(), key=lambda x: x[1]) if intervention_types else ("none", 0)
            
            summary = f"""
            🎯 INTERVENTION SUMMARY
            
            Total Interventions: {intervention_count}
            Most Common Type: {most_common_type[0]} ({most_common_type[1]} times)
            
            Intervention Types:
            """
            
            for int_type, count in sorted(intervention_types.items()):
                summary += f"• {int_type.replace('_', ' ').title()}: {count}\n"
            
            return summary.strip()
            
        except Exception as e:
            self.telemetry.log_error("generate_intervention_summary", str(e))
            return "Intervention summary unavailable." 