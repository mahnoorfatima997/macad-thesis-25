from typing import Callable

from ..types import WorkflowState


def make_domain_expert_node(domain_expert, state_validator, state_monitor, logger) -> Callable[[WorkflowState], WorkflowState]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in domain_expert_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "domain_expert_node_input")

        student_state = state["student_state"]
        analysis_result = state.get("analysis_result", {})

        visual_analysis = analysis_result.get("visual_analysis", {})
        if visual_analysis and not visual_analysis.get("error"):
            student_state.agent_context["visual_insights"] = {
                "design_strengths": visual_analysis.get("design_strengths", []),
                "improvement_opportunities": visual_analysis.get("improvement_opportunities", []),
                "identified_elements": visual_analysis.get("identified_elements", []),
                "has_visual_analysis": True,
            }
            analysis_result["visual_context"] = {
                "has_visual": True,
                "elements": visual_analysis.get("identified_elements", []),
                "strengths": visual_analysis.get("design_strengths", []),
                "opportunities": visual_analysis.get("improvement_opportunities", []),
            }
        else:
            student_state.agent_context["visual_insights"] = {"has_visual_analysis": False}
            analysis_result["visual_context"] = {"has_visual": False}

        cognitive_flags = analysis_result.get("cognitive_flags", [])
        primary_gap = cognitive_flags[0].replace("needs_", "").replace("_guidance", "_awareness") if cognitive_flags else "brief_development"

        # Prepare required arguments according to DomainExpertAgent API
        context_classification = state.get("student_classification", {}) or {}
        if primary_gap and isinstance(context_classification, dict):
            context_classification["primary_gap"] = primary_gap
        routing_decision = state.get("routing_decision", {}) or {}

        # AGENT COORDINATION: Add other agents' responses to context for coordination
        other_agent_responses = {}
        if "socratic_result" in state:
            socratic_result = state["socratic_result"]
            if hasattr(socratic_result, 'to_dict'):
                socratic_dict = socratic_result.to_dict()
            elif isinstance(socratic_result, dict):
                socratic_dict = socratic_result
            else:
                socratic_dict = {"response_text": str(socratic_result)}

            other_agent_responses["socratic_tutor"] = {
                "response_text": socratic_dict.get("response_text", ""),
                "response_type": socratic_dict.get("response_type", "socratic"),
                "key_insights": socratic_dict.get("key_insights", [])
            }

        if "analysis_result" in state:
            analysis_data = state["analysis_result"]
            if isinstance(analysis_data, dict):
                other_agent_responses["analysis_agent"] = {
                    "cognitive_state": analysis_data.get("cognitive_state", {}),
                    "primary_gap": analysis_data.get("cognitive_state", {}).get("primary_gap", ""),
                    "understanding_level": analysis_data.get("cognitive_state", {}).get("understanding_level", "moderate")
                }

        # Add coordination context to classification
        if other_agent_responses:
            context_classification["agent_coordination"] = {
                "other_responses": other_agent_responses,
                "coordination_notes": "Domain expert can build upon or complement other agents' responses"
            }

        domain_result = await domain_expert.provide_knowledge(
            student_state,
            context_classification,
            analysis_result,
            routing_decision,
        )
        
        # Ensure domain_result is a dictionary, not an AgentResponse object
        if hasattr(domain_result, 'to_dict'):
            try:
                domain_result = domain_result.to_dict()
            except Exception as e:
                logger.error(f"Failed to convert AgentResponse to dict: {e}")
                # Fallback: create a basic dictionary
                domain_result = {
                    "response_text": str(domain_result),
                    "response_type": "error",
                    "error_message": f"Conversion failed: {e}"
                }
        elif not isinstance(domain_result, dict):
            # If it's not a dict and doesn't have to_dict, convert to string
            domain_result = {
                "response_text": str(domain_result),
                "response_type": "unknown",
                "error_message": "Result was not an AgentResponse or dict"
            }

        result_state = {**state, "domain_expert_result": domain_result}

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in domain_expert_node: {output_validation.errors}")
        state_monitor.record_state_change(result_state["student_state"], "domain_expert_node_output")
        return result_state

    return handler


