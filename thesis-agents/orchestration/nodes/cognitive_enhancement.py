from typing import Callable

from ..types import WorkflowState


def make_cognitive_enhancement_node(cognitive_agent, state_validator, state_monitor, logger) -> Callable[[WorkflowState], WorkflowState]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in cognitive_enhancement_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "cognitive_enhancement_node_input")

        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        context_classification = state.get("student_classification", {})
        routing_decision = state.get("routing_decision", {})

        enhancement_result = await cognitive_agent.provide_challenge(
            student_state, context_classification, analysis_result, routing_decision
        )
        if hasattr(enhancement_result, "response_text"):
            enhancement_result = enhancement_result.to_dict()

        result_state = {**state, "cognitive_enhancement_result": enhancement_result}

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in cognitive_enhancement_node: {output_validation.errors}")
        state_monitor.record_state_change(result_state["student_state"], "cognitive_enhancement_node_output")
        return result_state

    return handler


