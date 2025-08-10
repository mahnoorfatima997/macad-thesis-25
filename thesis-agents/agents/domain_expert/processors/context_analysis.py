"""
Context analysis processing module for analyzing conversation context and extracting topics.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


@dataclass
class ContextAnalysis:
    """Data class for context analysis results."""
    building_type: str
    topic_focus: str
    complexity_level: str
    user_intent: str
    recent_topics: List[str]
    confidence_score: float


class ContextAnalysisProcessor:
    """
    Processes conversation context analysis and topic extraction.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("context_analysis")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def analyze_conversation_context_internal(self, state: ArchMentorState) -> ContextAnalysis:
        """
        Analyze conversation context for knowledge retrieval optimization.
        """
        self.telemetry.log_agent_start("analyze_conversation_context_internal")
        
        try:
            # Extract messages for analysis
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if not user_messages:
                return self._get_default_context_analysis()
            
            # Analyze different aspects of context
            building_type = self._extract_building_type_from_context(state)
            topic_focus = self._extract_topic_focus(user_messages)
            complexity_level = self._assess_complexity_level(user_messages)
            user_intent = self._analyze_user_intent(user_messages)
            # Backward-compatible alias: some callers referenced a private name
            recent_topics = self.extract_recent_topics(user_messages)
            
            # Calculate confidence in analysis
            confidence_score = self._calculate_context_confidence(
                user_messages, building_type, topic_focus, complexity_level
            )
            
            context_analysis = ContextAnalysis(
                building_type=building_type,
                topic_focus=topic_focus,
                complexity_level=complexity_level,
                user_intent=user_intent,
                recent_topics=recent_topics,
                confidence_score=confidence_score
            )
            
            self.telemetry.log_agent_end("analyze_conversation_context_internal")
            return context_analysis
            
        except Exception as e:
            self.telemetry.log_error("analyze_conversation_context_internal", str(e))
            return self._get_default_context_analysis()
    
    def extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type from conversation context."""
        try:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if not user_messages:
                return "general"
            
            # Combine recent messages for analysis
            combined_text = ' '.join(user_messages[-5:]).lower()
            
            # Building type patterns with confidence scores
            building_patterns = {
                'residential': {
                    'keywords': ['house', 'home', 'apartment', 'residential', 'housing', 'dwelling', 'villa', 'townhouse'],
                    'weight': 1.0
                },
                'commercial': {
                    'keywords': ['office', 'retail', 'commercial', 'store', 'shopping', 'business', 'corporate'],
                    'weight': 1.0
                },
                'institutional': {
                    'keywords': ['school', 'hospital', 'library', 'museum', 'university', 'civic', 'public'],
                    'weight': 1.0
                },
                'industrial': {
                    'keywords': ['factory', 'warehouse', 'industrial', 'manufacturing', 'plant'],
                    'weight': 1.0
                },
                'mixed-use': {
                    'keywords': ['mixed-use', 'mixed use', 'multi-purpose', 'combined'],
                    'weight': 1.2
                },
                'cultural': {
                    'keywords': ['theater', 'gallery', 'cultural', 'arts', 'performance'],
                    'weight': 1.0
                },
                'hospitality': {
                    'keywords': ['hotel', 'restaurant', 'hospitality', 'resort'],
                    'weight': 1.0
                }
            }
            
            # Score each building type
            type_scores = {}
            for building_type, config in building_patterns.items():
                score = 0
                for keyword in config['keywords']:
                    if keyword in combined_text:
                        score += config['weight']
                type_scores[building_type] = score
            
            # Return highest scoring type or 'general' if no clear match
            if type_scores and max(type_scores.values()) > 0:
                return max(type_scores, key=type_scores.get)
            
            return "general"
            
        except Exception as e:
            self.telemetry.log_error("extract_building_type_from_context", str(e))
            return "general"
    
    def extract_topic_from_context(self, analysis_result: Dict, state: ArchMentorState) -> str:
        """Extract main topic from analysis result and conversation context."""
        try:
            # Try to get topic from analysis result first
            if analysis_result:
                # Check various possible topic fields
                topic_fields = ['topic', 'main_topic', 'subject', 'focus_area']
                for field in topic_fields:
                    if field in analysis_result and analysis_result[field]:
                        return str(analysis_result[field])
            
            # Fall back to extracting from conversation
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            
            if not user_messages:
                return "architectural design"
            
            # Get the most recent message as primary topic source
            recent_message = user_messages[-1].lower()
            
            # Topic extraction patterns
            topic_patterns = {
                'sustainable design': ['sustainable', 'green', 'eco', 'environmental', 'energy efficient'],
                'structural systems': ['structure', 'structural', 'beam', 'column', 'foundation', 'frame'],
                'building materials': ['material', 'materials', 'concrete', 'steel', 'wood', 'brick'],
                'space planning': ['space', 'planning', 'layout', 'organization', 'circulation'],
                'building codes': ['code', 'codes', 'regulation', 'compliance', 'zoning'],
                'accessibility': ['accessible', 'accessibility', 'universal design', 'barrier-free'],
                'lighting design': ['lighting', 'light', 'illumination', 'daylighting', 'artificial light'],
                'HVAC systems': ['hvac', 'heating', 'cooling', 'ventilation', 'air conditioning'],
                'construction methods': ['construction', 'building', 'assembly', 'installation'],
                'architectural history': ['history', 'historical', 'style', 'movement', 'period'],
                'urban planning': ['urban', 'city', 'planning', 'development', 'zoning']
            }
            
            # Find best matching topic
            for topic, keywords in topic_patterns.items():
                if any(keyword in recent_message for keyword in keywords):
                    return topic
            
            # If no specific topic found, extract key nouns
            key_terms = self._extract_key_architectural_terms(recent_message)
            if key_terms:
                return key_terms[0]
            
            return "architectural design"
            
        except Exception as e:
            self.telemetry.log_error("extract_topic_from_context", str(e))
            return "architectural design"
    
    def extract_recent_topics(self, user_messages: List[str]) -> List[str]:
        """Extract recent topics from user messages."""
        try:
            if not user_messages:
                return []
            
            topics = []
            
            # Analyze last few messages
            recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
            
            for message in recent_messages:
                message_topics = self._extract_topics_from_message(message)
                topics.extend(message_topics)
            
            # Remove duplicates while preserving order
            unique_topics = []
            seen = set()
            for topic in topics:
                if topic not in seen:
                    unique_topics.append(topic)
                    seen.add(topic)
            
            return unique_topics[:5]  # Return top 5 recent topics
            
        except Exception as e:
            self.telemetry.log_error("extract_recent_topics", str(e))
            return []
    
    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Internal method for building type extraction."""
        return self.extract_building_type_from_context(state)
    
    def _extract_topic_focus(self, user_messages: List[str]) -> str:
        """Extract the main topic focus from user messages."""
        if not user_messages:
            return "general_architecture"
        
        # Combine recent messages
        combined_text = ' '.join(user_messages[-3:]).lower()
        
        # Focus area patterns
        focus_patterns = {
            'design_process': ['design', 'process', 'methodology', 'approach'],
            'technical_systems': ['technical', 'systems', 'engineering', 'mechanical'],
            'sustainability': ['sustainable', 'green', 'environmental', 'energy'],
            'aesthetics': ['aesthetic', 'beautiful', 'style', 'appearance'],
            'functionality': ['functional', 'function', 'use', 'purpose'],
            'construction': ['construction', 'building', 'assembly', 'installation'],
            'planning': ['planning', 'layout', 'organization', 'zoning'],
            'materials': ['material', 'materials', 'concrete', 'steel', 'wood']
        }
        
        # Score focus areas
        focus_scores = {}
        for focus, keywords in focus_patterns.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            focus_scores[focus] = score
        
        # Return highest scoring focus or default
        if focus_scores and max(focus_scores.values()) > 0:
            return max(focus_scores, key=focus_scores.get)
        
        return "general_architecture"
    
    def _assess_complexity_level(self, user_messages: List[str]) -> str:
        """Assess the complexity level of user questions."""
        if not user_messages:
            return "intermediate"
        
        # Analyze recent messages for complexity indicators
        recent_text = ' '.join(user_messages[-2:]).lower()
        
        # Complexity indicators
        beginner_indicators = ['what is', 'how do i', 'basic', 'simple', 'introduction']
        advanced_indicators = ['integration', 'optimization', 'complex', 'sophisticated', 'advanced']
        technical_indicators = ['calculation', 'analysis', 'specification', 'engineering', 'technical']
        
        beginner_count = sum(1 for indicator in beginner_indicators if indicator in recent_text)
        advanced_count = sum(1 for indicator in advanced_indicators if indicator in recent_text)
        technical_count = sum(1 for indicator in technical_indicators if indicator in recent_text)
        
        # Determine complexity level
        if advanced_count > 0 or technical_count > 1:
            return "advanced"
        elif beginner_count > 0:
            return "beginner"
        else:
            return "intermediate"
    
    def _analyze_user_intent(self, user_messages: List[str]) -> str:
        """Analyze user intent from messages."""
        if not user_messages:
            return "learning"
        
        recent_message = user_messages[-1].lower()
        
        # Intent patterns
        intent_patterns = {
            'learning': ['what', 'how', 'why', 'explain', 'learn', 'understand'],
            'problem_solving': ['problem', 'issue', 'solve', 'fix', 'help'],
            'comparison': ['compare', 'difference', 'better', 'versus', 'vs'],
            'recommendation': ['recommend', 'suggest', 'best', 'should', 'advice'],
            'validation': ['correct', 'right', 'validate', 'check', 'confirm'],
            'exploration': ['explore', 'possibilities', 'options', 'alternatives']
        }
        
        # Score intents
        intent_scores = {}
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in recent_message)
            intent_scores[intent] = score
        
        # Return highest scoring intent or default
        if intent_scores and max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        
        return "learning"
    
    def _calculate_context_confidence(self, user_messages: List[str], building_type: str, 
                                    topic_focus: str, complexity_level: str) -> float:
        """Calculate confidence in context analysis."""
        try:
            confidence_factors = []
            
            # Message count factor
            message_count = len(user_messages)
            count_factor = min(message_count / 5.0, 1.0)
            confidence_factors.append(count_factor)
            
            # Specificity factor
            specificity = 0.5
            if building_type != "general":
                specificity += 0.2
            if topic_focus != "general_architecture":
                specificity += 0.2
            if complexity_level != "intermediate":
                specificity += 0.1
            confidence_factors.append(specificity)
            
            # Content richness factor
            if user_messages:
                avg_length = sum(len(msg.split()) for msg in user_messages) / len(user_messages)
                richness_factor = min(avg_length / 20.0, 1.0)
                confidence_factors.append(richness_factor)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_context_confidence", str(e))
            return 0.5
    
    def _extract_key_architectural_terms(self, text: str) -> List[str]:
        """Extract key architectural terms from text."""
        architectural_terms = [
            'architecture', 'design', 'building', 'structure', 'construction',
            'space', 'material', 'sustainable', 'planning', 'engineering',
            'aesthetic', 'functional', 'technical', 'systems', 'environment'
        ]
        
        text_lower = text.lower()
        found_terms = []
        
        for term in architectural_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms[:3]  # Return top 3 terms
    
    def _extract_topics_from_message(self, message: str) -> List[str]:
        """Extract topics from a single message."""
        topics = []
        message_lower = message.lower()
        
        # Common architectural topics
        topic_keywords = {
            'sustainability': ['sustainable', 'green', 'eco', 'environmental'],
            'structure': ['structure', 'structural', 'engineering'],
            'materials': ['material', 'materials', 'construction'],
            'design': ['design', 'aesthetic', 'style'],
            'planning': ['planning', 'layout', 'organization'],
            'systems': ['systems', 'hvac', 'mechanical', 'electrical'],
            'codes': ['code', 'codes', 'regulation', 'compliance']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _get_default_context_analysis(self) -> ContextAnalysis:
        """Return default context analysis when analysis fails."""
        return ContextAnalysis(
            building_type="general",
            topic_focus="general_architecture",
            complexity_level="intermediate",
            user_intent="learning",
            recent_topics=[],
            confidence_score=0.3
        )
    
    def assess_knowledge_gaps(self, topic: str, results: List[Dict]) -> Dict[str, Any]:
        """Assess knowledge gaps based on search results."""
        try:
            gaps = {
                'coverage_gaps': [],
                'depth_gaps': [],
                'technical_gaps': [],
                'practical_gaps': []
            }
            
            if not results:
                gaps['coverage_gaps'] = ['No relevant information found']
                return gaps
            
            # Analyze result coverage
            covered_aspects = set()
            for result in results:
                snippet = result.get('snippet', '').lower()
                title = result.get('title', '').lower()
                
                # Check coverage of different aspects
                if any(word in snippet or word in title for word in ['theory', 'principle', 'concept']):
                    covered_aspects.add('theoretical')
                if any(word in snippet or word in title for word in ['example', 'case', 'project']):
                    covered_aspects.add('practical')
                if any(word in snippet or word in title for word in ['technical', 'specification', 'detail']):
                    covered_aspects.add('technical')
                if any(word in snippet or word in title for word in ['how to', 'guide', 'tutorial']):
                    covered_aspects.add('instructional')
            
            # Identify gaps
            all_aspects = {'theoretical', 'practical', 'technical', 'instructional'}
            missing_aspects = all_aspects - covered_aspects
            
            for aspect in missing_aspects:
                if aspect == 'theoretical':
                    gaps['coverage_gaps'].append('Theoretical foundations')
                elif aspect == 'practical':
                    gaps['practical_gaps'].append('Practical examples and case studies')
                elif aspect == 'technical':
                    gaps['technical_gaps'].append('Technical specifications and details')
                elif aspect == 'instructional':
                    gaps['depth_gaps'].append('Step-by-step guidance')
            
            return gaps
            
        except Exception as e:
            self.telemetry.log_error("assess_knowledge_gaps", str(e))
            return {'coverage_gaps': [], 'depth_gaps': [], 'technical_gaps': [], 'practical_gaps': []}
    
    def create_learning_path(self, topic: str, user_level: str = 'intermediate') -> Dict[str, Any]:
        """Create a learning path based on topic and user level."""
        try:
            learning_path = {
                'topic': topic,
                'user_level': user_level,
                'stages': [],
                'estimated_time': '',
                'resources': []
            }
            
            # Define learning stages based on user level
            if user_level == 'beginner':
                stages = [
                    f'Introduction to {topic}',
                    f'Basic principles of {topic}',
                    f'Common applications of {topic}',
                    f'Practical examples of {topic}'
                ]
                estimated_time = '2-4 weeks'
            elif user_level == 'advanced':
                stages = [
                    f'Advanced concepts in {topic}',
                    f'Complex applications of {topic}',
                    f'Research and innovation in {topic}',
                    f'Professional practice of {topic}'
                ]
                estimated_time = '4-8 weeks'
            else:  # intermediate
                stages = [
                    f'Fundamentals of {topic}',
                    f'Design applications of {topic}',
                    f'Technical considerations for {topic}',
                    f'Case studies in {topic}'
                ]
                estimated_time = '3-6 weeks'
            
            learning_path['stages'] = stages
            learning_path['estimated_time'] = estimated_time
            
            # Add recommended resources
            learning_path['resources'] = [
                'Professional architecture publications',
                'Case study databases',
                'Technical standards and codes',
                'Educational videos and tutorials'
            ]
            
            return learning_path
            
        except Exception as e:
            self.telemetry.log_error("create_learning_path", str(e))
            return {
                'topic': topic,
                'user_level': user_level,
                'stages': [f'Learn about {topic}'],
                'estimated_time': '2-4 weeks',
                'resources': ['General architecture resources']
            } 