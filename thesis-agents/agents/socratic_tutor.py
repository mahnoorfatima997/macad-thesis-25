# agents/socratic_tutor.py - Sophisticated Socratic Tutoring Implementation
from typing import Dict, Any, List, Optional
import os
import random
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics

load_dotenv()

class SocraticTutorAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "socratic_tutor"
        print(f"🤔 {self.name} initialized for domain: {domain}")
    
    #3107 ADDED DOMAIN EXPERT RESULT ONLY
    async def generate_response(self, state: ArchMentorState, analysis_result: Dict[str, Any], context_classification: Optional[Dict] = None, domain_expert_result: Optional[Dict] = None) -> AgentResponse:
        """Generate sophisticated Socratic responses with advanced analysis - now returns AgentResponse"""
        
        print(f"\n🤔 {self.name} generating sophisticated Socratic response...")
        
        # Get user's last input
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        if not last_message:
            fallback_response = self._generate_fallback_response()
            return self._convert_to_agent_response(fallback_response, state, analysis_result, context_classification, domain_expert_result)
        
        # 0208 UPDATED: Check if this is a first-time interaction or early in conversation
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        is_early_conversation = len(user_messages) <= 2
        
        # Advanced analysis of student state
        student_analysis = self._analyze_student_state(state, analysis_result, context_classification)
        conversation_progression = self._analyze_conversation_progression(state, last_message)
        student_insights = self._extract_student_insights(state, last_message)
        
        # 3107-BELOW LINE: Check if we have domain expert results (examples) to ask questions about
        # 0108 added before: has_examples = domain_expert_result and domain_expert_result.get("response_text", "")Only consider it has examples if it's not a cognitive protection response
        has_examples = (domain_expert_result and 
                       domain_expert_result.get("response_text", "") and 
                       domain_expert_result.get("response_type") != "cognitive_protection_response")
        
        # Determine response strategy based on analysis
        response_strategy = self._determine_response_strategy(student_analysis, conversation_progression)
        
        print(f"📊 Student Analysis: {student_analysis}")
        print(f"🔄 Conversation Stage: {conversation_progression['stage']}")
        print(f"💡 Student Insights: {student_insights['key_insights']}")
        print(f"🎯 Response Strategy: {response_strategy}")
        
        # 0208 UPDATED: For early conversations, use enhanced clarifying guidance
        if is_early_conversation and not has_examples:
            print("🆕 Early conversation detected - providing enhanced clarifying guidance")
            response_result = await self._generate_clarifying_guidance(state, student_analysis, conversation_progression)
        # 3107-BEFORE IT WAS if response_strategy == "clarifying_guidance": Generate response based on strategy, with special handling for examples
        elif has_examples:
            # If we have examples from domain expert, ask questions about them
            print("📚 Domain expert provided examples - generating questions about those examples")
            response_result = await self._generate_example_based_question(state, student_analysis, conversation_progression, domain_expert_result)
        elif response_strategy == "clarifying_guidance":
            response_result = await self._generate_clarifying_guidance(state, student_analysis, conversation_progression)
        elif response_strategy == "supportive_guidance":
            response_result = await self._generate_supportive_guidance(state, student_analysis, conversation_progression)
        elif response_strategy == "challenging_question":
            response_result = await self._generate_challenging_question(state, student_analysis, conversation_progression)
        elif response_strategy == "exploratory_question":
            response_result = await self._generate_exploratory_question(state, student_analysis, conversation_progression)
        elif response_strategy == "assumption_challenge":
            response_result = await self._generate_assumption_challenge(state, student_analysis, conversation_progression)
        elif response_strategy == "depth_promotion":
            response_result = await self._generate_depth_promotion(state, student_analysis, conversation_progression)
        else:
            response_result = await self._generate_adaptive_question(state, student_analysis, conversation_progression, response_strategy)
        
        # Add analysis metadata
        response_result.update({
            "agent": self.name,
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression,
            "student_insights": student_insights,
            "response_strategy": response_strategy,
            "educational_intent": self._get_educational_intent(response_strategy, student_analysis)
        })
        
        # Add cognitive flags to the original response result for backward compatibility
        cognitive_flags = self._extract_cognitive_flags(response_result, state)
        response_result["cognitive_flags"] = cognitive_flags
        
        # Convert to standardized AgentResponse format
        return self._convert_to_agent_response(response_result, state, analysis_result, context_classification, domain_expert_result)
    
    def _convert_to_agent_response(self, response_result: Dict, state: ArchMentorState, analysis_result: Dict, context_classification: Optional[Dict], domain_expert_result: Optional[Dict]) -> AgentResponse:
        """Convert the original response to AgentResponse format while preserving all data"""
        
        # Calculate enhancement metrics
        enhancement_metrics = self._calculate_enhancement_metrics(response_result, state, analysis_result)
        
        # Convert cognitive flags to standardized format
        cognitive_flags = self._extract_cognitive_flags(response_result, state)
        cognitive_flags_standardized = self._convert_cognitive_flags(cognitive_flags)
        
        # Create standardized response while preserving original data
        response = ResponseBuilder.create_socratic_response(
            response_text=response_result.get("response_text", ""),
            cognitive_flags=cognitive_flags_standardized,
            enhancement_metrics=enhancement_metrics,
            quality_score=response_result.get("quality_score", 0.5),
            confidence_score=response_result.get("confidence_score", 0.5),
            metadata={
                # Preserve all original data for backward compatibility
                "original_response_result": response_result,
                "student_analysis": response_result.get("student_analysis", {}),
                "conversation_progression": response_result.get("conversation_progression", {}),
                "student_insights": response_result.get("student_insights", {}),
                "response_strategy": response_result.get("response_strategy", ""),
                "educational_intent": response_result.get("educational_intent", ""),
                "analysis_result": analysis_result,
                "context_classification": context_classification,
                "domain_expert_result": domain_expert_result,
                "cognitive_flags": cognitive_flags  # Original format
            }
        )
        
        return response
    
    def _calculate_enhancement_metrics(self, response_result: Dict, state: ArchMentorState, analysis_result: Dict) -> EnhancementMetrics:
        """Calculate cognitive enhancement metrics for Socratic tutoring"""
        
        response_strategy = response_result.get("response_strategy", "")
        student_analysis = response_result.get("student_analysis", {})
        conversation_progression = response_result.get("conversation_progression", {})
        
        # Cognitive offloading prevention score
        # Higher score if using challenging questions or assumption challenges
        challenging_strategies = ["challenging_question", "assumption_challenge", "depth_promotion"]
        cop_score = 0.8 if response_strategy in challenging_strategies else 0.4
        
        # Deep thinking engagement score
        # Higher score if using exploratory or clarifying questions
        deep_thinking_strategies = ["exploratory_question", "clarifying_guidance", "adaptive_question"]
        dte_score = 0.9 if response_strategy in deep_thinking_strategies else 0.6
        
        # Knowledge integration score
        # Based on whether domain expert results were used
        has_domain_expert = bool(response_result.get("domain_expert_result"))
        ki_score = 0.8 if has_domain_expert else 0.3
        
        # Scaffolding effectiveness score
        # Higher score for supportive guidance or clarifying guidance
        scaffolding_strategies = ["supportive_guidance", "clarifying_guidance"]
        scaffolding_score = 0.9 if response_strategy in scaffolding_strategies else 0.5
        
        # Learning progression score
        # Based on conversation progression and student analysis
        progression_stage = conversation_progression.get("stage", "early")
        student_confidence = student_analysis.get("confidence_level", "medium")
        
        if progression_stage == "advanced" and student_confidence == "high":
            learning_progression = 0.9
        elif progression_stage == "intermediate":
            learning_progression = 0.7
        else:
            learning_progression = 0.5
        
        # Metacognitive awareness score
        # Higher score if using assumption challenges or depth promotion
        metacognitive_strategies = ["assumption_challenge", "depth_promotion"]
        metacognitive_score = 0.8 if response_strategy in metacognitive_strategies else 0.4
        
        # Overall cognitive score
        overall_score = (cop_score + dte_score + ki_score + scaffolding_score + learning_progression + metacognitive_score) / 6
        
        # Scientific confidence
        # Based on response quality and strategy effectiveness
        response_quality = response_result.get("quality_score", 0.5)
        strategy_confidence = 0.8 if response_strategy in ["challenging_question", "exploratory_question"] else 0.6
        scientific_confidence = (response_quality + strategy_confidence) / 2
        
        return EnhancementMetrics(
            cognitive_offloading_prevention_score=cop_score,
            deep_thinking_engagement_score=dte_score,
            knowledge_integration_score=ki_score,
            scaffolding_effectiveness_score=scaffolding_score,
            learning_progression_score=learning_progression,
            metacognitive_awareness_score=metacognitive_score,
            overall_cognitive_score=overall_score,
            scientific_confidence=scientific_confidence
        )
    
    def _extract_cognitive_flags(self, response_result: Dict, state: ArchMentorState) -> List[str]:
        """Extract cognitive flags from the response and student state"""
        
        flags = []
        response_strategy = response_result.get("response_strategy", "")
        student_analysis = response_result.get("student_analysis", {})
        
        # Add flags based on response strategy
        if response_strategy == "challenging_question":
            flags.append("deep_thinking_encouraged")
        elif response_strategy == "supportive_guidance":
            flags.append("scaffolding_provided")
        elif response_strategy == "clarifying_guidance":
            flags.append("scaffolding_provided")
        elif response_strategy == "assumption_challenge":
            flags.append("cognitive_offloading_detected")
            flags.append("deep_thinking_encouraged")
        elif response_strategy == "depth_promotion":
            flags.append("deep_thinking_encouraged")
        elif response_strategy == "exploratory_question":
            flags.append("engagement_maintained")
        
        # Add flags based on student analysis
        confidence_level = student_analysis.get("confidence_level", "medium")
        if confidence_level == "low":
            flags.append("scaffolding_provided")
        elif confidence_level == "high":
            flags.append("deep_thinking_encouraged")
        
        # Add engagement flag if student is responding
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        if len(user_messages) > 1:
            flags.append("engagement_maintained")
        
        return flags
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Convert cognitive flags to standardized format"""
        
        flag_mapping = {
            "deep_thinking_encouraged": CognitiveFlag.DEEP_THINKING_ENCOURAGED,
            "scaffolding_provided": CognitiveFlag.SCAFFOLDING_PROVIDED,
            "cognitive_offloading_detected": CognitiveFlag.COGNITIVE_OFFLOADING_DETECTED,
            "engagement_maintained": CognitiveFlag.ENGAGEMENT_MAINTAINED,
            "learning_progression": CognitiveFlag.LEARNING_PROGRESSION,
            "metacognitive_awareness": CognitiveFlag.METACOGNITIVE_AWARENESS
        }
        
        converted_flags = []
        for flag in cognitive_flags:
            if flag in flag_mapping:
                converted_flags.append(flag_mapping[flag])
            else:
                # Default to scaffolding for unknown flags
                converted_flags.append(CognitiveFlag.SCAFFOLDING_PROVIDED)
        
        return converted_flags
    
    def _analyze_student_state(self, state: ArchMentorState, analysis_result: Dict, context_classification: Optional[Dict]) -> Dict[str, Any]:
        """Analyze student's current learning state and confidence"""
        
        # Get confidence and understanding from context classification
        confidence_level = context_classification.get("confidence_level", "confident") if context_classification else "confident"
        understanding_level = context_classification.get("understanding_level", "medium") if context_classification else "medium"
        engagement_level = context_classification.get("engagement_level", "medium") if context_classification else "medium"
        
        # Analyze conversation patterns
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        total_messages = len(user_messages)
        
        # Detect confusion indicators
        confusion_indicators = ["confused", "don't understand", "not sure", "unclear", "help", "what do you mean"]
        shows_confusion = any(indicator in " ".join(user_messages).lower() for indicator in confusion_indicators)
        
        # Detect overconfidence indicators
        overconfidence_indicators = ["obviously", "clearly", "definitely", "absolutely", "perfect", "best"]
        shows_overconfidence = any(indicator in " ".join(user_messages).lower() for indicator in overconfidence_indicators)
        
        # Analyze question complexity
        avg_question_length = sum(len(msg.split()) for msg in user_messages) / max(len(user_messages), 1)
        question_complexity = "simple" if avg_question_length < 8 else "moderate" if avg_question_length < 15 else "complex"
        
        return {
            "confidence_level": confidence_level,
            "understanding_level": understanding_level,
            "engagement_level": engagement_level,
            "shows_confusion": shows_confusion,
            "shows_overconfidence": shows_overconfidence,
            "question_complexity": question_complexity,
            "total_messages": total_messages,
            "learning_progression": self._assess_learning_progression(state)
        }
    
    def _analyze_conversation_progression(self, state: ArchMentorState, current_message: str) -> Dict[str, Any]:
        """Analyze the progression of the conversation"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) <= 1:
            stage = "initial"
            progression_summary = "First interaction"
        elif len(user_messages) <= 3:
            stage = "exploration"
            progression_summary = "Exploring initial concepts"
        elif len(user_messages) <= 6:
            stage = "deepening"
            progression_summary = "Diving deeper into specific topics"
        else:
            stage = "advanced"
            progression_summary = "Advanced discussion and synthesis"
        
        # Analyze topic evolution
        topic_evolution = self._analyze_topic_evolution(user_messages)
        
        # Detect conversation patterns
        patterns = {
            "seeking_clarification": any("what do you mean" in msg.lower() or "can you explain" in msg.lower() for msg in user_messages[-3:]),
            "requesting_examples": any("example" in msg.lower() or "show me" in msg.lower() for msg in user_messages[-3:]),
            "seeking_feedback": any("feedback" in msg.lower() or "review" in msg.lower() for msg in user_messages[-3:]),
            "exploring_alternatives": any("alternative" in msg.lower() or "different" in msg.lower() for msg in user_messages[-3:])
        }
        
        return {
            "stage": stage,
            "progression_summary": progression_summary,
            "topic_evolution": topic_evolution,
            "patterns": patterns,
            "message_count": len(user_messages)
        }
    
    def _extract_student_insights(self, state: ArchMentorState, current_message: str) -> Dict[str, Any]:
        """Extract key insights from student's responses"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        # Use AI to extract insights
        prompt = f"""
        Analyze these architecture student messages and extract key insights about their understanding and approach:
        
        MESSAGES: {user_messages}
        CURRENT MESSAGE: "{current_message}"
        
        Extract:
        1. Key insights about their design thinking
        2. Areas where they show understanding
        3. Potential misconceptions or gaps
        4. Their design priorities and values
        5. Learning style indicators
        
        Return as a structured analysis.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            insights_analysis = response.choices[0].message.content.strip()
            
            return {
                "key_insights": insights_analysis,
                "message_count": len(user_messages),
                "current_focus": self._identify_current_focus(current_message)
            }
            
        except Exception as e:
            print(f"⚠️ Insight extraction failed: {e}")
            return {
                "key_insights": "Unable to extract insights",
                "message_count": len(user_messages),
                "current_focus": "general inquiry"
            }
    
    def _determine_response_strategy(self, student_analysis: Dict, conversation_progression: Dict) -> str:
        """Enhanced response strategy determination with cognitive protection focus"""
        
        # COGNITIVE OFFLOADING PROTECTION
        if student_analysis.get("shows_overconfidence") and student_analysis.get("engagement_level") == "low":
            return "assumption_challenge"  # Challenge superficial confidence
        
        if student_analysis.get("question_complexity") == "simple" and conversation_progression.get("stage") == "deepening":
            return "depth_promotion"  # Push for deeper thinking
        
        if student_analysis.get("shows_confusion"):
            return "clarifying_guidance"  # Build understanding
        
        # STANDARD SOCRATIC STRATEGIES
        if student_analysis.get("confidence_level") == "uncertain":
            return "supportive_guidance"  # Build confidence
        
        if student_analysis.get("engagement_level") == "high":
            return "exploratory_question"  # Leverage engagement
        
        if conversation_progression.get("stage") == "initial":
            return "foundational_question"  # Start with basics
        
        return "adaptive_question"  # Default adaptive approach
    
    async def _generate_clarifying_guidance(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate specific clarifying guidance that provides concrete architectural direction"""
        
        building_type = self._extract_building_type_from_context(state)
        
        # Get the user's last message to understand what they're asking about
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        # Extract the main topic the user is asking about
        main_topic = self._extract_main_topic(last_message)
        
        # Check if user has already specified a focus area within that topic
        user_specified_focus = self._extract_user_specified_focus(last_message)
        
        # Generate specific architectural guidance based on the topic
        if user_specified_focus:
            response_text = self._generate_specific_architectural_guidance(user_specified_focus, building_type, main_topic)
        else:
            response_text = await self._generate_topic_specific_guidance(main_topic, building_type, last_message)
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "clarifying_guidance",
            "educational_intent": "build_understanding",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }
    
    def _generate_specific_architectural_guidance(self, focus_area: str, building_type: str, main_topic: str) -> str:
        """Generate specific architectural guidance using LLM for any building type"""
        
        # Use LLM to generate context-aware guidance instead of hardcoded templates
        prompt = f"""
        You are an architectural mentor helping a student design a {building_type}.
        The student is asking about {focus_area} in the context of {main_topic}.
        
        Generate a specific, helpful guidance response that:
        1. Addresses the specific {focus_area} for {building_type}
        2. Asks probing questions to guide discovery
        3. Encourages deep thinking about the relationship between {focus_area} and {main_topic}
        4. Is specific to {building_type} but not overly prescriptive
        5. Helps the student think through the design challenges
        
        Keep the response conversational and educational. Focus on guiding the student's thinking rather than providing direct answers.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Fallback to generic guidance if LLM fails
            return f"Let's focus on {focus_area} for your {building_type}. What specific challenges or opportunities do you see in this area? How does it relate to your overall design goals?"
    
    async def _generate_topic_specific_guidance(self, main_topic: str, building_type: str, last_message: str) -> str:
        """Generate topic-specific architectural guidance using LLM"""
        
        # Use LLM to generate context-aware guidance
        prompt = f"""
        You are an architectural mentor helping a student design a {building_type}.
        The student is asking about {main_topic}.
        
        Generate a specific, helpful guidance response that:
        1. Addresses {main_topic} in the context of {building_type}
        2. Asks probing questions to guide discovery
        3. Encourages deep thinking about {main_topic}
        4. Is specific to {building_type} but not overly prescriptive
        5. Helps the student think through the design challenges
        
        Keep the response conversational and educational. Focus on guiding the student's thinking rather than providing direct answers.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Fallback to generic guidance if LLM fails
            return f"Let's explore {main_topic} for your {building_type}. What specific aspects of {main_topic} are most important for your project? How does it relate to your overall design goals?"

    async def _generate_supportive_guidance(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate supportive guidance with specific architectural knowledge"""
        
        building_type = self._extract_building_type_from_context(state)
        
        # Get the user's last message
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        main_topic = self._extract_main_topic(last_message)
        
        # Provide specific, encouraging guidance based on the topic
        supportive_guidance = self._get_supportive_architectural_guidance(main_topic, building_type, student_analysis)
        
        return {
            "response_text": supportive_guidance,
            "response_type": "supportive_guidance",
            "user_input_addressed": "learning_support"
        }
    
    def _get_supportive_architectural_guidance(self, topic: str, building_type: str, student_analysis: Dict) -> str:
        """Get specific supportive guidance for architectural topics using LLM"""
        
        # Use LLM to generate context-aware supportive guidance
        prompt = f"""
        You are an architectural mentor helping a student design a {building_type}.
        The student is asking about {topic} and needs supportive, encouraging guidance.
        
        Generate a supportive, encouraging response that:
        1. Acknowledges the student's interest in {topic}
        2. Provides positive reinforcement for their thinking
        3. Offers helpful guidance specific to {building_type}
        4. Encourages deeper exploration of {topic}
        5. Maintains an encouraging, educational tone
        
        Keep the response conversational and supportive. Focus on building confidence while guiding learning.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Fallback to generic supportive guidance if LLM fails
            return f"Excellent question about {topic}! This is a key aspect of your {building_type} project. What specific aspects of {topic} are you most interested in exploring? Let's break this down step by step."

    async def _generate_challenging_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate challenging questions that push architectural thinking deeper"""
        
        building_type = self._extract_building_type_from_context(state)
        
        # Get the user's last message
        last_message = ""
        for msg in reversed(state.messages):
            if msg.get('role') == 'user':
                last_message = msg['content']
                break
        
        main_topic = self._extract_main_topic(last_message)
        
        # Generate specific challenging questions based on the topic
        challenging_question = self._get_challenging_architectural_question(main_topic, building_type, student_analysis)
        
        return {
            "response_text": challenging_question,
            "response_type": "challenging_question",
            "user_input_addressed": "deep_thinking"
        }
    
    def _get_challenging_architectural_question(self, topic: str, building_type: str, student_analysis: Dict) -> str:
        """Get specific challenging questions for architectural topics using LLM"""
        
        # Use LLM to generate context-aware challenging questions
        prompt = f"""
        You are an architectural mentor helping a student design a {building_type}.
        The student is asking about {topic} and needs a challenging question to push their thinking deeper.
        
        Generate a challenging, thought-provoking question that:
        1. Addresses complex trade-offs in {topic} for {building_type}
        2. Pushes the student to think about competing requirements
        3. Encourages deeper analysis of {topic} decisions
        4. Challenges assumptions about {topic}
        5. Helps the student consider long-term implications
        
        Make the question specific to {building_type} but applicable to architectural thinking in general.
        Keep it challenging but not overwhelming.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Fallback to generic challenging question if LLM fails
            return f"Your {topic} choices will shape the entire project. How will you make decisions that balance function, aesthetics, and long-term value? What happens when your ideal {topic} solution conflicts with other project requirements?"
    
    async def _generate_exploratory_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Generate exploratory questions for students in exploration stage"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        The student is in exploration stage. Generate an exploratory question that opens up new avenues of thinking.
        
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Generate an exploratory question that:
        1. Opens up new possibilities
        2. Encourages creative thinking
        3. Explores different approaches
        4. Guides discovery
        5. Is open-ended and inspiring
        
        Ask ONE exploratory question:
        """
        
        try:
            response = self.llm.invoke(prompt)
            exploratory_question = response.content.strip()
            
            if not exploratory_question.endswith('?'):
                exploratory_question += '?'
            
            return {
                "response_text": exploratory_question,
                "response_type": "exploratory_question",
                "user_input_addressed": "exploration"
            }
            
        except Exception as e:
            print(f"⚠️ Exploratory question generation failed: {e}")
            return {
                "response_text": "What other approaches could you consider for this aspect of your design?",
                "response_type": "exploratory_question",
                "user_input_addressed": "exploration"
            }
    
    async def _generate_adaptive_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict, strategy: str) -> Dict[str, Any]:
        """Generate adaptive questions based on specific strategy"""
        
        building_type = self._extract_building_type_from_context(state)
        
        prompt = f"""
        Generate an adaptive question based on the specific strategy and student analysis.
        
        STRATEGY: {strategy}
        STUDENT STATE: {student_analysis}
        CONVERSATION STAGE: {conversation_progression['stage']}
        BUILDING TYPE: {building_type}
        
        Generate a question that adapts to the student's current needs and learning stage.
        """
        
        try:
            response = self.llm.invoke(prompt)
            adaptive_question = response.content.strip()
            
            if not adaptive_question.endswith('?'):
                adaptive_question += '?'
            
            return {
                "response_text": adaptive_question,
                "response_type": "adaptive_question",
                "user_input_addressed": "adaptive_guidance"
            }
            
        except Exception as e:
            print(f"⚠️ Adaptive question generation failed: {e}")
            return {
                "response_text": "How does this relate to your overall design goals?",
                "response_type": "adaptive_question",
                "user_input_addressed": "adaptive_guidance"
            }
    
    async def _generate_assumption_challenge(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Challenge assumptions to prevent superficial confidence"""
        
        building_type = self._extract_building_type_from_context(state)
        
        response_text = f"""
**🧠 Let's examine your assumptions**

I notice you're expressing confidence, but let's make sure it's built on solid reasoning.

**Let's challenge your thinking:**

1. **What evidence supports your current approach?** (Not just opinions, but concrete reasons)

2. **What are the potential weaknesses in your reasoning?** (Every design has trade-offs - what are yours?)

3. **How would you defend this to a skeptical critic?** (Imagine someone questioning every decision)

4. **What alternatives have you considered and rejected?** (Why did you choose this path over others?)

**The goal isn't to undermine your confidence, but to strengthen it through rigorous thinking.**

*Which of these questions feels most challenging to answer?*
"""
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "assumption_challenge",
            "educational_intent": "challenge_assumptions",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }
    
    async def _generate_depth_promotion(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict) -> Dict[str, Any]:
        """Promote deeper thinking when responses are too superficial"""
        
        building_type = self._extract_building_type_from_context(state)
        
        response_text = f"""
**🔍 Let's go deeper**

I sense you might be scratching the surface of this problem. Let's explore the layers beneath.

**Let's dive deeper:**

1. **What's the underlying principle driving your design decisions?** (Not just "it looks good" but the fundamental reasoning)

2. **How does your design respond to the specific context?** (What makes this solution right for this particular situation?)

3. **What are the long-term implications of your choices?** (How will this design perform over time?)

4. **What would happen if you took the opposite approach?** (Sometimes the best way to understand your choice is to consider its opposite)

**Deep thinking creates lasting understanding. Let's build that together.**

*Which of these deeper questions resonates most with your current thinking?*
"""
        
        return {
            "agent": self.name,
            "response_text": response_text,
            "response_type": "depth_promotion",
            "educational_intent": "promote_deep_thinking",
            "student_analysis": student_analysis,
            "conversation_progression": conversation_progression
        }
    
    def _assess_learning_progression(self, state: ArchMentorState) -> str:
        """Assess the student's learning progression"""
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if len(user_messages) <= 2:
            return "beginning"
        elif len(user_messages) <= 5:
            return "developing"
        elif len(user_messages) <= 8:
            return "intermediate"
        else:
            return "advanced"
    
    def _analyze_topic_evolution(self, user_messages: List[str]) -> Dict[str, Any]:
        """Analyze how topics have evolved in the conversation"""
        if len(user_messages) < 2:
            return {"evolution": "single_topic", "topics": ["initial"]}
        
        # Simple topic analysis
        topics = []
        for msg in user_messages:
            if any(word in msg.lower() for word in ["light", "window", "glazing"]):
                topics.append("environmental")
            elif any(word in msg.lower() for word in ["circulation", "flow", "movement"]):
                topics.append("circulation")
            elif any(word in msg.lower() for word in ["material", "construction", "structure"]):
                topics.append("materials")
            else:
                topics.append("general")
        
        return {
            "evolution": "topic_progression" if len(set(topics)) > 1 else "focused_discussion",
            "topics": topics,
            "topic_count": len(set(topics))
        }
    
    def _identify_current_focus(self, current_message: str) -> str:
        """Identify the current focus of the student's message"""
        if any(word in current_message.lower() for word in ["light", "window", "glazing"]):
            return "environmental_design"
        elif any(word in current_message.lower() for word in ["circulation", "flow", "movement"]):
            return "circulation_design"
        elif any(word in current_message.lower() for word in ["material", "construction", "structure"]):
            return "materials_and_construction"
        else:
            return "general_design"
    
    def _get_educational_intent(self, strategy: str, student_analysis: Dict) -> str:
        """Get the educational intent of the response strategy"""
        intents = {
            "clarifying_guidance": "Clarify confusion and build understanding",
            "supportive_guidance": "Support learning and build confidence",
            "challenging_question": "Challenge assumptions and promote critical thinking",
            "exploratory_question": "Encourage exploration and creative thinking",
            "adaptive_question": "Adapt to student's current learning needs"
        }
        return intents.get(strategy, "Guide student learning")
    
    def _generate_fallback_response(self, user_input: str = "", building_type: str = "project") -> Dict[str, Any]:
        """Generate a fallback Socratic question when AI fails"""
        
        if not user_input:
            return {
                "agent": self.name,
                "response_text": "What specific aspect of your design would you like to explore further?",
                "response_type": "fallback_socratic",
                "educational_intent": "Encourage specific exploration",
                "user_input_addressed": "general inquiry"
            }
        
        # Simple template-based fallback
        fallback_questions = [
            f"What specific challenges do you anticipate with {user_input.lower()} in your {building_type}?",
            f"How do you think {user_input.lower()} will impact the overall design of your {building_type}?",
            f"What factors would you consider when implementing {user_input.lower()} in your {building_type}?",
            f"How might {user_input.lower()} affect the user experience in your {building_type}?"
        ]
        
        return {
            "agent": self.name,
            "response_text": random.choice(fallback_questions),
            "response_type": "fallback_socratic",
            "educational_intent": "Guide exploration of specific design aspect",
            "user_input_addressed": user_input[:50] + "..." if len(user_input) > 50 else user_input
        }
    #3107-FULL DEFITINIO ADDED FOR EXAMPLE BASED QUESTION  
    async def _generate_example_based_question(self, state: ArchMentorState, student_analysis: Dict, conversation_progression: Dict, domain_expert_result: Dict) -> Dict[str, Any]:
        """Generate Socratic questions specifically about the examples that were just provided - Enhanced for deeper probing"""
        
        building_type = self._extract_building_type_from_context(state)
        examples_text = domain_expert_result.get("response_text", "")
        
        # Extract the specific topic being discussed
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        last_user_message = user_messages[-1] if user_messages else ""
        
        # Determine the level of probing needed based on student state
        confidence_level = student_analysis.get("confidence_level", "confident")
        understanding_level = student_analysis.get("understanding_level", "medium")
        
        if confidence_level == "overconfident":
            question_strategy = "challenge_assumptions"
        elif confidence_level == "uncertain":
            question_strategy = "build_confidence"
        elif understanding_level == "low":
            question_strategy = "clarify_understanding"
        else:
            question_strategy = "deepen_analysis"
        
        prompt = f"""
        The Domain Expert just provided these examples to the student:
        
        {examples_text}
        
        STUDENT'S LAST MESSAGE: "{last_user_message}"
        BUILDING TYPE: {building_type}
        STUDENT CONFIDENCE: {confidence_level}
        STUDENT UNDERSTANDING: {understanding_level}
        QUESTION STRATEGY: {question_strategy}
        
        Generate ONE specific Socratic question that:
        1. References the specific examples that were just provided
        2. Uses the {question_strategy} approach to probe deeper thinking
        3. Encourages critical analysis of those examples
        4. Prompts them to consider how principles apply to their own design
        5. Is specific to the examples provided, not generic
        6. Builds on their current understanding level
        
        QUESTION STRATEGIES:
        - challenge_assumptions: "What assumptions underlie [specific example]? How might those assumptions not apply to your context?"
        - build_confidence: "What aspects of [specific example] do you find most compelling for your project? Why?"
        - clarify_understanding: "Can you explain how [specific example] addresses [specific challenge]? What makes it effective?"
        - deepen_analysis: "Looking at [specific example], what underlying principles do you see that could inform your approach?"
        
        Generate ONE targeted question using the {question_strategy} approach:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.3
            )
            
            example_question = response.choices[0].message.content.strip()
            
            if not example_question.endswith('?'):
                example_question += '?'
            
            return {
                "response_text": example_question,
                "response_type": "example_based_question",
                "user_input_addressed": "critical_analysis_of_examples",
                "examples_referenced": True,
                "question_strategy": question_strategy,
                "probing_depth": "deep"
            }
            
        except Exception as e:
            print(f"⚠️ Example-based question generation failed: {e}")
            return {
                "response_text": "Looking at these examples, what specific aspects do you think would be most relevant to your own design approach, and why?",
                "response_type": "example_based_question",
                "user_input_addressed": "critical_analysis_of_examples",
                "examples_referenced": True,
                "question_strategy": "deepen_analysis",
                "probing_depth": "deep"
            }

    def _extract_building_type_from_context(self, state: ArchMentorState) -> str:
        """Extract building type from the current design brief"""
        if not state.current_design_brief:
            return "project"
        
        # Simple extraction - look for building type in the brief
        brief_words = state.current_design_brief.lower().split()
        building_types = ["museum", "library", "school", "hospital", "office", "residential", "commercial", "community", "center"]
        
        for word in brief_words:
            if word in building_types:
                return word
        
        return "project"
    
    def _extract_main_topic(self, last_message: str) -> str:
        """Extract the main architectural topic the user is asking about"""
        message_lower = last_message.lower()
        
        # Common architectural topics - this is just for context, not hardcoding responses
        architectural_topics = [
            "adaptive reuse", "sustainability", "lighting", "acoustics", "circulation", 
            "materials", "structure", "accessibility", "energy efficiency", "ventilation",
            "thermal comfort", "daylighting", "spatial organization", "programming",
            "site planning", "landscape", "interior design", "facade design", "construction",
            "building codes", "fire safety", "mechanical systems", "electrical systems",
            "plumbing", "roofing", "foundations", "seismic design", "wind loads",
            "architectural history", "urban design", "placemaking", "community engagement"
        ]
        
        # Find the most relevant topic mentioned
        for topic in architectural_topics:
            if topic in message_lower:
                return topic
        
        # If no specific topic found, extract from context
        words = message_lower.split()
        if "principles" in words:
            # Look for the word before "principles"
            for i, word in enumerate(words):
                if word == "principles" and i > 0:
                    return words[i-1]
        
        # Default to a general architectural inquiry
        return "architectural design"
    
    def _extract_user_specified_focus(self, last_message: str) -> str:
        """Extract what focus area the user has already specified within a topic"""
        message_lower = last_message.lower()
        
        # Generic focus areas that apply to any architectural topic
        focus_indicators = {
            "principles": "principles",
            "examples": "examples", 
            "process": "process",
            "technical": "technical_details",
            "challenges": "challenges",
            "strategies": "strategies",
            "considerations": "considerations",
            "requirements": "requirements",
            "standards": "standards",
            "best practices": "best_practices",
            "approaches": "approaches",
            "methods": "methods",
            "techniques": "techniques",
            "solutions": "solutions",
            "applications": "applications"
        }
        
        # Check for focus indicators
        for indicator, focus_type in focus_indicators.items():
            if indicator in message_lower:
                return focus_type
        
        return ""
    
    def _generate_focused_exploration_question(self, focus_area: str, building_type: str, main_topic: str) -> str:
        """Generate a focused exploration question based on user's specified focus and topic"""








        # Generate contextual questions based on the specific focus area and topic
        if focus_area == "examples":
            return f"Great! You're looking for {main_topic} examples. What specific type of {main_topic} examples would be most helpful for your {building_type} project? Are you interested in seeing how other projects have successfully implemented {main_topic}, or are you looking for examples that solved particular challenges similar to yours?"
        
        elif focus_area == "principles":
            return f"Excellent! Understanding {main_topic} principles is key. What aspect of {main_topic} principles feels most relevant to your {building_type} project right now? Are you looking for the fundamental concepts, or do you need help understanding how to apply these principles in practice?"
        
        elif focus_area == "process":
            return f"Perfect! The {main_topic} process is crucial. What stage of the {main_topic} process are you currently working through in your {building_type} project? Are you in the planning phase, or do you need guidance on implementation steps?"
        
        elif focus_area == "technical_details":
            return f"Good focus! Technical details of {main_topic} are important. What specific technical aspect of {main_topic} are you wrestling with in your {building_type} project? Are you looking at materials, systems integration, or compliance requirements?"
        
        elif focus_area == "challenges":
            return f"Smart thinking! Understanding {main_topic} challenges will help you prepare. What type of {main_topic} challenges are you most concerned about for your {building_type} project? Are you thinking about site-specific issues, budget constraints, or integration with other design elements?"
        
        else:
            return f"Great! You've identified {main_topic} as important for your {building_type} project. What specific question or challenge about {main_topic} are you working through right now? This will help me provide the most relevant guidance for where you are in your design process."






    async def _generate_dynamic_topic_guidance(self, main_topic: str, building_type: str, last_message: str) -> str:
        """Generate dynamic topic-specific guidance using AI for truly contextual responses"""
        
        prompt = f"""
        Generate a dynamic, contextual Socratic question for an architecture student.
        
        CONTEXT:
        - Topic: {main_topic}
        - Building Type: {building_type}
        - Student's Last Message: "{last_message}"
        
        REQUIREMENTS:
        1. Make it specific to their {building_type} project and {main_topic} interest
        2. Reference their actual question/concern from the last message
        3. Ask ONE focused question that will guide their thinking
        4. Avoid generic templates - be specific and contextual
        5. Use a warm, encouraging tone
        6. Keep it under 100 words
        
        Generate ONE dynamic, contextual question:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.7
            )
            
            dynamic_question = response.choices[0].message.content.strip()
            
            if not dynamic_question.endswith('?'):
                dynamic_question += '?'
            
            return dynamic_question
            
        except Exception as e:
            print(f"⚠️ Dynamic guidance generation failed: {e}")
            # Fallback to contextual template
            return f"What specific aspect of {main_topic} in your {building_type} project would you like to explore first?"