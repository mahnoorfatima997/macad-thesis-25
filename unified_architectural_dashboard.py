import streamlit as st
import os
import asyncio
import json
import tempfile
from PIL import Image
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fix Python path for thesis_tests imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import mega mentor components
from mega_architectural_mentor import MegaArchitecturalMentor, get_raw_gpt_response


from phase_progression_system import PhaseProgressionSystem
# Cached resources (after imports)
@st.cache_resource
def get_cached_orchestrator():
    # Correctly initialize with domain (not API key)
    return LangGraphOrchestrator(domain="architecture")

@st.cache_resource
def get_cached_mentor(api_key: str):
    return MegaArchitecturalMentor(api_key)

@st.cache_resource
def get_cached_phase_system():
    return PhaseProgressionSystem()


# Fix thesis-agents import path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))
try:
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator
except ImportError:
    # Fallback import path
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator


# Import test dashboard components
from thesis_tests.test_dashboard import TestDashboard

# Import data collection components                                    
from thesis_tests.data_models import TestGroup, TestPhase
import sys
sys.path.append('./thesis-agents')
from data_collection.interaction_logger import InteractionLogger
import uuid

# Configure Streamlit for clean interface
st.set_page_config(
    page_title="🏗️ Unified Architectural Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern interface (matching mega_architectural_mentor)
st.markdown("""
<style>
    /* Dark theme styling */
    .stApp {
        background: #ffffff !important;
        color: black !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #ffffff !important;
        border-right: 1px solid #404040 !important;
        display: block !important;
        visibility: visible !important;
    }
    
    /* Ensure sidebar is visible */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Ensure main content doesn't overlap with sidebar */
    .main .block-container {
        background: #ffffff !important;
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 2rem;
        margin-left: 0 !important;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    /* Top section styling */
    .top-section {
        text-align: center;
        margin-bottom: 3rem;
        padding-top: 2rem;
    }
    
    .plan-badge {
        display: inline-block;
        background: #ffffff;
        color: black;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .greeting {
        font-size: 2.5rem;
        font-weight: bold;
        color: black;
        margin-bottom: 1rem;
    }
    
    .compact-text {
        font-size: 14px;
        line-height: 1.4;
        color: #000000;
    }
    
    /* Chat message styling */
    .chat-message {
        background: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    
    .chat-message.assistant {
        background: #ffffff;
        border-left: 4px solid #2196F3;
    }
    
    /* Metric cards */
    .metric-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #404040;
        margin: 0.5rem 0;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-ready {
        background: #00ff00;
    }
    
    .status-warning {
        background: #ffaa00;
    }
    
    .status-error {
        background: #ff0000;
    }
    
    /* Mode selector styling */
    .mode-selector {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #404040;
        margin-bottom: 1rem;
    }
    
    /* Chat container */
    .chat-container {
        background: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #404040;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "MENTOR"
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'test_active' not in st.session_state:
        st.session_state.test_active = False
    
    if 'test_paused' not in st.session_state:
        st.session_state.test_paused = False
    
    if 'test_config' not in st.session_state:
        st.session_state.test_config = None
    
    if 'phase_system' not in st.session_state:
        st.session_state.phase_system = None
    
    if 'phase_session_id' not in st.session_state:
        st.session_state.phase_session_id = None
    
    # Participant/session meta for sidebar
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = "unified_user"
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = ""
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    # UI preferences
    if 'show_routing_meta' not in st.session_state:
        st.session_state.show_routing_meta = False
    
    # Socratic dialogue control flags
    if 'awaiting_socratic_response' not in st.session_state:
        st.session_state.awaiting_socratic_response = False
    if 'current_question_id' not in st.session_state:
        st.session_state.current_question_id = None

class UnifiedArchitecturalDashboard:
    def __init__(self):
        self.api_key = self._get_api_key()
        if not self.api_key:
            st.error("❌ OPENAI_API_KEY not found. Please set it as an environment variable or in Streamlit secrets.")
            st.stop()

        # Initialize session state once
        initialize_session_state()

        # Lazy + cached heavy objects
        self.mentor = get_cached_mentor(self.api_key)
        self.orchestrator = get_cached_orchestrator()
        self.phase_system = get_cached_phase_system()

        # Data collector: store once in session
        if 'data_collector' not in st.session_state or not isinstance(st.session_state.data_collector, InteractionLogger):
            st.session_state.data_collector = InteractionLogger(session_id="unified_dashboard_session")
        self.data_collector = st.session_state.data_collector

        # Test dashboard lazy load (spacy heavy)
        if 'test_dashboard' not in st.session_state:
            st.session_state.test_dashboard = None
        self.test_dashboard = st.session_state.test_dashboard
    
    def _get_api_key(self) -> str:
        """Get API key from environment or Streamlit secrets"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            try:
                api_key = st.secrets.get('OPENAI_API_KEY', '')
            except:
                api_key = ''
        return api_key
    
    def render_chat_message(self, message: Dict[str, Any]):
        """Render a chat message with appropriate styling (matching mega_architectural_mentor)"""
        
        if message["role"] == "user":
            st.markdown(f"""
            <div style="background: #ffffff; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4CAF50;">
                <strong>👤 You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Get mentor type for display
            mentor_type = message.get("mentor_type", "Multi-Agent System")
            if mentor_type == "MENTOR":
                mentor_icon = "🏗️"
                mentor_label = "Architectural Mentor"
            elif mentor_type == "GENERIC_AI":
                mentor_icon = "🤖"
                mentor_label = "Generic AI"
            elif mentor_type == "CONTROL":
                mentor_icon = "🎯"
                mentor_label = "Control Mode"
            else:
                mentor_icon = "🏗️"
                mentor_label = mentor_type
            
            st.markdown(f"""
            <div style="background: #ffffff; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #2196F3;">
                <strong>{mentor_icon} {mentor_label}:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar with single-flow controls"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # API Key status
            if self.api_key:
                st.success("✅ API Key: Configured")
            else:
                st.error("❌ API Key: Missing")
            
            # Pre-Test placed near top
            self._render_inline_pretest()

            # Participant info
            st.markdown("### 👤 Participant")
            pid = st.text_input("Participant ID", value=st.session_state.participant_id)
            pname = st.text_input("Name (optional)", value=st.session_state.participant_name)
            st.session_state.participant_id = pid or "unified_user"
            st.session_state.participant_name = pname or ""
            # keep logger in sync
            try:
                # InteractionLogger doesn't have participant_id, but we can store it in metadata
                pass
            except Exception:
                pass
            
            # Reset data collector if needed
            if st.button("🔄 Reset Data Collector"):
                st.session_state.data_collector = InteractionLogger(session_id="unified_dashboard_session")
                st.success("Data collector reset!")
                st.rerun()

            # Session meta
            st.markdown("### 🕒 Session")
            # set start time when a session id is first created
            if st.session_state.session_id and not st.session_state.session_start_time:
                st.session_state.session_start_time = datetime.now()
            st.caption(f"ID: {st.session_state.session_id or '—'}")
            if st.session_state.session_start_time:
                st.caption(f"Started: {st.session_state.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                try:
                    elapsed_min = (datetime.now() - st.session_state.session_start_time).total_seconds() / 60.0
                    st.caption(f"Elapsed: {elapsed_min:.1f} min")
                except Exception:
                    pass

            # System status
            st.markdown("### 🔧 System Status")
            st.info("**Vision**: GPT Vision Available")
            st.info("**Agents**: Multi-Agent System Ready")
            st.checkbox("Show route/agents meta in replies", key="show_routing_meta")
            
            # Current session info
            if st.session_state.analysis_complete:
                st.markdown("### 📊 Current Session")
                current_mode = st.session_state.get('current_mode', 'MENTOR')
                
                if current_mode == "MENTOR":
                    st.success(f"**Mode**: {current_mode} 🤖")
                elif current_mode == "GENERIC_AI":
                    st.warning(f"**Mode**: {current_mode} 🤖")
                else:
                    st.info(f"**Mode**: {current_mode} 🎯")
            
            # Session management
            st.markdown("### 📊 Session Management")
            if st.button("🔄 Reset Session"):
                self._reset_session()
                st.rerun()
            
            if st.button("💾 Export Data"):
                self._export_session_data()
            
            # Single-flow: no page selector
            return "Main"

    def _response_contains_questions(self, text: str) -> bool:
        """Light heuristic: treat response as already inquisitive if it contains a question."""
        if not text:
            return False
        return text.count('?') >= 1
    
    def _reset_session(self):
        """Reset the current session"""
        st.session_state.messages = []
        st.session_state.analysis_results = None
        # Remove any leftover benchmarking state
        st.session_state.test_results = {}
        st.session_state.session_id = None
        st.session_state.analysis_complete = False
        st.success("Session reset successfully!")
    
    def _export_session_data(self):
        """Export session data"""
        if not st.session_state.messages:
            st.warning("No data to export")
            return
        
        # Export comprehensive data using InteractionLogger
        try:
            summary = self.data_collector.export_for_thesis_analysis()
            st.success("✅ Session data exported to thesis_data/")
            st.info(f"Files created: interactions_{self.data_collector.session_id}.csv, design_moves_{self.data_collector.session_id}.csv, session_summary_{self.data_collector.session_id}.json, full_log_{self.data_collector.session_id}.json")
        except Exception as e:
            st.warning(f"Data export warning: {e}")
        
        # Prepare data for export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": st.session_state.current_mode,
            "messages": st.session_state.messages,
            "analysis_results": st.session_state.analysis_results,
            "test_results": st.session_state.test_results
        }
        
        # Convert to JSON
        json_str = json.dumps(export_data, indent=2, default=str)
        
        # Create download button
        st.download_button(
            label="📥 Download Session Data",
            data=json_str,
            file_name=f"session_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    async def process_chat_response(self, user_input: str, mode: str) -> str:
        """Process chat response based on selected mode"""
        try:
            if mode == "MENTOR":
                # Use the full multi-agent mentor system
                response = await self._process_mentor_mode(user_input)
            elif mode == "RAW_GPT":
                response = await self._process_raw_gpt_mode(user_input)
            elif mode == "GENERIC_AI":
                # Use generic AI response
                response = await self._process_generic_ai_mode(user_input)
            elif mode == "CONTROL":
                # Use control mode (no AI assistance)
                response = await self._process_control_mode(user_input)
            else:
                response = "Invalid mode selected."
            
            return response
        
        except Exception as e:
            st.error(f"❌ Error in process_chat_response: {str(e)}")
            return f"An error occurred: {str(e)}"
    
    async def _process_mentor_mode(self, user_input: str) -> str:
        """Process using the full mentor system"""
        # Initialize session if needed
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create ArchMentorState for the orchestrator
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thesis-agents'))
        from state_manager import ArchMentorState, StudentProfile
        
        # Create student profile
        student_profile = StudentProfile(
            skill_level="intermediate",
            learning_style="visual",
            cognitive_load=0.3,
            engagement_level=0.7
        )
        
        # Create state with current conversation history
        state = ArchMentorState(
            messages=st.session_state.messages.copy(),
            current_design_brief=st.session_state.analysis_results.get('text_analysis', {}).get('building_type', 'architectural project') if st.session_state.analysis_results else "architectural project",
            student_profile=student_profile,
            domain="architecture"
        )
        
        # Ensure we don't duplicate the same user message (we already appended to session history)
        if not state.messages or state.messages[-1].get("role") != "user" or state.messages[-1].get("content") != user_input:
            state.messages.append({
                "role": "user",
                "content": user_input
            })
        
        # Process with orchestrator
        result = await self.orchestrator.process_student_input(state)
        response = result.get("response", "I apologize, but I couldn't generate a response.")
        # Orchestrator returns metadata under key "metadata"
        response_metadata = result.get("metadata", {})
        # Store latest metadata for use when rendering chat
        try:
            st.session_state.last_response_metadata = response_metadata
        except Exception:
            pass
        
        # Collect data for analysis (simplified for now)
        try:
            # Log the interaction using the TestSessionLogger's actual methods
            from thesis_tests.data_models import InteractionData, MoveType, TestPhase, Modality, DesignFocus, MoveSource
            
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
            
            self.data_collector.log_interaction(interaction)
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
        return response

    async def _process_raw_gpt_mode(self, user_input: str) -> str:
        """Process using direct Raw GPT (no multi-agent)"""
        # Initialize session if needed
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
        # Store metadata for suffix display
        st.session_state.last_response_metadata = response_metadata
        # Log interaction
        try:
            from thesis_tests.data_models import InteractionData, TestPhase
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
            self.data_collector.log_interaction(interaction)
        except Exception as e:
            print(f"Warning: Could not log Raw GPT interaction: {e}")
        return response
    
    async def _process_generic_ai_mode(self, user_input: str) -> str:
        """Process using generic AI"""
        # Initialize session if needed
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Use test dashboard's generic AI mode
        response = self.test_dashboard.generic_ai_env.process_input(user_input)
        
        # Collect data for analysis (simplified for now)
        try:
            from thesis_tests.data_models import InteractionData
            
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
            
            self.data_collector.log_interaction(interaction)
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
        return response
    
    async def _process_control_mode(self, user_input: str) -> str:
        """Process using control mode (no AI)"""
        # Initialize session if needed
        if not st.session_state.session_id:
            st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Use test dashboard's control mode
        response = self.test_dashboard.control_env.process_input(user_input)
        
        # Collect data for analysis (simplified for now)
        try:
            from thesis_tests.data_models import InteractionData
            
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
            
            self.data_collector.log_interaction(interaction)
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
        return response
    
    def render_main_chat(self):
        """Render the combined pre-test + agentic chat structured by phase progression"""
        
        # Top section with greeting
        st.markdown("""
        <div class="top-section">
        <div class="greeting">
            Welcome to your Unified AI Architectural Mentor!
        </div>
        <p style="text-align: center; color: #888; margin-top: 1rem;">
            Choose your testing mode and start a conversation. This unified dashboard combines 
            multi-agent mentoring and research testing capabilities.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mode selection in center column (kept minimal)
        with st.columns([1, 2, 1])[1]:  # Center column
            st.markdown("""
            <div class="compact-text" style="font-size: 14px; font-weight: bold; margin-bottom: 10px; text-align: center;">
                🧪 Testing Mode Configuration
            </div>
            """, unsafe_allow_html=True)
            
            # Mode selection dropdown (matching mega_architectural_mentor style)
            current_mode = st.selectbox(
                "🤖 Select Testing Mode:",
                ["MENTOR", "RAW_GPT", "GENERIC_AI", "CONTROL"],
                index=0,
                help="MENTOR: Full multi-agent system with cognitive enhancement\nGENERIC_AI: Basic AI responses for comparison\nCONTROL: No AI assistance for baseline testing"
            )
            st.session_state.current_mode = current_mode
            
            # Template design prompts (matching mega_architectural_mentor)
            template_prompts = {
                "Select a template...": "",
                "🏢 Sustainable Office Building": "I'm designing a sustainable office building for a tech company. The building should accommodate 200 employees with flexible workspaces, meeting rooms, and common areas. I want to focus on energy efficiency, natural lighting, and creating a collaborative environment. The site is in an urban area with limited green space.",
                "🏫 Community Learning Center": "I'm creating a community learning center that will serve as a hub for education, workshops, and community events. The building needs to include classrooms, a library, multipurpose spaces, and outdoor learning areas. I want it to be welcoming to all ages and accessible to everyone in the community.",
                "🏠 Residential Complex": "I'm designing a residential complex that combines modern living with community spaces. The project includes apartments, shared amenities, and green spaces. I want to create a sense of community while maintaining privacy and sustainability.",
                "🏛️ Cultural Center": "I'm designing a cultural center that will showcase local arts and provide performance spaces. The building needs to include galleries, theaters, workshops, and public gathering areas. I want it to be both functional and inspiring."
            }
            
            selected_template = st.selectbox(
                "📋 Quick Start Templates:",
                list(template_prompts.keys()),
                help="Choose a template to get started quickly, or write your own description below"
            )
            
            # Skill level selection
            skill_level = st.selectbox(
                "🎯 Your Skill Level:",
                ["beginner", "intermediate", "advanced"],
                index=1,
                help="This helps the AI provide appropriate guidance"
            )
            
            # Project description input
            template_text = template_prompts.get(selected_template, "")
            project_description = st.text_area(
                "📝 Project Description:",
                value=template_text,
                placeholder="Describe your architectural project here...",
                height=120,
                help="Provide details about your architectural project, design goals, constraints, or specific questions"
            )
            # Optional image upload (to match Mega Mentor capabilities)
            uploaded_file = st.file_uploader(
                "📁 Upload your architectural drawing (optional)",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear image of your architectural design, plan, or sketch"
            )
            
            # Start analysis button
            # Form to avoid reruns while typing
            with st.form(key="start_form"):
                start_clicked = st.form_submit_button("🚀 Start")
            if start_clicked:
                if not project_description.strip():
                    st.error("📝 Please describe your project to start analysis")
                else:
                    with st.spinner("🧠 Analyzing your design..."):
                        try:
                            # Initialize session
                            if not st.session_state.session_id:
                                st.session_state.session_id = f"unified_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            
                            # Initialize data collector with session ID
                            self.data_collector.session_id = st.session_state.session_id
                            
                                                        # Run analysis based on selected mode
                            if current_mode == "MENTOR":
                                # Use asyncio to run the async analyze_design method
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                try:
                                    temp_image_path = None
                                    if uploaded_file is not None:
                                        image = Image.open(uploaded_file)
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                            image.save(tmp_file.name)
                                            temp_image_path = tmp_file.name
                                    results = loop.run_until_complete(
                                        self.mentor.analyze_design(
                                            design_brief=project_description,
                                            image_path=temp_image_path,
                                            skill_level=skill_level,
                                            domain="architecture"
                                        )
                                    )
                                finally:
                                    loop.close()
                            else:
                                # For other modes, create a comprehensive analysis structure
                                results = {
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
                            
                            # Store results
                            st.session_state.analysis_results = results
                            st.session_state.analysis_complete = True
                            
                            # Ensure phase session initialized for immediate first response
                            if st.session_state.phase_system is None:
                                st.session_state.phase_system = self.phase_system
                            if st.session_state.phase_session_id is None:
                                st.session_state.phase_session_id = f"phase_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                self.phase_system.start_session(st.session_state.phase_session_id)
                            
                            # Immediately treat the provided project description as the first user prompt
                            initial_user_input = project_description
                            if initial_user_input and initial_user_input.strip():
                                # Add user message to chat history (for UI continuity)
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": initial_user_input,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                # Process response based on current mode
                                response = asyncio.run(self.process_chat_response(initial_user_input, current_mode))
                                
                                # Optionally include the next Socratic question in the SAME assistant message
                                combined_response = response
                                if not st.session_state.awaiting_socratic_response:
                                    next_question = self.phase_system.get_next_question(st.session_state.phase_session_id)
                                    if next_question and not self._response_contains_questions(response):
                                        combined_response = f"{response}\n\n{next_question.question_text}"
                                        st.session_state.awaiting_socratic_response = True
                                        st.session_state.current_question_id = next_question.question_id
                                
                                # Include routing/agents metadata if available
                                response_metadata = st.session_state.get("last_response_metadata", {})
                                routing_path = response_metadata.get("routing_path") or response_metadata.get("route")
                                agents_used = response_metadata.get("agents_used") or []
                                meta_suffix = ""
                                if routing_path or agents_used:
                                    used = ", ".join(agents_used) if agents_used else ""
                                    meta_suffix = f"\n\n— Route: {routing_path or 'unknown'}{f' | Agents: {used}' if used else ''}"
                                final_message = combined_response + (meta_suffix if st.session_state.get('show_routing_meta', False) else "")
                                
                                # Append assistant message
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": final_message,
                                    "timestamp": datetime.now().isoformat(),
                                    "mentor_type": current_mode
                                })
                            
                            st.success("✅ Analysis complete. Multi-agent mentor has responded to your initial prompt.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
        
        # Pre-Test is rendered in the sidebar now

        # Chat interface (after or during pre-test)
        if st.session_state.analysis_complete:
            # Chat interface - confined to center column
            with st.columns([1, 2, 1])[1]:  # Center column
                # Display chat messages
                for message in st.session_state.messages:
                    self.render_chat_message(message)
                
                # Chat input
                user_input = st.chat_input("Ask about improvements, precedents, or request a review...")
                
                if user_input:
                    # Add user message to chat history
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": user_input,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Log to data collector using InteractionLogger
                    try:
                        # Get metadata from orchestrator response
                        response_metadata = st.session_state.get("last_response_metadata", {})
                        routing_path = response_metadata.get("routing_path") or response_metadata.get("route") or "mentor_mode"
                        agents_used = response_metadata.get("agents_used") or ["orchestrator"]
                        cognitive_flags = response_metadata.get("cognitive_flags") or []
                        
                        # Log the interaction with comprehensive metadata
                        self.data_collector.log_interaction(
                            student_input=user_input,
                            agent_response="Processing...",  # Will be updated after response
                            routing_path=routing_path,
                            agents_used=agents_used,
                            response_type="mentor_response",
                            cognitive_flags=cognitive_flags,
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
                                "phase_analysis": {
                                    "phase": "ideation",
                                    "confidence": 0.8
                                },
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
                    
                    # Display user message
                    self.render_chat_message({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Ensure phase session initialized
                    if st.session_state.phase_system is None:
                        st.session_state.phase_system = self.phase_system
                    if st.session_state.phase_session_id is None:
                        st.session_state.phase_session_id = f"phase_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self.phase_system.start_session(st.session_state.phase_session_id)

                    # If we are awaiting a Socratic response, grade first, then generate agentic reply
                    if st.session_state.awaiting_socratic_response:
                        phase_result = self.phase_system.process_response(st.session_state.phase_session_id, user_input)
                        st.session_state.awaiting_socratic_response = False
                        st.session_state.current_question_id = None
                        if "error" not in phase_result:
                            grade = phase_result["grade"]
                            st.caption(f"Phase {phase_result['current_phase'].title()} | Score {grade['overall_score']:.1f}/5")

                    # Generate response (always)
                    with st.spinner("🧠 Thinking..."):
                        try:
                            # Process response based on current mode
                            response = asyncio.run(self.process_chat_response(user_input, st.session_state.current_mode))

                            # Optionally include the next Socratic question in the SAME assistant message
                            combined_response = response
                            if not st.session_state.awaiting_socratic_response:
                                next_question = self.phase_system.get_next_question(st.session_state.phase_session_id)
                                # Only append Socratic question if the agentic response didn't already ask questions
                                if next_question and not self._response_contains_questions(response):
                                    combined_response = f"{response}\n\n{next_question.question_text}"
                                    st.session_state.awaiting_socratic_response = True
                                    st.session_state.current_question_id = next_question.question_id

                            # Add a single assistant message (agentic + optional Socratic prompt)
                            # Include routing/agents metadata if available
                            response_metadata = st.session_state.get("last_response_metadata", {})
                            routing_path = response_metadata.get("routing_path") or response_metadata.get("route")
                            agents_used = response_metadata.get("agents_used") or []
                            meta_suffix = ""
                            if routing_path or agents_used:
                                used = ", ".join(agents_used) if agents_used else ""
                                meta_suffix = f"\n\n— Route: {routing_path or 'unknown'}{f' | Agents: {used}' if used else ''}"
                            final_message = combined_response + (meta_suffix if st.session_state.get('show_routing_meta', False) else "")

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": final_message,
                                "timestamp": datetime.now().isoformat(),
                                "mentor_type": st.session_state.current_mode
                            })
                            
                            # Update data collector with response
                            try:
                                if self.data_collector.interactions:
                                    # Update the last interaction's agent_response
                                    self.data_collector.interactions[-1]["agent_response"] = response
                                    
                                    # Also update checklist via phase system using user+assistant contents
                                    try:
                                        delta = self.phase_system.update_checklist_from_interaction(
                                            st.session_state.phase_session_id,
                                            user_input,
                                            response
                                        )
                                        # Merge delta into metadata for this turn
                                        if isinstance(delta, dict):
                                            response_metadata = st.session_state.get("last_response_metadata", {}) or {}
                                            response_metadata["checklist_delta"] = delta.get("checklist_delta", [])
                                            st.session_state.last_response_metadata = response_metadata
                                    except Exception as _e:
                                        pass
                            except Exception as e:
                                st.warning(f"Response logging error: {e}")
                            
                        except Exception as e:
                            error_response = f"I apologize, but I encountered an error: {str(e)}"
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_response,
                                "timestamp": datetime.now().isoformat(),
                                "mentor_type": st.session_state.current_mode
                            })
                    
                    st.rerun()
        
        # Phase Progression and Learning Insights Section - show underneath chat
        if len(st.session_state.messages) > 0 and st.session_state.phase_session_id:
            with st.columns([1, 2, 1])[1]:  # Center column
                st.markdown("---")
                st.markdown("""
                <div class="compact-text" style="font-size: 12px; font-weight: bold; margin-bottom: 10px; text-align: center; color: #1f77b4;">
                    🎯 Phase Progression & Learning Insights
                </div>
                """, unsafe_allow_html=True)
                
                # Analyze phase progression and learning insights
                try:
                    # Create session data from chat messages
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
                    
                    session_data = {
                        "session_id": st.session_state.get('session_id', 'unknown'),
                        "interactions": chat_interactions,
                        "duration": 0
                    }
                    
                    # Analyze phase progression from conversation content and interaction patterns
                    current_phase, phase_progress = self._calculate_conversation_progress(chat_interactions)
                    
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
                        st.markdown("**🎯 Key Challenges Identified**")
                        challenges = [
                            "Understanding project requirements",
                            "Balancing functionality and aesthetics",
                            "Integrating sustainable design principles"
                        ]
                        
                        for challenge in challenges[:3]:  # Show top 3 challenges
                            st.markdown(f"• {challenge}")
                        
                        st.markdown("**💡 Learning Points**")
                        learning_points = [
                            "Developing systematic approach to design",
                            "Enhancing spatial reasoning skills",
                            "Improving design communication"
                        ]
                        
                        for point in learning_points[:3]:  # Show top 3 learning points
                            st.markdown(f"• {point}")
                    
                    # Session summary
                    st.markdown("---")
                    st.markdown("**📊 Session Summary**")
                    total_interactions = len(chat_interactions)
                    session_duration = 'Ongoing'
                    
                    summary_col1, summary_col2, summary_col3 = st.columns(3)
                    with summary_col1:
                        st.metric("Interactions", total_interactions)
                    with summary_col2:
                        st.metric("Phase Progress", f"{phase_progress:.0f}%")
                    with summary_col3:
                        st.metric("Session Status", session_duration)
                    
                except Exception as e:
                    st.error(f"Error analyzing progression: {str(e)}")
                    
                    # Progress summary
                    total_interactions = len(chat_interactions)
                    st.markdown(f"**📊 Session: {total_interactions} interactions**")
     
    # Benchmarking UI removed entirely
    
    def _calculate_conversation_progress(self, chat_interactions: List[Dict]) -> tuple[str, float]:
        """Calculate current phase and progress based on conversation content"""
        if not chat_interactions:
            return "ideation", 0.0
        
        # Combine all conversation text for analysis
        all_text = ""
        for interaction in chat_interactions:
            user_input = interaction.get("data", {}).get("input", "")
            response = interaction.get("data", {}).get("response", "")
            all_text += f" {user_input} {response}"
        
        all_text = all_text.lower()
        
        # Phase detection based on keywords and conversation patterns
        phase_scores = {
            "ideation": 0,
            "visualization": 0, 
            "materialization": 0
        }
        
        # Ideation keywords (concept, requirements, goals, etc.)
        ideation_keywords = [
            "concept", "idea", "approach", "strategy", "vision", "goal", "objective", 
            "purpose", "intention", "brainstorm", "explore", "consider", "think about", 
            "what if", "imagine", "envision", "precedent", "example", "reference", 
            "inspiration", "influence", "site", "context", "requirements", "program",
            "need", "want", "should", "could", "might", "maybe", "perhaps"
        ]
        
        # Visualization keywords (form, space, layout, etc.)
        visualization_keywords = [
            "form", "shape", "massing", "volume", "proportion", "scale", "circulation", 
            "flow", "layout", "plan", "section", "elevation", "sketch", "drawing", 
            "model", "3d", "render", "visualize", "spatial", "arrangement", 
            "composition", "geometry", "structure", "lighting", "spatial organization",
            "room", "space", "area", "zone", "floor", "level", "height", "width",
            "dimension", "size", "placement", "position", "orientation"
        ]
        
        # Materialization keywords (construction, details, etc.)
        materialization_keywords = [
            "construction", "structure", "system", "detail", "material", "technical", 
            "engineering", "performance", "cost", "budget", "timeline", "schedule", 
            "specification", "implementation", "fabrication", "assembly", "installation", 
            "maintenance", "durability", "sustainability", "efficiency", "code", "standard",
            "wall", "floor", "ceiling", "door", "window", "roof", "foundation"
        ]
        
        # Score each phase based on keyword frequency
        for keyword in ideation_keywords:
            if keyword in all_text:
                phase_scores["ideation"] += 1
        
        for keyword in visualization_keywords:
            if keyword in all_text:
                phase_scores["visualization"] += 1
                
        for keyword in materialization_keywords:
            if keyword in all_text:
                phase_scores["materialization"] += 1
        
        # Determine current phase based on highest score
        current_phase = max(phase_scores, key=phase_scores.get)
        max_score = phase_scores[current_phase]
        
        # Calculate progress based on interaction depth and phase completion
        # Base progress on number of interactions and keyword density
        interaction_count = len(chat_interactions)
        keyword_density = max_score / len(all_text.split()) * 1000  # normalize per 1000 words
        
        # Progress calculation: combine interaction count and keyword density
        # Each interaction contributes ~15-25% progress, keyword density adds 0-20%
        base_progress = min(interaction_count * 20, 80)  # cap at 80% from interactions
        keyword_bonus = min(keyword_density * 2, 20)  # up to 20% from keywords
        total_progress = min(base_progress + keyword_bonus, 100)
        
        # Phase transitions based on conversation depth
        if current_phase == "ideation" and total_progress > 60:
            # Move to visualization if ideation is well explored
            current_phase = "visualization"
            total_progress = max(0, total_progress - 40)  # reset progress for new phase
        elif current_phase == "visualization" and total_progress > 70:
            # Move to materialization if visualization is well explored
            current_phase = "materialization"
            total_progress = max(0, total_progress - 50)  # reset progress for new phase
        
        return current_phase, total_progress

    def _analyze_phase_progression(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze design phase progression from interactions"""
        if not interactions:
            # Return sample phase progression for demonstration
            return {
                "current_phase": "ideation",
                "phase_progress": 25,
                "session_duration": "Active",
                "challenges": [
                    "Understanding project requirements and constraints",
                    "Balancing functionality with aesthetic considerations",
                    "Integrating sustainable design principles effectively"
                ],
                "learning_points": [
                    "Developing systematic approach to design problems",
                    "Enhancing spatial reasoning and visualization skills",
                    "Improving design communication and presentation"
                ]
            }
        
        # Simple phase detection based on interaction content
        content_text = " ".join([str(i.get("data", {}).get("input", "")) + " " + str(i.get("data", {}).get("response", "")) for i in interactions])
        content_lower = content_text.lower()
        
        # Design thinking phases with keywords (matching thesis framework)
        design_phases = {
            "ideation": ["concept", "idea", "approach", "strategy", "vision", "goal", "objective", "purpose", "intention", "brainstorm", "explore", "consider", "think about", "what if", "imagine", "envision", "precedent", "example", "reference", "inspiration", "influence", "site", "context", "requirements", "program"],
            "visualization": ["form", "shape", "massing", "volume", "proportion", "scale", "circulation", "flow", "layout", "plan", "section", "elevation", "sketch", "drawing", "model", "3d", "render", "visualize", "spatial", "arrangement", "composition", "geometry", "structure", "lighting", "spatial organization"],
            "materialization": ["construction", "structure", "system", "detail", "material", "technical", "engineering", "performance", "cost", "budget", "timeline", "schedule", "specification", "implementation", "fabrication", "assembly", "installation", "maintenance", "durability", "sustainability", "efficiency"]
        }
        
        # Calculate phase scores
        phase_scores = {}
        for phase, keywords in design_phases.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            phase_scores[phase] = score
        
        # Determine current phase
        if phase_scores:
            current_phase = max(phase_scores, key=phase_scores.get)
            max_score = phase_scores[current_phase]
            total_possible = max(len(keywords) for keywords in design_phases.values())
            phase_progress = min((max_score / total_possible) * 100, 100)
        else:
            current_phase = "ideation"
            phase_progress = 0
        
        # Identify challenges based on content analysis
        challenges = []
        if "requirement" in content_lower or "constraint" in content_lower:
            challenges.append("Clarifying project requirements and constraints")
        if "balance" in content_lower or "trade" in content_lower:
            challenges.append("Balancing competing design priorities")
        if "sustain" in content_lower or "green" in content_lower:
            challenges.append("Integrating sustainable design principles")
        if "budget" in content_lower or "cost" in content_lower:
            challenges.append("Working within budget constraints")
        if "time" in content_lower or "schedule" in content_lower:
            challenges.append("Managing project timeline effectively")
        if "client" in content_lower or "stakeholder" in content_lower:
            challenges.append("Addressing stakeholder needs and feedback")
        
        # Default challenges if none detected
        if not challenges:
            challenges = [
                "Understanding project requirements and constraints",
                "Balancing functionality with aesthetic considerations",
                "Integrating sustainable design principles effectively"
            ]
        
        # Identify learning points based on interaction patterns
        learning_points = []
        if len(interactions) > 5:
            learning_points.append("Developing systematic approach to design problems")
        if "spatial" in content_lower or "layout" in content_lower:
            learning_points.append("Enhancing spatial reasoning and visualization skills")
        if "communicat" in content_lower or "present" in content_lower:
            learning_points.append("Improving design communication and presentation")
        if "detail" in content_lower or "technical" in content_lower:
            learning_points.append("Understanding technical and construction details")
        if "material" in content_lower or "finish" in content_lower:
            learning_points.append("Learning about material properties and applications")
        if "light" in content_lower or "climate" in content_lower:
            learning_points.append("Integrating environmental and lighting considerations")
        
        # Default learning points if none detected
        if not learning_points:
            learning_points = [
                "Developing systematic approach to design problems",
                "Enhancing spatial reasoning and visualization skills",
                "Improving design communication and presentation"
            ]
        
        return {
            "current_phase": current_phase,
            "phase_progress": phase_progress,
            "session_duration": "Active" if len(interactions) > 0 else "New",
            "challenges": challenges,
            "learning_points": learning_points
        }
    
    def render_phase_progression(self):
        """Render the phase progression dashboard with both phase and agentic methods"""
        st.markdown("## 🎯 Phase Progression Dashboard")
        st.markdown("Structured Socratic assessment with integrated multi-agent mentoring")
        
        # Mode selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Assessment Mode")
            assessment_mode = st.radio(
                "Choose your assessment approach:",
                ["Phase-Based Socratic", "Agentic Mentor", "Combined Mode"],
                help="Phase-Based: Structured 4-step Socratic dialogue\nAgentic: Multi-agent system with cognitive enhancement\nCombined: Both approaches integrated"
            )
        
        with col2:
            st.markdown("### 📊 Session Status")
            if st.session_state.phase_session_id:
                st.success(f"✅ Active Session: {st.session_state.phase_session_id}")
                if st.button("🔄 Reset Session"):
                    st.session_state.phase_session_id = None
                    st.session_state.phase_system = None
                    st.rerun()
            else:
                st.info("⏳ No active session")
        
        # Initialize phase system if needed
        if st.session_state.phase_system is None:
            st.session_state.phase_system = PhaseProgressionSystem()
        
        # Project setup section
        st.markdown("---")
        st.markdown("### 🏗️ Project Setup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_type = st.selectbox(
                "🏢 Project Type:",
                ["Community Center", "Office Building", "Residential Complex", "Cultural Center", "Educational Facility", "Custom Project"],
                help="Select the type of architectural project you're working on"
            )
            
            skill_level = st.selectbox(
                "🎯 Your Skill Level:",
                ["beginner", "intermediate", "advanced"],
                index=1,
                help="This helps tailor the assessment to your experience level"
            )
        
        with col2:
            project_description = st.text_area(
                "📝 Project Description:",
                placeholder="Describe your architectural project, site context, requirements, and goals...",
                height=100,
                help="Provide details about your project to enable personalized assessment"
            )
            
            if st.button("🚀 Start Phase Assessment", type="primary", use_container_width=True):
                if project_description.strip():
                    # Initialize phase session
                    session_id = f"phase_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    st.session_state.phase_session_id = session_id
                    st.session_state.phase_system.start_session(session_id)
                    st.success("✅ Phase assessment session started!")
                    st.rerun()
                else:
                    st.error("📝 Please provide a project description to start assessment")
        
        # Phase progression interface
        if st.session_state.phase_session_id:
            st.markdown("---")
            st.markdown("### 🎯 Phase Assessment")
            
            # Get current session state
            session = st.session_state.phase_system.sessions.get(st.session_state.phase_session_id)
            
            if session:
                # Display current phase and progress
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**📍 Current Phase:** {session.current_phase.value.title()}")
                    phase_progress = session.phase_progress.get(session.current_phase)
                    if phase_progress:
                        completed_steps = len(phase_progress.completed_steps)
                        total_steps = 4
                        progress_percent = (completed_steps / total_steps) * 100
                        st.progress(progress_percent / 100)
                        st.caption(f"Step {completed_steps + 1} of {total_steps}")
                
                with col2:
                    st.markdown(f"**📊 Overall Score:** {session.overall_score:.2f}/5.0")
                    if session.overall_score > 0:
                        st.metric("Average Score", f"{session.overall_score:.2f}")
                
                with col3:
                    # Phase weights display
                    weights = {"Ideation": "25%", "Visualization": "35%", "Materialization": "40%"}
                    st.markdown("**⚖️ Phase Weights:**")
                    for phase, weight in weights.items():
                        st.caption(f"{phase}: {weight}")
                
                # Get next question
                next_question = st.session_state.phase_system.get_next_question(st.session_state.phase_session_id)
                
                if next_question:
                    st.markdown("---")
                    st.markdown("### 🤔 Socratic Question")
                    
                    # Display question with context
                    st.markdown(f"""
                    <div style="background: #2a2a2a; padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3;">
                        <h4 style="color: white; margin-bottom: 10px;">{next_question.step.value.replace('_', ' ').title()}</h4>
                        <p style="color: #f0f0f0; font-size: 16px; line-height: 1.6;">{next_question.question_text}</p>
                        <p style="color: #888; font-size: 12px; margin-top: 10px;">
                            <strong>Phase:</strong> {next_question.phase.value.title()} | 
                            <strong>Keywords:</strong> {', '.join(next_question.keywords[:3])}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Response input
                    user_response = st.text_area(
                        "📝 Your Response:",
                        placeholder="Provide your detailed response to the Socratic question...",
                        height=150,
                        help="Be thorough and thoughtful in your response. Consider multiple perspectives and provide specific examples."
                    )
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.button("📤 Submit Response", type="primary", use_container_width=True):
                            if user_response.strip():
                                # Process response
                                result = st.session_state.phase_system.process_response(st.session_state.phase_session_id, user_response)
                                
                                if "error" not in result:
                                    # Display grading results
                                    st.success("✅ Response submitted and graded!")
                                    
                                    # Show grading breakdown
                                    grade = result['grade']
                                    col1, col2, col3, col4, col5 = st.columns(5)
                                    
                                    with col1:
                                        st.metric("Completeness", f"{grade['completeness']:.1f}/5.0")
                                    with col2:
                                        st.metric("Depth", f"{grade['depth']:.1f}/5.0")
                                    with col3:
                                        st.metric("Relevance", f"{grade['relevance']:.1f}/5.0")
                                    with col4:
                                        st.metric("Innovation", f"{grade['innovation']:.1f}/5.0")
                                    with col5:
                                        st.metric("Technical", f"{grade['technical_understanding']:.1f}/5.0")
                                    
                                    # Show feedback
                                    if grade['strengths']:
                                        st.markdown("**✅ Strengths:**")
                                        for strength in grade['strengths'][:3]:
                                            st.markdown(f"• {strength}")
                                    
                                    if grade['weaknesses']:
                                        st.markdown("**⚠️ Areas for Improvement:**")
                                        for weakness in grade['weaknesses'][:3]:
                                            st.markdown(f"• {weakness}")
                                    
                                    if grade['recommendations']:
                                        st.markdown("**💡 Recommendations:**")
                                        for rec in grade['recommendations'][:3]:
                                            st.markdown(f"• {rec}")
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {result['error']}")
                            else:
                                st.error("📝 Please provide a response before submitting")
                    
                    with col2:
                        if st.button("🔄 Skip Question", use_container_width=True):
                            st.info("Question skipped. Moving to next step...")
                            st.rerun()
                
                else:
                    # Session complete or phase complete
                    if st.session_state.phase_system._is_session_complete(session):
                        st.success("🎉 Congratulations! You've completed all phases!")
                        
                        # Show final summary
                        summary = st.session_state.phase_system.get_session_summary(st.session_state.phase_session_id)
                        
                        st.markdown("### 📊 Final Assessment Summary")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Overall Score", f"{summary['overall_score']:.2f}/5.0")
                            st.metric("Session Duration", f"{summary['session_duration']:.1f} minutes")
                            st.metric("Total Responses", summary['total_responses'])
                        
                        with col2:
                            st.markdown("**📈 Phase Breakdown:**")
                            for phase, phase_summary in summary['phase_summaries'].items():
                                status = "✅" if phase_summary['completed'] else "⏳"
                                st.markdown(f"{status} {phase.title()}: {phase_summary['average_score']:.2f}/5.0")
                        
                        # Export results
                        if st.button("💾 Export Results", type="primary"):
                            save_result = st.session_state.phase_system.save_session(st.session_state.phase_session_id)
                            if "success" in save_result:
                                st.success(f"✅ Results saved to: {save_result['filename']}")
                    else:
                        st.info("🎯 Phase complete! Moving to next phase...")
                        st.rerun()
        
        # Agentic mentor integration
        if assessment_mode in ["Agentic Mentor", "Combined Mode"]:
            st.markdown("---")
            st.markdown("### 🤖 Agentic Mentor Integration")
            
            if st.session_state.phase_session_id:
                st.info("🤖 Agentic mentor is available for additional guidance and cognitive enhancement.")
                
                # Agentic mentor chat interface
                agentic_input = st.text_area(
                    "🤖 Ask the Agentic Mentor:",
                    placeholder="Ask for additional guidance, clarification, or cognitive enhancement...",
                    height=100
                )
                
                if st.button("🤖 Get Agentic Response", use_container_width=True):
                    if agentic_input.strip():
                        with st.spinner("🤖 Processing with multi-agent system..."):
                            try:
                                # Use the orchestrator for agentic response
                                response = asyncio.run(self._process_mentor_mode(agentic_input))
                                
                                st.markdown("**🤖 Agentic Mentor Response:**")
                                st.markdown(f"""
                                <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;">
                                    {response}
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.error("📝 Please provide a question for the agentic mentor")
            else:
                st.warning("⏳ Start a phase assessment session to enable agentic mentor integration")
    
    def render_test_dashboard(self):
        """Render the test dashboard using the full TestDashboard functionality"""
        st.markdown("## 🧪 Test Dashboard")
        st.markdown("Comprehensive testing environment for architectural design evaluation")
        
        # Run the full test dashboard
        self.test_dashboard.run()
    
    def render_test_results(self):
        """Render test results page"""
        st.markdown("### 🧪 Test Results")
        
        if st.session_state.test_results:
            # Display test results
            for test_name, results in st.session_state.test_results.items():
                with st.expander(f"📊 {test_name}"):
                    st.json(results)
        else:
            st.info("No test results available. Run tests to see results here.")
    
    def render_settings(self):
        """Render settings page"""
        st.markdown("### ⚙️ Settings")
        
        # API Configuration
        st.markdown("#### 🔑 API Configuration")
        st.info(f"API Key Status: {'✅ Configured' if self.api_key else '❌ Missing'}")
        
        # System Configuration
        st.markdown("#### 🔧 System Configuration")
        
        # Data collection settings
        st.checkbox("Enable Data Collection", value=True, key="enable_data_collection")
        st.checkbox("Enable Test Mode", value=True, key="enable_test_mode")
        
        # Export settings
        st.markdown("#### 📤 Export Settings")
        st.selectbox("Default Export Format", ["JSON", "CSV", "Excel"], key="default_export_format")
        st.checkbox("Auto-export on session end", value=False, key="auto_export")
    
    def run(self):
        """Main run method"""
        # Single combined flow
        self.render_sidebar()
        self.render_main_chat()

    def _render_inline_pretest(self):
        """Inline pre-test section from test dashboard to keep one-tab flow."""
        try:
            from thesis_tests.assessment_tools import PreTestAssessment
            if 'pre_test_component' not in st.session_state:
                st.session_state.pre_test_component = PreTestAssessment()

            # Render Pre-Test controls in the sidebar instead of main chat
            with st.sidebar:
                st.markdown("### 🧪 Pre-Test (optional)")
                with st.expander("Show/Hide Pre-Test", expanded=False):
                    comp = st.session_state.pre_test_component
                    comp.render_critical_thinking_questions()
                    comp.render_architectural_knowledge_questions()
                    comp.render_spatial_reasoning_questions()
                    if st.button("Save Pre-Test Responses", key="save_pretest_sidebar"):
                        st.success("Pre-test responses saved for this session.")
        except Exception as e:
            st.info("Pre-test tools unavailable. Skipping pre-test section.")

def main():
    """Main function"""
    # Initialize and run dashboard
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 