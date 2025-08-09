from typing import Callable, Dict, Any

from ..types import WorkflowState


def make_router_node(route_decision_fn, state_validator, state_monitor, logger) -> Callable[[WorkflowState], Any]:
    async def handler(state: WorkflowState) -> WorkflowState:
        validation_result = state_validator.validate_state(state["student_state"])
        if not validation_result.is_valid:
            logger.warning(f"State validation failed in router_node: {validation_result.errors}")

        state_monitor.record_state_change(state["student_state"], "router_node_input")

        context_analysis = state.get("context_analysis", {})
        routing_suggestions = context_analysis.get("routing_suggestions", {})
        classification = state.get("student_classification", {})

        # Ensure suggestions are visible to the decision function
        state["routing_suggestions"] = routing_suggestions

        routing_path = route_decision_fn(state)
        # Prefer advanced system reason if available in state
        detailed = state.get("detailed_routing_decision", {})
        advanced_reason = detailed.get("reason") if isinstance(detailed, dict) else None
        routing_decision = {
            "path": routing_path,
            "reasoning": advanced_reason or _generate_routing_reasoning(routing_path, routing_suggestions, classification, logger),
        }

        result_state = {**state, "routing_decision": routing_decision}

        output_validation = state_validator.validate_state(result_state["student_state"])
        if not output_validation.is_valid:
            logger.warning(f"Output state validation failed in router_node: {output_validation.errors}")
        state_monitor.record_state_change(result_state["student_state"], "router_node_output")
        return result_state

    return handler


def _generate_routing_reasoning(routing_path: str, routing_suggestions: Dict[str, Any], classification: Dict[str, Any], logger) -> str:
    # This mirrors the fallback reasoning logic; advanced system reasoning is attached by the caller if present
    if routing_suggestions and routing_suggestions.get("confidence", 0) > 0.6:
        primary_route = routing_suggestions.get("primary_route", "default")
        confidence = routing_suggestions.get("confidence", 0)
        return f"Context agent suggested '{primary_route}' with {confidence:.1%} confidence, mapped to '{routing_path}'"

    interaction_type = classification.get("interaction_type", "general_statement")
    confidence_level = classification.get("confidence_level", "confident")
    understanding_level = classification.get("understanding_level", "medium")

    reasoning_parts = []
    if interaction_type == "example_request":
        reasoning_parts.append("User requested examples")
    elif interaction_type == "feedback_request":
        reasoning_parts.append("User requested feedback")
    elif interaction_type == "technical_question":
        reasoning_parts.append("User asked technical question")
    elif interaction_type == "confusion_expression":
        reasoning_parts.append("User expressed confusion")

    if confidence_level == "overconfident":
        reasoning_parts.append("User appears overconfident")
    elif confidence_level == "uncertain":
        reasoning_parts.append("User appears uncertain")

    if understanding_level == "low":
        reasoning_parts.append("User has low understanding")
    elif understanding_level == "high":
        reasoning_parts.append("User has high understanding")

    route_reason = {
        "cognitive_intervention": "Cognitive offloading detected",
        "knowledge_only": "Pure knowledge request identified",
        "socratic_exploration": "Exploration/guidance needed",
        "multi_agent_comprehensive": "Complex request requiring multiple agents",
        "socratic_clarification": "Clarification needed",
        "supportive_scaffolding": "Supportive scaffolding needed",
        "foundational_building": "Foundational knowledge needed",
        "knowledge_with_challenge": "Knowledge with challenge needed",
        "balanced_guidance": "Balanced guidance approach",
        "design_guidance": "Design guidance requested",
        "progressive_opening": "Progressive conversation opening",
        "topic_transition": "Topic transition detected",
    }.get(routing_path)

    if route_reason:
        reasoning_parts.append(route_reason)

    return f"Route '{routing_path}' selected based on: {', '.join(reasoning_parts)}" if reasoning_parts else f"Route '{routing_path}' selected as default balanced guidance"


