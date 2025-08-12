"""
Response building processing module for creating AgentResponse objects and enhancement metrics.
"""
from typing import Dict, Any, List, Optional
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics
from ..schemas import ContextPackage, CoreClassification, ContentAnalysis, ConversationPatterns, ContextualMetadata
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class ResponseBuilderProcessor:
    """
    Processes response building and enhancement metrics calculation for context agent.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("response_builder")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def convert_to_agent_response(self, context_package: ContextPackage, current_input: str, 
                                state: ArchMentorState) -> AgentResponse:
        """
        Convert context package to AgentResponse format.
        """
        self.telemetry.log_agent_start("convert_to_agent_response")
        
        try:
            # Generate response text
            response_text = self._generate_response_text(context_package.core_classification, current_input)
            
            # Extract cognitive flags
            cognitive_flags = self._extract_cognitive_flags(context_package.core_classification)
            
            # Calculate enhancement metrics
            enhancement_metrics = self._calculate_enhancement_metrics(context_package)
            
            # Convert CoreClassification object to dictionary for compatibility
            core_classification_dict = {}
            if hasattr(context_package.core_classification, '__dict__'):
                core_classification_dict = context_package.core_classification.__dict__.copy()
            else:
                # Fallback: extract key attributes
                core_classification_dict = {
                    "interaction_type": getattr(context_package.core_classification, 'interaction_type', 'unknown'),
                    "understanding_level": getattr(context_package.core_classification, 'understanding_level', 'medium'),
                    "confidence_level": getattr(context_package.core_classification, 'confidence_level', 'confident'),
                    "engagement_level": getattr(context_package.core_classification, 'engagement_level', 'medium'),
                    "is_response_to_question": getattr(context_package.core_classification, 'is_response_to_question', False),
                    "is_technical_question": getattr(context_package.core_classification, 'is_technical_question', False),
                    "is_feedback_request": getattr(context_package.core_classification, 'is_feedback_request', False),
                    "classification_confidence": getattr(context_package.core_classification, 'classification_confidence', 0.5),
                }

            # Build complete context package dictionary (like FROMOLDREPO)
            complete_context_package = {
                "core_classification": core_classification_dict,
                "content_analysis": context_package.content_analysis.__dict__ if hasattr(context_package.content_analysis, '__dict__') else context_package.content_analysis,
                "conversation_patterns": context_package.conversation_patterns.__dict__ if hasattr(context_package.conversation_patterns, '__dict__') else context_package.conversation_patterns,
                "contextual_metadata": context_package.contextual_metadata.__dict__ if hasattr(context_package.contextual_metadata, '__dict__') else context_package.contextual_metadata,
                "routing_suggestions": context_package.routing_suggestions,
                "agent_contexts": context_package.agent_contexts,
                "context_quality": context_package.context_quality,
                "timestamp": context_package.package_timestamp
            }

            # Build the agent response
            agent_response = ResponseBuilder.create_context_analysis_response(
                response_text,
                cognitive_flags=cognitive_flags,
                enhancement_metrics=enhancement_metrics,
                metadata=complete_context_package  # Store complete context package like FROMOLDREPO
            )
            
            self.telemetry.log_agent_end("convert_to_agent_response")
            return agent_response
            
        except Exception as e:
            self.telemetry.log_error("convert_to_agent_response", str(e))
            return ResponseBuilder.create_error_response(
                f"Context analysis failed: {str(e)}",
                agent_name="context_agent"
            )
    
    def calculate_enhancement_metrics(self, context_package: ContextPackage) -> EnhancementMetrics:
        """
        Calculate enhancement metrics for the context analysis.
        """
        self.telemetry.log_agent_start("calculate_enhancement_metrics")
        
        try:
            # Calculate individual metrics
            cognitive_offloading_prevention = self._calculate_cognitive_offloading_prevention(
                context_package.core_classification
            )
            
            deep_thinking_engagement = self._calculate_deep_thinking_engagement(
                context_package.core_classification
            )
            
            knowledge_integration = self._calculate_knowledge_integration(
                context_package.content_analysis
            )
            
            learning_progression = self._calculate_learning_progression(context_package)
            
            metacognitive_awareness = self._calculate_metacognitive_awareness(
                context_package.core_classification
            )
            
            scientific_confidence = self._calculate_scientific_confidence(
                context_package.core_classification
            )
            
            scaffolding_effectiveness = self._assess_scaffolding_effectiveness(context_package)
            
            # Create enhancement metrics object
            metrics = EnhancementMetrics()
            
            self.telemetry.log_agent_end("calculate_enhancement_metrics")
            return metrics
            
        except Exception as e:
            self.telemetry.log_error("calculate_enhancement_metrics", str(e))
            return EnhancementMetrics()
    
    def extract_cognitive_flags(self, core_classification: CoreClassification) -> List[CognitiveFlag]:
        """
        Extract cognitive flags from core classification.
        """
        try:
            flags = []
            
            # Understanding level flags
            if core_classification.understanding_level == 'high':
                flags.append(CognitiveFlag.DEEP_THINKING_ENCOURAGED)
            elif core_classification.understanding_level == 'low':
                flags.append(CognitiveFlag.NEEDS_ENCOURAGEMENT)
            else:
                flags.append(CognitiveFlag.ENGAGEMENT_MAINTAINED)
            
            # Confidence level flags
            if core_classification.confidence_level == 'low':
                flags.append(CognitiveFlag.NEEDS_ENCOURAGEMENT)
            elif core_classification.confidence_level == 'high':
                flags.append(CognitiveFlag.CHALLENGE_APPROPRIATE)
            
            # Engagement level flags
            if core_classification.engagement_level == 'high':
                flags.append(CognitiveFlag.ENGAGEMENT_MAINTAINED)
            elif core_classification.engagement_level == 'low':
                flags.append(CognitiveFlag.NEEDS_ENCOURAGEMENT)
            
            # Technical question flags
            if core_classification.is_technical_question:
                flags.append(CognitiveFlag.KNOWLEDGE_INTEGRATED)
            
            # Feedback request flags
            if core_classification.is_feedback_request:
                flags.append(CognitiveFlag.METACOGNITIVE_AWARENESS)
            
            # Learning intent flags
            if core_classification.learning_intent == 'understanding':
                flags.append(CognitiveFlag.DEEP_THINKING_ENCOURAGED)
            elif core_classification.learning_intent == 'application':
                flags.append(CognitiveFlag.PRACTICAL_APPLICATION)
            
            # Ensure we have at least one flag
            if not flags:
                flags.append(CognitiveFlag.ENGAGEMENT_MAINTAINED)
            
            return flags
            
        except Exception as e:
            self.telemetry.log_error("extract_cognitive_flags", str(e))
            return [CognitiveFlag.ENGAGEMENT_MAINTAINED]
    
    def generate_response_text(self, core_classification: CoreClassification, current_input: str) -> str:
        """
        Generate response text based on classification.
        """
        try:
            # Base response structure
            response_parts = []
            
            # Acknowledgment based on interaction type
            interaction_type = core_classification.interaction_type
            
            if interaction_type == 'help_request':
                response_parts.append("I understand you're looking for help with this.")
            elif interaction_type == 'information_question':
                response_parts.append("That's an excellent question about architecture.")
            elif interaction_type == 'confusion_expression':
                response_parts.append("I can see this topic is challenging.")
            elif interaction_type == 'idea_sharing':
                response_parts.append("I appreciate you sharing your thoughts.")
            elif interaction_type == 'feedback_request':
                response_parts.append("I'd be happy to provide feedback on your approach.")
            else:
                response_parts.append("Thank you for your input.")
            
            # Understanding level response
            understanding = core_classification.understanding_level
            
            if understanding == 'low':
                response_parts.append("Let me help clarify the fundamental concepts.")
            elif understanding == 'high':
                response_parts.append("Given your strong understanding, let's explore this further.")
            elif understanding == 'partial':
                response_parts.append("You're on the right track - let's build on what you know.")
            
            # Engagement level response
            engagement = core_classification.engagement_level
            
            if engagement == 'low':
                response_parts.append("Let's make this more engaging and relevant to your interests.")
            elif engagement == 'high':
                response_parts.append("Your enthusiasm is great - let's channel it productively.")
            
            # Technical question handling
            if core_classification.is_technical_question:
                response_parts.append("This involves some technical aspects we should address carefully.")
            
            # Combine response parts
            full_response = " ".join(response_parts)
            
            # Add context-specific guidance
            if core_classification.question_complexity == 'advanced':
                full_response += " This is a complex topic that deserves thorough exploration."
            elif core_classification.question_complexity == 'basic':
                full_response += " Let's start with the basics and build from there."
            
            return full_response
            
        except Exception as e:
            self.telemetry.log_error("generate_response_text", str(e))
            return "I'm analyzing your input to provide the most helpful response."
    
    # Metrics calculation methods
    
    def _calculate_cognitive_offloading_prevention(self, classification: CoreClassification) -> float:
        """Calculate cognitive offloading prevention score."""
        try:
            prevention_score = 0.5  # Base score
            
            # High understanding suggests good cognitive engagement
            if classification.understanding_level == 'high':
                prevention_score += 0.2
            elif classification.understanding_level == 'low':
                prevention_score -= 0.1
            
            # High confidence suggests self-reliance
            if classification.confidence_level == 'high':
                prevention_score += 0.2
            elif classification.confidence_level == 'low':
                prevention_score -= 0.1
            
            # Complex questions suggest deeper thinking
            if classification.question_complexity == 'advanced':
                prevention_score += 0.2
            elif classification.question_complexity == 'basic':
                prevention_score -= 0.1
            
            # Independent learning intent
            if classification.learning_intent in ['exploration', 'application']:
                prevention_score += 0.1
            
            return max(0.0, min(1.0, prevention_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_cognitive_offloading_prevention", str(e))
            return 0.5
    
    def _calculate_deep_thinking_engagement(self, classification: CoreClassification) -> float:
        """Calculate deep thinking engagement score."""
        try:
            engagement_score = 0.5  # Base score
            
            # High engagement indicates deeper thinking
            if classification.engagement_level == 'high':
                engagement_score += 0.3
            elif classification.engagement_level == 'low':
                engagement_score -= 0.2
            
            # Complex questions indicate deeper thinking
            if classification.question_complexity == 'advanced':
                engagement_score += 0.2
            
            # Technical questions suggest analytical thinking
            if classification.is_technical_question:
                engagement_score += 0.1
            
            # Feedback requests suggest reflective thinking
            if classification.is_feedback_request:
                engagement_score += 0.1
            
            return max(0.0, min(1.0, engagement_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_deep_thinking_engagement", str(e))
            return 0.5
    
    def _calculate_knowledge_integration(self, content_analysis: ContentAnalysis) -> float:
        """Calculate knowledge integration score."""
        try:
            integration_score = 0.5  # Base score
            
            # Technical terms suggest knowledge integration
            technical_term_count = len(content_analysis.technical_terms)
            if technical_term_count >= 3:
                integration_score += 0.3
            elif technical_term_count >= 1:
                integration_score += 0.1
            
            # Domain concepts suggest deeper integration
            domain_concept_count = len(content_analysis.domain_concepts)
            if domain_concept_count >= 2:
                integration_score += 0.2
            
            # High complexity suggests integrated thinking
            if content_analysis.complexity_score > 0.7:
                integration_score += 0.2
            
            # High information density suggests knowledge synthesis
            if content_analysis.information_density > 0.6:
                integration_score += 0.1
            
            return max(0.0, min(1.0, integration_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_knowledge_integration", str(e))
            return 0.5
    
    def _calculate_learning_progression(self, context_package: ContextPackage) -> float:
        """Calculate learning progression score."""
        try:
            progression_score = 0.5  # Base score
            
            # Understanding progression
            if hasattr(context_package, 'conversation_patterns'):
                understanding_progression = context_package.conversation_patterns.understanding_progression
                if understanding_progression == 'improving':
                    progression_score += 0.3
                elif understanding_progression == 'declining':
                    progression_score -= 0.2
            
            # Engagement trend
            if hasattr(context_package, 'conversation_patterns'):
                engagement_trend = context_package.conversation_patterns.engagement_trend
                if engagement_trend == 'increasing':
                    progression_score += 0.2
                elif engagement_trend == 'decreasing':
                    progression_score -= 0.1
            
            # Question complexity as progression indicator
            if context_package.core_classification.question_complexity == 'advanced':
                progression_score += 0.1
            
            return max(0.0, min(1.0, progression_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_learning_progression", str(e))
            return 0.5
    
    def _calculate_metacognitive_awareness(self, classification: CoreClassification) -> float:
        """Calculate metacognitive awareness score."""
        try:
            awareness_score = 0.5  # Base score
            
            # Feedback requests indicate metacognitive awareness
            if classification.is_feedback_request:
                awareness_score += 0.3
            
            # Self-reflection in learning intent
            if classification.learning_intent == 'validation':
                awareness_score += 0.2
            
            # Confidence level awareness
            if classification.confidence_level in ['low', 'high']:  # Clear self-assessment
                awareness_score += 0.1
            
            # Understanding level awareness
            if classification.understanding_level in ['low', 'high']:  # Clear self-assessment
                awareness_score += 0.1
            
            return max(0.0, min(1.0, awareness_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_metacognitive_awareness", str(e))
            return 0.5
    
    def _calculate_scientific_confidence(self, classification: CoreClassification) -> float:
        """Calculate scientific confidence in the analysis."""
        try:
            # Use the classification confidence as base
            base_confidence = classification.classification_confidence
            
            # Adjust based on clear indicators
            confidence_adjustments = 0
            
            if classification.is_technical_question:
                confidence_adjustments += 0.1
            
            if classification.is_feedback_request:
                confidence_adjustments += 0.1
            
            if classification.interaction_type in ['help_request', 'information_question', 'confusion_expression']:
                confidence_adjustments += 0.1
            
            final_confidence = base_confidence + confidence_adjustments
            return max(0.0, min(1.0, final_confidence))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_scientific_confidence", str(e))
            return 0.6
    
    def _assess_scaffolding_effectiveness(self, context_package: ContextPackage) -> float:
        """Assess scaffolding effectiveness."""
        try:
            effectiveness_score = 0.5  # Base score
            
            # Appropriate complexity suggests good scaffolding
            if hasattr(context_package, 'contextual_metadata'):
                complexity_appropriateness = context_package.contextual_metadata.complexity_appropriateness
                if complexity_appropriateness == 'appropriate':
                    effectiveness_score += 0.2
                elif complexity_appropriateness in ['too_simple', 'too_complex']:
                    effectiveness_score -= 0.1
            
            # Engagement level suggests scaffolding success
            engagement = context_package.core_classification.engagement_level
            if engagement == 'high':
                effectiveness_score += 0.2
            elif engagement == 'low':
                effectiveness_score -= 0.1
            
            # Understanding level progression
            if hasattr(context_package, 'conversation_patterns'):
                understanding_progression = context_package.conversation_patterns.understanding_progression
                if understanding_progression == 'improving':
                    effectiveness_score += 0.2
                elif understanding_progression == 'declining':
                    effectiveness_score -= 0.2
            
            return max(0.0, min(1.0, effectiveness_score))
            
        except Exception as e:
            self.telemetry.log_error("_assess_scaffolding_effectiveness", str(e))
            return 0.5
    
    # Helper methods
    
    def _generate_response_text(self, classification: CoreClassification, current_input: str) -> str:
        """Generate response text (delegates to public method)."""
        return self.generate_response_text(classification, current_input)
    
    def _extract_cognitive_flags(self, classification: CoreClassification) -> List[CognitiveFlag]:
        """Extract cognitive flags (delegates to public method)."""
        return self.extract_cognitive_flags(classification)
    
    def _calculate_enhancement_metrics(self, context_package: ContextPackage) -> EnhancementMetrics:
        """Calculate enhancement metrics (delegates to public method)."""
        return self.calculate_enhancement_metrics(context_package)
    
    def _convert_engagement_to_score(self, engagement_level: str) -> float:
        """Convert engagement level to numerical score."""
        engagement_mapping = {
            'high': 0.9,
            'moderate': 0.6,
            'low': 0.3
        }
        return engagement_mapping.get(engagement_level, 0.5)
    
    def _assess_cognitive_load_from_context(self, context_package: ContextPackage) -> float:
        """Assess cognitive load from context package."""
        try:
            load_factors = []
            
            # Content complexity contributes to cognitive load
            complexity_score = context_package.content_analysis.complexity_score
            load_factors.append(complexity_score)
            
            # Technical terms increase cognitive load
            technical_term_count = len(context_package.content_analysis.technical_terms)
            technical_load = min(technical_term_count / 5.0, 1.0)
            load_factors.append(technical_load)
            
            # Question complexity affects load
            complexity_mapping = {'basic': 0.3, 'intermediate': 0.6, 'advanced': 0.9}
            question_load = complexity_mapping.get(
                context_package.core_classification.question_complexity, 0.5
            )
            load_factors.append(question_load)
            
            # Information density affects load
            density_load = context_package.content_analysis.information_density
            load_factors.append(density_load)
            
            return sum(load_factors) / len(load_factors)
            
        except Exception as e:
            self.telemetry.log_error("_assess_cognitive_load_from_context", str(e))
            return 0.5
    
    def _get_interaction_count(self, context_package: ContextPackage) -> int:
        """Get interaction count from context package."""
        try:
            if hasattr(context_package, 'conversation_patterns'):
                metrics = context_package.conversation_patterns.conversation_metrics
                return int(metrics.get('total_messages', 1))
            return 1
            
        except Exception as e:
            self.telemetry.log_error("_get_interaction_count", str(e))
            return 1
    
    def create_context_summary(self, context_package: ContextPackage) -> str:
        """Create a summary of the context analysis."""
        try:
            classification = context_package.core_classification
            content = context_package.content_analysis
            
            summary = f"Context Analysis Summary:\n"
            summary += f"• Interaction: {classification.interaction_type}\n"
            summary += f"• Understanding: {classification.understanding_level}\n"
            summary += f"• Engagement: {classification.engagement_level}\n"
            summary += f"• Complexity: {classification.question_complexity}\n"
            summary += f"• Technical Terms: {len(content.technical_terms)}\n"
            summary += f"• Content Quality: {content.content_quality}\n"
            
            if hasattr(context_package, 'contextual_metadata'):
                summary += f"• Pedagogical Opportunity: {context_package.contextual_metadata.pedagogical_opportunity}\n"
                summary += f"• Response Urgency: {context_package.contextual_metadata.response_urgency}\n"
            
            if hasattr(context_package, 'routing_suggestions'):
                summary += f"• Primary Agent: {context_package.routing_suggestions.get('primary_agent', 'unknown')}\n"
            
            return summary
            
        except Exception as e:
            self.telemetry.log_error("create_context_summary", str(e))
            return "Context analysis summary unavailable."
    
    def validate_response_structure(self, agent_response: AgentResponse) -> bool:
        """Validate the structure of the agent response."""
        try:
            # Check required fields
            if not hasattr(agent_response, 'response_text') or not agent_response.response_text:
                return False
            
            if not hasattr(agent_response, 'response_type'):
                return False
            
            if not hasattr(agent_response, 'enhancement_metrics'):
                return False
            
            if not hasattr(agent_response, 'cognitive_flags'):
                return False
            
            # Check response text quality
            if len(agent_response.response_text.strip()) < 10:
                return False
            
            return True
            
        except Exception as e:
            self.telemetry.log_error("validate_response_structure", str(e))
            return False
    
    def assess_context_quality(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> float:
        """Assess the overall quality of the context analysis."""
        try:
            quality_factors = []
            
            # Classification confidence
            quality_factors.append(classification.classification_confidence)
            
            # Content analysis confidence
            quality_factors.append(content_analysis.analysis_confidence)
            
            # Content richness
            content_richness = min(len(content_analysis.technical_terms) / 3.0, 1.0)
            quality_factors.append(content_richness)
            
            # Information density
            quality_factors.append(content_analysis.information_density)
            
            # Complexity appropriateness
            if content_analysis.complexity_score > 0.2:  # Not too simple
                quality_factors.append(0.7)
            else:
                quality_factors.append(0.4)
            
            return sum(quality_factors) / len(quality_factors)
            
        except Exception as e:
            self.telemetry.log_error("assess_context_quality", str(e))
            return 0.6 