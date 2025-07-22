#!/usr/bin/env python3
"""
Design Thinking App for Architectural Design
Transforms the architectural analysis system into an interactive design thinking process
that guides users through their design decisions rather than providing direct answers.
"""

import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime
import threading
import queue
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Import our new unified engine
from core.unified_engine import UnifiedArchitecturalEngine

class DesignPhase(Enum):
    """Design thinking phases"""
    DISCOVER = "discover"
    DEFINE = "define"
    IDEATE = "ideate"
    PROTOTYPE = "prototype"
    TEST = "test"
    REFLECT = "reflect"

class QuestionType(Enum):
    """Types of questions to guide design thinking"""
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    REFLECTION = "reflection"

@dataclass
class DesignQuestion:
    """A question to guide the user's design thinking"""
    id: str
    phase: DesignPhase
    type: QuestionType
    question: str
    context: str
    hints: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    related_elements: List[str] = field(default_factory=list)
    user_response: Optional[str] = None
    timestamp: Optional[datetime] = None

@dataclass
class DesignSession:
    """A design thinking session"""
    session_id: str
    project_name: str
    image_path: str
    current_phase: DesignPhase
    questions: List[DesignQuestion] = field(default_factory=list)
    user_responses: Dict[str, str] = field(default_factory=dict)
    design_decisions: List[Dict[str, Any]] = field(default_factory=list)
    sketches: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class DesignThinkingApp:
    """
    Interactive design thinking app that guides users through architectural design decisions
    """
    
    def __init__(self, config_path: str = "design_thinking_config.json"):
        """
        Initialize the design thinking app
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize unified engine for analysis
        self.unified_engine = UnifiedArchitecturalEngine()
        
        # Session management
        self.current_session: Optional[DesignSession] = None
        self.sessions: Dict[str, DesignSession] = {}
        
        # Question database
        self.question_database = self._initialize_question_database()
        
        # Analysis cache
        self.analysis_cache = {}
        
        print("🧠 Design Thinking App initialized")
        print("   Focus: Guiding users through design decisions")
        print("   Approach: Question-based learning")
    
    def _get_analysis_for_question(self, question_id: str) -> Dict[str, Any]:
        """Get relevant analysis data for a specific question"""
        if not self.current_session:
            return {"error": "No active session"}
        
        # Use the unified engine to get analysis
        try:
            analysis_results = self.unified_engine.analyze_architecture(
                self.current_session.image_path
            )
            return analysis_results
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'phases': {
                    'discover': {
                        'description': 'Understand the context and constraints',
                        'duration_minutes': 15,
                        'questions_per_phase': 5
                    },
                    'define': {
                        'description': 'Identify key problems and opportunities',
                        'duration_minutes': 10,
                        'questions_per_phase': 3
                    },
                    'ideate': {
                        'description': 'Generate creative solutions',
                        'duration_minutes': 20,
                        'questions_per_phase': 4
                    },
                    'prototype': {
                        'description': 'Create and test solutions',
                        'duration_minutes': 25,
                        'questions_per_phase': 4
                    },
                    'test': {
                        'description': 'Evaluate and refine solutions',
                        'duration_minutes': 15,
                        'questions_per_phase': 3
                    },
                    'reflect': {
                        'description': 'Learn from the process',
                        'duration_minutes': 10,
                        'questions_per_phase': 2
                    }
                },
                'interaction': {
                    'enable_hints': True,
                    'enable_follow_up': True,
                    'enable_sketching': True,
                    'enable_analysis': True
                },
                'analysis': {
                    'confidence_threshold': 0.5,
                    'enable_spatial_analysis': True,
                    'enable_critique': False  # We don't want direct critique
                }
            }
    
    def _initialize_question_database(self) -> Dict[DesignPhase, List[DesignQuestion]]:
        """Initialize the database of design thinking questions"""
        questions = {
            DesignPhase.DISCOVER: [
                DesignQuestion(
                    id="discover_001",
                    phase=DesignPhase.DISCOVER,
                    type=QuestionType.OBSERVATION,
                    question="What do you notice about the spatial organization of this design?",
                    context="Look at how spaces are arranged and connected",
                    hints=["Consider circulation patterns", "Look at room adjacencies", "Think about public vs private spaces"],
                    follow_up_questions=["How does this organization affect user experience?", "What are the strengths of this layout?"],
                    related_elements=["walls", "doors", "corridors", "rooms"]
                ),
                DesignQuestion(
                    id="discover_002",
                    phase=DesignPhase.DISCOVER,
                    type=QuestionType.OBSERVATION,
                    question="What environmental factors might influence this design?",
                    context="Consider natural light, ventilation, and site conditions",
                    hints=["Look for windows and openings", "Consider orientation", "Think about climate"],
                    follow_up_questions=["How could these factors be better addressed?", "What opportunities exist?"],
                    related_elements=["windows", "openings", "orientation"]
                ),
                DesignQuestion(
                    id="discover_003",
                    phase=DesignPhase.DISCOVER,
                    type=QuestionType.ANALYSIS,
                    question="What are the primary functions this space needs to serve?",
                    context="Identify the main activities and users",
                    hints=["List the key activities", "Consider different user groups", "Think about flexibility"],
                    follow_up_questions=["Are all functions adequately supported?", "What functions might be missing?"],
                    related_elements=["rooms", "spaces", "functions"]
                )
            ],
            DesignPhase.DEFINE: [
                DesignQuestion(
                    id="define_001",
                    phase=DesignPhase.DEFINE,
                    type=QuestionType.SYNTHESIS,
                    question="What is the most critical design challenge you're facing?",
                    context="Based on your observations, identify the key problem",
                    hints=["Consider user needs", "Think about constraints", "Prioritize issues"],
                    follow_up_questions=["Why is this the most important challenge?", "What would success look like?"],
                    related_elements=["all"]
                ),
                DesignQuestion(
                    id="define_002",
                    phase=DesignPhase.DEFINE,
                    type=QuestionType.ANALYSIS,
                    question="Who are the primary users and what are their needs?",
                    context="Define your user personas and their requirements",
                    hints=["Consider accessibility", "Think about different abilities", "Include diverse perspectives"],
                    follow_up_questions=["Are there conflicting user needs?", "How can you prioritize these needs?"],
                    related_elements=["accessibility", "user_needs"]
                )
            ],
            DesignPhase.IDEATE: [
                DesignQuestion(
                    id="ideate_001",
                    phase=DesignPhase.IDEATE,
                    type=QuestionType.SYNTHESIS,
                    question="How could you reorganize the spaces to better serve the users?",
                    context="Think creatively about spatial arrangements",
                    hints=["Consider alternative layouts", "Think about adjacencies", "Explore different scales"],
                    follow_up_questions=["What are the trade-offs of each approach?", "How would this affect circulation?"],
                    related_elements=["spatial_organization", "circulation"]
                ),
                DesignQuestion(
                    id="ideate_002",
                    phase=DesignPhase.IDEATE,
                    type=QuestionType.SYNTHESIS,
                    question="What innovative solutions could address the environmental challenges?",
                    context="Explore sustainable and innovative approaches",
                    hints=["Consider passive design", "Think about renewable energy", "Explore new materials"],
                    follow_up_questions=["What are the implementation challenges?", "How would this affect the budget?"],
                    related_elements=["sustainability", "environmental"]
                )
            ],
            DesignPhase.PROTOTYPE: [
                DesignQuestion(
                    id="prototype_001",
                    phase=DesignPhase.PROTOTYPE,
                    type=QuestionType.EVALUATION,
                    question="How would you test your proposed solution?",
                    context="Design experiments to validate your ideas",
                    hints=["Consider user testing", "Think about simulations", "Plan for feedback"],
                    follow_up_questions=["What metrics would you use?", "How would you measure success?"],
                    related_elements=["testing", "validation"]
                )
            ],
            DesignPhase.TEST: [
                DesignQuestion(
                    id="test_001",
                    phase=DesignPhase.TEST,
                    type=QuestionType.EVALUATION,
                    question="What feedback would you expect from users?",
                    context="Anticipate user reactions and concerns",
                    hints=["Consider different perspectives", "Think about accessibility", "Include diverse users"],
                    follow_up_questions=["How would you address negative feedback?", "What would you change based on feedback?"],
                    related_elements=["user_feedback", "accessibility"]
                )
            ],
            DesignPhase.REFLECT: [
                DesignQuestion(
                    id="reflect_001",
                    phase=DesignPhase.REFLECT,
                    type=QuestionType.REFLECTION,
                    question="What did you learn about your design process?",
                    context="Reflect on your approach and methodology",
                    hints=["Consider your assumptions", "Think about your decision-making", "Reflect on collaboration"],
                    follow_up_questions=["How would you approach this differently next time?", "What tools or methods were most helpful?"],
                    related_elements=["process", "learning"]
                )
            ]
        }
        return questions
    
    def start_new_session(self, project_name: str, image_path: str) -> str:
        """
        Start a new design thinking session
        
        Args:
            project_name: Name of the design project
            image_path: Path to the architectural image
            
        Returns:
            str: Session ID
        """
        session_id = f"session_{int(time.time())}"
        
        self.current_session = DesignSession(
            session_id=session_id,
            project_name=project_name,
            image_path=image_path,
            current_phase=DesignPhase.DISCOVER
        )
        
        self.sessions[session_id] = self.current_session
        
        # Load the image for analysis
        self._load_image_for_session(image_path)
        
        print(f"🎯 Started new design session: {project_name}")
        print(f"   Session ID: {session_id}")
        print(f"   Current Phase: {self.current_session.current_phase.value}")
        
        return session_id
    
    def _load_image_for_session(self, image_path: str):
        """Load and prepare image for the session"""
        try:
            # Perform initial analysis using unified engine
            if self.config['analysis']['enable_spatial_analysis']:
                analysis_results = self.unified_engine.analyze_architecture(image_path)
                self.analysis_cache['full_analysis'] = analysis_results
            
            print(f"✅ Image loaded and analyzed: {Path(image_path).name}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not fully analyze image: {e}")
    
    def get_current_question(self) -> Optional[DesignQuestion]:
        """Get the current question for the user"""
        if not self.current_session:
            return None
        
        phase_questions = self.question_database.get(self.current_session.current_phase, [])
        
        # Find the next unanswered question
        for question in phase_questions:
            if question.id not in self.current_session.user_responses:
                return question
        
        return None
    
    def submit_response(self, question_id: str, response: str) -> Dict[str, Any]:
        """
        Submit a user response to a question
        
        Args:
            question_id: ID of the question being answered
            response: User's response
            
        Returns:
            dict: Feedback and next steps
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        # Find the question
        question = None
        for phase_questions in self.question_database.values():
            for q in phase_questions:
                if q.id == question_id:
                    question = q
                    break
            if question:
                break
        
        if not question:
            return {"error": "Question not found"}
        
        # Store the response
        self.current_session.user_responses[question_id] = response
        question.user_response = response
        question.timestamp = datetime.now()
        
        # Generate contextual feedback
        feedback = self._generate_contextual_feedback(question, response)
        
        # Check if phase is complete
        phase_complete = self._check_phase_completion()
        
        # Get next steps
        next_steps = self._get_next_steps(phase_complete)
        
        return {
            "feedback": feedback,
            "phase_complete": phase_complete,
            "next_steps": next_steps,
            "session_progress": self._get_session_progress()
        }
    
    def _generate_contextual_feedback(self, question: DesignQuestion, response: str) -> Dict[str, Any]:
        """Generate contextual feedback based on the user's response"""
        feedback = {
            "acknowledgment": f"Thank you for your thoughtful response about {question.context.lower()}.",
            "insights": [],
            "suggestions": [],
            "follow_up": []
        }
        
        # Analyze response based on question type
        if question.type == QuestionType.OBSERVATION:
            feedback["insights"].append("Your observations show attention to detail.")
            if len(response.split()) < 20:
                feedback["suggestions"].append("Consider adding more specific details about what you observe.")
        
        elif question.type == QuestionType.ANALYSIS:
            feedback["insights"].append("Your analysis demonstrates critical thinking.")
            if "because" in response.lower() or "since" in response.lower():
                feedback["insights"].append("Good use of reasoning to support your analysis.")
        
        elif question.type == QuestionType.SYNTHESIS:
            feedback["insights"].append("Your synthesis shows creative problem-solving.")
            if len(question.follow_up_questions) > 0:
                feedback["follow_up"] = question.follow_up_questions[:2]  # Limit to 2 follow-ups
        
        elif question.type == QuestionType.EVALUATION:
            feedback["insights"].append("Your evaluation shows thoughtful consideration of trade-offs.")
        
        elif question.type == QuestionType.REFLECTION:
            feedback["insights"].append("Your reflection demonstrates metacognitive awareness.")
        
        # Add contextual hints if response is brief
        if len(response.split()) < 15:
            feedback["suggestions"].append("Consider expanding on your thoughts to deepen your design thinking.")
            if question.hints:
                feedback["suggestions"].append(f"Hint: {question.hints[0]}")
        
        return feedback
    
    def _check_phase_completion(self) -> bool:
        """Check if the current phase is complete"""
        if not self.current_session:
            return False
        
        phase_questions = self.question_database.get(self.current_session.current_phase, [])
        answered_questions = sum(1 for q in phase_questions if q.id in self.current_session.user_responses)
        
        return answered_questions >= len(phase_questions)
    
    def _get_next_steps(self, phase_complete: bool) -> Dict[str, Any]:
        """Get next steps for the user"""
        if not self.current_session:
            return {"error": "No active session"}
        
        if phase_complete:
            # Move to next phase
            next_phase = self._get_next_phase()
            if next_phase:
                self.current_session.current_phase = next_phase
                return {
                    "action": "phase_complete",
                    "next_phase": next_phase.value,
                    "phase_description": self.config['phases'][next_phase.value]['description'],
                    "message": f"Congratulations! You've completed the {self.current_session.current_phase.value} phase. Let's move to {next_phase.value}."
                }
            else:
                return {
                    "action": "session_complete",
                    "message": "Congratulations! You've completed the design thinking process. Let's review your journey."
                }
        else:
            # Continue with current phase
            next_question = self.get_current_question()
            if next_question:
                return {
                    "action": "continue_phase",
                    "next_question": {
                        "id": next_question.id,
                        "question": next_question.question,
                        "context": next_question.context,
                        "hints": next_question.hints if self.config['interaction']['enable_hints'] else []
                    }
                }
        
        return {"error": "Unable to determine next steps"}
    
    def _get_next_phase(self) -> Optional[DesignPhase]:
        """Get the next phase in the design thinking process"""
        phases = list(DesignPhase)
        current_index = phases.index(self.current_session.current_phase)
        
        if current_index < len(phases) - 1:
            return phases[current_index + 1]
        
        return None
    
    def _get_session_progress(self) -> Dict[str, Any]:
        """Get the current session progress"""
        if not self.current_session:
            return {"error": "No active session"}
        
        total_questions = sum(len(questions) for questions in self.question_database.values())
        answered_questions = len(self.current_session.user_responses)
        
        phase_progress = {}
        for phase in DesignPhase:
            phase_questions = self.question_database.get(phase, [])
            phase_answered = sum(1 for q in phase_questions if q.id in self.current_session.user_responses)
            phase_progress[phase.value] = {
                "total": len(phase_questions),
                "answered": phase_answered,
                "percentage": (phase_answered / len(phase_questions) * 100) if phase_questions else 0
            }
        
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "overall_progress": (answered_questions / total_questions * 100) if total_questions > 0 else 0,
            "phase_progress": phase_progress,
            "current_phase": self.current_session.current_phase.value
        }
    
    def get_contextual_analysis(self, question_id: str) -> Dict[str, Any]:
        """
        Get contextual analysis to support the user's thinking
        
        Args:
            question_id: ID of the current question
            
        Returns:
            dict: Relevant analysis data
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        # Find the question
        question = None
        for phase_questions in self.question_database.values():
            for q in phase_questions:
                if q.id == question_id:
                    question = q
                    break
            if question:
                break
        
        if not question:
            return {"error": "Question not found"}
        
        # Get analysis from unified engine
        analysis_results = self._get_analysis_for_question(question_id)
        
        if "error" in analysis_results:
            return analysis_results
        
        # Extract relevant insights based on question elements
        analysis_data = {
            "general_observations": self._get_general_observations(question),
            "analysis_summary": analysis_results.get("summary", {}),
            "detection_results": analysis_results.get("yolo_detection", {}),
            "segmentation_results": analysis_results.get("sam_segmentation", {}),
            "visual_analysis": analysis_results.get("clip_blip_analysis", {}),
            "gpt4_insights": analysis_results.get("gpt4_analysis", {}),
            "criticism": analysis_results.get("architectural_criticism", {})
        }
        
        return analysis_data
    
    def _get_general_observations(self, question: DesignQuestion) -> List[str]:
        """Get general observations that support thinking without giving answers"""
        observations = []
        
        if "circulation" in question.related_elements:
            observations.append("Consider how people move through the space")
        
        if "lighting" in question.related_elements:
            observations.append("Think about natural and artificial lighting sources")
        
        if "accessibility" in question.related_elements:
            observations.append("Consider the needs of users with different abilities")
        
        if "sustainability" in question.related_elements:
            observations.append("Environmental factors can influence design decisions")
        
        return observations
    
    def add_design_decision(self, decision: str, rationale: str, phase: DesignPhase) -> Dict[str, Any]:
        """
        Add a design decision to the session
        
        Args:
            decision: The design decision made
            rationale: Reasoning behind the decision
            phase: Phase when decision was made
            
        Returns:
            dict: Confirmation and feedback
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        design_decision = {
            "id": f"decision_{len(self.current_session.design_decisions) + 1}",
            "decision": decision,
            "rationale": rationale,
            "phase": phase.value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.current_session.design_decisions.append(design_decision)
        
        return {
            "success": True,
            "message": "Design decision recorded successfully",
            "decision_id": design_decision["id"]
        }
    
    def add_insight(self, insight: str) -> Dict[str, Any]:
        """
        Add an insight to the session
        
        Args:
            insight: The insight gained
            
        Returns:
            dict: Confirmation
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        self.current_session.insights.append({
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": "Insight recorded successfully"
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the design thinking session
        
        Returns:
            dict: Session summary
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        return {
            "session_id": self.current_session.session_id,
            "project_name": self.current_session.project_name,
            "current_phase": self.current_session.current_phase.value,
            "progress": self._get_session_progress(),
            "design_decisions": self.current_session.design_decisions,
            "insights": self.current_session.insights,
            "total_responses": len(self.current_session.user_responses),
            "session_duration": (datetime.now() - self.current_session.created_at).total_seconds() / 60
        }
    
    def export_session_report(self, output_path: str) -> Dict[str, Any]:
        """
        Export a comprehensive report of the design thinking session
        
        Args:
            output_path: Path to save the report
            
        Returns:
            dict: Export status
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        try:
            report = {
                "session_summary": self.get_session_summary(),
                "detailed_responses": {},
                "phase_analysis": {},
                "recommendations": self._generate_recommendations()
            }
            
            # Add detailed responses
            for question_id, response in self.current_session.user_responses.items():
                question = self._find_question_by_id(question_id)
                if question:
                    report["detailed_responses"][question_id] = {
                        "question": question.question,
                        "context": question.context,
                        "response": response,
                        "phase": question.phase.value,
                        "type": question.type.value
                    }
            
            # Add phase analysis
            for phase in DesignPhase:
                phase_questions = self.question_database.get(phase, [])
                phase_responses = {q.id: self.current_session.user_responses.get(q.id, "") 
                                 for q in phase_questions}
                report["phase_analysis"][phase.value] = {
                    "questions": len(phase_questions),
                    "responses": len([r for r in phase_responses.values() if r]),
                    "completion_percentage": (len([r for r in phase_responses.values() if r]) / len(phase_questions) * 100) if phase_questions else 0
                }
            
            # Save report
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str, ensure_ascii=False)
            
            return {
                "success": True,
                "message": f"Session report exported to {output_path}",
                "report_path": output_path
            }
            
        except Exception as e:
            return {
                "error": f"Failed to export report: {str(e)}"
            }
    
    def _find_question_by_id(self, question_id: str) -> Optional[DesignQuestion]:
        """Find a question by its ID"""
        for phase_questions in self.question_database.values():
            for question in phase_questions:
                if question.id == question_id:
                    return question
        return None
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on the session"""
        recommendations = []
        
        if not self.current_session:
            return recommendations
        
        # Analyze responses to generate recommendations
        responses = self.current_session.user_responses
        
        # Check for common patterns and provide recommendations
        if len(responses) < 5:
            recommendations.append("Consider spending more time in each phase to develop deeper insights")
        
        if self.current_session.current_phase == DesignPhase.REFLECT:
            recommendations.append("Continue reflecting on your design process to improve future projects")
        else:
            recommendations.append("Complete the design thinking process to gain full insights")
        
        return recommendations

def main():
    """Example usage of the design thinking app"""
    app = DesignThinkingApp()
    
    # Start a new session
    session_id = app.start_new_session(
        project_name="Residential Design Project",
        image_path="data/raw/sample_plan.jpg"
    )
    
    # Get the first question
    question = app.get_current_question()
    if question:
        print(f"\n🎯 Current Question: {question.question}")
        print(f"   Context: {question.context}")
        print(f"   Hints: {question.hints}")
        
        # Simulate user response
        response = "I notice the living room is centrally located with good access to the kitchen and bedrooms. The circulation seems logical."
        
        # Submit response
        result = app.submit_response(question.id, response)
        print(f"\n📝 Response submitted!")
        print(f"   Feedback: {result['feedback']['acknowledgment']}")
        print(f"   Insights: {result['feedback']['insights']}")
        
        # Get next steps
        print(f"\n➡️ Next Steps: {result['next_steps']['action']}")
        
        # Get session progress
        progress = app._get_session_progress()
        print(f"\n📊 Progress: {progress['overall_progress']:.1f}% complete")

if __name__ == "__main__":
    main() 