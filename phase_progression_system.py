"""
Phase Progression System - Standalone Implementation
A focused system for managing design phase progression with Socratic dialogue patterns
and internal grading capabilities.

This system operates independently of the main Mega Architectural Mentor system
to provide clean, testable phase-based assessment functionality.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesignPhase(Enum):
    """Design phases with their weights and purposes"""
    IDEATION = "ideation"
    VISUALIZATION = "visualization" 
    MATERIALIZATION = "materialization"

class SocraticStep(Enum):
    """Socratic dialogue progression steps"""
    INITIAL_CONTEXT_REASONING = "initial_context_reasoning"
    KNOWLEDGE_SYNTHESIS_TRIGGER = "knowledge_synthesis_trigger"
    SOCRATIC_QUESTIONING = "socratic_questioning"
    METACOGNITIVE_PROMPT = "metacognitive_prompt"
    # New flexible steps
    CONTEXTUAL_EXPLORATION = "contextual_exploration"
    DEEPER_INQUIRY = "deeper_inquiry"
    SYNTHESIS_CHECK = "synthesis_check"
    READINESS_ASSESSMENT = "readiness_assessment"

@dataclass
class SocraticQuestion:
    """Represents a Socratic question with its context and assessment criteria"""
    step: SocraticStep
    question_text: str
    keywords: List[str]
    assessment_criteria: Dict[str, str]
    phase: DesignPhase
    question_id: str

@dataclass
class GradingResult:
    """Result of grading a user response"""
    completeness: float  # 0-5
    depth: float  # 0-5
    relevance: float  # 0-5
    innovation: float  # 0-5
    technical_understanding: float  # 0-5
    overall_score: float  # 0-5
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PhaseProgress:
    """Tracks progress through a specific design phase"""
    phase: DesignPhase
    current_step: SocraticStep
    completed_steps: List[SocraticStep] = field(default_factory=list)
    responses: Dict[str, str] = field(default_factory=dict)  # question_id -> response
    grades: Dict[str, GradingResult] = field(default_factory=dict)  # question_id -> grade
    average_score: float = 0.0
    completion_percent: float = 0.0
    is_complete: bool = False
    start_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SessionState:
    """Tracks the overall session state and progression"""
    session_id: str
    current_phase: DesignPhase = DesignPhase.IDEATION
    phase_progress: Dict[DesignPhase, PhaseProgress] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    overall_score: float = 0.0
    session_start: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    # Added rubric/checklist tracking and timeline
    checklist_state: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # phase -> item_id -> state
    timeline: List[Dict[str, Any]] = field(default_factory=list)

class SocraticQuestionBank:
    """Manages the Socratic question bank for all phases"""
    
    def __init__(self):
        self.questions = self._initialize_question_bank()
    
    def _initialize_question_bank(self) -> Dict[DesignPhase, Dict[SocraticStep, SocraticQuestion]]:
        """Initialize the complete Socratic question bank"""
        
        return {
            DesignPhase.IDEATION: {
                SocraticStep.INITIAL_CONTEXT_REASONING: SocraticQuestion(
                    step=SocraticStep.INITIAL_CONTEXT_REASONING,
                    question_text="Before we begin designing, what do you think are the most important questions we should ask about this community?",
                    keywords=["community", "questions", "important", "designing", "begin"],
                    assessment_criteria={
                        "completeness": "Addresses multiple aspects of community needs",
                        "depth": "Shows thoughtful consideration of community context",
                        "relevance": "Questions are relevant to architectural design",
                        "innovation": "Shows creative thinking about community needs",
                        "technical_understanding": "Demonstrates understanding of design process"
                    },
                    phase=DesignPhase.IDEATION,
                    question_id="ideation_context_001"
                ),
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: SocraticQuestion(
                    step=SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
                    question_text="What are some successful examples of warehouse-to-community transformations you're aware of?",
                    keywords=["examples", "successful", "warehouse", "community", "transformations", "precedents"],
                    assessment_criteria={
                        "completeness": "Provides multiple relevant examples",
                        "depth": "Explains why examples are successful",
                        "relevance": "Examples are relevant to the project type",
                        "innovation": "Shows understanding of innovative approaches",
                        "technical_understanding": "Demonstrates knowledge of architectural precedents"
                    },
                    phase=DesignPhase.IDEATION,
                    question_id="ideation_knowledge_001"
                ),
                SocraticStep.SOCRATIC_QUESTIONING: SocraticQuestion(
                    step=SocraticStep.SOCRATIC_QUESTIONING,
                    question_text="Why might the existing industrial character be valuable to preserve? What would be lost if we completely transformed it?",
                    keywords=["industrial", "character", "preserve", "transform", "value", "lost"],
                    assessment_criteria={
                        "completeness": "Addresses both preservation and transformation aspects",
                        "depth": "Provides detailed reasoning for preservation value",
                        "relevance": "Connects to architectural heritage and context",
                        "innovation": "Shows creative thinking about adaptive reuse",
                        "technical_understanding": "Demonstrates understanding of preservation principles"
                    },
                    phase=DesignPhase.IDEATION,
                    question_id="ideation_socratic_001"
                ),
                SocraticStep.METACOGNITIVE_PROMPT: SocraticQuestion(
                    step=SocraticStep.METACOGNITIVE_PROMPT,
                    question_text="How are you approaching this problem differently than a typical new-build community center?",
                    keywords=["approaching", "differently", "typical", "new-build", "community center", "problem"],
                    assessment_criteria={
                        "completeness": "Explains the unique approach to the problem",
                        "depth": "Shows self-awareness of design thinking process",
                        "relevance": "Connects to the specific project context",
                        "innovation": "Demonstrates creative problem-solving approach",
                        "technical_understanding": "Shows understanding of design methodology"
                    },
                    phase=DesignPhase.IDEATION,
                    question_id="ideation_meta_001"
                )
            },
            
            DesignPhase.VISUALIZATION: {
                SocraticStep.INITIAL_CONTEXT_REASONING: SocraticQuestion(
                    step=SocraticStep.INITIAL_CONTEXT_REASONING,
                    question_text="How does your spatial organization respond to the site's existing conditions and program requirements?",
                    keywords=["spatial", "organization", "site", "existing", "conditions", "program", "requirements"],
                    assessment_criteria={
                        "completeness": "Addresses both site conditions and program requirements",
                        "depth": "Shows detailed understanding of spatial relationships",
                        "relevance": "Connects spatial decisions to architectural principles",
                        "innovation": "Shows creative spatial solutions",
                        "technical_understanding": "Demonstrates understanding of spatial planning"
                    },
                    phase=DesignPhase.VISUALIZATION,
                    question_id="visualization_context_001"
                ),
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: SocraticQuestion(
                    step=SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
                    question_text="What precedents inform your approach to circulation and spatial hierarchy?",
                    keywords=["precedents", "circulation", "spatial", "hierarchy", "approach"],
                    assessment_criteria={
                        "completeness": "References relevant precedents",
                        "depth": "Explains how precedents inform the approach",
                        "relevance": "Precedents are appropriate for the project type",
                        "innovation": "Shows creative adaptation of precedents",
                        "technical_understanding": "Demonstrates understanding of circulation principles"
                    },
                    phase=DesignPhase.VISUALIZATION,
                    question_id="visualization_knowledge_001"
                ),
                SocraticStep.SOCRATIC_QUESTIONING: SocraticQuestion(
                    step=SocraticStep.SOCRATIC_QUESTIONING,
                    question_text="How does your form development balance functional efficiency with architectural expression?",
                    keywords=["form", "development", "functional", "efficiency", "architectural", "expression"],
                    assessment_criteria={
                        "completeness": "Addresses both functional and expressive aspects",
                        "depth": "Shows detailed understanding of form-function relationship",
                        "relevance": "Connects to architectural design principles",
                        "innovation": "Shows creative form development",
                        "technical_understanding": "Demonstrates understanding of architectural form"
                    },
                    phase=DesignPhase.VISUALIZATION,
                    question_id="visualization_socratic_001"
                ),
                SocraticStep.METACOGNITIVE_PROMPT: SocraticQuestion(
                    step=SocraticStep.METACOGNITIVE_PROMPT,
                    question_text="What design decisions are you most confident about, and which ones need more exploration?",
                    keywords=["design", "decisions", "confident", "exploration", "need"],
                    assessment_criteria={
                        "completeness": "Identifies both confident and uncertain decisions",
                        "depth": "Shows self-awareness of design process",
                        "relevance": "Connects to the specific design challenges",
                        "innovation": "Shows willingness to explore and experiment",
                        "technical_understanding": "Demonstrates understanding of design methodology"
                    },
                    phase=DesignPhase.VISUALIZATION,
                    question_id="visualization_meta_001"
                )
            },
            
            DesignPhase.MATERIALIZATION: {
                SocraticStep.INITIAL_CONTEXT_REASONING: SocraticQuestion(
                    step=SocraticStep.INITIAL_CONTEXT_REASONING,
                    question_text="How do your material choices respond to both the building's function and its environmental context?",
                    keywords=["material", "choices", "function", "environmental", "context"],
                    assessment_criteria={
                        "completeness": "Addresses both functional and environmental considerations",
                        "depth": "Shows detailed understanding of material properties",
                        "relevance": "Connects to architectural and environmental principles",
                        "innovation": "Shows creative material solutions",
                        "technical_understanding": "Demonstrates understanding of material science"
                    },
                    phase=DesignPhase.MATERIALIZATION,
                    question_id="materialization_context_001"
                ),
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: SocraticQuestion(
                    step=SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
                    question_text="What construction precedents demonstrate effective integration of your chosen materials?",
                    keywords=["construction", "precedents", "integration", "materials", "effective"],
                    assessment_criteria={
                        "completeness": "References relevant construction precedents",
                        "depth": "Explains how precedents inform material integration",
                        "relevance": "Precedents are appropriate for the materials chosen",
                        "innovation": "Shows creative material integration approaches",
                        "technical_understanding": "Demonstrates understanding of construction methods"
                    },
                    phase=DesignPhase.MATERIALIZATION,
                    question_id="materialization_knowledge_001"
                ),
                SocraticStep.SOCRATIC_QUESTIONING: SocraticQuestion(
                    step=SocraticStep.SOCRATIC_QUESTIONING,
                    question_text="How does your technical approach balance innovation with constructability and cost considerations?",
                    keywords=["technical", "approach", "innovation", "constructability", "cost"],
                    assessment_criteria={
                        "completeness": "Addresses innovation, constructability, and cost",
                        "depth": "Shows detailed understanding of technical constraints",
                        "relevance": "Connects to practical construction realities",
                        "innovation": "Shows creative technical solutions",
                        "technical_understanding": "Demonstrates understanding of construction economics"
                    },
                    phase=DesignPhase.MATERIALIZATION,
                    question_id="materialization_socratic_001"
                ),
                SocraticStep.METACOGNITIVE_PROMPT: SocraticQuestion(
                    step=SocraticStep.METACOGNITIVE_PROMPT,
                    question_text="What aspects of your design would you prioritize if budget or time constraints required simplification?",
                    keywords=["aspects", "prioritize", "budget", "time", "constraints", "simplification"],
                    assessment_criteria={
                        "completeness": "Identifies key aspects for prioritization",
                        "depth": "Shows understanding of design value hierarchy",
                        "relevance": "Connects to practical project constraints",
                        "innovation": "Shows creative problem-solving under constraints",
                        "technical_understanding": "Demonstrates understanding of project management"
                    },
                    phase=DesignPhase.MATERIALIZATION,
                    question_id="materialization_meta_001"
                )
            }
        }
    
    def get_question(self, phase: DesignPhase, step: SocraticStep) -> Optional[SocraticQuestion]:
        """Get a specific Socratic question"""
        return self.questions.get(phase, {}).get(step)
    
    def get_next_question(self, phase: DesignPhase, completed_steps: List[SocraticStep]) -> Optional[SocraticQuestion]:
        """Get the next question in the Socratic sequence"""
        print(f"\n🏦 QUESTION_BANK: Getting next question for {phase.value}")

        phase_questions = self.questions.get(phase, {})
        print(f"   📚 Available questions for phase: {len(phase_questions)}")
        print(f"   🔑 Question keys: {list(phase_questions.keys())}")

        # Define the order of Socratic steps
        step_order = [
            SocraticStep.INITIAL_CONTEXT_REASONING,
            SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
            SocraticStep.SOCRATIC_QUESTIONING,
            SocraticStep.METACOGNITIVE_PROMPT
        ]

        print(f"   ✅ Completed steps: {[step.value for step in completed_steps]}")

        # Find the next uncompleted step
        for step in step_order:
            print(f"   🔍 Checking step: {step.value}")
            if step not in completed_steps:
                print(f"      ➡️ Step not completed")
                question = phase_questions.get(step)
                if question:
                    print(f"      ✅ Found question: {question.question_text[:60]}...")
                    return question
                else:
                    print(f"      ❌ No question available for step")
            else:
                print(f"      ⏭️ Step already completed")

        print(f"   ❌ No next question found - all steps completed")
        return None  # All steps completed

class FlexibleQuestionGenerator:
    """Generates contextual questions based on conversation history and phase needs"""

    def __init__(self):
        self.question_templates = self._initialize_question_templates()
        self.phase_keywords = self._initialize_phase_keywords()

    def _initialize_question_templates(self) -> Dict[DesignPhase, Dict[str, List[str]]]:
        """Initialize flexible question templates for each phase"""
        return {
            DesignPhase.IDEATION: {
                "exploration": [
                    "What other approaches could you consider for {topic}?",
                    "How might {concept} be interpreted differently?",
                    "What if you approached {challenge} from the perspective of {stakeholder}?",
                    "Can you think of precedents that handle {aspect} in innovative ways?"
                ],
                "clarification": [
                    "Can you elaborate on what you mean by {concept}?",
                    "How does {element} relate to your overall vision?",
                    "What specific qualities make {feature} important to your design?",
                    "Why is {consideration} particularly relevant to this project?"
                ],
                "synthesis": [
                    "How do these ideas connect to form a coherent concept?",
                    "What themes are emerging from your exploration?",
                    "Which of these directions feels most promising and why?",
                    "How might you combine {idea1} and {idea2}?"
                ]
            },
            DesignPhase.VISUALIZATION: {
                "spatial": [
                    "How does your {space} support the activities you've described?",
                    "What spatial relationships are most important in your design?",
                    "How do people move through and experience your {area}?",
                    "What views and connections does your design create?"
                ],
                "form": [
                    "How does the building form express your conceptual ideas?",
                    "What role does {element} play in the overall composition?",
                    "How do interior and exterior spaces relate to each other?",
                    "What gives your design its distinctive character?"
                ],
                "development": [
                    "How might you refine {aspect} to better serve your goals?",
                    "What design moves would strengthen your concept?",
                    "How do you balance {consideration1} with {consideration2}?",
                    "What would happen if you emphasized {feature} more strongly?"
                ]
            },
            DesignPhase.MATERIALIZATION: {
                "technical": [
                    "How do your material choices support your design intentions?",
                    "What construction approach best realizes your vision?",
                    "How do you address {technical_challenge} in your design?",
                    "What details are critical to your design's success?"
                ],
                "practical": [
                    "How does your design respond to budget and timeline constraints?",
                    "What aspects of your design are most important to preserve?",
                    "How might you phase the construction to manage complexity?",
                    "What partnerships or expertise would help realize this project?"
                ],
                "refinement": [
                    "How might you optimize {system} for better performance?",
                    "What would you change if you had to reduce the scope by 20%?",
                    "How do you ensure your design intent survives the construction process?",
                    "What innovations could make your design more impactful?"
                ]
            }
        }

    def _initialize_phase_keywords(self) -> Dict[DesignPhase, List[str]]:
        """Initialize keywords that indicate phase-relevant content"""
        return {
            DesignPhase.IDEATION: [
                "concept", "idea", "vision", "approach", "strategy", "philosophy", "inspiration",
                "community", "needs", "program", "function", "purpose", "goals", "objectives"
            ],
            DesignPhase.VISUALIZATION: [
                "space", "form", "layout", "organization", "circulation", "views", "light",
                "composition", "massing", "scale", "proportion", "relationship", "experience"
            ],
            DesignPhase.MATERIALIZATION: [
                "material", "construction", "detail", "system", "structure", "technology",
                "cost", "budget", "timeline", "feasibility", "implementation", "realization"
            ]
        }

    def generate_contextual_question(self, phase: DesignPhase, conversation_history: List[Dict],
                                   recent_response: str, completed_steps: List[SocraticStep]) -> Optional[SocraticQuestion]:
        """Generate a contextual question based on conversation history and current needs"""

        print(f"\n🎨 FLEXIBLE_GENERATOR: Generating contextual question for {phase.value}")
        print(f"   Recent response: {recent_response[:80]}...")
        print(f"   Completed steps: {[step.value for step in completed_steps]}")

        # Analyze recent response for key concepts
        key_concepts = self._extract_key_concepts(recent_response, phase)
        print(f"   Key concepts found: {key_concepts}")

        # Determine question type needed
        question_type = self._determine_question_type(conversation_history, recent_response, completed_steps, phase)
        print(f"   Question type needed: {question_type}")

        # Generate appropriate question
        question_text = self._generate_question_text(phase, question_type, key_concepts, recent_response)

        if question_text:
            question = SocraticQuestion(
                step=SocraticStep.CONTEXTUAL_EXPLORATION,  # Use flexible step
                question_text=question_text,
                keywords=key_concepts,
                assessment_criteria={
                    "completeness": "Addresses the question comprehensively",
                    "depth": "Shows deeper thinking about the topic",
                    "relevance": "Connects to design goals and context",
                    "innovation": "Demonstrates creative problem-solving",
                    "technical_understanding": "Shows appropriate technical awareness"
                },
                phase=phase,
                question_id=f"{phase.value}_contextual_{len(completed_steps)+1:03d}"
            )
            print(f"   ✅ Generated question: {question_text}")
            return question

        print(f"   ❌ Could not generate contextual question")
        return None

    def _extract_key_concepts(self, response: str, phase: DesignPhase) -> List[str]:
        """Extract key concepts from user response relevant to the current phase"""
        response_lower = response.lower()
        phase_keywords = self.phase_keywords.get(phase, [])

        found_concepts = []
        for keyword in phase_keywords:
            if keyword in response_lower:
                found_concepts.append(keyword)

        # Also extract quoted terms and capitalized terms that might be important
        import re
        quoted_terms = re.findall(r'"([^"]*)"', response)
        found_concepts.extend([term.lower() for term in quoted_terms if len(term) > 2])

        return found_concepts[:5]  # Limit to top 5 concepts

    def _determine_question_type(self, conversation_history: List[Dict], recent_response: str,
                               completed_steps: List[SocraticStep], phase: DesignPhase) -> str:
        """Determine what type of question is most needed"""

        response_length = len(recent_response.split())

        # If response is very short, ask for clarification
        if response_length < 20:
            return "clarification"

        # If we haven't done much exploration, focus on that
        if len(completed_steps) < 2:
            return "exploration"

        # If we have good content, focus on synthesis
        if len(completed_steps) >= 3:
            return "synthesis"

        # Default to exploration for middle stages
        return "exploration"

    def _generate_question_text(self, phase: DesignPhase, question_type: str,
                              key_concepts: List[str], recent_response: str) -> Optional[str]:
        """Generate the actual question text"""

        templates = self.question_templates.get(phase, {}).get(question_type, [])
        if not templates:
            return None

        # Select template based on available concepts
        import random
        template = random.choice(templates)

        # Fill in template with concepts from the response
        try:
            if "{topic}" in template and key_concepts:
                template = template.replace("{topic}", key_concepts[0])
            if "{concept}" in template and key_concepts:
                template = template.replace("{concept}", key_concepts[0])
            if "{challenge}" in template:
                template = template.replace("{challenge}", "this design challenge")
            if "{stakeholder}" in template:
                stakeholders = ["users", "community members", "building operators", "visitors"]
                template = template.replace("{stakeholder}", random.choice(stakeholders))
            if "{aspect}" in template and key_concepts:
                template = template.replace("{aspect}", key_concepts[0] if key_concepts else "this aspect")

            # Handle multiple concept placeholders
            if len(key_concepts) >= 2:
                template = template.replace("{idea1}", key_concepts[0])
                template = template.replace("{idea2}", key_concepts[1])

            return template

        except Exception as e:
            print(f"   ⚠️ Template filling error: {e}")
            return templates[0]  # Return basic template if filling fails

class ResponseGradingSystem:
    """Grades user responses to Socratic questions"""
    
    def __init__(self):
        self.architectural_terms = self._initialize_architectural_terms()
        self.creative_indicators = self._initialize_creative_indicators()
    
    def _initialize_architectural_terms(self) -> List[str]:
        """Initialize list of architectural terms for relevance scoring"""
        return [
            "design", "space", "building", "site", "program", "function", "form", "structure",
            "material", "light", "circulation", "context", "precedent", "innovation", "sustainability",
            "community", "urban", "rural", "interior", "exterior", "facade", "plan", "section",
            "elevation", "detail", "construction", "technology", "environment", "climate", "culture"
        ]
    
    def _initialize_creative_indicators(self) -> List[str]:
        """Initialize indicators of creative thinking"""
        return [
            "imagine", "what if", "consider", "explore", "innovative", "creative", "unique",
            "different", "alternative", "possibility", "potential", "transform", "reimagine",
            "reinvent", "challenge", "break", "convention", "unconventional", "experimental"
        ]
    
    def grade_response(self, question: SocraticQuestion, response: str) -> GradingResult:
        """Grade a user response to a Socratic question"""
        
        response_lower = response.lower()
        response_words = len(response.split())
        
        # 1. Completeness Score (0-5)
        completeness = self._calculate_completeness(question.keywords, response_lower)
        
        # 2. Depth Score (0-5)
        depth = self._calculate_depth(response_words, response_lower)
        
        # 3. Relevance Score (0-5)
        relevance = self._calculate_relevance(response_lower)
        
        # 4. Innovation Score (0-5)
        innovation = self._calculate_innovation(response_lower)
        
        # 5. Technical Understanding Score (0-5)
        technical = self._calculate_technical(question.phase, response_lower)
        
        # Overall Score
        overall = (completeness + depth + relevance + innovation + technical) / 5.0
        
        # Generate feedback
        strengths, weaknesses, recommendations = self._generate_feedback(
            completeness, depth, relevance, innovation, technical, question
        )
        
        return GradingResult(
            completeness=completeness,
            depth=depth,
            relevance=relevance,
            innovation=innovation,
            technical_understanding=technical,
            overall_score=overall,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )

    def _calculate_completeness(self, keywords: List[str], response: str) -> float:
        """Calculate completeness based on keyword coverage"""
        keyword_matches = sum(1 for keyword in keywords if keyword in response)
        return min(5.0, (keyword_matches / len(keywords)) * 5.0)

    def _calculate_depth(self, word_count: int, response: str) -> float:
        """Calculate depth based on response length and complexity"""
        # Base score from length (50 words = 3.0 score)
        length_score = min(3.0, (word_count / 50.0) * 3.0)

        # Bonus for complex sentences and reasoning indicators
        reasoning_indicators = ["because", "therefore", "however", "although", "while", "since", "thus"]
        reasoning_bonus = min(2.0, sum(1 for indicator in reasoning_indicators if indicator in response) * 0.5)

        return min(5.0, length_score + reasoning_bonus)

    def _calculate_relevance(self, response: str) -> float:
        """Calculate relevance based on architectural terms"""
        arch_term_matches = sum(1 for term in self.architectural_terms if term in response)
        return min(5.0, (arch_term_matches / len(self.architectural_terms)) * 5.0)

    def _calculate_innovation(self, response: str) -> float:
        """Calculate innovation based on creative indicators"""
        creative_matches = sum(1 for indicator in self.creative_indicators if indicator in response)
        return min(5.0, (creative_matches / len(self.creative_indicators)) * 5.0)

    def _calculate_technical(self, phase: DesignPhase, response: str) -> float:
        """Calculate technical understanding based on phase-appropriate terms"""
        phase_terms = {
            DesignPhase.IDEATION: ["program", "site", "context", "user", "function", "concept"],
            DesignPhase.VISUALIZATION: ["space", "form", "circulation", "light", "scale", "proportion"],
            DesignPhase.MATERIALIZATION: ["material", "structure", "detail", "construction", "cost", "feasibility"]
        }

        relevant_terms = phase_terms.get(phase, [])
        term_matches = sum(1 for term in relevant_terms if term in response)
        return min(5.0, (term_matches / len(relevant_terms)) * 5.0)

    def _generate_feedback(self, completeness: float, depth: float, relevance: float,
                          innovation: float, technical: float, question: SocraticQuestion) -> Tuple[List[str], List[str], List[str]]:
        """Generate feedback based on scores"""
        strengths = []
        weaknesses = []
        recommendations = []

        if completeness >= 4.0:
            strengths.append("Comprehensive response addressing key aspects")
        elif completeness < 2.0:
            weaknesses.append("Response could be more complete")
            recommendations.append("Try to address more aspects of the question")

        if depth >= 4.0:
            strengths.append("Shows deep thinking and reasoning")
        elif depth < 2.0:
            weaknesses.append("Could benefit from more detailed explanation")
            recommendations.append("Elaborate on your reasoning and provide more detail")

        if relevance >= 4.0:
            strengths.append("Highly relevant to architectural design")
        elif relevance < 2.0:
            weaknesses.append("Could be more focused on architectural considerations")
            recommendations.append("Connect your ideas more directly to design principles")

        if innovation >= 3.0:
            strengths.append("Shows creative thinking")
        elif innovation < 2.0:
            recommendations.append("Consider exploring more creative or innovative approaches")

        if technical >= 3.0:
            strengths.append("Demonstrates good technical understanding")
        elif technical < 2.0:
            recommendations.append("Consider the technical aspects more deeply")

        return strengths, weaknesses, recommendations

class PhaseTransitionSystem:
    """Manages transitions between design phases"""

    def __init__(self):
        self.transition_thresholds = {
            DesignPhase.IDEATION: {
                "min_interactions": 3,
                "min_avg_score": 2.5,
                "min_completion": 60.0,
                "required_concepts": ["concept", "program", "site", "community"]
            },
            DesignPhase.VISUALIZATION: {
                "min_interactions": 4,
                "min_avg_score": 3.0,
                "min_completion": 70.0,
                "required_concepts": ["space", "form", "circulation", "experience"]
            },
            DesignPhase.MATERIALIZATION: {
                "min_interactions": 4,
                "min_avg_score": 3.2,
                "min_completion": 75.0,
                "required_concepts": ["material", "construction", "detail", "feasibility"]
            }
        }

    def assess_phase_readiness(self, session: 'SessionState', phase_progress: 'PhaseProgress') -> Dict[str, Any]:
        """Assess if the user is ready to transition to the next phase"""

        current_phase = session.current_phase
        print(f"\n🔄 TRANSITION_ASSESSMENT: Checking readiness for {current_phase.value}")

        # Get transition criteria for current phase
        criteria = self.transition_thresholds.get(current_phase, {})

        # Check interaction count
        interaction_count = len(session.conversation_history)
        min_interactions = criteria.get("min_interactions", 3)
        interactions_met = interaction_count >= min_interactions
        print(f"   📊 Interactions: {interaction_count}/{min_interactions} {'✅' if interactions_met else '❌'}")

        # Check average score
        avg_score = phase_progress.average_score
        min_score = criteria.get("min_avg_score", 2.5)
        score_met = avg_score >= min_score
        print(f"   🎯 Avg Score: {avg_score:.2f}/{min_score} {'✅' if score_met else '❌'}")

        # Check completion percentage
        completion = phase_progress.completion_percent
        min_completion = criteria.get("min_completion", 60.0)
        completion_met = completion >= min_completion
        print(f"   📈 Completion: {completion:.1f}%/{min_completion}% {'✅' if completion_met else '❌'}")

        # Check for required concepts in conversation
        required_concepts = criteria.get("required_concepts", [])
        conversation_text = " ".join([h.get("response", "") for h in session.conversation_history]).lower()
        concepts_found = [concept for concept in required_concepts if concept in conversation_text]
        concepts_met = len(concepts_found) >= len(required_concepts) * 0.6  # 60% of concepts
        print(f"   💡 Concepts: {len(concepts_found)}/{len(required_concepts)} {'✅' if concepts_met else '❌'}")
        print(f"      Found: {concepts_found}")

        # Overall readiness
        criteria_met = [interactions_met, score_met, completion_met, concepts_met]
        readiness_score = sum(criteria_met) / len(criteria_met)
        is_ready = readiness_score >= 0.75  # 75% of criteria must be met

        print(f"   🎯 READINESS: {readiness_score:.1%} {'✅ READY' if is_ready else '❌ NOT READY'}")

        return {
            "is_ready": is_ready,
            "readiness_score": readiness_score,
            "criteria_met": {
                "interactions": interactions_met,
                "score": score_met,
                "completion": completion_met,
                "concepts": concepts_met
            },
            "next_phase": self._get_next_phase(current_phase),
            "transition_message": self._generate_transition_message(current_phase, is_ready, readiness_score)
        }

    def _get_next_phase(self, current_phase: DesignPhase) -> Optional[DesignPhase]:
        """Get the next phase in the sequence"""
        phase_order = [DesignPhase.IDEATION, DesignPhase.VISUALIZATION, DesignPhase.MATERIALIZATION]
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
        except ValueError:
            pass
        return None

    def _generate_transition_message(self, current_phase: DesignPhase, is_ready: bool, readiness_score: float) -> str:
        """Generate a message about phase transition readiness"""

        if is_ready:
            next_phase = self._get_next_phase(current_phase)
            if next_phase:
                phase_descriptions = {
                    DesignPhase.VISUALIZATION: "spatial organization and form development",
                    DesignPhase.MATERIALIZATION: "technical development and implementation planning"
                }
                next_description = phase_descriptions.get(next_phase, "the next phase")

                return f"🎉 Great progress on {current_phase.value}! You seem ready to move into {next_description}. Would you like to transition to the {next_phase.value} phase?"
            else:
                return f"🎉 Excellent work! You've completed the {current_phase.value} phase thoroughly."
        else:
            if readiness_score < 0.5:
                return f"Let's continue developing your {current_phase.value} thinking. I have more questions to help deepen your exploration."
            else:
                return f"You're making good progress on {current_phase.value}. Let's explore a bit more to strengthen your foundation before moving forward."
    
    def _calculate_completeness(self, keywords: List[str], response: str) -> float:
        """Calculate completeness based on keyword coverage"""
        keyword_matches = sum(1 for keyword in keywords if keyword in response)
        return min(5.0, (keyword_matches / len(keywords)) * 5.0)
    
    def _calculate_depth(self, word_count: int, response: str) -> float:
        """Calculate depth based on response length and complexity"""
        # Base score from length (50 words = 3.0 score)
        length_score = min(3.0, (word_count / 50.0) * 3.0)
        
        # Bonus for complex sentences and reasoning indicators
        reasoning_indicators = ["because", "therefore", "however", "although", "while", "since", "thus"]
        reasoning_bonus = min(2.0, sum(1 for indicator in reasoning_indicators if indicator in response) * 0.5)
        
        return min(5.0, length_score + reasoning_bonus)
    
    def _calculate_relevance(self, response: str) -> float:
        """Calculate relevance based on architectural terms"""
        arch_term_matches = sum(1 for term in self.architectural_terms if term in response)
        return min(5.0, (arch_term_matches / len(self.architectural_terms)) * 5.0)
    
    def _calculate_innovation(self, response: str) -> float:
        """Calculate innovation based on creative indicators"""
        creative_matches = sum(1 for indicator in self.creative_indicators if indicator in response)
        return min(5.0, (creative_matches / len(self.creative_indicators)) * 5.0)
    
    def _calculate_technical(self, phase: DesignPhase, response: str) -> float:
        """Calculate technical understanding based on phase-specific knowledge"""
        phase_terms = {
            DesignPhase.IDEATION: ["concept", "context", "program", "site", "community", "precedent"],
            DesignPhase.VISUALIZATION: ["spatial", "circulation", "form", "organization", "hierarchy", "flow"],
            DesignPhase.MATERIALIZATION: ["material", "construction", "technical", "detail", "assembly", "system"]
        }
        
        relevant_terms = phase_terms.get(phase, [])
        if not relevant_terms:
            return 3.0  # Default middle score
        
        term_matches = sum(1 for term in relevant_terms if term in response)
        return min(5.0, (term_matches / len(relevant_terms)) * 5.0)
    
    def _generate_feedback(self, completeness: float, depth: float, relevance: float, 
                          innovation: float, technical: float, question: SocraticQuestion) -> Tuple[List[str], List[str], List[str]]:
        """Generate feedback based on scores"""
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Completeness feedback
        if completeness >= 4.0:
            strengths.append("Comprehensive coverage of the topic")
        elif completeness <= 2.0:
            weaknesses.append("Incomplete coverage of key aspects")
            recommendations.append("Consider addressing all aspects mentioned in the question")
        
        # Depth feedback
        if depth >= 4.0:
            strengths.append("Detailed and thoughtful analysis")
        elif depth <= 2.0:
            weaknesses.append("Superficial analysis")
            recommendations.append("Provide more detailed explanations and reasoning")
        
        # Relevance feedback
        if relevance >= 4.0:
            strengths.append("Strong connection to architectural design")
        elif relevance <= 2.0:
            weaknesses.append("Limited connection to architectural design")
            recommendations.append("Focus more on architectural implications and design decisions")
        
        # Innovation feedback
        if innovation >= 4.0:
            strengths.append("Creative and original thinking")
        elif innovation <= 2.0:
            weaknesses.append("Limited creative thinking")
            recommendations.append("Consider more innovative approaches and unique solutions")
        
        # Technical feedback
        if technical >= 4.0:
            strengths.append("Good technical understanding")
        elif technical <= 2.0:
            weaknesses.append("Limited technical understanding")
            recommendations.append("Strengthen your understanding of architectural principles")
        
        return strengths, weaknesses, recommendations

class PhaseProgressionSystem:
    """Main system for managing phase progression with Socratic dialogue"""
    
    def __init__(self):
        self.question_bank = SocraticQuestionBank()
        self.grading_system = ResponseGradingSystem()
        self.flexible_generator = FlexibleQuestionGenerator()
        self.transition_system = PhaseTransitionSystem()
        self.sessions: Dict[str, SessionState] = {}

        # Phase configuration
        self.phase_weights = {
            DesignPhase.IDEATION: 0.25,
            DesignPhase.VISUALIZATION: 0.35,
            DesignPhase.MATERIALIZATION: 0.40
        }

        self.phase_thresholds = {
            DesignPhase.IDEATION: 3.0,
            DesignPhase.VISUALIZATION: 3.5,
            DesignPhase.MATERIALIZATION: 4.0
        }

        # Debug: Check question bank initialization
        print(f"\n🏦 PHASE_SYSTEM: Question bank initialized")
        for phase in DesignPhase:
            questions = self.question_bank.questions.get(phase, {})
            print(f"   {phase.value}: {len(questions)} questions")
            for step, question in questions.items():
                print(f"      {step.value}: {question.question_text[:50]}...")

        print(f"🎨 Flexible question generator initialized")
        print(f"🔄 Phase transition system initialized")
        # Minimal rubric items (extensible via loader)
        self.phase_checklist_items: Dict[DesignPhase, List[Dict[str, Any]]] = {
            DesignPhase.IDEATION: [
                {"id": "site_context_understood", "keywords": ["site", "context"], "required": True},
                {"id": "program_defined", "keywords": ["program", "requirements"], "required": True}
            ],
            DesignPhase.VISUALIZATION: [
                {"id": "circulation_defined", "keywords": ["circulation", "flow"], "required": True},
                {"id": "form_strategy", "keywords": ["form", "massing"], "required": False}
            ],
            DesignPhase.MATERIALIZATION: [
                {"id": "materials_selected", "keywords": ["material", "materials"], "required": True},
                {"id": "constructability_considered", "keywords": ["construct", "cost"], "required": False}
            ]
        }
    
    def start_session(self, session_id: str) -> SessionState:
        """Start a new session"""
        session = SessionState(session_id=session_id)
        # Initialize Ideation phase with first Socratic step
        session.phase_progress[DesignPhase.IDEATION] = PhaseProgress(
            phase=DesignPhase.IDEATION,
            current_step=SocraticStep.INITIAL_CONTEXT_REASONING
        )
        # Initialize checklist state containers
        session.checklist_state = {p.value: {} for p in DesignPhase}
        self.sessions[session_id] = session
        logger.info(f"Started new session: {session_id}")
        return session
    
    def get_next_question(self, session_id: str) -> Optional[SocraticQuestion]:
        """Get the next question for the current session - now with flexible generation"""
        print(f"\n❓ GET_NEXT_QUESTION: Session {session_id}")

        session = self.sessions.get(session_id)
        if not session:
            print(f"   ❌ Session not found")
            return None

        print(f"   📊 Current phase: {session.current_phase.value}")
        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            print(f"   ❌ No phase progress found")
            return None

        print(f"   🔢 Completed steps: {len(current_phase_progress.completed_steps)}")
        print(f"   📝 Steps: {[step.value for step in current_phase_progress.completed_steps]}")

        # First, try to get a standard question from the question bank
        standard_question = self.question_bank.get_next_question(
            session.current_phase,
            current_phase_progress.completed_steps
        )

        if standard_question:
            print(f"   ✅ Standard question found: {standard_question.question_text[:80]}...")
            return standard_question

        # If no standard questions available, check if we should transition phases
        print(f"   🔄 No standard questions left, checking phase transition...")
        transition_assessment = self.transition_system.assess_phase_readiness(session, current_phase_progress)

        if transition_assessment["is_ready"]:
            print(f"   🎉 Phase transition ready!")
            # Create a transition question
            transition_question = SocraticQuestion(
                step=SocraticStep.READINESS_ASSESSMENT,
                question_text=transition_assessment["transition_message"],
                keywords=["transition", "ready", "next", "phase"],
                assessment_criteria={
                    "completeness": "Confirms readiness for next phase",
                    "depth": "Shows understanding of current phase completion",
                    "relevance": "Acknowledges phase progression",
                    "innovation": "Shows enthusiasm for next challenges",
                    "technical_understanding": "Demonstrates phase comprehension"
                },
                phase=session.current_phase,
                question_id=f"{session.current_phase.value}_transition_{len(current_phase_progress.completed_steps)+1:03d}"
            )
            return transition_question

        # If not ready for transition, generate a flexible contextual question
        print(f"   🎨 Generating flexible contextual question...")
        recent_response = ""
        if session.conversation_history:
            recent_response = session.conversation_history[-1].get("response", "")

        flexible_question = self.flexible_generator.generate_contextual_question(
            session.current_phase,
            session.conversation_history,
            recent_response,
            current_phase_progress.completed_steps
        )

        if flexible_question:
            print(f"   ✅ Flexible question generated: {flexible_question.question_text[:80]}...")
            return flexible_question

        print(f"   ❌ No questions available")
        return None

    def transition_to_next_phase(self, session_id: str) -> Dict[str, Any]:
        """Transition the session to the next phase"""
        print(f"\n🔄 PHASE_TRANSITION: Transitioning session {session_id}")

        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        current_phase = session.current_phase
        next_phase = self.transition_system._get_next_phase(current_phase)

        if not next_phase:
            print(f"   ❌ No next phase available after {current_phase.value}")
            return {"error": "No next phase available"}

        print(f"   🎯 Transitioning from {current_phase.value} to {next_phase.value}")

        # Mark current phase as complete
        current_progress = session.phase_progress.get(current_phase)
        if current_progress:
            current_progress.is_complete = True
            current_progress.completion_percent = 100.0

        # Initialize next phase
        session.current_phase = next_phase
        session.phase_progress[next_phase] = PhaseProgress(
            phase=next_phase,
            current_step=SocraticStep.INITIAL_CONTEXT_REASONING
        )

        # Update session
        session.last_updated = datetime.now()

        print(f"   ✅ Successfully transitioned to {next_phase.value}")

        return {
            "success": True,
            "previous_phase": current_phase.value,
            "new_phase": next_phase.value,
            "message": f"Welcome to the {next_phase.value} phase! Let's begin exploring how to develop your ideas further."
        }

    def process_response(self, session_id: str, response: str) -> Dict[str, Any]:
        """Process a user response and return assessment results"""
        print(f"\n🎯 PHASE PROGRESSION: Processing response for session {session_id}")
        print(f"📝 User response: {response[:100]}...")

        session = self.sessions.get(session_id)
        if not session:
            print(f"❌ PHASE ERROR: Session {session_id} not found")
            return {"error": "Session not found"}

        print(f"📊 Current phase: {session.current_phase.value}")
        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            print(f"❌ PHASE ERROR: No progress found for phase {session.current_phase.value}")
            return {"error": "No current phase progress"}

        print(f"📈 Phase progress before: {current_phase_progress.completion_percent:.1f}%")
        print(f"🔢 Completed steps before: {len(current_phase_progress.completed_steps)}")

        # Get the current question (this should be the question they just answered)
        # We need to reconstruct what question they were answering
        current_question = None

        # Check if this is a response to a transition question
        if "yes" in response.lower() and ("ready" in response.lower() or "next" in response.lower() or "transition" in response.lower()):
            print(f"🔄 Detected transition acceptance response")
            transition_result = self.transition_to_next_phase(session_id)
            if "error" not in transition_result:
                # Return successful transition result
                return {
                    "session_id": session_id,
                    "current_phase": transition_result["new_phase"],
                    "phase_transition": True,
                    "transition_message": transition_result["message"],
                    "grade": {
                        "overall_score": 5.0,  # Perfect score for accepting transition
                        "completeness": 5.0,
                        "depth": 5.0,
                        "relevance": 5.0,
                        "innovation": 5.0,
                        "technical_understanding": 5.0,
                        "strengths": ["Ready for next phase"],
                        "weaknesses": [],
                        "recommendations": ["Continue with new phase exploration"]
                    },
                    "phase_complete": True,
                    "session_complete": self._is_session_complete(self.sessions[session_id]),
                    "nudge": f"Great! Let's begin the {transition_result['new_phase']} phase."
                }

        # Try to get the question they were supposed to answer
        # This is tricky because we need to know what question was asked
        # For now, we'll use the most recent question type based on their progress

        # First try standard questions
        current_question = self.question_bank.get_next_question(
            session.current_phase,
            current_phase_progress.completed_steps
        )

        # If no standard question, create a flexible one for grading purposes
        if not current_question:
            print(f"🎨 Creating flexible question for grading response")
            recent_history_response = ""
            if len(session.conversation_history) > 0:
                recent_history_response = session.conversation_history[-1].get("response", "")

            current_question = self.flexible_generator.generate_contextual_question(
                session.current_phase,
                session.conversation_history,
                recent_history_response,
                current_phase_progress.completed_steps
            )

        if not current_question:
            print(f"❌ PHASE ERROR: No current question found for phase {session.current_phase.value}")
            return {"error": "No current question found"}

        print(f"❓ Current question: {current_question.question_text[:80]}...")
        print(f"🎯 Question step: {current_question.step.value}")

        # Grade the response
        grade = self.grading_system.grade_response(current_question, response)
        print(f"📊 GRADING RESULTS:")
        print(f"   Overall Score: {grade.overall_score:.2f}/5.0")
        print(f"   Completeness: {grade.completeness:.2f}/5.0")
        print(f"   Depth: {grade.depth:.2f}/5.0")
        print(f"   Relevance: {grade.relevance:.2f}/5.0")
        print(f"   Innovation: {grade.innovation:.2f}/5.0")
        print(f"   Technical: {grade.technical_understanding:.2f}/5.0")

        # Update progress
        current_phase_progress.responses[current_question.question_id] = response
        current_phase_progress.grades[current_question.question_id] = grade
        current_phase_progress.completed_steps.append(current_question.step)
        current_phase_progress.last_updated = datetime.now()

        # Recalculate average score
        scores = [g.overall_score for g in current_phase_progress.grades.values()]
        old_avg = current_phase_progress.average_score
        current_phase_progress.average_score = sum(scores) / len(scores) if scores else 0.0
        print(f"📊 Average score: {old_avg:.2f} → {current_phase_progress.average_score:.2f}")

        # Recalculate completion percent for the current phase
        old_percent = current_phase_progress.completion_percent
        current_phase_progress.completion_percent = self._compute_phase_completion_percent(session, current_phase_progress)
        print(f"📈 Completion percent: {old_percent:.1f}% → {current_phase_progress.completion_percent:.1f}%")
        print(f"🔢 Completed steps after: {len(current_phase_progress.completed_steps)}")

        # Check if phase is complete
        was_complete = current_phase_progress.is_complete
        self._check_phase_completion(session, current_phase_progress)
        if current_phase_progress.is_complete and not was_complete:
            print(f"🎉 PHASE COMPLETED: {session.current_phase.value}")

        # Update session
        session.last_updated = datetime.now()
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "phase": session.current_phase.value,
            "step": current_question.step.value,
            "question": current_question.question_text,
            "response": response,
            "grade": grade.overall_score
        })

        print(f"💾 Session updated with {len(session.conversation_history)} total interactions")

        # Generate phase nudge if needed
        nudge = self._generate_phase_nudge(session, current_phase_progress, grade)

        # Get next question or phase transition info
        next_question = self.get_next_question(session_id)
        
        return {
            "session_id": session_id,
            "current_phase": session.current_phase.value,
            "current_step": current_question.step.value,
            "grade": {
                "overall_score": grade.overall_score,
                "completeness": grade.completeness,
                "depth": grade.depth,
                "relevance": grade.relevance,
                "innovation": grade.innovation,
                "technical_understanding": grade.technical_understanding,
                "strengths": grade.strengths,
                "weaknesses": grade.weaknesses,
                "recommendations": grade.recommendations
            },
            "phase_progress": {
                "completed_steps": [step.value for step in current_phase_progress.completed_steps],
                "average_score": current_phase_progress.average_score,
                "is_complete": current_phase_progress.is_complete
            },
            "next_question": next_question.question_text if next_question else None,
            "phase_complete": current_phase_progress.is_complete,
            "session_complete": self._is_session_complete(session),
            "nudge": nudge
        }
    
    def _compute_phase_completion_percent(self, session: SessionState, phase_progress: PhaseProgress) -> float:
        """Compute a stable completion percent (0-100) for the current phase.

        Combines three signals:
        - Socratic steps completion (60%)
        - Required checklist items for the current phase (30%)
        - Score readiness vs. threshold (10%)
        """
        print(f"\n🧮 CALCULATING COMPLETION PERCENT for {session.current_phase.value}:")

        # Steps completion ratio - now more flexible
        # Base completion on minimum 3 interactions, but allow for more
        min_steps = 3
        steps_completed = len(phase_progress.completed_steps)

        # Calculate ratio with diminishing returns after minimum steps
        if steps_completed <= min_steps:
            steps_ratio = steps_completed / min_steps
        else:
            # After minimum steps, each additional step adds less value
            extra_steps = steps_completed - min_steps
            steps_ratio = 1.0 + (extra_steps * 0.1)  # Each extra step adds 10% bonus
            steps_ratio = min(steps_ratio, 1.5)  # Cap at 150%

        steps_ratio = min(steps_ratio, 1.0)  # Cap at 100% for the calculation
        print(f"   📊 Steps: {steps_completed} (min: {min_steps}) = {steps_ratio:.2f} ({steps_ratio*60:.1f}% of total)")

        # Checklist completion ratio for the current phase
        items = self.phase_checklist_items.get(session.current_phase, [])
        required_items = [i for i in items if i.get('required')]
        total_required = len(required_items)
        phase_key = session.current_phase.value
        completed_required = 0
        if total_required > 0:
            for item in required_items:
                item_id = item.get('id')
                if not item_id:
                    continue
                state = session.checklist_state.get(phase_key, {}).get(item_id, {})
                if state.get('status') == 'completed':
                    completed_required += 1
        checklist_ratio = (completed_required / total_required) if total_required > 0 else 0.0
        print(f"   ✅ Checklist: {completed_required}/{total_required} = {checklist_ratio:.2f} ({checklist_ratio*30:.1f}% of total)")

        # Score readiness ratio
        threshold = self.phase_thresholds.get(session.current_phase, 3.0)
        score_ratio = min(phase_progress.average_score / threshold, 1.0) if threshold > 0 else 0.0
        print(f"   🎯 Score: {phase_progress.average_score:.2f}/{threshold:.1f} = {score_ratio:.2f} ({score_ratio*10:.1f}% of total)")

        percent = 100.0 * (0.6 * steps_ratio + 0.3 * checklist_ratio + 0.1 * score_ratio)
        print(f"   🧮 CALCULATION: (60% × {steps_ratio:.2f}) + (30% × {checklist_ratio:.2f}) + (10% × {score_ratio:.2f})")
        print(f"   🧮 CALCULATION: {0.6 * steps_ratio:.2f} + {0.3 * checklist_ratio:.2f} + {0.1 * score_ratio:.2f} = {percent/100:.2f}")

        # Clamp to [0, 100]
        if percent < 0.0:
            percent = 0.0
        elif percent > 100.0:
            percent = 100.0

        print(f"   📈 FINAL COMPLETION: {percent:.1f}%")
        return percent

    def _generate_phase_nudge(self, session: SessionState, phase_progress: PhaseProgress, grade: GradingResult) -> Optional[str]:
        """Generate a nudge to help the user progress in the current phase."""
        current_phase = session.current_phase.value
        completion_percent = phase_progress.completion_percent
        steps_completed = len(phase_progress.completed_steps)
        avg_score = phase_progress.average_score

        print(f"\n🎯 GENERATING PHASE NUDGE:")
        print(f"   Phase: {current_phase}")
        print(f"   Completion: {completion_percent:.1f}%")
        print(f"   Steps: {steps_completed}/4")
        print(f"   Avg Score: {avg_score:.2f}/5.0")

        # No nudge if doing well
        if completion_percent > 75 and avg_score > 3.5:
            print(f"   ✅ No nudge needed - good progress")
            return None

        # Generate nudges based on phase and progress
        nudges = {
            "ideation": [
                "💡 Try exploring different conceptual approaches to your design challenge.",
                "🎯 Consider the core user needs and how your space can address them uniquely.",
                "🌟 What if you approached this problem from a completely different angle?",
                "📝 Break down your design challenge into smaller, manageable components."
            ],
            "visualization": [
                "✏️ Try sketching your ideas to better understand spatial relationships.",
                "📐 Consider how different design elements work together visually.",
                "🎨 Explore how materials and lighting could enhance your concept.",
                "📊 Think about how to communicate your design ideas more clearly."
            ],
            "materialization": [
                "🔧 Consider the practical aspects of implementing your design.",
                "📋 Think about construction methods and material choices.",
                "💰 How would budget and timeline constraints affect your design?",
                "🏗️ What technical challenges need to be addressed in your proposal?"
            ]
        }

        phase_nudges = nudges.get(current_phase, [])
        if not phase_nudges:
            return None

        # Select nudge based on progress level
        if completion_percent < 25:
            nudge_index = 0  # Getting started nudge
        elif completion_percent < 50:
            nudge_index = 1  # Development nudge
        elif completion_percent < 75:
            nudge_index = 2  # Refinement nudge
        else:
            nudge_index = 3  # Completion nudge

        selected_nudge = phase_nudges[min(nudge_index, len(phase_nudges) - 1)]
        print(f"   💬 Selected nudge: {selected_nudge}")

        return selected_nudge

    def _check_phase_completion(self, session: SessionState, phase_progress: PhaseProgress):
        """Check if the current phase is complete"""
        threshold = self.phase_thresholds.get(session.current_phase, 3.0)
        
        # Check if all Socratic steps are completed and average score meets threshold
        all_steps_completed = len(phase_progress.completed_steps) == 4
        score_meets_threshold = phase_progress.average_score >= threshold

        # Add stabilization by requiring high completion percent
        has_sufficient_completion = phase_progress.completion_percent >= 95.0

        if all_steps_completed and score_meets_threshold and has_sufficient_completion:
            phase_progress.is_complete = True
            self._advance_to_next_phase(session)
    
    def _advance_to_next_phase(self, session: SessionState):
        """Advance to the next phase"""
        phase_order = [DesignPhase.IDEATION, DesignPhase.VISUALIZATION, DesignPhase.MATERIALIZATION]
        
        try:
            current_index = phase_order.index(session.current_phase)
            if current_index < len(phase_order) - 1:
                next_phase = phase_order[current_index + 1]
                session.current_phase = next_phase
                session.phase_progress[next_phase] = PhaseProgress(
                    phase=next_phase,
                    current_step=SocraticStep.INITIAL_CONTEXT_REASONING
                )
                logger.info(f"Advanced to phase: {next_phase.value}")
        except ValueError:
            logger.error(f"Invalid phase: {session.current_phase}")
    
    def _is_session_complete(self, session: SessionState) -> bool:
        """Check if the entire session is complete"""
        return all(
            phase_progress.is_complete 
            for phase_progress in session.phase_progress.values()
        )
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of the session"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Calculate overall session score
        all_scores = []
        for phase_progress in session.phase_progress.values():
            all_scores.extend([g.overall_score for g in phase_progress.grades.values()])
        
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Generate phase summaries
        phase_summaries = {}
        for phase, phase_progress in session.phase_progress.items():
            phase_scores = [g.overall_score for g in phase_progress.grades.values()]
            phase_summaries[phase.value] = {
                "completed": phase_progress.is_complete,
                "average_score": sum(phase_scores) / len(phase_scores) if phase_scores else 0.0,
                "completed_steps": len(phase_progress.completed_steps),
                "total_steps": 4,
                "completion_percent": phase_progress.completion_percent
            }
        
        return {
            "session_id": session_id,
            "overall_score": overall_score,
            "session_complete": self._is_session_complete(session),
            "current_phase": session.current_phase.value,
            "phase_summaries": phase_summaries,
            "session_duration": (datetime.now() - session.session_start).total_seconds() / 60,  # minutes
            "total_responses": len(session.conversation_history),
            # Newly added summary fields
            "final_checklist_state": session.checklist_state,
            "phase_progression_timeline": session.timeline
        }

    # New: Update checklist from a raw interaction (user+assistant texts) and return delta
    def update_checklist_from_interaction(self, session_id: str, user_text: str, assistant_text: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            return {"checklist_delta": []}
        current_phase = session.current_phase
        items = self.phase_checklist_items.get(current_phase, [])
        text = f"{user_text}\n{assistant_text}".lower()
        phase_key = current_phase.value
        if phase_key not in session.checklist_state:
            session.checklist_state[phase_key] = {}
        delta = []
        for item in items:
            item_id = item.get("id")
            if not item_id:
                continue
            already = session.checklist_state[phase_key].get(item_id, {}).get('status') == 'completed'
            if already:
                continue
            kws = [kw.lower() for kw in item.get("keywords", [])]
            if any(kw in text for kw in kws):
                state = {
                    'status': 'completed',
                    'first_met_ts': datetime.now().isoformat(),
                    'evidence_interaction_ids': []
                }
                session.checklist_state[phase_key][item_id] = state
                delta.append({'item_id': item_id, 'status': 'completed', 'evidence_interaction_ids': []})
        return {"checklist_delta": delta}

    # New: Compute a periodic snapshot for timeline and export
    def get_snapshot(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            return {}
        # Completion per phase (required items)
        timeline_entry = {
            'ts': datetime.now().isoformat(),
            'current_phase': session.current_phase.value,
        }
        # Include current phase completion percent from engine
        current_progress = session.phase_progress.get(session.current_phase)
        if current_progress:
            timeline_entry['current_phase_completion_percent'] = current_progress.completion_percent
        completed_items = []
        pending_required = []
        for phase, items in self.phase_checklist_items.items():
            phase_key = phase.value
            for item in items:
                item_id = item['id']
                is_completed = session.checklist_state.get(phase_key, {}).get(item_id, {}).get('status') == 'completed'
                if item.get('required', False):
                    if is_completed:
                        completed_items.append(item_id)
                    else:
                        pending_required.append(item_id)
        total_required = len([i for items in self.phase_checklist_items.values() for i in items if i.get('required')])
        completion_pct = int((len(completed_items) / total_required) * 100) if total_required > 0 else 0
        timeline_entry.update({
            'completion_pct': completion_pct,
            'completed_items': completed_items,
            'pending_required': pending_required,
            'evidence_ids': []
        })
        # Append to session timeline
        session.timeline.append(timeline_entry)
        return timeline_entry
    
    def save_session(self, session_id: str, filename: str = None):
        """Save session data to file"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        if not filename:
            filename = f"session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert session to serializable format
        session_data = {
            "session_id": session.session_id,
            "current_phase": session.current_phase.value,
            "overall_score": session.overall_score,
            "session_start": session.session_start.isoformat(),
            "last_updated": session.last_updated.isoformat(),
            "conversation_history": session.conversation_history,
            "user_profile": session.user_profile,
            "phase_progress": {}
        }
        
        for phase, progress in session.phase_progress.items():
            session_data["phase_progress"][phase.value] = {
                "current_step": progress.current_step.value if progress.current_step else None,
                "completed_steps": [step.value for step in progress.completed_steps],
                "responses": progress.responses,
                "grades": {
                    qid: {
                        "overall_score": grade.overall_score,
                        "completeness": grade.completeness,
                        "depth": grade.depth,
                        "relevance": grade.relevance,
                        "innovation": grade.innovation,
                        "technical_understanding": grade.technical_understanding,
                        "strengths": grade.strengths,
                        "weaknesses": grade.weaknesses,
                        "recommendations": grade.recommendations,
                        "timestamp": grade.timestamp.isoformat()
                    }
                    for qid, grade in progress.grades.items()
                },
                "average_score": progress.average_score,
                "completion_percent": progress.completion_percent,
                "is_complete": progress.is_complete,
                "start_time": progress.start_time.isoformat(),
                "last_updated": progress.last_updated.isoformat()
            }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Session saved to: {filename}")
        return {"success": True, "filename": filename}

# Example usage and testing
def main():
    """Example usage of the Phase Progression System"""
    
    # Initialize the system
    system = PhaseProgressionSystem()
    
    # Start a new session
    session_id = "test_session_001"
    session = system.start_session(session_id)
    
    print(f"Started session: {session_id}")
    print(f"Current phase: {session.current_phase.value}")
    
    # Get the first question
    first_question = system.get_next_question(session_id)
    if first_question:
        print(f"\nFirst question: {first_question.question_text}")
    
    # Example responses for testing
    example_responses = [
        "I think we should ask about the community's current needs, what activities they want to support, and how the building can serve as a gathering place. We also need to understand the site's constraints and opportunities.",
        "Some great examples include the Tate Modern in London, which transformed a power station into an art museum, and the High Line in New York, which turned an elevated railway into a public park. These show how industrial spaces can become vibrant community assets.",
        "The industrial character is valuable because it tells the story of the site's history and gives the building authenticity. If we completely transformed it, we'd lose that sense of place and the unique character that makes this location special.",
        "I'm approaching this differently by focusing on adaptive reuse rather than demolition and new construction. I'm thinking about how to preserve the industrial aesthetic while making it welcoming for community use."
    ]
    
    # Process responses
    for i, response in enumerate(example_responses):
        print(f"\n--- Response {i+1} ---")
        print(f"Response: {response[:100]}...")
        
        result = system.process_response(session_id, response)
        
        print(f"Grade: {result['grade']['overall_score']:.2f}/5.0")
        print(f"Strengths: {', '.join(result['grade']['strengths'][:2])}")
        print(f"Current phase: {result['current_phase']}")
        print(f"Phase complete: {result['phase_complete']}")
        
        if result['next_question']:
            print(f"Next question: {result['next_question'][:100]}...")
    
    # Get session summary
    summary = system.get_session_summary(session_id)
    print(f"\n--- Session Summary ---")
    print(f"Overall score: {summary['overall_score']:.2f}/5.0")
    print(f"Session complete: {summary['session_complete']}")
    print(f"Current phase: {summary['current_phase']}")
    
    # Save session
    system.save_session(session_id)

if __name__ == "__main__":
    main()

