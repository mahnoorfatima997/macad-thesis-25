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
from thesis_tests.data_models import InteractionData, TestPhase


class ModeProcessor:
    """Base class for mode processors."""
    
    def __init__(self, orchestrator=None, data_collector=None, test_dashboard=None):
        self.orchestrator = orchestrator
        self.data_collector = data_collector
        self.test_dashboard = test_dashboard
    
    async def process_input(self, user_input: str, mode: str) -> str:
        """Process user input based on the selected mode."""
        try:
            # Handle both old testing modes and new mentor type modes
            if mode in ["MENTOR", "Socratic Agent"]:
                return await self._process_mentor_mode(user_input)
            elif mode in ["RAW_GPT", "Raw GPT"]:
                return await self._process_raw_gpt_mode(user_input)
            elif mode == "GENERIC_AI":
                return await self._process_generic_ai_mode(user_input)
            elif mode == "CONTROL":
                return await self._process_control_mode(user_input)
            else:
                return "Invalid mode selected."
        except Exception as e:
            st.error(f"❌ Error in process_input: {str(e)}")
            return f"An error occurred: {str(e)}"
    
    async def _process_mentor_mode(self, user_input: str) -> str:
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
        
        state = ArchMentorState(
            messages=st.session_state.messages.copy(),
            current_design_brief=current_brief,
            student_profile=student_profile,
            domain="architecture"
        )
        
        # Ensure we don't duplicate the same user message
        if not state.messages or state.messages[-1].get("role") != "user" or state.messages[-1].get("content") != user_input:
            state.messages.append({
                "role": "user",
                "content": user_input
            })
        
        # Process with orchestrator
        result = await self.orchestrator.process_student_input(state)
        response = result.get("response", "I apologize, but I couldn't generate a response.")
        response_metadata = result.get("metadata", {})
        
        # Store metadata for display
        try:
            st.session_state.last_response_metadata = response_metadata
        except Exception:
            pass
        
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
    
    async def _process_raw_gpt_mode(self, user_input: str) -> str:
        """Process using direct Raw GPT (no multi-agent)."""
        # Ensure session is initialized
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Build project context from analysis if available
        project_context = ""
        if st.session_state.analysis_results:
            ta = st.session_state.analysis_results.get('text_analysis', {})
            bt = ta.get('building_type')
            if bt:
                project_context = f"Building type: {bt}"
        
        # Call Raw GPT helper
        try:
            result = get_raw_gpt_response(user_input, project_context)
        except Exception as e:
            return f"I apologize, but I encountered an error calling Raw GPT: {e}"
        
        response = result.get("response", "I couldn't generate a response.")
        response_metadata = result.get("metadata", {})
        
        # Store metadata for display
        st.session_state.last_response_metadata = response_metadata
        
        # Log interaction
        try:
            interaction = InteractionData(
                id=str(uuid.uuid4()),
                session_id=st.session_state.session_id,
                timestamp=datetime.now(),
                phase=TestPhase.IDEATION,
                interaction_type="raw_gpt_response",
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
                agents_used = routing_meta.get("agents_used", []) or ["raw_gpt"]
                routing_path = routing_meta.get("routing_path") or routing_meta.get("route") or "raw_gpt_mode"
                cognitive_flags = routing_meta.get("cognitive_flags", [])
                self.data_collector.log_interaction(
                    student_input=user_input,
                    agent_response=str(response)[:500],
                    routing_path=routing_path,
                    agents_used=agents_used,
                    response_type="raw_gpt",
                    cognitive_flags=cognitive_flags if isinstance(cognitive_flags, list) else [],
                    student_skill_level='intermediate',
                    confidence_score=0.7,
                    sources_used=routing_meta.get('sources', []),
                    response_time=1.0,
                    context_classification=routing_meta.get('classification', {}),
                    metadata=routing_meta
                )
        except Exception as e:
            print(f"Warning: Could not log Raw GPT interaction: {e}")
        
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