"""
Domain Expert Agent Adapter - streamlined modular version.

This adapter maintains backward compatibility while delegating to processor modules.
"""

import sys
import os
from typing import Dict, Any, List, Optional

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics

# Import modular components
from .config import *
from .processors import (
    KnowledgeSearchProcessor,
    ContextAnalysisProcessor,
    ContextAnalysis,
    KnowledgeSynthesisProcessor,
    ContentProcessingProcessor,
    ResponseBuilderProcessor
)
from ..common import LLMClient, AgentTelemetry, MetricsCalculator, TextProcessor, SafetyValidator


class DomainExpertAgent:
    """
    Domain Expert Agent for providing architectural knowledge and expertise.
    
    This streamlined adapter delegates to specialized processor modules.
    """
    
    def __init__(self, domain="architecture"):
        """Initialize the Domain Expert Agent with modular processors."""
        self.telemetry = AgentTelemetry("domain_expert")
        self.telemetry.log_agent_start("__init__", domain=domain)
        
        # Core properties
        self.domain = domain
        self.name = "domain_expert"
        
        # Initialize LLM client
        self.client = LLMClient(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        
        # Initialize shared utilities
        self.text_processor = TextProcessor()
        self.safety_validator = SafetyValidator()
        self.metrics_calculator = MetricsCalculator()
        
        # Initialize modular processors
        self.search_processor = KnowledgeSearchProcessor()
        self.context_processor = ContextAnalysisProcessor()
        self.synthesis_processor = KnowledgeSynthesisProcessor()
        self.content_processor = ContentProcessingProcessor()
        self.response_processor = ResponseBuilderProcessor()
        
        self.telemetry.log_agent_end("__init__")
        print(f"🏛️ {self.name} initialized for domain: {domain}")
    
    async def provide_knowledge(self, state: ArchMentorState, context_classification: Dict,
                              analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """
        Main processing method - provides architectural knowledge and expertise.
        """
        self.telemetry.log_agent_start("provide_knowledge")
        
        try:
            # Step 1: Analyze conversation context
            context_analysis = self.context_processor.analyze_conversation_context_internal(state)
            
            # Step 2: Extract topic from context
            topic = self.context_processor.extract_topic_from_context(analysis_result, state)
            
            # Step 3: Search for knowledge
            knowledge_data = await self.search_processor.search_web_for_knowledge(topic, state)
            
            # Step 4: Synthesize knowledge
            synthesis_result = await self.synthesis_processor.synthesize_knowledge_internal(
                topic, knowledge_data, context_analysis.__dict__, state
            )
            
            # Step 5: Process and optimize content
            optimized_content = self.content_processor.optimize_for_learning(
                synthesis_result.get('educational_response', ''),
                context_analysis.complexity_level
            )
            synthesis_result['educational_response'] = optimized_content
            
            # Step 6: Finalize response
            finalized_response = self.content_processor.finalize_knowledge_response(synthesis_result)
            
            # Step 7: Convert to AgentResponse
            agent_response = self.response_processor.convert_to_agent_response(
                finalized_response, state, context_classification, analysis_result, routing_decision
            )
            
            # Step 8: Track usage
            self.content_processor.track_knowledge_usage(
                topic, len(knowledge_data), context_analysis.__dict__
            )
            
            self.telemetry.log_agent_end("provide_knowledge")
            return agent_response
            
        except Exception as e:
            self.telemetry.log_error(f"Knowledge provision failed: {str(e)}")
            return ResponseBuilder.create_error_response(
                f"Knowledge provision failed: {str(e)}",
                agent_name=self.name
            )
    
    async def discover_knowledge(self, state: ArchMentorState, context_classification: Dict,
                               analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """
        Alternative knowledge discovery method.
        """
        # For now, delegate to provide_knowledge
        return await self.provide_knowledge(state, context_classification, analysis_result, routing_decision)
    
    # Delegation methods for backward compatibility
    
    async def search_web_for_knowledge(self, topic: str, state: ArchMentorState = None) -> List[Dict]:
        """Search web for knowledge (delegates to processor)."""
        return await self.search_processor.search_web_for_knowledge(topic, state)
    
    def analyze_conversation_context_internal(self, state: ArchMentorState) -> ContextAnalysis:
        """Analyze conversation context (delegates to processor)."""
        return self.context_processor.analyze_conversation_context_internal(state)
    
    def create_knowledge_request(self, topic: str, context: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Create knowledge request (simplified implementation)."""
        return {
            'topic': topic,
            'context': context,
            'building_type': context.get('building_type', 'general'),
            'complexity_level': context.get('complexity_level', 'intermediate'),
            'user_intent': context.get('user_intent', 'learning')
        }
    
    async def synthesize_knowledge_internal(self, topic: str, knowledge_data: List[Dict], 
                                          context: Dict = None, state: ArchMentorState = None) -> Dict[str, Any]:
        """Synthesize knowledge (delegates to processor)."""
        return await self.synthesis_processor.synthesize_knowledge_internal(topic, knowledge_data, context, state)
    
    async def generate_response_internal(self, topic: str, knowledge_data: List[Dict], 
                                       context: Dict = None, delivery_style: str = 'educational') -> str:
        """Generate response (delegates to processor)."""
        return await self.synthesis_processor.generate_response_internal(topic, knowledge_data, context, delivery_style)
    
    def convert_to_agent_response(self, knowledge_response: Dict[str, Any], 
                                state: ArchMentorState, context_classification: Dict,
                                analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """Convert to agent response (delegates to processor)."""
        return self.response_processor.convert_to_agent_response(
            knowledge_response, state, context_classification, analysis_result, routing_decision
        )
    
    def calculate_enhancement_metrics(self, knowledge_response: Dict[str, Any],
                                    state: ArchMentorState, analysis_result: Dict) -> EnhancementMetrics:
        """Calculate enhancement metrics (delegates to processor)."""
        return self.response_processor.calculate_enhancement_metrics(knowledge_response, state, analysis_result)
    
    def extract_cognitive_flags(self, knowledge_response: Dict[str, Any],
                               state: ArchMentorState, context_classification: Dict) -> List[str]:
        """Extract cognitive flags (delegates to processor)."""
        return self.response_processor.extract_cognitive_flags(knowledge_response, state, context_classification)
    
    def convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Convert cognitive flags (delegates to processor)."""
        return self.response_processor.convert_cognitive_flags(cognitive_flags)
    
    # Context extraction methods
    
    def extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type (delegates to processor)."""
        return self.context_processor.extract_building_type_from_context(state)
    
    def extract_topic_from_context(self, analysis_result: Dict, state: ArchMentorState) -> str:
        """Extract topic (delegates to processor)."""
        return self.context_processor.extract_topic_from_context(analysis_result, state)
    
    def extract_recent_topics(self, user_messages: List[str]) -> List[str]:
        """Extract recent topics (delegates to processor)."""
        return self.context_processor.extract_recent_topics(user_messages)
    
    # Content processing methods
    
    def format_examples_list(self, examples: List[str]) -> str:
        """Format examples list (delegates to processor)."""
        return self.content_processor.format_examples_list(examples)
    
    def enhance_search_results(self, results: List[Dict], context: Dict) -> List[Dict]:
        """Enhance search results (delegates to processor)."""
        return self.content_processor.enhance_search_results(results, context)
    
    def validate_response_completeness(self, response: Dict[str, Any]) -> bool:
        """Validate response completeness (delegates to processor)."""
        return self.content_processor.validate_response_completeness(response)
    
    def optimize_for_learning(self, content: str, user_level: str = 'intermediate') -> str:
        """Optimize for learning (delegates to processor)."""
        return self.content_processor.optimize_for_learning(content, user_level)
    
    def finalize_knowledge_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize knowledge response (delegates to processor)."""
        return self.content_processor.finalize_knowledge_response(response_data)
    
    def track_knowledge_usage(self, topic: str, results_count: int, user_context: Dict = None) -> None:
        """Track knowledge usage (delegates to processor)."""
        self.content_processor.track_knowledge_usage(topic, results_count, user_context)
    
    # Search utility methods
    
    def is_building_request(self, text: str) -> bool:
        """Check if request is about buildings (delegates to processor)."""
        return self.search_processor.is_building_request(text)
    
    def is_landscape_request(self, text: str) -> bool:
        """Check if request is about landscape (delegates to processor)."""
        return self.search_processor.is_landscape_request(text)
    
    def get_search_query_modifiers(self, topic: str, state: ArchMentorState = None) -> List[str]:
        """Get search query modifiers (delegates to processor)."""
        return self.search_processor.get_search_query_modifiers(topic, state)
    
    def analyze_conversation_context_for_search(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze context for search (delegates to processor)."""
        return self.search_processor.analyze_conversation_context_for_search(state)
    
    def generate_context_aware_search_query(self, base_topic: str, context: Dict[str, Any]) -> str:
        """Generate context-aware search query (delegates to processor)."""
        return self.search_processor.generate_context_aware_search_query(base_topic, context)
    
    # Configuration and utility methods (for backward compatibility)
    
    def get_model(self, use_case="cheap"):
        """Get model configuration."""
        return MODEL_CONFIG.get(use_case, DEFAULT_MODEL)
    
    def get_token_limit(self, component):
        """Get token limit for component."""
        return TOKEN_LIMITS.get(component, DEFAULT_MAX_TOKENS)
    
    def is_feature_enabled(self, feature_name):
        """Check if feature is enabled."""
        return FEATURE_FLAGS.get(feature_name, False)
    
    def get_mock_response(self, topic):
        """Get mock response for testing."""
        return f"Mock response for {topic} - this is a test response for development purposes."
    
    def should_skip_expensive_call(self):
        """Check if expensive calls should be skipped."""
        return os.getenv('SKIP_EXPENSIVE_CALLS', 'false').lower() == 'true'
    
    def get_dev_token_limit(self):
        """Get development token limit."""
        return int(os.getenv('DEV_TOKEN_LIMIT', str(DEFAULT_MAX_TOKENS)))
    
    # Private methods for internal processing (maintain compatibility)
    
    def _analyze_conversation_context_internal(self, state: ArchMentorState) -> ContextAnalysis:
        """Internal context analysis method."""
        return self.analyze_conversation_context_internal(state)
    
    def _create_knowledge_request(self, topic: str, context: Dict, state: ArchMentorState) -> Dict[str, Any]:
        """Internal knowledge request creation."""
        return self.create_knowledge_request(topic, context, state)
    
    async def _synthesize_knowledge_internal(self, topic: str, knowledge_data: List[Dict], 
                                           context: Dict = None, state: ArchMentorState = None) -> Dict[str, Any]:
        """Internal knowledge synthesis."""
        return await self.synthesize_knowledge_internal(topic, knowledge_data, context, state)
    
    async def _generate_response_internal(self, topic: str, knowledge_data: List[Dict], 
                                        context: Dict = None, delivery_style: str = 'educational') -> str:
        """Internal response generation."""
        return await self.generate_response_internal(topic, knowledge_data, context, delivery_style)
    
    def _convert_to_agent_response(self, knowledge_response: Dict[str, Any], 
                                 state: ArchMentorState, context_classification: Dict,
                                 analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """Internal agent response conversion."""
        return self.convert_to_agent_response(knowledge_response, state, context_classification, analysis_result, routing_decision)
    
    def _calculate_enhancement_metrics(self, knowledge_response: Dict[str, Any],
                                     state: ArchMentorState, analysis_result: Dict) -> EnhancementMetrics:
        """Internal enhancement metrics calculation."""
        return self.calculate_enhancement_metrics(knowledge_response, state, analysis_result)
    
    def _extract_cognitive_flags(self, knowledge_response: Dict[str, Any],
                               state: ArchMentorState, context_classification: Dict) -> List[str]:
        """Internal cognitive flags extraction."""
        return self.extract_cognitive_flags(knowledge_response, state, context_classification)
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Internal cognitive flags conversion."""
        return self.convert_cognitive_flags(cognitive_flags)
    
    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Internal building type extraction."""
        return self.extract_building_type_from_context(state)
    
    def _extract_topic_from_context(self, analysis_result: Dict, state: ArchMentorState) -> str:
        """Internal topic extraction."""
        return self.extract_topic_from_context(analysis_result, state)
    
    def _extract_recent_topics(self, user_messages: List[str]) -> List[str]:
        """Internal recent topics extraction."""
        return self.extract_recent_topics(user_messages)
    
    def _extract_key_points(self, content_list: List[str]) -> List[str]:
        """Extract key points from content."""
        key_points = []
        for content in content_list[:5]:  # Limit to first 5 items
            if isinstance(content, str) and len(content.strip()) > 20:
                # Extract first meaningful sentence
                sentences = content.split('.')
                for sentence in sentences:
                    if len(sentence.strip()) > 15:
                        key_points.append(sentence.strip())
                        break
        return key_points[:5]  # Return top 5 key points
    
    # Cleanup
    def __del__(self):
        """Cleanup method."""
        try:
            self.telemetry.log_agent_end("cleanup")
        except:
            pass 