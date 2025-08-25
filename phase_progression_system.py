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
import asyncio
import os

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

# REMOVED: QuestionResponsePair - restored to working simple version

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
    """Tracks the overall session state and progression - RESTORED WORKING VERSION"""
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
    """Generates dynamic, contextual Socratic questions for all phases using LLM"""

    def __init__(self):
        # Initialize OpenAI client for question generation
        try:
            from openai import OpenAI
            import os
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.llm_available = True
            print("🤖 LLM-powered question generation initialized")
        except Exception as e:
            print(f"⚠️ LLM not available for question generation: {e}")
            self.client = None
            self.llm_available = False
    
    def generate_contextual_question(self, phase: DesignPhase, step: SocraticStep,
                                   user_context: str = "", project_context: str = "") -> SocraticQuestion:
        """Generate a contextual Socratic question using LLM based on phase, step, and user context"""

        if not self.llm_available:
            return self._get_fallback_question(phase, step)

        try:
            # Define phase-specific themes and objectives
            phase_themes = {
                DesignPhase.IDEATION: {
                    "focus": "conceptual thinking, problem definition, and creative exploration",
                    "objectives": "understanding context, identifying opportunities, exploring possibilities"
                },
                DesignPhase.VISUALIZATION: {
                    "focus": "spatial organization, form development, and design synthesis",
                    "objectives": "organizing space, developing form, integrating systems"
                },
                DesignPhase.MATERIALIZATION: {
                    "focus": "technical development, material selection, and implementation",
                    "objectives": "resolving details, selecting materials, ensuring constructability"
                }
            }

            # Define step-specific approaches
            step_approaches = {
                SocraticStep.INITIAL_CONTEXT_REASONING: "Ask about foundational understanding and context analysis",
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: "Prompt for precedent knowledge and synthesis of examples",
                SocraticStep.SOCRATIC_QUESTIONING: "Challenge assumptions and deepen critical thinking",
                SocraticStep.METACOGNITIVE_PROMPT: "Encourage reflection on design process and decision-making"
            }

            # Create the prompt for LLM question generation
            theme = phase_themes.get(phase, {})
            approach = step_approaches.get(step, "Ask a thoughtful question")

            prompt = f"""You are an expert architecture educator using the Socratic method. Generate a single, thoughtful question for a student working on an architectural design project.

CONTEXT:
- Design Phase: {phase.value} (Focus: {theme.get('focus', 'architectural design')})
- Socratic Step: {step.value} ({approach})
- Phase Objectives: {theme.get('objectives', 'design development')}
- User Context: {user_context if user_context else 'General architectural design project'}
- Project Context: {project_context if project_context else 'Community-focused architectural project'}

REQUIREMENTS:
1. Generate ONE specific, engaging question that fits the phase and step
2. Make it contextual to the user's situation and project
3. Encourage deep thinking and reflection
4. Avoid generic or overly broad questions
5. Make it appropriate for architecture students
6. Keep it concise but thought-provoking

Generate only the question text, no additional explanation."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert architecture educator specializing in Socratic questioning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

            question_text = response.choices[0].message.content.strip()

            # Generate assessment criteria based on the phase and step
            criteria_prompt = f"""Based on this Socratic question for {phase.value} phase, {step.value} step:
"{question_text}"

Generate 5 assessment criteria as a JSON object with keys: completeness, depth, relevance, innovation, technical_understanding. Each value should be a brief description of what constitutes a good response for that criterion."""

            criteria_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in architectural education assessment."},
                    {"role": "user", "content": criteria_prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            try:
                import json
                criteria_text = criteria_response.choices[0].message.content.strip()
                # Extract JSON from response if it's wrapped in markdown
                if "```json" in criteria_text:
                    criteria_text = criteria_text.split("```json")[1].split("```")[0].strip()
                elif "```" in criteria_text:
                    criteria_text = criteria_text.split("```")[1].strip()

                assessment_criteria = json.loads(criteria_text)
            except:
                # Fallback criteria if JSON parsing fails
                assessment_criteria = {
                    "completeness": f"Addresses key aspects of {phase.value} phase thinking",
                    "depth": "Shows thoughtful analysis and reasoning",
                    "relevance": "Connects to architectural design principles",
                    "innovation": "Demonstrates creative thinking",
                    "technical_understanding": f"Shows understanding of {phase.value} phase concepts"
                }

            # Extract keywords from the question for assessment
            keywords = self._extract_keywords(question_text, phase, step)

            # Create and return the dynamic question
            return SocraticQuestion(
                step=step,
                question_text=question_text,
                keywords=keywords,
                assessment_criteria=assessment_criteria,
                phase=phase,
                question_id=f"{phase.value}_{step.value}_{hash(question_text) % 1000:03d}"
            )

        except Exception as e:
            print(f"⚠️ LLM question generation failed: {e}")
            return self._get_fallback_question(phase, step)

    def _extract_keywords(self, question_text: str, phase: DesignPhase, step: SocraticStep) -> List[str]:
        """Extract relevant keywords from the generated question"""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', question_text.lower())

        # Add phase and step specific keywords
        phase_keywords = {
            DesignPhase.IDEATION: ["concept", "idea", "context", "community", "needs"],
            DesignPhase.VISUALIZATION: ["spatial", "form", "organization", "design", "visual"],
            DesignPhase.MATERIALIZATION: ["material", "construction", "technical", "detail", "implementation"]
        }

        keywords = list(set(words[:5] + phase_keywords.get(phase, [])))
        return keywords[:8]  # Limit to 8 keywords

    def _get_fallback_question(self, phase: DesignPhase, step: SocraticStep) -> SocraticQuestion:
        """Provide simple fallback questions when LLM is not available"""

        fallback_questions = {
            (DesignPhase.IDEATION, SocraticStep.INITIAL_CONTEXT_REASONING):
                "What are the most important aspects to consider for this design project?",
            (DesignPhase.IDEATION, SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER):
                "What examples or precedents might inform your approach?",
            (DesignPhase.IDEATION, SocraticStep.SOCRATIC_QUESTIONING):
                "What assumptions are you making about this project?",
            (DesignPhase.IDEATION, SocraticStep.METACOGNITIVE_PROMPT):
                "How are you approaching this design challenge?",

            (DesignPhase.VISUALIZATION, SocraticStep.INITIAL_CONTEXT_REASONING):
                "How does your spatial organization respond to the project requirements?",
            (DesignPhase.VISUALIZATION, SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER):
                "What precedents inform your spatial approach?",
            (DesignPhase.VISUALIZATION, SocraticStep.SOCRATIC_QUESTIONING):
                "How does your design balance different functional needs?",
            (DesignPhase.VISUALIZATION, SocraticStep.METACOGNITIVE_PROMPT):
                "What design decisions are you most confident about?",

            (DesignPhase.MATERIALIZATION, SocraticStep.INITIAL_CONTEXT_REASONING):
                "How do your material choices respond to the project context?",
            (DesignPhase.MATERIALIZATION, SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER):
                "What construction precedents inform your technical approach?",
            (DesignPhase.MATERIALIZATION, SocraticStep.SOCRATIC_QUESTIONING):
                "How does your technical approach balance different constraints?",
            (DesignPhase.MATERIALIZATION, SocraticStep.METACOGNITIVE_PROMPT):
                "What aspects of your design would you prioritize under constraints?"
        }

        question_text = fallback_questions.get((phase, step), "What are your thoughts on this aspect of the design?")

        return SocraticQuestion(
            step=step,
            question_text=question_text,
            keywords=["design", "architecture", "thinking"],
            assessment_criteria={
                "completeness": f"Addresses key aspects of {phase.value} phase",
                "depth": "Shows thoughtful analysis",
                "relevance": "Connects to architectural principles",
                "innovation": "Demonstrates creative thinking",
                "technical_understanding": f"Shows understanding of {phase.value} concepts"
            },
            phase=phase,
            question_id=f"fallback_{phase.value}_{step.value}"
        )

    def get_question(self, phase: DesignPhase, step: SocraticStep,
                    user_context: str = "", project_context: str = "") -> Optional[SocraticQuestion]:
        """Get a contextual Socratic question using LLM generation"""
        return self.generate_contextual_question(phase, step, user_context, project_context)

    def get_next_question(self, phase: DesignPhase, completed_steps: List[SocraticStep],
                         user_context: str = "", project_context: str = "") -> Optional[SocraticQuestion]:
        """Get the next question in the Socratic sequence using dynamic generation"""
        print(f"\n🏦 QUESTION_BANK: Getting next question for {phase.value}")

        # Define the order of Socratic steps
        step_order = [
            SocraticStep.INITIAL_CONTEXT_REASONING,
            SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER,
            SocraticStep.SOCRATIC_QUESTIONING,
            SocraticStep.METACOGNITIVE_PROMPT
        ]

        print(f"   ✅ Completed steps: {[step.value for step in completed_steps]}")

        # Find the next step that hasn't been completed
        for step in step_order:
            if step not in completed_steps:
                print(f"   🎯 Next step: {step.value}")
                return self.generate_contextual_question(phase, step, user_context, project_context)

        print("   🏁 All steps completed for this phase")
        return None

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
                ],
                "synthesis": [
                    "How do your material choices work together to create a cohesive design language?",
                    "What connections do you see between your technical decisions and your design concept?",
                    "How does your construction approach support the overall project goals?",
                    "What relationships exist between your material palette and the building's performance?",
                    "How do the technical systems integrate with your architectural vision?",
                    "What story does your material strategy tell about the project's values?"
                ],
                "exploration": [
                    "What other material approaches might achieve similar results?",
                    "How might different construction methods change your design?",
                    "What technical innovations could enhance your concept?",
                    "How do environmental factors influence your material decisions?",
                    "What construction details deserve more exploration?",
                    "How might you test or validate your technical assumptions?"
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

        # ENHANCED: Always generate a question - never return None
        if not question_text:
            # If all else fails, use guaranteed fallback questions
            fallback_questions = {
                DesignPhase.IDEATION: [
                    "What new aspects of your design concept are you considering?",
                    "How might you refine your initial ideas further?",
                    "What questions about your project remain unanswered?",
                    "How do you see your concept evolving?"
                ],
                DesignPhase.VISUALIZATION: [
                    "What spatial relationships in your design could be explored more deeply?",
                    "How might you develop your design's formal qualities?",
                    "What aspects of the user experience need more attention?",
                    "How could your design better respond to its context?"
                ],
                DesignPhase.MATERIALIZATION: [
                    "What technical aspects of your design deserve more exploration?",
                    "How might you refine your material strategy?",
                    "What construction challenges need more consideration?",
                    "How could you optimize your design for better performance?"
                ]
            }

            import random
            phase_questions = fallback_questions.get(phase, ["What would you like to explore next in your design?"])
            question_text = random.choice(phase_questions)
            print(f"   🔄 Using guaranteed fallback: {question_text}")

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
            print(f"   ⚠️ No templates found for {phase.value} - {question_type}, trying AI generation")
            return self._generate_ai_question(phase, question_type, key_concepts, recent_response)

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

    def _generate_ai_question(self, phase: DesignPhase, question_type: str,
                            key_concepts: List[str], recent_response: str) -> Optional[str]:
        """Generate a question using AI when templates fail or are unavailable"""
        try:
            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Create context for AI generation
            concepts_text = ", ".join(key_concepts) if key_concepts else "general design concepts"
            response_preview = recent_response[:200] if recent_response else "No recent response"

            prompt = f"""You are an expert architectural mentor. Generate a thoughtful, engaging Socratic question for a student in the {phase.value} phase of design.

Context:
- Current phase: {phase.value}
- Question type needed: {question_type}
- Key concepts from student's recent work: {concepts_text}
- Student's recent response: "{response_preview}"

Requirements:
1. Ask a question that encourages deeper thinking about {phase.value} phase concepts
2. Build on the student's recent work and concepts they've mentioned
3. Use a {question_type} approach (exploratory, synthesis, technical, etc.)
4. Keep it conversational and engaging, not academic or dry
5. Focus on architectural design thinking appropriate for {phase.value}
6. Make it specific enough to be actionable but open enough to encourage creativity

Generate only the question, no explanations or formatting."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            ai_question = response.choices[0].message.content.strip()
            print(f"   🤖 AI generated question: {ai_question}")
            return ai_question

        except Exception as e:
            print(f"   ❌ AI question generation failed: {e}")
            # Ultimate fallback - simple but functional questions
            fallback_questions = {
                DesignPhase.IDEATION: "What aspects of your design concept would you like to explore further?",
                DesignPhase.VISUALIZATION: "How might you develop your spatial ideas in more detail?",
                DesignPhase.MATERIALIZATION: "What technical aspects of your design need more consideration?"
            }
            fallback = fallback_questions.get(phase, "What would you like to explore next in your design?")
            print(f"   🔄 Using fallback question: {fallback}")
            return fallback

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
        """Calculate completeness based on keyword coverage - ENHANCED: More generous scoring"""
        if not keywords:
            return 4.0  # Default good score if no keywords specified

        keyword_matches = sum(1 for keyword in keywords if keyword in response)
        base_score = (keyword_matches / len(keywords)) * 5.0

        # Bonus for detailed responses (length indicates thoroughness)
        word_count = len(response.split())
        if word_count > 100:  # Detailed response
            base_score += 1.0
        elif word_count > 50:  # Moderate response
            base_score += 0.5

        return min(5.0, base_score)

    def _calculate_depth(self, word_count: int, response: str) -> float:
        """Calculate depth based on response length and complexity - ENHANCED: More generous scoring"""
        # More generous base score from length (30 words = 3.0 score instead of 50)
        length_score = min(4.0, (word_count / 30.0) * 3.0)

        # Bonus for complex sentences and reasoning indicators
        reasoning_indicators = ["because", "therefore", "however", "although", "while", "since", "thus", "when", "if", "unless", "whereas"]
        reasoning_bonus = min(1.5, sum(1 for indicator in reasoning_indicators if indicator in response) * 0.3)

        # Additional bonus for detailed architectural thinking
        detail_indicators = ["consider", "approach", "strategy", "design", "space", "relationship", "connection", "experience"]
        detail_bonus = min(1.0, sum(1 for indicator in detail_indicators if indicator in response) * 0.2)

        total_score = length_score + reasoning_bonus + detail_bonus
        return min(5.0, max(2.0, total_score))  # Minimum score of 2.0 for any substantive response

    def _calculate_relevance(self, response: str) -> float:
        """Calculate relevance based on architectural terms - ENHANCED: More generous scoring"""
        arch_term_matches = sum(1 for term in self.architectural_terms if term in response)
        base_score = (arch_term_matches / len(self.architectural_terms)) * 5.0

        # More generous baseline - if response shows architectural thinking, give credit
        word_count = len(response.split())
        if word_count > 20 and any(term in response.lower() for term in ["design", "space", "building", "architecture", "project"]):
            base_score = max(base_score, 2.5)  # Minimum 2.5 for architectural responses

        # Bonus for detailed architectural discussion
        if word_count > 100:
            base_score += 1.0
        elif word_count > 50:
            base_score += 0.5

        return min(5.0, base_score)

    def _calculate_innovation(self, response: str) -> float:
        """Calculate innovation based on creative indicators - ENHANCED: More generous scoring"""
        creative_matches = sum(1 for indicator in self.creative_indicators if indicator in response)
        base_score = (creative_matches / len(self.creative_indicators)) * 5.0

        # Look for innovative thinking patterns
        innovation_patterns = ["unique", "different", "creative", "novel", "innovative", "original", "alternative", "new approach", "reimagine", "transform"]
        pattern_matches = sum(1 for pattern in innovation_patterns if pattern in response.lower())

        # Bonus for showing creative thinking
        if pattern_matches > 0:
            base_score += 1.5

        # Bonus for detailed exploration of ideas
        word_count = len(response.split())
        if word_count > 80:  # Detailed creative exploration
            base_score += 1.0
        elif word_count > 40:
            base_score += 0.5

        # Minimum score for any thoughtful response
        if word_count > 20:
            base_score = max(base_score, 2.0)

        return min(5.0, base_score)

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
        # OPTIMIZED THRESHOLDS FOR BETTER IMAGE GENERATION TRIGGERING
        self.transition_thresholds = {
            DesignPhase.IDEATION: {
                "min_interactions": 2,  # Reduced from 3 to 2
                "min_avg_score": 0.8,   # Reduced from 2.5 to 0.8 (more realistic)
                "min_completion": 40.0, # Reduced from 60.0 to 40.0
                "required_concepts": ["concept", "program", "site", "community"]
            },
            DesignPhase.VISUALIZATION: {
                "min_interactions": 3,  # Reduced from 4 to 3
                "min_avg_score": 1.0,   # Reduced from 3.0 to 1.0
                "min_completion": 45.0, # Reduced from 70.0 to 45.0
                "required_concepts": ["space", "form", "circulation", "experience"]
            },
            DesignPhase.MATERIALIZATION: {
                "min_interactions": 3,  # Reduced from 4 to 3
                "min_avg_score": 1.2,   # Reduced from 3.2 to 1.2
                "min_completion": 50.0, # Reduced from 75.0 to 50.0
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

        # ENHANCED: More adaptive and rational readiness assessment
        # Weight criteria differently - engagement and concepts matter more than rigid scores
        engagement_score = min(interaction_count / min_interactions, 2.0)  # Can exceed 1.0 for high engagement
        concept_coverage = len(concepts_found) / max(len(required_concepts), 1)

        # Adaptive scoring - if user is highly engaged, be more lenient on scores
        if engagement_score >= 1.5:  # High engagement
            effective_score_threshold = min_score * 0.8  # Reduce score requirement by 20%
            score_met = avg_score >= effective_score_threshold
            print(f"   🎯 Adaptive Score: {avg_score:.2f}/{effective_score_threshold:.2f} (reduced for high engagement) {'✅' if score_met else '❌'}")

        # Adaptive completion - if concepts are well covered, be more lenient on completion
        if concept_coverage >= 0.8:  # Good concept coverage
            effective_completion_threshold = min_completion * 0.8  # Reduce completion requirement
            completion_met = completion >= effective_completion_threshold
            print(f"   📈 Adaptive Completion: {completion:.1f}%/{effective_completion_threshold:.1f}% (reduced for good concepts) {'✅' if completion_met else '❌'}")

        # Smart readiness calculation - prioritize engagement and learning over rigid metrics
        readiness_factors = []

        # Core engagement (must have meaningful interaction)
        if interactions_met:
            readiness_factors.append(1.0)
        else:
            readiness_factors.append(0.0)

        # Learning evidence (either good scores OR good concept coverage)
        if score_met or concept_coverage >= 0.5:
            readiness_factors.append(1.0)
        else:
            readiness_factors.append(0.5)  # Partial credit for some learning

        # Progress evidence (either completion OR sustained engagement)
        if completion_met or engagement_score >= 1.5:
            readiness_factors.append(1.0)
        else:
            readiness_factors.append(0.3)  # Some credit for effort

        # Concept understanding (flexible threshold)
        if concepts_met or concept_coverage >= 0.4:
            readiness_factors.append(1.0)
        else:
            readiness_factors.append(0.2)  # Some credit for partial understanding

        readiness_score = sum(readiness_factors) / len(readiness_factors)

        # More lenient transition threshold - 60% instead of 75%
        is_ready = readiness_score >= 0.6

        print(f"   🎯 ADAPTIVE READINESS: {readiness_score:.1%} {'✅ READY' if is_ready else '❌ NOT READY'}")
        print(f"      Engagement factor: {engagement_score:.1f}x")
        print(f"      Concept coverage: {concept_coverage:.1%}")

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

                return f"🎉 Excellent work on {current_phase.value}! You've demonstrated strong understanding and are ready to advance. Let's now move into {next_description} in the {next_phase.value} phase."
            else:
                # This is the final phase - provide a comprehensive completion message
                if current_phase == DesignPhase.MATERIALIZATION:
                    return f"🎉 Congratulations! You've successfully completed all three phases of the design process - ideation, visualization, and materialization. You've demonstrated comprehensive architectural thinking from initial concept through technical implementation. Your design journey shows strong development of critical thinking, creative problem-solving, and technical understanding."
                else:
                    return f"🎉 Excellent work! You've completed the {current_phase.value} phase thoroughly."
        else:
            if readiness_score < 0.5:
                return f"Let's continue developing your {current_phase.value} thinking. I have more questions to help deepen your exploration."
            else:
                return f"You're making good progress on {current_phase.value}. Let's explore a bit more to strengthen your foundation before moving forward."
    
    def _calculate_completeness(self, keywords: List[str], response: str) -> float:
        """Calculate completeness based on keyword coverage - ENHANCED: More generous scoring"""
        if not keywords:
            return 4.0  # Default good score if no keywords specified

        keyword_matches = sum(1 for keyword in keywords if keyword in response)
        base_score = (keyword_matches / len(keywords)) * 5.0

        # Bonus for detailed responses (length indicates thoroughness)
        word_count = len(response.split())
        if word_count > 100:  # Detailed response
            base_score += 1.0
        elif word_count > 50:  # Moderate response
            base_score += 0.5

        return min(5.0, base_score)

    def _calculate_depth(self, word_count: int, response: str) -> float:
        """Calculate depth based on response length and complexity - ENHANCED: More generous scoring"""
        # More generous base score from length (30 words = 3.0 score instead of 50)
        length_score = min(4.0, (word_count / 30.0) * 3.0)

        # Bonus for complex sentences and reasoning indicators
        reasoning_indicators = ["because", "therefore", "however", "although", "while", "since", "thus", "when", "if", "unless", "whereas"]
        reasoning_bonus = min(1.5, sum(1 for indicator in reasoning_indicators if indicator in response) * 0.3)

        # Additional bonus for detailed architectural thinking
        detail_indicators = ["consider", "approach", "strategy", "design", "space", "relationship", "connection", "experience"]
        detail_bonus = min(1.0, sum(1 for indicator in detail_indicators if indicator in response) * 0.2)

        total_score = length_score + reasoning_bonus + detail_bonus
        return min(5.0, max(2.0, total_score))  # Minimum score of 2.0 for any substantive response

    def _calculate_relevance(self, response: str) -> float:
        """Calculate relevance based on architectural terms - ENHANCED: More generous scoring"""
        arch_term_matches = sum(1 for term in self.architectural_terms if term in response)
        base_score = (arch_term_matches / len(self.architectural_terms)) * 5.0

        # More generous baseline - if response shows architectural thinking, give credit
        word_count = len(response.split())
        if word_count > 20 and any(term in response.lower() for term in ["design", "space", "building", "architecture", "project"]):
            base_score = max(base_score, 2.5)  # Minimum 2.5 for architectural responses

        # Bonus for detailed architectural discussion
        if word_count > 100:
            base_score += 1.0
        elif word_count > 50:
            base_score += 0.5

        return min(5.0, base_score)

    def _calculate_innovation(self, response: str) -> float:
        """Calculate innovation based on creative indicators - ENHANCED: More generous scoring"""
        creative_matches = sum(1 for indicator in self.creative_indicators if indicator in response)
        base_score = (creative_matches / len(self.creative_indicators)) * 5.0

        # Look for innovative thinking patterns
        innovation_patterns = ["unique", "different", "creative", "novel", "innovative", "original", "alternative", "new approach", "reimagine", "transform"]
        pattern_matches = sum(1 for pattern in innovation_patterns if pattern in response.lower())

        # Bonus for showing creative thinking
        if pattern_matches > 0:
            base_score += 1.5

        # Bonus for detailed exploration of ideas
        word_count = len(response.split())
        if word_count > 80:  # Detailed creative exploration
            base_score += 1.0
        elif word_count > 40:
            base_score += 0.5

        # Minimum score for any thoughtful response
        if word_count > 20:
            base_score = max(base_score, 2.0)

        return min(5.0, base_score)
    
    def _calculate_technical(self, phase: DesignPhase, response: str) -> float:
        """Calculate technical understanding based on phase-specific knowledge - ENHANCED: More generous scoring"""
        phase_terms = {
            DesignPhase.IDEATION: ["concept", "context", "program", "site", "community", "precedent", "user", "function", "needs", "goals", "vision"],
            DesignPhase.VISUALIZATION: ["spatial", "circulation", "form", "organization", "hierarchy", "flow", "layout", "space", "relationship", "connection"],
            DesignPhase.MATERIALIZATION: ["material", "construction", "technical", "detail", "assembly", "system", "structure", "building", "implementation"]
        }

        relevant_terms = phase_terms.get(phase, [])
        if not relevant_terms:
            return 3.5  # More generous default score

        term_matches = sum(1 for term in relevant_terms if term in response.lower())
        base_score = (term_matches / len(relevant_terms)) * 5.0

        # Bonus for showing phase-appropriate thinking even without exact terms
        word_count = len(response.split())
        if word_count > 50:  # Detailed technical discussion
            base_score += 1.0
        elif word_count > 25:
            base_score += 0.5

        # Minimum score for substantive responses
        if word_count > 15:
            base_score = max(base_score, 2.5)

        return min(5.0, base_score)
    
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

        # Initialize image generation components
        try:
            import sys
            import os
            # Add the thesis-agents directory to the path
            thesis_agents_path = os.path.join(os.path.dirname(__file__), 'thesis-agents')
            if thesis_agents_path not in sys.path:
                sys.path.insert(0, thesis_agents_path)

            from vision.image_generator import ReplicateImageGenerator, DesignPromptGenerator
            self.image_generator = ReplicateImageGenerator()
            self.prompt_generator = DesignPromptGenerator()
            self.image_generation_enabled = True
            print("🎨 Image generation system initialized")
        except ImportError as e:
            print(f"⚠️ Image generation not available: {e}")
            self.image_generator = None
            self.prompt_generator = None
            self.image_generation_enabled = False

        # Phase configuration
        self.phase_weights = {
            DesignPhase.IDEATION: 0.25,
            DesignPhase.VISUALIZATION: 0.35,
            DesignPhase.MATERIALIZATION: 0.40
        }

        self.phase_thresholds = {
            DesignPhase.IDEATION: 2.5,  # Reduced from 3.0 to be more achievable
            DesignPhase.VISUALIZATION: 2.8,  # Reduced from 3.5
            DesignPhase.MATERIALIZATION: 3.2  # Reduced from 4.0
        }

        # Debug: Check question bank initialization
        print(f"\n🏦 PHASE_SYSTEM: Dynamic question bank initialized")
        if self.question_bank.llm_available:
            print(f"   🤖 LLM-powered question generation enabled")
        else:
            print(f"   📝 Using fallback question generation")

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
                {"id": "materials_selected", "keywords": ["material", "materials", "concrete", "steel", "wood", "brick", "glass", "stone", "timber", "metal", "fabric", "finish", "finishes"], "required": True},
                {"id": "constructability_considered", "keywords": ["construct", "construction", "build", "building", "cost", "budget", "feasible", "structural", "technical"], "required": False}
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
            print(f"   ❌ No phase progress found for {session.current_phase.value}")
            # ENHANCED: Initialize phase progress if missing
            print(f"   🔧 Initializing missing phase progress for {session.current_phase.value}")
            current_phase_progress = PhaseProgress(
                phase=session.current_phase,
                current_step=SocraticStep.INITIAL_CONTEXT_REASONING
            )
            session.phase_progress[session.current_phase] = current_phase_progress

        print(f"   🔢 Completed steps: {len(current_phase_progress.completed_steps)}")
        print(f"   📝 Steps: {[step.value for step in current_phase_progress.completed_steps]}")

        # ENHANCED: Verify we're asking questions for the correct phase
        print(f"   🔍 PHASE VERIFICATION:")
        print(f"      Session current phase: {session.current_phase.value}")
        print(f"      Progress phase: {current_phase_progress.phase.value}")
        print(f"      Phase match: {session.current_phase == current_phase_progress.phase}")

        # First, try to get a contextual question from the dynamic question bank
        user_context = ""  # No user input context available in this method
        project_context = session.project_description if hasattr(session, 'project_description') else ""

        standard_question = self.question_bank.get_next_question(
            session.current_phase,
            current_phase_progress.completed_steps,
            user_context,
            project_context
        )

        if standard_question:
            print(f"   ✅ Standard question found for {standard_question.phase.value}: {standard_question.question_text[:80]}...")
            # ENHANCED: Double-check the question phase matches current phase
            if standard_question.phase != session.current_phase:
                print(f"   ⚠️ WARNING: Question phase ({standard_question.phase.value}) doesn't match session phase ({session.current_phase.value})")
                print(f"   🔧 Correcting question phase to match session phase")
                # Create a corrected question with the right phase
                corrected_question = SocraticQuestion(
                    step=standard_question.step,
                    question_text=standard_question.question_text,
                    keywords=standard_question.keywords,
                    assessment_criteria=standard_question.assessment_criteria,
                    phase=session.current_phase,  # Use session's current phase
                    question_id=f"{session.current_phase.value}_{standard_question.step.value}_corrected"
                )
                return corrected_question
            return standard_question

        # If no standard questions available, check if we should transition phases
        print(f"   🔄 No standard questions left, checking phase transition...")
        transition_assessment = self.transition_system.assess_phase_readiness(session, current_phase_progress)

        if transition_assessment["is_ready"]:
            # Check if there's a next phase to transition to
            next_phase = transition_assessment.get("next_phase")
            if next_phase:
                print(f"   🎉 Phase transition ready! Automatically transitioning...")
                # ENHANCED: Automatically transition instead of asking for permission
                transition_result = self.transition_to_next_phase(session_id)
                if "error" not in transition_result:
                    print(f"   ✅ Transitioned to {transition_result['new_phase']} phase")
                    # Get the updated session after transition
                    updated_session = self.sessions.get(session_id)
                    if updated_session:
                        # Get the first question for the new phase
                        new_phase_progress = updated_session.phase_progress.get(updated_session.current_phase)
                        if new_phase_progress:
                            first_question = self.question_bank.get_next_question(
                                updated_session.current_phase,
                                new_phase_progress.completed_steps,
                                user_context,
                                project_context
                            )
                            if first_question:
                                # Modify the question text to include transition announcement
                                welcome_message = transition_result["message"]
                                combined_text = f"{welcome_message}\n\n{first_question.question_text}"
                                first_question.question_text = combined_text
                                return first_question
                    # Fallback if we can't get the first question
                    print(f"   ⚠️ Could not get first question for new phase")
                else:
                    print(f"   ❌ Transition failed: {transition_result['error']}")
                    # Fall through to flexible question generation
            else:
                # Final phase completed - generate celebration question for continued exploration
                print(f"   🎉 Final phase completed! Generating celebration question...")
                completion_message = transition_assessment["transition_message"]
                celebration_question = SocraticQuestion(
                    step=SocraticStep.CONTEXTUAL_EXPLORATION,
                    question_text=f"{completion_message}\n\nAs you reflect on your complete design journey, what aspects of your project do you feel most proud of, and what would you explore further if you had more time?",
                    keywords=["reflection", "completion", "design", "journey"],
                    assessment_criteria={
                        "completeness": "Reflects comprehensively on the design process",
                        "depth": "Shows deep understanding of design development",
                        "relevance": "Connects to overall design goals and learning",
                        "innovation": "Demonstrates creative insights from the process",
                        "technical_understanding": "Shows integrated understanding across all phases"
                    },
                    phase=session.current_phase,
                    question_id=f"{session.current_phase.value}_completion_celebration"
                )
                return celebration_question

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
            print(f"   ✅ Flexible question generated for {flexible_question.phase.value}: {flexible_question.question_text[:80]}...")
            # ENHANCED: Ensure flexible question has correct phase
            if flexible_question.phase != session.current_phase:
                print(f"   🔧 Correcting flexible question phase from {flexible_question.phase.value} to {session.current_phase.value}")
                flexible_question.phase = session.current_phase
                flexible_question.question_id = f"{session.current_phase.value}_flexible_{len(current_phase_progress.completed_steps)+1:03d}"
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
        new_phase_progress = PhaseProgress(
            phase=next_phase,
            current_step=SocraticStep.INITIAL_CONTEXT_REASONING
        )
        session.phase_progress[next_phase] = new_phase_progress

        # Update session
        session.last_updated = datetime.now()

        print(f"   ✅ Successfully transitioned to {next_phase.value}")
        print(f"   🔍 New phase initialized:")
        print(f"      - Phase: {new_phase_progress.phase.value}")
        print(f"      - Is complete: {new_phase_progress.is_complete}")
        print(f"      - Completed steps: {len(new_phase_progress.completed_steps)}")
        print(f"      - Completion percent: {new_phase_progress.completion_percent:.1f}%")

        # Generate phase-specific welcome message
        phase_welcome_messages = {
            DesignPhase.VISUALIZATION: "Welcome to the visualization phase! Now we'll focus on spatial organization, form development, and how your ideas take shape. How does your spatial organization respond to the site's existing conditions and program requirements?",
            DesignPhase.MATERIALIZATION: "Welcome to the materialization phase! Now we'll explore technical development, material choices, and implementation strategies. How do your material choices respond to both the building's function and its environmental context?"
        }

        welcome_message = phase_welcome_messages.get(
            next_phase,
            f"Welcome to the {next_phase.value} phase! Let's continue developing your design thinking."
        )

        # Generate phase-specific image
        generated_image = None
        if self.image_generation_enabled and self.image_generator and self.prompt_generator:
            try:
                print(f"🎨 Generating {next_phase.value} phase image...")

                # Generate image prompt from conversation history
                conversation_history = session.conversation_history if hasattr(session, 'conversation_history') else []
                project_type = getattr(session, 'project_type', 'community center')

                design_description = self.prompt_generator.generate_image_prompt_from_conversation(
                    conversation_history,
                    next_phase.value.lower(),
                    project_type
                )

                # Generate the image
                image_result = self.image_generator.generate_phase_image(
                    design_description,
                    next_phase.value.lower(),
                    f"{project_type} design project"
                )

                if image_result.get("success"):
                    generated_image = {
                        "url": image_result["image_url"],
                        "prompt": image_result["prompt"],
                        "style": image_result["style"],
                        "phase": next_phase.value
                    }
                    print(f"✅ Generated {next_phase.value} phase image successfully")
                else:
                    print(f"❌ Image generation failed: {image_result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"❌ Error during image generation: {e}")

        transition_result = {
            "success": True,
            "previous_phase": current_phase.value,
            "new_phase": next_phase.value,
            "message": welcome_message,
            "generated_image": generated_image
        }

        # Store the transition result for capture by process_user_message
        self._last_transition_result = transition_result

        return transition_result

    def process_user_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a user message and return assessment results - RESTORED WORKING VERSION"""
        print(f"\n🎯 PHASE PROGRESSION: Processing response for session {session_id}")
        print(f"📝 User response: {message[:100]}...")

        session = self.sessions.get(session_id)
        if not session:
            print(f"❌ PHASE ERROR: Session {session_id} not found")
            return {"error": "Session not found"}

        print(f"📊 Current phase: {session.current_phase.value}")
        # Store the initial phase to detect transitions
        initial_phase = session.current_phase

        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            print(f"❌ PHASE ERROR: No progress found for phase {session.current_phase.value}")
            return {"error": "No current phase progress"}

        print(f"📈 Phase progress before: {current_phase_progress.completion_percent:.1f}%")
        print(f"🔢 Completed steps before: {len(current_phase_progress.completed_steps)}")

        # Get the current question with context
        user_context = message[:200] if message else ""
        project_context = session.project_description if hasattr(session, 'project_description') else ""

        current_question = self.question_bank.get_next_question(
            session.current_phase,
            current_phase_progress.completed_steps,
            user_context,
            project_context
        )

        # If no standard question, create a flexible one
        if not current_question:
            print(f"🎨 Creating flexible question for continued engagement")
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
        grade = self.grading_system.grade_response(current_question, message)
        print(f"📊 GRADING RESULTS:")
        print(f"   Overall Score: {grade.overall_score:.2f}/5.0")
        print(f"   Completeness: {grade.completeness:.2f}/5.0")
        print(f"   Depth: {grade.depth:.2f}/5.0")
        print(f"   Relevance: {grade.relevance:.2f}/5.0")
        print(f"   Innovation: {grade.innovation:.2f}/5.0")
        print(f"   Technical: {grade.technical_understanding:.2f}/5.0")

        # Update progress
        current_phase_progress.responses[current_question.question_id] = message
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
            "response": message,
            "grade": grade.overall_score
        })

        print(f"💾 Session updated with {len(session.conversation_history)} total interactions")

        # Generate phase nudge if needed
        nudge = self._generate_phase_nudge(session, current_phase_progress, grade)

        # Check for phase transitions and capture transition results
        phase_transition_result = None
        original_phase = session.current_phase.value

        # Get next question or phase transition info
        next_question = self.get_next_question(session_id)

        # Check if phase changed during get_next_question (indicates transition occurred)
        updated_session = self.sessions.get(session_id)
        if updated_session and updated_session.current_phase.value != original_phase:
            print(f"🔄 Phase transition detected: {original_phase} → {updated_session.current_phase.value}")
            # Capture the transition result from the last transition
            if hasattr(self, '_last_transition_result'):
                phase_transition_result = self._last_transition_result
                print(f"✅ Captured transition result with generated image: {bool(phase_transition_result.get('generated_image'))}")

        # Also check for final phase completion (when phase doesn't change but completes)
        elif hasattr(self, '_last_transition_result') and self._last_transition_result:
            print(f"🎉 Final phase completion detected")
            phase_transition_result = self._last_transition_result
            print(f"✅ Captured final phase result with generated image: {bool(phase_transition_result.get('generated_image'))}")
            # Clear the result after capturing it
            self._last_transition_result = None

        result = {
            "session_id": session_id,
            "current_phase": updated_session.current_phase.value if updated_session else session.current_phase.value,
            "current_step": current_question.step.value if current_question else "unknown",
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
            "session_complete": self._is_session_complete(updated_session if updated_session else session),
            "nudge": nudge,
            "question_answered": True  # Always true in working version
        }

        # Add phase transition information if transition occurred
        if phase_transition_result:
            result.update({
                "phase_transition": True,
                "transition_message": phase_transition_result.get("message", "Phase transition completed!"),
                "previous_phase": original_phase,
                "generated_image": phase_transition_result.get("generated_image")
            })
            print(f"✅ Added phase transition info to result")

        return result

    def process_response(self, session_id: str, response: str) -> Dict[str, Any]:
        """DEPRECATED: Use process_user_message instead. Kept for backward compatibility."""
        print(f"\n⚠️ DEPRECATED: process_response called - redirecting to process_user_message")
        return self.process_user_message(session_id, response)

    def get_contextual_question(self, session_id: str) -> Optional[SocraticQuestion]:
        """Get a contextual question for the current session state - RESTORED WORKING VERSION"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            return None

        # Get next question from question bank with context
        user_context = ""  # No user input context for next question
        project_context = session.project_description if hasattr(session, 'project_description') else ""

        next_question = self.question_bank.get_next_question(
            session.current_phase,
            current_phase_progress.completed_steps,
            user_context,
            project_context
        )

        return next_question

    def _check_and_handle_phase_transition(self, session_id: str) -> Dict[str, Any]:
        """Check if phase transition should occur and handle it"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            return {"no_transition": "No current phase progress"}

        # Check if current phase is ready for transition
        transition_assessment = self.transition_system.assess_phase_readiness(session, current_phase_progress)

        if transition_assessment["is_ready"]:
            next_phase = transition_assessment.get("next_phase")
            if next_phase:
                print(f"🔄 AUTO-TRANSITION: Phase transition criteria met, transitioning...")
                transition_result = self.transition_to_next_phase(session_id)
                if "error" not in transition_result:
                    print(f"✅ Successfully transitioned to {transition_result['new_phase']}")
                    return {
                        "transition_occurred": True,
                        "previous_phase": transition_result["previous_phase"],
                        "new_phase": transition_result["new_phase"],
                        "message": transition_result["message"]
                    }
                else:
                    print(f"❌ Transition failed: {transition_result['error']}")
                    return {"transition_failed": transition_result["error"]}
            else:
                print(f"ℹ️ Ready for transition but no next phase available")
                return {"no_next_phase": "Ready but no next phase"}
        else:
            print(f"ℹ️ Not ready for phase transition yet")
            return {"not_ready": "Phase transition criteria not met"}

        return {"no_transition": "No transition needed"}

        current_phase_progress = session.phase_progress.get(session.current_phase)
        if not current_phase_progress:
            print(f"❌ PHASE ERROR: No progress found for phase {session.current_phase.value}")
            return {"error": "No current phase progress"}

        print(f"📈 Phase progress before: {current_phase_progress.completion_percent:.1f}%")
        print(f"🔢 Completed steps before: {len(current_phase_progress.completed_steps)}")

        # Get the current question (this should be the question they just answered)
        # We need to reconstruct what question they were answering
        current_question = None

        # REMOVED: No longer check for transition acceptance since transitions are automatic
        # The system now automatically transitions when criteria are met

        # Try to get the question they were supposed to answer
        # This is tricky because we need to know what question was asked
        # For now, we'll use the most recent question type based on their progress

        # First try contextual questions
        user_context = ""  # No user input context available in this method
        project_context = session.project_description if hasattr(session, 'project_description') else ""

        current_question = self.question_bank.get_next_question(
            session.current_phase,
            current_phase_progress.completed_steps,
            user_context,
            project_context
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

        # Check if a phase transition occurred during processing
        phase_transitioned = session.current_phase != initial_phase
        transition_message = None

        if phase_transitioned:
            print(f"🔄 PHASE TRANSITION DETECTED: {initial_phase.value} → {session.current_phase.value}")
            transition_message = f"Congratulations! You've successfully completed the {initial_phase.value} phase and advanced to {session.current_phase.value}."
            print(f"🔍 DEBUG: New phase progress status:")
            new_progress = session.phase_progress.get(session.current_phase)
            if new_progress:
                print(f"   - Completed steps: {len(new_progress.completed_steps)}")
                print(f"   - Is complete: {new_progress.is_complete}")
                print(f"   - Completion percent: {new_progress.completion_percent:.1f}%")

        # CRITICAL FIX: Get the correct phase progress for the CURRENT phase (not the old one)
        final_phase_progress = session.phase_progress.get(session.current_phase)
        if not final_phase_progress:
            # This shouldn't happen, but fallback to avoid crashes
            final_phase_progress = current_phase_progress
            print(f"⚠️ WARNING: No progress found for current phase {session.current_phase.value}, using fallback")

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
                "completed_steps": [step.value for step in final_phase_progress.completed_steps],
                "average_score": final_phase_progress.average_score,
                "is_complete": final_phase_progress.is_complete
            },
            "next_question": next_question.question_text if next_question else None,
            "phase_complete": final_phase_progress.is_complete,
            "session_complete": self._is_session_complete(session),
            "nudge": nudge,
            # Add phase transition information
            "phase_transition": phase_transitioned,
            "transition_message": transition_message,
            "previous_phase": initial_phase.value if phase_transitioned else None
        }
    
    def _compute_phase_completion_percent(self, session: SessionState, phase_progress: PhaseProgress) -> float:
        """Compute a meaningful completion percent (0-100) for the current phase.

        Uses a balanced approach that progresses at reasonable pace:
        - Interaction engagement (50%) - based on meaningful exchanges IN CURRENT PHASE
        - Quality of responses (30%) - based on actual grading scores
        - Concept coverage (20%) - checklist items completed
        """
        print(f"\n🧮 CALCULATING COMPLETION PERCENT for {session.current_phase.value}:")

        # 1. INTERACTION ENGAGEMENT (50%) - Based on meaningful exchanges IN CURRENT PHASE ONLY
        # Count interactions since this phase started, not total session interactions
        phase_start_time = phase_progress.start_time
        current_phase_interactions = 0

        for interaction in session.conversation_history:
            interaction_time = interaction.get('timestamp')
            if interaction_time and isinstance(interaction_time, str):
                try:
                    from datetime import datetime
                    interaction_dt = datetime.fromisoformat(interaction_time.replace('Z', '+00:00'))
                    if interaction_dt >= phase_start_time:
                        current_phase_interactions += 1
                except:
                    # If timestamp parsing fails, count all interactions (fallback)
                    current_phase_interactions = len(session.conversation_history)
                    break
            elif not interaction_time:
                # If no timestamps, use completed steps as proxy for phase-specific interactions
                # But ensure we count at least some interactions if there's conversation history
                current_phase_interactions = max(len(phase_progress.completed_steps),
                                               min(len(session.conversation_history), 3))
                break

        # More generous progression - each meaningful interaction adds significant value
        if current_phase_interactions >= 3:
            engagement_ratio = 1.0  # Full credit after 3 interactions
        elif current_phase_interactions >= 2:
            engagement_ratio = 0.75  # Good progress after 2 interactions
        elif current_phase_interactions >= 1:
            engagement_ratio = 0.5   # Decent start after 1 interaction
        else:
            engagement_ratio = 0.0

        print(f"   💬 Engagement: {current_phase_interactions} interactions in current phase = {engagement_ratio:.2f} ({engagement_ratio*50:.1f}% of total)")

        # 2. QUALITY OF RESPONSES (30%) - Based on actual grading scores
        if phase_progress.grades:
            print(f"   🔍 DEBUG: Computing quality from {len(phase_progress.grades)} grades")
            total_score = sum(grade.overall_score for grade in phase_progress.grades.values())
            max_possible = len(phase_progress.grades) * 5.0  # Assuming 5.0 is max score
            quality_ratio = min(total_score / max_possible, 1.0) if max_possible > 0 else 0.0
            print(f"   🔍 DEBUG: Quality calculation successful: {total_score}/{max_possible} = {quality_ratio}")
        else:
            # No grades yet - give some baseline credit for participation
            quality_ratio = 0.6 if current_phase_interactions > 0 else 0.0
            print(f"   🔍 DEBUG: No grades yet, baseline quality_ratio = {quality_ratio}")

        print(f"   🎯 Quality: {quality_ratio:.2f} ({quality_ratio*30:.1f}% of total)")

        # 3. CONCEPT COVERAGE (20%) - Checklist items completed
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

        # More forgiving concept calculation - give partial credit for engagement even without keyword matches
        if total_required > 0:
            base_concept_ratio = completed_required / total_required
            # Give some baseline credit (20%) for being in the phase and engaging
            concept_ratio = max(base_concept_ratio, 0.2)
        else:
            concept_ratio = 0.5  # Give some baseline credit when no required items
        print(f"   ✅ Concepts: {completed_required}/{total_required} = {concept_ratio:.2f} ({concept_ratio*15:.1f}% of total)")

        # 4. VISUAL ENGAGEMENT (5%) - Based on visual artifacts and analysis
        visual_ratio = 0.0
        if hasattr(session, 'visual_artifacts') and session.visual_artifacts:
            # Check if there are visual artifacts in the current phase
            phase_visual_count = 0
            for artifact in session.visual_artifacts:
                if hasattr(artifact, 'timestamp') and artifact.timestamp >= phase_start_time:
                    phase_visual_count += 1

            if phase_visual_count > 0:
                visual_ratio = min(1.0, phase_visual_count / 2.0)  # Full credit for 2+ visual artifacts
                print(f"   🖼️ Visual: {phase_visual_count} artifacts in current phase = {visual_ratio:.2f} ({visual_ratio*5:.1f}% of total)")
            else:
                print(f"   🖼️ Visual: No visual artifacts in current phase = 0.0 (0.0% of total)")
        else:
            print(f"   🖼️ Visual: No visual artifacts available = 0.0 (0.0% of total)")

        # Combine all factors with adjusted weights (50% + 30% + 15% + 5% = 100%)
        percent = 100.0 * (0.50 * engagement_ratio + 0.30 * quality_ratio + 0.15 * concept_ratio + 0.05 * visual_ratio)
        print(f"   🧮 CALCULATION: (50% × {engagement_ratio:.2f}) + (30% × {quality_ratio:.2f}) + (15% × {concept_ratio:.2f}) + (5% × {visual_ratio:.2f})")
        print(f"   🧮 CALCULATION: {0.50 * engagement_ratio:.2f} + {0.30 * quality_ratio:.2f} + {0.15 * concept_ratio:.2f} + {0.05 * visual_ratio:.2f} = {percent/100:.2f}")

        # Special case: If all 4 core steps are completed, ensure high completion
        if len(phase_progress.completed_steps) >= 4 and current_phase_interactions >= 3:
            percent = max(percent, 85.0)
            print(f"   🎯 ALL STEPS BONUS: 4 steps completed, minimum 85%")

        # Clamp to [0, 100]
        percent = max(0.0, min(100.0, percent))

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
        """Check if the current phase is complete based on meaningful progress"""
        threshold = self.phase_thresholds.get(session.current_phase, 3.0)

        # Much more achievable completion criteria for better user experience
        has_meaningful_engagement = len(session.conversation_history) >= 2  # At least 2 interactions
        has_sufficient_quality = phase_progress.average_score >= 0.8  # Lowered from 2.0 to 0.8 (more realistic)
        has_good_completion = phase_progress.completion_percent >= 45.0  # Lowered from 60% to 45%

        # Check if required checklist items are completed
        items = self.phase_checklist_items.get(session.current_phase, [])
        required_items = [i for i in items if i.get('required')]
        phase_key = session.current_phase.value
        completed_required = 0

        if required_items:
            for item in required_items:
                item_id = item.get('id')
                if item_id:
                    state = session.checklist_state.get(phase_key, {}).get(item_id, {})
                    if state.get('status') == 'completed':
                        completed_required += 1

        # Special handling for final phase (materialization) - be more lenient
        if session.current_phase == DesignPhase.MATERIALIZATION and len(phase_progress.completed_steps) >= 4:
            has_core_concepts = True  # Allow completion if all steps are done
            print(f"   🎯 FINAL PHASE OVERRIDE: Allowing completion with {len(phase_progress.completed_steps)} steps")
        else:
            has_core_concepts = (completed_required >= len(required_items) * 0.2) if required_items else True  # Reduced to 20% of required concepts

        print(f"   🔍 PHASE COMPLETION CHECK (OPTIMIZED FOR IMAGE GENERATION):")
        print(f"      Engagement: {has_meaningful_engagement} (≥2 interactions)")
        print(f"      Quality: {has_sufficient_quality} (score ≥0.8)")
        print(f"      Completion: {has_good_completion} (≥45%)")
        print(f"      Concepts: {has_core_concepts} ({completed_required}/{len(required_items)} required)")

        if has_meaningful_engagement and has_sufficient_quality and has_good_completion and has_core_concepts:
            phase_progress.is_complete = True
            phase_progress.completion_percent = 100.0  # Ensure completed phases show 100%
            print(f"   🎉 PHASE MARKED COMPLETE! 🎨 IMAGE GENERATION WILL BE TRIGGERED!")
            print(f"   📈 COMPLETION SET TO 100%")
            self._advance_to_next_phase(session)
    
    def _advance_to_next_phase(self, session: SessionState):
        """Advance to the next phase or handle final phase completion"""
        phase_order = [DesignPhase.IDEATION, DesignPhase.VISUALIZATION, DesignPhase.MATERIALIZATION]

        try:
            current_index = phase_order.index(session.current_phase)
            if current_index < len(phase_order) - 1:
                # Advance to next phase
                next_phase = phase_order[current_index + 1]
                session.current_phase = next_phase
                session.phase_progress[next_phase] = PhaseProgress(
                    phase=next_phase,
                    current_step=SocraticStep.INITIAL_CONTEXT_REASONING
                )
                logger.info(f"Advanced to phase: {next_phase.value}")
            else:
                # Final phase completed - generate completion image
                print(f"🎉 FINAL PHASE COMPLETED: {session.current_phase.value}")
                self._generate_final_phase_image(session)
        except ValueError:
            logger.error(f"Invalid phase: {session.current_phase}")

    def _generate_final_phase_image(self, session: SessionState):
        """Generate image for the completed final phase"""
        if self.image_generation_enabled and self.image_generator and self.prompt_generator:
            try:
                print(f"🎨 Generating final {session.current_phase.value} phase image...")

                # Generate image prompt from conversation history
                conversation_history = session.conversation_history if hasattr(session, 'conversation_history') else []
                project_type = getattr(session, 'project_type', 'community center')

                design_description = self.prompt_generator.generate_image_prompt_from_conversation(
                    conversation_history,
                    session.current_phase.value.lower(),
                    project_type
                )

                # Generate the image
                image_result = self.image_generator.generate_phase_image(
                    design_description,
                    session.current_phase.value.lower(),
                    f"{project_type} design project"
                )

                if image_result.get("success"):
                    generated_image = {
                        "url": image_result["image_url"],
                        "prompt": image_result["prompt"],
                        "style": image_result["style"],
                        "phase": session.current_phase.value
                    }
                    print(f"✅ Generated final {session.current_phase.value} phase image successfully")

                    # Store the image result for the dashboard to pick up
                    self._last_transition_result = {
                        "success": True,
                        "previous_phase": session.current_phase.value,
                        "new_phase": "complete",
                        "message": f"🎉 Congratulations! You've completed the {session.current_phase.value} phase.",
                        "generated_image": generated_image
                    }
                else:
                    print(f"❌ Final image generation failed: {image_result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"❌ Error during final image generation: {e}")
    
    def _is_session_complete(self, session: SessionState) -> bool:
        """Check if the entire session is complete"""
        return all(
            phase_progress.is_complete 
            for phase_progress in session.phase_progress.values()
        )
    
    def get_progress_summary(self, session_id: str) -> Dict[str, Any]:
        """Get progress summary for dashboard integration (alias for get_session_summary)"""
        return self.get_session_summary(session_id)

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

# Commented out to prevent test execution when imported
# if __name__ == "__main__":
#     main()

