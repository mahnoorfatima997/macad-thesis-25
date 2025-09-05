from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph

from orchestration.types import WorkflowState
from orchestration.graph_builder import build_workflow
from orchestration.nodes import (
    make_context_node,
    make_router_node,
    make_analysis_node,
    make_domain_expert_node,
    make_socratic_node,
    make_cognitive_enhancement_node,
    make_synthesizer_node,
)
from orchestration.synthesis import build_synthesizer


class LangGraphOrchestrator:
    """Modular LangGraph orchestrator.

    Preserves behavior of the previous monolithic orchestrator while
    organizing nodes, routing, synthesis, and graph wiring into modules.
    """

    def __init__(self, domain: str = "architecture", config: Optional[Any] = None):
        # Import here to avoid circulars and preserve original dependency creation
        from config.orchestrator_config import OrchestratorConfig, DEFAULT_CONFIG
        from agents.analysis_agent import AnalysisAgent
        from agents.socratic_tutor import SocraticTutorAgent
        from agents.domain_expert import DomainExpertAgent
        from agents.context_agent import ContextAgent
        from agents.cognitive_enhancement import CognitiveEnhancementAgent
        from conversation_progression import ConversationProgressionManager
        from first_response_generator import FirstResponseGenerator
        from utils.routing_decision_tree import AdvancedRoutingDecisionTree
        from utils.state_validator import StateValidator, StateMonitor
        from utils.response_length_controller import ensure_quality as ensure_quality_fn

        self.domain = domain
        self.config = config or DEFAULT_CONFIG
        self.logger = logging.getLogger(f"{__name__}.{domain}")

        # Agents
        self.analysis_agent = AnalysisAgent(domain)
        self.socratic_agent = SocraticTutorAgent(domain)
        self.domain_expert = DomainExpertAgent(domain)
        self.cognitive_enhancement_agent = CognitiveEnhancementAgent(domain)
        self.context_agent = ContextAgent(domain)

        # Progression
        self.progression_manager = ConversationProgressionManager(domain)
        self.first_response_generator = FirstResponseGenerator(domain)

        # Routing & validation
        self.routing_decision_tree = AdvancedRoutingDecisionTree()
        self.state_validator = StateValidator()
        self.state_monitor = StateMonitor()

        # Bind synthesis using original methods from the legacy class (we re-implement them below)
        synthesize_fn, _ = build_synthesizer(self)

        # Create node handlers
        context_h = make_context_node(
            self.context_agent,
            self.progression_manager,
            self.first_response_generator,
            self.state_validator,
            self.state_monitor,
            self.logger,
        )
        router_h = make_router_node(self.route_decision, self.state_validator, self.state_monitor, self.logger)
        analysis_h = make_analysis_node(self.analysis_agent, self.state_validator, self.state_monitor, self.logger, self.progression_manager)
        domain_h = make_domain_expert_node(self.domain_expert, self.state_validator, self.state_monitor, self.logger)
        socratic_h = make_socratic_node(self.socratic_agent, self.state_validator, self.state_monitor, self.logger)
        cognitive_h = make_cognitive_enhancement_node(self.cognitive_enhancement_agent, self.state_validator, self.state_monitor, self.logger)
        synthesizer_h = make_synthesizer_node(synthesize_fn, ensure_quality_fn, self.state_validator, self.state_monitor, self.logger)

        class Handlers:
            pass

        handlers = Handlers()
        handlers.context = context_h
        handlers.router = router_h
        handlers.analysis = analysis_h
        handlers.domain_expert = domain_h
        handlers.socratic = socratic_h
        handlers.cognitive = cognitive_h
        handlers.synthesizer = synthesizer_h

        # Build workflow
        self.workflow = build_workflow(WorkflowState, handlers, self.route_decision)

        # Expose handlers for legacy helper methods (execute_agent_sequence)
        self.handlers = handlers

        self.logger.info(f"LangGraph orchestrator initialized for {domain}")

    # The following methods mirror the legacy class implementations
    # to preserve routing decisions and synthesis behaviors.

    def route_decision(self, state: WorkflowState) -> str:
        from utils.routing_decision_tree import RoutingContext

        classification = state.get("student_classification", {})
        context_analysis = state.get("context_analysis", {})
        routing_suggestions = state.get("routing_suggestions", {})
        student_state = state.get("student_state", None)

        try:
            classification["user_input"] = state.get("last_message", "")
        except Exception:
            pass

        # CONTEXT CONSISTENCY: Validate and repair context before routing
        if student_state:
            context_validation = student_state.validate_and_repair_context_consistency()
            if context_validation["repairs_made"]:
                print(f"🔧 Context repairs made: {context_validation['repairs_made']}")
            if context_validation["context_stability"] < 0.5:
                print(f"⚠️ Low context stability: {context_validation['context_stability']:.2f}")

        # Get conversation continuity context
        continuity_context = {}
        if student_state:
            continuity_context = student_state.get_conversation_continuity_context()

        routing_context = RoutingContext(
            classification=classification,
            context_analysis=context_analysis,
            routing_suggestions=routing_suggestions,
            student_state=student_state.__dict__ if student_state else None,
            conversation_history=student_state.messages if student_state else [],
            current_phase=student_state.design_phase.value if student_state else "ideation",
            phase_progress=0.0,
            # Conversation continuity context
            conversation_continuity=continuity_context,
            is_continuing_conversation=student_state.is_continuing_conversation() if student_state else False,
            current_topic=continuity_context.get("current_topic", ""),
            last_route_used=continuity_context.get("last_route_used", ""),
            topic_history=continuity_context.get("topic_history", []),
            route_history=continuity_context.get("route_history", []),
            detected_building_type=continuity_context.get("detected_building_type", ""),
            building_type_confidence=continuity_context.get("building_type_confidence", 0.0),
            design_phase_detected=continuity_context.get("design_phase_detected", ""),
            phase_confidence=continuity_context.get("phase_confidence", 0.0),
            # CRITICAL FIX: Extract is_first_message from classification
            is_first_message=classification.get("is_first_message", False),
        )

        decision = self.routing_decision_tree.decide_route(routing_context)
        self.last_routing_decision = decision  # for reasoning access

        # CRITICAL FIX: Update state with enhanced classification from routing decision
        # This ensures the metadata uses the correct user_intent (not design_problem)
        if hasattr(decision, 'classification') and decision.classification:
            state["student_classification"] = decision.classification
            print(f"🔧 FIXED: Updated classification with user_intent = {decision.classification.get('user_intent', 'unknown')}")

        # Update conversation context with routing decision
        if student_state:
            user_input = state.get("last_message", "")
            detected_topic = classification.get("topic", "") or classification.get("building_type", "")
            student_state.update_conversation_context(user_input, decision.route.value, detected_topic)

            # Update building type and design phase context if detected
            # IMPORTANT: Only update building type from brief or first message, not every message
            if classification.get("building_type") and len(student_state.messages) <= 2:  # Only for first interaction
                confidence = classification.get("building_type_confidence", 0.5)
                student_state.update_building_type_context(classification["building_type"], confidence)

            # Update project context from conversation (adaptive reuse, warehouse, etc.)
            student_state.detect_and_update_project_context_from_conversation()

            # ADDITIONAL: Extract building type from design brief if not already set
            if (student_state.building_type == "unknown" and
                hasattr(student_state, 'current_design_brief') and
                student_state.current_design_brief):
                extracted_type = student_state.extract_building_type_from_brief_only()
                if extracted_type != "unknown":
                    print(f"🏗️ Orchestrator extracted building type from brief: {extracted_type}")
                    student_state.building_type = extracted_type

            if classification.get("design_phase"):
                confidence = classification.get("design_phase_confidence", 0.5)
                student_state.update_design_phase_context(classification["design_phase"], confidence)

        # Store detailed decision in state for later use
        state["detailed_routing_decision"] = {
            "route": decision.route.value,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "rule_applied": decision.rule_applied,
            "context_agent_override": decision.context_agent_override,
            "cognitive_offloading_detected": decision.cognitive_offloading_detected,
            "cognitive_offloading_type": getattr(decision.cognitive_offloading_type, "value", None),
            "context_agent_confidence": decision.context_agent_confidence,
            "classification": decision.classification,
            "metadata": decision.metadata,
        }
        
        # CRITICAL FIX: Store the routing decision path in the main routing_decision field
        # This is what the synthesis method actually uses
        if "routing_decision" not in state:
            state["routing_decision"] = {}
        state["routing_decision"]["path"] = decision.route.value
        state["routing_decision"]["reasoning"] = decision.reason
        state["routing_decision"]["confidence"] = decision.confidence
        state["routing_decision"]["rule_applied"] = decision.rule_applied

        return decision.route.value

    # ------------- Synthesis helpers (ported) -------------

    def synthesize_responses(self, state: WorkflowState) -> tuple[str, Dict[str, Any]]:
        self.logger.info("Synthesizing responses...")

        agent_results = self._get_agent_results(state)
        routing_decision = state.get("routing_decision", {})
        user_input = state.get("last_message", "")
        classification = state.get("student_classification", {})

        routing_path = routing_decision.get("path", "default")

        # Progressive conversation paths use precomputed response
        if routing_path in ["progressive_opening", "topic_transition"] and state.get("final_response"):
            metadata = self._build_metadata("progressive_opening", agent_results, routing_decision, classification)
            # Check for image-specific discussion enhancement
            enhanced_response = self._enhance_response_with_image_discussion(state.get("final_response", ""), user_input)
            return enhanced_response, metadata

        final_response, response_type = self._synthesize_by_routing_path(
            routing_path, agent_results, user_input, classification, state
        )

        # ENHANCEMENT: Apply route-specific shaping before quality controls
        try:
            from .synthesis import shape_by_route
            user_message_count = len([m for m in state.get("messages", []) if m.get("role") == "user"])
            context_analysis = state.get("context_analysis", {})
            final_response = shape_by_route(
                text=final_response,
                routing_path=routing_path,
                classification=classification,
                ordered_results=agent_results,
                user_message_count=user_message_count,
                context_analysis=context_analysis,
            )
        except Exception as e:
            self.logger.warning(f"Route shaping failed: {e}")

        # Apply response quality controls similar to legacy logic
        agent_type_map = {
            "domain_knowledge": "domain_expert",
            "socratic_guidance": "socratic_tutor",
            "cognitive_enhancement": "cognitive_enhancement",
        }
        agent_type = agent_type_map.get(response_type, "default")
        final_response = self.ensure_quality(final_response, agent_type)

        # Check for image-specific discussion enhancement
        enhanced_response = self._enhance_response_with_image_discussion(final_response, user_input)

        # ENHANCEMENT: Build metadata with quality flags and student state
        metadata = self._build_metadata(response_type, agent_results, routing_decision, classification, state)

        # Add quality flags to metadata
        try:
            from .synthesis import calculate_quality_flags
            metadata["quality"] = calculate_quality_flags(enhanced_response)
        except Exception as e:
            self.logger.warning(f"Quality flags calculation failed: {e}")

        return enhanced_response, metadata

    def _get_agent_results(self, state: WorkflowState) -> Dict[str, Any]:
        # Ensure all agent results are dictionaries, not AgentResponse objects
        socratic_result = state.get("socratic_result", {})
        domain_result = state.get("domain_expert_result", {})
        analysis_result = state.get("analysis_result", {})
        cognitive_result = state.get("cognitive_enhancement_result", {})
        
        # Convert AgentResponse objects to dictionaries if needed
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(analysis_result, 'to_dict'):
            analysis_result = analysis_result.to_dict()
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()
        
        return {
            "socratic": socratic_result,
            "domain": domain_result,
            "analysis": analysis_result,
            "cognitive": cognitive_result,
        }

    def _synthesize_by_routing_path(
        self,
        routing_path: str,
        agent_results: Dict[str, Any],
        user_input: str,
        classification: Dict[str, Any],
        state: WorkflowState,
    ) -> tuple[str, str]:
        """Enhanced synthesis method aligned with gamified routing system"""

        # Conversation management routes
        if routing_path in ["progressive_opening", "topic_transition"]:
            final_response = state.get("final_response", "")
            if final_response:
                return final_response, routing_path
            return self._synthesize_default_response(agent_results)

        # Core learning routes
        if routing_path == "knowledge_only":
            return self._synthesize_knowledge_only_response(agent_results, user_input, classification)
        elif routing_path == "socratic_exploration":
            return self._synthesize_socratic_exploration_response(agent_results)
        elif routing_path == "cognitive_challenge":
            return self._synthesize_cognitive_challenge_response(agent_results)
        elif routing_path == "multi_agent_comprehensive":
            return self._synthesize_multi_agent_comprehensive_response(agent_results, user_input, classification)

        # Support and scaffolding routes
        elif routing_path == "socratic_clarification":
            return self._synthesize_socratic_clarification_response(agent_results, user_input, classification)
        elif routing_path == "supportive_scaffolding":
            return self._synthesize_supportive_scaffolding_response(agent_results, user_input, classification)
        elif routing_path == "foundational_building":
            return self._synthesize_foundational_building_response(agent_results, user_input, classification)
        elif routing_path == "knowledge_with_challenge":
            return self._synthesize_knowledge_with_challenge_response(agent_results, user_input, classification)
        elif routing_path == "balanced_guidance":
            return self._synthesize_balanced_guidance_response(agent_results, user_input, classification, state)

        # Intervention routes
        elif routing_path == "cognitive_intervention":
            return self._synthesize_cognitive_intervention_response(agent_results)

        # Error handling route
        elif routing_path == "error":
            return self._synthesize_error_response(agent_results, user_input, classification)

        # Legacy route handling for backward compatibility
        elif routing_path == "technical_question":
            return self._synthesize_knowledge_only_response(agent_results, user_input, classification)
        elif routing_path == "feedback_request":
            return self._synthesize_multi_agent_comprehensive_response(agent_results, user_input, classification)
        elif routing_path == "design_guidance":
            return self._synthesize_balanced_guidance_response(agent_results, user_input, classification, state)

        # Fallback
        return self._synthesize_default_response(agent_results)

    def _synthesize_knowledge_only_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        
        # Safety check: ensure results are dictionaries
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        
        # Detect example requests for special handling
        has_example_keywords = any(k in user_input.lower() for k in ["example", "examples", "precedent", "case study", "case studies", "project", "projects"])
        is_example_intent = classification.get("interaction_type") == "example_request" or classification.get("user_intent") == "example_request"
        is_example_req = has_example_keywords and is_example_intent

        if is_example_req:
            # ENHANCED: Add synthesis and thoughtful questions to example responses
            text = domain_result.get('response_text', '') if domain_result else ''
            if text:
                enhanced_text = self._enhance_example_response_with_synthesis(text, user_input, classification)
                return enhanced_text, "knowledge_only"
            else:
                return self._synthesize_example_response(domain_result, user_input, classification), "knowledge_only"

        # ENHANCED: For knowledge_only routes, add thoughtful questions to domain expert responses
        if domain_result and domain_result.get('response_text'):
            domain_text = domain_result.get('response_text', '')
            enhanced_text = self._enhance_knowledge_response_with_questions(domain_text, user_input, classification)
            formatted_text = self._format_response_for_readability(enhanced_text)
            return formatted_text, "knowledge_only"
        elif socratic_result and socratic_result.get('response_text'):
            socratic_text = socratic_result.get('response_text', '')
            enhanced_text = self._enhance_knowledge_response_with_questions(socratic_text, user_input, classification)
            formatted_text = self._format_response_for_readability(enhanced_text)
            return formatted_text, "knowledge_only"
        return self._synthesize_example_response(domain_result, user_input, classification), "knowledge_only"

    def _synthesize_socratic_exploration_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        socratic_result = agent_results.get("socratic", {})

        # Safety check: ensure socratic_result is a dictionary
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()

        if socratic_result and socratic_result.get("response_text"):
            response_text = socratic_result.get("response_text", "")

            # IMPROVED: Only add questions if the response truly lacks them
            # Check if response already contains questions (not just ending with ?)
            has_questions = bool(re.search(r'\?', response_text))

            if not has_questions:
                # Check if there's a separate question in the result
                socratic_question = socratic_result.get("question_text", "")
                if not socratic_question:
                    # Look for question in metadata or other fields
                    metadata = socratic_result.get("metadata", {})
                    socratic_question = metadata.get("socratic_question", "")

                # If we found a question, append it
                if socratic_question and not socratic_question in response_text:
                    response_text = f"{response_text}\n\n{socratic_question}"
                elif not socratic_question:
                    # Only add fallback if response is very short or clearly incomplete
                    if len(response_text.strip()) < 100:
                        response_text = f"{response_text}\n\nWhat aspects of this would you like to explore further?"

            return response_text, "socratic_exploration"
        return (
            "I'd be happy to help you explore this topic together. What specific aspects would you like to think about?",
            "socratic_exploration",
        )

    def _synthesize_cognitive_intervention_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        cognitive_result = agent_results.get("cognitive", {})
        
        # Safety check: ensure result is a dictionary
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()
        
        if cognitive_result and cognitive_result.get("response_text"):
            return cognitive_result.get("response_text", ""), "cognitive_intervention"
        return (
            "I notice you're asking for specific answers early in your design process. Let's explore this together instead.",
            "cognitive_intervention",
        )

    def _synthesize_default_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        cognitive_result = agent_results.get("cognitive", {})
        
        # Safety check: ensure all results are dictionaries
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()
        
        if domain_result and socratic_result:
            return (
                f"{domain_result.get('response_text', '')}\n\n{socratic_result.get('response_text', '')}",
                "multi_agent_synthesis",
            )
        if domain_result:
            return domain_result.get("response_text", ""), "domain_knowledge"
        if socratic_result:
            return socratic_result.get("response_text", ""), "socratic_guidance"
        if cognitive_result:
            return cognitive_result.get("response_text", ""), "cognitive_enhancement"
        return (
            "I'd be happy to help you with your architectural project. What specific aspect would you like to explore?",
            "fallback",
        )

    def _extract_building_type_from_context(self, state) -> str:
        """
        Get building type from centralized conversation continuity context.
        Uses the enhanced conversation context to avoid multiple detections.
        """
        # PRIORITY 1: Use conversation continuity context (highest confidence)
        if state and 'student_state' in state and state['student_state'] and hasattr(state['student_state'], 'conversation_context'):
            continuity_context = state['student_state'].conversation_context
            if continuity_context.detected_building_type and continuity_context.building_type_confidence > 0.7:
                return continuity_context.detected_building_type

        # PRIORITY 2: Use state.building_type if available and not unknown
        if hasattr(state, "building_type") and state.building_type and state.building_type != "unknown":
            return state.building_type

        # PRIORITY 3: Use student_state.building_type if available and not unknown
        if state and 'student_state' in state and state['student_state'] and hasattr(state['student_state'], 'building_type'):
            if state['student_state'].building_type and state['student_state'].building_type != "unknown":
                return state['student_state'].building_type

        # PRIORITY 4: Use conversation continuity context even with lower confidence
        if state and 'student_state' in state and state['student_state'] and hasattr(state['student_state'], 'conversation_context'):
            continuity_context = state['student_state'].conversation_context
            if continuity_context.detected_building_type and continuity_context.building_type_confidence > 0.3:
                return continuity_context.detected_building_type

        # FALLBACK: Return unknown (no more local detection)
        return "unknown"

    def _extract_student_state_from_results(self, agent_results: Dict[str, Any]) -> Any:
        """Extract student state from agent results for phase detection."""
        # Try to get student state from various sources
        for agent_name, result in agent_results.items():
            if result and hasattr(result, 'student_state'):
                return result.student_state
            elif result and isinstance(result, dict) and 'student_state' in result:
                return result['student_state']
        
        # If no student state found, return None
        return None

    def _extract_topic_from_user_input(self, user_input: str) -> str:
        topics = ["circulation", "lighting", "spatial", "form", "function", "context", "materials", "structure"]
        user_lower = user_input.lower()
        for t in topics:
            if t in user_lower:
                return t
        return "design"

    def _synthesize_example_response(self, domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any], state=None) -> str:
        # Safety check: ensure result is a dictionary
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        
        domain_text = domain_result.get("response_text", "") if domain_result else ""
        if domain_text:
            return domain_text
        building_type = self._extract_building_type_from_context(state) if state is not None else "project"
        topic = self._extract_topic_from_user_input(user_input)
        return (
            f"I'd be happy to help you explore {topic} for your {building_type} project! "
            f"To provide the most relevant guidance, could you tell me what specific aspect of {topic} you're most interested in understanding?"
        )

    def _synthesize_feedback_response(self, socratic_result: Dict[str, Any], domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        # Safety check: ensure results are dictionaries
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        return "I'd be glad to provide feedback! What specific aspects of your project should I focus on?"

    def _synthesize_technical_response(self, domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        # Safety check: ensure result is a dictionary
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        topic = self._extract_topic_from_user_input(user_input)
        return f"I'd be happy to help with technical requirements for {topic}! Could you specify what technical aspects you need information about?"

    def _synthesize_clarification_response(self, socratic_result: Dict[str, Any], domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        # Safety check: ensure results are dictionaries
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        topic = self._extract_topic_from_user_input(user_input)
        return f"I understand {topic} can be complex! What specific part would you like me to explain in more detail?"

    def _synthesize_design_guidance_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        
        # Safety check: ensure results are dictionaries
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", "")
        if domain_result and domain_result.get("response_text"):
            return domain_result.get("response_text", "")
        return "That's a great design question! What specific aspects are you trying to optimize?"

    # ------------- Enhanced synthesis methods for new routing system -------------

    def _synthesize_cognitive_challenge_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize cognitive challenge response"""
        cognitive_result = agent_results.get("cognitive", {})

        # Safety check: ensure result is a dictionary
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()

        if cognitive_result and cognitive_result.get("response_text"):
            return cognitive_result.get("response_text", ""), "cognitive_challenge"
        return (
            "Let me challenge your thinking on this. What assumptions are you making that we could question?",
            "cognitive_challenge",
        )

    def _synthesize_multi_agent_comprehensive_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize comprehensive multi-agent response"""
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        cognitive_result = agent_results.get("cognitive", {})
        analysis_result = agent_results.get("analysis", {})

        # Safety check: ensure all results are dictionaries
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()
        if hasattr(analysis_result, 'to_dict'):
            analysis_result = analysis_result.to_dict()

        # ENHANCED: Create contextual response that addresses user's specific input
        responses = []

        # Add domain expertise if available and relevant
        if domain_result and domain_result.get("response_text"):
            domain_text = domain_result.get("response_text", "").strip()
            if domain_text and len(domain_text) > 50:  # Ensure substantial content
                responses.append(domain_text)

        # Add socratic guidance if available and different from domain
        if socratic_result and socratic_result.get("response_text"):
            socratic_text = socratic_result.get("response_text", "").strip()
            if socratic_text and len(socratic_text) > 50:
                # Only add if significantly different from domain response
                if not responses or not self._responses_too_similar(socratic_text, responses[0]):
                    responses.append(socratic_text)

        # FIXED: Synthesize multiple perspectives into one cohesive response
        if len(responses) >= 2:
            # CRITICAL FIX: Create intelligent, contextual synthesis instead of mechanical combination
            synthesis_prompt = f"""
            You are an expert architectural mentor responding to this student's specific design challenge:

            STUDENT'S QUESTION: "{user_input}"

            AVAILABLE EXPERT KNOWLEDGE: {responses[0]}
            AVAILABLE SOCRATIC INSIGHTS: {responses[1]}

            CRITICAL REQUIREMENTS:
            - DO NOT mechanically combine the two responses
            - DO NOT insert technical terms unless they genuinely solve their specific problem
            - CREATE ONE intelligent response that feels like a thoughtful expert mentor
            - DIRECTLY address their specific design challenge about warehouse transformation
            - USE the knowledge and insights to provide contextual, creative guidance
            - CRITICAL: Take the socratic questions and integrate them seamlessly within the domain content - don't just append them at the end
            - Use the questions to transition between concepts, deepen understanding, and encourage reflection
            - Make it feel like one expert speaking who naturally asks thought-provoking questions while providing guidance
            - AVOID generic architectural education language

            FORMATTING REQUIREMENTS:
            - Use **bold text** for key concepts and important design principles
            - Use *italics* for emphasis on specific considerations or nuanced points
            - Structure in 2-3 clear paragraphs with natural breaks
            - Integrate questions naturally within the flow, not as a separate section

            Write a well-formatted response that demonstrates deep understanding of their specific project and provides creative, contextual guidance that builds on their exact words and concepts.
            """


            try:
                import openai
                client = openai.OpenAI()
                synthesis_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": synthesis_prompt}],
                    max_tokens=800,
                    temperature=0.7
                )
                synthesized_text = synthesis_response.choices[0].message.content.strip()
                # Apply simple paragraph formatting without changing content balance
                formatted_text = self._format_response_for_readability(synthesized_text)
                return formatted_text, "multi_agent_comprehensive"
            except Exception as e:
                print(f"⚠️ Synthesis failed, using fallback: {e}")
                # Fallback to better concatenation
                return f"{responses[0]}\n\n{responses[1]}", "multi_agent_comprehensive"

        elif len(responses) == 1:
            return responses[0], "multi_agent_comprehensive"
        elif cognitive_result and cognitive_result.get("response_text"):
            return cognitive_result.get("response_text", ""), "multi_agent_comprehensive"

        return (
            f"I'd be happy to provide comprehensive feedback on your approach. Your idea about {user_input.lower()[:50]}... shows thoughtful consideration. What specific aspects would you like me to focus on?",
            "multi_agent_comprehensive",
        )

    def _responses_too_similar(self, response1: str, response2: str) -> bool:
        """Check if two responses are too similar to warrant combining"""
        # Simple similarity check based on common words
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        similarity = intersection / union if union > 0 else 0

        # Consider responses too similar if >70% overlap
        return similarity > 0.7

    def _synthesize_socratic_clarification_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize comprehensive Socratic clarification response with theoretical grounding"""
        socratic_result = agent_results.get("socratic", {})
        domain_result = agent_results.get("domain", {})

        # Safety check: ensure results are dictionaries
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()

        # Extract response texts
        socratic_text = socratic_result.get("response_text", "") if socratic_result else ""
        domain_text = domain_result.get("response_text", "") if domain_result else ""

        # ENHANCED: Synthesize both responses for comprehensive clarification
        if socratic_text and domain_text:
            # Both agents provided responses - create intelligent synthesis
            try:
                synthesis_prompt = f"""
                You are synthesizing comprehensive clarification for a confused student.

                STUDENT'S CONFUSION: "{user_input}"

                SOCRATIC GUIDANCE: {socratic_text}
                DOMAIN KNOWLEDGE: {domain_text}

                Create a cohesive response that:
                1. Maintains the theoretical grounding and architectural depth from the domain knowledge
                2. Preserves the Socratic questioning approach and educational structure
                3. Combines both perspectives into a seamless, comprehensive clarification
                4. Ensures proper flow and avoids repetition
                5. Maintains professor-level architectural education quality

                Generate a unified, comprehensive clarification response:
                """

                import openai
                client = openai.OpenAI()
                synthesis_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": synthesis_prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                synthesized_text = synthesis_response.choices[0].message.content.strip() if synthesis_response.choices[0].message.content else ""
                formatted_text = self._format_response_for_readability(synthesized_text)
                return formatted_text, "socratic_clarification"
            except Exception as e:
                print(f"⚠️ Clarification synthesis failed, using fallback: {e}")
                # Fallback to domain response (more comprehensive) with socratic ending
                combined_text = f"{domain_text}\n\n{socratic_text.split('?')[-1] if '?' in socratic_text else 'What specific aspect would help you move forward?'}"
                formatted_text = self._format_response_for_readability(combined_text)
                return formatted_text, "socratic_clarification"

        # Single response handling with preference for comprehensive domain knowledge
        elif domain_text:
            formatted_text = self._format_response_for_readability(domain_text)
            return formatted_text, "socratic_clarification"
        elif socratic_text:
            formatted_text = self._format_response_for_readability(socratic_text)
            return formatted_text, "socratic_clarification"

        # Final fallback
        return (
            "Let me help clarify this concept with some theoretical grounding. What specific part would you like me to explain in more detail?",
            "socratic_clarification",
        )

    def _synthesize_supportive_scaffolding_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize supportive scaffolding response"""
        socratic_result = agent_results.get("socratic", {})
        domain_result = agent_results.get("domain", {})

        # Safety check: ensure results are dictionaries
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()

        if socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", ""), "supportive_scaffolding"
        elif domain_result and domain_result.get("response_text"):
            return domain_result.get("response_text", ""), "supportive_scaffolding"
        return (
            "I understand this can feel overwhelming. Let's break it down step by step. What's the first thing you'd like to tackle?",
            "supportive_scaffolding",
        )

    def _synthesize_foundational_building_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize foundational building response"""
        socratic_result = agent_results.get("socratic", {})
        domain_result = agent_results.get("domain", {})

        # Safety check: ensure results are dictionaries
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()

        if socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", ""), "foundational_building"
        elif domain_result and domain_result.get("response_text"):
            return domain_result.get("response_text", ""), "foundational_building"
        return (
            "Let's start with the fundamentals. What basic concepts would help you understand this better?",
            "foundational_building",
        )

    def _synthesize_knowledge_with_challenge_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        """Synthesize knowledge with challenge response"""
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})

        # Safety check: ensure results are dictionaries
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()

        # Combine knowledge with challenge
        if domain_result and socratic_result:
            domain_text = domain_result.get("response_text", "")
            socratic_text = socratic_result.get("response_text", "")
            if domain_text and socratic_text:
                # CRITICAL FIX: Use AI synthesis to create integrated educational response
                # This should weave questions throughout the content, not dump them at the end

                try:
                    import openai
                    client = openai.OpenAI()

                    synthesis_prompt = f"""
                    You are an expert architectural educator providing in-depth knowledge with integrated questioning.

                    DOMAIN KNOWLEDGE: {domain_text}
                    SOCRATIC QUESTIONS: {socratic_text}

                    Create an educational response that:
                    1. INTEGRATES QUESTIONS THROUGHOUT: Weave the socratic questions naturally within the knowledge content, not at the end
                    2. PROVIDES DEEP ARCHITECTURAL KNOWLEDGE: Include precedents, techniques, theoretical frameworks, and advanced concepts
                    3. USES EDUCATIONAL FORMATTING: Bold key concepts, italicize important terms
                    4. CREATES NATURAL PARAGRAPHS: Break into 3-4 well-structured paragraphs
                    5. MAINTAINS SCHOLARLY TONE: Write like an architecture professor teaching advanced concepts

                    FORMATTING REQUIREMENTS:
                    - Use **bold** for architectural concepts and key terms
                    - Use *italics* for emphasis and important considerations
                    - Structure in clear paragraphs with natural breaks
                    - Integrate questions within paragraphs, not as separate sections
                    - Include specific techniques, precedents, or theoretical approaches where relevant

                    Write a comprehensive educational response that teaches advanced architectural knowledge while challenging their thinking throughout.
                    """

                    synthesis_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": synthesis_prompt}],
                        max_tokens=600,
                        temperature=0.7
                    )
                    synthesized_text = synthesis_response.choices[0].message.content.strip()

                    # Apply paragraph formatting to ensure proper structure
                    formatted_text = self._format_response_for_readability(synthesized_text)
                    return formatted_text, "knowledge_with_challenge"

                except Exception as e:
                    print(f"⚠️ Knowledge synthesis failed, using enhanced fallback: {e}")
                    # Enhanced fallback with better integration
                    enhanced_domain = self._enhance_educational_formatting(domain_text)
                    formatted_domain = self._format_response_for_readability(enhanced_domain)
                    return formatted_domain, "knowledge_with_challenge"

        if domain_result and domain_result.get("response_text"):
            return domain_result.get("response_text", ""), "knowledge_with_challenge"
        elif socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", ""), "knowledge_with_challenge"
        return (
            "Here's the information you need, but let me challenge you to think deeper about how to apply it.",
            "knowledge_with_challenge",
        )

    def _synthesize_balanced_guidance_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any], state: Dict[str, Any] = None) -> tuple[str, str]:
        """Synthesize balanced guidance response using proper synthesis logic"""
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        cognitive_result = agent_results.get("cognitive", {})

        # Safety check: ensure all results are dictionaries
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()

        # Extract response texts
        domain_text = domain_result.get("response_text", "") if domain_result else ""
        socratic_text = socratic_result.get("response_text", "") if socratic_result else ""
        cognitive_text = cognitive_result.get("response_text", "") if cognitive_result else ""

        # Use synthesis shaping for balanced guidance
        try:
            from .synthesis import shape_by_route

            # For balanced_guidance, don't pre-combine texts - let synthesis template handle it
            # Pass a minimal base text and let shape_by_route use the ordered_results properly
            base_text = domain_text or socratic_text or cognitive_text or "I'd be happy to help you explore this topic. What specific aspect would you like to focus on?"

            # Apply synthesis shaping
            synthesized_response = shape_by_route(
                text=base_text,
                routing_path="balanced_guidance",
                classification=classification,
                ordered_results=agent_results,
                user_message_count=len([m for m in (state or {}).get("messages", []) if m.get("role") == "user"]),
                context_analysis=classification  # Use classification as context analysis
            )

            return synthesized_response, "balanced_guidance"

        except Exception as e:
            print(f"⚠️ Synthesis shaping failed: {e}")
            # Fallback - use synthesis template manually
            fallback_response = "Synthesis:\n- Insight: I'd be happy to help you explore this topic\n- Direction: What specific aspect would you like to focus on?\n- Watch: Consider how your design decisions will impact the user experience"
            return fallback_response, "balanced_guidance"

    def _synthesize_error_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        """Handle error routing gracefully"""
        try:
            # Try to provide a helpful response despite the error
            error_response = "I apologize, but I encountered a technical issue while processing your request. Let me try to help you with your design question.\n\n"

            # Try to extract any available agent responses
            domain_result = agent_results.get("domain", {})
            socratic_result = agent_results.get("socratic", {})

            if hasattr(domain_result, 'to_dict'):
                domain_result = domain_result.to_dict()
            if hasattr(socratic_result, 'to_dict'):
                socratic_result = socratic_result.to_dict()

            # If we have any agent responses, use them
            if domain_result and domain_result.get('response_text'):
                error_response += domain_result.get('response_text', '')
            elif socratic_result and socratic_result.get('response_text'):
                error_response += socratic_result.get('response_text', '')
            else:
                # Provide a generic helpful response based on the user input
                if any(word in user_input.lower() for word in ['circulation', 'flow', 'movement']):
                    error_response += "Regarding circulation design, consider how people will move through your space naturally. Think about main pathways, secondary routes, and how different user groups might navigate the building."
                elif any(word in user_input.lower() for word in ['layout', 'organization', 'space']):
                    error_response += "For spatial organization, consider the relationships between different functions, adjacency requirements, and how spaces can support the activities they're designed for."
                else:
                    error_response += "I'd be happy to help you explore your design question. Could you provide more details about what specific aspect you'd like to focus on?"

            return error_response, "error"

        except Exception as e:
            # Ultimate fallback
            return "I apologize, but I'm experiencing technical difficulties. Please try rephrasing your question, and I'll do my best to help.", "error"

    # ------------- Response Formatting Utilities -------------

    def _enhance_educational_formatting(self, text: str) -> str:
        """Add educational formatting with bold concepts and italic emphasis."""
        if not text or len(text) < 50:
            return text

        # Key architectural concepts that should be bold
        concepts = [
            'spatial hierarchy', 'circulation', 'program', 'zoning', 'connectivity',
            'accessibility', 'flexibility', 'adaptability', 'community engagement',
            'user experience', 'spatial narrative', 'design principles', 'building typology',
            'site context', 'materiality', 'sustainability', 'inclusivity', 'wayfinding',
            'public space', 'private space', 'semi-private', 'threshold', 'transition',
            'scale', 'proportion', 'rhythm', 'transparency', 'permeability'
        ]

        # Emphasis words that should be italic
        emphasis_words = [
            'essential', 'crucial', 'critical', 'important', 'significant', 'key',
            'fundamental', 'vital', 'particularly', 'especially', 'notably',
            'thoughtfully', 'carefully', 'strategically', 'intentionally'
        ]

        enhanced_text = text

        # Add bold formatting to architectural concepts (case-insensitive)
        import re
        for concept in concepts:
            pattern = r'\b(' + re.escape(concept) + r')\b'
            enhanced_text = re.sub(pattern, r'**\1**', enhanced_text, flags=re.IGNORECASE)

        # Add italic formatting to emphasis words (case-insensitive)
        for word in emphasis_words:
            pattern = r'\b(' + re.escape(word) + r')\b'
            enhanced_text = re.sub(pattern, r'*\1*', enhanced_text, flags=re.IGNORECASE)

        return enhanced_text

    def _format_response_for_readability(self, response_text: str) -> str:
        """Format response text for better readability with natural paragraph breaks."""
        if not response_text or len(response_text) < 150:
            return response_text

        # Split into sentences more carefully
        import re
        # Split on sentence endings but preserve the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', response_text.strip())
        if len(sentences) < 4:
            return response_text

        # Group sentences into paragraphs with natural breaks
        paragraphs = []
        current_paragraph = []

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            current_paragraph.append(sentence)

            # Create paragraph break at natural points:
            # - After 3-4 sentences
            # - After questions (if paragraph has at least 2 sentences)
            # - Before topic transitions (sentences starting with certain words)
            next_sentence = sentences[i + 1].strip() if i + 1 < len(sentences) else ""

            should_break = (
                len(current_paragraph) >= 3 or  # More frequent breaks (was 4)
                (len(current_paragraph) >= 2 and i < len(sentences) - 1) or  # More frequent breaks (was 3)
                (sentence.endswith('?') and len(current_paragraph) >= 1) or  # Break after any question (was 2)
                (next_sentence and any(next_sentence.startswith(word) for word in
                 ['Consider', 'Think', 'Reflect', 'How', 'What', 'Why', 'When', 'Where', 'By', 'This', 'Using', 'Finally', 'Additionally', 'Moreover', 'Furthermore', 'However', 'Nevertheless']))  # More transition words
            )

            if should_break and i < len(sentences) - 1:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []

        # Add remaining sentences
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))

        # Join paragraphs with double line breaks for better spacing
        return '\n\n'.join(paragraphs)

    # ------------- Metadata helpers (ported minimally) -------------

    def _build_metadata(self, response_type: str, agent_results: Dict[str, Any], routing_decision: Dict, classification: Dict, state: WorkflowState = None) -> Dict[str, Any]:
        agents_used: List[str] = []
        if agent_results.get("socratic"): agents_used.append("socratic_tutor")
        if agent_results.get("domain"): agents_used.append("domain_expert")
        if agent_results.get("analysis"): agents_used.append("analysis_agent")
        if agent_results.get("cognitive"): agents_used.append("cognitive_enhancement")

        analysis_result = agent_results.get("analysis", {})
        cognitive_result = agent_results.get("cognitive", {})
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        
        # Safety check: ensure all results are dictionaries
        if hasattr(analysis_result, 'to_dict'):
            analysis_result = analysis_result.to_dict()
        if hasattr(cognitive_result, 'to_dict'):
            cognitive_result = cognitive_result.to_dict()
        if hasattr(domain_result, 'to_dict'):
            domain_result = domain_result.to_dict()
        if hasattr(socratic_result, 'to_dict'):
            socratic_result = socratic_result.to_dict()

        # Extract enhancement metrics from all agents
        enhancement_metrics = {}

        # Get metrics from cognitive enhancement agent
        if cognitive_result and hasattr(cognitive_result, 'enhancement_metrics'):
            metrics = cognitive_result.enhancement_metrics
            enhancement_metrics.update({
                "cognitive_offloading_prevention_score": getattr(metrics, 'cognitive_offloading_prevention_score', 0),
                "deep_thinking_engagement_score": getattr(metrics, 'deep_thinking_engagement_score', 0),
                "knowledge_integration_score": getattr(metrics, 'knowledge_integration_score', 0),
                "scaffolding_effectiveness_score": getattr(metrics, 'scaffolding_effectiveness_score', 0),
                "learning_progression_score": getattr(metrics, 'learning_progression_score', 0),
                "metacognitive_awareness_score": getattr(metrics, 'metacognitive_awareness_score', 0),
                "overall_cognitive_score": getattr(metrics, 'overall_cognitive_score', 0),
                "scientific_confidence": getattr(metrics, 'scientific_confidence', 0)
            })

        # Get metrics from socratic tutor
        if socratic_result and hasattr(socratic_result, 'enhancement_metrics'):
            metrics = socratic_result.enhancement_metrics
            enhancement_metrics.update({
                "socratic_deep_thinking_score": getattr(metrics, 'deep_thinking_engagement_score', 0),
                "socratic_scaffolding_score": getattr(metrics, 'scaffolding_effectiveness_score', 0),
                "socratic_metacognitive_score": getattr(metrics, 'metacognitive_awareness_score', 0)
            })

        # Extract phase information
        phase_info = {}
        if analysis_result and hasattr(analysis_result, 'phase_assessment'):
            phase_assessment = analysis_result.phase_assessment
            phase_info = {
                "current_phase": getattr(phase_assessment, 'current_phase', 'ideation'),
                "phase_confidence": getattr(phase_assessment, 'phase_confidence', 0),
                "progression_score": getattr(phase_assessment, 'progression_score', 0),
                "next_phase": getattr(phase_assessment, 'next_phase', None)
            }
        else:
            # Generate phase analysis using the phase manager
            try:
                from phase_assessment.phase_manager import PhaseAssessmentManager
                phase_manager = PhaseAssessmentManager()
                
                # ENHANCED: Use phase info from dashboard if available, otherwise detect
                if state and 'student_state' in state and state['student_state'] and hasattr(state['student_state'], 'phase_info') and state['student_state'].phase_info:
                    # Use phase information from dashboard's phase progression system
                    dashboard_phase_info = state['student_state'].phase_info
                    current_phase_name = dashboard_phase_info.get("current_phase", "ideation")
                    print(f"🎯 Phase detection: Using dashboard phase info: {current_phase_name}")

                    # Map phase progress to step progression
                    phase_progress = dashboard_phase_info.get("phase_progress", {})
                    current_phase_progress = phase_progress.get(current_phase_name, {})
                    completion_percent = current_phase_progress.get("completion_percent", 0.0)

                    # DEBUG: PRINT REMOVED
                    #print(f"🔍 ORCHESTRATOR DEBUG: Phase progress data: {phase_progress}")
                    #print(f"🔍 ORCHESTRATOR DEBUG: Current phase progress: {current_phase_progress}")
                    #print(f"🔍 ORCHESTRATOR DEBUG: Completion percent: {completion_percent}")

                    # Estimate step based on completion
                    if completion_percent < 25:
                        current_step_name = "initial_context_reasoning"
                        prog = 0.25
                    elif completion_percent < 50:
                        current_step_name = "knowledge_synthesis_trigger"
                        prog = 0.5
                    elif completion_percent < 75:
                        current_step_name = "socratic_questioning"
                        prog = 0.75
                    else:
                        current_step_name = "metacognitive_prompt"
                        prog = 1.0

                    confidence = max(0.7, min(0.95, completion_percent / 100.0))

                    phase_info = {
                        "phase": current_phase_name,
                        "step": current_step_name,
                        "confidence": confidence,
                        "progression_score": prog,
                        "completion_percent": completion_percent,
                        # Back-compat keys
                        "current_phase": current_phase_name,
                        "current_step": current_step_name,
                        "phase_confidence": confidence,
                        "next_phase": None,
                    }
                elif state and 'student_state' in state and state['student_state']:
                    # Fallback to phase detection if no dashboard info available
                    student_state = state['student_state']
                    messages = getattr(student_state, 'messages', [])
                    print(f"🔍 Phase detection: Using student state with {len(messages)} messages")
                    current_phase, current_step = phase_manager.detect_current_phase(student_state)
                    print(f"🎯 Phase detection result: {current_phase.value} - {current_step.value}")
                    #1108 tracking: Phase detection (real tracking): compute early and attach to analysis_result
                    # Map step to a 0-1 progression within the current phase
                    step_progress_map = {
                        "initial_context_reasoning": 0.25,
                        "knowledge_synthesis_trigger": 0.5,
                        "socratic_questioning": 0.75,
                        "metacognitive_prompt": 1.0,
                    }
                    prog = step_progress_map.get(getattr(current_step, 'value', ''), 0.25)

                    # Heuristic confidence: grows with messages and later steps
                    user_msg_count = len([m for m in getattr(student_state, 'messages', []) if m.get('role') == 'user'])
                    confidence = max(0.5, min(0.95, 0.5 + (user_msg_count / 20.0) + (prog - 0.25) / 2))

                    # Provide both legacy and logger-expected keys
                    phase_info = {
                        "phase": current_phase.value,
                        "step": current_step.value,
                        "confidence": confidence,
                        "progression_score": prog,
                        # Back-compat keys
                        "current_phase": current_phase.value,
                        "current_step": current_step.value,
                        "phase_confidence": confidence,
                        "next_phase": None,
                    }
                else:
                    print(f"⚠️ Phase detection: No student state available, using fallback")
                    # Fallback phase info (use logger-expected keys too)
                    phase_info = {
                        "phase": "ideation",
                        "step": "initial_context_reasoning",
                        "confidence": 0.7,
                        "progression_score": 0.25,
                        # Back-compat keys
                        "current_phase": "ideation",
                        "current_step": "initial_context_reasoning",
                        "phase_confidence": 0.7,
                        "next_phase": None,
                    }
            except Exception as e:
                print(f"⚠️ Phase detection failed: {e}")
                # Fallback phase info
                phase_info = {
                    "phase": "ideation",
                    "step": "initial_context_reasoning",
                    "confidence": 0.6,
                    "progression_score": 0.25,
                    # Back-compat keys
                    "current_phase": "ideation",
                    "current_step": "initial_context_reasoning",
                    "phase_confidence": 0.6,
                    "next_phase": None,
                }

        # ENHANCED: Extract gamification metadata from cognitive enhancement agent
        gamification_metadata = {}

        # Handle both AgentResponse objects and dict results
        if cognitive_result:
            # If it's an AgentResponse object, access metadata directly
            if hasattr(cognitive_result, 'metadata') and cognitive_result.metadata:
                if 'gamification_display' in cognitive_result.metadata:
                    gamification_metadata = cognitive_result.metadata['gamification_display']
                    
                    #print(f"🎮 ORCHESTRATOR: Found gamification metadata from AgentResponse: {gamification_metadata}")
            # If it's a dict, use the old method
            elif isinstance(cognitive_result, dict) and cognitive_result.get("metadata", {}).get("gamification_display"):
                gamification_metadata = cognitive_result.get("metadata", {}).get("gamification_display", {})
                #print(f"🎮 ORCHESTRATOR: Found gamification metadata from dict: {gamification_metadata}")

        # Also check routing decision for gamification triggers
        detailed_routing = routing_decision.get("detailed_routing_decision", {}) or state.get("detailed_routing_decision", {}) if state else {}
        gamification_triggers = detailed_routing.get("metadata", {}).get("gamification_triggers", [])
        if gamification_triggers:
            #print(f"🎮 ORCHESTRATOR: Found gamification triggers: {gamification_triggers}")
            if not gamification_metadata:
                # Create gamification metadata from triggers
                gamification_metadata = {
                    "is_gamified": True,
                    "trigger_type": gamification_triggers[0] if gamification_triggers else "unknown",
                    "display_type": "enhanced_visual",
                    "challenge_data": {"triggers": gamification_triggers}
                }

        return {
            "response_type": response_type,
            "agents_used": agents_used,
            "routing_path": routing_decision.get("path", "unknown"),
            "ai_reasoning": routing_decision.get("reasoning", "No AI reasoning available"),
            "phase_analysis": phase_info,
            "enhancement_metrics": enhancement_metrics,
            # FIXED: Extract scientific metrics and cognitive state from metadata (handle AgentResponse objects)
            "scientific_metrics": (
                cognitive_result.metadata.get("scientific_metrics", {}) if hasattr(cognitive_result, 'metadata') and cognitive_result.metadata
                else cognitive_result.get("metadata", {}).get("scientific_metrics", cognitive_result.get("scientific_metrics", {})) if isinstance(cognitive_result, dict)
                else {}
            ),
            "cognitive_state": (
                cognitive_result.metadata.get("cognitive_state", {}) if hasattr(cognitive_result, 'metadata') and cognitive_result.metadata
                else cognitive_result.get("metadata", {}).get("cognitive_state", cognitive_result.get("cognitive_state", {})) if isinstance(cognitive_result, dict)
                else {}
            ),
            "analysis_result": analysis_result,
            "sources": domain_result.get("sources", []) if domain_result else [],
            "processing_time": "N/A",
            "classification": classification,
            # Add explicit interaction_type and user_intent for routing display
            "interaction_type": classification.get("interaction_type") or classification.get("user_intent", "unknown"),
            "user_intent": classification.get("user_intent") or classification.get("interaction_type", "unknown"),
            # ENHANCED: Include gamification metadata
            "gamification_display": gamification_metadata,
            "gamification": gamification_metadata  # Also include under 'gamification' key for compatibility

        }

    # expose ensure_quality used by nodes.synthesizer via synthesis.build_synthesizer binding
    @staticmethod
    def ensure_quality(text: str, agent_type: str) -> str:
        try:
            from utils.response_length_controller import ensure_quality as eq
            return eq(text, agent_type)
        except Exception:
            return text

    # Main entrypoint mirrors legacy behavior
    async def process_student_input(self, student_state) -> Dict[str, Any]:
        import time
        start_time = time.time()

        # Get user input first
        user_messages = [m for m in student_state.messages if m.get("role") == "user"]

        print(f"\n🎯 ORCHESTRATOR: process_student_input called")
        print(f"   User messages count: {len(user_messages)}")
        print(f"   Phase info available: {hasattr(student_state, 'phase_info') and student_state.phase_info is not None}")
        if hasattr(student_state, 'phase_info') and student_state.phase_info:
            print(f"   Current phase from state: {student_state.phase_info.get('current_phase', 'unknown')}")

        # Debug: Check the latest user message for image analysis
        if user_messages:
            latest_user_input = user_messages[-1].get("content", "")
            print(f"🔍 ORCHESTRATOR: Latest user input length: {len(latest_user_input)} chars")
            print(f"🔍 ORCHESTRATOR: Latest user input preview: {latest_user_input[:200]}...")
            has_enhanced = "[ENHANCED IMAGE ANALYSIS:" in latest_user_input
            has_uploaded = "[UPLOADED IMAGE ANALYSIS:" in latest_user_input
            print(f"🔍 ORCHESTRATOR: Has ENHANCED marker in input: {has_enhanced}")
            print(f"🔍 ORCHESTRATOR: Has UPLOADED marker in input: {has_uploaded}")
        print(f"   Last user message: {user_messages[-1] if user_messages else 'No messages'}...")
        current_user_input = user_messages[-1]["content"] if user_messages else ""

        print(f"\n🚀 ArchMentor Processing Pipeline Started")
        print(f"   📝 User input: {current_user_input[:100]}..." if len(current_user_input) > 100 else f"   📝 User input: {current_user_input}")
        print(f"   🏗️ Project: {getattr(student_state, 'current_design_brief', 'No brief set')}")
        student_profile = getattr(student_state, 'student_profile', None)
        skill_level = getattr(student_profile, 'skill_level', 'unknown') if student_profile else 'unknown'
        print(f"   👤 Student profile: {skill_level} level")

        self.logger.info("Starting workflow...")

        # Ensure brief is placed if needed
        if hasattr(student_state, "ensure_brief_in_messages") and student_state.ensure_brief_in_messages():
            if not any(m.get("role") == "brief" for m in student_state.messages):
                student_state.messages.insert(0, {"role": "brief", "content": getattr(student_state, "current_design_brief", "")})
                print(f"   📋 Design brief added to conversation context")

        # Progression
        self.progression_manager.update_state(student_state)
        milestone_guidance = self.progression_manager.get_milestone_driven_agent_guidance(current_user_input, student_state)
        if len(user_messages) == 1:
            progression_analysis = self.progression_manager.analyze_first_message(current_user_input, student_state)
        else:
            last_assistant_message = next((m.get("content", "") for m in reversed(student_state.messages) if m.get("role") == "assistant"), "")
            _ = self.progression_manager.assess_milestone_completion(current_user_input, last_assistant_message, student_state)
            progression_analysis = self.progression_manager.progress_conversation(current_user_input, last_assistant_message, student_state)

        initial_state: WorkflowState = WorkflowState(
            student_state=student_state,
            last_message=current_user_input,
            student_classification={},
            context_analysis={},
            routing_decision={},
            analysis_result={},
            domain_expert_result={},
            socratic_result={},
            cognitive_enhancement_result={},
            final_response="",
            response_metadata={},
            conversation_progression=progression_analysis,
            milestone_guidance=milestone_guidance,
        )

        print(f"\n🔄 Processing through agent workflow...")
        final_state = await self.workflow.ainvoke(initial_state)

        processing_time = time.time() - start_time
        self.logger.info(f"Workflow completed in {processing_time:.2f}s")

        # Enhanced Process Summary
        user_input_text = initial_state.get('user_input', 'Unknown input')
        self._print_enhanced_process_summary(final_state, processing_time, user_input_text)

        if "response_metadata" in final_state:
            final_state["response_metadata"]["processing_time"] = f"{processing_time:.2f}s"
            final_state["response_metadata"]["conversation_progression"] = progression_analysis
            final_state["response_metadata"]["milestone_guidance"] = milestone_guidance

        # Optional console summary like legacy implementation
        try:
            self._print_user_requested_info(final_state)
        except Exception:
            pass

        # CRITICAL FIX: Extract gamification metadata from response_metadata and add to top level
        response_metadata = final_state.get("response_metadata", {})
        gamification_metadata = response_metadata.get("gamification", {})

        final_response = final_state.get("final_response", "")

        # Debug the final response
        print(f"🔍 ORCHESTRATOR: Final response length: {len(final_response)}")
        print(f"🔍 ORCHESTRATOR: Final response preview: {final_response[:200]}...")

        # Check if image discussion is in final response
        if "Looking at your image, I can see" in final_response:
            print(f"✅ ORCHESTRATOR: Image discussion found in final response!")
        else:
            print(f"❌ ORCHESTRATOR: No image discussion found in final response")

        return {
            "response": final_response,
            "metadata": response_metadata,
            "routing_path": final_state.get("routing_decision", {}).get("path", "unknown"),
            "classification": final_state.get("student_classification", {}),
            "conversation_progression": progression_analysis,
            "milestone_guidance": milestone_guidance,
            # CRITICAL FIX: Add gamification metadata to top level for UI access
            "gamification": gamification_metadata,
            "gamification_display": gamification_metadata,  # Also add as gamification_display for compatibility
        }

    def _print_enhanced_process_summary(self, final_state: Dict, processing_time: float, user_input: str):
        """Print an enhanced, clean process summary."""
        print(f"\n{'='*80}")
        print(f"🎯 ORCHESTRATION SUMMARY")
        print(f"{'='*80}")

        # Input summary
        input_preview = user_input[:60] + "..." if len(user_input) > 60 else user_input
        print(f"📝 Input: {input_preview}")

        # Routing information
        routing_decision = final_state.get('routing_decision', {})
        routing_path = routing_decision.get('path', 'unknown')
        print(f"🛤️  Route: {routing_path}")

        # Agents activated
        agents_used = []
        if final_state.get("analysis_result"): agents_used.append("Analysis")
        if final_state.get("domain_expert_result"): agents_used.append("Domain Expert")
        if final_state.get("socratic_result"): agents_used.append("Socratic Tutor")
        if final_state.get("cognitive_enhancement_result"): agents_used.append("Cognitive Enhancement")

        print(f"🤖 Agents: {', '.join(agents_used) if agents_used else 'None'}")

        # Response information
        response_length = len(final_state.get('final_response', ''))
        print(f"📊 Response: {response_length} characters")

        # Classification information
        classification = final_state.get('student_classification', {})
        if classification:
            intent = classification.get('interaction_type') or classification.get('user_intent', 'unknown')
            print(f"🎯 Intent: {intent}")

        # Gamification information
        metadata = final_state.get('response_metadata', {})
        gamification_info = metadata.get('gamification', {})
        if gamification_info.get('trigger_type'):
            trigger = gamification_info.get('trigger_type')
            enhanced = "✨ Enhanced" if gamification_info.get('enhancement_applied') else "🎯 Detected"
            print(f"🎮 Gamification: {enhanced} - {trigger}")

        # Performance
        print(f"⏱️  Processing: {processing_time:.2f}s")

        # Scientific metrics if available
        scientific_metrics = metadata.get('scientific_metrics', {})
        if scientific_metrics and scientific_metrics.get('overall_cognitive_score', 0) > 0:
            cognitive_score = scientific_metrics.get('overall_cognitive_score', 0)
            confidence = scientific_metrics.get('scientific_confidence', 0)
            print(f"🧠 Cognitive Score: {cognitive_score:.2f} (confidence: {confidence:.2f})")

        print(f"{'='*80}")
        print(f"✅ Processing completed successfully")
        print(f"{'='*80}\n")

    def _print_user_requested_info(self, final_state: Dict[str, Any]) -> None:
        routing_path = final_state.get("routing_decision", {}).get("path", "unknown")
        classification = final_state.get("student_classification", {})
        response_type = final_state.get("response_metadata", {}).get("response_type", "unknown")
        ai_reasoning = final_state.get("response_metadata", {}).get("ai_reasoning", "No AI reasoning available")

        print("\n" + "─" * 50)
        print("📋 PROCESS SUMMARY")
        print("─" * 50)
        print(f"🛣️  Route: {routing_path}")
        print(f"💬 Interaction Type: {classification.get('interaction_type', 'unknown')}")
        print(f"📝 Response Type: {response_type}")
        print(f"🤖 AI Reasoning: {ai_reasoning[:100]}{'...' if len(ai_reasoning) > 100 else ''}")
        print("─" * 50)

        print("\n⚡ PROCESS OVERVIEW:")
        agents_used = []
        if final_state.get("analysis_result"): agents_used.append("Analysis")
        if final_state.get("domain_expert_result"): agents_used.append("Domain Expert")
        if final_state.get("socratic_result"): agents_used.append("Socratic Tutor")
        if final_state.get("cognitive_enhancement_result"): agents_used.append("Cognitive Enhancement")

        print(f"🤖 Agents activated: {', '.join(agents_used) if agents_used else 'None'}")

        # Show scientific metrics if available
        if final_state.get("response_metadata", {}).get("enhancement_metrics"):
            metrics = final_state["response_metadata"]["enhancement_metrics"]
            print(f"\n📊 COGNITIVE ENHANCEMENT METRICS:")
            print(f"   🧠 Critical Thinking Score: {metrics.get('critical_thinking_score', 0):.2f}")
            print(f"   🏗️ Scaffolding Effectiveness: {metrics.get('scaffolding_effectiveness_score', 0):.2f}")
            print(f"   💡 Engagement Maintenance: {metrics.get('engagement_maintenance_score', 0):.2f}")
            print(f"   🎯 Metacognitive Awareness: {metrics.get('metacognitive_awareness_score', 0):.2f}")
            print(f"   📈 Overall Cognitive Score: {metrics.get('overall_cognitive_score', 0):.2f}")
            print(f"   🔬 Scientific Confidence: {metrics.get('scientific_confidence', 0):.2f}")

        # Show conversation analysis if available
        analysis_result = final_state.get("analysis_result", {})
        if hasattr(analysis_result, 'to_dict'):
            analysis_result = analysis_result.to_dict()
        
        if analysis_result and analysis_result.get("conversation_patterns"):
            patterns = analysis_result["conversation_patterns"]
            print(f"\n🔍 CONVERSATION ANALYSIS:")
            print(f"   📈 Engagement Trend: {patterns.get('engagement_trend', 'unknown')}")
            print(f"   🎓 Understanding Progression: {patterns.get('understanding_progression', 'unknown')}")
            print(f"   🔄 Conversation Depth: {patterns.get('conversation_depth', {}).get('overall_depth', 'unknown')}")
            print(f"   🎯 Recent Focus: {', '.join(patterns.get('recent_focus', [])[:3])}")

        # Show data collection status
        print(f"\n💾 DATA COLLECTION:")
        print(f"   📝 Interaction logged for thesis analysis")
        print(f"   📊 Scientific metrics captured")
        print(f"   🔬 Benchmarking data available for export")
        print(f"   Agents used: {', '.join(agents_used) if agents_used else 'None'}")
        print(f"   Processing time: {final_state.get('response_metadata', {}).get('processing_time', 'N/A')}")
        print("─" * 50 + "\n")

    # ---------------- Legacy helpers preserved for API compatibility ----------------

    def classify_student_input(self, message: str, student_state: Any) -> Dict[str, Any]:
        if not message:
            return {"classification": "initial", "understanding": "unknown", "confidence": "medium", "engagement": "medium"}
        message_lower = message.lower()
        overconfidence_words = ["obviously", "clearly", "definitely", "perfect", "best", "optimal", "ideal", "flawless"]
        absolute_patterns = ["this is the", "this will", "my design is", "the solution is", "it's clear that"]
        overconfidence_score = sum(1 for w in overconfidence_words if w in message_lower) + sum(1 for p in absolute_patterns if p in message_lower)
        feedback_patterns = [
            "review my", "feedback on", "thoughts on", "critique", "evaluate",
            "what do you think", "how does this look", "check my design", "can you review",
            "analyze my plan", "analyze my design", "look at my", "thoughts about my",
            "how can i improve", "can you help me improve", "improve the", "improve my",
        ]
        is_feedback_request = any(p in message_lower for p in feedback_patterns)
        technical_patterns = ["what are the", "what is the", "requirements for", "ada requirements", "building codes", "standards for", "guidelines", "regulations"]
        is_technical_question = any(p in message_lower for p in technical_patterns)
        example_patterns = ["example", "examples", "precedent", "precedents", "case study", "case studies", "project", "projects", "reference", "references"]
        is_example_request = any(p in message_lower for p in example_patterns) and "?" in message_lower
        confusion_words = ["confused", "don't understand", "unclear", "help", "lost", "stuck"]
        confusion_score = sum(1 for w in confusion_words if w in message_lower)
        socratic_clarification_patterns = ["what do you mean", "can you explain", "why did you ask", "why are you asking", "what's the point of", "what is the point of"]
        is_socratic_clarification = any(p in message_lower for p in socratic_clarification_patterns)
        technical_terms = ["accessibility", "circulation", "programming", "design", "community", "building"]
        tech_usage = sum(1 for t in technical_terms if t in message_lower)
        understanding = "high" if tech_usage >= 2 else ("medium" if tech_usage >= 1 else "low")
        if overconfidence_score >= 1:
            confidence = "overconfident"
        elif any(w in message_lower for w in ["think", "maybe", "might"]):
            confidence = "confident"
        else:
            confidence = "uncertain"
        word_count = len(message.split())
        engagement = "high" if word_count > 10 else ("medium" if word_count > 5 else "low")
        if is_feedback_request:
            interaction_type = "design_feedback_request"
        elif is_example_request:
            interaction_type = "example_request"
        elif is_technical_question:
            interaction_type = "technical_question"
        elif confusion_score > 0:
            interaction_type = "confusion_expression"
        elif "?" in message:
            interaction_type = "question"
        else:
            interaction_type = "statement"
        return {
            "classification": interaction_type,
            "understanding_level": understanding,
            "confidence_level": confidence,
            "engagement_level": engagement,
            "confusion_score": confusion_score,
            "overconfidence_score": overconfidence_score,
            "word_count": word_count,
            "technical_usage": tech_usage,
            "is_technical_question": is_technical_question,
            "is_feedback_request": is_feedback_request,
            "is_example_request": is_example_request,
            "is_socratic_clarification": is_socratic_clarification,
        }

    # Removed unused legacy determine_routing method (routing handled by AdvancedRoutingDecisionTree)

    # Removed unused legacy _check_conversation_thread helper (handled by advanced router logic)

    async def execute_agent_sequence(self, state: WorkflowState) -> WorkflowState:
        routing = state.get("routing_decision", {})
        path = routing.get("path", "default")
        agents_to_activate = routing.get("agents_to_activate", [])
        self.logger.info(f"Executing {path} with agents: {agents_to_activate}")
        if path == "knowledge_only":
            state = await self.handlers.domain_expert(state)
        elif path == "socratic_focus":
            state = await self.handlers.socratic(state)
            if "cognitive_enhancement" in agents_to_activate:
                cognitive_state = await self.handlers.cognitive(state)
                state["cognitive_support_result"] = cognitive_state.get("cognitive_enhancement_result")
        elif path == "cognitive_challenge":
            state = await self.handlers.cognitive(state)
            if "socratic_tutor" in agents_to_activate:
                soc_state = await self.handlers.socratic(state)
                state["socratic_followup_result"] = soc_state.get("socratic_result")
        elif path == "multi_agent":
            state = await self.handlers.domain_expert(state)
            state = await self.handlers.socratic(state)
            state = await self.handlers.cognitive(state)
        else:
            state = await self.handlers.domain_expert(state)
            state = await self.handlers.socratic(state)
        return state

    def _detect_cognitive_offloading(self, classification: Dict[str, Any], context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {"detected": False, "type": None, "confidence": 0.0, "indicators": []}

        # FIXED: Expand premature answer seeking detection to include direct_answer_request
        interaction_type = classification.get("interaction_type")
        if interaction_type in ["feedback_request", "direct_answer_request"]:
            recent_messages = context_analysis.get("conversation_patterns", {}).get("recent_messages", [])
            if len(recent_messages) < 6:
                indicators.update({"detected": True, "type": "premature_answer_seeking", "confidence": 0.8})
                indicators["indicators"].append(f"Asking for answers before exploration (type: {interaction_type})")
        if (classification.get("confidence_level") == "overconfident" and classification.get("engagement_level") == "low"):
            indicators.update({"detected": True, "type": "superficial_confidence", "confidence": 0.7})
            indicators["indicators"].append("Overconfident but not engaged")
        patterns = context_analysis.get("conversation_patterns", {})
        if patterns.get("repetitive_topics", False):
            if classification.get("interaction_type", "") != "question_response":
                user_input = classification.get("last_message", "").lower()
                if not any(word in user_input for word in ["circulation", "lighting", "structure", "materials", "program", "context"]):
                    indicators.update({"detected": True, "type": "repetitive_dependency", "confidence": 0.6})
                    indicators["indicators"].append("Repeating same questions")
        return indicators

    def _detect_topic_transition(self, student_state: Any, current_message: str) -> Optional[str]:
        recent_messages = student_state.messages[-3:] if len(student_state.messages) >= 3 else student_state.messages
        recent_topics: List[str] = []
        for msg in recent_messages:
            if msg.get('role') == 'user':
                topics = self._extract_topics_from_message(msg['content'])
                recent_topics.extend(topics)
        current_topics = self._extract_topics_from_message(current_message)
        new_topics = [t for t in current_topics if t not in recent_topics]
        transition_indicators = ["what about", "how about", "let's talk about", "i want to discuss", "can we explore", "i'm interested in", "tell me about", "what if", "another thing", "different topic", "switch to", "move on to"]
        has_transition_indicator = any(ind in current_message.lower() for ind in transition_indicators)
        if new_topics and (has_transition_indicator or len(new_topics) > 1):
            return new_topics[0]
        return None

    def _extract_topics_from_message(self, message: str) -> List[str]:
        topics: List[str] = []
        message_lower = message.lower()
        topic_keywords = {
            "residential": ["house", "home", "apartment", "residential", "living", "dwelling"],
            "commercial": ["office", "commercial", "retail", "business", "workplace", "corporate"],
            "cultural": ["museum", "theater", "gallery", "cultural", "arts", "performance"],
            "educational": ["school", "university", "education", "learning", "classroom", "academic"],
            "healthcare": ["hospital", "clinic", "healthcare", "medical", "health"],
            "sustainability": ["sustainable", "green", "environmental", "eco", "climate"],
            "urban": ["urban", "city", "public", "street", "neighborhood", "public space"],
            "interior": ["interior", "furniture", "furnishing", "decoration", "inside"],
            "structure": ["structure", "construction", "building", "system", "engineering"],
            "design_process": ["design", "process", "methodology", "approach", "thinking"],
        }
        for topic, keywords in topic_keywords.items():
            if any(k in message_lower for k in keywords):
                topics.append(topic)
        return topics

    def _print_summary_if_enabled(self, state: WorkflowState, response_type: str, metadata: Dict[str, Any]) -> None:
        student_state = state.get("student_state", {})
        if hasattr(student_state, 'show_response_summary') and student_state.show_response_summary:
            self._print_response_summary(
                user_input=state.get("last_message", ""),
                response_type=response_type,
                agents_used=metadata.get("agents_used", []),
                routing_path=metadata.get("routing_path", "unknown"),
                classification=metadata.get("classification", {}),
                phase_analysis=metadata.get("phase_analysis", {}),
                cognitive_state=metadata.get("cognitive_state", {}),
                sources=metadata.get("sources", []),
            )

    def _print_response_summary(self, user_input: str, response_type: str, agents_used: List[str], routing_path: str, classification: Dict[str, Any], phase_analysis: Dict[str, Any], cognitive_state: Dict[str, Any], sources: List[str]) -> None:
        self.logger.info("\n" + "=" * 80)
        self.logger.info("RESPONSE PROCESSING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"USER INPUT: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        self.logger.info(f"Path: {routing_path} | Type: {response_type} | Agents: {', '.join(agents_used) if agents_used else 'None'}")
        if phase_analysis:
            self.logger.info(f"Phase: {phase_analysis.get('phase', 'unknown')} | Confidence: {phase_analysis.get('confidence', 0):.1%}")
        if cognitive_state:
            self.logger.info(f"Cognitive: {cognitive_state}")
        if sources:
            self.logger.info(f"Sources: {sources[:3]}")
        self.logger.info("=" * 80 + "\n")

    def _enhance_response_with_image_discussion(self, response: str, user_input: str) -> str:
        """FIXED: Re-enable image enhancement to properly handle uploaded images."""
        # Check if user input contains image analysis markers
        if "[ENHANCED IMAGE ANALYSIS:" in user_input or "[UPLOADED IMAGE ANALYSIS:" in user_input:
            self.logger.info("✅ IMAGE ENHANCEMENT: Image analysis found in user input")
            # The image analysis is already embedded in the user input, so the response should naturally reference it
            return response
        else:
            self.logger.info("ℹ️ IMAGE ENHANCEMENT: No image analysis markers found")
            return response

    def _should_auto_reference_image(self, user_input: str) -> bool:
        """Check if we should automatically reference the image in the response."""
        try:
            # Initialize image reference tracking in session state if not exists
            # This ensures the counter persists across orchestrator instances
            try:
                import streamlit as st
                if 'image_reference_count' not in st.session_state:
                    st.session_state.image_reference_count = {}
                image_reference_count = st.session_state.image_reference_count
            except ImportError:
                # Fallback to instance variable if streamlit not available (for testing)
                if not hasattr(self, '_image_reference_count'):
                    self._image_reference_count = {}
                image_reference_count = self._image_reference_count

            # Extract image analysis to get a unique identifier
            image_analysis = ""
            if "[ENHANCED IMAGE ANALYSIS:" in user_input:
                start = user_input.find("[ENHANCED IMAGE ANALYSIS:")
                # Look for the end of the image analysis section (usually ends with "]")
                # But also handle cases where it might end differently
                remaining_text = user_input[start:]
                if "]" in remaining_text:
                    end_pos = remaining_text.find("]") + 1
                    image_analysis = remaining_text[:end_pos]
                else:
                    # If no closing bracket, take the whole remaining text
                    image_analysis = remaining_text
            elif "[UPLOADED IMAGE ANALYSIS:" in user_input:
                start = user_input.find("[UPLOADED IMAGE ANALYSIS:")
                remaining_text = user_input[start:]
                if "]" in remaining_text:
                    end_pos = remaining_text.find("]") + 1
                    image_analysis = remaining_text[:end_pos]
                else:
                    image_analysis = remaining_text

            if not image_analysis:
                self.logger.info(f"🖼️ IMAGE REFERENCE: No image analysis found in user input")
                return False

            self.logger.info(f"🖼️ IMAGE REFERENCE: Extracted image analysis: {image_analysis[:100]}...")

            # Create a simple hash for tracking - use a consistent identifier
            # Extract image path from session state if available for consistent hashing
            import hashlib
            image_identifier = image_analysis[:200]  # Use first 200 chars of analysis as identifier
            image_hash = hashlib.md5(image_identifier.encode()).hexdigest()[:8]

            # Check if user is explicitly asking about the image
            # Only check the user message part, not the image analysis part
            # Use more specific phrases that clearly indicate user is asking about the image
            explicit_image_phrases = [
                'in the image', 'in this image', 'from the image', 'about the image',
                'in the picture', 'in this picture', 'from the picture', 'about the picture',
                'in the drawing', 'in this drawing', 'from the drawing', 'about the drawing',
                'what do you see', 'what can you see', 'tell me about the',
                'describe the image', 'describe the picture', 'describe the drawing',
                'analyze the image', 'analyze the picture', 'analyze the drawing'
            ]

            # Extract just the user message (before the image analysis)
            if "[ENHANCED IMAGE ANALYSIS:" in user_input:
                user_message_only = user_input.split("[ENHANCED IMAGE ANALYSIS:")[0].strip()
            elif "[UPLOADED IMAGE ANALYSIS:" in user_input:
                user_message_only = user_input.split("[UPLOADED IMAGE ANALYSIS:")[0].strip()
            else:
                user_message_only = user_input

            user_text = user_message_only.lower()
            user_explicitly_asks_about_image = any(phrase in user_text for phrase in explicit_image_phrases)
            self.logger.info(f"🖼️ IMAGE REFERENCE: User message only: '{user_message_only}' - explicitly asks about image: {user_explicitly_asks_about_image}")

            # If user explicitly asks about the image, always reference it (bypasses counter)
            if user_explicitly_asks_about_image:
                self.logger.info(f"🖼️ IMAGE REFERENCE: User explicitly asked about image, allowing reference (bypasses counter)")
                return True

            # AGGRESSIVE FIX: Always return False after 2 messages to stop "Looking at your image"
            # This is the most direct way to stop the persistent image references
            try:
                import streamlit as st
                # Check if dashboard has already determined we should stop bundling
                if hasattr(st.session_state, 'last_image_upload_message_count') and hasattr(st.session_state, 'messages'):
                    current_message_count = len(st.session_state.messages)
                    messages_since_upload = current_message_count - st.session_state.last_image_upload_message_count

                    self.logger.info(f"🖼️ IMAGE REFERENCE: Dashboard sync - messages since upload: {messages_since_upload}")

                    # STRICT LIMIT: Only allow for first 2 messages, then NEVER again
                    if messages_since_upload >= 2:
                        self.logger.info(f"� IMAGE REFERENCE: BLOCKED - limit reached ({messages_since_upload}/2)")
                        return False
                    else:
                        self.logger.info(f"✅ IMAGE REFERENCE: ALLOWED ({messages_since_upload}/2)")
                        return True
                else:
                    # Even in fallback, be strict about the limit
                    current_count = image_reference_count.get(image_hash, 0)
                    self.logger.info(f"🖼️ IMAGE REFERENCE: Fallback tracking: {current_count}/2")

                    if current_count >= 2:
                        self.logger.info(f"� IMAGE REFERENCE: BLOCKED - fallback limit reached ({current_count}/2)")
                        return False
                    else:
                        image_reference_count[image_hash] = current_count + 1
                        self.logger.info(f"✅ IMAGE REFERENCE: ALLOWED - fallback ({current_count + 1}/2)")
                        return True
            except ImportError:
                # Even in non-streamlit, be strict
                current_count = image_reference_count.get(image_hash, 0)
                if current_count >= 2:
                    return False
                else:
                    image_reference_count[image_hash] = current_count + 1
                    return True

        except Exception as e:
            self.logger.error(f"Error checking image reference policy: {e}")
            # Default to allowing reference on error
            return True

    def _enhance_knowledge_response_with_questions(self, response_text: str, user_input: str, classification: Dict[str, Any]) -> str:
        """Enhance knowledge-only responses with thoughtful questions that provoke deeper thinking."""

        # Check if response already has questions
        if '?' in response_text:
            return response_text

        try:
            # Generate contextual follow-up question based on the content provided
            prompt = f"""
You are an expert architectural mentor. You just provided this knowledge to a student:

KNOWLEDGE PROVIDED: "{response_text}"

STUDENT'S ORIGINAL QUESTION: "{user_input}"

Generate ONE thoughtful follow-up question that:
1. Builds on the knowledge you just provided
2. Encourages the student to think deeper about how to apply this knowledge to their specific project
3. Connects the general knowledge to their specific design challenge
4. Provokes critical thinking rather than asking for more information
5. Is specific and actionable, not generic

The question should help them think about HOW to use this knowledge in their design process.

Generate only the question (no introduction, no explanation):
"""

            import openai
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )

            question = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

            if question and not question.endswith('?'):
                question += '?'

            if question:
                return f"{response_text}\n\n{question}"
            else:
                return f"{response_text}\n\nHow might you apply these concepts to your specific design challenge?"

        except Exception as e:
            print(f"⚠️ Question enhancement failed: {e}")
            # Fallback to contextual question
            return f"{response_text}\n\nHow might you apply these concepts to your specific design challenge?"

    def _enhance_example_response_with_synthesis(self, response_text: str, user_input: str, classification: Dict[str, Any]) -> str:
        """Enhance example responses with synthesis sections and thoughtful questions."""

        try:
            # Generate synthesis and thoughtful questions for example responses
            prompt = f"""
You are an expert architectural mentor. You just provided these project examples to a student:

EXAMPLES PROVIDED: "{response_text}"

STUDENT'S ORIGINAL REQUEST: "{user_input}"

Add a synthesis section that:
1. Identifies 2-3 key design strategies or principles that emerge from these examples
2. Explains how these strategies could inspire or inform the student's own warehouse-to-community-center project
3. Connects the examples to broader architectural concepts or approaches
4. Ends with ONE thoughtful question that encourages the student to think about how these precedents could influence their specific design decisions

Format:
[Original examples text]

**Key Insights from These Examples:**
[2-3 key strategies/principles with brief explanations of how they could inspire the student's project]

[One thoughtful question about application to their project]

Generate the synthesis section only (starting with "**Key Insights from These Examples:**"):
"""

            import openai
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )

            synthesis = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

            if synthesis:
                return f"{response_text}\n\n{synthesis}"
            else:
                # Fallback synthesis
                return f"{response_text}\n\n**Key Insights from These Examples:**\nThese projects demonstrate how adaptive reuse can preserve existing architectural character while introducing new community functions. Consider how the balance between preservation and transformation in these examples might inform your own approach to converting warehouse space for community use.\n\nWhich of these strategies for balancing old and new resonates most with your vision for the warehouse transformation?"

        except Exception as e:
            print(f"⚠️ Example synthesis enhancement failed: {e}")
            # Fallback synthesis
            return f"{response_text}\n\n**Key Insights from These Examples:**\nThese projects demonstrate how adaptive reuse can preserve existing architectural character while introducing new community functions. Consider how the balance between preservation and transformation in these examples might inform your own approach to converting warehouse space for community use.\n\nWhich of these strategies for balancing old and new resonates most with your vision for the warehouse transformation?"


