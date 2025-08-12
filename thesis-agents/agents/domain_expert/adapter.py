"""
Domain Expert Agent Adapter - streamlined modular version.

This adapter maintains backward compatibility while delegating to processor modules.
"""

import sys
import os
import logging
import re
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
        Enhanced AI-powered knowledge provision with contextual, thinking-prompting responses.
        """
        self.telemetry.log_agent_start("provide_knowledge")

        try:
            # Get user's actual question
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            user_input = user_messages[-1] if user_messages else ""

            if not user_input:
                return self._generate_fallback_response(state, context_classification, analysis_result, routing_decision)

            # Extract building type and project context
            building_type = self._extract_building_type_from_context(state)
            project_context = state.current_design_brief or "architectural project"

            # Determine knowledge gap type
            gap_type = context_classification.get("primary_gap", "general_knowledge")

            print(f"\n📚 {self.name} providing AI-powered knowledge for: {gap_type}")
            print(f"   Building type: {building_type}")
            print(f"   User question: {user_input[:100]}...")

            # DETECT KNOWLEDGE REQUEST PATTERNS
            print(f"🔍 Analyzing knowledge request: '{user_input[:50]}...'")
            knowledge_pattern = self._analyze_knowledge_request(user_input, gap_type, state)
            print(f"🎯 Knowledge pattern detected: {knowledge_pattern['type']}")
            
            # Handle legitimate example requests properly
            if knowledge_pattern["type"] == "legitimate_example_request":
                print(f"📚 Legitimate example request detected - providing examples")
                response_result = await self._provide_focused_examples(state, user_input, gap_type)
                return self._convert_to_agent_response_internal(response_result, state, context_classification, analysis_result, routing_decision)
            
            # Handle premature example requests (cognitive offloading protection)
            if knowledge_pattern["type"] == "premature_example_request":
                print(f"🛡️ Cognitive protection: Example request too early")
                response_result = await self._generate_premature_example_response(user_input, building_type, project_context)
                return self._convert_to_agent_response_internal(response_result, state, context_classification, analysis_result, routing_decision)

            # Generate AI-powered contextual response for standard requests
            ai_response = await self._generate_contextual_knowledge_response(
                user_input, building_type, project_context, gap_type, state
            )

            # Create response metadata
            response_metadata = {
                "agent": self.name,
                "response_type": "thinking_prompt_knowledge",
                "knowledge_gap_addressed": gap_type,
                "building_type": building_type,
                "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                "sources": [],
                "processing_method": "ai_powered_contextual"
            }

            # Convert to AgentResponse
            agent_response = ResponseBuilder.create_knowledge_response(
                response_text=ai_response,
                sources_used=[],
                metadata=response_metadata
            )

            # Add cognitive flags manually
            agent_response.cognitive_flags = [CognitiveFlag.ENCOURAGES_THINKING] if "?" in ai_response else []

            self.telemetry.log_agent_end("provide_knowledge")
            return agent_response

        except Exception as e:
            self.telemetry.log_error(f"Knowledge provision failed: {str(e)}")
            return ResponseBuilder.create_error_response(
                f"Knowledge provision failed: {str(e)}",
                agent_name=self.name
            )

    async def _generate_gamified_knowledge_challenge_response(self, user_input: str, state: ArchMentorState,
                                                           context_classification: Dict, analysis_result: Dict, gap_type: str):
        """Generate gamified knowledge response with application challenge."""
        try:
            building_type = self._extract_building_type_from_context(state)
            project_context = state.current_design_brief or "architectural project"

            # Create gamified knowledge prompt
            prompt = f"""
            Provide rich, contextual knowledge about the user's question, then create an engaging application challenge.

            User's question: "{user_input}"
            Building type: {building_type}
            Project context: {project_context}

            Structure your response as:
            1. Rich knowledge explanation with real-world relevance
            2. Connect directly to their project context
            3. Quick application challenge with 3-4 options (A, B, C, D format with emojis)
            4. Ask for their choice and reasoning
            5. Set up exploration of implications

            Make the knowledge engaging and the challenge thought-provoking.
            Use emojis strategically for visual appeal but maintain professional depth.
            Include research backing or examples where relevant.
            """

            response = await self._generate_llm_response(prompt, state, analysis_result)

            return {
                "response_text": response,
                "response_strategy": "knowledge_with_application_challenge",
                "educational_intent": "knowledge_application",
                "gamified_behavior": "knowledge_with_application_challenge",
                "sources": [],
                "metadata": {
                    "knowledge_type": gap_type,
                    "building_type": building_type,
                    "challenge_included": True
                }
            }

        except Exception as e:
            self.telemetry.log_error(f"Gamified knowledge challenge response failed: {str(e)}")
            return await self._generate_fallback_knowledge_response(state, analysis_result, gap_type)
    
    async def discover_knowledge(self, state: ArchMentorState, context_classification: Dict,
                               analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """
        Alternative knowledge discovery method.
        """
        # For now, delegate to provide_knowledge
        return await self.provide_knowledge(state, context_classification, analysis_result, routing_decision)

    async def provide_domain_knowledge(self, user_input: str, state: ArchMentorState) -> Dict[str, Any]:
        """
        Backward compatibility method for original API.
        """
        # Create minimal context for the new API
        context_classification = {"primary_gap": "general_knowledge"}
        analysis_result = {"cognitive_flags": ["needs_knowledge_guidance"]}
        routing_decision = {"route": "domain_expert"}

        # Call the new method
        agent_response = await self.provide_knowledge(state, context_classification, analysis_result, routing_decision)

        # Convert back to old format
        if hasattr(agent_response, 'to_dict'):
            return agent_response.to_dict()
        else:
            return {
                "response_text": str(agent_response),
                "agent": self.name,
                "response_type": "knowledge_delivery"
            }
    
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

    async def _generate_contextual_knowledge_response(self, user_input: str, building_type: str,
                                                    project_context: str, gap_type: str, state: ArchMentorState) -> str:
        """Generate AI-powered contextual knowledge response that encourages thinking."""

        # Import OpenAI client
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
        You are a distinguished architectural scholar and mentor with expertise in design theory, building science, and critical practice. Your role is to provide academically rigorous knowledge that stimulates intellectual inquiry rather than passive consumption.

        STUDENT INQUIRY: "{user_input}"
        BUILDING TYPOLOGY: {building_type}
        PROJECT CONTEXT: {project_context}
        KNOWLEDGE DOMAIN: {gap_type}

        CRITICAL REQUIREMENT: You MUST provide EXACTLY the number of strategies you promise. If you say "three strategies," you MUST provide THREE complete strategies.

        Craft a complete scholarly response that:
        1. PROVIDES PRACTICAL SOLUTION: Offer concrete, actionable guidance that directly addresses their question
        2. GROUNDS IN THEORY: Reference architectural theory, design principles, or established methodologies
        3. PRESENTS MULTIPLE APPROACHES: Show 2-3 different design strategies with their rationales
        4. ENCOURAGES CRITICAL THINKING: Explain the implications and trade-offs of different approaches
        5. CONTEXTUALIZES TO PROJECT: Make all guidance specific to their {building_type} project
        6. MAINTAINS ACADEMIC RIGOR: Use scholarly language while remaining accessible
        7. ENDS NATURALLY: Ensure the response concludes with a complete thought before any question

        RESPONSE STRUCTURE:
        - Start with direct acknowledgment of their question
        - If you mention "three strategies," you MUST provide THREE numbered strategies (1., 2., 3.)
        - If you mention "two approaches," you MUST provide TWO numbered approaches (1., 2.)
        - Each strategy/approach must be complete with explanation and rationale
        - Explain practical implications for their specific building type
        - End with a complete conclusion that synthesizes the guidance
        - THEN ask ONE specific, thoughtful question that builds directly on the guidance provided

        STRATEGY COMPLETENESS RULE: 
        - If you say "Here are three strategies," you MUST provide:
          1. First strategy with full explanation
          2. Second strategy with full explanation  
          3. Third strategy with full explanation
        - Do NOT promise more strategies than you deliver
        - Each strategy must be substantial and complete

        For example, if they ask about "sustainable materials":
        "Your question about sustainable materials touches on a fundamental tension in contemporary practice between environmental responsibility and design performance. For your {building_type} project, I'd recommend considering three approaches:

        1. Bio-based materials like cross-laminated timber offer structural efficiency while sequestering carbon, though they require careful moisture detailing. Second, reclaimed materials provide embodied energy savings and unique aesthetic qualities, but need structural verification. Third, high-performance recycled materials like recycled steel or concrete with fly ash reduce environmental impact while maintaining familiar construction methods.

        The choice depends on your project's priorities and local availability. Each approach has different implications for your design language, construction timeline, and long-term performance.

        Given your {building_type} program, which aspect is most critical - minimizing environmental impact, achieving specific aesthetic goals, or optimizing construction efficiency?"

        Write a complete, naturally-ending response (250-350 words) that provides real value and follows the strategy completeness rule:
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,  # Increased for complete responses
                temperature=0.3
            )

            ai_response = response.choices[0].message.content.strip()

            # Ensure response ends naturally (not mid-sentence)
            if ai_response and not ai_response.endswith(('.', '?', '!')):
                # Find the last complete sentence
                sentences = ai_response.split('.')
                if len(sentences) > 1:
                    ai_response = '.'.join(sentences[:-1]) + '.'

            print(f"📚 AI-generated contextual response: {ai_response[:100]}...")
            return ai_response

        except Exception as e:
            print(f"⚠️ AI response generation failed: {e}")
            return await self._generate_llm_fallback_knowledge_response(user_input, building_type, project_context, gap_type)

    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Robust building-type inference that prefers the declared project type and only changes on explicit signals.

        Rules:
        - Prefer analysis_result.text_analysis.building_type if set and not 'unknown'.
        - Establish a base_type from the initial brief + first user message.
        - Mentions in later messages do NOT change the type unless an explicit switch phrase is detected.
        - Avoid inferring 'museum' from generic words like 'exhibition' or 'cultural center'.
        """

        def detect_explicit(text: str, type_word: str) -> bool:
            t = text.lower()
            patterns = [
                f"i am designing a {type_word}",
                f"designing a {type_word}",
                f"project is a {type_word}",
                f"project type is {type_word}",
                f"this is a {type_word}",
            ]
            return any(p in t for p in patterns)

        def detect_switch(text: str, type_word: str) -> bool:
            t = text.lower()
            patterns = [
                f"switch to {type_word}",
                f"change to {type_word}",
                f"make it a {type_word}",
                f"let's make it a {type_word}",
            ]
            return any(p in t for p in patterns)

        canonical_types = [
            "community center", "school", "office", "museum", "library", "hospital",
            "residential", "restaurant", "retail", "industrial", "religious"
        ]

        # 1) Prefer analyzer result if available
        try:
            analysis = getattr(state, 'analysis_result', None)
            if isinstance(analysis, dict):
                bt = analysis.get('text_analysis', {}).get('building_type')
                if bt and bt != 'unknown':
                    base_type = bt.lower()
                else:
                    base_type = None
            else:
                base_type = None
        except Exception:
            base_type = None

        # 2) Establish base from initial brief and first user message (if not set)
        initial_user_msgs = [m.get('content', '') for m in state.messages if m.get('role') == 'user']
        first_user = initial_user_msgs[0].lower() if initial_user_msgs else ""
        brief_lower = (getattr(state, 'current_design_brief', None) or "").lower()

        if not base_type:
            # Strong phrase-first detection across canonical types
            for ct in canonical_types:
                if detect_explicit(brief_lower, ct) or detect_explicit(first_user, ct):
                    base_type = ct
                    break
        if not base_type:
            # Keyword presence as a weak hint, pick first match in brief or first message
            for ct in canonical_types:
                if ct in brief_lower or ct in first_user:
                    base_type = ct
                    break

        # Default fallback if still unknown
        if not base_type:
            base_type = "project"

        # 3) Only change type later if explicit switch phrases are detected
        recent_user_msgs = [m.get('content', '') for m in state.messages[-5:] if m.get('role') == 'user']
        combined_recent = " \n".join(recent_user_msgs).lower()
        for ct in canonical_types:
            if detect_switch(combined_recent, ct) or detect_explicit(combined_recent, ct):
                # Respect an explicit change
                return ct

        # 4) Avoid over-triggering 'museum' from generic terms
        if base_type == "museum":
            # Confirm 'museum' explicitly exists; ignore generic exhibition terms
            if ("museum" not in brief_lower) and ("museum" not in first_user):
                # Roll back to project unless explicitly switched later
                base_type = "project"

        return base_type

    async def _generate_llm_fallback_knowledge_response(self, user_input: str, building_type: str,
                                                      project_context: str, gap_type: str) -> str:
        """Generate LLM-based fallback response when AI fails."""

        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""
        You are an architectural domain expert. Your main LLM generation failed, so you need to provide a helpful fallback response.

        STUDENT'S QUESTION: "{user_input}"
        BUILDING TYPE: {building_type}
        PROJECT CONTEXT: {project_context}
        KNOWLEDGE DOMAIN: {gap_type}

        Provide a helpful response that:
        1. Acknowledges their specific question about {gap_type}
        2. Offers 2-3 concrete principles or approaches they can consider
        3. Relates specifically to their {building_type} project
        4. Ends with a thoughtful question that builds on the guidance provided
        5. Avoids saying you "don't have information" - instead provide what you can

        Keep it educational and specific to their situation (150-200 words).
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.4
            )

            fallback_response = response.choices[0].message.content.strip()

            # Ensure response ends naturally
            if fallback_response and not fallback_response.endswith(('.', '?', '!')):
                sentences = fallback_response.split('.')
                if len(sentences) > 1:
                    fallback_response = '.'.join(sentences[:-1]) + '.'

            return fallback_response

        except Exception as e:
            print(f"⚠️ LLM fallback response generation failed: {e}")
            # Only as last resort, use a contextual template
            return f"Let me help you explore {gap_type.replace('_', ' ')} for your {building_type} project. This involves considering user needs, functional requirements, and design principles. What specific aspect of {gap_type.replace('_', ' ')} is most important for your project goals?"

    def _generate_fallback_knowledge_response(self, user_input: str, building_type: str,
                                            project_context: str, gap_type: str) -> str:
        """Legacy fallback method - now calls LLM version."""
        import asyncio
        return asyncio.run(self._generate_llm_fallback_knowledge_response(user_input, building_type, project_context, gap_type))

    def _generate_fallback_response(self, state: ArchMentorState, context_classification: Dict,
                                  analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """Generate fallback response when no user input is available."""

        building_type = self._extract_building_type_from_context(state)

        response_text = f"""I'm here to help you explore architectural knowledge for your {building_type} project.

What specific aspect would you like to discuss? I can help you think through:
- Design principles and strategies
- Technical requirements and considerations
- Material choices and their implications
- Spatial organization and circulation
- Environmental and sustainability factors

What questions do you have about your design?"""

        return ResponseBuilder.create_knowledge_response(
            response_text=response_text,
            sources_used=[],
            metadata={"response_type": "fallback_prompt", "building_type": building_type}
        )

    # Cleanup
    def __del__(self):
        """Cleanup method."""
        try:
            self.telemetry.log_agent_end("cleanup")
        except:
            pass

    def _analyze_knowledge_request(self, user_input: str, gap_type: str, state: ArchMentorState = None) -> Dict[str, Any]:
        """Analyze the type of knowledge request to prevent cognitive offloading."""
        
        analysis = {
            "type": "standard_knowledge_request",
            "cognitive_risk": "low",
            "indicators": []
        }
        
        user_input_lower = user_input.lower()
        
        # ENHANCED: Better detection of legitimate example requests
        example_request_keywords = [
            "example", "examples", "precedent", "precedents", "case study", "case studies",
            "project", "projects", "show me", "can you give", "can you provide", "provide",
            "inspiration", "references", "similar projects", "ideas", "real project", "built project"
        ]
        
        # Check if this is a legitimate example request
        is_example_request = any(keyword in user_input_lower for keyword in example_request_keywords)
        print(f"🔍 Example request check: {is_example_request} (keywords found: {[k for k in example_request_keywords if k in user_input_lower]})")
        
        if is_example_request:
            # Check cognitive offloading protection (minimum 5 messages required)
            if state and hasattr(state, 'messages'):
                message_count = len([msg for msg in state.messages if msg.get('role') == 'user'])
                if message_count < 5:
                    analysis["type"] = "premature_example_request"
                    analysis["cognitive_risk"] = "high"
                    analysis["indicators"].append(f"Example request too early (only {message_count} messages, need 5+)")
                    analysis["cognitive_protection"] = "active"
                    return analysis
            
            # This is a legitimate example request - should provide examples
            analysis["type"] = "legitimate_example_request"
            analysis["cognitive_risk"] = "low"
            analysis["indicators"].append("Legitimate example request detected")
            return analysis
        
        # PATTERN 1: Direct answer seeking (but NOT example requests)
        direct_patterns = [
            "what is the", "what are the", "tell me the", 
            "what should I", "what do I need", "the answer is", "the solution is"
        ]
        
        if any(pattern in user_input_lower for pattern in direct_patterns):
            analysis["type"] = "direct_answer_seeking"
            analysis["cognitive_risk"] = "high"
            analysis["indicators"].append("Direct answer seeking detected")
        
        # PATTERN 2: Passive acceptance indicators
        passive_patterns = [
            "okay", "sure", "fine", "whatever", "I guess",
            "that works", "good enough"
        ]
        
        if any(pattern in user_input_lower for pattern in passive_patterns):
            analysis["type"] = "passive_acceptance"
            analysis["cognitive_risk"] = "high"
            analysis["indicators"].append("Passive acceptance detected")
        
        return analysis

    async def _provide_focused_examples(self, state: ArchMentorState, user_input: str, gap_type: str) -> Dict[str, Any]:
        """Provide focused examples using database and web search - completely topic-agnostic."""
        print(f"🔄 Providing focused examples for: {user_input}")
        
        # Extract building type and topic
        building_type = self._extract_building_type_from_context(state)
        user_topic = self._extract_topic_from_user_input(user_input)
        project_context = getattr(state, 'current_design_brief', '') or ''
        
        print(f"   🏗️  Building type: {building_type}")
        print(f"   🎯 Topic: {user_topic}")
        print(f"   📋 Context: {project_context}")
        
        # Search examples: local DB first, then web
        try:
            knowledge_results: List[Dict[str, Any]] = []
            
            # Try local database first
            try:
                from knowledge_base.knowledge_manager import KnowledgeManager
                km = KnowledgeManager(domain="architecture")
                
                # Create flexible, topic-agnostic search query
                db_query = f"{user_topic} {building_type} architecture case study precedent project example"
                
                print(f"   🗄️  DB search query: {db_query}")
                db_results = km.search_knowledge(db_query, n_results=8)
                
                # Convert DB results to the format expected by synthesis processor
                for r in db_results:
                    knowledge_results.append({
                        "title": r.get("metadata", {}).get("title", "Untitled"),
                        "url": r.get("metadata", {}).get("source_url", ""),
                        "snippet": r.get("content", "")[:200] + "..." if len(r.get("content", "")) > 200 else r.get("content", ""),
                        "content": r.get("content", ""),
                        "source": "local_db"
                    })
                    
                print(f"   ✅ Found {len(knowledge_results)} database results")
                
            except Exception as e:
                print(f"⚠️ Local DB search unavailable: {e}")

            # If we don't have enough results, try web search
            if len(knowledge_results) < 3:
                try:
                    # Create flexible web search query
                    context_query = f"{user_topic} {building_type} architecture case study precedent project"
                    print(f"   🌐 Web search query: {context_query}")
                    
                    web_results = await self.search_processor.search_web_for_knowledge(context_query, state)
                    if web_results:
                        # Convert web results to the format expected by synthesis processor
                        for r in web_results:
                            # Extract from metadata structure that web search actually returns
                            title = r.get("metadata", {}).get("title", "Untitled")
                            url = r.get("metadata", {}).get("url", "")
                            content = r.get("content", "")
                            snippet = content[:200] + "..." if len(content) > 200 else content
                            
                            knowledge_results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "content": content,
                                "source": "web_search",
                                # Add metadata structure for compatibility
                                "metadata": {
                                    "title": title,
                                    "url": url,
                                    "source_url": url
                                }
                            })
                        
                        print(f"   ✅ Found {len([r for r in knowledge_results if r['source'] == 'web_search'])} web results")
                        
                except Exception as e:
                    print(f"⚠️ Web search failed: {e}")

            # Use the knowledge synthesis processor to create properly formatted examples
            # This processor handles relevance filtering and formatting dynamically
            if knowledge_results:
                # Use the simple, working approach from the old repository
                # Let the LLM intelligently process all results instead of pre-filtering
                examples_text = await self._synthesize_examples_with_llm(
                    user_topic, knowledge_results, building_type
                )
                
                return {
                    "response_text": examples_text,
                    "response_type": "focused_examples",
                    "sources": knowledge_results,
                    "examples_provided": True
                }
            else:
                # If no results at all, provide a helpful message about the topic
                return {
                    "response_text": f"I'd be happy to help you find examples of {user_topic} in {building_type} architecture. This is an interesting area that could benefit from case studies and precedents. Would you like me to search for specific aspects of this topic, or do you have particular examples in mind?",
                    "response_type": "no_examples_found",
                    "sources": [],
                    "examples_provided": False
                }
                
        except Exception as e:
            print(f"⚠️ Example search failed: {e}")
            return {
                "response_text": f"I encountered an issue while searching for examples of {user_topic} in {building_type} architecture. This could be due to technical limitations or the specific nature of your question. Would you like to rephrase your question or focus on a different aspect of {user_topic}?",
                "response_type": "search_error",
                "sources": [],
                "examples_provided": False
            }

    def _get_quality_modifiers(self, user_input: str, topic: str) -> str:
        """Get quality modifiers to enhance search queries and get better examples."""
        user_input_lower = user_input.lower()
        topic_lower = topic.lower()
        
        # Extract quality indicators from user input
        quality_words = []
        
        # Check for specific quality indicators
        if any(word in user_input_lower for word in ["interesting", "innovative", "creative", "unique"]):
            quality_words.extend(["interesting", "innovative"])
        elif any(word in user_input_lower for word in ["famous", "renowned", "iconic", "landmark"]):
            quality_words.extend(["famous", "renowned"])
        elif any(word in user_input_lower for word in ["best", "excellent", "outstanding", "award-winning"]):
            quality_words.extend(["best", "award-winning"])
        elif any(word in user_input_lower for word in ["modern", "contemporary", "cutting-edge"]):
            quality_words.extend(["modern", "contemporary"])
        elif any(word in user_input_lower for word in ["sustainable", "green", "eco-friendly"]):
            quality_words.extend(["sustainable", "innovative"])
        
        # Add topic-specific quality modifiers
        if topic_lower == "circulation":
            if not quality_words:
                quality_words.extend(["innovative", "interesting"])
        elif topic_lower == "lighting":
            if not quality_words:
                quality_words.extend(["excellent", "innovative"])
        elif topic_lower == "materials":
            if not quality_words:
                quality_words.extend(["innovative", "sustainable"])
        elif topic_lower == "sustainability":
            if not quality_words:
                quality_words.extend(["leading", "innovative"])
        
        # Default quality modifiers if none found
        if not quality_words:
            quality_words = ["innovative", "interesting"]
        
        # Return the first 2-3 quality modifiers
        return " ".join(quality_words[:2])

    def _extract_topic_from_user_input(self, user_input: str) -> str:
        """Extract the main architectural topic from user input"""
        
        # Common architectural topics
        topic_keywords = {
            "flexible spaces": ["flexible", "flexibility", "adaptable", "multi-use"],
            "lighting": ["light", "lighting", "daylight", "illumination"],
            "circulation": ["circulation", "flow", "movement", "path"],
            "accessibility": ["access", "accessible", "universal design"],
            "sustainability": ["sustainable", "green", "environmental", "eco"],
            "materials": ["material", "finish", "texture", "surface"],
            "structure": ["structure", "structural", "support", "frame"],
            "acoustics": ["acoustic", "sound", "noise", "audio"],
            "ventilation": ["ventilation", "air", "breathing", "fresh air"],
            "shading": ["shade", "shading", "sun protection", "overhang"],
            "community spaces": ["community", "social", "gathering", "public"],
            "office design": ["office", "workplace", "work", "desk"],
            "open plan": ["open plan", "open space", "open office"],
            "private spaces": ["private", "quiet", "focus", "individual"],
            "adaptive reuse": ["adaptive reuse", "adaptive", "reuse", "renovation", "retrofit", "conversion", "repurposing"],
            "energy efficiency": ["energy", "efficient", "efficiency", "thermal", "insulation"],
            "natural ventilation": ["natural ventilation", "cross ventilation", "passive cooling"],
            "daylighting": ["daylighting", "daylight", "natural light", "sunlight"],
            "passive design": ["passive", "passive design", "passive solar"],
            "biophilic design": ["biophilic", "nature", "natural elements", "green walls"],
            "universal design": ["universal design", "inclusive design", "accessibility"],
            "modular design": ["modular", "modular design", "prefabricated", "prefab"],
            "smart building": ["smart", "intelligent", "automation", "technology"],
            "historic preservation": ["historic", "preservation", "heritage", "conservation"],
            "urban design": ["urban", "city", "street", "public space"],
            "landscape architecture": ["landscape", "garden", "outdoor", "green space"],
            "interior design": ["interior", "furniture", "furnishings", "spatial design"],
            "parametric design": ["parametric", "algorithmic", "computational", "digital fabrication"],
            "prefabrication": ["prefabrication", "prefab", "modular construction", "off-site"],
            "mass timber": ["mass timber", "cross laminated timber", "clt", "wood construction"],
            "net zero": ["net zero", "zero energy", "carbon neutral", "sustainable"],
            "green building": ["green building", "leed", "sustainable building", "eco-friendly"]
        }
        
        user_input_lower = user_input.lower()
        
        # Find the most specific topic match (prioritize longer/more specific terms first)
        # Sort topics by specificity (longer topic names first)
        sorted_topics = sorted(topic_keywords.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Check all topics for matches
        for topic, keywords in sorted_topics:
            if any(keyword in user_input_lower for keyword in keywords):
                return topic
        
        # If no specific topic found, extract from user input
        words = user_input_lower.split()
        # Look for architectural terms
        architectural_terms = ["space", "design", "building", "room", "area", "zone", "layout"]
        for word in words:
            if word in architectural_terms:
                return f"{word} design"
        
        # Default to the gap_type if nothing specific found
        return "design approach"

    async def _synthesize_examples_from_results(self, knowledge_results: List[Dict], user_topic: str, building_type: str, project_context: str) -> str:
        """Synthesize examples with titles and links; avoid truncation and ellipses; use how-phrasing."""

        bt = (building_type or "project").replace("architectural project", "project")
        header = f"Here are strong precedent examples showing how {bt} {user_topic} is handled:\n\n"
        lines: List[str] = [header]

        for i, result in enumerate(knowledge_results[:3], 1):
            meta = result.get('metadata', {})
            title = meta.get('title') or f'Example {i}'
            url = meta.get('url') or ''
            content = (result.get('content') or '').strip()
            
            # Extract full content without truncation - take first 2-3 sentences
            summary = ''
            if content:
                # Split into sentences and take first 2-3 for better context
                sentences = re.split(r'[.!?]+', content)
                valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]  # Only substantial sentences
                
                if valid_sentences:
                    if len(valid_sentences) >= 2:
                        # Take first 2 sentences for better context
                        summary = valid_sentences[0] + '. ' + valid_sentences[1] + '.'
                    else:
                        # Take first sentence if only one substantial sentence
                        summary = valid_sentences[0] + '.'
                else:
                    # Fallback: take first sentence even if short
                    summary = sentences[0].strip() + '.' if sentences else ''
            
            # Format with clickable link if available
            if url:
                lines.append(f"{i}. **{title}**\n   🔗 {url}\n   {summary}\n")
            else:
                lines.append(f"{i}. **{title}**\n   {summary}\n")

        # End with a question about the examples
        lines.append(f"Which of these examples best fits how you want to approach {user_topic} in your {bt}?")
        return "\n".join(lines)

    async def _generate_ai_examples(self, user_input: str, building_type: str, project_context: str, user_topic: str) -> Dict[str, Any]:
        """Generate AI-powered examples when search fails."""
        
        examples_text = f"Based on your request for {user_topic} examples in {building_type} architecture, here are some key projects to consider:\n\n"
        
        # Generate contextual examples based on building type and topic
        if building_type == "museum" and "circulation" in user_topic.lower():
            examples_text += "**1. Guggenheim Museum, New York** - Famous spiral circulation that creates a continuous journey through the art, eliminating the need for backtracking\n"
            examples_text += "**2. Centre Pompidou, Paris** - Innovative circulation with exposed escalators and multiple access points, making movement itself an architectural feature\n"
            examples_text += "**3. Tate Modern, London** - Adaptive reuse with clear circulation zones and flexible gallery spaces, creating intuitive visitor flow\n\n"
        elif building_type == "museum":
            examples_text += "**1. Louvre Pyramid, Paris** - Central circulation hub connecting multiple wings, creating a clear spatial hierarchy\n"
            examples_text += "**2. Museum of Modern Art, New York** - Grid-based circulation with flexible gallery arrangements, allowing multiple viewing paths\n"
            examples_text += "**3. Bilbao Guggenheim, Spain** - Organic circulation responding to urban context, with fluid transitions between spaces\n\n"
        elif building_type == "school" and "circulation" in user_topic.lower():
            examples_text += "**1. Orestad Gymnasium, Copenhagen** - Innovative circulation with learning streets and flexible movement zones\n"
            examples_text += "**2. Green School, Bali** - Natural circulation paths that integrate with the landscape and learning environment\n"
            examples_text += "**3. Ørestad College, Denmark** - Open circulation that promotes collaboration and chance encounters\n\n"
        elif building_type == "office" and "circulation" in user_topic.lower():
            examples_text += "**1. Google Campus, Mountain View** - Circulation as social space with multiple pathways and gathering areas\n"
            examples_text += "**2. Bloomberg HQ, London** - Innovative circulation with ramps and open staircases promoting interaction\n"
            examples_text += "**3. Apple Park, Cupertino** - Circular circulation that creates continuous flow and connection\n\n"
        elif building_type == "residential" and "circulation" in user_topic.lower():
            examples_text += "**1. Villa Savoye, France** - Promenade architecturale with circulation as architectural journey\n"
            examples_text += "**2. Fallingwater, Pennsylvania** - Circulation that responds to natural topography and views\n"
            examples_text += "**3. Casa da Música, Portugal** - Innovative circulation that creates spatial drama and flow\n\n"
        else:
            examples_text += "**1. High Line, New York** - Elevated circulation as public space and urban connector\n"
            examples_text += "**2. Pompidou Center, Paris** - Exposed circulation as architectural expression and urban theater\n"
            examples_text += "**3. Tate Modern, London** - Adaptive circulation for cultural programming and visitor experience\n\n"
        
        examples_text += f"These examples show how {user_topic} can enhance the user experience in {building_type} projects. "
        examples_text += f"What specific aspects would you like to explore for your {project_context}?"
        
        return {
            "response_text": examples_text,
            "response_type": "ai_generated_examples",
            "sources": [],
            "examples_provided": True
        }

    async def _generate_premature_example_response(self, user_input: str, building_type: str, project_context: str) -> Dict[str, Any]:
        """Generate response for premature example requests (cognitive offloading protection)."""
        
        response_text = f"I understand you're interested in {user_input.lower()} for your {building_type} project! "
        response_text += f"However, let's first explore the fundamental principles together. "
        response_text += f"What specific aspects of {user_input.lower()} are you most curious about? "
        response_text += f"This will help us identify the most relevant examples for your {project_context}."
        
        return {
            "response_text": response_text,
            "response_type": "premature_example_guidance",
            "sources": [],
            "examples_provided": False
        }

    def _convert_to_agent_response_internal(self, response_result: Dict[str, Any], state: ArchMentorState,
                                          context_classification: Dict, analysis_result: Dict, routing_decision: Dict) -> AgentResponse:
        """Convert response result to AgentResponse format - internal method."""

        # Ensure response_result is a dictionary
        if not isinstance(response_result, dict):
            response_result = {"response_text": str(response_result), "response_type": "fallback"}

        response_metadata = {
            "agent": self.name,
            "response_type": response_result.get("response_type", "knowledge_delivery"),
            "knowledge_gap_addressed": context_classification.get("primary_gap", "general"),
            "building_type": self._extract_building_type_from_context(state),
            "user_input_addressed": "example_request" if response_result.get("examples_provided") else "knowledge_request",
            "sources": response_result.get("sources", []),
            "processing_method": "example_detection" if response_result.get("examples_provided") else "standard_knowledge"
        }

        return ResponseBuilder.create_knowledge_response(
            response_text=response_result.get("response_text", ""),
            sources_used=response_result.get("sources", []),
            metadata=response_metadata
        )

    async def _synthesize_examples_with_llm(self, user_topic: str, knowledge_results: List[Dict], building_type: str) -> str:
        """Use the simple, working approach from the old repository - let LLM intelligently process all results."""
        
        # Extract URLs for clickable links
        urls = []
        for result in knowledge_results:
            if result.get('url'):
                urls.append({
                    'title': result.get('title', 'Source'),
                    'url': result.get('url')
                })
        
        # Combine knowledge content for LLM processing
        combined_knowledge = "\n\n---\n\n".join([
            f"Source: {r.get('title', 'Unknown')}\nContent: {r.get('content', r.get('snippet', ''))}" 
            for r in knowledge_results
        ])
        
        # Use the working prompt from the old repository
        synthesis_prompt = f"""
        The student is asking for specific examples and knowledge about {user_topic}.
        
        AVAILABLE KNOWLEDGE: {combined_knowledge}
        
        AVAILABLE URLS FOR LINKS: {urls}
        
        CRITICAL REQUIREMENT: You MUST include clickable markdown links for each example.
        
        Create a response that:
        1. Provides specific, concrete examples from the knowledge sources
        2. Includes project names, locations, and brief descriptions where available
        3. Explains the key approaches and strategies used
        4. Makes the content directly relevant to the student's specific context
        5. Varies the response style and approach based on the content available
        6. Keeps it informative and factual
        7. ALWAYS include the web links when available - they are crucial for credibility
        
        RESPONSE FORMAT REQUIREMENT:
        You MUST format each example exactly like this:
        1. **[Project Name](URL)**: Brief description of the project...
        2. **[Project Name](URL)**: Brief description of the project...
        3. **[Project Name](URL)**: Brief description of the project...
        
        CRITICAL INSTRUCTIONS:
        - You MUST format each example with clickable markdown links: [Project Name](URL)
        - Example format: "1. **[Project Name](URL)**: Brief description of the project..."
        - Keep response under 200 words to avoid cut-off
        - Focus on providing actual information, not questions
        - Make sure to vary the examples and not repeat the same projects
        - Present 2-3 specific examples with brief explanations
        - Address the student's specific question directly
        - ALWAYS use the exact URLs provided in AVAILABLE URLS FOR LINKS
        - DO NOT skip the markdown links - they are required!
        """
        
        try:
            # Use OpenAI client directly like the old repository
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=250,
                temperature=0.4
            )
            
            synthesized_text = response.choices[0].message.content.strip()
            return synthesized_text
            
        except Exception as e:
            print(f"⚠️ LLM synthesis failed: {e}")
            # Fallback to simple examples
            return self._create_simple_examples_fallback(knowledge_results, user_topic, urls)
    
    def _create_simple_examples_fallback(self, knowledge_results: List[Dict], user_topic: str, urls: List[Dict]) -> str:
        """Create simple examples when LLM fails."""
        lines = [f"Here are examples of {user_topic}:"]
        lines.append("")
        
        for i, result in enumerate(knowledge_results[:3], 1):
            title = result.get('title', f'Example {i}')
            url = result.get('url', '')
            content = result.get('content', result.get('snippet', ''))
            
            if url:
                lines.append(f"{i}. [{title}]({url})")
            else:
                lines.append(f"{i}. {title}")
            
            # Add brief description
            if content:
                snippet = content[:100] + "..." if len(content) > 100 else content
                lines.append(f"   {snippet}")
            lines.append("")
        
        lines.append("How could these approaches inform your design process?")
        return "\n".join(lines) 