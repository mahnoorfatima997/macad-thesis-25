"""
Input classification processing module for analyzing and classifying student input.
"""
from typing import Dict, Any, List, Optional
import re
from openai import OpenAI
import os
from ..schemas import CoreClassification
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class InputClassificationProcessor:
    """
    Processes input classification and understanding level detection.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("input_classification")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize analysis patterns from original
        self.analysis_patterns = self._initialize_analysis_patterns()

    def _initialize_analysis_patterns(self) -> Dict[str, List[str]]:
        """Initialize linguistic and behavioral analysis patterns from original"""

        return {
            # UNDERSTANDING LEVEL INDICATORS
            "low_understanding": [
                "what is", "how do", "i don't know", "can you explain",
                "help me understand", "what does", "basic", "simple"
            ],
            "medium_understanding": [
                "i think", "maybe", "could be", "seems like", "probably",
                "how about", "what about", "similar to"
            ],
            "high_understanding": [
                "considering", "analyzing", "evaluating", "comparing",
                "implementing", "optimizing", "integrating", "synthesizing"
            ],

            # CONFIDENCE LEVEL INDICATORS
            "uncertain": [
                "not sure", "maybe", "i think", "possibly", "might be",
                "uncertain", "confused", "unclear", "hesitant"
            ],
            "confident": [
                "i believe", "i know", "definitely", "certainly", "sure",
                "confident", "convinced", "positive"
            ],
            "overconfident": [
                "obviously", "clearly", "definitely", "perfect", "optimal",
                "best", "ideal", "no doubt", "certainly", "absolutely"
            ],

            # ENGAGEMENT LEVEL INDICATORS
            "high_engagement": [
                "interesting", "fascinating", "curious", "excited", "wonder",
                "what if", "how about", "could we", "let's try"
            ],
            "low_engagement": [
                "ok", "sure", "fine", "whatever", "i guess", "boring",
                "don't care", "doesn't matter"
            ],

            # EMOTIONAL INDICATORS
            "confusion": [
                "confused", "lost", "unclear", "don't understand", "puzzled",
                "bewildered", "perplexed", "mixed up"
            ],
            "frustration": [
                "frustrated", "annoying", "difficult", "hard", "stuck",
                "can't figure out", "giving up", "impossible"
            ],
            "enthusiasm": [
                "excited", "love", "amazing", "awesome", "great", "fantastic",
                "wonderful", "brilliant", "perfect"
            ]
        }

    async def perform_core_classification(self, input_text: str, state: ArchMentorState) -> CoreClassification:
        """
        Enhanced AI-powered learning state detection with manual override for specific interaction types
        """
        self.telemetry.log_agent_start("perform_core_classification")

        try:
            # FIRST: Check if this matches specific patterns using manual classification (context-aware)
            manual_interaction_type = self._classify_interaction_type(input_text, state)

            # Define interaction types that should use manual override (priority over AI)
            # REDUCED LIST: Let AI handle knowledge_request and general_statement for better context understanding
            manual_override_types = [
                "confusion_expression", "direct_answer_request",
                "implementation_request", "example_request",
                "feedback_request", "technical_question", "improvement_seeking"
                # Removed: "knowledge_request", "general_question", "general_statement"
                # → Let AI classification handle these for better context awareness
            ]

            # If it matches a specific pattern, prioritize this over AI classification
            if manual_interaction_type in manual_override_types:
                print(f"🎯 MANUAL OVERRIDE: Detected {manual_interaction_type}, bypassing AI classification")

                # Use manual classification for interaction type, but get other metrics from AI
                ai_classification = await self._get_ai_classification_for_other_metrics(input_text, state)

                # Preserve question-response as thread context flag, not main type
                is_q_response = self._is_response_to_previous_question(input_text, state)

                # Ensure confusion takes precedence if present
                input_lower = input_text.lower()
                confusion_patterns = [
                    "confused", "don't understand", "unclear", "not sure", "help", "lost", "stuck",
                    "struggling", "difficult", "what does this mean", "i don't get it"
                ]
                shows_confusion = any(p in input_lower for p in confusion_patterns)
                final_interaction_type = "confusion_expression" if shows_confusion else manual_interaction_type

                classification_dict = {
                    "interaction_type": final_interaction_type,  # Manual override with confusion priority
                    "understanding_level": ai_classification.get("understanding_level", "medium"),
                    "confidence_level": ai_classification.get("confidence_level", "confident"),
                    "engagement_level": ai_classification.get("engagement_level", "medium"),
                    "overconfidence_score": 2 if ai_classification.get("confidence_level") == "overconfident" else 0,
                    "is_technical_question": final_interaction_type == "technical_question",
                    "is_feedback_request": final_interaction_type == "feedback_request",
                    "is_example_request": final_interaction_type == "example_request",
                    "shows_confusion": shows_confusion or final_interaction_type == "confusion_expression",
                    "requests_help": final_interaction_type in ["confusion_expression", "direct_answer_request"],
                    "demonstrates_overconfidence": ai_classification.get("demonstrates_overconfidence", False),
                    "seeks_validation": False,
                    "classification": "question" if "?" in input_text else "statement",
                    "ai_reasoning": f"Manual override for {final_interaction_type}",
                    "manual_override": True,
                    "is_question_response": is_q_response,
                    "thread_context": "answering_previous_question" if is_q_response else "normal_turn"
                }
            else:
                # OTHERWISE: Use AI classification as before
                classification_dict = await self._get_ai_classification_for_other_metrics(input_text, state)

            # Convert to CoreClassification object
            interaction_type = classification_dict["interaction_type"]
            understanding_level = classification_dict["understanding_level"]
            confidence_level = classification_dict["confidence_level"]
            engagement_level = classification_dict["engagement_level"]
            
            # Additional classification aspects
            is_response_to_previous = self._is_response_to_previous_question(input_text, state)
            is_technical_question = self._is_technical_question(input_text)
            is_feedback_request = self._is_feedback_request(input_text)
            
            # Assess question complexity
            question_complexity = self._assess_question_complexity(input_text)
            
            # Detect learning intent
            learning_intent = self._detect_learning_intent(input_text)
            
            # Assess context dependency
            context_dependency = self._assess_context_dependency(input_text, state)
            
            classification = CoreClassification(
                interaction_type=interaction_type,
                understanding_level=understanding_level,
                confidence_level=confidence_level,
                engagement_level=engagement_level,
                is_response_to_question=is_response_to_previous,
            )
            # Attach extended fields dynamically to preserve richer data
            classification.is_technical_question = is_technical_question
            classification.is_feedback_request = is_feedback_request
            classification.question_complexity = question_complexity
            classification.learning_intent = learning_intent
            classification.context_dependency = context_dependency
            classification.classification_confidence = self._calculate_classification_confidence(
                interaction_type, understanding_level, confidence_level, engagement_level
            )
            
            self.telemetry.log_agent_end("perform_core_classification")
            return classification
            
        except Exception as e:
            self.telemetry.log_error("perform_core_classification", str(e))
            return self._get_fallback_classification()
    
    def _classify_interaction_type(self, input_text: str, state: ArchMentorState = None) -> str:
        """Enhanced interaction type classification from FROMOLDREPO - WORKING VERSION"""

        input_lower = input_text.lower()

        # FROMOLDREPO PATTERN SYSTEM - Level 1: High-Confidence Patterns

        # 1. Direct Answer Request (Cognitive Offloading) - HIGH PRIORITY
        direct_answer_patterns = [
            "can you design", "design this for me", "do it for me",
            "make it for me", "complete design", "full design", "finished design",
            "design it for me", "what should I design"
        ]
        if any(pattern in input_lower for pattern in direct_answer_patterns):
            return "direct_answer_request"

        # FROMOLDREPO: Check if this is a response to a previous question FIRST
        if self._is_response_to_previous_question(input_text, state):
            # If it's a response, classify based on response content
            return self._classify_response_content(input_text, state)

        # 2. Example Request - HIGH PRIORITY (More specific patterns to avoid conflicts)
        example_request_patterns = [
            # Explicit example requests
            "show me examples", "give me examples", "provide examples", "need examples",
            "can you give me examples", "can you show me examples", "can you provide examples",
            # Project-specific requests
            "example project", "example projects", "example building", "example buildings",
            "project examples", "building examples", "design examples",
            "precedent projects", "precedents", "case studies", "case study",
            # Specific building type examples
            "adaptive reuse projects", "community center projects", "projects for",
            "museum examples", "residential examples", "commercial examples",
            # References and inspiration
            "references", "inspiration", "built projects", "real projects"
        ]
        # Only classify as example_request if it contains "example", "project", "precedent", "case", or "reference"
        has_example_keywords = any(keyword in input_lower for keyword in ["example", "project", "precedent", "case", "reference"])
        if has_example_keywords and any(pattern in input_lower for pattern in example_request_patterns):
            return "example_request"

        # 3. Knowledge Request - HIGH PRIORITY (Avoid conflicts with example requests)
        knowledge_request_patterns = [
            # Direct knowledge requests (without example keywords)
            "tell me about", "what are", "what is", "explain", "describe",
            "how does", "why does", "when should", "where should",
            "I want to learn about", "can you explain", "can you describe",
            "definition of", "meaning of", "concept of",
            # Enhanced patterns for program elements and design guidance
            "what program elements", "program elements", "what elements",
            "what should i consider", "what do you suggest", "what would you suggest",
            "what considerations", "what factors", "what aspects",
            "curious about", "wondering about", "interested in learning",
            "what components", "key considerations", "important factors"
        ]
        # Only classify as knowledge_request if it doesn't have example keywords
        if not has_example_keywords and any(pattern in input_lower for pattern in knowledge_request_patterns):
            return "knowledge_request"

        # ENHANCED PATTERN SYSTEM - Level 2: Context-Dependent Patterns

        # 4. Enhanced example request detection with context awareness (HIGHER PRIORITY)
        example_context_patterns = [
            "I want to see case studies", "I'd like to see some", "Can I get references",
            "I want to see precedents", "show me precedents", "I need references",
            "I need some references", "precedent projects", "industrial buildings", "community centers",
            "for museums", "for residential", "for commercial", "for office", "for schools",
            "museum project", "residential project", "commercial project", "office project"
        ]
        if any(pattern in input_lower for pattern in example_context_patterns):
            return "example_request"

        # 5. Enhanced knowledge request detection with context awareness (HIGHER PRIORITY)
        knowledge_context_patterns = [
            "I need to understand", "I want to learn about", "I want to know about",
            "can you tell me about", "I'd like to learn"
        ]
        if any(pattern in input_lower for pattern in knowledge_context_patterns):
            return "knowledge_request"

        # 6. Enhanced direct answer request detection with context awareness (HIGHER PRIORITY)
        direct_answer_context_patterns = [
            "I need you to create", "Could you build", "I want you to make",
            "Please design", "Show me how to", "I want you to design"
        ]
        if any(pattern in input_lower for pattern in direct_answer_context_patterns):
            return "direct_answer_request"

        # ENHANCED PATTERN SYSTEM - Level 3: Specific Pattern Disambiguation

        # 7. Disambiguate "show me" patterns based on context
        if "show me" in input_lower:
            if any(word in input_lower for word in ["exactly", "precisely", "the answer", "the solution", "how to"]):
                return "direct_answer_request"
            elif any(word in input_lower for word in ["examples", "precedents", "case studies", "references"]):
                return "example_request"
            else:
                # Let AI handle ambiguous "show me" cases
                return "unknown"

        # 7.5. Enhanced "can you provide" pattern disambiguation
        if "can you provide" in input_lower:
            if any(word in input_lower for word in ["examples", "precedents", "case studies", "references", "projects", "project", "example"]):
                return "example_request"
            elif any(word in input_lower for word in ["information", "details", "explanation", "help"]):
                return "knowledge_request"
            else:
                # Let AI handle ambiguous "can you provide" cases
                return "unknown"

        # 8. Disambiguate "tell me" patterns based on context
        if "tell me" in input_lower:
            if any(word in input_lower for word in ["exactly", "precisely", "the answer", "the solution"]):
                return "direct_answer_request"
            elif any(word in input_lower for word in ["about", "more", "details", "information"]):
                return "knowledge_request"
            else:
                # Let AI handle ambiguous "tell me" cases
                return "unknown"

        # 9. Disambiguate "what is/are" patterns - ENHANCED: Added "what are" support
        if "what is" in input_lower or "what are" in input_lower:
            # Check if it's asking for technical information
            technical_indicators = ["requirement", "requirements", "standard", "standards", "code", "codes", "regulation", "regulations", "specification", "specifications", "technical", "ada", "ibc", "building code"]
            if any(indicator in input_lower for indicator in technical_indicators):
                return "technical_question"
            else:
                return "knowledge_request"

        # ENHANCED PATTERN SYSTEM - Level 4: Specific Interaction Types

        # 10. Feedback request detection
        feedback_patterns = [
            "feedback", "review", "critique", "evaluate", "assess",
            "what do you think", "how is this", "is this good", "am i on track",
            "what's your take", "your thoughts", "should we", "should i",
            "would you", "do you think", "your opinion", "feedback on"
        ]
        if any(pattern in input_lower for pattern in feedback_patterns):
            return "feedback_request"

        # 11. Technical question detection - FIXED: More specific patterns to avoid false positives
        # FIXED: Make "how to" more specific to avoid catching design questions like "how to organize"
        technical_patterns = [
            "how to calculate", "how to size", "how to specify", "how to meet code",
            "how to comply", "technical", "specification", "requirement", "standard",
            "code", "regulation", "building code", "ada requirement"
        ]
        # Additional check: only classify as technical if it's asking about specific technical procedures
        has_technical_context = any(context in input_lower for context in [
            "calculate", "size", "specify", "code", "standard", "requirement",
            "regulation", "specification", "technical", "engineering"
        ])
        has_technical_pattern = any(pattern in input_lower for pattern in technical_patterns)

        if has_technical_pattern and has_technical_context:
            return "technical_question"

        # 12. Project description detection - HIGH PRIORITY: Detect clear project descriptions (CHECK FIRST)
        project_description_patterns = [
            "i am designing", "i'm designing", "i am working on", "i'm working on",
            "i am creating", "i'm creating", "i am building", "i'm building",
            "my project is", "my design is", "i want to create", "i want to design",
            "i want to build", "i plan to", "i'm planning to", "my goal is",
            "i have a project", "i'm working on a", "this is my project"
        ]
        if any(pattern in input_lower for pattern in project_description_patterns):
            print(f"Input classification: Detected project_description pattern in: {input_text[:100]}...")
            return "project_description"

        # 12.5. Design guidance request detection - HIGH PRIORITY: Detect requests for design help (CHECK SECOND)
        design_guidance_patterns = [
            "can you help me", "could you help me", "i need help with",
            "i want help with", "can you guide me", "could you guide me",
            "i need guidance", "i want guidance", "can you advise me",
            "could you advise me", "i need advice", "i want advice",
            "can you suggest", "could you suggest", "i need suggestions",
            "i want suggestions", "what should i", "how should i",
            # ENHANCED: More flexible patterns to catch variations
            "what should my", "how should my", "what should we", "how should we",
            "what approach should", "how approach should", "what strategy should",
            "how strategy should", "what method should", "how method should",
            "curious how", "wondering how", "thinking about how",
            "not sure how", "unsure how", "confused about how",
            "need help organizing", "want help organizing", "help me organize",
            "guidance on", "advice on", "suggestions for", "help with",
            # ENHANCED: More specific patterns for approach/strategy questions
            "what should my approach", "how should my approach",
            "what approach should i", "how approach should i",
            "what is my approach", "how is my approach",
            "what would be my approach", "how would be my approach",
            "what do you think my approach", "how do you think my approach",
            "approach should", "strategy should", "method should",
            "organize my", "organize the", "organize spaces",
            "organize around", "organize courtyards", "organize gardens"
        ]
        if any(pattern in input_lower for pattern in design_guidance_patterns):
            print(f"Input classification: Detected design_guidance_request pattern in: {input_text[:100]}...")
            return "design_guidance_request"

        # 12.6. Confusion expression detection - ENHANCED: More specific patterns (CHECK LAST)
        confusion_patterns = [
            "confused", "don't understand", "unclear", "not sure",
            "lost", "stuck", "struggling", "difficult",
            "what does this mean", "i don't get it", "i'm confused",
            "this doesn't make sense", "i'm lost", "i'm stuck",
            "this is confusing", "i'm struggling", "this is difficult"
        ]
        if any(pattern in input_lower for pattern in confusion_patterns):
            print(f"Input classification: Detected confusion_expression pattern in: {input_text[:100]}...")
            return "confusion_expression"

        # 13. Improvement seeking detection
        improvement_patterns = [
            "improve", "better", "enhance", "optimize", "refine",
            "make it better", "how can i", "what should i change"
        ]
        if any(pattern in input_lower for pattern in improvement_patterns):
            return "improvement_seeking"

        # 14. Implementation request detection (ENHANCED PATTERNS)
        implementation_patterns = [
            "how do i", "how should i", "what steps", "how to implement",
            "how to start", "how to begin", "what should i do", "what steps should i",
            # ENHANCED: Add design action patterns that indicate user is taking action
            "i'll try", "i will try", "i'm going to", "i plan to",
            "let me try", "i want to try", "i think i'll",
            "first i'll", "next i'll", "then i'll",
            "i'll start by", "i'll begin with", "my approach is",
            "i'm thinking of", "i'd like to test", "i want to explore",
            "shifting the", "moving the", "changing the", "testing a change",
            "trying a different", "experimenting with", "i think the first thing"
        ]
        if any(pattern in input_lower for pattern in implementation_patterns):
            return "implementation_request"

        # ENHANCED PATTERN SYSTEM - Level 5: General Classification

        # 15. Enhanced general statement detection - CONTEXT-AWARE
        # Check for knowledge-seeking patterns first, even with "I am"
        knowledge_seeking_with_i_am = [
            "i am curious", "i am wondering", "i am asking", "i am interested",
            "i am looking for", "i am trying to understand", "i am confused about"
        ]
        if any(pattern in input_lower for pattern in knowledge_seeking_with_i_am):
            return "knowledge_request"

        # Then check for general statements (but exclude knowledge-seeking)
        statement_patterns = [
            "i am working", "i am thinking", "i am planning", "i am designing",
            "i have", "i want", "i need", "i like", "i prefer",
            "this is", "that is", "it is", "there is", "here is"
        ]
        if any(pattern in input_lower for pattern in statement_patterns):
            return "general_statement"

        # 16. Default based on question mark presence
        if "?" in input_text:
            return "general_question"
        else:
            return "general_statement"

    def _is_response_to_previous_question(self, current_input: str, state: ArchMentorState) -> bool:
        """Check if the current input is a response to a previous question from the assistant (FROM FROMOLDREPO)"""

        if not state or not hasattr(state, 'messages') or not state.messages or len(state.messages) < 2:
            return False

        # Get the last assistant message (should be the most recent message)
        last_assistant_message = None
        for message in reversed(state.messages):
            if message.get("role") == "assistant":
                last_assistant_message = message.get("content", "")
                break

        if not last_assistant_message:
            return False

        # Check if the last assistant message contains a question
        assistant_message_lower = last_assistant_message.lower()

        # More precise question detection - check for actual question patterns
        has_question_mark = "?" in last_assistant_message

        # Question words that typically start questions (more specific)
        question_starters = [
            "how", "what", "why", "when", "where", "which", "who",
            "can you", "could you", "would you", "do you", "are you",
            "think about", "consider", "imagine", "suppose", "what if",
            "how might", "what might", "why might", "when might"
        ]

        # Check if any question starter appears at the beginning of a sentence or after punctuation
        has_question_starter = False
        for starter in question_starters:
            # Check if it appears at the start of the message or after sentence-ending punctuation
            if (assistant_message_lower.startswith(starter) or
                f". {starter}" in assistant_message_lower or
                f"? {starter}" in assistant_message_lower or
                f"! {starter}" in assistant_message_lower or
                f": {starter}" in assistant_message_lower):
                has_question_starter = True
                break

        assistant_asked_question = has_question_mark or has_question_starter

        # Now check if the current user input looks like a response
        current_input_lower = current_input.lower()

        # Response indicators in user's message (FROM FROMOLDREPO)
        response_indicators = [
            "i would", "i will", "i think", "i believe", "i feel", "i see",
            "i understand", "i know", "i can", "i should", "i might",
            "yes", "no", "because", "since", "as", "therefore", "however",
            "i would keep", "i would use", "i would add", "i would create",
            "i would highlight", "i would maintain", "i would preserve",
            "i would combine", "i would balance", "i would integrate",
            "interests me the most", "i am most interested in", "i would choose",
            "it's going to be", "it will be", "we've got", "they'll need",
            "it should be", "i like that", "plus it's", "figuring out how to"
        ]

        # Check if user input contains response indicators
        user_gave_response = any(indicator in current_input_lower for indicator in response_indicators)

        return assistant_asked_question and user_gave_response

    def _classify_response_content(self, input_text: str, state: ArchMentorState) -> str:
        """Classify the content of a response to a previous question (FROM FROMOLDREPO)"""

        input_lower = input_text.lower()

        # Enhanced response detection: Check if user is describing their project/ideas
        project_description_indicators = [
            "it's going to be", "it will be", "we've got", "they'll need",
            "it should be", "i like that", "plus it's", "figuring out how to",
            "the main purpose", "the users will be", "the space needs to",
            "i am considering", "i am working on", "my project is",
            "i will place", "i would place", "i'd place", "i'll place",
            "i will organize", "i would organize", "i'd organize", "i'll organize",
            "i will design", "i would design", "i'd design", "i'll design"
        ]

        describing_project = any(indicator in input_lower for indicator in project_description_indicators)

        if describing_project:
            return "design_problem"  # User is describing their design approach

        # Check for other response types
        if any(word in input_lower for word in ["confused", "don't understand", "unclear", "help"]):
            return "confusion_expression"
        elif any(word in input_lower for word in ["example", "examples", "precedent", "case study"]):
            return "example_request"
        elif any(word in input_lower for word in ["what is", "how does", "tell me about"]):
            return "knowledge_request"
        else:
            return "general_statement"
    
    def _detect_understanding_level(self, input_lower: str) -> str:
        """Detect the student's understanding level from their input."""
        try:
            # High understanding indicators
            high_understanding = [
                'i understand', 'makes sense', 'i see how', 'clear', 'obvious',
                'integration', 'relationship', 'connection', 'implication'
            ]
            
            # Low understanding indicators
            low_understanding = [
                'don\'t understand', 'confused', 'unclear', 'what does', 'what is',
                'help me', 'i\'m lost', 'no idea', 'don\'t know'
            ]
            
            # Partial understanding indicators
            partial_understanding = [
                'i think', 'maybe', 'not sure', 'seems like', 'partially',
                'somewhat', 'kind of', 'sort of'
            ]
            
            high_count = sum(1 for indicator in high_understanding if indicator in input_lower)
            low_count = sum(1 for indicator in low_understanding if indicator in input_lower)
            partial_count = sum(1 for indicator in partial_understanding if indicator in input_lower)
            
            if high_count > 0:
                return 'high'
            elif low_count > 0:
                return 'low'
            elif partial_count > 0:
                return 'partial'
            else:
                return 'moderate'
                
        except Exception as e:
            self.telemetry.log_error("_detect_understanding_level", str(e))
            return 'moderate'
    
    def _assess_confidence_level(self, input_lower: str) -> str:
        """Assess the student's confidence level from their input."""
        try:
            # High confidence indicators
            high_confidence = [
                'definitely', 'certainly', 'sure', 'confident', 'know that',
                'obviously', 'clearly', 'without doubt', 'absolutely'
            ]
            
            # Low confidence indicators
            low_confidence = [
                'not sure', 'maybe', 'i think', 'possibly', 'might be',
                'uncertain', 'doubt', 'hesitant', 'worried', 'afraid'
            ]
            
            # Moderate confidence indicators
            moderate_confidence = [
                'believe', 'seems', 'appears', 'likely', 'probably',
                'assume', 'suppose', 'expect'
            ]
            
            high_count = sum(1 for indicator in high_confidence if indicator in input_lower)
            low_count = sum(1 for indicator in low_confidence if indicator in input_lower)
            moderate_count = sum(1 for indicator in moderate_confidence if indicator in input_lower)
            
            if high_count > 0:
                return 'high'
            elif low_count > 0:
                return 'low'
            elif moderate_count > 0:
                return 'moderate'
            else:
                return 'neutral'
                
        except Exception as e:
            self.telemetry.log_error("_assess_confidence_level", str(e))
            return 'neutral'
    
    def _detect_engagement_level(self, input_lower: str, input_text: str) -> str:
        """Detect the student's engagement level from their input."""
        try:
            # High engagement indicators
            high_engagement = [
                'interesting', 'fascinating', 'curious', 'excited', 'love',
                'amazing', 'wonderful', 'explore', 'discover', 'learn more'
            ]
            
            # Low engagement indicators
            low_engagement = [
                'boring', 'tired', 'bored', 'uninteresting', 'don\'t care',
                'whatever', 'fine', 'okay', 'sure'
            ]
            
            # Message length as engagement indicator
            word_count = len(input_text.split())
            question_marks = input_text.count('?')
            exclamation_marks = input_text.count('!')
            
            high_count = sum(1 for indicator in high_engagement if indicator in input_lower)
            low_count = sum(1 for indicator in low_engagement if indicator in input_lower)
            
            # Calculate engagement score
            engagement_score = 0
            
            if high_count > 0:
                engagement_score += 2
            if low_count > 0:
                engagement_score -= 2
            if word_count > 20:
                engagement_score += 1
            if question_marks > 0:
                engagement_score += 1
            if exclamation_marks > 0:
                engagement_score += 1
            
            if engagement_score >= 2:
                return 'high'
            elif engagement_score <= -1:
                return 'low'
            else:
                return 'moderate'
                
        except Exception as e:
            self.telemetry.log_error("_detect_engagement_level", str(e))
            return 'moderate'
    
    def _is_response_to_previous_question(self, current_input: str, state: ArchMentorState) -> bool:
        """Check if current input is a response to a previous question."""
        try:
            if not hasattr(state, 'messages') or not state.messages:
                return False
            
            # Get the last assistant message
            assistant_messages = [msg for msg in state.messages if msg.get('role') == 'assistant']
            if not assistant_messages:
                return False
            
            last_assistant_message = assistant_messages[-1].get('content', '').lower()
            
            # Check if last assistant message contained a question
            question_indicators = ['?', 'what do you think', 'how would you', 'can you', 'would you']
            has_question = any(indicator in last_assistant_message for indicator in question_indicators)
            
            if not has_question:
                return False
            
            # Check if current input is a direct response
            current_lower = current_input.lower()
            response_indicators = [
                'yes', 'no', 'i would', 'i think', 'my answer', 'i believe',
                'in my opinion', 'i feel', 'i suppose', 'i guess'
            ]
            
            return any(indicator in current_lower for indicator in response_indicators)
            
        except Exception as e:
            self.telemetry.log_error("_is_response_to_previous_question", str(e))
            return False
    
    def _is_technical_question(self, input_text: str) -> bool:
        """Check if the input is a technical question."""
        try:
            technical_terms = [
                'calculation', 'formula', 'equation', 'specification', 'standard',
                'code', 'regulation', 'engineering', 'structural', 'mechanical',
                'electrical', 'hvac', 'plumbing', 'foundation', 'load', 'stress',
                'material', 'concrete', 'steel', 'timber', 'insulation'
            ]
            
            input_lower = input_text.lower()
            technical_count = sum(1 for term in technical_terms if term in input_lower)
            
            # Also check for technical question patterns
            technical_patterns = [
                'how to calculate', 'what is the formula', 'how do you design',
                'what are the requirements', 'how do you determine'
            ]
            
            pattern_match = any(pattern in input_lower for pattern in technical_patterns)
            
            return technical_count >= 2 or pattern_match
            
        except Exception as e:
            self.telemetry.log_error("_is_technical_question", str(e))
            return False
    
    def _is_feedback_request(self, input_text: str) -> bool:
        """Check if the input is requesting feedback."""
        try:
            feedback_indicators = [
                'what do you think', 'is this right', 'is this correct', 'feedback',
                'review', 'check', 'evaluate', 'assess', 'critique', 'opinion',
                'thoughts', 'comments', 'suggestions', 'advice'
            ]
            
            input_lower = input_text.lower()
            return any(indicator in input_lower for indicator in feedback_indicators)
            
        except Exception as e:
            self.telemetry.log_error("_is_feedback_request", str(e))
            return False
    
    def _assess_question_complexity(self, input_text: str) -> str:
        """Assess the complexity level of the question."""
        try:
            input_lower = input_text.lower()
            
            # Simple question indicators
            simple_indicators = [
                'what is', 'who is', 'when is', 'where is', 'how do i',
                'can you tell me', 'what does', 'define'
            ]
            
            # Complex question indicators
            complex_indicators = [
                'how would you integrate', 'what are the implications', 'compare and contrast',
                'analyze', 'evaluate', 'synthesize', 'relationship between',
                'why do you think', 'what if', 'how might'
            ]
            
            # Advanced question indicators
            advanced_indicators = [
                'optimization', 'trade-offs', 'systematic approach', 'methodology',
                'framework', 'comprehensive analysis', 'interdisciplinary'
            ]
            
            simple_count = sum(1 for indicator in simple_indicators if indicator in input_lower)
            complex_count = sum(1 for indicator in complex_indicators if indicator in input_lower)
            advanced_count = sum(1 for indicator in advanced_indicators if indicator in input_lower)
            
            # Also consider word count and sentence structure
            word_count = len(input_text.split())
            sentence_count = len([s for s in input_text.split('.') if s.strip()])
            
            if advanced_count > 0 or (word_count > 30 and sentence_count > 2):
                return 'advanced'
            elif complex_count > 0 or (word_count > 15 and sentence_count > 1):
                return 'intermediate'
            elif simple_count > 0 or word_count <= 10:
                return 'basic'
            else:
                return 'intermediate'
                
        except Exception as e:
            self.telemetry.log_error("_assess_question_complexity", str(e))
            return 'intermediate'
    
    def _detect_learning_intent(self, input_text: str) -> str:
        """Detect the student's learning intent."""
        try:
            input_lower = input_text.lower()
            
            # Different learning intents
            understanding_intent = [
                'understand', 'learn', 'explain', 'clarify', 'help me grasp',
                'make sense of', 'comprehend'
            ]
            
            application_intent = [
                'how to apply', 'use in practice', 'implement', 'put into practice',
                'real world', 'practical', 'hands-on'
            ]
            
            exploration_intent = [
                'explore', 'investigate', 'discover', 'find out', 'research',
                'look into', 'examine'
            ]
            
            problem_solving_intent = [
                'solve', 'fix', 'resolve', 'address', 'tackle', 'deal with',
                'overcome', 'handle'
            ]
            
            validation_intent = [
                'validate', 'verify', 'confirm', 'check', 'ensure', 'make sure',
                'is this right', 'am i correct'
            ]
            
            # Count matches for each intent
            intent_scores = {
                'understanding': sum(1 for indicator in understanding_intent if indicator in input_lower),
                'application': sum(1 for indicator in application_intent if indicator in input_lower),
                'exploration': sum(1 for indicator in exploration_intent if indicator in input_lower),
                'problem_solving': sum(1 for indicator in problem_solving_intent if indicator in input_lower),
                'validation': sum(1 for indicator in validation_intent if indicator in input_lower)
            }
            
            # Return the intent with the highest score
            if max(intent_scores.values()) > 0:
                return max(intent_scores, key=intent_scores.get)
            else:
                return 'general_inquiry'
                
        except Exception as e:
            self.telemetry.log_error("_detect_learning_intent", str(e))
            return 'general_inquiry'
    
    def _assess_context_dependency(self, input_text: str, state: ArchMentorState) -> str:
        """Assess how much the input depends on previous context."""
        try:
            input_lower = input_text.lower()
            
            # High context dependency indicators
            high_context = [
                'this', 'that', 'it', 'they', 'them', 'these', 'those',
                'the previous', 'what you said', 'your explanation', 'earlier',
                'before', 'above', 'mentioned'
            ]
            
            # Low context dependency indicators (self-contained)
            low_context = [
                'what is', 'how do', 'can you explain', 'i want to know',
                'tell me about', 'help me understand'
            ]
            
            high_count = sum(1 for indicator in high_context if indicator in input_lower)
            low_count = sum(1 for indicator in low_context if indicator in input_lower)
            
            # Also consider if input is very short (likely context-dependent)
            word_count = len(input_text.split())
            
            if high_count >= 2 or word_count <= 5:
                return 'high'
            elif low_count >= 1 and word_count >= 10:
                return 'low'
            else:
                return 'medium'
                
        except Exception as e:
            self.telemetry.log_error("_assess_context_dependency", str(e))
            return 'medium'
    
    def _calculate_classification_confidence(self, interaction_type: str, understanding_level: str,
                                          confidence_level: str, engagement_level: str) -> float:
        """Calculate confidence in the classification results."""
        try:
            confidence_factors = []
            
            # Interaction type confidence
            if interaction_type in ['help_request', 'information_question', 'confusion_expression']:
                confidence_factors.append(0.8)  # Clear patterns
            else:
                confidence_factors.append(0.6)  # Less clear patterns
            
            # Understanding level confidence
            if understanding_level in ['high', 'low']:
                confidence_factors.append(0.8)  # Clear indicators
            else:
                confidence_factors.append(0.6)  # Moderate indicators
            
            # Confidence level confidence
            if confidence_level in ['high', 'low']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Engagement level confidence
            if engagement_level in ['high', 'low']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            return sum(confidence_factors) / len(confidence_factors)
            
        except Exception as e:
            self.telemetry.log_error("_calculate_classification_confidence", str(e))
            return 0.6
    
    def _get_fallback_classification(self) -> CoreClassification:
        """Return fallback classification when analysis fails."""
        fallback = CoreClassification(
            interaction_type='general_statement',
            understanding_level='moderate',
            confidence_level='neutral',
            engagement_level='moderate',
            is_response_to_question=False,
        )
        fallback.is_technical_question = False
        fallback.is_feedback_request = False
        fallback.question_complexity = 'intermediate'
        fallback.learning_intent = 'general_inquiry'
        fallback.context_dependency = 'medium'
        fallback.classification_confidence = 0.4
        return fallback
    
    def validate_classification(self, classification: CoreClassification) -> bool:
        """Validate the classification results."""
        try:
            # Check required fields
            required_fields = [
                'interaction_type', 'understanding_level', 'confidence_level',
                'engagement_level', 'question_complexity', 'learning_intent'
            ]
            
            for field in required_fields:
                if not hasattr(classification, field) or getattr(classification, field) is None:
                    return False
            
            # Check confidence score
            if not hasattr(classification, 'classification_confidence'):
                return False
            
            confidence = classification.classification_confidence
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                return False
            
            return True
            
        except Exception as e:
            self.telemetry.log_error("validate_classification", str(e))
            return False
    
    def get_classification_summary(self, classification: CoreClassification) -> str:
        """Generate a summary of the classification results."""
        try:
            summary = f"Input Classification Summary:\n"
            summary += f"• Type: {classification.interaction_type}\n"
            summary += f"• Understanding: {classification.understanding_level}\n"
            summary += f"• Confidence: {classification.confidence_level}\n"
            summary += f"• Engagement: {classification.engagement_level}\n"
            summary += f"• Complexity: {classification.question_complexity}\n"
            summary += f"• Intent: {classification.learning_intent}\n"
            summary += f"• Context Dependency: {classification.context_dependency}\n"
            summary += f"• Classification Confidence: {classification.classification_confidence:.2f}"
            
            return summary
            
        except Exception as e:
            self.telemetry.log_error("get_classification_summary", str(e))
            return "Classification summary unavailable."

    async def _get_ai_classification_for_other_metrics(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
        """AI-powered classification for non-interaction-type metrics"""

        # Get conversation context
        recent_context = self._get_recent_context(state)

        prompt = f"""
        Analyze this student's architectural learning state to determine the best educational response:

        CURRENT INPUT: "{input_text}"
        CONVERSATION CONTEXT: {recent_context}
        SKILL LEVEL: {state.student_profile.skill_level if hasattr(state, 'student_profile') else 'intermediate'}
        PROJECT: {getattr(state, 'current_design_brief', 'No project set')}

        Classify the student's input into these clear categories:

        1. INTERACTION TYPE (most important for routing):
        - design_problem: Describing design actions/decisions: "I'm designing", "I will place", "I would organize", "My approach is", "I'd design", "I'll create", "I plan to"
        - example_request: ANY mention of "example", "examples", "project", "projects", "precedent", "case study", "show me", "can you provide", "real project", "built project"
        - feedback_request: Asks for review, feedback, thoughts, critique, evaluation, "what do you think", "how does this look"
        - technical_question: Asks about specific standards, requirements, codes, procedures, "what are the requirements", "how many", "what size", "how do I calculate"
        - confusion_expression: Shows confusion, uncertainty, "I don't understand", "help me", "I'm lost", "unclear", "I don't know how"
        - improvement_seeking: Wants to improve, enhance, fix, "how can I", "ways to improve", "make it better"
        - direct_answer_request: Asking for solutions: "design this for me", "tell me what to do", "give me the answer", "solve this"
        - knowledge_seeking: Asks for information, explanations, "what is", "how do", "can you explain"
        - general_statement: Standard conversation or comments

        2. CONFIDENCE LEVEL:
        - overconfident: Uses absolute terms ("obviously", "clearly", "perfect", "optimal", "best", "ideal", "definitely", "certainly")
        - uncertain: Shows doubt, confusion, asks for help
        - confident: Balanced confidence, thoughtful engagement

        3. UNDERSTANDING LEVEL:
        - low: Basic questions, confusion, misunderstands concepts
        - medium: Partial understanding, makes some connections
        - high: Uses architectural vocabulary correctly, demonstrates conceptual grasp

        4. ENGAGEMENT LEVEL:
        - low: Very short responses (under 5 words), passive language
        - medium: Standard responses, follows prompts
        - high: Detailed responses (15+ words), asks questions, shows curiosity

        Respond in valid JSON format:
        {{
            "interaction_type": "design_problem|example_request|feedback_request|technical_question|confusion_expression|improvement_seeking|direct_answer_request|knowledge_seeking|general_statement",
            "confidence_level": "overconfident|uncertain|confident",
            "understanding_level": "low|medium|high",
            "engagement_level": "low|medium|high",
            "is_example_request": true/false,
            "is_feedback_request": true/false,
            "is_technical_question": true/false,
            "is_design_problem": true/false,
            "shows_confusion": true/false,
            "requests_help": true/false,
            "demonstrates_overconfidence": true/false,
            "reasoning": "brief explanation of classification"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2
            )

            classification_text = response.choices[0].message.content.strip()
            classification = self._parse_ai_classification(classification_text)

            print(f"🔍 AI Learning State Detection:")
            print(f"   Type: {classification['interaction_type']}")
            print(f"   Confidence: {classification['confidence_level']}")
            print(f"   Understanding: {classification['understanding_level']}")
            print(f"   Engagement: {classification['engagement_level']}")
            print(f"   Is Example Request: {classification.get('is_example_request', False)}")
            print(f"   Reasoning: {classification.get('reasoning', 'No reasoning')}")

            return {
                "interaction_type": classification["interaction_type"],
                "understanding_level": classification["understanding_level"],
                "confidence_level": classification["confidence_level"],
                "engagement_level": classification["engagement_level"],
                "overconfidence_score": 2 if classification["confidence_level"] == "overconfident" else 0,
                "is_technical_question": classification["is_technical_question"],
                "is_feedback_request": classification["is_feedback_request"],
                "is_example_request": classification.get("is_example_request", False),
                "shows_confusion": classification["shows_confusion"],
                "requests_help": classification["requests_help"],
                "demonstrates_overconfidence": classification["demonstrates_overconfidence"],
                "seeks_validation": False,
                "classification": "question" if "?" in input_text else "statement",
                "ai_reasoning": classification.get("reasoning", ""),
                "manual_override": False
            }

        except Exception as e:
            print(f"⚠️ AI classification failed, using enhanced fallback: {e}")
            return self._enhanced_fallback_detection(input_text)

    def _get_recent_context(self, state: ArchMentorState) -> str:
        """Get recent conversation context for AI analysis"""

        recent_messages = []
        if hasattr(state, 'messages') and state.messages:
            for msg in state.messages[-3:]:  # Last 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]  # Truncate long messages
                recent_messages.append(f"{role}: {content}")

        return " | ".join(recent_messages) if recent_messages else "No previous conversation"

    def _parse_ai_classification(self, text: str) -> Dict[str, Any]:
        """Parse AI classification response with error handling"""
        import json
        try:
            # Find JSON in response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                parsed = json.loads(json_str)

                # Validate required fields
                required_fields = ["confidence_level", "understanding_level", "engagement_level", "interaction_type"]
                for field in required_fields:
                    if field not in parsed:
                        print(f"⚠️ Missing field {field} in AI response")
                        return self._default_classification()

                return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
        except Exception as e:
            print(f"⚠️ Classification parsing error: {e}")

        return self._default_classification()

    def _enhanced_fallback_detection(self, input_text: str) -> Dict[str, Any]:
        """Enhanced fallback that detects example requests reliably"""

        input_lower = input_text.lower()
        word_count = len(input_text.split())

        # ENHANCED EXAMPLE REQUEST DETECTION - MORE SPECIFIC PATTERNS
        example_patterns = [
            r"\bexample\b", r"\bexamples\b", r"\bprecedent\b", r"\bprecedents\b",
            r"\bcase study\b", r"\bcase studies\b", r"\breference\b", r"\breferences\b",
            r"\breal project\b", r"\bbuilt project\b", r"\bactual project\b", r"\binspiration\b"
        ]

        # Project patterns (only when combined with example keywords)
        project_patterns = [
            r"\bproject\b", r"\bprojects\b", r"\bbuilding\b", r"\bbuildings\b"
        ]

        # Request patterns (only when combined with example keywords)
        request_patterns = [
            r"\bshow me\b", r"\bcan you give\b", r"\bcan you provide\b", r"\bcan you show\b"
        ]

        # Check for example keywords first
        has_example_keywords = any(re.search(pattern, input_lower) for pattern in example_patterns)

        # Check for project/building keywords
        has_project_keywords = any(re.search(pattern, input_lower) for pattern in project_patterns)

        # Check for request patterns
        has_request_patterns = any(re.search(pattern, input_lower) for pattern in request_patterns)

        # Example request is true if:
        # 1. Has explicit example keywords, OR
        # 2. Has project keywords AND request patterns (e.g., "show me projects")
        is_example_request = has_example_keywords or (has_project_keywords and has_request_patterns)

        # OVERCONFIDENCE DETECTION (critical for cognitive enhancement)
        overconfident_indicators = [
            "obviously", "clearly", "definitely", "perfect", "optimal", "best",
            "ideal", "certainly", "absolutely", "undoubtedly", "without question",
            "simple", "easy", "straightforward", "should just", "just need to",
            "only need", "all you do", "simply", "only way", "right way"
        ]
        overconfidence_score = sum(1 for word in overconfident_indicators if word in input_lower)

        # CONFUSION DETECTION (critical for Socratic support)
        confusion_indicators = [
            "confused", "don't understand", "unclear", "help", "lost", "stuck",
            "overwhelmed", "complicated", "difficult to understand"
        ]
        shows_confusion = any(indicator in input_lower for indicator in confusion_indicators)

        # FEEDBACK REQUEST DETECTION (critical for multi-agent routing)
        feedback_indicators = [
            "review my", "feedback on", "thoughts on", "critique", "evaluate",
            "what do you think", "how does this look", "can you review",
            "analyze my", "assess my", "opinion on", "thoughts about"
        ]
        is_feedback_request = any(indicator in input_lower for indicator in feedback_indicators)

        # TECHNICAL QUESTION DETECTION (critical for knowledge-only routing)
        technical_indicators = [
            "requirements for", "standards for", "code for", "regulation",
            "ada requirements", "building codes", "specifications", "guidelines",
            "what are the", "what is the requirement", "how many", "what size"
        ]
        is_technical_question = any(indicator in input_lower for indicator in technical_indicators)

        # HELP REQUEST DETECTION
        help_indicators = ["help me", "can you help", "need help", "assist me", "guidance"]
        requests_help = any(indicator in input_lower for indicator in help_indicators)

        # IMPROVEMENT SEEKING DETECTION
        improvement_indicators = [
            "improve", "better", "enhance", "optimize", "refine",
            "make it better", "how can i", "what should i change"
        ]
        improvement_seeking = any(indicator in input_lower for indicator in improvement_indicators)

        # Check for design problem patterns (FROMOLDREPO style)
        design_problem_indicators = [
            "i'm designing", "i will place", "i would place", "i'd place", "i'll place",
            "i will organize", "i would organize", "i'd organize", "i'll organize",
            "i will design", "i would design", "i'd design", "i'll design",
            "my approach is", "my strategy is", "my plan is", "i plan to",
            # Enhanced patterns for spatial organization and design decisions
            "spatial organization", "organize", "arrangement", "layout",
            "what can i do", "what else can i", "how can i", "how should i",
            "decide about", "decisions about", "choices for", "options for",
            "placement", "positioning", "circulation", "flow"
        ]
        is_design_problem = any(indicator in input_lower for indicator in design_problem_indicators)

        # DETERMINE INTERACTION TYPE - PRIORITIZE DESIGN PROBLEMS
        if is_design_problem:
            interaction_type = "design_problem"
        elif is_example_request:
            interaction_type = "example_request"
        elif is_feedback_request:
            interaction_type = "feedback_request"
        elif is_technical_question:
            interaction_type = "technical_question"
        elif shows_confusion:
            interaction_type = "confusion_expression"
        elif overconfidence_score >= 1:
            interaction_type = "overconfident_statement"
        elif improvement_seeking:
            interaction_type = "improvement_seeking"
        elif requests_help or "?" in input_text:
            interaction_type = "knowledge_seeking"
        else:
            interaction_type = "general_statement"

        # DETERMINE CONFIDENCE LEVEL
        if overconfidence_score >= 1:
            confidence_level = "overconfident"
        elif shows_confusion or requests_help:
            confidence_level = "uncertain"
        else:
            confidence_level = "confident"

        # DETERMINE ENGAGEMENT LEVEL
        if word_count < 5 or any(word in input_lower for word in ["ok", "sure", "fine", "whatever"]):
            engagement_level = "low"
        elif word_count > 15 or "?" in input_text:
            engagement_level = "high"
        else:
            engagement_level = "medium"

        # DETERMINE UNDERSTANDING LEVEL (simple heuristic)
        technical_terms = ["accessibility", "circulation", "program", "design", "architecture", "building"]
        tech_usage = sum(1 for term in technical_terms if term in input_lower)

        if shows_confusion or tech_usage == 0:
            understanding_level = "low"
        elif tech_usage >= 2:
            understanding_level = "high"
        else:
            understanding_level = "medium"

        return {
            "interaction_type": interaction_type,
            "understanding_level": understanding_level,
            "confidence_level": confidence_level,
            "engagement_level": engagement_level,
            "overconfidence_score": overconfidence_score,
            "is_technical_question": is_technical_question,
            "is_feedback_request": is_feedback_request,
            "is_example_request": is_example_request,
            "is_design_problem": is_design_problem,  # ← ADDED THIS
            "shows_confusion": shows_confusion,
            "requests_help": requests_help,
            "demonstrates_overconfidence": overconfidence_score >= 1,
            "seeks_validation": False,
            "classification": "question" if "?" in input_text else "statement",
            "ai_reasoning": "Enhanced fallback classification used"
        }

    def _default_classification(self) -> Dict[str, Any]:
        """Safe default when all else fails"""
        return {
            "confidence_level": "confident",
            "understanding_level": "medium",
            "engagement_level": "medium",
            "interaction_type": "general_statement",
            "overconfidence_score": 0,
            "is_technical_question": False,
            "is_feedback_request": False,
            "is_example_request": False,
            "shows_confusion": False,
            "requests_help": False,
            "demonstrates_overconfidence": False,
            "seeks_validation": False,
            "reasoning": "Default classification"
        }

    def _extract_building_type_from_text(self, input_text: str) -> str:
        """
        Get building type from state - NO MORE DETECTION, just retrieval.
        Building type is now centrally managed in conversation_progression.py
        """
        # This method is now deprecated - building type detection is centralized
        # Return unknown to force use of centrally managed building type
        return "unknown"