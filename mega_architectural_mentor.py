#!/usr/bin/env python3
"""
Mega Architectural Mentor - Unified AI System
Clean, modern chatbot interface with hover sidebar
"""

import streamlit as st
import os
import asyncio
import tempfile
import json
from datetime import datetime
import base64
from PIL import Image
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path

# Import all the thesis-agents components
import sys
sys.path.append('./thesis-agents')

from state_manager import ArchMentorState, VisualArtifact, StudentProfile
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from agents.domain_expert import DomainExpertAgent
from agents.cognitive_enhancement import CognitiveEnhancementAgent
from agents.context_agent import ContextAgent
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
from vision.gpt_sam_analyzer import GPTSAMAnalyzer
from data_collection.interaction_logger import InteractionLogger

# Import detection components (SAM is included in requirements)
try:
    sys.path.append('./src/core/detection')
    from sam2_module_fixed import SAM2Segmenter
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("⚠️ SAM2 module not available - check installation")

# Configure Streamlit for clean interface
st.set_page_config(
    page_title="🏗️ Architectural Mentor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern interface
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
    
    .upgrade-link {
        color: #ff6b35;
        text-decoration: none;
        margin-left: 8px;
    }
    
    .greeting {
        font-size: 2rem;
        color: white;
        margin-bottom: 2rem;
    }
    
    .greeting-icon {
        color: #ff6b35;
        margin-right: 8px;
    }
    
    /* Main chat input area */
    .chat-input-container {
        background: #2a2a2a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0 auto;
        max-width: 800px;
        position: relative;
        border: 1px solid #404040;
    }
    
    .chat-input {
        background: transparent;
        border: none;
        color: white;
        font-size: 1.1rem;
        width: 100%;
        min-height: 60px;
        resize: none;
        outline: none;
    }
    
    .chat-input::placeholder {
        color: #888;
    }
    
    /* Input controls */
    .input-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #404040;
    }
    
    .left-controls {
        display: flex;
        gap: 8px;
    }
    
    .control-button {
        background: #404040;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .control-button:hover {
        background: #505050;
    }
    
    .model-selector {
        color: white;
        background: transparent;
        border: none;
        font-size: 0.9rem;
        cursor: pointer;
    }
    
    .send-button {
        background: #ff6b35;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 500;
    }
    
    .send-button:hover {
        background: #e55a2b;
    }
    
    /* Action buttons */
    .action-buttons {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .action-button {
        background: transparent;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 8px 16px;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    
    .action-button:hover {
        background: #2a2a2a;
        border-color: #ff6b35;
    }
    
    /* Left sidebar */
    .left-sidebar {
        position: fixed;
        left: 0;
        top: 0;
        width: 120px;
        height: 100vh;
        background: #2a2a2a;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1rem 0;
        z-index: 1000;
        font-size: 11px;
        color: #ccc;
    }
    
    .sidebar-info {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        padding: 0.5rem;
    }
    
    .info-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 0.8rem;
        text-align: center;
        width: 100%;
    }
    
    .info-label {
        font-weight: bold;
        color: #888;
        margin-bottom: 0.2rem;
        font-size: 10px;
    }
    
    .info-value {
        color: #fff;
        font-size: 11px;
        background: #404040;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        min-width: 60px;
        text-align: center;
    }
    
    /* Chat messages */
    .chat-message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 8px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .user-message {
        background: #2a2a2a;
        border-left: 4px solid #ff6b35;
    }
    
    .assistant-message {
        background: #2a2a2a;
        border-left: 4px solid #4CAF50;
    }
    
    /* Dropdown styling */
    .stSelectbox > div > div {
        background: #404040 !important;
        color: white !important;
        border: 1px solid #505050 !important;
    }
    
    .stSelectbox > div > div:hover {
        background: #505050 !important;
    }
    
    /* Hide labels */
    .stSelectbox label {
        display: none !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: transparent !important;
        border: none !important;
    }
    
    .stFileUploader label {
        display: none !important;
    }
    
    /* Compact text styling */
    .compact-text {
        font-size: 12px;
        color: #888;
        line-height: 1.4;
        margin-bottom: 10px;
    }
    
    /* Configuration container styling */
    .config-container {
        background: #2a2a2a;
        border: 1px solid #404040;
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        max-width: 600px;
    }
    
    /* Smaller button styling */
    .small-button {
        max-width: 200px;
        margin: 0 auto;
    }
    
    /* Compact radio and checkbox styling */
    .stRadio > div {
        font-size: 12px !important;
    }
    
    .stCheckbox > div {
        font-size: 12px !important;
    }
    
    .stSelectbox > div {
        font-size: 12px !important;
    }
    

""", unsafe_allow_html=True)

# Initialize session state with a helper function
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'analysis_complete': False,
        'chat_messages': [],
        'arch_state': None,
        'analysis_result': None,
        'gpt_sam_results': None,
        'uploaded_image_path': None,
        'interaction_logger': InteractionLogger(),
        'orchestrator': None,
        'use_sam': False,
        'input_mode': "Text Only",
        'mentor_type': "Socratic Agent" # Added for new logic
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize session state
initialize_session_state()

class MegaArchitecturalMentor:
    """Main orchestrator class for the Mega Architectural Mentor system"""
    
    def __init__(self, api_key: str, use_sam: bool = False):
        self.api_key = api_key
        self.use_sam = use_sam and SAM_AVAILABLE
        self.gpt_sam_analyzer = None
        self.orchestrator = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize GPT-SAM analyzer (SAM is optional)
            self.gpt_sam_analyzer = GPTSAMAnalyzer(self.api_key)
            print(f"✅ GPT Vision initialized (SAM: {'enabled' if self.use_sam else 'disabled'})")
            
            # Initialize orchestrator
            self.orchestrator = LangGraphOrchestrator(domain="architecture")
            print("✅ Multi-agent orchestrator initialized")
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            raise
    
    async def analyze_design(self, design_brief: str, image_path: Optional[str] = None, 
                           skill_level: str = "intermediate", domain: str = "architecture") -> Dict[str, Any]:
        """Main analysis pipeline that handles text-only, image-only, and image+text scenarios"""
        
        # Step 1: Initialize state
        state = ArchMentorState()
        state.current_design_brief = design_brief
        state.student_profile = StudentProfile(skill_level=skill_level)
        state.domain = domain
        
        # Add a user message to trigger LLM analysis instead of edge case handler
        state.messages = [
            {"role": "user", "content": f"I'm working on my {design_brief.lower()} and need help with the design process."}
        ]
        
        # Step 2: Handle image if provided
        gpt_sam_results = None
        vision_available = False
        
        if image_path and os.path.exists(image_path):
            vision_available = True
            artifact = VisualArtifact(
                id="uploaded_sketch",
                type="sketch",
                image_path=image_path
            )
            state.current_sketch = artifact
            state.visual_artifacts.append(artifact)
            
            # Step 3: Run vision analysis (if SAM enabled)
            if self.use_sam and self.gpt_sam_analyzer:
                try:
                    gpt_sam_results = self.gpt_sam_analyzer.analyze_image(image_path)
                    print(f"✅ Vision analysis completed with SAM: {'enabled' if self.use_sam else 'disabled'}")
                except Exception as e:
                    print(f"⚠️ Vision analysis failed: {e}")
                    gpt_sam_results = {"error": f"Vision analysis failed: {str(e)}"}
            else:
                # Basic GPT Vision analysis without SAM
                try:
                    if self.gpt_sam_analyzer:
                        gpt_sam_results = self.gpt_sam_analyzer.analyze_with_coordinates(image_path)
                        print("✅ Basic GPT Vision analysis completed")
                except Exception as e:
                    print(f"⚠️ Basic vision analysis failed: {e}")
                    gpt_sam_results = {"error": f"Basic vision analysis failed: {str(e)}"}
        
        # Step 4: Run cognitive analysis
        analysis_agent = AnalysisAgent(domain)
        analysis_result = await analysis_agent.process(state)
        
        # Step 5: Return comprehensive results
        return {
            "state": state,
            "analysis_result": analysis_result,
            "gpt_sam_results": gpt_sam_results,
            "vision_available": vision_available,
            "sam_enabled": self.use_sam and vision_available
        }
    
    async def process_chat_message(self, user_input: str, state: ArchMentorState) -> Dict[str, Any]:
        """Process a chat message through the multi-agent system"""
        if not self.orchestrator:
            raise Exception("Orchestrator not initialized")
        
        # Update state with user message
        state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Process through LangGraph workflow
        result = await self.orchestrator.process_student_input(state)
        
        # Update state with assistant response
        state.messages.append({
            "role": "assistant",
            "content": result["response"]
        })
        
        return result

def render_left_sidebar():
    """Render the left sidebar with app information"""
    # Get current mode from session state
    current_mode = st.session_state.get('input_mode', 'Text Only')
    sam_status = "Enabled" if st.session_state.get('use_sam', False) else "Disabled"
    
    st.markdown(f"""
    <div class="left-sidebar">
        <div class="sidebar-info">
            <div class="info-item">
                <span class="info-label">Mode:</span>
                <span class="info-value">{current_mode}</span>
            </div>
            <div class="info-item">
                <span class="info-label">SAM:</span>
                <span class="info-value">{sam_status}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Status:</span>
                <span class="info-value">Ready</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add benchmarking section
    st.markdown("---")
    st.markdown("**📊 Benchmarking**")
    
    # Check if benchmarking results exist
    benchmark_results_path = Path("benchmarking/results/benchmark_report.json")
    if benchmark_results_path.exists():
        st.success("✅ Results available")
        if st.button("📈 View Dashboard", use_container_width=True):
            # Launch benchmarking dashboard in new tab
            import subprocess
            import sys
            dashboard_path = Path("benchmarking/benchmark_dashboard.py")
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                str(dashboard_path), "--server.port", "8502"
            ])
            st.info("🌐 Dashboard opening in new tab...")
    else:
        st.warning("⚠️ No results yet")
        if st.button("🔬 Run Benchmarking", use_container_width=True):
            # Run benchmarking analysis
            import subprocess
            import sys
            st.info("🧠 Running cognitive benchmarking analysis...")
            try:
                result = subprocess.run([
                    sys.executable, "benchmarking/run_benchmarking.py"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Benchmarking complete! Click 'View Dashboard' to see results.")
                else:
                    st.error(f"❌ Benchmarking failed: {result.stderr}")
            except Exception as e:
                st.error(f"❌ Error running benchmarking: {str(e)}")

def render_chat_message(message: Dict[str, Any]):
    """Render a chat message with appropriate styling"""
    
    if message["role"] == "user":
        st.markdown(f"""
        <div style="background: #2a2a2a; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4CAF50;">
            <strong>You:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Get mentor type for display
        mentor_type = message.get("mentor_type", "Socratic Agent")
        mentor_icon = "🤖" if mentor_type == "Raw GPT" else "🏗️"
        mentor_label = f"{mentor_icon} {mentor_type}"
        
        st.markdown(f"""
        <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #2196F3;">
            <strong>{mentor_label}:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)

def run_async_analysis(mentor, design_brief: str, temp_image_path: Optional[str], 
                      skill_level: str) -> Dict[str, Any]:
    """Run the analysis pipeline asynchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(
            mentor.analyze_design(
                design_brief=design_brief,
                image_path=temp_image_path,
                skill_level=skill_level,
                domain="architecture"
            )
        )
        return results
    finally:
        loop.close()

def get_raw_gpt_response(user_input: str, project_context: str = "") -> Dict[str, Any]:
    """Get a direct GPT response for comparison with the Socratic agent"""
    
    try:
        from openai import OpenAI
        import os
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a prompt for direct GPT response
        prompt = f"""
        You are an architectural expert. Answer this student's question directly and comprehensively:
        
        STUDENT QUESTION: "{user_input}"
        PROJECT CONTEXT: {project_context}
        
        Provide a detailed, informative answer that directly addresses their question. 
        Give specific architectural advice, examples, and technical information.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,  # Increased from 400 to prevent cut-off responses
            temperature=0.3
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        return {
            "response": raw_response,
            "metadata": {
                "response_type": "raw_gpt",
                "agents_used": ["gpt-4o"],
                "interaction_type": "direct_answer",
                "confidence_level": "high",
                "understanding_level": "high",
                "engagement_level": "medium",
                "sources": [],
                "response_time": 0,
                "routing_path": "raw_gpt"
            },
            "routing_path": "raw_gpt",
            "classification": {
                "interaction_type": "direct_answer",
                "confidence_level": "high",
                "understanding_level": "high",
                "engagement_level": "medium"
            }
        }
        
    except Exception as e:
        print(f"❌ Raw GPT response failed: {e}")
        return {
            "response": "I apologize, but I'm unable to provide a response at the moment. Please try again.",
            "metadata": {
                "response_type": "error",
                "agents_used": [],
                "error": str(e)
            },
            "routing_path": "error",
            "classification": {}
        }

def process_chat_response(user_input: str) -> Dict[str, Any]:
    """Process chat response through orchestrator or raw GPT based on mentor type"""
    
    print(f"💬 Processing chat response: {user_input[:50]}...")
    
    # Get the selected mentor type from session state
    mentor_type = st.session_state.get('mentor_type', 'Socratic Agent')
    
    # Add user message to chat history
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        if mentor_type == "Raw GPT":
            # Use raw GPT for direct comparison
            print("🤖 Using Raw GPT for direct response...")
            
            # Get project context from session state
            project_context = ""
            if st.session_state.arch_state and hasattr(st.session_state.arch_state, 'current_design_brief'):
                project_context = st.session_state.arch_state.current_design_brief
            
            result = get_raw_gpt_response(user_input, project_context)
            
        else:
            # Use Socratic Agent (multi-agent system)
            print("🤖 Using Socratic Agent (multi-agent system)...")
            
            # Add user input to arch state
            if st.session_state.arch_state:
                st.session_state.arch_state.messages.append({
                    "role": "user",
                    "content": user_input
                })
            
            # Process through orchestrator
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                st.session_state.orchestrator.process_student_input(
                    st.session_state.arch_state
                )
            )
            
            loop.close()
        
        print(f"✅ Response generated: {result.get('response', 'No response')[:100]}...")
        print(f"✅ Response type: {result.get('metadata', {}).get('response_type', 'Unknown')}")
        print(f"✅ Agents used: {result.get('metadata', {}).get('agents_used', [])}")
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": result.get("response", "I apologize, but I couldn't generate a response."),
            "timestamp": datetime.now().isoformat(),
            "metadata": result.get("metadata", {}),
            "mentor_type": mentor_type
        })
        
        # Update progress tracking after each interaction
        if st.session_state.arch_state and st.session_state.orchestrator:
            try:
                # Re-analyze the current state to update progress
                analysis_agent = AnalysisAgent("architecture")
                
                # Create a new event loop for the async analysis
                progress_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(progress_loop)
                
                updated_analysis = progress_loop.run_until_complete(
                    analysis_agent.process(st.session_state.arch_state)
                )
                
                progress_loop.close()
                
                # Update the analysis result in session state
                st.session_state.analysis_result = updated_analysis
                
                # Log the progress update
                current_phase = updated_analysis.get('phase_analysis', {}).get('current_phase', 'unknown')
                phase_completion = updated_analysis.get('phase_analysis', {}).get('phase_completion', 0)
                print(f"📊 Progress Updated: {current_phase} ({phase_completion}% complete)")
                
            except Exception as e:
                print(f"⚠️ Progress update failed: {e}")
        
        # Log interaction for data collection
        if st.session_state.interaction_logger:
            # Extract metadata for logging
            metadata = result.get("metadata", {})
            agents_used = metadata.get("agents_used", [])
            response_type = metadata.get("response_type", "unknown")
            routing_path = metadata.get("routing_path", "unknown")
            cognitive_flags = metadata.get("cognitive_flags", [])
            confidence_score = metadata.get("confidence_score", 0.5)
            sources_used = metadata.get("sources", [])
            context_classification = metadata.get("classification", {})
            
            # Get student skill level from session state
            student_skill_level = "intermediate"  # Default
            if st.session_state.arch_state and hasattr(st.session_state.arch_state, 'student_profile'):
                student_skill_level = st.session_state.arch_state.student_profile.skill_level
            
            st.session_state.interaction_logger.log_interaction(
                student_input=user_input,
                agent_response=result.get("response", ""),
                routing_path=routing_path,
                agents_used=agents_used,
                response_type=response_type,
                cognitive_flags=cognitive_flags,
                student_skill_level=student_skill_level,
                confidence_score=confidence_score,
                sources_used=sources_used,
                context_classification=context_classification,
                metadata=metadata
            )
        
        return result
        
    except Exception as e:
        print(f"❌ Error in process_chat_response: {e}")
        print(f"❌ Exception in chat processing: {e}")
        
        error_response = f"I apologize, but I encountered an error: {str(e)}"
        
        # Add error response to chat history
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": error_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"response_type": "error", "error": str(e)},
            "mentor_type": mentor_type
        })
        
        return {
            "response": error_response,
            "metadata": {"response_type": "error", "error": str(e)},
            "routing_path": "error",
            "classification": {}
        }

def reset_session():
    """Reset all session state for new project"""
    st.session_state.analysis_complete = False
    st.session_state.chat_messages = []
    st.session_state.arch_state = None
    st.session_state.analysis_result = None
    st.session_state.gpt_sam_results = None
    st.session_state.uploaded_image_path = None
    st.session_state.orchestrator = None
    st.session_state.interaction_logger = InteractionLogger()
    # Reset input mode and SAM settings
    st.session_state.input_mode = "Text Only"
    st.session_state.use_sam = False
    st.session_state.mentor_type = "Socratic Agent" # Reset mentor type
    st.rerun()

def main():
    """Main Streamlit application with integrated chat interface"""
    
    # Initialize session state if not already done
    initialize_session_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key handling
        st.subheader("🔑 OpenAI API Key")
        env_api_key = os.getenv("OPENAI_API_KEY")
        
        if env_api_key:
            st.success("API key loaded from environment")
            api_key = env_api_key
        else:
            api_key = st.text_input(
                "Enter your OpenAI API Key:",
                type="password",
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            
            if not api_key:
                st.warning("⚠️ Please set OPENAI_API_KEY or enter your API key")
        
        # Current session info
        if st.session_state.analysis_complete:
            st.subheader("📊 Current Session")
            input_mode = st.session_state.get('input_mode', 'Text Only')
            mentor_type = st.session_state.get('mentor_type', 'Socratic Agent')
            
            st.info(f"**Mode**: {input_mode}")
            if mentor_type == "Socratic Agent":
                st.success(f"**Mentor**: {mentor_type} 🤖")
            else:
                st.warning(f"**Mentor**: {mentor_type} 🤖")
            
            if st.session_state.use_sam:
                st.success("**SAM**: Enabled")
            else:
                st.info("**SAM**: Disabled")
        
        # System status
        if api_key:
            st.subheader("🤖 System Status")
            try:
                # Test GPT-SAM
                gpt_sam = GPTSAMAnalyzer(api_key)
                st.success("GPT Vision: Ready")
                
                # Show SAM availability
                if SAM_AVAILABLE:
                    st.success("SAM: Available")
                else:
                    st.warning("SAM: Not available")
                
                # Test agents
                if st.session_state.orchestrator:
                    st.success("Multi-Agent System: Ready")
                else:
                    st.info("⏳ Multi-Agent System: Not initialized")
                    
            except Exception as e:
                st.error(f"System Error: {e}")
        
        # Pipeline information
        st.subheader("🔄 Flexible Analysis Pipeline")
        st.markdown("""
        **Text-Only Mode**:
        - 📝 Text analysis and cognitive assessment
        - 🤖 Multi-agent guidance
        - 📊 Learning progression tracking
        
        **Image + Text Mode**:
        - 🧠 GPT Vision analyzes image
        - 🎨 SAM segmentation (optional)
        - 📝 Text + visual analysis
        - 🤖 Multi-agent enhancement
        
        **Image-Only Mode**:
        - 🧠 GPT Vision analysis
        - 🎨 SAM segmentation (optional)
        - 🤖 Multi-agent interpretation
        """)
        
        # Data export section
        st.subheader("📊 Data Collection")
        
        # Export session data button
        if st.session_state.interaction_logger and hasattr(st.session_state.interaction_logger, 'interactions') and len(st.session_state.interaction_logger.interactions) > 0:
            if st.button("💾 Export Session Data"):
                try:
                    # Export data for thesis analysis
                    st.session_state.interaction_logger.export_for_thesis_analysis()
                    
                    # Get session summary
                    summary = st.session_state.interaction_logger.get_session_summary()
                    
                    st.success(f"Session data exported to ./thesis_data/")
                    st.info(f"Session ID: {st.session_state.interaction_logger.session_id}")
                    st.info(f"Total interactions: {len(st.session_state.interaction_logger.interactions)}")
                    
                    # Show key metrics
                    if summary:
                        st.metric("Cognitive Offloading Prevention", f"{summary.get('cognitive_offloading_prevention_rate', 0):.1%}")
                        st.metric("Deep Thinking Engagement", f"{summary.get('deep_thinking_encouragement_rate', 0):.1%}")
                except Exception as e:
                    st.error(f"Error exporting data: {str(e)}")
        else:
            st.info("No interaction data to export yet. Start a conversation to generate data.")
        
        # Reset button
        if st.button("🔄 Start New Project"):
            reset_session()
    
    if not api_key:
        st.error("⚠️ Please set OPENAI_API_KEY environment variable")
        return
    
    # Main chat interface
    if not st.session_state.analysis_complete:
        # Initialize input_mode from session state or set default
        if 'input_mode' not in st.session_state:
            st.session_state.input_mode = "Text Only"
        input_mode = st.session_state.input_mode
        
        # Top section with greeting
        st.markdown("""
        <div class="top-section">
        <div class="greeting">
            Welcome to your AI Architectural Mentor!
        </div>
        <p style="text-align: center; color: #888; margin-top: 1rem;">
            Describe your project or upload an image to get started. You can work with text descriptions, 
            upload images, or combine both for comprehensive guidance.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Compact configuration section
        with st.container():
            st.markdown("""
            <div class="compact-text" style="text-align: center; margin-bottom: 15px;">
                <strong>💡 Quick Examples:</strong><br>
                <strong>Text:</strong> "I'm designing a sustainable office building"<br>
                <strong>Image+Text:</strong> Upload sketch + "How can I improve circulation?"<br>
                <strong>Image Only:</strong> Upload floor plan for analysis
            </div>
            """, unsafe_allow_html=True)
            
            # Analysis configuration in a compact column
            with st.columns([1, 2, 1])[1]:  # Center column
                st.markdown("""
                <div class="compact-text" style="font-size: 14px; font-weight: bold; margin-bottom: 10px; text-align: center;">
                    🔧 Analysis Configuration
                </div>
                """, unsafe_allow_html=True)
                
                # Input mode selection
                input_mode = st.radio(
                    "Choose your input mode:",
                    ["Text Only", "Image + Text", "Image Only"],
                    index=0,
                    help="Text Only: Describe your project without images\nImage + Text: Upload image and describe project\nImage Only: Analyze image without text description"
                )
                # Store input_mode in session state
                st.session_state.input_mode = input_mode
                
                # SAM analysis option (only show if image is involved)
                use_sam = False
                if input_mode in ["Image + Text", "Image Only"]:
                    use_sam = st.checkbox(
                        "🔍 Enable SAM Segmentation Analysis",
                        value=st.session_state.get('use_sam', False),
                        help="SAM provides precise spatial segmentation of architectural elements. Disable for faster analysis."
                    )
                # Store use_sam in session state
                st.session_state.use_sam = use_sam
                
                # Mentor type selection
                mentor_type = st.selectbox(
                    "🤖 Mentor Type:",
                    ["Socratic Agent", "Raw GPT"],
                    index=0,
                    help="Socratic Agent: Multi-agent system that challenges and guides thinking\nRaw GPT: Direct GPT responses for comparison"
                )
                # Store mentor_type in session state
                st.session_state.mentor_type = mentor_type
                
                # Template design prompts
                template_prompts = {
                    "Select a template...": "",
                    "🏢 Sustainable Office Building": "I'm designing a sustainable office building for a tech company. The building should accommodate 200 employees with flexible workspaces, meeting rooms, and common areas. I want to focus on energy efficiency, natural lighting, and creating a collaborative environment. The site is in an urban area with limited green space.",
                    "🏫 Community Learning Center": "I'm creating a community learning center that will serve as a hub for education, workshops, and community events. The building needs to include classrooms, a library, multipurpose spaces, and outdoor learning areas. I want it to be welcoming to all ages and accessible to everyone in the community."
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
        
        # Main input area with integrated functionality - confined to center column
        with st.columns([1, 2, 1])[1]:  # Center column
            # File uploader (only show if image mode is selected)
            uploaded_file = None
            if input_mode in ["Image + Text", "Image Only"]:
                uploaded_file = st.file_uploader(
                    "📁 Upload your architectural drawing",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload a clear image of your architectural design, plan, or sketch"
                )
            
            # Text input area
            design_brief = ""
            if input_mode in ["Text Only", "Image + Text"]:
                # Get template text if selected
                template_text = template_prompts.get(selected_template, "")
                placeholder_text = "Describe your architectural project here..." if input_mode == "Text Only" else "Describe your project along with the uploaded image..."
                
                design_brief = st.text_area(
                    "📝 Project Description:",
                    value=template_text,
                    placeholder=placeholder_text,
                    height=120,
                    help="Provide details about your architectural project, design goals, constraints, or specific questions"
                )
            
            # Analysis button
            if st.button("🚀 Start Analysis", type="primary", use_container_width=False):
                    # Validate input based on selected mode
                    if input_mode == "Text Only" and not design_brief.strip():
                        st.error("📝 Please describe your project for text-only analysis")
                    elif input_mode in ["Image + Text", "Image Only"] and not uploaded_file:
                        st.error("🖼️ Please upload an image for image analysis")
                    elif input_mode == "Image + Text" and not design_brief.strip():
                        st.error("📝 Please describe your project along with the image")
                    else:
                        with st.spinner("🧠 Analyzing your design..."):
                            try:
                                # Initialize Mega Mentor
                                mentor = MegaArchitecturalMentor(api_key, use_sam)
                                
                                # Handle image if provided
                                temp_image_path = None
                                if uploaded_file and input_mode in ["Image + Text", "Image Only"]:
                                    image = Image.open(uploaded_file)
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                        image.save(tmp_file.name)
                                        temp_image_path = tmp_file.name
                                    st.session_state.uploaded_image_path = temp_image_path
                                
                                # Handle text input
                                if input_mode == "Image Only":
                                    design_brief = "Analyze this architectural drawing"
                                elif not design_brief.strip():
                                    design_brief = "Please analyze my architectural project"
                                
                                # Run analysis
                                results = run_async_analysis(mentor, design_brief, temp_image_path, skill_level)
                                
                                # Store results
                                st.session_state.arch_state = results["state"]
                                st.session_state.analysis_result = results["analysis_result"]
                                st.session_state.gpt_sam_results = results["gpt_sam_results"]
                                st.session_state.orchestrator = mentor.orchestrator
                                st.session_state.analysis_complete = True
                                st.session_state.use_sam = use_sam
                                st.session_state.input_mode = input_mode
                                # mentor_type is already set from the dropdown selection
                                
                                st.success("✅ Analysis complete! Let's continue our conversation.")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Analysis failed: {str(e)}")
    
    else:
        # Chat interface phase - same layout as initial page
        
        # Mentor acknowledgment - show above chat after initial analysis
        if st.session_state.analysis_complete and len(st.session_state.chat_messages) == 0:
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
                    building_type=st.session_state.analysis_result.get('text_analysis', {}).get('building_type', 'architectural').title()
                ), unsafe_allow_html=True)
        
        # Chat interface - confined to center column
        with st.columns([1, 2, 1])[1]:  # Center column
            # Display chat messages
            for message in st.session_state.chat_messages:
                render_chat_message(message)
            
            # Chat input with integrated file upload capability
            # File upload for additional images during conversation
            additional_image = st.file_uploader(
                "📎 Add image to conversation (optional)",
                type=['png', 'jpg', 'jpeg'],
                help="Upload additional images to discuss during the conversation"
            )
            
            # Chat input
            user_input = st.chat_input("Ask about improvements, precedents, or request a review...")
            
            if user_input:
                # Generate response
                with st.spinner("🧠 Thinking..."):
                    try:
                        # Process through LangGraph workflow (this already handles chat history and logging)
                        result = process_chat_response(user_input)
                        
                    except Exception as e:
                        print(f"❌ Exception in chat processing: {str(e)}")
                        import traceback
                        print(f"❌ Full traceback: {traceback.format_exc()}")
                        
                        # Add error response to chat history
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": "I'd love to help with that. Can you be more specific about what aspect you'd like to explore?",
                            "timestamp": datetime.now().isoformat(),
                            "metadata": {"response_type": "error_fallback"},
                            "mentor_type": st.session_state.get('mentor_type', 'Socratic Agent')
                        })
                
                st.rerun()
        
        # Analysis results section - confined to center column below chat
        with st.columns([1, 2, 1])[1]:  # Center column
            st.markdown("---")
            st.markdown("""
            <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                📊 Analysis Results
            </div>
            """, unsafe_allow_html=True)
            
            # Get analysis data
            result = st.session_state.analysis_result
            input_mode = st.session_state.get('input_mode', 'Text Only')
            gpt_sam_results = st.session_state.gpt_sam_results
            
            # Progress update button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Update Progress", help="Re-analyze your current progress based on our conversation"):
                    if st.session_state.arch_state and st.session_state.orchestrator:
                        with st.spinner("🔄 Updating progress..."):
                            try:
                                # Re-analyze the current state
                                analysis_agent = AnalysisAgent("architecture")
                                progress_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(progress_loop)
                                
                                updated_analysis = progress_loop.run_until_complete(
                                    analysis_agent.process(st.session_state.arch_state)
                                )
                                
                                progress_loop.close()
                                
                                # Update the analysis result
                                st.session_state.analysis_result = updated_analysis
                                
                                current_phase = updated_analysis.get('phase_analysis', {}).get('current_phase', 'unknown')
                                phase_completion = updated_analysis.get('phase_analysis', {}).get('phase_completion', 0)
                                
                                st.success(f"✅ Progress updated! Current phase: {current_phase.title()} ({phase_completion}% complete)")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Progress update failed: {e}")
            
            # Analysis details (expandable)
            with st.expander("📊 Analysis Details", expanded=False):
                st.write("**📊 What the AI Detected:**")
                
                # Phase Analysis
                phase_analysis = result.get('phase_analysis', {})
                if phase_analysis:
                    current_phase = phase_analysis.get('current_phase', 'unknown')
                    phase_completion = phase_analysis.get('phase_completion', 0)
                    st.write(f"• **Design Phase**: {current_phase.title()} ({phase_completion}% complete)")
                else:
                    st.write("• **Design Phase**: Not detected")
                
                # Text Analysis
                text_analysis = result.get('text_analysis', {})
                if text_analysis:
                    building_type = text_analysis.get('building_type', 'unknown')
                    st.write(f"• **Building Type**: {building_type.title()}")
                    
                    requirements = text_analysis.get('program_requirements', [])
                    if requirements:
                        st.write(f"• **Program Requirements**: {len(requirements)} found")
                        for req in requirements[:3]:
                            st.write(f"  - {req}")
                else:
                    st.write("• **Building Type**: Not detected")
                
                # Cognitive Flags
                cognitive_flags = result.get('cognitive_flags', [])
                if cognitive_flags:
                    st.write(f"• **Learning Areas**: {len(cognitive_flags)} identified")
                    for flag in cognitive_flags[:3]:
                        flag_name = flag.replace('_', ' ').title()
                        st.write(f"  - {flag_name}")
                else:
                    st.write("• **Learning Areas**: None detected")
                
                # Synthesis
                synthesis = result.get('synthesis', {})
                if synthesis:
                    challenges = synthesis.get('cognitive_challenges', [])
                    if challenges:
                        st.write(f"• **Cognitive Challenges**: {len(challenges)} identified")
                        for challenge in challenges[:2]:
                            challenge_name = challenge.replace('_', ' ').title()
                            st.write(f"  - {challenge_name}")
                
                st.write("---")
                st.write("**🔧 Technical Details:**")
                st.write("• **Analysis Method**: AI-Powered Analysis")
                st.write(f"• **Domain**: {result.get('domain', 'unknown').title()}")
                st.write(f"• **Confidence Level**: {result.get('confidence_score', 0):.1%}")
                
                # Human-readable summary
                st.write("---")
                st.write("**📋 Analysis Summary:**")
                
                # Phase summary
                phase_analysis = result.get('phase_analysis', {})
                current_phase = phase_analysis.get('current_phase', 'unknown')
                phase_completion = phase_analysis.get('phase_completion', 0)
                
                phase_descriptions = {
                    'ideation': 'You are in the early stages of your design process, focusing on concept development and problem framing.',
                    'visualization': 'You are developing spatial relationships and exploring form, working on the visual aspects of your design.',
                    'materialization': 'You are working on technical details, construction methods, and material specifications.',
                    'completion': 'You are in the final stages, refining details and preparing for presentation.'
                }
                
                description = phase_descriptions.get(current_phase, 'Your design process is being analyzed.')
                st.write(f"**Current Status**: {description}")
                
                # Progress interpretation
                if phase_completion < 25:
                    st.write("**Progress**: Early stage - you're just getting started with this phase.")
                elif phase_completion < 50:
                    st.write("**Progress**: Developing - you're making good progress but have more work ahead.")
                elif phase_completion < 75:
                    st.write("**Progress**: Advanced - you're well into this phase with significant progress made.")
                else:
                    st.write("**Progress**: Nearly complete - you're close to finishing this phase.")
                
                # Next steps
                if current_phase != 'completion' and phase_completion > 70:
                    next_phases = {
                        'ideation': 'visualization',
                        'visualization': 'materialization', 
                        'materialization': 'completion'
                    }
                    next_phase = next_phases.get(current_phase, 'completion')
                    st.write(f"**Next Step**: You're ready to move to the **{next_phase.title()}** phase!")
                elif current_phase == 'completion' and phase_completion > 90:
                    st.write("**Next Step**: Excellent work! Your design process is nearly complete.")
                else:
                    st.write("**Next Step**: Continue developing your current phase to build a stronger foundation.")
                
                # Suggested questions based on current phase
                st.write("---")
                st.write("**💡 Suggested Questions to Progress:**")
                
                phase_questions = {
                    'ideation': [
                        "What is the main purpose of this building?",
                        "Who are the primary users and what are their needs?",
                        "What are the key functional requirements?",
                        "What is the site context and constraints?",
                        "What is your initial concept or vision?"
                    ],
                    'visualization': [
                        "How should the spaces be organized and connected?",
                        "What is the circulation flow between different areas?",
                        "How can natural light be maximized?",
                        "What are the key spatial relationships?",
                        "How does the form respond to the site?"
                    ],
                    'materialization': [
                        "What construction methods would be most appropriate?",
                        "What materials would work best for this project?",
                        "How can sustainability be integrated?",
                        "What are the technical requirements?",
                        "How can the design be optimized for construction?"
                    ],
                    'completion': [
                        "What final details need to be resolved?",
                        "How can the presentation be improved?",
                        "What are the key design highlights?",
                        "How does the final design meet all requirements?",
                        "What are the next steps for implementation?"
                    ]
                }
                
                questions = phase_questions.get(current_phase, [
                    "What aspect of your design would you like to explore?",
                    "What challenges are you facing?",
                    "What would you like to improve?"
                ])
                
                for i, question in enumerate(questions[:3], 1):
                    st.write(f"{i}. {question}")
                
                st.write("*Ask any of these questions or your own to advance your design process!*")
            
            # Analysis summary metrics
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            
            with col_metric1:
                # Display current design phase instead of confidence
                phase_analysis = result.get('phase_analysis', {})
                current_phase = phase_analysis.get('current_phase', 'unknown')
                phase_completion = phase_analysis.get('phase_completion', 0)
                
                # Format phase display
                phase_display = {
                    'ideation': '💡 Ideation',
                    'visualization': '🎨 Visualization', 
                    'materialization': '🏗️ Materialization',
                    'completion': '✅ Completion',
                    'unknown': '❓ Unknown'
                }
                
                phase_name = phase_display.get(current_phase, f"❓ {current_phase.title()}")
                st.metric("Design Phase", f"{phase_name} ({phase_completion}%)")
            
            with col_metric2:
                flags = len(result.get('cognitive_flags', []))
                st.metric("Learning Areas", flags)
            
            with col_metric3:
                building_type = result.get('text_analysis', {}).get('building_type', 'unknown')
                # Ensure building type is properly capitalized and formatted
                if building_type and building_type != 'unknown':
                    formatted_type = building_type.replace('_', ' ').title()
                    st.metric("Project Type", formatted_type)
                else:
                    st.metric("Project Type", "Unknown")
            
            with col_metric4:
                if gpt_sam_results and 'error' not in gpt_sam_results and input_mode in ["Image + Text", "Image Only"]:
                    spatial_elements = gpt_sam_results.get('gpt_analysis', {}).get('spatial_elements', [])
                    st.metric("Spatial Elements", len(spatial_elements))
                else:
                    mode_text = "Text Only" if input_mode == "Text Only" else "Not available"
                    st.metric("Vision Analysis", mode_text)
            
            # Design brief and image
            col_brief, col_image = st.columns([2, 1])
            
            with col_brief:
                brief = st.session_state.arch_state.current_design_brief
                st.markdown(f"**Design Brief:** {brief}")
            
            with col_image:
                if st.session_state.uploaded_image_path and input_mode in ["Image + Text", "Image Only"]:
                    st.image(st.session_state.uploaded_image_path, caption="Your Design", use_container_width=True)
                elif input_mode == "Text Only":
                    st.info("📝 **Text-Only Analysis**: No image uploaded for this session")
            
            # Phase Progress Section
            phase_analysis = result.get('phase_analysis', {})
            if phase_analysis:
                st.markdown("---")
                st.markdown("""
                <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                    🎯 Design Phase Progress
                </div>
                """, unsafe_allow_html=True)
                
                current_phase = phase_analysis.get('current_phase', 'unknown')
                phase_completion = phase_analysis.get('phase_completion', 0)
                next_phase = phase_analysis.get('next_phase')
                progression_ready = phase_analysis.get('progression_ready', False)
                
                # Phase descriptions
                phase_descriptions = {
                    'ideation': 'Concept development and problem framing',
                    'visualization': 'Spatial development and form exploration', 
                    'materialization': 'Technical development and implementation',
                    'completion': 'Final refinement and presentation'
                }
                
                # Phase activities
                phase_activities = {
                    'ideation': ['Site analysis', 'Program development', 'Concept exploration'],
                    'visualization': ['Spatial planning', 'Form development', 'Circulation design'],
                    'materialization': ['Construction details', 'Material specification', 'Technical systems'],
                    'completion': ['Final details', 'Presentation preparation', 'Documentation']
                }
                
                col_phase1, col_phase2 = st.columns([1, 1])
                
                with col_phase1:
                    # Progress bar
                    st.progress(phase_completion / 100)
                    st.write(f"**{phase_completion}% Complete**")
                    
                    # Phase description
                    description = phase_descriptions.get(current_phase, 'Phase description not available')
                    st.write(f"**Current Focus:** {description}")
                    
                    # Next phase info
                    if next_phase and progression_ready:
                        next_phase_name = next_phase.replace('_', ' ').title()
                        st.success(f"🎉 Ready to progress to **{next_phase_name}** phase!")
                    elif next_phase:
                        next_phase_name = next_phase.replace('_', ' ').title()
                        st.info(f"Next phase: **{next_phase_name}**")
                
                with col_phase2:
                    # Current phase activities
                    activities = phase_activities.get(current_phase, [])
                    if activities:
                        st.write("**Key Activities for This Phase:**")
                        for activity in activities:
                            st.write(f"• {activity}")
                    
                    # Learning opportunities from synthesis
                    synthesis = result.get('synthesis', {})
                    learning_opportunities = synthesis.get('learning_opportunities', [])
                    if learning_opportunities:
                        st.write("**Learning Opportunities:**")
                        for opportunity in learning_opportunities[:2]:  # Show top 2
                            st.write(f"• {opportunity}")
            
            # Design suggestions from analysis (only show if image was used and suggestions available)
            if gpt_sam_results and 'error' not in gpt_sam_results and input_mode in ["Image + Text", "Image Only"]:
                gpt_analysis = gpt_sam_results.get('gpt_analysis', {})
                design_insights = gpt_analysis.get('design_insights', {})
                suggestions = design_insights.get('suggestions', [])
                
                if suggestions:
                    st.markdown("---")
                    st.markdown("""
                    <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                        💡 Design Suggestions
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, suggestion in enumerate(suggestions[:5], 1):
                        st.markdown(f"**{i}.** {suggestion}")
            
            # GPT-SAM Results (only show if image was used)
            if gpt_sam_results and 'error' not in gpt_sam_results and input_mode in ["Image + Text", "Image Only"]:
                with st.expander("🤖 GPT Vision + SAM Analysis", expanded=True):
                    st.subheader("🎨 Vision Analysis Results")
                    
                    # Show visualization if available
                    if gpt_sam_results.get('visualization') is not None:
                        st.image(gpt_sam_results['visualization'], caption="AI Analysis Visualization", use_container_width=True)
                    
                    # Show detailed GPT analysis
                    gpt_analysis = gpt_sam_results.get('gpt_analysis', {})
                    if gpt_analysis:
                        col_gpt1, col_gpt2 = st.columns(2)
                        
                        with col_gpt1:
                            spatial_elements = gpt_analysis.get('spatial_elements', [])
                            if spatial_elements:
                                st.write("**🏗️ Spatial Elements Detected:**")
                                for elem in spatial_elements[:6]:
                                    elem_type = elem.get('type', 'unknown')
                                    label = elem.get('label', 'unnamed')
                                    confidence = elem.get('coordinate_confidence', 0)
                                    st.write(f"• {elem_type.title()}: {label} ({confidence:.1%})")
                            
                            circulation = gpt_analysis.get('circulation_analysis', {})
                            if circulation:
                                st.write("**🔄 Circulation Analysis:**")
                                primary = circulation.get('primary_path', 'Unknown')
                                st.write(f"• Primary: {primary}")
                                secondary = circulation.get('secondary_paths', [])
                                if secondary:
                                    st.write(f"• Secondary: {', '.join(secondary[:2])}")
                        
                        with col_gpt2:
                            design_insights = gpt_analysis.get('design_insights', {})
                            if design_insights:
                                strengths = design_insights.get('strengths', [])
                                if strengths:
                                    st.write("**Design Strengths:**")
                                    for strength in strengths[:3]:
                                        st.write(f"• {strength}")
                                
                                issues = design_insights.get('issues', [])
                                if issues:
                                    st.write("**⚠️ Design Issues:**")
                                    for issue in issues[:3]:
                                        st.write(f"• {issue}")
                                
                                suggestions = design_insights.get('suggestions', [])
                                if suggestions:
                                    st.write("**💡 Suggestions:**")
                                    for suggestion in suggestions[:3]:
                                        st.write(f"• {suggestion}")
                    
                    # Show SAM segmentation results
                    sam_results = gpt_sam_results.get('sam_results', {})
                    if sam_results and 'error' not in sam_results:
                        st.write(f"**🎨 SAM Segments Created:** {sam_results.get('num_segments', 0)}")
            
            # Dynamic Cognitive Analysis (based on latest interaction)
            if st.session_state.chat_messages:
                # Get the latest assistant message to analyze current cognitive state
                latest_assistant_msg = None
                for msg in reversed(st.session_state.chat_messages):
                    if msg.get('role') == 'assistant':
                        latest_assistant_msg = msg
                        break
                
                if latest_assistant_msg:
                    metadata = latest_assistant_msg.get('metadata', {})
                    cognitive_flags = metadata.get('cognitive_flags', [])
                    response_type = metadata.get('response_type', '')
                    
                    with st.expander("🧠 Current Cognitive Analysis", expanded=False):
                        if cognitive_flags:
                            st.warning("🚩 Areas for Cognitive Development Detected:")
                            
                            flag_explanations = {
                                "needs_accessibility_guidance": "♿ **Accessibility Awareness**: Consider universal design principles",
                                "needs_spatial_thinking_support": "🏗️ **Spatial Thinking**: Think about how spaces connect and flow",
                                "needs_brief_clarification": "📝 **Brief Development**: More specific requirements needed",
                                "needs_basic_guidance": "📚 **Foundational**: Building fundamental understanding",
                                "needs_public_space_consideration": "🏛️ **Public Space**: Consider community interaction patterns",
                                "needs_program_clarification": "📋 **Program**: Clarify functional requirements",
                                "ready_for_advanced_challenge": "🎯 **Advanced Ready**: Can handle complex challenges",
                                "showing_growth": "📈 **Growth Detected**: Demonstrating learning progression",
                                "stuck_on_topic": "🔄 **Pattern**: Returning to same topic - trying new approach"
                            }
                            
                            for flag in cognitive_flags:
                                explanation = flag_explanations.get(flag, f"• **{flag.replace('_', ' ').title()}**")
                                st.markdown(explanation)
                        else:
                            st.success("Strong cognitive awareness demonstrated!")
                        
                        # Show response type and educational intent
                        if response_type:
                            st.info(f"**Response Type**: {response_type.replace('_', ' ').title()}")
                        
                        # Show learning opportunities based on response type
                        if response_type in ['challenging_question', 'exploratory_question', 'clarifying_guidance']:
                            st.write("**🎯 Current Learning Focus:**")
                            if response_type == 'challenging_question':
                                st.write("• Deepening critical thinking")
                                st.write("• Challenging assumptions")
                            elif response_type == 'exploratory_question':
                                st.write("• Exploring new possibilities")
                                st.write("• Creative thinking development")
                            elif response_type == 'clarifying_guidance':
                                st.write("• Building foundational understanding")
                                st.write("• Clarifying concepts")
            
            # Dynamic Skill Assessment (based on latest interaction)
            if st.session_state.chat_messages:
                # Get the latest assistant message for skill assessment
                latest_assistant_msg = None
                for msg in reversed(st.session_state.chat_messages):
                    if msg.get('role') == 'assistant':
                        latest_assistant_msg = msg
                        break
                
                if latest_assistant_msg:
                    metadata = latest_assistant_msg.get('metadata', {})
                    classification = metadata.get('classification', {})
                    confidence_level = classification.get('confidence_level', 'medium')
                    understanding_level = classification.get('understanding_level', 'medium')
                    engagement_level = classification.get('engagement_level', 'medium')
                    
                    with st.expander("🎯 Current Learning Assessment", expanded=False):
                        col_skill1, col_skill2 = st.columns(2)
                        
                        with col_skill1:
                            st.write(f"**Confidence Level:** {confidence_level.title()}")
                            st.write(f"**Understanding Level:** {understanding_level.title()}")
                            st.write(f"**Engagement Level:** {engagement_level.title()}")
                            
                            # Show current skill level from session state
                            if st.session_state.arch_state and hasattr(st.session_state.arch_state, 'student_profile'):
                                current_skill = st.session_state.arch_state.student_profile.skill_level
                                st.info(f"**Current Skill Level:** {current_skill.title()}")
                        
                        with col_skill2:
                            # Convert levels to confidence scores for visualization
                            level_scores = {
                                'low': 0.3, 'medium': 0.6, 'high': 0.9,
                                'uncertain': 0.2, 'confident': 0.7, 'overconfident': 0.8
                            }
                            
                            confidence_score = level_scores.get(confidence_level, 0.5)
                            st.write(f"**Confidence Score:** {confidence_score:.1%}")
                            st.progress(confidence_score)
                            
                            # Show interaction insights
                            agents_used = metadata.get('agents_used', [])
                            if agents_used:
                                st.write(f"**Agents Used:** {', '.join(agents_used)}")
            
            # Download results
            st.markdown("---")
            st.markdown("""
            <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                📥 Download Results
            </div>
            """, unsafe_allow_html=True)
            
            # Create comprehensive JSON for download
            download_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "pipeline_version": "mega_architectural_mentor_v1.0",
                "design_brief": st.session_state.arch_state.current_design_brief if st.session_state.arch_state else "",
                "student_profile": {
                    "skill_level": st.session_state.arch_state.student_profile.skill_level if st.session_state.arch_state else "unknown"
                },
                "gpt_sam_results": gpt_sam_results,
                "cognitive_analysis": result,
                "interaction_log": st.session_state.interaction_logger.get_session_summary() if st.session_state.interaction_logger else {}
            }
            
            json_str = json.dumps(download_data, indent=2, default=str)
            
            st.download_button(
                label="📥 Download Complete Analysis (JSON)",
                data=json_str,
                file_name=f"mega_architectural_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Download complete analysis results including vision analysis and cognitive assessment",
                use_container_width=False
            )
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 3rem;'>
    <p><strong>🏗️ Architectural Mentor</strong> | Powered by AI Vision + Multi-Agent Learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 