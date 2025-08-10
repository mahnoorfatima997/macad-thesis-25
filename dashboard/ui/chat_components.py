"""
Chat components and message rendering for the dashboard.
"""

import streamlit as st
from typing import Dict, Any
from ..config.settings import INPUT_MODES, MENTOR_TYPES, TEMPLATE_PROMPTS, SKILL_LEVELS


def render_chat_message(message: Dict[str, Any]):
    """Render a chat message with appropriate styling."""
    
    if message["role"] == "user":
        st.markdown(
            f"""
        <div class="chat-message user">
            <strong>👤 You:</strong><br>
            {message["content"]}
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        # Get mentor type for display
        mentor_type = message.get("mentor_type", "Multi-Agent System")
        if mentor_type == "MENTOR" or mentor_type == "Socratic Agent":
            mentor_icon = "🏗️"
            mentor_label = "Architectural Mentor"
        elif mentor_type == "GENERIC_AI":
            mentor_icon = "🤖"
            mentor_label = "Generic AI"
        elif mentor_type == "CONTROL":
            mentor_icon = "🎯"
            mentor_label = "Control Mode"
        elif mentor_type == "RAW_GPT" or mentor_type == "Raw GPT":
            mentor_icon = "🤖"
            mentor_label = "Raw GPT"
        else:
            mentor_icon = "🏗️"
            mentor_label = mentor_type
        
        st.markdown(
            f"""
        <div class="chat-message assistant">
            <strong>{mentor_icon} {mentor_label}:</strong><br>
            {message["content"]}
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_welcome_section():
    """Render the welcome section at the top of the chat."""
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


def render_mode_configuration():
    """Render the testing mode configuration section."""
    st.markdown("""
    <div class="compact-text" style="font-size: 14px; font-weight: bold; margin-bottom: 10px; text-align: center;">
        🔧 Analysis Configuration
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Examples
    st.markdown("""
    <div class="compact-text" style="text-align: center; margin-bottom: 15px;">
        <strong>💡 Quick Examples:</strong><br>
        <strong>Text:</strong> "I'm designing a sustainable office building"<br>
        <strong>Image+Text:</strong> Upload sketch + "How can I improve circulation?"<br>
        <strong>Image Only:</strong> Upload floor plan for analysis
    </div>
    """, unsafe_allow_html=True)


def render_input_mode_selection():
    """Render input mode selection component."""
    input_mode = st.radio(
        "Choose your input mode:",
        INPUT_MODES,
        index=0,
        help="Text Only: Describe your project without images\n"
             "Image + Text: Upload image and describe project\n"
             "Image Only: Analyze image without text description"
    )
    return input_mode


def render_mentor_type_selection():
    """Render mentor type selection component."""
    mentor_type = st.selectbox(
        "🤖 Mentor Type:",
        MENTOR_TYPES,
        index=0,
        help="Socratic Agent: Multi-agent system that challenges and guides thinking\n"
             "Raw GPT: Direct GPT responses for comparison"
    )
    return mentor_type


def render_template_selection():
    """Render template selection component."""
    selected_template = st.selectbox(
        "📋 Quick Start Templates:",
        list(TEMPLATE_PROMPTS.keys()),
        help="Choose a template to get started quickly, or write your own description below"
    )
    return selected_template


def render_skill_level_selection():
    """Render skill level selection component."""
    skill_level = st.selectbox(
        "🎯 Your Skill Level:",
        SKILL_LEVELS,
        index=1,
        help="This helps the AI provide appropriate guidance"
    )
    return skill_level


def render_project_description_input(template_text: str, input_mode: str):
    """Render project description input area."""
    if input_mode in ["Text Only", "Image + Text"]:
        placeholder_text = ("Describe your architectural project here..." 
                          if input_mode == "Text Only" 
                          else "Describe your project along with the uploaded image...")
        
        project_description = st.text_area(
            "📝 Project Description:",
            value=template_text,
            placeholder=placeholder_text,
            height=120,
            help="Provide details about your architectural project, design goals, constraints, or specific questions"
        )
        return project_description
    return ""


def render_file_upload(input_mode: str):
    """Render file upload component."""
    uploaded_file = None
    if input_mode in ["Image + Text", "Image Only"]:
        uploaded_file = st.file_uploader(
            "📁 Upload your architectural drawing",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear image of your architectural design, plan, or sketch"
        )
    return uploaded_file


def render_chat_history():
    """Render all chat messages from session state."""
    for message in st.session_state.messages:
        render_chat_message(message)


def get_chat_input() -> str:
    """Get chat input from user."""
    return st.chat_input("Ask about improvements, precedents, or request a review...")


def response_contains_questions(text: str) -> bool:
    """Light heuristic: treat response as already inquisitive if it contains a question."""
    if not text:
        return False
    return text.count('?') >= 1


def validate_input(input_mode: str, project_description: str, uploaded_file) -> tuple[bool, str]:
    """Validate input based on selected mode."""
    if input_mode == "Text Only" and not project_description.strip():
        return False, "📝 Please describe your project for text-only analysis"
    elif input_mode in ["Image + Text", "Image Only"] and not uploaded_file:
        return False, "🖼️ Please upload an image for image analysis"
    elif input_mode == "Image + Text" and not project_description.strip():
        return False, "📝 Please describe your project along with the image"
    return True, "" 