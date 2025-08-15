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

            # AGENT COORDINATION: Check for other agents' responses
            coordination_context = context_classification.get("agent_coordination", {})
            other_responses = coordination_context.get("other_responses", {})

            print(f"\n📚 {self.name} providing AI-powered knowledge for: {gap_type}")
            print(f"   Building type: {building_type}")
            print(f"   User question: {user_input[:100]}...")

            if other_responses:
                print(f"🤝 Coordination: Building upon {list(other_responses.keys())} responses")
                # Extract key insights from other agents
                socratic_insights = other_responses.get("socratic_tutor", {}).get("key_insights", [])
                if socratic_insights:
                    print(f"   📝 Socratic insights to address: {socratic_insights[:2]}")  # Show first 2

            # DETECT KNOWLEDGE REQUEST PATTERNS
            print(f"🔍 Analyzing knowledge request: '{user_input[:50]}...'")
            knowledge_pattern = self._analyze_knowledge_request(user_input, gap_type, state)
            print(f"🎯 Knowledge pattern detected: {knowledge_pattern['type']}")

            # Handle balanced guidance requests (provide specific strategies)
            routing_path = routing_decision.get("path", "")
            if routing_path == "balanced_guidance":
                print(f"⚖️ Balanced guidance request detected - providing specific strategies")
                response_result = await self._generate_balanced_guidance_strategies(
                    user_input, building_type, project_context, gap_type, state
                )
                return self._convert_to_agent_response_internal(response_result, state, context_classification, analysis_result, routing_decision)

            # Handle feedback/guidance requests (should get AI analysis, not examples)
            if knowledge_pattern["type"] == "feedback_guidance_request":
                print(f"💬 Feedback/guidance request detected - providing AI analysis")
                response_result = await self._generate_contextual_knowledge_response(
                    user_input, building_type, project_context, gap_type, state
                )
                return self._convert_to_agent_response_internal(response_result, state, context_classification, analysis_result, routing_decision)

            # Handle legitimate example requests properly (both project and general examples use same method)
            if knowledge_pattern["type"] in ["legitimate_project_example_request", "legitimate_general_example_request"]:
                if "project" in knowledge_pattern["type"]:
                    print(f"🏗️ Legitimate PROJECT example request detected - providing specific built projects")
                else:
                    print(f"📚 Legitimate GENERAL example request detected - providing examples/strategies")
                response_result = await self._provide_focused_examples(state, user_input, gap_type)
                return self._convert_to_agent_response_internal(response_result, state, context_classification, analysis_result, routing_decision)

            # Handle premature example requests (cognitive offloading protection)
            if knowledge_pattern["type"] in ["premature_project_example_request", "premature_general_example_request"]:
                print(f"🛡️ Cognitive protection: Example request too early")
                response_result = await self._generate_premature_example_response(user_input, building_type, project_context)
                return self._convert_to_agent_response_internal(response_result, state, context_classification, analysis_result, routing_decision)

            # KNOWLEDGE REQUESTS: Database first, then AI generation as fallback
            print(f"🔍 KNOWLEDGE REQUEST: Checking database first for: {user_input[:50]}...")

            # Step 1: Try database search first
            knowledge_results = []
            user_topic = self._extract_topic_from_user_input(user_input)

            try:
                from knowledge_base.knowledge_manager import KnowledgeManager
                km = KnowledgeManager(domain="architecture")

                # Create knowledge-focused search query
                db_query = f"{user_topic} {building_type} architecture principles guidelines requirements"
                print(f"   🗄️  DB search query: {db_query}")

                db_results = km.search_knowledge(db_query, n_results=5)
                if db_results:
                    knowledge_results.extend(db_results)
                    print(f"   ✅ Found {len(db_results)} database results")
                else:
                    print(f"   ❌ No database results found")

            except Exception as e:
                print(f"   ⚠️ Database search failed: {e}")

            # Step 2: If database has sufficient results, synthesize them
            if len(knowledge_results) >= 2:
                print(f"   📚 Using database knowledge for synthesis")
                knowledge_text = await self._synthesize_knowledge_with_llm(
                    user_topic, knowledge_results, building_type, synthesis_type="knowledge"
                )

                response_metadata = {
                    "agent": self.name,
                    "response_type": "database_knowledge",
                    "knowledge_gap_addressed": gap_type,
                    "building_type": building_type,
                    "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                    "sources": knowledge_results,
                    "processing_method": "database_synthesis"
                }

                agent_response = ResponseBuilder.create_knowledge_response(
                    response_text=knowledge_text,
                    sources_used=knowledge_results,
                    metadata=response_metadata
                )

            else:
                # Step 3: Fallback to AI generation if database insufficient
                print(f"   🤖 Database insufficient - using AI generation as fallback")
                ai_response = await self._generate_contextual_knowledge_response(
                    user_input, building_type, project_context, gap_type, state
                )

                response_metadata = {
                    "agent": self.name,
                    "response_type": "ai_generated_knowledge",
                    "knowledge_gap_addressed": gap_type,
                    "building_type": building_type,
                    "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                    "sources": knowledge_results,  # Include any partial results
                    "processing_method": "ai_fallback"
                }

                agent_response = ResponseBuilder.create_knowledge_response(
                    response_text=ai_response,
                    sources_used=knowledge_results,
                    metadata=response_metadata
            )

            # Add cognitive flags manually - check if response contains questions
            response_text = getattr(agent_response, 'response_text', '') or ''
            agent_response.cognitive_flags = [CognitiveFlag.ENCOURAGES_THINKING] if "?" in response_text else []

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
        - PRIORITY 1: Use conversation_context.detected_building_type if available (highest confidence)
        - PRIORITY 2: Use state.building_type if available
        - PRIORITY 3: Prefer analysis_result.text_analysis.building_type if set and not 'unknown'.
        - Establish a base_type from the initial brief + first user message.
        - Mentions in later messages do NOT change the type unless an explicit switch phrase is detected.
        - Avoid inferring 'museum' from generic words like 'exhibition' or 'cultural center'.
        """

        # PRIORITY 1: Use conversation continuity context (highest confidence)
        if hasattr(state, 'conversation_context') and state.conversation_context.detected_building_type:
            if state.conversation_context.building_type_confidence > 0.7:
                print(f"🏗️ Using stored building type: {state.conversation_context.detected_building_type} (confidence: {state.conversation_context.building_type_confidence:.2f})")
                return state.conversation_context.detected_building_type

        # PRIORITY 2: Use state.building_type if available and not unknown
        if hasattr(state, 'building_type') and state.building_type and state.building_type != "unknown":
            print(f"🏗️ Using state building type: {state.building_type}")
            return state.building_type

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
        
        # ENHANCED: Better detection of legitimate example requests (exclude feedback requests)
        # First check if this is a feedback/evaluation request (should NOT get examples)
        feedback_patterns = [
            "feedback", "evaluate", "assessment", "review", "critique", "thoughts on", "opinion on",
            "what do you think", "give me feedback", "provide feedback", "can you evaluate"
        ]

        is_feedback_request = any(pattern in user_input_lower for pattern in feedback_patterns)

        if is_feedback_request:
            # This is a feedback request - should get AI guidance, not examples
            analysis["type"] = "feedback_guidance_request"
            analysis["cognitive_risk"] = "low"
            analysis["indicators"].append("Feedback/guidance request - should provide AI analysis")
            return analysis

        # DISTINGUISH between PROJECT EXAMPLES and GENERAL EXAMPLES

        # PROJECT EXAMPLES: Specific built projects with names, locations, architects
        project_example_keywords = [
            "example projects", "project examples", "examples of projects",
            "precedent", "precedents", "case study", "case studies",
            "similar projects", "real project", "built project", "built projects",
            "actual projects", "specific projects", "project references"
        ]

        # GENERAL EXAMPLES: Strategies, approaches, concepts, methods
        general_example_keywords = [
            "show me examples", "give me examples", "provide examples", "need examples",
            "examples of", "example of", "for example", "such as",
            "inspiration", "references", "approaches", "strategies"
        ]

        # Check what type of example request this is
        is_project_example_request = any(keyword in user_input_lower for keyword in project_example_keywords)
        is_general_example_request = any(keyword in user_input_lower for keyword in general_example_keywords)

        print(f"🔍 Project example request: {is_project_example_request} (keywords: {[k for k in project_example_keywords if k in user_input_lower]})")
        print(f"🔍 General example request: {is_general_example_request} (keywords: {[k for k in general_example_keywords if k in user_input_lower]})")

        if is_project_example_request:
            # Check cognitive offloading protection (minimum 5 messages required)
            if state and hasattr(state, 'messages'):
                message_count = len([msg for msg in state.messages if msg.get('role') == 'user'])
                if message_count < 5:
                    analysis["type"] = "premature_project_example_request"
                    analysis["cognitive_risk"] = "high"
                    analysis["indicators"].append(f"Project example request too early (only {message_count} messages, need 5+)")
                    analysis["cognitive_protection"] = "active"
                    return analysis

            # This is a legitimate PROJECT example request - should provide specific built projects
            analysis["type"] = "legitimate_project_example_request"
            analysis["cognitive_risk"] = "low"
            analysis["indicators"].append("Legitimate PROJECT example request detected - will provide specific built projects")
            return analysis

        elif is_general_example_request:
            # Check cognitive offloading protection (minimum 3 messages for general examples)
            if state and hasattr(state, 'messages'):
                message_count = len([msg for msg in state.messages if msg.get('role') == 'user'])
                if message_count < 3:
                    analysis["type"] = "premature_general_example_request"
                    analysis["cognitive_risk"] = "high"
                    analysis["indicators"].append(f"General example request too early (only {message_count} messages, need 3+)")
                    analysis["cognitive_protection"] = "active"
                    return analysis

            # This is a legitimate GENERAL example request - should provide strategies/approaches
            analysis["type"] = "legitimate_general_example_request"
            analysis["cognitive_risk"] = "low"
            analysis["indicators"].append("Legitimate GENERAL example request detected - will provide strategies/approaches")
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
        """
        Provide focused examples with different strategies based on request type:
        - "examples" (general) → Database first, then AI generation if no relevant info
        - "example projects" (specific) → Database first, then web search if no relevant info (NO AI generation)
        """
        print(f"🔄 Providing focused examples for: {user_input}")

        # Extract building type and topic
        building_type = self._extract_building_type_from_context(state)
        user_topic = self._extract_topic_from_user_input(user_input)
        project_context = getattr(state, 'current_design_brief', '') or ''

        print(f"   🏗️  Building type: {building_type}")
        print(f"   🎯 Topic: {user_topic}")
        print(f"   📋 Context: {project_context}")

        # Determine if this is a PROJECT example request or GENERAL example request
        user_input_lower = user_input.lower()
        project_example_keywords = [
            "example projects", "project examples", "examples of projects",
            "precedent", "precedents", "case study", "case studies",
            "similar projects", "real project", "built project", "built projects",
            "actual projects", "specific projects", "project references"
        ]

        is_project_example_request = any(keyword in user_input_lower for keyword in project_example_keywords)
        request_type = "project_examples" if is_project_example_request else "general_examples"

        print(f"   📋 Request type: {request_type}")

        # Search examples: local DB first, then different fallback strategies
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
                    # Preserve similarity/distance information for relevance checking
                    distance = r.get("distance", 1.0)
                    similarity = 1.0 - distance  # Convert distance to similarity

                    knowledge_results.append({
                        "title": r.get("metadata", {}).get("title", "Untitled"),
                        "url": r.get("metadata", {}).get("source_url", ""),
                        "snippet": r.get("content", "")[:200] + "..." if len(r.get("content", "")) > 200 else r.get("content", ""),
                        "content": r.get("content", ""),
                        "source": "local_db",
                        "similarity": similarity,
                        "distance": distance
                    })
                    
                print(f"   ✅ Found {len(knowledge_results)} database results")
                
            except Exception as e:
                print(f"⚠️ Local DB search unavailable: {e}")

            # IMPLEMENT DIFFERENT FALLBACK STRATEGIES BASED ON REQUEST TYPE
            # Check both quantity AND quality of database results
            has_sufficient_db_results = len(knowledge_results) >= 3
            has_relevant_db_results = False

            if knowledge_results:
                # Check if database results are relevant by looking at similarity scores
                avg_similarity = sum(r.get('similarity', 0) for r in knowledge_results) / len(knowledge_results)
                has_relevant_db_results = avg_similarity > 0.3  # Threshold for relevance
                print(f"   📊 Database relevance check: {avg_similarity:.3f} (threshold: 0.3)")

            if not has_sufficient_db_results or not has_relevant_db_results:
                if request_type == "project_examples":
                    # PROJECT EXAMPLES: Database → Web search (NO AI generation)
                    print(f"   🏗️ PROJECT EXAMPLES: Trying web search for specific built projects")
                    try:
                        # Create web search query focused on specific projects
                        context_query = f"{user_topic} {building_type} architecture case study precedent project built examples"
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

                else:
                    # GENERAL EXAMPLES: Database → AI generation (NO web search)
                    print(f"   📚 GENERAL EXAMPLES: Using AI generation for strategies/approaches")
                    # For general examples, we'll use AI generation as fallback
                    # This will be handled in the final synthesis section

            # SYNTHESIS LOGIC: Different strategies based on request type and available data
            if knowledge_results:
                # We have database or web search results - synthesize them
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
                # NO RESULTS FOUND - Apply different fallback strategies
                if request_type == "project_examples":
                    # PROJECT EXAMPLES: No AI generation - just inform user
                    return {
                        "response_text": f"I wasn't able to find specific built project examples for {user_topic} in {building_type} architecture in my current database or web search. This could be because it's a specialized area or the search terms need refinement. Could you provide more specific details about what type of {user_topic} examples you're looking for, or try a different search approach?",
                        "response_type": "no_project_examples_found",
                        "sources": [],
                        "examples_provided": False
                    }
                else:
                    # GENERAL EXAMPLES: Use AI generation as fallback
                    print(f"   🤖 No database/web results found - generating AI examples for general strategies")
                    ai_examples = await self._generate_ai_examples_for_general_strategies(
                        user_input, user_topic, building_type, project_context
                    )

                    return {
                        "response_text": ai_examples,
                        "response_type": "ai_generated_examples",
                        "sources": [],
                        "examples_provided": True,
                        "generation_method": "ai_fallback"
                    }
                
        except Exception as e:
            print(f"⚠️ Example search failed: {e}")
            return {
                "response_text": f"I encountered an issue while searching for examples of {user_topic} in {building_type} architecture. This could be due to technical limitations or the specific nature of your question. Would you like to rephrase your question or focus on a different aspect of {user_topic}?",
                "response_type": "search_error",
                "sources": [],
                "examples_provided": False
            }

    async def _generate_ai_examples_for_general_strategies(self, user_input: str, topic: str, building_type: str, project_context: str) -> str:
        """
        Generate AI-powered examples for general strategies/approaches when no database/web results are found.
        This is only used for GENERAL example requests, not PROJECT example requests.
        """
        try:
            prompt = f"""
            As an expert architecture educator, provide helpful examples and strategies for: {topic}

            Context:
            - Building type: {building_type}
            - User question: {user_input}
            - Project context: {project_context}

            Since this is a request for general examples/strategies (not specific built projects), provide:
            1. Key approaches and strategies for {topic}
            2. General principles and considerations
            3. Common methods and techniques
            4. Conceptual examples and scenarios

            Focus on educational value and practical guidance rather than specific project names.
            Keep the response informative but concise (2-3 paragraphs).
            """

            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert architecture educator providing helpful examples and strategies."),
                self.client.create_user_message(prompt)
            ])

            return response.strip()

        except Exception as e:
            print(f"⚠️ AI example generation failed: {e}")
            return f"I'd be happy to help you explore {topic} in {building_type} architecture. This is an interesting area that involves various approaches and strategies. Could you tell me more specifically what aspect of {topic} you'd like to understand better?"

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
            "social spaces": ["social interaction", "gathering spaces", "public areas"],
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
        """Generate AI-powered examples using LLM for contextual, relevant responses."""

        try:
            # Get conversation context to understand references
            conversation_history = self._get_conversation_context_for_examples(user_input, building_type, project_context)

            # Create a comprehensive prompt for generating contextual examples
            prompt = f"""
            You are an expert architectural educator providing specific, relevant project examples.

            USER REQUEST: "{user_input}"
            BUILDING TYPE: {building_type}
            TOPIC: {user_topic}
            PROJECT CONTEXT: {project_context}
            CONVERSATION CONTEXT: {conversation_history}

            Generate 3 specific, real architectural project examples that directly address the user's request.

            REQUIREMENTS:
            1. Focus specifically on {building_type} projects or similar building types
            2. Each example should demonstrate {user_topic} effectively
            3. Include project name, location, and architect when possible
            4. Explain WHY each example is relevant to their request
            5. For community centers, focus on projects that serve diverse user groups
            6. For elder people/senior centers, prioritize accessibility and age-friendly design
            7. For adaptive reuse, show how existing buildings were transformed
            8. Avoid generic famous buildings unless they're directly relevant

            FORMAT:
            **1. [Project Name, Location]** - [Brief description of how it addresses the topic]
            **2. [Project Name, Location]** - [Brief description of how it addresses the topic]
            **3. [Project Name, Location]** - [Brief description of how it addresses the topic]

            End with: "Which of these approaches resonates most with your {building_type} project vision?"
            """

            response = await self.client.generate_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=400, temperature=0.6)

            if response and response.get("content"):
                ai_examples = response["content"].strip()

                return {
                    "response_text": ai_examples,
                    "response_type": "ai_generated_examples",
                    "sources": ["AI Generated Examples"],
                    "examples_provided": True
                }

        except Exception as e:
            print(f"⚠️ AI example generation failed: {e}")

        # Fallback to a more generic but still contextual response
        return {
            "response_text": f"I'd be happy to help you explore {user_topic} examples for your {building_type} project. To provide the most relevant examples, could you tell me what specific aspect of {user_topic} you're most interested in understanding?",
            "response_type": "fallback_examples",
            "sources": [],
            "examples_provided": False
        }

    def _get_conversation_context_for_examples(self, user_input: str, building_type: str, project_context: str) -> str:
        """Get conversation context to better understand example requests."""
        try:
            # This would ideally get the conversation state, but for now we'll extract from available context
            context_details = []

            # Check for specific project details in the current context
            if 'warehouse' in project_context.lower() or 'warehouse' in user_input.lower():
                context_details.append("adaptive reuse of warehouse building")
            if 'community center' in project_context.lower() or 'community center' in user_input.lower():
                context_details.append("community center program")
            if 'elder' in project_context.lower() or 'elder' in user_input.lower():
                context_details.append("serving elder/senior population")
            if 'adaptive reuse' in project_context.lower() or 'adaptive reuse' in user_input.lower():
                context_details.append("adaptive reuse project")

            return '; '.join(context_details) if context_details else "general architectural project"

        except Exception as e:
            print(f"⚠️ Error getting conversation context: {e}")
            return "architectural project"

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

    async def _synthesize_knowledge_with_llm(self, user_topic: str, knowledge_results: List[Dict], building_type: str, synthesis_type: str = "examples") -> str:
        """Synthesize knowledge from database results - can handle both examples and general knowledge."""

        if synthesis_type == "examples":
            return await self._synthesize_examples_with_llm(user_topic, knowledge_results, building_type)
        else:
            # Handle general knowledge synthesis
            return await self._synthesize_general_knowledge_with_llm(user_topic, knowledge_results, building_type)

    async def _synthesize_general_knowledge_with_llm(self, user_topic: str, knowledge_results: List[Dict], building_type: str) -> str:
        """Synthesize general knowledge from database results."""

        try:
            # Prepare knowledge content for synthesis
            knowledge_content = []
            for result in knowledge_results:
                content = result.get('content', '') or result.get('snippet', '') or result.get('text', '')
                title = result.get('title', 'Knowledge Source')
                if content:
                    knowledge_content.append(f"**{title}**: {content[:300]}...")

            if not knowledge_content:
                # Fallback if no content found
                return f"I'd be happy to help you understand {user_topic} in {building_type} architecture. This involves several key considerations and principles. Could you tell me more specifically what aspect you'd like to explore?"

            # Create synthesis prompt
            prompt = f"""
            Based on the following knowledge sources about {user_topic} in {building_type} architecture, provide a comprehensive and educational response:

            Knowledge Sources:
            {chr(10).join(knowledge_content)}

            Please synthesize this information to:
            1. Explain the key concepts and principles
            2. Provide practical guidance and considerations
            3. Make it relevant to {building_type} projects
            4. Keep it educational and informative

            Focus on understanding rather than just listing information.
            """

            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert architecture educator synthesizing knowledge from reliable sources."),
                self.client.create_user_message(prompt)
            ])

            # FIXED: Extract content from response dictionary
            if response and response.get("content"):
                return response["content"].strip()
            else:
                return f"Based on architectural principles, {user_topic} in {building_type} design involves careful consideration of user needs, functional requirements, and design standards. What specific aspect would you like to explore further?"

        except Exception as e:
            print(f"⚠️ Knowledge synthesis failed: {e}")
            return f"Based on architectural principles, {user_topic} in {building_type} design involves careful consideration of user needs, functional requirements, and design standards. What specific aspect would you like to explore further?"

    async def _synthesize_examples_with_llm(self, user_topic: str, knowledge_results: List[Dict], building_type: str) -> str:
        """Use the simple, working approach from the old repository - let LLM intelligently process all results."""
        
        # Extract URLs for clickable links (check both direct and metadata fields)
        urls = []
        for result in knowledge_results:
            # Try multiple ways to get URL and title
            url = result.get('url') or result.get('metadata', {}).get('url', '')
            title = result.get('title') or result.get('metadata', {}).get('title', 'Source')

            if url:
                urls.append({
                    'title': title,
                    'url': url
                })
                print(f"🔗 Found URL: {title} -> {url}")
        
        # Combine knowledge content for LLM processing
        combined_knowledge = "\n\n---\n\n".join([
            f"Source: {r.get('title', 'Unknown')}\nContent: {r.get('content', r.get('snippet', ''))}"
            for r in knowledge_results
        ])

        # DEBUG: Print what content is being passed to synthesis
        print(f"🔍 DEBUG: Synthesizing {len(knowledge_results)} results")
        for i, r in enumerate(knowledge_results[:3]):
            title = r.get('title', 'Unknown')[:50]
            content = r.get('content', r.get('snippet', ''))[:100]
            print(f"   📄 Result {i+1}: {title} | Content: {content}...")
        print(f"🔍 DEBUG: Combined knowledge length: {len(combined_knowledge)} chars")
        print(f"🔍 DEBUG: User topic: {user_topic}")
        print(f"🔍 DEBUG: Building type: {building_type}")
        
        # Use the working prompt from the old repository
        synthesis_prompt = f"""
        The student is asking for SPECIFIC PROJECT EXAMPLES about {user_topic}.

        AVAILABLE KNOWLEDGE: {combined_knowledge}

        AVAILABLE URLS FOR LINKS: {urls}

        CRITICAL REQUIREMENT: You MUST provide ACTUAL PROJECT EXAMPLES, not general strategies or theories.

        IMPORTANT: You MUST base your examples on the AVAILABLE KNOWLEDGE provided above. Do NOT make up examples that are not mentioned in the knowledge sources.

        DO NOT PROVIDE:
        - General strategies like "Historical Preservation and Integration"
        - Theoretical approaches like "Flexible Interior Reconfiguration"
        - Abstract concepts or principles

        DO PROVIDE:
        - Specific building names (e.g., "Tate Modern", "High Line", "Gasometer City")
        - Actual locations (e.g., "London", "New York", "Vienna")
        - Real architects/firms (e.g., "Herzog & de Meuron", "James Corner Field Operations")
        - Concrete project details and what makes each project notable

        RESPONSE FORMAT REQUIREMENT:
        You MUST format each example exactly like this:
        1. **[Actual Project Name](URL)**: Brief description of the actual project, location, architect, and key features...
        2. **[Actual Project Name](URL)**: Brief description of the actual project, location, architect, and key features...
        3. **[Actual Project Name](URL)**: Brief description of the actual project, location, architect, and key features...

        CRITICAL INSTRUCTIONS:
        - You MUST provide REAL PROJECT NAMES, not strategy names
        - You MUST format each example with clickable markdown links: [Project Name](URL)
        - Keep response under 200 words to avoid cut-off
        - Focus on actual built projects, not theoretical concepts
        - Present 2-3 specific project examples with brief explanations
        - Include architect names and locations when available
        - ALWAYS use the exact URLs provided in AVAILABLE URLS FOR LINKS
        - DO NOT create your own URLs - only use the URLs I provided above
        - DO NOT use generic category URLs like "archdaily.com/category/community-center"
        - If no specific URLs are available, use **Project Name** (bold text without links) instead of fake URLs
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

            # Fix generic/fake URLs by replacing them with placeholder links
            import re
            # Replace generic ArchDaily category URLs with placeholder links
            synthesized_text = re.sub(
                r'\[([^\]]+)\]\(https://www\.archdaily\.com/category/[^)]+\)',
                r'[\1](#)',
                synthesized_text
            )
            # Replace other generic/fake URLs with placeholder links
            synthesized_text = re.sub(
                r'\[([^\]]+)\]\(https://www\.archdaily\.com/search/[^)]+\)',
                r'[\1](#)',
                synthesized_text
            )

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

    async def _generate_balanced_guidance_strategies(self, user_input: str, building_type: str, project_context: str, gap_type: str, state: ArchMentorState) -> Dict[str, Any]:
        """Generate specific strategies for balanced guidance responses."""
        print(f"⚖️ Generating balanced guidance strategies for: {user_input}")

        # Extract topic from user input
        user_topic = self._extract_topic_from_user_input(user_input)

        try:
            # Generate specific strategies using LLM
            strategies_prompt = f"""
            The student is working on a {building_type} project and asking about: "{user_input}"

            Project context: {project_context}
            Topic: {user_topic}

            Provide 2-3 SPECIFIC STRATEGIES that directly address their question about {user_topic} for {building_type} design.

            Format each strategy as:
            1. **Strategy Name**: Clear description of the approach and how it applies to their {building_type} project.
            2. **Strategy Name**: Clear description of the approach and how it applies to their {building_type} project.

            Requirements:
            - Make strategies specific to {building_type} projects
            - Address their specific question about {user_topic}
            - Provide actionable, practical guidance
            - Keep each strategy concise but informative
            - Focus on design approaches, not generic advice

            Do NOT include questions or follow-ups - just provide the strategies.
            """

            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": strategies_prompt}],
                max_tokens=300,
                temperature=0.7
            )

            strategies_text = response.choices[0].message.content.strip()

            return {
                "response_text": strategies_text,
                "response_type": "balanced_guidance_strategies",
                "sources": [],
                "strategies_provided": True,
                "building_type": building_type,
                "topic": user_topic
            }

        except Exception as e:
            print(f"⚠️ Balanced guidance strategies generation failed: {e}")
            # Fallback to generic but helpful strategies
            return {
                "response_text": f"""Here are key strategies to consider for {user_topic} in your {building_type} project:

1. **Contextual Integration**: Consider how your approach to {user_topic} can respond to the specific site conditions and community needs of your {building_type}.

2. **Flexible Implementation**: Design solutions that can adapt over time, allowing your {building_type} to evolve with changing community requirements.

3. **User-Centered Approach**: Focus on how different user groups will experience and interact with the {user_topic} aspects of your {building_type} design.""",
                "response_type": "balanced_guidance_strategies_fallback",
                "sources": [],
                "strategies_provided": True,
                "building_type": building_type,
                "topic": user_topic
            }

