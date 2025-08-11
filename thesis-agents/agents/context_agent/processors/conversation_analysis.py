"""
Conversation analysis processing module for analyzing conversation patterns and engagement.
"""
from typing import Dict, Any, List, Optional
from ..schemas import ConversationPatterns
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class ConversationAnalysisProcessor:
    """
    Processes conversation pattern analysis and engagement tracking.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("conversation_analysis")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def analyze_conversation_patterns(self, state: ArchMentorState, current_input: str) -> ConversationPatterns:
        """
        Analyze conversation patterns and engagement trends.
        """
        self.telemetry.log_agent_start("analyze_conversation_patterns")
        
        try:
            if not hasattr(state, 'messages') or not state.messages:
                return self._get_empty_conversation_patterns()
            
            # Extract user messages for analysis
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if not user_messages:
                return self._get_empty_conversation_patterns()
            
            # Analyze different conversation aspects
            has_repetitive_topics = self._detect_repetitive_topics(user_messages)
            has_topic_jumping = self._detect_topic_jumping(user_messages)
            engagement_trend = self._analyze_engagement_trend(user_messages)
            understanding_progression = self._analyze_understanding_progression(user_messages)
            
            # Analyze recent focus
            recent_focus = self._identify_recent_focus(user_messages[-3:] if len(user_messages) >= 3 else user_messages)
            
            # Analyze conversation depth
            conversation_depth = self._analyze_conversation_depth(user_messages)
            
            # Analyze question patterns
            question_patterns = self._analyze_question_patterns(user_messages)
            
            # Analyze response patterns
            response_patterns = self._analyze_response_patterns(user_messages, state)
            
            # Calculate conversation metrics
            conversation_metrics = self._calculate_conversation_metrics(user_messages)
            
            patterns = ConversationPatterns(
                has_repetitive_topics=has_repetitive_topics,
                has_topic_jumping=has_topic_jumping,
                engagement_trend=engagement_trend,
                understanding_progression=understanding_progression,
                recent_focus=recent_focus,
                conversation_depth=conversation_depth,
                question_patterns=question_patterns,
                response_patterns=response_patterns,
                conversation_metrics=conversation_metrics,
                pattern_confidence=self._calculate_pattern_confidence(
                    user_messages, engagement_trend, understanding_progression
                )
            )
            
            self.telemetry.log_agent_end("analyze_conversation_patterns")
            return patterns
            
        except Exception as e:
            self.telemetry.log_error("analyze_conversation_patterns", str(e))
            return self._get_empty_conversation_patterns()
    
    def _detect_repetitive_topics(self, messages: List[str]) -> bool:
        """Detect if the student is repeating topics."""
        try:
            if len(messages) < 3:
                return False
            
            # Extract topics from each message
            message_topics = []
            for message in messages:
                topics = self._extract_topics_from_text(message)
                message_topics.append(set(topics))
            
            # Check for topic overlap across messages
            repetition_count = 0
            for i in range(1, len(message_topics)):
                current_topics = message_topics[i]
                previous_topics = message_topics[i-1]
                
                # Calculate overlap
                if current_topics and previous_topics:
                    overlap = len(current_topics.intersection(previous_topics))
                    overlap_ratio = overlap / min(len(current_topics), len(previous_topics))
                    
                    if overlap_ratio > 0.5:  # More than 50% overlap
                        repetition_count += 1
            
            # Consider repetitive if more than 30% of transitions show high overlap
            return repetition_count / (len(message_topics) - 1) > 0.3
            
        except Exception as e:
            self.telemetry.log_error("_detect_repetitive_topics", str(e))
            return False
    
    def _detect_topic_jumping(self, messages: List[str]) -> bool:
        """Detect if the student is jumping between topics."""
        try:
            if len(messages) < 3:
                return False
            
            # Extract topics from each message
            message_topics = []
            for message in messages:
                topics = self._extract_topics_from_text(message)
                message_topics.append(set(topics))
            
            # Check for topic discontinuity
            jump_count = 0
            for i in range(1, len(message_topics)):
                current_topics = message_topics[i]
                previous_topics = message_topics[i-1]
                
                # Calculate overlap
                if current_topics and previous_topics:
                    overlap = len(current_topics.intersection(previous_topics))
                    if overlap == 0:  # No topic overlap
                        jump_count += 1
            
            # Consider jumping if more than 40% of transitions show no overlap
            return jump_count / (len(message_topics) - 1) > 0.4
            
        except Exception as e:
            self.telemetry.log_error("_detect_topic_jumping", str(e))
            return False
    
    def _analyze_engagement_trend(self, messages: List[str]) -> str:
        """Analyze the trend in student engagement over time."""
        try:
            if len(messages) < 2:
                return 'stable'
            
            # Calculate engagement scores for each message
            engagement_scores = []
            for message in messages:
                score = self._calculate_message_engagement_score(message)
                engagement_scores.append(score)
            
            # Analyze trend
            if len(engagement_scores) < 3:
                # Simple comparison for 2 messages
                if engagement_scores[-1] > engagement_scores[0]:
                    return 'increasing'
                elif engagement_scores[-1] < engagement_scores[0]:
                    return 'decreasing'
                else:
                    return 'stable'
            
            # Linear regression for trend analysis
            recent_scores = engagement_scores[-3:]
            early_scores = engagement_scores[:3] if len(engagement_scores) >= 6 else engagement_scores[:2]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            early_avg = sum(early_scores) / len(early_scores)
            
            if recent_avg > early_avg + 0.1:
                return 'increasing'
            elif recent_avg < early_avg - 0.1:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            self.telemetry.log_error("_analyze_engagement_trend", str(e))
            return 'stable'
    
    def _analyze_understanding_progression(self, messages: List[str]) -> str:
        """Analyze how the student's understanding is progressing."""
        try:
            if len(messages) < 2:
                return 'stable'
            
            # Calculate understanding indicators for each message
            understanding_scores = []
            for message in messages:
                score = self._calculate_understanding_score(message)
                understanding_scores.append(score)
            
            # Analyze progression
            if len(understanding_scores) >= 3:
                recent_avg = sum(understanding_scores[-3:]) / 3
                early_avg = sum(understanding_scores[:3]) / min(3, len(understanding_scores))
                
                if recent_avg > early_avg + 0.15:
                    return 'improving'
                elif recent_avg < early_avg - 0.15:
                    return 'declining'
                else:
                    return 'stable'
            else:
                # Simple comparison
                if understanding_scores[-1] > understanding_scores[0] + 0.1:
                    return 'improving'
                elif understanding_scores[-1] < understanding_scores[0] - 0.1:
                    return 'declining'
                else:
                    return 'stable'
                    
        except Exception as e:
            self.telemetry.log_error("_analyze_understanding_progression", str(e))
            return 'stable'
    
    def _identify_recent_focus(self, recent_messages: List[str]) -> List[str]:
        """Identify the main focus areas in recent messages."""
        try:
            if not recent_messages:
                return []
            
            # Combine recent messages
            combined_text = ' '.join(recent_messages)
            
            # Extract topics with frequency
            topic_counts = {}
            topics = self._extract_topics_from_text(combined_text)
            
            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Sort by frequency and return top topics
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, count in sorted_topics[:5]]
            
        except Exception as e:
            self.telemetry.log_error("_identify_recent_focus", str(e))
            return []
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text using keyword matching."""
        try:
            topic_keywords = {
                'structural': ['structure', 'structural', 'beam', 'column', 'foundation', 'load'],
                'materials': ['material', 'materials', 'concrete', 'steel', 'wood', 'timber'],
                'sustainability': ['sustainable', 'green', 'environmental', 'energy', 'solar'],
                'design': ['design', 'aesthetic', 'form', 'style', 'appearance', 'visual'],
                'planning': ['planning', 'layout', 'organization', 'space', 'program'],
                'systems': ['system', 'systems', 'hvac', 'mechanical', 'electrical', 'plumbing'],
                'construction': ['construction', 'building', 'assembly', 'installation'],
                'codes': ['code', 'codes', 'regulation', 'standard', 'compliance', 'requirement']
            }
            
            text_lower = text.lower()
            found_topics = []
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    found_topics.append(topic)
            
            return found_topics
            
        except Exception as e:
            self.telemetry.log_error("_extract_topics_from_text", str(e))
            return []
    
    def _analyze_conversation_depth(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze the depth and quality of conversation."""
        try:
            depth_analysis = {
                'total_messages': len(messages),
                'average_message_length': 0,
                'vocabulary_richness': 0,
                'question_density': 0,
                'technical_depth': 0,
                'conceptual_depth': 0,
                'overall_depth': 'shallow'
            }
            
            if not messages:
                return depth_analysis
            
            # Calculate average message length
            total_words = sum(len(message.split()) for message in messages)
            depth_analysis['average_message_length'] = total_words / len(messages)
            
            # Calculate vocabulary richness
            all_words = []
            for message in messages:
                all_words.extend(word.lower() for word in message.split())
            
            if all_words:
                unique_words = len(set(all_words))
                depth_analysis['vocabulary_richness'] = unique_words / len(all_words)
            
            # Calculate question density
            total_questions = sum(message.count('?') for message in messages)
            depth_analysis['question_density'] = total_questions / len(messages)
            
            # Calculate technical depth
            technical_terms = []
            for message in messages:
                technical_terms.extend(self._extract_technical_terms_simple(message))
            depth_analysis['technical_depth'] = len(set(technical_terms)) / len(messages)
            
            # Calculate conceptual depth
            conceptual_indicators = [
                'because', 'therefore', 'however', 'although', 'integration',
                'relationship', 'implication', 'consequence', 'synthesis'
            ]
            conceptual_count = sum(
                sum(1 for indicator in conceptual_indicators if indicator in message.lower())
                for message in messages
            )
            depth_analysis['conceptual_depth'] = conceptual_count / len(messages)
            
            # Determine overall depth
            depth_score = (
                min(depth_analysis['average_message_length'] / 15, 1.0) * 0.3 +
                depth_analysis['vocabulary_richness'] * 0.2 +
                min(depth_analysis['question_density'], 1.0) * 0.2 +
                min(depth_analysis['technical_depth'], 1.0) * 0.15 +
                min(depth_analysis['conceptual_depth'], 1.0) * 0.15
            )
            
            if depth_score >= 0.7:
                depth_analysis['overall_depth'] = 'deep'
            elif depth_score >= 0.4:
                depth_analysis['overall_depth'] = 'moderate'
            else:
                depth_analysis['overall_depth'] = 'shallow'
            
            return depth_analysis
            
        except Exception as e:
            self.telemetry.log_error("_analyze_conversation_depth", str(e))
            return {'overall_depth': 'shallow', 'total_messages': 0}
    
    def _analyze_question_patterns(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze patterns in the types of questions asked."""
        try:
            question_patterns = {
                'total_questions': 0,
                'question_types': {
                    'what': 0, 'how': 0, 'why': 0, 'when': 0, 'where': 0, 'which': 0
                },
                'question_complexity': {'simple': 0, 'moderate': 0, 'complex': 0},
                'question_trend': 'stable'
            }
            
            question_messages = [msg for msg in messages if '?' in msg]
            question_patterns['total_questions'] = len(question_messages)
            
            if not question_messages:
                return question_patterns
            
            # Analyze question types
            for question in question_messages:
                question_lower = question.lower()
                for q_type in question_patterns['question_types']:
                    if question_lower.startswith(q_type) or f' {q_type} ' in question_lower:
                        question_patterns['question_types'][q_type] += 1
            
            # Analyze question complexity
            for question in question_messages:
                complexity = self._assess_question_complexity_simple(question)
                question_patterns['question_complexity'][complexity] += 1
            
            # Analyze question trend (if enough data)
            if len(question_messages) >= 4:
                early_questions = question_messages[:len(question_messages)//2]
                recent_questions = question_messages[len(question_messages)//2:]
                
                early_complexity = sum(
                    1 for q in early_questions 
                    if self._assess_question_complexity_simple(q) in ['moderate', 'complex']
                )
                recent_complexity = sum(
                    1 for q in recent_questions 
                    if self._assess_question_complexity_simple(q) in ['moderate', 'complex']
                )
                
                if recent_complexity > early_complexity:
                    question_patterns['question_trend'] = 'increasing_complexity'
                elif recent_complexity < early_complexity:
                    question_patterns['question_trend'] = 'decreasing_complexity'
            
            return question_patterns
            
        except Exception as e:
            self.telemetry.log_error("_analyze_question_patterns", str(e))
            return {'total_questions': 0, 'question_trend': 'stable'}
    
    def _analyze_response_patterns(self, messages: List[str], state: ArchMentorState) -> Dict[str, Any]:
        """Analyze patterns in how the student responds."""
        try:
            response_patterns = {
                'response_length_trend': 'stable',
                'response_detail_level': 'moderate',
                'follow_up_frequency': 0,
                'acknowledgment_frequency': 0,
                'clarification_requests': 0
            }
            
            if len(messages) < 2:
                return response_patterns
            
            # Analyze response length trend
            message_lengths = [len(msg.split()) for msg in messages]
            if len(message_lengths) >= 4:
                early_avg = sum(message_lengths[:len(message_lengths)//2]) / (len(message_lengths)//2)
                recent_avg = sum(message_lengths[len(message_lengths)//2:]) / (len(message_lengths) - len(message_lengths)//2)
                
                if recent_avg > early_avg * 1.2:
                    response_patterns['response_length_trend'] = 'increasing'
                elif recent_avg < early_avg * 0.8:
                    response_patterns['response_length_trend'] = 'decreasing'
            
            # Analyze response detail level
            total_words = sum(len(msg.split()) for msg in messages)
            avg_length = total_words / len(messages)
            
            if avg_length > 25:
                response_patterns['response_detail_level'] = 'high'
            elif avg_length > 10:
                response_patterns['response_detail_level'] = 'moderate'
            else:
                response_patterns['response_detail_level'] = 'low'
            
            # Count specific response types
            for message in messages:
                message_lower = message.lower()
                
                # Follow-up questions
                if any(phrase in message_lower for phrase in ['what about', 'also', 'and what', 'another']):
                    response_patterns['follow_up_frequency'] += 1
                
                # Acknowledgments
                if any(phrase in message_lower for phrase in ['thank', 'thanks', 'helpful', 'understand']):
                    response_patterns['acknowledgment_frequency'] += 1
                
                # Clarification requests
                if any(phrase in message_lower for phrase in ['clarify', 'explain', 'mean', 'confused']):
                    response_patterns['clarification_requests'] += 1
            
            return response_patterns
            
        except Exception as e:
            self.telemetry.log_error("_analyze_response_patterns", str(e))
            return {'response_detail_level': 'moderate'}
    
    def _calculate_conversation_metrics(self, messages: List[str]) -> Dict[str, float]:
        """Calculate quantitative conversation metrics."""
        try:
            if not messages:
                return {'engagement_score': 0.0, 'depth_score': 0.0, 'progression_score': 0.0}
            
            # Engagement score
            engagement_score = self._calculate_overall_engagement_score(messages)
            
            # Depth score
            depth_score = self._calculate_overall_depth_score(messages)
            
            # Progression score
            progression_score = self._calculate_progression_score(messages)
            
            return {
                'engagement_score': engagement_score,
                'depth_score': depth_score,
                'progression_score': progression_score,
                'total_messages': len(messages),
                'average_length': sum(len(msg.split()) for msg in messages) / len(messages)
            }
            
        except Exception as e:
            self.telemetry.log_error("_calculate_conversation_metrics", str(e))
            return {'engagement_score': 0.5, 'depth_score': 0.5, 'progression_score': 0.5}
    
    # Helper methods
    
    def _calculate_message_engagement_score(self, message: str) -> float:
        """Calculate engagement score for a single message."""
        try:
            score = 0.5  # Base score
            
            # Length factor
            word_count = len(message.split())
            if word_count > 20:
                score += 0.2
            elif word_count > 10:
                score += 0.1
            elif word_count < 5:
                score -= 0.1
            
            # Question factor
            if '?' in message:
                score += 0.1
            
            # Exclamation factor
            if '!' in message:
                score += 0.1
            
            # Engagement words
            engagement_words = ['interesting', 'curious', 'excited', 'love', 'amazing']
            if any(word in message.lower() for word in engagement_words):
                score += 0.2
            
            # Disengagement words
            disengagement_words = ['boring', 'tired', 'whatever', 'don\'t care']
            if any(word in message.lower() for word in disengagement_words):
                score -= 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_message_engagement_score", str(e))
            return 0.5
    
    def _calculate_understanding_score(self, message: str) -> float:
        """Calculate understanding score for a single message."""
        try:
            score = 0.5  # Base score
            
            # Understanding indicators
            understanding_words = ['understand', 'clear', 'makes sense', 'i see', 'got it']
            if any(word in message.lower() for word in understanding_words):
                score += 0.3
            
            # Confusion indicators
            confusion_words = ['confused', 'don\'t understand', 'unclear', 'lost']
            if any(word in message.lower() for word in confusion_words):
                score -= 0.3
            
            # Technical term usage (indicates growing understanding)
            technical_terms = self._extract_technical_terms_simple(message)
            if len(technical_terms) >= 2:
                score += 0.2
            elif len(technical_terms) >= 1:
                score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_understanding_score", str(e))
            return 0.5
    
    def _extract_technical_terms_simple(self, text: str) -> List[str]:
        """Simple technical term extraction for conversation analysis."""
        try:
            simple_technical_terms = [
                'structure', 'design', 'material', 'construction', 'engineering',
                'sustainable', 'energy', 'system', 'building', 'architecture'
            ]
            
            text_lower = text.lower()
            found_terms = [term for term in simple_technical_terms if term in text_lower]
            return found_terms
            
        except Exception as e:
            self.telemetry.log_error("_extract_technical_terms_simple", str(e))
            return []
    
    def _assess_question_complexity_simple(self, question: str) -> str:
        """Simple question complexity assessment."""
        try:
            question_lower = question.lower()
            
            complex_indicators = ['why', 'how would', 'what if', 'compare', 'analyze']
            simple_indicators = ['what is', 'who is', 'when is', 'where is']
            
            if any(indicator in question_lower for indicator in complex_indicators):
                return 'complex'
            elif any(indicator in question_lower for indicator in simple_indicators):
                return 'simple'
            else:
                return 'moderate'
                
        except Exception as e:
            self.telemetry.log_error("_assess_question_complexity_simple", str(e))
            return 'moderate'
    
    def _calculate_overall_engagement_score(self, messages: List[str]) -> float:
        """Calculate overall engagement score for all messages."""
        try:
            if not messages:
                return 0.5
            
            scores = [self._calculate_message_engagement_score(msg) for msg in messages]
            return sum(scores) / len(scores)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_overall_engagement_score", str(e))
            return 0.5
    
    def _calculate_overall_depth_score(self, messages: List[str]) -> float:
        """Calculate overall conversation depth score."""
        try:
            if not messages:
                return 0.5
            
            # Factors for depth calculation
            avg_length = sum(len(msg.split()) for msg in messages) / len(messages)
            length_score = min(avg_length / 20, 1.0)
            
            # Technical term density
            all_technical_terms = []
            for msg in messages:
                all_technical_terms.extend(self._extract_technical_terms_simple(msg))
            
            total_words = sum(len(msg.split()) for msg in messages)
            technical_density = len(all_technical_terms) / total_words if total_words > 0 else 0
            technical_score = min(technical_density * 10, 1.0)
            
            # Question depth
            questions = [msg for msg in messages if '?' in msg]
            complex_questions = [q for q in questions if self._assess_question_complexity_simple(q) == 'complex']
            question_score = len(complex_questions) / len(questions) if questions else 0
            
            # Combined depth score
            depth_score = (length_score * 0.4 + technical_score * 0.3 + question_score * 0.3)
            return max(0.0, min(1.0, depth_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_overall_depth_score", str(e))
            return 0.5
    
    def _calculate_progression_score(self, messages: List[str]) -> float:
        """Calculate learning progression score."""
        try:
            if len(messages) < 2:
                return 0.5
            
            # Compare early and recent messages
            mid_point = len(messages) // 2
            early_messages = messages[:mid_point]
            recent_messages = messages[mid_point:]
            
            # Calculate complexity progression
            early_complexity = sum(
                len(self._extract_technical_terms_simple(msg)) for msg in early_messages
            ) / len(early_messages)
            
            recent_complexity = sum(
                len(self._extract_technical_terms_simple(msg)) for msg in recent_messages
            ) / len(recent_messages)
            
            # Calculate understanding progression
            early_understanding = sum(
                self._calculate_understanding_score(msg) for msg in early_messages
            ) / len(early_messages)
            
            recent_understanding = sum(
                self._calculate_understanding_score(msg) for msg in recent_messages
            ) / len(recent_messages)
            
            # Combined progression score
            complexity_progression = (recent_complexity - early_complexity + 1) / 2  # Normalize to 0-1
            understanding_progression = recent_understanding - early_understanding + 0.5  # Normalize to 0-1
            
            progression_score = (complexity_progression + understanding_progression) / 2
            return max(0.0, min(1.0, progression_score))
            
        except Exception as e:
            self.telemetry.log_error("_calculate_progression_score", str(e))
            return 0.5
    
    def _calculate_pattern_confidence(self, messages: List[str], engagement_trend: str, 
                                    understanding_progression: str) -> float:
        """Calculate confidence in pattern analysis."""
        try:
            confidence_factors = []
            
            # Message count factor
            message_count = len(messages)
            if message_count >= 5:
                confidence_factors.append(0.8)
            elif message_count >= 3:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
            
            # Trend clarity factor
            if engagement_trend in ['increasing', 'decreasing']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            if understanding_progression in ['improving', 'declining']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Data quality factor
            avg_length = sum(len(msg.split()) for msg in messages) / len(messages) if messages else 0
            if avg_length > 15:
                confidence_factors.append(0.8)
            elif avg_length > 8:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_pattern_confidence", str(e))
            return 0.6
    
    def _get_empty_conversation_patterns(self) -> ConversationPatterns:
        """Return empty conversation patterns when no data is available."""
        return ConversationPatterns(
            has_repetitive_topics=False,
            has_topic_jumping=False,
            engagement_trend='stable',
            understanding_progression='stable',
            recent_focus=[],
            conversation_depth={'overall_depth': 'shallow', 'total_messages': 0},
            question_patterns={'total_questions': 0, 'question_trend': 'stable'},
            response_patterns={'response_detail_level': 'moderate'},
            conversation_metrics={'engagement_score': 0.5, 'depth_score': 0.5, 'progression_score': 0.5},
            pattern_confidence=0.3
        )