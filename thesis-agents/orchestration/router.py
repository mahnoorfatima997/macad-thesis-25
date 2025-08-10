from typing import Dict, Any

from .types import WorkflowState


class RouterHelper:
    def __init__(self, advanced_decision_tree, logger):
        self.decision_tree = advanced_decision_tree
        self.logger = logger
        self.last_routing_decision = None

    def decide_route(self, state: WorkflowState) -> str:
        classification = state.get("student_classification", {})
        context_analysis = state.get("context_analysis", {})
        routing_suggestions = state.get("routing_suggestions", {})
        student_state = state.get("student_state")

        try:
            classification["user_input"] = state.get("last_message", "")
        except Exception:
            pass

        routing_context = self.decision_tree.RoutingContext(
            classification=classification,
            context_analysis=context_analysis,
            routing_suggestions=routing_suggestions,
            student_state=getattr(student_state, "__dict__", None) if student_state else None,
            conversation_history=getattr(student_state, "messages", []) if student_state else [],
            current_phase=getattr(getattr(student_state, "design_phase", None), "value", "ideation") if student_state else "ideation",
            phase_progress=0.0,
        ) if hasattr(self.decision_tree, "RoutingContext") else None

        if routing_context is not None and hasattr(self.decision_tree, "decide_route"):
            decision = self.decision_tree.decide_route(routing_context)
            self.last_routing_decision = decision
            try:
                self.logger.info(f"Advanced Routing Decision: {decision.route.value}")
                self.logger.info(f"Reason: {decision.reason}")
            except Exception:
                pass
            state["detailed_routing_decision"] = getattr(decision, "__dict__", {})
            return getattr(getattr(decision, "route", None), "value", None) or getattr(decision, "route", "default")

        # Fallback: call the original function-style route_decision on orchestrator
        # The orchestrator will bind this helper via a thin wrapper.
        raise RuntimeError("RouterHelper.decide_route requires advanced decision tree or a wrapper.")


