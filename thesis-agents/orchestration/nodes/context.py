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
        agent_response = await context_agent.analyze_student_input(student_state, last_message)

        # Extract data from AgentResponse
        if hasattr(agent_response, "metadata") and agent_response.metadata:
            # The ContextPackage is stored in the metadata field of AgentResponse
            context_package_data = agent_response.metadata
            core_classification = context_package_data.get("core_classification", {})
            contextual_metadata = context_package_data.get("contextual_metadata", {})
            conversation_patterns = context_package_data.get("conversation_patterns", {})
            routing_suggestions = context_package_data.get("routing_suggestions", {})
            agent_contexts = context_package_data.get("agent_contexts", {})
            context_package = context_package_data
        elif hasattr(agent_response, "to_dict"):
            # Fallback: convert AgentResponse to dict
            agent_response_dict = agent_response.to_dict()
            context_package_data = agent_response_dict.get("metadata", {})
            core_classification = context_package_data.get("core_classification", {})
            contextual_metadata = context_package_data.get("contextual_metadata", {})
            conversation_patterns = context_package_data.get("conversation_patterns", {})
            routing_suggestions = context_package_data.get("routing_suggestions", {})
            agent_contexts = context_package_data.get("agent_contexts", {})
            context_package = context_package_data
        else:
            # Final fallback
            core_classification = {}
            contextual_metadata = {}
            conversation_patterns = {}
            routing_suggestions = {}
            agent_contexts = {}
            context_package = {}

        # Convert CoreClassification object to dictionary for student_classification
        classification_dict = {}

        if isinstance(core_classification, dict):
            classification_dict = core_classification.copy()
        elif hasattr(core_classification, '__dict__'):
            classification_dict = core_classification.__dict__.copy()
        else:
            # Fallback: extract key attributes
            classification_dict = {
                "interaction_type": getattr(core_classification, 'interaction_type', 'unknown'),
                "understanding_level": getattr(core_classification, 'understanding_level', 'medium'),
                "confidence_level": getattr(core_classification, 'confidence_level', 'confident'),
                "engagement_level": getattr(core_classification, 'engagement_level', 'medium'),
            }

        result_state = {
            **state,
            "last_message": last_message,
            "student_classification": {**classification_dict, "last_message": last_message},
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


