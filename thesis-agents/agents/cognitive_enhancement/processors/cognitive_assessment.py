"""
Cognitive assessment processing module for evaluating student cognitive states.
"""
from typing import Dict, Any, List
from ..config import COGNITIVE_THRESHOLDS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class CognitiveAssessmentProcessor:
    """
    Processes cognitive state assessment for architecture students.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("cognitive_assessment")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def assess_cognitive_state(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict) -> Dict[str, Any]:
        """
        Comprehensive cognitive state assessment.
        """
        self.telemetry.log_agent_start("assess_cognitive_state")
        
        try:
            # Individual cognitive dimension assessments
            engagement_level = self._assess_engagement_indicators(state, context_classification)
            cognitive_load = self._assess_cognitive_load_indicators(state, context_classification)
            metacognitive_awareness = self._assess_metacognitive_awareness(state, context_classification)
            passivity_level = self._assess_passivity_level(state, context_classification)
            overconfidence_level = self._assess_overconfidence_level(state, context_classification)
            conversation_depth = self._assess_conversation_depth(state)
            learning_progression = self._assess_learning_progression(state, analysis_result)
            
            # Composite assessment
            cognitive_state = {
                "engagement_level": engagement_level,
                "cognitive_load": cognitive_load,
                "metacognitive_awareness": metacognitive_awareness,
                "passivity_level": passivity_level,
                "overconfidence_level": overconfidence_level,
                "conversation_depth": conversation_depth,
                "learning_progression": learning_progression,
                "overall_state": self._determine_overall_cognitive_state(
                    engagement_level, cognitive_load, metacognitive_awareness, 
                    passivity_level, overconfidence_level
                ),
                "assessment_confidence": self._calculate_assessment_confidence(state, context_classification),
                "assessment_timestamp": self.telemetry.get_timestamp()
            }
            
            self.telemetry.log_agent_end("assess_cognitive_state")
            return cognitive_state
            
        except Exception as e:
            self.telemetry.log_error("assess_cognitive_state", str(e))
            return self._get_fallback_cognitive_state()
    
    def _assess_engagement_indicators(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess student engagement level from conversation patterns."""
        try:
            # Get engagement indicators from context classification
            engagement_score = context_classification.get("engagement_level", "moderate")
            if engagement_score in ["high", "moderate", "low"]:
                return engagement_score
            
            # Fallback assessment based on message patterns
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return "unknown"
            
            # Simple heuristic based on message characteristics
            recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
            
            engagement_indicators = [
                "interesting", "curious", "why", "how", "explore", "tell me more",
                "fascinating", "intriguing", "want to know", "excited"
            ]
            
            engagement_count = sum(
                1 for msg in recent_messages 
                for indicator in engagement_indicators
                if indicator.lower() in msg.lower()
            )
            
            if engagement_count >= 2:
                return "high"
            elif engagement_count >= 1:
                return "moderate"
            else:
                return "low"
                
        except Exception as e:
            self.telemetry.log_error("_assess_engagement_indicators", str(e))
            return "moderate"
    
    def _assess_cognitive_load_indicators(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess cognitive load level from conversation patterns."""
        try:
            # Check for cognitive load indicators
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return "unknown"
            
            recent_message = user_messages[-1].lower() if user_messages else ""
            
            # High cognitive load indicators
            overload_indicators = [
                "confused", "overwhelmed", "too much", "don't understand", 
                "complicated", "difficult", "hard to follow", "lost"
            ]
            
            # Low cognitive load indicators  
            underload_indicators = [
                "easy", "simple", "obvious", "boring", "too basic", 
                "already know", "straightforward"
            ]
            
            overload_count = sum(1 for indicator in overload_indicators if indicator in recent_message)
            underload_count = sum(1 for indicator in underload_indicators if indicator in recent_message)
            
            if overload_count > 0:
                return "overload"
            elif underload_count > 0:
                return "underload"
            else:
                return "optimal"
                
        except Exception as e:
            self.telemetry.log_error("_assess_cognitive_load_indicators", str(e))
            return "optimal"
    
    def _assess_metacognitive_awareness(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess metacognitive awareness level."""
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return "unknown"
            
            recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
            
            metacognitive_indicators = [
                "i think", "i believe", "i'm not sure", "it seems", "i wonder",
                "my approach", "my strategy", "i realize", "i notice", "i'm learning",
                "i understand", "i don't know", "i need to", "i should"
            ]
            
            metacognitive_count = sum(
                1 for msg in recent_messages 
                for indicator in metacognitive_indicators
                if indicator.lower() in msg.lower()
            )
            
            if metacognitive_count >= 3:
                return "high"
            elif metacognitive_count >= 1:
                return "moderate"
            else:
                return "low"
                
        except Exception as e:
            self.telemetry.log_error("_assess_metacognitive_awareness", str(e))
            return "moderate"
    
    def _assess_passivity_level(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess student passivity level."""
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return "unknown"
            
            # Check for passive vs active language patterns
            recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
            
            passive_indicators = [
                "tell me", "give me", "show me", "what should", "what do you think",
                "is this right", "am i correct", "help me", "i don't know what"
            ]
            
            active_indicators = [
                "i will", "i'm going to", "i want to", "i plan to", "let me try",
                "i think we should", "what if i", "i could", "i would like to"
            ]
            
            passive_count = sum(
                1 for msg in recent_messages 
                for indicator in passive_indicators
                if indicator.lower() in msg.lower()
            )
            
            active_count = sum(
                1 for msg in recent_messages 
                for indicator in active_indicators
                if indicator.lower() in msg.lower()
            )
            
            if passive_count > active_count and passive_count >= 2:
                return "high"
            elif passive_count > active_count:
                return "moderate"
            else:
                return "low"
                
        except Exception as e:
            self.telemetry.log_error("_assess_passivity_level", str(e))
            return "moderate"
    
    def _assess_overconfidence_level(self, state: ArchMentorState, context_classification: Dict) -> str:
        """Assess student overconfidence level."""
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if not user_messages:
                return "unknown"
            
            recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
            
            overconfidence_indicators = [
                "obviously", "clearly", "definitely", "certainly", "of course",
                "easy", "simple", "no problem", "i'm sure", "i know exactly",
                "without doubt", "absolutely"
            ]
            
            uncertainty_indicators = [
                "maybe", "perhaps", "i think", "possibly", "might be", "could be",
                "not sure", "uncertain", "don't know", "seems like"
            ]
            
            overconfidence_count = sum(
                1 for msg in recent_messages 
                for indicator in overconfidence_indicators
                if indicator.lower() in msg.lower()
            )
            
            uncertainty_count = sum(
                1 for msg in recent_messages 
                for indicator in uncertainty_indicators
                if indicator.lower() in msg.lower()
            )
            
            if overconfidence_count > uncertainty_count and overconfidence_count >= 2:
                return "high"
            elif overconfidence_count > uncertainty_count:
                return "moderate"
            else:
                return "low"
                
        except Exception as e:
            self.telemetry.log_error("_assess_overconfidence_level", str(e))
            return "moderate"
    
    def _assess_conversation_depth(self, state: ArchMentorState) -> str:
        """Assess the depth of conversation engagement."""
        try:
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            
            if message_count > 15:
                return "deep"
            elif message_count > 5:
                return "medium"
            else:
                return "shallow"
                
        except Exception as e:
            self.telemetry.log_error("_assess_conversation_depth", str(e))
            return "medium"
    
    def _assess_learning_progression(self, state: ArchMentorState, analysis_result: Dict) -> str:
        """Assess learning progression patterns."""
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if len(user_messages) < 2:
                return "stable"
            
            # Compare recent vs earlier messages for complexity and depth
            recent_avg_length = sum(len(msg.split()) for msg in user_messages[-2:]) / 2
            earlier_avg_length = sum(len(msg.split()) for msg in user_messages[:2]) / min(2, len(user_messages))
            
            if recent_avg_length > earlier_avg_length * 1.5:
                return "progressing"
            elif recent_avg_length < earlier_avg_length * 0.7:
                return "regressing"
            else:
                return "stable"
                
        except Exception as e:
            self.telemetry.log_error("_assess_learning_progression", str(e))
            return "stable"
    
    def _determine_overall_cognitive_state(self, engagement: str, cognitive_load: str, 
                                         metacognitive_awareness: str, passivity: str, 
                                         overconfidence: str) -> str:
        """Determine overall cognitive state from individual assessments."""
        try:
            # Simple rule-based determination
            if cognitive_load == "overload":
                return "overwhelmed"
            elif engagement == "low" and passivity == "high":
                return "disengaged"
            elif overconfidence == "high" and metacognitive_awareness == "low":
                return "overconfident"
            elif engagement == "high" and cognitive_load == "optimal" and metacognitive_awareness == "high":
                return "optimal"
            elif engagement == "high":
                return "engaged"
            elif metacognitive_awareness == "high":
                return "reflective"
            else:
                return "neutral"
                
        except Exception as e:
            self.telemetry.log_error("_determine_overall_cognitive_state", str(e))
            return "neutral"
    
    def _calculate_assessment_confidence(self, state: ArchMentorState, context_classification: Dict) -> float:
        """Calculate confidence in the cognitive assessment."""
        try:
            confidence_factors = []
            
            # Data availability
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            if message_count > 5:
                confidence_factors.append(0.8)
            elif message_count > 2:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.3)
            
            # Context classification quality
            if context_classification:
                confidence_factors.append(0.7)
            
            # Consistency check (simplified)
            confidence_factors.append(0.6)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_assessment_confidence", str(e))
            return 0.5
    
    def _get_fallback_cognitive_state(self) -> Dict[str, Any]:
        """Return fallback cognitive state when assessment fails."""
        return {
            "engagement_level": "moderate",
            "cognitive_load": "optimal",
            "metacognitive_awareness": "moderate",
            "passivity_level": "moderate",
            "overconfidence_level": "low",
            "conversation_depth": "medium",
            "learning_progression": "stable",
            "overall_state": "neutral",
            "assessment_confidence": 0.4,
            "assessment_timestamp": self.telemetry.get_timestamp()
        }
    
    def create_cognitive_assessment_summary(self, scientific_metrics: Dict, cognitive_state: Dict, analysis_result: Dict) -> str:
        """Create a summary of cognitive assessment for thesis research."""
        try:
            engagement = scientific_metrics.get("engagement_metrics", {}).get("overall_score", 0.5)
            complexity = scientific_metrics.get("complexity_metrics", {}).get("overall_score", 0.5)
            reflection = scientific_metrics.get("reflection_metrics", {}).get("overall_score", 0.5)
            
            # Get current phase if available
            current_phase = analysis_result.get("current_phase", "design_development")
            
            engagement_level = self._get_level_description(engagement)
            complexity_level = self._get_level_description(complexity)
            reflection_level = self._get_level_description(reflection)
            
            key_insight = self._generate_key_insight(engagement, complexity, reflection, current_phase)
            quick_tip = self._generate_quick_tip(engagement, complexity, reflection)
            
            summary = f"""
            🧠 COGNITIVE ASSESSMENT SUMMARY
            
            📊 Current Metrics:
            • Engagement: {engagement_level} ({engagement:.2f})
            • Complexity: {complexity_level} ({complexity:.2f})
            • Reflection: {reflection_level} ({reflection:.2f})
            
            💡 Key Insight: {key_insight}
            
            🎯 Quick Tip: {quick_tip}
            
            Phase: {current_phase.replace('_', ' ').title()}
            """
            
            return summary.strip()
            
        except Exception as e:
            self.telemetry.log_error("create_cognitive_assessment_summary", str(e))
            return "Cognitive assessment summary unavailable."
    
    def _get_level_description(self, score: float) -> str:
        """Convert numeric score to level description."""
        if score >= 0.7:
            return "High"
        elif score >= 0.4:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_key_insight(self, engagement: float, complexity: float, reflection: float, phase: str) -> str:
        """Generate key insight based on metrics and phase."""
        if engagement > 0.7 and complexity > 0.7:
            return f"You're showing strong engagement with complex {phase} challenges - excellent cognitive involvement!"
        elif engagement < 0.4 and complexity < 0.4:
            return f"Consider diving deeper into the {phase} complexities to enhance your learning experience."
        elif reflection > 0.7:
            return f"Your reflective approach to {phase} is developing strong metacognitive skills."
        elif reflection < 0.4:
            return f"Try reflecting more on your {phase} decision-making process for deeper learning."
        else:
            return f"You're making steady progress through the {phase} phase with balanced cognitive engagement."
    
    def _generate_quick_tip(self, engagement: float, complexity: float, reflection: float) -> str:
        """Generate quick tip based on metrics."""
        if engagement < 0.4:
            return "Try asking more questions about aspects that intrigue you."
        elif complexity < 0.4:
            return "Challenge yourself with 'what if' scenarios to explore complexity."
        elif reflection < 0.4:
            return "Pause to consider why you're making specific design choices."
        else:
            return "Keep up the balanced approach to thinking and learning!" 