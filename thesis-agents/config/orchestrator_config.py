
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class OrchestratorConfig:
    """Configuration class for LangGraph orchestrator thresholds and patterns"""
    
    # Confidence thresholds
    CONTEXT_AGENT_CONFIDENCE_THRESHOLD: float = 0.6
    AI_THREAD_DETECTION_CONFIDENCE: float = 0.8
    COGNITIVE_OFFLOADING_CONFIDENCE: float = 0.7
    ROUTING_CONFIDENCE_THRESHOLD: float = 0.6
    
    # AI model settings
    AI_MODEL: str = "gpt-4o"
    AI_MAX_TOKENS: int = 20
    AI_TEMPERATURE: float = 0.3
    
    # Pattern matching lists
    FOLLOWUP_EXAMPLE_PATTERNS: List[str] = None
    OVERCONFIDENCE_WORDS: List[str] = None
    TECHNICAL_QUESTION_PATTERNS: List[str] = None
    FEEDBACK_REQUEST_PATTERNS: List[str] = None
    DESIGN_GUIDANCE_PATTERNS: List[str] = None
    DESIGN_DECISION_PATTERNS: List[str] = None
    CONFUSION_WORDS: List[str] = None
    ABSOLUTE_PATTERNS: List[str] = None
    
    def __post_init__(self):
        """Initialize pattern lists if not provided"""
        if self.FOLLOWUP_EXAMPLE_PATTERNS is None:
            self.FOLLOWUP_EXAMPLE_PATTERNS = [
                "another example", "more examples", "different example", "other example",
                "another project", "more projects", "different project", "other projects",
                "another precedent", "more precedents", "different precedent", "other precedents",
                "can you give another", "can you show another", "can you provide another",
                "give me another", "show me another", "any other", "what about another"
            ]
        
        if self.OVERCONFIDENCE_WORDS is None:
            self.OVERCONFIDENCE_WORDS = [
                "obviously", "clearly", "definitely", "perfect", "best", "optimal", "ideal", "flawless"
            ]
        
        if self.TECHNICAL_QUESTION_PATTERNS is None:
            self.TECHNICAL_QUESTION_PATTERNS = [
                "what are the", "what is the", "requirements for", "ada requirements",
                "building codes", "standards for", "guidelines", "regulations"
            ]
        
        if self.FEEDBACK_REQUEST_PATTERNS is None:
            self.FEEDBACK_REQUEST_PATTERNS = [
                "review my", "feedback on", "thoughts on", "critique", "evaluate", 
                "what do you think", "how does this look", "check my design", "can you review",
                "analyze my plan", "analyze my design", "look at my", "thoughts about my",
                "how can i improve", "can you help me improve", "improve the", "improve my"
            ]
        
        if self.DESIGN_GUIDANCE_PATTERNS is None:
            self.DESIGN_GUIDANCE_PATTERNS = [
                "how can i", "how do i", "how to", "how might", "how should",
                "what's the best way", "what are ways to", "approaches to",
                "incorporate", "integrate", "implement", "apply", "use",
                "design", "create", "make", "develop", "enhance", "improve"
            ]
        
        if self.DESIGN_DECISION_PATTERNS is None:
            self.DESIGN_DECISION_PATTERNS = [
                "can you suggest", "should i have", "should i use", "which one", "which should",
                "what should i choose", "what would you recommend", "recommend", "suggest",
                "better to have", "is it better", "which is better", "which approach",
                "one or two", "single or multiple", "big or small", "central or distributed"
            ]
        
        if self.CONFUSION_WORDS is None:
            self.CONFUSION_WORDS = [
                "confused", "don't understand", "unclear", "help", "lost", "stuck"
            ]
        
        if self.ABSOLUTE_PATTERNS is None:
            self.ABSOLUTE_PATTERNS = [
                "this is the", "this will", "my design is", "the solution is", "it's clear that"
            ]

# Default configuration instance
DEFAULT_CONFIG = OrchestratorConfig() 

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class OrchestratorConfig:
    """Configuration class for LangGraph orchestrator thresholds and patterns"""
    
    # Confidence thresholds
    CONTEXT_AGENT_CONFIDENCE_THRESHOLD: float = 0.6
    AI_THREAD_DETECTION_CONFIDENCE: float = 0.8
    COGNITIVE_OFFLOADING_CONFIDENCE: float = 0.7
    ROUTING_CONFIDENCE_THRESHOLD: float = 0.6
    
    # AI model settings
    AI_MODEL: str = "gpt-4o"
    AI_MAX_TOKENS: int = 20
    AI_TEMPERATURE: float = 0.3
    
    # Pattern matching lists
    FOLLOWUP_EXAMPLE_PATTERNS: List[str] = None
    OVERCONFIDENCE_WORDS: List[str] = None
    TECHNICAL_QUESTION_PATTERNS: List[str] = None
    FEEDBACK_REQUEST_PATTERNS: List[str] = None
    DESIGN_GUIDANCE_PATTERNS: List[str] = None
    DESIGN_DECISION_PATTERNS: List[str] = None
    CONFUSION_WORDS: List[str] = None
    ABSOLUTE_PATTERNS: List[str] = None
    
    def __post_init__(self):
        """Initialize pattern lists if not provided"""
        if self.FOLLOWUP_EXAMPLE_PATTERNS is None:
            self.FOLLOWUP_EXAMPLE_PATTERNS = [
                "another example", "more examples", "different example", "other example",
                "another project", "more projects", "different project", "other projects",
                "another precedent", "more precedents", "different precedent", "other precedents",
                "can you give another", "can you show another", "can you provide another",
                "give me another", "show me another", "any other", "what about another"
            ]
        
        if self.OVERCONFIDENCE_WORDS is None:
            self.OVERCONFIDENCE_WORDS = [
                "obviously", "clearly", "definitely", "perfect", "best", "optimal", "ideal", "flawless"
            ]
        
        if self.TECHNICAL_QUESTION_PATTERNS is None:
            self.TECHNICAL_QUESTION_PATTERNS = [
                "what are the", "what is the", "requirements for", "ada requirements",
                "building codes", "standards for", "guidelines", "regulations"
            ]
        
        if self.FEEDBACK_REQUEST_PATTERNS is None:
            self.FEEDBACK_REQUEST_PATTERNS = [
                "review my", "feedback on", "thoughts on", "critique", "evaluate", 
                "what do you think", "how does this look", "check my design", "can you review",
                "analyze my plan", "analyze my design", "look at my", "thoughts about my",
                "how can i improve", "can you help me improve", "improve the", "improve my"
            ]
        
        if self.DESIGN_GUIDANCE_PATTERNS is None:
            self.DESIGN_GUIDANCE_PATTERNS = [
                "how can i", "how do i", "how to", "how might", "how should",
                "what's the best way", "what are ways to", "approaches to",
                "incorporate", "integrate", "implement", "apply", "use",
                "design", "create", "make", "develop", "enhance", "improve"
            ]
        
        if self.DESIGN_DECISION_PATTERNS is None:
            self.DESIGN_DECISION_PATTERNS = [
                "can you suggest", "should i have", "should i use", "which one", "which should",
                "what should i choose", "what would you recommend", "recommend", "suggest",
                "better to have", "is it better", "which is better", "which approach",
                "one or two", "single or multiple", "big or small", "central or distributed"
            ]
        
        if self.CONFUSION_WORDS is None:
            self.CONFUSION_WORDS = [
                "confused", "don't understand", "unclear", "help", "lost", "stuck"
            ]
        
        if self.ABSOLUTE_PATTERNS is None:
            self.ABSOLUTE_PATTERNS = [
                "this is the", "this will", "my design is", "the solution is", "it's clear that"
            ]

# Default configuration instance
DEFAULT_CONFIG = OrchestratorConfig() 