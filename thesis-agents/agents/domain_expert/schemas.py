"""
Typed data models and schemas for the Domain Expert Agent.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class GapType(Enum):
    """Types of knowledge gaps the domain expert can address."""
    KNOWLEDGE_GAP = "knowledge_gap"
    EXAMPLE_GAP = "example_gap"
    TECHNICAL_GAP = "technical_gap"
    CONCEPTUAL_GAP = "conceptual_gap"


class BuildingCategory(Enum):
    """Building categories for knowledge classification."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INSTITUTIONAL = "institutional"
    COMMUNITY = "community"
    TRANSPORTATION = "transportation"
    MIXED_USE = "mixed_use"
    LANDSCAPE = "landscape"
    URBAN = "urban"


class SearchStrategy(Enum):
    """Available search strategies for knowledge retrieval."""
    WEB_SEARCH = "web_search"
    KNOWLEDGE_BASE = "knowledge_base"
    FALLBACK = "fallback"
    AI_GENERATION = "ai_generation"


@dataclass
class SearchResult:
    """Results from a knowledge search operation."""
    title: str
    content: str
    source: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    search_strategy: SearchStrategy = SearchStrategy.WEB_SEARCH


@dataclass
class ContextAnalysis:
    """Analysis of conversation context for knowledge retrieval."""
    building_type: str = "unknown"
    design_phase: str = "unknown"
    user_focus_areas: List[str] = field(default_factory=list)
    project_context: str = ""
    conversation_depth: int = 0
    recent_topics: List[str] = field(default_factory=list)


@dataclass
class KnowledgeRequest:
    """Structured representation of a knowledge request."""
    topic: str
    gap_type: GapType
    building_category: Optional[BuildingCategory] = None
    context: Optional[ContextAnalysis] = None
    urgency: str = "normal"  # low, normal, high
    specificity: str = "general"  # general, specific, technical


@dataclass
class FocusArea:
    """A specific area of focus for targeted knowledge provision."""
    name: str
    description: str
    category: str = "general"
    priority: float = 1.0
    examples: List[str] = field(default_factory=list)


@dataclass
class KnowledgeItem:
    """A single piece of domain knowledge."""
    title: str
    content: str
    category: str
    examples: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    relevance_score: float = 1.0
    technical_level: str = "intermediate"  # beginner, intermediate, advanced


@dataclass
class SynthesizedKnowledge:
    """Synthesized knowledge from multiple sources."""
    main_content: str
    key_points: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    confidence_score: float = 1.0


@dataclass
class ResponseGeneration:
    """Configuration for response generation."""
    focus_type: str  # educational, practical, technical
    max_length: int = 800
    include_examples: bool = True
    include_sources: bool = True
    technical_level: str = "intermediate"
    tone: str = "educational"  # educational, conversational, technical


@dataclass
class DomainExpertResult:
    """Complete result from domain expert processing."""
    knowledge_request: KnowledgeRequest
    context_analysis: ContextAnalysis
    search_results: List[SearchResult] = field(default_factory=list)
    synthesized_knowledge: Optional[SynthesizedKnowledge] = None
    focus_areas: List[FocusArea] = field(default_factory=list)
    response_config: Optional[ResponseGeneration] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            "knowledge_request": {
                "topic": self.knowledge_request.topic,
                "gap_type": self.knowledge_request.gap_type.value,
                "building_category": self.knowledge_request.building_category.value if self.knowledge_request.building_category else None,
                "urgency": self.knowledge_request.urgency,
                "specificity": self.knowledge_request.specificity
            },
            "context_analysis": {
                "building_type": self.context_analysis.building_type,
                "design_phase": self.context_analysis.design_phase,
                "user_focus_areas": self.context_analysis.user_focus_areas,
                "project_context": self.context_analysis.project_context,
                "conversation_depth": self.context_analysis.conversation_depth,
                "recent_topics": self.context_analysis.recent_topics
            },
            "search_results": [
                {
                    "title": result.title,
                    "content": result.content,
                    "source": result.source,
                    "url": result.url,
                    "relevance_score": result.relevance_score,
                    "search_strategy": result.search_strategy.value
                }
                for result in self.search_results
            ],
            "synthesized_knowledge": {
                "main_content": self.synthesized_knowledge.main_content,
                "key_points": self.synthesized_knowledge.key_points,
                "examples": self.synthesized_knowledge.examples,
                "sources": self.synthesized_knowledge.sources,
                "related_topics": self.synthesized_knowledge.related_topics,
                "confidence_score": self.synthesized_knowledge.confidence_score
            } if self.synthesized_knowledge else None,
            "focus_areas": [
                {
                    "name": area.name,
                    "description": area.description,
                    "category": area.category,
                    "priority": area.priority,
                    "examples": area.examples
                }
                for area in self.focus_areas
            ]
        } 