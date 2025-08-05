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

# Import benchmarking components
from benchmarking.benchmark_dashboard import BenchmarkDashboard
from benchmarking.linkography_analyzer import LinkographySessionAnalyzer

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
        background: #1a1a1a !important;
        color: white !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #2a2a2a !important;
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
        background: #1a1a1a !important;
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
        background: #2a2a2a;
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .greeting {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 1rem;
    }
    
    .compact-text {
        font-size: 14px;
        line-height: 1.4;
        color: #f0f0f0;
    }
    
    /* Chat message styling */
    .chat-message {
        background: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    
    .chat-message.assistant {
        background: #1e1e1e;
        border-left: 4px solid #2196F3;
    }
    
    /* Metric cards */
    .metric-card {
        background: #2a2a2a;
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
        background: #2a2a2a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #404040;
        margin-bottom: 1rem;
    }
    
    /* Chat container */
    .chat-container {
        background: #2a2a2a;
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
    
    if 'benchmark_data' not in st.session_state:
        st.session_state.benchmark_data = {}
    
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

class UnifiedArchitecturalDashboard:
    def __init__(self):
        self.api_key = self._get_api_key()
        if not self.api_key:
            st.error("❌ OPENAI_API_KEY not found. Please set it as an environment variable or in Streamlit secrets.")
            st.stop()
        
        # Initialize components
        self.mentor = MegaArchitecturalMentor(self.api_key)
        self.orchestrator = LangGraphOrchestrator(self.api_key)
        
        # Initialize benchmarking components
        self.benchmark_dashboard = BenchmarkDashboard()
        self.linkography_analyzer = LinkographySessionAnalyzer()
        
        # Initialize test dashboard
        self.test_dashboard = TestDashboard()
        
        # Initialize data collection
        self.data_collector = TestSessionLogger(
            session_id="unified_dashboard_session",
            participant_id="unified_user",
            test_group=TestGroup.MENTOR  # Use proper enum
        )
        
        # Initialize cognitive analyzer using the actual multi-agent system
        self.cognitive_analyzer = self.orchestrator
        
        # Initialize session state
        initialize_session_state()
    
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
            <div style="background: #2a2a2a; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4CAF50;">
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
            <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #2196F3;">
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
            st.info("**Benchmarking**: Data Collection Active")
            
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
                ["Main Chat", "Benchmarking Dashboard", "Test Results", "Settings"]
            )
            
            # Quick benchmarking toggle
            st.markdown("### 📊 Quick Access")
            if st.button("📊 Go to Benchmarking Dashboard", use_container_width=True):
                page = "Benchmarking Dashboard"
            
            if st.button("🧪 Go to Test Results", use_container_width=True):
                page = "Test Results"
            
            return page
    
    def _reset_session(self):
        """Reset the current session"""
        st.session_state.messages = []
        st.session_state.analysis_results = None
        st.session_state.benchmark_data = {}
        st.session_state.test_results = {}
        st.session_state.session_id = None
        st.session_state.analysis_complete = False
        st.success("Session reset successfully!")
    
    def _export_session_data(self):
        """Export session data"""
        if not st.session_state.messages and not st.session_state.benchmark_data:
            st.warning("No data to export")
            return
        
        # Prepare data for export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": st.session_state.current_mode,
            "messages": st.session_state.messages,
            "analysis_results": st.session_state.analysis_results,
            "benchmark_data": st.session_state.benchmark_data,
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
        
        # Collect data for benchmarking (simplified for now)
        try:
            # Log the interaction using the TestSessionLogger's actual methods
            from thesis_tests.data_models import InteractionData, MoveType, TestPhase, Modality, DesignFocus, MoveSource
            from datetime import datetime
            
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
        response = self.test_dashboard.process_generic_ai(user_input)
        
        # Collect data for benchmarking (simplified for now)
        try:
            from thesis_tests.data_models import InteractionData
            from datetime import datetime
            
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
        response = self.test_dashboard.process_control(user_input)
        
        # Collect data for benchmarking (simplified for now)
        try:
            from thesis_tests.data_models import InteractionData
            from datetime import datetime
            
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
            multi-agent mentoring, benchmarking analysis, and research testing capabilities.
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
                            
                        except Exception as e:
                            error_response = f"I apologize, but I encountered an error: {str(e)}"
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_response,
                                "timestamp": datetime.now().isoformat(),
                                "mentor_type": st.session_state.current_mode
                            })
                    
                    st.rerun()
        
        # Analysis results section - show progression and milestones (matching mega_architectural_mentor)
        if st.session_state.analysis_complete and st.session_state.analysis_results:
             with st.columns([1, 2, 1])[1]:  # Center column
                 st.markdown("---")
                 st.markdown("""
                 <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                     📊 Analysis Results
                 </div>
                 """, unsafe_allow_html=True)
                 
                 # Enhanced Cognitive Analysis Dashboard (matching mega_architectural_mentor)
                 with st.expander("🧠 Cognitive Analysis Dashboard", expanded=True):
                     st.markdown("""
                     <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center; color: #1f77b4;">
                         🧠 Your Learning Journey Analysis
                     </div>
                     <style>
                     .stExpander .stMarkdown p { font-size: 13px !important; line-height: 1.3 !important; margin-bottom: 8px !important; }
                     .stExpander .stMarkdown strong { font-size: 13px !important; }
                     .stExpander .stMarkdown div { font-size: 13px !important; }
                     </style>
                     """, unsafe_allow_html=True)
                     
                     # Get analysis data
                     result = st.session_state.analysis_results
                     
                     # Create three columns for different analysis sections
                     col1, col2, col3 = st.columns([1, 1, 1])
                     
                     with col1:
                         st.markdown("**🎯 Current Design Phase**")
                         phase_analysis = result.get('phase_analysis', {})
                         if phase_analysis:
                             current_phase = phase_analysis.get('phase', 'unknown')
                             phase_confidence = phase_analysis.get('confidence', 0)
                             phase_completion = phase_analysis.get('progression_score', 0) * 100
                             
                             # Phase status with color coding
                             if phase_confidence > 0.8:
                                 phase_color = "🟢"
                             elif phase_confidence > 0.6:
                                 phase_color = "🟡"
                             else:
                                 phase_color = "🔴"
                             
                             st.write(f"{phase_color} **{current_phase.title()}**")
                             st.write(f"Confidence: {phase_confidence:.1%}")
                             st.write(f"Progress: {phase_completion:.0f}%")
                             
                             # Show next milestone if available
                             next_milestone = phase_analysis.get('next_milestone')
                             if next_milestone:
                                 milestone_names = {
                                     'site_analysis': 'Site Analysis',
                                     'program_requirements': 'Program Requirements',
                                     'concept_development': 'Concept Development',
                                     'spatial_organization': 'Spatial Organization',
                                     'circulation_design': 'Circulation Design',
                                     'form_development': 'Form Development',
                                     'lighting_strategy': 'Lighting Strategy',
                                     'construction_systems': 'Construction Systems',
                                     'material_selection': 'Material Selection',
                                     'technical_details': 'Technical Details',
                                     'presentation_prep': 'Presentation Preparation',
                                     'documentation': 'Documentation'
                                 }
                                 next_milestone_name = milestone_names.get(next_milestone, next_milestone.replace('_', ' ').title())
                                 st.write(f"🎯 **Next:** {next_milestone_name}")
                         else:
                             st.write("🔍 Phase not detected yet")
                     
                     with col2:
                         st.markdown("**💡 Learning Insights**")
                         synthesis = result.get('synthesis', {})
                         
                         # Cognitive Challenges
                         cognitive_challenges = synthesis.get('cognitive_challenges', [])
                         if cognitive_challenges:
                             st.write(f"🚧 **Challenges** ({len(cognitive_challenges)}):")
                             for challenge in cognitive_challenges[:3]:  # Show top 3
                                 challenge_name = challenge.replace('_', ' ').title()
                                 st.write(f"• {challenge_name}")
                             if len(cognitive_challenges) > 3:
                                 st.write(f"• ... and {len(cognitive_challenges) - 3} more")
                         else:
                             st.write("✅ No major challenges detected")
                         
                         # Learning Opportunities
                         learning_opportunities = synthesis.get('learning_opportunities', [])
                         if learning_opportunities:
                             st.write(f"🌟 **Opportunities** ({len(learning_opportunities)}):")
                             for opportunity in learning_opportunities[:3]:  # Show top 3
                                 st.write(f"• {opportunity}")
                             if len(learning_opportunities) > 3:
                                 st.write(f"• ... and {len(learning_opportunities) - 3} more")
                         else:
                             st.write("📚 Ready for new challenges")
                     
                     with col3:
                         st.markdown("**📋 Project Context**")
                         text_analysis = result.get('text_analysis', {})
                         
                         # Building Type
                         building_type = text_analysis.get('building_type', 'unknown')
                         if building_type != 'unknown':
                             st.write(f"🏗️ **Type:** {building_type.title()}")
                         else:
                             st.write("🏗️ **Type:** Not specified")
                         
                         # Program Requirements
                         requirements = text_analysis.get('program_requirements', [])
                         if requirements:
                             st.write(f"📝 **Requirements** ({len(requirements)}):")
                             for req in requirements[:2]:  # Show top 2
                                 st.write(f"• {req}")
                             if len(requirements) > 2:
                                 st.write(f"• ... and {len(requirements) - 2} more")
                         else:
                             st.write("📝 **Requirements:** Not specified")
                         
                         # Missing Considerations
                         missing_considerations = synthesis.get('missing_considerations', [])
                         if missing_considerations:
                             st.write(f"⚠️ **Missing** ({len(missing_considerations)}):")
                             for consideration in missing_considerations[:2]:  # Show top 2
                                 st.write(f"• {consideration}")
                             if len(missing_considerations) > 2:
                                 st.write(f"• ... and {len(missing_considerations) - 2} more")
                     
                     # Dynamic recommendations section
                     has_recommendations = False
                     
                     # Check if we have any meaningful recommendations
                     next_focus_areas = synthesis.get('next_focus_areas', [])
                     phase_recommendations = phase_analysis.get('phase_recommendations', [])
                     missing_considerations = synthesis.get('missing_considerations', [])
                     
                     if next_focus_areas or phase_recommendations or missing_considerations:
                         has_recommendations = True
                         st.markdown("---")
                         st.markdown("**🎯 Smart Recommendations**")
                         
                         # Next Focus Areas
                         if next_focus_areas:
                             st.write("**Focus on these areas next:**")
                             for i, focus in enumerate(next_focus_areas[:3], 1):  # Show top 3
                                 focus_name = focus.replace('_', ' ').title()
                                 st.write(f"{i}. {focus_name}")
                         
                         # Phase Recommendations
                         if phase_recommendations:
                             st.write("**Phase-specific guidance:**")
                             for rec in phase_recommendations[:2]:  # Show top 2
                                 st.write(f"• {rec}")
                         
                         # Missing Considerations
                         if missing_considerations:
                             st.write("**Consider addressing:**")
                             for consideration in missing_considerations[:2]:  # Show top 2
                                 st.write(f"• {consideration}")
                     
                     # Overall progress summary
                     if phase_analysis:
                         completed_milestones = phase_analysis.get('completed_milestones', 0)
                         total_milestones = phase_analysis.get('total_milestones', 0)
                         phase_completion = phase_analysis.get('progression_score', 0) * 100
                         
                         if total_milestones > 0:
                             if completed_milestones > 0:
                                 st.markdown("---")
                                 st.markdown(f"**📊 Overall Progress: {completed_milestones}/{total_milestones} milestones completed**")
                                 
                                 # Progress visualization
                                 progress_ratio = completed_milestones / total_milestones
                                 st.progress(progress_ratio)
                                 
                                 if progress_ratio < 0.25:
                                     st.write("🔄 **Getting Started** - Building foundational knowledge")
                                 elif progress_ratio < 0.5:
                                     st.write("📝 **In Progress** - Developing design thinking")
                                 elif progress_ratio < 0.75:
                                     st.write("🎯 **Making Good Progress** - Applying concepts effectively")
                                 elif progress_ratio < 1.0:
                                     st.write("✨ **Almost Complete** - Refining and polishing")
                                 else:
                                     st.write("✅ **Project Complete** - Excellent work!")
                             else:
                                 # Show phase-based progress when no milestones completed
                                 st.markdown("---")
                                 st.markdown(f"**📊 Phase Progress: {phase_completion:.0f}% complete**")
                                 
                                 # Progress visualization
                                 progress_ratio = phase_completion / 100
                                 st.progress(progress_ratio)
                                 
                                 if progress_ratio < 0.25:
                                     st.write("🔄 **Getting Started** - Building foundational knowledge")
                                 elif progress_ratio < 0.5:
                                     st.write("📝 **In Progress** - Developing design thinking")
                                 elif progress_ratio < 0.75:
                                     st.write("🎯 **Making Good Progress** - Applying concepts effectively")
                                 elif progress_ratio < 1.0:
                                     st.write("✨ **Almost Complete** - Refining and polishing")
                                 else:
                                     st.write("✅ **Phase Complete** - Ready for next phase!")
                         else:
                             # Fallback to phase-based progress
                             st.markdown("---")
                             st.markdown(f"**📊 Phase Progress: {phase_completion:.0f}% complete**")
                             
                             # Progress visualization
                             progress_ratio = phase_completion / 100
                             st.progress(progress_ratio)
                             
                             if progress_ratio < 0.25:
                                 st.write("🔄 **Getting Started** - Building foundational knowledge")
                             elif progress_ratio < 0.5:
                                 st.write("📝 **In Progress** - Developing design thinking")
                             elif progress_ratio < 0.75:
                                 st.write("🎯 **Making Good Progress** - Applying concepts effectively")
                             elif progress_ratio < 1.0:
                                 st.write("✨ **Almost Complete** - Refining and polishing")
                             else:
                                 st.write("✅ **Phase Complete** - Ready for next phase!")
     
    def render_benchmarking_dashboard(self):
        """Render the benchmarking dashboard"""
        st.markdown("### 📊 Benchmarking Dashboard")
        
        # Get session data
        if st.session_state.session_id:
            try:
                # Try to get session data from the TestSessionLogger
                session_data = {
                    "session_id": st.session_state.session_id,
                    "interactions": self.data_collector.interactions,
                    "duration": (datetime.now() - self.data_collector.session_start_time).total_seconds()
                }
                
                if session_data["interactions"]:
                    # Create tabs for different benchmarking views
                    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Cognitive Analysis", "Linkography", "Raw Data"])
                    
                    with tab1:
                        self._render_overview_tab(session_data)
                    
                    with tab2:
                        self._render_cognitive_analysis_tab(session_data)
                    
                    with tab3:
                        self._render_linkography_tab(session_data)
                    
                    with tab4:
                        self._render_raw_data_tab(session_data)
                else:
                    st.info("No session data available. Start a conversation to see benchmarking data.")
            except Exception as e:
                st.error(f"Error loading session data: {e}")
                st.info("No session data available. Start a conversation to begin data collection.")
        else:
            st.info("No active session. Start a conversation to begin data collection.")
    
    def _render_overview_tab(self, session_data: Dict):
        """Render overview tab"""
        st.markdown("#### 📈 Session Overview")
        
        # Basic metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Interactions", len(session_data.get("interactions", [])))
        
        with col2:
            st.metric("Session Duration", f"{session_data.get('duration', 0):.1f}s")
        
        with col3:
            st.metric("User Inputs", len([i for i in session_data.get("interactions", []) if hasattr(i, 'student_input')]))
        
        with col4:
            st.metric("AI Responses", len([i for i in session_data.get("interactions", []) if hasattr(i, 'agent_response')]))
        
        # Interaction timeline
        if session_data.get("interactions"):
            st.markdown("#### 📅 Interaction Timeline")
            
            # Create timeline data
            timeline_data = []
            for interaction in session_data["interactions"]:
                if hasattr(interaction, 'timestamp') and hasattr(interaction, 'student_input'):
                    timeline_data.append({
                        "timestamp": interaction.timestamp.strftime("%H:%M:%S") if hasattr(interaction.timestamp, 'strftime') else str(interaction.timestamp),
                        "type": "user_input",
                        "mode": getattr(interaction, 'metadata', {}).get("mode", "Unknown"),
                        "content": str(interaction.student_input)[:50] + "..."
                    })
                if hasattr(interaction, 'timestamp') and hasattr(interaction, 'agent_response'):
                    timeline_data.append({
                        "timestamp": interaction.timestamp.strftime("%H:%M:%S") if hasattr(interaction.timestamp, 'strftime') else str(interaction.timestamp),
                        "type": "ai_response",
                        "mode": getattr(interaction, 'metadata', {}).get("mode", "Unknown"),
                        "content": str(interaction.agent_response)[:50] + "..."
                    })
            
            if timeline_data:
                df = pd.DataFrame(timeline_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No interaction data available yet.")
    
    def _render_cognitive_analysis_tab(self, session_data: Dict):
        """Render cognitive analysis tab using the actual multi-agent system"""
        st.markdown("#### 🧠 Cognitive Analysis")
        
        # Use the actual multi-agent system for cognitive analysis
        if session_data.get("interactions"):
            st.markdown("**Multi-Agent Cognitive Analysis**")
            
            # Display agent interactions and routing decisions
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Agent Interactions**")
                agent_interactions = [i for i in session_data.get("interactions", []) 
                                    if i.get("data", {}).get("mode") == "MENTOR"]
                st.metric("Multi-Agent Interactions", len(agent_interactions))
                
                # Show agent routing patterns
                if agent_interactions:
                    st.markdown("**Agent Routing Patterns**")
                    routing_patterns = {}
                    for interaction in agent_interactions:
                        mode = interaction.get("data", {}).get("mode", "Unknown")
                        routing_patterns[mode] = routing_patterns.get(mode, 0) + 1
                    
                    for agent, count in routing_patterns.items():
                        st.metric(f"{agent} Agent", count)
            
            with col2:
                st.markdown("**Cognitive Enhancement Interventions**")
                cognitive_interventions = [i for i in session_data.get("interactions", []) 
                                         if "cognitive" in str(i).lower()]
                st.metric("Cognitive Interventions", len(cognitive_interventions))
                
                # Show design thinking phases from multi-agent analysis
                st.markdown("**Design Thinking Phases**")
                phases = {
                    "Analysis": len([i for i in agent_interactions if "analysis" in str(i).lower()]),
                    "Socratic": len([i for i in agent_interactions if "socratic" in str(i).lower()]),
                    "Domain Expert": len([i for i in agent_interactions if "domain" in str(i).lower()]),
                    "Cognitive Enhancement": len(cognitive_interventions)
                }
                
                for phase, count in phases.items():
                    st.metric(phase, count)
            
            # Show detailed multi-agent analysis
            st.markdown("#### 🤖 Multi-Agent System Analysis")
            
            # Display recent interactions with agent details
            if agent_interactions:
                st.markdown("**Recent Multi-Agent Interactions**")
                recent_interactions = agent_interactions[-5:]  # Show last 5
                
                for interaction in recent_interactions:
                    with st.expander(f"Interaction at {interaction.get('timestamp', 'Unknown')}"):
                        st.markdown(f"**Mode**: {interaction.get('data', {}).get('mode', 'Unknown')}")
                        st.markdown(f"**Type**: {interaction.get('type', 'Unknown')}")
                        content = interaction.get('data', {}).get('input', interaction.get('data', {}).get('response', ''))
                        st.markdown(f"**Content**: {str(content)[:200]}...")
            
            # Show LangGraph routing visualization
            st.markdown("#### 🔄 LangGraph Routing Analysis")
            st.info("""
            **Multi-Agent Routing System**:
            - **Analysis Agent**: Processes design briefs and generates detailed analysis
            - **Socratic Agent**: Provides guided questioning and learning
            - **Domain Expert Agent**: Offers specialized architectural knowledge
            - **Cognitive Enhancement Agent**: Prevents cognitive offloading and promotes learning
            - **Context Agent**: Manages conversation flow and routing decisions
            """)
            
            # Display routing metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Agent Calls", len(agent_interactions))
            with col2:
                st.metric("Routing Decisions", len([i for i in agent_interactions if i.get("type") == "ai_response"]))
            with col3:
                st.metric("Cognitive Interventions", len(cognitive_interventions))
    
    def _render_linkography_tab(self, session_data: Dict):
        """Render linkography analysis tab"""
        st.markdown("#### 🔗 Linkography Analysis")
        
        if session_data.get("interactions"):
            # Perform linkography analysis
            linkography = self.linkography_analyzer.analyze_session(session_data)
            
            # Display linkography metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Links", linkography.get("total_links", 0))
            
            with col2:
                st.metric("Link Density", f"{linkography.get('link_density', 0):.2f}")
            
            with col3:
                st.metric("Critical Moves", linkography.get("critical_moves", 0))
            
            # Linkography visualization
            if "link_graph" in linkography:
                st.markdown("#### 🔗 Link Graph")
                
                # Create network visualization
                nodes = linkography["link_graph"].get("nodes", [])
                edges = linkography["link_graph"].get("edges", [])
                
                if nodes and edges:
                    # Create a simple network visualization
                    st.markdown("**Interaction Network**")
                    
                    # Display as a table for now
                    edge_data = []
                    for edge in edges:
                        edge_data.append({
                            "From": edge.get("from", ""),
                            "To": edge.get("to", ""),
                            "Type": edge.get("type", ""),
                            "Weight": edge.get("weight", 0)
                        })
                    
                    df = pd.DataFrame(edge_data)
                    st.dataframe(df, use_container_width=True)
    
    def _render_raw_data_tab(self, session_data: Dict):
        """Render raw data tab"""
        st.markdown("#### 📋 Raw Session Data")
        
        # Display raw session data
        st.json(session_data)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download JSON"):
                json_str = json.dumps(session_data, indent=2, default=str)
                st.download_button(
                    label="Download",
                    data=json_str,
                    file_name=f"session_data_{st.session_state.session_id}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export to CSV"):
                # Convert interactions to CSV
                if session_data.get("interactions"):
                    df = pd.DataFrame(session_data["interactions"])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"session_data_{st.session_state.session_id}.csv",
                        mime="text/csv"
                    )
    
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
        st.checkbox("Enable Benchmarking", value=True, key="enable_benchmarking")
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
        elif current_page == "Benchmarking Dashboard":
            self.render_benchmarking_dashboard()
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