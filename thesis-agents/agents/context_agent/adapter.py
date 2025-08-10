"""
Context Agent Adapter - streamlined modular version.

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
from .schemas import ContextPackage, CoreClassification, ContentAnalysis, ConversationPatterns, ContextualMetadata
from .processors import (
    InputClassificationProcessor,
    ContentAnalysisProcessor,
    ConversationAnalysisProcessor,
    ContextGenerationProcessor,
    ResponseBuilderProcessor
)
from ..common import LLMClient, AgentTelemetry, MetricsCalculator, TextProcessor, SafetyValidator


class ContextAgent:
    """
    Context Agent for analyzing student input and providing contextual guidance.
    
    This streamlined adapter delegates to specialized processor modules.
    """
    
    def __init__(self, domain="architecture"):
        """Initialize the Context Agent with modular processors."""
        self.telemetry = AgentTelemetry("context_agent")
        self.telemetry.log_agent_start("__init__", domain=domain)
        
        # Core properties
        self.domain = domain
        self.name = "context_agent"
        
        # Initialize LLM client
        self.client = LLMClient(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        
        # Initialize shared utilities
        self.text_processor = TextProcessor()
        self.safety_validator = SafetyValidator()
        self.metrics_calculator = MetricsCalculator()
        
        # Initialize modular processors
        self.input_processor = InputClassificationProcessor()
        self.content_processor = ContentAnalysisProcessor()
        self.conversation_processor = ConversationAnalysisProcessor()
        self.context_processor = ContextGenerationProcessor()
        self.response_processor = ResponseBuilderProcessor()
        
        self.telemetry.log_agent_end("__init__")
        print(f"🎯 {self.name} initialized for domain: {domain}")
    
    async def analyze_student_input(self, state: ArchMentorState, current_input: str) -> AgentResponse:
        """
        Main processing method - analyzes student input and provides contextual guidance.
        """
        self.telemetry.log_agent_start("analyze_student_input")
        
        try:
            # Step 1: Perform core classification
            core_classification = await self.input_processor.perform_core_classification(current_input, state)
            
            # Step 2: Perform content analysis
            content_analysis = self.content_processor.perform_content_analysis(current_input, state)
            
            # Step 3: Analyze conversation patterns
            conversation_patterns = self.conversation_processor.analyze_conversation_patterns(state, current_input)
            
            # Step 4: Generate contextual metadata
            contextual_metadata = self.context_processor.generate_contextual_metadata(
                current_input, state, core_classification
            )
            
            # Step 5: Prepare routing suggestions
            routing_suggestions = self.context_processor.prepare_routing_suggestions(
                core_classification, content_analysis, conversation_patterns, contextual_metadata
            )
            
            # Step 6: Prepare agent contexts
            agent_contexts = self.context_processor.prepare_agent_contexts(
                core_classification, content_analysis, conversation_patterns, contextual_metadata
            )
            
            # Step 7: Create context package
            context_package = ContextPackage(
                core_classification=core_classification,
                content_analysis=content_analysis,
                conversation_patterns=conversation_patterns,
                contextual_metadata=contextual_metadata,
                routing_suggestions=routing_suggestions,
                agent_contexts=agent_contexts,
                context_quality=self.response_processor.assess_context_quality(core_classification, content_analysis),
                package_timestamp=self._get_current_timestamp()
            )
            
            # Step 8: Convert to AgentResponse
            agent_response = self.response_processor.convert_to_agent_response(
                context_package, current_input, state
            )
            
            self.telemetry.log_agent_end("analyze_student_input")
            return agent_response
            
        except Exception as e:
            self.telemetry.log_error(f"Student input analysis failed: {str(e)}")
            return ResponseBuilder.create_error_response(
                f"Context analysis failed: {str(e)}",
                agent_name=self.name
            )
    
    # Delegation methods for backward compatibility
    
    async def perform_core_classification(self, input_text: str, state: ArchMentorState) -> CoreClassification:
        """Perform core classification (delegates to processor)."""
        return await self.input_processor.perform_core_classification(input_text, state)
    
    def perform_content_analysis(self, input_text: str, state: ArchMentorState) -> ContentAnalysis:
        """Perform content analysis (delegates to processor)."""
        return self.content_processor.perform_content_analysis(input_text, state)
    
    def analyze_conversation_patterns(self, state: ArchMentorState, current_input: str) -> ConversationPatterns:
        """Analyze conversation patterns (delegates to processor)."""
        return self.conversation_processor.analyze_conversation_patterns(state, current_input)
    
    def generate_contextual_metadata(self, input_text: str, state: ArchMentorState, 
                                   classification: CoreClassification) -> ContextualMetadata:
        """Generate contextual metadata (delegates to processor)."""
        return self.context_processor.generate_contextual_metadata(input_text, state, classification)
    
    def prepare_routing_suggestions(self, core_classification: CoreClassification, 
                                  content_analysis: ContentAnalysis,
                                  conversation_patterns: ConversationPatterns,
                                  metadata: ContextualMetadata) -> Dict[str, Any]:
        """Prepare routing suggestions (delegates to processor)."""
        return self.context_processor.prepare_routing_suggestions(
            core_classification, content_analysis, conversation_patterns, metadata
        )
    
    def prepare_agent_contexts(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                             conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Dict[str, Any]]:
        """Prepare agent contexts (delegates to processor)."""
        return self.context_processor.prepare_agent_contexts(
            classification, content_analysis, conversation_patterns, metadata
        )
    
    def convert_to_agent_response(self, context_package: ContextPackage, current_input: str, 
                                state: ArchMentorState) -> AgentResponse:
        """Convert to agent response (delegates to processor)."""
        return self.response_processor.convert_to_agent_response(context_package, current_input, state)
    
    def calculate_enhancement_metrics(self, context_package: ContextPackage) -> EnhancementMetrics:
        """Calculate enhancement metrics (delegates to processor)."""
        return self.response_processor.calculate_enhancement_metrics(context_package)
    
    def extract_cognitive_flags(self, core_classification: CoreClassification) -> List[CognitiveFlag]:
        """Extract cognitive flags (delegates to processor)."""
        return self.response_processor.extract_cognitive_flags(core_classification)
    
    def generate_response_text(self, core_classification: CoreClassification, current_input: str) -> str:
        """Generate response text (delegates to processor)."""
        return self.response_processor.generate_response_text(core_classification, current_input)
    
    # Input classification delegation methods
    
    def _classify_interaction_type(self, input_text: str, state: ArchMentorState = None) -> str:
        """Classify interaction type (delegates to processor)."""
        return self.input_processor._classify_interaction_type(input_text, state)
    
    def _detect_understanding_level(self, input_lower: str) -> str:
        """Detect understanding level (delegates to processor)."""
        return self.input_processor._detect_understanding_level(input_lower)
    
    def _assess_confidence_level(self, input_lower: str) -> str:
        """Assess confidence level (delegates to processor)."""
        return self.input_processor._assess_confidence_level(input_lower)
    
    def _detect_engagement_level(self, input_lower: str, input_text: str) -> str:
        """Detect engagement level (delegates to processor)."""
        return self.input_processor._detect_engagement_level(input_lower, input_text)
    
    def _is_response_to_previous_question(self, current_input: str, state: ArchMentorState) -> bool:
        """Check if response to previous question (delegates to processor)."""
        return self.input_processor._is_response_to_previous_question(current_input, state)
    
    def _is_technical_question(self, input_text: str) -> bool:
        """Check if technical question (delegates to processor)."""
        return self.input_processor._is_technical_question(input_text)
    
    def _is_feedback_request(self, input_text: str) -> bool:
        """Check if feedback request (delegates to processor)."""
        return self.input_processor._is_feedback_request(input_text)
    
    # Content analysis delegation methods
    
    def _extract_technical_terms(self, input_text: str) -> List[str]:
        """Extract technical terms (delegates to processor)."""
        return self.content_processor._extract_technical_terms(input_text)
    
    def _extract_emotional_indicators(self, input_text: str) -> Dict[str, int]:
        """Extract emotional indicators (delegates to processor)."""
        return self.content_processor._extract_emotional_indicators(input_text)
    
    def _assess_complexity(self, input_text: str) -> float:
        """Assess complexity (delegates to processor)."""
        return self.content_processor._assess_complexity(input_text)
    
    def _assess_specificity(self, input_text: str, state: ArchMentorState) -> float:
        """Assess specificity (delegates to processor)."""
        return self.content_processor._assess_specificity(input_text, state)
    
    # Conversation analysis delegation methods
    
    def _detect_repetitive_topics(self, messages: List[str]) -> bool:
        """Detect repetitive topics (delegates to processor)."""
        return self.conversation_processor._detect_repetitive_topics(messages)
    
    def _detect_topic_jumping(self, messages: List[str]) -> bool:
        """Detect topic jumping (delegates to processor)."""
        return self.conversation_processor._detect_topic_jumping(messages)
    
    def _analyze_engagement_trend(self, messages: List[str]) -> str:
        """Analyze engagement trend (delegates to processor)."""
        return self.conversation_processor._analyze_engagement_trend(messages)
    
    def _analyze_understanding_progression(self, messages: List[str]) -> str:
        """Analyze understanding progression (delegates to processor)."""
        return self.conversation_processor._analyze_understanding_progression(messages)
    
    def _identify_recent_focus(self, recent_messages: List[str]) -> List[str]:
        """Identify recent focus (delegates to processor)."""
        return self.conversation_processor._identify_recent_focus(recent_messages)
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text (delegates to processor)."""
        return self.conversation_processor._extract_topics_from_text(text)
    
    # Context generation delegation methods
    
    def _assess_complexity_appropriateness(self, classification: CoreClassification, state: ArchMentorState) -> str:
        """Assess complexity appropriateness (delegates to processor)."""
        return self.context_processor._assess_complexity_appropriateness(classification, state)
    
    def _assess_response_urgency(self, classification: CoreClassification) -> str:
        """Assess response urgency (delegates to processor)."""
        return self.context_processor._assess_response_urgency(classification)
    
    def _identify_pedagogical_opportunity(self, classification: CoreClassification, input_text: str) -> str:
        """Identify pedagogical opportunity (delegates to processor)."""
        return self.context_processor._identify_pedagogical_opportunity(classification, input_text)
    
    def _identify_continuation_cues(self, state: ArchMentorState, input_text: str) -> List[str]:
        """Identify continuation cues (delegates to processor)."""
        return self.context_processor._identify_continuation_cues(state, input_text)
    
    def _assess_difficulty_adjustment(self, classification: CoreClassification, state: ArchMentorState) -> str:
        """Assess difficulty adjustment (delegates to processor)."""
        return self.context_processor._assess_difficulty_adjustment(classification, state)
    
    def _suggest_question_type(self, classification: CoreClassification) -> str:
        """Suggest question type based on classification."""
        try:
            if classification.understanding_level == 'low':
                return 'clarifying_question'
            elif classification.understanding_level == 'high' and classification.confidence_level == 'high':
                return 'challenging_question'
            elif classification.engagement_level == 'low':
                return 'engaging_question'
            elif classification.is_technical_question:
                return 'technical_deep_dive'
            else:
                return 'exploratory_question'
                
        except Exception as e:
            self.telemetry.log_error("_suggest_question_type", str(e))
            return 'exploratory_question'
    
    def _assess_challenge_readiness(self, classification: CoreClassification) -> str:
        """Assess challenge readiness (delegates to processor)."""
        return self.context_processor._assess_challenge_readiness(classification)
    
    def _identify_information_gaps(self, input_text: str) -> List[str]:
        """Identify information gaps (delegates to processor)."""
        return self.context_processor._identify_information_gaps(input_text)
    
    def _identify_analysis_focus_areas(self, input_text: str, state: ArchMentorState) -> List[str]:
        """Identify analysis focus areas (delegates to processor)."""
        return self.context_processor._identify_analysis_focus_areas(input_text, state)
    
    # Response building delegation methods
    
    def _calculate_cognitive_offloading_prevention(self, classification: CoreClassification) -> float:
        """Calculate cognitive offloading prevention (delegates to processor)."""
        return self.response_processor._calculate_cognitive_offloading_prevention(classification)
    
    def _calculate_deep_thinking_engagement(self, classification: CoreClassification) -> float:
        """Calculate deep thinking engagement (delegates to processor)."""
        return self.response_processor._calculate_deep_thinking_engagement(classification)
    
    def _calculate_knowledge_integration(self, content_analysis: ContentAnalysis) -> float:
        """Calculate knowledge integration (delegates to processor)."""
        return self.response_processor._calculate_knowledge_integration(content_analysis)
    
    def _calculate_learning_progression(self, context_package: ContextPackage) -> float:
        """Calculate learning progression (delegates to processor)."""
        return self.response_processor._calculate_learning_progression(context_package)
    
    def _calculate_metacognitive_awareness(self, classification: CoreClassification) -> float:
        """Calculate metacognitive awareness (delegates to processor)."""
        return self.response_processor._calculate_metacognitive_awareness(classification)
    
    def _calculate_scientific_confidence(self, classification: CoreClassification) -> float:
        """Calculate scientific confidence (delegates to processor)."""
        return self.response_processor._calculate_scientific_confidence(classification)
    
    def _assess_scaffolding_effectiveness(self, context_package: ContextPackage) -> float:
        """Assess scaffolding effectiveness (delegates to processor)."""
        return self.response_processor._assess_scaffolding_effectiveness(context_package)
    
    def assess_context_quality(self, classification: CoreClassification, content_analysis: ContentAnalysis) -> float:
        """Assess context quality (delegates to processor)."""
        return self.response_processor.assess_context_quality(classification, content_analysis)
    
    # Utility methods
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        return self.telemetry.get_timestamp()
    
    def create_context_summary(self, context_package: ContextPackage) -> str:
        """Create context summary (delegates to processor)."""
        return self.response_processor.create_context_summary(context_package)
    
    def validate_classification(self, classification: CoreClassification) -> bool:
        """Validate classification (delegates to processor)."""
        return self.input_processor.validate_classification(classification)
    
    def get_classification_summary(self, classification: CoreClassification) -> str:
        """Get classification summary (delegates to processor)."""
        return self.input_processor.get_classification_summary(classification)
    
    # Private methods for internal processing (maintain compatibility)
    
    async def _perform_core_classification(self, input_text: str, state: ArchMentorState) -> CoreClassification:
        """Internal core classification method."""
        return await self.perform_core_classification(input_text, state)
    
    def _perform_content_analysis(self, input_text: str, state: ArchMentorState) -> ContentAnalysis:
        """Internal content analysis method."""
        return self.perform_content_analysis(input_text, state)
    
    def _analyze_conversation_patterns(self, state: ArchMentorState, current_input: str) -> ConversationPatterns:
        """Internal conversation patterns analysis."""
        return self.analyze_conversation_patterns(state, current_input)
    
    def _generate_contextual_metadata(self, input_text: str, state: ArchMentorState, 
                                    classification: CoreClassification) -> ContextualMetadata:
        """Internal contextual metadata generation."""
        return self.generate_contextual_metadata(input_text, state, classification)
    
    def _prepare_routing_suggestions(self, core_classification: CoreClassification, 
                                   content_analysis: ContentAnalysis,
                                   conversation_patterns: ConversationPatterns,
                                   metadata: ContextualMetadata) -> Dict[str, Any]:
        """Internal routing suggestions preparation."""
        return self.prepare_routing_suggestions(core_classification, content_analysis, conversation_patterns, metadata)
    
    def _prepare_agent_contexts(self, classification: CoreClassification, content_analysis: ContentAnalysis,
                              conversation_patterns: ConversationPatterns, metadata: ContextualMetadata) -> Dict[str, Dict[str, Any]]:
        """Internal agent contexts preparation."""
        return self.prepare_agent_contexts(classification, content_analysis, conversation_patterns, metadata)
    
    def _convert_to_agent_response(self, context_package: ContextPackage, current_input: str, 
                                 state: ArchMentorState) -> AgentResponse:
        """Internal agent response conversion."""
        return self.convert_to_agent_response(context_package, current_input, state)
    
    def _generate_response_text(self, core_classification: CoreClassification, current_input: str) -> str:
        """Internal response text generation."""
        return self.generate_response_text(core_classification, current_input)
    
    def _extract_cognitive_flags(self, core_classification: CoreClassification) -> List[CognitiveFlag]:
        """Internal cognitive flags extraction."""
        return self.extract_cognitive_flags(core_classification)
    
    def _calculate_enhancement_metrics(self, context_package: ContextPackage) -> EnhancementMetrics:
        """Internal enhancement metrics calculation."""
        return self.calculate_enhancement_metrics(context_package)
    
    # Cleanup
    def __del__(self):
        """Cleanup method."""
        try:
            self.telemetry.log_agent_end("cleanup")
        except:
            pass 