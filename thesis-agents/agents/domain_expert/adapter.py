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
            user_topic = await self._extract_topic_from_user_input(user_input)

            try:
                from knowledge_base.knowledge_manager import KnowledgeManager
                km = KnowledgeManager(domain="architecture")

                # Create flexible, context-aware search query
                building_type_clean = building_type.replace('_', ' ')

                # Use flexible query construction
                db_query = self._create_flexible_db_query(user_topic, building_type_clean)

                print(f"   🗄️  Flexible DB search query: {db_query}")

                db_results = km.search_knowledge(db_query, n_results=5)
                if db_results:
                    knowledge_results.extend(db_results)
                    print(f"   ✅ Found {len(db_results)} database results")
                else:
                    print(f"   ❌ No database results found")

            except Exception as e:
                print(f"   ⚠️ Database search failed: {e}")

            # Step 2: Check if database results are actually relevant before using them
            if len(knowledge_results) >= 2:
                # Check relevance of database results
                relevant_results = self._filter_relevant_results(knowledge_results, user_topic, user_input, building_type)

                if len(relevant_results) >= 2:
                    print(f"   📚 Using {len(relevant_results)} relevant database results for synthesis")
                    knowledge_text = await self._synthesize_knowledge_with_llm(
                        user_topic, relevant_results, building_type, synthesis_type="knowledge"
                    )

                    response_metadata = {
                        "agent": self.name,
                        "response_type": "database_knowledge",
                        "knowledge_gap_addressed": gap_type,
                        "building_type": building_type,
                        "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                        "sources": relevant_results,
                        "processing_method": "database_synthesis"
                    }

                    agent_response = ResponseBuilder.create_knowledge_response(
                        response_text=knowledge_text,
                        sources_used=relevant_results,
                        metadata=response_metadata
                    )
                else:
                    print(f"   ⚠️ Database results not sufficiently relevant to {user_topic} - using AI generation")
                    # Fall through to AI generation
                    agent_response = None

            else:
                # Not enough database results - fall through to AI generation
                agent_response = None

            # Step 3: Try web search for project examples if database was insufficient
            if agent_response is None and ("example projects" in user_input.lower() or "project examples" in user_input.lower()):
                print(f"   🌐 Database insufficient for project examples - trying web search")
                try:
                    # Use existing knowledge search processor for web search
                    from .processors.knowledge_search import KnowledgeSearchProcessor
                    knowledge_search = KnowledgeSearchProcessor()

                    # Create web search query for project examples
                    search_topic = f"{building_type} adaptive reuse projects examples"
                    print(f"   🔍 Web search topic: {search_topic}")

                    web_results = await knowledge_search.search_web_for_knowledge(search_topic, state)

                    if web_results and len(web_results) > 0:
                        print(f"   ✅ Found {len(web_results)} web search results")

                        # Synthesize web results into response
                        web_response = await self._synthesize_knowledge_with_llm(
                            search_topic, web_results, building_type, synthesis_type="project_examples"
                        )

                        response_metadata = {
                            "agent": self.name,
                            "response_type": "web_search_knowledge",
                            "knowledge_gap_addressed": gap_type,
                            "building_type": building_type,
                            "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                            "sources": web_results,
                            "processing_method": "web_search"
                        }

                        # Convert web results to source format
                        web_sources = [result.get('metadata', {}).get('url', 'Web Search') for result in web_results]

                        agent_response = ResponseBuilder.create_knowledge_response(
                            response_text=web_response,
                            sources_used=web_sources,
                            metadata=response_metadata
                        )
                    else:
                        print(f"   ⚠️ Web search also returned no results")
                        agent_response = None

                except Exception as e:
                    print(f"   ⚠️ Web search failed: {e}")
                    agent_response = None

            # Step 4: Use AI generation as final fallback
            if agent_response is None:
                print(f"   🤖 Database and web search insufficient - using AI generation as final fallback")
                ai_response = await self._generate_contextual_knowledge_response(
                    user_input, building_type, project_context, gap_type, state
                )

                response_metadata = {
                    "agent": self.name,
                    "response_type": "ai_generated_knowledge",
                    "knowledge_gap_addressed": gap_type,
                    "building_type": building_type,
                    "user_input_addressed": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                    "sources": [],  # No relevant database sources
                    "processing_method": "ai_fallback"
                }

                agent_response = ResponseBuilder.create_knowledge_response(
                    response_text=ai_response,
                    sources_used=[],
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

            # FIXED: Create more integrated knowledge-challenge response
            prompt = f"""
            Address the user's specific question with contextual knowledge that flows seamlessly into practical application.

            User's question: "{user_input}"
            Building type: {building_type}
            Project context: {project_context}

            Structure your response as ONE COHESIVE FLOW:
            1. Start by directly addressing their specific question
            2. Provide relevant knowledge that connects to their project context
            3. Seamlessly transition into practical considerations for their {building_type}
            4. End with thought-provoking questions that encourage deeper exploration

            AVOID: Generic introductions or separate "knowledge section" + "challenge section"
            FOCUS: Make it feel like a natural conversation that builds from their question
            Keep it engaging but maintain professional architectural depth.
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
        """Create knowledge request with enhanced context."""
        # Extract user's actual question from conversation
        user_question = topic
        project_context = ""

        if state and hasattr(state, 'messages') and state.messages:
            # Get the latest user message
            for msg in reversed(state.messages):
                if msg.get('role') == 'user':
                    user_question = msg.get('content', topic)
                    break

            # Extract project context from conversation history
            project_mentions = []
            for msg in state.messages[-5:]:  # Look at last 5 messages
                if msg.get('role') == 'user':
                    content = msg.get('content', '').lower()
                    # Look for project-specific mentions
                    if any(keyword in content for keyword in ['warehouse', 'copenhagen', 'skylight', 'garden', 'transform', 'existing']):
                        project_mentions.append(msg.get('content', ''))

            if project_mentions:
                project_context = " ".join(project_mentions[-2:])  # Last 2 relevant mentions

        return {
            'topic': topic,
            'context': context,
            'user_question': user_question,
            'project_context': project_context,
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

        # Check if visual analysis is available
        visual_context = ""
        visual_insights = state.agent_context.get('visual_insights', {})
        if visual_insights.get('has_visual_analysis'):
            strengths = visual_insights.get('design_strengths', [])
            improvements = visual_insights.get('improvement_opportunities', [])
            elements = visual_insights.get('identified_elements', [])

            visual_context = f"""
        VISUAL ANALYSIS AVAILABLE:
        - Design strengths noted: {', '.join(strengths[:3]) if strengths else 'None'}
        - Areas for improvement: {', '.join(improvements[:3]) if improvements else 'None'}
        - Elements identified: {', '.join(elements[:4]) if elements else 'None'}

        IMPORTANT: Reference and build upon these visual observations in your response. The student has shared visual material that should inform your guidance.
        """

        prompt = f"""
        You are a distinguished architectural scholar and mentor with expertise in design theory, building science, and critical practice. Your role is to provide academically rigorous knowledge that stimulates intellectual inquiry rather than passive consumption.

        STUDENT INQUIRY: "{user_input}"
        BUILDING TYPOLOGY: {building_type}
        PROJECT CONTEXT: {project_context}
        KNOWLEDGE DOMAIN: {gap_type}
        {visual_context}

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

        # PERFORMANCE: Check cache first
        import streamlit as st
        cache_key = f"domain_expert_{hash(prompt[:100])}_{building_type}"
        if hasattr(st.session_state, cache_key):
            print(f"📚 CACHE_HIT: Using cached domain expert response")
            return getattr(st.session_state, cache_key)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # PERFORMANCE: Use cheaper model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,  # INCREASED: Fix contextual response truncation
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

            # PERFORMANCE: Cache the response
            setattr(st.session_state, cache_key, ai_response)
            print(f"📚 CACHE_STORE: Cached domain expert response")

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

        # Check if visual analysis is available for fallback too
        visual_context = ""
        visual_insights = state.agent_context.get('visual_insights', {})
        if visual_insights.get('has_visual_analysis'):
            strengths = visual_insights.get('design_strengths', [])
            improvements = visual_insights.get('improvement_opportunities', [])
            elements = visual_insights.get('identified_elements', [])

            visual_context = f"""
        VISUAL ANALYSIS AVAILABLE:
        - Design strengths: {', '.join(strengths[:2]) if strengths else 'None'}
        - Improvement areas: {', '.join(improvements[:2]) if improvements else 'None'}
        - Elements seen: {', '.join(elements[:3]) if elements else 'None'}

        Reference these visual observations in your response.
        """

        prompt = f"""
        You are an architectural domain expert. Your main LLM generation failed, so you need to provide a helpful fallback response.

        STUDENT'S QUESTION: "{user_input}"
        BUILDING TYPE: {building_type}
        PROJECT CONTEXT: {project_context}
        KNOWLEDGE DOMAIN: {gap_type}
        {visual_context}

        Provide a helpful response that:
        1. Acknowledges their specific question about {gap_type}
        2. Offers 2-3 concrete principles or approaches they can consider
        3. Relates specifically to their {building_type} project
        4. References any visual elements they've shared (if visual analysis is available)
        5. Ends with a thoughtful question that builds on the guidance provided
        6. Avoids saying you "don't have information" - instead provide what you can

        Keep it educational and specific to their situation (150-200 words).
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,  # INCREASED: Fix fallback response truncation
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
            "specific example project", "specific example projects", "example project",
            "precedent", "precedents", "case study", "case studies",
            "similar projects", "real project", "built project", "built projects",
            "actual projects", "specific projects", "project references",
            "show me specific", "specific.*projects", "examples of.*projects",
            "real examples", "built examples", "actual examples",
            "give me a specific example", "give me specific example"
        ]

        # GENERAL EXAMPLES: Strategies, approaches, concepts, methods (FLEXIBLE MATCHING)
        general_example_keywords = [
            "show me examples", "give me examples", "give some examples", "provide examples", "need examples",
            "can you give examples", "can you show examples", "can you provide examples",
            "examples of", "example of", "for example", "such as",
            "inspiration", "references", "approaches", "strategies", "for inspiration"
        ]

        # Check for negative context (user explicitly saying they DON'T want examples)
        negative_patterns = ["don't want", "dont want", "not want", "no examples", "no projects", "not examples", "not projects"]
        has_negative_context = any(pattern in user_input_lower for pattern in negative_patterns)

        # Check what type of example request this is (only if no negative context)
        if has_negative_context:
            is_project_example_request = False
            is_general_example_request = False
            print(f"🚫 Negative context detected - user explicitly doesn't want examples")
        else:
            is_project_example_request = any(keyword in user_input_lower for keyword in project_example_keywords)
            is_general_example_request = any(keyword in user_input_lower for keyword in general_example_keywords)

            # ADDITIONAL FLEXIBLE MATCHING for common patterns
            if not is_general_example_request:
                # Check for flexible patterns like "give [some/any] examples"
                import re
                flexible_patterns = [
                    r"give\s+(some|any|me)?\s*examples",
                    r"show\s+(some|any|me)?\s*examples",
                    r"provide\s+(some|any|me)?\s*examples",
                    r"can you give.*examples",
                    r"examples.*for inspiration"
                ]
                is_general_example_request = any(re.search(pattern, user_input_lower) for pattern in flexible_patterns)

        print(f"🔍 Project example request: {is_project_example_request} (keywords: {[k for k in project_example_keywords if k in user_input_lower]})")
        print(f"🔍 General example request: {is_general_example_request} (keywords: {[k for k in general_example_keywords if k in user_input_lower]})")

        if is_project_example_request:
            # FIXED: More intelligent cognitive offloading protection (ISSUE 2 FIX)
            if state and hasattr(state, 'messages'):
                message_count = len([msg for msg in state.messages if msg.get('role') == 'user'])

                # Check if user has provided meaningful project context
                user_messages = [msg['content'].lower() for msg in state.messages if msg.get('role') == 'user']
                project_context_indicators = [
                    'designing', 'converting', 'transforming', 'adapting', 'building', 'creating',
                    'site', 'location', 'program', 'requirements', 'constraints', 'challenges',
                    'community center', 'warehouse', 'factory', 'building type'
                ]

                has_project_context = any(
                    any(indicator in msg for indicator in project_context_indicators)
                    for msg in user_messages[:-1]  # Exclude current message
                )

                # Only apply protection if both conditions are true:
                # 1. Less than 3 messages (reduced from 5)
                # 2. No meaningful project context provided
                if message_count < 3 and not has_project_context:
                    analysis["type"] = "premature_project_example_request"
                    analysis["cognitive_risk"] = "high"
                    analysis["indicators"].append(f"Project example request too early (only {message_count} messages, no project context)")
                    analysis["cognitive_protection"] = "active"
                    return analysis
                elif message_count >= 3 or has_project_context:
                    print(f"   ✅ PROJECT CONTEXT: Allowing example request (messages: {message_count}, context: {has_project_context})")

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
        user_topic = await self._extract_topic_from_user_input(user_input)
        project_context = getattr(state, 'current_design_brief', '') or ''

        print(f"   🏗️  Building type: {building_type}")
        print(f"   🎯 Topic: {user_topic}")
        print(f"   📋 Context: {project_context}")

        # Determine if this is a PROJECT example request or GENERAL example request
        user_input_lower = user_input.lower()
        project_example_keywords = [
            "example projects", "project examples", "examples of projects",
            "specific example project", "specific example projects", "example project",
            "precedent", "precedents", "case study", "case studies",
            "similar projects", "real project", "built project", "built projects",
            "actual projects", "specific projects", "project references",
            "show me specific", "specific.*projects", "examples of.*projects",
            "real examples", "built examples", "actual examples",
            "give me a specific example", "give me specific example"
        ]

        # Check for negative context (user explicitly saying they DON'T want examples)
        negative_patterns = ["don't want", "dont want", "not want", "no examples", "no projects", "not examples", "not projects"]
        has_negative_context = any(pattern in user_input_lower for pattern in negative_patterns)

        if has_negative_context:
            is_project_example_request = False
            print(f"🚫 Negative context detected - treating as general knowledge request")
        else:
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
                
                # Create specific database search query using AI-powered query generation
                try:
                    db_query = await self._create_smart_search_query(user_input, user_topic, building_type, request_type, "database")
                    # Ensure db_query is a string
                    if not isinstance(db_query, str):
                        db_query = str(db_query) if db_query else f"{user_topic} {building_type} architecture"
                except Exception as query_error:
                    print(f"   ⚠️ Smart query generation failed: {query_error}")
                    # Fallback to simple query
                    db_query = f"{user_topic} {building_type} architecture"

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
                # Check if database results are relevant by looking at similarity scores - LOWERED THRESHOLD
                avg_similarity = sum(r.get('similarity', 0) for r in knowledge_results) / len(knowledge_results)
                has_relevant_db_results = avg_similarity > 0.15  # LOWERED: Was 0.25, now 0.15 to capture more relevant results
                print(f"   📊 Database relevance check: {avg_similarity:.3f} (threshold: 0.15)")

            # ISSUE 2 FIX: For project examples, ALWAYS use web search - database is unreliable for project names
            should_try_web_search = False
            if request_type == "project_examples":
                # Skip database entirely for project examples - go straight to web search
                should_try_web_search = True
                print(f"   🏗️ PROJECT EXAMPLES: Using web search directly (database unreliable for project names)")
            elif not has_sufficient_db_results or not has_relevant_db_results:
                should_try_web_search = True
                print(f"   🌐 Database insufficient - trying web search")

            if should_try_web_search:
                if request_type == "project_examples":
                    # PROJECT EXAMPLES: Database → Web search (NO AI generation)
                    print(f"   🏗️ PROJECT EXAMPLES: Searching web for specific built projects")
                    try:
                        # Create specific web search query using AI-powered query generation
                        context_query = await self._create_smart_search_query(user_input, user_topic, building_type, request_type, "web")
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
                # Skip relevance check for web search results (already relevant from search engine)
                has_web_results = any(r.get('source') == 'web_search' for r in knowledge_results)
                relevance_threshold = 0.15  # LOWERED: Was 0.25, now 0.15 to capture more relevant results

                if has_web_results:
                    # Web search results are already relevant - proceed directly to synthesis
                    should_synthesize = True
                    avg_relevance = 1.0  # Assume web results are relevant
                else:
                    # Check if database results are relevant enough for synthesis
                    avg_relevance = sum(result.get('similarity', 0) for result in knowledge_results) / len(knowledge_results)
                    should_synthesize = avg_relevance >= relevance_threshold

                if should_synthesize:
                    # We have good database or web search results - synthesize them
                    if request_type == "project_examples":
                        examples_text = await self._synthesize_examples_with_llm(
                            user_topic, knowledge_results, building_type
                        )
                    else:
                        # GENERAL EXAMPLES: Use general knowledge synthesis
                        examples_text = await self._synthesize_general_knowledge_with_llm(
                            user_topic, knowledge_results, building_type
                        )

                    return {
                        "response_text": examples_text,
                        "response_type": "focused_examples",
                        "sources": knowledge_results,
                        "examples_provided": True
                    }
                else:
                    # Results are too low relevance - treat as no results and use AI generation
                    if not has_web_results:
                        print(f"   📊 Results too low relevance ({avg_relevance:.3f} < {relevance_threshold}) - using AI generation")
                    else:
                        print(f"   📊 Web results filtered out - using AI generation")
                    knowledge_results = []  # Clear results to trigger AI generation below
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

            # Handle both string and dict responses
            if isinstance(response, dict):
                response_text = response.get("content", "")
            else:
                response_text = str(response) if response else ""

            return response_text.strip()

        except Exception as e:
            print(f"⚠️ AI example generation failed: {e}")
            # Generate LLM fallback response instead of hardcoded text
            try:
                fallback_prompt = f"""
                The user is asking about {topic} in {building_type} architecture.
                Generate a helpful, engaging response that:
                1. Acknowledges their interest in the topic
                2. Asks a specific follow-up question to understand what aspect they want to explore
                3. Avoids generic phrases like "This is an interesting area" or "various approaches and strategies"
                4. Sounds natural and educational, not templated

                Keep it concise (1-2 sentences) and focus on guiding them toward more specific exploration.
                """

                fallback_response = await self.client.generate_completion([
                    self.client.create_system_message("You are an expert architecture educator providing personalized guidance."),
                    self.client.create_user_message(fallback_prompt)
                ])

                return fallback_response.strip() if fallback_response else f"What specific aspect of {topic} in {building_type} design would you like to explore further?"

            except Exception as fallback_error:
                print(f"⚠️ Fallback response generation also failed: {fallback_error}")
                # Last resort - simple contextual response without hardcoded phrases
                return f"What specific aspect of {topic} in {building_type} design would you like to explore further?"

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

    def _filter_relevant_results(self, knowledge_results: List[Dict], user_topic: str, user_input: str = "", building_type: str = "") -> List[Dict]:
        """Enhanced filter for knowledge results with building type and feature matching."""
        if not knowledge_results:
            return []

        relevant_results = []
        user_topic_lower = user_topic.lower()
        user_input_lower = user_input.lower()
        building_type_lower = building_type.lower()

        # Extract specific features from user input
        features = self._extract_architectural_features(user_input)

        for result in knowledge_results:
            # Get content from various possible fields
            content = result.get('content', '') or result.get('snippet', '') or result.get('text', '')
            title = result.get('title', '')

            # Combine title and content for relevance checking
            full_text = f"{title} {content}".lower()

            # Calculate relevance score
            relevance_score = 0

            # 1. Topic relevance (30% weight) - MORE FLEXIBLE
            topic_mentions = full_text.count(user_topic_lower)

            # Break down topic into individual words for better matching
            topic_words = user_topic_lower.split()
            word_mentions = sum(full_text.count(word) for word in topic_words if len(word) > 2)

            related_terms = self._get_related_terms(user_topic_lower)
            related_mentions = sum(full_text.count(term) for term in related_terms)

            # More generous scoring - if any topic words are found, give some credit
            topic_score = min(1.0, (topic_mentions * 1.0 + word_mentions * 0.3 + related_mentions * 0.2) / max(1, len(topic_words)))
            relevance_score += topic_score * 0.3

            # 2. Building type relevance (40% weight)
            building_score = 0
            if building_type_lower and building_type_lower != "project":
                building_mentions = full_text.count(building_type_lower)
                building_synonyms = self._get_building_type_synonyms(building_type_lower)
                synonym_mentions = sum(full_text.count(syn) for syn in building_synonyms)
                building_score = min(1.0, (building_mentions * 0.7 + synonym_mentions * 0.3) / 2)
            relevance_score += building_score * 0.4

            # 3. Feature relevance (30% weight) - MORE FLEXIBLE
            feature_score = 0
            if features:
                feature_mentions = sum(full_text.count(feature.lower()) for feature in features)
                feature_score = min(1.0, feature_mentions / len(features))
            else:
                # If no specific features, give some credit for general architectural terms
                general_arch_terms = ['design', 'space', 'building', 'architecture', 'structure']
                general_mentions = sum(1 for term in general_arch_terms if term in full_text)
                feature_score = min(0.5, general_mentions * 0.1)  # Max 0.5 for general terms
            relevance_score += feature_score * 0.3

            # 4. Use similarity score if available
            similarity = result.get('similarity', 0)
            if similarity > 0:
                relevance_score = max(relevance_score, similarity)

            # LOWERED THRESHOLD - not too strict, not too permissive
            # Require either good similarity OR good relevance score, but with reasonable minimums
            if (similarity > 0.15 and relevance_score > 0.10) or relevance_score > 0.25:
                relevant_results.append(result)
                # ISSUE 3 FIX: Commented out verbose debug prints for performance
                # print(f"   ✅ Relevant result: {title[:50]}... (score: {relevance_score:.3f}, similarity: {similarity:.3f}, topic: {topic_score:.2f}, building: {building_score:.2f}, features: {feature_score:.2f})")
            else:
                pass
                # ISSUE 3 FIX: Commented out verbose debug prints for performance
                # print(f"   ❌ Filtered out: {title[:50]}... (score: {relevance_score:.3f}, similarity: {similarity:.3f}, topic: {topic_score:.2f}, building: {building_score:.2f}, features: {feature_score:.2f})")

        return relevant_results

    def _extract_architectural_features(self, user_input: str) -> List[str]:
        """Extract specific architectural features from user input."""
        features = []
        user_input_lower = user_input.lower()

        # Common architectural features
        feature_keywords = [
            'courtyard', 'atrium', 'skylight', 'balcony', 'terrace', 'garden',
            'plaza', 'lobby', 'entrance', 'facade', 'roof', 'basement',
            'mezzanine', 'gallery', 'corridor', 'staircase', 'elevator',
            'window', 'door', 'column', 'beam', 'wall', 'ceiling',
            'amphitheater', 'auditorium', 'library', 'cafeteria', 'kitchen',
            'workshop', 'studio', 'office', 'meeting room', 'conference room'
        ]

        for feature in feature_keywords:
            if feature in user_input_lower:
                features.append(feature)

        return features

    def _get_building_type_synonyms(self, building_type: str) -> List[str]:
        """Get synonyms for building types to improve matching."""
        synonyms_map = {
            'community center': ['community centre', 'civic center', 'community building', 'neighborhood center'],
            'library': ['public library', 'branch library', 'media center', 'learning center'],
            'museum': ['gallery', 'exhibition hall', 'cultural center', 'art center'],
            'school': ['educational facility', 'learning facility', 'academic building', 'campus'],
            'hospital': ['medical center', 'healthcare facility', 'clinic', 'medical facility'],
            'office': ['office building', 'commercial building', 'workplace', 'corporate building'],
            'residential': ['housing', 'apartment', 'residential building', 'dwelling'],
            'retail': ['shopping center', 'commercial space', 'store', 'marketplace']
        }

        return synonyms_map.get(building_type, [])

    def _get_related_terms(self, topic: str) -> List[str]:
        """Get related terms for a topic to improve relevance checking."""
        related_terms_map = {
            'circulation': ['flow', 'movement', 'wayfinding', 'navigation', 'corridor', 'pathway', 'route'],
            'lighting': ['daylight', 'illumination', 'natural light', 'artificial light', 'luminance'],
            'materials': ['construction', 'building materials', 'finishes', 'structural materials'],
            'sustainability': ['green', 'environmental', 'energy efficient', 'sustainable design'],
            'accessibility': ['universal design', 'ada', 'barrier-free', 'inclusive design']
        }

        return related_terms_map.get(topic, [])

    async def _extract_topic_from_user_input(self, user_input: str) -> str:
        """Extract the main topic from user input using AI - TRULY FLEXIBLE for ANY topic"""

        try:
            # Use AI to intelligently extract the topic and search intent
            prompt = f"""
            Analyze this user question and extract the main architectural topic they're asking about.

            User question: "{user_input}"

            Instructions:
            1. Identify what the user is specifically asking about
            2. Extract the core architectural topic/concept
            3. If it's about sizing/capacity, include that aspect
            4. If it's about examples, focus on the subject they want examples of
            5. Return a concise search-friendly topic (2-4 words max)

            Examples:
            - "organic forms examples" → "organic forms"
            - "event space size for 200 people" → "event space capacity"
            - "sustainable materials for hospitals" → "sustainable materials"
            - "how to design flexible spaces" → "flexible spaces"
            - "parametric design in museums" → "parametric design"
            - "lighting requirements for offices" → "office lighting"

            Topic:"""

            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert at understanding architectural questions and extracting search topics. Be concise and specific."),
                self.client.create_user_message(prompt)
            ])

            if response and response.get("content"):
                extracted_topic = response["content"].strip()

                # Clean up the response (remove quotes, extra text)
                if extracted_topic.startswith('"') and extracted_topic.endswith('"'):
                    extracted_topic = extracted_topic[1:-1]

                # Take only the first line if multiple lines
                extracted_topic = extracted_topic.split('\n')[0].strip()

                # Validate it's reasonable (not too long, not empty)
                if extracted_topic and len(extracted_topic.split()) <= 5:
                    print(f"🧠 AI extracted topic: '{extracted_topic}'")
                    return extracted_topic

            # Fallback to simple extraction if AI fails
            print("⚠️ AI extraction failed, using fallback")
            return self._simple_topic_fallback(user_input)

        except Exception as e:
            print(f"⚠️ AI topic extraction error: {e}")
            return self._simple_topic_fallback(user_input)

    def _simple_topic_fallback(self, user_input: str) -> str:
        """Simple fallback topic extraction when AI fails"""
        # Remove question words and get meaningful terms
        words = user_input.lower().split()
        stop_words = {"what", "how", "why", "when", "where", "which", "who", "can", "could", "would", "should", "do", "does", "is", "are", "the", "a", "an", "of", "for", "in", "on", "at", "to", "from", "with", "about", "me", "you", "i", "we", "they"}

        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]

        # Return first few meaningful words
        if meaningful_words:
            return " ".join(meaningful_words[:3])
        else:
            return "architectural design"

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
            
            # ISSUE 4 FIX: Format with clickable markdown link to prevent truncation
            if url:
                lines.append(f"{i}. **[{title}]({url})**\n   {summary}\n")
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
            ], max_tokens=400, temperature=0.6)  # INCREASED: Fix example truncation

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

        # Generate LLM fallback response instead of hardcoded text
        try:
            fallback_prompt = f"""
            The user is asking for examples of {user_topic} in {building_type} architecture.
            Generate a helpful response that:
            1. Acknowledges their request for examples
            2. Asks a specific follow-up question to understand what type of examples would be most helpful
            3. Avoids generic phrases like "I'd be happy to help you explore"
            4. Sounds natural and educational, not templated

            Keep it concise (1-2 sentences) and focus on understanding their specific needs.
            """

            fallback_response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert architecture educator helping students find relevant examples."),
                self.client.create_user_message(fallback_prompt)
            ])

            # Handle both string and dict responses
            if isinstance(fallback_response, dict):
                response_text = fallback_response.get("content", "")
            else:
                response_text = str(fallback_response) if fallback_response else ""

            response_text = response_text.strip() if response_text else f"What type of {user_topic} examples would be most helpful for your {building_type} project?"

        except Exception as fallback_error:
            print(f"⚠️ Fallback response generation also failed: {fallback_error}")
            # Last resort - simple contextual response without hardcoded phrases
            response_text = f"What type of {user_topic} examples would be most helpful for your {building_type} project?"

        return {
            "response_text": response_text,
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
                # Generate LLM fallback response instead of hardcoded text
                try:
                    fallback_prompt = f"""
                    The user is asking about {user_topic} in {building_type} architecture, but no specific knowledge content was found.
                    Generate a helpful response that:
                    1. Acknowledges their interest in the topic
                    2. Asks a specific follow-up question to understand what aspect they want to learn about
                    3. Avoids generic phrases like "I'd be happy to help" or "This involves several key considerations"
                    4. Sounds natural and educational, not templated

                    Keep it concise (1-2 sentences) and focus on guiding them toward more specific exploration.
                    """

                    fallback_response = await self.client.generate_completion([
                        self.client.create_system_message("You are an expert architecture educator providing personalized guidance."),
                        self.client.create_user_message(fallback_prompt)
                    ])

                    return fallback_response.strip() if fallback_response else f"What specific aspect of {user_topic} in {building_type} design would you like to learn more about?"

                except Exception as fallback_error:
                    print(f"⚠️ Fallback response generation failed: {fallback_error}")
                    # Last resort - simple contextual response without hardcoded phrases
                    return f"What specific aspect of {user_topic} in {building_type} design would you like to learn more about?"

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

    def _create_specific_db_query(self, user_input: str, building_type: str, request_type: str) -> str:
        """Create a specific database search query by extracting meaningful keywords from user input."""
        import re

        # Clean and tokenize user input
        user_input_clean = re.sub(r'[^\w\s]', ' ', user_input.lower())
        words = user_input_clean.split()

        print(f"   🔍 Input words: {words}")

        # Remove only essential stop words (keep ALL domain-specific terms for any topic)
        stop_words = {
            'can', 'you', 'give', 'me', 'show', 'find', 'get', 'what', 'how', 'where', 'when', 'why',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'this', 'that', 'these', 'those', 'i', 'we', 'they', 'it', 'he', 'she',
            'example', 'examples', 'provide', 'need', 'want'  # Generic request words only
        }

        # Extract meaningful keywords (keep all architectural and descriptive terms)
        meaningful_words = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                meaningful_words.append(word)

        # Remove building type components to avoid redundancy
        building_type_words = building_type.replace('_', ' ').lower().split()
        meaningful_words = [word for word in meaningful_words if word not in building_type_words]

        print(f"   🎯 Extracted keywords: {meaningful_words}")

        # Build query using the actual user keywords
        if meaningful_words:
            # Take the most relevant keywords (limit to avoid over-specification)
            key_terms = meaningful_words[:3]  # Reduced from 4 to 3 to avoid over-specification
            if request_type == "project_examples":
                query = f"{building_type.replace('_', ' ')} {' '.join(key_terms)} project"
            else:
                query = f"{building_type.replace('_', ' ')} {' '.join(key_terms)}"
        else:
            # Fallback if no meaningful words extracted
            if request_type == "project_examples":
                query = f"{building_type.replace('_', ' ')} project case study"
            else:
                query = f"{building_type.replace('_', ' ')} design"

        print(f"   🎯 Final DB query: {query}")
        return query

    def _create_specific_db_query_with_topic(self, user_topic: str, building_type: str, request_type: str) -> str:
        """Create a specific database search query using the extracted topic."""

        print(f"   🎯 Using extracted topic: '{user_topic}' for {building_type}")

        # Build query using the extracted topic
        if user_topic and user_topic.strip():
            # Clean the topic
            topic_clean = user_topic.strip()

            if request_type == "project_examples":
                # For project examples: "organic forms architecture project" or "event space community center project"
                if building_type and building_type != "unknown":
                    query = f"{topic_clean} {building_type.replace('_', ' ')} project"
                else:
                    query = f"{topic_clean} architecture project"
            else:
                # For general examples: "organic forms architecture" or "event space design"
                if building_type and building_type != "unknown":
                    query = f"{topic_clean} {building_type.replace('_', ' ')}"
                else:
                    query = f"{topic_clean} architecture"
        else:
            # Fallback if no topic extracted
            if request_type == "project_examples":
                query = f"{building_type.replace('_', ' ')} project case study"
            else:
                query = f"{building_type.replace('_', ' ')} design"

        print(f"   🎯 Final DB query with topic: {query}")
        return query

    def _create_specific_web_query(self, user_input: str, building_type: str, request_type: str) -> str:
        """Create a specific web search query by extracting meaningful keywords from user input."""
        import re

        # Clean and tokenize user input
        user_input_clean = re.sub(r'[^\w\s]', ' ', user_input.lower())
        words = user_input_clean.split()

        # Remove only essential stop words (keep architectural terms)
        stop_words = {
            'can', 'you', 'give', 'me', 'show', 'find', 'get', 'what', 'how', 'where', 'when', 'why',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'this', 'that', 'these', 'those', 'i', 'we', 'they', 'it', 'he', 'she',
            'example', 'examples'  # Only remove generic request words, keep architectural terms
        }

        # Extract meaningful keywords
        meaningful_words = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                meaningful_words.append(word)

        print(f"   🌐 Web keywords extracted: {meaningful_words}")

        # Build web search query using actual user keywords
        if request_type == "project_examples":
            if meaningful_words:
                # Use quotes for building type and key terms for better matching
                key_terms = " ".join(meaningful_words[:3])  # Limit to avoid over-specification
                query = f'"{building_type}" {key_terms} architect project built site:archdaily.com OR site:dezeen.com'
            else:
                # Fallback for project search
                query = f'"{building_type}" architecture project built site:archdaily.com OR site:dezeen.com'
        else:
            # For general examples, broader search
            if meaningful_words:
                key_terms = " ".join(meaningful_words[:3])
                query = f'{building_type} {key_terms} architecture design'
            else:
                query = f'{building_type} architecture design'

        print(f"   🌐 Final web query: {query}")
        return query

    def _create_flexible_db_query(self, user_topic: str, building_type: str) -> str:
        """Create flexible database query based on semantic analysis"""

        # Start with core terms
        query_parts = []

        # Add user topic (always include)
        if user_topic and user_topic.strip():
            query_parts.append(user_topic.strip())

        # Add building type if different from topic
        if building_type and building_type.lower() not in user_topic.lower():
            query_parts.append(building_type)

        # Analyze topic for architectural concepts and add related terms
        topic_lower = user_topic.lower()

        # Spatial/dimensional queries
        if any(term in topic_lower for term in ['size', 'dimension', 'area', 'capacity']):
            query_parts.extend(['area', 'square feet', 'dimensions'])

        # Construction/material queries
        elif any(term in topic_lower for term in ['construction', 'steel', 'concrete', 'material']):
            query_parts.extend(['building', 'structure', 'materials'])

        # Spatial element queries
        elif any(term in topic_lower for term in ['courtyard', 'atrium', 'plaza']):
            query_parts.extend(['outdoor space', 'central court'])

        # Meeting/conference space queries
        elif any(term in topic_lower for term in ['conference', 'meeting', 'hall']):
            query_parts.extend(['meeting room', 'assembly', 'auditorium'])

        # Always add architecture context
        query_parts.append('architecture')

        # Join and clean
        query = ' '.join(query_parts)

        # Remove duplicates while preserving order
        words = []
        seen = set()
        for word in query.split():
            if word.lower() not in seen:
                words.append(word)
                seen.add(word.lower())

        return ' '.join(words)

    def _create_specific_web_query_with_topic(self, user_topic: str, building_type: str, request_type: str) -> str:
        """Create a specific web search query using the extracted topic."""

        print(f"   🌐 Using extracted topic: '{user_topic}' for web search")

        # Build web search query using the extracted topic
        if user_topic and user_topic.strip():
            topic_clean = user_topic.strip()

            if request_type == "project_examples":
                # For project examples: search for specific built projects
                if building_type and building_type != "unknown":
                    query = f'"{building_type}" {topic_clean} architect project built site:archdaily.com OR site:dezeen.com'
                else:
                    query = f'{topic_clean} architecture project built site:archdaily.com OR site:dezeen.com'
            else:
                # For general examples: broader search for strategies/approaches
                if building_type and building_type != "unknown":
                    query = f'{building_type} {topic_clean} architecture design'
                else:
                    query = f'{topic_clean} architecture design'
        else:
            # Fallback if no topic extracted
            if request_type == "project_examples":
                query = f'"{building_type}" architect project built site:archdaily.com OR site:dezeen.com'
            else:
                query = f'{building_type} architecture design'

        print(f"   🌐 Final web query with topic: {query}")
        return query

    async def _create_smart_search_query(self, user_input: str, extracted_topic: str, building_type: str, request_type: str, search_type: str) -> str:
        """Create intelligent search queries using AI to understand user intent"""

        try:
            # Use AI to create the best search query
            prompt = f"""
            Create an optimal search query for finding architectural information.

            User's original question: "{user_input}"
            Extracted topic: "{extracted_topic}"
            Building type: "{building_type}"
            Request type: "{request_type}"
            Search platform: "{search_type}"

            Instructions:
            1. Create queries optimized for the specific search platform and request type
            2. For DATABASE searches: Use broader architectural concepts + building type
            3. For WEB searches: Add "projects", "examples", or "case studies" for findability
            4. For GENERAL EXAMPLES: Focus on design approaches and strategies
            5. For PROJECT EXAMPLES: Include "buildings", "projects", "case studies"
            6. Keep queries 3-5 words for optimal performance

            Query Strategy Examples:
            DATABASE (broader concepts):
            - "circulation examples" → "circulation design community centers"
            - "facade materials" → "facade materials residential architecture"
            - "sustainable design" → "sustainable architecture green design"

            WEB (project-focused):
            - "circulation examples" → "community center circulation design projects"
            - "facade materials" → "residential facade materials case studies"
            - "sustainable design" → "sustainable architecture projects examples"

            Search query:"""

            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert at creating effective search queries for architectural information. Be specific and use professional terminology."),
                self.client.create_user_message(prompt)
            ])

            if response and response.get("content"):
                smart_query = response["content"].strip()

                # Clean up the response
                if smart_query.startswith('"') and smart_query.endswith('"'):
                    smart_query = smart_query[1:-1]

                smart_query = smart_query.split('\n')[0].strip()

                if smart_query and len(smart_query.split()) <= 8:
                    print(f"🧠 AI generated {search_type} query: '{smart_query}'")
                    return smart_query

            # Fallback to topic-based query
            print(f"⚠️ AI query generation failed, using topic fallback")
            return self._create_fallback_query(extracted_topic, building_type, request_type)

        except Exception as e:
            print(f"⚠️ AI query generation error: {e}")
            return self._create_fallback_query(extracted_topic, building_type, request_type)

    def _create_fallback_query(self, topic: str, building_type: str, request_type: str) -> str:
        """Simple fallback query when AI fails"""
        if topic and building_type:
            return f"{topic} {building_type.replace('_', ' ')}"
        elif topic:
            return f"{topic} architecture"
        else:
            return f"{building_type.replace('_', ' ')} design"

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

        # DEBUG: Print what content is being passed to synthesis (ISSUE 3 FIX - COMMENTED OUT)
        # print(f"🔍 DEBUG: Synthesizing {len(knowledge_results)} results")
        # for i, r in enumerate(knowledge_results[:3]):
        #     title = r.get('title', 'Unknown')[:50]
        #     content = r.get('content', r.get('snippet', ''))[:100]
        #     print(f"   📄 Result {i+1}: {title} | Content: {content}...")
        # print(f"🔍 DEBUG: Combined knowledge length: {len(combined_knowledge)} chars")
        # print(f"🔍 DEBUG: User topic: {user_topic}")
        # print(f"🔍 DEBUG: Building type: {building_type}")
        
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
                max_tokens=350,  # INCREASED: Fix project example truncation with links
                temperature=0.4
            )
            
            synthesized_text = response.choices[0].message.content.strip()

            # Keep URLs intact - don't replace them with placeholders
            # The URLs from web search should be clickable

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
        user_topic = await self._extract_topic_from_user_input(user_input)

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
                max_tokens=400,  # INCREASED: Fix strategies response truncation
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

