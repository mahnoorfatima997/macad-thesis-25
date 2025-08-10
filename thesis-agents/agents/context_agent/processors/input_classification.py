"""
Input classification processing module for analyzing and classifying student input.
"""
from typing import Dict, Any, List, Optional
from ..schemas import CoreClassification
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class InputClassificationProcessor:
    """
    Processes input classification and understanding level detection.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("input_classification")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    async def perform_core_classification(self, input_text: str, state: ArchMentorState) -> CoreClassification:
        """
        Perform comprehensive core classification of student input.
        """
        self.telemetry.log_agent_start("perform_core_classification")
        
        try:
            input_lower = input_text.lower()
            
            # Classify different aspects of the input
            interaction_type = self._classify_interaction_type(input_text, state)
            understanding_level = self._detect_understanding_level(input_lower)
            confidence_level = self._assess_confidence_level(input_lower)
            engagement_level = self._detect_engagement_level(input_lower, input_text)
            
            # Additional classification aspects
            is_response_to_previous = self._is_response_to_previous_question(input_text, state)
            is_technical_question = self._is_technical_question(input_text)
            is_feedback_request = self._is_feedback_request(input_text)
            
            # Assess question complexity
            question_complexity = self._assess_question_complexity(input_text)
            
            # Detect learning intent
            learning_intent = self._detect_learning_intent(input_text)
            
            # Assess context dependency
            context_dependency = self._assess_context_dependency(input_text, state)
            
            classification = CoreClassification(
                interaction_type=interaction_type,
                understanding_level=understanding_level,
                confidence_level=confidence_level,
                engagement_level=engagement_level,
                is_response_to_question=is_response_to_previous,
            )
            # Attach extended fields dynamically to preserve richer data
            classification.is_technical_question = is_technical_question
            classification.is_feedback_request = is_feedback_request
            classification.question_complexity = question_complexity
            classification.learning_intent = learning_intent
            classification.context_dependency = context_dependency
            classification.classification_confidence = self._calculate_classification_confidence(
                interaction_type, understanding_level, confidence_level, engagement_level
            )
            
            self.telemetry.log_agent_end("perform_core_classification")
            return classification
            
        except Exception as e:
            self.telemetry.log_error("perform_core_classification", str(e))
            return self._get_fallback_classification()
    
    def _classify_interaction_type(self, input_text: str, state: ArchMentorState = None) -> str:
        """Classify the type of interaction based on input patterns."""
        try:
            input_lower = input_text.lower()
            
            # Question patterns
            question_indicators = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
            if any(indicator in input_lower for indicator in question_indicators) or input_text.endswith('?'):
                # Determine question type
                if any(word in input_lower for word in ['help', 'explain', 'show', 'teach']):
                    return 'help_request'
                elif any(word in input_lower for word in ['example', 'case', 'instance']):
                    return 'example_request'
                elif any(word in input_lower for word in ['compare', 'difference', 'versus']):
                    return 'comparison_question'
                else:
                    return 'information_question'
            
            # Statement patterns
            elif any(word in input_lower for word in ['i think', 'i believe', 'my idea', 'my approach']):
                return 'idea_sharing'
            elif any(word in input_lower for word in ['i understand', 'i see', 'makes sense', 'got it']):
                return 'understanding_confirmation'
            elif any(word in input_lower for word in ['i don\'t understand', 'confused', 'unclear']):
                return 'confusion_expression'
            elif any(word in input_lower for word in ['thanks', 'thank you', 'helpful']):
                return 'acknowledgment'
            elif any(word in input_lower for word in ['let me try', 'i will', 'i\'m going to']):
                return 'action_intent'
            else:
                return 'general_statement'
                
        except Exception as e:
            self.telemetry.log_error("_classify_interaction_type", str(e))
            return 'general_statement'
    
    def _detect_understanding_level(self, input_lower: str) -> str:
        """Detect the student's understanding level from their input."""
        try:
            # High understanding indicators
            high_understanding = [
                'i understand', 'makes sense', 'i see how', 'clear', 'obvious',
                'integration', 'relationship', 'connection', 'implication'
            ]
            
            # Low understanding indicators
            low_understanding = [
                'don\'t understand', 'confused', 'unclear', 'what does', 'what is',
                'help me', 'i\'m lost', 'no idea', 'don\'t know'
            ]
            
            # Partial understanding indicators
            partial_understanding = [
                'i think', 'maybe', 'not sure', 'seems like', 'partially',
                'somewhat', 'kind of', 'sort of'
            ]
            
            high_count = sum(1 for indicator in high_understanding if indicator in input_lower)
            low_count = sum(1 for indicator in low_understanding if indicator in input_lower)
            partial_count = sum(1 for indicator in partial_understanding if indicator in input_lower)
            
            if high_count > 0:
                return 'high'
            elif low_count > 0:
                return 'low'
            elif partial_count > 0:
                return 'partial'
            else:
                return 'moderate'
                
        except Exception as e:
            self.telemetry.log_error("_detect_understanding_level", str(e))
            return 'moderate'
    
    def _assess_confidence_level(self, input_lower: str) -> str:
        """Assess the student's confidence level from their input."""
        try:
            # High confidence indicators
            high_confidence = [
                'definitely', 'certainly', 'sure', 'confident', 'know that',
                'obviously', 'clearly', 'without doubt', 'absolutely'
            ]
            
            # Low confidence indicators
            low_confidence = [
                'not sure', 'maybe', 'i think', 'possibly', 'might be',
                'uncertain', 'doubt', 'hesitant', 'worried', 'afraid'
            ]
            
            # Moderate confidence indicators
            moderate_confidence = [
                'believe', 'seems', 'appears', 'likely', 'probably',
                'assume', 'suppose', 'expect'
            ]
            
            high_count = sum(1 for indicator in high_confidence if indicator in input_lower)
            low_count = sum(1 for indicator in low_confidence if indicator in input_lower)
            moderate_count = sum(1 for indicator in moderate_confidence if indicator in input_lower)
            
            if high_count > 0:
                return 'high'
            elif low_count > 0:
                return 'low'
            elif moderate_count > 0:
                return 'moderate'
            else:
                return 'neutral'
                
        except Exception as e:
            self.telemetry.log_error("_assess_confidence_level", str(e))
            return 'neutral'
    
    def _detect_engagement_level(self, input_lower: str, input_text: str) -> str:
        """Detect the student's engagement level from their input."""
        try:
            # High engagement indicators
            high_engagement = [
                'interesting', 'fascinating', 'curious', 'excited', 'love',
                'amazing', 'wonderful', 'explore', 'discover', 'learn more'
            ]
            
            # Low engagement indicators
            low_engagement = [
                'boring', 'tired', 'bored', 'uninteresting', 'don\'t care',
                'whatever', 'fine', 'okay', 'sure'
            ]
            
            # Message length as engagement indicator
            word_count = len(input_text.split())
            question_marks = input_text.count('?')
            exclamation_marks = input_text.count('!')
            
            high_count = sum(1 for indicator in high_engagement if indicator in input_lower)
            low_count = sum(1 for indicator in low_engagement if indicator in input_lower)
            
            # Calculate engagement score
            engagement_score = 0
            
            if high_count > 0:
                engagement_score += 2
            if low_count > 0:
                engagement_score -= 2
            if word_count > 20:
                engagement_score += 1
            if question_marks > 0:
                engagement_score += 1
            if exclamation_marks > 0:
                engagement_score += 1
            
            if engagement_score >= 2:
                return 'high'
            elif engagement_score <= -1:
                return 'low'
            else:
                return 'moderate'
                
        except Exception as e:
            self.telemetry.log_error("_detect_engagement_level", str(e))
            return 'moderate'
    
    def _is_response_to_previous_question(self, current_input: str, state: ArchMentorState) -> bool:
        """Check if current input is a response to a previous question."""
        try:
            if not hasattr(state, 'messages') or not state.messages:
                return False
            
            # Get the last assistant message
            assistant_messages = [msg for msg in state.messages if msg.get('role') == 'assistant']
            if not assistant_messages:
                return False
            
            last_assistant_message = assistant_messages[-1].get('content', '').lower()
            
            # Check if last assistant message contained a question
            question_indicators = ['?', 'what do you think', 'how would you', 'can you', 'would you']
            has_question = any(indicator in last_assistant_message for indicator in question_indicators)
            
            if not has_question:
                return False
            
            # Check if current input is a direct response
            current_lower = current_input.lower()
            response_indicators = [
                'yes', 'no', 'i would', 'i think', 'my answer', 'i believe',
                'in my opinion', 'i feel', 'i suppose', 'i guess'
            ]
            
            return any(indicator in current_lower for indicator in response_indicators)
            
        except Exception as e:
            self.telemetry.log_error("_is_response_to_previous_question", str(e))
            return False
    
    def _is_technical_question(self, input_text: str) -> bool:
        """Check if the input is a technical question."""
        try:
            technical_terms = [
                'calculation', 'formula', 'equation', 'specification', 'standard',
                'code', 'regulation', 'engineering', 'structural', 'mechanical',
                'electrical', 'hvac', 'plumbing', 'foundation', 'load', 'stress',
                'material', 'concrete', 'steel', 'timber', 'insulation'
            ]
            
            input_lower = input_text.lower()
            technical_count = sum(1 for term in technical_terms if term in input_lower)
            
            # Also check for technical question patterns
            technical_patterns = [
                'how to calculate', 'what is the formula', 'how do you design',
                'what are the requirements', 'how do you determine'
            ]
            
            pattern_match = any(pattern in input_lower for pattern in technical_patterns)
            
            return technical_count >= 2 or pattern_match
            
        except Exception as e:
            self.telemetry.log_error("_is_technical_question", str(e))
            return False
    
    def _is_feedback_request(self, input_text: str) -> bool:
        """Check if the input is requesting feedback."""
        try:
            feedback_indicators = [
                'what do you think', 'is this right', 'is this correct', 'feedback',
                'review', 'check', 'evaluate', 'assess', 'critique', 'opinion',
                'thoughts', 'comments', 'suggestions', 'advice'
            ]
            
            input_lower = input_text.lower()
            return any(indicator in input_lower for indicator in feedback_indicators)
            
        except Exception as e:
            self.telemetry.log_error("_is_feedback_request", str(e))
            return False
    
    def _assess_question_complexity(self, input_text: str) -> str:
        """Assess the complexity level of the question."""
        try:
            input_lower = input_text.lower()
            
            # Simple question indicators
            simple_indicators = [
                'what is', 'who is', 'when is', 'where is', 'how do i',
                'can you tell me', 'what does', 'define'
            ]
            
            # Complex question indicators
            complex_indicators = [
                'how would you integrate', 'what are the implications', 'compare and contrast',
                'analyze', 'evaluate', 'synthesize', 'relationship between',
                'why do you think', 'what if', 'how might'
            ]
            
            # Advanced question indicators
            advanced_indicators = [
                'optimization', 'trade-offs', 'systematic approach', 'methodology',
                'framework', 'comprehensive analysis', 'interdisciplinary'
            ]
            
            simple_count = sum(1 for indicator in simple_indicators if indicator in input_lower)
            complex_count = sum(1 for indicator in complex_indicators if indicator in input_lower)
            advanced_count = sum(1 for indicator in advanced_indicators if indicator in input_lower)
            
            # Also consider word count and sentence structure
            word_count = len(input_text.split())
            sentence_count = len([s for s in input_text.split('.') if s.strip()])
            
            if advanced_count > 0 or (word_count > 30 and sentence_count > 2):
                return 'advanced'
            elif complex_count > 0 or (word_count > 15 and sentence_count > 1):
                return 'intermediate'
            elif simple_count > 0 or word_count <= 10:
                return 'basic'
            else:
                return 'intermediate'
                
        except Exception as e:
            self.telemetry.log_error("_assess_question_complexity", str(e))
            return 'intermediate'
    
    def _detect_learning_intent(self, input_text: str) -> str:
        """Detect the student's learning intent."""
        try:
            input_lower = input_text.lower()
            
            # Different learning intents
            understanding_intent = [
                'understand', 'learn', 'explain', 'clarify', 'help me grasp',
                'make sense of', 'comprehend'
            ]
            
            application_intent = [
                'how to apply', 'use in practice', 'implement', 'put into practice',
                'real world', 'practical', 'hands-on'
            ]
            
            exploration_intent = [
                'explore', 'investigate', 'discover', 'find out', 'research',
                'look into', 'examine'
            ]
            
            problem_solving_intent = [
                'solve', 'fix', 'resolve', 'address', 'tackle', 'deal with',
                'overcome', 'handle'
            ]
            
            validation_intent = [
                'validate', 'verify', 'confirm', 'check', 'ensure', 'make sure',
                'is this right', 'am i correct'
            ]
            
            # Count matches for each intent
            intent_scores = {
                'understanding': sum(1 for indicator in understanding_intent if indicator in input_lower),
                'application': sum(1 for indicator in application_intent if indicator in input_lower),
                'exploration': sum(1 for indicator in exploration_intent if indicator in input_lower),
                'problem_solving': sum(1 for indicator in problem_solving_intent if indicator in input_lower),
                'validation': sum(1 for indicator in validation_intent if indicator in input_lower)
            }
            
            # Return the intent with the highest score
            if max(intent_scores.values()) > 0:
                return max(intent_scores, key=intent_scores.get)
            else:
                return 'general_inquiry'
                
        except Exception as e:
            self.telemetry.log_error("_detect_learning_intent", str(e))
            return 'general_inquiry'
    
    def _assess_context_dependency(self, input_text: str, state: ArchMentorState) -> str:
        """Assess how much the input depends on previous context."""
        try:
            input_lower = input_text.lower()
            
            # High context dependency indicators
            high_context = [
                'this', 'that', 'it', 'they', 'them', 'these', 'those',
                'the previous', 'what you said', 'your explanation', 'earlier',
                'before', 'above', 'mentioned'
            ]
            
            # Low context dependency indicators (self-contained)
            low_context = [
                'what is', 'how do', 'can you explain', 'i want to know',
                'tell me about', 'help me understand'
            ]
            
            high_count = sum(1 for indicator in high_context if indicator in input_lower)
            low_count = sum(1 for indicator in low_context if indicator in input_lower)
            
            # Also consider if input is very short (likely context-dependent)
            word_count = len(input_text.split())
            
            if high_count >= 2 or word_count <= 5:
                return 'high'
            elif low_count >= 1 and word_count >= 10:
                return 'low'
            else:
                return 'medium'
                
        except Exception as e:
            self.telemetry.log_error("_assess_context_dependency", str(e))
            return 'medium'
    
    def _calculate_classification_confidence(self, interaction_type: str, understanding_level: str,
                                          confidence_level: str, engagement_level: str) -> float:
        """Calculate confidence in the classification results."""
        try:
            confidence_factors = []
            
            # Interaction type confidence
            if interaction_type in ['help_request', 'information_question', 'confusion_expression']:
                confidence_factors.append(0.8)  # Clear patterns
            else:
                confidence_factors.append(0.6)  # Less clear patterns
            
            # Understanding level confidence
            if understanding_level in ['high', 'low']:
                confidence_factors.append(0.8)  # Clear indicators
            else:
                confidence_factors.append(0.6)  # Moderate indicators
            
            # Confidence level confidence
            if confidence_level in ['high', 'low']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Engagement level confidence
            if engagement_level in ['high', 'low']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_classification_confidence", str(e))
            return 0.6
    
    def _get_fallback_classification(self) -> CoreClassification:
        """Return fallback classification when analysis fails."""
        fallback = CoreClassification(
            interaction_type='general_statement',
            understanding_level='moderate',
            confidence_level='neutral',
            engagement_level='moderate',
            is_response_to_question=False,
        )
        fallback.is_technical_question = False
        fallback.is_feedback_request = False
        fallback.question_complexity = 'intermediate'
        fallback.learning_intent = 'general_inquiry'
        fallback.context_dependency = 'medium'
        fallback.classification_confidence = 0.4
        return fallback
    
    def validate_classification(self, classification: CoreClassification) -> bool:
        """Validate the classification results."""
        try:
            # Check required fields
            required_fields = [
                'interaction_type', 'understanding_level', 'confidence_level',
                'engagement_level', 'question_complexity', 'learning_intent'
            ]
            
            for field in required_fields:
                if not hasattr(classification, field) or getattr(classification, field) is None:
                    return False
            
            # Check confidence score
            if not hasattr(classification, 'classification_confidence'):
                return False
            
            confidence = classification.classification_confidence
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                return False
            
            return True
            
        except Exception as e:
            self.telemetry.log_error("validate_classification", str(e))
            return False
    
    def get_classification_summary(self, classification: CoreClassification) -> str:
        """Generate a summary of the classification results."""
        try:
            summary = f"Input Classification Summary:\n"
            summary += f"• Type: {classification.interaction_type}\n"
            summary += f"• Understanding: {classification.understanding_level}\n"
            summary += f"• Confidence: {classification.confidence_level}\n"
            summary += f"• Engagement: {classification.engagement_level}\n"
            summary += f"• Complexity: {classification.question_complexity}\n"
            summary += f"• Intent: {classification.learning_intent}\n"
            summary += f"• Context Dependency: {classification.context_dependency}\n"
            summary += f"• Classification Confidence: {classification.classification_confidence:.2f}"
            
            return summary
            
        except Exception as e:
            self.telemetry.log_error("get_classification_summary", str(e))
            return "Classification summary unavailable." 