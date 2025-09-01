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
import sys

from dashboard.config.settings import PAGE_CONFIG, TEMPLATE_PROMPTS, TESTING_MODES, SKILL_LEVELS, MENTOR_TYPES, get_api_key
from dashboard.ui.styles import apply_dashboard_styles
from dashboard.core.session_manager import initialize_session_state, ensure_session_started
from dashboard.ui.chat_components import (
    render_welcome_section, render_mode_configuration, render_chat_history,
    get_chat_input, render_chat_message, response_contains_questions,
    render_mentor_type_selection, render_template_selection,
    render_skill_level_selection, render_project_description_input, validate_input,
    render_chat_interface
)
from dashboard.ui.sidebar_components import render_complete_sidebar
from dashboard.ui.analysis_components import render_cognitive_analysis_dashboard, render_metrics_summary, render_phase_progress_section
from dashboard.ui.phase_circles import render_phase_circles, render_phase_metrics
from dashboard.ui.manual_phase_controls import render_manual_phase_controls, render_phase_completion_indicator, should_show_manual_controls
from dashboard.processors.mode_processors import ModeProcessor
from dashboard.processors.dynamic_task_manager import DynamicTaskManager
from dashboard.analysis.phase_analyzer import PhaseAnalyzer
from dashboard.core.image_database import ImageDatabase

# Import external dependencies
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase_progression_system import PhaseProgressionSystem
from thesis_tests.test_dashboard import TestDashboard
from thesis_tests.data_models import InteractionData, TestPhase, TestGroup

# Test mode components now integrated into sidebar_components.py


# Page config moved to mentor.py to avoid multiple calls

# Cached resources
@st.cache_resource
def get_cached_task_manager():
    """Get cached task manager instance."""
    return DynamicTaskManager()

@st.cache_resource
def get_cached_orchestrator():
    """Get cached orchestrator instance."""
    import sys
    import os

    # Set environment variable to prevent GUI dependencies
    os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    # Add thesis-agents to path
    thesis_agents_path = os.path.join(os.path.dirname(__file__), '../thesis-agents')
    if thesis_agents_path not in sys.path:
        sys.path.insert(0, thesis_agents_path)

    try:
        from orchestration.orchestrator import LangGraphOrchestrator
        orchestrator = LangGraphOrchestrator(domain="architecture")
        print(f"✅ DASHBOARD: LangGraphOrchestrator initialized successfully")
        return orchestrator
    except ImportError as e:
        print(f"❌ DASHBOARD: LangGraphOrchestrator import failed: {e}")
        st.warning(f"LangGraphOrchestrator not available: {e}")
        st.info("Running in fallback mode without multi-agent orchestration.")
        return None
    except Exception as e:
        print(f"❌ DASHBOARD: LangGraphOrchestrator initialization failed: {e}")
        st.warning(f"Failed to initialize LangGraphOrchestrator: {e}")
        st.info("Running in fallback mode without multi-agent orchestration.")
        return None


# Removed: get_cached_mentor - functionality integrated into dashboard


@st.cache_resource
def get_cached_phase_system():
    """Get cached phase system instance - v2.0 with improved completion calculation."""
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

        # Image database
        self.image_database = ImageDatabase()
        
        # Data collector: store once in session with enhanced test integration
        if 'data_collector' not in st.session_state:
            # Import InteractionLogger from the correct location
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../thesis-agents'))
            from data_collection.interaction_logger import InteractionLogger

            # Get test group and participant info from session state
            test_group = st.session_state.get('test_group', 'MENTOR')
            if hasattr(test_group, 'value'):
                test_group = test_group.value
            participant_id = st.session_state.get('participant_id', 'unified_user')
            session_id = st.session_state.get('session_id', 'unified_dashboard_session')

            st.session_state.data_collector = InteractionLogger(
                session_id=session_id,
                test_group=test_group,
                participant_id=participant_id
            )
        self.data_collector = st.session_state.data_collector
        
        # Test dashboard lazy load (spacy heavy)
        if 'test_dashboard' not in st.session_state:
            st.session_state.test_dashboard = None
        self.test_dashboard = st.session_state.test_dashboard
        
        # Mode processor - CRITICAL FIX: Persist mode processor to maintain task manager state
        if 'mode_processor' not in st.session_state or st.session_state.mode_processor is None:
            print(f"🔍 DASHBOARD_DEBUG: Creating new mode processor instance")
            self.mode_processor = ModeProcessor(
                orchestrator=self.orchestrator,
                data_collector=self.data_collector,
                test_dashboard=self.test_dashboard,
                image_database=self.image_database
            )
            # Store mode processor in session state for persistence
            st.session_state.mode_processor = self.mode_processor
        else:
            print(f"🔍 DASHBOARD_DEBUG: Using existing mode processor from session state")
            self.mode_processor = st.session_state.mode_processor

            # CRITICAL FIX: Ensure task manager consistency across all components
            if hasattr(self.mode_processor, 'task_manager') and self.mode_processor.task_manager:
                session_task_manager = st.session_state.get('task_manager_instance')
                if session_task_manager and self.mode_processor.task_manager != session_task_manager:
                    print(f"🚨 DASHBOARD_SYNC: Syncing mode processor to session task manager")
                    print(f"🚨 DASHBOARD_SYNC: Mode processor: {id(self.mode_processor.task_manager)}")
                    print(f"🚨 DASHBOARD_SYNC: Session state: {id(session_task_manager)}")
                    self.mode_processor.task_manager = session_task_manager

            # Update references in case they changed
            self.mode_processor.orchestrator = self.orchestrator
            self.mode_processor.data_collector = self.data_collector
            self.mode_processor.test_dashboard = self.test_dashboard
            self.mode_processor.image_database = self.image_database
    
    def run(self):
        """Main run method for the dashboard."""
        # Render sidebar
        render_complete_sidebar(self.data_collector)

        # Test mode components now integrated into sidebar

        # ENHANCED: Add gamification progress to sidebar (simplified for test mode)
        try:
            from dashboard.ui.gamification_components import render_gamification_sidebar
            render_gamification_sidebar()
            # Note: Advanced gamification dashboard removed for test mode focus

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

        # Check dashboard mode from sidebar
        dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

        if dashboard_mode == "Test Mode":
            # Test mode: Fixed community center challenge, no templates
            mentor_type = st.session_state.get('mentor_type', 'Socratic Agent')
            skill_level = "Intermediate"  # Fixed for research consistency

            # Project description input with fixed challenge (no templates)
            project_description, uploaded_file = render_project_description_input("")

        else:  # Flexible Mode
            # Original mentor.py functionality with templates
            mentor_type = render_mentor_type_selection()
            st.session_state.mentor_type = mentor_type
            st.session_state.current_mode = mentor_type

            # Template prompts (only in flexible mode)
            selected_template = render_template_selection()

            # Skill level selection (flexible in flexible mode)
            skill_level = render_skill_level_selection()

            # Project description input with template support
            template_text = TEMPLATE_PROMPTS.get(selected_template, "")
            project_description, uploaded_file = render_project_description_input(template_text)
        
        # Start analysis button (centered, no form rectangle)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            start_clicked = st.button("Start Analysis", use_container_width=True, type="primary")
        
        if start_clicked:
            # Validate input
            is_valid, error_msg = validate_input(project_description, uploaded_file)
            if not is_valid:
                st.error(error_msg)
            else:
                self._handle_start_analysis(project_description, uploaded_file, skill_level, mentor_type)
        
        # REAL APP TASK UI TEST - TEMPORARILY DISABLED
        if False and st.session_state.get("show_task_ui_test", False):
            print("🔧 TASK_UI_TEST: Test interface is being rendered")
            st.markdown("# 🔧 REAL APP TASK UI TEST")
            st.markdown("Testing all 8 tasks UI rendering in actual Streamlit application context")

            try:
                # Import and run the test directly here to avoid import issues
                from dashboard.processors.dynamic_task_manager import TaskType, DynamicTaskManager
                from dashboard.processors.task_guidance_system import TaskGuidanceSystem
                from dashboard.ui.chat_components import _render_single_task_component
                from thesis_tests.data_models import TestGroup
                from datetime import datetime

                st.success("✅ Successfully imported real application components")

                # Initialize guidance system (same as the real app)
                if 'guidance_system' not in st.session_state:
                    st.session_state['guidance_system'] = TaskGuidanceSystem()

                guidance_system = st.session_state['guidance_system']
                st.success("✅ Guidance system initialized from session state")

                # Initialize task manager (same as real app)
                if 'task_manager' not in st.session_state:
                    st.session_state['task_manager'] = DynamicTaskManager()

                task_manager = st.session_state['task_manager']
                st.success("✅ Task manager initialized from session state")

                # Test REAL phase transition scenarios with actual thresholds
                phase_scenarios = [
                    # Ideation phase tasks
                    {"phase": "ideation", "completion": 5.0, "expected_tasks": ["architectural_concept"]},
                    {"phase": "ideation", "completion": 35.0, "expected_tasks": ["spatial_program"]},

                    # Visualization phase tasks
                    {"phase": "visualization", "completion": 5.0, "expected_tasks": ["visual_analysis_2d"]},
                    {"phase": "visualization", "completion": 45.0, "expected_tasks": ["environmental_contextual"]},

                    # Materialization phase tasks
                    {"phase": "materialization", "completion": 5.0, "expected_tasks": ["spatial_analysis_3d"]},
                    {"phase": "materialization", "completion": 45.0, "expected_tasks": ["realization_implementation"]},
                    {"phase": "materialization", "completion": 55.0, "expected_tasks": ["design_evolution"]},
                    {"phase": "materialization", "completion": 65.0, "expected_tasks": ["knowledge_transfer"]},
                ]

                st.markdown(f"## Testing Real Phase Transition Scenarios")

                results = []
                for i, scenario in enumerate(phase_scenarios):
                    phase = scenario["phase"]
                    completion = scenario["completion"]
                    expected_tasks = scenario["expected_tasks"]

                    st.markdown(f"### Scenario {i+1}: {phase.title()} Phase at {completion}% completion")

                    try:
                        # Simulate real phase progression (same as actual app)
                        st.session_state['test_current_phase'] = phase.title()

                        # Create mock conversation history
                        mock_conversation = [
                            {"role": "user", "content": f"I'm working on {phase} phase"},
                            {"role": "assistant", "content": f"Great! Let's explore {phase} concepts."}
                        ]

                        # Test threshold crossing detection (real system)
                        triggered_tasks = task_manager._detect_threshold_crossings(
                            current_phase=phase,
                            last_completion=completion - 10.0,  # Previous completion
                            current_completion=completion,      # Current completion
                            user_input=f"Phase {phase} at {completion}%",
                            conversation_history=mock_conversation,
                            test_group="MENTOR",
                            image_uploaded=False,
                            image_analysis=None
                        )

                        st.write(f"🎯 Triggered tasks: {[t.value for t in triggered_tasks]}")
                        st.write(f"🎯 Expected tasks: {expected_tasks}")

                        # Check if expected tasks were triggered
                        triggered_task_names = [t.value for t in triggered_tasks]
                        scenario_success = all(task in triggered_task_names for task in expected_tasks)

                        if scenario_success:
                            st.success(f"✅ Correct tasks triggered for {phase} at {completion}%")

                            # Test ACTUAL UI RENDERING for triggered tasks
                            for task_type in triggered_tasks:
                                if task_type.value in expected_tasks:
                                    # Get active task from task manager
                                    active_tasks = task_manager.get_active_tasks()
                                    active_task = next((t for t in active_tasks if t.task_type == task_type), None)

                                    if active_task:
                                        st.write(f"   🎨 Testing VISIBLE UI for {task_type.value}")

                                        # Test task data lookup (the actual issue from terminal)
                                        task_data = guidance_system.mentor_tasks.get(task_type, {})
                                        if task_data:
                                            st.success(f"   ✅ Task data found for {task_type.value}")

                                            # NOW TEST ACTUAL UI RENDERING (what user sees)
                                            try:
                                                st.write(f"   🖼️ Rendering actual UI component...")

                                                # Create task entry (same as real app)
                                                task_entry = {
                                                    'task': active_task,
                                                    'task_id': f"test_{task_type.value}_{i}",
                                                    'guidance_type': 'socratic',
                                                    'should_render': True,
                                                    'message_index': i,
                                                    'displayed': False
                                                }

                                                # Render the ACTUAL UI component (same function as real app)
                                                with st.container():
                                                    st.markdown(f"**🎯 TASK UI COMPONENT FOR {task_type.value.upper()}:**")
                                                    _render_single_task_component(task_entry)

                                                st.success(f"   ✅ UI component VISIBLE for {task_type.value}")

                                            except Exception as ui_error:
                                                st.error(f"   ❌ UI rendering FAILED for {task_type.value}: {ui_error}")
                                                scenario_success = False
                                        else:
                                            st.error(f"   ❌ No task data found for {task_type.value}")
                                            scenario_success = False

                            results.append({'scenario': f"{phase} {completion}%", 'success': scenario_success})
                        else:
                            st.error(f"❌ Wrong tasks triggered for {phase} at {completion}%")
                            results.append({'scenario': f"{phase} {completion}%", 'success': False})

                    except Exception as scenario_error:
                        st.error(f"❌ Scenario failed: {scenario_error}")
                        results.append({'scenario': f"{phase} {completion}%", 'success': False})

                # Summary
                successful = sum(1 for r in results if r['success'])
                st.markdown("---")
                st.markdown(f"## 📊 RESULTS: {successful}/{len(all_tasks)} tasks successful")

                if successful == len(all_tasks):
                    st.success("🎉 ALL 8 TASKS WORKING! Task UI system is fully functional!")
                    st.balloons()
                elif successful >= 6:
                    st.warning(f"⚠️ Most tasks working ({successful}/{len(all_tasks)})")
                else:
                    st.error(f"❌ Major issues: Only {successful}/{len(all_tasks)} tasks working")

            except Exception as e:
                st.error(f"❌ Test failed: {e}")
                st.exception(e)

            if st.button("❌ Close Test"):
                st.session_state['show_task_ui_test'] = False
                st.rerun()
            return

        # Chat interface (after analysis)
        if st.session_state.analysis_complete:
            self._render_chat_interface()

            # Phase progression insights
            if len(st.session_state.messages) > 0:
                self._render_phase_insights()
    
    def _handle_start_analysis(self, project_description: str, uploaded_file, skill_level: str, mentor_type: str):
        """Handle the start analysis process."""
        # Handle case where only image is provided
        if not project_description.strip() and uploaded_file:
            project_description = "Analyze this architectural drawing"
        elif not project_description.strip():
            project_description = "Please analyze my architectural project"
        
        with st.spinner("Analyzing your design..."):
            try:
                # Initialize session
                ensure_session_started()
                self.data_collector.session_id = st.session_state.session_id
                
                # Store image path if uploaded
                if uploaded_file:
                    import tempfile
                    from PIL import Image
                    image = Image.open(uploaded_file)

                    # Convert RGBA to RGB if necessary for JPEG format
                    if image.mode == 'RGBA':
                        # Create white background
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                        image = background
                    elif image.mode not in ['RGB', 'L']:
                        image = image.convert('RGB')

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        image.save(tmp_file.name, 'JPEG', quality=95)
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

            # Convert RGBA to RGB if necessary for JPEG format
            if image.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            elif image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                image.save(tmp_file.name, 'JPEG', quality=95)
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
        
        # Add Socratic question if needed (only for MENTOR mode)
        combined_response = self._add_socratic_question_if_needed(response, current_mode)
        
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

            # MANUAL PHASE CONTROLS: Show for GENERIC_AI and CONTROL modes
            self._render_manual_phase_controls()

            # FIXED: Check for game responses that need processing
            if st.session_state.get('should_process_message', False):
                # Get the last message (which should be the game response)
                if st.session_state.get('messages') and len(st.session_state.messages) > 0:
                    last_message = st.session_state.messages[-1]
                    if last_message.get('role') == 'user':
                        print(f"🎮 PROCESSING GAME RESPONSE: {last_message['content'][:50]}...")
                        # Process the game response through the normal chat pipeline
                        self._handle_chat_input(last_message['content'])
                        # Clear the flag
                        st.session_state.should_process_message = False

            # Chat input with seamless image upload
            user_input, uploaded_image = get_chat_input()

            if user_input:
                self._handle_chat_input(user_input, uploaded_image)
            elif uploaded_image:
                # Store image but don't process until user provides input
                self._store_uploaded_image(uploaded_image)

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

    def _render_manual_phase_controls(self):
        """Render manual phase controls for GENERIC_AI and CONTROL modes."""
        try:
            # Only show in Test Mode
            dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')
            if dashboard_mode != 'Test Mode':
                return

            # Get current test group
            test_group = st.session_state.get('test_group')
            if not test_group:
                return

            # Only show for GENERIC_AI and CONTROL modes
            if should_show_manual_controls(test_group):
                # Render phase completion indicator
                render_phase_completion_indicator(test_group)

                # Render manual phase controls
                render_manual_phase_controls(self.mode_processor, test_group)

        except Exception as e:
            print(f"⚠️ Error rendering manual phase controls: {e}")

    def _handle_chat_input(self, user_input: str, uploaded_image=None):
        """Handle new chat input from the user with optional image."""
        print(f"\n🎯 DASHBOARD: _handle_chat_input called with: {user_input[:50]}...")
        if uploaded_image:
            print(f"📷 DASHBOARD: Image uploaded: {uploaded_image.name}")

        # Process image if uploaded and extract comprehensive analysis
        enhanced_user_input = user_input
        image_path = None

        if uploaded_image:
            image_path = self._process_uploaded_image(uploaded_image)
            if image_path:
                # Check if this image was already processed to avoid redundant analysis
                if not self._is_image_already_processed(image_path):
                    # Extract comprehensive image analysis and bundle with text
                    enhanced_user_input = self._bundle_image_with_text(user_input, image_path, uploaded_image.name)
                    # Mark image as processed
                    self._mark_image_as_processed(image_path, uploaded_image.name)
                else:
                    print(f"⚡ DASHBOARD: Image already processed, using existing analysis")
                    # Get existing analysis from session state
                    enhanced_user_input = self._get_existing_image_analysis(user_input, image_path)

        # Check for pending images from previous uploads
        pending_images = st.session_state.get('pending_images', [])
        if pending_images and not uploaded_image:
            # Use the most recent pending image
            latest_image = pending_images[-1]
            image_path = latest_image['path']
            print(f"📷 DASHBOARD: Using pending image: {latest_image['filename']}")

            # Check if this image was already processed to avoid redundant analysis
            if not self._is_image_already_processed(image_path):
                # Check if we should bundle image analysis based on reference counter
                if self._should_bundle_image_analysis(image_path):
                    # Extract comprehensive image analysis and bundle with text
                    enhanced_user_input = self._bundle_image_with_text(user_input, image_path, latest_image['filename'])
                else:
                    print(f"🔄 DASHBOARD: Image reference limit reached, not bundling analysis")
                    enhanced_user_input = user_input
                # Mark image as processed
                self._mark_image_as_processed(image_path, latest_image['filename'])
            else:
                print(f"⚡ DASHBOARD: Image already processed, checking if should bundle")
                # Check if we should bundle existing analysis
                if self._should_bundle_image_analysis(image_path):
                    # Get existing analysis from session state
                    enhanced_user_input = self._get_existing_image_analysis(user_input, image_path)
                else:
                    print(f"🔄 DASHBOARD: Image reference limit reached, not bundling existing analysis")
                    enhanced_user_input = user_input

            # Clear pending images after use
            st.session_state.pending_images = []

        # Debug: Check what enhanced_user_input contains
        print(f"🔍 DASHBOARD: Enhanced user input length: {len(enhanced_user_input)} chars")
        print(f"🔍 DASHBOARD: Enhanced user input preview: {enhanced_user_input[:300]}...")
        has_enhanced = "[ENHANCED IMAGE ANALYSIS:" in enhanced_user_input
        has_uploaded = "[UPLOADED IMAGE ANALYSIS:" in enhanced_user_input
        print(f"🔍 DASHBOARD: Has ENHANCED marker: {has_enhanced}")
        print(f"🔍 DASHBOARD: Has UPLOADED marker: {has_uploaded}")

        # Add user message to chat history (display only the original user input, not the bundled analysis)
        user_message = {
            "role": "user",
            "content": user_input,  # Display only original user input to user
            "timestamp": datetime.now().isoformat(),
            "enhanced_content": enhanced_user_input  # Store enhanced content for system processing
        }

        st.session_state.messages.append(user_message)

        # Log interaction
        self._log_user_interaction(user_input)

        # Display user message - no need to render separately as it's already in session state
        # The chat interface will automatically show all messages including the new one

        # Initialize phase system if needed
        print(f"🔧 DASHBOARD: Initializing phase system...")
        self._initialize_phase_system()

        # Process ALL user responses through phase system (not just Socratic ones)
        print(f"🎯 DASHBOARD: Processing user response for phases...")
        phase_result = self._process_user_response_for_phases(user_input)

        # CRITICAL FIX: Store updated phase completion for task manager
        updated_phase_completion = 0.0
        if phase_result and 'phase_progress' in phase_result:
            phase_progress = phase_result['phase_progress']
            # CRITICAL FIX: phase_progress is a dict with completion_percent key
            if isinstance(phase_progress, dict):
                updated_phase_completion = phase_progress.get('completion_percent', 0.0)
                print(f"🎯 DASHBOARD: Found completion_percent in phase_progress dict: {updated_phase_completion:.1f}%")
            elif hasattr(phase_progress, 'completion_percent'):
                updated_phase_completion = phase_progress.completion_percent
                print(f"🎯 DASHBOARD: Found completion_percent in phase_progress object: {updated_phase_completion:.1f}%")
            st.session_state.current_phase_completion = updated_phase_completion
            print(f"🎯 DASHBOARD: Updated phase completion stored: {updated_phase_completion:.1f}%")

        # CRITICAL FIX: Check for task triggers with updated completion
        # IMPORTANT: Include 0% completion to catch phase transition tasks (like Task 2.1)
        if phase_result and updated_phase_completion >= 0:
            task_manager = get_cached_task_manager()
            current_phase = phase_result.get('current_phase', 'ideation')

            print(f"🎯 DASHBOARD: Checking task triggers at {updated_phase_completion:.1f}% in {current_phase} phase")

            triggered_task = task_manager.check_task_triggers(
                user_input=user_input,
                conversation_history=st.session_state.messages,
                current_phase=current_phase,
                test_group=st.session_state.get('test_group', 'MENTOR'),
                image_uploaded=False,
                image_analysis=None,
                phase_completion_percent=updated_phase_completion
            )

            if triggered_task:
                task_name = triggered_task.value if hasattr(triggered_task, 'value') else str(triggered_task)
                print(f"🎯 DASHBOARD: Task triggered: {task_name}")

                # Store triggered task for UI display
                st.session_state.triggered_task = {
                    'task_name': task_name,
                    'task_type': triggered_task,
                    'completion_percent': updated_phase_completion,
                    'phase': current_phase,
                    'triggered_at': datetime.now().isoformat()
                }

                # Display task message immediately
                from dashboard.processors.dynamic_task_manager import TaskType
                task_type_enum = None
                for task_enum in TaskType:
                    if task_enum.value == task_name:
                        task_type_enum = task_enum
                        break

                task_config = task_manager.task_triggers.get(task_type_enum, {}) if task_type_enum else {}

                # Create user-friendly task names and descriptions
                task_display_names = {
                    'architectural_concept': 'Architectural Concept Development',
                    'spatial_program': 'Spatial Program Development',
                    'visual_conceptualization': 'Visual Conceptualization',
                    'visual_analysis_2d': '2D Visual Analysis',
                    'environmental_contextual': 'Environmental Context Analysis'
                }

                task_descriptions = {
                    'architectural_concept': 'Develop and refine your core architectural concepts and design approach.',
                    'spatial_program': 'Define and organize the spatial program and functional relationships.',
                    'visual_conceptualization': 'Create visual representations of your design concepts.',
                    'visual_analysis_2d': 'Analyze and develop 2D visual representations of your design.',
                    'environmental_contextual': 'Consider environmental and contextual factors in your design.'
                }

                display_name = task_display_names.get(task_name, task_name.replace('_', ' ').title())
                description = task_descriptions.get(task_name, f'Task {task_name} has been triggered.')

                # REMOVED: Task display messages - tasks now render as UI components
                # st.success(f"🎯 **New Task Available**: {display_name}")
                # st.info(f"📋 {description}")

                print(f"✅ DASHBOARD: Task {task_name} triggered (UI component will render separately)")
            else:
                print(f"🎯 DASHBOARD: No tasks triggered at {updated_phase_completion:.1f}%")

        # Handle Socratic response state management
        if st.session_state.awaiting_socratic_response:
            # Check if the phase processing handled the question response
            phase_result = st.session_state.get('last_phase_result', {})
            if phase_result.get('question_answered', False):
                print(f"✅ Question was answered, clearing awaiting state")
                st.session_state.awaiting_socratic_response = False
                st.session_state.current_question_id = None

        # Generate response (this will now handle phase transitions properly)
        # Get image path from the last message if present
        image_path = None
        if st.session_state.messages and "image_path" in st.session_state.messages[-1]:
            image_path = st.session_state.messages[-1]["image_path"]

        self._generate_and_display_response(user_input, image_path)

        # Check if we need to rerun after response generation (for phase transitions)
        if st.session_state.get('pending_rerun', False):
            st.session_state.pending_rerun = False
            st.rerun()

    def _process_uploaded_image(self, uploaded_file) -> str:
        """Process uploaded image and return the file path."""
        try:
            import tempfile
            from PIL import Image

            print(f"📷 Processing uploaded image: {uploaded_file.name}")

            # Open and process the image
            image = Image.open(uploaded_file)

            # Convert RGBA to RGB if necessary for JPEG format
            if image.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            elif image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                image.save(tmp_file.name, 'JPEG', quality=95)
                temp_path = tmp_file.name

            print(f"✅ Image saved to: {temp_path}")
            return temp_path

        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return None

    def _store_uploaded_image(self, uploaded_file):
        """Store uploaded image without processing it immediately."""
        try:
            # Process and save the image
            image_path = self._process_uploaded_image(uploaded_file)

            if image_path:
                # Store in session state for later use
                if 'pending_images' not in st.session_state:
                    st.session_state.pending_images = []

                st.session_state.pending_images.append({
                    'path': image_path,
                    'filename': uploaded_file.name,
                    'upload_time': datetime.now().isoformat()
                })

                # Update image upload tracking for reference limiting
                st.session_state.last_image_upload_message_count = len(st.session_state.messages)
                st.session_state.last_uploaded_image_path = image_path

                print(f"📷 Image stored for later processing: {uploaded_file.name}")
                return image_path

        except Exception as e:
            print(f"❌ Error storing image: {e}")
            return None

    def _bundle_image_with_text(self, user_input: str, image_path: str, image_filename: str) -> str:
        """Bundle comprehensive image analysis with user text as a unified message."""
        try:
            print(f"🔍 DASHBOARD: Bundling image analysis with text for: {image_filename}")

            # Get enhanced image analysis using comprehensive vision analyzer
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../thesis-agents'))
            from vision.comprehensive_vision_analyzer import ComprehensiveVisionAnalyzer

            # Initialize enhanced analyzer
            analyzer = ComprehensiveVisionAnalyzer(domain="architecture", use_cache=True)

            # Build comprehensive project context string
            current_phase = getattr(st.session_state, 'current_phase', 'unknown')
            building_type = getattr(st.session_state, 'project_type', 'unknown')
            conversation_summary = self._get_conversation_summary()
            project_description = getattr(st.session_state, 'project_description', user_input)

            project_context = f"Current Phase: {current_phase}, Building Type: {building_type}, Project: {project_description}, Context: {conversation_summary[:300]}"

            # Check if we already have this enhanced analysis cached in session state
            session_analyses = st.session_state.get('enhanced_image_analyses', [])
            for analysis in session_analyses:
                if analysis['path'] == image_path:
                    print(f"⚡ DASHBOARD: Using session-cached enhanced analysis for: {image_filename}")
                    cached_analysis = analysis['detailed_analysis']
                    contextual_response = analyzer.generate_contextual_response(cached_analysis, user_input)
                    bundled_message = f"{user_input}\n\n[ENHANCED IMAGE ANALYSIS: {contextual_response}]"
                    return bundled_message

            # Perform enhanced comprehensive image analysis
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Get enhanced comprehensive analysis with context
                enhanced_analysis = loop.run_until_complete(
                    analyzer.get_detailed_image_understanding(image_path, project_context)
                )

                # Generate contextual chat response
                contextual_response = analyzer.generate_contextual_response(enhanced_analysis, user_input)

                print(f"✅ DASHBOARD: Enhanced image analysis complete - Confidence: {enhanced_analysis.get('confidence_score', 0.7)}")

                # Bundle the text and enhanced image analysis as one unified message
                bundled_message = f"{user_input}\n\n[ENHANCED IMAGE ANALYSIS: {contextual_response}]"

                # Store in session state for potential future reference
                if 'enhanced_image_analyses' not in st.session_state:
                    st.session_state.enhanced_image_analyses = []
                st.session_state.enhanced_image_analyses.append({
                    "filename": image_filename,
                    "path": image_path,
                    "detailed_analysis": enhanced_analysis,
                    "project_context": project_context,
                    "timestamp": datetime.now().isoformat()
                })

                return bundled_message

            finally:
                loop.close()

        except Exception as e:
            print(f"⚠️ DASHBOARD: Enhanced image analysis failed, using contextual fallback: {e}")
            # Fallback to contextual message based on session state
            building_type = getattr(st.session_state, 'project_type', 'architectural project')
            current_phase = getattr(st.session_state, 'current_phase', 'design')
            fallback_response = f"I can see you've uploaded an architectural image for your {building_type}. While I had some difficulty with the detailed analysis, I can tell this appears to be related to your {current_phase} phase work. Let's discuss what you're working on and how I can help you develop this further."
            return f"{user_input}\n\n[IMAGE UPLOADED: {fallback_response}]"

    def _process_user_response_for_phases(self, user_input: str):
        """Process user response through the phase progression system."""
        try:
            print(f"\n🎯 DASHBOARD: Processing user message for phase progression")
            print(f"📝 Input: {user_input[:100]}...")

            # Use the new process_user_message method instead of process_response
            phase_result = self.phase_system.process_user_message(st.session_state.phase_session_id, user_input)

            if "error" in phase_result:
                print(f"❌ PHASE ERROR: {phase_result['error']}")
                return None

            # Log the phase progression results
            print(f"✅ PHASE PROCESSING COMPLETE:")
            print(f"   Current Phase: {phase_result['current_phase']}")

            # Only show grade if a question was actually answered
            if phase_result.get('question_answered', False) and 'grade' in phase_result:
                print(f"   Grade: {phase_result['grade']['overall_score']:.2f}/5.0")
                print(f"   Phase Complete: {phase_result['phase_complete']}")
                print(f"   Session Complete: {phase_result['session_complete']}")
            else:
                print(f"   Message processed (no grading - no active question)")

            # Store phase result for UI display
            st.session_state.last_phase_result = phase_result
            print(f"🎨 DEBUG: Stored phase_result in session_state with keys: {list(phase_result.keys())}")
            if phase_result.get('phase_transition'):
                print(f"🎨 DEBUG: Phase transition detected in phase processing")
                if 'generated_image' in phase_result:
                    print(f"🎨 DEBUG: Generated image present in phase_result: {bool(phase_result['generated_image'])}")
                else:
                    print(f"🎨 DEBUG: No generated_image in phase_result")

            # Display nudge if available
            if phase_result.get('nudge'):
                st.info(f"💡 **Phase Guidance**: {phase_result['nudge']}")

            # REMOVED: Duplicate phase transition display - this is now handled in _generate_and_display_response
            # to prevent double messages. Only handle task triggering here.
            if phase_result.get('phase_transition'):
                print(f"🔄 PHASE_TRANSITION_TASK_HANDLING: Phase transition detected, handling tasks only")

                # CRITICAL FIX: Handle task triggering during phase transitions
                previous_phase = phase_result.get('previous_phase', 'unknown')
                current_phase = phase_result.get('current_phase', 'unknown')

                print(f"🔄 PHASE_TRANSITION_DETECTED: {previous_phase} → {current_phase}")

                # Trigger phase transition task handling
                if hasattr(self.mode_processor, '_handle_phase_transition'):
                    test_group = st.session_state.get('test_group', 'MENTOR')
                    # Convert string to enum if needed
                    if isinstance(test_group, str):
                        from processors.mode_processors import TestGroup
                        test_group = TestGroup.MENTOR if test_group == 'MENTOR' else TestGroup.GENERIC_AI

                    self.mode_processor._handle_phase_transition(
                        from_phase=previous_phase.lower(),
                        to_phase=current_phase.lower(),
                        test_group=test_group,
                        user_input=f"Phase transition from {previous_phase} to {current_phase}"
                    )
                    print(f"🔄 PHASE_TRANSITION_HANDLED: Task triggering completed")
                else:
                    print(f"⚠️ PHASE_TRANSITION_WARNING: _handle_phase_transition method not available")

                # Save generated image if available (display will be handled in chat)
                generated_image = phase_result.get('generated_image')
                if generated_image:
                    # Save the image to thesis data
                    saved_path = self._save_generated_image(generated_image)
                    if saved_path:
                        generated_image['local_path'] = saved_path
                    print(f"✅ Generated image saved and will be displayed in chat")

                # Mark that we need to rerun after response generation
                st.session_state.pending_rerun = True

            # CRITICAL FIX: Return phase result for task manager
            return phase_result

        except Exception as e:
            print(f"❌ PHASE PROCESSING ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_and_display_response(self, user_input: str, image_path: str = None):
        """Generate and display the AI response with optional image."""
        # Simple spinner without typing indicator to avoid conflicts

        with st.spinner("Thinking..."):
            try:
                # Process response based on current mode with image support
                response = asyncio.run(
                    self.mode_processor.process_input(user_input, st.session_state.current_mode, image_path)
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

                # Handle phase transitions first
                phase_result = st.session_state.get('last_phase_result', {})
                generated_image_data = None

                print(f"🎨 DEBUG: Checking for phase transitions...")
                print(f"🎨 DEBUG: Phase result keys: {list(phase_result.keys()) if phase_result else 'None'}")
                print(f"🎨 DEBUG: Phase transition: {phase_result.get('phase_transition', False)}")

                # ENHANCED DUPLICATE PREVENTION: More robust checking
                should_process_transition = False
                transition_id = None

                if phase_result.get('phase_transition'):
                    # Create unique ID for this transition
                    transition_id = f"{phase_result.get('previous_phase', 'unknown')}_{phase_result.get('new_phase', 'unknown')}_{len(st.session_state.messages)}"
                    processed_transitions = st.session_state.get('processed_phase_transitions', set())

                    if transition_id not in processed_transitions:
                        print(f"🎨 DUPLICATE_PREVENTION: New transition {transition_id}, will process")
                        should_process_transition = True
                        # Mark as processed immediately to prevent race conditions
                        if 'processed_phase_transitions' not in st.session_state:
                            st.session_state.processed_phase_transitions = set()
                        st.session_state.processed_phase_transitions.add(transition_id)
                    else:
                        print(f"🎨 DUPLICATE_PREVENTION: Transition {transition_id} already processed, skipping completely")
                        should_process_transition = False

                # CRITICAL: Clear phase result immediately to prevent any reprocessing
                if st.session_state.get('last_phase_result'):
                    st.session_state.last_phase_result = {}
                    print(f"🎨 DUPLICATE_PREVENTION: Cleared last_phase_result immediately")

                # Only process transition if it should be processed (not a duplicate)
                if should_process_transition and phase_result.get('phase_transition'):
                    transition_msg = f"\n\n🎉 **Phase Transition!** {phase_result.get('transition_message', 'Moving to next phase!')}"
                    response_content += transition_msg
                    print(f"✅ PROCESSING_TRANSITION: Added phase transition message to response")

                    # Handle generated image if available
                    generated_image = phase_result.get('generated_image')
                    print(f"🎨 PROCESSING_TRANSITION: Generated image from phase result: {bool(generated_image)}")
                    if generated_image:
                        print(f"🎨 DEBUG: Generated image keys: {list(generated_image.keys())}")
                        print(f"🎨 DEBUG: Image URL: {generated_image.get('url', 'No URL')}")

                        # Check if we're running on Streamlit Cloud
                        is_cloud = (
                            os.environ.get('STREAMLIT_SHARING_MODE') or
                            'streamlit.app' in os.environ.get('HOSTNAME', '') or
                            os.environ.get('STREAMLIT_SERVER_PORT') or
                            'streamlit' in os.environ.get('SERVER_SOFTWARE', '').lower()
                        )
                        print(f"🎨 DEBUG: Running on cloud: {is_cloud}")

                        if not is_cloud:
                            # Only try to save locally if not on cloud
                            saved_path = self._save_generated_image(generated_image)
                            if saved_path:
                                generated_image['local_path'] = saved_path
                                print(f"🎨 DEBUG: Added local_path to generated_image: {saved_path}")
                        else:
                            print(f"🎨 DEBUG: Skipping local save on cloud deployment")

                        # Store image data for inclusion in chat message
                        generated_image_data = generated_image
                        print(f"✅ Generated image will be included in chat message")
                        print(f"🎨 DEBUG: Final generated_image_data keys: {list(generated_image_data.keys())}")
                    else:
                        print(f"❌ DEBUG: No generated_image found in phase_result")

                # Add Socratic question if needed (only for MENTOR mode)
                combined_response = self._add_socratic_question_if_needed(response_content, st.session_state.current_mode)

                # Add routing metadata if available
                final_message = self._add_routing_metadata(combined_response)

                # ENHANCED: Check if this is a gamified response
                response_metadata = st.session_state.get("last_response_metadata", {})
                gamification_display = response_metadata.get("gamification_display", {})

                # FIXED: Also check for 'gamification' key as fallback
                if not gamification_display:
                    gamification_display = response_metadata.get("gamification", {})

                # DEBUG: Log gamification data for troubleshooting
                # if gamification_display:
                #     #print(f"🎮 UI DEBUG: Gamification data found: {gamification_display.get('is_gamified', False)}")
                #     print(f"🎮 UI DEBUG: Display type: {gamification_display.get('display_type', 'none')}")
                # else:
                #     print(f"🎮 UI DEBUG: No gamification data found in metadata keys: {list(response_metadata.keys())}")

                # Add assistant message with gamification info and generated image
                assistant_message = {
                    "role": "assistant",
                    "content": final_message,
                    "timestamp": datetime.now().isoformat(),
                    "mentor_type": st.session_state.current_mode,
                    "gamification": gamification_display
                }

                # Include generated image data if available
                print(f"🎨 DEBUG: Checking if generated_image_data should be added to message: {bool(generated_image_data)}")
                if generated_image_data:
                    assistant_message["generated_image"] = generated_image_data
                    print(f"✅ Added generated image to assistant message")
                    print(f"🎨 DEBUG: Assistant message now has generated_image: {bool(assistant_message.get('generated_image'))}")
                    print(f"🎨 DEBUG: Generated image URL in message: {assistant_message.get('generated_image', {}).get('url', 'No URL')}")
                else:
                    print(f"❌ DEBUG: No generated_image_data to add to assistant message")
                    # Check if there was a phase result but no image data made it through
                    if phase_result.get('phase_transition'):
                        print(f"🎨 DEBUG: Phase transition occurred but no image data - phase_result keys: {list(phase_result.keys())}")
                        if 'generated_image' in phase_result:
                            print(f"🎨 DEBUG: Phase result has generated_image but it didn't make it to generated_image_data")
                            print(f"🎨 DEBUG: Phase result generated_image: {phase_result.get('generated_image')}")
                        else:
                            print(f"🎨 DEBUG: Phase result has no generated_image key")

                st.session_state.messages.append(assistant_message)

                # CRITICAL FIX: Only rerun if we haven't already set pending_rerun
                # This prevents double rerun when phase transitions occur
                if not st.session_state.get('pending_rerun', False):
                    st.rerun()
                else:
                    print(f"🎨 DEBUG: Skipping rerun - pending_rerun already set for phase transition")
                
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
    
    def _add_socratic_question_if_needed(self, response: str, current_mode: str = None) -> str:
        """Add Socratic question to response if needed (only for MENTOR mode)."""
        # Only add socratic questions for MENTOR mode
        if current_mode not in ["MENTOR", "Socratic Agent"]:
            print(f"\n🤔 SOCRATIC: Skipping for mode '{current_mode}' (not MENTOR)")
            return response

        print(f"\n🤔 SOCRATIC: Checking if question needed for MENTOR mode...")
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

        # RESTORED WORKING VERSION: Always try to get next question if not already awaiting response
        if not st.session_state.get('awaiting_socratic_response', False):
            next_question = self.phase_system.get_contextual_question(st.session_state.phase_session_id)
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
    
    # REMOVED: _handle_socratic_response - now handled in _process_user_response_for_phases
    
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
                if st.session_state.get('uploaded_image_path'):
                    st.image(st.session_state.uploaded_image_path, caption="Your Design", use_container_width=True)
                else:
                    st.info("📝 **No image uploaded for this session**")
            
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

    def _save_generated_image(self, generated_image: dict) -> str:
        """Save generated image to thesis data directory"""

        if not generated_image or not generated_image.get('url'):
            return None

        try:
            import requests
            import os
            from datetime import datetime

            # Create thesis data directory if it doesn't exist
            thesis_data_dir = os.path.join(os.getcwd(), "thesis_data", "generated_images")
            os.makedirs(thesis_data_dir, exist_ok=True)

            # Generate filename with timestamp and phase
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            phase = generated_image.get('phase', 'unknown')
            style = generated_image.get('style', 'unknown')
            filename = f"{timestamp}_{phase}_{style}.png"
            filepath = os.path.join(thesis_data_dir, filename)

            # Download and save the image
            print(f"📥 Downloading generated image from: {generated_image['url']}")
            response = requests.get(generated_image['url'], timeout=30)

            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"✅ Generated image saved to: {filepath}")

                # Also save metadata
                metadata_file = filepath.replace('.png', '_metadata.json')
                import json
                metadata = {
                    'url': generated_image['url'],
                    'phase': generated_image.get('phase'),
                    'style': generated_image.get('style'),
                    'prompt': generated_image.get('prompt'),
                    'timestamp': timestamp,
                    'local_path': filepath
                }

                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)

                print(f"✅ Image metadata saved to: {metadata_file}")

                # Skip Dropbox upload here - image generator already uploaded it
                print(f"ℹ️ Skipping Dropbox upload (already uploaded by image generator)")

                return filepath
            else:
                print(f"❌ Failed to download image: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error saving generated image: {e}")
            return None

    def _upload_image_to_dropbox(self, local_path: str, filename: str):
        """Upload image to Dropbox"""
        try:
            from dashboard.core.dropbox_integration import dropbox_exporter

            if dropbox_exporter and dropbox_exporter.dropbox_client:
                dropbox_path = f"/thesis_exports/generated_images/{filename}"
                result = dropbox_exporter.upload_to_dropbox(local_path, dropbox_path)

                if result.get("success"):
                    print(f"✅ Image uploaded to Dropbox: {dropbox_path}")
                else:
                    print(f"❌ Dropbox upload failed: {result.get('error', 'Unknown error')}")
            else:
                print("⚠️ Dropbox client not available for image upload")

        except Exception as e:
            print(f"❌ Error uploading image to Dropbox: {e}")



    def _is_image_already_processed(self, image_path: str) -> bool:
        """Check if an image has already been processed in this session."""
        processed_images = st.session_state.get('processed_images', set())
        return image_path in processed_images

    def _mark_image_as_processed(self, image_path: str, filename: str):
        """Mark an image as processed to avoid redundant analysis."""
        if 'processed_images' not in st.session_state:
            st.session_state.processed_images = set()
        st.session_state.processed_images.add(image_path)
        print(f"📝 DASHBOARD: Marked image as processed: {filename}")

    def _should_bundle_image_analysis(self, image_path: str) -> bool:
        """Check if we should bundle image analysis based on message count since last image upload."""
        try:
            # Initialize tracking if not exists
            if 'last_image_upload_message_count' not in st.session_state:
                st.session_state.last_image_upload_message_count = 0
                st.session_state.last_uploaded_image_path = None

            # Check if this is a new image
            if st.session_state.last_uploaded_image_path != image_path:
                # New image uploaded, reset counter
                st.session_state.last_image_upload_message_count = 0
                st.session_state.last_uploaded_image_path = image_path
                print(f"📷 DASHBOARD: New image detected, resetting counter")

            # Count messages since last image upload
            current_message_count = len(st.session_state.messages)
            messages_since_upload = current_message_count - st.session_state.last_image_upload_message_count

            print(f"🔍 DASHBOARD: Messages since image upload: {messages_since_upload}")

            # Only bundle for the first 2 messages after upload (changed from 4 to 2)
            if messages_since_upload < 2:  # 2 messages max: first user message + first assistant response
                print(f"✅ DASHBOARD: Bundling image analysis (messages since upload: {messages_since_upload}/2)")
                return True
            else:
                print(f"🔄 DASHBOARD: Image reference limit reached, not bundling (messages since upload: {messages_since_upload}/2)")
                return False

        except Exception as e:
            print(f"❌ DASHBOARD: Error checking image reference counter: {e}")
            # Default to not bundling on error to be safe
            return False

    def _get_existing_image_analysis(self, user_input: str, image_path: str) -> str:
        """Get existing enhanced image analysis from session state."""
        # First check for enhanced analyses
        enhanced_analyses = st.session_state.get('enhanced_image_analyses', [])
        for analysis in enhanced_analyses:
            if analysis['path'] == image_path:
                # Import the comprehensive analyzer to generate a fresh contextual response
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../thesis-agents'))
                from vision.comprehensive_vision_analyzer import ComprehensiveVisionAnalyzer

                analyzer = ComprehensiveVisionAnalyzer()
                cached_analysis = analysis['detailed_analysis']
                contextual_response = analyzer.generate_contextual_response(cached_analysis, user_input)
                return f"{user_input}\n\n[ENHANCED IMAGE ANALYSIS: {contextual_response}]"

        # Fallback to legacy analyses if available
        session_analyses = st.session_state.get('image_analyses', [])
        for analysis in session_analyses:
            if analysis['path'] == image_path:
                image_description = analysis['detailed_analysis'].get('chat_summary', 'Image analysis completed.')
                return f"{user_input}\n\n[UPLOADED IMAGE ANALYSIS: {image_description}]"

        # Final fallback if no analysis found
        building_type = getattr(st.session_state, 'project_type', 'architectural project')
        return f"{user_input}\n\n[IMAGE REFERENCE: I can see you're referencing a previously uploaded image for your {building_type}. Let's continue our discussion based on what we've already analyzed.]"

    def _get_conversation_summary(self) -> str:
        """Get a summary of the current conversation for context."""
        try:
            messages = getattr(st.session_state, 'messages', [])
            if not messages:
                return "New conversation starting"

            # Get the last few messages for context
            recent_messages = messages[-3:] if len(messages) > 3 else messages

            # Extract user messages for context
            user_messages = [msg.get('content', '') for msg in recent_messages if msg.get('role') == 'user']

            if user_messages:
                # Join the recent user messages to provide context
                summary = " | ".join(user_messages)
                return summary[:500]  # Limit length
            else:
                return "Conversation in progress"

        except Exception as e:
            print(f"⚠️ Error getting conversation summary: {e}")
            return "Conversation context unavailable"

    # Test action handlers removed - now handled in sidebar_components.py


def main():
    """Main function to run the dashboard."""
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()


if __name__ == "__main__":
    main() 