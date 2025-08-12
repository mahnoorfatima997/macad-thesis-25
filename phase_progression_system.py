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
        phase_questions = self.questions.get(phase, {})
        
        # Define the order of Socratic steps
        step_order = [
            SocraticStep.INITIAL_CONTEXT_REASONING,
            SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
            SocraticStep.SOCRATIC_QUESTIONING,
            SocraticStep.METACOGNITIVE_PROMPT
        ]
        
        # Find the next uncompleted step
        for step in step_order:
            if step not in completed_steps:
                return phase_questions.get(step)
        
        return None  # All steps completed

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
        """Get the next question for the current session"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            return None
        
        return self.question_bank.get_next_question(
            session.current_phase, 
            current_phase_progress.completed_steps
        )
    
    def process_response(self, session_id: str, response: str) -> Dict[str, Any]:
        """Process a user response and return assessment results"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            return {"error": "No current phase progress"}
        
        # Get the current question
        current_question = self.question_bank.get_next_question(
            session.current_phase, 
            current_phase_progress.completed_steps
        )
        
        if not current_question:
            return {"error": "No current question found"}
        
        # Grade the response
        grade = self.grading_system.grade_response(current_question, response)
        
        # Update progress
        current_phase_progress.responses[current_question.question_id] = response
        current_phase_progress.grades[current_question.question_id] = grade
        current_phase_progress.completed_steps.append(current_question.step)
        current_phase_progress.last_updated = datetime.now()
        
        # Recalculate average score
        scores = [g.overall_score for g in current_phase_progress.grades.values()]
        current_phase_progress.average_score = sum(scores) / len(scores) if scores else 0.0

        # Recalculate completion percent for the current phase
        current_phase_progress.completion_percent = self._compute_phase_completion_percent(session, current_phase_progress)
        
        # Check if phase is complete
        self._check_phase_completion(session, current_phase_progress)
        
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
            "session_complete": self._is_session_complete(session)
        }
    
    def _compute_phase_completion_percent(self, session: SessionState, phase_progress: PhaseProgress) -> float:
        """Compute a stable completion percent (0-100) for the current phase.

        Combines three signals:
        - Socratic steps completion (60%)
        - Required checklist items for the current phase (30%)
        - Score readiness vs. threshold (10%)
        """
        # Steps completion ratio
        total_steps = 4
        steps_completed = len(phase_progress.completed_steps)
        steps_ratio = steps_completed / total_steps if total_steps > 0 else 0.0

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

        # Score readiness ratio
        threshold = self.phase_thresholds.get(session.current_phase, 3.0)
        score_ratio = min(phase_progress.average_score / threshold, 1.0) if threshold > 0 else 0.0

        percent = 100.0 * (0.6 * steps_ratio + 0.3 * checklist_ratio + 0.1 * score_ratio)
        # Clamp to [0, 100]
        if percent < 0.0:
            percent = 0.0
        elif percent > 100.0:
            percent = 100.0
        return percent

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

