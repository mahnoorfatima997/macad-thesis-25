from typing import Callable, Dict, Any, Tuple

from ..types import WorkflowState


def make_synthesizer_node(synthesize_fn, ensure_quality_fn, state_validator, state_monitor, logger) -> Callable[[WorkflowState], WorkflowState]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in synthesizer_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "synthesizer_node_input")

        existing_response = state.get("final_response", "")
        if existing_response:
            metadata = state.get("response_metadata", {})
            result_state = {**state, "final_response": existing_response, "response_metadata": metadata}
            output_validation = state_validator.validate_state(result_state["student_state"])
            if not output_validation.is_valid:
                logger.warning(f"Output state validation failed in synthesizer_node: {output_validation.errors}")
            state_monitor.record_state_change(result_state["student_state"], "synthesizer_node_output")
            return result_state

        final_response, metadata = synthesize_fn(state)

        result_state = {**state, "final_response": final_response, "response_metadata": metadata}

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in synthesizer_node: {output_validation.errors}")
        state_monitor.record_state_change(result_state["student_state"], "synthesizer_node_output")
        return result_state

    return handler


