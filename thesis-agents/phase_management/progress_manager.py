"""
Progress Manager for Design Phase Milestones
Tracks milestone completion, manages assessment profiles, and calculates meaningful progress
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import numpy as np

from .milestone_questions import MilestoneType, Question, GradingResult

@dataclass
class MilestoneAssessment:
    """Assessment data for a specific milestone"""
    milestone: MilestoneType
    questions_asked: List[str] = field(default_factory=list)
    responses: Dict[str, str] = field(default_factory=dict)
    grades: Dict[str, GradingResult] = field(default_factory=dict)
    average_score: float = 0.0
    completion_percentage: float = 0.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    is_complete: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class PhaseProgress:
    """Progress data for a design phase"""
    phase_name: str
    milestones: Dict[MilestoneType, MilestoneAssessment] = field(default_factory=dict)
    overall_progress: float = 0.0
    phase_weight: float = 0.0
    is_complete: bool = False
    next_milestone: Optional[MilestoneType] = None
    phase_recommendations: List[str] = field(default_factory=list)

@dataclass
class StudentAssessmentProfile:
    """Complete assessment profile for a student"""
    student_id: str
    project_name: str
    current_phase: str = "ideation"
    phases: Dict[str, PhaseProgress] = field(default_factory=dict)
    overall_progress: float = 0.0
    total_assessment_score: float = 0.0
    project_strengths: List[str] = field(default_factory=list)
    project_weaknesses: List[str] = field(default_factory=list)
    improvement_recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class ProgressManager:
    """Manages progress tracking and assessment for design phases"""
    
    def __init__(self):
        self.phase_structure = self._initialize_phase_structure()
        self.milestone_weights = self._initialize_milestone_weights()
        self.assessment_profiles: Dict[str, StudentAssessmentProfile] = {}
    
    def _initialize_phase_structure(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the phase structure with milestones and weights"""
        
        return {
            "ideation": {
                "weight": 0.25,  # 25% of total project
                "milestones": [
                    MilestoneType.SITE_ANALYSIS,
                    MilestoneType.PROGRAM_REQUIREMENTS,
                    MilestoneType.CONCEPT_DEVELOPMENT
                ],
                "description": "Concept development and problem framing",
                "exit_criteria": [
                    "Clear design concept established",
                    "Program requirements defined",
                    "Site analysis completed"
                ]
            },
            "visualization": {
                "weight": 0.35,  # 35% of total project
                "milestones": [
                    MilestoneType.SPATIAL_ORGANIZATION,
                    MilestoneType.CIRCULATION_DESIGN,
                    MilestoneType.FORM_DEVELOPMENT,
                    MilestoneType.LIGHTING_STRATEGY
                ],
                "description": "Spatial development and form exploration",
                "exit_criteria": [
                    "Spatial organization established",
                    "Circulation patterns defined",
                    "Form development explored",
                    "Lighting strategy developed"
                ]
            },
            "materialization": {
                "weight": 0.30,  # 30% of total project
                "milestones": [
                    MilestoneType.CONSTRUCTION_SYSTEMS,
                    MilestoneType.MATERIAL_SELECTION,
                    MilestoneType.TECHNICAL_DETAILS
                ],
                "description": "Technical development and implementation",
                "exit_criteria": [
                    "Construction systems selected",
                    "Material palette defined",
                    "Technical details developed"
                ]
            },
            "completion": {
                "weight": 0.10,  # 10% of total project
                "milestones": [
                    MilestoneType.PRESENTATION_PREP,
                    MilestoneType.DOCUMENTATION
                ],
                "description": "Final refinement and presentation",
                "exit_criteria": [
                    "Presentation materials prepared",
                    "Documentation completed"
                ]
            }
        }
    
    def _initialize_milestone_weights(self) -> Dict[MilestoneType, float]:
        """Initialize weights for individual milestones within phases"""
        
        return {
            # Ideation phase milestones
            MilestoneType.SITE_ANALYSIS: 0.4,  # 40% of ideation phase
            MilestoneType.PROGRAM_REQUIREMENTS: 0.35,  # 35% of ideation phase
            MilestoneType.CONCEPT_DEVELOPMENT: 0.25,  # 25% of ideation phase
            
            # Visualization phase milestones
            MilestoneType.SPATIAL_ORGANIZATION: 0.3,  # 30% of visualization phase
            MilestoneType.CIRCULATION_DESIGN: 0.25,  # 25% of visualization phase
            MilestoneType.FORM_DEVELOPMENT: 0.25,  # 25% of visualization phase
            MilestoneType.LIGHTING_STRATEGY: 0.2,  # 20% of visualization phase
            
            # Materialization phase milestones
            MilestoneType.CONSTRUCTION_SYSTEMS: 0.4,  # 40% of materialization phase
            MilestoneType.MATERIAL_SELECTION: 0.35,  # 35% of materialization phase
            MilestoneType.TECHNICAL_DETAILS: 0.25,  # 25% of materialization phase
            
            # Completion phase milestones
            MilestoneType.PRESENTATION_PREP: 0.6,  # 60% of completion phase
            MilestoneType.DOCUMENTATION: 0.4,  # 40% of completion phase
        }
    
    def create_assessment_profile(self, student_id: str, project_name: str) -> StudentAssessmentProfile:
        """Create a new assessment profile for a student"""
        
        profile = StudentAssessmentProfile(
            student_id=student_id,
            project_name=project_name
        )
        
        # Initialize phases
        for phase_name, phase_data in self.phase_structure.items():
            phase_progress = PhaseProgress(
                phase_name=phase_name,
                phase_weight=phase_data["weight"]
            )
            
            # Initialize milestones for this phase
            for milestone in phase_data["milestones"]:
                phase_progress.milestones[milestone] = MilestoneAssessment(milestone=milestone)
            
            profile.phases[phase_name] = phase_progress
        
        self.assessment_profiles[student_id] = profile
        return profile
    
    def get_assessment_profile(self, student_id: str) -> Optional[StudentAssessmentProfile]:
        """Get an existing assessment profile"""
        return self.assessment_profiles.get(student_id)
    
    def record_response(self, student_id: str, milestone: MilestoneType, 
                       question_id: str, response: str, grade: GradingResult) -> None:
        """Record a student response and grade for a milestone"""
        
        profile = self.get_assessment_profile(student_id)
        if not profile:
            raise ValueError(f"No assessment profile found for student {student_id}")
        
        # Find which phase contains this milestone
        target_phase = None
        for phase_name, phase_data in self.phase_structure.items():
            if milestone in phase_data["milestones"]:
                target_phase = phase_name
                break
        
        if not target_phase:
            raise ValueError(f"Milestone {milestone} not found in any phase")
        
        # Update the milestone assessment
        milestone_assessment = profile.phases[target_phase].milestones[milestone]
        milestone_assessment.questions_asked.append(question_id)
        milestone_assessment.responses[question_id] = response
        milestone_assessment.grades[question_id] = grade
        milestone_assessment.last_updated = datetime.now()
        
        # Recalculate milestone progress
        self._update_milestone_progress(milestone_assessment)
        
        # Update phase progress
        self._update_phase_progress(profile.phases[target_phase])
        
        # Update overall progress
        self._update_overall_progress(profile)
        
        # Update profile timestamp
        profile.last_updated = datetime.now()
    
    def _update_milestone_progress(self, milestone_assessment: MilestoneAssessment) -> None:
        """Update progress for a specific milestone"""
        
        if not milestone_assessment.grades:
            return
        
        # Calculate average score
        scores = [grade.overall_score for grade in milestone_assessment.grades.values()]
        milestone_assessment.average_score = np.mean(scores)
        
        # Determine completion percentage based on score and number of questions
        # A milestone is considered complete if:
        # 1. Average score >= 3.5/5.0 (70%)
        # 2. At least 2 questions have been answered
        if len(scores) >= 2 and milestone_assessment.average_score >= 3.5:
            milestone_assessment.completion_percentage = 100.0
            milestone_assessment.is_complete = True
        else:
            # Partial completion based on score and question count
            score_factor = milestone_assessment.average_score / 5.0
            question_factor = min(len(scores) / 3.0, 1.0)  # Assume 3 questions per milestone
            milestone_assessment.completion_percentage = (score_factor * question_factor) * 100.0
            milestone_assessment.is_complete = False
        
        # Aggregate strengths, weaknesses, and recommendations
        all_strengths = []
        all_weaknesses = []
        all_recommendations = []
        
        for grade in milestone_assessment.grades.values():
            all_strengths.extend(grade.strengths)
            all_weaknesses.extend(grade.weaknesses)
            all_recommendations.extend(grade.recommendations)
        
        # Remove duplicates and keep most common
        milestone_assessment.strengths = list(set(all_strengths))[:3]  # Top 3 strengths
        milestone_assessment.weaknesses = list(set(all_weaknesses))[:3]  # Top 3 weaknesses
        milestone_assessment.recommendations = list(set(all_recommendations))[:3]  # Top 3 recommendations
    
    def _update_phase_progress(self, phase_progress: PhaseProgress) -> None:
        """Update progress for a specific phase"""
        
        total_weighted_progress = 0.0
        completed_milestones = 0
        total_milestones = len(phase_progress.milestones)
        
        for milestone, assessment in phase_progress.milestones.items():
            milestone_weight = self.milestone_weights.get(milestone, 1.0)
            weighted_progress = (assessment.completion_percentage / 100.0) * milestone_weight
            total_weighted_progress += weighted_progress
            
            if assessment.is_complete:
                completed_milestones += 1
        
        # Calculate overall phase progress
        phase_progress.overall_progress = total_weighted_progress * 100.0
        
        # Determine if phase is complete (all milestones complete)
        phase_progress.is_complete = completed_milestones == total_milestones
        
        # Determine next milestone
        if not phase_progress.is_complete:
            for milestone, assessment in phase_progress.milestones.items():
                if not assessment.is_complete:
                    phase_progress.next_milestone = milestone
                    break
        
        # Generate phase recommendations
        phase_progress.phase_recommendations = self._generate_phase_recommendations(phase_progress)
    
    def _update_overall_progress(self, profile: StudentAssessmentProfile) -> None:
        """Update overall project progress"""
        
        total_weighted_progress = 0.0
        total_assessment_score = 0.0
        total_milestones = 0
        
        for phase_name, phase_progress in profile.phases.items():
            phase_weight = self.phase_structure[phase_name]["weight"]
            weighted_progress = (phase_progress.overall_progress / 100.0) * phase_weight
            total_weighted_progress += weighted_progress
            
            # Calculate assessment score for this phase
            phase_scores = []
            for assessment in phase_progress.milestones.values():
                if assessment.average_score > 0:
                    phase_scores.append(assessment.average_score)
                    total_milestones += 1
            
            if phase_scores:
                phase_assessment_score = np.mean(phase_scores)
                total_assessment_score += phase_assessment_score * phase_weight
        
        profile.overall_progress = total_weighted_progress * 100.0
        profile.total_assessment_score = total_assessment_score
        
        # Determine current phase
        for phase_name, phase_progress in profile.phases.items():
            if not phase_progress.is_complete:
                profile.current_phase = phase_name
                break
            else:
                profile.current_phase = phase_name  # Will be the last completed phase
        
        # Generate project-level insights
        self._generate_project_insights(profile)
    
    def _generate_phase_recommendations(self, phase_progress: PhaseProgress) -> List[str]:
        """Generate recommendations for a specific phase"""
        
        recommendations = []
        
        if phase_progress.overall_progress < 50:
            recommendations.append("Focus on completing the basic milestones before moving to advanced topics")
        
        # Phase-specific recommendations
        if phase_progress.phase_name == "ideation":
            if phase_progress.overall_progress < 75:
                recommendations.append("Strengthen your concept development and site analysis")
        elif phase_progress.phase_name == "visualization":
            if phase_progress.overall_progress < 75:
                recommendations.append("Develop more detailed spatial organization and circulation patterns")
        elif phase_progress.phase_name == "materialization":
            if phase_progress.overall_progress < 75:
                recommendations.append("Focus on technical details and material selection")
        
        # Add milestone-specific recommendations
        for milestone, assessment in phase_progress.milestones.items():
            if not assessment.is_complete and assessment.recommendations:
                recommendations.extend(assessment.recommendations[:2])  # Top 2 recommendations per milestone
        
        return list(set(recommendations))[:5]  # Top 5 unique recommendations
    
    def _generate_project_insights(self, profile: StudentAssessmentProfile) -> None:
        """Generate project-level strengths, weaknesses, and recommendations"""
        
        all_strengths = []
        all_weaknesses = []
        all_recommendations = []
        
        for phase_progress in profile.phases.values():
            for assessment in phase_progress.milestones.values():
                all_strengths.extend(assessment.strengths)
                all_weaknesses.extend(assessment.weaknesses)
                all_recommendations.extend(assessment.recommendations)
        
        # Aggregate and prioritize insights
        profile.project_strengths = self._prioritize_insights(all_strengths, 5)
        profile.project_weaknesses = self._prioritize_insights(all_weaknesses, 5)
        profile.improvement_recommendations = self._prioritize_insights(all_recommendations, 5)
    
    def _prioritize_insights(self, insights: List[str], max_count: int) -> List[str]:
        """Prioritize insights by frequency and importance"""
        
        if not insights:
            return []
        
        # Count frequency
        insight_counts = {}
        for insight in insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1
        
        # Sort by frequency (descending) and return top insights
        sorted_insights = sorted(insight_counts.items(), key=lambda x: x[1], reverse=True)
        return [insight for insight, count in sorted_insights[:max_count]]
    
    def get_next_question_for_student(self, student_id: str, milestone: MilestoneType) -> Optional[str]:
        """Get the next question for a student based on their progress"""
        
        profile = self.get_assessment_profile(student_id)
        if not profile:
            return None
        
        # Find the milestone assessment
        milestone_assessment = None
        for phase_progress in profile.phases.values():
            if milestone in phase_progress.milestones:
                milestone_assessment = phase_progress.milestones[milestone]
                break
        
        if not milestone_assessment:
            return None
        
        # If milestone is complete, suggest moving to next milestone
        if milestone_assessment.is_complete:
            return "milestone_complete"
        
        # Return the next question ID (this would be determined by the question bank)
        return "next_question_id"
    
    def generate_assessment_report(self, student_id: str) -> Dict[str, Any]:
        """Generate a comprehensive assessment report for a student"""
        
        profile = self.get_assessment_profile(student_id)
        if not profile:
            return {"error": "No assessment profile found"}
        
        report = {
            "student_id": profile.student_id,
            "project_name": profile.project_name,
            "overall_progress": profile.overall_progress,
            "current_phase": profile.current_phase,
            "total_assessment_score": profile.total_assessment_score,
            "phases": {},
            "project_strengths": profile.project_strengths,
            "project_weaknesses": profile.project_weaknesses,
            "improvement_recommendations": profile.improvement_recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        # Add phase details
        for phase_name, phase_progress in profile.phases.items():
            phase_report = {
                "progress": phase_progress.overall_progress,
                "is_complete": phase_progress.is_complete,
                "next_milestone": phase_progress.next_milestone.value if phase_progress.next_milestone else None,
                "recommendations": phase_progress.phase_recommendations,
                "milestones": {}
            }
            
            for milestone, assessment in phase_progress.milestones.items():
                milestone_report = {
                    "completion_percentage": assessment.completion_percentage,
                    "average_score": assessment.average_score,
                    "is_complete": assessment.is_complete,
                    "strengths": assessment.strengths,
                    "weaknesses": assessment.weaknesses,
                    "recommendations": assessment.recommendations
                }
                phase_report["milestones"][milestone.value] = milestone_report
            
            report["phases"][phase_name] = phase_report
        
        return report
    
    def save_assessment_profile(self, student_id: str, filepath: str) -> None:
        """Save assessment profile to file"""
        
        profile = self.get_assessment_profile(student_id)
        if not profile:
            raise ValueError(f"No assessment profile found for student {student_id}")
        
        # Convert to serializable format
        profile_data = {
            "student_id": profile.student_id,
            "project_name": profile.project_name,
            "current_phase": profile.current_phase,
            "overall_progress": profile.overall_progress,
            "total_assessment_score": profile.total_assessment_score,
            "project_strengths": profile.project_strengths,
            "project_weaknesses": profile.project_weaknesses,
            "improvement_recommendations": profile.improvement_recommendations,
            "created_at": profile.created_at.isoformat(),
            "last_updated": profile.last_updated.isoformat(),
            "phases": {}
        }
        
        # Add phase data
        for phase_name, phase_progress in profile.phases.items():
            phase_data = {
                "phase_name": phase_progress.phase_name,
                "overall_progress": phase_progress.overall_progress,
                "phase_weight": phase_progress.phase_weight,
                "is_complete": phase_progress.is_complete,
                "next_milestone": phase_progress.next_milestone.value if phase_progress.next_milestone else None,
                "phase_recommendations": phase_progress.phase_recommendations,
                "milestones": {}
            }
            
            for milestone, assessment in phase_progress.milestones.items():
                milestone_data = {
                    "milestone": assessment.milestone.value,
                    "questions_asked": assessment.questions_asked,
                    "responses": assessment.responses,
                    "average_score": assessment.average_score,
                    "completion_percentage": assessment.completion_percentage,
                    "strengths": assessment.strengths,
                    "weaknesses": assessment.weaknesses,
                    "recommendations": assessment.recommendations,
                    "is_complete": assessment.is_complete,
                    "last_updated": assessment.last_updated.isoformat()
                }
                phase_data["milestones"][milestone.value] = milestone_data
            
            profile_data["phases"][phase_name] = phase_data
        
        with open(filepath, 'w') as f:
            json.dump(profile_data, f, indent=2)
    
    def load_assessment_profile(self, student_id: str, filepath: str) -> StudentAssessmentProfile:
        """Load assessment profile from file"""
        
        with open(filepath, 'r') as f:
            profile_data = json.load(f)
        
        # Reconstruct the profile
        profile = StudentAssessmentProfile(
            student_id=profile_data["student_id"],
            project_name=profile_data["project_name"],
            current_phase=profile_data["current_phase"],
            overall_progress=profile_data["overall_progress"],
            total_assessment_score=profile_data["total_assessment_score"],
            project_strengths=profile_data["project_strengths"],
            project_weaknesses=profile_data["project_weaknesses"],
            improvement_recommendations=profile_data["improvement_recommendations"],
            created_at=datetime.fromisoformat(profile_data["created_at"]),
            last_updated=datetime.fromisoformat(profile_data["last_updated"])
        )
        
        # Reconstruct phases
        for phase_name, phase_data in profile_data["phases"].items():
            phase_progress = PhaseProgress(
                phase_name=phase_data["phase_name"],
                overall_progress=phase_data["overall_progress"],
                phase_weight=phase_data["phase_weight"],
                is_complete=phase_data["is_complete"],
                next_milestone=MilestoneType(phase_data["next_milestone"]) if phase_data["next_milestone"] else None,
                phase_recommendations=phase_data["phase_recommendations"]
            )
            
            # Reconstruct milestones
            for milestone_name, milestone_data in phase_data["milestones"].items():
                milestone = MilestoneType(milestone_data["milestone"])
                assessment = MilestoneAssessment(
                    milestone=milestone,
                    questions_asked=milestone_data["questions_asked"],
                    responses=milestone_data["responses"],
                    average_score=milestone_data["average_score"],
                    completion_percentage=milestone_data["completion_percentage"],
                    strengths=milestone_data["strengths"],
                    weaknesses=milestone_data["weaknesses"],
                    recommendations=milestone_data["recommendations"],
                    is_complete=milestone_data["is_complete"],
                    last_updated=datetime.fromisoformat(milestone_data["last_updated"])
                )
                phase_progress.milestones[milestone] = assessment
            
            profile.phases[phase_name] = phase_progress
        
        self.assessment_profiles[student_id] = profile
        return profile 