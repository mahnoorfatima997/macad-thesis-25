"""
Configuration constants and settings for the Socratic Tutor Agent.
"""
from typing import Dict, List, Any

# LLM Configuration - ENHANCED: Updated to GPT-4o for better response quality
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.4
MAX_TOKENS = 1500  # Increased for generous academic responses

# Socratic Method Configuration
QUESTION_MAX_WORDS = 30
# REMOVED: FALLBACK_QUESTION - now using LLM-generated fallbacks instead of hardcoded ones

# Question Types
QUESTION_TYPES = {
    'clarifying': 'Help students articulate their thinking clearly',
    'assumption_challenging': 'Question underlying beliefs and assumptions',
    'evidence': 'Ask for supporting reasoning and evidence',
    'perspective': 'Encourage viewing from different angles',
    'implication': 'Explore consequences of design decisions',
    'socratic': 'Classic Socratic questioning approach',
    'fallback': 'General exploratory question'
}

# Pedagogical Intents Based on Student State
PEDAGOGICAL_INTENTS = {
    'overconfident': 'Challenge assumptions and encourage critical thinking',
    'uncertain': 'Build confidence through guided discovery',
    'confusion': 'Clarify understanding through structured questioning',
    'default': 'Guide learning through thoughtful inquiry'
}

# Question Generation Guidelines
QUESTION_GUIDELINES = [
    "Ask ONE specific question that encourages deeper thinking",
    "Don't give answers - guide them to discover insights",
    "Connect to their specific project context",
    "Match their understanding level",
    "If they're overconfident, ask challenging questions",
    "If they're uncertain, ask supportive, clarifying questions",
    "Keep it under 30 words"
]

# Enhancement Metrics Configuration
ENHANCEMENT_METRICS = {
    'socratic_question': {
        'cognitive_offloading_prevention_score': 0.8,
        'deep_thinking_engagement_score': 0.9,
        'knowledge_integration_score': 0.6,
        'scaffolding_effectiveness_score': 0.8,
        'learning_progression_score': 0.6,
        'metacognitive_awareness_score': 0.9,
        'scientific_confidence': 0.8
    },
    'fallback_question': {
        'cognitive_offloading_prevention_score': 0.6,
        'deep_thinking_engagement_score': 0.7,
        'knowledge_integration_score': 0.6,
        'scaffolding_effectiveness_score': 0.7,
        'learning_progression_score': 0.6,
        'metacognitive_awareness_score': 0.6,
        'scientific_confidence': 0.8
    }
}

# Cognitive Flags Mapping
COGNITIVE_FLAGS_MAPPING = {
    'deep_thinking_encouraged': 'DEEP_THINKING_ENCOURAGED',
    'assumption_challenged': 'DEEP_THINKING_ENCOURAGED',
    'scaffolding_provided': 'SCAFFOLDING_PROVIDED',
    'metacognitive_awareness': 'METACOGNITIVE_AWARENESS'
}

# System Messages
SYSTEM_MESSAGE = "You are a distinguished architectural educator and scholar employing the Socratic method to advance student learning through rigorous intellectual inquiry."

# Advanced Question Prompts Template
QUESTION_PROMPT_TEMPLATE = """
You are an accomplished architectural theorist and educator employing sophisticated Socratic pedagogy to advance graduate-level design thinking. Your questions should challenge assumptions, reveal hidden complexities, and connect local design decisions to broader architectural discourse.

STUDENT INQUIRY: "{user_input}"
PROJECT CONTEXT: {project_context}
INTERACTION TYPE: {interaction_type}
UNDERSTANDING LEVEL: {understanding_level}
CONFIDENCE LEVEL: {confidence_level}
KNOWLEDGE DOMAIN: {gap_type}

Advanced Pedagogical Guidelines:
{guidelines}

Craft a sophisticated Socratic question that operates at multiple levels:

THEORETICAL DEPTH: Connect their inquiry to broader architectural theory, critical discourse, or methodological frameworks. Reference specific theorists, movements, or contemporary debates when relevant.

MULTI-SCALAR THINKING: Challenge them to consider how their design decisions operate across scales - from detail to building to urban to territorial implications.

INTERDISCIPLINARY CONNECTIONS: Prompt them to consider structural, environmental, social, economic, or cultural dimensions that intersect with their inquiry.

ASSUMPTION CHALLENGING: Identify and question the underlying assumptions in their approach or the conventional wisdom in their domain.

CONTEMPORARY RELEVANCE: Connect their thinking to current architectural challenges - climate change, social equity, technological innovation, changing work patterns, etc.

PRECEDENT INTERROGATION: If they reference examples, ask them to analyze WHY those precedents work, not just WHAT they do.

Generate ONE incisive question (under 35 words) that advances their critical thinking:
"""