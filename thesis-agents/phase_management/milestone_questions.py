"""
Milestone Question Bank and Grading System
Manages intelligent questioning and assessment for design phase milestones
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

class MilestoneType(Enum):
    SITE_ANALYSIS = "site_analysis"
    PROGRAM_REQUIREMENTS = "program_requirements"
    CONCEPT_DEVELOPMENT = "concept_development"
    SPATIAL_ORGANIZATION = "spatial_organization"
    CIRCULATION_DESIGN = "circulation_design"
    FORM_DEVELOPMENT = "form_development"
    LIGHTING_STRATEGY = "lighting_strategy"
    CONSTRUCTION_SYSTEMS = "construction_systems"
    MATERIAL_SELECTION = "material_selection"
    TECHNICAL_DETAILS = "technical_details"
    PRESENTATION_PREP = "presentation_prep"
    DOCUMENTATION = "documentation"

class QuestionDifficulty(Enum):
    BASIC = "basic"
    ANALYTICAL = "analytical"
    SYNTHETIC = "synthetic"
    EVALUATIVE = "evaluative"

@dataclass
class Question:
    id: str
    milestone: MilestoneType
    difficulty: QuestionDifficulty
    text: str
    keywords: List[str]
    follow_up_questions: List[str]
    grading_criteria: Dict[str, str]

@dataclass
class GradingResult:
    completeness: float  # 0-5
    depth: float  # 0-5
    relevance: float  # 0-5
    innovation: float  # 0-5
    technical_understanding: float  # 0-5
    overall_score: float  # 0-5
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

class MilestoneQuestionBank:
    """Comprehensive question bank for design phase milestones"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
        self.grading_rubrics = self._initialize_grading_rubrics()
    
    def _initialize_questions(self) -> Dict[MilestoneType, List[Question]]:
        """Initialize the question bank for each milestone"""
        
        questions = {
            MilestoneType.SITE_ANALYSIS: [
                Question(
                    id="site_001",
                    milestone=MilestoneType.SITE_ANALYSIS,
                    difficulty=QuestionDifficulty.BASIC,
                    text="What are the key physical characteristics of your site?",
                    keywords=["topography", "climate", "vegetation", "soil", "drainage"],
                    follow_up_questions=[
                        "How do these physical characteristics influence your design decisions?",
                        "What are the main opportunities and constraints these characteristics present?"
                    ],
                    grading_criteria={
                        "completeness": "Addresses multiple physical aspects (topography, climate, vegetation, etc.)",
                        "depth": "Provides detailed analysis rather than just observations",
                        "relevance": "Connects site characteristics to design implications",
                        "innovation": "Shows unique insights or creative responses to site conditions",
                        "technical_understanding": "Demonstrates understanding of site analysis principles"
                    }
                ),
                Question(
                    id="site_002",
                    milestone=MilestoneType.SITE_ANALYSIS,
                    difficulty=QuestionDifficulty.ANALYTICAL,
                    text="How does the site's context influence your design approach?",
                    keywords=["context", "surroundings", "neighborhood", "urban", "rural"],
                    follow_up_questions=[
                        "What specific contextual elements are most important to your design?",
                        "How will your building respond to its immediate surroundings?"
                    ],
                    grading_criteria={
                        "completeness": "Considers multiple contextual factors (urban/rural, neighbors, history)",
                        "depth": "Analyzes context beyond surface observations",
                        "relevance": "Shows clear connection between context and design decisions",
                        "innovation": "Proposes creative responses to contextual challenges",
                        "technical_understanding": "Understands contextual analysis methods"
                    }
                ),
                Question(
                    id="site_003",
                    milestone=MilestoneType.SITE_ANALYSIS,
                    difficulty=QuestionDifficulty.SYNTHETIC,
                    text="What are the main opportunities and constraints of your site?",
                    keywords=["opportunities", "constraints", "potential", "limitations", "challenges"],
                    follow_up_questions=[
                        "How are you planning to maximize the opportunities?",
                        "What strategies will you use to address the constraints?"
                    ],
                    grading_criteria={
                        "completeness": "Identifies both opportunities and constraints comprehensively",
                        "depth": "Analyzes the implications of each opportunity/constraint",
                        "relevance": "Connects opportunities/constraints to design strategy",
                        "innovation": "Shows creative approaches to leveraging opportunities or overcoming constraints",
                        "technical_understanding": "Demonstrates understanding of site potential and limitations"
                    }
                )
            ],
            
            MilestoneType.PROGRAM_REQUIREMENTS: [
                Question(
                    id="program_001",
                    milestone=MilestoneType.PROGRAM_REQUIREMENTS,
                    difficulty=QuestionDifficulty.BASIC,
                    text="What are the primary functions your building needs to serve?",
                    keywords=["functions", "program", "activities", "spaces", "requirements"],
                    follow_up_questions=[
                        "How do these functions relate to each other?",
                        "What are the spatial requirements for each function?"
                    ],
                    grading_criteria={
                        "completeness": "Lists all major functions and their basic requirements",
                        "depth": "Explains the nature and complexity of each function",
                        "relevance": "Shows understanding of functional requirements in architectural terms",
                        "innovation": "Suggests creative approaches to functional organization",
                        "technical_understanding": "Demonstrates knowledge of programming principles"
                    }
                ),
                Question(
                    id="program_002",
                    milestone=MilestoneType.PROGRAM_REQUIREMENTS,
                    difficulty=QuestionDifficulty.ANALYTICAL,
                    text="Who are the main users and what are their specific needs?",
                    keywords=["users", "occupants", "needs", "requirements", "accessibility"],
                    follow_up_questions=[
                        "How do different user groups interact with each other?",
                        "What are the accessibility requirements for your users?"
                    ],
                    grading_criteria={
                        "completeness": "Identifies all major user groups and their needs",
                        "depth": "Analyzes user needs in detail, including behavioral patterns",
                        "relevance": "Shows clear connection between user needs and design requirements",
                        "innovation": "Proposes creative solutions for meeting diverse user needs",
                        "technical_understanding": "Understands user-centered design principles"
                    }
                ),
                Question(
                    id="program_003",
                    milestone=MilestoneType.PROGRAM_REQUIREMENTS,
                    difficulty=QuestionDifficulty.SYNTHETIC,
                    text="What are the spatial relationships between different functions?",
                    keywords=["adjacency", "relationships", "proximity", "separation", "connection"],
                    follow_up_questions=[
                        "How will these relationships affect the building's organization?",
                        "What are the circulation requirements between functions?"
                    ],
                    grading_criteria={
                        "completeness": "Maps out relationships between all major functions",
                        "depth": "Explains the reasoning behind spatial relationships",
                        "relevance": "Shows understanding of how relationships affect design",
                        "innovation": "Proposes creative organizational strategies",
                        "technical_understanding": "Demonstrates knowledge of spatial planning principles"
                    }
                )
            ],
            
            MilestoneType.CONCEPT_DEVELOPMENT: [
                Question(
                    id="concept_001",
                    milestone=MilestoneType.CONCEPT_DEVELOPMENT,
                    difficulty=QuestionDifficulty.BASIC,
                    text="What is your core design concept or philosophy?",
                    keywords=["concept", "philosophy", "approach", "idea", "vision"],
                    follow_up_questions=[
                        "How did you develop this concept?",
                        "What makes this concept unique or appropriate for your project?"
                    ],
                    grading_criteria={
                        "completeness": "Clearly articulates the main concept and its key elements",
                        "depth": "Explains the reasoning and development of the concept",
                        "relevance": "Shows how the concept addresses the project requirements",
                        "innovation": "Demonstrates creative and original thinking",
                        "technical_understanding": "Shows understanding of conceptual design principles"
                    }
                ),
                Question(
                    id="concept_002",
                    milestone=MilestoneType.CONCEPT_DEVELOPMENT,
                    difficulty=QuestionDifficulty.ANALYTICAL,
                    text="How does your concept respond to the site and program?",
                    keywords=["response", "site", "program", "integration", "harmony"],
                    follow_up_questions=[
                        "What specific site or program elements influenced your concept?",
                        "How will your concept be expressed in the building's form and organization?"
                    ],
                    grading_criteria={
                        "completeness": "Explains how concept addresses both site and program requirements",
                        "depth": "Analyzes the specific ways concept responds to project conditions",
                        "relevance": "Shows clear connection between concept and project needs",
                        "innovation": "Proposes creative responses to site and program challenges",
                        "technical_understanding": "Demonstrates understanding of concept-site-program integration"
                    }
                ),
                Question(
                    id="concept_003",
                    milestone=MilestoneType.CONCEPT_DEVELOPMENT,
                    difficulty=QuestionDifficulty.EVALUATIVE,
                    text="What precedents or inspirations inform your approach?",
                    keywords=["precedents", "inspirations", "references", "influences", "examples"],
                    follow_up_questions=[
                        "How are you adapting these precedents to your specific project?",
                        "What makes your approach different from these precedents?"
                    ],
                    grading_criteria={
                        "completeness": "Identifies relevant precedents and explains their influence",
                        "depth": "Analyzes how precedents inform the design approach",
                        "relevance": "Shows appropriate selection and use of precedents",
                        "innovation": "Demonstrates creative adaptation of precedents",
                        "technical_understanding": "Shows understanding of precedent analysis and application"
                    }
                )
            ]
        }
        
        # Add more milestones as needed...
        return questions
    
    def _initialize_grading_rubrics(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize grading rubrics for different criteria"""
        
        return {
            "completeness": {
                "5": ["Comprehensive coverage of all aspects", "Addresses multiple dimensions", "No significant gaps"],
                "4": ["Good coverage of most aspects", "Addresses key dimensions", "Minor gaps"],
                "3": ["Adequate coverage of main aspects", "Addresses primary dimensions", "Some gaps"],
                "2": ["Limited coverage", "Addresses few dimensions", "Significant gaps"],
                "1": ["Very limited coverage", "Addresses minimal dimensions", "Major gaps"],
                "0": ["No relevant coverage", "Does not address the question", "Complete lack of response"]
            },
            "depth": {
                "5": ["Detailed analysis and explanation", "Shows sophisticated understanding", "Provides insights"],
                "4": ["Good analysis with explanation", "Shows solid understanding", "Some insights"],
                "3": ["Basic analysis", "Shows adequate understanding", "Limited insights"],
                "2": ["Superficial analysis", "Shows basic understanding", "No insights"],
                "1": ["Very superficial", "Shows minimal understanding", "No insights"],
                "0": ["No analysis", "No understanding demonstrated", "No response"]
            },
            "relevance": {
                "5": ["Highly relevant to architectural design", "Clear connection to design process", "Appropriate for context"],
                "4": ["Relevant to architectural design", "Good connection to design process", "Mostly appropriate"],
                "3": ["Somewhat relevant", "Basic connection to design process", "Generally appropriate"],
                "2": ["Limited relevance", "Weak connection to design process", "Somewhat appropriate"],
                "1": ["Minimal relevance", "Very weak connection", "Not very appropriate"],
                "0": ["Not relevant", "No connection to design process", "Inappropriate"]
            },
            "innovation": {
                "5": ["Highly creative and original", "Shows unique thinking", "Innovative approach"],
                "4": ["Creative and original", "Shows good thinking", "Some innovation"],
                "3": ["Some creativity", "Shows adequate thinking", "Limited innovation"],
                "2": ["Little creativity", "Shows basic thinking", "Minimal innovation"],
                "1": ["Very little creativity", "Shows minimal thinking", "No innovation"],
                "0": ["No creativity", "No original thinking", "No innovation"]
            },
            "technical_understanding": {
                "5": ["Demonstrates sophisticated technical knowledge", "Shows deep understanding of principles", "Applies knowledge effectively"],
                "4": ["Demonstrates good technical knowledge", "Shows solid understanding", "Applies knowledge well"],
                "3": ["Demonstrates adequate technical knowledge", "Shows basic understanding", "Applies knowledge adequately"],
                "2": ["Demonstrates limited technical knowledge", "Shows weak understanding", "Applies knowledge poorly"],
                "1": ["Demonstrates minimal technical knowledge", "Shows very weak understanding", "Applies knowledge very poorly"],
                "0": ["No technical knowledge demonstrated", "No understanding shown", "No knowledge application"]
            }
        }
    
    def get_questions_for_milestone(self, milestone: MilestoneType, difficulty: Optional[QuestionDifficulty] = None) -> List[Question]:
        """Get questions for a specific milestone, optionally filtered by difficulty"""
        
        if milestone not in self.questions:
            return []
        
        milestone_questions = self.questions[milestone]
        
        if difficulty:
            return [q for q in milestone_questions if q.difficulty == difficulty]
        
        return milestone_questions
    
    def get_next_question(self, milestone: MilestoneType, previous_score: float, asked_questions: List[str]) -> Optional[Question]:
        """Get the next appropriate question based on previous performance"""
        
        available_questions = self.get_questions_for_milestone(milestone)
        
        # Filter out already asked questions
        available_questions = [q for q in available_questions if q.id not in asked_questions]
        
        if not available_questions:
            return None
        
        # Select difficulty based on previous score
        if previous_score >= 4.0:
            # High performer - challenge with harder questions
            difficulty_priority = [QuestionDifficulty.EVALUATIVE, QuestionDifficulty.SYNTHETIC, QuestionDifficulty.ANALYTICAL, QuestionDifficulty.BASIC]
        elif previous_score >= 3.0:
            # Medium performer - build on strengths
            difficulty_priority = [QuestionDifficulty.ANALYTICAL, QuestionDifficulty.SYNTHETIC, QuestionDifficulty.BASIC, QuestionDifficulty.EVALUATIVE]
        else:
            # Low performer - reinforce basics
            difficulty_priority = [QuestionDifficulty.BASIC, QuestionDifficulty.ANALYTICAL, QuestionDifficulty.SYNTHETIC, QuestionDifficulty.EVALUATIVE]
        
        # Find the best available question
        for difficulty in difficulty_priority:
            for question in available_questions:
                if question.difficulty == difficulty:
                    return question
        
        # Fallback to any available question
        return available_questions[0] if available_questions else None
    
    def grade_response(self, question: Question, response: str) -> GradingResult:
        """Grade a student response to a specific question"""
        
        # This is a simplified grading system - in practice, this could use AI analysis
        # For now, we'll use keyword matching and response length as proxies
        
        response_lower = response.lower()
        response_words = len(response.split())
        
        # Calculate completeness based on keyword coverage
        keyword_matches = sum(1 for keyword in question.keywords if keyword in response_lower)
        completeness_score = min(5.0, (keyword_matches / len(question.keywords)) * 5.0)
        
        # Calculate depth based on response length and complexity
        depth_score = min(5.0, (response_words / 50.0) * 5.0)  # 50 words = 5.0 score
        
        # Calculate relevance based on architectural terms
        arch_terms = ["design", "space", "building", "site", "program", "function", "form", "structure", "material", "light", "circulation"]
        arch_term_matches = sum(1 for term in arch_terms if term in response_lower)
        relevance_score = min(5.0, (arch_term_matches / len(arch_terms)) * 5.0)
        
        # Calculate innovation (simplified - could be enhanced with AI analysis)
        innovation_score = 3.0  # Default middle score
        
        # Calculate technical understanding
        technical_score = min(5.0, (completeness_score + relevance_score) / 2.0)
        
        # Calculate overall score
        overall_score = (completeness_score + depth_score + relevance_score + innovation_score + technical_score) / 5.0
        
        # Generate feedback
        strengths = []
        weaknesses = []
        recommendations = []
        
        if completeness_score >= 4.0:
            strengths.append("Comprehensive coverage of the topic")
        elif completeness_score <= 2.0:
            weaknesses.append("Incomplete coverage of key aspects")
            recommendations.append("Consider addressing all aspects mentioned in the question")
        
        if depth_score >= 4.0:
            strengths.append("Detailed and thoughtful analysis")
        elif depth_score <= 2.0:
            weaknesses.append("Superficial analysis")
            recommendations.append("Provide more detailed explanations and reasoning")
        
        if relevance_score >= 4.0:
            strengths.append("Strong connection to architectural design")
        elif relevance_score <= 2.0:
            weaknesses.append("Limited connection to architectural design")
            recommendations.append("Focus more on architectural implications and design decisions")
        
        if innovation_score >= 4.0:
            strengths.append("Creative and original thinking")
        elif innovation_score <= 2.0:
            weaknesses.append("Limited creative thinking")
            recommendations.append("Consider more innovative approaches and unique solutions")
        
        if technical_score >= 4.0:
            strengths.append("Good technical understanding")
        elif technical_score <= 2.0:
            weaknesses.append("Limited technical understanding")
            recommendations.append("Strengthen your understanding of architectural principles")
        
        return GradingResult(
            completeness=completeness_score,
            depth=depth_score,
            relevance=relevance_score,
            innovation=innovation_score,
            technical_understanding=technical_score,
            overall_score=overall_score,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        ) 