"""
Phase Integration Layer
Connects the simplified phase system with the dashboard and Streamlit session state.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .simplified_phase_system import SimplifiedPhaseSystem, DesignPhase


class PhaseIntegration:
    """Integration layer between phase system and dashboard"""
    
    def __init__(self):
        self.phase_system = SimplifiedPhaseSystem()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state for phase tracking"""
        if 'phase_session_id' not in st.session_state:
            st.session_state.phase_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if 'phase_system_initialized' not in st.session_state:
            # Create session in phase system
            self.phase_system.create_session(st.session_state.phase_session_id)
            st.session_state.phase_system_initialized = True
    
    def get_current_phase_data(self) -> Dict[str, Any]:
        """Get current phase data for UI display"""
        session_id = st.session_state.phase_session_id
        progress_summary = self.phase_system.get_progress_summary(session_id)
        
        if "error" in progress_summary:
            # Reinitialize if session lost
            self.phase_system.create_session(session_id)
            progress_summary = self.phase_system.get_progress_summary(session_id)
        
        return progress_summary
    
    def get_phase_circles_data(self) -> Dict[str, Dict[str, Any]]:
        """Get data formatted for the phase circles UI component"""
        progress_summary = self.get_current_phase_data()
        phase_summaries = progress_summary.get('phase_summaries', {})
        
        circles_data = {}
        for phase_name in ['ideation', 'visualization', 'materialization']:
            phase_data = phase_summaries.get(phase_name, {})
            circles_data[phase_name] = {
                'completion_percent': phase_data.get('completion_percent', 0),
                'questions_completed': phase_data.get('questions_completed', 0),
                'total_questions': phase_data.get('total_questions', 5),
                'average_score': phase_data.get('average_score', 0),
                'is_complete': phase_data.get('is_complete', False)
            }
        
        return circles_data
    
    def analyze_conversation_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation messages for phase progression"""
        if not messages:
            return {"analyzed_responses": [], "progress_summary": self.get_current_phase_data()}
        
        # Extract user messages and combine into conversation text
        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
        conversation_text = ' '.join(user_messages)
        
        session_id = st.session_state.phase_session_id
        return self.phase_system.analyze_conversation(session_id, conversation_text)
    
    def process_new_message(self, message_content: str, role: str = 'user') -> Dict[str, Any]:
        """Process a new message for phase progression"""
        if role != 'user':
            return {"no_analysis": True}
        
        session_id = st.session_state.phase_session_id
        
        # Check if this message addresses current question
        current_question = self.phase_system.get_current_question(session_id)
        if current_question:
            # Simple check if message might be answering the question
            keyword_matches = sum(1 for keyword in current_question.keywords 
                                if keyword.lower() in message_content.lower())
            
            if keyword_matches >= 1 and len(message_content.split()) >= 10:
                # Process as response to current question using new method
                return self.phase_system.process_user_message(session_id, message_content)
        
        # Otherwise, analyze for any phase progression
        return self.phase_system.analyze_conversation(session_id, message_content)
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question for the user"""
        session_id = st.session_state.phase_session_id
        question = self.phase_system.get_current_question(session_id)
        
        if question:
            return {
                "id": question.id,
                "phase": question.phase.value,
                "text": question.text,
                "keywords": question.keywords
            }
        return None
    
    def get_phase_guidance(self) -> Dict[str, Any]:
        """Get guidance for the current phase"""
        progress_summary = self.get_current_phase_data()
        current_phase = progress_summary.get('current_phase', 'ideation')
        phase_summaries = progress_summary.get('phase_summaries', {})
        current_phase_data = phase_summaries.get(current_phase, {})
        
        # Get current question
        current_question = self.get_current_question()
        
        # Phase descriptions
        phase_descriptions = {
            'ideation': 'Focus on understanding the problem, users, and developing core concepts',
            'visualization': 'Develop spatial arrangements, forms, and architectural character',
            'materialization': 'Work out technical details, systems, and construction approaches'
        }
        
        return {
            'current_phase': current_phase,
            'phase_description': phase_descriptions.get(current_phase, ''),
            'current_question': current_question,
            'completion_percent': current_phase_data.get('completion_percent', 0),
            'questions_completed': current_phase_data.get('questions_completed', 0),
            'total_questions': current_phase_data.get('total_questions', 5),
            'strengths': current_phase_data.get('strengths', []),
            'improvement_areas': current_phase_data.get('improvement_areas', []),
            'average_score': current_phase_data.get('average_score', 0)
        }
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall progress across all phases"""
        progress_summary = self.get_current_phase_data()
        
        return {
            'overall_completion': progress_summary.get('overall_completion', 0),
            'overall_score': progress_summary.get('overall_score', 0),
            'current_phase': progress_summary.get('current_phase', 'ideation'),
            'total_questions_answered': progress_summary.get('total_questions_answered', 0),
            'total_questions': progress_summary.get('total_questions', 15)
        }
    
    def reset_session(self):
        """Reset the current session"""
        # Clear session state
        if 'phase_session_id' in st.session_state:
            del st.session_state.phase_session_id
        if 'phase_system_initialized' in st.session_state:
            del st.session_state.phase_system_initialized
        
        # Reinitialize
        self._initialize_session_state()
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export session data for analysis or storage"""
        session_id = st.session_state.phase_session_id
        session = self.phase_system.get_session(session_id)
        
        if not session:
            return {"error": "No session found"}
        
        # Convert session to serializable format
        export_data = {
            'session_id': session.session_id,
            'current_phase': session.current_phase.value,
            'created_at': session.created_at.isoformat(),
            'last_updated': session.last_updated.isoformat(),
            'overall_score': session.overall_score,
            'phase_progress': {},
            'conversation_history': session.conversation_history
        }
        
        # Export phase progress
        for phase, progress in session.phase_progress.items():
            export_data['phase_progress'][phase.value] = {
                'questions_answered': progress.questions_answered,
                'completion_percent': progress.completion_percent,
                'average_score': progress.average_score,
                'is_complete': progress.is_complete,
                'strengths': progress.strengths,
                'improvement_areas': progress.improvement_areas,
                'grades': {
                    qid: {
                        'overall_score': grade.overall_score,
                        'completeness': grade.completeness,
                        'depth': grade.depth,
                        'relevance': grade.relevance,
                        'innovation': grade.innovation,
                        'technical': grade.technical,
                        'strengths': grade.strengths,
                        'improvements': grade.improvements,
                        'timestamp': grade.timestamp.isoformat()
                    }
                    for qid, grade in progress.grades.items()
                }
            }
        
        return export_data
    
    def get_detailed_feedback(self) -> Dict[str, Any]:
        """Get detailed feedback for the current session"""
        progress_summary = self.get_current_phase_data()
        phase_summaries = progress_summary.get('phase_summaries', {})
        
        feedback = {
            'overall_assessment': self._generate_overall_assessment(progress_summary),
            'phase_feedback': {},
            'recommendations': self._generate_recommendations(progress_summary)
        }
        
        # Generate feedback for each phase
        for phase_name, phase_data in phase_summaries.items():
            if phase_data.get('questions_completed', 0) > 0:
                feedback['phase_feedback'][phase_name] = {
                    'completion_status': 'Complete' if phase_data.get('is_complete') else 'In Progress',
                    'score_assessment': self._assess_score(phase_data.get('average_score', 0)),
                    'strengths': phase_data.get('strengths', []),
                    'improvement_areas': phase_data.get('improvement_areas', []),
                    'progress_percent': phase_data.get('completion_percent', 0)
                }
        
        return feedback
    
    def _generate_overall_assessment(self, progress_summary: Dict[str, Any]) -> str:
        """Generate overall assessment text"""
        overall_score = progress_summary.get('overall_score', 0)
        overall_completion = progress_summary.get('overall_completion', 0)
        
        if overall_completion < 20:
            return "Just getting started - focus on exploring your design ideas thoroughly."
        elif overall_completion < 50:
            return "Making good progress - continue developing your concepts with depth."
        elif overall_completion < 80:
            return "Well underway - you're developing a comprehensive design approach."
        else:
            return "Excellent progress - you've demonstrated strong design thinking across all phases."
    
    def _assess_score(self, score: float) -> str:
        """Assess a score and return descriptive text"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.7:
            return "Good"
        elif score >= 0.6:
            return "Satisfactory"
        elif score >= 0.5:
            return "Needs Improvement"
        else:
            return "Requires Attention"
    
    def _generate_recommendations(self, progress_summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on progress"""
        recommendations = []
        current_phase = progress_summary.get('current_phase', 'ideation')
        phase_summaries = progress_summary.get('phase_summaries', {})
        
        # Current phase recommendations
        current_phase_data = phase_summaries.get(current_phase, {})
        completion = current_phase_data.get('completion_percent', 0)
        
        if completion < 50:
            recommendations.append(f"Focus on completing more questions in the {current_phase} phase")
        
        # Score-based recommendations
        overall_score = progress_summary.get('overall_score', 0)
        if overall_score < 0.6:
            recommendations.append("Try to provide more detailed and comprehensive responses")
        
        # Phase-specific recommendations
        if current_phase == 'ideation' and completion > 80:
            recommendations.append("Consider moving to the visualization phase to develop spatial concepts")
        elif current_phase == 'visualization' and completion > 80:
            recommendations.append("Begin thinking about technical and material considerations")
        
        return recommendations
