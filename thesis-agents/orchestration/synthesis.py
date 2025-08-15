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

    # Multi-agent synthesis shaping - ALWAYS apply synthesis template for balanced_guidance
    if path in {"multi_agent_comprehensive", "balanced_guidance", "knowledge_with_challenge"}:
        # For balanced_guidance, ALWAYS use the synthesis template to ensure consistent format
        if path == "balanced_guidance":
            # Skip the content length check and go directly to synthesis template
            pass
        else:
            # For other paths, check if we already have substantial content from agents
            total_content_length = len(domain_text) + len(socratic_text) + len(cognitive_text)

            # If we have good content from agents, ensure it ends with a Socratic question
            if total_content_length > 100:  # Agents provided substantial responses
                # CRITICAL FIX: Ensure Socratic question is included
                if not text.strip().endswith('?'):
                    # Extract Socratic question from socratic agent result
                    socratic_result = ordered_results.get("socratic", {})
                    if hasattr(socratic_result, 'to_dict'):
                        socratic_result = socratic_result.to_dict()

                    socratic_question = socratic_result.get("question_text", "")
                    if not socratic_question:
                        # Look in metadata
                        metadata = socratic_result.get("metadata", {})
                        socratic_question = metadata.get("socratic_question", "")

                    # Add the question if found and not already in text
                    if socratic_question and socratic_question not in text:
                        text = f"{text}\n\n{socratic_question}"
                    elif not socratic_question:
                        # Generate contextual follow-up question
                        text = f"{text}\n\nWhat aspects of this would you like to explore further?"

                return text

        # Use synthesis template for balanced_guidance and as fallback for others
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

        def _generate_contextual_question(user_input: str, domain_text: str) -> str:
            """Generate a contextual question based on what the user actually asked."""
            user_input_lower = user_input.lower()

            # Check if user is asking about placement/organization
            if any(word in user_input_lower for word in ["place", "organize", "layout", "arrange", "position", "where"]):
                if "outdoor" in user_input_lower or "garden" in user_input_lower or "courtyard" in user_input_lower:
                    return "Which of these placement strategies feels most aligned with your vision for the learning environment?"
                else:
                    return "How do you envision the relationship between these different spaces?"

            # Check if user is asking about approach/strategy
            elif any(word in user_input_lower for word in ["approach", "strategy", "method", "how", "what should"]):
                return "What aspect of this approach resonates most with your design goals?"

            # Check if user is asking about examples/references
            elif any(word in user_input_lower for word in ["example", "reference", "precedent", "case study"]):
                return "Which of these examples best fits your project's context and requirements?"

            # Default contextual question
            return "How does this information help you move forward with your design?"

        def _generate_building_type_specific_watch(building_type: str) -> str:
            """Generate building-type specific watch items instead of generic fallbacks."""
            building_type_lower = building_type.lower()

            if "community" in building_type_lower or "sports" in building_type_lower:
                return "Consider circulation patterns, user flow, and how spaces can adapt between different activities and times of day"
            elif "learning" in building_type_lower or "educational" in building_type_lower:
                return "Consider how the learning environment supports different teaching methods and student needs"
            elif "residential" in building_type_lower:
                return "Consider how the space supports daily living patterns and personal comfort"
            elif "cultural" in building_type_lower or "museum" in building_type_lower:
                return "Consider how the space enhances visitor experience and showcases exhibits effectively"
            elif "healthcare" in building_type_lower or "medical" in building_type_lower:
                return "Consider patient comfort, staff efficiency, and infection control requirements"
            elif "office" in building_type_lower or "commercial" in building_type_lower:
                return "Consider workflow efficiency, collaboration opportunities, and professional atmosphere"
            else:
                return "Consider how users will experience your architectural project at different times of the day and year"

        items = []

        # Generate Insight from domain expert or fallback
        if domain_text:
            insight = _sanitize(_extract_insight(domain_text))
        else:
            # Generate fallback insight based on user input
            user_input = classification.get("user_input", "") if classification else ""
            building_type = context_analysis.get("building_type", "architectural project")
            insight = f"Organizing spaces in a {building_type} requires careful consideration of user flow, functional relationships, and spatial hierarchy"

        if insight:
            items.append(f"- Insight: {insight}")

        # Generate Direction from socratic agent or fallback
        if socratic_text:
            direction = _sanitize(_first_question(socratic_text))
            if direction and not direction.endswith("?"):
                direction = direction + "?"
        else:
            # Generate fallback direction question
            user_input = classification.get("user_input", "") if classification else ""
            direction = _generate_contextual_question(user_input, domain_text)

        if direction:
            items.append(f"- Direction: {direction}")

        # Generate Watch from cognitive agent or fallback
        if cognitive_text:
            watch = _sanitize(_extract_insight(cognitive_text, max_len=600))
        else:
            # ENHANCED: Use building-type specific fallback instead of generic one
            building_type = context_analysis.get("building_type", "mixed_use")
            watch = _generate_building_type_specific_watch(building_type)

        if watch:
            items.append(f"- Watch: {watch}")

        # Ensure we have at least the basic structure
        items = [it for it in items if it][:3]
        if not items:
            items = [f"- Insight: {_first_sentence(text) or 'Let me help you explore this design challenge'}"]

        body = header + "\n" + "\n".join(items)

        # ENHANCED: Generate contextual question instead of hardcoded generic ones
        user_input = classification.get("user_input", "") if classification else ""
        contextual_question = _generate_contextual_question(user_input, domain_text)

        # Ensure we always have a question
        if not contextual_question or not contextual_question.strip().endswith('?'):
            contextual_question = "How does this information help you move forward with your design?"

        return f"{body}\n\n{contextual_question}"

    # Default: return text as-is
    return text


