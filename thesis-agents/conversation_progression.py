# conversation_progression.py - Progressive Conversation Management System
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConversationPhase(Enum):
    """Defines the progressive phases of conversation"""
    DISCOVERY = "discovery"           # Opening design space, understanding user intent
    EXPLORATION = "exploration"       # Deepening understanding, building knowledge
    SYNTHESIS = "synthesis"          # Connecting ideas, forming insights
    APPLICATION = "application"      # Applying knowledge to specific problems
    REFLECTION = "reflection"        # Evaluating understanding, identifying gaps

class DesignSpaceDimension(Enum):
    """Different dimensions of the architectural design space"""
    FUNCTIONAL = "functional"        # Program, use, requirements
    SPATIAL = "spatial"             # Form, space, circulation
    TECHNICAL = "technical"         # Structure, materials, systems
    CONTEXTUAL = "contextual"       # Site, climate, culture
    AESTHETIC = "aesthetic"         # Style, expression, meaning
    SUSTAINABLE = "sustainable"     # Environmental, social, economic

class MilestoneType(Enum):
    """Types of conversation milestones"""
    PHASE_ENTRY = "phase_entry"           # Entering a new phase
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"  # Gaining new understanding
    SKILL_DEMONSTRATION = "skill_demonstration"      # Showing application ability
    INSIGHT_FORMATION = "insight_formation"          # Connecting ideas
    PROBLEM_SOLVING = "problem_solving"             # Applying to specific problems
    REFLECTION_POINT = "reflection_point"           # Evaluating progress
    READINESS_ASSESSMENT = "readiness_assessment"    # Checking if ready to advance

@dataclass
class ConversationMilestone:
    """Represents a milestone in the conversation progression"""
    milestone_type: MilestoneType
    phase: ConversationPhase
    dimension: Optional[DesignSpaceDimension] = None
    topic: str = ""
    user_understanding: str = "unknown"  # low, medium, high
    confidence_level: str = "unknown"    # uncertain, confident, overconfident
    engagement_level: str = "unknown"    # low, medium, high
    progress_percentage: float = 0.0     # 0-100% progress in current phase
    required_actions: List[str] = field(default_factory=list)  # What needs to happen next
    success_criteria: List[str] = field(default_factory=list)  # How to know milestone is complete
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DesignSpaceOpening:
    """Represents an opening of the design space"""
    dimension: DesignSpaceDimension
    opening_questions: List[str] = field(default_factory=list)
    exploration_prompts: List[str] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    user_interests: List[str] = field(default_factory=list)
    complexity_level: str = "beginner"  # beginner, intermediate, advanced

class ConversationProgressionManager:
    """Manages progressive conversation flow and design space exploration with milestone-driven logic"""
    
    def __init__(self, domain: str = "architecture"):
        self.domain = domain
        self.current_phase = ConversationPhase.DISCOVERY
        self.milestones: List[ConversationMilestone] = []
        self.opened_dimensions: List[DesignSpaceDimension] = []
        self.user_profile = self._initialize_user_profile()
        self.design_space_map = self._initialize_design_space_map()
        self.milestone_rules = self._initialize_milestone_rules()
        self.progression_sequence = self._initialize_progression_sequence()
        self.current_state = None  # Store current state for access in methods
        
        logger.info(f"Conversation Progression Manager initialized for {domain}")
    
    def update_state(self, state):
        """Update the current state for use in progression analysis"""
        self.current_state = state
    
    def _initialize_user_profile(self) -> Dict[str, Any]:
        """Initialize user learning profile"""
        return {
            "knowledge_level": "unknown",  # beginner, intermediate, advanced
            "learning_style": "unknown",   # visual, analytical, experiential
            "interests": [],
            "strengths": [],
            "gaps": [],
            "engagement_patterns": [],
            "conversation_preferences": [],
            "milestone_progress": {}  # Track progress through specific milestones
        }
    
    def _initialize_milestone_rules(self) -> Dict[MilestoneType, Dict[str, Any]]:
        """Initialize rules for milestone progression"""
        return {
            MilestoneType.PHASE_ENTRY: {
                "required_understanding": "medium",
                "min_engagement": "medium",
                "next_milestone": MilestoneType.KNOWLEDGE_ACQUISITION,
                "agent_focus": "context_agent"
            },
            MilestoneType.KNOWLEDGE_ACQUISITION: {
                "required_understanding": "high",
                "min_engagement": "high",
                "next_milestone": MilestoneType.SKILL_DEMONSTRATION,
                "agent_focus": "domain_expert"
            },
            MilestoneType.SKILL_DEMONSTRATION: {
                "required_understanding": "high",
                "min_engagement": "high",
                "next_milestone": MilestoneType.INSIGHT_FORMATION,
                "agent_focus": "socratic_tutor"
            },
            MilestoneType.INSIGHT_FORMATION: {
                "required_understanding": "high",
                "min_engagement": "high",
                "next_milestone": MilestoneType.PROBLEM_SOLVING,
                "agent_focus": "cognitive_enhancement"
            },
            MilestoneType.PROBLEM_SOLVING: {
                "required_understanding": "high",
                "min_engagement": "high",
                "next_milestone": MilestoneType.REFLECTION_POINT,
                "agent_focus": "analysis_agent"
            },
            MilestoneType.REFLECTION_POINT: {
                "required_understanding": "high",
                "min_engagement": "medium",
                "next_milestone": MilestoneType.READINESS_ASSESSMENT,
                "agent_focus": "context_agent"
            },
            MilestoneType.READINESS_ASSESSMENT: {
                "required_understanding": "high",
                "min_engagement": "high",
                "next_milestone": None,  # Will determine based on assessment
                "agent_focus": "analysis_agent"
            }
        }
    
    def _initialize_progression_sequence(self) -> Dict[ConversationPhase, List[MilestoneType]]:
        """Initialize the progression sequence for each phase"""
        return {
            ConversationPhase.DISCOVERY: [
                MilestoneType.PHASE_ENTRY,
                MilestoneType.KNOWLEDGE_ACQUISITION,
                MilestoneType.READINESS_ASSESSMENT
            ],
            ConversationPhase.EXPLORATION: [
                MilestoneType.PHASE_ENTRY,
                MilestoneType.KNOWLEDGE_ACQUISITION,
                MilestoneType.SKILL_DEMONSTRATION,
                MilestoneType.READINESS_ASSESSMENT
            ],
            ConversationPhase.SYNTHESIS: [
                MilestoneType.PHASE_ENTRY,
                MilestoneType.INSIGHT_FORMATION,
                MilestoneType.SKILL_DEMONSTRATION,
                MilestoneType.READINESS_ASSESSMENT
            ],
            ConversationPhase.APPLICATION: [
                MilestoneType.PHASE_ENTRY,
                MilestoneType.PROBLEM_SOLVING,
                MilestoneType.SKILL_DEMONSTRATION,
                MilestoneType.READINESS_ASSESSMENT
            ],
            ConversationPhase.REFLECTION: [
                MilestoneType.PHASE_ENTRY,
                MilestoneType.REFLECTION_POINT,
                MilestoneType.READINESS_ASSESSMENT
            ]
        }
    
    def _initialize_design_space_map(self) -> Dict[DesignSpaceDimension, DesignSpaceOpening]:
        """Initialize the architectural design space with opening strategies"""
        return {
            DesignSpaceDimension.FUNCTIONAL: DesignSpaceOpening(
                dimension=DesignSpaceDimension.FUNCTIONAL,
                opening_questions=[
                    "What is the primary purpose of your design?",
                    "Who are the main users and what do they need?",
                    "What activities will take place in this space?",
                    "How do you envision people moving through and using this design?"
                ],
                exploration_prompts=[
                    "Let's explore how the program influences the spatial organization",
                    "Consider how user needs might evolve over time",
                    "Think about the relationship between function and form"
                ],
                knowledge_gaps=["programming", "user analysis", "functional relationships"],
                complexity_level="beginner"
            ),
            DesignSpaceDimension.SPATIAL: DesignSpaceOpening(
                dimension=DesignSpaceDimension.SPATIAL,
                opening_questions=[
                    "How do you imagine the overall form and massing?",
                    "What kind of spatial qualities are you seeking?",
                    "How will people experience and move through the spaces?",
                    "What role does light and view play in your design?"
                ],
                exploration_prompts=[
                    "Explore how spatial relationships create meaning",
                    "Consider the dialogue between interior and exterior",
                    "Think about scale and proportion in relation to human experience"
                ],
                knowledge_gaps=["spatial composition", "circulation", "proportion"],
                complexity_level="intermediate"
            ),
            DesignSpaceDimension.TECHNICAL: DesignSpaceOpening(
                dimension=DesignSpaceDimension.TECHNICAL,
                opening_questions=[
                    "What construction systems are you considering?",
                    "How do you envision the structure supporting your design?",
                    "What materials resonate with your concept?",
                    "How will your design respond to environmental forces?"
                ],
                exploration_prompts=[
                    "Explore how technical decisions support design intent",
                    "Consider the relationship between structure and space",
                    "Think about materiality and its expressive potential"
                ],
                knowledge_gaps=["structural systems", "materials", "construction"],
                complexity_level="advanced"
            ),
            DesignSpaceDimension.CONTEXTUAL: DesignSpaceOpening(
                dimension=DesignSpaceDimension.CONTEXTUAL,
                opening_questions=[
                    "What is the character of the site and surrounding context?",
                    "How does your design respond to its environment?",
                    "What cultural or historical factors influence your approach?",
                    "How will your design contribute to its place?"
                ],
                exploration_prompts=[
                    "Explore how context shapes design decisions",
                    "Consider the dialogue between building and place",
                    "Think about cultural and environmental responsiveness"
                ],
                knowledge_gaps=["site analysis", "contextual design", "cultural sensitivity"],
                complexity_level="intermediate"
            ),
            DesignSpaceDimension.AESTHETIC: DesignSpaceOpening(
                dimension=DesignSpaceDimension.AESTHETIC,
                opening_questions=[
                    "What aesthetic qualities are you seeking to achieve?",
                    "How do you want people to feel in your spaces?",
                    "What architectural language or style interests you?",
                    "How does beauty and meaning relate to function in your design?"
                ],
                exploration_prompts=[
                    "Explore how aesthetic choices communicate meaning",
                    "Consider the relationship between beauty and utility",
                    "Think about architectural expression and its impact"
                ],
                knowledge_gaps=["aesthetic theory", "architectural expression", "design language"],
                complexity_level="intermediate"
            ),
            DesignSpaceDimension.SUSTAINABLE: DesignSpaceOpening(
                dimension=DesignSpaceDimension.SUSTAINABLE,
                opening_questions=[
                    "How does sustainability inform your design approach?",
                    "What environmental challenges does your design address?",
                    "How will your design contribute to social and economic sustainability?",
                    "What sustainable strategies are most relevant to your project?"
                ],
                exploration_prompts=[
                    "Explore how sustainability principles shape design",
                    "Consider the triple bottom line: environmental, social, economic",
                    "Think about long-term sustainability and resilience"
                ],
                knowledge_gaps=["sustainable design", "environmental systems", "lifecycle thinking"],
                complexity_level="advanced"
            )
        }
    
    def analyze_first_message(self, user_input: str, state: Any) -> Dict[str, Any]:
        """Analyze the first message to understand user intent and open design space"""
        
        logger.info("Analyzing first message for design space opening")
        
        # Analyze user's initial intent
        intent_analysis = self._analyze_user_intent(user_input)
        
        # Identify potential design space dimensions
        relevant_dimensions = self._identify_relevant_dimensions(user_input)
        
        # Assess user's knowledge level
        knowledge_assessment = self._assess_initial_knowledge(user_input)
        
        # Generate opening strategy
        opening_strategy = self._generate_opening_strategy(
            intent_analysis, relevant_dimensions, knowledge_assessment
        )
        
        # Update user profile
        self._update_user_profile(intent_analysis, knowledge_assessment)
        
        # Create first milestone
        first_milestone = ConversationMilestone(
            milestone_type=MilestoneType.PHASE_ENTRY,
            phase=ConversationPhase.DISCOVERY,
            dimension=relevant_dimensions[0] if relevant_dimensions else None,
            topic=intent_analysis.get("primary_topic", ""),
            user_understanding=knowledge_assessment.get("level", "unknown"),
            confidence_level=intent_analysis.get("confidence", "unknown"),
            engagement_level=intent_analysis.get("engagement", "unknown"),
            progress_percentage=0.0, # Initial progress
            required_actions=[],
            success_criteria=[]
        )
        self.milestones.append(first_milestone)
        
        return {
            "conversation_phase": ConversationPhase.DISCOVERY.value,
            "opening_strategy": opening_strategy,
            "relevant_dimensions": [d.value for d in relevant_dimensions],
            "user_profile": self.user_profile,
            "milestone": first_milestone,
            "next_steps": self._suggest_next_steps(first_milestone)
        }
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user's intent from their first message"""
        
        input_lower = user_input.lower()
        
        # Intent patterns
        intent_patterns = {
            "seeking_knowledge": [
                "what is", "how do", "can you explain", "help me understand",
                "i want to learn", "i need to know", "teach me"
            ],
            "seeking_guidance": [
                "help me", "guide me", "i'm stuck", "i don't know where to start",
                "what should i do", "how should i approach", "don't understand",
                "everything seems so complicated", "don't know where to begin"
            ],
            "seeking_feedback": [
                "what do you think", "is this good", "am i on the right track",
                "feedback", "review", "critique"
            ],
            "exploring_ideas": [
                "i'm thinking about", "i have an idea", "what if", "imagine",
                "consider", "explore", "brainstorm"
            ],
            "solving_problem": [
                "problem", "issue", "challenge", "difficulty", "trouble",
                "need to solve", "figure out"
            ],
            "overconfident_assertion": [
                "obviously", "clearly", "perfect", "best", "ideal", "no way it could be improved",
                "obviously perfect", "best solution possible"
            ]
        }
        
        detected_intents = []
        for intent, patterns in intent_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                detected_intents.append(intent)
        
        # Topic identification
        topics = self._extract_topics(user_input)
        
        # Confidence assessment
        confidence_indicators = {
            "uncertain": ["maybe", "i think", "not sure", "possibly", "might"],
            "confident": ["i know", "definitely", "certainly", "sure"],
            "overconfident": ["obviously", "clearly", "perfect", "best", "ideal"]
        }
        
        confidence = "neutral"
        for level, indicators in confidence_indicators.items():
            if any(indicator in input_lower for indicator in indicators):
                confidence = level
                break
        
        # Engagement assessment
        engagement_indicators = {
            "high": ["excited", "interested", "curious", "fascinated", "love"],
            "medium": ["want", "need", "would like", "interested in"],
            "low": ["ok", "fine", "whatever", "i guess"]
        }
        
        engagement = "medium"
        for level, indicators in engagement_indicators.items():
            if any(indicator in input_lower for indicator in indicators):
                engagement = level
                break
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else "general_inquiry",
            "all_intents": detected_intents,
            "primary_topic": topics[0] if topics else "general_architecture",
            "all_topics": topics,
            "confidence": confidence,
            "engagement": engagement,
            "complexity": self._assess_complexity(user_input)
        }
    
    def _identify_relevant_dimensions(self, user_input: str) -> List[DesignSpaceDimension]:
        """Identify which design space dimensions are relevant to user's input"""
        
        input_lower = user_input.lower()
        relevant_dimensions = []
        
        dimension_keywords = {
            DesignSpaceDimension.FUNCTIONAL: [
                "function", "program", "use", "purpose", "activity", "user", "need",
                "requirement", "space", "room", "area", "facility"
            ],
            DesignSpaceDimension.SPATIAL: [
                "form", "shape", "space", "volume", "massing", "layout", "plan",
                "circulation", "flow", "proportion", "scale", "composition"
            ],
            DesignSpaceDimension.TECHNICAL: [
                "structure", "construction", "material", "system", "technical",
                "building", "engineering", "detail", "assembly"
            ],
            DesignSpaceDimension.CONTEXTUAL: [
                "site", "context", "environment", "place", "location", "surrounding",
                "climate", "culture", "history", "neighborhood"
            ],
            DesignSpaceDimension.AESTHETIC: [
                "beauty", "aesthetic", "style", "appearance", "look", "feel",
                "expression", "meaning", "artistic", "visual"
            ],
            DesignSpaceDimension.SUSTAINABLE: [
                "sustainable", "environmental", "green", "eco", "energy", "climate",
                "social", "economic", "future", "long-term"
            ]
        }
        
        for dimension, keywords in dimension_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                relevant_dimensions.append(dimension)
        
        # If no specific dimensions detected, suggest functional and spatial as starting points
        if not relevant_dimensions:
            relevant_dimensions = [DesignSpaceDimension.FUNCTIONAL, DesignSpaceDimension.SPATIAL]
        
        return relevant_dimensions
    
    def _assess_initial_knowledge(self, user_input: str) -> Dict[str, Any]:
        """Assess user's initial knowledge level from their first message"""
        
        input_lower = user_input.lower()
        
        # Technical vocabulary assessment
        technical_terms = [
            "programming", "circulation", "massing", "proportion", "structure",
            "sustainability", "context", "aesthetic", "spatial", "functional",
            "construction", "material", "system", "detail", "assembly"
        ]
        
        technical_count = sum(1 for term in technical_terms if term in input_lower)
        
        # Complexity assessment
        word_count = len(user_input.split())
        sentence_count = user_input.count('.') + user_input.count('!') + user_input.count('?')
        
        # Knowledge level determination
        if technical_count >= 3 and word_count > 20:
            level = "advanced"
        elif technical_count >= 1 and word_count > 10:
            level = "intermediate"
        else:
            level = "beginner"
        
        return {
            "level": level,
            "technical_vocabulary": technical_count,
            "complexity_score": word_count + sentence_count,
            "identified_gaps": self._identify_knowledge_gaps(user_input)
        }
    
    def _generate_opening_strategy(self, intent_analysis: Dict, 
                                 relevant_dimensions: List[DesignSpaceDimension],
                                 knowledge_assessment: Dict) -> Dict[str, Any]:
        """Generate strategy for opening the design space"""
        
        primary_dimension = relevant_dimensions[0]
        design_space = self.design_space_map[primary_dimension]
        
        # Select appropriate opening questions based on user's knowledge level
        knowledge_level = knowledge_assessment.get("level", "beginner")
        
        if knowledge_level == "beginner":
            opening_questions = design_space.opening_questions[:2]  # Start with basics
        elif knowledge_level == "intermediate":
            opening_questions = design_space.opening_questions[1:3]  # Middle complexity
        else:
            opening_questions = design_space.opening_questions[2:]  # Advanced questions
        
        # Generate personalized opening message
        opening_message = self._create_opening_message(
            intent_analysis, primary_dimension, knowledge_level
        )
        
        return {
            "opening_message": opening_message,
            "primary_dimension": primary_dimension.value,
            "opening_questions": opening_questions,
            "exploration_prompts": design_space.exploration_prompts,
            "knowledge_gaps": design_space.knowledge_gaps,
            "complexity_level": knowledge_level,
            "suggested_approach": self._suggest_approach(intent_analysis, knowledge_level)
        }
    
    def _create_opening_message(self, intent_analysis: Dict, 
                              primary_dimension: DesignSpaceDimension,
                              knowledge_level: str) -> str:
        """Create personalized opening message using LLM instead of hardcoded templates"""
        
        try:
            # Import OpenAI client for dynamic response generation
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            intent = intent_analysis.get("primary_intent", "general_inquiry")
            topic = intent_analysis.get("primary_topic", "architecture")
            engagement = intent_analysis.get("engagement", "medium")
            
            # Create dynamic prompt for LLM-based opening message
            prompt = f"""
            You are an expert architectural mentor helping a student explore {topic}. 
            
            CONTEXT:
            - Student intent: {intent}
            - Primary dimension: {primary_dimension.value}
            - Knowledge level: {knowledge_level}
            - Engagement level: {engagement}
            
            TASK: Generate a personalized, engaging opening message (2-3 sentences) that:
            1. Acknowledges their specific interest in {topic}
            2. Connects to the {primary_dimension.value} dimension of architectural thinking
            3. Matches their {knowledge_level} knowledge level
            4. Encourages their {engagement} engagement level
            5. Sounds natural and conversational, not like a template
            
            RESPONSE: Write only the opening message, no explanations or formatting.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_generated_message = response.choices[0].message.content.strip()
            
            # Fallback to template if LLM fails
            if not ai_generated_message or len(ai_generated_message) < 20:
                return self._generate_fallback_opening_message(intent, topic, primary_dimension, engagement)
            
            return ai_generated_message
            
        except Exception as e:
            # Fallback to template-based generation if LLM fails
            intent = intent_analysis.get("primary_intent", "general_inquiry")
            topic = intent_analysis.get("primary_topic", "architecture")
            engagement = intent_analysis.get("engagement", "medium")
            return self._generate_fallback_opening_message(intent, topic, primary_dimension, engagement)
    
    def _generate_fallback_opening_message(self, intent: str, topic: str, 
                                        primary_dimension: DesignSpaceDimension,
                                        engagement: str) -> str:
        """Fallback method for generating opening messages when LLM is unavailable"""
        
        # Base opening messages by intent
        intent_openings = {
            "seeking_knowledge": f"I'd love to help you explore {topic}! This is a fascinating area of architectural thinking.",
            "seeking_guidance": f"Great question about {topic}! Let's work through this together step by step.",
            "seeking_feedback": f"Thanks for sharing your thoughts on {topic}! I'm excited to explore this with you.",
            "exploring_ideas": f"What an interesting approach to {topic}! I'm curious to hear more about your thinking.",
            "solving_problem": f"I see you're working through a challenge with {topic}. Let's break this down together.",
            "general_inquiry": f"Welcome to exploring {topic}! This is a rich area of architectural design."
        }
        
        base_message = intent_openings.get(intent, intent_openings["general_inquiry"])
        
        # Add dimension-specific context
        dimension_context = {
            DesignSpaceDimension.FUNCTIONAL: "Let's start by understanding the core purpose and user needs.",
            DesignSpaceDimension.SPATIAL: "Let's explore how space and form work together to create meaning.",
            DesignSpaceDimension.TECHNICAL: "Let's examine how technical decisions support design intent.",
            DesignSpaceDimension.CONTEXTUAL: "Let's understand how context shapes design decisions.",
            DesignSpaceDimension.AESTHETIC: "Let's explore how aesthetic choices communicate meaning.",
            DesignSpaceDimension.SUSTAINABLE: "Let's examine how sustainability principles inform design."
        }
        
        dimension_message = dimension_context.get(primary_dimension, "")
        
        # Add engagement-specific encouragement
        if engagement == "high":
            encouragement = "Your enthusiasm for this topic is great - let's dive deep!"
        elif engagement == "low":
            encouragement = "I'm here to help make this engaging and meaningful for you."
        else:
            encouragement = "I'm excited to explore this together!"
        
        return f"{base_message} {dimension_message} {encouragement}"
    
    def _suggest_approach(self, intent_analysis: Dict, knowledge_level: str) -> str:
        """Suggest appropriate approach based on intent and knowledge level"""
        
        intent = intent_analysis.get("primary_intent", "general_inquiry")
        
        approaches = {
            "seeking_knowledge": {
                "beginner": "concept_introduction",
                "intermediate": "concept_deepening", 
                "advanced": "concept_synthesis"
            },
            "seeking_guidance": {
                "beginner": "step_by_step_scaffolding",
                "intermediate": "guided_exploration",
                "advanced": "collaborative_problem_solving"
            },
            "seeking_feedback": {
                "beginner": "constructive_encouragement",
                "intermediate": "detailed_analysis",
                "advanced": "critical_dialogue"
            },
            "exploring_ideas": {
                "beginner": "idea_development",
                "intermediate": "idea_refinement",
                "advanced": "idea_synthesis"
            },
            "solving_problem": {
                "beginner": "problem_breakdown",
                "intermediate": "solution_exploration",
                "advanced": "solution_optimization"
            },
            "overconfident_assertion": {
                "beginner": "collaborative_problem_solving",
                "intermediate": "collaborative_problem_solving",
                "advanced": "collaborative_problem_solving"
            }
        }
        
        return approaches.get(intent, {}).get(knowledge_level, "guided_exploration")
    
    def _suggest_next_steps(self, milestone: ConversationMilestone) -> List[str]:
        """Suggest next steps based on current milestone"""
        
        phase = milestone.phase
        dimension = milestone.dimension
        
        if phase == ConversationPhase.DISCOVERY:
            return [
                "Ask follow-up questions to deepen understanding",
                "Explore related design space dimensions",
                "Begin building foundational knowledge",
                "Identify specific areas of interest"
            ]
        elif phase == ConversationPhase.EXPLORATION:
            return [
                "Provide examples and case studies",
                "Explore theoretical frameworks",
                "Connect to practical applications",
                "Address knowledge gaps"
            ]
        elif phase == ConversationPhase.SYNTHESIS:
            return [
                "Help connect different ideas",
                "Identify patterns and relationships",
                "Formulate insights and principles",
                "Prepare for application"
            ]
        elif phase == ConversationPhase.APPLICATION:
            return [
                "Apply knowledge to specific problems",
                "Provide feedback on applications",
                "Refine and improve approaches",
                "Build confidence in application"
            ]
        else:  # REFLECTION
            return [
                "Evaluate understanding and progress",
                "Identify remaining gaps",
                "Plan next learning steps",
                "Celebrate achievements"
            ]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract architectural topics from text"""
        
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            "residential": ["house", "home", "apartment", "residential", "living"],
            "commercial": ["office", "commercial", "retail", "business", "workplace"],
            "cultural": ["museum", "theater", "gallery", "cultural", "arts"],
            "educational": ["school", "university", "education", "learning", "classroom"],
            "healthcare": ["hospital", "clinic", "healthcare", "medical"],
            "sustainability": ["sustainable", "green", "environmental", "eco"],
            "urban": ["urban", "city", "public", "street", "neighborhood"],
            "interior": ["interior", "furniture", "furnishing", "decoration"],
            "structure": ["structure", "construction", "building", "system"],
            "design_process": ["design", "process", "methodology", "approach"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _assess_complexity(self, text: str) -> str:
        """Assess complexity of user input"""
        
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        if word_count > 30 and sentence_count > 3:
            return "high"
        elif word_count > 15 and sentence_count > 1:
            return "medium"
        else:
            return "low"
    
    def _identify_knowledge_gaps(self, text: str) -> List[str]:
        """Identify potential knowledge gaps from user input"""
        
        gaps = []
        text_lower = text.lower()
        
        # Look for indicators of gaps
        gap_indicators = {
            "technical_understanding": ["don't understand", "confused about", "not sure how"],
            "process_knowledge": ["don't know where to start", "what's the process", "how do I"],
            "context_awareness": ["what about", "considering", "thinking about"],
            "evaluation_skills": ["is this good", "how do I know", "what makes"]
        }
        
        for gap_type, indicators in gap_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                gaps.append(gap_type)
        
        return gaps
    
    def _update_user_profile(self, intent_analysis: Dict, knowledge_assessment: Dict):
        """Update user profile based on first message analysis"""
        
        self.user_profile["knowledge_level"] = knowledge_assessment.get("level", "unknown")
        self.user_profile["interests"] = intent_analysis.get("all_topics", [])
        self.user_profile["gaps"] = knowledge_assessment.get("identified_gaps", [])
        
        # Infer learning style from communication patterns
        complexity = intent_analysis.get("complexity", "low")
        if complexity == "high":
            self.user_profile["learning_style"] = "analytical"
        elif complexity == "medium":
            self.user_profile["learning_style"] = "balanced"
        else:
            self.user_profile["learning_style"] = "visual"
    
    def progress_conversation(self, user_input: str, current_response: str, 
                            state: Any) -> Dict[str, Any]:
        """Progress the conversation to the next phase"""
        
        # Store current state for context access
        self.current_state = state
        
        # Analyze current state
        current_analysis = self._analyze_conversation_state(user_input, current_response, state)
        
        # Determine if phase transition is needed
        should_transition = self._should_transition_phase(current_analysis)
        
        if should_transition:
            new_phase = self._determine_next_phase(current_analysis)
            self.current_phase = new_phase
            
            # Create new milestone
            new_milestone = ConversationMilestone(
                milestone_type=MilestoneType.PHASE_ENTRY, # Always PHASE_ENTRY for phase transition
                phase=new_phase,
                dimension=current_analysis.get("active_dimension"),
                topic=current_analysis.get("current_topic", ""),
                user_understanding=current_analysis.get("understanding", "unknown"),
                confidence_level=current_analysis.get("confidence", "unknown"),
                engagement_level=current_analysis.get("engagement", "unknown"),
                progress_percentage=0.0, # Reset progress for new phase
                required_actions=[],
                success_criteria=[]
            )
            self.milestones.append(new_milestone)
        
        return {
            "current_phase": self.current_phase.value,
            "phase_transition": should_transition,
            "new_milestone": new_milestone if should_transition else None,
            "progression_guidance": self._generate_progression_guidance(current_analysis),
            "conversation_summary": self._summarize_conversation_progress()
        }
    
    def _analyze_conversation_state(self, user_input: str, current_response: str, 
                                  state: Any) -> Dict[str, Any]:
        """Analyze current conversation state for progression decisions"""
        
        # This would integrate with your existing context analysis
        # For now, returning a basic structure
        return {
            "message_count": len(state.messages) if hasattr(state, 'messages') else 0,
            "current_topic": self._extract_current_topic(user_input),
            "understanding_depth": self._assess_understanding_depth(user_input),
            "engagement_trend": self._assess_engagement_trend(state),
            "knowledge_demonstration": self._assess_knowledge_demonstration(user_input),
            "readiness_for_advancement": self._assess_readiness_for_advancement(user_input, state)
        }
    
    def _should_transition_phase(self, analysis: Dict) -> bool:
        """Determine if conversation should transition to next phase"""
        
        # More responsive heuristic based on message count, understanding, and content
        message_count = analysis.get("message_count", 0)
        understanding = analysis.get("understanding_depth", "low")
        readiness = analysis.get("readiness_for_advancement", False)
        current_topic = analysis.get("current_topic", "")
        
        # Transition rules - more responsive thresholds
        if self.current_phase == ConversationPhase.DISCOVERY:
            # Transition to EXPLORATION when user shows understanding and asks for examples/details
            return (message_count >= 2 and understanding in ["medium", "high"]) or \
                   any(word in current_topic.lower() for word in ["example", "show me", "can you show", "demonstrate"])
                   
        elif self.current_phase == ConversationPhase.EXPLORATION:
            # Transition to SYNTHESIS when user connects ideas or shows synthesis thinking
            return (message_count >= 4 and readiness) or \
                   any(word in current_topic.lower() for word in ["connect", "relationship", "how these", "together", "support", "benefits", "make it viable"])
                   
        elif self.current_phase == ConversationPhase.SYNTHESIS:
            # Transition to APPLICATION when user wants to apply knowledge
            return (message_count >= 6 and understanding == "high") or \
                   any(word in current_topic.lower() for word in ["apply", "my design", "project", "implement", "using", "building", "orientation", "maximizes"])
                   
        elif self.current_phase == ConversationPhase.APPLICATION:
            # Transition to REFLECTION when user evaluates or reflects
            return (message_count >= 8 and readiness) or \
                   any(word in current_topic.lower() for word in ["learned", "looking back", "feel confident", "understand", "realized", "discovered", "now see"])
        
        return False
    
    def _determine_next_phase(self, analysis: Dict) -> ConversationPhase:
        """Determine the next conversation phase"""
        
        phase_sequence = [
            ConversationPhase.DISCOVERY,
            ConversationPhase.EXPLORATION,
            ConversationPhase.SYNTHESIS,
            ConversationPhase.APPLICATION,
            ConversationPhase.REFLECTION
        ]
        
        current_index = phase_sequence.index(self.current_phase)
        next_index = min(current_index + 1, len(phase_sequence) - 1)
        
        return phase_sequence[next_index]
    
    def _generate_progression_guidance(self, analysis: Dict) -> Dict[str, Any]:
        """Generate guidance for conversation progression"""
        
        current_phase = self.current_phase
        
        guidance = {
            "phase_objectives": self._get_phase_objectives(current_phase),
            "suggested_approaches": self._get_suggested_approaches(current_phase),
            "success_indicators": self._get_success_indicators(current_phase),
            "next_phase_preparation": self._get_next_phase_preparation(current_phase)
        }
        
        return guidance
    
    def _get_phase_objectives(self, phase: ConversationPhase) -> List[str]:
        """Get objectives for current phase"""
        
        objectives = {
            ConversationPhase.DISCOVERY: [
                "Understand user's intent and interests",
                "Open relevant design space dimensions",
                "Establish learning baseline",
                "Build engagement and rapport"
            ],
            ConversationPhase.EXPLORATION: [
                "Deepen understanding of key concepts",
                "Explore multiple perspectives and approaches",
                "Address knowledge gaps",
                "Build foundational knowledge"
            ],
            ConversationPhase.SYNTHESIS: [
                "Connect different ideas and concepts",
                "Identify patterns and relationships",
                "Form insights and principles",
                "Prepare for practical application"
            ],
            ConversationPhase.APPLICATION: [
                "Apply knowledge to specific problems",
                "Practice and refine skills",
                "Build confidence in application",
                "Receive feedback and improvement"
            ],
            ConversationPhase.REFLECTION: [
                "Evaluate understanding and progress",
                "Identify remaining gaps",
                "Plan next learning steps",
                "Celebrate achievements"
            ]
        }
        
        return objectives.get(phase, [])
    
    def _get_suggested_approaches(self, phase: ConversationPhase) -> List[str]:
        """Get suggested approaches for current phase"""
        
        approaches = {
            ConversationPhase.DISCOVERY: [
                "Ask open-ended questions",
                "Listen actively and reflect back",
                "Validate user's interests and concerns",
                "Provide encouraging feedback"
            ],
            ConversationPhase.EXPLORATION: [
                "Provide examples and case studies",
                "Ask probing questions",
                "Introduce new concepts gradually",
                "Connect to user's existing knowledge"
            ],
            ConversationPhase.SYNTHESIS: [
                "Help identify connections between ideas",
                "Ask synthesis questions",
                "Encourage pattern recognition",
                "Support insight formation"
            ],
            ConversationPhase.APPLICATION: [
                "Provide practice opportunities",
                "Give constructive feedback",
                "Encourage experimentation",
                "Support problem-solving"
            ],
            ConversationPhase.REFLECTION: [
                "Ask reflective questions",
                "Help evaluate progress",
                "Identify next steps",
                "Celebrate learning achievements"
            ]
        }
        
        return approaches.get(phase, [])
    
    def _get_success_indicators(self, phase: ConversationPhase) -> List[str]:
        """Get indicators of success for current phase"""
        
        indicators = {
            ConversationPhase.DISCOVERY: [
                "User shows clear interests and intent",
                "Relevant design dimensions identified",
                "Engagement and rapport established",
                "Learning baseline established"
            ],
            ConversationPhase.EXPLORATION: [
                "User demonstrates growing understanding",
                "Knowledge gaps being addressed",
                "User asks deeper questions",
                "Concepts being connected"
            ],
            ConversationPhase.SYNTHESIS: [
                "User identifies patterns and relationships",
                "Insights and principles emerging",
                "User can explain concepts in their own words",
                "Ready for practical application"
            ],
            ConversationPhase.APPLICATION: [
                "User successfully applies knowledge",
                "Skills being practiced and refined",
                "Confidence growing in application",
                "Feedback being incorporated"
            ],
            ConversationPhase.REFLECTION: [
                "User can evaluate their own understanding",
                "Gaps and next steps identified",
                "Learning achievements recognized",
                "Future learning planned"
            ]
        }
        
        return indicators.get(phase, [])
    
    def _get_next_phase_preparation(self, phase: ConversationPhase) -> List[str]:
        """Get preparation needed for next phase"""
        
        preparation = {
            ConversationPhase.DISCOVERY: [
                "Prepare exploration strategies",
                "Identify key concepts to introduce",
                "Plan knowledge gap addressing",
                "Design engagement activities"
            ],
            ConversationPhase.EXPLORATION: [
                "Prepare synthesis activities",
                "Identify connection opportunities",
                "Plan insight formation support",
                "Design application preparation"
            ],
            ConversationPhase.SYNTHESIS: [
                "Prepare application opportunities",
                "Identify practice scenarios",
                "Plan feedback strategies",
                "Design confidence building"
            ],
            ConversationPhase.APPLICATION: [
                "Prepare reflection activities",
                "Identify evaluation criteria",
                "Plan next step identification",
                "Design celebration activities"
            ],
            ConversationPhase.REFLECTION: [
                "Prepare new topic exploration",
                "Identify advanced concepts",
                "Plan continued learning",
                "Design ongoing support"
            ]
        }
        
        return preparation.get(phase, [])
    
    def _extract_current_topic(self, user_input: str) -> str:
        """Extract current topic from user input"""
        topics = self._extract_topics(user_input)
        return topics[0] if topics else "general"
    
    def _assess_understanding_depth(self, user_input: str) -> str:
        """Assess depth of understanding from user input"""
        input_lower = user_input.lower()
        
        # Advanced understanding indicators
        synthesis_indicators = [
            "connect", "relationship", "how these", "together", "integrate",
            "because", "therefore", "however", "although", "considering",
            "support", "benefits", "make it viable", "work together"
        ]
        
        # Application indicators
        application_indicators = [
            "apply", "my design", "project", "implement", "using",
            "building", "orientation", "maximizes", "creating", "spaces"
        ]
        
        # Reflection indicators
        reflection_indicators = [
            "learned", "looking back", "feel confident", "understand",
            "realized", "discovered", "now see", "appreciate"
        ]
        
        # Count indicators
        synthesis_count = sum(1 for term in synthesis_indicators if term in input_lower)
        application_count = sum(1 for term in application_indicators if term in input_lower)
        reflection_count = sum(1 for term in reflection_indicators if term in input_lower)
        
        # Determine understanding level
        if reflection_count >= 2 or (synthesis_count >= 2 and application_count >= 1):
            return "high"
        elif synthesis_count >= 2 or application_count >= 2:
            return "medium"
        elif synthesis_count >= 1 or application_count >= 1:
            return "medium"
        elif any(word in input_lower for word in ["understand", "involves", "factors", "economic", "social", "environmental"]):
            return "medium"  # User shows some understanding of concepts
        else:
            return "low"
    
    def _assess_engagement_trend(self, state: Any) -> str:
        """Assess engagement trend from conversation history"""
        # Simplified - would analyze message history
        return "stable"
    
    def _assess_knowledge_demonstration(self, user_input: str) -> bool:
        """Assess if user is demonstrating knowledge"""
        # Simplified - would look for evidence of learning
        return len(user_input.split()) > 10
    
    def _assess_readiness_for_advancement(self, user_input: str, state: Any) -> bool:
        """Assess if user is ready to advance to next phase"""
        input_lower = user_input.lower()
        
        # Readiness indicators
        readiness_indicators = [
            "can you show me", "examples", "demonstrate", "how to",
            "connect", "relationship", "together", "integrate",
            "apply", "my project", "implement", "using",
            "learned", "understand", "feel confident", "realized"
        ]
        
        # Count readiness indicators
        readiness_count = sum(1 for term in readiness_indicators if term in input_lower)
        
        # Also consider message length as a basic indicator
        word_count = len(user_input.split())
        
        # User is ready if they show multiple readiness indicators or have substantial input
        return readiness_count >= 1 or word_count > 15
    
    def _summarize_conversation_progress(self) -> Dict[str, Any]:
        """Summarize overall conversation progress"""
        
        # Extract project context from state if available
        project_context = {}
        if hasattr(self, 'current_state') and self.current_state:
            # PRIORITY 1: Use the state's building_type if already set
            if hasattr(self.current_state, 'building_type') and self.current_state.building_type and self.current_state.building_type != "unknown":
                project_context['building_type'] = self.current_state.building_type
                logger.info(f"🏗️ Using state building_type: {self.current_state.building_type}")
            else:
                # PRIORITY 2: Try to extract building type from design brief
                design_brief = getattr(self.current_state, 'current_design_brief', '')
                if design_brief:
                    # Comprehensive building type detection using enhanced patterns
                    project_context['building_type'] = self._extract_building_type_from_text(design_brief)
                    
                    # Also check recent messages if no design brief
                    if hasattr(self.current_state, 'messages') and self.current_state.messages:
                        for msg in reversed(self.current_state.messages):
                            if msg.get('role') == 'user':
                                user_building_type = self._extract_building_type_from_text(msg['content'])
                                if user_building_type != "mixed_use":
                                    project_context['building_type'] = user_building_type
                                    break
        
                # Assess complexity based on brief content
                brief_lower = design_brief.lower()
                if any(word in brief_lower for word in ['sustainable', 'complex', 'advanced', 'innovative']):
                    project_context['complexity_level'] = 'high'
                elif any(word in brief_lower for word in ['simple', 'basic', 'standard']):
                    project_context['complexity_level'] = 'moderate'
                else:
                    project_context['complexity_level'] = 'low'
        
        # Generate challenges and opportunities based on current phase
        challenges = []
        opportunities = []
        
        if self.current_phase == ConversationPhase.DISCOVERY:
            challenges = ["Understanding project scope", "Identifying key requirements"]
            opportunities = ["Exploring design possibilities", "Building foundational knowledge"]
        elif self.current_phase == ConversationPhase.EXPLORATION:
            challenges = ["Processing complex information", "Connecting theoretical concepts"]
            opportunities = ["Learning from examples", "Developing analytical skills"]
        elif self.current_phase == ConversationPhase.SYNTHESIS:
            challenges = ["Integrating diverse concepts", "Forming coherent insights"]
            opportunities = ["Creating innovative solutions", "Building design confidence"]
        elif self.current_phase == ConversationPhase.APPLICATION:
            challenges = ["Applying knowledge practically", "Overcoming implementation barriers"]
            opportunities = ["Demonstrating skills", "Receiving constructive feedback"]
        elif self.current_phase == ConversationPhase.REFLECTION:
            challenges = ["Evaluating progress objectively", "Identifying remaining gaps"]
            opportunities = ["Celebrating achievements", "Planning next steps"]
        
        return {
            "total_milestones": len(self.milestones),
            "current_phase": self.current_phase.value,
            "opened_dimensions": [d.value for d in self.opened_dimensions],
            "user_profile": self.user_profile,
            "learning_progress": self._assess_learning_progress(),
            "conversation_quality": self._assess_conversation_quality(),
            "project_context": project_context,
            "challenges": challenges,
            "opportunities": opportunities
        }
    
    def _assess_learning_progress(self) -> Dict[str, Any]:
        """Assess overall learning progress"""
        
        if not self.milestones:
            return {"status": "not_started", "progress": 0}
        
        # Calculate progress based on phases completed
        phase_values = {
            ConversationPhase.DISCOVERY: 0.2,
            ConversationPhase.EXPLORATION: 0.4,
            ConversationPhase.SYNTHESIS: 0.6,
            ConversationPhase.APPLICATION: 0.8,
            ConversationPhase.REFLECTION: 1.0
        }
        
        current_progress = phase_values.get(self.current_phase, 0)
        
        return {
            "status": "in_progress",
            "progress": current_progress,
            "phases_completed": len([m for m in self.milestones if m.phase != self.current_phase]),
            "current_phase_progress": self._assess_current_phase_progress()
        }
    
    def _assess_current_phase_progress(self) -> float:
        """Assess progress within current phase"""
        # Simplified - would analyze recent milestones and interactions
        return 0.5
    
    def _assess_conversation_quality(self) -> Dict[str, Any]:
        """Assess overall conversation quality"""
        
        if not self.milestones:
            return {"quality": "unknown", "strengths": [], "improvements": []}
        
        # Analyze milestone patterns
        engagement_levels = [m.engagement_level for m in self.milestones]
        understanding_levels = [m.user_understanding for m in self.milestones]
        
        avg_engagement = sum(1 for level in engagement_levels if level == "high") / len(engagement_levels)
        avg_understanding = sum(1 for level in understanding_levels if level in ["medium", "high"]) / len(understanding_levels)
        
        quality_score = (avg_engagement + avg_understanding) / 2
        
        if quality_score > 0.7:
            quality = "excellent"
        elif quality_score > 0.5:
            quality = "good"
        else:
            quality = "needs_improvement"
        
        return {
            "quality": quality,
            "score": quality_score,
            "engagement_trend": "improving" if avg_engagement > 0.5 else "declining",
            "understanding_trend": "improving" if avg_understanding > 0.5 else "declining"
        } 

    def get_current_milestone(self) -> Optional[ConversationMilestone]:
        """Get the current active milestone"""
        if not self.milestones:
            return None
        return self.milestones[-1]
    
    def get_next_milestone(self) -> Optional[MilestoneType]:
        """Get the next milestone type based on current progress"""
        current_milestone = self.get_current_milestone()
        if not current_milestone:
            # First milestone for current phase
            phase_sequence = self.progression_sequence.get(self.current_phase, [])
            return phase_sequence[0] if phase_sequence else None
        
        # Get next milestone in sequence
        phase_sequence = self.progression_sequence.get(self.current_phase, [])
        try:
            current_index = phase_sequence.index(current_milestone.milestone_type)
            if current_index + 1 < len(phase_sequence):
                return phase_sequence[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def assess_milestone_completion(self, user_input: str, current_response: str, state: Any) -> Dict[str, Any]:
        """Assess if current milestone is complete and determine next steps"""
        # Store state for context access
        self.current_state = state
        
        current_milestone = self.get_current_milestone()
        if not current_milestone:
            return {"milestone_complete": False, "next_milestone": None, "guidance": "No active milestone"}
        
        # Assess completion based on milestone type
        completion_criteria = self._get_completion_criteria(current_milestone.milestone_type)
        completion_status = self._evaluate_completion_criteria(user_input, current_response, state, completion_criteria)
        
        if completion_status["complete"]:
            # Create next milestone
            next_milestone_type = self.get_next_milestone()
            if next_milestone_type:
                next_milestone = self._create_milestone(next_milestone_type, user_input, state)
                self.milestones.append(next_milestone)
                return {
                    "milestone_complete": True,
                    "next_milestone": next_milestone,
                    "guidance": self._get_milestone_guidance(next_milestone)
                }
            else:
                # Phase complete, check if ready for next phase
                return self._assess_phase_transition(user_input, state)
        
        return {
            "milestone_complete": False,
            "next_milestone": current_milestone,
            "guidance": self._get_milestone_guidance(current_milestone)
        }
    
    def _get_completion_criteria(self, milestone_type: MilestoneType) -> Dict[str, Any]:
        """Get completion criteria for a milestone type"""
        criteria_map = {
            MilestoneType.PHASE_ENTRY: {
                "understanding_demonstrated": True,
                "engagement_shown": True,
                "topic_identified": True
            },
            MilestoneType.KNOWLEDGE_ACQUISITION: {
                "new_knowledge_demonstrated": True,
                "concept_understanding": True,
                "application_readiness": True
            },
            MilestoneType.SKILL_DEMONSTRATION: {
                "skill_application": True,
                "problem_solving": True,
                "confidence_demonstrated": True
            },
            MilestoneType.INSIGHT_FORMATION: {
                "connections_made": True,
                "patterns_identified": True,
                "principles_formed": True
            },
            MilestoneType.PROBLEM_SOLVING: {
                "problem_identified": True,
                "solution_developed": True,
                "approach_justified": True
            },
            MilestoneType.REFLECTION_POINT: {
                "progress_evaluated": True,
                "gaps_identified": True,
                "next_steps_planned": True
            },
            MilestoneType.READINESS_ASSESSMENT: {
                "phase_objectives_met": True,
                "readiness_demonstrated": True,
                "advancement_appropriate": True
            }
        }
        return criteria_map.get(milestone_type, {})
    
    def _evaluate_completion_criteria(self, user_input: str, current_response: str, state: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if completion criteria are met"""
        evaluation = {"complete": True, "details": {}}
        
        for criterion, required in criteria.items():
            if required:
                result = self._evaluate_single_criterion(criterion, user_input, current_response, state)
                evaluation["details"][criterion] = result
                if not result["met"]:
                    evaluation["complete"] = False
        
        return evaluation
    
    def _evaluate_single_criterion(self, criterion: str, user_input: str, current_response: str, state: Any) -> Dict[str, Any]:
        """Evaluate a single completion criterion"""
        # This is a simplified evaluation - in practice, you'd use more sophisticated analysis
        user_input_lower = user_input.lower()
        
        criterion_evaluators = {
            "understanding_demonstrated": lambda: {"met": len(user_input.split()) > 10, "confidence": 0.7},
            "engagement_shown": lambda: {"met": "?" in user_input or "!" in user_input, "confidence": 0.6},
            "topic_identified": lambda: {"met": len(self._extract_topics(user_input)) > 0, "confidence": 0.8},
            "new_knowledge_demonstrated": lambda: {"met": any(word in user_input_lower for word in ["learned", "understood", "realized"]), "confidence": 0.7},
            "concept_understanding": lambda: {"met": any(word in user_input_lower for word in ["because", "since", "therefore"]), "confidence": 0.6},
            "application_readiness": lambda: {"met": any(word in user_input_lower for word in ["apply", "use", "implement"]), "confidence": 0.5},
            "skill_application": lambda: {"met": any(word in user_input_lower for word in ["designed", "planned", "created"]), "confidence": 0.7},
            "problem_solving": lambda: {"met": any(word in user_input_lower for word in ["solve", "address", "handle"]), "confidence": 0.6},
            "confidence_demonstrated": lambda: {"met": any(word in user_input_lower for word in ["confident", "sure", "clear"]), "confidence": 0.5},
            "connections_made": lambda: {"met": any(word in user_input_lower for word in ["connect", "relate", "link"]), "confidence": 0.6},
            "patterns_identified": lambda: {"met": any(word in user_input_lower for word in ["pattern", "trend", "similar"]), "confidence": 0.5},
            "principles_formed": lambda: {"met": any(word in user_input_lower for word in ["principle", "rule", "guideline"]), "confidence": 0.6},
            "problem_identified": lambda: {"met": any(word in user_input_lower for word in ["problem", "issue", "challenge"]), "confidence": 0.7},
            "solution_developed": lambda: {"met": any(word in user_input_lower for word in ["solution", "approach", "method"]), "confidence": 0.6},
            "approach_justified": lambda: {"met": any(word in user_input_lower for word in ["because", "since", "therefore"]), "confidence": 0.5},
            "progress_evaluated": lambda: {"met": any(word in user_input_lower for word in ["progress", "improved", "better"]), "confidence": 0.6},
            "gaps_identified": lambda: {"met": any(word in user_input_lower for word in ["gap", "missing", "need"]), "confidence": 0.5},
            "next_steps_planned": lambda: {"met": any(word in user_input_lower for word in ["next", "plan", "will"]), "confidence": 0.6},
            "phase_objectives_met": lambda: {"met": self._assess_phase_objectives_met(state), "confidence": 0.7},
            "readiness_demonstrated": lambda: {"met": self._assess_readiness_demonstrated(user_input), "confidence": 0.6},
            "advancement_appropriate": lambda: {"met": self._assess_advancement_appropriate(state), "confidence": 0.5}
        }
        
        evaluator = criterion_evaluators.get(criterion)
        if evaluator:
            return evaluator()
        else:
            return {"met": False, "confidence": 0.0}
    
    def _assess_phase_objectives_met(self, state: Any) -> bool:
        """Assess if phase objectives have been met"""
        # Simplified assessment - in practice, you'd analyze conversation history
        return True  # Placeholder
    
    def _assess_readiness_demonstrated(self, user_input: str) -> bool:
        """Assess if user demonstrates readiness for advancement"""
        readiness_indicators = ["ready", "prepared", "confident", "understand", "clear"]
        return any(indicator in user_input.lower() for indicator in readiness_indicators)
    
    def _assess_advancement_appropriate(self, state: Any) -> bool:
        """Assess if advancement to next phase is appropriate"""
        # Simplified assessment - in practice, you'd analyze comprehensive state
        return True  # Placeholder
    
    def _create_milestone(self, milestone_type: MilestoneType, user_input: str, state: Any) -> ConversationMilestone:
        """Create a new milestone"""
        # Store state for context access
        self.current_state = state
        
        current_topic = self._extract_current_topic(user_input)
        understanding = self._assess_understanding_depth(user_input)
        engagement = self._assess_engagement_trend(state)
        
        # Calculate progress percentage
        phase_sequence = self.progression_sequence.get(self.current_phase, [])
        try:
            milestone_index = phase_sequence.index(milestone_type)
            progress_percentage = (milestone_index / len(phase_sequence)) * 100
        except ValueError:
            progress_percentage = 0.0
        
        # Get required actions and success criteria
        required_actions = self._get_milestone_required_actions(milestone_type)
        success_criteria = self._get_milestone_success_criteria(milestone_type)
        
        return ConversationMilestone(
            milestone_type=milestone_type,
            phase=self.current_phase,
            topic=current_topic,
            user_understanding=understanding,
            engagement_level=engagement,
            progress_percentage=progress_percentage,
            required_actions=required_actions,
            success_criteria=success_criteria
        )
    
    def _get_milestone_required_actions(self, milestone_type: MilestoneType) -> List[str]:
        """Get required actions for a milestone type"""
        actions_map = {
            MilestoneType.PHASE_ENTRY: [
                "Demonstrate understanding of phase objectives",
                "Show engagement with current topic",
                "Identify specific areas of interest"
            ],
            MilestoneType.KNOWLEDGE_ACQUISITION: [
                "Demonstrate new knowledge acquisition",
                "Show understanding of key concepts",
                "Express readiness to apply knowledge"
            ],
            MilestoneType.SKILL_DEMONSTRATION: [
                "Apply knowledge to specific problems",
                "Show confidence in application",
                "Demonstrate problem-solving skills"
            ],
            MilestoneType.INSIGHT_FORMATION: [
                "Make connections between ideas",
                "Identify patterns and relationships",
                "Form principles or guidelines"
            ],
            MilestoneType.PROBLEM_SOLVING: [
                "Identify specific problems or challenges",
                "Develop and justify solutions",
                "Show systematic approach to problem-solving"
            ],
            MilestoneType.REFLECTION_POINT: [
                "Evaluate current progress and understanding",
                "Identify remaining gaps or challenges",
                "Plan next steps in learning journey"
            ],
            MilestoneType.READINESS_ASSESSMENT: [
                "Demonstrate mastery of phase objectives",
                "Show readiness for advancement",
                "Express confidence in current understanding"
            ]
        }
        return actions_map.get(milestone_type, [])
    
    def _get_milestone_success_criteria(self, milestone_type: MilestoneType) -> List[str]:
        """Get success criteria for a milestone type"""
        criteria_map = {
            MilestoneType.PHASE_ENTRY: [
                "Clear understanding of phase objectives demonstrated",
                "Active engagement with topic shown",
                "Specific interests or questions identified"
            ],
            MilestoneType.KNOWLEDGE_ACQUISITION: [
                "New knowledge clearly demonstrated",
                "Key concepts understood and explained",
                "Readiness to apply knowledge expressed"
            ],
            MilestoneType.SKILL_DEMONSTRATION: [
                "Knowledge successfully applied to problems",
                "Confidence in application demonstrated",
                "Problem-solving approach shown"
            ],
            MilestoneType.INSIGHT_FORMATION: [
                "Connections between ideas made",
                "Patterns or relationships identified",
                "Principles or guidelines formed"
            ],
            MilestoneType.PROBLEM_SOLVING: [
                "Specific problems clearly identified",
                "Solutions developed and justified",
                "Systematic approach demonstrated"
            ],
            MilestoneType.REFLECTION_POINT: [
                "Current progress accurately evaluated",
                "Gaps or challenges identified",
                "Next steps clearly planned"
            ],
            MilestoneType.READINESS_ASSESSMENT: [
                "Phase objectives mastered",
                "Readiness for advancement demonstrated",
                "Confidence in understanding expressed"
            ]
        }
        return criteria_map.get(milestone_type, [])
    
    def _get_milestone_guidance(self, milestone: ConversationMilestone) -> str:
        """Get dynamic guidance for the current milestone that encourages LLM-based responses"""
        guidance_map = {
            MilestoneType.PHASE_ENTRY: f"Welcome to the {milestone.phase.value} phase! Focus on exploring {milestone.topic or 'your design interests'} through active inquiry and discovery.",
            MilestoneType.KNOWLEDGE_ACQUISITION: f"Deepen your understanding of {milestone.topic or 'key concepts'} by asking specific questions and seeking examples that resonate with your project.",
            MilestoneType.SKILL_DEMONSTRATION: f"Apply what you've learned about {milestone.topic or 'these concepts'} by describing how you would approach a specific design challenge.",
            MilestoneType.INSIGHT_FORMATION: f"Connect the ideas you've learned by identifying patterns or relationships in {milestone.topic or 'your understanding'} that could inform your design decisions.",
            MilestoneType.PROBLEM_SOLVING: f"Tackle a specific problem related to {milestone.topic or 'your design'} by breaking it down into manageable components and exploring multiple solutions.",
            MilestoneType.REFLECTION_POINT: f"Reflect on your progress with {milestone.topic or 'your learning'} by evaluating what you've discovered and identifying areas for further exploration.",
            MilestoneType.READINESS_ASSESSMENT: f"Assess your readiness to advance by considering how confident you feel about {milestone.topic or 'your current understanding'} and what additional support you might need."
        }
        return guidance_map.get(milestone.milestone_type, "Continue exploring and learning through active inquiry!")
    
    def _assess_phase_transition(self, user_input: str, state: Any) -> Dict[str, Any]:
        """Assess if ready to transition to next phase"""
        # Store state for context access
        self.current_state = state
        
        phase_order = list(ConversationPhase)
        try:
            current_index = phase_order.index(self.current_phase)
            if current_index + 1 < len(phase_order):
                next_phase = phase_order[current_index + 1]
                # Create phase entry milestone for next phase
                phase_entry_milestone = self._create_milestone(MilestoneType.PHASE_ENTRY, user_input, state)
                phase_entry_milestone.phase = next_phase
                self.milestones.append(phase_entry_milestone)
                self.current_phase = next_phase
                
                return {
                    "milestone_complete": True,
                    "phase_transition": True,
                    "next_phase": next_phase,
                    "next_milestone": phase_entry_milestone,
                    "guidance": f"Congratulations! You're ready to move to the {next_phase.value} phase."
                }
        except ValueError:
            pass
        
        return {
            "milestone_complete": False,
            "phase_transition": False,
            "guidance": "Continue working on current objectives."
        }

    def get_milestone_driven_agent_guidance(self, user_input: str, state: Any) -> Dict[str, Any]:
        """Get agent guidance based on current milestone"""
        # Store state for context access
        self.current_state = state
        
        current_milestone = self.get_current_milestone()
        if not current_milestone:
            # Create first milestone for current phase
            first_milestone_type = self.progression_sequence.get(self.current_phase, [MilestoneType.PHASE_ENTRY])[0]
            current_milestone = self._create_milestone(first_milestone_type, user_input, state)
            self.milestones.append(current_milestone)
        
        # Get agent focus for current milestone
        milestone_rules = self.milestone_rules.get(current_milestone.milestone_type, {})
        agent_focus = milestone_rules.get("agent_focus", "context_agent")
        
        # Get specific guidance for the agent
        agent_guidance = self._get_agent_specific_guidance(current_milestone, agent_focus)
        
        return {
            "current_milestone": current_milestone,
            "agent_focus": agent_focus,
            "agent_guidance": agent_guidance,
            "milestone_progress": current_milestone.progress_percentage,
            "phase": self.current_phase.value
        }
    
    def _get_agent_specific_guidance(self, milestone: ConversationMilestone, agent_focus: str) -> Dict[str, Any]:
        """Get specific guidance for the focused agent"""
        guidance_map = {
            "context_agent": {
                "primary_role": "Analyze user input and conversation context",
                "focus_areas": ["intent classification", "conversation state", "routing decisions"],
                "milestone_context": f"Current milestone: {milestone.milestone_type.value} in {milestone.phase.value} phase",
                "guidance": f"Focus on understanding user intent and ensuring conversation aligns with {milestone.milestone_type.value} objectives"
            },
            "domain_expert": {
                "primary_role": "Provide architectural knowledge and expertise",
                "focus_areas": ["knowledge provision", "example provision", "web search"],
                "milestone_context": f"Current milestone: {milestone.milestone_type.value} in {milestone.phase.value} phase",
                "guidance": f"Provide knowledge that supports {milestone.milestone_type.value} objectives, focusing on {milestone.topic or 'relevant concepts'}"
            },
            "socratic_tutor": {
                "primary_role": "Generate Socratic questions and guidance",
                "focus_areas": ["question generation", "scaffolding", "critical thinking"],
                "milestone_context": f"Current milestone: {milestone.milestone_type.value} in {milestone.phase.value} phase",
                "guidance": f"Generate questions that help user achieve {milestone.milestone_type.value} objectives, focusing on {milestone.required_actions}"
            },
            "cognitive_enhancement": {
                "primary_role": "Provide cognitive challenges and enhancement",
                "focus_areas": ["cognitive challenges", "skill development", "complex thinking"],
                "milestone_context": f"Current milestone: {milestone.milestone_type.value} in {milestone.phase.value} phase",
                "guidance": f"Provide challenges that support {milestone.milestone_type.value} objectives, focusing on {milestone.success_criteria}"
            },
            "analysis_agent": {
                "primary_role": "Analyze design and provide insights",
                "focus_areas": ["design analysis", "skill assessment", "progress evaluation"],
                "milestone_context": f"Current milestone: {milestone.milestone_type.value} in {milestone.phase.value} phase",
                "guidance": f"Analyze progress toward {milestone.milestone_type.value} objectives and provide insights for advancement"
            }
        }
        
        return guidance_map.get(agent_focus, {
            "primary_role": "Support conversation progression",
            "focus_areas": ["general support"],
            "milestone_context": f"Current milestone: {milestone.milestone_type.value}",
            "guidance": "Support the current milestone objectives"
        })
    
    def _extract_building_type_from_text(self, text: str) -> str:
        """
        Enhanced building type detection - SINGLE SOURCE OF TRUTH.
        This method is called once and the result persists throughout the conversation.
        """
        if not text:
            return "unknown"
        
        text_lower = text.lower()
        
        # Enhanced building type detection patterns (SINGLE SOURCE OF TRUTH)
        detection_patterns = [
            # High Priority - Specific building types
            ("learning_center", ["learning center", "education center", "learning hub", "training center", "skill center", "study center", "workshop center", "kindergarten"], 10),
            ("community_center", ["community center", "community facility", "civic center", "public center", "social hub", "gathering place", "neighborhood center", "town hall", "community center for sports", "community sports center"], 10),
            ("sports_center", ["sports center", "fitness center", "gym", "athletic center", "sports facility", "fitness facility", "athletic facility", "sports complex", "recreation center", "activity center"], 10),
            ("cultural_institution", ["museum", "gallery", "theater", "cultural center", "arts center", "performance center", "exhibition center", "cultural hub", "heritage center"], 10),
            ("library", ["library", "librarian", "reading room", "study space", "research center", "information center", "book center"], 10),
            ("research_facility", ["research facility", "laboratory", "lab", "research center", "innovation center", "development center", "testing facility"], 10),
            
            # High Priority - Healthcare
            ("hospital", ["hospital", "medical center", "health center", "clinic", "medical facility", "healthcare facility", "treatment center"], 9),
            ("specialized_clinic", ["specialized clinic", "specialty clinic", "medical clinic", "health clinic", "outpatient clinic", "diagnostic center"], 9),
            ("wellness_center", ["wellness center", "health center", "medical spa", "holistic center", "alternative medicine", "wellness facility"], 9),
            ("rehabilitation_center", ["rehabilitation center", "rehab center", "recovery center", "therapy center", "treatment facility"], 9),
            
            # High Priority - Educational
            ("educational", ["school", "university", "college", "classroom", "educational", "learning", "academy", "institute"], 9),
            
            # Medium Priority - Residential
            ("residential", ["house", "home", "apartment", "residential", "housing", "dwelling", "residence", "domestic"], 8),
            ("multi_family", ["multi-family", "apartment building", "condominium", "townhouse", "duplex", "triplex", "residential complex"], 8),
            ("senior_housing", ["senior housing", "elderly housing", "retirement community", "assisted living", "nursing home", "care facility"], 8),
            ("student_housing", ["student housing", "dormitory", "student residence", "college housing", "university housing"], 8),
            
            # Medium Priority - Commercial
            ("office", ["office", "workplace", "corporate", "business", "commercial", "workspace", "professional", "executive"], 7),
            ("retail", ["store", "shop", "retail", "commercial", "market", "shopping", "merchant", "boutique"], 7),
            ("restaurant", ["restaurant", "cafe", "dining", "eatery", "bistro", "food service", "culinary", "dining establishment"], 7),
            ("hotel", ["hotel", "lodging", "accommodation", "inn", "resort", "guesthouse", "hostel", "bed and breakfast"], 7),
            
            # Medium Priority - Community & Recreation
            ("recreation_center", ["recreation center", "leisure center", "entertainment center"], 7),
            ("senior_center", ["senior center", "elderly center", "aging center", "retirement center", "adult center", "mature center"], 7),
            ("youth_center", ["youth center", "teen center", "adolescent center", "young center", "teenager center"], 7),
            
            # Medium Priority - Industrial
            ("industrial", ["factory", "warehouse", "industrial", "manufacturing", "production", "industrial facility", "manufacturing plant"], 6),
            ("logistics_center", ["logistics center", "distribution center", "fulfillment center", "storage facility", "warehouse facility"], 6),
            ("research_industrial", ["research and development", "R&D facility", "innovation center", "technology center", "development facility"], 6),
            
            # Medium Priority - Transportation
            ("transportation_hub", ["transportation hub", "transit center", "transport hub", "mobility center", "travel center"], 6),
            ("parking_facility", ["parking facility", "parking garage", "parking structure", "parking center", "car park"], 6),
            ("maintenance_facility", ["maintenance facility", "service center", "repair facility", "maintenance center"], 6),
            
            # Lower Priority - Religious & Spiritual
            ("religious", ["church", "temple", "mosque", "synagogue", "religious", "worship", "spiritual", "sacred", "faith center"], 5),
            ("meditation_center", ["meditation center", "spiritual center", "zen center", "mindfulness center", "contemplation center"], 5),
            
            # Lower Priority - Agricultural & Environmental
            ("agricultural", ["farm", "agricultural", "greenhouse", "nursery", "agricultural facility", "farming center"], 4),
            ("environmental_center", ["environmental center", "nature center", "conservation center", "ecology center", "sustainability center"], 4),
            
            # Lower Priority - Specialized
            ("conference_center", ["conference center", "convention center", "meeting center", "event center", "summit center"], 4),
            ("innovation_hub", ["innovation hub", "startup center", "entrepreneurial center", "business incubator", "tech hub"], 4),
            ("creative_workspace", ["creative workspace", "artist studio", "design studio", "creative center", "artistic space"], 4),
            
            # Lower Priority - Government & Public
            ("government", ["government building", "civic building", "public building", "administrative center", "public service"], 3),
            ("emergency_services", ["fire station", "police station", "emergency center", "public safety", "emergency facility"], 3),
            ("utility_facility", ["utility facility", "power plant", "water treatment", "energy center", "infrastructure facility"], 3),
            
            # Lowest Priority - Mixed Use (only if no specific type detected)
            ("mixed_use", ["mixed use", "multi-use", "combined use", "integrated", "hybrid", "versatile", "flexible"], 2)
        ]
        
        # Score each building type based on keyword matches
        building_scores = {}
        for building_type, keywords, base_priority in detection_patterns:
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += base_priority
                    # Bonus for exact matches
                    if keyword == text_lower.strip():
                        score += 5
                    # Bonus for longer, more specific keywords
                    if len(keyword.split()) > 1:
                        score += 2
                    # Bonus for multiple keyword matches
                    if text_lower.count(keyword) > 1:
                        score += 1
            
            if score > 0:
                building_scores[building_type] = score
        
        # Return the highest scoring building type, or unknown as fallback (no more mixed_use default!)
        if building_scores:
            best_match = max(building_scores, key=building_scores.get)
            # Only return specific types if score is high enough
            if building_scores[best_match] >= 5:
                logger.info(f"🏗️ Building type detected from text: {best_match} (confidence: {building_scores[best_match]})")
                return best_match
        
        logger.info("🏗️ No specific building type detected, returning 'unknown'")
        return "unknown"

    def _assess_conversation_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess conversation analysis data and extract key insights.
        This is where building type is detected ONCE and persists.
        """
        if not analysis_data:
            return {}
        
        # PRIORITY 1: Use existing building type from state if available
        if hasattr(self.current_state, 'building_type') and self.current_state.building_type and self.current_state.building_type != "unknown":
            building_type = self.current_state.building_type
            logger.info(f"🏗️ Using existing building_type from state: {building_type}")
        else:
            # PRIORITY 2: Extract building type from text analysis
            text_analysis = analysis_data.get("text_analysis", {})
            user_building_type = text_analysis.get("building_type", "unknown")
            
            if user_building_type and user_building_type != "unknown":
                building_type = user_building_type
                logger.info(f"🏗️ Using building_type from text analysis: {building_type}")
            else:
                # PRIORITY 3: Extract from user input text
                user_input = analysis_data.get("user_input", "")
                if user_input:
                    building_type = self._extract_building_type_from_text(user_input)
                    logger.info(f"🏗️ Extracted building_type from user input: {building_type}")
                else:
                    building_type = "unknown"
                    logger.info("🏗️ No user input available, building_type set to 'unknown'")
        
        # CRITICAL: Update the state with the detected building type
        if building_type != "unknown":
            self.current_state.building_type = building_type
            logger.info(f"🏗️ Updated current_state.building_type to: {building_type}")
        
        # Return the building type for use in other parts of the system
        return {
            "building_type": building_type,
            "building_type_source": "conversation_progression_single_source",
            "building_type_persistent": True
        }