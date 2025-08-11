"""
Configuration constants and settings for the Cognitive Enhancement Agent.
"""

from typing import Dict, List, Any

# Model configuration - ENHANCED: Updated to GPT-4o-mini per FROMOLDREPO
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.6
MAX_TOKENS = 1200  # Increased for generous academic responses

# Cognitive metrics thresholds
COGNITIVE_THRESHOLDS = {
    "engagement": {
        "high": 0.7,
        "medium": 0.4,
        "low": 0.0
    },
    "complexity": {
        "high": 0.8,
        "medium": 0.5,
        "low": 0.0
    },
    "reflection": {
        "high": 0.7,
        "medium": 0.4,
        "low": 0.0
    },
    "cognitive_load": {
        "overload": 0.8,
        "optimal": 0.6,
        "underload": 0.3
    }
}

# Challenge templates for different types of cognitive interventions
CHALLENGE_TEMPLATES = {
    "constraint_challenges": {
        "space": [
            "What if your available space was reduced by 30%? How would this change your priorities?",
            "Consider you only had half the square footage. What would be most essential to keep?",
            "If you had to design in a narrow, linear space, how would your approach change?"
        ],
        "budget": [
            "With a significantly reduced budget, what would you prioritize and why?",
            "If you could only afford three key design elements, which would you choose?",
            "How would you achieve your design goals with basic materials?"
        ],
        "time": [
            "If this project had to be completed in half the time, what would change?",
            "What if you had unlimited time? Would your approach be different?",
            "Consider the long-term maintenance implications of your choices."
        ]
    },
    "perspective_challenges": {
        "user_groups": [
            "How would a person using a wheelchair experience your design differently?",
            "Consider how children versus elderly users might interact with your space.",
            "What would someone from a different cultural background think of your approach?"
        ],
        "professionals": [
            "How might a structural engineer view your proposal?",
            "What concerns might a building code official raise?",
            "How would a facilities manager evaluate your design?"
        ],
        "temporal": [
            "How will your design age over the next 20 years?",
            "What if technology changes significantly during construction?",
            "Consider how seasonal changes might affect your design."
        ]
    },
    "alternative_challenges": {
        "approach": [
            "What's the opposite approach to what you're proposing? Could it work?",
            "If you had to achieve the same goals with completely different methods, what would you do?",
            "Consider three radically different ways to solve this problem."
        ],
        "precedent": [
            "What if this type of building didn't exist before? How would you invent it?",
            "Look at a completely different building type. What can you learn from it?",
            "How would architects from a different era approach this?"
        ],
        "scale": [
            "What if this was 10 times larger? What would change?",
            "Consider this at the scale of a single room. What's essential?",
            "How would your solution work in a different climate?"
        ]
    },
    "metacognitive_challenges": {
        "assumptions": [
            "What assumptions are you making that might not be true?",
            "What do you take for granted in your approach?",
            "What biases might be influencing your decisions?"
        ],
        "process": [
            "How did you arrive at this solution? Walk through your thinking.",
            "What other options did you consider and why did you reject them?",
            "What would you do differently if you started over?"
        ],
        "evaluation": [
            "How will you know if your design is successful?",
            "What criteria are you using to evaluate your choices?",
            "What might you be overlooking or missing?"
        ]
    }
}

# Backward-compatibility aliases (singular keys expected by processors)
CHALLENGE_TEMPLATES["constraint_challenge"] = CHALLENGE_TEMPLATES.get("constraint_challenges", {})
CHALLENGE_TEMPLATES["perspective_challenge"] = CHALLENGE_TEMPLATES.get("perspective_challenges", {})
CHALLENGE_TEMPLATES["alternative_challenge"] = CHALLENGE_TEMPLATES.get("alternative_challenges", {})
CHALLENGE_TEMPLATES["metacognitive_challenge"] = CHALLENGE_TEMPLATES.get("metacognitive_challenges", {})

# Enhancement strategies based on cognitive state
ENHANCEMENT_STRATEGIES = {
    "high_engagement_low_complexity": "increase_challenge",
    "low_engagement_high_complexity": "reduce_cognitive_load",
    "high_overconfidence": "challenge_assumptions",
    "high_passivity": "increase_engagement",
    "low_metacognition": "promote_reflection",
    "shallow_thinking": "deepen_analysis",
    "repetitive_patterns": "encourage_exploration"
}

# Cognitive offloading patterns to detect
OFFLOADING_PATTERNS = {
    "premature_example_seeking": {
        "indicators": ["show me", "give me examples", "what should I do"],
        "threshold": 3,  # messages
        "intervention": "socratic_questioning"
    },
    "direct_answer_seeking": {
        "indicators": ["tell me the answer", "what's the solution", "just tell me"],
        "threshold": 1,
        "intervention": "constraint_challenge"
    },
    "passive_acceptance": {
        "indicators": ["ok", "sure", "that's fine", "whatever"],
        "threshold": 2,
        "intervention": "perspective_challenge"
    },
    "overconfident_dismissal": {
        "indicators": ["obviously", "clearly", "definitely", "of course"],
        "threshold": 2,
        "intervention": "alternative_challenge"
    }
}

# Scientific metrics configuration
SCIENTIFIC_METRICS = {
    "baseline_scores": {
        "engagement": 0.5,
        "complexity": 0.5,
        "reflection": 0.5,
        "cognitive_load": 0.5
    },
    "improvement_thresholds": {
        "significant": 0.2,
        "moderate": 0.1,
        "minimal": 0.05
    },
    "confidence_levels": {
        "high": 0.8,
        "medium": 0.6,
        "low": 0.4
    }
}

# Phase-specific cognitive demands
PHASE_DEMANDS = {
    "ideation": {
        "focus": "creative_thinking",
        "demands": "divergent thinking, exploration, concept generation",
        "duration": "weeks to months",
        "indicators": ["brainstorming", "exploring", "conceptualizing", "researching"]
    },
    "development": {
        "focus": "analytical_thinking", 
        "demands": "convergent thinking, decision-making, refinement",
        "duration": "months",
        "indicators": ["developing", "refining", "analyzing", "optimizing"]
    },
    "resolution": {
        "focus": "implementation_thinking",
        "demands": "technical thinking, problem-solving, finalization",
        "duration": "weeks to months", 
        "indicators": ["finalizing", "implementing", "detailing", "completing"]
    }
}

# Engagement indicators
ENGAGEMENT_INDICATORS = {
    "high": [
        "curious", "interested", "exploring", "wondering", "what if",
        "excited", "passionate", "engaged", "motivated", "inspired"
    ],
    "medium": [
        "thinking", "considering", "looking at", "working on", "trying"
    ],
    "low": [
        "ok", "sure", "fine", "whatever", "i guess", "boring", "tired"
    ]
}

# Complexity indicators
COMPLEXITY_INDICATORS = {
    "high": [
        "complex", "complicated", "sophisticated", "intricate", "multifaceted",
        "challenging", "demanding", "advanced", "comprehensive"
    ],
    "medium": [
        "moderate", "balanced", "reasonable", "appropriate", "manageable"
    ],
    "low": [
        "simple", "basic", "easy", "straightforward", "elementary", "minimal"
    ]
}

# Metacognitive awareness indicators
METACOGNITIVE_INDICATORS = {
    "high": [
        "i think", "i believe", "i'm considering", "i realize", "i understand",
        "reflecting on", "thinking about", "aware that", "conscious of"
    ],
    "medium": [
        "maybe", "perhaps", "could be", "might", "possibly"
    ],
    "low": [
        "don't know", "unsure", "confused", "unclear", "lost"
    ]
} 