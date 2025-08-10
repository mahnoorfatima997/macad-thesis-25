from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph

from .types import WorkflowState
from .graph_builder import build_workflow
from .nodes import (
    make_context_node,
    make_router_node,
    make_analysis_node,
    make_domain_expert_node,
    make_socratic_node,
    make_cognitive_enhancement_node,
    make_synthesizer_node,
)
from .synthesis import build_synthesizer


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

        routing_context = RoutingContext(
            classification=classification,
            context_analysis=context_analysis,
            routing_suggestions=routing_suggestions,
            student_state=student_state.__dict__ if student_state else None,
            conversation_history=student_state.messages if student_state else [],
            current_phase=student_state.design_phase.value if student_state else "ideation",
            phase_progress=0.0,
        )

        decision = self.routing_decision_tree.decide_route(routing_context)
        self.last_routing_decision = decision  # for reasoning access

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
            return state.get("final_response", ""), metadata

        final_response, response_type = self._synthesize_by_routing_path(
            routing_path, agent_results, user_input, classification, state
        )

        # Apply response quality controls similar to legacy logic
        agent_type_map = {
            "domain_knowledge": "domain_expert",
            "socratic_guidance": "socratic_tutor",
            "cognitive_enhancement": "cognitive_enhancement",
        }
        agent_type = agent_type_map.get(response_type, "default")
        final_response = self.ensure_quality(final_response, agent_type)

        metadata = self._build_metadata(response_type, agent_results, routing_decision, classification)
        return final_response, metadata

    def _get_agent_results(self, state: WorkflowState) -> Dict[str, Any]:
        return {
            "socratic": state.get("socratic_result", {}),
            "domain": state.get("domain_expert_result", {}),
            "analysis": state.get("analysis_result", {}),
            "cognitive": state.get("cognitive_enhancement_result", {}),
        }

    def _synthesize_by_routing_path(
        self,
        routing_path: str,
        agent_results: Dict[str, Any],
        user_input: str,
        classification: Dict[str, Any],
        state: WorkflowState,
    ) -> tuple[str, str]:
        if routing_path in ["progressive_opening", "topic_transition"]:
            final_response = state.get("final_response", "")
            if final_response:
                return final_response, "progressive_opening"
            return self._synthesize_default_response(agent_results)
        if routing_path == "knowledge_only":
            return self._synthesize_knowledge_only_response(agent_results, user_input, classification)
        if routing_path == "socratic_exploration":
            return self._synthesize_socratic_exploration_response(agent_results)
        if routing_path == "cognitive_intervention":
            return self._synthesize_cognitive_intervention_response(agent_results)
        if routing_path == "technical_question":
            domain_result = agent_results.get("domain", {})
            return self._synthesize_technical_response(domain_result, user_input, classification), "technical_question"
        if routing_path == "feedback_request":
            return self._synthesize_feedback_response(
                agent_results.get("socratic", {}), agent_results.get("domain", {}), user_input, classification
            ), "feedback_request"
        if routing_path == "design_guidance":
            return self._synthesize_design_guidance_response(agent_results, user_input, classification), "design_guidance"
        if routing_path == "supportive_scaffolding":
            return self._synthesize_clarification_response(
                agent_results.get("socratic", {}), agent_results.get("domain", {}), user_input, classification
            ), "supportive_scaffolding"
        return self._synthesize_default_response(agent_results)

    def _synthesize_knowledge_only_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> tuple[str, str]:
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        if domain_result and socratic_result:
            final_response = f"{domain_result.get('response_text', '')}\n\n{socratic_result.get('response_text', '')}"
            return final_response, "knowledge_only_with_socratic"
        return self._synthesize_example_response(domain_result, user_input, classification), "knowledge_only"

    def _synthesize_socratic_exploration_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        socratic_result = agent_results.get("socratic", {})
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", ""), "socratic_exploration"
        return (
            "I'd be happy to help you explore this topic together. What specific aspects would you like to think about?",
            "socratic_exploration",
        )

    def _synthesize_cognitive_intervention_response(self, agent_results: Dict[str, Any]) -> tuple[str, str]:
        cognitive_result = agent_results.get("cognitive", {})
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
        try:
            if hasattr(state, "analysis_result") and state.analysis_result:
                analysis_result = state.analysis_result
                if isinstance(analysis_result, dict):
                    text_analysis = analysis_result.get("text_analysis", {})
                    building_type = text_analysis.get("building_type", "project")
                    return building_type if building_type != "unknown" else "project"
            if hasattr(state, "current_design_brief") and state.current_design_brief:
                brief_lower = state.current_design_brief.lower()
                building_types = [
                    "residential",
                    "commercial",
                    "educational",
                    "healthcare",
                    "cultural",
                    "office",
                    "retail",
                ]
                for b in building_types:
                    if b in brief_lower:
                        return b
            return "project"
        except Exception:
            return "project"

    def _extract_topic_from_user_input(self, user_input: str) -> str:
        topics = ["circulation", "lighting", "spatial", "form", "function", "context", "materials", "structure"]
        user_lower = user_input.lower()
        for t in topics:
            if t in user_lower:
                return t
        return "design"

    def _synthesize_example_response(self, domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any], state=None) -> str:
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
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        return "I'd be glad to provide feedback! What specific aspects of your project should I focus on?"

    def _synthesize_technical_response(self, domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        topic = self._extract_topic_from_user_input(user_input)
        return f"I'd be happy to help with technical requirements for {topic}! Could you specify what technical aspects you need information about?"

    def _synthesize_clarification_response(self, socratic_result: Dict[str, Any], domain_result: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result["response_text"]
        if domain_result and domain_result.get("response_text"):
            return domain_result["response_text"]
        topic = self._extract_topic_from_user_input(user_input)
        return f"I understand {topic} can be complex! What specific part would you like me to explain in more detail?"

    def _synthesize_design_guidance_response(self, agent_results: Dict[str, Any], user_input: str, classification: Dict[str, Any]) -> str:
        domain_result = agent_results.get("domain", {})
        socratic_result = agent_results.get("socratic", {})
        if socratic_result and socratic_result.get("response_text"):
            return socratic_result.get("response_text", "")
        if domain_result and domain_result.get("response_text"):
            return domain_result.get("response_text", "")
        return "That's a great design question! What specific aspects are you trying to optimize?"

    # ------------- Metadata helpers (ported minimally) -------------

    def _build_metadata(self, response_type: str, agent_results: Dict[str, Any], routing_decision: Dict, classification: Dict) -> Dict[str, Any]:
        agents_used: List[str] = []
        if agent_results.get("socratic"): agents_used.append("socratic_tutor")
        if agent_results.get("domain"): agents_used.append("domain_expert")
        if agent_results.get("analysis"): agents_used.append("analysis_agent")
        if agent_results.get("cognitive"): agents_used.append("cognitive_enhancement")

        analysis_result = agent_results.get("analysis", {})
        cognitive_result = agent_results.get("cognitive", {})
        domain_result = agent_results.get("domain", {})

        return {
            "response_type": response_type,
            "agents_used": agents_used,
            "routing_path": routing_decision.get("path", "unknown"),
            "ai_reasoning": routing_decision.get("reasoning", "No AI reasoning available"),
            "phase_analysis": analysis_result.get("phase_analysis", {}),
            "scientific_metrics": cognitive_result.get("scientific_metrics", {}),
            "cognitive_state": cognitive_result.get("cognitive_state", {}),
            "analysis_result": analysis_result,
            "sources": domain_result.get("sources", []) if domain_result else [],
            "processing_time": "N/A",
            "classification": classification,
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

        self.logger.info("Starting workflow...")

        # Ensure brief is placed if needed
        if hasattr(student_state, "ensure_brief_in_messages") and student_state.ensure_brief_in_messages():
            if not any(m.get("role") == "brief" for m in student_state.messages):
                student_state.messages.insert(0, {"role": "brief", "content": getattr(student_state, "current_design_brief", "")})

        user_messages = [m for m in student_state.messages if m.get("role") == "user"]
        current_user_input = user_messages[-1]["content"] if user_messages else ""

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

        final_state = await self.workflow.ainvoke(initial_state)

        processing_time = time.time() - start_time
        if "response_metadata" in final_state:
            final_state["response_metadata"]["processing_time"] = f"{processing_time:.2f}s"
            final_state["response_metadata"]["conversation_progression"] = progression_analysis
            final_state["response_metadata"]["milestone_guidance"] = milestone_guidance

        # Optional console summary like legacy implementation
        try:
            self._print_user_requested_info(final_state)
        except Exception:
            pass

        return {
            "response": final_state.get("final_response", ""),
            "metadata": final_state.get("response_metadata", {}),
            "routing_path": final_state.get("routing_decision", {}).get("path", "unknown"),
            "classification": final_state.get("student_classification", {}),
            "conversation_progression": progression_analysis,
            "milestone_guidance": milestone_guidance,
        }

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
        if classification.get("interaction_type") == "feedback_request":
            recent_messages = context_analysis.get("conversation_patterns", {}).get("recent_messages", [])
            if len(recent_messages) < 3:
                indicators.update({"detected": True, "type": "premature_answer_seeking", "confidence": 0.8})
                indicators["indicators"].append("Asking for answers before exploration")
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


