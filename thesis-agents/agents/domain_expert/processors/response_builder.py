"""
Response building processing module for creating AgentResponse objects and enhancement metrics.
"""
from typing import Dict, Any, List, Optional
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class ResponseBuilderProcessor:
    """
    Processes response building and enhancement metrics calculation.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("response_builder")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def convert_to_agent_response(self, knowledge_response: Dict[str, Any], 
                                state: ArchMentorState, context_classification: Dict,
                                analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """
        Convert knowledge response to AgentResponse format.
        """
        self.telemetry.log_agent_start("convert_to_agent_response")
        
        try:
            # Extract main response text
            response_text = self._extract_response_text(knowledge_response)
            
            # Calculate enhancement metrics
            enhancement_metrics = self._calculate_enhancement_metrics(
                knowledge_response, state, analysis_result
            )
            
            # Extract cognitive flags
            cognitive_flags = self._extract_cognitive_flags(
                knowledge_response, state, context_classification
            )
            
            # Convert cognitive flags to proper format
            converted_flags = self._convert_cognitive_flags(cognitive_flags)
            
            # Build the agent response
            agent_response = ResponseBuilder.create_knowledge_response(
                response_text,
                sources_used=knowledge_response.get('sources', []),
                metadata={
                    'source_count': knowledge_response.get('source_count', 0),
                    'synthesis_quality': knowledge_response.get('synthesis_quality', 'medium')
                }
            )
            # Preserve enhancement metrics and flags on the response
            agent_response.enhancement_metrics = enhancement_metrics
            agent_response.cognitive_flags = converted_flags
            
            self.telemetry.log_agent_end("convert_to_agent_response")
            return agent_response
            
        except Exception as e:
            self.telemetry.log_error("convert_to_agent_response", str(e))
            return ResponseBuilder.create_error_response(
                f"Knowledge response conversion failed: {str(e)}",
                agent_name="domain_expert"
            )
    
    def calculate_enhancement_metrics(self, knowledge_response: Dict[str, Any],
                                    state: ArchMentorState, analysis_result: Dict) -> EnhancementMetrics:
        """
        Calculate enhancement metrics for the knowledge response.
        """
        self.telemetry.log_agent_start("calculate_enhancement_metrics")
        
        try:
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(knowledge_response)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(knowledge_response, state)
            
            # Calculate learning velocity
            learning_velocity = self._calculate_learning_velocity(state, analysis_result)
            
            # Calculate cognitive load
            cognitive_load = self._calculate_cognitive_load(knowledge_response)
            
            # Calculate analysis depth
            analysis_depth = self._calculate_analysis_depth(knowledge_response)
            
            # Get interaction count
            interaction_count = len(state.messages) if hasattr(state, 'messages') else 0
            
            # Map computed values into our standardized EnhancementMetrics
            overall = (
                (1 - min(max(cognitive_load, 0.0), 1.0)) * 0.2 +
                min(max(engagement_score, 0.0), 1.0) * 0.2 +
                min(max(learning_velocity, 0.0), 1.0) * 0.2 +
                min(max(complexity_score, 0.0), 1.0) * 0.2 +
                min(max(analysis_depth, 0.0), 1.0) * 0.2
            )
            metrics = EnhancementMetrics(
                cognitive_offloading_prevention_score=max(0.0, 1.0 - cognitive_load),
                deep_thinking_engagement_score=min(max(engagement_score, 0.0), 1.0),
                knowledge_integration_score=min(max(analysis_depth, 0.0), 1.0),
                scaffolding_effectiveness_score=min(max((engagement_score + (1 - cognitive_load)) / 2, 0.0), 1.0),
                learning_progression_score=min(max(learning_velocity, 0.0), 1.0),
                metacognitive_awareness_score=min(max((engagement_score + complexity_score) / 2, 0.0), 1.0),
                overall_cognitive_score=min(max(overall, 0.0), 1.0),
                scientific_confidence=0.7
            )
            
            self.telemetry.log_agent_end("calculate_enhancement_metrics")
            return metrics
            
        except Exception as e:
            self.telemetry.log_error("calculate_enhancement_metrics", str(e))
            return EnhancementMetrics()
    
    def extract_cognitive_flags(self, knowledge_response: Dict[str, Any],
                               state: ArchMentorState, context_classification: Dict) -> List[str]:
        """
        Extract cognitive flags from knowledge response and context.
        """
        try:
            flags = []
            
            # Knowledge quality flags
            source_count = knowledge_response.get('source_count', 0)
            if source_count > 3:
                flags.append('comprehensive_knowledge')
            elif source_count > 1:
                flags.append('adequate_knowledge')
            else:
                flags.append('limited_knowledge')
            
            # Response quality flags
            response_quality = knowledge_response.get('synthesis_quality', 'medium')
            if response_quality == 'high':
                flags.append('high_quality_response')
            elif response_quality == 'medium':
                flags.append('adequate_response')
            else:
                flags.append('basic_response')
            
            # Learning support flags
            if knowledge_response.get('follow_up_questions'):
                flags.append('learning_support')
            
            if knowledge_response.get('examples') or knowledge_response.get('formatted_examples'):
                flags.append('examples_provided')
            
            # Context appropriateness flags
            building_type = context_classification.get('building_type', 'general')
            if building_type != 'general':
                flags.append('context_specific')
            
            # Engagement flags
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if user_messages and len(user_messages[-1].split()) > 10:
                flags.append('engaged_user')
            
            return flags
            
        except Exception as e:
            self.telemetry.log_error("extract_cognitive_flags", str(e))
            return ['basic_response']
    
    def convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """
        Convert string flags to CognitiveFlag enums.
        """
        try:
            flag_mapping = {
                'comprehensive_knowledge': CognitiveFlag.KNOWLEDGE_INTEGRATED,
                'adequate_knowledge': CognitiveFlag.KNOWLEDGE_INTEGRATED,
                'limited_knowledge': CognitiveFlag.NEEDS_ENCOURAGEMENT,
                'high_quality_response': CognitiveFlag.DEEP_THINKING_ENCOURAGED,
                'adequate_response': CognitiveFlag.ENGAGEMENT_MAINTAINED,
                'basic_response': CognitiveFlag.NEEDS_ENCOURAGEMENT,
                'learning_support': CognitiveFlag.METACOGNITIVE_AWARENESS,
                'examples_provided': CognitiveFlag.PRACTICAL_APPLICATION,
                'context_specific': CognitiveFlag.CONTEXT_AWARENESS,
                'engaged_user': CognitiveFlag.ENGAGEMENT_MAINTAINED
            }
            
            converted_flags = []
            for flag in cognitive_flags:
                if flag in flag_mapping:
                    converted_flags.append(flag_mapping[flag])
                else:
                    converted_flags.append(CognitiveFlag.NEEDS_ENCOURAGEMENT)
            
            # Ensure we have at least one flag
            if not converted_flags:
                converted_flags.append(CognitiveFlag.NEEDS_ENCOURAGEMENT)
            
            return converted_flags
            
        except Exception as e:
            self.telemetry.log_error("convert_cognitive_flags", str(e))
            return [CognitiveFlag.NEEDS_ENCOURAGEMENT]
    
    # Helper methods for metrics calculation
    
    def _extract_response_text(self, knowledge_response: Dict[str, Any]) -> str:
        """Extract main response text from knowledge response."""
        # Try different possible text fields
        text_fields = [
            'educational_response',
            'main_content', 
            'knowledge_summary',
            'response_text'
        ]
        
        for field in text_fields:
            if field in knowledge_response and knowledge_response[field]:
                text = knowledge_response[field]
                if isinstance(text, str) and len(text.strip()) > 20:
                    return text.strip()
        
        # Fallback to topic-based response
        topic = knowledge_response.get('topic', 'architectural knowledge')
        return f"Here's information about {topic} in architectural design and practice."
    
    def _calculate_complexity_score(self, knowledge_response: Dict[str, Any]) -> float:
        """Calculate complexity score based on response content."""
        try:
            complexity_indicators = []
            
            # Source diversity
            source_count = knowledge_response.get('source_count', 0)
            source_complexity = min(source_count / 5.0, 1.0)
            complexity_indicators.append(source_complexity)
            
            # Content depth
            main_content = knowledge_response.get('educational_response', '') or knowledge_response.get('main_content', '')
            if main_content:
                word_count = len(main_content.split())
                depth_complexity = min(word_count / 200.0, 1.0)
                complexity_indicators.append(depth_complexity)
            
            # Technical content
            technical_terms = ['specification', 'engineering', 'technical', 'analysis', 'calculation']
            technical_count = 0
            for content in [knowledge_response.get('educational_response', ''), knowledge_response.get('main_content', '')]:
                if content:
                    technical_count += sum(1 for term in technical_terms if term.lower() in content.lower())
            
            technical_complexity = min(technical_count / 3.0, 1.0)
            complexity_indicators.append(technical_complexity)
            
            # Synthesis quality
            quality = knowledge_response.get('synthesis_quality', 'medium')
            quality_complexity = {'basic': 0.3, 'medium': 0.6, 'high': 0.9}.get(quality, 0.5)
            complexity_indicators.append(quality_complexity)
            
            return sum(complexity_indicators) / len(complexity_indicators)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_complexity_score", str(e))
            return 0.5
    
    def _calculate_engagement_score(self, knowledge_response: Dict[str, Any], state: ArchMentorState) -> float:
        """Calculate engagement score based on response and context."""
        try:
            engagement_factors = []
            
            # Interactive elements
            follow_up_questions = knowledge_response.get('follow_up_questions', [])
            if follow_up_questions:
                engagement_factors.append(0.8)
            else:
                engagement_factors.append(0.4)
            
            # Examples and practical content
            examples = knowledge_response.get('examples', [])
            if examples:
                engagement_factors.append(0.7)
            else:
                engagement_factors.append(0.3)
            
            # Contextual relevance
            contextual_insights = knowledge_response.get('contextual_insights', [])
            if contextual_insights:
                engagement_factors.append(0.8)
            else:
                engagement_factors.append(0.5)
            
            # Response personalization
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if user_messages and len(user_messages) > 2:
                engagement_factors.append(0.7)  # Ongoing conversation
            else:
                engagement_factors.append(0.5)
            
            return sum(engagement_factors) / len(engagement_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_engagement_score", str(e))
            return 0.5
    
    def _calculate_learning_velocity(self, state: ArchMentorState, analysis_result: Dict) -> float:
        """Calculate learning velocity based on conversation progression."""
        try:
            # Simple learning velocity calculation
            message_count = len(state.messages) if hasattr(state, 'messages') else 0
            
            if message_count < 2:
                return 0.5
            
            # Assess question complexity progression
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if len(user_messages) >= 2:
                # Compare first and last message complexity
                first_msg_complexity = len(user_messages[0].split())
                last_msg_complexity = len(user_messages[-1].split())
                
                if last_msg_complexity > first_msg_complexity:
                    velocity = min((last_msg_complexity / max(first_msg_complexity, 1)) / 2.0, 1.0)
                else:
                    velocity = 0.5
            else:
                velocity = 0.5
            
            # Factor in conversation depth
            depth_factor = min(message_count / 10.0, 1.0)
            
            return (velocity + depth_factor) / 2
            
        except Exception as e:
            self.telemetry.log_error("_calculate_learning_velocity", str(e))
            return 0.5
    
    def _calculate_cognitive_load(self, knowledge_response: Dict[str, Any]) -> float:
        """Calculate cognitive load of the response."""
        try:
            load_factors = []
            
            # Content length load
            main_content = knowledge_response.get('educational_response', '') or knowledge_response.get('main_content', '')
            if main_content:
                word_count = len(main_content.split())
                length_load = min(word_count / 300.0, 1.0)
                load_factors.append(length_load)
            
            # Information density load
            source_count = knowledge_response.get('source_count', 0)
            density_load = min(source_count / 4.0, 1.0)
            load_factors.append(density_load)
            
            # Complexity load
            synthesis_quality = knowledge_response.get('synthesis_quality', 'medium')
            complexity_load = {'basic': 0.3, 'medium': 0.6, 'high': 0.9}.get(synthesis_quality, 0.5)
            load_factors.append(complexity_load)
            
            # Technical content load
            technical_indicators = ['specification', 'engineering', 'analysis', 'calculation', 'technical']
            technical_count = 0
            
            for content in [knowledge_response.get('educational_response', ''), knowledge_response.get('main_content', '')]:
                if content:
                    technical_count += sum(1 for term in technical_indicators if term.lower() in content.lower())
            
            technical_load = min(technical_count / 5.0, 1.0)
            load_factors.append(technical_load)
            
            return sum(load_factors) / len(load_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_cognitive_load", str(e))
            return 0.5
    
    def _calculate_analysis_depth(self, knowledge_response: Dict[str, Any]) -> int:
        """Calculate analysis depth in terms of content length."""
        try:
            total_length = 0
            
            # Count main content
            main_content = knowledge_response.get('educational_response', '') or knowledge_response.get('main_content', '')
            if main_content:
                total_length += len(main_content)
            
            # Count knowledge summary
            knowledge_summary = knowledge_response.get('knowledge_summary', '')
            if knowledge_summary:
                total_length += len(knowledge_summary)
            
            # Count contextual insights
            contextual_insights = knowledge_response.get('contextual_insights', [])
            for insight in contextual_insights:
                if isinstance(insight, str):
                    total_length += len(insight)
            
            return total_length
            
        except Exception as e:
            self.telemetry.log_error("_calculate_analysis_depth", str(e))
            return 100
    
    def create_response_summary(self, knowledge_response: Dict[str, Any]) -> str:
        """Create a summary of the response for logging/analysis."""
        try:
            topic = knowledge_response.get('topic', 'Unknown')
            source_count = knowledge_response.get('source_count', 0)
            quality = knowledge_response.get('synthesis_quality', 'unknown')
            
            summary = f"Domain Expert Response - Topic: {topic}, Sources: {source_count}, Quality: {quality}"
            
            # Add key features
            features = []
            if knowledge_response.get('examples'):
                features.append('examples')
            if knowledge_response.get('follow_up_questions'):
                features.append('follow-ups')
            if knowledge_response.get('contextual_insights'):
                features.append('insights')
            
            if features:
                summary += f", Features: {', '.join(features)}"
            
            return summary
            
        except Exception as e:
            self.telemetry.log_error("create_response_summary", str(e))
            return "Domain Expert Response Summary"
    
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
            
            # Check response text quality
            if len(agent_response.response_text.strip()) < 20:
                return False
            
            return True
            
        except Exception as e:
            self.telemetry.log_error("validate_response_structure", str(e))
            return False
    
    # Public interface methods for backward compatibility
    
    def _convert_to_agent_response(self, *args, **kwargs):
        """Backward compatibility method."""
        return self.convert_to_agent_response(*args, **kwargs)
    
    def _calculate_enhancement_metrics(self, *args, **kwargs):
        """Backward compatibility method."""
        return self.calculate_enhancement_metrics(*args, **kwargs)
    
    def _extract_cognitive_flags(self, *args, **kwargs):
        """Backward compatibility method."""
        return self.extract_cognitive_flags(*args, **kwargs)
    
    def _convert_cognitive_flags(self, *args, **kwargs):
        """Backward compatibility method."""
        return self.convert_cognitive_flags(*args, **kwargs) 