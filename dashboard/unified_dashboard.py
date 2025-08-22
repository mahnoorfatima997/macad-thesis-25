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
from dashboard.processors.mode_processors import ModeProcessor
from dashboard.analysis.phase_analyzer import PhaseAnalyzer
from dashboard.core.image_database import ImageDatabase

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

    # Set environment variable to prevent GUI dependencies
    os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    # Add thesis-agents to path
    thesis_agents_path = os.path.join(os.path.dirname(__file__), '../thesis-agents')
    if thesis_agents_path not in sys.path:
        sys.path.insert(0, thesis_agents_path)

    try:
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        return LangGraphOrchestrator(domain="architecture")
    except ImportError as e:
        st.warning(f"LangGraphOrchestrator not available: {e}")
        st.info("Running in fallback mode without multi-agent orchestration.")
        return None
    except Exception as e:
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
            test_dashboard=self.test_dashboard,
            image_database=self.image_database
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

        # Mentor type selection
        mentor_type = render_mentor_type_selection()
        st.session_state.mentor_type = mentor_type
        st.session_state.current_mode = mentor_type  # Map to current_mode for compatibility

        # Template prompts
        selected_template = render_template_selection()

        # Skill level selection
        skill_level = render_skill_level_selection()

        # Project description input with inline image upload
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

            # Chat input with seamless image upload
            user_input, uploaded_image = get_chat_input()

            if user_input:
                self._handle_chat_input(user_input, uploaded_image)
            elif uploaded_image:
                # Store image but don't process until user provides input
                self._store_uploaded_image(uploaded_image)
                st.info("📷 Image uploaded! Type a message or question and press Enter to analyze it.")

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
                # Extract comprehensive image analysis and bundle with text
                enhanced_user_input = self._bundle_image_with_text(user_input, image_path, latest_image['filename'])
                # Mark image as processed
                self._mark_image_as_processed(image_path, latest_image['filename'])
            else:
                print(f"⚡ DASHBOARD: Image already processed, using existing analysis")
                # Get existing analysis from session state
                enhanced_user_input = self._get_existing_image_analysis(user_input, image_path)

            # Clear pending images after use
            st.session_state.pending_images = []

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
        self._process_user_response_for_phases(user_input)

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

                print(f"📷 Image stored for later processing: {uploaded_file.name}")
                return image_path

        except Exception as e:
            print(f"❌ Error storing image: {e}")
            return None

    def _bundle_image_with_text(self, user_input: str, image_path: str, image_filename: str) -> str:
        """Bundle comprehensive image analysis with user text as a unified message."""
        try:
            print(f"🔍 DASHBOARD: Bundling image analysis with text for: {image_filename}")

            # Get comprehensive image analysis using GPT Vision with caching
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../thesis-agents'))
            from vision.comprehensive_vision_analyzer import ComprehensiveVisionAnalyzer

            # Initialize analyzer with caching enabled (default)
            analyzer = ComprehensiveVisionAnalyzer(domain="architecture", use_cache=True)

            # Get project context from session state if available
            project_context = st.session_state.get('project_description', user_input)

            # Check if we already have this analysis cached in session state
            session_analyses = st.session_state.get('image_analyses', [])
            for analysis in session_analyses:
                if analysis['path'] == image_path and analysis.get('project_context') == project_context:
                    print(f"⚡ DASHBOARD: Using session-cached analysis for: {image_filename}")
                    image_description = analysis['detailed_analysis'].get('chat_summary', 'Image analysis completed.')
                    bundled_message = f"{user_input}\n\n[UPLOADED IMAGE ANALYSIS: {image_description}]"
                    return bundled_message

            # Perform comprehensive image analysis (will use cache if available)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Get detailed image understanding for chat context
                detailed_understanding = loop.run_until_complete(
                    analyzer.get_detailed_image_understanding(image_path, project_context)
                )

                # Extract the chat-ready description
                image_description = detailed_understanding.get('chat_summary', 'Image analysis completed.')

                print(f"✅ DASHBOARD: Image analysis complete - {len(image_description)} chars")

                # Bundle the text and image analysis as one unified message
                bundled_message = f"{user_input}\n\n[UPLOADED IMAGE ANALYSIS: {image_description}]"

                # Store the detailed analysis for potential future reference
                if 'image_analyses' not in st.session_state:
                    st.session_state.image_analyses = []
                st.session_state.image_analyses.append({
                    "filename": image_filename,
                    "path": image_path,
                    "detailed_analysis": detailed_understanding,
                    "project_context": project_context,
                    "timestamp": datetime.now().isoformat()
                })

                return bundled_message

            finally:
                loop.close()

        except Exception as e:
            print(f"⚠️ DASHBOARD: Image analysis failed, using basic bundling: {e}")
            # Fallback to basic image reference
            return f"{user_input}\n\n[Image uploaded: {image_filename} - Analysis unavailable]"

    def _process_user_response_for_phases(self, user_input: str):
        """Process user response through the phase progression system."""
        try:
            print(f"\n🎯 DASHBOARD: Processing user message for phase progression")
            print(f"📝 Input: {user_input[:100]}...")

            # Use the new process_user_message method instead of process_response
            phase_result = self.phase_system.process_user_message(st.session_state.phase_session_id, user_input)

            if "error" in phase_result:
                print(f"❌ PHASE ERROR: {phase_result['error']}")
                return

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

            # Display nudge if available
            if phase_result.get('nudge'):
                st.info(f"💡 **Phase Guidance**: {phase_result['nudge']}")

            # Handle phase transitions - but don't rerun yet, let response generation complete
            if phase_result.get('phase_transition'):
                st.success(f"🎉 **Phase Transition**: {phase_result.get('transition_message', 'Moving to next phase!')}")

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

        except Exception as e:
            print(f"❌ PHASE PROCESSING ERROR: {e}")
            import traceback
            traceback.print_exc()

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

                if phase_result.get('phase_transition'):
                    transition_msg = f"\n\n🎉 **Phase Transition!** {phase_result.get('transition_message', 'Moving to next phase!')}"
                    response_content += transition_msg
                    print(f"✅ Added phase transition message to response")

                    # Handle generated image if available
                    generated_image = phase_result.get('generated_image')
                    if generated_image:
                        # Save the image to thesis data
                        saved_path = self._save_generated_image(generated_image)
                        if saved_path:
                            generated_image['local_path'] = saved_path

                        # Store image data for inclusion in chat message
                        generated_image_data = generated_image
                        print(f"✅ Generated image will be included in chat message")

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
                if gamification_display:
                    print(f"🎮 UI DEBUG: Gamification data found: {gamification_display.get('is_gamified', False)}")
                    print(f"🎮 UI DEBUG: Display type: {gamification_display.get('display_type', 'none')}")
                else:
                    print(f"🎮 UI DEBUG: No gamification data found in metadata keys: {list(response_metadata.keys())}")

                # Add assistant message with gamification info and generated image
                assistant_message = {
                    "role": "assistant",
                    "content": final_message,
                    "timestamp": datetime.now().isoformat(),
                    "mentor_type": st.session_state.current_mode,
                    "gamification": gamification_display
                }

                # Include generated image data if available
                if generated_image_data:
                    assistant_message["generated_image"] = generated_image_data
                    print(f"✅ Added generated image to assistant message")

                st.session_state.messages.append(assistant_message)
                
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

                # Upload to Dropbox
                self._upload_image_to_dropbox(filepath, filename)

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

    def _display_generated_phase_image(self, generated_image: dict):
        """Display the generated phase image and ask for user feedback"""

        if not generated_image or not generated_image.get('url'):
            return

        st.markdown("---")
        st.markdown("### 🎨 **Generated Design Visualization**")

        # Display the image
        try:
            st.image(
                generated_image['url'],
                caption=f"AI-generated {generated_image.get('phase', 'design')} visualization",
                use_container_width=True
            )

            # Show the prompt used
            with st.expander("🔍 View Generation Details"):
                st.markdown(f"**Phase:** {generated_image.get('phase', 'Unknown')}")
                st.markdown(f"**Style:** {generated_image.get('style', 'Unknown')}")
                st.markdown(f"**Prompt:** {generated_image.get('prompt', 'No prompt available')}")

            # Ask for user feedback
            st.markdown("**Does this visualization match your design thinking?**")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Yes, this captures my ideas", key=f"feedback_yes_{generated_image.get('phase', 'unknown')}"):
                    st.success("Great! This confirms we're aligned on your design direction.")
                    # Store positive feedback
                    if 'image_feedback' not in st.session_state:
                        st.session_state.image_feedback = []
                    st.session_state.image_feedback.append({
                        'phase': generated_image.get('phase'),
                        'feedback': 'positive',
                        'timestamp': str(datetime.now())
                    })

            with col2:
                if st.button("🤔 Partially, but needs adjustment", key=f"feedback_partial_{generated_image.get('phase', 'unknown')}"):
                    st.info("Thanks for the feedback! Let's continue refining your design ideas.")
                    # Store partial feedback
                    if 'image_feedback' not in st.session_state:
                        st.session_state.image_feedback = []
                    st.session_state.image_feedback.append({
                        'phase': generated_image.get('phase'),
                        'feedback': 'partial',
                        'timestamp': str(datetime.now())
                    })

            with col3:
                if st.button("❌ No, this doesn't match", key=f"feedback_no_{generated_image.get('phase', 'unknown')}"):
                    st.warning("No problem! Let's continue exploring your design ideas to better understand your vision.")
                    # Store negative feedback
                    if 'image_feedback' not in st.session_state:
                        st.session_state.image_feedback = []
                    st.session_state.image_feedback.append({
                        'phase': generated_image.get('phase'),
                        'feedback': 'negative',
                        'timestamp': str(datetime.now())
                    })

            st.markdown("---")

        except Exception as e:
            st.error(f"Error displaying generated image: {e}")
            print(f"❌ Error displaying generated image: {e}")

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

    def _get_existing_image_analysis(self, user_input: str, image_path: str) -> str:
        """Get existing image analysis from session state."""
        session_analyses = st.session_state.get('image_analyses', [])
        for analysis in session_analyses:
            if analysis['path'] == image_path:
                image_description = analysis['detailed_analysis'].get('chat_summary', 'Image analysis completed.')
                return f"{user_input}\n\n[UPLOADED IMAGE ANALYSIS: {image_description}]"

        # Fallback if no analysis found
        return f"{user_input}\n\n[UPLOADED IMAGE: Analysis not available]"


def main():
    """Main function to run the dashboard."""
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()


if __name__ == "__main__":
    main() 