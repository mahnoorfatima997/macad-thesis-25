from typing import Dict, Any
from typing_extensions import TypedDict

# Avoid NameError for forward reference by providing a minimal protocol-like fallback.
try:
    # During runtime, this import should succeed when `state_manager` is available on sys.path
    from state_manager import ArchMentorState as _ArchMentorState  # type: ignore
except Exception:  # pragma: no cover - used only for typing/runtime fallback
    class _ArchMentorState:  # type: ignore
        pass

# Ensure the forward ref can be resolved by get_type_hints during runtime
ArchMentorState = _ArchMentorState  # type: ignore

# Local imports are typed as strings to avoid circular imports at type-check time


class WorkflowState(TypedDict):
    """LangGraph state that flows between agents.

    Mirrors the original structure used by the monolithic orchestrator.
    """
    # Core state
    student_state: "ArchMentorState"  # forward ref for type checkers
    last_message: str

    # Context analysis
    student_classification: Dict[str, Any]
    context_analysis: Dict[str, Any]
    routing_decision: Dict[str, Any]

    # Agent results
    analysis_result: Dict[str, Any]
    domain_expert_result: Dict[str, Any]
    socratic_result: Dict[str, Any]
    cognitive_enhancement_result: Dict[str, Any]

    # Conversation progression
    conversation_progression: Dict[str, Any]
    milestone_guidance: Dict[str, Any]

    # Final output
    final_response: str
    response_metadata: Dict[str, Any]


