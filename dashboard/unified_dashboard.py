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
from .ui.phase_circles import render_phase_circles, render_phase_metrics
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

        # ENHANCED: Add gamification progress to sidebar
        try:
            from dashboard.ui.gamification_components import render_gamification_sidebar
            render_gamification_sidebar()
        except Exception as e:
            print(f"⚠️ Error rendering gamification sidebar: {e}")

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
            # ENHANCED: Use more unique session ID with microseconds to prevent conflicts
            import uuid
            unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
            st.session_state.phase_session_id = f"phase_session_{timestamp}_{unique_id}"
            print(f"🔧 DASHBOARD: Creating new phase session: {st.session_state.phase_session_id}")
            self.phase_system.start_session(st.session_state.phase_session_id)
        else:
            print(f"🔧 DASHBOARD: Using existing phase session: {st.session_state.phase_session_id}")
            # ENHANCED: Verify session exists in phase system
            if st.session_state.phase_session_id not in self.phase_system.sessions:
                print(f"⚠️ DASHBOARD: Session not found in phase system, recreating...")
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

            # PHASE QUESTION DISPLAY: Show current phase question if available
            self._render_current_phase_question()

            # Chat input
            user_input = get_chat_input()
            
            if user_input:
                self._handle_chat_input(user_input)

    def _render_current_phase_question(self):
        """Render the current phase question if available."""
        try:
            if hasattr(self, 'phase_integration') and self.phase_integration:
                current_question = self.phase_integration.get_current_question()

                if current_question:
                    # Display the current phase question in a highlighted box
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f8ff;
                        border-left: 4px solid #4CAF50;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                    ">
                        <h4 style="color: #2E7D32; margin-top: 0;">
                            🎯 Current Phase Question ({current_question['phase'].title()})
                        </h4>
                        <p style="margin-bottom: 0; font-size: 1.1em;">
                            {current_question['text']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show keywords as hints
                    if current_question.get('keywords'):
                        keywords_text = ", ".join(current_question['keywords'])
                        st.markdown(f"💡 *Consider these aspects: {keywords_text}*")

                    print(f"🎯 UI: Displayed phase question: {current_question['text'][:50]}...")
                else:
                    print(f"🎯 UI: No current phase question available")

        except Exception as e:
            print(f"⚠️ UI: Error displaying phase question: {e}")

    def _handle_chat_input(self, user_input: str):
        """Handle new chat input from the user."""
        print(f"\n🎯 DASHBOARD: _handle_chat_input called with: {user_input[:50]}...")

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
        print(f"🔧 DASHBOARD: Initializing phase system...")
        self._initialize_phase_system()

        # Process ALL user responses through phase system (not just Socratic ones)
        print(f"🎯 DASHBOARD: Processing user response for phases...")
        self._process_user_response_for_phases(user_input)

        # Handle Socratic response if awaiting one
        if st.session_state.awaiting_socratic_response:
            self._handle_socratic_response(user_input)

        # Generate response
        self._generate_and_display_response(user_input)
        
        # Don't rerun - let the response display naturally

    def _process_user_response_for_phases(self, user_input: str):
        """Process user response through the phase progression system."""
        try:
            print(f"\n🎯 DASHBOARD: Processing user response for phase progression")
            print(f"📝 Input: {user_input[:100]}...")

            # Process the response through the phase system
            phase_result = self.phase_system.process_response(st.session_state.phase_session_id, user_input)

            if "error" in phase_result:
                print(f"❌ PHASE ERROR: {phase_result['error']}")
                return

            # Log the phase progression results
            print(f"✅ PHASE PROCESSING COMPLETE:")
            print(f"   Current Phase: {phase_result['current_phase']}")
            print(f"   Grade: {phase_result['grade']['overall_score']:.2f}/5.0")
            print(f"   Phase Complete: {phase_result['phase_complete']}")
            print(f"   Session Complete: {phase_result['session_complete']}")

            # Store phase result for UI display
            st.session_state.last_phase_result = phase_result

            # Display nudge if available
            if phase_result.get('nudge'):
                st.info(f"💡 **Phase Guidance**: {phase_result['nudge']}")

            # Handle phase transitions
            if phase_result.get('phase_transition'):
                st.success(f"🎉 **Phase Transition**: {phase_result.get('transition_message', 'Moving to next phase!')}")
                # Force a rerun to update the phase circles
                st.rerun()

        except Exception as e:
            print(f"❌ PHASE PROCESSING ERROR: {e}")
            import traceback
            traceback.print_exc()

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
                if hasattr(response, 'content'):
                    response_content = response.content
                elif hasattr(response, 'response'):
                    response_content = response.response
                elif isinstance(response, str):
                    response_content = response
                else:
                    # Try to convert to string
                    response_content = str(response)

                # Add Socratic question if needed
                combined_response = self._add_socratic_question_if_needed(response_content)

                # Add routing metadata if available
                final_message = self._add_routing_metadata(combined_response)

                # ENHANCED: Check if this is a gamified response
                response_metadata = st.session_state.get("last_response_metadata", {})
                gamification_display = response_metadata.get("gamification_display", {})

                # Add assistant message with gamification info
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_message,
                    "timestamp": datetime.now().isoformat(),
                    "mentor_type": st.session_state.current_mode,
                    "gamification": gamification_display
                })
                
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
        print(f"\n🤔 SOCRATIC: Checking if question needed...")
        print(f"   Session ID: {st.session_state.phase_session_id}")
        print(f"   Awaiting response: {st.session_state.get('awaiting_socratic_response', False)}")

        # ENHANCED: Verify phase system state before getting question
        session = self.phase_system.sessions.get(st.session_state.phase_session_id)
        if session:
            print(f"   Current phase in session: {session.current_phase.value}")
            current_progress = session.phase_progress.get(session.current_phase)
            if current_progress:
                print(f"   Phase progress steps: {len(current_progress.completed_steps)}")
                print(f"   Phase completion: {current_progress.completion_percent:.1f}%")
            else:
                print(f"   ⚠️ No progress found for current phase: {session.current_phase.value}")
        else:
            print(f"   ❌ No session found for ID: {st.session_state.phase_session_id}")

        # # Check if this was a knowledge_only route (example requests should not get questions)
        # routing_path = st.session_state.get('routing_path', '')
        # print(f"   Last routing path: {routing_path}")

        # # Don't add questions for knowledge_only routes (example requests)
        # if routing_path == 'knowledge_only':
        #     print(f"   🚫 Skipping Socratic question for knowledge_only route")
        #     return response

        # Always try to get next question if not already awaiting response
        if not st.session_state.get('awaiting_socratic_response', False):
            next_question = self.phase_system.get_next_question(st.session_state.phase_session_id)
            print(f"   Next question available: {next_question is not None}")

            if next_question:
                print(f"   Question phase: {next_question.phase.value}")
                print(f"   Question step: {next_question.step.value}")
                print(f"   Question: {next_question.question_text[:80]}...")
                if not response_contains_questions(response):
                    st.session_state.awaiting_socratic_response = True
                    st.session_state.current_question_id = next_question.question_id
                    enhanced_response = f"{response}\n\n**🤔 Let me ask you this to help develop your thinking:**\n\n{next_question.question_text}"
                    print(f"   ✅ Added Socratic question to response")
                    return enhanced_response
                else:
                    print(f"   ⏭️ Response already contains questions, skipping")
            else:
                print(f"   ℹ️ No next question available")
        else:
            print(f"   ⏳ Already awaiting Socratic response")

        return response
    
    def _add_routing_metadata(self, response: str) -> str:
        """Add routing metadata to response if enabled."""
        response_metadata = st.session_state.get("last_response_metadata", {})
        routing_path = response_metadata.get("routing_path") or response_metadata.get("route")
        agents_used = response_metadata.get("agents_used") or []
        interaction_type = response_metadata.get("interaction_type") or response_metadata.get("user_intent")
        response_type = response_metadata.get("response_type")

        # Extract gamification info if available
        gamification_info = response_metadata.get("gamification", {})
        gamification_trigger = gamification_info.get("trigger_type", "")
        gamification_enhancement = gamification_info.get("enhancement_applied", False)

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

            # Add gamification info if available
            if gamification_enhancement and gamification_trigger:
                parts.append(f"🎮 Gamified: {gamification_trigger}")
            elif gamification_trigger:
                parts.append(f"🎯 Trigger: {gamification_trigger}")

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
        """Render only the phase circles."""
        # Display phase progression with circles - no extra wrapper columns needed
        render_phase_circles(self.phase_system, st.session_state.phase_session_id)
    
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