"""
Context generation processing module for creating contextual metadata and routing suggestions.
"""
from typing import Dict, Any, List, Optional
from ..schemas import ContextualMetadata, CoreClassification, ContentAnalysis, ConversationPatterns
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class ContextGenerationProcessor:
    """
    Processes contextual metadata generation and routing suggestions.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("context_generation")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def generate_contextual_metadata(self, input_text: str, state: ArchMentorState, 
                                   classification: CoreClassification) -> ContextualMetadata:
        """
        Generate comprehensive contextual metadata for routing and response preparation.
        """
        self.telemetry.log_agent_start("generate_contextual_metadata")
        
        try:
            # Assess various contextual aspects
            complexity_appropriateness = self._assess_complexity_appropriateness(classification, state)
            response_urgency = self._assess_response_urgency(classification)
            pedagogical_opportunity = self._identify_pedagogical_opportunity(classification, input_text)
            continuation_cues = self._identify_continuation_cues(state, input_text)
            difficulty_adjustment = self._assess_difficulty_adjustment(classification, state)
            
            # Generate learning context
            learning_context = self._generate_learning_context(classification, state)
            
            # Assess student readiness for different types of responses
            challenge_readiness = self._assess_challenge_readiness(classification)
            explanation_need = self._assess_explanation_need(classification, input_text)
            
            # Identify information gaps
            information_gaps = self._identify_information_gaps(input_text)
            
            # Identify analysis focus areas
            analysis_focus_areas = self._identify_analysis_focus_areas(input_text, state)
            
            # Generate engagement recommendations
            engagement_recommendations = self._generate_engagement_recommendations(classification, state)
            
            metadata = ContextualMetadata(
                complexity_appropriateness=complexity_appropriateness,
                response_urgency=response_urgency,
                pedagogical_opportunity=pedagogical_opportunity,
                continuation_cues=continuation_cues,
                difficulty_adjustment=difficulty_adjustment,
                learning_context=learning_context,
                challenge_readiness=challenge_readiness,
                explanation_need=explanation_need,
                information_gaps=information_gaps,
                analysis_focus_areas=analysis_focus_areas,
                engagement_recommendations=engagement_recommendations,
                metadata_confidence=self._calculate_metadata_confidence(
                    classification, complexity_appropriateness, response_urgency
                ),
                generation_timestamp=self._get_current_timestamp()
            )
            
            self.telemetry.log_agent_end("generate_contextual_metadata")
            return metadata
            
        except Exception as e:
            self.telemetry.log_error("generate_contextual_metadata", str(e))
            return self._get_fallback_metadata()
    
    def prepare_routing_suggestions(self, core_classification: CoreClassification, 
                                  content_analysis: ContentAnalysis,
                                  conversation_patterns: ConversationPatterns,
                                  metadata: ContextualMetadata) -> Dict[str, Any]:
        """
        Prepare routing suggestions for the orchestrator.
        """
        self.telemetry.log_agent_start("prepare_routing_suggestions")
        
        try:
            routing_suggestions = {
                'primary_agent': self._suggest_primary_agent(core_classification, content_analysis),
                'secondary_agents': self._suggest_secondary_agents(core_classification, content_analysis),
                'agent_priorities': self._calculate_agent_priorities(core_classification, content_analysis),
                'routing_confidence': self._calculate_routing_confidence(core_classification, content_analysis),
                'special_considerations': self._identify_special_considerations(
                    core_classification, conversation_patterns, metadata
                ),
                'response_style': self._suggest_response_style(core_classification, metadata),
                'complexity_level': self._suggest_complexity_level(core_classification, content_analysis),
                'pedagogical_approach': self._suggest_pedagogical_approach(
                    core_classification, conversation_patterns, metadata
                )
            }
            
            self.telemetry.log_agent_end("prepare_routing_suggestions")
            return routing_suggestions
            
        except Exception as e:
            self.telemetry.log_error("prepare_routing_suggestions", str(e))
            return self._get_fallback_routing_suggestions()
    
    def prepare_agent_contexts(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                             conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Dict[str, Any]]:
        """
        Prepare specific contexts for different agents.
        """
        self.telemetry.log_agent_start("prepare_agent_contexts")
        
        try:
            agent_contexts = {
                'socratic_tutor': self._prepare_socratic_context(
                    classification, content_analysis, conversation_patterns, metadata
                ),
                'domain_expert': self._prepare_domain_expert_context(
                    classification, content_analysis, conversation_patterns, metadata
                ),
                'analysis_agent': self._prepare_analysis_context(
                    classification, content_analysis, conversation_patterns, metadata
                ),
                'cognitive_enhancement': self._prepare_cognitive_context(
                    classification, content_analysis, conversation_patterns, metadata
                )
            }
            
            self.telemetry.log_agent_end("prepare_agent_contexts")
            return agent_contexts
            
        except Exception as e:
            self.telemetry.log_error("prepare_agent_contexts", str(e))
            return self._get_fallback_agent_contexts()
    
    # Assessment methods
    
    def _assess_complexity_appropriateness(self, classification: CoreClassification, state: ArchMentorState) -> str:
        """Assess if the complexity level is appropriate for the student."""
        try:
            understanding_level = classification.understanding_level
            confidence_level = classification.confidence_level
            question_complexity = classification.question_complexity
            
            # Get conversation history length as experience indicator
            message_count = len(state.messages) if hasattr(state, 'messages') and state.messages else 0
            
            # Assess appropriateness
            if understanding_level == 'high' and confidence_level == 'high':
                if question_complexity == 'basic':
                    return 'too_simple'
                elif question_complexity == 'advanced':
                    return 'appropriate'
                else:
                    return 'could_be_more_challenging'
            
            elif understanding_level == 'low' or confidence_level == 'low':
                if question_complexity == 'advanced':
                    return 'too_complex'
                elif question_complexity == 'basic':
                    return 'appropriate'
                else:
                    return 'slightly_challenging'
            
            else:  # moderate levels
                if question_complexity == 'intermediate':
                    return 'appropriate'
                elif question_complexity == 'basic':
                    return 'could_be_more_challenging'
                else:
                    return 'manageable_challenge'
            
        except Exception as e:
            self.telemetry.log_error("_assess_complexity_appropriateness", str(e))
            return 'appropriate'
    
    def _assess_response_urgency(self, classification: CoreClassification) -> str:
        """Assess how urgently the student needs a response."""
        try:
            urgency_factors = []
            
            # Confusion indicates high urgency
            if classification.understanding_level == 'low':
                urgency_factors.append('high')
            
            # Low confidence indicates moderate urgency
            if classification.confidence_level == 'low':
                urgency_factors.append('moderate')
            
            # Feedback requests indicate moderate urgency
            if classification.is_feedback_request:
                urgency_factors.append('moderate')
            
            # Technical questions may need prompt response
            if classification.is_technical_question:
                urgency_factors.append('moderate')
            
            # Determine overall urgency
            if 'high' in urgency_factors:
                return 'high'
            elif urgency_factors.count('moderate') >= 2:
                return 'moderate'
            elif 'moderate' in urgency_factors:
                return 'moderate'
            else:
                return 'low'
                
        except Exception as e:
            self.telemetry.log_error("_assess_response_urgency", str(e))
            return 'moderate'
    
    def _identify_pedagogical_opportunity(self, classification: CoreClassification, input_text: str) -> str:
        """Identify pedagogical opportunities in the current interaction."""
        try:
            # High-level pedagogical opportunities
            if classification.understanding_level == 'high' and classification.confidence_level == 'high':
                return 'challenge_extension'
            
            # Confusion offers teaching moments
            elif classification.understanding_level == 'low':
                return 'foundational_clarification'
            
            # Partial understanding offers building opportunities
            elif classification.understanding_level == 'partial':
                return 'scaffolded_development'
            
            # Technical questions offer deep dive opportunities
            elif classification.is_technical_question:
                return 'technical_deep_dive'
            
            # Feedback requests offer reflection opportunities
            elif classification.is_feedback_request:
                return 'reflective_assessment'
            
            # High engagement offers exploration opportunities
            elif classification.engagement_level == 'high':
                return 'exploratory_extension'
            
            # Low confidence offers confidence building
            elif classification.confidence_level == 'low':
                return 'confidence_building'
            
            else:
                return 'general_support'
                
        except Exception as e:
            self.telemetry.log_error("_identify_pedagogical_opportunity", str(e))
            return 'general_support'
    
    def _identify_continuation_cues(self, state: ArchMentorState, input_text: str) -> List[str]:
        """Identify cues for continuing the conversation."""
        try:
            continuation_cues = []
            input_lower = input_text.lower()
            
            # Question patterns that suggest follow-up
            if any(phrase in input_lower for phrase in ['what about', 'also', 'and', 'another']):
                continuation_cues.append('follow_up_questions')
            
            # Incomplete thoughts
            if input_text.endswith('...') or 'but' in input_lower:
                continuation_cues.append('incomplete_thought')
            
            # Comparison requests
            if any(phrase in input_lower for phrase in ['compare', 'versus', 'difference', 'similar']):
                continuation_cues.append('comparison_opportunity')
            
            # Example requests
            if any(phrase in input_lower for phrase in ['example', 'instance', 'case']):
                continuation_cues.append('example_opportunity')
            
            # Exploration indicators
            if any(phrase in input_lower for phrase in ['explore', 'investigate', 'learn more']):
                continuation_cues.append('exploration_interest')
            
            # Application interest
            if any(phrase in input_lower for phrase in ['apply', 'use', 'practice', 'implement']):
                continuation_cues.append('application_interest')
            
            return continuation_cues
            
        except Exception as e:
            self.telemetry.log_error("_identify_continuation_cues", str(e))
            return []
    
    def _assess_difficulty_adjustment(self, classification: CoreClassification, state: ArchMentorState) -> str:
        """Assess if difficulty should be adjusted."""
        try:
            understanding = classification.understanding_level
            confidence = classification.confidence_level
            complexity = classification.question_complexity
            
            # Determine adjustment needs
            if understanding == 'low' and confidence == 'low':
                return 'decrease_significantly'
            elif understanding == 'low' or confidence == 'low':
                return 'decrease_slightly'
            elif understanding == 'high' and confidence == 'high' and complexity == 'basic':
                return 'increase_significantly'
            elif understanding == 'high' and confidence == 'high':
                return 'increase_slightly'
            else:
                return 'maintain_current'
                
        except Exception as e:
            self.telemetry.log_error("_assess_difficulty_adjustment", str(e))
            return 'maintain_current'
    
    def _generate_learning_context(self, classification: CoreClassification, state: ArchMentorState) -> Dict[str, Any]:
        """Generate learning context for the current interaction."""
        try:
            learning_context = {
                'learning_stage': self._determine_learning_stage(classification),
                'learning_style_indicators': self._identify_learning_style_indicators(classification),
                'motivation_level': self._assess_motivation_level(classification),
                'support_needs': self._identify_support_needs(classification),
                'learning_preferences': self._infer_learning_preferences(classification, state)
            }
            
            return learning_context
            
        except Exception as e:
            self.telemetry.log_error("_generate_learning_context", str(e))
            return {'learning_stage': 'development', 'motivation_level': 'moderate'}
    
    def _assess_challenge_readiness(self, classification: CoreClassification) -> str:
        """Assess student's readiness for cognitive challenges."""
        try:
            readiness_score = 0
            
            # Positive readiness factors
            if classification.understanding_level == 'high':
                readiness_score += 2
            elif classification.understanding_level == 'partial':
                readiness_score += 1
            
            if classification.confidence_level == 'high':
                readiness_score += 2
            elif classification.confidence_level == 'neutral':
                readiness_score += 1
            
            if classification.engagement_level == 'high':
                readiness_score += 2
            elif classification.engagement_level == 'moderate':
                readiness_score += 1
            
            # Negative readiness factors
            if classification.understanding_level == 'low':
                readiness_score -= 2
            
            if classification.confidence_level == 'low':
                readiness_score -= 1
            
            # Determine readiness level
            if readiness_score >= 4:
                return 'high'
            elif readiness_score >= 2:
                return 'moderate'
            elif readiness_score >= 0:
                return 'low'
            else:
                return 'not_ready'
                
        except Exception as e:
            self.telemetry.log_error("_assess_challenge_readiness", str(e))
            return 'moderate'
    
    def _assess_explanation_need(self, classification: CoreClassification, input_text: str) -> str:
        """Assess how much explanation the student needs."""
        try:
            need_level = 0
            
            # Understanding level influence
            if classification.understanding_level == 'low':
                need_level += 3
            elif classification.understanding_level == 'partial':
                need_level += 2
            elif classification.understanding_level == 'moderate':
                need_level += 1
            
            # Question complexity influence
            if classification.question_complexity == 'advanced':
                need_level += 2
            elif classification.question_complexity == 'intermediate':
                need_level += 1
            
            # Direct requests for explanation
            input_lower = input_text.lower()
            if any(phrase in input_lower for phrase in ['explain', 'clarify', 'help me understand']):
                need_level += 2
            
            # Determine explanation need
            if need_level >= 5:
                return 'comprehensive'
            elif need_level >= 3:
                return 'moderate'
            elif need_level >= 1:
                return 'minimal'
            else:
                return 'none'
                
        except Exception as e:
            self.telemetry.log_error("_assess_explanation_need", str(e))
            return 'moderate'
    
    def _identify_information_gaps(self, input_text: str) -> List[str]:
        """Identify information gaps in the student's question or statement."""
        try:
            gaps = []
            input_lower = input_text.lower()
            
            # Context gaps
            if any(phrase in input_lower for phrase in ['this', 'that', 'it']) and len(input_text.split()) < 10:
                gaps.append('context_specification')
            
            # Scope gaps
            if any(phrase in input_lower for phrase in ['generally', 'usually', 'sometimes']) and 'specific' not in input_lower:
                gaps.append('scope_clarification')
            
            # Purpose gaps
            if '?' in input_text and not any(phrase in input_lower for phrase in ['why', 'purpose', 'goal', 'objective']):
                gaps.append('purpose_clarification')
            
            # Constraint gaps
            if any(phrase in input_lower for phrase in ['design', 'solution', 'approach']) and not any(phrase in input_lower for phrase in ['requirement', 'constraint', 'limit']):
                gaps.append('constraint_identification')
            
            # Scale gaps
            if any(phrase in input_lower for phrase in ['building', 'structure', 'project']) and not any(phrase in input_lower for phrase in ['size', 'scale', 'dimension']):
                gaps.append('scale_specification')
            
            return gaps
            
        except Exception as e:
            self.telemetry.log_error("_identify_information_gaps", str(e))
            return []
    
    def _identify_analysis_focus_areas(self, input_text: str, state: ArchMentorState) -> List[str]:
        """Identify areas that need focused analysis."""
        try:
            focus_areas = []
            input_lower = input_text.lower()
            
            # Technical analysis needs
            if any(phrase in input_lower for phrase in ['calculate', 'size', 'determine', 'analyze']):
                focus_areas.append('technical_analysis')
            
            # Design analysis needs
            if any(phrase in input_lower for phrase in ['design', 'aesthetic', 'form', 'appearance']):
                focus_areas.append('design_analysis')
            
            # Performance analysis needs
            if any(phrase in input_lower for phrase in ['performance', 'efficiency', 'effectiveness']):
                focus_areas.append('performance_analysis')
            
            # Sustainability analysis needs
            if any(phrase in input_lower for phrase in ['sustainable', 'green', 'environmental', 'energy']):
                focus_areas.append('sustainability_analysis')
            
            # Code compliance analysis needs
            if any(phrase in input_lower for phrase in ['code', 'regulation', 'requirement', 'standard']):
                focus_areas.append('compliance_analysis')
            
            # Cost analysis needs
            if any(phrase in input_lower for phrase in ['cost', 'budget', 'economic', 'financial']):
                focus_areas.append('cost_analysis')
            
            return focus_areas
            
        except Exception as e:
            self.telemetry.log_error("_identify_analysis_focus_areas", str(e))
            return []
    
    def _generate_engagement_recommendations(self, classification: CoreClassification, state: ArchMentorState) -> List[str]:
        """Generate recommendations for maintaining or improving engagement."""
        try:
            recommendations = []
            
            # Based on engagement level
            if classification.engagement_level == 'low':
                recommendations.extend([
                    'use_interactive_elements',
                    'provide_concrete_examples',
                    'connect_to_real_world_applications'
                ])
            elif classification.engagement_level == 'moderate':
                recommendations.extend([
                    'introduce_mild_challenges',
                    'encourage_exploration'
                ])
            else:  # high engagement
                recommendations.extend([
                    'provide_advanced_challenges',
                    'encourage_independent_exploration'
                ])
            
            # Based on understanding level
            if classification.understanding_level == 'low':
                recommendations.extend([
                    'use_scaffolded_approach',
                    'provide_foundational_support'
                ])
            elif classification.understanding_level == 'high':
                recommendations.extend([
                    'encourage_critical_thinking',
                    'introduce_complex_scenarios'
                ])
            
            # Based on confidence level
            if classification.confidence_level == 'low':
                recommendations.extend([
                    'provide_positive_reinforcement',
                    'break_down_complex_tasks'
                ])
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception as e:
            self.telemetry.log_error("_generate_engagement_recommendations", str(e))
            return ['maintain_supportive_tone']
    
    # Routing suggestion methods
    
    def _suggest_primary_agent(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> str:
        """Suggest the primary agent for handling this interaction."""
        try:
            # Technical questions go to domain expert
            if classification.is_technical_question or len(content_analysis.technical_terms) >= 3:
                return 'domain_expert'
            
            # Feedback requests go to analysis agent
            if classification.is_feedback_request:
                return 'analysis_agent'
            
            # High complexity questions with low understanding go to socratic tutor
            if classification.question_complexity == 'advanced' and classification.understanding_level == 'low':
                return 'socratic_tutor'
            
            # High confidence with basic questions might need cognitive challenge
            if classification.confidence_level == 'high' and classification.question_complexity == 'basic':
                return 'cognitive_enhancement'
            
            # General questions with moderate engagement
            if classification.engagement_level in ['moderate', 'high']:
                return 'socratic_tutor'
            
            # Default to domain expert for knowledge needs
            return 'domain_expert'
            
        except Exception as e:
            self.telemetry.log_error("_suggest_primary_agent", str(e))
            return 'domain_expert'
    
    def _suggest_secondary_agents(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> List[str]:
        """Suggest secondary agents that might contribute."""
        try:
            secondary_agents = []
            
            # Always consider analysis for complex interactions
            if classification.question_complexity in ['intermediate', 'advanced']:
                secondary_agents.append('analysis_agent')
            
            # Consider cognitive enhancement for confidence issues
            if classification.confidence_level == 'low' or classification.understanding_level == 'low':
                secondary_agents.append('cognitive_enhancement')
            
            # Consider socratic approach for high engagement
            if classification.engagement_level == 'high' and 'socratic_tutor' not in secondary_agents:
                secondary_agents.append('socratic_tutor')
            
            # Consider domain expert for technical content
            if len(content_analysis.technical_terms) >= 1 and 'domain_expert' not in secondary_agents:
                secondary_agents.append('domain_expert')
            
            return secondary_agents[:2]  # Limit to 2 secondary agents
            
        except Exception as e:
            self.telemetry.log_error("_suggest_secondary_agents", str(e))
            return []
    
    def _calculate_agent_priorities(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> Dict[str, float]:
        """Calculate priority scores for different agents."""
        try:
            priorities = {
                'socratic_tutor': 0.5,
                'domain_expert': 0.5,
                'analysis_agent': 0.5,
                'cognitive_enhancement': 0.5
            }
            
            # Adjust based on classification
            if classification.is_technical_question:
                priorities['domain_expert'] += 0.3
            
            if classification.is_feedback_request:
                priorities['analysis_agent'] += 0.3
            
            if classification.engagement_level == 'high':
                priorities['socratic_tutor'] += 0.2
            
            if classification.confidence_level == 'low':
                priorities['cognitive_enhancement'] += 0.2
            
            if len(content_analysis.technical_terms) >= 2:
                priorities['domain_expert'] += 0.2
            
            # Normalize priorities
            max_priority = max(priorities.values())
            if max_priority > 1.0:
                for agent in priorities:
                    priorities[agent] = priorities[agent] / max_priority
            
            return priorities
            
        except Exception as e:
            self.telemetry.log_error("_calculate_agent_priorities", str(e))
            return {'domain_expert': 0.6, 'socratic_tutor': 0.5, 'analysis_agent': 0.4, 'cognitive_enhancement': 0.4}
    
    def _calculate_routing_confidence(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> float:
        """Calculate confidence in routing decisions."""
        try:
            confidence_factors = []
            
            # Classification confidence
            confidence_factors.append(classification.classification_confidence)
            
            # Content analysis confidence
            confidence_factors.append(content_analysis.analysis_confidence)
            
            # Clear indicators boost confidence
            if classification.is_technical_question:
                confidence_factors.append(0.8)
            
            if classification.is_feedback_request:
                confidence_factors.append(0.8)
            
            if len(content_analysis.technical_terms) >= 3:
                confidence_factors.append(0.7)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_routing_confidence", str(e))
            return 0.6
    
    def _identify_special_considerations(self, classification: CoreClassification, 
                                       conversation_patterns: ConversationPatterns,
                                       metadata: ContextualMetadata) -> List[str]:
        """Identify special considerations for routing."""
        try:
            considerations = []
            
            # Engagement considerations
            if classification.engagement_level == 'low':
                considerations.append('low_engagement_risk')
            
            # Understanding considerations
            if classification.understanding_level == 'low':
                considerations.append('foundational_support_needed')
            
            # Pattern considerations
            if conversation_patterns.has_repetitive_topics:
                considerations.append('topic_repetition_detected')
            
            if conversation_patterns.has_topic_jumping:
                considerations.append('topic_jumping_detected')
            
            # Urgency considerations
            if metadata.response_urgency == 'high':
                considerations.append('urgent_response_needed')
            
            return considerations
            
        except Exception as e:
            self.telemetry.log_error("_identify_special_considerations", str(e))
            return []
    
    def _suggest_response_style(self, classification: CoreClassification, metadata: ContextualMetadata) -> str:
        """Suggest appropriate response style."""
        try:
            # Based on understanding level
            if classification.understanding_level == 'low':
                return 'explanatory'
            elif classification.understanding_level == 'high':
                return 'challenging'
            
            # Based on engagement level
            if classification.engagement_level == 'low':
                return 'engaging'
            elif classification.engagement_level == 'high':
                return 'exploratory'
            
            # Based on confidence level
            if classification.confidence_level == 'low':
                return 'supportive'
            
            # Based on pedagogical opportunity
            if metadata.pedagogical_opportunity == 'challenge_extension':
                return 'challenging'
            elif metadata.pedagogical_opportunity == 'foundational_clarification':
                return 'explanatory'
            
            return 'balanced'
            
        except Exception as e:
            self.telemetry.log_error("_suggest_response_style", str(e))
            return 'balanced'
    
    def _suggest_complexity_level(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> str:
        """Suggest appropriate complexity level for response."""
        try:
            # Start with input complexity
            base_complexity = classification.question_complexity
            
            # Adjust based on understanding
            if classification.understanding_level == 'low':
                if base_complexity == 'advanced':
                    return 'intermediate'
                elif base_complexity == 'intermediate':
                    return 'basic'
                else:
                    return 'basic'
            elif classification.understanding_level == 'high':
                if base_complexity == 'basic':
                    return 'intermediate'
                elif base_complexity == 'intermediate':
                    return 'advanced'
                else:
                    return 'advanced'
            
            # Maintain current complexity for moderate understanding
            return base_complexity
            
        except Exception as e:
            self.telemetry.log_error("_suggest_complexity_level", str(e))
            return 'intermediate'
    
    def _suggest_pedagogical_approach(self, classification: CoreClassification, 
                                    conversation_patterns: ConversationPatterns,
                                    metadata: ContextualMetadata) -> str:
        """Suggest pedagogical approach."""
        try:
            # Based on pedagogical opportunity
            opportunity = metadata.pedagogical_opportunity
            
            if opportunity == 'challenge_extension':
                return 'socratic_questioning'
            elif opportunity == 'foundational_clarification':
                return 'direct_instruction'
            elif opportunity == 'scaffolded_development':
                return 'guided_discovery'
            elif opportunity == 'reflective_assessment':
                return 'reflective_dialogue'
            elif opportunity == 'confidence_building':
                return 'supportive_coaching'
            else:
                return 'adaptive_teaching'
                
        except Exception as e:
            self.telemetry.log_error("_suggest_pedagogical_approach", str(e))
            return 'adaptive_teaching'
    
    # Agent context preparation methods
    
    def _prepare_socratic_context(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                                conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Any]:
        """Prepare context for Socratic tutor."""
        return {
            'questioning_level': classification.question_complexity,
            'student_understanding': classification.understanding_level,
            'engagement_level': classification.engagement_level,
            'challenge_readiness': metadata.challenge_readiness,
            'key_topics': content_analysis.key_topics,
            'pedagogical_opportunity': metadata.pedagogical_opportunity
        }
    
    def _prepare_domain_expert_context(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                                     conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Any]:
        """Prepare context for domain expert."""
        return {
            'technical_level': 'high' if classification.is_technical_question else 'moderate',
            'technical_terms': content_analysis.technical_terms,
            'explanation_need': metadata.explanation_need,
            'information_gaps': metadata.information_gaps,
            'domain_concepts': content_analysis.domain_concepts,
            'complexity_level': classification.question_complexity
        }
    
    def _prepare_analysis_context(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                                conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Any]:
        """Prepare context for analysis agent."""
        return {
            'analysis_focus': metadata.analysis_focus_areas,
            'content_complexity': content_analysis.complexity_score,
            'feedback_type': 'comprehensive' if classification.is_feedback_request else 'supportive',
            'understanding_level': classification.understanding_level,
            'technical_depth': len(content_analysis.technical_terms)
        }
    
    def _prepare_cognitive_context(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                                 conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Any]:
        """Prepare context for cognitive enhancement."""
        return {
            'confidence_level': classification.confidence_level,
            'understanding_level': classification.understanding_level,
            'challenge_readiness': metadata.challenge_readiness,
            'engagement_trend': conversation_patterns.engagement_trend,
            'cognitive_load': 'high' if content_analysis.complexity_score > 0.7 else 'moderate'
        }
    
    # Helper methods
    
    def _determine_learning_stage(self, classification: CoreClassification) -> str:
        """Determine the student's current learning stage."""
        if classification.understanding_level == 'low' and classification.confidence_level == 'low':
            return 'initial_exploration'
        elif classification.understanding_level == 'partial':
            return 'skill_development'
        elif classification.understanding_level == 'high' and classification.confidence_level == 'high':
            return 'mastery_application'
        else:
            return 'knowledge_building'
    
    def _identify_learning_style_indicators(self, classification: CoreClassification) -> List[str]:
        """Identify learning style indicators."""
        indicators = []
        
        if classification.is_technical_question:
            indicators.append('analytical_learner')
        
        if classification.engagement_level == 'high':
            indicators.append('active_learner')
        
        if classification.is_feedback_request:
            indicators.append('reflective_learner')
        
        return indicators
    
    def _assess_motivation_level(self, classification: CoreClassification) -> str:
        """Assess student motivation level."""
        if classification.engagement_level == 'high':
            return 'high'
        elif classification.engagement_level == 'low':
            return 'low'
        else:
            return 'moderate'
    
    def _identify_support_needs(self, classification: CoreClassification) -> List[str]:
        """Identify what kind of support the student needs."""
        needs = []
        
        if classification.understanding_level == 'low':
            needs.append('conceptual_support')
        
        if classification.confidence_level == 'low':
            needs.append('confidence_building')
        
        if classification.is_technical_question:
            needs.append('technical_guidance')
        
        return needs
    
    def _infer_learning_preferences(self, classification: CoreClassification, state: ArchMentorState) -> Dict[str, str]:
        """Infer learning preferences from interaction patterns."""
        preferences = {
            'interaction_style': 'balanced',
            'content_depth': 'moderate',
            'challenge_level': 'appropriate'
        }
        
        # Adjust based on classification
        if classification.engagement_level == 'high':
            preferences['interaction_style'] = 'interactive'
        
        if classification.question_complexity == 'advanced':
            preferences['content_depth'] = 'detailed'
        
        if classification.confidence_level == 'high':
            preferences['challenge_level'] = 'elevated'
        
        return preferences
    
    def _calculate_metadata_confidence(self, classification: CoreClassification, 
                                     complexity_appropriateness: str, response_urgency: str) -> float:
        """Calculate confidence in metadata generation."""
        try:
            confidence_factors = []
            
            # Classification confidence
            confidence_factors.append(classification.classification_confidence)
            
            # Clear assessments boost confidence
            if complexity_appropriateness in ['appropriate', 'too_simple', 'too_complex']:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.6)
            
            if response_urgency in ['high', 'low']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.6)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_metadata_confidence", str(e))
            return 0.6
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        return self.telemetry.get_timestamp()
    
    def _get_fallback_metadata(self) -> ContextualMetadata:
        """Return fallback metadata when generation fails."""
        return ContextualMetadata(
            complexity_appropriateness='appropriate',
            response_urgency='moderate',
            pedagogical_opportunity='general_support',
            continuation_cues=[],
            difficulty_adjustment='maintain_current',
            learning_context={'learning_stage': 'knowledge_building', 'motivation_level': 'moderate'},
            challenge_readiness='moderate',
            explanation_need='moderate',
            information_gaps=[],
            analysis_focus_areas=[],
            engagement_recommendations=['maintain_supportive_tone'],
            metadata_confidence=0.4,
            generation_timestamp=self._get_current_timestamp()
        )
    
    def _get_fallback_routing_suggestions(self) -> Dict[str, Any]:
        """Return fallback routing suggestions."""
        return {
            'primary_agent': 'domain_expert',
            'secondary_agents': ['socratic_tutor'],
            'agent_priorities': {'domain_expert': 0.6, 'socratic_tutor': 0.5},
            'routing_confidence': 0.5,
            'special_considerations': [],
            'response_style': 'balanced',
            'complexity_level': 'intermediate',
            'pedagogical_approach': 'adaptive_teaching'
        }
    
    def _get_fallback_agent_contexts(self) -> Dict[str, Dict[str, Any]]:
        """Return fallback agent contexts."""
        return {
            'socratic_tutor': {'questioning_level': 'intermediate', 'engagement_level': 'moderate'},
            'domain_expert': {'technical_level': 'moderate', 'explanation_need': 'moderate'},
            'analysis_agent': {'analysis_focus': [], 'understanding_level': 'moderate'},
            'cognitive_enhancement': {'confidence_level': 'neutral', 'challenge_readiness': 'moderate'}
        } 