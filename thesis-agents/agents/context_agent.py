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
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics

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
            ],
            
            # DESIGN PHASE INDICATORS
            "ideation": [
                "concept", "idea", "approach", "strategy", "vision", "goal",
                "objective", "purpose", "intention", "brainstorm", "explore",
                "consider", "think about", "what if", "imagine", "envision",
                "precedent", "example", "reference", "inspiration", "influence"
            ],
            "visualization": [
                "form", "shape", "massing", "volume", "proportion", "scale",
                "circulation", "flow", "layout", "plan", "section", "elevation",
                "sketch", "drawing", "model", "3d", "render", "visualize",
                "spatial", "arrangement", "composition", "geometry", "structure"
            ],
            "materialization": [
                "construction", "structure", "system", "detail", "material",
                "technical", "engineering", "performance", "cost", "budget",
                "timeline", "schedule", "specification", "implementation",
                "fabrication", "assembly", "installation", "maintenance",
                "durability", "sustainability", "efficiency"
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



    async def analyze_student_input(self, state: ArchMentorState, current_input: str) -> AgentResponse:
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
        
        # 0208COGNITIVE OFFLOADING DETECTION
        cognitive_offloading_patterns = self._detect_cognitive_offloading_patterns(
            core_classification, content_analysis, conversation_patterns
        )
        
        # COMPILE COMPLETE CONTEXT PACKAGE
        context_package = {
            "core_classification": core_classification,
            "content_analysis": content_analysis,
            "contextual_metadata": contextual_metadata,
            "conversation_patterns": conversation_patterns,
            "cognitive_offloading_patterns": cognitive_offloading_patterns,  # ADDED
            "routing_suggestions": routing_suggestions,
            "agent_contexts": agent_contexts,
            "design_phase": self.detect_design_phase(current_input, state),
            "context_quality": self._assess_context_quality(core_classification, content_analysis),
            "timestamp": self._get_current_timestamp(),
            "agent": self.name,
            # 3107 ADDED BELOW LINE: Add conversation history for better analysis
            "conversation_history": state.messages if hasattr(state, 'messages') else []
        }
        
        print(f"   ✅ Context analysis complete")
        print(f"   🎯 Interaction type: {core_classification['interaction_type']}")
        print(f"   📊 Understanding: {core_classification['understanding_level']}")
        print(f"   💭 Confidence: {core_classification['confidence_level']}")
        print(f"   ⚡ Engagement: {core_classification['engagement_level']}")
        
        # Convert to AgentResponse format
        return self._convert_to_agent_response(context_package, current_input, state)
    
    #0208super enhanced AI-powered classification for learning state detection
    async def _perform_core_classification(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
        """Enhanced AI-powered learning state detection with manual override for specific interaction types"""
        
        # FIRST: Check if this matches specific patterns using manual classification (context-aware)
        manual_interaction_type = self._classify_interaction_type(input_text, state)
        
        # Define interaction types that should use manual override (priority over AI)
        manual_override_types = [
            "confusion_expression", "direct_answer_request", 
            "knowledge_request", "implementation_request", "example_request",
            "feedback_request", "technical_question", "improvement_seeking",
            "general_question", "general_statement"
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

            return {
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
        
        # OTHERWISE: Use AI classification as before
        return await self._get_ai_classification_for_other_metrics(input_text, state)
    
    async def _get_ai_classification_for_other_metrics(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
        """AI-powered classification for non-interaction-type metrics"""
        
        # Get conversation context
        recent_context = self._get_recent_context(state)
        
        prompt = f"""
        Analyze this student's architectural learning state to determine the best educational response:
        
        CURRENT INPUT: "{input_text}"
        CONVERSATION CONTEXT: {recent_context}
        SKILL LEVEL: {state.student_profile.skill_level}
        PROJECT: {getattr(state, 'current_design_brief', 'No project set')}
        
        Classify the student's input into these clear categories:
        
        1. INTERACTION TYPE (most important for routing):
        - example_request: ANY mention of "example", "examples", "project", "projects", "precedent", "case study", "show me", "can you provide", "real project", "built project"
        - feedback_request: Asks for review, feedback, thoughts, critique, evaluation, "what do you think", "how does this look"
        - technical_question: Asks about specific standards, requirements, codes, procedures, "what are the requirements", "how many", "what size"
        - confusion_expression: Shows confusion, uncertainty, "I don't understand", "help me", "I'm lost", "unclear"
        - improvement_seeking: Wants to improve, enhance, fix, "how can I", "ways to improve", "make it better"
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
            "interaction_type": "example_request|feedback_request|technical_question|confusion_expression|improvement_seeking|knowledge_seeking|general_statement",
            "confidence_level": "overconfident|uncertain|confident",
            "understanding_level": "low|medium|high",
            "engagement_level": "low|medium|high",
            "is_example_request": true/false,
            "is_feedback_request": true/false,
            "is_technical_question": true/false,
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
        
        # ENHANCED EXAMPLE REQUEST DETECTION - MORE PATTERNS
        example_patterns = [
            r"\bexample\b", r"\bexamples\b", r"\bproject\b", r"\bprojects\b",
            r"\bprecedent\b", r"\bprecedents\b", r"\bcase study\b", r"\bcase studies\b",
            r"\bshow me\b", r"\bcan you give\b", r"\bcan you provide\b", r"\bcan you show\b",
            r"\breal project\b", r"\bbuilt project\b", r"\bactual project\b",
            r"\breference\b", r"\breferences\b", r"\binspiration\b"
        ]
        
        import re
        is_example_request = any(re.search(pattern, input_lower) for pattern in example_patterns)
        
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
        
        # DETERMINE INTERACTION TYPE - PRIORITIZE EXAMPLE REQUESTS
        if is_example_request:
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
            "is_example_request": is_example_request,  # ← THIS IS KEY
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
            "shows_confusion": False,
            "requests_help": False,
            "demonstrates_overconfidence": False,
            "seeks_validation": False,
            "reasoning": "Default classification"
        }








    
    def _classify_interaction_type(self, input_text: str, state: ArchMentorState = None) -> str:
        """Enhanced interaction type classification with improved pattern matching and context awareness"""
        
        input_lower = input_text.lower()
        
        # Note: Do not return 'question_response' as primary type; this is handled as thread context flag elsewhere
        
        # ENHANCED PATTERN SYSTEM - Level 1: High-Confidence Patterns
        
        # 1. Direct Answer Request (Cognitive Offloading) - HIGH PRIORITY
        direct_answer_patterns = [
            "can you design", "design this for me", "do it for me",
            "make it for me", "complete design", "full design", "finished design",
            "design it for me", "what should I design"
        ]
        if any(pattern in input_lower for pattern in direct_answer_patterns):
            return "direct_answer_request"
        
        # 2. Example Request - HIGH PRIORITY
        example_request_patterns = [
            "show me examples", "can you give me examples", "provide me with examples",
            "can you show me precedents", "I need some references", "give me some examples",
            "can you provide", "precedent projects", "case studies", "examples of",
            "can you give some examples", "can you give examples", "give me examples"
        ]
        if any(pattern in input_lower for pattern in example_request_patterns):
            return "example_request"
        
        # 3. Knowledge Request - HIGH PRIORITY
        knowledge_request_patterns = [
            "tell me about", "what are", "explain", "describe",
            "I want to learn about", "can you explain"
        ]
        if any(pattern in input_lower for pattern in knowledge_request_patterns):
            return "knowledge_request"
        
        # ENHANCED PATTERN SYSTEM - Level 2: Context-Dependent Patterns
        
        # 4. Enhanced example request detection with context awareness (HIGHER PRIORITY)
        example_context_patterns = [
            "I want to see case studies", "I'd like to see some", "Can I get references",
            "I want to see precedents", "show me precedents", "I need references",
            "I need some references", "precedent projects", "industrial buildings", "community centers"
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
            if any(word in input_lower for word in ["examples", "precedents", "case studies", "references", "projects"]):
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
        
        # 9. Disambiguate "what is" patterns
        if "what is" in input_lower:
            # Check if it's asking for technical information
            technical_indicators = ["requirement", "standard", "code", "regulation", "specification", "technical"]
            if any(indicator in input_lower for indicator in technical_indicators):
                return "technical_question"
            else:
                return "knowledge_request"
        
        # ENHANCED PATTERN SYSTEM - Level 4: Specific Interaction Types
        
        # 10. Feedback request detection
        feedback_patterns = [
            "feedback", "review", "critique", "evaluate", "assess",
            "what do you think", "how is this", "is this good", "am i on track"
        ]
        if any(pattern in input_lower for pattern in feedback_patterns):
            return "feedback_request"
        
        # 11. Technical question detection
        technical_patterns = [
            "how to", "technical", "specification", "requirement", "standard",
            "code", "regulation", "material", "system", "structure"
        ]
        if any(pattern in input_lower for pattern in technical_patterns):
            return "technical_question"
        
        # 12. Confusion expression detection
        confusion_patterns = [
            "confused", "don't understand", "unclear", "not sure",
            "help", "lost", "stuck", "struggling", "difficult",
            "what does this mean", "i don't get it"
        ]
        if any(pattern in input_lower for pattern in confusion_patterns):
            return "confusion_expression"
        
        # 13. Improvement seeking detection
        improvement_patterns = [
            "improve", "better", "enhance", "optimize", "refine",
            "make it better", "how can i", "what should i change"
        ]
        if any(pattern in input_lower for pattern in improvement_patterns):
            return "improvement_seeking"
        
        # 14. Implementation request detection (HIGHER PRIORITY)
        implementation_patterns = [
            "how do i", "how should i", "what steps", "how to implement",
            "how to start", "how to begin", "what should i do", "what steps should i"
        ]
        if any(pattern in input_lower for pattern in implementation_patterns):
            return "implementation_request"
        
        # ENHANCED PATTERN SYSTEM - Level 5: General Classification
        
        # 15. Enhanced general statement detection
        statement_patterns = [
            "i am", "i have", "i want", "i need", "i like", "i prefer",
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
        """Check if the current input is a response to a previous question from the assistant"""
        
        if not state.messages or len(state.messages) < 2:
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
        
        if not assistant_asked_question:
            return False
        
        # Now check if the current user input looks like a response
        current_input_lower = current_input.lower()
        
        # Response indicators in user's message
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
        
        # Additional check: if the user input doesn't contain a question mark and is not asking for examples/help
        not_asking_question = "?" not in current_input
        not_requesting_help = not any(pattern in current_input_lower for pattern in [
            "can you", "help me", "show me", "give me", "provide", "explain"
        ])
        
        # Enhanced response detection: Check if user is describing their project/ideas
        project_description_indicators = [
            "it's going to be", "it will be", "we've got", "they'll need",
            "it should be", "i like that", "plus it's", "figuring out how to",
            "the main purpose", "the users will be", "the space needs to",
            "i am considering", "i am working on", "my project is"
        ]
        
        describing_project = any(indicator in current_input_lower for indicator in project_description_indicators)
        
        return (user_gave_response or describing_project) and not_asking_question and not_requesting_help
    
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
        
        #0208Check if the last message is a response to a question (not repetitive)
        last_message = messages[-1].lower()
        response_indicators = [
            "i would", "i will", "i think", "i believe", "i'd", "i'll",
            "then i", "so i", "this way", "in this way", "by doing",
            "keeping", "maintaining", "using", "applying", "following"
        ]
        
        # If the last message contains response indicators, it's likely answering a question
        if any(indicator in last_message for indicator in response_indicators):
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
    #0208 UPDATED
    def _prepare_routing_suggestions(self, classification: Dict, content_analysis: Dict, patterns: Dict) -> Dict[str, Any]:
        """Enhanced routing suggestions with more variety and contextual awareness"""
        
        interaction_type = classification.get("interaction_type", "general_statement")
        confidence_level = classification.get("confidence_level", "confident")
        understanding_level = classification.get("understanding_level", "medium")
        engagement_level = classification.get("engagement_level", "medium")
        
        # Enhanced routing logic with more variety
        if interaction_type == "question_response":
            # User is responding to a question - continue exploration
            return {
                "primary_route": "socratic_exploration",
                "suggested_agents": ["socratic_tutor", "domain_expert"],
                "response_type": "exploratory_question",
                "priority": "high",
                "confidence": 0.95,
                "reasoning": "User responding to previous question - continue dialogue"
            }
        
        elif interaction_type == "example_request":
            # User wants examples - provide with context
            return {
                "primary_route": "knowledge_exploration",
                "suggested_agents": ["domain_expert", "socratic_tutor"],
                "response_type": "contextual_examples",
                "priority": "high",
                "confidence": 0.9,
                "reasoning": "User requesting examples - provide with Socratic follow-up"
            }
        
        elif interaction_type == "feedback_request":
            # User wants feedback - analyze and guide
            return {
                "primary_route": "analysis_guidance",
                "suggested_agents": ["analysis_agent", "socratic_tutor"],
                "response_type": "constructive_feedback",
                "priority": "high",
                "confidence": 0.9,
                "reasoning": "User seeking feedback - provide analysis with guidance"
            }
        
        elif interaction_type == "technical_question":
            # Technical question - provide knowledge with application
            return {
                "primary_route": "technical_guidance",
                "suggested_agents": ["domain_expert", "socratic_tutor"],
                "response_type": "technical_knowledge",
                "priority": "medium",
                "confidence": 0.85,
                "reasoning": "Technical question - provide knowledge with application guidance"
            }
        
        elif interaction_type == "design_guidance_request":
            # Design guidance request - provide architectural principles with Socratic guidance
            return {
                "primary_route": "socratic_exploration",
                "suggested_agents": ["domain_expert", "socratic_tutor"],
                "response_type": "design_guidance",
                "priority": "high",
                "confidence": 0.9,
                "reasoning": "Design guidance request - provide architectural principles with Socratic exploration"
            }
        
        elif interaction_type == "confusion_expression":
            # User is confused - provide clarification
            return {
                "primary_route": "clarification_support",
                "suggested_agents": ["socratic_tutor", "domain_expert"],
                "response_type": "clarifying_guidance",
                "priority": "high",
                "confidence": 0.9,
                "reasoning": "User expressing confusion - provide clarification and support"
            }
        
        elif interaction_type == "improvement_seeking":
            # User wants to improve - provide guidance
            return {
                "primary_route": "improvement_guidance",
                "suggested_agents": ["socratic_tutor", "analysis_agent"],
                "response_type": "improvement_suggestions",
                "priority": "medium",
                "confidence": 0.8,
                "reasoning": "User seeking improvement - provide guidance and analysis"
            }
        
        elif interaction_type == "knowledge_seeking":
            # User wants knowledge - provide with context
            return {
                "primary_route": "knowledge_provision",
                "suggested_agents": ["domain_expert", "socratic_tutor"],
                "response_type": "contextual_knowledge",
                "priority": "medium",
                "confidence": 0.8,
                "reasoning": "User seeking knowledge - provide with contextual application"
            }
        
        elif interaction_type == "general_question":
            # General question - explore and guide
            return {
                "primary_route": "exploratory_guidance",
                "suggested_agents": ["socratic_tutor", "domain_expert"],
                "response_type": "exploratory_question",
                "priority": "medium",
                "confidence": 0.75,
                "reasoning": "General question - explore topic with guidance"
            }
        
        elif interaction_type == "general_statement":
            # General statement - respond based on confidence and engagement
            if confidence_level == "overconfident":
                return {
                    "primary_route": "cognitive_challenge",
                    "suggested_agents": ["cognitive_enhancement", "socratic_tutor"],
                    "response_type": "assumption_challenge",
                    "priority": "medium",
                    "confidence": 0.8,
                    "reasoning": "Overconfident statement - challenge assumptions"
                }
            elif confidence_level == "uncertain":
                return {
                    "primary_route": "confidence_building",
                    "suggested_agents": ["socratic_tutor", "domain_expert"],
                    "response_type": "supportive_guidance",
                    "priority": "medium",
                    "confidence": 0.8,
                    "reasoning": "Uncertain statement - build confidence"
                }
            else:
                return {
                    "primary_route": "exploratory_guidance",
                    "suggested_agents": ["socratic_tutor", "domain_expert"],
                    "response_type": "exploratory_question",
                    "priority": "low",
                    "confidence": 0.7,
                    "reasoning": "General statement - explore further"
                }
        
        else:
            # Default fallback
            return {
                "primary_route": "general_guidance",
                "suggested_agents": ["socratic_tutor"],
                "response_type": "general_question",
                "priority": "low",
                "confidence": 0.6,
                "reasoning": "Default routing for unknown interaction type"
            }
    




    def _detect_cognitive_offloading_patterns(self, classification: Dict, content_analysis: Dict, patterns: Dict) -> Dict[str, Any]:
        """Detect cognitive offloading patterns based on MIT research findings"""
        
        flags = {
            "detected": False,
            "type": None,
            "confidence": 0.0,
            "indicators": [],
            "mitigation_strategy": None
        }
        
        # 0208 UPDATED: Don't flag offloading if user is responding to a question
        if classification.get("interaction_type") == "question_response":
            return flags
        



        # PATTERN 1: Premature Answer Seeking (requires minimum 5 messages)
        conversation_depth = patterns.get("conversation_depth", 0)
        
        if (classification.get("interaction_type") == "example_request" and
            conversation_depth < 5):
            flags["detected"] = True
            flags["type"] = "premature_answer_seeking"
            flags["confidence"] = 0.9
            flags["indicators"].append(f"Asking for examples too early (only {conversation_depth} messages, need 5+)")
            flags["mitigation_strategy"] = "socratic_exploration"
        
        # PATTERN 1b: Premature Feedback Seeking (requires minimum 3 messages)
        elif (classification.get("interaction_type") == "feedback_request" and
              conversation_depth < 3):
            flags["detected"] = True
            flags["type"] = "premature_answer_seeking"
            flags["confidence"] = 0.8
            #0108-before: flags["indicators"].append(f"Asking for feedback too early (only {conversation_depth} messages, need 3+)")
            flags["indicators"].append(f"Asking for feedback too early (only {conversation_depth} messages, need 3+)")
            flags["mitigation_strategy"] = "socratic_exploration"
        
        # PATTERN 2: Superficial Confidence
        if (classification.get("confidence_level") == "overconfident" and
            classification.get("engagement_level") == "low"):
            flags["detected"] = True
            flags["type"] = "superficial_confidence"
            flags["confidence"] = 0.7
            flags["indicators"].append("Overconfident but not engaged")
            flags["mitigation_strategy"] = "cognitive_challenge"
        
        # 0208UPDATED PATTERN 3: Repetitive Dependency (only if not responding to questions)
        if (patterns.get("repetitive_topics", False) and 
            classification.get("interaction_type") != "question_response"):



            
            flags["detected"] = True
            flags["type"] = "repetitive_dependency"
            flags["confidence"] = 0.6
            flags["indicators"].append("Repeating same questions")
            flags["mitigation_strategy"] = "foundational_building"
        
        # PATTERN 4: Passive Acceptance
        if (classification.get("engagement_level") == "low" and
            content_analysis.get("specificity_score", 0) < 0.3):
            flags["detected"] = True
            flags["type"] = "passive_acceptance"
            flags["confidence"] = 0.7
            flags["indicators"].append("Passive acceptance without engagement")
            flags["mitigation_strategy"] = "supportive_scaffolding"
        
        return flags
    
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
    
    def detect_design_phase(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
        """Detect the current design phase based on input content and conversation history"""
        
        input_lower = input_text.lower()
        
        # Calculate phase scores based on keyword matches
        phase_scores = {
            "ideation": 0,
            "visualization": 0,
            "materialization": 0
        }
        
        # Score based on current input
        for phase, keywords in self.analysis_patterns.items():
            if phase in ["ideation", "visualization", "materialization"]:
                for keyword in keywords:
                    if keyword in input_lower:
                        phase_scores[phase] += 1
        
        # Consider conversation history for phase progression
        recent_messages = [msg.get('content', '') for msg in state.messages[-5:]]
        for message in recent_messages:
            message_lower = message.lower()
            for phase, keywords in self.analysis_patterns.items():
                if phase in ["ideation", "visualization", "materialization"]:
                    for keyword in keywords:
                        if keyword in message_lower:
                            phase_scores[phase] += 0.5  # Lower weight for historical context
        
        # Determine primary phase
        max_score = max(phase_scores.values())
        if max_score == 0:
            primary_phase = "ideation"  # Default to ideation
        else:
            primary_phase = max(phase_scores, key=phase_scores.get)
        
        # Calculate phase confidence
        total_score = sum(phase_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        # Detect phase transitions
        previous_phase = getattr(state, 'current_design_phase', 'ideation')
        phase_transition = primary_phase != previous_phase
        
        # Update state
        state.current_design_phase = primary_phase
        
        return {
            "current_phase": primary_phase,
            "previous_phase": previous_phase,
            "phase_transition": phase_transition,
            "phase_scores": phase_scores,
            "confidence": confidence,
            "phase_indicators": self._extract_phase_indicators(input_text, primary_phase)
        }
    
    def _extract_phase_indicators(self, input_text: str, phase: str) -> List[str]:
        """Extract specific indicators that led to phase classification"""
        
        input_lower = input_text.lower()
        indicators = []
        
        for keyword in self.analysis_patterns.get(phase, []):
            if keyword in input_lower:
                indicators.append(keyword)
        
        return indicators

    def _convert_to_agent_response(self, context_package: Dict[str, Any], current_input: str, state: ArchMentorState) -> AgentResponse:
        """Convert context package to AgentResponse format while preserving original data"""
        
        # Extract core classification for response text generation
        core_classification = context_package.get('core_classification', {})
        
        # Generate response text based on classification
        response_text = self._generate_response_text(core_classification, current_input)
        
        # Extract cognitive flags
        cognitive_flags = self._extract_cognitive_flags(core_classification)
        
        # Calculate enhancement metrics
        enhancement_metrics = self._calculate_enhancement_metrics(context_package)
        
        # Create AgentResponse using ResponseBuilder
        return ResponseBuilder.create_context_analysis_response(
            response_text=response_text,
            cognitive_flags=cognitive_flags,
            enhancement_metrics=enhancement_metrics,
            metadata=context_package  # Preserve all original data for interaction_logger.py
        )
    
    def _generate_response_text(self, core_classification: Dict[str, Any], current_input: str) -> str:
        """Generate response text based on classification"""
        
        interaction_type = core_classification.get('interaction_type', 'general')
        understanding_level = core_classification.get('understanding_level', 'medium')
        confidence_level = core_classification.get('confidence_level', 'confident')
        
        # Generate appropriate response text based on classification
        if interaction_type == 'question_response':
            return f"Context analysis: Student provided a response to previous question with {understanding_level} understanding and {confidence_level} confidence."
        elif interaction_type == 'question':
            return f"Context analysis: Student asked a question showing {understanding_level} understanding and {confidence_level} confidence."
        elif interaction_type == 'statement':
            return f"Context analysis: Student made a statement with {understanding_level} understanding and {confidence_level} confidence."
        else:
            return f"Context analysis: {interaction_type} interaction detected with {understanding_level} understanding and {confidence_level} confidence."
    
    def _extract_cognitive_flags(self, core_classification: Dict[str, Any]) -> List[CognitiveFlag]:
        """Extract cognitive flags from classification"""
        
        flags = []
        
        # Check for various cognitive indicators
        if core_classification.get('shows_confusion', False):
            flags.append(CognitiveFlag.COGNITIVE_OFFLOADING_DETECTED)
        
        if core_classification.get('requests_help', False):
            flags.append(CognitiveFlag.SCAFFOLDING_PROVIDED)
        
        if core_classification.get('demonstrates_overconfidence', False):
            flags.append(CognitiveFlag.COGNITIVE_OFFLOADING_DETECTED)
        
        if core_classification.get('seeks_validation', False):
            flags.append(CognitiveFlag.METACOGNITIVE_AWARENESS)
        
        # Check confidence level
        confidence_level = core_classification.get('confidence_level', 'confident')
        if confidence_level == 'overconfident':
            flags.append(CognitiveFlag.COGNITIVE_OFFLOADING_DETECTED)
        elif confidence_level == 'uncertain':
            flags.append(CognitiveFlag.SCAFFOLDING_PROVIDED)
        
        # Check understanding level
        understanding_level = core_classification.get('understanding_level', 'medium')
        if understanding_level == 'low':
            flags.append(CognitiveFlag.SCAFFOLDING_PROVIDED)
        elif understanding_level == 'high':
            flags.append(CognitiveFlag.DEEP_THINKING_ENCOURAGED)
        
        # Check engagement level
        engagement_level = core_classification.get('engagement_level', 'medium')
        if engagement_level == 'high':
            flags.append(CognitiveFlag.ENGAGEMENT_MAINTAINED)
        
        return flags
    
    def _calculate_enhancement_metrics(self, context_package: Dict[str, Any]) -> EnhancementMetrics:
        """Calculate enhancement metrics from context package"""
        
        core_classification = context_package.get('core_classification', {})
        content_analysis = context_package.get('content_analysis', {})
        
        # Calculate various scores
        cognitive_offloading_prevention_score = self._calculate_cognitive_offloading_prevention(core_classification)
        deep_thinking_engagement_score = self._calculate_deep_thinking_engagement(core_classification)
        knowledge_integration_score = self._calculate_knowledge_integration(content_analysis)
        scaffolding_effectiveness_score = self._assess_scaffolding_effectiveness(context_package)
        learning_progression_score = self._calculate_learning_progression(context_package)
        metacognitive_awareness_score = self._calculate_metacognitive_awareness(core_classification)
        
        # Calculate overall cognitive score
        overall_cognitive_score = (
            cognitive_offloading_prevention_score + 
            deep_thinking_engagement_score + 
            knowledge_integration_score + 
            scaffolding_effectiveness_score + 
            learning_progression_score + 
            metacognitive_awareness_score
        ) / 6.0
        
        return EnhancementMetrics(
            cognitive_offloading_prevention_score=cognitive_offloading_prevention_score,
            deep_thinking_engagement_score=deep_thinking_engagement_score,
            knowledge_integration_score=knowledge_integration_score,
            scaffolding_effectiveness_score=scaffolding_effectiveness_score,
            learning_progression_score=learning_progression_score,
            metacognitive_awareness_score=metacognitive_awareness_score,
            overall_cognitive_score=overall_cognitive_score,
            scientific_confidence=self._calculate_scientific_confidence(core_classification)
        )
    
    def _calculate_cognitive_offloading_prevention(self, core_classification: Dict[str, Any]) -> float:
        """Calculate cognitive offloading prevention score"""
        
        # Higher score for detecting and preventing cognitive offloading
        confidence_level = core_classification.get('confidence_level', 'confident')
        demonstrates_overconfidence = core_classification.get('demonstrates_overconfidence', False)
        
        if confidence_level == 'overconfident' or demonstrates_overconfidence:
            return 0.8  # High score for detecting overconfidence
        elif confidence_level == 'uncertain':
            return 0.6  # Medium score for uncertainty
        else:
            return 0.4  # Lower score for normal confidence
    
    def _calculate_deep_thinking_engagement(self, core_classification: Dict[str, Any]) -> float:
        """Calculate deep thinking engagement score"""
        
        understanding_level = core_classification.get('understanding_level', 'medium')
        engagement_level = core_classification.get('engagement_level', 'medium')
        
        if understanding_level == 'high' and engagement_level == 'high':
            return 0.9
        elif understanding_level == 'high' or engagement_level == 'high':
            return 0.7
        elif understanding_level == 'low' and engagement_level == 'low':
            return 0.3
        else:
            return 0.5
    
    def _calculate_knowledge_integration(self, content_analysis: Dict[str, Any]) -> float:
        """Calculate knowledge integration score"""
        
        technical_terms = content_analysis.get('technical_terms', [])
        complexity_score = content_analysis.get('complexity_score', 0.5)
        
        # Higher score for more technical terms and appropriate complexity
        if len(technical_terms) > 3 and 0.4 <= complexity_score <= 0.8:
            return 0.8
        elif len(technical_terms) > 1:
            return 0.6
        else:
            return 0.4
    
    def _calculate_learning_progression(self, context_package: Dict[str, Any]) -> float:
        """Calculate learning progression score"""
        
        patterns = context_package.get('conversation_patterns', {})
        progression = patterns.get('understanding_progression', 'stable')
        
        if progression == 'improving':
            return 0.8
        elif progression == 'stable':
            return 0.6
        else:
            return 0.4
    
    def _calculate_metacognitive_awareness(self, core_classification: Dict[str, Any]) -> float:
        """Calculate metacognitive awareness score"""
        
        seeks_validation = core_classification.get('seeks_validation', False)
        requests_help = core_classification.get('requests_help', False)
        shows_confusion = core_classification.get('shows_confusion', False)
        
        # Higher score for metacognitive behaviors
        if seeks_validation or requests_help:
            return 0.8
        elif shows_confusion:
            return 0.6
        else:
            return 0.4
    
    def _calculate_scientific_confidence(self, core_classification: Dict[str, Any]) -> float:
        """Calculate scientific confidence score"""
        
        # Based on the quality of the classification
        is_technical = core_classification.get('is_technical_question', False)
        understanding_level = core_classification.get('understanding_level', 'medium')
        
        if is_technical and understanding_level == 'high':
            return 0.9
        elif is_technical:
            return 0.7
        else:
            return 0.5
    
    def _assess_scaffolding_effectiveness(self, context_package: Dict[str, Any]) -> float:
        """Assess scaffolding effectiveness based on context"""
        
        # Simple heuristic based on understanding progression
        patterns = context_package.get('conversation_patterns', {})
        progression = patterns.get('understanding_progression', 'stable')
        
        if progression == 'improving':
            return 0.8
        elif progression == 'stable':
            return 0.6
        else:
            return 0.4

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