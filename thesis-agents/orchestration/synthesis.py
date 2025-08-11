from typing import Dict, Any, Tuple
import re

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


# Enhanced text processing functions ported from FROMOLDREPO
def _sanitize(line: str) -> str:
    """Enhanced sanitization function with constraint: label support.

    Remove leading bullets/quotes and redundant label echoes.
    Ported from FROMOLDREPO lines 2028-2043.
    """
    # Remove leading bullets/quotes and redundant label echoes
    t = (line or "").lstrip("-• \t\"'")
    # Drop repeated label if present
    lowered = t.lower().strip()
    if lowered.startswith("insight:"):
        t = t.split(":", 1)[1].strip()
    if lowered.startswith("direction:"):
        t = t.split(":", 1)[1].strip()
    if lowered.startswith("watch:"):
        t = t.split(":", 1)[1].strip()
    if lowered.startswith("constraint:"):
        t = t.split(":", 1)[1].strip()
    # Remove extra quotes that might be present
    t = t.strip('"\'')
    return t


def _first_sentence(s: str, max_len: int = 400) -> str:
    """Extract first sentence with length limit."""
    if not s:
        return ""
    import re
    sentences = re.split(r'[.!?]+', s)
    first = sentences[0].strip() if sentences else s
    return first[:max_len].rstrip()


def _first_question(s: str, max_len: int = 400) -> str:
    """Extract first question from text."""
    if not s:
        return ""
    import re
    m = re.search(r"[^?\n]{3,}\?", s)
    q = m.group(0) if m else _first_sentence(s, max_len)
    q = q.replace("\n", " ")
    return q[:max_len].rstrip()


def calculate_quality_flags(response: str) -> Dict[str, Any]:
    """Calculate basic response quality flags for quick health checks.

    Ported from FROMOLDREPO lines 1700-1709.
    """
    try:
        quality_flags = {
            "ends_with_question": (response.strip().endswith("?")),
            "has_bullets": ("- " in response),
            "has_synthesis_header": ("Synthesis:" in response),
            "char_length": len(response),
        }
        return quality_flags
    except Exception:
        return {}


def shape_by_route(text: str, routing_path: str, classification: Dict[str, Any],
                  ordered_results: Dict[str, Any], user_message_count: int,
                  context_analysis: Dict[str, Any]) -> str:
    """Lightweight, deterministic shaping per route to match thesis Study Mode styles.

    Ported from FROMOLDREPO lines 1822-2100+

    - technical_question: 3-5 bullets + 1 application question
    - confusion_expression: 1-2 clarifying questions
    - example_request: early → probe; later → 2 examples + apply question
    - cognitive_intervention: 3 prompts
    - multi_agent: short synthesis + 1 next action + 1 question
    """
    if not text:
        text = ""

    path = routing_path or "default"
    is_technical = bool(classification.get("is_technical_question"))
    is_confusion = classification.get("interaction_type") == "confusion_expression"
    is_example = classification.get("is_example_request", False)
    early = user_message_count <= 2

    domain_text = (ordered_results.get("domain", {}) or {}).get("response_text", "")
    socratic_text = (ordered_results.get("socratic", {}) or {}).get("response_text", "")
    cognitive_text = (ordered_results.get("cognitive", {}) or {}).get("response_text", "")

    def _to_bullets(src: str, max_items: int = 5) -> str:
        lines = [l.strip("-• \t") for l in src.splitlines() if l.strip()]
        # If no clear lines, split by sentences
        if len(lines) <= 1:
            lines = [s.strip() for s in re.split(r"(?<=[.!?])\s+", src) if s.strip()]
        return "\n".join([f"- {l}" for l in lines[:max_items]])

    def _ensure_question(qtext: str, fallback: str) -> str:
        return qtext if "?" in qtext else fallback

    # Technical question shaping
    if path == "technical_question" or is_technical:
        body = domain_text or text
        bullets = _to_bullets(body, max_items=5)
        apply_q = "Where in your current scheme would this change your approach, and why?"
        return f"{bullets}\n\n{apply_q}"

    # Confusion expression shaping
    if path == "confusion_expression" or is_confusion:
        base = socratic_text or text
        if base.count("?") >= 2:
            return base
        clarifiers = [
            "What specific part feels unclear?",
            "Which aspect would help you move forward?"
        ]
        return f"{base}\n\n{clarifiers[0]}\n{clarifiers[1]}"

    # Multi-agent synthesis shaping
    if path in {"multi_agent_comprehensive", "balanced_guidance"}:
        header = "Synthesis:"

        def _first_sentence(s: str, max_len: int = 400) -> str:
            if not s:
                return ""
            sentences = re.split(r'[.!?]+', s)
            first = sentences[0].strip() if sentences else s
            return first[:max_len].rstrip()

        def _extract_insight(s: str, max_len: int = 800) -> str:
            """Extract a more substantial insight from domain expert response."""
            if not s:
                return ""

            # Split into sentences
            sentences = re.split(r'[.!?]+', s)
            sentences = [sent.strip() for sent in sentences if sent.strip()]

            if not sentences:
                return s[:max_len].rstrip()

            # Take first 2-3 sentences for a more substantial insight
            if len(sentences) >= 3:
                insight = '. '.join(sentences[:3]) + '.'
            elif len(sentences) >= 2:
                insight = '. '.join(sentences[:2]) + '.'
            else:
                insight = sentences[0] + '.'

            # Ensure it doesn't exceed max length
            if len(insight) > max_len:
                insight = insight[:max_len].rstrip()
                # Find last complete sentence within limit
                last_period = insight.rfind('.')
                if last_period > max_len * 0.7:  # If we have at least 70% of content
                    insight = insight[:last_period + 1]

            return insight

        items = []
        if domain_text:
            insight = _sanitize(_extract_insight(domain_text))
            if insight:
                items.append(f"- Insight: {insight}")
        if socratic_text:
            direction = _sanitize(_first_question(socratic_text))
            if direction and not direction.endswith("?"):
                direction = direction + "?"
            if direction:
                items.append(f"- Direction: {direction}")
        if cognitive_text:
            watch = _sanitize(_extract_insight(cognitive_text, max_len=600))  # Use extract_insight for Watch too
        else:
            # ENHANCED: Use context-aware fallback based on conversation content
            watch = "Consider how users will experience your architectural project at different times of the day and year"
        if watch:
            items.append(f"- Watch: {watch}")
        items = [it for it in items if it][:3]
        body = header + ("\n" + "\n".join(items) if items else "\n" + _first_sentence(text))
        next_action = "Next: test one concrete change and tell me what you notice."
        question = "What will you try first?"
        return f"{body}\n\n{next_action} {question}"

    # Default: return text as-is
    return text


