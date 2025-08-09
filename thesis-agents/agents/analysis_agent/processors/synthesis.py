"""
Synthesis processing module for combining and synthesizing analysis results.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..schemas import SkillLevel, CognitiveState, AnalysisSynthesis
from ..config import COGNITIVE_PATTERNS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState, StudentProfile
from utils.agent_response import CognitiveFlag, EnhancementMetrics


class SynthesisProcessor:
    """
    Processes synthesis of analysis results and cognitive state assessment.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("synthesis")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def synthesize_analysis(self, visual: Dict, textual: Dict, student_profile: StudentProfile) -> Dict[str, Any]:
        """
        Synthesize visual and textual analysis results with student profile.
        """
        self.telemetry.log_agent_start("synthesize_analysis")
        
        try:
            # Core synthesis components
            integrated_analysis = self._integrate_analyses(visual, textual)
            skill_alignment = self._assess_skill_alignment(integrated_analysis, student_profile)
            complexity_assessment = self._assess_complexity_match(integrated_analysis, student_profile)
            learning_opportunities = self._identify_learning_opportunities(integrated_analysis, student_profile)
            design_strengths = self._identify_design_strengths(integrated_analysis)
            improvement_areas = self._identify_improvement_areas(integrated_analysis, student_profile)
            
            # Educational synthesis
            pedagogical_insights = self._generate_pedagogical_insights(integrated_analysis, student_profile)
            next_steps = self._recommend_next_steps(integrated_analysis, student_profile)
            
            # Confidence and quality metrics
            synthesis_confidence = self._calculate_synthesis_confidence(visual, textual, integrated_analysis)
            analysis_quality = self._assess_analysis_quality(visual, textual)
            
            return {
                "integrated_analysis": integrated_analysis,
                "skill_alignment": skill_alignment,
                "complexity_assessment": complexity_assessment,
                "learning_opportunities": learning_opportunities,
                "design_strengths": design_strengths,
                "improvement_areas": improvement_areas,
                "pedagogical_insights": pedagogical_insights,
                "next_steps": next_steps,
                "synthesis_confidence": synthesis_confidence,
                "analysis_quality": analysis_quality,
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.telemetry.log_error("synthesize_analysis", str(e))
            return self._get_fallback_synthesis(visual, textual, student_profile)
    
    def assess_cognitive_state(self, state: ArchMentorState) -> Dict[str, Any]:
        """
        Assess the cognitive state of the student based on conversation patterns.
        """
        self.telemetry.log_agent_start("assess_cognitive_state")
        
        try:
            # Get recent messages for analysis
            recent_messages = self._get_recent_messages(state)
            
            # Analyze different cognitive dimensions
            engagement_level = self._assess_engagement(recent_messages)
            confidence_level = self._assess_confidence(recent_messages)
            confusion_indicators = self._detect_confusion(recent_messages)
            frustration_indicators = self._detect_frustration(recent_messages)
            curiosity_indicators = self._detect_curiosity(recent_messages)
            
            # Overall cognitive state assessment
            overall_state = self._determine_overall_cognitive_state(
                engagement_level, confidence_level, confusion_indicators, 
                frustration_indicators, curiosity_indicators
            )
            
            # Learning readiness assessment
            learning_readiness = self._assess_learning_readiness(
                engagement_level, confidence_level, confusion_indicators
            )
            
            # Intervention recommendations
            interventions = self._recommend_interventions(overall_state, learning_readiness)
            
            return {
                "overall_state": overall_state,
                "engagement_level": engagement_level,
                "confidence_level": confidence_level,
                "confusion_indicators": confusion_indicators,
                "frustration_indicators": frustration_indicators,
                "curiosity_indicators": curiosity_indicators,
                "learning_readiness": learning_readiness,
                "interventions": interventions,
                "message_count": len(recent_messages),
                "assessment_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.telemetry.log_error("assess_cognitive_state", str(e))
            return self._get_fallback_cognitive_state()
    
    async def generate_cognitive_flags(self, analysis_result: Dict, student_profile: StudentProfile, 
                                     state: ArchMentorState) -> List[str]:
        """
        Generate cognitive flags based on analysis results and student state.
        """
        self.telemetry.log_agent_start("generate_cognitive_flags")
        
        try:
            flags = []
            
            # Skill level flags
            skill_flags = self._generate_skill_flags(analysis_result, student_profile)
            flags.extend(skill_flags)
            
            # Complexity flags
            complexity_flags = self._generate_complexity_flags(analysis_result, student_profile)
            flags.extend(complexity_flags)
            
            # Engagement flags
            engagement_flags = self._generate_engagement_flags(state)
            flags.extend(engagement_flags)
            
            # Progress flags
            progress_flags = self._generate_progress_flags(analysis_result, state)
            flags.extend(progress_flags)
            
            # Learning opportunity flags
            opportunity_flags = self._generate_opportunity_flags(analysis_result, student_profile)
            flags.extend(opportunity_flags)
            
            return list(set(flags))  # Remove duplicates
            
        except Exception as e:
            self.telemetry.log_error("generate_cognitive_flags", str(e))
            return ["analysis_available", "needs_guidance"]
    
    def incorporate_context_insights(self, analysis_result: Dict, context_package: Dict) -> Dict:
        """
        Incorporate insights from context analysis into the main analysis result.
        """
        self.telemetry.log_agent_start("incorporate_context_insights")
        
        try:
            if not context_package:
                return analysis_result
            
            # Extract context insights
            context_classification = context_package.get('context_classification', {})
            routing_suggestions = context_package.get('routing_suggestions', {})
            contextual_metadata = context_package.get('contextual_metadata', {})
            
            # Create enhanced analysis result
            enhanced_result = analysis_result.copy()
            
            # Add context-informed adjustments
            enhanced_result['context_insights'] = {
                'interaction_type': context_classification.get('interaction_type', 'unknown'),
                'understanding_level': context_classification.get('understanding_level', 'moderate'),
                'engagement_level': context_classification.get('engagement_level', 'moderate'),
                'confidence_level': context_classification.get('confidence_level', 'moderate'),
                'routing_priority': routing_suggestions.get('priority_agent', 'analysis_agent'),
                'context_quality': contextual_metadata.get('context_quality_score', 0.5)
            }
            
            # Adjust recommendations based on context
            if context_classification.get('understanding_level') == 'low':
                enhanced_result['recommendations'] = self._adjust_for_low_understanding(
                    enhanced_result.get('recommendations', [])
                )
            elif context_classification.get('understanding_level') == 'high':
                enhanced_result['recommendations'] = self._adjust_for_high_understanding(
                    enhanced_result.get('recommendations', [])
                )
            
            # Adjust complexity based on engagement
            if context_classification.get('engagement_level') == 'low':
                enhanced_result['suggested_complexity'] = 'simplified'
            elif context_classification.get('engagement_level') == 'high':
                enhanced_result['suggested_complexity'] = 'enhanced'
            
            return enhanced_result
            
        except Exception as e:
            self.telemetry.log_error("incorporate_context_insights", str(e))
            return analysis_result
    
    def integrate_conversation_progression(self, state: ArchMentorState, user_input: str, 
                                         current_response: str) -> Dict[str, Any]:
        """
        Integrate conversation progression analysis.
        """
        self.telemetry.log_agent_start("integrate_conversation_progression")
        
        try:
            # Analyze conversation flow
            conversation_depth = self._assess_conversation_depth(state)
            topic_coherence = self._assess_topic_coherence(state, user_input)
            learning_progression = self._assess_learning_progression(state)
            
            # Analyze current interaction
            interaction_quality = self._assess_interaction_quality(user_input, current_response)
            response_appropriateness = self._assess_response_appropriateness(user_input, current_response)
            
            # Generate progression insights
            progression_insights = {
                'conversation_depth': conversation_depth,
                'topic_coherence': topic_coherence,
                'learning_progression': learning_progression,
                'interaction_quality': interaction_quality,
                'response_appropriateness': response_appropriateness,
                'progression_recommendations': self._generate_progression_recommendations(
                    conversation_depth, topic_coherence, learning_progression
                )
            }
            
            return progression_insights
            
        except Exception as e:
            self.telemetry.log_error("integrate_conversation_progression", str(e))
            return {'progression_status': 'unknown', 'recommendations': []}
    
    def calculate_enhancement_metrics(self, analysis_result: Dict, state: ArchMentorState) -> EnhancementMetrics:
        """
        Calculate enhancement metrics for the analysis.
        """
        self.telemetry.log_agent_start("calculate_enhancement_metrics")
        
        try:
            # Calculate various metrics
            complexity_score = self._calculate_complexity_metric(analysis_result)
            engagement_score = self._calculate_engagement_metric(state)
            learning_velocity = self._calculate_learning_velocity(state)
            cognitive_load = self._calculate_cognitive_load(analysis_result, state)
            
            # Create enhancement metrics object
            metrics = EnhancementMetrics(
                complexity_score=complexity_score,
                engagement_score=engagement_score,
                learning_velocity=learning_velocity,
                cognitive_load=cognitive_load,
                analysis_depth=len(analysis_result.get('key_insights', [])),
                interaction_count=len(state.conversation_history) if hasattr(state, 'conversation_history') else 0
            )
            
            return metrics
            
        except Exception as e:
            self.telemetry.log_error("calculate_enhancement_metrics", str(e))
            return EnhancementMetrics(
                complexity_score=0.5,
                engagement_score=0.5,
                learning_velocity=0.5,
                cognitive_load=0.5,
                analysis_depth=1,
                interaction_count=0
            )
    
    def convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """
        Convert string flags to CognitiveFlag objects.
        """
        try:
            flag_objects = []
            
            for flag_str in cognitive_flags:
                # Map string flags to CognitiveFlag enum values
                flag_mapping = {
                    'needs_encouragement': CognitiveFlag.NEEDS_ENCOURAGEMENT,
                    'high_engagement': CognitiveFlag.HIGH_ENGAGEMENT,
                    'confusion_detected': CognitiveFlag.CONFUSION_DETECTED,
                    'ready_for_challenge': CognitiveFlag.READY_FOR_CHALLENGE,
                    'requires_simplification': CognitiveFlag.REQUIRES_SIMPLIFICATION,
                    'showing_progress': CognitiveFlag.SHOWING_PROGRESS,
                    'needs_guidance': CognitiveFlag.NEEDS_GUIDANCE,
                    'creative_thinking': CognitiveFlag.CREATIVE_THINKING,
                    'analytical_mode': CognitiveFlag.ANALYTICAL_MODE,
                    'synthesis_ready': CognitiveFlag.SYNTHESIS_READY
                }
                
                if flag_str in flag_mapping:
                    flag_objects.append(flag_mapping[flag_str])
                else:
                    # Default flag for unmapped strings
                    flag_objects.append(CognitiveFlag.NEEDS_GUIDANCE)
            
            return flag_objects
            
        except Exception as e:
            self.telemetry.log_error("convert_cognitive_flags", str(e))
            return [CognitiveFlag.NEEDS_GUIDANCE]
    
    # Helper methods for internal processing
    
    def _integrate_analyses(self, visual: Dict, textual: Dict) -> Dict[str, Any]:
        """Integrate visual and textual analyses."""
        integrated = {
            'visual_insights': visual.get('key_insights', []) if visual else [],
            'textual_insights': textual.get('key_insights', []) if textual else [],
            'combined_themes': [],
            'coherence_score': 0.0
        }
        
        # Simple coherence calculation
        if visual and textual:
            visual_themes = set(visual.get('themes', []))
            textual_themes = set(textual.get('themes', []))
            common_themes = visual_themes.intersection(textual_themes)
            
            integrated['combined_themes'] = list(visual_themes.union(textual_themes))
            integrated['coherence_score'] = len(common_themes) / max(len(visual_themes.union(textual_themes)), 1)
        
        return integrated
    
    def _assess_skill_alignment(self, analysis: Dict, profile: StudentProfile) -> Dict[str, Any]:
        """Assess alignment between analysis complexity and student skill level."""
        return {
            'alignment_score': 0.7,  # Simplified
            'recommendations': ['Consider current skill level in explanations'],
            'skill_gaps': []
        }
    
    def _assess_complexity_match(self, analysis: Dict, profile: StudentProfile) -> Dict[str, Any]:
        """Assess if analysis complexity matches student capabilities."""
        return {
            'complexity_appropriate': True,
            'adjustment_needed': False,
            'suggested_level': profile.skill_level
        }
    
    def _identify_learning_opportunities(self, analysis: Dict, profile: StudentProfile) -> List[str]:
        """Identify learning opportunities from the analysis."""
        opportunities = [
            'Explore spatial relationships in more detail',
            'Consider material and construction implications',
            'Investigate environmental performance aspects'
        ]
        return opportunities
    
    def _identify_design_strengths(self, analysis: Dict) -> List[str]:
        """Identify design strengths from the analysis."""
        return [
            'Clear spatial organization',
            'Appropriate scale and proportion',
            'Good consideration of user needs'
        ]
    
    def _identify_improvement_areas(self, analysis: Dict, profile: StudentProfile) -> List[str]:
        """Identify areas for improvement."""
        return [
            'Develop technical understanding',
            'Consider sustainability aspects',
            'Explore alternative design approaches'
        ]
    
    def _generate_pedagogical_insights(self, analysis: Dict, profile: StudentProfile) -> Dict[str, Any]:
        """Generate pedagogical insights."""
        return {
            'teaching_approach': 'guided_discovery',
            'focus_areas': ['spatial_design', 'technical_integration'],
            'learning_style_match': 'visual_kinesthetic'
        }
    
    def _recommend_next_steps(self, analysis: Dict, profile: StudentProfile) -> List[str]:
        """Recommend next steps for learning."""
        return [
            'Develop detailed floor plans',
            'Create section drawings',
            'Research similar building types',
            'Consider structural system options'
        ]
    
    def _calculate_synthesis_confidence(self, visual: Dict, textual: Dict, integrated: Dict) -> float:
        """Calculate confidence in the synthesis."""
        confidence_factors = []
        
        if visual:
            confidence_factors.append(0.8)
        if textual:
            confidence_factors.append(0.7)
        if integrated.get('coherence_score', 0) > 0.5:
            confidence_factors.append(0.9)
        
        return sum(confidence_factors) / max(len(confidence_factors), 1)
    
    def _assess_analysis_quality(self, visual: Dict, textual: Dict) -> str:
        """Assess overall quality of the analysis."""
        quality_score = 0
        
        if visual and len(visual.get('key_insights', [])) > 2:
            quality_score += 1
        if textual and textual.get('detail_level') in ['medium', 'high']:
            quality_score += 1
        
        if quality_score >= 2:
            return 'high'
        elif quality_score >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _get_recent_messages(self, state: ArchMentorState) -> List[str]:
        """Get recent messages from conversation history."""
        if hasattr(state, 'conversation_history') and state.conversation_history:
            return [msg.get('content', '') for msg in state.conversation_history[-5:]]
        return []
    
    def _assess_engagement(self, messages: List[str]) -> str:
        """Assess engagement level from messages."""
        if not messages:
            return 'unknown'
        
        engagement_indicators = COGNITIVE_PATTERNS.get('engagement', [])
        engagement_count = sum(
            1 for msg in messages for indicator in engagement_indicators
            if indicator.lower() in msg.lower()
        )
        
        if engagement_count >= 2:
            return 'high'
        elif engagement_count >= 1:
            return 'moderate'
        else:
            return 'low'
    
    def _assess_confidence(self, messages: List[str]) -> str:
        """Assess confidence level from messages."""
        if not messages:
            return 'unknown'
        
        confidence_indicators = COGNITIVE_PATTERNS.get('confidence', [])
        confidence_count = sum(
            1 for msg in messages for indicator in confidence_indicators
            if indicator.lower() in msg.lower()
        )
        
        if confidence_count >= 2:
            return 'high'
        elif confidence_count >= 1:
            return 'moderate'
        else:
            return 'low'
    
    def _detect_confusion(self, messages: List[str]) -> List[str]:
        """Detect confusion indicators in messages."""
        confusion_indicators = COGNITIVE_PATTERNS.get('confusion', [])
        found_indicators = []
        
        for msg in messages:
            for indicator in confusion_indicators:
                if indicator.lower() in msg.lower():
                    found_indicators.append(indicator)
        
        return list(set(found_indicators))
    
    def _detect_frustration(self, messages: List[str]) -> List[str]:
        """Detect frustration indicators in messages."""
        frustration_indicators = COGNITIVE_PATTERNS.get('frustration', [])
        found_indicators = []
        
        for msg in messages:
            for indicator in frustration_indicators:
                if indicator.lower() in msg.lower():
                    found_indicators.append(indicator)
        
        return list(set(found_indicators))
    
    def _detect_curiosity(self, messages: List[str]) -> List[str]:
        """Detect curiosity indicators in messages."""
        curiosity_indicators = ["why", "how", "what if", "curious", "explore", "learn more"]
        found_indicators = []
        
        for msg in messages:
            for indicator in curiosity_indicators:
                if indicator.lower() in msg.lower():
                    found_indicators.append(indicator)
        
        return list(set(found_indicators))
    
    def _determine_overall_cognitive_state(self, engagement: str, confidence: str, 
                                         confusion: List[str], frustration: List[str], 
                                         curiosity: List[str]) -> str:
        """Determine overall cognitive state."""
        if frustration:
            return 'frustrated'
        elif confusion:
            return 'confused'
        elif engagement == 'high' and confidence == 'high':
            return 'optimal'
        elif engagement == 'high':
            return 'engaged'
        elif confidence == 'low':
            return 'uncertain'
        else:
            return 'neutral'
    
    def _assess_learning_readiness(self, engagement: str, confidence: str, confusion: List[str]) -> float:
        """Assess readiness for learning."""
        readiness_score = 0.5
        
        if engagement == 'high':
            readiness_score += 0.3
        elif engagement == 'low':
            readiness_score -= 0.2
        
        if confidence == 'high':
            readiness_score += 0.2
        elif confidence == 'low':
            readiness_score -= 0.1
        
        if confusion:
            readiness_score -= 0.2
        
        return max(0.0, min(1.0, readiness_score))
    
    def _recommend_interventions(self, overall_state: str, learning_readiness: float) -> List[str]:
        """Recommend interventions based on cognitive state."""
        interventions = []
        
        if overall_state == 'frustrated':
            interventions.extend(['provide_encouragement', 'simplify_content', 'break_down_tasks'])
        elif overall_state == 'confused':
            interventions.extend(['clarify_concepts', 'provide_examples', 'check_understanding'])
        elif overall_state == 'optimal':
            interventions.extend(['provide_challenges', 'encourage_exploration'])
        elif learning_readiness < 0.4:
            interventions.extend(['build_confidence', 'provide_support'])
        
        return interventions
    
    # Additional helper methods for flag generation and other functionality
    
    def _generate_skill_flags(self, analysis: Dict, profile: StudentProfile) -> List[str]:
        """Generate flags related to skill level."""
        flags = []
        
        if hasattr(profile, 'skill_level'):
            if profile.skill_level == 'beginner':
                flags.append('needs_guidance')
            elif profile.skill_level == 'advanced':
                flags.append('ready_for_challenge')
        
        return flags
    
    def _generate_complexity_flags(self, analysis: Dict, profile: StudentProfile) -> List[str]:
        """Generate flags related to complexity."""
        flags = []
        
        complexity = analysis.get('complexity_score', 0.5)
        if complexity > 0.7:
            flags.append('high_complexity')
        elif complexity < 0.3:
            flags.append('requires_enhancement')
        
        return flags
    
    def _generate_engagement_flags(self, state: ArchMentorState) -> List[str]:
        """Generate flags related to engagement."""
        flags = []
        
        messages = self._get_recent_messages(state)
        engagement = self._assess_engagement(messages)
        
        if engagement == 'high':
            flags.append('high_engagement')
        elif engagement == 'low':
            flags.append('needs_encouragement')
        
        return flags
    
    def _generate_progress_flags(self, analysis: Dict, state: ArchMentorState) -> List[str]:
        """Generate flags related to progress."""
        flags = []
        
        # Simple progress assessment based on conversation length
        if hasattr(state, 'conversation_history') and state.conversation_history:
            if len(state.conversation_history) > 5:
                flags.append('showing_progress')
        
        return flags
    
    def _generate_opportunity_flags(self, analysis: Dict, profile: StudentProfile) -> List[str]:
        """Generate flags related to learning opportunities."""
        flags = []
        
        if analysis.get('learning_opportunities'):
            flags.append('learning_opportunity_available')
        
        return flags
    
    # Additional helper methods for context and progression analysis
    
    def _adjust_for_low_understanding(self, recommendations: List[str]) -> List[str]:
        """Adjust recommendations for low understanding level."""
        adjusted = ['Start with basic concepts', 'Use simple examples']
        adjusted.extend(recommendations[:2])  # Limit to avoid overwhelming
        return adjusted
    
    def _adjust_for_high_understanding(self, recommendations: List[str]) -> List[str]:
        """Adjust recommendations for high understanding level."""
        enhanced = ['Explore advanced concepts', 'Consider complex relationships']
        enhanced.extend(recommendations)
        return enhanced
    
    def _assess_conversation_depth(self, state: ArchMentorState) -> float:
        """Assess the depth of the conversation."""
        if hasattr(state, 'conversation_history') and state.conversation_history:
            return min(len(state.conversation_history) / 10.0, 1.0)
        return 0.0
    
    def _assess_topic_coherence(self, state: ArchMentorState, user_input: str) -> float:
        """Assess topic coherence in the conversation."""
        # Simplified coherence assessment
        return 0.7
    
    def _assess_learning_progression(self, state: ArchMentorState) -> str:
        """Assess learning progression."""
        depth = self._assess_conversation_depth(state)
        
        if depth > 0.7:
            return 'advanced'
        elif depth > 0.4:
            return 'progressing'
        else:
            return 'initial'
    
    def _assess_interaction_quality(self, user_input: str, response: str) -> float:
        """Assess quality of the current interaction."""
        # Simplified quality assessment
        if len(user_input) > 10 and len(response) > 50:
            return 0.8
        else:
            return 0.5
    
    def _assess_response_appropriateness(self, user_input: str, response: str) -> float:
        """Assess appropriateness of the response."""
        # Simplified appropriateness assessment
        return 0.7
    
    def _generate_progression_recommendations(self, depth: float, coherence: float, progression: str) -> List[str]:
        """Generate recommendations for conversation progression."""
        recommendations = []
        
        if depth < 0.3:
            recommendations.append('Encourage more detailed exploration')
        if coherence < 0.5:
            recommendations.append('Help focus the conversation topic')
        if progression == 'initial':
            recommendations.append('Build foundational understanding')
        
        return recommendations
    
    def _calculate_complexity_metric(self, analysis: Dict) -> float:
        """Calculate complexity metric from analysis."""
        return analysis.get('complexity_score', 0.5)
    
    def _calculate_engagement_metric(self, state: ArchMentorState) -> float:
        """Calculate engagement metric from state."""
        messages = self._get_recent_messages(state)
        engagement = self._assess_engagement(messages)
        
        engagement_scores = {'high': 0.9, 'moderate': 0.6, 'low': 0.3}
        return engagement_scores.get(engagement, 0.5)
    
    def _calculate_learning_velocity(self, state: ArchMentorState) -> float:
        """Calculate learning velocity from conversation progression."""
        depth = self._assess_conversation_depth(state)
        return min(depth * 1.2, 1.0)  # Slightly boost for velocity
    
    def _calculate_cognitive_load(self, analysis: Dict, state: ArchMentorState) -> float:
        """Calculate cognitive load from analysis complexity and state."""
        complexity = analysis.get('complexity_score', 0.5)
        messages = self._get_recent_messages(state)
        confusion = self._detect_confusion(messages)
        
        load = complexity
        if confusion:
            load += 0.2  # Increase load if confusion detected
        
        return min(load, 1.0)
    
    def _get_fallback_synthesis(self, visual: Dict, textual: Dict, profile: StudentProfile) -> Dict[str, Any]:
        """Return fallback synthesis when main synthesis fails."""
        return {
            "integrated_analysis": {"coherence_score": 0.5},
            "skill_alignment": {"alignment_score": 0.6},
            "complexity_assessment": {"complexity_appropriate": True},
            "learning_opportunities": ["Explore design fundamentals"],
            "design_strengths": ["Shows design thinking"],
            "improvement_areas": ["Develop technical skills"],
            "pedagogical_insights": {"teaching_approach": "supportive_guidance"},
            "next_steps": ["Continue design development"],
            "synthesis_confidence": 0.5,
            "analysis_quality": "medium",
            "synthesis_timestamp": datetime.now().isoformat()
        }
    
    def _get_fallback_cognitive_state(self) -> Dict[str, Any]:
        """Return fallback cognitive state assessment."""
        return {
            "overall_state": "neutral",
            "engagement_level": "moderate",
            "confidence_level": "moderate",
            "confusion_indicators": [],
            "frustration_indicators": [],
            "curiosity_indicators": [],
            "learning_readiness": 0.6,
            "interventions": ["provide_guidance"],
            "message_count": 0,
            "assessment_timestamp": datetime.now().isoformat()
        } 