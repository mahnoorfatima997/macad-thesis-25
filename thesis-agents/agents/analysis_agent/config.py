"""
Configuration constants and settings for the Analysis Agent.
"""

from typing import Dict, List, Any

# Model configuration - ENHANCED: Updated to GPT-4o for better response quality
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 2000  # Increased for generous academic responses

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

# Building type detection patterns - Enhanced comprehensive classification
BUILDING_TYPE_PATTERNS = {
    # Educational & Learning
    "educational": ["school", "university", "college", "classroom", "educational", "learning", "academy", "institute"],
    "learning_center": ["learning center", "education center", "learning hub", "training center", "skill center", "knowledge center", "study center", "workshop center"],
    "library": ["library", "librarian", "reading room", "study space", "research center", "information center", "book center"],
    "research_facility": ["research facility", "laboratory", "lab", "research center", "innovation center", "development center", "testing facility"],
    
    # Community & Civic
    "community_center": ["community center", "community facility", "civic center", "public center", "social hub", "gathering place", "neighborhood center", "town hall"],
    "cultural_institution": ["museum", "gallery", "theater", "cultural center", "arts center", "performance center", "exhibition center", "cultural hub", "heritage center"],
    "recreation_center": ["recreation center", "sports center", "fitness center", "wellness center", "activity center", "leisure center", "entertainment center"],
    "senior_center": ["senior center", "elderly center", "aging center", "retirement center", "adult center", "mature center"],
    "youth_center": ["youth center", "teen center", "adolescent center", "young center", "teenager center"],
    
    # Healthcare & Wellness
    "hospital": ["hospital", "medical center", "health center", "clinic", "medical facility", "healthcare facility", "treatment center"],
    "specialized_clinic": ["specialized clinic", "specialty clinic", "medical clinic", "health clinic", "outpatient clinic", "diagnostic center"],
    "wellness_center": ["wellness center", "health center", "medical spa", "holistic center", "alternative medicine", "wellness facility"],
    "rehabilitation_center": ["rehabilitation center", "rehab center", "recovery center", "therapy center", "treatment facility"],
    
    # Commercial & Business
    "office": ["office", "workplace", "corporate", "business", "commercial", "workspace", "professional", "executive"],
    "retail": ["store", "shop", "retail", "commercial", "market", "shopping", "merchant", "boutique"],
    "restaurant": ["restaurant", "cafe", "dining", "eatery", "bistro", "food service", "culinary", "dining establishment"],
    "hotel": ["hotel", "lodging", "accommodation", "inn", "resort", "guesthouse", "hostel", "bed and breakfast"],
    
    # Residential
    "residential": ["house", "home", "apartment", "residential", "housing", "dwelling", "residence", "domestic"],
    "multi_family": ["multi-family", "apartment building", "condominium", "townhouse", "duplex", "triplex", "residential complex"],
    "senior_housing": ["senior housing", "elderly housing", "retirement community", "assisted living", "nursing home", "care facility"],
    "student_housing": ["student housing", "dormitory", "student residence", "college housing", "university housing"],
    
    # Industrial & Manufacturing
    "industrial": ["factory", "warehouse", "industrial", "manufacturing", "production", "industrial facility", "manufacturing plant"],
    "logistics_center": ["logistics center", "distribution center", "fulfillment center", "storage facility", "warehouse facility"],
    "research_industrial": ["research and development", "R&D facility", "innovation center", "technology center", "development facility"],
    
    # Transportation & Infrastructure
    "transportation_hub": ["transportation hub", "transit center", "transport hub", "mobility center", "travel center"],
    "parking_facility": ["parking facility", "parking garage", "parking structure", "parking center", "car park"],
    "maintenance_facility": ["maintenance facility", "service center", "repair facility", "maintenance center"],
    
    # Religious & Spiritual
    "religious": ["church", "temple", "mosque", "synagogue", "religious", "worship", "spiritual", "sacred", "faith center"],
    "meditation_center": ["meditation center", "spiritual center", "zen center", "mindfulness center", "contemplation center"],
    
    # Agricultural & Environmental
    "agricultural": ["farm", "agricultural", "greenhouse", "nursery", "agricultural facility", "farming center"],
    "environmental_center": ["environmental center", "nature center", "conservation center", "ecology center", "sustainability center"],
    
    # Mixed-Use & Specialized
    "mixed_use": ["mixed use", "multi-use", "combined use", "integrated", "hybrid", "versatile", "flexible"],
    "conference_center": ["conference center", "convention center", "meeting center", "event center", "summit center"],
    "innovation_hub": ["innovation hub", "startup center", "entrepreneurial center", "business incubator", "tech hub"],
    "creative_workspace": ["creative workspace", "artist studio", "design studio", "creative center", "artistic space"],
    
    # Government & Public
    "government": ["government building", "civic building", "public building", "administrative center", "public service"],
    "emergency_services": ["fire station", "police station", "emergency center", "public safety", "emergency facility"],
    "utility_facility": ["utility facility", "power plant", "water treatment", "energy center", "infrastructure facility"]
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