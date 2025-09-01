"""
Phase-Based Assessment Manager for Structured Socratic Learning

Implements the comprehensive phase-based assessment system described in phase_based.txt
with automatic phase detection, Socratic questioning patterns, and progression tracking.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os
from openai import OpenAI

from state_manager import ArchMentorState


class DesignPhase(Enum):
    """Design phases with specific weights and requirements."""
    IDEATION = "ideation"
    VISUALIZATION = "visualization" 
    MATERIALIZATION = "materialization"


class SocraticStep(Enum):
    """4-Step Socratic Progression for each phase."""
    INITIAL_CONTEXT_REASONING = "initial_context_reasoning"
    KNOWLEDGE_SYNTHESIS_TRIGGER = "knowledge_synthesis_trigger"
    SOCRATIC_QUESTIONING = "socratic_questioning"
    METACOGNITIVE_PROMPT = "metacognitive_prompt"


@dataclass
class PhaseAssessment:
    """Assessment results for a specific phase."""
    phase: DesignPhase
    step: SocraticStep
    score: float
    completeness: float
    depth: float
    relevance: float
    innovation: float
    technical_understanding: float
    overall_score: float
    feedback: str
    ready_for_next: bool


@dataclass
class SocraticQuestion:
    """Structured Socratic question with context."""
    phase: DesignPhase
    step: SocraticStep
    question_text: str
    assessment_criteria: List[str]
    expected_elements: List[str]
    difficulty_level: str


class PhaseAssessmentManager:
    """
    Manages phase-based assessment with Socratic questioning patterns.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Phase weights from phase_based.txt
        self.phase_weights = {
            DesignPhase.IDEATION: 0.25,
            DesignPhase.VISUALIZATION: 0.35,
            DesignPhase.MATERIALIZATION: 0.40
        }
        
        # Minimum scores for phase progression
        self.phase_thresholds = {
            DesignPhase.IDEATION: 3.0,
            DesignPhase.VISUALIZATION: 3.5,
            DesignPhase.MATERIALIZATION: 4.0
        }
        
        # Initialize Socratic question patterns
        self.socratic_patterns = self._initialize_socratic_patterns()
        
    def _initialize_socratic_patterns(self) -> Dict[DesignPhase, Dict[SocraticStep, Dict[str, Any]]]:
        """Initialize Socratic question patterns for each phase and step."""
        
        return {
            DesignPhase.IDEATION: {
                SocraticStep.INITIAL_CONTEXT_REASONING: {
                    "template": "Before we begin designing, what do you think are the most important questions we should ask about this {building_type}?",
                    "criteria": ["problem_understanding", "contextual_awareness"],
                    "expected_elements": ["user_needs", "site_context", "program_requirements"]
                },
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: {
                    "template": "What are some successful examples of {building_type} transformations you're aware of?",
                    "criteria": ["precedent_knowledge", "knowledge_application"],
                    "expected_elements": ["precedent_examples", "design_principles", "lessons_learned"]
                },
                SocraticStep.SOCRATIC_QUESTIONING: {
                    "template": "Why might the existing {context_element} be valuable to preserve? What would be lost if we completely transformed it?",
                    "criteria": ["critical_thinking", "analytical_skills"],
                    "expected_elements": ["trade_off_analysis", "value_assessment", "design_reasoning"]
                },
                SocraticStep.METACOGNITIVE_PROMPT: {
                    "template": "How are you approaching this problem differently than a typical new-build {building_type}?",
                    "criteria": ["metacognitive_reflection", "self_awareness"],
                    "expected_elements": ["process_reflection", "approach_comparison", "learning_awareness"]
                }
            },
            DesignPhase.VISUALIZATION: {
                SocraticStep.INITIAL_CONTEXT_REASONING: {
                    "template": "How does your spatial organization respond to the site's existing conditions and program requirements?",
                    "criteria": ["spatial_reasoning", "site_response"],
                    "expected_elements": ["spatial_organization", "site_integration", "program_response"]
                },
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: {
                    "template": "What precedents inform your approach to circulation and spatial hierarchy?",
                    "criteria": ["precedent_application", "circulation_design"],
                    "expected_elements": ["circulation_patterns", "spatial_hierarchy", "precedent_integration"]
                },
                SocraticStep.SOCRATIC_QUESTIONING: {
                    "template": "How does your form development balance functional efficiency with architectural expression?",
                    "criteria": ["form_development", "design_balance"],
                    "expected_elements": ["form_logic", "functional_efficiency", "architectural_expression"]
                },
                SocraticStep.METACOGNITIVE_PROMPT: {
                    "template": "What design decisions are you most confident about, and which ones need more exploration?",
                    "criteria": ["design_confidence", "uncertainty_awareness"],
                    "expected_elements": ["confidence_assessment", "uncertainty_identification", "exploration_needs"]
                }
            },
            DesignPhase.MATERIALIZATION: {
                SocraticStep.INITIAL_CONTEXT_REASONING: {
                    "template": "How do your material choices respond to both the building's function and its environmental context?",
                    "criteria": ["material_selection", "environmental_integration"],
                    "expected_elements": ["material_strategy", "environmental_response", "functional_integration"]
                },
                SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER: {
                    "template": "What construction precedents demonstrate effective integration of your chosen materials?",
                    "criteria": ["construction_knowledge", "precedent_application"],
                    "expected_elements": ["construction_precedents", "material_integration", "technical_solutions"]
                },
                SocraticStep.SOCRATIC_QUESTIONING: {
                    "template": "How does your technical approach balance innovation with constructability and cost considerations?",
                    "criteria": ["technical_understanding", "practical_considerations"],
                    "expected_elements": ["technical_innovation", "constructability", "cost_awareness"]
                },
                SocraticStep.METACOGNITIVE_PROMPT: {
                    "template": "What aspects of your design would you prioritize if budget or time constraints required simplification?",
                    "criteria": ["constraint_understanding", "priority_assessment"],
                    "expected_elements": ["constraint_awareness", "priority_hierarchy", "simplification_strategy"]
                }
            }
        }
    
    def detect_current_phase(self, state: ArchMentorState) -> Tuple[DesignPhase, SocraticStep]:
        """
        Detect the current design phase and Socratic step based on conversation analysis.
        """
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if not user_messages:
            return DesignPhase.IDEATION, SocraticStep.INITIAL_CONTEXT_REASONING
        
        # Analyze conversation content to determine phase
        recent_content = " ".join(user_messages[-3:]).lower()
        
        # ENHANCED: More conservative phase detection with stronger keyword requirements
        materialization_keywords = ["material", "construction", "detail", "technical", "build", "cost", "feasibility", "structure", "system", "method"]
        visualization_keywords = ["space", "form", "layout", "circulation", "organization", "diagram", "plan", "spatial", "arrangement"]
        ideation_keywords = ["concept", "idea", "approach", "strategy", "vision", "philosophy", "purpose", "goal", "need", "want"]

        # Count keyword matches for more robust detection
        mat_count = sum(1 for keyword in materialization_keywords if keyword in recent_content)
        viz_count = sum(1 for keyword in visualization_keywords if keyword in recent_content)
        idea_count = sum(1 for keyword in ideation_keywords if keyword in recent_content)

        # Get total messages count first
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        total_messages = len(user_messages)

        # BALANCED: Require substantial evidence AND minimum messages for phase advancement
        min_messages_for_viz = 8   # Balanced: 8 user messages before considering visualization (was 10, too strict)
        min_messages_for_mat = 12  # Balanced: 12 user messages before considering materialization (was 16, too strict)

        # Also require action-oriented language, not just conceptual discussion
        has_design_actions = any(action in recent_content for action in [
            "i'll place", "i will place", "i'm placing", "i'll put", "i will put",
            "i'll locate", "i will locate", "i'll position", "i will position",
            "i'll organize", "i will organize", "i'll arrange", "i will arrange"
        ])

        has_specific_proposals = any(proposal in recent_content for proposal in [
            "my approach is", "my strategy is", "i propose", "i suggest",
            "the plan is", "the idea is", "i'll start by", "first i'll"
        ])

        # MATERIALIZATION: Requires many more messages + multiple material keywords + specific technical discussion
        # Increased threshold to make materialization phase longer
        if (total_messages >= min_messages_for_mat + 8 and  # Increased by 8 messages
            mat_count >= 4 and  # Increased keyword requirement
            ("construction" in recent_content or "detail" in recent_content or "material" in recent_content)):
            current_phase = DesignPhase.MATERIALIZATION

        # VISUALIZATION: Requires more messages + multiple spatial keywords + actual design actions
        # Increased threshold to make visualization phase longer
        elif (total_messages >= min_messages_for_viz + 6 and  # Increased by 6 messages
              viz_count >= 4 and  # Increased keyword requirement
              (has_design_actions or has_specific_proposals)):
            current_phase = DesignPhase.VISUALIZATION

        else:
            # Stay in IDEATION much longer - this is where most of the learning happens
            current_phase = DesignPhase.IDEATION
        
        # ENHANCED: Determine Socratic step based on content depth, not just message count
        # (total_messages already defined above)
        recent_content = " ".join(user_messages[-3:]).lower()

        # ENHANCED: Check for depth indicators in recent messages
        has_detailed_analysis = any(indicator in recent_content for indicator in [
            "because", "therefore", "however", "although", "considering", "given that",
            "this means", "as a result", "on the other hand", "in contrast",
            # ENHANCED: Add more architectural reasoning indicators
            "this supports", "this responds to", "this enhances", "this allows",
            "while still", "without undermining", "it leans toward", "i think this",
            "who is", "what kind of", "how should", "if we can", "are we prioritizing"
        ])

        has_specific_examples = any(indicator in recent_content for indicator in [
            "for example", "such as", "like", "similar to", "precedent", "case study",
            "project", "building", "architect", "firm"
        ])

        has_implementation_details = any(indicator in recent_content for indicator in [
            "material", "construction", "detail", "technical", "build", "cost",
            "feasibility", "structure", "system", "method"
        ])

        # EXTREMELY CONSERVATIVE step progression - spend much more time in each step
        # Increased thresholds to make phases significantly longer
        if total_messages <= 8 or not has_detailed_analysis:
            current_step = SocraticStep.INITIAL_CONTEXT_REASONING
        elif total_messages <= 16 or not has_specific_examples:
            current_step = SocraticStep.KNOWLEDGE_SYNTHESIS_TRIGGER
        elif total_messages <= 24 or not has_implementation_details:
            current_step = SocraticStep.SOCRATIC_QUESTIONING
        else:
            current_step = SocraticStep.METACOGNITIVE_PROMPT
        
        return current_phase, current_step
    
    async def generate_socratic_question(self, phase: DesignPhase, step: SocraticStep, 
                                 building_type: str, context: Dict[str, Any]) -> SocraticQuestion:
        """
        Generate a Socratic question for the specified phase and step using LLM instead of hardcoded templates.
        """
        
        pattern = self.socratic_patterns[phase][step]
        
        try:
            # Generate dynamic question using LLM instead of hardcoded template
            prompt = f"""
            You are an expert architectural mentor helping a student in the {phase.value} phase of design.
            
            CONTEXT:
            - Building type: {building_type}
            - Current step: {step.value}
            - Phase: {phase.value}
            - Assessment criteria: {', '.join(pattern['criteria'])}
            - Expected elements: {', '.join(pattern['expected_elements'])}
            
            TASK: Generate a thoughtful, engaging Socratic question that:
            1. Encourages critical thinking about {building_type} design
            2. Is appropriate for the {step.value} step in the {phase.value} phase
            3. Helps the student consider {', '.join(pattern['expected_elements'])}
            4. Sounds natural and conversational, not like a template
            5. Is specific to {building_type} projects
            
            RESPONSE: Write only the question, no explanations or formatting.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_generated_question = response.choices[0].message.content.strip()
            
            # Fallback to template if LLM fails
            if not ai_generated_question or len(ai_generated_question) < 20:
                question_text = pattern["template"].format(
                    building_type=building_type,
                    context_element=context.get("context_element", "character")
                )
            else:
                question_text = ai_generated_question
                
        except Exception as e:
            # Fallback to template if LLM fails
            question_text = pattern["template"].format(
                building_type=building_type,
                context_element=context.get("context_element", "character")
            )
        
        return SocraticQuestion(
            phase=phase,
            step=step,
            question_text=question_text,
            assessment_criteria=pattern["criteria"],
            expected_elements=pattern["expected_elements"],
            difficulty_level=context.get("difficulty_level", "moderate")
        )
    
    async def assess_response(self, question: SocraticQuestion, user_response: str, 
                            context: Dict[str, Any]) -> PhaseAssessment:
        """
        Assess a user's response to a Socratic question using AI-powered analysis.
        """
        
        # Use AI to grade the response
        scores = await self._ai_grade_response(question, user_response, context)
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Generate feedback
        feedback = await self._generate_assessment_feedback(question, user_response, scores, context)
        
        # Determine if ready for next step/phase
        threshold = self.phase_thresholds[question.phase]
        ready_for_next = overall_score >= threshold
        
        return PhaseAssessment(
            phase=question.phase,
            step=question.step,
            score=overall_score,
            completeness=scores.get("completeness", 0),
            depth=scores.get("depth", 0),
            relevance=scores.get("relevance", 0),
            innovation=scores.get("innovation", 0),
            technical_understanding=scores.get("technical_understanding", 0),
            overall_score=overall_score,
            feedback=feedback,
            ready_for_next=ready_for_next
        )
    
    async def _ai_grade_response(self, question: SocraticQuestion, user_response: str,
                               context: Dict[str, Any]) -> Dict[str, float]:
        """
        Use AI to grade the user's response against the assessment criteria with smart optimization.
        """

        # PERFORMANCE: Skip AI grading for very short responses
        if len(user_response.strip()) < 15:
            print(f"📊 QUICK_GRADE: Response too short ({len(user_response)} chars) - using basic scoring")
            return {
                "completeness": 1.0,
                "depth": 1.0,
                "relevance": 2.0,
                "innovation": 1.0,
                "technical_understanding": 1.0
            }

        # PERFORMANCE: Check cache for similar responses
        import streamlit as st
        cache_key = f"grade_{hash(user_response.lower().strip())}_{question.phase.value}"
        if hasattr(st.session_state, cache_key):
            print(f"📊 CACHE_HIT: Using cached grade for similar response")
            return getattr(st.session_state, cache_key)

        prompt = f"""
        Grade this architecture student's response to a Socratic question on a scale of 0-5 for each criterion.
        
        QUESTION: {question.question_text}
        STUDENT RESPONSE: {user_response}
        PHASE: {question.phase.value}
        STEP: {question.step.value}
        
        Grade on these criteria (0-5 scale):
        1. Completeness: Does the response address all aspects of the question?
        2. Depth: Does the response show detailed analysis and reasoning?
        3. Relevance: Is the response relevant to architectural design principles?
        4. Innovation: Does the response show creative and original thinking?
        5. Technical Understanding: Does the response demonstrate appropriate knowledge?
        
        Return only a JSON object with scores:
        {{"completeness": X.X, "depth": X.X, "relevance": X.X, "innovation": X.X, "technical_understanding": X.X}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse the JSON response
            import json
            scores_text = response.choices[0].message.content.strip()
            scores = json.loads(scores_text)

            # PERFORMANCE: Cache the grading result
            setattr(st.session_state, cache_key, scores)
            print(f"📊 CACHE_STORE: Cached grading result")

            return scores
            
        except Exception as e:
            print(f"AI grading failed: {e}")
            # Fallback scoring
            return {
                "completeness": 3.0,
                "depth": 3.0,
                "relevance": 3.0,
                "innovation": 3.0,
                "technical_understanding": 3.0
            }
    
    async def _generate_assessment_feedback(self, question: SocraticQuestion, user_response: str, 
                                          scores: Dict[str, float], context: Dict[str, Any]) -> str:
        """
        Generate detailed feedback based on the assessment scores.
        """
        
        prompt = f"""
        Generate constructive feedback for an architecture student based on their response assessment.
        
        QUESTION: {question.question_text}
        STUDENT RESPONSE: {user_response}
        SCORES: {scores}
        
        Provide feedback that:
        1. Acknowledges strengths in their response
        2. Identifies specific areas for improvement
        3. Suggests concrete next steps
        4. Maintains an encouraging tone
        
        Keep it under 150 words.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Feedback generation failed: {e}")
            return "Good work on your response. Continue developing your ideas with more specific details and consider how your approach relates to broader architectural principles."
