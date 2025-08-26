"""
Mode processors for different AI interaction modes.
"""

import streamlit as st
import asyncio
import sys
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import required components
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from processors.raw_gpt_processor import get_raw_gpt_response
from processors.no_ai_processor import get_no_ai_response
from processors.question_validator import validate_user_question
from thesis_tests.data_models import InteractionData, TestPhase, TestGroup
from dashboard.processors.dynamic_task_manager import DynamicTaskManager, TaskType
from dashboard.processors.task_guidance_system import TaskGuidanceSystem


class ModeProcessor:
    """Base class for mode processors."""

    def __init__(self, orchestrator=None, data_collector=None, test_dashboard=None, image_database=None):
        self.orchestrator = orchestrator
        self.data_collector = data_collector
        self.test_dashboard = test_dashboard
        self.image_database = image_database

        # Initialize dynamic task system ONLY for Test Mode
        # These will be None in Flexible Mode to prevent any task-related functionality
        self.task_manager = None
        self.task_guidance = None

        print("🎯 TASK_SYSTEM: Task system initialization deferred until mode is determined")

    def _ensure_task_system_initialized(self):
        """Initialize task system only when in Test Mode"""
        dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

        if dashboard_mode == "Test Mode":
            if self.task_manager is None:
                self.task_manager = DynamicTaskManager()
                self.task_guidance = TaskGuidanceSystem()
                print("🎯 TASK_SYSTEM: Dynamic task manager initialized for Test Mode")
        else:
            # Ensure task system is disabled in Flexible Mode
            if self.task_manager is not None:
                self.task_manager = None
                self.task_guidance = None
                print("🎯 TASK_SYSTEM: Task system disabled for Flexible Mode")

    def render_active_tasks_ui(self):
        """Render active tasks UI - ONLY in Test Mode"""
        dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

        if dashboard_mode != "Test Mode":
            print("🎯 TASK_UI: Disabled - running in Flexible Mode")
            return

        if self.task_manager is None:
            print("🎯 TASK_UI: Task manager not initialized")
            return

        # Render task UI only in Test Mode
        try:
            active_tasks = self.task_manager.get_active_tasks()
            if active_tasks:
                st.markdown("### 🎯 Active Tasks")
                for task in active_tasks:
                    with st.expander(f"Task: {task.task_type.value.replace('_', ' ').title()}", expanded=False):
                        st.write(f"**Test Group**: {task.test_group}")
                        st.write(f"**Phase**: {task.current_phase}")
                        st.write(f"**Triggered at**: {task.triggered_at_completion:.1f}% completion")
                        st.write(f"**Phase Range**: {task.phase_completion_range}")

                        if st.button(f"Complete {task.task_type.value}", key=f"complete_{task.task_type.value}"):
                            self.task_manager.complete_task(task.task_type)
                            st.rerun()
        except AttributeError:
            print("🎯 TASK_UI: Task manager is None - cannot render tasks")

    async def process_input(self, user_input: str, mode: str, image_path: str = None) -> str:
        """Process user input based on the selected mode with optional image."""
        try:
            # CRITICAL: Check dashboard mode to determine if test features should be active
            dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')
            test_mode_active = (dashboard_mode == "Test Mode")

            # Initialize or disable task system based on mode
            self._ensure_task_system_initialized()

            # Only get test-specific variables if in Test Mode
            test_group_raw = None
            if test_mode_active:
                # Get test group from multiple possible sources
                test_group_raw = (
                    st.session_state.get('test_group', None) or
                    st.session_state.get('test_group_selection', None) or
                    st.session_state.get('current_mode', None)
                )

                # Convert to TestGroup enum if needed
                if test_group_raw:
                    if isinstance(test_group_raw, str):
                        # Map string values to TestGroup enum
                        test_group_mapping = {
                            "MENTOR": TestGroup.MENTOR,
                            "GENERIC_AI": TestGroup.GENERIC_AI,
                            "CONTROL": TestGroup.CONTROL,
                            "Socratic Agent": TestGroup.MENTOR,
                            "Raw GPT": TestGroup.GENERIC_AI,
                            "No AI": TestGroup.CONTROL
                        }
                        test_group = test_group_mapping.get(test_group_raw, None)
                    else:
                        test_group = test_group_raw
                else:
                    test_group = None

                # Convert test_current_phase from string to TestPhase enum if needed
                test_phase_raw = st.session_state.get('test_current_phase', 'Ideation')
                if isinstance(test_phase_raw, str):
                    # Map string values to TestPhase enum
                    test_phase_mapping = {
                        "Ideation": TestPhase.IDEATION,
                        "Visualization": TestPhase.VISUALIZATION,
                        "Materialization": TestPhase.MATERIALIZATION,
                        "ideation": TestPhase.IDEATION,
                        "visualization": TestPhase.VISUALIZATION,
                        "materialization": TestPhase.MATERIALIZATION
                    }
                    test_phase = test_phase_mapping.get(test_phase_raw, TestPhase.IDEATION)
                else:
                    test_phase = test_phase_raw or TestPhase.IDEATION
            else:
                test_group = None
                test_phase = None

            print(f"🔬 MODE_PROCESSOR: dashboard_mode={dashboard_mode}, test_mode_active={test_mode_active}, test_group={test_group}, test_phase={test_phase}")

            # DEBUG: Show all test-related session state variables
            if test_mode_active:
                print(f"🔍 DEBUG: test_group_raw={test_group_raw}")
                print(f"🔍 DEBUG: session_state.test_group={st.session_state.get('test_group', 'NOT_SET')}")
                print(f"🔍 DEBUG: session_state.test_group_selection={st.session_state.get('test_group_selection', 'NOT_SET')}")
                print(f"🔍 DEBUG: session_state.current_mode={st.session_state.get('current_mode', 'NOT_SET')}")
                print(f"🔍 DEBUG: session_state.mentor_type={st.session_state.get('mentor_type', 'NOT_SET')}")

            # First, validate the question for appropriateness
            conversation_context = getattr(st.session_state, 'messages', [])[-5:]  # Last 5 messages for context
            validation_result = await validate_user_question(user_input, conversation_context)

            print(f"🔍 QUESTION VALIDATION: {validation_result}")

            # If question is inappropriate or off-topic, return redirection
            if not validation_result.get('is_appropriate', True) or not validation_result.get('is_on_topic', True):
                suggested_response = validation_result.get('suggested_response')
                if suggested_response:
                    print(f"🚫 REDIRECTING: Question deemed inappropriate/off-topic")
                    return suggested_response

            # Enhance user input with image context if available
            enhanced_input = self._enhance_input_with_image_context(user_input)

            # Handle test mode processing
            if test_mode_active and test_group and test_phase:
                return await self._process_test_mode(enhanced_input, test_group, test_phase, image_path)

            # Handle regular modes
            if mode in ["MENTOR", "Socratic Agent"]:
                return await self._process_mentor_mode(enhanced_input, image_path)
            elif mode in ["RAW_GPT", "Raw GPT"]:
                return await self._process_raw_gpt_mode(enhanced_input, image_path)
            elif mode in ["NO_AI", "No AI"]:
                return await self._process_no_ai_mode(enhanced_input, image_path)
            elif mode == "GENERIC_AI":
                return await self._process_generic_ai_mode(enhanced_input)
            elif mode == "CONTROL":
                return await self._process_control_mode(enhanced_input)
            else:
                return "Invalid mode selected."
        except Exception as e:
            st.error(f"❌ Error in process_input: {str(e)}")
            return f"An error occurred: {str(e)}"

    def _enhance_input_with_image_context(self, user_input: str) -> str:
        """Image context is now bundled at dashboard level - no enhancement needed here."""
        return user_input

    async def _process_test_mode(self, user_input: str, test_group: TestGroup,
                               test_phase: TestPhase, image_path: str = None) -> str:
        """Process input in test mode according to test logic documents with dynamic task system"""

        # Get current phase from session state for compatibility
        current_phase_str = st.session_state.get('test_current_phase', 'Ideation')
        test_group_name = test_group.value if test_group else "None"
        print(f"🔬 TEST_MODE: Processing {test_group_name} in {current_phase_str} phase")

        # Get conversation history for task detection
        conversation_history = st.session_state.get('messages', [])

        # Check for image analysis if image was uploaded
        image_analysis = None
        image_uploaded = image_path is not None
        if image_uploaded:
            # Get image analysis from session state if available
            image_analyses = st.session_state.get('image_analyses', [])
            for analysis in image_analyses:
                if analysis.get('path') == image_path:
                    image_analysis = analysis.get('detailed_analysis', {})
                    break

        # Get phase completion percentage from session state
        phase_completion_percent = 0.0
        try:
            # Try to get phase completion from phase progression system
            if hasattr(st.session_state, 'phase_session_id') and st.session_state.phase_session_id:
                # Import phase progression system
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                from phase_progression_system import PhaseProgressionSystem

                phase_system = PhaseProgressionSystem()
                session = phase_system.sessions.get(st.session_state.phase_session_id)
                if session and session.current_phase:
                    current_progress = session.phase_progress.get(session.current_phase)
                    if current_progress:
                        phase_completion_percent = current_progress.completion_percent
                        print(f"🎯 TASK_TRIGGER: Phase completion: {phase_completion_percent:.1f}%")
        except Exception as e:
            print(f"⚠️ Could not get phase completion: {e}")

        # TASK SYSTEM: Only process tasks if in Test Mode and task system is initialized
        triggered_task = None
        print(f"🎯 TASK_DEBUG: task_manager={self.task_manager is not None}, test_group={test_group}, phase_completion={phase_completion_percent:.1f}%")

        if self.task_manager is not None and test_group is not None:
            print(f"🎯 TASK_TRIGGER_CHECK: Checking triggers for {test_group.value} at {phase_completion_percent:.1f}% completion")

            # Check for dynamic task triggers
            triggered_task = self.task_manager.check_task_triggers(
                user_input=user_input,
                conversation_history=conversation_history,
                current_phase=current_phase_str.lower(),
                test_group=test_group.value,
                image_uploaded=image_uploaded,
                image_analysis=image_analysis,
                phase_completion_percent=phase_completion_percent
            )

            print(f"🎯 TASK_TRIGGER_RESULT: triggered_task={triggered_task}")

            # Activate triggered task
            if triggered_task:
                task = self.task_manager.activate_task(
                    task_type=triggered_task,
                    test_group=test_group.value,
                    current_phase=current_phase_str.lower(),
                    trigger_reason=f"Triggered by: {user_input[:50]}...",
                    task_data={'image_path': image_path} if image_path else {},
                    phase_completion_percent=phase_completion_percent
                )
                print(f"🎯 TASK_ACTIVATED: {triggered_task.value} for {test_group.value} at {phase_completion_percent:.1f}% completion")
            else:
                print(f"🎯 TASK_NO_TRIGGER: No tasks triggered at {phase_completion_percent:.1f}% completion")
        elif self.task_manager is None:
            print(f"🎯 TASK_SYSTEM: Disabled - task manager not initialized")
        elif test_group is None:
            print(f"🎯 TASK_SYSTEM: Disabled - test group not set (running in Flexible Mode or test group not selected)")

        # Check if phase transition is needed (only if test_group is set)
        if test_group is not None:
            self._check_phase_transition(user_input, test_group)

        # Route to appropriate test condition
        if test_group == TestGroup.MENTOR:
            # MENTOR Test (Group A) - Multi-agent scaffolding with phase-specific enhancements
            response = await self._process_mentor_test_mode(user_input, test_phase, image_path)

        elif test_group == TestGroup.GENERIC_AI:
            # Generic AI Test (Group B) - Direct assistance without scaffolding
            response = await self._process_generic_ai_test_mode(user_input, test_phase, image_path)

        elif test_group == TestGroup.CONTROL:
            # Control Group Test (Group C) - No AI assistance, self-directed
            response = await self._process_control_test_mode(user_input, test_phase, image_path)

        else:
            response = "Invalid test group configuration."

        # Apply dynamic task guidance if tasks are active AND task system is initialized (Test Mode only)
        if self.task_manager is not None and self.task_guidance is not None:
            active_tasks = self.task_manager.get_active_tasks()
            if active_tasks:
                for task in active_tasks:
                    print(f"🎯 APPLYING_GUIDANCE: {task.task_type.value} for {task.test_group}")
                    response = self.task_guidance.get_task_guidance(
                        task=task,
                        user_input=user_input,
                        base_response=response,
                        conversation_context=st.session_state.get('messages', [])
                    )
        else:
            print(f"🎯 TASK_GUIDANCE: Disabled - running in Flexible Mode")

        # Log test-specific interaction with enhanced metadata (only if test_group and test_phase are valid)
        if test_group is not None and test_phase is not None:
            await self._log_test_interaction(user_input, response, test_group, test_phase)

        return response

    def _check_phase_transition(self, user_input: str, test_group: TestGroup):
        """Check if phase transition should occur based on interaction patterns"""

        current_phase = st.session_state.get('test_current_phase', 'Ideation')
        interaction_count = len(st.session_state.get('messages', [])) // 2  # User + assistant pairs

        # Phase transition logic based on test group and interaction patterns
        if test_group == TestGroup.MENTOR:
            # MENTOR mode: Use existing automatic phase transition (no changes needed)
            # The phase system handles this automatically based on content analysis
            pass

        elif test_group == TestGroup.GENERIC_AI:
            # Generic AI mode: Timer-based or interaction-count-based transitions
            phase_interaction_limits = {
                'Ideation': 4,  # 4 interactions before moving to visualization
                'Visualization': 4,  # 4 interactions before moving to materialization
                'Materialization': 6  # 6 interactions before completion
            }

            limit = phase_interaction_limits.get(current_phase, 999)
            if interaction_count >= limit:
                self._advance_phase_automatically()

        elif test_group == TestGroup.CONTROL:
            # Control mode: Similar to Generic AI but with different thresholds
            phase_interaction_limits = {
                'Ideation': 5,  # Slightly more interactions since no AI guidance
                'Visualization': 5,
                'Materialization': 7
            }

            limit = phase_interaction_limits.get(current_phase, 999)
            if interaction_count >= limit:
                self._advance_phase_automatically()

    def _advance_phase_automatically(self):
        """Automatically advance to the next phase"""

        current_phase = st.session_state.get('test_current_phase', 'Ideation')

        phase_progression = {
            'Ideation': 'Visualization',
            'Visualization': 'Materialization',
            'Materialization': 'Complete'
        }

        next_phase = phase_progression.get(current_phase, 'Complete')

        if next_phase != 'Complete':
            st.session_state.test_current_phase = next_phase
            print(f"🔄 AUTO_PHASE: Advanced from {current_phase} to {next_phase}")

            # CRITICAL FIX: Handle phase transition with proper task checking
            test_group = st.session_state.get('test_group', TestGroup.MENTOR).name
            self._handle_phase_transition(
                from_phase=current_phase.lower(),
                to_phase=next_phase.lower(),
                test_group=test_group,
                user_input=f"Phase transition to {next_phase}"
            )

            # Add a system message about phase transition
            phase_transition_message = f"**Phase Transition**: Moving from {current_phase} to {next_phase} phase."

            if 'messages' not in st.session_state:
                st.session_state.messages = []

            st.session_state.messages.append({
                "role": "system",
                "content": phase_transition_message,
                "timestamp": datetime.now().isoformat(),
                "phase_transition": True
            })

    async def _process_mentor_test_mode(self, user_input: str, test_phase: TestPhase, image_path: str = None) -> str:
        """MENTOR Test (Group A) - Enhanced multi-agent scaffolding with phase-specific interactions"""

        # Use the existing mentor mode as base
        base_response = await self._process_mentor_mode(user_input, image_path)

        # Add test-specific phase enhancements based on test logic documents
        phase_enhancement = self._get_mentor_phase_enhancement(test_phase, user_input, base_response)

        if phase_enhancement:
            enhanced_response = f"{base_response}\n\n{phase_enhancement}"
        else:
            enhanced_response = base_response

        print(f"🎯 MENTOR_TEST: Phase={test_phase.value}, Enhanced={bool(phase_enhancement)}")
        return enhanced_response

    async def _process_generic_ai_test_mode(self, user_input: str, test_phase: TestPhase, image_path: str = None) -> str:
        """Generic AI Test (Group B) - Direct assistance without scaffolding"""

        # Use RAW_GPT mode as base for direct assistance
        base_response = await self._process_raw_gpt_mode(user_input, image_path)

        # Ensure response is direct and informational (no scaffolding)
        direct_response = self._ensure_direct_assistance_style(base_response, test_phase)

        # IMPORTANT: Ensure phase progression is tracked for GENERIC_AI mode too
        self._ensure_phase_progression_tracking(user_input, "GENERIC_AI")

        print(f"🤖 GENERIC_AI_TEST: Phase={test_phase.value}, Direct assistance provided")
        return direct_response

    async def _process_control_test_mode(self, user_input: str, test_phase: TestPhase, image_path: str = None) -> str:
        """Control Group Test (Group C) - No AI assistance, self-directed prompts only"""

        # Use NO_AI mode as base
        base_response = await self._process_no_ai_mode(user_input, image_path)

        # Ensure minimal, self-directed prompts only
        control_response = self._ensure_control_group_style(base_response, test_phase)

        # IMPORTANT: Ensure phase progression is tracked for CONTROL mode too
        self._ensure_phase_progression_tracking(user_input, "CONTROL")

        print(f"🎯 CONTROL_TEST: Phase={test_phase.value}, Self-directed prompt provided")
        return control_response

    def _get_mentor_phase_enhancement(self, test_phase: TestPhase, user_input: str, base_response: str) -> str:
        """Get phase-specific enhancements for MENTOR test based on test logic documents"""

        # Get current phase from session state (using string values for compatibility)
        current_phase_str = st.session_state.get('test_current_phase', 'Ideation')

        # Avoid adding enhancement if response already has questions
        if "?" in base_response:
            return None

        if current_phase_str == 'Ideation' or test_phase == TestPhase.IDEATION:
            # Ideation phase enhancements from test logic documents
            enhancements = [
                "Before we begin designing, what do you think are the most important questions we should ask about this community?",
                "What are some successful examples of warehouse-to-community transformations you're aware of?",
                "Why might the existing industrial character be valuable to preserve? What would be lost if we completely transformed it?",
                "How are you approaching this problem differently than a typical new-build community center?",
                "What assumptions are you making about how this community gathers and interacts?"
            ]
            return enhancements[len(user_input) % len(enhancements)]

        elif current_phase_str == 'Visualization' or test_phase == TestPhase.VISUALIZATION:
            # Visualization phase enhancements from test logic documents
            enhancements = [
                "How might you visualize these spatial relationships? Consider sketching your concepts.",
                "What does this proportion suggest about your intended community capacity?",
                "How do your spatial relationships reflect community interaction patterns?",
                "What are the implications of your circulation pattern for spontaneous interaction?",
                "How can you represent the integration between existing industrial elements and new community functions?"
            ]
            return enhancements[len(user_input) % len(enhancements)]

        elif current_phase_str == 'Materialization' or test_phase == TestPhase.MATERIALIZATION:
            # Materialization phase enhancements from test logic documents
            enhancements = [
                "What materials and construction methods would support your design vision while respecting the existing structure?",
                "How do your design modifications work with the existing structural grid?",
                "Where will your new systems integrate with the preserved industrial elements?",
                "How does your vertical circulation strategy ensure inclusive access for all community members?",
                "What construction sequencing would allow the community center to remain partially operational during renovation?"
            ]
            return enhancements[len(user_input) % len(enhancements)]

        return None

    def _ensure_direct_assistance_style(self, response: str, test_phase: TestPhase) -> str:
        """Ensure response provides direct assistance without scaffolding questions"""

        # Remove any scaffolding questions that might have been added
        lines = response.split('\n')
        filtered_lines = []

        for line in lines:
            # Keep informational content, remove questions
            if '?' not in line or 'consider' not in line.lower():
                filtered_lines.append(line)

        direct_response = '\n'.join(filtered_lines).strip()

        # Add phase-specific direct information if response is too short
        if len(direct_response.split()) < 20:
            phase_info = self._get_direct_phase_information(test_phase)
            direct_response = f"{direct_response}\n\n{phase_info}"

        return direct_response

    def _ensure_control_group_style(self, response: str, test_phase: TestPhase) -> str:
        """Ensure response provides minimal self-directed prompts only"""

        # Get current phase from session state for compatibility
        current_phase_str = st.session_state.get('test_current_phase', 'Ideation')

        # Control group responses should be minimal and self-directed based on test logic documents
        if current_phase_str == 'Ideation':
            return "Continue developing your community center concept. Document your thinking process and design decisions as you work through the challenge."
        elif current_phase_str == 'Visualization':
            return "Proceed with visualizing your design concept. Use sketches, diagrams, or written descriptions to develop your spatial ideas."
        elif current_phase_str == 'Materialization':
            return "Work on the technical implementation of your design. Consider materials, structural systems, and construction methods that support your concept."
        else:
            return "Continue with your design work. Document your process and decisions."

    def _get_direct_phase_information(self, test_phase: TestPhase) -> str:
        """Get direct informational content for generic AI test mode based on test logic documents"""

        # Get current phase from session state for compatibility
        current_phase_str = st.session_state.get('test_current_phase', 'Ideation')

        if current_phase_str == 'Ideation':
            return """For community center design in adaptive reuse projects, consider these key elements:

            **Programming**: Meeting rooms, recreational spaces, educational areas, social services, flexible multipurpose zones
            **Community Analysis**: Demographics, cultural needs, existing social patterns, accessibility requirements
            **Adaptive Reuse Strategy**: Preserving industrial character while introducing community functions, structural assessment, code compliance
            **Site Integration**: Urban context, transportation access, parking, outdoor community spaces"""

        elif current_phase_str == 'Visualization':
            return """Effective architectural visualization for community centers should include:

            **Spatial Diagrams**: Circulation patterns, adjacency relationships, public/private zones, flexible space configurations
            **Technical Drawings**: Floor plans showing existing structure integration, sections revealing height utilization, site plans with community connections
            **Design Communication**: Sketches showing community interaction scenarios, material and lighting studies, accessibility compliance diagrams"""

        elif current_phase_str == 'Materialization':
            return """Technical implementation for warehouse-to-community center conversion involves:

            **Structural Systems**: Assessment of existing steel/concrete frame, new load requirements for community programming, seismic upgrades if needed
            **Building Envelope**: Insulation strategies for existing walls, new window/door openings, sustainable material selections
            **MEP Systems**: HVAC for diverse programming needs, electrical upgrades for modern community functions, plumbing for kitchens/restrooms
            **Construction Approach**: Phased construction to minimize community disruption, material sourcing, budget considerations"""

        return "Proceed with your design development using appropriate architectural methods and considerations."

    async def _log_test_interaction(self, user_input: str, response: str,
                                  test_group: TestGroup, test_phase: TestPhase):
        """Log interaction with test-specific metadata for research analysis"""

        if self.data_collector:
            # Calculate test-specific cognitive metrics
            cognitive_metrics = self._calculate_test_cognitive_metrics(user_input, response, test_group, test_phase)

            # Enhanced metadata for test mode
            test_metadata = {
                'test_mode_active': True,
                'test_group': test_group.value,
                'test_phase': test_phase.value,
                'test_timestamp': datetime.now().isoformat(),
                'cognitive_metrics': cognitive_metrics,
                'design_move_data': self._extract_design_moves(user_input, response, test_phase),
                'linkography_context': self._create_linkography_context(test_group, test_phase)
            }

            # Log with enhanced test metadata using existing interaction_logger.py
            self.data_collector.log_interaction(
                student_input=user_input,
                agent_response=response,
                routing_path=f"test_{test_group.value.lower()}",
                agents_used=self._get_test_agents_used(test_group),
                response_type=f"test_{test_group.value.lower()}_response",
                cognitive_flags=self._get_test_cognitive_flags(test_group, cognitive_metrics),
                student_skill_level="intermediate",
                confidence_score=cognitive_metrics.get('confidence_score', 0.7),
                sources_used=[],
                response_time=1.0,
                context_classification={'test_mode': True, 'test_group': test_group.value, 'test_phase': test_phase.value},
                metadata=test_metadata
            )

    def _calculate_test_cognitive_metrics(self, user_input: str, response: str,
                                        test_group: TestGroup, test_phase: TestPhase) -> Dict[str, float]:
        """Calculate cognitive metrics specific to test conditions based on test logic documents"""

        metrics = {}

        if test_group == TestGroup.MENTOR:
            # MENTOR group - High scaffolding effectiveness, cognitive engagement
            metrics = {
                'cognitive_offloading_prevention': 0.85,  # High COP due to scaffolding
                'deep_thinking_engagement': 0.90,        # High DTE from Socratic dialogue
                'scaffolding_effectiveness': 0.88,       # High SE from multi-agent system
                'knowledge_integration': 0.75,           # Good KI from guided discovery
                'learning_progression': 0.80,            # Good LP from phase progression
                'metacognitive_awareness': 0.82,         # High MA from reflection prompts
                'confidence_score': 0.78
            }
        elif test_group == TestGroup.GENERIC_AI:
            # Generic AI group - Direct assistance, potential cognitive offloading
            metrics = {
                'cognitive_offloading_prevention': 0.35,  # Lower COP due to direct answers
                'deep_thinking_engagement': 0.55,        # Moderate DTE
                'scaffolding_effectiveness': 0.25,       # Low SE - no scaffolding
                'knowledge_integration': 0.60,           # Moderate KI from information provision
                'learning_progression': 0.50,            # Moderate LP
                'metacognitive_awareness': 0.40,         # Lower MA - less reflection
                'confidence_score': 0.70
            }
        elif test_group == TestGroup.CONTROL:
            # Control group - No AI assistance, autonomous thinking
            metrics = {
                'cognitive_offloading_prevention': 1.0,   # Perfect COP - no external help
                'deep_thinking_engagement': 0.65,        # Good DTE from self-direction
                'scaffolding_effectiveness': 0.0,        # No SE - no scaffolding
                'knowledge_integration': 0.45,           # Lower KI - limited resources
                'learning_progression': 0.40,            # Lower LP - no guidance
                'metacognitive_awareness': 0.70,         # Good MA - self-reflection
                'confidence_score': 0.50
            }

        # Adjust metrics based on phase
        phase_multiplier = self._get_phase_complexity_multiplier(test_phase)
        for key in metrics:
            if key != 'confidence_score':
                metrics[key] *= phase_multiplier

        return metrics

    def _get_phase_complexity_multiplier(self, test_phase: TestPhase) -> float:
        """Get complexity multiplier based on test phase"""
        multipliers = {
            TestPhase.PRE_TEST: 0.8,
            TestPhase.IDEATION: 1.0,
            TestPhase.VISUALIZATION: 1.1,
            TestPhase.MATERIALIZATION: 1.2,
            TestPhase.POST_TEST: 0.9
        }
        return multipliers.get(test_phase, 1.0)

    async def _process_mentor_mode(self, user_input: str, image_path: str = None) -> str:
        """Process using the full mentor system."""
        # Ensure session is initialized
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create ArchMentorState for the orchestrator
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../thesis-agents'))
        from state_manager import ArchMentorState, StudentProfile
        
        # Create student profile
        student_profile = StudentProfile(
            skill_level="intermediate",
            learning_style="visual",
            cognitive_load=0.3,
            engagement_level=0.7
        )
        
        # Create state with current conversation history
        current_brief = "architectural project"
        if st.session_state.analysis_results:
            text_analysis = st.session_state.analysis_results.get('text_analysis', {})
            current_brief = text_analysis.get('building_type', current_brief)

        # ENHANCEMENT: Get current phase information from dashboard's phase system
        current_phase_info = None
        try:
            # Access the phase system from session state (set by dashboard)
            if hasattr(st.session_state, 'phase_system') and hasattr(st.session_state, 'phase_session_id'):
                phase_system = st.session_state.phase_system
                phase_session_id = st.session_state.phase_session_id

                # Get current phase from the phase progression system
                progress_summary = phase_system.get_progress_summary(phase_session_id)
                if "error" not in progress_summary:
                    current_phase_info = {
                        "current_phase": progress_summary.get("current_phase", "ideation"),
                        "phase_progress": progress_summary.get("phase_progress", {}),
                        "session_id": phase_session_id
                    }
                    print(f"🎯 MODE_PROCESSOR: Using phase info from dashboard: {current_phase_info['current_phase']}")
        except Exception as e:
            print(f"⚠️ MODE_PROCESSOR: Could not get phase info: {e}")

        state = ArchMentorState(
            messages=st.session_state.messages.copy(),
            current_design_brief=current_brief,
            student_profile=student_profile,
            domain="architecture",
            # Pass phase information to the orchestrator
            phase_info=current_phase_info
        )

        # Image processing is now handled at the dashboard level and bundled with user input
        # No separate image processing needed here - the orchestrator receives the complete message

        # Check if the last message has enhanced content (with image analysis)
        enhanced_content = user_input
        if st.session_state.messages and st.session_state.messages[-1].get("enhanced_content"):
            enhanced_content = st.session_state.messages[-1]["enhanced_content"]
            print(f"🔍 MODE_PROCESSOR: Using enhanced content with image analysis")

        # Add user message to state using enhanced content for system processing
        user_message = {
            "role": "user",
            "content": enhanced_content  # Use enhanced content with image analysis for orchestrator
        }
        state.messages.append(user_message)
        
        # Process with orchestrator
        print(f"🎯 MODE_PROCESSOR: Calling orchestrator with phase: {current_phase_info.get('current_phase', 'unknown') if current_phase_info else 'no_phase_info'}")
        print(f"🎯 MODE_PROCESSOR: State messages count: {len(state.messages)}")
        print(f"🎯 MODE_PROCESSOR: Last message: {state.messages[-1].get('content', '')[:100] if state.messages else 'No messages'}...")

        try:
            result = await self.orchestrator.process_student_input(state)
            print(f"✅ MODE_PROCESSOR: Orchestrator returned result")
            print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

            response = result.get("response", "I apologize, but I couldn't generate a response.")
            response_metadata = result.get("metadata", {})

            print(f"📝 MODE_PROCESSOR: Response length: {len(response) if response else 0}")
            print(f"📝 MODE_PROCESSOR: Response preview: {response[:100] if response else 'No response'}...")

        except Exception as e:
            print(f"❌ MODE_PROCESSOR: Orchestrator error: {e}")
            import traceback
            traceback.print_exc()
            response = f"I apologize, but I encountered an error: {str(e)}"
            response_metadata = {}

        # Store comprehensive metadata for display
        try:
            # Store the full metadata including enhancement metrics and phase info
            st.session_state.last_response_metadata = response_metadata

            # Also store specific metrics for easy access
            if "enhancement_metrics" in response_metadata:
                st.session_state.enhancement_metrics = response_metadata["enhancement_metrics"]

            if "phase_analysis" in response_metadata:
                st.session_state.phase_analysis = response_metadata["phase_analysis"]

            # Store processing info
            agents_used = response_metadata.get("agents_used", [])
            routing_path = response_metadata.get("routing_path", "unknown")

            st.session_state.agents_used = agents_used
            st.session_state.routing_path = routing_path

            # Debug logging for routing
            print(f"🎯 Dashboard: Routing path = {routing_path}")
            print(f"🤖 Dashboard: Agents used = {agents_used}")

        except Exception as e:
            print(f"Warning: Could not store metadata: {e}")
        
        # Log interaction
        try:
            interaction = InteractionData(
                id=str(uuid.uuid4()),
                session_id=st.session_state.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,
                interaction_type="mentor_response",
                user_input=user_input,
                system_response=response,
                response_time=1.0,
                cognitive_metrics={
                    "understanding_level": 0.7,
                    "confidence_level": 0.6,
                    "engagement_level": 0.8,
                    "confidence_score": 0.8
                },
                metadata={
                    **{"mode": "MENTOR"},
                    **(response_metadata if isinstance(response_metadata, dict) else {})
                }
            )
            
            if self.data_collector:
                # Minimal safe logging to satisfy logger signature
                routing_meta = response_metadata if isinstance(response_metadata, dict) else {}
                agents_used = routing_meta.get("agents_used", []) or [st.session_state.get('current_mode','MENTOR')]
                routing_path = routing_meta.get("routing_path") or routing_meta.get("route") or "mentor_mode"
                cognitive_flags = routing_meta.get("cognitive_flags", [])
                self.data_collector.log_interaction(
                    student_input=user_input,
                    agent_response=str(response)[:500],
                    routing_path=routing_path,
                    agents_used=agents_used,
                    response_type=st.session_state.get('current_mode','MENTOR').lower(),
                    cognitive_flags=cognitive_flags if isinstance(cognitive_flags, list) else [],
                    student_skill_level=student_profile.skill_level,
                    confidence_score=0.6,
                    sources_used=routing_meta.get('sources', []),
                    response_time=1.0,
                    context_classification=routing_meta.get('classification', {}),
                    metadata=routing_meta
                )
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
        return response
    
    async def _process_raw_gpt_mode(self, user_input: str, image_path: str = None) -> str:
        """Process using pure Raw GPT (completely independent of multi-agent system)."""
        # Ensure session is initialized
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Get conversation history for phase calculation and context
        messages = st.session_state.get('messages', [])

        # Call Pure Raw GPT processor with image support
        try:
            result = await get_raw_gpt_response(user_input, messages, st.session_state.session_id, image_path)
        except Exception as e:
            return f"I apologize, but I encountered an error calling Raw GPT: {e}"

        response = result.get("response", "I couldn't generate a response.")
        response_metadata = result.get("metadata", {})
        phase_info = result.get("phase_info", {})

        # Store metadata for display
        st.session_state.last_response_metadata = response_metadata

        # Store phase information
        if phase_info:
            st.session_state.raw_gpt_phase_info = phase_info
            print(f"🎯 RAW_GPT: Current phase = {phase_info.get('current_phase', 'unknown')}")
            print(f"📊 RAW_GPT: Phase progression = {phase_info.get('phase_progression', 0):.1%}")

        # Log interaction
        try:
            interaction = InteractionData(
                id=str(uuid.uuid4()),
                session_id=st.session_state.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,  # Map to enum if needed
                interaction_type="pure_raw_gpt_response",
                user_input=user_input,
                system_response=response,
                response_time=1.0,
                cognitive_metrics={
                    "understanding_level": 0.7,
                    "confidence_level": 0.6,
                    "engagement_level": 0.8,
                    "confidence_score": 0.7
                },
                metadata={**{"mode": "RAW_GPT"}, **response_metadata}
            )

            if self.data_collector:
                routing_meta = response_metadata if isinstance(response_metadata, dict) else {}
                agents_used = routing_meta.get("agents_used", []) or ["pure_raw_gpt"]
                routing_path = routing_meta.get("routing_path") or "pure_raw_gpt_mode"
                self.data_collector.log_interaction(
                    student_input=user_input,
                    agent_response=str(response)[:500],
                    routing_path=routing_path,
                    agents_used=agents_used,
                    response_type="pure_raw_gpt",
                    cognitive_flags=[],
                    student_skill_level='intermediate',
                    confidence_score=0.7,
                    sources_used=[],
                    response_time=1.0,
                    context_classification=routing_meta.get('classification', {}),
                    metadata=routing_meta
                )
        except Exception as e:
            print(f"Warning: Could not log Raw GPT interaction: {e}")

        return response

    async def _process_no_ai_mode(self, user_input: str, image_path: str = None) -> str:
        """Process using No AI mode (hardcoded questions only with phase calculation)."""
        # Ensure session is initialized
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Get conversation history for phase calculation
        messages = st.session_state.get('messages', [])

        # Call No AI processor with image acknowledgment
        try:
            result = await get_no_ai_response(user_input, messages, st.session_state.session_id, image_path)
        except Exception as e:
            return f"I apologize, but I encountered an error: {e}"

        response = result.get("response", "Please continue with your design thinking.")
        response_metadata = result.get("metadata", {})
        phase_info = result.get("phase_info", {})

        # Store metadata for display
        st.session_state.last_response_metadata = response_metadata

        # Store phase information
        if phase_info:
            st.session_state.no_ai_phase_info = phase_info
            print(f"🎯 NO_AI: Current phase = {phase_info.get('current_phase', 'unknown')}")
            print(f"📊 NO_AI: Phase progression = {phase_info.get('phase_progression', 0):.1%}")

        # Log interaction
        try:
            interaction = InteractionData(
                id=str(uuid.uuid4()),
                session_id=st.session_state.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,  # Map string to enum if needed
                interaction_type="no_ai_response",
                user_input=user_input,
                system_response=response,
                response_time=0.0,
                cognitive_metrics={
                    "understanding_level": 0.0,  # No AI understanding
                    "confidence_level": 0.0,     # No AI confidence
                    "engagement_level": 0.5,     # Neutral engagement
                    "confidence_score": 0.0
                },
                metadata={**{"mode": "NO_AI"}, **response_metadata}
            )

            if self.data_collector:
                routing_meta = response_metadata if isinstance(response_metadata, dict) else {}
                agents_used = routing_meta.get("agents_used", []) or ["no_ai"]
                routing_path = routing_meta.get("routing_path") or "no_ai_mode"
                self.data_collector.log_interaction(
                    student_input=user_input,
                    agent_response=str(response)[:500],
                    routing_path=routing_path,
                    agents_used=agents_used,
                    response_type="no_ai",
                    cognitive_flags=[],
                    student_skill_level='intermediate',
                    confidence_score=0.0,
                    sources_used=[],
                    response_time=0.0,
                    context_classification={},
                    metadata=routing_meta
                )
        except Exception as e:
            print(f"Warning: Could not log No AI interaction: {e}")

        return response

    async def _process_generic_ai_mode(self, user_input: str) -> str:
        """Process using generic AI."""
        # Ensure session is initialized
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Use test dashboard's generic AI mode
        if not self.test_dashboard:
            return "Generic AI mode is not available."
        
        response = self.test_dashboard.generic_ai_env.process_input(user_input)
        
        # Log interaction
        try:
            interaction = InteractionData(
                id=str(uuid.uuid4()),
                session_id=st.session_state.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,
                interaction_type="generic_response",
                user_input=user_input,
                system_response=response,
                response_time=1.0,
                cognitive_metrics={
                    "understanding_level": 0.7,
                    "confidence_level": 0.6,
                    "engagement_level": 0.8,
                    "confidence_score": 0.6
                },
                metadata={"mode": "GENERIC_AI", "routing_path": "generic_ai_mode", "agents_used": ["generic_ai"]}
            )
            
            if self.data_collector:
                routing_meta = {"routing_path": "generic_ai_mode", "agents_used": ["generic_ai"]}
                self.data_collector.log_interaction(
                    student_input=user_input,
                    agent_response=str(response)[:500],
                    routing_path=routing_meta["routing_path"],
                    agents_used=routing_meta["agents_used"],
                    response_type="generic_ai",
                    cognitive_flags=[],
                    student_skill_level='intermediate',
                    confidence_score=0.6,
                    sources_used=[],
                    response_time=1.0,
                    context_classification={},
                    metadata=routing_meta
                )
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
        return response
    
    async def _process_control_mode(self, user_input: str) -> str:
        """Process using control mode (no AI)."""
        # Ensure session is initialized
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Use test dashboard's control mode
        if not self.test_dashboard:
            return "Control mode is not available."
        
        response = self.test_dashboard.control_env.process_input(user_input)
        
        # Log interaction
        try:
            interaction = InteractionData(
                id=str(uuid.uuid4()),
                session_id=st.session_state.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,
                interaction_type="control_response",
                user_input=user_input,
                system_response=response,
                response_time=1.0,
                cognitive_metrics={
                    "understanding_level": 0.7,
                    "confidence_level": 0.6,
                    "engagement_level": 0.8,
                    "confidence_score": 0.5
                },
                metadata={"mode": "CONTROL", "routing_path": "control_mode", "agents_used": ["control"]}
            )
            
            if self.data_collector:
                routing_meta = {"routing_path": "control_mode", "agents_used": ["control"]}
                self.data_collector.log_interaction(
                    student_input=user_input,
                    agent_response=str(response)[:500],
                    routing_path=routing_meta["routing_path"],
                    agents_used=routing_meta["agents_used"],
                    response_type="control",
                    cognitive_flags=[],
                    student_skill_level='intermediate',
                    confidence_score=0.5,
                    sources_used=[],
                    response_time=1.0,
                    context_classification={},
                    metadata=routing_meta
                )
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
        return response

    def _extract_design_moves(self, user_input: str, response: str, test_phase: TestPhase) -> Dict[str, Any]:
        """Extract design moves for linkography analysis based on test logic documents"""

        # Simple move extraction - in production this would be more sophisticated
        moves = []

        # Extract moves from user input
        if len(user_input.strip()) > 10:
            moves.append({
                'content': user_input,
                'move_type': 'analysis' if '?' in user_input else 'proposal',
                'phase': test_phase.value,
                'modality': 'text',
                'source': 'user_generated'
            })

        # Extract moves from system response
        if len(response.strip()) > 10:
            moves.append({
                'content': response,
                'move_type': 'support' if '?' in response else 'information',
                'phase': test_phase.value,
                'modality': 'text',
                'source': 'system_generated'
            })

        return {
            'moves': moves,
            'move_count': len(moves),
            'phase': test_phase.value
        }

    def _create_linkography_context(self, test_group: TestGroup, test_phase: TestPhase) -> Dict[str, Any]:
        """Create linkography context for benchmarking analysis"""

        return {
            'test_group': test_group.value,
            'test_phase': test_phase.value,
            'interaction_trigger': 'test_mode',
            'tool_used': f'test_{test_group.value.lower()}',
            'semantic_links': [],  # Would be calculated by benchmarking system
            'temporal_links': [],  # Would be calculated by benchmarking system
        }

    def _get_test_agents_used(self, test_group: TestGroup) -> List[str]:
        """Get agents used based on test group"""

        if test_group == TestGroup.MENTOR:
            return ['socratic_tutor', 'domain_expert', 'cognitive_enhancement', 'context_agent']
        elif test_group == TestGroup.GENERIC_AI:
            return ['generic_ai']
        elif test_group == TestGroup.CONTROL:
            return ['control_system']
        else:
            return ['unknown']

    def _get_test_cognitive_flags(self, test_group: TestGroup, cognitive_metrics: Dict[str, float]) -> List[str]:
        """Get cognitive flags based on test group and metrics"""

        flags = ['test_mode']

        if test_group == TestGroup.MENTOR:
            flags.extend(['scaffolding_active', 'socratic_dialogue', 'multi_agent'])
            if cognitive_metrics.get('cognitive_offloading_prevention', 0) > 0.7:
                flags.append('high_cop')
            if cognitive_metrics.get('deep_thinking_engagement', 0) > 0.7:
                flags.append('high_dte')

        elif test_group == TestGroup.GENERIC_AI:
            flags.extend(['direct_assistance', 'information_provision'])
            if cognitive_metrics.get('cognitive_offloading_prevention', 0) < 0.5:
                flags.append('potential_offloading')

        elif test_group == TestGroup.CONTROL:
            flags.extend(['self_directed', 'no_ai_assistance', 'autonomous'])
            if cognitive_metrics.get('metacognitive_awareness', 0) > 0.6:
                flags.append('high_metacognition')

        return flags

    def get_active_task_status(self) -> Dict[str, Any]:
        """Get status of active dynamic tasks for UI display"""
        return self.task_manager.get_task_status()

    # REMOVED: Duplicate render_active_tasks_ui method - using the mode-restricted version above

    def _ensure_phase_progression_tracking(self, user_input: str, test_group: str):
        """Ensure phase progression is tracked for all test groups"""
        try:
            # Initialize phase progression system if not already done
            if not hasattr(st.session_state, 'phase_session_id') or not st.session_state.phase_session_id:
                # Import phase progression system
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                from phase_progression_system import PhaseProgressionSystem

                phase_system = PhaseProgressionSystem()

                # Create a new session for this test group
                session_id = f"{test_group}_{st.session_state.session_id}"
                phase_system.create_session(session_id)
                st.session_state.phase_session_id = session_id

                print(f"🎯 PHASE_TRACKING: Created phase session for {test_group}: {session_id}")

            # Process the user input to update phase progression
            if hasattr(st.session_state, 'phase_session_id') and st.session_state.phase_session_id:
                from phase_progression_system import PhaseProgressionSystem
                phase_system = PhaseProgressionSystem()

                # Process the user message to update phase progression
                result = phase_system.process_user_message(st.session_state.phase_session_id, user_input)

                if result:
                    current_phase = result.get('current_phase', 'ideation')
                    completion_percent = 0.0

                    # Get completion percentage from phase progress
                    phase_progress = result.get('phase_progress', {})
                    if 'completion_percent' in phase_progress:
                        completion_percent = phase_progress['completion_percent']

                    print(f"🎯 PHASE_TRACKING: {test_group} - Phase: {current_phase}, Completion: {completion_percent:.1f}%")

                    # Update session state for consistency
                    phase_mapping = {
                        'ideation': 'Ideation',
                        'visualization': 'Visualization',
                        'materialization': 'Materialization'
                    }
                    st.session_state.test_current_phase = phase_mapping.get(current_phase, 'Ideation')

                    # CRITICAL FIX: Check for task triggers based on phase completion
                    self._check_and_trigger_tasks(user_input, current_phase, test_group, completion_percent)

        except Exception as e:
            print(f"⚠️ Phase progression tracking failed for {test_group}: {e}")
            # Don't let phase tracking errors break the main flow

    def _check_and_trigger_tasks(self, user_input: str, current_phase: str, test_group: str, completion_percent: float):
        """Check and trigger tasks based on phase completion percentage"""
        try:
            if self.task_manager is None:
                print(f"🎯 TASK_TRIGGER: Task manager not initialized - initializing now")
                self._ensure_task_system_initialized()

            if self.task_manager is None:
                print(f"🎯 TASK_TRIGGER: Task manager still not initialized - skipping")
                return

            # Get conversation history for task triggering
            conversation_history = st.session_state.get('messages', [])

            # Check if any tasks should be triggered
            triggered_task = self.task_manager.check_task_triggers(
                user_input=user_input,
                conversation_history=conversation_history,
                current_phase=current_phase,
                test_group=test_group,
                image_uploaded=False,  # TODO: Add image upload detection
                image_analysis=None,   # TODO: Add image analysis if needed
                phase_completion_percent=completion_percent
            )

            if triggered_task:
                print(f"🎯 TASK_TRIGGERED: {triggered_task.value} at {completion_percent:.1f}% completion in {current_phase} phase")

                # Activate the triggered task
                activated_task = self.task_manager.activate_task(
                    task_type=triggered_task,
                    test_group=test_group,
                    current_phase=current_phase,
                    trigger_reason=f"Phase completion: {completion_percent:.1f}%",
                    phase_completion_percent=completion_percent
                )

                if activated_task:
                    print(f"🎯 TASK_ACTIVATED: {activated_task.task_type.value} for {test_group}")

                    # Store task for UI rendering (like gamification does)
                    st.session_state['active_task'] = {
                        'task': activated_task,
                        'user_input': user_input,
                        'guidance_type': self._get_guidance_type_for_test_group(test_group),
                        'should_render': True
                    }
                else:
                    print(f"🎯 TASK_ACTIVATION_FAILED: Could not activate {triggered_task.value}")
            else:
                print(f"🎯 TASK_CHECK: No tasks triggered at {completion_percent:.1f}% completion in {current_phase}")

        except Exception as e:
            print(f"⚠️ Task triggering failed: {e}")
            import traceback
            traceback.print_exc()

    def _handle_phase_transition(self, from_phase: str, to_phase: str, test_group: str, user_input: str):
        """Handle phase transitions with proper task checking for missed and new tasks"""
        try:
            if self.task_manager is None:
                print(f"🔄 PHASE_TRANSITION: Task manager not initialized - initializing now")
                self._ensure_task_system_initialized()

            if self.task_manager is None:
                print(f"🔄 PHASE_TRANSITION: Task manager still not initialized - skipping")
                return

            # Get conversation history for task triggering
            conversation_history = st.session_state.get('messages', [])

            # Check for phase transition tasks (missed tasks + new phase tasks)
            transition_tasks = self.task_manager.check_phase_transition_tasks(
                from_phase=from_phase,
                to_phase=to_phase,
                user_input=user_input,
                conversation_history=conversation_history,
                test_group=test_group,
                image_uploaded=False,  # TODO: Add image upload detection
                image_analysis=None    # TODO: Add image analysis if needed
            )

            if transition_tasks:
                # Activate the highest priority task (first in the list)
                task_to_activate = transition_tasks[0]

                print(f"🔄 PHASE_TRANSITION_TASK: {task_to_activate.value} triggered during {from_phase} → {to_phase}")

                activated_task = self.task_manager.activate_task(
                    task_type=task_to_activate,
                    test_group=test_group,
                    current_phase=to_phase,
                    trigger_reason=f"Phase transition: {from_phase} → {to_phase}",
                    phase_completion_percent=0.0
                )

                if activated_task:
                    print(f"🔄 PHASE_TRANSITION_ACTIVATED: {activated_task.task_type.value} for {test_group}")

                    # Store task for UI rendering
                    st.session_state['active_task'] = {
                        'task': activated_task,
                        'user_input': user_input,
                        'guidance_type': self._get_guidance_type_for_test_group(test_group),
                        'should_render': True
                    }
                else:
                    print(f"🔄 PHASE_TRANSITION_ACTIVATION_FAILED: Could not activate {task_to_activate.value}")
            else:
                print(f"🔄 PHASE_TRANSITION: No tasks triggered for {from_phase} → {to_phase}")

        except Exception as e:
            print(f"⚠️ Phase transition handling failed: {e}")
            import traceback
            traceback.print_exc()

    def _get_guidance_type_for_test_group(self, test_group: str) -> str:
        """Get guidance type based on test group"""
        if test_group == "MENTOR":
            return "socratic"
        elif test_group == "GENERIC_AI":
            return "direct"
        elif test_group == "CONTROL":
            return "minimal"
        else:
            return "minimal"