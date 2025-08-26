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
            # CRITICAL FIX: Check for specific gamification triggers first to get correct game types
            if state:
                user_message = self._get_latest_user_message(state).lower().strip()

                # Map specific trigger patterns to strategies for correct game types
                # PRIORITY 1: Perspective shift triggers (most specific first)
                if any(pattern in user_message for pattern in [
                    'i wonder what would happen', 'wonder what would happen', 'what if i', 'what would happen if',
                    'alternative', 'different angle', 'other way', 'different approach'
                ]):
                    print(f"🎮 STRATEGY: Alternative trigger detected → stimulate_curiosity → alternative_challenge → perspective_shift")
                    return "stimulate_curiosity"  # → alternative_challenge → perspective_shift

                # PRIORITY 2: Detective/mystery triggers (ENHANCED with test cases)
                elif any(pattern in user_message for pattern in [
                    'users seem to avoid', 'people avoid', 'users don\'t use', 'people don\'t use',
                    'feels uncomfortable but', 'feels unwelcoming but', 'don\'t know why',
                    'can\'t identify', 'can\'t pinpoint', 'bottlenecks but', 'investigate', 'analyze why',
                    # ADDED: Test case patterns
                    'why isn\'t this', 'what\'s wrong with', 'need to investigate', 'something feels off'
                ]):
                    print(f"🎮 STRATEGY: Detective trigger detected → challenge_assumptions → metacognitive_challenge → detective")
                    return "challenge_assumptions"  # → metacognitive_challenge → detective

                # PRIORITY 3: Constraint triggers (enhanced patterns)
                elif any(pattern in user_message for pattern in [
                    'stuck', 'completely stuck', 'totally stuck', 'really stuck',
                    'need fresh ideas', 'need creative ideas', 'need new ideas', 'fresh ideas',
                    'constraint', 'limited', 'having trouble', 'struggling with'
                ]):
                    print(f"🎮 STRATEGY: Constraint trigger detected → increase_challenge → constraint_challenge → constraint")
                    return "increase_challenge"  # → constraint_challenge → constraint

                # PRIORITY 4: Transformation triggers - FIXED: More flexible patterns for real transformation requests
                elif any(pattern in user_message for pattern in [
                    'converting', 'transforming', 'transform the', 'convert this', 'adaptive reuse',
                    'warehouse into', 'warehouse to', 'building into',
                    'industrial scale', 'human scale', 'challenge is how to transform',
                    'how to make it feel', 'make it more human', 'more welcoming'
                ]):
                    # ISSUE 1 FIX: Check for recent transformation challenges before triggering
                    messages = getattr(state, 'messages', [])
                    recent_assistant_messages = [msg['content'].lower() for msg in messages[-4:] if msg.get('role') == 'assistant']
                    recent_transformation = any('transformation challenge' in msg or 'transformation game' in msg or 'space_transformation' in msg
                                              for msg in recent_assistant_messages)

                    if recent_transformation:
                        print(f"🎮 STRATEGY SKIP: Transformation recently used - falling back to general challenge")
                        return "general_challenge"  # Fall back to general challenge instead

                    print(f"🎮 STRATEGY: Transformation trigger detected → transformation_design → space_transformation → transformation")
                    return "transformation_design"  # → space_transformation → transformation

                # PRIORITY 5: Storytelling triggers
                elif any(pattern in user_message for pattern in [
                    'user journey', 'user experience', 'journey through', 'story of',
                    'narrative', 'sequence of spaces', 'progression through', 'flow of movement',
                    'experience as they move', 'path through', 'spatial story'
                ]):
                    print(f"🎮 STRATEGY: Storytelling trigger detected → spatial_storytelling → spatial_storytelling → storytelling")
                    return "spatial_storytelling"  # → spatial_storytelling → storytelling

                # PRIORITY 6: Time travel triggers
                elif any(pattern in user_message for pattern in [
                    'over time', 'through time', 'years from now', 'in the future',
                    'decades', 'generations', 'evolve', 'evolution', 'lifecycle',
                    'aging', 'changing needs', 'future use', 'long-term'
                ]):
                    print(f"🎮 STRATEGY: Time travel trigger detected → temporal_exploration → time_travel_challenge → time_travel")
                    return "temporal_exploration"  # → time_travel_challenge → time_travel

                # PRIORITY 7: Role-play triggers (more specific patterns)
                elif any(pattern in user_message for pattern in [
                    'how would a', 'what would a', 'how would an', 'what would an',
                    'how would someone', 'what would someone', 'how would they feel', 'what would they think',
                    'visitor feel', 'user feel', 'person experience', 'elderly person', 'child feel'
                ]):
                    print(f"🎮 STRATEGY: Role-play trigger detected → increase_engagement → perspective_challenge → role_play")
                    return "increase_engagement"  # → perspective_challenge → role_play

            # FIXED: Add missing strategy detection based on trigger patterns
            if state:
                user_message = self._get_latest_user_message(state).lower().strip()

                # Check for storytelling patterns
                storytelling_patterns = ['tell me a story', 'story about', 'narrative', 'imagine a story']
                if any(pattern in user_message for pattern in storytelling_patterns):
                    return "spatial_storytelling"

                # Check for time travel patterns
                time_travel_patterns = ['time travel', 'different era', 'future', 'past', 'over time', 'through time']
                if any(pattern in user_message for pattern in time_travel_patterns):
                    return "temporal_exploration"

                # Check for SPECIFIC transformation patterns (FIXED: More flexible for real transformation requests)
                transformation_patterns = [
                    'converting', 'transforming', 'transform the', 'convert this', 'adaptive reuse',
                    'warehouse into', 'warehouse to', 'building into', 'building to',
                    'industrial scale', 'human scale', 'challenge is how to transform',
                    'how to make it feel', 'make it more human', 'more welcoming'
                ]
                if any(pattern in user_message.lower() for pattern in transformation_patterns):
                    return "transformation_design"

                # Check for creative constraint patterns
                constraint_patterns = ['stuck', 'struggling', 'need inspiration', 'creative', 'ideas']
                if any(pattern in user_message for pattern in constraint_patterns):
                    return "creative_constraint_challenge"

            # Fallback to cognitive state-based selection
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
                "balanced_development": ("perspective_challenge", "temporal_perspective"),
                # FIXED: Add missing creative constraint mapping
                "creative_constraint_challenge": ("constraint_challenge", "structural"),
                # NEW: Additional game types
                "spatial_storytelling": ("spatial_storytelling", "narrative"),
                "temporal_exploration": ("time_travel_challenge", "temporal"),
                "transformation_design": ("space_transformation", "adaptive")
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
            # NEW: Additional game types
            elif challenge_type == "spatial_storytelling":
                challenge_result = await self._generate_storytelling_challenge(cognitive_state, state, analysis_result, subtype)
            elif challenge_type == "time_travel_challenge":
                challenge_result = await self._generate_time_travel_challenge(cognitive_state, state, analysis_result, subtype)
            elif challenge_type == "space_transformation":
                challenge_result = await self._generate_transformation_challenge(cognitive_state, state, analysis_result, subtype)
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
            # Check if gamification should be applied
            should_gamify = self._should_apply_gamification(state, constraint_type, "constraint_challenge")

            if should_gamify:
                # Extract context-aware information
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))
                context_data = self._extract_challenge_context(user_message, building_type, "constraint")

                # FIXED: Generate proper constraint challenge instead of echoing user input
                if "structural" in user_message.lower() or constraint_type == "structural":
                    challenge_text = f"Given the tight site constraints of your {building_type} project, explore how different structural systems (e.g., steel frame, timber, or concrete) impact the interior space organization. Consider how each system might influence spatial flexibility, ceiling heights, and natural light penetration. Create a layout for each scenario, focusing on how structural elements like columns or load-bearing walls affect the flow and usability of spaces. How do these structural choices align with your design goals for community interaction and accessibility within the limited site footprint?"
                elif "spatial" in user_message.lower() or constraint_type == "spatial":
                    challenge_text = f"Your {building_type} has a challenging irregular site boundary. Design three different spatial configurations that maximize usable area while maintaining code compliance. Consider how circulation, natural lighting, and programmatic adjacencies change with each approach. Which configuration best supports the intended community activities while addressing the site constraints?"
                else:
                    challenge_text = f"Working within budget and zoning constraints for your {building_type}, explore how material choices impact both design expression and functional performance. Compare three different material strategies and their implications for maintenance, sustainability, and user experience."

                return {
                    "challenge_text": challenge_text,
                    "challenge_type": "constraint_challenge",
                    "constraint_type": constraint_type,
                    "building_type": building_type,
                    "specific_constraint": context_data.get("specific_constraint", "design challenge"),
                    "context_keywords": context_data.get("keywords", []),
                    "challenge_focus": context_data.get("focus_area", "spatial design"),
                    "specific_elements": context_data.get("specific_elements", []),
                    "pedagogical_intent": f"Overcome {context_data.get('specific_constraint', 'design constraints')} through creative problem-solving",
                    "cognitive_target": "constraint_resolution",
                    "expected_outcome": f"Enhanced problem-solving for {context_data.get('focus_area', 'design challenges')}",
                    "gamification_applied": True
                }
            else:
                # Use traditional challenge generation
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
                    "expected_outcome": "Increased design flexibility and creative problem-solving",
                    "gamification_applied": False
                }

        except Exception as e:
            self.telemetry.log_error("_generate_constraint_challenge", str(e))
            return {
                "challenge_text": "Consider how your design would adapt to different constraints.",
                "challenge_type": "constraint_challenge",
                "constraint_type": constraint_type,
                "pedagogical_intent": "Encourage adaptive thinking",
                "cognitive_target": "flexibility",
                "gamification_applied": False
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
                # Pass the original user message for flexible content generation
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))

                # ISSUE 5 FIX: Generate proper response instead of echoing user message
                response_text = await self._generate_contextual_perspective_response(user_message, building_type, perspective_type)

                return {
                    "challenge_text": response_text,  # Proper generated response
                    "challenge_type": "perspective_challenge",
                    "perspective_type": perspective_type,
                    "building_type": building_type,
                    "pedagogical_intent": "Expand perspective and empathy in design thinking",
                    "cognitive_target": "perspective_taking",
                    "expected_outcome": "Enhanced empathy and user-centered design thinking",
                    "gamification_applied": True,
                    "user_message": user_message  # Keep original message for gamification UI
                }
            else:
                return {
                    "challenge_text": contextualized_challenge,
                    "challenge_type": "perspective_challenge",
                    "perspective_type": perspective_type,
                    "pedagogical_intent": "Expand perspective and empathy in design thinking",
                    "cognitive_target": "perspective_taking",
                    "expected_outcome": "Enhanced empathy and user-centered design thinking",
                    "gamification_applied": False
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

    # Removed old hardcoded gamification method - now using flexible content generation system

    def _get_latest_user_message(self, state: ArchMentorState) -> str:
        """Get the latest user message from conversation history."""
        try:
            messages = getattr(state, 'messages', [])
            user_messages = [msg for msg in messages if msg.get('role') == 'user']
            if user_messages:
                return user_messages[-1].get('content', '').strip()
            return "How would different users experience this space?"
        except Exception:
            return "How would different users experience this space?"

    def _should_apply_gamification(self, state: ArchMentorState, challenge_type: str, context: str) -> bool:
        """
        Smart gamification trigger with frequency control (1 game every 4 messages).

        Gamification should ONLY be applied for specific trigger patterns:
        - Role-play questions (How would a visitor feel...)
        - Perspective questions (What would an elderly person think...)
        - Curiosity amplification (I wonder what would happen...)
        - Creative constraints (I'm stuck on...)
        - Reality checks (This seems pretty easy...)
        - Low engagement (Ok, Yes, Sure...)
        - Overconfidence (I already know exactly what to do...)
        - Cognitive offloading (Just tell me what to do...)

        FREQUENCY CONTROL: Only trigger every 4 messages (20% rate)
        """
        try:
            # Get conversation history
            messages = getattr(state, 'messages', [])
            user_messages = [msg for msg in messages if msg.get('role') == 'user']

            if len(user_messages) == 0:
                return False

            latest_message = user_messages[-1].get('content', '').lower().strip()

            # Check for strong triggers that should override frequency control
            strong_trigger_patterns = [
                'i\'m stuck on', 'stuck on', 'completely stuck', 'really stuck', 'totally stuck',
                # FIXED: Add inspiration patterns to strong triggers
                'need inspiration', 'inspiration for', 'inspire me', 'creative ideas', 'need ideas',
                # REVERTED: Remove overly broad transformation triggers that fire on knowledge requests
                'warehouse to community center', 'converting warehouse', 'transforming warehouse',
                'user journey', 'journey through', 'story of', 'narrative',
                'over time', 'through time', 'evolve', 'evolution', 'future',
                # ADDED: Role-play and perspective patterns should be strong triggers (high engagement)
                'how would a visitor feel', 'how would a user feel', 'young visitor feel',
                'elderly person feel', 'child feel', 'teenager feel', 'adult feel',
                'from a user\'s perspective', 'from a visitor\'s perspective',
                'different perspective', 'another perspective', 'alternative viewpoint'
            ]

            has_strong_trigger = any(pattern in latest_message for pattern in strong_trigger_patterns)

            # FIXED: FREQUENCY CONTROL: Check last 2-3 messages for games, not modulo
            total_user_messages = len(user_messages)

            # Check if gamification was used in recent messages (look at last 2-3 assistant messages)
            recent_assistant_messages = [msg['content'].lower() for msg in messages[-6:] if msg.get('role') == 'assistant']

            # Look for COMPREHENSIVE gamification indicators in recent assistant messages
            gamification_indicators = [
                # Specific game challenges
                'perspective wheel', 'role-play challenge', 'detective mystery', 'constraint puzzle',
                'storytelling challenge', 'time travel challenge', 'transformation game',
                'enhanced gamification', 'gamified challenge', 'interactive game',
                'spin the wheel', 'persona game', 'mystery investigation',
                # Common game emojis and markers
                '🎭', '🎮', '⏰', '🔍', '🌟', '🎯', '🎪', '🎨',
                # Game type keywords that appear in responses
                'challenge:', 'game:', 'perspective shift', 'role-play:', 'time travel:',
                'transformation:', 'detective:', 'constraint:', 'storytelling:',
                # Interactive elements
                'choose your', 'select an option', 'pick a', 'which would you'
            ]

            recent_gamification = any(
                any(indicator in msg for indicator in gamification_indicators)
                for msg in recent_assistant_messages[-3:]  # Check last 3 assistant messages (increased from 2)
            )

            # Allow gamification if no recent games OR if strong trigger overrides
            if recent_gamification and not has_strong_trigger:
                print(f"🎮 FREQUENCY CONTROL: Skipping gamification - recent game detected in last 2 messages")
                return False
            elif has_strong_trigger:
                print(f"🎮 FREQUENCY OVERRIDE: Strong trigger detected, overriding frequency control")
            else:
                print(f"🎮 FREQUENCY CONTROL: Allowing gamification - no recent games detected")

            # ENHANCED GAME VARIETY SYSTEM: Prevent consecutive identical game types
            recent_assistant_messages = [msg['content'].lower() for msg in messages[-6:] if msg.get('role') == 'assistant']

            # COMPREHENSIVE GAME TYPE TRACKING - Map all game types to their indicators (FIXED)
            game_type_indicators = {
                'transformation': ['transformation challenge', 'transformation game', 'converting this', 'shape-shift', 'adaptive reuse', '🔄'],
                'role_play': ['role-play', 'perspective of', 'imagine you are', 'step into', 'as a visitor', 'as a user', '🎭'],
                'detective': ['detective', 'investigate', 'mystery', 'clues', 'investigation', 'solve the mystery', '🔍'],
                'constraint': ['constraint', 'limitation', 'creative challenge', 'design challenge', 'puzzle', '🧩'],
                'storytelling': ['storytelling', 'story', 'narrative', 'journey through', 'user journey', '📖'],
                'time_travel': ['time travel', 'fast-forward', 'over time', 'future', 'past', 'temporal', '⏰'],
                'perspective_shift': ['perspective wheel', 'reality check', 'different angle', 'alternative view', '👁️']
            }

            # Track which game types were used recently
            recent_game_types = set()
            for game_type, indicators in game_type_indicators.items():
                if any(any(indicator in msg for indicator in indicators) for msg in recent_assistant_messages):
                    recent_game_types.add(game_type)

            print(f"🎮 GAME VARIETY: Recently used game types: {recent_game_types}")

            # LEGACY COMPATIBILITY: Keep individual flags for existing logic
            recent_transformation = 'transformation' in recent_game_types
            recent_role_play = 'role_play' in recent_game_types
            recent_detective = 'detective' in recent_game_types
            recent_constraint = 'constraint' in recent_game_types
            recent_storytelling = 'storytelling' in recent_game_types
            recent_time_travel = 'time_travel' in recent_game_types
            recent_perspective_shift = 'perspective_shift' in recent_game_types

            # GAME VARIETY HELPER FUNCTION
            def should_skip_game_type(game_type: str, recent_types: set) -> bool:
                """Check if a game type should be skipped due to recent usage"""
                if game_type in recent_types:
                    print(f"🎮 GAME VARIETY: Skipping {game_type} - used recently")
                    return True
                return False

            # 1. ROLE-PLAY TRIGGERS - FIXED: More specific patterns to avoid false positives
            role_play_patterns = [
                # Specific role-play questions about feelings/experiences
                'how would a visitor feel', 'how would a user feel', 'how would someone feel',
                'how would they feel', 'what would a visitor think', 'what would a user think',
                'how do users feel', 'what would an elderly person', 'what would a child',
                'how would an elderly', 'how would a child', 'how would an adult',
                # Specific feeling/experience patterns (more precise)
                'feel in this space', 'feel when they enter', 'feel in the space', 'experience in this',
                'member feel when', 'user feel when', 'visitor feel when', 'person feel when',
                # Perspective patterns (more specific to avoid "how should I approach")
                'from a user\'s perspective', 'from a visitor\'s perspective', 'as a user would',
                'teenager\'s perspective', 'child\'s perspective', 'user\'s perspective',
                'elderly person\'s perspective', 'visitor\'s perspective'
            ]
            if any(pattern in latest_message for pattern in role_play_patterns):
                # ENHANCED GAME VARIETY: Skip if role-play was used recently
                if should_skip_game_type('role_play', recent_game_types):
                    return False

                # ENHANCED RESPONSE DETECTION: Skip if user is responding to ANY recent challenge
                challenge_response_indicators = [
                    # Direct response indicators
                    '🎭 role-play response:', '🎭 roleplay', 'role-play response:',
                    'as this role:', 'from this perspective:', 'my response as',
                    # Perspective shift response patterns (from the user's actual response)
                    'warehouse building opens up', 'building opens up towards', 'merges with the surrounding',
                    'extension for market places', 'towards exterior and merges',
                    # General challenge response patterns
                    'responding to your challenge', 'my answer to the challenge', 'challenge response'
                ]

                # Also check if recent assistant messages contained challenges
                recent_assistant_messages = [msg['content'].lower() for msg in messages[-3:] if msg.get('role') == 'assistant']
                recent_challenges = any(
                    indicator in msg for msg in recent_assistant_messages
                    for indicator in ['🎭', '🎮', '⏰', '🔍', 'challenge:', 'game:', 'perspective shift']
                )

                if (any(indicator in latest_message.lower() for indicator in challenge_response_indicators) or
                    recent_challenges):
                    print(f"🎮 GAMIFICATION SKIP: User is responding to recent challenge - no new challenge needed")
                    return False

                print(f"🎮 GAMIFICATION TRIGGER: Role-play question detected - '{latest_message}'")
                return True

            # 2. CURIOSITY AMPLIFICATION - FIXED: Removed 'what if' to let perspective patterns handle spatial design
            curiosity_patterns = ['i wonder what would happen', 'i wonder']
            if any(pattern in latest_message for pattern in curiosity_patterns):
                # ISSUE 3 FIX: Keep important trigger but reduce verbosity
                print(f"🎮 GAMIFICATION TRIGGER: Curiosity amplification detected")
                return True

            # 2.5. PERSPECTIVE SHIFT REQUESTS - ENHANCED with spatial flow patterns
            perspective_shift_patterns = [
                # Original patterns
                'help me see this from a different angle', 'different angle', 'see this differently',
                'think about this differently', 'different perspective', 'another way to think',
                'alternative viewpoint', 'fresh perspective',
                # NEW: Simpler patterns
                'different angle', 'differently', 'another way', 'alternative',
                'fresh perspective', 'new perspective', 'see this', 'think about this',
                # ADDED: Spatial flow and "what if" patterns that should trigger perspective challenges
                'what if i place', 'what if i move', 'what if i put', 'what if we place',
                'would that create', 'would this create', 'engaging flow', 'flow for people',
                'people moving through', 'flow through', 'circulation through', 'movement through'
            ]
            if any(pattern in latest_message for pattern in perspective_shift_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Perspective shift request detected - '{latest_message}'")
                return True

            # 3. CREATIVE CONSTRAINTS - Only for actual stuck/blocked situations
            # FIXED: Removed "not sure how" - this is often part of thoughtful design questions
            constraint_patterns = [
                # Actual stuck/blocked patterns
                'i\'m stuck on', 'stuck on', 'having trouble', 'i\'m stuck',
                'completely stuck', 'really stuck', 'totally stuck',
                # Fresh ideas patterns (when explicitly asking for ideas)
                'i need fresh ideas', 'need fresh ideas', 'fresh ideas', 'new ideas',
                'creative ideas', 'need ideas', 'ideas for', 'inspire me', 'inspiration',
                'help me think', 'new approach', 'different approach'
            ]

            # 4. TRANSFORMATION TRIGGERS - FIXED: More flexible patterns for real transformation requests
            transformation_patterns = [
                # Conversion statements and questions (more flexible)
                'converting', 'convert this', 'convert the', 'conversion',
                'transforming', 'transform this', 'transform the', 'transformation',
                'adapting', 'adapt this', 'adapt the', 'adaptive reuse',
                'repurposing', 'repurpose this', 'repurpose the',
                # Building type conversions (common patterns)
                'warehouse into', 'warehouse to', 'building into', 'building to',
                'factory into', 'factory to', 'church into', 'church to',
                # Scale and character transformation (key architectural concepts)
                'transform the scale', 'transform the character', 'change the scale',
                'industrial scale', 'human scale', 'intimate scale',
                # Challenge-focused transformation language
                'challenge is how to transform', 'challenge of transforming',
                'how to make it feel', 'make it more human', 'more welcoming'
            ]

            # 5. STORYTELLING TRIGGERS - NEW
            storytelling_patterns = [
                'user journey', 'user experience', 'journey through', 'story of',
                'narrative', 'sequence of spaces', 'progression through', 'flow of movement',
                'experience as they move', 'path through', 'spatial story'
            ]

            # 6. TIME TRAVEL TRIGGERS - FIXED: More precise patterns to avoid false matches
            time_travel_patterns = [
                'over time', 'through time', 'years from now', 'in the future',
                'decades', 'generations', 'evolve over time', 'evolution of', 'lifecycle',
                'aging building', 'changing needs over', 'future use', 'long-term use',
                # ADDED: More specific temporal patterns
                'future community needs', 'adapt to future', 'evolve.*future',
                '10.*years', '20.*years', 'next decade', 'coming years',
                'digital.*future', 'technological.*future', 'future.*formats',
                # FIXED: More specific patterns to avoid false matches
                'building over time', 'space over time', 'community over time'
            ]

            # ADDITIONAL CHECK: Don't trigger for thoughtful design questions or example requests
            thoughtful_design_indicators = [
                'how should i approach', 'how should i', 'what would be the best way',
                'considering', 'thinking about', 'exploring', 'approach this'
            ]

            # ISSUE 2 FIX: Enhanced filtering for information/example requests
            example_request_indicators = [
                'give example', 'show example', 'example project', 'project example',
                'can you give', 'can you show', 'can you provide', 'provide example',
                'examples of', 'example of', 'show me examples', 'give me examples',
                # ISSUE 2 FIX: Add more patterns that should NOT trigger gamification
                'provide some examples', 'can you provide examples', 'examples about',
                'how to change a courtyard', 'how to approach', 'not sure about how to approach'
            ]

            is_thoughtful_question = any(indicator in latest_message for indicator in thoughtful_design_indicators)
            is_example_request = any(indicator in latest_message for indicator in example_request_indicators)

            # ENHANCED: Skip gamification for example requests and knowledge requests (ISSUE 1 FIX)
            if is_example_request:
                print(f"🎮 GAMIFICATION SKIP: Example request detected - no gamification needed")
                return False

            # ISSUE 2 FIX: Enhanced filtering for knowledge and design process requests
            knowledge_request_indicators = [
                'what is', 'what are', 'how does', 'tell me about', 'explain',
                'definition of', 'meaning of', 'principles of', 'information about'
            ]

            # ISSUE 2 FIX: Add design process question filtering
            design_process_indicators = [
                'how do i design', 'how to design', 'design that narrative flow',
                'create a user journey', 'design process', 'approach to',
                'methodology for', 'strategy for', 'process for'
            ]

            is_knowledge_request = any(indicator in latest_message for indicator in knowledge_request_indicators)
            is_design_process_question = any(indicator in latest_message for indicator in design_process_indicators)

            if is_knowledge_request:
                print(f"🎮 GAMIFICATION SKIP: Knowledge request detected - no gamification needed")
                return False

            if is_design_process_question:
                print(f"🎮 GAMIFICATION SKIP: Design process question detected - no gamification needed")
                return False

            if any(pattern in latest_message for pattern in constraint_patterns) and not is_thoughtful_question:
                # ENHANCED GAME VARIETY: Skip if constraint challenge was used recently
                if should_skip_game_type('constraint', recent_game_types):
                    return False
                print(f"🎮 GAMIFICATION TRIGGER: Creative constraint detected - '{latest_message}'")
                return True

            # FIXED: Check time travel patterns FIRST (higher priority than transformation)
            if any(pattern in latest_message for pattern in time_travel_patterns):
                # ENHANCED GAME VARIETY: Skip if time travel was used recently
                if should_skip_game_type('time_travel', recent_game_types):
                    return False

                # ISSUE 2 FIX: Skip if user is responding to a time travel challenge
                timetravel_response_indicators = [
                    '⏰ time travel response:', '⏰ temporal', 'time travel response:',
                    'in the future:', 'in the past:', 'temporal response:'
                ]
                if any(indicator in latest_message.lower() for indicator in timetravel_response_indicators):
                    print(f"🎮 GAMIFICATION SKIP: User is responding to time travel challenge - no new challenge needed")
                    return False

                print(f"🎮 GAMIFICATION TRIGGER: Time travel challenge detected - '{latest_message}'")
                return True

            # Check storytelling patterns
            if any(pattern in latest_message for pattern in storytelling_patterns):
                # ENHANCED GAME VARIETY: Skip if storytelling was used recently
                if should_skip_game_type('storytelling', recent_game_types):
                    return False

                # ISSUE 2 FIX: Skip if user is responding to a storytelling challenge
                storytelling_response_indicators = [
                    '📚 story response:', '📚 storytelling', 'story response:',
                    'my story:', 'the story goes:', 'narrative response:'
                ]
                if any(indicator in latest_message.lower() for indicator in storytelling_response_indicators):
                    print(f"🎮 GAMIFICATION SKIP: User is responding to storytelling challenge - no new challenge needed")
                    return False

                print(f"🎮 GAMIFICATION TRIGGER: Storytelling challenge detected - '{latest_message}'")
                return True

            # Check transformation patterns (lower priority than time travel)
            if any(pattern in latest_message for pattern in transformation_patterns):
                # ENHANCED GAME VARIETY: Skip if transformation was used recently
                if should_skip_game_type('transformation', recent_game_types):
                    return False

                # ADDITIONAL COOLDOWN: Check for transformation keywords in recent user messages to prevent over-triggering
                recent_user_messages = [msg['content'].lower() for msg in messages[-6:] if msg.get('role') == 'user']
                transformation_keyword_count = sum(
                    1 for msg in recent_user_messages
                    for pattern in ['transform', 'convert', 'adapt', 'reuse', 'repurpose']
                    if pattern in msg
                )

                if transformation_keyword_count >= 3:  # If user mentioned transformation concepts 3+ times recently
                    print(f"🎮 GAMIFICATION SKIP: Too many transformation keywords recently ({transformation_keyword_count}) - preventing over-triggering")
                    return False

                print(f"🎮 GAMIFICATION TRIGGER: Transformation challenge detected - '{latest_message}'")
                return True

            # ADDED: Check detective/mystery patterns
            detective_patterns = [
                'why isn\'t this', 'what\'s wrong with', 'need to investigate', 'something feels off',
                'users seem to avoid', 'people avoid', 'don\'t know why', 'can\'t identify',
                'bottlenecks but', 'investigate', 'analyze why'
            ]
            if any(pattern in latest_message for pattern in detective_patterns):
                # ISSUE 1 FIX: Skip if we recently used detective challenge
                if recent_detective:
                    print(f"🎮 GAMIFICATION SKIP: Detective challenge recently used - avoiding repetition")
                    return False

                # ISSUE 2 FIX: Skip if user is responding to a detective challenge
                detective_response_indicators = [
                    '🔍 detective response:', '🔍 investigation', 'detective response:',
                    'my investigation shows:', 'investigation findings:', 'mystery solved:'
                ]
                if any(indicator in latest_message.lower() for indicator in detective_response_indicators):
                    print(f"🎮 GAMIFICATION SKIP: User is responding to detective challenge - no new challenge needed")
                    return False

                print(f"🎮 GAMIFICATION TRIGGER: Detective/mystery challenge detected - '{latest_message}'")
                return True

            # 4. REALITY CHECK / OVERCONFIDENCE - ENHANCED patterns
            overconfidence_patterns = [
                'this seems pretty easy', 'this is easy', 'i already know exactly',
                'i already know', 'that\'s obvious', 'simple', 'basic',
                # ADDED: Enhanced patterns for dismissive overconfidence
                'my approach is great', 'nothing need to be done', 'nothing needs to be done',
                'nothing to improve', 'no need to improve', 'don\'t need to improve',
                'already perfect', 'already good enough', 'good enough as is',
                'no changes needed', 'no improvements needed', 'fine as it is'
            ]
            if any(pattern in latest_message for pattern in overconfidence_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Overconfidence/reality check detected")
                return True

            # 5. LOW ENGAGEMENT (lines 27-31)
            low_engagement_responses = ['ok', 'yes', 'sure', 'fine', 'alright', 'cool', 'maybe']
            if latest_message in low_engagement_responses:
                # ISSUE 3 FIX: Commented out less critical trigger print
                # print(f"🎮 GAMIFICATION TRIGGER: Low engagement detected")
                return True

            # 6. COGNITIVE OFFLOADING (lines 223-233)
            offloading_patterns = [
                'just tell me what to do', 'can you design this', 'tell me what to do',
                'what should i do', 'give me the answer', 'what\'s the standard solution'
            ]
            if any(pattern in latest_message for pattern in offloading_patterns):
                print(f"🎮 GAMIFICATION TRIGGER: Cognitive offloading detected")
                return True

            # ADDITIONAL CHECK: Skip gamification for design exploration questions
            design_exploration_indicators = [
                'i am thinking about', 'i\'m thinking about', 'thinking about',
                'considering', 'exploring', 'approach this', 'how should i',
                'what would be the best', 'how might i', 'spatial organization',
                'design approach', 'design strategy', 'user flow', 'circulation',
                'organize spaces', 'layout', 'planning'
            ]

            if any(indicator in latest_message for indicator in design_exploration_indicators):
                print(f"🎮 GAMIFICATION SKIP: Design exploration question - should get direct guidance")
                return False

            # Default: no gamification for normal design statements, technical questions, etc.
            # ISSUE 3 FIX: Commented out verbose skip message
            # print(f"🎮 GAMIFICATION SKIP: Normal design statement/question (no trigger patterns)")
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
            # Check if gamification should be applied
            should_gamify = self._should_apply_gamification(state, alternative_type, "alternative_challenge")

            if should_gamify:
                # Pass original user message for flexible content generation
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))

                return {
                    "challenge_text": user_message,
                    "challenge_type": "alternative_challenge",
                    "alternative_type": alternative_type,
                    "building_type": building_type,
                    "pedagogical_intent": "Encourage exploration of design alternatives",
                    "cognitive_target": "divergent_thinking",
                    "expected_outcome": "Increased creative exploration and solution diversity",
                    "gamification_applied": True
                }
            else:
                # Use traditional challenge generation
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
                    "expected_outcome": "Increased creative exploration and solution diversity",
                    "gamification_applied": False
                }

        except Exception as e:
            self.telemetry.log_error("_generate_alternative_challenge", str(e))
            return {
                "challenge_text": "Explore alternative approaches to your current design solution.",
                "challenge_type": "alternative_challenge",
                "alternative_type": alternative_type,
                "pedagogical_intent": "Encourage creative exploration",
                "cognitive_target": "creativity",
                "gamification_applied": False
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
                # Pass original user message for flexible content generation
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))

                return {
                    "challenge_text": user_message,
                    "challenge_type": "metacognitive_challenge",
                    "metacognitive_type": metacognitive_type,
                    "building_type": building_type,
                    "pedagogical_intent": "Foster metacognitive awareness and self-evaluation with focus on increasing engagement",
                    "cognitive_target": "metacognition",
                    "expected_outcome": "Enhanced self-awareness and reflective practice",
                    "gamification_applied": True
                }
            else:
                return {
                    "challenge_text": contextualized_challenge,
                    "challenge_type": "metacognitive_challenge",
                    "metacognitive_type": metacognitive_type,
                    "pedagogical_intent": "Foster metacognitive awareness and self-evaluation",
                    "cognitive_target": "metacognition",
                    "expected_outcome": "Enhanced self-awareness and reflective practice",
                    "gamification_applied": False
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

    async def _generate_contextual_perspective_response(self, user_message: str, building_type: str, perspective_type: str) -> str:
        """ISSUE 5 FIX: Generate proper response for perspective challenges instead of echoing user message."""
        try:
            # Generate a thoughtful response that addresses the user's question while introducing the gamification
            response_prompt = f"""
            The user asked: "{user_message}"

            Generate a brief, thoughtful response (2-3 sentences) that:
            1. Acknowledges their question about {building_type}
            2. Introduces the perspective-taking challenge naturally
            3. Connects to their specific context

            Keep it under 100 words and make it feel like a natural mentor response, not a game announcement.
            """

            response = await self.client.generate_completion([
                self.client.create_system_message("You are an architectural mentor who provides thoughtful, contextual responses."),
                self.client.create_user_message(response_prompt)
            ])

            if response and response.get("content"):
                return response["content"].strip()
            else:
                # Fallback response
                return f"That's a thoughtful question about {building_type} design. Let's explore this through different perspectives to deepen your understanding."

        except Exception as e:
            print(f"⚠️ Contextual perspective response generation failed: {e}")
            return f"That's an interesting question about {building_type}. Let's explore this from different viewpoints."

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

    async def _generate_storytelling_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, narrative_type: str = "narrative") -> Dict[str, Any]:
        """Generate spatial storytelling cognitive challenge."""
        self.telemetry.log_agent_start("_generate_storytelling_challenge")

        try:
            # Check if gamification should be applied
            should_gamify = self._should_apply_gamification(state, narrative_type, "spatial_storytelling")

            if should_gamify:
                # Extract context-aware information
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))
                context_data = self._extract_challenge_context(user_message, building_type, "storytelling")

                return {
                    "challenge_text": user_message,
                    "challenge_type": "spatial_storytelling",
                    "narrative_type": narrative_type,
                    "building_type": building_type,
                    "specific_constraint": context_data.get("specific_constraint", "narrative design"),
                    "context_keywords": context_data.get("keywords", []),
                    "challenge_focus": context_data.get("focus_area", "spatial narrative"),
                    "specific_elements": context_data.get("specific_elements", []),
                    "pedagogical_intent": f"Explore {context_data.get('specific_constraint', 'spatial narratives and user journeys')}",
                    "cognitive_target": "narrative_thinking",
                    "expected_outcome": f"Enhanced understanding of {context_data.get('focus_area', 'spatial storytelling and user experience')}",
                    "gamification_applied": True
                }
            else:
                return {
                    "challenge_text": "Consider the story your space tells through its design and user journey.",
                    "challenge_type": "spatial_storytelling",
                    "narrative_type": narrative_type,
                    "pedagogical_intent": "Encourage narrative design thinking",
                    "cognitive_target": "storytelling",
                    "gamification_applied": False
                }

        except Exception as e:
            self.telemetry.log_error("_generate_storytelling_challenge", str(e))
            return {
                "challenge_text": "How does your design tell a story through space?",
                "challenge_type": "spatial_storytelling",
                "narrative_type": narrative_type,
                "pedagogical_intent": "Encourage narrative thinking",
                "cognitive_target": "storytelling",
                "gamification_applied": False
            }

    async def _generate_time_travel_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, temporal_type: str = "temporal") -> Dict[str, Any]:
        """Generate time travel cognitive challenge."""
        self.telemetry.log_agent_start("_generate_time_travel_challenge")

        try:
            # Check if gamification should be applied
            should_gamify = self._should_apply_gamification(state, temporal_type, "time_travel_challenge")

            if should_gamify:
                # Extract context-aware information
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))
                context_data = self._extract_challenge_context(user_message, building_type, "time_travel")

                return {
                    "challenge_text": user_message,
                    "challenge_type": "time_travel_challenge",
                    "temporal_type": temporal_type,
                    "building_type": building_type,
                    "specific_constraint": context_data.get("specific_constraint", "temporal design"),
                    "context_keywords": context_data.get("keywords", []),
                    "challenge_focus": context_data.get("focus_area", "temporal design"),
                    "specific_elements": context_data.get("specific_elements", []),
                    "pedagogical_intent": f"Explore {context_data.get('specific_constraint', 'temporal aspects of design and space evolution')}",
                    "cognitive_target": "temporal_thinking",
                    "expected_outcome": f"Enhanced understanding of {context_data.get('focus_area', 'how spaces change over time')}",
                    "gamification_applied": True
                }
            else:
                return {
                    "challenge_text": "Consider how your space will evolve and be used across different time periods.",
                    "challenge_type": "time_travel_challenge",
                    "temporal_type": temporal_type,
                    "pedagogical_intent": "Encourage temporal design thinking",
                    "cognitive_target": "temporal_awareness",
                    "gamification_applied": False
                }

        except Exception as e:
            self.telemetry.log_error("_generate_time_travel_challenge", str(e))
            return {
                "challenge_text": "How will your design adapt and change over time?",
                "challenge_type": "time_travel_challenge",
                "temporal_type": temporal_type,
                "pedagogical_intent": "Encourage temporal thinking",
                "cognitive_target": "temporal_awareness",
                "gamification_applied": False
            }

    async def _generate_transformation_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, transformation_type: str = "adaptive") -> Dict[str, Any]:
        """Generate space transformation cognitive challenge."""
        self.telemetry.log_agent_start("_generate_transformation_challenge")

        try:
            # Check if gamification should be applied
            should_gamify = self._should_apply_gamification(state, transformation_type, "space_transformation")

            if should_gamify:
                # Extract context-aware information
                user_message = self._get_latest_user_message(state)
                building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))
                context_data = self._extract_challenge_context(user_message, building_type, "transformation")

                return {
                    "challenge_text": user_message,
                    "challenge_type": "space_transformation",
                    "transformation_type": transformation_type,
                    "building_type": building_type,
                    "specific_constraint": context_data.get("specific_constraint", "transformation challenge"),
                    "context_keywords": context_data.get("keywords", []),
                    "challenge_focus": context_data.get("focus_area", "adaptive design"),
                    "specific_elements": context_data.get("specific_elements", []),
                    "pedagogical_intent": f"Explore {context_data.get('specific_constraint', 'adaptive and transformative')} design strategies",
                    "cognitive_target": "transformation_thinking",
                    "expected_outcome": f"Enhanced understanding of {context_data.get('focus_area', 'adaptive and flexible design')}",
                    "gamification_applied": True
                }
            else:
                return {
                    "challenge_text": "Consider how your space can transform and adapt to different uses and needs.",
                    "challenge_type": "space_transformation",
                    "transformation_type": transformation_type,
                    "pedagogical_intent": "Encourage adaptive design thinking",
                    "cognitive_target": "flexibility",
                    "gamification_applied": False
                }

        except Exception as e:
            self.telemetry.log_error("_generate_transformation_challenge", str(e))
            return {
                "challenge_text": "How can your design transform to meet changing needs?",
                "challenge_type": "space_transformation",
                "transformation_type": transformation_type,
                "pedagogical_intent": "Encourage transformative thinking",
                "cognitive_target": "adaptability",
                "gamification_applied": False
            }

    def _extract_challenge_context(self, user_message: str, building_type: str, challenge_type: str) -> Dict[str, Any]:
        """Extract specific context from user message to make challenges highly relevant."""
        try:
            user_lower = user_message.lower()
            context = {
                "keywords": [],
                "specific_constraint": "design challenge",
                "focus_area": "spatial design",
                "user_intent": "general",
                "specific_elements": []
            }

            # Extract building-specific context
            if building_type:
                context["building_type"] = building_type

            # CONSTRAINT CHALLENGE CONTEXT
            if challenge_type == "constraint":
                # Circulation issues
                if any(word in user_lower for word in ["circulation", "flow", "movement", "path", "route"]):
                    context["specific_constraint"] = "circulation challenges"
                    context["focus_area"] = "movement and flow"
                    context["keywords"] = ["circulation", "flow", "pathways", "navigation"]

                # Space planning issues
                elif any(word in user_lower for word in ["layout", "space", "room", "area", "zone"]):
                    context["specific_constraint"] = "spatial organization challenges"
                    context["focus_area"] = "space planning"
                    context["keywords"] = ["layout", "zoning", "spatial organization"]

                # Structural constraints
                elif any(word in user_lower for word in ["structure", "beam", "column", "load", "support"]):
                    context["specific_constraint"] = "structural limitations"
                    context["focus_area"] = "structural design"
                    context["keywords"] = ["structure", "support", "load-bearing"]

                # Programming constraints
                elif any(word in user_lower for word in ["program", "function", "use", "activity", "flexible"]):
                    context["specific_constraint"] = "programming challenges"
                    context["focus_area"] = "functional programming"
                    context["keywords"] = ["programming", "functionality", "multi-use"]

            # TRANSFORMATION CHALLENGE CONTEXT
            elif challenge_type == "transformation":
                # Adaptive reuse
                if any(word in user_lower for word in ["convert", "warehouse", "factory", "office", "adaptive reuse"]):
                    context["specific_constraint"] = "adaptive reuse challenges"
                    context["focus_area"] = "building conversion"
                    context["keywords"] = ["conversion", "adaptive reuse", "transformation"]

                    # Specific conversion types
                    if "warehouse" in user_lower:
                        context["specific_elements"] = ["high ceilings", "open spaces", "industrial character"]
                    elif "office" in user_lower:
                        context["specific_elements"] = ["cellular spaces", "HVAC systems", "partition walls"]

            # STORYTELLING CHALLENGE CONTEXT
            elif challenge_type == "storytelling":
                if any(word in user_lower for word in ["journey", "experience", "narrative", "story"]):
                    context["specific_constraint"] = "user experience design"
                    context["focus_area"] = "spatial narrative"
                    context["keywords"] = ["user journey", "experience", "narrative flow"]

            # TIME TRAVEL CHALLENGE CONTEXT
            elif challenge_type == "time_travel":
                if any(word in user_lower for word in ["evolve", "future", "time", "generations", "lifecycle"]):
                    context["specific_constraint"] = "temporal design considerations"
                    context["focus_area"] = "long-term adaptability"
                    context["keywords"] = ["evolution", "future needs", "adaptability"]

            return context

        except Exception as e:
            return {
                "keywords": [],
                "specific_constraint": "design challenge",
                "focus_area": "spatial design",
                "user_intent": "general",
                "specific_elements": []
            }

    async def _generate_storytelling_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, subtype: str) -> Dict:
        """Generate spatial storytelling challenge using AI for flexible content generation"""
        user_message = self._get_latest_user_message(state)
        building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))

        # FLEXIBLE AI-POWERED: Generate contextual story prompt for ANY topic
        story_prompt = await self._generate_ai_contextual_story_prompt(user_message, building_type)

        return {
            "challenge_text": story_prompt,
            "challenge_type": "spatial_storytelling",
            "story_type": subtype,
            "building_type": building_type,
            "narrative_focus": "building_perspective",
            "gamification_applied": True
        }

    async def _generate_time_travel_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, subtype: str) -> Dict:
        """Generate time travel challenge using AI for flexible content generation"""
        user_message = self._get_latest_user_message(state)
        building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))

        # FLEXIBLE AI-POWERED: Generate contextual time travel prompt for ANY topic
        time_prompt = await self._generate_ai_contextual_time_travel_prompt(user_message, building_type)

        return {
            "challenge_text": time_prompt,
            "challenge_type": "time_travel_challenge",
            "temporal_type": subtype,
            "building_type": building_type,
            "time_periods": ["1950", "2024", "2050"],
            "gamification_applied": True
        }

    async def _generate_transformation_challenge(self, cognitive_state: Dict, state: ArchMentorState, analysis_result: Dict, subtype: str) -> Dict:
        """Generate space transformation challenge using AI for flexible content generation"""
        user_message = self._get_latest_user_message(state)
        building_type = self._extract_building_type(getattr(state, 'current_design_brief', 'architectural project'))

        # FLEXIBLE AI-POWERED: Generate contextual transformation prompt for ANY topic
        transform_prompt = await self._generate_ai_contextual_transformation_prompt(user_message, building_type)

        return {
            "challenge_text": transform_prompt,
            "challenge_type": "space_transformation",
            "transformation_type": subtype,
            "building_type": building_type,
            "adaptation_scenarios": ["daily", "seasonal", "programmatic"],
            "gamification_applied": True
        }

    async def _generate_ai_contextual_story_prompt(self, user_message: str, building_type: str) -> str:
        """Generate flexible story prompt using AI for any architectural topic"""
        try:
            import openai
            client = openai.OpenAI()

            # Escape quotes in user message to prevent string formatting issues
            safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
            safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

            # Extract the main architectural topic from user message
            topic_extraction_prompt = f"""
            Extract the main architectural topic/concept from this user message: "{safe_user_message}"

            Examples:
            - "circulation strategies" → "circulation"
            - "lighting design" → "lighting"
            - "sustainable materials" → "sustainability"
            - "acoustic performance" → "acoustics"
            - "accessibility features" → "accessibility"
            - "landscape integration" → "landscape"
            - "structural systems" → "structure"

            Return only the main topic (1-2 words):
            """

            topic_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": topic_extraction_prompt}],
                max_tokens=50,
                temperature=0.3
            )

            main_topic = topic_response.choices[0].message.content.strip().lower()

            # Generate contextual story prompt
            story_generation_prompt = f"""
            Create a creative storytelling challenge for an architecture student working on a {safe_building_type} project.

            User's question/context: "{safe_user_message}"
            Main architectural topic: "{main_topic}"
            Building type: "{safe_building_type}"

            Generate a storytelling prompt that:
            1. Relates specifically to the topic "{main_topic}" in the context of a {safe_building_type}
            2. Uses narrative perspective (from building's POV, user's POV, or element's POV)
            3. Encourages creative thinking about how {main_topic} affects user experience
            4. Is engaging and imaginative, not generic
            5. Connects to real architectural design considerations

            Format: Write a 2-3 sentence storytelling prompt that starts with an engaging hook.

            Example format: "Tell the story of [perspective] in your {safe_building_type}. How does [topic-specific element] [specific action/impact]? What [specific questions about user experience/design impact]?"
            """

            story_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_generation_prompt}],
                max_tokens=200,
                temperature=0.7
            )

            return story_response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ AI story generation failed: {e}")
            # Fallback to generic prompt
            return f"Imagine your {building_type} as a character in a story. What would it say about the people who visit and the experiences it creates? Write a short narrative from the building's perspective, focusing on how your design decisions shape daily life and community interaction."

    async def _generate_ai_contextual_time_travel_prompt(self, user_message: str, building_type: str) -> str:
        """Generate flexible time travel prompt using AI for any architectural topic"""
        try:
            import openai
            client = openai.OpenAI()

            time_travel_prompt = f"""
            Create a time travel challenge for an architecture student working on a {building_type} project.

            User's question/context: "{user_message}"
            Building type: "{building_type}"

            Generate a time travel prompt that:
            1. Relates specifically to the user's question/topic
            2. Explores how the topic would differ across three time periods: 1950, 2024, 2050
            3. Considers technological, social, and cultural changes
            4. Encourages thinking about adaptation and evolution
            5. Is specific to the architectural topic, not generic

            Format: 2-3 sentences that guide the student through time periods with specific considerations.

            Example structure: "Travel through time with your {building_type}'s [specific topic]. In 1950, [period-specific consideration]. Today, [current consideration]. In 2050, [future consideration]."
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": time_travel_prompt}],
                max_tokens=200,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ AI time travel generation failed: {e}")
            return f"Travel through time with your {building_type} design. Imagine visiting it in 1950, today, and 2050. How would the same spaces be used differently in each era? What technologies, social patterns, and community needs would shape the experience?"

    async def _generate_ai_contextual_transformation_prompt(self, user_message: str, building_type: str) -> str:
        """Generate flexible transformation prompt using AI for any architectural topic"""
        try:
            import openai
            client = openai.OpenAI()

            # Escape quotes in user message to prevent string formatting issues
            safe_user_message = user_message.replace('"', '\\"').replace("'", "\\'")
            safe_building_type = building_type.replace('"', '\\"').replace("'", "\\'")

            transformation_prompt = f"""
            Create a transformation challenge for an architecture student working on a {safe_building_type} project.

            User's question/context: "{safe_user_message}"
            Building type: "{safe_building_type}"

            Generate a transformation prompt that:
            1. Relates specifically to the user's question/topic
            2. Explores how spaces can adapt and transform
            3. Considers different scenarios (daily, seasonal, programmatic, or functional changes)
            4. Encourages thinking about flexibility and adaptability
            5. Is specific to the architectural topic and building type

            Format: 2-3 sentences that challenge the student to think about transformation scenarios.

            Example structure: "Your {safe_building_type} needs to [specific transformation challenge]. [Specific scenarios]. What [specific design elements] would enable these transformations?"
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": transformation_prompt}],
                max_tokens=200,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ AI transformation generation failed: {e}")
            return f"Your {building_type} needs to transform throughout the day and seasons. Design a space that can adapt to different uses and user needs. What moveable elements, flexible systems, and adaptive features would enable these transformations while maintaining spatial quality?"