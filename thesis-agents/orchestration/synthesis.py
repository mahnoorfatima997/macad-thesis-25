from typing import Dict, Any, Tuple

from .types import WorkflowState


def build_synthesizer(orchestrator_like) -> Tuple:
    """Return (synthesize_fn, ensure_quality_fn) bound to the provided orchestrator-like object.

    This adapts the existing synthesis methods on the original orchestrator, preserving behavior.
    """

    def synthesize_fn(state: WorkflowState) -> Tuple[str, Dict[str, Any]]:
        # Delegate to the original orchestrator methods to preserve logic exactly
        return orchestrator_like.synthesize_responses(state)

    # ensure_quality is imported in the original orchestrator, reuse via orchestrator
    def ensure_quality_fn(text: str, agent_type: str) -> str:
        return orchestrator_like.ensure_quality(text, agent_type) if hasattr(orchestrator_like, "ensure_quality") else text

    return synthesize_fn, ensure_quality_fn


