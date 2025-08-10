from typing import Callable

from ..types import WorkflowState


def make_analysis_node(analysis_agent, state_validator, state_monitor, logger, progression_manager) -> Callable[[WorkflowState], WorkflowState]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in analysis_agent_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "analysis_agent_node_input")

        student_state = state["student_state"]
        context_package = state.get("context_package", {})
        last_message = state.get("last_message", "")

        progression_integration = analysis_agent.integrate_conversation_progression(student_state, last_message, "")
        analysis_result = await analysis_agent.process(student_state, context_package)
        if hasattr(analysis_result, "response_text"):
            analysis_result = analysis_result.to_dict()

        analysis_result.update({
            "conversation_progression": progression_integration.get("conversation_progression", {}),
            "current_milestone": progression_integration.get("current_milestone"),
            "milestone_assessment": progression_integration.get("milestone_assessment", {}),
            "agent_guidance": progression_integration.get("agent_guidance", {}),
        })

        result_state = {
            **state,
            "analysis_result": analysis_result,
            "conversation_progression": progression_integration.get("conversation_progression", {}),
            "milestone_guidance": progression_integration.get("agent_guidance", {}),
        }

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in analysis_agent_node: {output_validation.errors}")

        state_monitor.record_state_change(result_state["student_state"], "analysis_agent_node_output")
        return result_state

    return handler


