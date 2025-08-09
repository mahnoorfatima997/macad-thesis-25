"""
Question generation processing module for creating Socratic questions.
"""
from typing import Dict, Any, List, Optional
from ..schemas import QuestionContext, QuestionResult, ConfidenceLevel, UnderstandingLevel
from ..config import *
from ...common import LLMClient, AgentTelemetry, TextProcessor
from state_manager import ArchMentorState


class QuestionGeneratorProcessor:
    """
    Processes Socratic question generation based on student context.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("question_generator")
        self.client = LLMClient(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        self.text_processor = TextProcessor()
        
    async def generate_socratic_question(
        self, 
        user_input: str, 
        state: ArchMentorState, 
        context_classification: Dict, 
        analysis_result: Dict, 
        gap_type: str
    ) -> QuestionResult:
        """
        Generate appropriate Socratic question based on context.
        This is the main method from the original adapter.
        """
        self.telemetry.log_agent_start("generate_socratic_question")
        
        try:
            # Extract project context
            project_context = getattr(state, 'current_design_brief', 'architectural project')
            
            # Extract classification data
            core_classification = context_classification.get('core_classification', {})
            interaction_type = core_classification.get('interaction_type', 'general')
            understanding_level = core_classification.get('understanding_level', 'medium')
            confidence_level = core_classification.get('confidence_level', 'confident')
            
            # Create question context
            question_context = QuestionContext(
                user_input=user_input,
                project_context=project_context,
                interaction_type=interaction_type,
                understanding_level=understanding_level,
                confidence_level=confidence_level,
                gap_type=gap_type
            )
            
            # Generate the question using LLM
            question_result = await self._generate_question_with_llm(question_context)
            
            self.telemetry.log_agent_end("generate_socratic_question")
            return question_result
            
        except Exception as e:
            self.telemetry.log_error("generate_socratic_question", str(e))
            return self._get_fallback_question_result()
    
    async def _generate_question_with_llm(self, context: QuestionContext) -> QuestionResult:
        """Generate question using LLM based on context."""
        try:
            # Format guidelines
            guidelines = "\n".join([f"{i+1}. {guideline}" for i, guideline in enumerate(QUESTION_GUIDELINES)])
            
            # Create prompt from template
            prompt = QUESTION_PROMPT_TEMPLATE.format(
                user_input=context.user_input,
                project_context=context.project_context,
                interaction_type=context.interaction_type,
                understanding_level=context.understanding_level,
                confidence_level=context.confidence_level,
                gap_type=context.gap_type,
                guidelines=guidelines
            )
            
            # Generate response using LLM client
            response = await self.client.generate_completion([
                self.client.create_system_message(SYSTEM_MESSAGE),
                self.client.create_user_message(prompt)
            ])
            
            if response and response.get("content"):
                question_text = response["content"].strip()
                
                # Ensure it's a question
                if not question_text.endswith('?'):
                    question_text += '?'
                
                # Determine pedagogical intent
                pedagogical_intent = self._get_pedagogical_intent(
                    context.interaction_type, 
                    context.confidence_level
                )
                
                return QuestionResult(
                    question_text=question_text,
                    question_type="socratic",
                    interaction_type=context.interaction_type,
                    understanding_level=context.understanding_level,
                    confidence_level=context.confidence_level,
                    pedagogical_intent=pedagogical_intent,
                    generation_confidence=0.8
                )
            
        except Exception as e:
            self.telemetry.log_error("_generate_question_with_llm", str(e))
        
        return self._get_fallback_question_result()
    
    def _get_pedagogical_intent(self, interaction_type: str, confidence_level: str) -> str:
        """
        Get pedagogical intent based on student state.
        This logic is from the original adapter.
        """
        try:
            if confidence_level == "overconfident":
                return PEDAGOGICAL_INTENTS['overconfident']
            elif confidence_level == "uncertain":
                return PEDAGOGICAL_INTENTS['uncertain']
            elif interaction_type == "confusion":
                return PEDAGOGICAL_INTENTS['confusion']
            else:
                return PEDAGOGICAL_INTENTS['default']
                
        except Exception as e:
            self.telemetry.log_error("_get_pedagogical_intent", str(e))
            return PEDAGOGICAL_INTENTS['default']
    
    def _get_fallback_question_result(self) -> QuestionResult:
        """
        Return fallback question when generation fails.
        Uses the exact fallback from the original adapter.
        """
        return QuestionResult(
            question_text=FALLBACK_QUESTION,
            question_type="fallback",
            pedagogical_intent="Encourage exploration and curiosity",
            generation_confidence=0.6
        )
    
    def validate_question(self, question_text: str) -> bool:
        """Validate that the generated question meets quality criteria."""
        try:
            if not question_text or len(question_text.strip()) < 5:
                return False
            
            # Check word count
            word_count = len(question_text.split())
            if word_count > QUESTION_MAX_WORDS:
                return False
            
            # Check if it's actually a question
            if not question_text.strip().endswith('?'):
                return False
            
            # Check for basic quality indicators
            question_lower = question_text.lower()
            quality_indicators = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'consider', 'think', 'approach']
            
            if not any(indicator in question_lower for indicator in quality_indicators):
                return False
            
            return True
            
        except Exception as e:
            self.telemetry.log_error("validate_question", str(e))
            return False
    
    def get_question_complexity(self, question_text: str) -> str:
        """Assess the complexity level of a generated question."""
        try:
            question_lower = question_text.lower()
            
            # Complex question indicators
            complex_indicators = [
                'implications', 'consequences', 'relationship', 'integration',
                'synthesis', 'evaluation', 'analysis', 'comparison', 'trade-offs'
            ]
            
            # Simple question indicators
            simple_indicators = [
                'what is', 'who is', 'when is', 'where is', 'which is'
            ]
            
            if any(indicator in question_lower for indicator in complex_indicators):
                return 'complex'
            elif any(indicator in question_lower for indicator in simple_indicators):
                return 'simple'
            else:
                return 'moderate'
                
        except Exception as e:
            self.telemetry.log_error("get_question_complexity", str(e))
            return 'moderate'
    
    def suggest_question_improvements(self, question_text: str, context: QuestionContext) -> List[str]:
        """Suggest improvements for generated questions."""
        suggestions = []
        
        try:
            # Check word count
            word_count = len(question_text.split())
            if word_count > QUESTION_MAX_WORDS:
                suggestions.append(f"Reduce word count from {word_count} to under {QUESTION_MAX_WORDS} words")
            
            # Check specificity
            if 'project' not in question_text.lower() and context.project_context != 'architectural project':
                suggestions.append("Make question more project-specific")
            
            # Check question type appropriateness
            if context.confidence_level == 'overconfident' and 'challenge' not in question_text.lower():
                suggestions.append("Add more challenging elements for overconfident student")
            
            if context.understanding_level == 'low' and self.get_question_complexity(question_text) == 'complex':
                suggestions.append("Simplify question for student with low understanding")
            
            return suggestions
            
        except Exception as e:
            self.telemetry.log_error("suggest_question_improvements", str(e))
            return []
    
    def get_question_statistics(self, question_text: str) -> Dict[str, Any]:
        """Get statistics about the generated question."""
        try:
            words = question_text.split()
            
            return {
                'word_count': len(words),
                'character_count': len(question_text),
                'complexity': self.get_question_complexity(question_text),
                'ends_with_question_mark': question_text.endswith('?'),
                'contains_project_reference': 'project' in question_text.lower() or 'design' in question_text.lower(),
                'question_words': [word for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who'] 
                                 if word in question_text.lower()],
                'is_valid': self.validate_question(question_text)
            }
            
        except Exception as e:
            self.telemetry.log_error("get_question_statistics", str(e))
            return {'word_count': 0, 'is_valid': False} 