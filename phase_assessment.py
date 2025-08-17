"""
Phase Assessment Module
Handles phase-specific assessment criteria and grading
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PhaseAssessment:
    """Assessment results for a specific phase"""
    score: float  # 0-100
    competencies: Dict[str, float]  # Specific competency scores
    strengths: List[str]
    areas_for_improvement: List[str]
    completed_questions: int
    total_questions: int
    timestamp: datetime = datetime.now()

class PhaseAssessmentSystem:
    """Manages phase-specific assessment criteria and grading"""
    
    def __init__(self):
        # Phase-specific competencies
        self.phase_competencies = {
            "ideation": [
                "problem_framing",
                "contextual_awareness",
                "creative_thinking"
            ],
            "visualization": [
                "spatial_reasoning",
                "form_development",
                "circulation_design"
            ],
            "materialization": [
                "technical_understanding",
                "material_selection",
                "constructability"
            ]
        }
        
        # Questions per phase
        self.phase_questions = {
            "ideation": [
                "What are the key challenges and opportunities in the project context?",
                "How does your concept address the user needs and site constraints?",
                "What precedents or references inform your approach?",
                "How might your initial ideas evolve to better serve the project goals?",
                "What assumptions are you making that should be validated?"
            ],
            "visualization": [
                "How does your spatial organization respond to the program requirements?",
                "What is the primary circulation strategy and why?",
                "How does the form development reflect the project's purpose?",
                "How do light and views influence the spatial experience?",
                "What are the key spatial relationships that drive your design?"
            ],
            "materialization": [
                "What materials are most appropriate for your design and why?",
                "How do your technical solutions support the design intent?",
                "What construction methods will be used and why?",
                "How have you addressed sustainability in your material choices?",
                "What are the key technical challenges and your solutions?"
            ]
        }
        
        # Phase completion requirements
        self.phase_requirements = {
            "ideation": {
                "min_score": 70,
                "min_questions": 4
            },
            "visualization": {
                "min_score": 75,
                "min_questions": 4
            },
            "materialization": {
                "min_score": 80,
                "min_questions": 4
            }
        }
    
    def assess_response(self, phase: str, response: str, question_idx: int) -> Tuple[float, Dict[str, float], List[str], List[str]]:
        """
        Assess a single response within a phase
        Returns: (score, competency_scores, strengths, improvements)
        """
        score = 0
        competency_scores = {}
        strengths = []
        improvements = []
        
        # Assess based on phase-specific criteria
        if phase == "ideation":
            score, competency_scores, strengths, improvements = self._assess_ideation(response)
        elif phase == "visualization":
            score, competency_scores, strengths, improvements = self._assess_visualization(response)
        elif phase == "materialization":
            score, competency_scores, strengths, improvements = self._assess_materialization(response)
        
        return score, competency_scores, strengths, improvements
    
    def check_phase_completion(self, phase: str, assessments: List[PhaseAssessment]) -> bool:
        """Check if phase completion requirements are met"""
        requirements = self.phase_requirements[phase]
        
        # Calculate average score
        scores = [a.score for a in assessments]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Check requirements
        meets_min_score = avg_score >= requirements["min_score"]
        meets_min_questions = len(assessments) >= requirements["min_questions"]
        
        return meets_min_score and meets_min_questions
    
    def _assess_ideation(self, response: str) -> Tuple[float, Dict[str, float], List[str], List[str]]:
        """Assess ideation phase response"""
        # Initialize scoring
        competency_scores = {
            "problem_framing": 0,
            "contextual_awareness": 0,
            "creative_thinking": 0
        }
        strengths = []
        improvements = []
        
        # Problem framing assessment
        if any(kw in response.lower() for kw in ["challenge", "problem", "need", "requirement"]):
            competency_scores["problem_framing"] += 25
            if any(kw in response.lower() for kw in ["analysis", "strategy", "approach"]):
                competency_scores["problem_framing"] += 25
        
        # Contextual awareness assessment
        if any(kw in response.lower() for kw in ["context", "site", "environment", "community"]):
            competency_scores["contextual_awareness"] += 25
            if any(kw in response.lower() for kw in ["relationship", "impact", "integration"]):
                competency_scores["contextual_awareness"] += 25
        
        # Creative thinking assessment
        if any(kw in response.lower() for kw in ["innovative", "creative", "unique", "alternative"]):
            competency_scores["creative_thinking"] += 25
            if any(kw in response.lower() for kw in ["possibility", "potential", "explore"]):
                competency_scores["creative_thinking"] += 25
        
        # Calculate overall score
        score = sum(competency_scores.values()) / len(competency_scores)
        
        # Generate feedback
        for comp, score in competency_scores.items():
            if score >= 75:
                strengths.append(f"Strong {comp.replace('_', ' ')}")
            elif score <= 50:
                improvements.append(f"Could improve {comp.replace('_', ' ')}")
        
        return score, competency_scores, strengths, improvements
    
    def _assess_visualization(self, response: str) -> Tuple[float, Dict[str, float], List[str], List[str]]:
        """Assess visualization phase response"""
        competency_scores = {
            "spatial_reasoning": 0,
            "form_development": 0,
            "circulation_design": 0
        }
        strengths = []
        improvements = []
        
        # Spatial reasoning assessment
        if any(kw in response.lower() for kw in ["space", "spatial", "organization", "layout"]):
            competency_scores["spatial_reasoning"] += 25
            if any(kw in response.lower() for kw in ["relationship", "hierarchy", "connection"]):
                competency_scores["spatial_reasoning"] += 25
        
        # Form development assessment
        if any(kw in response.lower() for kw in ["form", "shape", "volume", "massing"]):
            competency_scores["form_development"] += 25
            if any(kw in response.lower() for kw in ["development", "evolution", "strategy"]):
                competency_scores["form_development"] += 25
        
        # Circulation design assessment
        if any(kw in response.lower() for kw in ["circulation", "flow", "movement", "path"]):
            competency_scores["circulation_design"] += 25
            if any(kw in response.lower() for kw in ["sequence", "experience", "connection"]):
                competency_scores["circulation_design"] += 25
        
        # Calculate overall score
        score = sum(competency_scores.values()) / len(competency_scores)
        
        # Generate feedback
        for comp, score in competency_scores.items():
            if score >= 75:
                strengths.append(f"Strong {comp.replace('_', ' ')}")
            elif score <= 50:
                improvements.append(f"Could improve {comp.replace('_', ' ')}")
        
        return score, competency_scores, strengths, improvements
    
    def _assess_materialization(self, response: str) -> Tuple[float, Dict[str, float], List[str], List[str]]:
        """Assess materialization phase response"""
        competency_scores = {
            "technical_understanding": 0,
            "material_selection": 0,
            "constructability": 0
        }
        strengths = []
        improvements = []
        
        # Technical understanding assessment
        if any(kw in response.lower() for kw in ["technical", "system", "detail", "assembly"]):
            competency_scores["technical_understanding"] += 25
            if any(kw in response.lower() for kw in ["integration", "performance", "solution"]):
                competency_scores["technical_understanding"] += 25
        
        # Material selection assessment
        if any(kw in response.lower() for kw in ["material", "finish", "texture", "surface"]):
            competency_scores["material_selection"] += 25
            if any(kw in response.lower() for kw in ["appropriate", "sustainable", "durable"]):
                competency_scores["material_selection"] += 25
        
        # Constructability assessment
        if any(kw in response.lower() for kw in ["construct", "build", "assembly", "fabrication"]):
            competency_scores["constructability"] += 25
            if any(kw in response.lower() for kw in ["method", "process", "sequence"]):
                competency_scores["constructability"] += 25
        
        # Calculate overall score
        score = sum(competency_scores.values()) / len(competency_scores)
        
        # Generate feedback
        for comp, score in competency_scores.items():
            if score >= 75:
                strengths.append(f"Strong {comp.replace('_', ' ')}")
            elif score <= 50:
                improvements.append(f"Could improve {comp.replace('_', ' ')}")
        
        return score, competency_scores, strengths, improvements
