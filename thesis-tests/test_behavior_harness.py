"""
Lightweight behavior harness to validate routing aliases, shaping, and basic classification fallbacks
without hitting external LLMs. Run:

  python thesis-tests/test_behavior_harness.py

This script checks:
- Route→response shaping structure (bullets/questions/headers) for key routes
- Response type normalization mapping
- Basic classification fallback detection for confusion/example/technical
"""

from typing import Dict, Any
import os
import importlib.util


def _load_module(module_name: str, relative_path: str):
    """Load a module by file path to avoid hyphenated package import issues."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
    file_path = os.path.join(base_dir, relative_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load required modules directly from file paths
orch_mod = _load_module("orch_mod", os.path.join("thesis-agents", "orchestration", "langgraph_orchestrator.py"))
state_mod = _load_module("state_mod", os.path.join("thesis-agents", "state_manager.py"))
ctx_mod = _load_module("ctx_mod", os.path.join("thesis-agents", "agents", "context_agent.py"))

LangGraphOrchestrator = getattr(orch_mod, "LangGraphOrchestrator")
ArchMentorState = getattr(state_mod, "ArchMentorState")
ContextAgent = getattr(ctx_mod, "ContextAgent")


def assert_in(text: str, needle: str, label: str) -> None:
    assert needle in text, f"[{label}] expected '{needle}' in text. Got: {text[:200]}..."


def test_shaping() -> None:
    orch = LangGraphOrchestrator()
    classification_base: Dict[str, Any] = {
        "is_technical_question": False,
        "is_example_request": False,
        "shows_confusion": False,
    }

    # Technical guidance
    shaped = orch._shape_by_route(
        text="Door widths must comply with local codes.",
        routing_path="technical_guidance",
        classification={**classification_base, "is_technical_question": True},
        ordered_results={"domain": {"response_text": "Provide 32 inch clear width. Landings required at doors."}},
        user_message_count=3,
        context_analysis={},
    )
    assert_in(shaped, "Key points:", "technical.header")
    assert_in(shaped, "- ", "technical.bullets")
    assert_in(shaped, "Apply:", "technical.apply")

    # Clarification support (confusion)
    shaped = orch._shape_by_route(
        text="",
        routing_path="clarification_support",
        classification={**classification_base, "shows_confusion": True},
        ordered_results={"socratic": {"response_text": ""}},
        user_message_count=1,
        context_analysis={},
    )
    assert_in(shaped, "Let's clarify together:", "clarify.header")
    assert_in(shaped, "?", "clarify.questions")

    # Example request early probe
    shaped = orch._shape_by_route(
        text="",
        routing_path="knowledge_exploration",
        classification={**classification_base, "is_example_request": True},
        ordered_results={"domain": {"response_text": "Project A – central atrium. Project B – distributed cores."}},
        user_message_count=1,
        context_analysis={},
    )
    assert_in(shaped, "Probe:", "examples.probe")

    # Example request later with apply
    shaped = orch._shape_by_route(
        text="",
        routing_path="knowledge_exploration",
        classification={**classification_base, "is_example_request": True},
        ordered_results={"domain": {"response_text": "Project A – central atrium. Project B – distributed cores."}},
        user_message_count=4,
        context_analysis={},
    )
    assert_in(shaped, "Examples:", "examples.header")
    assert_in(shaped, "Apply:", "examples.apply")

    # 1008Example request later with url_items titles preferred as labels
    shaped = orch._shape_by_route(
        text="",
        routing_path="example_request",
        classification={**classification_base, "is_example_request": True},
        ordered_results={
            "domain": {
                "response_text": "Tate Modern - A converted power station with innovative gallery spaces.\nThe High Line - An elevated park that transformed an abandoned railway.",
                "url_items": [
                    {"title": "Tate Modern", "url": "https://www.tate.org.uk/visit/tate-modern"},
                    {"title": "The High Line", "url": "https://www.thehighline.org/"},
                ],
            }
        },
        user_message_count=5,
        context_analysis={},
    )
    assert_in(shaped, "Examples:", "examples2.header")
    assert_in(shaped, "1. **Tate Modern**", "examples2.title1")
    assert_in(shaped, "2. **The High Line**", "examples2.title2")

    # Cognitive challenge framing + prompts
    shaped = orch._shape_by_route(
        text="",
        routing_path="cognitive_challenge",
        classification=classification_base,
        ordered_results={"cognitive": {"response_text": "Let's test your thinking."}},
        user_message_count=3,
        context_analysis={},
    )
    assert_in(shaped, "- Try a constraint change:", "cog.prompt1")
    assert_in(shaped, "Which one will you try first?", "cog.question")

    # Multi-agent synthesis
    shaped = orch._shape_by_route(
        text="",
        routing_path="multi_agent_comprehensive",
        classification=classification_base,
        ordered_results={
            "domain": {"response_text": "Consider proportion and circulation patterns."},
            "socratic": {"response_text": "How might circulation inform massing?"},
        },
        user_message_count=3,
        context_analysis={},
    )
    assert_in(shaped, "Synthesis:", "synth.header")
    assert_in(shaped, "Next:", "synth.next")
    assert_in(shaped, "?", "synth.question")

    # 0908-ADDED:Design guidance synthesis
    shaped = orch._shape_by_route(
        text="",
        routing_path="design_guidance",
        classification=classification_base,
        ordered_results={
            "domain": {"response_text": "Balance daylight and privacy along the south facade."},
            "socratic": {"response_text": "Which orientation best supports your program needs?"},
        },
        user_message_count=3,
        context_analysis={},
    )
    assert_in(shaped, "Synthesis:", "design.header")
    assert_in(shaped, "Next:", "design.next")
    assert_in(shaped, "?", "design.question")




    # Normalization mapping checks
    assert orch._normalize_response_type("", "knowledge_with_challenge", {}) == "knowledge_support"
    assert orch._normalize_response_type("", "supportive_scaffolding", {}) == "socratic_primary"
    assert orch._normalize_response_type("", "cognitive_intervention", {}) == "cognitive_intervention"
    assert orch._normalize_response_type("", "multi_agent_comprehensive", {}) == "synthesis"


def test_classification_fallbacks() -> None:
    agent = ContextAgent("architecture")
    # Example request detection
    ex = agent._enhanced_fallback_detection("Can you show me precedents for atrium lighting?")
    assert ex.get("is_example_request", False) is True
    # Confusion detection
    cf = agent._enhanced_fallback_detection("I'm confused. I don't understand circulation.")
    assert cf.get("shows_confusion", False) is True
    # Technical detection
    tq = agent._enhanced_fallback_detection("What are ADA requirements for ramp slope?")
    assert tq.get("is_technical_question", False) is True


if __name__ == "__main__":
    print("Running behavior harness checks...")
    try:
        test_shaping()
        print("✓ Shaping tests passed")
    except AssertionError as e:
        print(f"✗ Shaping test failed: {e}")
    try:
        test_classification_fallbacks()
        print("✓ Classification fallback tests passed")
    except AssertionError as e:
        print(f"✗ Classification fallback test failed: {e}")

