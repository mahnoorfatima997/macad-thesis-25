# utils/routing_decision_tree.py - Advanced Routing Decision Tree
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass, field
import re

logger = logging.getLogger(__name__)

class RouteType(Enum):
    """Enhanced route types aligned with gamified routing system"""
    # Core conversation management routes
    PROGRESSIVE_OPENING = "progressive_opening"
    TOPIC_TRANSITION = "topic_transition"

    # Primary learning routes (from gamified_routing.md)
    KNOWLEDGE_ONLY = "knowledge_only"
    SOCRATIC_EXPLORATION = "socratic_exploration"
    COGNITIVE_CHALLENGE = "cognitive_challenge"
    MULTI_AGENT_COMPREHENSIVE = "multi_agent_comprehensive"

    # Support and scaffolding routes
    SOCRATIC_CLARIFICATION = "socratic_clarification"
    SUPPORTIVE_SCAFFOLDING = "supportive_scaffolding"
    FOUNDATIONAL_BUILDING = "foundational_building"
    KNOWLEDGE_WITH_CHALLENGE = "knowledge_with_challenge"
    BALANCED_GUIDANCE = "balanced_guidance"

    # Intervention routes
    COGNITIVE_INTERVENTION = "cognitive_intervention"

    # System routes
    ERROR = "error"
    FALLBACK = "fallback"

class InputType(Enum):
    """Enhanced input types aligned with gamified routing patterns"""
    # Core request types
    KNOWLEDGE_REQUEST = "knowledge_request"
    FEEDBACK_REQUEST = "feedback_request"
    EXAMPLE_REQUEST = "example_request"


    # Learning and exploration types
    DESIGN_EXPLORATION = "design_exploration"
    CREATIVE_EXPLORATION = "creative_exploration"
    IMPROVEMENT_SEEKING = "improvement_seeking"

    # Support request types
    CONFUSION_EXPRESSION = "confusion_expression"
    CLARIFICATION_REQUEST = "clarification_request"
    IMPLEMENTATION_REQUEST = "implementation_request"

    # Conversation management types
    FIRST_MESSAGE = "first_message"
    TOPIC_TRANSITION = "topic_transition"
    GENERAL_STATEMENT = "general_statement"

    # Problematic patterns
    COGNITIVE_OFFLOADING = "cognitive_offloading"
    OVERCONFIDENT_STATEMENT = "overconfident_statement"

    # Evaluation and analysis
    EVALUATION_REQUEST = "evaluation_request"

    # Fallback
    UNKNOWN = "unknown"

class UnderstandingLevel(Enum):
    """Understanding levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ConfidenceLevel(Enum):
    """Confidence levels"""
    UNCERTAIN = "uncertain"
    CONFIDENT = "confident"
    OVERCONFIDENT = "overconfident"

class EngagementLevel(Enum):
    """Engagement levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CognitiveOffloadingType(Enum):
    """Enhanced types of cognitive offloading"""
    SOLUTION_REQUEST = "solution_request"
    DIRECT_ANSWER_REQUEST = "direct_answer_request"
    AVOIDANCE_PATTERN = "avoidance_pattern"
    OVERRELIANCE = "overreliance"
    QUICK_FIX_REQUEST = "quick_fix_request"
    COMPLETE_DESIGN_REQUEST = "complete_design_request"
    STEP_BY_STEP_REQUEST = "step_by_step_request"
    NONE = "none"

@dataclass
class RoutingContext:
    """Enhanced context for routing decisions with conversation continuity"""
    classification: Dict[str, Any]
    context_analysis: Dict[str, Any]
    routing_suggestions: Dict[str, Any]
    student_state: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    current_phase: str = "ideation"
    phase_progress: float = 0.0
    project_context: Dict[str, Any] = field(default_factory=dict)
    user_intent: str = "unknown"
    cognitive_state: Dict[str, Any] = field(default_factory=dict)

    # Conversation continuity context
    conversation_continuity: Dict[str, Any] = field(default_factory=dict)
    is_continuing_conversation: bool = False
    current_topic: str = ""
    last_route_used: str = ""
    topic_history: List[str] = field(default_factory=list)
    route_history: List[str] = field(default_factory=list)

    # Context persistence to avoid re-detection
    detected_building_type: str = ""
    building_type_confidence: float = 0.0
    design_phase_detected: str = ""
    phase_confidence: float = 0.0

    # Enhanced context flags
    is_first_message: bool = False
    cognitive_offloading_detected: bool = False
    understanding_level: str = "medium"
    engagement_level: str = "medium"
    confidence_level: str = "medium"
    context_agent_confidence: float = 0.0
    context_agent_route_suggestion: str = ""
    is_pure_knowledge_request: bool = False

@dataclass
class RoutingDecision:
    """Enhanced detailed routing decision result"""
    route: RouteType
    reason: str
    confidence: float
    rule_applied: str
    context_agent_override: bool = False
    cognitive_offloading_detected: bool = False
    cognitive_offloading_type: Optional[CognitiveOffloadingType] = None
    context_agent_confidence: float = 0.0
    classification: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_intent: str = "unknown"
    suggested_agents: List[str] = field(default_factory=list)

class AdvancedRoutingDecisionTree:
    """Enhanced advanced routing decision tree with better context awareness"""
    
    def __init__(self):
        self.decision_rules = self._initialize_decision_rules()
        self.route_mapping = self._initialize_route_mapping()
        self.confidence_thresholds = self._initialize_confidence_thresholds()
        self.cognitive_offloading_patterns = self._initialize_cognitive_offloading_patterns()
        self.intent_patterns = self._initialize_intent_patterns()
        self.context_keywords = self._initialize_context_keywords()
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns aligned with gamified routing system"""
        return {
            # Pure knowledge requests - REFINED patterns for factual information
            "knowledge_request": [
                r"^what is", r"^what are", r"^how does", r"^how do",
                r"can you (tell|show|explain) me about", r"tell me about", r"explain.*about",
                r"^define", r"definition of", r"meaning of", r"concept of",
                r"principles of", r"information about", r"details about", r"facts about",
                # FIXED: Add quantitative questions that were being misclassified as feedback_request
                r"how many", r"how much", r"what size", r"what dimensions",
                r"should I consider", r"should I include", r"should I have",
                r"recommended.*number", r"typical.*number", r"standard.*size",
                # MERGED: Technical questions are now knowledge requests (per gamified_routing.md)
                r"specifications?", r"technical.*requirements?", r"codes?",
                r"regulations?", r"ada.*requirements?", r"accessibility.*requirements?",
                r"building codes?", r"fire codes?", r"zoning.*requirements?",
                r"what are.*ada", r"what are.*requirements", r"door widths?",
                r"clearance.*requirements?", r"minimum.*dimensions?"
                # Moved examples to example_request, removed guidance patterns
            ],
            "example_request": [
                # Specific example requests (high priority)
                r"give.*examples?", r"show.*examples?", r"need.*examples?", r"want.*examples?",
                r"case studies?", r"precedents?", r"similar projects?",
                r"example projects?", r"projects? for", r"looking for.*examples?",
                r"adaptive reuse projects?", r"community center.*projects?",
                r"give example", r"provide example", r"show example",
                r"real project", r"built project", r"actual project",
                # More specific patterns to avoid conflicts
                r"can you give.*examples?", r"can you provide.*examples?", r"can you show.*examples?",
                r"show me.*examples?", r"show me.*projects?", r"show me.*precedents?"
            ],


            # Learning and exploration (design_problem REMOVED - patterns moved to design_exploration)
            "design_exploration": [
                r"i'm thinking about", r"i'm exploring", r"i'm considering",
                r"i want to understand", r"help me explore", r"let's explore",
                r"i'm curious about", r"i want to dive deeper", r"how might i",
                r"what if i", r"i'm working on understanding", r"help me think through",
                r"i'm trying to figure out", r"i'm wondering about",
                # ISSUE 1 FIX: More specific design exploration patterns (not specific problems)
                r"i'm stuck.*understanding", r"having trouble.*understanding", r"not sure how.*works",
                r"difficulty.*understanding", r"challenge.*understanding", r"issue.*understanding",
                r"struggling.*understanding", r"can't figure out.*concept", r"don't know how.*works",
                r"layout.*exploration", r"spatial.*exploration", r"design.*exploration"
            ],
            "creative_exploration": [
                r"what if", r"imagine", r"suppose",
                r"explore.*possibilities", r"experiment", r"try.*different", r"test.*ideas",
                r"innovative", r"creative", r"different.*approach", r"alternative.*approach",
                r"spatial organization.*ideas", r"arrangement.*possibilities", r"layout.*options",
                r"decide about", r"choices", r"options", r"possibilities",
                r"inspiring.*what about", r"examples.*what about", r"what about if i create"
            ],
            "improvement_seeking": [
                r"improve", r"better", r"enhance", r"fix", r"optimize",
                r"how can i", r"how do i", r"how might", r"ways to",
                r"what else can i", r"what else should i", r"what else could i",
                r"what other", r"what more", r"additional", r"further",
                r"would like to focus", r"need more help", r"help.*about",
                r"best approach", r"best way", r"approach.*to",
                # ISSUE 1 FIX: Add patterns for specific problems that need solutions
                r"challenge.*i'm facing", r"challenge.*facing", r"problem.*i'm facing",
                r"issue.*i'm facing", r"difficulty.*i'm facing", r"struggling.*with.*how to",
                r"the challenge.*is.*how to", r"my challenge.*is", r"facing.*is.*how to"
            ],

            # Feedback and evaluation
            "feedback_request": [
                r"what do you think", r"your take", r"your thoughts", r"your opinion",
                r"feedback", r"review", r"critique", r"thoughts on", r"opinion on"
            ],
            "evaluation_request": [
                r"evaluate", r"assess", r"analyze", r"review", r"check",
                r"is this", r"does this", r"will this", r"should I",
                r"good idea", r"bad idea", r"better", r"worse",
                r"can you evaluate", r"evaluate my", r"assess my", r"review my"
            ],

            # Support requests - ENHANCED to distinguish confusion from design guidance
            "confusion_expression": [
                r"confused", r"don't understand", r"unclear", r"lost",
                r"overwhelmed", r"makes no sense", r"help", r"help me",
                r"having trouble understanding", r"not sure what.*means",
                r"not sure how.*works", r"not sure how.*done", r"not sure how.*achieved",
                # Removed "stuck", "not sure", "having trouble" - these are now in design_exploration
                r"uncertain.*about.*meaning", r"uncertain.*what.*means",
                # Added help patterns that should trigger socratic clarification
                r"^help", r"help.*with", r"help.*understand", r"help.*me.*understand",
                r"can you help", r"could you help", r"need help", r"need guidance"
            ],
            "clarification_request": [
                r"can you explain", r"what do you mean", r"clarify",
                r"help me understand", r"break down", r"simplify",
                r"but i need.*help", r"need help.*about", r"more help about"
            ],
            # NEW: Design guidance requests (not confusion)
            "design_guidance": [
                r"need help.*organizing", r"help.*organizing", r"help.*with.*organizing",
                r"need help.*handling", r"help.*handling", r"help.*with.*handling",
                r"need help.*creating", r"help.*creating", r"help.*with.*creating",
                r"need guidance", r"need advice", r"need direction",
                r"how should i.*handle", r"how should i.*organize", r"how should i.*approach",
                r"how do i.*handle", r"how do i.*organize", r"how do i.*approach",
                r"help.*circulation", r"help.*spaces", r"help.*layout",
                r"guidance.*on", r"advice.*on", r"direction.*on",
                r"^help$", r"^help me$"  # Simple "help" requests
            ],
            "design_guidance": [
                r"help me.*integrate", r"help me.*incorporate", r"help.*following.*principles",
                r"help.*adaptive reuse", r"help.*construction", r"guidance.*design",
                r"advice.*design", r"suggestions.*design", r"how can i.*integrate",
                r"how do i.*incorporate", r"how to.*integrate", r"need more help about.*design",
                # Enhanced patterns for program elements and design considerations
                r"what.*program elements", r"program elements.*consider", r"elements.*should.*consider",
                r"what.*considerations", r"design considerations", r"key considerations",
                r"what.*factors.*design", r"design factors", r"important.*factors",
                r"what.*should.*consider", r"what.*think about", r"what.*keep in mind",
                r"curious about.*elements", r"curious about.*considerations"
            ],
            "implementation_request": [
                r"how to", r"steps", r"process", r"procedure",
                r"implementation", r"execution", r"construction",
                r"build", r"create", r"develop", r"implement"
            ],

            # Problematic patterns
            "cognitive_offloading": [
                r"just tell me", r"give me the answer", r"what's the solution",
                r"do it for me", r"show me exactly", r"tell me exactly",
                r"what should I design", r"design it for me", r"make it for me",
                r"complete design", r"full design", r"finished design"
            ],
            "overconfident_statement": [
                r"obviously", r"clearly", r"definitely", r"perfect",
                r"this is the best", r"my.*is.*best", r"optimal", r"ideal", r"flawless",
                r"this is the", r"this will", r"my design is",
                r"just.*randomly", r"doesn't matter", r"any.*will work",
                r"i will just", r"i'll just", r"simply", r"easy",
                # ADDED: Enhanced patterns for dismissive overconfidence
                r"my.*approach.*is.*great", r"my.*is.*great", r"approach.*is.*great",
                r"nothing.*need.*to.*be.*done", r"nothing.*needs.*to.*be.*done",
                r"nothing.*to.*improve", r"no.*need.*to.*improve", r"don't.*need.*to.*improve",
                r"already.*perfect", r"already.*good.*enough", r"good.*enough.*as.*is",
                r"no.*changes.*needed", r"no.*improvements.*needed", r"fine.*as.*it.*is",
                r"think.*my.*.*is.*great.*and", r"my.*.*is.*great.*and.*nothing"
            ],

            # Conversation management
            "topic_transition": [
                r"let's talk about", r"can we discuss", r"let's discuss",
                r"i want to discuss", r"move on to", r"switch to", r"different topic",
                r"change the topic", r"new topic"
            ]
        }
    
    def _initialize_context_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for better context understanding"""
        return {
            "architectural_elements": [
                "space", "room", "area", "zone", "layout", "plan", "section",
                "elevation", "detail", "structure", "foundation", "roof", "wall",
                "floor", "ceiling", "window", "door", "stair", "corridor"
            ],
            "design_phases": [
                "concept", "schematic", "design development", "construction documents",
                "ideation", "development", "refinement", "evaluation"
            ],
            "project_types": [
                "residential", "commercial", "institutional", "community", "mixed-use",
                "adaptive reuse", "renovation", "new construction", "preservation"
            ],
            "technical_aspects": [
                "sustainability", "accessibility", "energy", "lighting", "acoustics",
                "ventilation", "materials", "structure", "circulation", "programming"
            ]
        }

    def _initialize_decision_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize enhanced decision rules aligned with gamified routing system"""
        return {
            # HIGHEST PRIORITY: Conversation management and continuity
            "progressive_opening": {
                "priority": 1,
                "route": RouteType.PROGRESSIVE_OPENING,
                "conditions": ["is_first_message == True"],
                "description": "First message - progressive opening with project spark",
                "context_agent_override": True,
                "agents": ["context_agent", "cognitive_enhancement", "socratic_tutor"]
            },
            "topic_transition": {
                "priority": 2,
                "route": RouteType.TOPIC_TRANSITION,
                "conditions": ["user_intent == 'topic_transition'"],
                "description": "Topic transition - bridge building between concepts",
                "context_agent_override": True,
                "agents": ["context_agent", "domain_expert", "cognitive_enhancement"]
            },

            # CONVERSATION CONTINUITY ROUTES
            "continuing_socratic_exploration": {
                "priority": 2.5,
                "route": RouteType.SOCRATIC_EXPLORATION,
                "conditions": ["is_continuing_conversation == True", "last_route_used == 'socratic_exploration'"],
                "description": "Continue Socratic exploration from previous interaction",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "context_agent"],
                "gamified_behavior": "visual_choice_reasoning"
            },
            "continuing_knowledge_building": {
                "priority": 2.6,
                "route": RouteType.KNOWLEDGE_WITH_CHALLENGE,
                "conditions": ["is_continuing_conversation == True", "last_route_used == 'knowledge_only'"],
                "description": "Build on previous knowledge with challenge",
                "context_agent_override": False,
                "agents": ["domain_expert", "socratic_tutor", "context_agent"],
                "gamified_behavior": "knowledge_with_application_challenge"
            },

            # GAMIFIED ENGAGEMENT ROUTES
            "cognitive_challenge_low_engagement": {
                "priority": 3.0,
                "route": RouteType.COGNITIVE_CHALLENGE,
                "conditions": ["engagement_level == 'low'", "confidence_level == 'overconfident'"],
                "description": "Challenge overconfident or disengaged students with constraints",
                "context_agent_override": False,
                "agents": ["cognitive_enhancement", "context_agent", "socratic_tutor"],
                "gamified_behavior": "constraint_storm_challenge"
            },
            "multi_perspective_analysis": {
                "priority": 3.1,
                "route": RouteType.MULTI_AGENT_COMPREHENSIVE,
                "conditions": ["user_intent == 'evaluation_request'", "understanding_level == 'high'"],
                "description": "Multi-perspective design analysis with student choice",
                "context_agent_override": False,
                "agents": ["analysis_agent", "domain_expert", "socratic_tutor", "context_agent"],
                "gamified_behavior": "perspective_roleplay_menu"
            },

            # HIGH PRIORITY: Cognitive interventions
            "cognitive_offloading_intervention": {
                "priority": 3,
                "route": RouteType.COGNITIVE_INTERVENTION,
                "conditions": ["cognitive_offloading_detected == True"],
                "description": "Cognitive offloading detected - redirect to exploration",
                "context_agent_override": True,
                "agents": ["cognitive_enhancement", "context_agent", "socratic_tutor"]
            },

            # MEDIUM-HIGH PRIORITY: Knowledge and exploration routes
            "pure_knowledge_request": {
                "priority": 4,
                "route": RouteType.KNOWLEDGE_ONLY,
                "conditions": ["user_intent in ['knowledge_seeking', 'technical_question']", "is_pure_knowledge_request == True"],
                "description": "Pure knowledge request - direct information delivery",
                "context_agent_override": False,
                "agents": ["domain_expert", "context_agent", "socratic_tutor"]
            },
            "knowledge_seeking_fallback": {
                "priority": 20,  # LOWER PRIORITY - let knowledge_request_basic (priority 12) take precedence
                "route": RouteType.KNOWLEDGE_ONLY,
                "conditions": ["user_intent == 'knowledge_seeking'"],
                "description": "Knowledge seeking request - direct information delivery (fallback)",
                "context_agent_override": False,
                "agents": ["domain_expert", "context_agent", "socratic_tutor"]
            },
            "technical_question_fallback": {
                "priority": 6,
                "route": RouteType.KNOWLEDGE_ONLY,
                "conditions": ["user_intent == 'technical_question'"],
                "description": "Technical question - direct information delivery",
                "context_agent_override": False,
                "agents": ["domain_expert", "context_agent", "socratic_tutor"]
            },
            # REMOVED: example_request_pure - handled by smart routing logic below


            # SOCRATIC EXPLORATION ROUTES
            "design_exploration": {
                "priority": 6,
                "route": RouteType.SOCRATIC_EXPLORATION,
                "conditions": ["user_intent == 'design_exploration'"],
                "description": "Design exploration - Socratic questioning and guided discovery",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "context_agent", "domain_expert"]
            },
            "design_exploration_high_engagement": {
                "priority": 7,
                "route": RouteType.SOCRATIC_EXPLORATION,
                "conditions": ["user_intent == 'design_exploration'", "engagement_level == 'high'"],
                "description": "Design exploration with high engagement - Socratic questioning",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "context_agent", "domain_expert"]
            },
            "creative_exploration": {
                "priority": 8,
                "route": RouteType.SOCRATIC_EXPLORATION,
                "conditions": ["user_intent == 'creative_exploration'"],
                "description": "Creative exploration - expand design imagination",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "cognitive_enhancement", "context_agent"],
                "gamified_behavior": "visual_choice_reasoning"
            },
            #1208 ROUTE CHANGE
            "improvement_seeking": {
                "priority": 9,
                "route": RouteType.BALANCED_GUIDANCE,
                "conditions": ["user_intent == 'improvement_seeking'"],
                "description": "Improvement seeking - guide through enhancement thinking",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "domain_expert", "context_agent"],
                "gamified_behavior": "visual_choice_reasoning"
            },

            # COMPREHENSIVE ANALYSIS ROUTES
            "evaluation_request": {
                "priority": 10,
                "route": RouteType.MULTI_AGENT_COMPREHENSIVE,
                "conditions": ["user_intent == 'evaluation_request'"],
                "description": "Evaluation request - comprehensive multi-perspective analysis",
                "context_agent_override": False,
                "agents": ["context_agent", "domain_expert", "socratic_tutor", "cognitive_enhancement"]
            },
            "feedback_request": {
                "priority": 11,
                "route": RouteType.MULTI_AGENT_COMPREHENSIVE,
                "conditions": ["user_intent == 'feedback_request'"],
                "description": "Feedback request - multi-agent perspective analysis",
                "context_agent_override": False,
                "agents": ["context_agent", "domain_expert", "socratic_tutor", "cognitive_enhancement"]
            },

            # COGNITIVE CHALLENGE ROUTES - CRITICAL: High priority for overconfidence detection
            "overconfident_statement": {
                "priority": 4.5,  # FIXED: Higher priority to catch overconfident statements before other routes
                "route": RouteType.COGNITIVE_CHALLENGE,
                "conditions": ["user_intent == 'overconfident_statement'"],
                "description": "Overconfident statement - reality check challenge",
                "context_agent_override": False,
                "agents": ["cognitive_enhancement", "context_agent", "socratic_tutor"]
            },

            # DESIGN GUIDANCE ROUTES
            "design_guidance": {
                "priority": 12,
                "route": RouteType.BALANCED_GUIDANCE,
                "conditions": ["user_intent == 'design_guidance'"],
                "description": "Design guidance request - balanced knowledge with follow-up questions",
                "context_agent_override": False,
                "agents": ["domain_expert", "socratic_tutor", "context_agent"]
            },

            # SUPPORTIVE SCAFFOLDING ROUTES - HIGHER PRIORITY
            "confusion_expression": {
                "priority": 5,  # MOVED UP: Confusion needs immediate attention
                "route": RouteType.SOCRATIC_CLARIFICATION,
                "conditions": ["user_intent == 'confusion_expression'"],
                "description": "Confusion expression - Socratic clarification guidance",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "domain_expert", "context_agent"]
            },
            "clarification_request": {
                "priority": 14,
                "route": RouteType.SOCRATIC_CLARIFICATION,
                "conditions": ["user_intent == 'clarification_request'"],
                "description": "Clarification request - diagnostic questions and foundation building",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "domain_expert", "context_agent"]
            },

            # FOUNDATIONAL BUILDING ROUTES
            "implementation_request_low_understanding": {
                "priority": 15,
                "route": RouteType.FOUNDATIONAL_BUILDING,
                "conditions": ["user_intent == 'implementation_request'", "understanding_level == 'low'"],
                "description": "Implementation request with low understanding - foundational building",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "domain_expert", "context_agent"]
            },

            # KNOWLEDGE WITH CHALLENGE ROUTES
            "knowledge_request_with_guidance": {
                "priority": 16,
                "route": RouteType.BALANCED_GUIDANCE,
                "conditions": ["user_intent == 'knowledge_request'", "is_pure_knowledge_request == False"],
                "description": "Knowledge request with guidance needed - Balanced guidance",
                "context_agent_override": False,
                "agents": ["domain_expert", "socratic_tutor", "context_agent"]
            },
            # REMOVED: example_request_with_guidance - handled by smart routing logic below
            "implementation_request_high_understanding": {
                "priority": 18,
                "route": RouteType.KNOWLEDGE_WITH_CHALLENGE,
                "conditions": ["user_intent == 'implementation_request'", "understanding_level == 'high'"],
                "description": "Implementation request with high understanding - knowledge with challenge",
                "context_agent_override": False,
                "agents": ["domain_expert", "socratic_tutor", "context_agent"]
            },

            # GENERAL STATEMENT AND FALLBACK ROUTES
            "general_statement": {
                "priority": 19,
                "route": RouteType.SOCRATIC_EXPLORATION,
                "conditions": ["user_intent == 'general_statement'"],
                "description": "General statement - explore through Socratic questioning",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "context_agent"]
            },
            # KNOWLEDGE ROUTES - Better differentiation - FIXED: Simpler conditions
            "knowledge_request_basic": {
                "priority": 10,  # VERY HIGH PRIORITY to override knowledge_only fallback
                "route": RouteType.KNOWLEDGE_WITH_CHALLENGE,
                "conditions": ["user_intent == 'knowledge_seeking'", "is_pure_knowledge_request == True"],
                "description": "Knowledge request - knowledge with follow-up challenge",
                "context_agent_override": False,
                "agents": ["domain_expert", "socratic_tutor", "context_agent"]
            },


            # CONTEXT AGENT CONFIDENCE ROUTING
            "context_agent_high_confidence": {
                "priority": 21,
                "route": None,  # Dynamic based on mapping
                "conditions": ["context_agent_confidence > 0.7"],
                "description": "Use context agent suggestion with high confidence",
                "context_agent_override": False,
                "agents": ["context_agent"]
            },

            # SUPPORTIVE SCAFFOLDING - FIXED: HIGHEST priority to override progressive_opening
            "supportive_scaffolding_help": {
                "priority": 0.5,  # HIGHEST PRIORITY to override progressive_opening
                "route": RouteType.SUPPORTIVE_SCAFFOLDING,
                "conditions": ["'help' in user_input.lower()", "'understanding' in user_input.lower()"],
                "description": "Help requests - supportive scaffolding",
                "context_agent_override": False,
                "agents": ["socratic_tutor", "context_agent"]
            },

            # FALLBACK ROUTES
            "balanced_guidance_fallback": {
                "priority": 99,  # FIXED: Make this truly last resort
                "route": RouteType.BALANCED_GUIDANCE,
                "conditions": ["default"],
                "description": "Default balanced guidance for unclear inputs",
                "context_agent_override": False,
                "agents": ["context_agent", "domain_expert", "socratic_tutor"]
            }
        }
    
    def _initialize_route_mapping(self) -> Dict[str, str]:
        """Initialize route mapping from context agent to enhanced orchestrator routes"""
        return {
            # Core routes (direct mapping)
            "knowledge_only": "knowledge_only",
            "socratic_exploration": "socratic_exploration",
            "cognitive_challenge": "cognitive_challenge",
            "multi_agent_comprehensive": "multi_agent_comprehensive",
            "socratic_clarification": "socratic_clarification",
            "supportive_scaffolding": "supportive_scaffolding",
            "foundational_building": "foundational_building",
            "knowledge_with_challenge": "knowledge_with_challenge",
            "balanced_guidance": "balanced_guidance",
            "cognitive_intervention": "cognitive_intervention",
            "progressive_opening": "progressive_opening",
            "topic_transition": "topic_transition",

            # Legacy mappings for backward compatibility
            "multi_agent": "multi_agent_comprehensive",
            "design_guidance": "balanced_guidance",  # Redirect to Socratic exploration
            "knowledge_exploration": "knowledge_only",
            "analysis_guidance": "multi_agent_comprehensive",
            "technical_guidance": "knowledge_with_challenge",
            "clarification_support": "socratic_clarification",
            "improvement_guidance": "socratic_exploration",
            "knowledge_provision": "knowledge_only",
            "exploratory_guidance": "socratic_exploration",
            "confidence_building": "supportive_scaffolding",
            "general_guidance": "balanced_guidance",

            # Fallback
            "default": "balanced_guidance",
            "fallback": "balanced_guidance"
        }
    
    def _initialize_confidence_thresholds(self) -> Dict[str, float]:
        """Initialize confidence thresholds"""
        return {
            "context_agent_confidence": 0.6,
            "cognitive_offloading_confidence": 0.7,
            "cognitive_offloading_override": 0.8,
            "understanding_confidence": 0.6,
            "confidence_level_confidence": 0.6,
            "engagement_confidence": 0.6,
            "overall_confidence": 0.6
        }
    
    def _initialize_cognitive_offloading_patterns(self) -> Dict[str, List[str]]:
        """Initialize cognitive offloading detection patterns - more specific to avoid false positives"""
        return {
            "solution_request": [
                "give me the complete answer", "tell me exactly what to do",
                "show me the final solution", "give me the finished design", "solve this completely for me"
            ],
            "direct_answer_request": [
                "just give me", "just show me", "just tell me the answer",
                "don't make me think", "make it simple for me"
            ],
            "avoidance_pattern": [
                "this is too hard for me", "i give up completely", "i don't want to try",
                "you do it instead", "i can't be bothered"
            ],
            "overreliance": [
                "you decide everything", "you choose for me", "whatever you think is best",
                "you know better than me", "i trust you completely", "do it all for me"
            ]
        }
    
    def classify_user_intent(self, user_input: str, context: RoutingContext) -> str:
        """Enhanced intent classification with smart hybrid approach"""

        user_input_lower = user_input.lower()

        # Priority 1: Check for cognitive offloading (highest priority)
        for pattern in self.intent_patterns["cognitive_offloading"]:
            if re.search(pattern, user_input_lower):
                return "cognitive_offloading"

        # Priority 2: Check for overconfident statements
        for pattern in self.intent_patterns["overconfident_statement"]:
            if re.search(pattern, user_input_lower):
                return "overconfident_statement"

        # Priority 3: Check for topic transitions
        for pattern in self.intent_patterns["topic_transition"]:
            if re.search(pattern, user_input_lower):
                return "topic_transition"

        # Priority 4: Use intent patterns for classification

        # Check each intent type in priority order - ALIGNED with gamified_routing.md
        intent_priority = [
            "confusion_expression",      # HIGHEST: User needs clarification
            "example_request",           # HIGH: Specific example requests
            "knowledge_request",         # MEDIUM: General knowledge seeking (includes technical questions)
            "design_exploration"         # MEDIUM: Design thinking questions
        ]

        for intent_type in intent_priority:
            if intent_type in self.intent_patterns:
                for pattern in self.intent_patterns[intent_type]:
                    if re.search(pattern, user_input_lower):
                        return intent_type

        # Design guidance (help with actual design work)
        design_guidance_patterns = [r"i need help (organizing|arranging|planning|designing)",
                                  r"help me (organize|arrange|plan|design)", r"need guidance (on|with|for)",
                                  r"help.*organizing.*spaces", r"help.*with.*layout", r"^help$"]
        for pattern in design_guidance_patterns:
            if re.search(pattern, user_input_lower):
                return "design_guidance"

        # Check other patterns from original system (design_problem removed)
        for intent_type in ["evaluation_request", "feedback_request",
                          "improvement_seeking", "creative_exploration",
                          "design_exploration", "implementation_request"]:
            if intent_type in self.intent_patterns:
                for pattern in self.intent_patterns[intent_type]:
                    if re.search(pattern, user_input_lower):
                        return intent_type

        # Default fallback - prefer design_exploration for descriptive statements
        if len(user_input.split()) > 10:  # Longer descriptive inputs
            return "design_exploration"
        else:
            return "knowledge_request"  # Short inputs likely asking for information
    
    def _is_pure_knowledge_request(self, classification: Dict[str, Any], context: RoutingContext) -> bool:
        """Enhanced check for pure knowledge requests"""
        user_input = classification.get("user_input", "").lower()
        interaction_type = classification.get("interaction_type", "")

        # If context agent classified as knowledge_seeking or technical_question, it's likely pure knowledge
        if interaction_type in ["knowledge_seeking", "technical_question"]:
            return True

        # Check for pure knowledge indicators
        pure_knowledge_indicators = [
            "what are", "what is", "examples", "case studies", "best practices",
            "principles", "guidelines", "standards", "requirements",
            "tell me about", "explain about", "information about",
            "can you tell me", "can you explain", "can you show me",
            "strategies", "techniques", "methods", "approaches",
            "what factors", "factors to consider", "considerations",
            "how should i handle", "how to handle", "handling",
            "how to create", "how to design", "how to implement",
            "circulation", "ada", "door width", "building code"
        ]

        # Check for guidance indicators (which would make it not pure knowledge)
        guidance_indicators = [
            "guide me", "help me", "advice",
            "suggestions", "recommendations", "tips"
            # Removed "how should" and "what should" as they can be part of pure knowledge requests
            # These are too broad and catch legitimate knowledge requests
        ]

        # ENHANCEMENT: Check for feedback request indicators (which would make it not pure knowledge)
        feedback_indicators = [
            "your take", "what do you think", "your thoughts", "your opinion",
            "feedback", "review", "critique", "evaluate", "assess"
        ]

        has_pure_knowledge = any(indicator in user_input for indicator in pure_knowledge_indicators)
        has_guidance = any(indicator in user_input for indicator in guidance_indicators)
        has_feedback = any(indicator in user_input for indicator in feedback_indicators)

        return has_pure_knowledge and not has_guidance and not has_feedback
    
    def _extract_context_keywords(self, user_input: str) -> Dict[str, List[str]]:
        """Extract context keywords from user input"""
        user_input_lower = user_input.lower()
        extracted_keywords = {}
        
        for category, keywords in self.context_keywords.items():
            found_keywords = [kw for kw in keywords if kw in user_input_lower]
            if found_keywords:
                extracted_keywords[category] = found_keywords
        
        return extracted_keywords

    def decide_route(self, context: RoutingContext) -> RoutingDecision:
        """Enhanced routing decision with conversation continuity awareness"""
        # Initialize classification early to avoid unbound variable in exception handler
        classification = context.classification if context and hasattr(context, 'classification') else {}
        
        try:
            # Extract context data
            routing_suggestions = context.routing_suggestions
            context_analysis = context.context_analysis

            # Populate conversation continuity context from student state
            if context.student_state:
                # Handle both dict and object types
                if isinstance(context.student_state, dict):
                    continuity_context = context.student_state.get("conversation_context", {})
                    context.is_continuing_conversation = context.student_state.get("is_continuing_conversation", False)
                else:
                    # Handle object with attributes
                    continuity_context = getattr(context.student_state, "conversation_context", None)
                    if continuity_context:
                        context.is_continuing_conversation = hasattr(context.student_state, "is_continuing_conversation") and context.student_state.is_continuing_conversation()
                    else:
                        continuity_context = {}
                        context.is_continuing_conversation = False

                context.conversation_continuity = continuity_context

                # Extract context values safely
                if isinstance(continuity_context, dict):
                    context.current_topic = continuity_context.get("current_topic", "")
                    context.last_route_used = continuity_context.get("last_route_used", "")
                    context.topic_history = continuity_context.get("topic_history", [])
                    context.route_history = continuity_context.get("route_history", [])
                    context.detected_building_type = continuity_context.get("detected_building_type", "")
                    context.building_type_confidence = continuity_context.get("building_type_confidence", 0.0)
                    context.design_phase_detected = continuity_context.get("design_phase_detected", "")
                    context.phase_confidence = continuity_context.get("phase_confidence", 0.0)
                else:
                    # Handle object attributes
                    context.current_topic = getattr(continuity_context, "current_topic", "")
                    context.last_route_used = getattr(continuity_context, "last_route_used", "")
                    context.topic_history = getattr(continuity_context, "topic_history", [])
                    context.route_history = getattr(continuity_context, "route_history", [])
                    context.detected_building_type = getattr(continuity_context, "detected_building_type", "")
                    context.building_type_confidence = getattr(continuity_context, "building_type_confidence", 0.0)
                    context.design_phase_detected = getattr(continuity_context, "design_phase_detected", "")
                    context.phase_confidence = getattr(continuity_context, "phase_confidence", 0.0)

            # Use context agent's interaction_type as user_intent if available
            interaction_type = classification.get("interaction_type", "")
            user_input = classification.get("user_input", "")
            original_user_intent = classification.get("user_intent", "")

            if interaction_type and interaction_type != "unknown":
                user_intent = interaction_type
            elif original_user_intent and original_user_intent not in ["unknown", ""]:
                # FIXED: Preserve original user_intent if it was already correctly classified
                user_intent = original_user_intent
            else:
                # Fallback to pattern-based classification
                user_intent = self.classify_user_intent(user_input, context)
            
            # Treat 'question_response' as thread context; map to concrete intent
            if user_intent == "question_response":
                if classification.get("shows_confusion") or classification.get("understanding_level") == "low" or classification.get("confidence_level") == "uncertain":
                    user_intent = "confusion_expression"
                elif classification.get("is_feedback_request"):
                    user_intent = "feedback_request"
                elif classification.get("is_example_request"):
                    user_intent = "example_request"

                else:
                    user_intent = "general_question"
            
            # Update context with user intent
            context.user_intent = user_intent
            
            # Detect cognitive offloading
            cognitive_offloading = self._detect_cognitive_offloading(classification, context_analysis)
            
            # Check for pure knowledge requests (enhanced)
            is_pure_knowledge_request = self._is_pure_knowledge_request(classification, context)
            
            # Prepare classification with additional data
            enhanced_classification = {
                **classification,
                "cognitive_offloading_detected": cognitive_offloading["detected"],
                "cognitive_offloading_type": cognitive_offloading["type"],
                "cognitive_offloading_confidence": cognitive_offloading["confidence"],
                "is_pure_knowledge_request": is_pure_knowledge_request,
                "user_intent": user_intent,
                "context_agent_confidence": routing_suggestions.get("confidence", 0.0) if routing_suggestions else 0.0,
                # Fix is_technical_question flag
                "is_technical_question": user_intent == "technical_question" or classification.get("is_technical_question", False)
            }
            
            # Update classification reference for exception handler
            classification = enhanced_classification
            
            # SMART ROUTING: Handle example requests - ALL go to KNOWLEDGE_ONLY
            if user_intent == "example_request":
                # FIXED: ALL example requests go to KNOWLEDGE_ONLY so domain expert can handle them properly
                # Domain expert will determine if it's project examples (database/web) or general examples (AI)
                route = RouteType.KNOWLEDGE_ONLY

                decision = RoutingDecision(
                    route=route,
                    reason="Example request - provide examples with appropriate follow-up",
                    confidence=0.90,
                    rule_applied="smart_example_request_knowledge",
                    context_agent_override=False,
                    cognitive_offloading_detected=cognitive_offloading["detected"],
                    cognitive_offloading_type=cognitive_offloading["type"],
                    context_agent_confidence=routing_suggestions.get("confidence", 0.0) if routing_suggestions else 0.0,
                    classification=enhanced_classification,
                    user_intent=user_intent,
                    metadata={
                        "cognitive_offloading_indicators": cognitive_offloading["indicators"],
                        "context_agent_primary_route": routing_suggestions.get("primary_route") if routing_suggestions else None,
                        "is_pure_knowledge_request": False,  # Example requests need Socratic guidance
                        "intent_classification": user_intent,
                        "context_keywords": self._extract_context_keywords(user_input)
                    }
                )

                logger.info(f"🎯 SMART ROUTING: Example request → {route.value}")
                print(f"🎯 SMART ROUTING: Example request → {route.value}")
                return decision

            # GAMIFICATION: Check for intelligent triggers but RESPECT higher priority routes
            gamification_triggers = cognitive_offloading.get("gamification_triggers", [])
            if gamification_triggers:
                # CRITICAL FIX: Don't override confusion_expression, example_request, or knowledge_request
                high_priority_intents = ["confusion_expression", "example_request", "knowledge_request", "cognitive_offloading"]
                if user_intent not in high_priority_intents:
                    # Apply gamification-enhanced routing
                    enhanced_route = self._apply_gamification_routing(gamification_triggers, enhanced_classification, context)
                    if enhanced_route:
                        decision = RoutingDecision(
                            route=enhanced_route,
                            reason=f"Gamification trigger: {', '.join(gamification_triggers)}",
                            confidence=0.90,
                            rule_applied="gamification_trigger",
                            context_agent_override=False,
                            cognitive_offloading_detected=cognitive_offloading["detected"],
                            cognitive_offloading_type=cognitive_offloading["type"],
                            context_agent_confidence=routing_suggestions.get("confidence", 0.0) if routing_suggestions else 0.0,
                            classification=enhanced_classification,
                            user_intent=user_intent,
                            metadata={
                                "gamification_triggers": gamification_triggers,
                                "cognitive_offloading_indicators": cognitive_offloading["indicators"],
                                "context_agent_primary_route": routing_suggestions.get("primary_route") if routing_suggestions else None,
                                "is_pure_knowledge_request": is_pure_knowledge_request,
                                "intent_classification": user_intent,
                                "context_keywords": self._extract_context_keywords(user_input)
                            }
                        )

                        logger.info(f"🎮 GAMIFICATION ROUTING: {enhanced_route.value} triggered by {gamification_triggers}")
                        print(f"🎮 GAMIFICATION ROUTING: {enhanced_route.value} triggered by {gamification_triggers}")
                        return decision
                else:
                    logger.info(f"🎮 GAMIFICATION SKIPPED: User intent '{user_intent}' has higher priority")
                    print(f"🎮 GAMIFICATION SKIPPED: User intent '{user_intent}' has higher priority")

            # Apply decision rules in priority order for other cases
            for rule_name, rule in sorted(self.decision_rules.items(), key=lambda x: x[1]["priority"]):
                if self._evaluate_rule(rule, enhanced_classification, context):
                    route = self._determine_route(rule, enhanced_classification, context)
                    
                    decision = RoutingDecision(
                        route=route,
                        reason=rule["description"],
                        confidence=self._calculate_route_confidence(enhanced_classification),
                        rule_applied=rule_name,
                        context_agent_override=rule.get("context_agent_override", False),
                        cognitive_offloading_detected=cognitive_offloading["detected"],
                        cognitive_offloading_type=cognitive_offloading["type"],
                        context_agent_confidence=routing_suggestions.get("confidence", 0.0) if routing_suggestions else 0.0,
                        classification=enhanced_classification,
                        user_intent=user_intent,
                        metadata={
                            "cognitive_offloading_indicators": cognitive_offloading["indicators"],
                            "context_agent_primary_route": routing_suggestions.get("primary_route") if routing_suggestions else None,
                            "is_pure_knowledge_request": is_pure_knowledge_request,
                            "intent_classification": user_intent,
                            "context_keywords": self._extract_context_keywords(user_input),
                            "gamified_behavior": rule.get("gamified_behavior", "")
                        }
                    )
                    
                    logger.info(f"🎯 Enhanced Routing Decision: {decision.route.value}")
                    logger.info(f"   User Intent: {user_intent}")
                    logger.info(f"   Reason: {decision.reason}")
                    logger.info(f"   Confidence: {decision.confidence:.2f}")
                    logger.info(f"   Rule Applied: {rule_name}")

                    # Additional debug logging
                    print(f"🎯 ROUTING DEBUG: Selected route = {decision.route.value}")
                    print(f"   User intent = {user_intent}")
                    print(f"   Rule applied = {rule_name}")
                    print(f"   Classification = {enhanced_classification}")

                    return decision
            
            # Fallback decision
            return RoutingDecision(
                route=RouteType.BALANCED_GUIDANCE,
                reason="Default balanced guidance",
                confidence=0.5,
                rule_applied="default_balanced",
                classification=enhanced_classification
            )
            
        except Exception as e:
            logger.error(f"Error in advanced routing decision: {e}")
            return RoutingDecision(
                route=RouteType.ERROR,
                reason=f"Routing error: {str(e)}",
                confidence=0.0,
                rule_applied="error",
                classification=classification  # Now guaranteed to be defined
            )
    
    def _evaluate_rule(self, rule: Dict[str, Any], classification: Dict[str, Any], context: RoutingContext) -> bool:
        """Evaluate if a rule applies"""
        conditions = rule.get("conditions", [])
        
        for condition in conditions:
            if not self._evaluate_condition(condition, classification, context):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: str, classification: Dict[str, Any], context: RoutingContext) -> bool:
        """Evaluate a single condition with context awareness"""
        try:
            # Handle special conditions
            if condition == "default":
                return True

            result: bool = False

            # Equality check
            if "==" in condition:
                field, value = condition.split("==")
                field = field.strip()
                value = value.strip().strip("'").strip('"')

                # Handle boolean values
                if isinstance(value, str):
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False

                # Resolve actual value
                actual_value = classification.get(field)
                if field == "user_intent":
                    actual_value = classification.get("user_intent") or classification.get("interaction_type", "")
                elif field == "understanding_level":
                    actual_value = classification.get("understanding_level", "medium")
                elif field == "engagement_level":
                    actual_value = classification.get("engagement_level", "medium")
                elif field == "confidence_level":
                    actual_value = classification.get("confidence_level", "uncertain")
                elif field == "is_pure_knowledge_request":
                    actual_value = classification.get("is_pure_knowledge_request", False)
                elif field == "cognitive_offloading_detected":
                    actual_value = classification.get("cognitive_offloading_detected", False)
                elif field == "is_first_message":
                    actual_value = classification.get("is_first_message", False)
                elif field == "context_agent_confidence":
                    actual_value = classification.get("context_agent_confidence", 0.0)
                # Conversation continuity fields
                elif field == "is_continuing_conversation":
                    actual_value = context.is_continuing_conversation
                elif field == "last_route_used":
                    actual_value = context.last_route_used
                elif field == "current_topic":
                    actual_value = context.current_topic
                elif field == "detected_building_type":
                    actual_value = context.detected_building_type
                elif field == "building_type_confidence":
                    actual_value = context.building_type_confidence
                elif field == "design_phase_detected":
                    actual_value = context.design_phase_detected
                elif field == "phase_confidence":
                    actual_value = context.phase_confidence

                logger.debug(f"Condition evaluation: {field} == {value} (actual: {actual_value})")
                result = (actual_value == value)

            # Greater-than numeric comparison, e.g., context_agent_confidence > 0.7
            elif ">" in condition:
                field, value = condition.split(">")
                field = field.strip()
                value = value.strip()
                if field == "user_intent":
                    actual_value = classification.get("user_intent") or classification.get("interaction_type", "")
                elif field == "understanding_level":
                    actual_value = classification.get("understanding_level", "medium")
                elif field == "engagement_level":
                    actual_value = classification.get("engagement_level", "medium")
                elif field == "confidence_level":
                    actual_value = classification.get("confidence_level", "uncertain")
                elif field == "is_pure_knowledge_request":
                    actual_value = classification.get("is_pure_knowledge_request", False)
                elif field == "cognitive_offloading_detected":
                    actual_value = classification.get("cognitive_offloading_detected", False)
                elif field == "is_first_message":
                    actual_value = classification.get("is_first_message", False)
                elif field == "context_agent_confidence":
                    actual_value = classification.get("context_agent_confidence", 0.0)
                else:
                    actual_value = classification.get(field)
                try:
                    # Ensure both values are valid numbers
                    if actual_value is None:
                        actual_value = 0.0
                    result = float(actual_value) > float(value)
                except (ValueError, TypeError, AttributeError):
                    result = False

            # Less-than numeric comparison
            elif "<" in condition:
                field, value = condition.split("<")
                field = field.strip()
                value = value.strip()
                if field == "context_agent_confidence":
                    actual_value = classification.get("context_agent_confidence", 0.0)
                else:
                    actual_value = classification.get(field)
                try:
                    # Ensure both values are valid numbers
                    if actual_value is None:
                        actual_value = 0.0
                    result = float(actual_value) < float(value)
                except (ValueError, TypeError, AttributeError):
                    result = False

            return result

        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def _determine_route(self, rule: Dict[str, Any], classification: Dict[str, Any], context: RoutingContext) -> RouteType:
        """Determine the actual route based on rule and context"""
        route = rule.get("route")
        
        # If route is None, use context agent mapping
        if route is None and context.routing_suggestions:
            primary_route = context.routing_suggestions.get("primary_route", "default")
            mapped_route = self.route_mapping.get(primary_route, "balanced_guidance")
            return RouteType(mapped_route)
        
        return route or RouteType.BALANCED_GUIDANCE
    
    def _detect_cognitive_offloading(self, classification: Dict[str, Any], context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect cognitive offloading patterns with improved specificity"""
        message = classification.get("last_message", "").lower()
        interaction_type = classification.get("interaction_type", "")
        
        detected = False
        offloading_type = CognitiveOffloadingType.NONE
        confidence = 0.0
        indicators = []
        
        # Only check for cognitive offloading if the interaction type is already flagged as such
        # or if we detect specific cognitive offloading patterns that are NOT legitimate requests
        
        # Check interaction type for cognitive offloading (highest priority)
        if interaction_type in ["direct_answer_request", "solution_request", "cognitive_offloading"]:
            detected = True
            if interaction_type == "cognitive_offloading":
                offloading_type = CognitiveOffloadingType.SOLUTION_REQUEST
            else:
                offloading_type = CognitiveOffloadingType(interaction_type)
            confidence = 0.8
            indicators.append(f"interaction_type: {interaction_type}")
        
        # Check for specific cognitive offloading patterns (more restrictive)
        # Only apply these if the interaction type is NOT a legitimate request type
        legitimate_requests = ["knowledge_request", "example_request", "feedback_request", "question_response"]
        
        if interaction_type not in legitimate_requests:
            # Check for solution request patterns
            solution_patterns = [
                "give me the answer", "tell me what to do", "what should i do",
                "show me the solution", "give me the design", "solve this for me",
                "do it for me", "make it for me", "complete design", "full design"
            ]
            for pattern in solution_patterns:
                if pattern in message:
                    detected = True
                    offloading_type = CognitiveOffloadingType.SOLUTION_REQUEST
                    confidence = 0.8
                    indicators.append(f"solution_request: '{pattern}'")
                    break
            
            # Check for overreliance patterns
            overreliance_patterns = [
                "you decide", "you choose", "whatever you think",
                "you know better", "i trust you", "do it for me"
            ]
            for pattern in overreliance_patterns:
                if pattern in message:
                    detected = True
                    offloading_type = CognitiveOffloadingType.OVERRELIANCE
                    confidence = 0.7
                    indicators.append(f"overreliance: '{pattern}'")
                    break
        
        # Check for avoidance patterns (regardless of interaction type)
        avoidance_patterns = [
            "i don't know", "i'm not sure", "i can't figure out",
            "this is too hard", "i give up", "i'm stuck"
        ]
        for pattern in avoidance_patterns:
            if pattern in message:
                detected = True
                offloading_type = CognitiveOffloadingType.AVOIDANCE_PATTERN
                confidence = max(confidence, 0.6)
                indicators.append(f"avoidance_pattern: '{pattern}'")
                break
        
        # GAMIFICATION: Add intelligent triggers based on patterns
        gamification_triggers = self._detect_gamification_triggers(message, interaction_type, context_analysis)

        return {
            "detected": detected,
            "type": offloading_type,
            "confidence": confidence,
            "indicators": indicators,
            "gamification_triggers": gamification_triggers
        }

    def _detect_gamification_triggers(self, message: str, interaction_type: str, context_analysis: Dict[str, Any]) -> List[str]:
        """Detect patterns that should trigger gamified responses - UPDATED to match challenge_generator.py patterns."""
        triggers = []
        message_lower = message.lower().strip()

        # 1. ROLE-PLAY TRIGGERS - Same patterns as challenge_generator.py
        role_play_patterns = [
            'how would a visitor feel', 'how would', 'what would', 'from the perspective of',
            'how do users feel', 'what would an elderly person', 'what would a child',
            'how a', 'feel in this', 'feel when they', 'feel in the', 'experience in',
            'member feel', 'user feel', 'visitor feel', 'person feel',
            'from a', 'as a', 'like a', 'perspective', "'s perspective",
            'teenager\'s perspective', 'child\'s perspective', 'user\'s perspective'
        ]
        if any(pattern in message_lower for pattern in role_play_patterns):
            triggers.append("perspective_shift_challenge")

        # 2. CURIOSITY AMPLIFICATION
        curiosity_patterns = ['i wonder what would happen', 'what if', 'i wonder']
        if any(pattern in message_lower for pattern in curiosity_patterns):
            triggers.append("curiosity_amplification")

        # 3. PERSPECTIVE SHIFT REQUESTS
        perspective_shift_patterns = [
            'help me see this from a different angle', 'different angle', 'see this differently',
            'think about this differently', 'different perspective', 'another way to think',
            'alternative viewpoint', 'fresh perspective',
            'different angle', 'differently', 'another way', 'alternative',
            'fresh perspective', 'new perspective', 'see this', 'think about this'
        ]
        if any(pattern in message_lower for pattern in perspective_shift_patterns):
            triggers.append("perspective_shift_challenge")

        # 4. CREATIVE CONSTRAINTS - Updated patterns
        constraint_patterns = [
            'i\'m stuck on', 'stuck on', 'having trouble', 'not sure how',
            'i need fresh ideas', 'need fresh ideas', 'fresh ideas', 'new ideas',
            'creative ideas', 'need ideas', 'ideas for', 'inspire', 'inspiration',
            'stuck', 'help me think', 'new approach', 'different approach'
        ]
        if any(pattern in message_lower for pattern in constraint_patterns):
            triggers.append("creative_constraint_challenge")

        # 5. REALITY CHECK / OVERCONFIDENCE
        overconfidence_patterns = [
            'this seems pretty easy', 'this is easy', 'i already know exactly',
            'i already know', 'that\'s obvious', 'simple', 'basic'
        ]
        if any(pattern in message_lower for pattern in overconfidence_patterns):
            triggers.append("reality_check_challenge")

        # 6. LOW ENGAGEMENT - FIXED: Added "that makes sense" and "okay"
        low_engagement_responses = ['ok', 'okay', 'yes', 'sure', 'fine', 'alright', 'cool', 'maybe', 'that makes sense', 'makes sense']
        if message_lower in low_engagement_responses:
            triggers.append("low_engagement_challenge")

        # 7. COGNITIVE OFFLOADING
        offloading_patterns = [
            'just tell me what to do', 'can you design this', 'tell me what to do',
            'what should i do', 'give me the answer', 'what\'s the standard solution'
        ]
        if any(pattern in message_lower for pattern in offloading_patterns):
            triggers.append("creative_constraint_challenge")  # Route to constraint challenge

        # NEW INTERACTIVE TRIGGERS - MUCH MORE SPECIFIC AND CONTEXTUAL
        # Detect storytelling opportunities (only with specific storytelling language)
        story_indicators = ["imagine if", "picture this", "envision a scenario", "what if we", "let's say"]
        if any(indicator in message_lower for indicator in story_indicators):
            triggers.append("narrative_engagement")

        # Detect comparison/contrast opportunities (only explicit comparisons)
        comparison_indicators = ["versus", "compared to", "different from", "better than", "worse than", "which is better"]
        if any(indicator in message_lower for indicator in comparison_indicators):
            triggers.append("comparison_challenge")

        # Detect role-playing opportunities (MUCH MORE SPECIFIC - only when explicitly asking about user experience)
        role_play_phrases = [
            "how would a", "what would a", "from the perspective of", "if i were a",
            "as a user", "as a visitor", "user experience", "user journey",
            "how do users feel", "what do people think when", "user's point of view"
        ]
        if any(phrase in message_lower for phrase in role_play_phrases):
            triggers.append("perspective_shift_challenge")

        # IMPORTANT: Don't trigger gamification for general design statements
        # Check if this is a thoughtful design statement (should NOT be gamified)
        design_statement_indicators = [
            "i am thinking", "i would like to", "my approach is", "the purpose is",
            "i want to design", "i plan to", "my intention is", "the goal is"
        ]
        is_design_statement = any(indicator in message_lower for indicator in design_statement_indicators)

        # If it's a design statement, remove inappropriate triggers
        if is_design_statement:
            # Remove triggers that don't make sense for design statements
            triggers = [t for t in triggers if t not in ["perspective_shift_challenge", "creative_constraint_challenge"]]

        return triggers

    def _apply_gamification_routing(self, triggers: List[str], classification: Dict[str, Any], context: RoutingContext) -> RouteType | None:
        """Apply gamification-enhanced routing based on detected triggers."""

        # Priority-based trigger routing with enhanced interactivity - FIXED: Check if gamification is allowed
        for trigger in triggers:
            # CRITICAL FIX: Check if gamification is actually allowed before routing to cognitive challenge
            gamification_triggers = [
                "low_engagement_challenge", "reality_check_challenge", "creative_constraint_challenge",
                "comparison_challenge", "perspective_shift_challenge"
            ]

            if trigger in gamification_triggers:
                # Check if gamification should be applied by looking at context
                gamification_allowed = context.get("gamification_allowed", True)
                if not gamification_allowed:
                    print(f"🎮 ROUTING FIX: {trigger} detected but gamification not allowed - routing to socratic_exploration")
                    return RouteType.SOCRATIC_EXPLORATION

            if trigger == "low_engagement_challenge":
                return RouteType.COGNITIVE_CHALLENGE
            elif trigger == "reality_check_challenge":
                return RouteType.COGNITIVE_CHALLENGE
            elif trigger == "curiosity_amplification":
                # Only use Socratic if user is asking exploratory questions
                if classification.get("user_intent") in ["design_exploration", "creative_exploration"]:
                    return RouteType.SOCRATIC_EXPLORATION
                else:
                    return RouteType.KNOWLEDGE_WITH_CHALLENGE
            elif trigger == "socratic_exploration_boost":
                return RouteType.SOCRATIC_EXPLORATION
            elif trigger == "creative_constraint_challenge":
                return RouteType.COGNITIVE_CHALLENGE
            elif trigger == "complexity_increase_ready":
                # Check if user is ready for multi-agent comprehensive
                return RouteType.MULTI_AGENT_COMPREHENSIVE
            elif trigger == "narrative_engagement":
                # Use balanced guidance for storytelling
                return RouteType.BALANCED_GUIDANCE
            elif trigger == "comparison_challenge":
                # Use cognitive challenge for comparison exercises
                return RouteType.COGNITIVE_CHALLENGE
            elif trigger == "perspective_shift_challenge":
                # Use cognitive challenge for role-playing and perspective shifts (gamification)
                return RouteType.COGNITIVE_CHALLENGE

        return None  # No gamification routing applied

    def _is_project_example_request(self, classification: Dict[str, Any], context: RoutingContext) -> bool:
        """Determine if this is asking for specific project examples"""
        message = (
            classification.get("user_input", "") or
            context.classification.get("user_input", "") or
            (context.conversation_history[-1].get("content", "") if context.conversation_history else "")
        ).lower()

        # Project example indicators
        project_indicators = [
            "example projects", "project examples", "case studies", "precedents",
            "similar projects", "built projects", "real projects", "actual projects"
        ]

        return any(indicator in message for indicator in project_indicators)

    def _is_pure_example_request(self, classification: Dict[str, Any], context: RoutingContext) -> bool:
        """Determine if this is a pure example request"""
        # Get message from multiple possible sources
        message = (
            classification.get("last_message", "") or 
            classification.get("user_input", "") or 
            classification.get("input_text", "") or 
            ""
        ).lower()
        
        interaction_type = classification.get("interaction_type", "")
        
        if interaction_type != "example_request":
            return False
        
        pure_example_keywords = [
            "example", "examples", "project", "projects", "precedent", "precedents",
            "case study", "case studies", "show me", "can you give", "can you provide",
            "can you show", "real project", "built project", "actual project",
            "museum examples", "building examples", "design examples"
        ]
        
        guidance_keywords = [
            "how can i", "how do i", "how to", "how might", "incorporate", 
            "integrate", "implement", "apply", "use", "adapt", "serve", "goals"
        ]
        
        has_pure_keywords = any(keyword in message for keyword in pure_example_keywords)
        has_guidance_keywords = any(keyword in message for keyword in guidance_keywords)
        
        return has_pure_keywords and not has_guidance_keywords
    
    def _calculate_route_confidence(self, classification: Dict[str, Any]) -> float:
        """Calculate confidence in routing decision"""
        confidences = []
        
        # Input type confidence
        if "input_type" in classification:
            confidences.append(classification.get("input_type_confidence", 0.5))
        
        # Understanding level confidence
        if "understanding_level" in classification:
            confidences.append(classification.get("understanding_confidence", 0.5))
        
        # Confidence level confidence
        if "confidence_level" in classification:
            confidences.append(classification.get("confidence_level_confidence", 0.5))
        
        # Engagement level confidence
        if "engagement_level" in classification:
            confidences.append(classification.get("engagement_confidence", 0.5))
        
        # Cognitive offloading confidence
        if classification.get("cognitive_offloading_detected"):
            confidences.append(classification.get("cognitive_offloading_confidence", 0.5))
        
        # Context agent confidence
        if classification.get("context_agent_confidence", 0) > 0:
            confidences.append(classification.get("context_agent_confidence", 0.5))
        
        # Return average confidence
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def validate_classification(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate classification data"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "missing_fields": []
        }
        
        # Check required fields
        required_fields = ["input_type", "understanding_level", "confidence_level", "engagement_level"]
        for field in required_fields:
            if field not in classification:
                validation_result["missing_fields"].append(field)
                validation_result["warnings"].append(f"Missing field: {field}")
        
        # Validate field values
        valid_input_types = [e.value for e in InputType]
        valid_understanding_levels = [e.value for e in UnderstandingLevel]
        valid_confidence_levels = [e.value for e in ConfidenceLevel]
        valid_engagement_levels = [e.value for e in EngagementLevel]
        
        if "input_type" in classification and classification["input_type"] not in valid_input_types:
            validation_result["errors"].append(f"Invalid input_type: {classification['input_type']}")
        
        if "understanding_level" in classification and classification["understanding_level"] not in valid_understanding_levels:
            validation_result["errors"].append(f"Invalid understanding_level: {classification['understanding_level']}")
        
        if "confidence_level" in classification and classification["confidence_level"] not in valid_confidence_levels:
            validation_result["errors"].append(f"Invalid confidence_level: {classification['confidence_level']}")
        
        if "engagement_level" in classification and classification["engagement_level"] not in valid_engagement_levels:
            validation_result["errors"].append(f"Invalid engagement_level: {classification['engagement_level']}")
        
        # Set default values for missing fields
        if "input_type" not in classification:
            classification["input_type"] = "unknown"
        
        if "understanding_level" not in classification:
            classification["understanding_level"] = "medium"
        
        if "confidence_level" not in classification:
            classification["confidence_level"] = "confident"
        
        if "engagement_level" not in classification:
            classification["engagement_level"] = "medium"
        
        if "cognitive_offloading_detected" not in classification:
            classification["cognitive_offloading_detected"] = False
        
        validation_result["is_valid"] = len(validation_result["errors"]) == 0
        
        return validation_result

class AdvancedRoutingOptimizer:
    """Advanced routing optimizer with performance tracking"""
    
    def __init__(self):
        self.routing_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.cognitive_offloading_tracking: Dict[str, int] = {}
    
    def record_routing_decision(self, decision: RoutingDecision, outcome: Dict[str, Any]):
        """Record a routing decision and its outcome"""
        record = {
            "timestamp": outcome.get("timestamp", ""),
            "route": decision.route.value,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "cognitive_offloading_detected": decision.cognitive_offloading_detected,
            "cognitive_offloading_type": decision.cognitive_offloading_type.value if decision.cognitive_offloading_type else None,
            "context_agent_override": decision.context_agent_override,
            "user_satisfaction": outcome.get("user_satisfaction", 0.0),
            "response_time": outcome.get("response_time", 0.0),
            "cognitive_enhancement_score": outcome.get("cognitive_enhancement_score", 0.0)
        }
        
        self.routing_history.append(record)
        
        # Update performance metrics
        route = decision.route.value
        if route:
            if route not in self.performance_metrics:
                self.performance_metrics[route] = {
                    "total_decisions": 0,
                    "avg_satisfaction": 0.0,
                    "avg_response_time": 0.0,
                    "avg_cognitive_score": 0.0,
                    "cognitive_offloading_count": 0
                }
            
            metrics = self.performance_metrics[route]
            metrics["total_decisions"] += 1
            
            # Update averages
            current_avg = metrics["avg_satisfaction"]
            metrics["avg_satisfaction"] = (current_avg * (metrics["total_decisions"] - 1) + record["user_satisfaction"]) / metrics["total_decisions"]
            
            current_avg = metrics["avg_response_time"]
            metrics["avg_response_time"] = (current_avg * (metrics["total_decisions"] - 1) + record["response_time"]) / metrics["total_decisions"]
            
            current_avg = metrics["avg_cognitive_score"]
            metrics["avg_cognitive_score"] = (current_avg * (metrics["total_decisions"] - 1) + record["cognitive_enhancement_score"]) / metrics["total_decisions"]
            
            # Track cognitive offloading
            if record["cognitive_offloading_detected"]:
                metrics["cognitive_offloading_count"] += 1
        
        # Track cognitive offloading types
        if record["cognitive_offloading_type"]:
            offloading_type = record["cognitive_offloading_type"]
            self.cognitive_offloading_tracking[offloading_type] = self.cognitive_offloading_tracking.get(offloading_type, 0) + 1
    
    def get_route_performance(self, route: str) -> Dict[str, float]:
        """Get performance metrics for a specific route"""
        return self.performance_metrics.get(route, {
            "total_decisions": 0,
            "avg_satisfaction": 0.0,
            "avg_response_time": 0.0,
            "avg_cognitive_score": 0.0,
            "cognitive_offloading_count": 0
        })
    
    def get_best_performing_route(self) -> str:
        """Get the best performing route based on cognitive enhancement score"""
        best_route = None
        best_score = 0.0
        
        for route, metrics in self.performance_metrics.items():
            if metrics["total_decisions"] >= 5:  # Minimum sample size
                if metrics["avg_cognitive_score"] > best_score:
                    best_score = metrics["avg_cognitive_score"]
                    best_route = route
        
        return best_route or "balanced_guidance"
    
    def get_cognitive_offloading_analysis(self) -> Dict[str, Any]:
        """Get analysis of cognitive offloading patterns"""
        total_offloading = sum(self.cognitive_offloading_tracking.values())
        
        return {
            "total_cognitive_offloading_instances": total_offloading,
            "offloading_type_distribution": self.cognitive_offloading_tracking,
            "most_common_offloading_type": max(self.cognitive_offloading_tracking.items(), key=lambda x: x[1])[0] if self.cognitive_offloading_tracking else None,
            "routes_with_most_offloading": [
                route for route, metrics in self.performance_metrics.items()
                if metrics["cognitive_offloading_count"] > 0
            ]
        }
    
    def suggest_route_improvements(self) -> List[Dict[str, Any]]:
        """Suggest improvements based on performance data"""
        suggestions = []
        
        for route, metrics in self.performance_metrics.items():
            if metrics["total_decisions"] >= 3:  # Minimum sample size
                if metrics["avg_satisfaction"] < 0.6:
                    suggestions.append({
                        "route": route,
                        "issue": "low_user_satisfaction",
                        "suggestion": f"Consider improving {route} responses to increase user satisfaction"
                    })
                
                if metrics["avg_response_time"] > 3.0:
                    suggestions.append({
                        "route": route,
                        "issue": "slow_response_time",
                        "suggestion": f"Optimize {route} for faster response times"
                    })
                
                if metrics["avg_cognitive_score"] < 0.5:
                    suggestions.append({
                        "route": route,
                        "issue": "low_cognitive_enhancement",
                        "suggestion": f"Enhance {route} to improve cognitive enhancement scores"
                    })
                
                if metrics["cognitive_offloading_count"] > metrics["total_decisions"] * 0.3:
                    suggestions.append({
                        "route": route,
                        "issue": "high_cognitive_offloading",
                        "suggestion": f"Route {route} has high cognitive offloading rate - consider more challenging responses"
                    })
        
        return suggestions

# Global instances
advanced_routing_tree = AdvancedRoutingDecisionTree()
advanced_routing_optimizer = AdvancedRoutingOptimizer()

def make_advanced_routing_decision(context: RoutingContext) -> RoutingDecision:
    """Convenience function to make advanced routing decision"""
    # Validate classification
    validation = advanced_routing_tree.validate_classification(context.classification)
    
    if not validation["is_valid"]:
        logger.error(f"Classification validation failed: {validation['errors']}")
        return RoutingDecision(
            route=RouteType.ERROR,
            reason=f"Classification validation failed: {validation['errors']}",
            confidence=0.0,
            rule_applied="validation_error",
            classification=context.classification
        )
    
    # Make routing decision
    decision = advanced_routing_tree.decide_route(context)
    
    logger.info(f"Advanced routing decision made: {decision.route.value} with confidence {decision.confidence}")
    
    return decision 