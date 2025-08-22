"""
Mode processors for different AI interaction modes.
"""

import streamlit as st
import asyncio
import sys
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Import required components
from .raw_gpt_processor import get_raw_gpt_response
from .no_ai_processor import get_no_ai_response
from .question_validator import validate_user_question
from thesis_tests.data_models import InteractionData, TestPhase


class ModeProcessor:
    """Base class for mode processors."""

    def __init__(self, orchestrator=None, data_collector=None, test_dashboard=None, image_database=None):
        self.orchestrator = orchestrator
        self.data_collector = data_collector
        self.test_dashboard = test_dashboard
        self.image_database = image_database
    
    async def process_input(self, user_input: str, mode: str, image_path: str = None) -> str:
        """Process user input based on the selected mode with optional image."""
        try:
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

            # Handle both old testing modes and new mentor type modes
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