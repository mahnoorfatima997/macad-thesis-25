"""
Assessment tools for pre and post tests
Based on validated instruments for critical thinking and architectural knowledge
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class PreTestAssessment:
    """Pre-test assessment instruments"""
    
    def __init__(self):
        self.responses = {}
        
    def render_critical_thinking_questions(self) -> Dict[str, Any]:
        """Render critical thinking assessment questions"""
        st.markdown("#### Critical Thinking Assessment")
        st.markdown("*Based on Halpern Critical Thinking Assessment*")
        
        questions = [
            {
                "id": "ct1",
                "question": "A community center design includes a large open space that can be divided. This flexibility is important because:",
                "options": [
                    "It looks more modern",
                    "It allows the space to adapt to different community needs over time",
                    "It's easier to construct",
                    "It reduces construction costs"
                ],
                "correct": 1,
                "reasoning_required": True
            },
            {
                "id": "ct2",
                "question": "Evaluate this design rationale: 'The entrance should be monumental because community centers need to make a strong civic statement.' What assumptions does this make?",
                "type": "text",
                "correct_elements": ["assumes civic importance", "monumentality equals significance", "community values"]
            },
            {
                "id": "ct3",
                "question": "If your community center design aims to promote intergenerational interaction, which spatial strategy would be LEAST effective?",
                "options": [
                    "Shared circulation spaces with seating areas",
                    "Visual connections between different activity zones",
                    "Completely separated areas for different age groups",
                    "Central gathering space accessible to all"
                ],
                "correct": 2
            },
            {
                "id": "ct4",
                "question": "Given limited community input data, describe your approach to making design decisions about program allocation.",
                "type": "text",
                "correct_elements": ["acknowledge uncertainty", "multiple scenarios", "iterative process", "community engagement"]
            },
            {
                "id": "ct5",
                "question": "A community group wants both a quiet library space and an active children's area in limited square footage. Which approach best resolves this conflict?",
                "options": [
                    "Choose one over the other based on majority preference",
                    "Place them at opposite ends with sound isolation",
                    "Combine them into one multi-use space",
                    "Schedule different times for each use"
                ],
                "correct": 1,
                "follow_up": "Explain your reasoning"
            }
        ]
        
        # Render questions
        for q in questions:
            st.markdown(f"**{q['id'].upper()}. {q['question']}**")
            
            if q.get('type') == 'text':
                response = st.text_area(
                    "Your answer:",
                    key=f"pretest_{q['id']}",
                    height=100
                )
                self.responses[q['id']] = response
            else:
                response = st.radio(
                    "Select one:",
                    options=q['options'],
                    key=f"pretest_{q['id']}"
                )
                self.responses[q['id']] = q['options'].index(response) if response else None
                
                if q.get('reasoning_required') or q.get('follow_up'):
                    reasoning = st.text_area(
                        q.get('follow_up', "Explain your reasoning:"),
                        key=f"pretest_{q['id']}_reasoning",
                        height=75
                    )
                    self.responses[f"{q['id']}_reasoning"] = reasoning
            
            st.divider()
        
        return self.responses
    
    def render_architectural_knowledge_questions(self) -> Dict[str, Any]:
        """Render architectural knowledge baseline questions"""
        st.markdown("#### Architectural Knowledge Assessment")
        
        questions = [
            {
                "id": "ak1",
                "question": "Which of the following is NOT typically considered in adaptive reuse projects?",
                "options": [
                    "Structural capacity assessment",
                    "Historical significance",
                    "Complete demolition of existing structure",
                    "Code compliance for new use"
                ],
                "correct": 2
            },
            {
                "id": "ak2",
                "question": "What is the primary purpose of a building's circulation system?",
                "options": [
                    "To provide emergency exits only",
                    "To organize movement and create spatial hierarchy",
                    "To minimize construction costs",
                    "To maximize floor area"
                ],
                "correct": 1
            },
            {
                "id": "ak3",
                "question": "In sustainable design, 'passive strategies' refer to:",
                "options": [
                    "Design features that work without mechanical systems",
                    "Strategies that don't require user participation",
                    "Low-cost construction methods",
                    "Minimal design interventions"
                ],
                "correct": 0
            },
            {
                "id": "ak4",
                "question": "Describe the relationship between building orientation and natural lighting.",
                "type": "text",
                "correct_elements": ["sun path", "glazing", "north/south", "heat gain", "glare"]
            },
            {
                "id": "ak5",
                "question": "Which spatial organization strategy creates the most flexible community space?",
                "options": [
                    "Fixed room divisions with corridors",
                    "Open plan with movable partitions",
                    "Central atrium with surrounding rooms",
                    "Linear arrangement of separate spaces"
                ],
                "correct": 1
            }
        ]
        
        # Render questions
        for q in questions:
            st.markdown(f"**{q['id'].upper()}. {q['question']}**")
            
            if q.get('type') == 'text':
                response = st.text_area(
                    "Your answer:",
                    key=f"pretest_{q['id']}",
                    height=100
                )
                self.responses[q['id']] = response
            else:
                response = st.radio(
                    "Select one:",
                    options=q['options'],
                    key=f"pretest_{q['id']}"
                )
                self.responses[q['id']] = q['options'].index(response) if response else None
            
            st.divider()
        
        return self.responses
    
    def render_spatial_reasoning_questions(self) -> Dict[str, Any]:
        """Render spatial reasoning test questions"""
        st.markdown("#### Spatial Reasoning Assessment")
        
        # Note: In a real implementation, these would include visual elements
        st.info("Note: In the actual test, these questions would include 3D diagrams and visual elements.")
        
        questions = [
            {
                "id": "sr1",
                "question": "If a rectangular space is rotated 90 degrees and a wall is added dividing it lengthwise, how many spaces result?",
                "options": ["1", "2", "3", "4"],
                "correct": 1
            },
            {
                "id": "sr2",
                "question": "A double-height space with a mezzanine level creates how many distinct spatial volumes?",
                "options": [
                    "1 - it's still one space",
                    "2 - upper and lower",
                    "3 - under, on, and above mezzanine",
                    "4 - depends on the configuration"
                ],
                "correct": 2
            },
            {
                "id": "sr3",
                "question": "Which circulation pattern provides the most efficient access to all spaces?",
                "options": [
                    "Linear corridor",
                    "Central hub",
                    "Perimeter loop",
                    "Branching system"
                ],
                "correct": 1
            }
        ]
        
        # Render questions
        for q in questions:
            st.markdown(f"**{q['id'].upper()}. {q['question']}**")
            
            response = st.radio(
                "Select one:",
                options=q['options'],
                key=f"pretest_{q['id']}"
            )
            self.responses[q['id']] = q['options'].index(response) if response else None
            
            st.divider()
        
        return self.responses
    
    def validate_responses(self) -> bool:
        """Check if all questions have been answered"""
        # Count expected responses
        expected_count = 13  # 5 CT + 5 AK + 3 SR questions
        
        # Count actual responses (excluding reasoning fields)
        actual_count = sum(1 for k in self.responses.keys() if not k.endswith('_reasoning'))
        
        return actual_count >= expected_count
    
    def score_critical_thinking(self) -> float:
        """Score critical thinking responses"""
        # Simple scoring for demo - would be more sophisticated in practice
        correct_answers = {
            'ct1': 1,
            'ct3': 2,
            'ct5': 1
        }
        
        score = 0
        total = len(correct_answers)
        
        for q_id, correct in correct_answers.items():
            if self.responses.get(q_id) == correct:
                score += 1
        
        # Add points for quality of text responses
        for q_id in ['ct2', 'ct4']:
            if q_id in self.responses and len(self.responses[q_id]) > 50:
                score += 0.5
                total += 1
        
        return score / total if total > 0 else 0
    
    def score_architectural_knowledge(self) -> float:
        """Score architectural knowledge responses"""
        correct_answers = {
            'ak1': 2,
            'ak2': 1,
            'ak3': 0,
            'ak5': 1
        }
        
        score = 0
        total = len(correct_answers)
        
        for q_id, correct in correct_answers.items():
            if self.responses.get(q_id) == correct:
                score += 1
        
        # Score text response
        if 'ak4' in self.responses:
            response = self.responses['ak4'].lower()
            keywords = ['sun path', 'orientation', 'glazing', 'heat', 'light']
            keyword_count = sum(1 for k in keywords if k in response)
            score += min(keyword_count / 3, 1)  # Max 1 point
            total += 1
        
        return score / total if total > 0 else 0
    
    def score_spatial_reasoning(self) -> float:
        """Score spatial reasoning responses"""
        correct_answers = {
            'sr1': 1,
            'sr2': 2,
            'sr3': 1
        }
        
        score = sum(1 for q_id, correct in correct_answers.items() 
                   if self.responses.get(q_id) == correct)
        
        return score / len(correct_answers)


class PostTestAssessment:
    """Post-test assessment instruments"""
    
    def __init__(self):
        self.responses = {}
    
    def render_reflection_questions(self) -> Dict[str, Any]:
        """Render design process reflection questions"""
        st.markdown("#### Design Process Reflection")
        
        questions = [
            {
                "id": "ref1",
                "question": "How did your understanding of the design problem evolve throughout the three phases?",
                "type": "text"
            },
            {
                "id": "ref2",
                "question": "What were the most significant learning moments in your design process?",
                "type": "text"
            },
            {
                "id": "ref3",
                "question": "How did you approach problems when you encountered difficulties?",
                "type": "text"
            },
            {
                "id": "ref4",
                "question": "What would you approach differently in future projects?",
                "type": "text"
            }
        ]
        
        # Render questions
        for q in questions:
            st.markdown(f"**{q['question']}**")
            response = st.text_area(
                "Your reflection:",
                key=f"posttest_{q['id']}",
                height=120
            )
            self.responses[q['id']] = response
            st.divider()
        
        return self.responses
    
    def render_transfer_task(self) -> Dict[str, Any]:
        """Render knowledge transfer challenge"""
        st.markdown("#### Knowledge Transfer Challenge")
        st.markdown("""
        **New Scenario**: Apply the principles and methodologies you've developed to a new scenario:
        
        *Adaptive reuse of a former shopping mall (200m x 150m) into a mixed-use community hub 
        combining educational facilities, maker spaces, and public services.*
        
        Describe your approach to this new challenge, demonstrating what you've learned:
        """)
        
        response = st.text_area(
            "Your approach:",
            key="posttest_transfer",
            height=200,
            placeholder="Describe how you would approach this new design challenge..."
        )
        
        self.responses['transfer'] = response
        
        # Specific questions about transfer
        st.markdown("**Specific considerations:**")
        
        considerations = [
            ("transfer_program", "How would you develop the program for this larger, more complex facility?"),
            ("transfer_structure", "What structural and spatial strategies from your community center design apply here?"),
            ("transfer_community", "How would you ensure community engagement in this different context?")
        ]
        
        for key, question in considerations:
            st.markdown(f"- {question}")
            response = st.text_area(
                "Your response:",
                key=f"posttest_{key}",
                height=80
            )
            self.responses[key] = response
        
        return self.responses
    
    def validate_responses(self) -> bool:
        """Check if all questions have been answered"""
        required_fields = ['ref1', 'ref2', 'ref3', 'ref4', 'transfer', 
                          'transfer_program', 'transfer_structure', 'transfer_community']
        
        for field in required_fields:
            if field not in self.responses or len(self.responses[field].strip()) < 20:
                return False
        
        return True
    
    def score_reflection(self) -> float:
        """Score reflection quality"""
        # Simple scoring based on response depth
        reflection_scores = []
        
        for q_id in ['ref1', 'ref2', 'ref3', 'ref4']:
            if q_id in self.responses:
                response = self.responses[q_id]
                # Score based on length and complexity
                word_count = len(response.split())
                
                if word_count > 100:
                    score = 1.0
                elif word_count > 50:
                    score = 0.75
                elif word_count > 25:
                    score = 0.5
                else:
                    score = 0.25
                
                reflection_scores.append(score)
        
        return sum(reflection_scores) / len(reflection_scores) if reflection_scores else 0
    
    def score_transfer(self) -> float:
        """Score knowledge transfer ability"""
        transfer_scores = []
        
        # Main transfer response
        if 'transfer' in self.responses:
            response = self.responses['transfer']
            # Look for application of learned principles
            principles = ['adaptive reuse', 'community', 'flexibility', 'program', 'circulation']
            principle_count = sum(1 for p in principles if p in response.lower())
            
            score = min(principle_count / 3, 1.0)
            transfer_scores.append(score)
        
        # Specific considerations
        for key in ['transfer_program', 'transfer_structure', 'transfer_community']:
            if key in self.responses and len(self.responses[key]) > 30:
                transfer_scores.append(0.75)
            else:
                transfer_scores.append(0.25)
        
        return sum(transfer_scores) / len(transfer_scores) if transfer_scores else 0