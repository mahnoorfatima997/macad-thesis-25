"""
Challenge generation processing module for creating cognitive challenges.
"""
from typing import Dict, Any, List
import random
from ..config import CHALLENGE_TEMPLATES
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry, LLMClient
from state_manager import ArchMentorState


class ChallengeGeneratorProcessor:
    """
    Processes cognitive challenge generation and strategy selection.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("challenge_generator")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        self.client = LLMClient()
        
    def select_enhancement_strategy(self, cognitive_state: Dict, analysis_result: Dict, state: ArchMentorState) -> str:
        """
        Select appropriate enhancement strategy based on cognitive state.
        """
        self.telemetry.log_agent_start("select_enhancement_strategy")
        
        try:
            # Strategy selection based on cognitive state
            if cognitive_state.get("overconfidence_level") == "high":
                return "challenge_assumptions"
            elif cognitive_state.get("passivity_level") == "high":
                return "increase_engagement"
            elif cognitive_state.get("metacognitive_awareness") == "low":
                return "promote_reflection"
            elif cognitive_state.get("cognitive_load") == "underload":
                return "increase_challenge"
            elif cognitive_state.get("engagement_level") == "low":
                return "stimulate_curiosity"
            else:
                return "balanced_development"
                
        except Exception as e:
            self.telemetry.log_error("select_enhancement_strategy", str(e))
            return "balanced_development"
    
    async def generate_cognitive_challenge(self, strategy: str, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """
        Generate appropriate cognitive challenge based on strategy.
        """
        self.telemetry.log_agent_start("generate_cognitive_challenge")
        
        try:
            # Select challenge type based on strategy
            challenge_mapping = {
                "challenge_assumptions": ("metacognitive_challenge", "assumptions"),
                "increase_engagement": ("perspective_challenge", "user_perspective"),
                "promote_reflection": ("metacognitive_challenge", "process_reflection"),
                "increase_challenge": ("constraint_challenge", "spatial"),
                "stimulate_curiosity": ("alternative_challenge", "structural"),
                "balanced_development": ("perspective_challenge", "temporal_perspective")
            }
            
            challenge_type, subtype = challenge_mapping.get(strategy, ("constraint_challenge", "functional"))
            
            # Generate specific challenge based on type
            if challenge_type == "constraint_challenge":
                challenge_result = await self._generate_constraint_challenge(cognitive_state, state, analysis_result, subtype)
            elif challenge_type == "perspective_challenge":
                challenge_result = await self._generate_perspective_challenge(cognitive_state, state, analysis_result, subtype)
            elif challenge_type == "alternative_challenge":
                challenge_result = await self._generate_alternative_challenge(cognitive_state, state, analysis_result, subtype)
            elif challenge_type == "metacognitive_challenge":
                challenge_result = await self._generate_metacognitive_challenge(cognitive_state, state, analysis_result, subtype)
            else:
                challenge_result = await self._generate_general_challenge(cognitive_state, state, analysis_result)
            
            # Add strategy and pedagogical information
            challenge_result.update({
                "strategy": strategy,
                "challenge_type": challenge_type,
                "subtype": subtype,
                "pedagogical_intent": self._get_pedagogical_intent(strategy, cognitive_state),
                "difficulty_level": self._assess_challenge_difficulty(challenge_result, cognitive_state),
                "generation_timestamp": self.telemetry.get_timestamp()
            })
            
            return challenge_result
            
        except Exception as e:
            self.telemetry.log_error("generate_cognitive_challenge", str(e))
            return self._get_fallback_challenge(strategy)
    
    async def _generate_constraint_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, constraint_type: str = "spatial") -> Dict[str, Any]:
        """Generate constraint-based cognitive challenge."""
        self.telemetry.log_agent_start("_generate_constraint_challenge")
        
        try:
            # Get challenge templates for constraint type
            challenges = CHALLENGE_TEMPLATES.get("constraint_challenge", {}).get(constraint_type, [])
            if not challenges:
                challenges = ["How would your design change under different constraints?"]
            
            base_challenge = random.choice(challenges)
            contextualized_challenge = await self._contextualize_challenge(base_challenge, state, "constraint_challenge", constraint_type)
            
            return {
                "challenge_text": contextualized_challenge,
                "challenge_type": "constraint_challenge",
                "constraint_type": constraint_type,
                "pedagogical_intent": "Challenge design assumptions through constraint exploration",
                "cognitive_target": "flexibility_and_adaptation",
                "expected_outcome": "Increased design flexibility and creative problem-solving"
            }
            
        except Exception as e:
            self.telemetry.log_error("_generate_constraint_challenge", str(e))
            return {
                "challenge_text": "Consider how your design would adapt to different constraints.",
                "challenge_type": "constraint_challenge",
                "constraint_type": constraint_type,
                "pedagogical_intent": "Encourage adaptive thinking",
                "cognitive_target": "flexibility"
            }
    
    async def _generate_perspective_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, perspective_type: str = "user_perspective") -> Dict[str, Any]:
        """Generate perspective-shifting cognitive challenge."""
        self.telemetry.log_agent_start("_generate_perspective_challenge")
        
        try:
            # Get challenge templates for perspective type
            challenges = CHALLENGE_TEMPLATES.get("perspective_challenge", {}).get(perspective_type, [])
            if not challenges:
                challenges = ["How would different users experience your design?"]
            
            base_challenge = random.choice(challenges)
            contextualized_challenge = await self._contextualize_challenge(base_challenge, state, "perspective_challenge", perspective_type)
            
            # SMART GAMIFICATION: Only apply gamification when appropriate
            should_gamify = self._should_apply_gamification(state, perspective_type, "perspective_challenge")

            if should_gamify:
                gamified_challenge = await self._add_gamification_elements(contextualized_challenge, perspective_type, state)
                gamification_applied = True
            else:
                gamified_challenge = contextualized_challenge
                gamification_applied = False

            return {
                "challenge_text": gamified_challenge,
                "challenge_type": "perspective_challenge",
                "perspective_type": perspective_type,
                "pedagogical_intent": "Expand perspective and empathy in design thinking",
                "cognitive_target": "perspective_taking",
                "expected_outcome": "Enhanced empathy and user-centered design thinking",
                "gamification_applied": gamification_applied
            }
            
        except Exception as e:
            self.telemetry.log_error("_generate_perspective_challenge", str(e))
            return {
                "challenge_text": "Consider how different users might experience your design.",
                "challenge_type": "perspective_challenge",
                "perspective_type": perspective_type,
                "pedagogical_intent": "Encourage empathetic design thinking",
                "cognitive_target": "empathy"
            }

    async def _add_gamification_elements(self, base_challenge: str, challenge_type: str, state: ArchMentorState) -> str:
        """Add interactive gamification elements to challenges."""
        try:
            # Get project context
            project_context = getattr(state, 'current_design_brief', 'architectural project')
            building_type = self._extract_building_type(project_context)

            # Gamification templates with nice formatting for UI
            gamification_templates = {
                "user_perspective": [
                    "🎭 ROLE-PLAY CHALLENGE: Step into someone else's shoes!\n\n*You are now a {user_type} entering your {building_type} for the first time.*\n\n{base_challenge}\n\nWalk me through your first 60 seconds - what do you see, feel, and think?",
                    "🎯 PERSPECTIVE SHIFT: Time for a reality check!\n\n*Plot twist: You're designing for someone completely different than you imagined.*\n\n{base_challenge}\n\nTell me: How does this change everything?",
                    "🔍 USER DETECTIVE: Let's solve a mystery!\n\n*Your {building_type} has a secret - different users experience it completely differently.*\n\n{base_challenge}\n\nWhat clues in your design reveal these hidden experiences?"
                ],
                "spatial": [
                    "🏗️ SPACE TRANSFORMATION: Your design just got interesting!\n\n*Imagine your {building_type} could shape-shift based on user needs.*\n\n{base_challenge}\n\nDescribe the transformation - what changes and why?",
                    "🎨 SPATIAL STORYTELLING: Every space tells a story!\n\n*Your {building_type} is the main character in an architectural narrative.*\n\n{base_challenge}\n\nWhat story does your space want to tell?",
                    "⚡ DESIGN CHALLENGE: Time for a creative constraint!\n\n*Your {building_type} just got a plot twist that changes everything.*\n\n{base_challenge}\n\nHow do you turn this constraint into your design's superpower?"
                ],
                "temporal_perspective": [
                    "⏰ TIME TRAVEL CHALLENGE: Your building through the ages!\n\n*Fast-forward 20 years - your {building_type} has evolved with its community.*\n\n{base_challenge}\n\nWhat story does this future version tell about adaptability?",
                    "🔄 LIFECYCLE ADVENTURE: From birth to rebirth!\n\n*Your {building_type} is about to go through a major life change.*\n\n{base_challenge}\n\nHow does good design prepare for transformation?",
                    "🌅 DAILY RHYTHM CHALLENGE: 24 hours in the life!\n\n*Your {building_type} experiences dawn, noon, dusk, and midnight differently.*\n\n{base_challenge}\n\nHow does your design dance with time?"
                ]
            }

            # Select appropriate template
            templates = gamification_templates.get(challenge_type, gamification_templates["spatial"])
            template = self.text_processor.select_random(templates)

            # Context-specific user types
            user_types = {
                "community center": ["busy parent", "elderly community member", "teenager", "person with mobility challenges"],
                "hospital": ["anxious patient", "worried family member", "exhausted healthcare worker", "first-time visitor"],
                "office": ["new employee", "client visitor", "maintenance worker", "executive"],
                "school": ["nervous student", "visiting parent", "substitute teacher", "administrator"]
            }

            user_type = self.text_processor.select_random(user_types.get(building_type, ["community member", "visitor", "user", "person"]))

            # Format the gamified challenge
            gamified_challenge = template.format(
                base_challenge=base_challenge,
                building_type=building_type,
                user_type=user_type
            )

            return gamified_challenge

        except Exception as e:
            self.telemetry.log_error("_add_gamification_elements", str(e))
            return base_challenge  # Return original if gamification fails

    def _should_apply_gamification(self, state: ArchMentorState, challenge_type: str, context: str) -> bool:
        """
        Smart gamification trigger - based on routing_test_user_inputs.md patterns.

        Gamification should ONLY be applied for specific trigger patterns:
        - Role-play questions (How would a visitor feel...)
        - Perspective questions (What would an elderly person think...)
        - Curiosity amplification (I wonder what would happen...)
        - Creative constraints (I'm stuck on...)
        - Reality checks (This seems pretty easy...)
        - Low engagement (Ok, Yes, Sure...)
        - Overconfidence (I already know exactly what to do...)
        - Cognitive offloading (Just tell me what to do...)
        """
        try:
            # Get conversation history
            messages = getattr(state, 'messages', [])
            user_messages = [msg for msg in messages if msg.get('role') == 'user']

            if len(user_messages) == 0:
                return False

            latest_message = user_messages[-1].get('content', '').lower().strip()

            # 1. ROLE-PLAY TRIGGERS (from routing test lines 12-16, 36-40)
            role_play_patterns = [
                'how would a visitor feel', 'how would', 'what would', 'from the perspective of',
                'how do users feel', 'what would an elderly person', 'what would a child'
            ]
            if any(pattern in latest_message for pattern in role_play_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Role-play question detected")
                return True

            # 2. CURIOSITY AMPLIFICATION (line 18)
            curiosity_patterns = ['i wonder what would happen', 'what if', 'i wonder']
            if any(pattern in latest_message for pattern in curiosity_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Curiosity amplification detected")
                return True

            # 3. CREATIVE CONSTRAINTS (line 21)
            constraint_patterns = ['i\'m stuck on', 'stuck on', 'having trouble', 'not sure how']
            if any(pattern in latest_message for pattern in constraint_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Creative constraint detected")
                return True

            # 4. REALITY CHECK / OVERCONFIDENCE (lines 24, 33)
            overconfidence_patterns = [
                'this seems pretty easy', 'this is easy', 'i already know exactly',
                'i already know', 'that\'s obvious', 'simple', 'basic'
            ]
            if any(pattern in latest_message for pattern in overconfidence_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Overconfidence/reality check detected")
                return True

            # 5. LOW ENGAGEMENT (lines 27-31)
            low_engagement_responses = ['ok', 'yes', 'sure', 'fine', 'alright', 'cool', 'maybe']
            if latest_message in low_engagement_responses:
                print(f"🎮 GAMIFICATION TRIGGER: Low engagement detected")
                return True

            # 6. COGNITIVE OFFLOADING (lines 223-233)
            offloading_patterns = [
                'just tell me what to do', 'can you design this', 'tell me what to do',
                'what should i do', 'give me the answer', 'what\'s the standard solution'
            ]
            if any(pattern in latest_message for pattern in offloading_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Cognitive offloading detected")
                return True

            # Default: no gamification for normal design statements, technical questions, etc.
            print(f"🎮 GAMIFICATION SKIP: Normal design statement/question (no trigger patterns)")
            return False

        except Exception as e:
            print(f"🎮 GAMIFICATION ERROR: {e}")
            return False  # Default to no gamification on error

    def _extract_building_type(self, project_context: str) -> str:
        """Extract building type from project context."""
        building_types = ["community center", "hospital", "office", "school", "library", "museum", "residential"]
        project_lower = project_context.lower()

        for building_type in building_types:
            if building_type in project_lower:
                return building_type

        return "building"  # Default fallback
    
    async def _generate_alternative_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, alternative_type: str = "structural") -> Dict[str, Any]:
        """Generate alternative exploration cognitive challenge."""
        self.telemetry.log_agent_start("_generate_alternative_challenge")
        
        try:
            # Get challenge templates for alternative type
            challenges = CHALLENGE_TEMPLATES.get("alternative_challenge", {}).get(alternative_type, [])
            if not challenges:
                challenges = ["What alternative approaches could you explore?"]
            
            base_challenge = random.choice(challenges)
            contextualized_challenge = await self._contextualize_challenge(base_challenge, state, "alternative_challenge", alternative_type)
            
            return {
                "challenge_text": contextualized_challenge,
                "challenge_type": "alternative_challenge",
                "alternative_type": alternative_type,
                "pedagogical_intent": "Encourage exploration of design alternatives",
                "cognitive_target": "divergent_thinking",
                "expected_outcome": "Increased creative exploration and solution diversity"
            }
            
        except Exception as e:
            self.telemetry.log_error("_generate_alternative_challenge", str(e))
            return {
                "challenge_text": "Explore alternative approaches to your current design solution.",
                "challenge_type": "alternative_challenge",
                "alternative_type": alternative_type,
                "pedagogical_intent": "Encourage creative exploration",
                "cognitive_target": "creativity"
            }
    
    async def _generate_metacognitive_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, metacognitive_type: str = "process_reflection") -> Dict[str, Any]:
        """Generate metacognitive reflection challenge."""
        self.telemetry.log_agent_start("_generate_metacognitive_challenge")
        
        try:
            # Get challenge templates for metacognitive type
            challenges = CHALLENGE_TEMPLATES.get("metacognitive_challenge", {}).get(metacognitive_type, [])
            if not challenges:
                challenges = ["What are you thinking about your thinking in this design process?"]
            
            base_challenge = random.choice(challenges)
            contextualized_challenge = await self._contextualize_challenge(base_challenge, state, "metacognitive_challenge", metacognitive_type)

            # SMART GAMIFICATION: Only apply gamification when appropriate
            should_gamify = self._should_apply_gamification(state, metacognitive_type, "metacognitive_challenge")

            if should_gamify:
                gamified_challenge = await self._add_gamification_elements(contextualized_challenge, metacognitive_type, state)
                gamification_applied = True
            else:
                gamified_challenge = contextualized_challenge
                gamification_applied = False

            return {
                "challenge_text": gamified_challenge,
                "challenge_type": "metacognitive_challenge",
                "metacognitive_type": metacognitive_type,
                "pedagogical_intent": "Foster metacognitive awareness and self-evaluation" + (" with focus on increasing engagement" if gamification_applied else ""),
                "cognitive_target": "metacognition",
                "expected_outcome": "Enhanced self-awareness and reflective practice",
                "gamification_applied": gamification_applied
            }
            
        except Exception as e:
            self.telemetry.log_error("_generate_metacognitive_challenge", str(e))
            return {
                "challenge_text": "Reflect on your design thinking process and decision-making.",
                "challenge_type": "metacognitive_challenge",
                "metacognitive_type": metacognitive_type,
                "pedagogical_intent": "Encourage self-reflection",
                "cognitive_target": "self_awareness"
            }
    
    async def _generate_general_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict) -> Dict[str, Any]:
        """Generate general cognitive challenge when specific types aren't suitable."""
        general_challenges = [
            "What aspect of your design would you like to explore more deeply?",
            "How might you approach this problem from a completely different angle?",
            "What would happen if you had to explain your design to someone from a different field?",
            "Which part of your design process feels most uncertain, and how could you address that?",
            "What would you do differently if you started this project again?"
        ]
        
        return {
            "challenge_text": random.choice(general_challenges),
            "challenge_type": "general_challenge",
            "pedagogical_intent": "Stimulate general cognitive engagement",
            "cognitive_target": "general_reflection",
            "expected_outcome": "Increased engagement and deeper thinking"
        }
    
    async def _contextualize_challenge(self, base_challenge: str, state: ArchMentorState, challenge_type: str, subtype: str) -> str:
        """Contextualize challenge to the current project and user's specific question."""
        try:
            project_context = getattr(state, 'current_design_brief', 'architectural project')
            
            # Get user's last question to make the challenge relevant
            user_messages = getattr(state, 'messages', [])
            user_input = ""
            if user_messages:
                for msg in reversed(user_messages):
                    if msg.get('role') == 'user':
                        user_input = msg.get('content', '')
                        break
            
            # Extract key context from user's question
            user_context = self._extract_user_context(user_input)
            
            prompt = f"""
            Adapt this cognitive challenge for an architecture student's specific project and question:
            
            BASE CHALLENGE: {base_challenge}
            STUDENT'S PROJECT: {project_context}
            STUDENT'S QUESTION: {user_input[:200] if user_input else "No specific question provided"}
            CHALLENGE TYPE: {challenge_type} - {subtype}
            USER CONTEXT: {user_context}
            
            Make the challenge:
            1. DIRECTLY RELEVANT to what they're asking about
            2. Specific to their architectural project
            3. Thought-provoking and engaging
            4. Appropriate for their skill level
            5. Clear and actionable
            
            IMPORTANT: The challenge must relate to their specific question, not be generic.
            If they're asking about outdoor area placement, focus on that.
            If they're asking about material choices, focus on that.
            
            Keep it under 100 words and end with a specific question that builds on their inquiry.
            """
            
            response = await self.client.generate_completion([
                self.client.create_system_message("You are an expert in architectural pedagogy who creates relevant, contextual challenges."),
                self.client.create_user_message(prompt)
            ])
            
            if response and response.get("content"):
                return response["content"]
            
        except Exception as e:
            self.telemetry.log_error(f"Challenge contextualization failed: {e}")
        
        # Fallback to context-aware challenge
        return self._generate_context_aware_fallback(user_input, project_context, challenge_type)
    
    def _extract_user_context(self, user_input: str) -> str:
        """Extract key context from user's question to make challenges relevant."""
        if not user_input:
            return "general architectural inquiry"
        
        user_input_lower = user_input.lower()
        
        # Check for specific architectural elements
        if any(word in user_input_lower for word in ["outdoor", "garden", "courtyard", "landscape"]):
            return "outdoor space design and placement"
        elif any(word in user_input_lower for word in ["classroom", "room", "space", "area"]):
            return "interior space organization and layout"
        elif any(word in user_input_lower for word in ["material", "construction", "building"]):
            return "material selection and construction methods"
        elif any(word in user_input_lower for word in ["light", "sunlight", "natural light"]):
            return "lighting and environmental factors"
        elif any(word in user_input_lower for word in ["organize", "layout", "arrange", "place"]):
            return "spatial organization and arrangement"
        elif any(word in user_input_lower for word in ["approach", "strategy", "method"]):
            return "design approach and methodology"
        else:
            return "general design inquiry"
    
    def _generate_context_aware_fallback(self, user_input: str, project_context: str, challenge_type: str) -> str:
        """Generate a context-aware fallback challenge when LLM fails."""
        if not user_input:
            return f"Consider how users will experience your {project_context} at different times and conditions."
        
        user_input_lower = user_input.lower()
        
        # Generate relevant fallback based on user's question
        if any(word in user_input_lower for word in ["outdoor", "garden", "courtyard"]):
            return f"Think about how the placement of outdoor areas in your {project_context} affects the flow and experience of users throughout the day and seasons."
        elif any(word in user_input_lower for word in ["classroom", "room", "space"]):
            return f"Consider how the organization of spaces in your {project_context} influences user movement, interaction, and learning outcomes."
        elif any(word in user_input_lower for word in ["organize", "layout", "arrange"]):
            return f"Reflect on how your spatial organization choices in this {project_context} will impact user experience and project success."
        else:
            return f"Consider how your design decisions for this {project_context} will be experienced by different users and in various conditions."
    
    def _get_pedagogical_intent(self, strategy: str, cognitive_state: Dict) -> str:
        """Get pedagogical intent for the strategy."""
        intent_mapping = {
            "challenge_assumptions": "Encourage critical thinking and question underlying assumptions",
            "increase_engagement": "Stimulate active participation and deeper involvement",
            "promote_reflection": "Foster metacognitive awareness and self-evaluation",
            "increase_challenge": "Provide appropriate cognitive challenge for growth",
            "stimulate_curiosity": "Spark interest and motivation for exploration",
            "balanced_development": "Support well-rounded cognitive development"
        }
        
        base_intent = intent_mapping.get(strategy, "Support cognitive development")
        
        # Customize based on cognitive state
        if cognitive_state.get("engagement_level") == "low":
            base_intent += " with focus on increasing engagement"
        elif cognitive_state.get("cognitive_load") == "overload":
            base_intent += " while managing cognitive load"
        
        return base_intent
    
    def _assess_challenge_difficulty(self, challenge_result: Dict, cognitive_state: Dict) -> str:
        """Assess the difficulty level of the generated challenge."""
        try:
            challenge_type = challenge_result.get("challenge_type", "general")
            cognitive_load = cognitive_state.get("cognitive_load", "optimal")
            engagement_level = cognitive_state.get("engagement_level", "moderate")
            
            # Base difficulty on challenge type
            difficulty_mapping = {
                "constraint_challenge": "medium",
                "perspective_challenge": "medium",
                "alternative_challenge": "high",
                "metacognitive_challenge": "high",
                "general_challenge": "low"
            }
            
            base_difficulty = difficulty_mapping.get(challenge_type, "medium")
            
            # Adjust based on cognitive state
            if cognitive_load == "overload":
                # Reduce difficulty if student is overwhelmed
                if base_difficulty == "high":
                    return "medium"
                elif base_difficulty == "medium":
                    return "low"
            elif cognitive_load == "underload" and engagement_level == "high":
                # Increase difficulty if student needs more challenge
                if base_difficulty == "low":
                    return "medium"
                elif base_difficulty == "medium":
                    return "high"
            
            return base_difficulty
            
        except Exception as e:
            self.telemetry.log_error("_assess_challenge_difficulty", str(e))
            return "medium"
    
    def _get_fallback_challenge(self, strategy: str) -> Dict[str, Any]:
        """Get fallback challenge when generation fails."""
        fallback_challenges = {
            "challenge_assumptions": "What assumptions might you be making about this design problem?",
            "increase_engagement": "What aspect of this project interests you most, and why?",
            "promote_reflection": "How would you describe your design thinking process so far?",
            "increase_challenge": "How might you make this design more ambitious or complex?",
            "stimulate_curiosity": "What would you like to learn more about in this project?",
            "balanced_development": "What's the next step in developing your design?"
        }
        
        return {
            "challenge_text": fallback_challenges.get(strategy, "Continue developing your design approach."),
            "challenge_type": "fallback_challenge",
            "strategy": strategy,
            "pedagogical_intent": "Maintain engagement and progress",
            "cognitive_target": "continued_development",
            "difficulty_level": "medium"
        }
    
    def evaluate_challenge_effectiveness(self, challenge_history: List[Dict], state: ArchMentorState) -> Dict[str, Any]:
        """Evaluate the effectiveness of previous challenges."""
        try:
            if not challenge_history:
                return {
                    "effectiveness_score": 0.5,
                    "recommendations": ["Continue with balanced challenge approach"]
                }
            
            recent_challenges = challenge_history[-3:] if len(challenge_history) >= 3 else challenge_history
            
            # Analyze challenge types and outcomes
            challenge_types = {}
            difficulty_levels = {}
            
            for challenge in recent_challenges:
                c_type = challenge.get("challenge_type", "unknown")
                difficulty = challenge.get("difficulty_level", "medium")
                
                challenge_types[c_type] = challenge_types.get(c_type, 0) + 1
                difficulty_levels[difficulty] = difficulty_levels.get(difficulty, 0) + 1
            
            # Simple effectiveness assessment
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            if len(user_messages) >= 2:
                recent_engagement = len(user_messages[-1].split())
                earlier_engagement = len(user_messages[-2].split())
                engagement_trend = recent_engagement / max(earlier_engagement, 1)
            else:
                engagement_trend = 1.0
            
            effectiveness_score = min(engagement_trend * 0.6 + 0.2, 1.0)
            
            return {
                "effectiveness_score": effectiveness_score,
                "challenge_types": challenge_types,
                "difficulty_distribution": difficulty_levels,
                "engagement_trend": engagement_trend,
                "recommendations": self._generate_challenge_recommendations(effectiveness_score, challenge_types, difficulty_levels)
            }
            
        except Exception as e:
            self.telemetry.log_error("evaluate_challenge_effectiveness", str(e))
            return {
                "effectiveness_score": 0.5,
                "error": str(e),
                "recommendations": ["Continue with current challenge approach"]
            }
    
    def _generate_challenge_recommendations(self, effectiveness_score: float, challenge_types: Dict, difficulty_levels: Dict) -> List[str]:
        """Generate recommendations for future challenge selection."""
        recommendations = []
        
        if effectiveness_score < 0.4:
            recommendations.append("Consider reducing challenge difficulty")
            recommendations.append("Focus on more engaging challenge types")
        elif effectiveness_score > 0.8:
            recommendations.append("Current challenge approach is highly effective")
            recommendations.append("Consider gradually increasing difficulty")
        else:
            recommendations.append("Challenge effectiveness is moderate - continue with adjustments")
        
        # Type-specific recommendations
        if challenge_types.get("metacognitive_challenge", 0) > 2:
            recommendations.append("Balance metacognitive challenges with more concrete tasks")
        
        if difficulty_levels.get("high", 0) > difficulty_levels.get("low", 0) + difficulty_levels.get("medium", 0):
            recommendations.append("Consider including more accessible challenges")
        
        return recommendations
    
    def generate_challenge_summary(self, challenges: List[Dict]) -> str:
        """Generate a summary of challenges for analysis."""
        try:
            if not challenges:
                return "No challenges generated in this session."
            
            challenge_count = len(challenges)
            challenge_types = {}
            difficulty_levels = {}
            
            for challenge in challenges:
                c_type = challenge.get("challenge_type", "unknown")
                difficulty = challenge.get("difficulty_level", "medium")
                
                challenge_types[c_type] = challenge_types.get(c_type, 0) + 1
                difficulty_levels[difficulty] = difficulty_levels.get(difficulty, 0) + 1
            
            most_common_type = max(challenge_types.items(), key=lambda x: x[1]) if challenge_types else ("none", 0)
            most_common_difficulty = max(difficulty_levels.items(), key=lambda x: x[1]) if difficulty_levels else ("medium", 0)
            
            summary = f"""
            🎯 CHALLENGE GENERATION SUMMARY
            
            Total Challenges: {challenge_count}
            Most Common Type: {most_common_type[0]} ({most_common_type[1]} times)
            Most Common Difficulty: {most_common_difficulty[0]} ({most_common_difficulty[1]} times)
            
            Challenge Types:
            """
            
            for c_type, count in sorted(challenge_types.items()):
                summary += f"• {c_type.replace('_', ' ').title()}: {count}\n"
            
            summary += "\nDifficulty Distribution:\n"
            for difficulty, count in sorted(difficulty_levels.items()):
                summary += f"• {difficulty.title()}: {count}\n"
            
            return summary.strip()
            
        except Exception as e:
            self.telemetry.log_error("generate_challenge_summary", str(e))
            return "Challenge summary unavailable." 