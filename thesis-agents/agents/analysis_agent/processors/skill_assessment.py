"""
Skill assessment processing module for analyzing student skill levels.
"""

from typing import List, Dict, Any
from ..schemas import SkillLevel, SkillAssessment
from ..config import SKILL_INDICATORS, SKILL_ASSESSMENT_THRESHOLDS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class SkillAssessmentProcessor:
    """
    Processes student skill level assessment from conversation history.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("skill_assessment")
        self.text_processor = TextProcessor()
    
    def assess_skill_level(self, state: ArchMentorState) -> SkillAssessment:
        """
        Dynamically assess student skill level from their inputs.
        
        Args:
            state: Current system state with conversation history
            
        Returns:
            SkillAssessment with level, confidence, and reasoning
        """
        with self.telemetry.time_operation("skill_assessment"):
            # Extract user messages
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if not user_messages:
                return self._create_default_assessment()
            
            # Combine all user input for analysis
            combined_input = " ".join(user_messages)
            
            # Analyze vocabulary indicators
            indicators = self._analyze_vocabulary_indicators(combined_input)
            
            # Analyze complexity metrics
            complexity_metrics = self.text_processor.calculate_complexity_score(combined_input)
            
            # Calculate skill level
            skill_level = self._determine_skill_level(
                indicators, complexity_metrics, len(user_messages)
            )
            
            # Calculate confidence
            confidence = MetricsCalculator.calculate_skill_confidence(
                len(user_messages),
                complexity_metrics["word_count"],
                indicators["intermediate"] + indicators["advanced"]
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(skill_level, indicators, complexity_metrics)
            
            self.telemetry.log_skill_assessment(skill_level.value, confidence)
            
            return SkillAssessment(
                skill_level=skill_level,
                confidence=confidence,
                indicators=indicators,
                complexity_metrics=complexity_metrics,
                reasoning=reasoning
            )
    
    def _create_default_assessment(self) -> SkillAssessment:
        """Create default assessment when no messages available."""
        return SkillAssessment(
            skill_level=SkillLevel.INTERMEDIATE,
            confidence=0.3,
            reasoning="Default assessment - insufficient data"
        )
    
    def _analyze_vocabulary_indicators(self, text: str) -> Dict[str, int]:
        """Analyze vocabulary indicators for each skill level."""
        indicators = {}
        
        for level, terms in SKILL_INDICATORS.items():
            indicators[level] = self.text_processor.extract_indicators(text, terms)
        
        return indicators
    
    def _determine_skill_level(
        self, 
        indicators: Dict[str, int], 
        complexity_metrics: Dict[str, float], 
        message_count: int
    ) -> SkillLevel:
        """
        Determine skill level based on indicators and complexity.
        
        Args:
            indicators: Vocabulary indicator counts
            complexity_metrics: Text complexity metrics
            message_count: Number of user messages
            
        Returns:
            Determined skill level
        """
        beginner_score = indicators.get("beginner", 0)
        intermediate_score = indicators.get("intermediate", 0)
        advanced_score = indicators.get("advanced", 0)
        
        avg_sentence_length = complexity_metrics.get("avg_sentence_length", 0)
        uses_technical_terms = intermediate_score + advanced_score > 0
        
        # Log analysis for debugging
        self.telemetry.log_debug(
            f"Skill indicators: Beginner({beginner_score}) "
            f"Intermediate({intermediate_score}) Advanced({advanced_score})"
        )
        self.telemetry.log_debug(
            f"Avg sentence length: {avg_sentence_length:.1f}, "
            f"Technical terms: {uses_technical_terms}"
        )
        
        # Decision logic
        thresholds = SKILL_ASSESSMENT_THRESHOLDS
        
        # Advanced: High technical vocabulary + complex questions
        if (advanced_score > 0 and 
            (advanced_score / message_count > thresholds["advanced_ratio"] or 
             avg_sentence_length > thresholds["min_sentence_length"])):
            return SkillLevel.ADVANCED
        
        # Beginner: Explicit beginner language or very simple inputs
        elif (beginner_score > 0 or 
              (avg_sentence_length < thresholds["beginner_sentence_length"] and 
               not uses_technical_terms)):
            return SkillLevel.BEGINNER
        
        # Intermediate: Default middle ground
        else:
            return SkillLevel.INTERMEDIATE
    
    def _generate_reasoning(
        self, 
        skill_level: SkillLevel, 
        indicators: Dict[str, int], 
        complexity_metrics: Dict[str, float]
    ) -> str:
        """Generate human-readable reasoning for the assessment."""
        reasons = []
        
        # Add indicator-based reasoning
        for level, count in indicators.items():
            if count > 0:
                reasons.append(f"{count} {level}-level terms detected")
        
        # Add complexity-based reasoning
        avg_length = complexity_metrics.get("avg_sentence_length", 0)
        if avg_length > 15:
            reasons.append("complex sentence structure")
        elif avg_length < 6:
            reasons.append("simple sentence structure")
        
        # Add final assessment
        reasons.append(f"assessed as {skill_level.value}")
        
        return "; ".join(reasons) 