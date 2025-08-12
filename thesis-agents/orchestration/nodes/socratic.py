from typing import Callable

from ..types import WorkflowState


def make_socratic_node(socratic_agent, state_validator, state_monitor, logger) -> Callable[[WorkflowState], WorkflowState]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in socratic_tutor_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "socratic_tutor_node_input")

        milestone_guidance = state.get("milestone_guidance", {})
        current_milestone = milestone_guidance.get("current_milestone")
        agent_guidance = milestone_guidance.get("agent_guidance", {})

        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})
        context_classification = state.get("student_classification", {})
        domain_expert_result = state.get("domain_expert_result", {})
        
        # Add routing path to context classification so Socratic tutor knows which route to use
        routing_decision = state.get("routing_decision", {})
        routing_path = routing_decision.get("path", "unknown")
        context_classification["routing_path"] = routing_path
        
        print(f"🔍 DEBUG: Socratic node - routing_path: {routing_path}")
        print(f"🔍 DEBUG: Socratic node - context_classification keys: {list(context_classification.keys())}")

        if current_milestone:
            analysis_result["milestone_context"] = {
                "milestone_type": current_milestone.milestone_type.value,
                "phase": current_milestone.phase.value,
                "required_actions": current_milestone.required_actions,
                "success_criteria": current_milestone.success_criteria,
                "agent_guidance": agent_guidance,
            }

        # Use the adapter's public API
        gap_type = (analysis_result.get("cognitive_state", {}) or {}).get("primary_gap", "general")
        socratic_result = await socratic_agent.provide_guidance(
            student_state,
            context_classification,
            analysis_result,
            gap_type,
        )
        
        # Ensure socratic_result is a dictionary, not an AgentResponse object
        if hasattr(socratic_result, 'to_dict'):
            try:
                socratic_result = socratic_result.to_dict()
            except Exception as e:
                logger.error(f"Failed to convert AgentResponse to dict: {e}")
                # Fallback: create a basic dictionary
                socratic_result = {
                    "response_text": str(socratic_result),
                    "response_type": "error",
                    "error_message": f"Conversion failed: {e}"
                }
        elif not isinstance(socratic_result, dict):
            # If it's not a dict and doesn't have to_dict, convert to string
            socratic_result = {
                "response_text": str(socratic_result),
                "response_type": "unknown",
                "error_message": "Result was not an AgentResponse or dict"
            }

        result_state = {**state, "socratic_result": socratic_result}

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in socratic_tutor_node: {output_validation.errors}")

        state_monitor.record_state_change(result_state["student_state"], "socratic_tutor_node_output")
        return result_state

    return handler


