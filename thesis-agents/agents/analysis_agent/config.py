"""
Configuration constants and settings for the Analysis Agent.
"""

from typing import Dict, List, Any

# Model configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 1500

# Phase detection configuration
PHASE_INDICATORS = {
    "ideation": {
        "conversation_indicators": [
            "concept", "idea", "approach", "strategy", "vision", "philosophy",
            "what if", "how might", "explore", "consider", "think about",
            "precedent", "inspiration", "reference", "example", "case study",
            "user needs", "program", "function", "purpose", "goal",
            "site analysis", "context", "environment", "climate", "culture"
        ],
        "visual_indicators": [
            "concept sketch", "bubble diagram", "program diagram", "site analysis",
            "mood board", "inspiration images", "rough sketches", "flow diagrams"
        ],
        "design_indicators": [
            "program development", "concept exploration", "site understanding",
            "user research", "precedent study", "design philosophy"
        ]
    },
    "visualization": {
        "conversation_indicators": [
            "form", "shape", "massing", "volume", "proportion", "scale",
            "circulation", "flow", "layout", "plan", "section", "elevation",
            "spatial relationship", "adjacency", "hierarchy", "organization",
            "sketch", "drawing", "model", "3d", "perspective", "rendering",
            "light", "shadow", "material", "texture", "color", "atmosphere",
            # Enhanced technical design terms that indicate visualization phase
            "orientation", "shading", "glazing", "atrium", "light wells", 
            "work zones", "meeting areas", "ventilation", "daylight",
            "energy efficiency", "natural lighting", "collaborative environment",
            "open spaces", "flexible spaces", "central space", "shared systems",
            "district heating", "solar panels", "high-performance", "smart glass",
            "adjustable blinds", "indoor green", "casual meeting", "open work"
        ],
        "visual_indicators": [
            "floor plan", "site plan", "section", "elevation", "3d model",
            "massing study", "spatial diagram", "circulation diagram",
            "lighting study", "material study", "rendering", "perspective"
        ],
        "design_indicators": [
            "spatial development", "form exploration", "circulation design",
            "proportion study", "lighting design", "material exploration"
        ]
    },
    "materialization": {
        "conversation_indicators": [
            "construction", "structure", "system", "detail", "joint", "connection",
            "material specification", "assembly", "fabrication", "installation",
            "technical", "engineering", "performance", "efficiency", "sustainability",
            "code", "regulation", "standard", "requirement", "specification",
            "cost", "budget", "timeline", "schedule", "phasing", "implementation"
        ],
        "visual_indicators": [
            "construction detail", "structural diagram", "building section",
            "material specification", "assembly detail", "technical drawing",
            "sustainability diagram", "performance analysis", "cost analysis"
        ],
        "design_indicators": [
            "technical development", "construction methodology", "material specification",
            "performance optimization", "cost analysis", "implementation planning"
        ]
    }
}

# Phase detection weights
PHASE_WEIGHTS = {
    "conversation_weight": 0.4,
    "visual_weight": 0.3,
    "design_weight": 0.2,
    "temporal_weight": 0.1,
    "confidence_threshold": 0.6
}

# Skill level indicators
SKILL_INDICATORS = {
    "beginner": [
        "don't know", "confused", "help", "what is", "how do", "basic", 
        "simple", "easy", "first time", "new to", "learning", "beginner"
    ],
    "intermediate": [
        "accessibility", "circulation", "programming", "design", "space", 
        "layout", "plan", "consider", "think about", "approach", "community",
        "building", "rooms", "areas", "entrance", "windows", "doors"
    ],
    "advanced": [
        "parti", "phenomenology", "tectonics", "typology", "morphology",
        "zoning", "egress", "life safety", "building codes", "structural systems",
        "environmental systems", "sustainable", "LEED", "passive design",
        "urban context", "precedent", "critical regionalism", "threshold",
        "spatial sequence", "materiality", "site analysis"
    ]
}

# Cognitive flags configuration
COGNITIVE_FLAGS = {
    "overwhelmed_by_complexity": {
        "indicators": ["too much", "overwhelming", "complex", "difficult", "confusing"],
        "threshold": 2
    },
    "needs_deeper_exploration": {
        "indicators": ["surface", "shallow", "quick", "basic", "simple"],
        "threshold": 1
    },
    "ready_for_challenge": {
        "indicators": ["understand", "clear", "ready", "next", "more"],
        "threshold": 2
    },
    "requires_scaffolding": {
        "indicators": ["help", "guidance", "support", "stuck", "unsure"],
        "threshold": 1
    }
}

# Analysis thresholds
SKILL_ASSESSMENT_THRESHOLDS = {
    "advanced_ratio": 0.1,  # Advanced terms per message
    "min_sentence_length": 15,  # For advanced classification
    "beginner_sentence_length": 6,  # For beginner classification
    "confidence_messages": 5,  # Messages needed for high confidence
    "confidence_words": 100  # Words needed for high confidence
}

# Phase progression thresholds
PHASE_PROGRESSION_THRESHOLDS = {
    "min_confidence": 0.6,
    "progression_ready": 0.8,
    "milestone_weight": 0.3,
    "temporal_decay": 0.1  # How much older messages matter less
}

# Building type detection patterns
BUILDING_TYPE_PATTERNS = {
    "office": ["office", "workplace", "corporate", "business", "commercial", "workspace"],
    "residential": ["house", "home", "apartment", "residential", "housing", "dwelling"],
    "educational": ["school", "university", "college", "classroom", "educational", "learning"],
    "cultural": ["museum", "gallery", "theater", "cultural", "arts", "performance"],
    "healthcare": ["hospital", "clinic", "medical", "healthcare", "health"],
    "retail": ["store", "shop", "retail", "commercial", "market"],
    "mixed_use": ["mixed", "multi", "combined", "various", "multiple"],
    "community": ["community", "civic", "public", "social", "gathering"]
}

# Detail level detection patterns for briefs
# Used by TextAnalysisProcessor.assess_detail_level
DETAIL_LEVEL_PATTERNS = {
    "low": [
        "brief", "short", "simple", "basic", "overview", "initial",
        "idea", "concept", "sketch"
    ],
    "medium": [
        "requirements", "program", "constraints", "materials", "context",
        "users", "lighting", "circulation", "layout", "functions"
    ],
    "high": [
        "dimensions", "specifications", "codes", "regulations", "structure",
        "hvac", "mep", "tolerances", "performance", "compliance"
    ],
}

# Cognitive pattern indicators used by SynthesisProcessor and related analyses
COGNITIVE_PATTERNS = {
    "engagement": [
        "interested", "curious", "explore", "learn more", "let's try",
        "I tried", "experiment", "iterate", "build on"
    ],
    "confidence": [
        "I think", "I believe", "I'm confident", "clear", "sure",
        "definitely", "obviously"
    ],
    "confusion": [
        "confused", "don't understand", "unclear", "stuck", "help",
        "not sure", "lost"
    ],
    "frustration": [
        "frustrated", "annoyed", "difficult", "hard", "overwhelmed",
        "too much"
    ],
}

# Response generation limits
RESPONSE_LIMITS = {
    "max_response_length": 800,
    "min_response_length": 100,
    "max_recommendations": 5,
    "max_cognitive_flags": 3
}

# Knowledge enhancement settings
KNOWLEDGE_ENHANCEMENT = {
    "max_context_length": 2000,
    "similarity_threshold": 0.7,
    "max_knowledge_items": 3
} 