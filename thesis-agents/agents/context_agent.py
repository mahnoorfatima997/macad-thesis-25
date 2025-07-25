# agents/context_agent.py - NEW FILE implementing Context Reasoning Logic
from typing import Dict, Any, List, Optional, Tuple
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState

load_dotenv()

class ContextAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "context_agent"
        
        # Initialize context analysis patterns
        self.analysis_patterns = self._initialize_analysis_patterns()
        
        print(f"🔍 {self.name} initialized for domain: {domain}")
    
    def _initialize_analysis_patterns(self) -> Dict[str, List[str]]:
        """Initialize linguistic and behavioral analysis patterns"""
        
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


    def _get_recent_context(self, state: ArchMentorState) -> str:
        """Get recent conversation context for AI analysis"""
        
        recent_messages = []
        for msg in state.messages[-3:]:  # Last 3 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # Truncate long messages
            recent_messages.append(f"{role}: {content}")
        
        return " | ".join(recent_messages) if recent_messages else "No previous conversation"



    async def analyze_student_input(self, state: ArchMentorState, current_input: str) -> Dict[str, Any]:
        """Main context analysis function - transforms raw input into rich context"""
        
        print(f"\n🔍 {self.name}: Analyzing student input...")
        print(f"   Input: {current_input[:100]}...")
        
        # CORE CLASSIFICATION
        core_classification = await self._perform_core_classification(current_input, state)  # <-- FIXED
        
        # CONTENT ANALYSIS
        content_analysis = self._perform_content_analysis(current_input, state)
        
        # CONTEXTUAL METADATA
        contextual_metadata = self._generate_contextual_metadata(current_input, state, core_classification)
        
        # CONVERSATION PATTERN ANALYSIS
        conversation_patterns = self._analyze_conversation_patterns(state, current_input)
        
        # ROUTING PREPARATION
        routing_suggestions = self._prepare_routing_suggestions(
            core_classification, content_analysis, conversation_patterns
        )
        
        # AGENT-SPECIFIC CONTEXT PREPARATION
        agent_contexts = self._prepare_agent_contexts(
            core_classification, content_analysis, state, current_input
        )
        
        # COMPILE COMPLETE CONTEXT PACKAGE
        context_package = {
            "core_classification": core_classification,
            "content_analysis": content_analysis,
            "contextual_metadata": contextual_metadata,
            "conversation_patterns": conversation_patterns,
            "routing_suggestions": routing_suggestions,
            "agent_contexts": agent_contexts,
            "context_quality": self._assess_context_quality(core_classification, content_analysis),
            "timestamp": self._get_current_timestamp(),
            "agent": self.name
        }
        
        print(f"   ✅ Context analysis complete")
        print(f"   🎯 Interaction type: {core_classification['interaction_type']}")
        print(f"   📊 Understanding: {core_classification['understanding_level']}")
        print(f"   💭 Confidence: {core_classification['confidence_level']}")
        print(f"   ⚡ Engagement: {core_classification['engagement_level']}")
        
        return context_package
    
    #super enhanced AI-powered classification for learning state detection
    async def _perform_core_classification(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
        """Complete AI-powered learning state detection - replaces ALL hard-coding"""
        
        # Get conversation context
        recent_context = self._get_recent_context(state)
        
        prompt = f"""
        Analyze this student's architectural learning state to determine cognitive enhancement needs:
        
        CURRENT INPUT: "{input_text}"
        CONVERSATION CONTEXT: {recent_context}
        SKILL LEVEL: {state.student_profile.skill_level}
        PROJECT: {getattr(state, 'current_design_brief', 'No project set')}
        
        Detect these critical learning states that require specific educational interventions:
        
        1. CONFIDENCE LEVEL (key for cognitive enhancement):
        - overconfident: Uses absolute terms ("obviously", "clearly", "perfect", "optimal", "best", "ideal", "definitely")
        - uncertain: Shows doubt, confusion ("confused", "don't understand", "help", "unclear", "lost", "not sure")
        - confident: Balanced confidence, thoughtful engagement
        
        2. UNDERSTANDING LEVEL (key for Socratic guidance):
        - low: Basic questions, confusion, misunderstands concepts, asks "what is" questions
        - medium: Partial understanding, makes some connections, uses some technical terms correctly
        - high: Uses architectural vocabulary correctly, demonstrates conceptual grasp, makes connections
        
        3. ENGAGEMENT LEVEL (key for re-engagement strategies):
        - low: Very short responses (under 5 words), passive language ("ok", "sure", "fine", "whatever")
        - medium: Standard responses, follows prompts, moderate length
        - high: Detailed responses (15+ words), asks questions, shows curiosity, elaborates
        
        4. INTERACTION TYPE (key for routing):
        - - confusion_expression: ANY indication of confusion, uncertainty, or asking for help ("I don't know", "can you help", "I'm confused", "help me", "I'm lost")
        - overconfident_statement: Makes absolute claims without justification
        - feedback_request: Asks for evaluation, review, critique, or opinions
        - technical_question: Asks about specific standards, requirements, codes, or procedures
        - improvement_seeking: Wants to enhance, fix, or better something specific
        - knowledge_seeking: Asks for information, examples, precedents, or explanations
        - general_statement: Standard conversation or comments
        
        5. SPECIAL INDICATORS:
        - shows_confusion: Any indication of being lost or overwhelmed
        - requests_help: Explicitly or implicitly asks for assistance
        - demonstrates_overconfidence: Uses language indicating excessive certainty
        - seeks_validation: Wants confirmation or approval
        
        Be sensitive to subtle expressions. A student saying "I think this approach might work" shows uncertainty, while "This is obviously the best solution" shows overconfidence.
        
        Respond in valid JSON format:
        {{
            "confidence_level": "overconfident|uncertain|confident",
            "understanding_level": "low|medium|high",
            "engagement_level": "low|medium|high",
            "interaction_type": "confusion_expression|overconfident_statement|feedback_request|technical_question|improvement_seeking|knowledge_seeking|general_statement",
            "shows_confusion": false,
            "requests_help": false,
            "demonstrates_overconfidence": false,
            "seeks_validation": false,
            "overconfidence_score": 0,
            "is_technical_question": false,
            "is_feedback_request": false,
            "reasoning": "brief explanation of classification"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            
            classification_text = response.choices[0].message.content.strip()
            classification = self._parse_ai_classification(classification_text)
            
            print(f"🔍 AI Learning State Detection:")
            print(f"   Confidence: {classification['confidence_level']}")
            print(f"   Understanding: {classification['understanding_level']}")
            print(f"   Engagement: {classification['engagement_level']}")
            print(f"   Type: {classification['interaction_type']}")
            print(f"   Reasoning: {classification.get('reasoning', 'No reasoning')}")
            
            return {
                "interaction_type": classification["interaction_type"],
                "understanding_level": classification["understanding_level"],
                "confidence_level": classification["confidence_level"],
                "engagement_level": classification["engagement_level"],
                "overconfidence_score": 2 if classification["confidence_level"] == "overconfident" else 0,
                "is_technical_question": classification["is_technical_question"],
                "is_feedback_request": classification["is_feedback_request"],
                "shows_confusion": classification["shows_confusion"],
                "requests_help": classification["requests_help"],
                "demonstrates_overconfidence": classification["demonstrates_overconfidence"],
                "seeks_validation": classification["seeks_validation"],
                "classification": "question" if "?" in input_text else "statement",
                "ai_reasoning": classification.get("reasoning", "")
            }
            
        except Exception as e:
            print(f"⚠️ AI classification failed, using enhanced fallback: {e}")
            return self._enhanced_fallback_detection(input_text)

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
        """Enhanced fallback that still detects key learning states"""
        
        input_lower = input_text.lower()
        word_count = len(input_text.split())
        
        # OVERCONFIDENCE DETECTION (critical for cognitive enhancement)
        overconfident_indicators = [
            "obviously", "clearly", "definitely", "perfect", "optimal", "best", 
            "ideal", "certainly", "absolutely", "undoubtedly", "without question"
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
            "improve", "better", "enhance", "fix", "upgrade", "optimize",
            "make it better", "how can i", "ways to improve"
        ]
        improvement_seeking = any(indicator in input_lower for indicator in improvement_indicators)
        
        # DETERMINE INTERACTION TYPE
        if is_feedback_request:
            interaction_type = "feedback_request"
        elif is_technical_question:
            interaction_type = "technical_question"
        elif shows_confusion:
            interaction_type = "confusion_expression"
        elif overconfidence_score >= 1:
            interaction_type = "overconfident_statement"
        elif improvement_seeking:
            interaction_type = "improvement_seeking"
        elif "?" in input_text:
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
            "shows_confusion": shows_confusion,
            "requests_help": requests_help,
            "demonstrates_overconfidence": overconfidence_score >= 1,
            "seeks_validation": False,
            "classification": "question" if "?" in input_text else "statement",
            "ai_reasoning": "Fallback classification used"
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
            "shows_confusion": False,
            "requests_help": False,
            "demonstrates_overconfidence": False,
            "seeks_validation": False,
            "reasoning": "Default classification"
        }








    
    def _classify_interaction_type(self, input_text: str) -> str:
        """Classify the type of interaction"""
        
        input_lower = input_text.lower()
        
        # Feedback requests
        if any(word in input_lower for word in ["review", "feedback", "thoughts", "evaluate", 
                                               "critique", "assess", "analyze my", "check my"]):
            return "feedback_request"
        
        # Improvement seeking
        if any(word in input_lower for word in ["improve", "better", "enhance", "fix", 
                                               "upgrade", "optimize"]):
            return "improvement_seeking"
        
        # Knowledge seeking
        if any(word in input_lower for word in ["precedents", "examples", "standards", 
                                               "requirements", "what are", "how do"]):
            return "knowledge_seeking"
        
        # Overconfident statements
        if any(word in input_lower for word in ["perfect", "optimal", "best", "obviously", 
                                               "clearly", "ideal"]):
            return "overconfident_statement"
        
        # Confusion expression
        if any(word in input_lower for word in ["confused", "unclear", "don't understand", 
                                               "lost", "help"]):
            return "confusion_expression"
        
        # Direct questions
        if "?" in input_text:
            return "direct_question"
        
        return "general_statement"
    
    def _detect_understanding_level(self, input_lower: str) -> str:
        """Detect understanding level from linguistic indicators"""
        
        # Count indicators for each level
        low_score = sum(1 for indicator in self.analysis_patterns["low_understanding"] 
                       if indicator in input_lower)
        medium_score = sum(1 for indicator in self.analysis_patterns["medium_understanding"] 
                          if indicator in input_lower)
        high_score = sum(1 for indicator in self.analysis_patterns["high_understanding"] 
                        if indicator in input_lower)
        
        # Determine level based on scores
        if high_score >= 2 or (high_score >= 1 and medium_score == 0 and low_score == 0):
            return "high"
        elif low_score >= 2 or (low_score >= 1 and medium_score == 0 and high_score == 0):
            return "low"
        else:
            return "medium"
    
    def _assess_confidence_level(self, input_lower: str) -> str:
        """Assess confidence level from language patterns"""
        
        # Count confidence indicators
        uncertain_score = sum(1 for indicator in self.analysis_patterns["uncertain"] 
                             if indicator in input_lower)
        confident_score = sum(1 for indicator in self.analysis_patterns["confident"] 
                             if indicator in input_lower)
        overconfident_score = sum(1 for indicator in self.analysis_patterns["overconfident"] 
                                 if indicator in input_lower)
        
        # Determine confidence level
        if overconfident_score >= 1:
            return "overconfident"
        elif uncertain_score >= 1:
            return "uncertain"
        elif confident_score >= 1:
            return "confident"
        else:
            return "uncertain"  # Default for ambiguous cases
    
    def _detect_engagement_level(self, input_lower: str, input_text: str) -> str:
        """Detect engagement level from multiple indicators"""
        
        # Word count indicator
        word_count = len(input_text.split())
        
        # Linguistic engagement indicators
        high_engagement_score = sum(1 for indicator in self.analysis_patterns["high_engagement"] 
                                   if indicator in input_lower)
        low_engagement_score = sum(1 for indicator in self.analysis_patterns["low_engagement"] 
                                  if indicator in input_lower)
        
        # Question indicators
        has_questions = "?" in input_text
        
        # Determine engagement level
        if high_engagement_score >= 1 or (word_count > 20 and has_questions):
            return "high"
        elif low_engagement_score >= 1 or word_count < 5:
            return "low"
        else:
            return "medium"
    
    def _calculate_overconfidence_score(self, input_lower: str) -> int:
        """Calculate overconfidence score for routing decisions"""
        
        overconfident_indicators = self.analysis_patterns["overconfident"]
        return sum(1 for indicator in overconfident_indicators if indicator in input_lower)
    
    def _is_technical_question(self, input_text: str) -> bool:
        """Detect if input is a technical question"""
        
        technical_patterns = [
            "ada requirements", "door width", "accessibility", "building code",
            "structural", "hvac", "lighting", "materials", "specifications"
        ]
        
        return any(pattern in input_text.lower() for pattern in technical_patterns)
    
    def _is_feedback_request(self, input_text: str) -> bool:
        """Detect if input is requesting feedback"""
        
        feedback_patterns = [
            "review my", "feedback on", "thoughts on", "critique", "evaluate", 
            "what do you think", "how does this look", "can you review",
            "analyze my plan", "analyze my design", "look at my"
        ]
        
        return any(pattern in input_text.lower() for pattern in feedback_patterns)
    
    def _perform_content_analysis(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze content characteristics of the input"""
        
        return {
            "word_count": len(input_text.split()),
            "sentence_count": len([s for s in input_text.split('.') if s.strip()]),
            "question_count": input_text.count('?'),
            "technical_terms": self._extract_technical_terms(input_text),
            "emotional_indicators": self._extract_emotional_indicators(input_text),
            "complexity_score": self._assess_complexity(input_text),
            "specificity_score": self._assess_specificity(input_text, state)
        }
    
    def _extract_technical_terms(self, input_text: str) -> List[str]:
        """Extract domain-specific technical terms"""
        
        if self.domain == "architecture":
            arch_terms = [
                "accessibility", "ada", "circulation", "program", "zoning",
                "site plan", "floor plan", "elevation", "section", "massing",
                "fenestration", "facade", "structural", "hvac", "lighting"
            ]
            return [term for term in arch_terms if term in input_text.lower()]
        
        return []
    
    def _extract_emotional_indicators(self, input_text: str) -> Dict[str, int]:
        """Extract and count emotional indicators"""
        
        input_lower = input_text.lower()
        
        return {
            "confusion": sum(1 for indicator in self.analysis_patterns["confusion"] 
                           if indicator in input_lower),
            "frustration": sum(1 for indicator in self.analysis_patterns["frustration"] 
                             if indicator in input_lower),
            "enthusiasm": sum(1 for indicator in self.analysis_patterns["enthusiasm"] 
                            if indicator in input_lower)
        }
    
    def _assess_complexity(self, input_text: str) -> float:
        """Assess complexity of the input"""
        
        # Simple complexity metrics
        word_count = len(input_text.split())
        unique_words = len(set(input_text.lower().split()))
        avg_word_length = sum(len(word) for word in input_text.split()) / max(word_count, 1)
        
        # Normalize complexity score (0-1)
        complexity = min((word_count / 50) + (unique_words / word_count) + (avg_word_length / 10), 1.0)
        
        return complexity
    
    def _assess_specificity(self, input_text: str, state: ArchMentorState) -> float:
        """Assess how specific the input is to the current project"""
        
        if not hasattr(state, 'current_design_brief') or not state.current_design_brief:
            return 0.5
        
        brief_words = set(state.current_design_brief.lower().split())
        input_words = set(input_text.lower().split())
        
        # Calculate overlap
        overlap = len(brief_words.intersection(input_words))
        specificity = overlap / max(len(input_words), 1)
        
        return min(specificity, 1.0)
    
    def _generate_contextual_metadata(self, input_text: str, state: ArchMentorState, classification: Dict) -> Dict[str, Any]:
        """Generate contextual metadata for orchestrator decisions"""
        
        return {
            "complexity_appropriateness": self._assess_complexity_appropriateness(
                classification, state
            ),
            "response_urgency": self._assess_response_urgency(classification),
            "pedagogical_opportunity": self._identify_pedagogical_opportunity(
                classification, input_text
            ),
            "continuation_cues": self._identify_continuation_cues(state, input_text),
            "difficulty_adjustment_needed": self._assess_difficulty_adjustment(
                classification, state
            )
        }
    
    def _assess_complexity_appropriateness(self, classification: Dict, state: ArchMentorState) -> str:
        """Assess if input complexity matches student level"""
        
        student_level = state.student_profile.skill_level
        understanding_level = classification["understanding_level"]
        
        level_mapping = {"beginner": "low", "intermediate": "medium", "advanced": "high"}
        expected_level = level_mapping.get(student_level, "medium")
        
        if understanding_level == expected_level:
            return "appropriate"
        elif understanding_level < expected_level:
            return "below_level"
        else:
            return "above_level"
    
    def _assess_response_urgency(self, classification: Dict) -> str:
        """Assess urgency of response needed"""
        
        if classification["interaction_type"] == "confusion_expression":
            return "high"
        elif classification["is_feedback_request"]:
            return "medium"
        else:
            return "low"
    
    def _identify_pedagogical_opportunity(self, classification: Dict, input_text: str) -> str:
        """Identify specific learning opportunities"""
        
        if classification["confidence_level"] == "overconfident":
            return "challenge_assumptions"
        elif classification["understanding_level"] == "low":
            return "build_foundation"
        elif classification["interaction_type"] == "knowledge_seeking":
            return "provide_guided_discovery"
        else:
            return "deepen_understanding"
    
    def _identify_continuation_cues(self, state: ArchMentorState, input_text: str) -> List[str]:
        """Identify cues for continuing the learning thread"""
        
        cues = []
        
        # Check for topic references to previous conversation
        if len(state.messages) > 0:
            recent_topics = self._extract_topics_from_recent_messages(state)
            input_topics = self._extract_topics_from_text(input_text)
            
            if any(topic in input_topics for topic in recent_topics):
                cues.append("topic_continuation")
        
        # Check for building on previous insights
        if any(word in input_text.lower() for word in ["building on", "based on", "following up"]):
            cues.append("insight_building")
        
        return cues
    
    def _assess_difficulty_adjustment(self, classification: Dict, state: ArchMentorState) -> str:
        """Assess if difficulty level needs adjustment"""
        
        if classification["confidence_level"] == "uncertain" and classification["understanding_level"] == "low":
            return "decrease_difficulty"
        elif classification["engagement_level"] == "low":
            return "increase_engagement"
        elif classification["confidence_level"] == "overconfident":
            return "increase_challenge"
        else:
            return "maintain_level"
    
    def _analyze_conversation_patterns(self, state: ArchMentorState, current_input: str) -> Dict[str, Any]:
        """Analyze patterns in conversation flow"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        return {
            "repetitive_topics": self._detect_repetitive_topics(user_messages + [current_input]),
            "topic_jumping": self._detect_topic_jumping(user_messages + [current_input]),
            "engagement_trend": self._analyze_engagement_trend(user_messages + [current_input]),
            "understanding_progression": self._analyze_understanding_progression(
                user_messages + [current_input]
            ),
            "conversation_depth": len(user_messages) + 1,
            "recent_focus": self._identify_recent_focus(user_messages[-3:] + [current_input])
        }
    
    def _detect_repetitive_topics(self, messages: List[str]) -> bool:
        """Detect if student is stuck on same topics"""
        
        if len(messages) < 3:
            return False
        
        # Extract key topics from each message
        topics = []
        for msg in messages[-3:]:  # Last 3 messages
            msg_topics = self._extract_topics_from_text(msg)
            topics.extend(msg_topics)
        
        # Check for repetition
        if len(topics) > 0:
            unique_ratio = len(set(topics)) / len(topics)
            return unique_ratio < 0.5
        
        return False
    
    def _detect_topic_jumping(self, messages: List[str]) -> bool:
        """Detect if student is jumping between topics without depth"""
        
        if len(messages) < 3:
            return False
        
        topics_per_message = []
        for msg in messages[-3:]:
            topics = self._extract_topics_from_text(msg)
            topics_per_message.append(set(topics))
        
        # Check for low overlap between consecutive messages
        overlaps = []
        for i in range(len(topics_per_message) - 1):
            current_topics = topics_per_message[i]
            next_topics = topics_per_message[i + 1]
            
            if len(current_topics) > 0 and len(next_topics) > 0:
                overlap = len(current_topics.intersection(next_topics)) / len(current_topics.union(next_topics))
                overlaps.append(overlap)
        
        if overlaps:
            avg_overlap = sum(overlaps) / len(overlaps)
            return avg_overlap < 0.3
        
        return False
    
    def _analyze_engagement_trend(self, messages: List[str]) -> str:
        """Analyze trend in engagement over recent messages"""
        
        if len(messages) < 3:
            return "stable"
        
        # Calculate engagement scores for recent messages
        engagement_scores = []
        for msg in messages[-3:]:
            word_count = len(msg.split())
            has_questions = "?" in msg
            enthusiasm_words = sum(1 for word in self.analysis_patterns["high_engagement"] 
                                 if word in msg.lower())
            
            score = word_count / 20 + (2 if has_questions else 0) + enthusiasm_words
            engagement_scores.append(score)
        
        # Determine trend
        if len(engagement_scores) >= 2:
            if engagement_scores[-1] > engagement_scores[-2] * 1.3:
                return "increasing"
            elif engagement_scores[-1] < engagement_scores[-2] * 0.7:
                return "decreasing"
        
        return "stable"
    
    def _analyze_understanding_progression(self, messages: List[str]) -> str:
        """Analyze progression in demonstrated understanding"""
        
        if len(messages) < 3:
            return "stable"
        
        # Analyze complexity progression
        complexity_scores = []
        for msg in messages[-3:]:
            technical_terms = len(self._extract_technical_terms(msg))
            unique_words = len(set(msg.lower().split()))
            total_words = len(msg.split())
            
            complexity = (technical_terms * 2 + unique_words) / max(total_words, 1)
            complexity_scores.append(complexity)
        
        # Determine progression
        if len(complexity_scores) >= 2:
            if complexity_scores[-1] > complexity_scores[-2] * 1.2:
                return "progressing"
            elif complexity_scores[-1] < complexity_scores[-2] * 0.8:
                return "regressing"
        
        return "stable"
    
    def _identify_recent_focus(self, recent_messages: List[str]) -> List[str]:
        """Identify key focus areas from recent messages"""
        
        all_topics = []
        for msg in recent_messages:
            topics = self._extract_topics_from_text(msg)
            all_topics.extend(topics)
        
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Return most frequent topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:3]]
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract key topics from text"""
        
        # Simple keyword extraction for architecture domain
        arch_topics = [
            "accessibility", "lighting", "circulation", "space", "design",
            "layout", "structure", "materials", "facade", "entrance",
            "community", "public", "private", "program", "zoning"
        ]
        
        text_lower = text.lower()
        found_topics = [topic for topic in arch_topics if topic in text_lower]
        
        return found_topics
    
    def _extract_topics_from_recent_messages(self, state: ArchMentorState) -> List[str]:
        """Extract topics from recent conversation"""
        
        recent_messages = [msg['content'] for msg in state.messages[-3:] 
                          if msg.get('role') == 'user']
        
        all_topics = []
        for msg in recent_messages:
            topics = self._extract_topics_from_text(msg)
            all_topics.extend(topics)
        
        return list(set(all_topics))
    
    def _prepare_routing_suggestions(self, classification: Dict, content_analysis: Dict, patterns: Dict) -> Dict[str, Any]:
        """Prepare routing suggestions for orchestrator"""
        
        suggestions = {
            "primary_route": "default",
            "confidence": 0.5,
            "reasoning": [],
            "alternative_routes": []
        }
        
        # Determine primary route based on classification
        if classification["is_technical_question"] and classification["understanding_level"] == "high":
            suggestions["primary_route"] = "knowledge_only"
            suggestions["confidence"] = 0.8
            suggestions["reasoning"].append("High understanding + technical question")
        
        elif classification["confidence_level"] == "overconfident":
            suggestions["primary_route"] = "cognitive_challenge"
            suggestions["confidence"] = 0.9
            suggestions["reasoning"].append("Overconfident student needs challenge")
        
        elif classification["interaction_type"] == "confusion_expression":
            suggestions["primary_route"] = "socratic_focus"
            suggestions["confidence"] = 0.8
            suggestions["reasoning"].append("Student expressing confusion")
        
        elif classification["is_feedback_request"]:
            suggestions["primary_route"] = "multi_agent"
            suggestions["confidence"] = 0.7
            suggestions["reasoning"].append("Comprehensive feedback requested")
        
        else:
            suggestions["primary_route"] = "default"
            suggestions["confidence"] = 0.6
            suggestions["reasoning"].append("Standard interaction pattern")
        
        # Add alternative routes
        if suggestions["primary_route"] != "socratic_focus":
            suggestions["alternative_routes"].append("socratic_focus")
        if suggestions["primary_route"] != "multi_agent":
            suggestions["alternative_routes"].append("multi_agent")
        
        return suggestions
    
    def _prepare_agent_contexts(self, classification: Dict, content_analysis: Dict, state: ArchMentorState, input_text: str) -> Dict[str, Dict[str, Any]]:
        """Prepare context packages for each agent type"""
        
        return {
            "knowledge_agent": {
                "information_gaps": self._identify_information_gaps(input_text),
                "complexity_level": classification["understanding_level"],
                "specificity_needed": content_analysis["specificity_score"]
            },
            "socratic_agent": {
                "questioning_level": classification["understanding_level"],
                "confidence_context": classification["confidence_level"],
                "engagement_context": classification["engagement_level"],
                "optimal_question_type": self._suggest_question_type(classification)
            },
            "cognitive_agent": {
                "challenge_readiness": self._assess_challenge_readiness(classification),
                "overconfidence_level": classification["overconfidence_score"],
                "engagement_level": classification["engagement_level"],
                "recommended_challenge_type": self._suggest_challenge_type(classification)
            },
            "analysis_agent": {
                "focus_areas": self._identify_analysis_focus_areas(input_text, state),
                "depth_level": classification["understanding_level"],
                "context_history": self._summarize_context_history(state)
            }
        }
    
    def _identify_information_gaps(self, input_text: str) -> List[str]:
        """Identify information gaps for knowledge agent"""
        
        gaps = []
        
        if "accessibility" in input_text.lower():
            gaps.append("accessibility_standards")
        if "lighting" in input_text.lower():
            gaps.append("lighting_design")
        if "space" in input_text.lower() or "layout" in input_text.lower():
            gaps.append("spatial_organization")
        
        return gaps
    
    def _suggest_question_type(self, classification: Dict) -> str:
        """Suggest optimal question type for Socratic agent"""
        
        if classification["understanding_level"] == "low":
            return "clarification"
        elif classification["confidence_level"] == "overconfident":
            return "challenging"
        elif classification["engagement_level"] == "high":
            return "analytical"
        else:
            return "exploratory"
    
    def _assess_challenge_readiness(self, classification: Dict) -> str:
        """Assess readiness for cognitive challenges"""
        
        if classification["confidence_level"] == "overconfident":
            return "high"
        elif classification["engagement_level"] == "low":
            return "medium"
        else:
            return "low"
    
    def _suggest_challenge_type(self, classification: Dict) -> str:
        """Suggest challenge type for cognitive agent"""
        
        if classification["confidence_level"] == "overconfident":
            return "perspective_shifts"
        elif classification["engagement_level"] == "low":
            return "constraint_changes"
        else:
            return "metacognitive_prompts"
    
    def _identify_analysis_focus_areas(self, input_text: str, state: ArchMentorState) -> List[str]:
        """Identify focus areas for analysis agent"""
        
        focus_areas = []
        
        # Based on input content
        if "design" in input_text.lower():
            focus_areas.append("design_analysis")
        if "space" in input_text.lower():
            focus_areas.append("spatial_analysis")
        if "user" in input_text.lower() or "people" in input_text.lower():
            focus_areas.append("user_analysis")
        
        return focus_areas
    
    def _summarize_context_history(self, state: ArchMentorState) -> Dict[str, Any]:
        """Summarize conversation context history"""
        
        return {
            "conversation_length": len(state.messages),
            "recent_topics": self._extract_topics_from_recent_messages(state),
            "skill_progression": getattr(state.student_profile, 'skill_level', 'intermediate')
        }
    
    def _assess_context_quality(self, classification: Dict, content_analysis: Dict) -> float:
        """Assess overall quality of context analysis"""
        
        quality_score = 0.0
        
        # Classification confidence
        if classification["understanding_level"] in ["low", "medium", "high"]:
            quality_score += 0.25
        
        # Content richness
        if content_analysis["word_count"] > 5:
            quality_score += 0.25
        
        # Emotional clarity
        emotional_indicators = content_analysis.get("emotional_indicators", {})
        if any(score > 0 for score in emotional_indicators.values()):
            quality_score += 0.25
        
        # Technical relevance
        if len(content_analysis.get("technical_terms", [])) > 0:
            quality_score += 0.25
        
        return quality_score
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for context tracking"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def validate_context_analysis(self, context_package: Dict[str, Any]) -> Dict[str, Any]:
        """Validate context analysis for quality assurance"""
        
        validation_results = {
            "classification_consistency": self._check_classification_consistency(
                context_package["core_classification"]
            ),
            "complexity_appropriateness": self._check_complexity_appropriateness(
                context_package["core_classification"],
                context_package["content_analysis"]
            ),
            "routing_logic": self._check_routing_logic(
                context_package["routing_suggestions"],
                context_package["core_classification"]
            ),
            "overall_quality": context_package["context_quality"],
            "validation_passed": True
        }
        
        # Check if validation passed
        if (validation_results["classification_consistency"] and 
            validation_results["complexity_appropriateness"] and 
            validation_results["overall_quality"] > 0.5):
            validation_results["validation_passed"] = True
        else:
            validation_results["validation_passed"] = False
        
        return validation_results
    
    def _check_classification_consistency(self, classification: Dict) -> bool:
        """Check if classifications are internally consistent"""
        
        # Example consistency checks
        if (classification["confidence_level"] == "overconfident" and 
            classification["understanding_level"] == "low"):
            return False  # Inconsistent: can't be overconfident with low understanding
        
        if (classification["engagement_level"] == "high" and 
            classification["interaction_type"] == "general_statement" and
            classification.get("word_count", 0) < 5):
            return False  # Inconsistent: high engagement but very short input
        
        return True
    
    def _check_complexity_appropriateness(self, classification: Dict, content_analysis: Dict) -> bool:
        """Check if complexity assessment is appropriate"""
        
        complexity = content_analysis.get("complexity_score", 0)
        understanding = classification["understanding_level"]
        
        # Check for reasonable complexity-understanding alignment
        if understanding == "low" and complexity > 0.8:
            return False  # Too complex for low understanding
        
        if understanding == "high" and complexity < 0.2:
            return False  # Too simple for high understanding
        
        return True
    
    def _check_routing_logic(self, routing_suggestions: Dict, classification: Dict) -> bool:
        """Check if routing suggestions are logical"""
        
        primary_route = routing_suggestions.get("primary_route")
        confidence_level = classification.get("confidence_level")
        
        # Check logical routing decisions
        if confidence_level == "overconfident" and primary_route != "cognitive_challenge":
            return False  # Should route overconfident students to cognitive challenge
        
        if classification.get("is_technical_question") and primary_route == "cognitive_challenge":
            return False  # Technical questions shouldn't go to cognitive challenge
        
        return True

# Test function
async def test_context_agent():
    print("🧪 Testing Context Agent...")
    
    # Create test state
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people with accessible entrances"
    state.student_profile.skill_level = "intermediate"
    
    # Add some conversation history
    state.messages = [
        {"role": "user", "content": "I'm working on the accessibility features"},
        {"role": "assistant", "content": "That's important to consider"},
        {"role": "user", "content": "I think my design is obviously perfect for accessibility"}
    ]
    
    # Test current input
    current_input = "Obviously my door widths are optimal and clearly meet all requirements"
    
    # Test context agent
    agent = ContextAgent("architecture")
    context_package = await agent.analyze_student_input(state, current_input)
    
    print(f"\n🔍 Context Analysis Results:")
    print(f"   Interaction Type: {context_package['core_classification']['interaction_type']}")
    print(f"   Understanding Level: {context_package['core_classification']['understanding_level']}")
    print(f"   Confidence Level: {context_package['core_classification']['confidence_level']}")
    print(f"   Engagement Level: {context_package['core_classification']['engagement_level']}")
    print(f"   Overconfidence Score: {context_package['core_classification']['overconfidence_score']}")
    
    print(f"\n📊 Content Analysis:")
    print(f"   Word Count: {context_package['content_analysis']['word_count']}")
    print(f"   Technical Terms: {context_package['content_analysis']['technical_terms']}")
    print(f"   Complexity Score: {context_package['content_analysis']['complexity_score']:.2f}")
    
    print(f"\n🎯 Routing Suggestions:")
    print(f"   Primary Route: {context_package['routing_suggestions']['primary_route']}")
    print(f"   Confidence: {context_package['routing_suggestions']['confidence']:.2f}")
    print(f"   Reasoning: {context_package['routing_suggestions']['reasoning']}")
    
    print(f"\n🔍 Conversation Patterns:")
    print(f"   Repetitive Topics: {context_package['conversation_patterns']['repetitive_topics']}")
    print(f"   Engagement Trend: {context_package['conversation_patterns']['engagement_trend']}")
    print(f"   Understanding Progression: {context_package['conversation_patterns']['understanding_progression']}")
    
    print(f"\n📋 Agent Contexts:")
    for agent_name, context in context_package['agent_contexts'].items():
        print(f"   {agent_name}: {list(context.keys())}")
    
    # Test validation
    validation = await agent.validate_context_analysis(context_package)
    print(f"\n✅ Validation Results:")
    print(f"   Classification Consistent: {validation['classification_consistency']}")
    print(f"   Complexity Appropriate: {validation['complexity_appropriateness']}")
    print(f"   Routing Logic Valid: {validation['routing_logic']}")
    print(f"   Overall Quality: {validation['overall_quality']:.2f}")
    print(f"   Validation Passed: {validation['validation_passed']}")
    
    print(f"\n✅ Context Agent working!")
    
    return context_package

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_context_agent())