from typing import Callable, Dict, Any

from ..types import WorkflowState


def make_context_node(context_agent, progression_manager, first_response_generator, state_validator, state_monitor, logger) -> Callable[[WorkflowState], Any]:
    async def handler(state: WorkflowState) -> WorkflowState:
        # Reuse original logic by delegating to the context_agent
        # The original orchestrator also handled "first message" logic; keep parity here.

        # Validate input
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in context_agent_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "context_agent_node_input")

        student_state = state["student_state"]
        last_message = state["last_message"]

        # Detect first-message progressive path using the same heuristic
        user_messages = [m["content"] for m in student_state.messages if m.get("role") == "user"]
        is_first_message = len(user_messages) == 0 or (
            len(user_messages) == 2 and getattr(student_state, "current_design_brief", None) and
            last_message != getattr(student_state, "current_design_brief", None) and
            len([m for m in student_state.messages if m.get("role") == "assistant"]) == 0
        )

        if is_first_message:
            first_response_result = await first_response_generator.generate_first_response(last_message, student_state)
            progression_analysis = first_response_result.get("progression_analysis", {})
            result_state: WorkflowState = {
                **state,
                "last_message": last_message,
                "student_classification": {
                    "interaction_type": "first_message",
                    "understanding_level": progression_analysis.get("user_profile", {}).get("knowledge_level", "unknown"),
                    "confidence_level": "neutral",
                    "engagement_level": "medium",
                    "is_first_message": True,
                },
                "context_analysis": {
                    "progression_analysis": progression_analysis,
                    "opening_strategy": first_response_result.get("opening_strategy", {}),
                    "conversation_phase": "discovery",
                },
                "routing_decision": {
                    "path": "progressive_opening",
                    "reasoning": "First message - using progressive conversation system",
                },
                "final_response": first_response_result.get("response_text", ""),
                "response_metadata": first_response_result.get("metadata", {}),
                "progression_data": progression_analysis,
            }

            output_validation = state_validator.validate_state(result_state["student_state"])
            if not output_validation.is_valid:
                logger.warning(f"Output state validation failed in context_agent_node: {output_validation.errors}")
            state_monitor.record_state_change(result_state["student_state"], "context_agent_node_output")
            return result_state

        # Ongoing conversation → use context agent comprehensive analysis
        context_package = await context_agent.analyze_student_input(student_state, last_message)

        if hasattr(context_package, "response_text"):
            context_package = context_package.to_dict()

        if isinstance(context_package, dict) and "metadata" in context_package:
            original_data = context_package["metadata"]
            core_classification = original_data.get("core_classification", {})
            contextual_metadata = original_data.get("contextual_metadata", {})
            conversation_patterns = original_data.get("conversation_patterns", {})
            routing_suggestions = original_data.get("routing_suggestions", {})
            agent_contexts = original_data.get("agent_contexts", {})
        elif hasattr(context_package, "metadata"):
            original_data = context_package.metadata
            core_classification = original_data.get("core_classification", {})
            contextual_metadata = original_data.get("contextual_metadata", {})
            conversation_patterns = original_data.get("conversation_patterns", {})
            routing_suggestions = original_data.get("routing_suggestions", {})
            agent_contexts = original_data.get("agent_contexts", {})
        else:
            core_classification = context_package.get("core_classification", {})
            contextual_metadata = context_package.get("contextual_metadata", {})
            conversation_patterns = context_package.get("conversation_patterns", {})
            routing_suggestions = context_package.get("routing_suggestions", {})
            agent_contexts = context_package.get("agent_contexts", {})

        result_state = {
            **state,
            "last_message": last_message,
            "student_classification": {**core_classification, "last_message": last_message},
            "context_analysis": context_package,
            "context_metadata": contextual_metadata,
            "conversation_patterns": conversation_patterns,
            "routing_suggestions": routing_suggestions,
            "agent_contexts": agent_contexts,
            "context_package": context_package,
        }

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in context_agent_node: {output_validation.errors}")
        state_monitor.record_state_change(result_state["student_state"], "context_agent_node_output")
        return result_state

    return handler


