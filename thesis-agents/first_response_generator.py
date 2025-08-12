# first_response_generator.py - Enhanced First Response Generation
from typing import Dict, Any, List, Optional, Tuple
import os
from openai import OpenAI
from dotenv import load_dotenv
import sys
import logging

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState
from conversation_progression import ConversationProgressionManager, ConversationPhase, DesignSpaceDimension

load_dotenv()

logger = logging.getLogger(__name__)

class FirstResponseGenerator:
    """Generates progressive first responses that open design spaces and guide users"""
    
    def __init__(self, domain: str = "architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.progression_manager = ConversationProgressionManager(domain)
        self.name = "first_response_generator"
        
        logger.info(f"First Response Generator initialized for {domain}")
    
    async def generate_first_response(self, user_input: str, state: ArchMentorState) -> Dict[str, Any]:
        """Generate a progressive first response that opens design space"""
        
        logger.info("Generating progressive first response")
        logger.info(f"User input: {user_input[:100]}...")
        
        # Analyze first message for progression planning
        logger.info("Step 1: Analyzing first message...")
        progression_analysis = self.progression_manager.analyze_first_message(user_input, state)
        logger.info(f"Progression analysis keys: {list(progression_analysis.keys())}")
        logger.info(f"Opening strategy: {progression_analysis.get('opening_strategy', {}).get('suggested_approach', 'unknown')}")
        
        # 1208-Extract building type from the first message
        logger.info("Step 1.5: Extracting building type from first message...")
        building_type = self._extract_building_type_from_text(user_input)
        logger.info(f"Building type detected: {building_type}")
        
        # 1208-Update progression analysis with building type
        if building_type and building_type != "mixed_use":
            progression_analysis["building_type"] = building_type
            if "opening_strategy" not in progression_analysis:
                progression_analysis["opening_strategy"] = {}
            progression_analysis["opening_strategy"]["building_type"] = building_type
        
        # Generate the opening response
        logger.info("Step 2: Generating opening response...")
        opening_response = await self._generate_opening_response(progression_analysis, user_input)
        logger.info(f"Opening response type: {type(opening_response)}")
        logger.info(f"Opening response length: {len(opening_response) if opening_response else 0}")
        logger.info(f"Opening response preview: {opening_response[:100] if opening_response else 'None'}...")
        
        # Generate follow-up questions to open design space
        logger.info("Step 3: Generating follow-up questions...")
        follow_up_questions = self._generate_follow_up_questions(progression_analysis)
        logger.info(f"Follow-up questions: {follow_up_questions}")
        
        # Create conversation guidance
        logger.info("Step 4: Creating conversation guidance...")
        conversation_guidance = self._create_conversation_guidance(progression_analysis)
        logger.info(f"Conversation guidance keys: {list(conversation_guidance.keys())}")
        
        # Compile complete response
        logger.info("Step 5: Compiling complete response...")
        complete_response = self._compile_complete_response(
            opening_response, follow_up_questions, conversation_guidance
        )
        logger.info(f"Complete response length: {len(complete_response)}")
        logger.info(f"Complete response preview: {complete_response[:200]}...")
        
        return {
            "response_text": complete_response,
            "response_type": "progressive_opening",
            "progression_analysis": progression_analysis,
            "opening_strategy": progression_analysis.get("opening_strategy", {}),
            "conversation_phase": ConversationPhase.DISCOVERY.value,
            "next_steps": progression_analysis.get("next_steps", []),
            "user_profile": progression_analysis.get("user_profile", {}),
            "metadata": {
                "generator": self.name,
                "opening_dimensions": progression_analysis.get("relevant_dimensions", []),
                "intent_analysis": progression_analysis.get("opening_strategy", {}).get("intent_analysis", {}),
                "knowledge_level": progression_analysis.get("user_profile", {}).get("knowledge_level", "unknown"),
                "building_type": progression_analysis.get("building_type", "unknown")
            }
        }
    
    async def _generate_opening_response(self, progression_analysis: Dict, user_input: str) -> str:
        """Generate the main opening response using AI"""
        
        opening_strategy = progression_analysis.get("opening_strategy", {})
        user_profile = progression_analysis.get("user_profile", {})
        
        # Build context for AI generation
        context = self._build_ai_context(progression_analysis, user_input)
        logger.info("Built AI context for opening response")
        
        # Generate response using AI
        try:
            logger.info("Attempting to generate AI opening response...")
            response = await self._generate_ai_response(context)
            logger.info("Successfully generated AI opening response")
            return response
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            logger.info("Falling back to template response")
            return self._generate_fallback_response(progression_analysis)
    
    def _build_ai_context(self, progression_analysis: Dict, user_input: str) -> str:
        """Build context for AI response generation"""
        
        opening_strategy = progression_analysis.get("opening_strategy", {})
        user_profile = progression_analysis.get("user_profile", {})
        milestone = progression_analysis.get("milestone")
        
        # Get building type from progression analysis
        building_type = progression_analysis.get("building_type", "unknown")
        
        context = f"""
You are an expert architectural mentor helping a student begin their learning journey. 

STUDENT'S FIRST MESSAGE: "{user_input}"

ANALYSIS:
- Knowledge Level: {user_profile.get('knowledge_level', 'unknown')}
- Learning Style: {user_profile.get('learning_style', 'unknown')}
- Primary Intent: {opening_strategy.get('suggested_approach', 'guided_exploration')}
- Primary Design Dimension: {opening_strategy.get('primary_dimension', 'functional')}
- Building Type: {building_type}
- Engagement Level: {getattr(milestone, 'engagement_level', 'medium') if milestone else 'medium'}

YOUR ROLE:
Generate a warm, engaging opening response that:
1. Acknowledges their specific project type ({building_type}) and interests
2. Opens up the design space in their area of interest
3. Shows enthusiasm for their learning journey
4. Sets up a collaborative, exploratory tone
5. Avoids overwhelming them with too much information
6. Encourages them to share more about their thinking

RESPONSE GUIDELINES:
- Keep it conversational and encouraging
- Reference their specific project type and interests from their message
- Open 2-3 related design space dimensions relevant to {building_type}
- Ask 1-2 thoughtful follow-up questions specific to their project
- Show you're excited to explore this with them
- Keep it under 150 words for the main response

Focus on opening the design space rather than providing answers.
"""
        
        return context
    
    async def _generate_ai_response(self, context: str) -> str:
        """Generate response using OpenAI"""
        
        try:
            logger.info("Generating AI response with context length: %d", len(context))
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert architectural mentor who excels at opening design spaces and guiding students through progressive learning journeys. You are warm, encouraging, and skilled at asking the right questions to help students explore their interests."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            logger.info("AI response generated successfully, length: %d", len(result))
            return result
            
        except Exception as e:
            logger.error(f"AI generation failed with error: {e}")
            logger.error(f"Context that failed: {context[:200]}...")
            raise e
    
    def _generate_fallback_response(self, progression_analysis: Dict) -> str:
        """Generate fallback response if AI fails"""
        
        opening_strategy = progression_analysis.get("opening_strategy", {})
        primary_dimension = opening_strategy.get("primary_dimension", "functional")
        user_profile = progression_analysis.get("user_profile", {})
        building_type = progression_analysis.get("building_type", "architectural project")
        
        # Simple template-based fallback
        dimension_openings = {
            "functional": "I'm excited to help you explore the functional aspects of your design!",
            "spatial": "Great to see you thinking about spatial relationships and form!",
            "technical": "Excellent focus on the technical aspects of architecture!",
            "contextual": "I love that you're considering the context and environment!",
            "aesthetic": "Wonderful to explore the aesthetic and expressive qualities!",
            "sustainable": "Fantastic to see sustainability informing your design thinking!"
        }
        
        opening = dimension_openings.get(primary_dimension, "I'm excited to help you explore architectural design!")
        
        # Add building type specific context
        if building_type != "unknown" and building_type != "mixed_use":
            building_context = f" I can see you're working on a {building_type} project, which is a fascinating area of architectural design!"
        else:
            building_context = ""
        
        return f"{opening}{building_context} Let's start by understanding what interests you most about this area. What specific aspects would you like to explore together?"
    
    def _generate_follow_up_questions(self, progression_analysis: Dict) -> List[str]:
        """Generate follow-up questions to open design space"""
        
        opening_strategy = progression_analysis.get("opening_strategy", {})
        opening_questions = opening_strategy.get("opening_questions", [])
        user_profile = progression_analysis.get("user_profile", {})
        
        # Select appropriate questions based on knowledge level
        knowledge_level = user_profile.get("knowledge_level", "beginner")
        
        if knowledge_level == "beginner":
            # Start with basic, accessible questions
            selected_questions = opening_questions[:2] if len(opening_questions) >= 2 else opening_questions
        elif knowledge_level == "intermediate":
            # Mix basic and intermediate questions
            selected_questions = opening_questions[1:3] if len(opening_questions) >= 3 else opening_questions
        else:
            # Use more advanced questions
            selected_questions = opening_questions[2:] if len(opening_questions) >= 3 else opening_questions
        
        # Add dimension-specific questions
        dimension_questions = self._get_dimension_specific_questions(progression_analysis)
        
        # Combine and limit to 3 questions maximum
        all_questions = selected_questions + dimension_questions
        return all_questions[:3]
    
    def _get_dimension_specific_questions(self, progression_analysis: Dict) -> List[str]:
        """Get dimension-specific questions based on user's interests"""
        
        relevant_dimensions = progression_analysis.get("relevant_dimensions", [])
        user_profile = progression_analysis.get("user_profile", {})
        knowledge_level = user_profile.get("knowledge_level", "beginner")
        
        dimension_questions = {
            "functional": {
                "beginner": [
                    "What do you think is the most important function this space needs to serve?",
                    "Who are the main people who will use this design?"
                ],
                "intermediate": [
                    "How do you see the program influencing the spatial organization?",
                    "What functional relationships are most critical to your concept?"
                ],
                "advanced": [
                    "How might the program evolve over time, and how does that affect your design approach?",
                    "What functional synergies or conflicts are you considering?"
                ]
            },
            "spatial": {
                "beginner": [
                    "How do you imagine people moving through this space?",
                    "What kind of feeling do you want the spaces to have?"
                ],
                "intermediate": [
                    "How are you thinking about the relationship between interior and exterior spaces?",
                    "What role does light and view play in your spatial concept?"
                ],
                "advanced": [
                    "How are you considering the dialogue between form and space?",
                    "What spatial hierarchies are emerging in your thinking?"
                ]
            },
            "technical": {
                "beginner": [
                    "What materials or construction methods interest you most?",
                    "How do you think the structure should support your design ideas?"
                ],
                "intermediate": [
                    "How are technical decisions supporting your design intent?",
                    "What role does materiality play in your concept?"
                ],
                "advanced": [
                    "How are you integrating technical innovation with design expression?",
                    "What technical challenges are driving your design decisions?"
                ]
            },
            "contextual": {
                "beginner": [
                    "What aspects of the site or context are most important to you?",
                    "How do you want your design to respond to its environment?"
                ],
                "intermediate": [
                    "How is the context shaping your design decisions?",
                    "What cultural or environmental factors are influencing your approach?"
                ],
                "advanced": [
                    "How are you creating a dialogue between building and place?",
                    "What contextual opportunities or constraints are driving innovation?"
                ]
            },
            "aesthetic": {
                "beginner": [
                    "What kind of aesthetic qualities are you drawn to?",
                    "How do you want people to feel when they experience your design?"
                ],
                "intermediate": [
                    "How are aesthetic choices communicating meaning?",
                    "What architectural language or style resonates with your concept?"
                ],
                "advanced": [
                    "How are you balancing beauty and utility in your approach?",
                    "What role does architectural expression play in your design philosophy?"
                ]
            },
            "sustainable": {
                "beginner": [
                    "What sustainable aspects are most important to your design?",
                    "How do you want your design to respond to environmental challenges?"
                ],
                "intermediate": [
                    "How are sustainability principles shaping your design decisions?",
                    "What environmental, social, and economic factors are you considering?"
                ],
                "advanced": [
                    "How are you integrating sustainability innovation with design excellence?",
                    "What sustainable strategies are driving your design approach?"
                ]
            }
        }
        
        questions = []
        for dimension in relevant_dimensions:
            if dimension in dimension_questions:
                dimension_question_set = dimension_questions[dimension]
                level_questions = dimension_question_set.get(knowledge_level, dimension_question_set.get("beginner", []))
                questions.extend(level_questions)
        
        return questions
    
    def _create_conversation_guidance(self, progression_analysis: Dict) -> Dict[str, Any]:
        """Create guidance for the conversation progression"""
        
        opening_strategy = progression_analysis.get("opening_strategy", {})
        user_profile = progression_analysis.get("user_profile", {})
        
        return {
            "current_phase": ConversationPhase.DISCOVERY.value,
            "phase_objectives": [
                "Understand your specific interests and goals",
                "Open relevant design space dimensions",
                "Establish a collaborative learning relationship",
                "Identify areas for deeper exploration"
            ],
            "suggested_approach": opening_strategy.get("suggested_approach", "guided_exploration"),
            "knowledge_gaps": opening_strategy.get("knowledge_gaps", []),
            "next_phase_preparation": [
                "Share your thoughts on the questions above",
                "Tell me more about what interests you most",
                "Ask about any concepts you'd like to explore further"
            ],
            "learning_style_adaptation": self._adapt_to_learning_style(user_profile)
        }
    
    def _adapt_to_learning_style(self, user_profile: Dict) -> Dict[str, Any]:
        """Adapt approach to user's learning style"""
        
        learning_style = user_profile.get("learning_style", "balanced")
        
        adaptations = {
            "visual": {
                "suggestions": [
                    "Consider sketching or diagramming your ideas",
                    "Look for visual examples and precedents",
                    "Think about spatial relationships visually"
                ],
                "resources": ["diagrams", "sketches", "visual examples", "spatial models"]
            },
            "analytical": {
                "suggestions": [
                    "Break down complex concepts systematically",
                    "Analyze relationships between different elements",
                    "Consider the underlying principles and logic"
                ],
                "resources": ["frameworks", "analysis tools", "systematic approaches", "theoretical foundations"]
            },
            "experiential": {
                "suggestions": [
                    "Think about how you would experience the spaces",
                    "Consider the human experience and interaction",
                    "Imagine walking through and using the design"
                ],
                "resources": ["experience mapping", "user scenarios", "interaction design", "sensory considerations"]
            },
            "balanced": {
                "suggestions": [
                    "Combine different ways of thinking about the problem",
                    "Balance intuitive and analytical approaches",
                    "Consider both the big picture and the details"
                ],
                "resources": ["integrated approaches", "multiple perspectives", "holistic thinking"]
            }
        }
        
        return adaptations.get(learning_style, adaptations["balanced"])
    
    def _compile_complete_response(self, opening_response: str, 
                                 follow_up_questions: List[str],
                                 conversation_guidance: Dict) -> str:
        """Compile the complete progressive response"""
        
        # Start with the opening response
        response_parts = [opening_response]
        
        # Add follow-up questions if they weren't already included in the opening
        if follow_up_questions and not any(q in opening_response for q in follow_up_questions):
            response_parts.append("\n\nTo help us explore this together, I'd love to hear your thoughts on:")
            
            for i, question in enumerate(follow_up_questions, 1):
                response_parts.append(f"\n{i}. {question}")
        
        # Add conversation guidance
        response_parts.append("\n\n**How we'll work together:**")
        response_parts.append("I'm here to guide you through a progressive learning journey. We'll start by understanding your interests and then explore the design space together, building your knowledge step by step.")
        
        # Add next steps
        next_steps = conversation_guidance.get("next_phase_preparation", [])
        if next_steps:
            response_parts.append("\n**Next steps:**")
            for step in next_steps:
                response_parts.append(f"• {step}")
        
        # Add encouragement
        response_parts.append("\nI'm excited to explore this architectural journey with you! What would you like to start with?")
        
        return " ".join(response_parts)
    
    def generate_topic_transition_response(self, new_topic: str, 
                                         current_progression: Dict,
                                         state: ArchMentorState) -> Dict[str, Any]:
        """Generate response for topic transitions within the conversation"""
        
        # Analyze the new topic
        topic_analysis = self._analyze_new_topic(new_topic, current_progression)
        
        # Generate transition response
        transition_response = self._generate_topic_transition(new_topic, topic_analysis)
        
        # Update progression for new topic
        updated_progression = self._update_progression_for_topic(new_topic, topic_analysis)
        
        return {
            "response_text": transition_response,
            "response_type": "topic_transition",
            "topic_analysis": topic_analysis,
            "updated_progression": updated_progression,
            "conversation_phase": ConversationPhase.DISCOVERY.value,  # Reset to discovery for new topic
            "metadata": {
                "generator": self.name,
                "transition_type": "topic_change",
                "new_topic": new_topic
            }
        }
    
    def _analyze_new_topic(self, new_topic: str, current_progression: Dict) -> Dict[str, Any]:
        """Analyze how the new topic relates to current progression"""
        
        # This would integrate with your existing topic analysis
        # For now, returning basic analysis
        return {
            "topic": new_topic,
            "related_dimensions": self._identify_topic_dimensions(new_topic),
            "complexity_level": "intermediate",  # Would be determined by analysis
            "connection_to_previous": "new_exploration",
            "learning_opportunities": ["concept_development", "skill_building"]
        }
    
    def _identify_topic_dimensions(self, topic: str) -> List[str]:
        """Identify which design dimensions the new topic relates to"""
        
        topic_lower = topic.lower()
        dimensions = []
        
        dimension_keywords = {
            "functional": ["function", "program", "use", "purpose"],
            "spatial": ["space", "form", "layout", "circulation"],
            "technical": ["structure", "construction", "material", "system"],
            "contextual": ["site", "context", "environment", "place"],
            "aesthetic": ["beauty", "style", "appearance", "expression"],
            "sustainable": ["sustainable", "environmental", "green", "eco"]
        }
        
        for dimension, keywords in dimension_keywords.items():
            if any(keyword in topic_lower for keyword in keywords):
                dimensions.append(dimension)
        
        return dimensions if dimensions else ["functional", "spatial"]
    
    def _generate_topic_transition(self, new_topic: str, topic_analysis: Dict) -> str:
        """Generate response for transitioning to new topic"""
        
        related_dimensions = topic_analysis.get("related_dimensions", [])
        
        transition_templates = {
            "functional": f"Great! Let's explore the functional aspects of {new_topic}. This is a fascinating area where we can examine how purpose and use shape design decisions.",
            "spatial": f"Excellent choice! {new_topic} offers wonderful opportunities to explore spatial relationships and how form creates meaning.",
            "technical": f"Perfect! {new_topic} is a great area to examine how technical decisions support and enhance design intent.",
            "contextual": f"Wonderful! {new_topic} is ideal for exploring how context and environment influence design choices.",
            "aesthetic": f"Fantastic! {new_topic} provides rich ground for exploring aesthetic expression and how beauty serves function.",
            "sustainable": f"Excellent! {new_topic} is perfect for examining how sustainability principles inform and enhance design."
        }
        
        # Use the first related dimension for the transition
        primary_dimension = related_dimensions[0] if related_dimensions else "functional"
        transition = transition_templates.get(primary_dimension, f"Great! Let's explore {new_topic} together. This is a fascinating area of architectural design.")
        
        return f"{transition}\n\nWhat specific aspects of {new_topic} interest you most? I'd love to hear your thoughts and help you explore this area."
    
    def _update_progression_for_topic(self, new_topic: str, topic_analysis: Dict) -> Dict[str, Any]:
        """Update progression analysis for the new topic"""
        
        # Reset to discovery phase for new topic
        self.progression_manager.current_phase = ConversationPhase.DISCOVERY
        
        # Create new milestone for topic transition
        new_milestone = self.progression_manager.milestones[-1] if self.progression_manager.milestones else None
        
        return {
            "current_phase": ConversationPhase.DISCOVERY.value,
            "new_topic": new_topic,
            "related_dimensions": topic_analysis.get("related_dimensions", []),
            "learning_opportunities": topic_analysis.get("learning_opportunities", []),
            "transition_type": "topic_change"
        } 
    
    def _extract_building_type_from_text(self, input_text: str) -> str:
        """
        Get building type from state - NO MORE DETECTION, just retrieval.
        Building type is now centrally managed in conversation_progression.py
        """
        # This method is now deprecated - building type detection is centralized
        # Return unknown to force use of centrally managed building type
        return "unknown"