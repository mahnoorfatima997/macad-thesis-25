"""
Configuration constants and settings for the Domain Expert Agent.
"""

from typing import Dict, List, Any

# Model configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 1500  # Increased for generous academic responses

# Enhanced architectural sources for better search results
ARCHITECTURAL_SOURCES = [
    "site:dezeen.com", "site:archdaily.com", "site:archello.com", 
    "site:architectural-review.com", "site:architecturaldigest.com", 
    "site:architectmagazine.com", "site:architecturalrecord.com",
    "site:architect.org", "site:aia.org", "site:architecturalleague.org",
    "site:architecturalfoundation.org", "site:architecturalassociation.org.uk",
    "site:architecturalrecord.com", "site:architecturaldigest.com"
]

# Comprehensive architectural keyword configuration for flexible detection
ARCHITECTURAL_KEYWORDS = {
    "building_types": {
        "residential": [
            "house", "home", "apartment", "condo", "townhouse", "villa", "mansion", "cottage", 
            "bungalow", "duplex", "triplex", "penthouse", "loft", "studio", "dormitory", "residence"
        ],
        "commercial": [
            "office", "retail", "shop", "store", "mall", "market", "restaurant", "cafe", "hotel", 
            "motel", "inn", "resort", "spa", "gym", "fitness", "cinema", "theater", "auditorium", 
            "conference", "exhibition", "gallery", "showroom", "warehouse", "factory", "industrial"
        ],
        "institutional": [
            "school", "university", "college", "academy", "institute", "hospital", "clinic", 
            "medical", "library", "museum", "archive", "courthouse", "city hall", "government", 
            "police", "fire station", "post office", "bank", "church", "temple", "mosque", "synagogue"
        ],
        "community": [
            "community center", "community hall", "recreation center", "youth center", "senior center",
            "cultural center", "arts center", "performance center", "multipurpose", "civic center",
            "town hall", "meeting hall", "assembly hall", "convention center", "exhibition center"
        ],
        "transportation": [
            "airport", "train station", "bus station", "metro", "subway", "terminal", "depot",
            "garage", "parking", "bridge", "tunnel", "port", "marina"
        ],
        "mixed_use": [
            "mixed use", "mixed-use", "live work", "live-work", "commercial residential",
            "retail residential", "office residential", "integrated", "complex", "development"
        ]
    },
    "building_elements": [
        "building", "structure", "facility", "center", "complex", "tower", "block", "wing",
        "annex", "extension", "addition", "renovation", "conversion", "adaptive reuse",
        "repurposing", "retrofitting", "rehabilitation", "restoration", "preservation"
    ],
    "landscape_types": [
        "landscape", "park", "garden", "outdoor", "public space", "plaza", "square", "courtyard",
        "terrace", "rooftop garden", "green roof", "urban park", "botanical garden", "arboretum",
        "playground", "sports field", "athletic", "recreation area", "trail", "pathway", "walkway",
        "promenade", "esplanade", "boulevard", "street", "alley", "pedestrian", "bike path"
    ],
    "urban_elements": [
        "urban", "city", "downtown", "neighborhood", "district", "zone", "area", "precinct",
        "quarter", "block", "street", "avenue", "road", "highway", "infrastructure", "utilities"
    ]
}

# Search configuration
SEARCH_CONFIG = {
    "max_results": 10,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "fallback_enabled": True
}

# Web search configuration (alias used by processors)
WEB_SEARCH_CONFIG = {
    "providers": ["serpapi", "bing", "google"],
    "max_results": SEARCH_CONFIG["max_results"],
    "timeout_seconds": SEARCH_CONFIG["timeout_seconds"],
    "retry_attempts": SEARCH_CONFIG["retry_attempts"],
}

# Supported search engines (alias used by processors)
SEARCH_ENGINES = ["serpapi", "bing", "google"]

# Knowledge domains (alias used by processors)
KNOWLEDGE_DOMAINS = {
    "architecture": ARCHITECTURAL_SOURCES,
}

# Knowledge synthesis configuration
SYNTHESIS_CONFIG = {
    "max_knowledge_items": 5,
    "relevance_threshold": 0.7,
    "max_response_length": 800,
    "include_sources": True
}

# Gap type configurations
GAP_TYPES = {
    "knowledge_gap": {
        "description": "Student needs domain knowledge",
        "response_focus": "educational_content",
        "max_examples": 3
    },
    "example_gap": {
        "description": "Student needs concrete examples",
        "response_focus": "practical_examples", 
        "max_examples": 5
    },
    "technical_gap": {
        "description": "Student needs technical information",
        "response_focus": "technical_details",
        "max_examples": 2
    },
    "conceptual_gap": {
        "description": "Student needs conceptual understanding",
        "response_focus": "conceptual_explanation",
        "max_examples": 3
    }
}

# Response generation limits
RESPONSE_LIMITS = {
    "max_response_length": 1000,
    "min_response_length": 150,
    "max_examples": 5,
    "max_sources": 3
}

# Fallback knowledge templates
FALLBACK_KNOWLEDGE_TEMPLATES = {
    "accessibility": {
        "title": "Universal Design Principles",
        "content": "Consider ramps, wide doorways, accessible restrooms, and clear wayfinding for all users.",
        "examples": ["ADA-compliant entrances", "Accessible parking spaces", "Tactile guidance systems"]
    },
    "sustainability": {
        "title": "Sustainable Design Strategies", 
        "content": "Focus on energy efficiency, natural lighting, renewable materials, and environmental impact.",
        "examples": ["Solar panels", "Green roofs", "Passive cooling systems"]
    },
    "circulation": {
        "title": "Circulation Design Principles",
        "content": "Plan efficient movement patterns, clear wayfinding, and appropriate corridor widths.",
        "examples": ["Central circulation spine", "Ring circulation", "Linear circulation"]
    }
}

# Context analysis patterns
CONTEXT_PATTERNS = {
    "building_type_indicators": [
        "office", "residential", "school", "hospital", "community center", "library", "museum"
    ],
    "design_phase_indicators": [
        "concept", "schematic", "design development", "construction documents"
    ],
    "user_need_indicators": [
        "accessibility", "sustainability", "cost", "efficiency", "aesthetics", "functionality"
    ]
} 