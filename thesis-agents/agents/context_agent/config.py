"""
Configuration constants and settings for the Context Agent.
"""

from typing import Dict, List, Any

# Model configuration - ENHANCED: Updated to GPT-4o for better response quality
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 1200  # Increased for generous academic responses

# Analysis patterns for different types of student input
ANALYSIS_PATTERNS = {
    "question_patterns": [
        "what", "how", "why", "when", "where", "which", "who",
        "can you", "could you", "would you", "should i", "do i need",
        "is it", "are there", "does this", "help me"
    ],
    "statement_patterns": [
        "i think", "i believe", "i want", "i need", "i'm trying",
        "my idea", "my plan", "i decided", "i chose", "i selected"
    ],
    "confusion_patterns": [
        "i don't understand", "i'm confused", "unclear", "not sure",
        "don't know", "help", "stuck", "lost", "difficult"
    ],
    "confidence_patterns": [
        "i know", "obviously", "clearly", "definitely", "certainly",
        "of course", "sure", "confident", "easy", "simple"
    ],
    "exploration_patterns": [
        "what if", "maybe", "perhaps", "could", "might", "possibly",
        "considering", "thinking about", "exploring", "investigating"
    ],
    "feedback_request_patterns": [
        "what do you think", "feedback", "thoughts", "opinion",
        "review", "check", "evaluate", "assess", "critique"
    ]
}

# Technical architectural terms for complexity assessment
TECHNICAL_TERMS = [
    "accessibility", "ada", "building code", "zoning", "egress",
    "circulation", "wayfinding", "spatial", "adjacency", "program",
    "massing", "facade", "envelope", "thermal", "hvac", "structural",
    "foundation", "framing", "sustainability", "leed", "energy",
    "daylighting", "acoustics", "materials", "finishes", "detailing"
]

# Emotional indicators for engagement assessment
EMOTIONAL_INDICATORS = {
    "positive": ["excited", "love", "great", "amazing", "wonderful", "fantastic"],
    "negative": ["frustrated", "hate", "terrible", "awful", "horrible", "annoying"],
    "neutral": ["okay", "fine", "alright", "decent", "acceptable", "reasonable"],
    "enthusiasm": ["passionate", "enthusiastic", "eager", "motivated", "inspired"],
    "concern": ["worried", "concerned", "anxious", "nervous", "uncertain"]
}

# Design phase indicators
DESIGN_PHASE_INDICATORS = {
    "ideation": [
        "concept", "idea", "brainstorm", "initial", "starting", "beginning",
        "explore", "research", "investigate", "understand", "analyze"
    ],
    "development": [
        "develop", "refine", "detail", "elaborate", "expand", "improve",
        "iterate", "modify", "adjust", "enhance", "optimize"
    ],
    "resolution": [
        "finalize", "complete", "finish", "resolve", "decide", "conclude",
        "implement", "execute", "deliver", "present", "submit"
    ]
}

# Interaction type classifications
INTERACTION_TYPES = {
    "question": "Student is asking for information or clarification",
    "statement": "Student is sharing their thoughts or decisions",
    "exploration": "Student is exploring possibilities or options",
    "feedback_request": "Student is seeking evaluation or critique",
    "confusion": "Student is expressing uncertainty or lack of understanding",
    "progress_update": "Student is reporting on their progress",
    "reflection": "Student is reflecting on their learning or process"
}

# Understanding levels
UNDERSTANDING_LEVELS = ["novice", "developing", "proficient", "advanced"]

# Confidence levels
CONFIDENCE_LEVELS = ["low", "moderate", "high", "overconfident"]

# Engagement levels
ENGAGEMENT_LEVELS = ["disengaged", "passive", "active", "highly_engaged"]

# Complexity assessment thresholds
COMPLEXITY_THRESHOLDS = {
    "word_count_low": 10,
    "word_count_high": 50,
    "technical_terms_low": 2,
    "technical_terms_high": 5,
    "sentence_complexity_threshold": 15
}

# Response urgency levels
URGENCY_LEVELS = ["low", "normal", "high", "immediate"]

# Pedagogical opportunity types
PEDAGOGICAL_OPPORTUNITIES = [
    "socratic_questioning",
    "knowledge_building",
    "skill_development",
    "reflection_prompting",
    "challenge_introduction",
    "concept_connection"
]

# Routing suggestions configuration
ROUTING_CONFIG = {
    "primary_agent_threshold": 0.7,
    "secondary_agent_threshold": 0.5,
    "confidence_threshold": 0.6,
    "max_agents": 3
}

# Context quality thresholds
CONTEXT_QUALITY_THRESHOLDS = {
    "excellent": 0.8,
    "good": 0.6,
    "fair": 0.4,
    "poor": 0.2
}

# Conversation pattern analysis settings
PATTERN_ANALYSIS = {
    "repetition_threshold": 3,  # Number of similar topics to consider repetitive
    "topic_jump_threshold": 4,  # Number of different topics in recent messages
    "engagement_window": 5,     # Number of recent messages to analyze for engagement
    "understanding_window": 7   # Number of messages to analyze for understanding progression
} 