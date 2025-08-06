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
from data_collection.interaction_logger import InteractionLogger

# Add this function after the imports and before the main functions
def convert_agent_response_to_dict(agent_response):
    """Convert AgentResponse object to dictionary format for backward compatibility"""
    if hasattr(agent_response, 'response_text'):  # AgentResponse object
        return {
            'response_text': agent_response.response_text,
            'response_type': agent_response.response_type.value if hasattr(agent_response.response_type, 'value') else str(agent_response.response_type),
            'cognitive_flags': [flag.value if hasattr(flag, 'value') else str(flag) for flag in agent_response.cognitive_flags],
            'enhancement_metrics': {
                'cognitive_offloading_prevention_score': agent_response.enhancement_metrics.cognitive_offloading_prevention_score,
                'deep_thinking_engagement_score': agent_response.enhancement_metrics.deep_thinking_engagement_score,
                'knowledge_integration_score': agent_response.enhancement_metrics.knowledge_integration_score,
                'scaffolding_effectiveness_score': agent_response.enhancement_metrics.scaffolding_effectiveness_score,
                'learning_progression_score': agent_response.enhancement_metrics.learning_progression_score,
                'metacognitive_awareness_score': agent_response.enhancement_metrics.metacognitive_awareness_score,
                'overall_cognitive_score': agent_response.enhancement_metrics.overall_cognitive_score,
                'scientific_confidence': agent_response.enhancement_metrics.scientific_confidence
            },
            'agent_name': agent_response.agent_name,
            'metadata': agent_response.metadata,
            'journey_alignment': {
                'current_phase': agent_response.journey_alignment.current_phase,
                'phase_progress': agent_response.journey_alignment.phase_progress,
                'milestone_progress': agent_response.journey_alignment.milestone_progress,
                'next_milestone': agent_response.journey_alignment.next_milestone,
                'journey_progress': agent_response.journey_alignment.journey_progress,
                'phase_confidence': agent_response.journey_alignment.phase_confidence,
                'milestone_questions_asked': agent_response.journey_alignment.milestone_questions_asked
            },
            'progress_update': {
                'phase_progress': agent_response.progress_update.phase_progress,
                'milestone_progress': agent_response.progress_update.milestone_progress,
                'cognitive_state': agent_response.progress_update.cognitive_state,
                'learning_progression': agent_response.progress_update.learning_progression,
                'skill_level_update': agent_response.progress_update.skill_level_update,
                'engagement_level_update': agent_response.progress_update.engagement_level_update
            }
        }
    else:  # Already a dictionary
        return agent_response

def safe_get_nested_dict(obj, *keys, default=None):
    """Safely get nested dictionary values, handling both dict and AgentResponse objects"""
    if obj is None:
        return default
    
    # Convert AgentResponse to dict if needed
    if hasattr(obj, 'response_text'):
        obj = convert_agent_response_to_dict(obj)
    
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

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

        'uploaded_image_path': None,
        'interaction_logger': InteractionLogger(),
        'orchestrator': None,
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
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.orchestrator = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize orchestrator with debug logging
            import logging
            logging.basicConfig(level=logging.DEBUG)
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
        
        # Step 4: Run cognitive analysis
        analysis_agent = AnalysisAgent(domain)
        analysis_result = await analysis_agent.process(state)
        
        # Step 5: Return comprehensive results
        return {
            "state": state,
            "analysis_result": analysis_result,
            "vision_available": vision_available
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
        # Handle both AgentResponse objects and dictionaries
        if hasattr(result, 'response_text'):
            response_content = result.response_text
        else:
            response_content = result.get("response", "")
        
        state.messages.append({
            "role": "assistant",
            "content": response_content
        })
        
        return result

def render_left_sidebar():
    """Render the left sidebar with app information"""
    # Get current mode from session state
    current_mode = st.session_state.get('input_mode', 'Text Only')
    
    st.markdown(f"""
    <div class="left-sidebar">
        <div class="sidebar-info">
            <div class="info-item">
                <span class="info-label">Mode:</span>
                <span class="info-value">{current_mode}</span>
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
        
        # Convert AgentResponse to dictionary if needed
        if hasattr(results["analysis_result"], 'response_text'):
            results["analysis_result"] = convert_agent_response_to_dict(results["analysis_result"])
        
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
            
            # Add user input to arch state before processing
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
        
        # Handle both old dict format and new AgentResponse format
        response_text = ""
        response_metadata = {}
        
        if hasattr(result, 'response_text'):  # AgentResponse object
            response_text = result.response_text
            response_metadata = {
                'response_type': result.response_type.value if hasattr(result.response_type, 'value') else str(result.response_type),
                'agents_used': [result.agent_name] if result.agent_name else [],
                'cognitive_flags': [flag.value if hasattr(flag, 'value') else str(flag) for flag in result.cognitive_flags],
                'metadata': result.metadata
            }
        else:  # Old dict format
            response_text = result.get('response', 'No response')
            response_metadata = result.get('metadata', {})
        
        print(f"✅ Response generated: {response_text[:100]}...")
        print(f"✅ Response type: {response_metadata.get('response_type', 'Unknown')}")
        print(f"✅ Agents used: {response_metadata.get('agents_used', [])}")
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat(),
            "metadata": response_metadata,
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
                
                # Convert AgentResponse to dictionary if needed
                if hasattr(updated_analysis, 'response_text'):
                    updated_analysis = updated_analysis.to_dict()
                
                # Update the analysis result in session state
                st.session_state.analysis_result = updated_analysis
                
                # Log the progress update
                current_phase = updated_analysis.get('phase_analysis', {}).get('phase', 'unknown')
                phase_completion = updated_analysis.get('phase_analysis', {}).get('progression_score', 0) * 100
                print(f"📊 Progress Updated: {current_phase} ({phase_completion:.0f}% complete)")
                
            except Exception as e:
                print(f"⚠️ Progress update failed: {e}")
        
        # Log interaction for data collection
        if st.session_state.interaction_logger:
            # Extract metadata for logging
            metadata = response_metadata  # Use the already processed metadata
            agents_used = metadata.get("agents_used", [])
            response_type = metadata.get("response_type", "unknown")
            routing_path = metadata.get("routing_path", "unknown")
            cognitive_flags = metadata.get("cognitive_flags", [])
            confidence_score = metadata.get("confidence_score", 0.5)
            sources_used = metadata.get("sources", [])
            # Get classification from the correct location in orchestrator result
            context_classification = result.get("student_classification", {})
            
            # Get student skill level from session state
            student_skill_level = "intermediate"  # Default
            if st.session_state.arch_state and hasattr(st.session_state.arch_state, 'student_profile'):
                student_skill_level = st.session_state.arch_state.student_profile.skill_level
            
            # Include detailed analysis result with internal grading metrics
            enhanced_metadata = metadata.copy()
            if st.session_state.analysis_result:
                # Add detailed phase analysis with benchmarking metrics
                enhanced_metadata["detailed_phase_analysis"] = safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis") or {}
                # Add benchmarking metrics
                enhanced_metadata["benchmarking_metrics"] = {
                    "cop_score": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "cop_score") or 0,
                    "dte_score": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "dte_score") or 0,
                    "ki_score": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "ki_score") or 0,
                    "cop_factor": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "cop_factor") or 0,
                    "dte_factor": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "dte_factor") or 0,
                    "ki_factor": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "ki_factor") or 0,
                    "milestone_progression": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "milestone_progression") or 0,
                    "quality_factor": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "quality_factor") or 0,
                    "engagement_factor": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "engagement_factor") or 0,
                    "completed_milestones": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "completed_milestones") or 0,
                    "total_milestones": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "total_milestones") or 0,
                    "average_grade": safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "average_grade") or 0
                }
                # Add assessment profile if available
                assessment_profile = safe_get_nested_dict(st.session_state.analysis_result, "phase_analysis", "assessment_profile")
                if assessment_profile:
                    enhanced_metadata["assessment_profile"] = {
                        "student_id": getattr(assessment_profile, 'student_id', 'unknown'),
                        "phases": {phase: {
                            "milestones": {milestone: {
                                "completion_percentage": getattr(milestone_data, 'completion_percentage', 0),
                                "average_grade": getattr(milestone_data, 'average_grade', 0),
                                "response_count": getattr(milestone_data, 'response_count', 0)
                            } for milestone, milestone_data in phase_data.milestones.items()}
                        } for phase, phase_data in assessment_profile.phases.items()}
                    }
            
            st.session_state.interaction_logger.log_interaction(
                student_input=user_input,
                agent_response=response_text,
                routing_path=routing_path,
                agents_used=agents_used,
                response_type=response_type,
                cognitive_flags=cognitive_flags,
                student_skill_level=student_skill_level,
                confidence_score=confidence_score,
                sources_used=sources_used,
                context_classification=context_classification,
                metadata=enhanced_metadata
            )
        
        # Return in the format expected by the app
        return {
            "response": response_text,
            "metadata": response_metadata,
            "routing_path": response_metadata.get("routing_path", "unknown"),
            "classification": result.get("student_classification", {}),
            "conversation_progression": result.get("conversation_progression", {})
        }
        
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
            "classification": {},
            "conversation_progression": {}
        }

def reset_session():
    """Reset all session state for new project"""
    st.session_state.analysis_complete = False
    st.session_state.chat_messages = []
    st.session_state.arch_state = None
    st.session_state.analysis_result = None
    
    st.session_state.uploaded_image_path = None
    st.session_state.orchestrator = None
    st.session_state.interaction_logger = InteractionLogger()
    # Reset input mode settings
    st.session_state.input_mode = "Text Only"
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
            
            st.info("**Vision**: GPT Vision Available")
        
        # System status
        if api_key:
            st.subheader("🤖 System Status")
            try:
                st.success("GPT Vision: Ready")
                
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
        - 📝 Text + visual analysis
        - 🤖 Multi-agent enhancement
        
        **Image-Only Mode**:
        - 🧠 GPT Vision analysis
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
                                mentor = MegaArchitecturalMentor(api_key)
                                
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
                                st.session_state.orchestrator = mentor.orchestrator
                                st.session_state.analysis_complete = True
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
                    building_type=safe_get_nested_dict(st.session_state.analysis_result, 'text_analysis', 'building_type') or 'architectural'
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
            
            # Progress update button
            col1, col2, col3 = st.columns([1, 2, 1])
       
            
            # Enhanced Cognitive Analysis Dashboard
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
                
                # Create three columns for different analysis sections
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.markdown("**🎯 Current Design Phase**")
                    # Use conversation progression if available, otherwise fall back to analysis
                    conversation_progression = result.get('conversation_progression', {})
                    phase_analysis = safe_get_nested_dict(result, 'phase_analysis') or {}
                    
                    if conversation_progression:
                        current_phase = conversation_progression.get('conversation_phase', 'unknown')
                        phase_completion = conversation_progression.get('phase_progress', 0) * 100
                        phase_confidence = conversation_progression.get('confidence', 0)
                    elif phase_analysis:
                        current_phase = phase_analysis.get('phase', 'unknown')
                        phase_confidence = phase_analysis.get('confidence', 0)
                        phase_completion = phase_analysis.get('progression_score', 0) * 100
                    else:
                        current_phase = 'unknown'
                        phase_confidence = 0
                        phase_completion = 0
                
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
                    synthesis = safe_get_nested_dict(result, 'synthesis') or {}
                    
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
                    text_analysis = safe_get_nested_dict(result, 'text_analysis') or {}
                    
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
                
                # Dynamic recommendations section - only show if we have meaningful data
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
                
                # Overall progress summary - show meaningful information
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
                
                # Removed static technical details, analysis summary, and suggested questions sections
            
            # Analysis summary metrics with smaller font
            st.markdown("""
            <style>
            .metric-container .stMetric {
                font-size: 12px !important;
            }
            .metric-container .stMetric label {
                font-size: 11px !important;
            }
            .metric-container .stMetric div[data-testid="metric-container"] {
                font-size: 12px !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            
            with col_metric1:
                # Display current design phase with progress
                # Use conversation progression if available, otherwise fall back to analysis
                conversation_progression = result.get('conversation_progression', {})
                phase_analysis = safe_get_nested_dict(result, 'phase_analysis') or {}
                
                if conversation_progression:
                    current_phase = conversation_progression.get('conversation_phase', 'unknown')
                    phase_completion = conversation_progression.get('phase_progress', 0) * 100
                else:
                    current_phase = phase_analysis.get('phase', 'unknown')
                    phase_completion = phase_analysis.get('progression_score', 0) * 100
                
                phase_confidence = phase_analysis.get('confidence', 0)
                
                # Format phase display
                phase_display = {
                    # Design phases
                    'ideation': '💡 Ideation',
                    'visualization': '🎨 Visualization', 
                    'materialization': '🏗️ Materialization',
                    'completion': '✅ Completion',
                    # Conversation progression phases
                    'discovery': '🔍 Discovery',
                    'exploration': '🔬 Exploration',
                    'synthesis': '🧠 Synthesis',
                    'application': '⚡ Application',
                    'reflection': '🤔 Reflection',
                    'unknown': '❓ Unknown'
                }
                
                phase_name = phase_display.get(current_phase, f"❓ {current_phase.title()}")
                # Custom metric display with smaller text
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <h5 style='margin-bottom: 0.2rem;'>Current Phase</h5>
                        <p style='font-size: 1rem; margin: 0;'>{phase_name}</p>
                        <p style='font-size: 0.8rem; color: gray;'>{phase_completion:.0f}% complete</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_metric2:
                # Learning balance indicator
                synthesis = safe_get_nested_dict(result, 'synthesis') or {}
                challenges = len(synthesis.get('cognitive_challenges', []))
                opportunities = len(synthesis.get('learning_opportunities', []))
                
                # Calculate learning balance
                if challenges + opportunities > 0:
                    balance_ratio = opportunities / (challenges + opportunities)
                    if balance_ratio > 0.6:
                        balance_status = "🌟 Strong"
                    elif balance_ratio > 0.4:
                        balance_status = "📈 Good"
                    else:
                        balance_status = "⚠️ Needs Focus"
                else:
                    balance_status = "🔄 Starting"
                
                # Custom metric display with smaller text
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <h5 style='margin-bottom: 0.2rem;'>Learning Balance</h5>
                        <p style='font-size: 1rem; margin: 0;'>{balance_status}</p>
                        <p style='font-size: 0.8rem; color: gray;'>{challenges} challenges, {opportunities} opportunities</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_metric3:
                # Milestone progress - show meaningful information
                completed_milestones = phase_analysis.get('completed_milestones', 0)
                total_milestones = phase_analysis.get('total_milestones', 0)
                
                if total_milestones > 0:
                    if completed_milestones > 0:
                        milestone_progress = (completed_milestones / total_milestones) * 100
                        # Custom metric display with smaller text
                        st.markdown(f"""
                            <div style='text-align: center;'>
                                <h5 style='margin-bottom: 0.2rem;'>Milestone Progress</h5>
                                <p style='font-size: 1rem; margin: 0;'>{completed_milestones}/{total_milestones}</p>
                                <p style='font-size: 0.8rem; color: gray;'>{milestone_progress:.0f}%</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Show next milestone when none completed
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
                            st.markdown(f"""
                                <div style='text-align: center;'>
                                    <h5 style='margin-bottom: 0.2rem;'>Next Milestone</h5>
                                    <p style='font-size: 1rem; margin: 0;'>{next_milestone_name}</p>
                                    <p style='font-size: 0.8rem; color: gray;'>0/{total_milestones} completed</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style='text-align: center;'>
                                    <h5 style='margin-bottom: 0.2rem;'>Milestone Progress</h5>
                                    <p style='font-size: 1rem; margin: 0;'>0/{total_milestones}</p>
                                    <p style='font-size: 0.8rem; color: gray;'>Getting started</p>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    # Show phase-based progress instead
                    phase_completion = phase_analysis.get('progression_score', 0) * 100
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <h5 style='margin-bottom: 0.2rem;'>Phase Progress</h5>
                            <p style='font-size: 1rem; margin: 0;'>{phase_completion:.0f}%</p>
                            <p style='font-size: 0.8rem; color: gray;'>Based on conversation</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            with col_metric4:
                # Project complexity indicator
                building_type = safe_get_nested_dict(result, 'text_analysis', 'building_type') or 'unknown'
                if building_type and building_type != 'unknown':
                    formatted_type = building_type.replace('_', ' ').title()
                    
                    # Add project complexity indicator
                    requirements = safe_get_nested_dict(result, 'text_analysis', 'program_requirements') or []
                    if len(requirements) > 8:
                        complexity = "🔴 Complex"
                    elif len(requirements) > 4:
                        complexity = "🟡 Moderate"
                    else:
                        complexity = "🟢 Simple"
                    
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <h5 style='margin-bottom: 0.2rem;'>Project Type</h5>
                            <p style='font-size: 1rem; margin: 0;'>{formatted_type}</p>
                            <p style='font-size: 0.8rem; color: gray;'>{complexity}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <h5 style='margin-bottom: 0.2rem;'>Project Type</h5>
                            <p style='font-size: 1rem; margin: 0;'>Unknown</p>
                            <p style='font-size: 0.8rem; color: gray;'>Not specified</p>
                        </div>
                    """, unsafe_allow_html=True)
            
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
            phase_analysis = safe_get_nested_dict(result, 'phase_analysis') or {}
            if phase_analysis:
                st.markdown("---")
                st.markdown("""
                <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
                    🎯 Design Phase Progress
                </div>
                """, unsafe_allow_html=True)
                
                current_phase = phase_analysis.get('phase', 'unknown')  # Fixed: use 'phase' instead of 'current_phase'
                phase_completion = phase_analysis.get('progression_score', 0) * 100  # Convert to percentage
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
                    # Progress bar with meaningful progress
                    meaningful_progress = phase_completion / 100
                    st.progress(meaningful_progress)
                    
                    # Display progress with context
                    if meaningful_progress < 0.25:
                        progress_status = "🔄 Getting Started"
                    elif meaningful_progress < 0.5:
                        progress_status = "📝 In Progress"
                    elif meaningful_progress < 0.75:
                        progress_status = "🎯 Making Good Progress"
                    elif meaningful_progress < 1.0:
                        progress_status = "✨ Almost Complete"
                    else:
                        progress_status = "✅ Phase Complete"
                    
                    st.write(f"**{progress_status}** ({phase_completion:.0f}% Complete)")
                    
                    # Show milestone information if available
                    milestone_completion = phase_analysis.get('milestone_completion', 0)
                    completed_milestones = phase_analysis.get('completed_milestones', 0)
                    total_milestones = phase_analysis.get('total_milestones', 0)
                    
                    if total_milestones > 0:
                        st.write(f"📋 **Milestones:** {completed_milestones}/{total_milestones} completed")
                        
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
                            st.write(f"🎯 **Next Focus:** {next_milestone_name}")
                    
                    # Show phase recommendations if available
                    phase_recommendations = phase_analysis.get('phase_recommendations', [])
                    if phase_recommendations:
                        st.write("💡 **Recommendations:**")
                        for rec in phase_recommendations[:3]:  # Show top 3 recommendations
                            st.write(f"• {rec}")
                    
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
                    synthesis = safe_get_nested_dict(result, 'synthesis') or {}
                    learning_opportunities = synthesis.get('learning_opportunities', [])
                    if learning_opportunities:
                        st.write("**Learning Opportunities:**")
                        for opportunity in learning_opportunities[:2]:  # Show top 2
                            st.write(f"• {opportunity}")
            

            

            
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
            

    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 3rem;'>
    <p><strong>🏗️ Architectural Mentor</strong> | Powered by AI Vision + Multi-Agent Learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 