"""
Refactored Unified Architectural Dashboard

A clean, modular dashboard for architectural design mentoring and testing.
"""

import streamlit as st
import os
import asyncio
import tempfile
from PIL import Image
from datetime import datetime
from typing import Dict, Any, Optional

# Import configuration and utilities
from .config.settings import PAGE_CONFIG, TEMPLATE_PROMPTS, TESTING_MODES, SKILL_LEVELS, INPUT_MODES, MENTOR_TYPES, get_api_key
from .ui.styles import apply_dashboard_styles
from .core.session_manager import initialize_session_state, ensure_session_started
from .ui.chat_components import (
    render_welcome_section, render_mode_configuration, render_chat_history,
    get_chat_input, render_chat_message, response_contains_questions,
    render_input_mode_selection, render_mentor_type_selection, render_template_selection,
    render_skill_level_selection, render_project_description_input, render_file_upload, validate_input,
    render_chat_interface
)
from .ui.sidebar_components import render_complete_sidebar
from .ui.analysis_components import render_cognitive_analysis_dashboard, render_metrics_summary, render_phase_progress_section
from .processors.mode_processors import ModeProcessor
from .analysis.phase_analyzer import PhaseAnalyzer

# Import external dependencies
from phase_progression_system import PhaseProgressionSystem
from thesis_tests.test_dashboard import TestDashboard
from thesis_tests.data_models import InteractionData, TestPhase


# Configure Streamlit (must be first Streamlit command)
st.set_page_config(**PAGE_CONFIG)

# Cached resources
@st.cache_resource
def get_cached_orchestrator():
    """Get cached orchestrator instance."""
    import sys
    import os
    # Add thesis-agents to path
    thesis_agents_path = os.path.join(os.path.dirname(__file__), '../thesis-agents')
    if thesis_agents_path not in sys.path:
        sys.path.insert(0, thesis_agents_path)

    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        return LangGraphOrchestrator(domain="architecture")
    except ImportError as e:
        st.error(f"Failed to import LangGraphOrchestrator: {e}")
        return None


# Removed: get_cached_mentor - functionality integrated into dashboard


@st.cache_resource
def get_cached_phase_system():
    """Get cached phase system instance."""
    return PhaseProgressionSystem()


class UnifiedArchitecturalDashboard:
    """Main dashboard class for the unified architectural mentor system."""
    
    def __init__(self):
        """Initialize the dashboard."""
        # Note: set_page_config moved to run() method to avoid duplicate calls

        # Apply styles
        apply_dashboard_styles()
        
        # Get API key
        self.api_key = get_api_key()
        if not self.api_key:
            st.error("❌ OPENAI_API_KEY not found. Please set it as an environment variable or in Streamlit secrets.")
            st.stop()
        
        # Initialize session state
        initialize_session_state()
        
        # Initialize core components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize core dashboard components."""
        # Lazy + cached heavy objects
        self.orchestrator = get_cached_orchestrator()
        self.phase_system = get_cached_phase_system()
        
        # Phase analyzer
        self.phase_analyzer = PhaseAnalyzer()
        
        # Data collector: store once in session
        if 'data_collector' not in st.session_state:
            # Import InteractionLogger from the correct location
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../thesis-agents'))
            from data_collection.interaction_logger import InteractionLogger
            st.session_state.data_collector = InteractionLogger(session_id="unified_dashboard_session")
        self.data_collector = st.session_state.data_collector
        
        # Test dashboard lazy load (spacy heavy)
        if 'test_dashboard' not in st.session_state:
            st.session_state.test_dashboard = None
        self.test_dashboard = st.session_state.test_dashboard
        
        # Mode processor
        self.mode_processor = ModeProcessor(
            orchestrator=self.orchestrator,
            data_collector=self.data_collector,
            test_dashboard=self.test_dashboard
        )
    
    def run(self):
        """Main run method for the dashboard."""
        # Render sidebar
        render_complete_sidebar(self.data_collector)
        
        # Render main chat interface
        self._render_main_chat()
    
    def _render_main_chat(self):
        """Render the main chat interface."""
        # Optional: show pre-test at the very top before any other UI (when enabled and before analysis)
        if st.session_state.get("show_pre_test", False) and not st.session_state.get("analysis_complete", False):
            self._render_pretest_block()

        # Welcome section
        render_welcome_section()
        
        # Mode configuration using full width
        render_mode_configuration()
        
        # Input mode selection
        input_mode = render_input_mode_selection()
        st.session_state.input_mode = input_mode
        
        # Mentor type selection
        mentor_type = render_mentor_type_selection()
        st.session_state.mentor_type = mentor_type
        st.session_state.current_mode = mentor_type  # Map to current_mode for compatibility
        
        # Template prompts
        selected_template = render_template_selection()
        
        # Skill level selection
        skill_level = render_skill_level_selection()
        
        # Project description input
        template_text = TEMPLATE_PROMPTS.get(selected_template, "")
        project_description = render_project_description_input(template_text, input_mode)
        
        # File upload based on input mode
        uploaded_file = render_file_upload(input_mode)
        
        # Start analysis button
        with st.form(key="start_form"):
            start_clicked = st.form_submit_button("Start Analysis")
        
        if start_clicked:
            # Validate input based on mode
            is_valid, error_msg = validate_input(input_mode, project_description, uploaded_file)
            if not is_valid:
                st.error(error_msg)
            else:
                self._handle_start_analysis(project_description, uploaded_file, skill_level, mentor_type, input_mode)
        
        # Chat interface (after analysis)
        if st.session_state.analysis_complete:
            self._render_chat_interface()
            
            # Comprehensive analysis results
            self._render_analysis_results()
            
            # Phase progression insights
            if len(st.session_state.messages) > 0:
                self._render_phase_insights()
    
    def _handle_start_analysis(self, project_description: str, uploaded_file, skill_level: str, mentor_type: str, input_mode: str):
        """Handle the start analysis process."""
        # Handle Image Only mode
        if input_mode == "Image Only":
            project_description = "Analyze this architectural drawing"
        elif not project_description.strip():
            project_description = "Please analyze my architectural project"
        
        with st.spinner("🧠 Analyzing your design..."):
            try:
                # Initialize session
                ensure_session_started()
                self.data_collector.session_id = st.session_state.session_id
                
                # Store image path if uploaded
                if uploaded_file:
                    import tempfile
                    from PIL import Image
                    image = Image.open(uploaded_file)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        image.save(tmp_file.name)
                        st.session_state.uploaded_image_path = tmp_file.name
                
                # Run analysis based on selected mode
                if mentor_type in ["MENTOR", "Socratic Agent"]:
                    results = self._run_mentor_analysis(project_description, uploaded_file, skill_level)
                else:
                    results = self._create_default_analysis_results()
                
                # Store results
                st.session_state.analysis_results = results
                st.session_state.analysis_complete = True
                
                # Initialize phase system
                self._initialize_phase_system()
                
                # Process initial user input
                self._process_initial_input(project_description, mentor_type)
                
                st.success("✅ Analysis complete. Multi-agent mentor has responded to your initial prompt.")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
    
    def _run_mentor_analysis(self, project_description: str, uploaded_file, skill_level: str):
        """Run mentor analysis for MENTOR mode using orchestrator directly."""
        # Create ArchMentorState for analysis
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../thesis-agents'))
        from state_manager import ArchMentorState, StudentProfile, VisualArtifact
        from agents.analysis_agent import AnalysisAgent
        
        # Create student profile
        student_profile = StudentProfile(
            skill_level=skill_level,
            learning_style="visual",
            cognitive_load=0.3,
            engagement_level=0.7
        )
        
        # Initialize state
        state = ArchMentorState()
        state.current_design_brief = project_description
        state.student_profile = student_profile
        state.domain = "architecture"
        
        # Add initial message
        state.messages = [
            {"role": "user", "content": f"I'm working on my {project_description.lower()} and need help with the design process."}
        ]
        
        # Handle image if provided
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                image.save(tmp_file.name)
                temp_image_path = tmp_file.name
                
            artifact = VisualArtifact(
                id="uploaded_sketch",
                type="sketch",
                image_path=temp_image_path
            )
            state.current_sketch = artifact
            state.visual_artifacts.append(artifact)
        
        # Run analysis using AnalysisAgent directly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            analysis_agent = AnalysisAgent("architecture")
            analysis_result = loop.run_until_complete(analysis_agent.process(state))
            
            # Convert AgentResponse to dictionary if needed
            if hasattr(analysis_result, 'response_text'):
                from .ui.analysis_components import convert_agent_response_to_dict
                analysis_result = convert_agent_response_to_dict(analysis_result)

            # Extract building type from state
            building_type = state.extract_building_type_from_brief_only()
            print(f"🏗️ Dashboard: Detected building type: {building_type}")

            # Ensure building type is in the analysis result
            if isinstance(analysis_result, dict):
                if 'text_analysis' not in analysis_result:
                    analysis_result['text_analysis'] = {}
                analysis_result['text_analysis']['building_type'] = building_type
                analysis_result['building_type'] = building_type  # Also at top level

            # Return comprehensive results
            return {
                "state": state,
                "analysis_result": analysis_result,
                "vision_available": uploaded_file is not None,
                "building_type": building_type,  # Ensure it's available at top level
                **analysis_result  # Merge analysis result into top level for compatibility
            }
        finally:
            loop.close()
    
    def _create_default_analysis_results(self):
        """Create default analysis results for non-mentor modes."""
        return {
            "text_analysis": {
                "building_type": "architectural project",
                "key_themes": ["design", "architecture", "planning"],
                "program_requirements": ["functional spaces", "user needs", "site constraints"]
            },
            "phase_analysis": {
                "phase": "initial_analysis",
                "confidence": 0.8,
                "progression_score": 0.15,
                "completed_milestones": 1,
                "total_milestones": 12,
                "next_milestone": "site_analysis",
                "phase_recommendations": ["Focus on site context", "Define program requirements"]
            },
            "synthesis": {
                "cognitive_challenges": ["complex_program_requirements", "site_constraints"],
                "learning_opportunities": ["sustainable_design", "user_centered_approach"],
                "missing_considerations": ["accessibility", "building_codes"],
                "next_focus_areas": ["site_analysis", "program_development"]
            }
        }
    
    def _initialize_phase_system(self):
        """Initialize the phase progression system."""
        if st.session_state.phase_system is None:
            st.session_state.phase_system = self.phase_system
        if st.session_state.phase_session_id is None:
            st.session_state.phase_session_id = f"phase_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.phase_system.start_session(st.session_state.phase_session_id)
    
    def _process_initial_input(self, initial_input: str, current_mode: str):
        """Process the initial user input and generate response."""
        if not initial_input or not initial_input.strip():
            return
        
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": initial_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process response based on current mode
        response = asyncio.run(self.mode_processor.process_input(initial_input, current_mode))
        
        # Add Socratic question if needed
        combined_response = self._add_socratic_question_if_needed(response)
        
        # Add routing metadata if available
        final_message = self._add_routing_metadata(combined_response)
        
        # Append assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_message,
            "timestamp": datetime.now().isoformat(),
            "mentor_type": current_mode
        })
    
    def _render_chat_interface(self):
        """Render the chat interface."""
        with st.columns([0.5, 3, 0.5])[1]:  # Wider center column for chat
            # Optional: show pre-test above the chat when enabled via sidebar
            if st.session_state.get("show_pre_test", False):
                self._render_pretest_block()

            # Display chat messages in modern interface
            render_chat_interface()
            
            # Chat input
            user_input = get_chat_input()
            
            if user_input:
                self._handle_chat_input(user_input)
    
    def _handle_chat_input(self, user_input: str):
        """Handle new chat input from the user."""
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Log interaction
        self._log_user_interaction(user_input)
        
        # Display user message - no need to render separately as it's already in session state
        # The chat interface will automatically show all messages including the new one
        
        # Initialize phase system if needed
        self._initialize_phase_system()
        
        # Handle Socratic response if awaiting one
        if st.session_state.awaiting_socratic_response:
            self._handle_socratic_response(user_input)
        
        # Generate response
        self._generate_and_display_response(user_input)
        
        # Don't rerun - let the response display naturally
    
    def _generate_and_display_response(self, user_input: str):
        """Generate and display the AI response."""
        # Simple spinner without typing indicator to avoid conflicts
        
        with st.spinner("Thinking..."):
            try:
                # Process response based on current mode
                response = asyncio.run(
                    self.mode_processor.process_input(user_input, st.session_state.current_mode)
                )
                
                # Extract the actual response content from the response object
                st.write(f"DEBUG: Response type: {type(response)}")
                st.write(f"DEBUG: Response attributes: {dir(response) if hasattr(response, '__dict__') else 'No __dict__'}")
                
                if hasattr(response, 'content'):
                    response_content = response.content
                    st.write(f"DEBUG: Using response.content: {response_content[:100]}...")
                elif hasattr(response, 'response'):
                    response_content = response.response
                    st.write(f"DEBUG: Using response.response: {response_content[:100]}...")
                elif isinstance(response, str):
                    response_content = response
                    st.write(f"DEBUG: Response is string: {response_content[:100]}...")
                else:
                    # Try to convert to string
                    response_content = str(response)
                    st.write(f"DEBUG: Converted to string: {response_content[:100]}...")
                
                # Add Socratic question if needed
                combined_response = self._add_socratic_question_if_needed(response_content)
                
                # Add routing metadata if available
                final_message = self._add_routing_metadata(combined_response)
                
                # Add assistant message
                st.write(f"DEBUG: Final message length: {len(final_message)}")
                st.write(f"DEBUG: Final message preview: {final_message[:200]}...")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_message,
                    "timestamp": datetime.now().isoformat(),
                    "mentor_type": st.session_state.current_mode
                })
                
                st.write(f"DEBUG: Messages in session state: {len(st.session_state.messages)}")
                st.write(f"DEBUG: Last message: {st.session_state.messages[-1]}")
                
                # Force chat interface to update
                st.rerun()
                
                # Update data collector with response
                self._update_data_collector_response(response, user_input)
                # Minimal safe logging to satisfy logger signature
                try:
                    routing_meta = st.session_state.get("last_response_metadata", {}) or {}
                    agents_used = routing_meta.get("agents_used", []) or [st.session_state.get('current_mode','mentor')]
                    routing_path = routing_meta.get("routing_path", "mentor_mode")
                    cognitive_flags = routing_meta.get("cognitive_flags", [])
                    self.data_collector.log_interaction(
                        student_input=user_input,
                        agent_response=str(response)[:500],
                        routing_path=routing_path,
                        agents_used=agents_used,
                        response_type=st.session_state.get('current_mode','MENTOR').lower(),
                        cognitive_flags=cognitive_flags if isinstance(cognitive_flags, list) else [],
                        student_skill_level='intermediate',
                        confidence_score=0.6,
                        sources_used=routing_meta.get('sources', []),
                        response_time=1.0,
                        context_classification=routing_meta.get('classification', {}),
                        metadata=routing_meta
                    )
                except Exception:
                    pass
                
            except Exception as e:
                error_response = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_response,
                    "timestamp": datetime.now().isoformat(),
                    "mentor_type": st.session_state.current_mode
                })
    
    def _add_socratic_question_if_needed(self, response: str) -> str:
        """Add Socratic question to response if needed."""
        if not st.session_state.awaiting_socratic_response:
            next_question = self.phase_system.get_next_question(st.session_state.phase_session_id)
            if next_question and not response_contains_questions(response):
                st.session_state.awaiting_socratic_response = True
                st.session_state.current_question_id = next_question.question_id
                return f"{response}\n\n{next_question.question_text}"
        return response
    
    def _add_routing_metadata(self, response: str) -> str:
        """Add routing metadata to response if enabled."""
        response_metadata = st.session_state.get("last_response_metadata", {})
        routing_path = response_metadata.get("routing_path") or response_metadata.get("route")
        agents_used = response_metadata.get("agents_used") or []
        interaction_type = response_metadata.get("interaction_type") or response_metadata.get("user_intent")
        response_type = response_metadata.get("response_type")

        if (routing_path or agents_used) and st.session_state.get('show_routing_meta', False):
            parts = []

            # Add interaction type if available
            if interaction_type:
                parts.append(f"Intent: {interaction_type}")

            # Add route
            parts.append(f"Route: {routing_path or 'unknown'}")

            # Add agents if available
            if agents_used:
                used = ", ".join(agents_used)
                parts.append(f"Agents: {used}")

            # Add response type if available
            if response_type:
                parts.append(f"Type: {response_type}")

            meta_suffix = f"\n\n— {' | '.join(parts)}"
            return response + meta_suffix
        return response
    
    def _handle_socratic_response(self, user_input: str):
        """Handle Socratic dialogue response."""
        phase_result = self.phase_system.process_response(st.session_state.phase_session_id, user_input)
        st.session_state.awaiting_socratic_response = False
        st.session_state.current_question_id = None
        
        if "error" not in phase_result:
            grade = phase_result["grade"]
            st.caption(f"Phase {phase_result['current_phase'].title()} | Score {grade['overall_score']:.1f}/5")
    
    def _log_user_interaction(self, user_input: str):
        """Log user interaction for data collection."""
        try:
            response_metadata = st.session_state.get("last_response_metadata", {})
            self.data_collector.log_interaction(
                student_input=user_input,
                agent_response="Processing...",
                routing_path=response_metadata.get("routing_path", "mentor_mode"),
                agents_used=response_metadata.get("agents_used", ["orchestrator"]),
                response_type="mentor_response",
                cognitive_flags=response_metadata.get("cognitive_flags", []),
                student_skill_level="intermediate",
                confidence_score=0.8,
                sources_used=response_metadata.get("sources", []),
                response_time=1.0,
                context_classification={
                    "understanding_level": "medium",
                    "confidence_level": "medium", 
                    "engagement_level": "high"
                },
                metadata={
                    "mode": st.session_state.current_mode,
                    "phase_analysis": {"phase": "ideation", "confidence": 0.8},
                    "scientific_metrics": {
                        "cognitive_offloading_prevention": 0.8,
                        "deep_thinking_encouragement": 0.9,
                        "knowledge_integration": 0.7,
                        "scaffolding_effectiveness": 0.8
                    },
                    "cognitive_state": {
                        "engagement": "high",
                        "confidence": "medium",
                        "understanding": "medium"
                    }
                }
            )
        except Exception as e:
            st.warning(f"Data logging error: {e}")
    
    def _update_data_collector_response(self, response: str, user_input: str):
        """Update data collector with the AI response."""
        try:
            if self.data_collector.interactions:
                # Update the last interaction's agent_response
                self.data_collector.interactions[-1]["agent_response"] = response
                
                # Update checklist via phase system
                try:
                    delta = self.phase_system.update_checklist_from_interaction(
                        st.session_state.phase_session_id, user_input, response
                    )
                    if isinstance(delta, dict):
                        response_metadata = st.session_state.get("last_response_metadata", {}) or {}
                        response_metadata["checklist_delta"] = delta.get("checklist_delta", [])
                        st.session_state.last_response_metadata = response_metadata
                except Exception:
                    pass
        except Exception as e:
            st.warning(f"Response logging error: {e}")
    
    def _render_pretest_block(self):
        """Render the pre-test assessment block in the main area (above chat)."""
        try:
            from thesis_tests.assessment_tools import PreTestAssessment

            if "pre_test_component" not in st.session_state:
                st.session_state.pre_test_component = PreTestAssessment()

            st.markdown("---")
            st.markdown(
                """
                <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 10px; text-align: center;">
                    🧪 Pre-Test Assessment
                </div>
                """,
                unsafe_allow_html=True,
            )

            comp = st.session_state.pre_test_component
            comp.render_critical_thinking_questions()
            comp.render_architectural_knowledge_questions()
            comp.render_spatial_reasoning_questions()

            if st.button("Save Pre-Test Responses", key="save_pretest_main"):
                st.success("Pre-test responses saved for this session.")

            st.markdown("---")

        except Exception:
            # If pre-test tools are not available, silently skip in main content
            pass

    def _render_phase_insights(self):
        """Render phase progression and learning insights."""
        with st.columns([1, 2, 1])[1]:  # Center column
            st.markdown("---")
            st.markdown("""
            <div class="compact-text" style="font-size: 12px; font-weight: bold; margin-bottom: 10px; text-align: center; color: var(--primary-purple);">
                🎯 Phase Progression & Learning Insights
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # Create session data from chat messages
                chat_interactions = self._create_chat_interactions_data()
                
                # Prefer engine-driven progress for display
                engine_phase = None
                engine_percent = 0.0
                try:
                    summary = self.phase_system.get_session_summary(st.session_state.phase_session_id)
                    engine_phase = summary.get('current_phase')
                    phase_summaries = summary.get('phase_summaries', {})
                    if engine_phase in phase_summaries:
                        engine_percent = phase_summaries[engine_phase].get('completion_percent', 0.0)
                except Exception:
                    pass

                # Fallback lightweight phase guess (percent shown only if engine unavailable)
                current_phase, heuristic_progress = self.phase_analyzer.calculate_conversation_progress(chat_interactions)
                phase_progress = engine_percent if engine_phase else heuristic_progress
                if engine_phase:
                    current_phase = engine_phase
                
                # Display phase progression
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Current Design Phase**")
                    st.info(f"**{current_phase}** - {phase_progress:.0f}% Complete")
                    
                    # Phase indicators
                    phases = ['ideation', 'visualization', 'materialization']
                    current_phase_idx = phases.index(current_phase) if current_phase in phases else 0
                    
                    for i, phase in enumerate(phases):
                        if i <= current_phase_idx:
                            st.markdown(f"✅ {phase}")
                        else:
                            st.markdown(f"⏳ {phase}")
                
                with col2:
                    # Analyze and display challenges and learning points (qualitative)
                    analysis = self.phase_analyzer.analyze_phase_progression(chat_interactions)
                    
                    st.markdown("**🎯 Key Challenges Identified**")
                    for challenge in analysis['challenges']:
                        st.markdown(f"• {challenge}")
                    
                    st.markdown("**💡 Learning Points**")
                    for point in analysis['learning_points']:
                        st.markdown(f"• {point}")
                
                # Session summary
                st.markdown("---")
                st.markdown("**📊 Session Summary**")
                total_interactions = len(chat_interactions)
                
                summary_col1, summary_col2, summary_col3 = st.columns(3)
                with summary_col1:
                    st.metric("Interactions", total_interactions)
                with summary_col2:
                    st.metric("Phase Progress", f"{phase_progress:.0f}%")
                with summary_col3:
                    st.metric("Session Status", "Ongoing")
                
            except Exception as e:
                st.error(f"Error analyzing progression: {str(e)}")
    
    def _render_analysis_results(self):
        """Render comprehensive analysis results."""
        if not st.session_state.analysis_results:
            return
        
        # Ensure analysis results are in dictionary format
        analysis_results = st.session_state.analysis_results
        if hasattr(analysis_results, 'response_text'):
            # Import the conversion function
            from .ui.analysis_components import convert_agent_response_to_dict
            analysis_results = convert_agent_response_to_dict(analysis_results)
        
        # Inject engine-driven phase status for UI components that consume it
        try:
            summary = self.phase_system.get_session_summary(st.session_state.phase_session_id)
            current_phase = summary.get('current_phase')
            phase_summaries = summary.get('phase_summaries', {})
            completion_percent = 0.0
            completed_phases = sum(1 for p in phase_summaries.values() if p.get('completed'))
            total_phases = len(phase_summaries) if phase_summaries else 3
            if current_phase in phase_summaries:
                completion_percent = phase_summaries[current_phase].get('completion_percent', 0.0)
            analysis_results['phase_engine_status'] = {
                'current_phase': current_phase,
                'completion_percent': completion_percent,
                'completed_phases': completed_phases,
                'total_phases': total_phases,
                # Optional confidence; not computed here
                'phase_confidence': 0.0,
            }
        except Exception:
            pass
            
        with st.columns([1, 2, 1])[1]:  # Center column
            st.markdown("---")
            st.markdown("""
            <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                📊 Analysis Results
            </div>
            """, unsafe_allow_html=True)
            
            # Render cognitive analysis dashboard
            render_cognitive_analysis_dashboard(analysis_results)
            
            # Render metrics summary
            render_metrics_summary(analysis_results)
            
            # Design brief and image display
            col_brief, col_image = st.columns([2, 1])
            
            with col_brief:
                # Get the project description from session or analysis
                brief = "Architectural project analysis"
                if st.session_state.messages and len(st.session_state.messages) > 0:
                    brief = st.session_state.messages[0].get("content", brief)
                st.markdown(f"**Design Brief:** {brief}")
            
            with col_image:
                if st.session_state.uploaded_image_path and st.session_state.input_mode in ["Image + Text", "Image Only"]:
                    st.image(st.session_state.uploaded_image_path, caption="Your Design", use_container_width=True)
                elif st.session_state.input_mode == "Text Only":
                    st.info("📝 **Text-Only Analysis**: No image uploaded for this session")
            
            # Render phase progress section
            render_phase_progress_section(analysis_results)
    
    def _create_chat_interactions_data(self):
        """Create chat interactions data for analysis."""
        chat_interactions = []
        for i in range(0, len(st.session_state.messages), 2):
            if i + 1 < len(st.session_state.messages):
                user_msg = st.session_state.messages[i]
                assistant_msg = st.session_state.messages[i + 1]
                if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                    chat_interactions.append({
                        "data": {
                            "input": user_msg["content"],
                            "response": assistant_msg["content"],
                            "mode": st.session_state.get('current_mode', 'MENTOR')
                        }
                    })
        return chat_interactions


def main():
    """Main function to run the dashboard."""
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()


if __name__ == "__main__":
    main() 