"""
Move Parser for extracting design moves from interactions
Analyzes text to identify discrete design moves for linkography
"""

import re
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import spacy
from textblob import TextBlob

from thesis_tests.data_models import (
    DesignMove, MoveType, TestPhase, MoveSource, 
    Modality, DesignFocus
)


class MoveParser:
    """Parses interactions to extract design moves"""
    
    def __init__(self):
        # Load spaCy model for NLP analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if spaCy model not installed
            self.nlp = None
        
        # Keywords for move type identification
        self.move_type_keywords = {
            MoveType.ANALYSIS: [
                'analyze', 'examine', 'consider', 'look at', 'study',
                'investigate', 'explore', 'understand', 'assess'
            ],
            MoveType.SYNTHESIS: [
                'combine', 'integrate', 'connect', 'merge', 'unite',
                'blend', 'fuse', 'incorporate', 'join', 'link'
            ],
            MoveType.EVALUATION: [
                'evaluate', 'judge', 'assess', 'critique', 'review',
                'compare', 'weigh', 'measure', 'test', 'validate'
            ],
            MoveType.TRANSFORMATION: [
                'transform', 'change', 'modify', 'adapt', 'convert',
                'alter', 'adjust', 'reshape', 'evolve', 'develop'
            ],
            MoveType.REFLECTION: [
                'reflect', 'think about', 'consider how', 'wonder',
                'realize', 'understand that', 'notice', 'observe'
            ]
        }
        
        # Keywords for design focus identification
        self.design_focus_keywords = {
            DesignFocus.FUNCTION: [
                'function', 'use', 'purpose', 'activity', 'program',
                'utility', 'operation', 'performance', 'work'
            ],
            DesignFocus.FORM: [
                'form', 'shape', 'geometry', 'appearance', 'aesthetic',
                'visual', 'look', 'style', 'composition'
            ],
            DesignFocus.STRUCTURE: [
                'structure', 'construction', 'framework', 'support',
                'stability', 'engineering', 'technical', 'system'
            ],
            DesignFocus.MATERIAL: [
                'material', 'texture', 'surface', 'finish', 'substance',
                'component', 'element', 'resource', 'medium'
            ],
            DesignFocus.ENVIRONMENT: [
                'environment', 'context', 'site', 'location', 'climate',
                'sustainability', 'ecology', 'setting', 'surrounding'
            ],
            DesignFocus.CULTURE: [
                'culture', 'community', 'social', 'people', 'tradition',
                'identity', 'heritage', 'values', 'meaning'
            ]
        }
    
    def parse_user_input(self, text: str, phase: TestPhase, 
                        source: MoveSource) -> List[DesignMove]:
        """Parse user input to extract design moves"""
        moves = []
        
        # Split text into sentences for move identification
        sentences = self._split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            if self._is_design_statement(sentence):
                move = self._create_move_from_sentence(
                    sentence, phase, source, Modality.TEXT, i
                )
                moves.append(move)
        
        # If no moves identified, create single move from entire input
        if not moves and text.strip():
            moves.append(self._create_move_from_sentence(
                text, phase, source, Modality.TEXT, 0
            ))
        
        return moves
    
    def parse_ai_response(self, text: str, phase: TestPhase, 
                         source: MoveSource) -> List[DesignMove]:
        """Parse AI response to extract design moves"""
        moves = []
        
        # AI responses often contain questions and suggestions
        # Extract substantive design-related content
        sentences = self._split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            # Skip pure questions without design content
            if sentence.strip().endswith('?') and not self._contains_design_content(sentence):
                continue
            
            # Extract design suggestions or observations
            if self._contains_design_content(sentence):
                move = self._create_move_from_sentence(
                    sentence, phase, source, Modality.TEXT, i
                )
                moves.append(move)
        
        return moves
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Simple regex-based splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _is_design_statement(self, sentence: str) -> bool:
        """Check if sentence contains design-related content"""
        sentence_lower = sentence.lower()
        
        # Check for design keywords
        design_keywords = [
            'design', 'create', 'build', 'develop', 'plan',
            'space', 'area', 'room', 'zone', 'layout',
            'material', 'structure', 'form', 'function'
        ]
        
        return any(keyword in sentence_lower for keyword in design_keywords)
    
    def _contains_design_content(self, sentence: str) -> bool:
        """Check if sentence contains substantive design content"""
        sentence_lower = sentence.lower()
        
        # Check for any design focus keywords
        for focus_keywords in self.design_focus_keywords.values():
            if any(keyword in sentence_lower for keyword in focus_keywords):
                return True
        
        # Check for action verbs related to design
        action_verbs = [
            'place', 'position', 'locate', 'arrange', 'organize',
            'connect', 'separate', 'divide', 'open', 'close',
            'expand', 'contract', 'elevate', 'lower', 'rotate'
        ]
        
        return any(verb in sentence_lower for verb in action_verbs)
    
    def _create_move_from_sentence(self, sentence: str, phase: TestPhase,
                                  source: MoveSource, modality: Modality,
                                  sequence: int) -> DesignMove:
        """Create a design move from a sentence"""
        # Determine move type
        move_type = self._identify_move_type(sentence)
        
        # Determine design focus
        design_focus = self._identify_design_focus(sentence)
        
        # Determine cognitive operation
        cognitive_operation = self._identify_cognitive_operation(sentence)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(sentence)
        
        # Create move
        move = DesignMove(
            id=str(uuid.uuid4()),
            session_id="",  # Will be set by logger
            timestamp=datetime.now(),
            sequence_number=0,  # Will be set by logger
            content=sentence,
            move_type=move_type,
            phase=phase,
            modality=modality,
            cognitive_operation=cognitive_operation,
            design_focus=design_focus,
            move_source=source,
            cognitive_load=self._assess_cognitive_load(complexity_score),
            complexity_score=complexity_score,
            pause_duration=0.0,  # Could be calculated from interaction timing
            revision_count=0,
            uncertainty_markers=self._count_uncertainty_markers(sentence)
        )
        
        return move
    
    def _identify_move_type(self, sentence: str) -> MoveType:
        """Identify the type of design move"""
        sentence_lower = sentence.lower()
        
        # Count keyword matches for each type
        type_scores = {}
        for move_type, keywords in self.move_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in sentence_lower)
            type_scores[move_type] = score
        
        # Return type with highest score, default to ANALYSIS
        if max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        
        # Additional heuristics
        if any(word in sentence_lower for word in ['create', 'make', 'build']):
            return MoveType.SYNTHESIS
        elif any(word in sentence_lower for word in ['change', 'modify', 'adapt']):
            return MoveType.TRANSFORMATION
        elif sentence.strip().endswith('?'):
            return MoveType.REFLECTION
        
        return MoveType.ANALYSIS
    
    def _identify_design_focus(self, sentence: str) -> DesignFocus:
        """Identify the design focus of the move"""
        sentence_lower = sentence.lower()
        
        # Count keyword matches for each focus
        focus_scores = {}
        for design_focus, keywords in self.design_focus_keywords.items():
            score = sum(1 for keyword in keywords if keyword in sentence_lower)
            focus_scores[design_focus] = score
        
        # Return focus with highest score, default to FUNCTION
        if max(focus_scores.values()) > 0:
            return max(focus_scores, key=focus_scores.get)
        
        return DesignFocus.FUNCTION
    
    def _identify_cognitive_operation(self, sentence: str) -> str:
        """Identify the cognitive operation type"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['propose', 'suggest', 'could', 'might']):
            return "proposal"
        elif any(word in sentence_lower for word in ['clarify', 'explain', 'define', 'specify']):
            return "clarification"
        elif any(word in sentence_lower for word in ['assess', 'evaluate', 'judge', 'measure']):
            return "assessment"
        elif any(word in sentence_lower for word in ['support', 'reinforce', 'strengthen']):
            return "support"
        elif any(word in sentence_lower for word in ['refer', 'cite', 'example', 'precedent']):
            return "reference"
        
        return "proposal"
    
    def _calculate_complexity(self, sentence: str) -> float:
        """Calculate linguistic complexity of the sentence"""
        # Simple complexity measure based on:
        # - Sentence length
        # - Word complexity
        # - Clause structure
        
        words = sentence.split()
        word_count = len(words)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        
        # Complex word count (words > 6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        
        # Clause indicators
        clause_indicators = [',', ';', ' - ', ' because ', ' although ', ' while ']
        clause_count = sum(1 for indicator in clause_indicators if indicator in sentence) + 1
        
        # Calculate complexity score (0-1)
        complexity = (
            min(word_count / 30, 1.0) * 0.3 +  # Length factor
            min(avg_word_length / 8, 1.0) * 0.3 +  # Word complexity
            min(complex_words / word_count, 1.0) * 0.2 +  # Complex word ratio
            min(clause_count / 3, 1.0) * 0.2  # Clause complexity
        )
        
        return complexity
    
    def _assess_cognitive_load(self, complexity_score: float) -> str:
        """Assess cognitive load based on complexity"""
        if complexity_score > 0.7:
            return "high"
        elif complexity_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _count_uncertainty_markers(self, sentence: str) -> int:
        """Count uncertainty markers in the sentence"""
        uncertainty_markers = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'uncertain', 'unclear', 'not sure', "don't know",
            'question', 'wonder', 'confused', 'unsure'
        ]
        
        sentence_lower = sentence.lower()
        count = sum(1 for marker in uncertainty_markers if marker in sentence_lower)
        
        return count
    
    def extract_moves_from_sketch(self, sketch_description: str, 
                                 phase: TestPhase) -> List[DesignMove]:
        """Extract design moves from sketch description"""
        # Sketches typically represent synthesis or transformation moves
        move = DesignMove(
            id=str(uuid.uuid4()),
            session_id="",
            timestamp=datetime.now(),
            sequence_number=0,
            content=sketch_description,
            move_type=MoveType.SYNTHESIS,
            phase=phase,
            modality=Modality.SKETCH,
            cognitive_operation="proposal",
            design_focus=DesignFocus.FORM,
            move_source=MoveSource.USER_GENERATED,
            cognitive_load="high",
            complexity_score=0.7  # Sketches are inherently complex
        )
        
        return [move]