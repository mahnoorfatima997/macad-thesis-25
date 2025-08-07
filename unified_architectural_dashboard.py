import streamlit as st
import os
import asyncio
import json
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
from mega_architectural_mentor import MegaArchitecturalMentor

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

# Benchmarking components removed

# Import test dashboard components
from thesis_tests.test_dashboard import TestDashboard

# Import data collection components                                    
from thesis_tests.logging_system import TestSessionLogger
from thesis_tests.data_models import TestGroup, TestPhase
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
    
    # Performance optimization: Cache components
    if 'dashboard_initialized' not in st.session_state:
        st.session_state.dashboard_initialized = False

class UnifiedArchitecturalDashboard:
    def __init__(self):
        self.api_key = self._get_api_key()
        if not self.api_key:
            st.error("❌ OPENAI_API_KEY not found. Please set it as an environment variable or in Streamlit secrets.")
            st.stop()
        
        # Initialize session state first
        initialize_session_state()
        
        # Performance optimization: Use cached components
        if not st.session_state.dashboard_initialized:
            with st.spinner("🚀 Initializing dashboard components..."):
                # Initialize components only once
                self.mentor = MegaArchitecturalMentor(self.api_key)
                self.orchestrator = LangGraphOrchestrator(self.api_key)
                self.test_dashboard = TestDashboard()
                self.data_collector = TestSessionLogger(
                    session_id="unified_dashboard_session",
                    participant_id="unified_user",
                    test_group=TestGroup.MENTOR
                )
                self.cognitive_analyzer = self.orchestrator
                
                # Cache components in session state
                st.session_state.mentor = self.mentor
                st.session_state.orchestrator = self.orchestrator
                st.session_state.test_dashboard = self.test_dashboard
                st.session_state.data_collector = self.data_collector
                st.session_state.cognitive_analyzer = self.cognitive_analyzer
                st.session_state.dashboard_initialized = True
        else:
            # Use cached components
            self.mentor = st.session_state.mentor
            self.orchestrator = st.session_state.orchestrator
            self.test_dashboard = st.session_state.test_dashboard
            self.data_collector = st.session_state.data_collector
            self.cognitive_analyzer = st.session_state.cognitive_analyzer
    
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
        """Render the sidebar with configuration options (matching mega_architectural_mentor style)"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # API Key status
            if self.api_key:
                st.success("✅ API Key: Configured")
            else:
                st.error("❌ API Key: Missing")
            
            # System status
            st.markdown("### 🔧 System Status")
            st.info("**Vision**: GPT Vision Available")
            st.info("**Agents**: Multi-Agent System Ready")
            
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
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            
            # Main navigation
            page = st.selectbox(
                "Select Page",
                ["Main Chat", "Test Dashboard", "Test Results", "Settings"]
            )
            
            # Navigation handled by dropdown menu above
            
            return page
    
    def _reset_session(self):
        """Reset the current session"""
        st.session_state.messages = []
        st.session_state.analysis_results = None
        st.session_state.test_results = {}
        st.session_state.session_id = None
        st.session_state.analysis_complete = False
        st.success("Session reset successfully!")
    
    def _export_session_data(self):
        """Export session data"""
        if not st.session_state.messages:
            st.warning("No data to export")
            return
        
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
        
        # Add the current user input to the state
        state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Process with orchestrator
        result = await self.orchestrator.process_student_input(state)
        response = result.get("response", "I apologize, but I couldn't generate a response.")
        
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
                 metadata={"mode": "MENTOR", "routing_path": "mentor_mode", "agents_used": ["orchestrator"]}
             )
            
            self.data_collector.log_interaction(interaction)
        except Exception as e:
            print(f"Warning: Could not log interaction: {e}")
        
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
        """Render the main chat interface (matching mega_architectural_mentor style)"""
        
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
        
        # Mode selection in center column (matching mega_architectural_mentor style)
        with st.columns([1, 2, 1])[1]:  # Center column
            st.markdown("""
            <div class="compact-text" style="font-size: 14px; font-weight: bold; margin-bottom: 10px; text-align: center;">
                🧪 Testing Mode Configuration
            </div>
            """, unsafe_allow_html=True)
            
            # Mode selection dropdown (matching mega_architectural_mentor style)
            current_mode = st.selectbox(
                "🤖 Select Testing Mode:",
                ["MENTOR", "GENERIC_AI", "CONTROL"],
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
            
            # Start analysis button
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
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
                                    results = loop.run_until_complete(
                                        self.mentor.analyze_design(
                                            design_brief=project_description,
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
                            
                            st.success("✅ Analysis complete! Let's continue our conversation.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
        
        # Chat interface (if analysis is complete)
        if st.session_state.analysis_complete:
            # Mentor acknowledgment
            if len(st.session_state.messages) == 0:
                with st.columns([1, 2, 1])[1]:  # Center column
                    st.markdown("---")
                    st.markdown("""
                    <div style="background: #2a2a2a; padding: 20px; border-radius: 10px; margin: 20px 0; 
                                border-left: 5px solid #4CAF50;">
                        <div style="color: white; font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                            🎓 Mentor Ready
                        </div>
                        <div style="color: #f0f0f0; font-size: 14px; line-height: 1.5;">
                            I've analyzed your <strong>{building_type}</strong> project and identified key areas for exploration. 
                            I'm ready to help you with specific questions about design improvements, technical requirements, 
                            precedents, or any aspect you'd like to explore further. What would you like to focus on?
                        </div>
                    </div>
                    """.format(
                        building_type=st.session_state.analysis_results.get('text_analysis', {}).get('building_type', 'architectural').title()
                    ), unsafe_allow_html=True)
            
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
                    
                    # Log to data collector - create InteractionData object
                    try:
                        from thesis_tests.data_models import InteractionData, TestPhase
                        
                        interaction_data = InteractionData(
                            id=str(uuid.uuid4()),
                            session_id=st.session_state.session_id,
                            timestamp=datetime.now(),
                            phase=TestPhase.IDEATION,  # Default phase
                            interaction_type="chat",
                            user_input=user_input,
                            system_response="Processing...",
                            response_time=0.0,
                            metadata={"mode": st.session_state.current_mode, "type": "user_input"}
                        )
                        self.data_collector.log_interaction(interaction_data)
                    except Exception as e:
                        st.warning(f"Data logging error: {e}")
                    
                    # Display user message
                    self.render_chat_message({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Generate response
                    with st.spinner("🧠 Thinking..."):
                        try:
                            # Process response based on current mode
                            response = asyncio.run(self.process_chat_response(user_input, st.session_state.current_mode))
                            
                            # Add assistant message to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response,
                                "timestamp": datetime.now().isoformat(),
                                "mentor_type": st.session_state.current_mode
                            })
                            
                            # Update data collector with response - update the last interaction
                            try:
                                if self.data_collector.interactions:
                                    # Update the last interaction's system_response
                                    self.data_collector.interactions[-1].system_response = response
                                    # Re-log the updated interaction
                                    self.data_collector.log_interaction(self.data_collector.interactions[-1])
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
        if len(st.session_state.messages) > 0:
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
                    
                    # Analyze phase progression
                    phase_analysis = self._analyze_phase_progression(chat_interactions)
                    
                    # Display phase progression
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Current Design Phase**")
                        current_phase = phase_analysis.get('current_phase', 'Exploration')
                        phase_progress = phase_analysis.get('phase_progress', 0)
                        
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
                        challenges = phase_analysis.get('challenges', [
                            "Understanding project requirements",
                            "Balancing functionality and aesthetics",
                            "Integrating sustainable design principles"
                        ])
                        
                        for challenge in challenges[:3]:  # Show top 3 challenges
                            st.markdown(f"• {challenge}")
                        
                        st.markdown("**💡 Learning Points**")
                        learning_points = phase_analysis.get('learning_points', [
                            "Developing systematic approach to design",
                            "Enhancing spatial reasoning skills",
                            "Improving design communication"
                        ])
                        
                        for point in learning_points[:3]:  # Show top 3 learning points
                            st.markdown(f"• {point}")
                    
                    # Session summary
                    st.markdown("---")
                    st.markdown("**📊 Session Summary**")
                    total_interactions = len(chat_interactions)
                    session_duration = phase_analysis.get('session_duration', 'Ongoing')
                    
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
        # Render sidebar and get current page
        current_page = self.render_sidebar()
        
        # Render main content based on page
        if current_page == "Main Chat":
            self.render_main_chat()
        elif current_page == "Test Dashboard":
            self.render_test_dashboard()
        elif current_page == "Test Results":
            self.render_test_results()
        elif current_page == "Settings":
            self.render_settings()

def main():
    """Main function"""
    # Initialize and run dashboard
    dashboard = UnifiedArchitecturalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 