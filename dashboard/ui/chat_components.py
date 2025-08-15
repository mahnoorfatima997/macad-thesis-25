"""
Chat components and message rendering for the dashboard.
"""

import streamlit as st
import re
from html import escape
from typing import Dict, Any, List
from ..config.settings import INPUT_MODES, MENTOR_TYPES, TEMPLATE_PROMPTS, SKILL_LEVELS


def safe_markdown_to_html(text: str) -> str:
    """
    Convert markdown formatting to HTML while safely escaping other content.
    Handles **bold** formatting and preserves line breaks.
    """
    if text is None:
        return ""

    # Normalize newlines and preserve line breaks
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")

    # Convert markdown bold (**text**) to HTML <strong> while safely escaping other content
    html_parts: List[str] = []
    last_idx = 0

    for match in re.finditer(r"\*\*(.+?)\*\*", normalized, flags=re.DOTALL):
        start, end = match.span()
        inner = match.group(1)
        # escape text before bold
        html_parts.append(escape(normalized[last_idx:start]))
        # add bold with escaped inner text
        html_parts.append(f"<strong>{escape(inner)}</strong>")
        last_idx = end

    # Add remaining text
    html_parts.append(escape(normalized[last_idx:]))
    html = "".join(html_parts)

    # Convert newlines to <br> tags for proper display
    html = html.replace("\n", "<br>")

    return html


def render_chat_message(message: Dict[str, Any]):
    """Render a chat message with appropriate styling."""
    # This function is kept for backward compatibility but not used in the new chat interface
    pass


def render_chat_interface():
    """Render a modern chat interface with messages in a single chat window."""
    # Create a container for the chat messages with a key that changes when messages update
    message_count = len(st.session_state.messages) if 'messages' in st.session_state else 0
    chat_container = st.container()
    
    with chat_container:
        # Create the chat window with custom CSS
        st.markdown(f"""
        <div class="chat-window" data-message-count="{message_count}">
            <div class="chat-messages" id="chat-messages">
        """, unsafe_allow_html=True)
        
        # Render all messages in the chat
        for i, message in enumerate(st.session_state.messages):
            render_single_message(message)
        
        st.markdown("""
            </div>
        </div>
        
        <script>
        // Debug: Log the chat interface setup
        console.log('Chat interface initialized');
        console.log('Message count:', {message_count});
        
        // Auto-scroll to bottom of chat
        function scrollToBottom() {
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
                console.log('Scrolled to bottom');
            }
        }
        
        // Scroll on page load
        window.addEventListener('load', function() {
            console.log('Page loaded, setting up chat');
            scrollToBottom();
            
            // Debug: Check message layout
            const messages = document.querySelectorAll('.message');
            console.log('Found messages:', messages.length);
            messages.forEach((msg, index) => {
                console.log(`Message ${index}:`, msg.className, msg.offsetWidth, msg.offsetHeight);
            });
        });
        
        // Scroll when new content is added (using MutationObserver)
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    console.log('New content added, scrolling');
                    scrollToBottom();
                    
                    // Debug: Check new message layout
                    const messages = document.querySelectorAll('.message');
                    console.log('Updated messages count:', messages.length);
                }
            });
        });
        
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            observer.observe(chatMessages, { childList: true, subtree: true });
            console.log('Observer attached to chat messages');
        }
        
        // Show typing indicator when needed
        function showTypingIndicator() {
            const indicator = document.getElementById('typing-indicator');
            if (indicator) {
                indicator.style.display = 'flex';
                scrollToBottom();
            }
        }
        
        function hideTypingIndicator() {
            const indicator = document.getElementById('typing-indicator');
            if (indicator) {
                indicator.style.display = 'none';
            }
        }
        
        // Listen for Streamlit events to show/hide typing indicator
        window.addEventListener('message', function(event) {
            if (event.data && event.data.type === 'streamlit:setComponentValue') {
                // Check if this is a new message being added
                if (event.data.value && event.data.value.includes('thinking')) {
                    showTypingIndicator();
                }
            }
        });
        
        // Global functions for Python to call
        window.showTypingIndicator = showTypingIndicator;
        window.hideTypingIndicator = hideTypingIndicator;
        
        // Enhanced message handling
        function enhanceMessageDisplay() {
            const messages = document.querySelectorAll('.message');
            messages.forEach((message, index) => {
                // Add fade-in animation for new messages
                if (!message.classList.contains('fade-in')) {
                    message.classList.add('fade-in');
                    message.style.opacity = '0';
                    message.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        message.style.transition = 'all 0.3s ease';
                        message.style.opacity = '1';
                        message.style.transform = 'translateY(0)';
                    }, index * 100);
                }
            });
        }
        
        // Run enhancement on load
        window.addEventListener('load', enhanceMessageDisplay);
        
        // Run enhancement when new messages are added
        observer.observe(chatMessages, { childList: true, subtree: true });
        </script>
        """, unsafe_allow_html=True)


def render_chat_interface_with_typing():
    """Render chat interface with typing indicator visible."""
    # Create a container for the chat messages
    chat_container = st.container()
    
    with chat_container:
        # Create the chat window with custom CSS
        st.markdown("""
        <div class="chat-window">
            <div class="chat-messages" id="chat-messages">
        """, unsafe_allow_html=True)
        
        # Render all messages in the chat
        for message in st.session_state.messages:
            render_single_message(message)
        
        st.markdown("""
            </div>
        </div>
        
        <!-- Typing indicator - visible by default -->
        <div class="typing-indicator" id="typing-indicator">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <script>
        // Same JavaScript as above but typing indicator is visible
        function scrollToBottom() {
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
        
        window.addEventListener('load', scrollToBottom);
        
        const observer = new MutationObserver(scrollToBottom);
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            observer.observe(chatMessages, { childList: true, subtree: true });
        }
        </script>
        """, unsafe_allow_html=True)


def show_typing_indicator():
    """Show the typing indicator using JavaScript."""
    st.markdown("""
    <script>
    if (window.showTypingIndicator) {
        window.showTypingIndicator();
    }
    </script>
    """, unsafe_allow_html=True)


def hide_typing_indicator():
    """Hide the typing indicator using JavaScript."""
    st.markdown("""
    <script>
    if (window.hideTypingIndicator) {
        window.hideTypingIndicator();
    }
    </script>
    """, unsafe_allow_html=True)


def render_single_message(message: Dict[str, Any]):
    """Render a single message in the chat interface."""
    if message["role"] == "user":
        # User message - right side
        st.markdown(
            f"""
            <div class="message user-message">
                <div class="message-content user-content">
                    <div class="message-text">{safe_markdown_to_html(message["content"])}</div>
                    <div class="message-time">{_format_timestamp(message.get("timestamp"))}</div>
                </div>
                <div class="message-avatar user-avatar"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Agent message - left side
        mentor_type = message.get("mentor_type", "Multi-Agent System")
        if mentor_type == "MENTOR" or mentor_type == "Socratic Agent":
            mentor_label = "Mentor"
        elif mentor_type == "GENERIC_AI":
            mentor_label = "Generic AI"
        elif mentor_type == "CONTROL":
            mentor_label = "Control Mode"
        elif mentor_type == "RAW_GPT" or mentor_type == "Raw GPT":
            mentor_label = "Raw GPT"
        else:
            mentor_label = mentor_type

        # ENHANCED: Check if this is a gamified challenge
        gamification_info = message.get("gamification", {})
        is_gamified = gamification_info.get("is_gamified", False)

        if is_gamified and gamification_info.get("display_type") == "enhanced_visual":
            # Render enhanced gamified challenge
            _render_gamified_message(message, mentor_label)
        else:
            # Render normal message
            st.markdown(
                f"""
                <div class="message agent-message">
                    <div class="message-avatar agent-avatar"></div>
                    <div class="message-content agent-content">
                        <div class="message-header">
                            <span class="agent-name">{mentor_label}</span>
                        </div>
                        <div class="message-text">{safe_markdown_to_html(message["content"])}</div>
                        <div class="message-time">{_format_timestamp(message.get("timestamp"))}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_gamified_message(message: Dict[str, Any], mentor_label: str):
    """Render a gamified challenge message with enhanced visuals."""
    try:
        # Import the gamification components
        from dashboard.ui.gamification_components import render_gamified_challenge

        # Show the mentor header first
        st.markdown(
            f"""
            <div class="message agent-message gamified-message">
                <div class="message-avatar agent-avatar"></div>
                <div class="message-content agent-content">
                    <div class="message-header">
                        <span class="agent-name">🎮 {mentor_label} - Challenge Mode!</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render the enhanced gamified challenge
        gamification_info = message.get("gamification", {})
        challenge_data = gamification_info.get("challenge_data", {})
        challenge_data["challenge_text"] = message["content"]

        render_gamified_challenge(challenge_data)

        # Add timestamp
        st.markdown(
            f"""
            <div style="text-align: right; color: #888; font-size: 0.8em; margin-top: 10px;">
                {_format_timestamp(message.get("timestamp"))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        print(f"⚠️ Error rendering gamified message: {e}")
        # Fallback to normal message rendering
        st.markdown(
            f"""
            <div class="message agent-message">
                <div class="message-avatar agent-avatar"></div>
                <div class="message-content agent-content">
                    <div class="message-header">
                        <span class="agent-name">🎮 {mentor_label}</span>
                    </div>
                    <div class="message-text">{safe_markdown_to_html(message["content"])}</div>
                    <div class="message-time">{_format_timestamp(message.get("timestamp"))}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def _format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    if not timestamp:
        return ""

    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%H:%M")
    except:
        return ""


def render_welcome_section():
    """Render the welcome section at the top of the chat."""
    st.markdown("""
    <div class="top-section">
    <div class="greeting">
        Welcome to your AI Mentor!
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
        Analysis Configuration
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Examples
    st.markdown("""
    <div class="compact-text" style="text-align: center; margin-bottom: 15px;">
        <strong>Quick Examples:</strong><br>
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
        "Mentor Type:",
        MENTOR_TYPES,
        index=0,
        help="Socratic Agent: Multi-agent system that challenges and guides thinking\n"
             "Raw GPT: Direct GPT responses for comparison"
    )
    return mentor_type


def render_template_selection():
    """Render template selection component."""
    selected_template = st.selectbox(
        "Quick Start Templates:",
        list(TEMPLATE_PROMPTS.keys()),
        help="Choose a template to get started quickly, or write your own description below"
    )
    return selected_template


def render_skill_level_selection():
    """Render skill level selection component."""
    skill_level = st.selectbox(
        "Your Skill Level:",
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
            "Project Description:",
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
            "Upload your architectural drawing",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear image of your architectural design, plan, or sketch"
        )
    return uploaded_file


def render_chat_history():
    """Render all chat messages from session state - kept for backward compatibility."""
    # This function is now deprecated in favor of render_chat_interface()
    render_chat_interface()


def get_chat_input() -> str:
    """Get chat input from user with enhanced styling and experience."""
    # Enhanced placeholder text based on context
    if 'messages' in st.session_state and st.session_state.messages:
        # Check if this is a follow-up to a question
        last_message = st.session_state.messages[-1]
        if last_message.get('role') == 'assistant':
            if '?' in last_message.get('content', ''):
                placeholder = "Type your response here..."
            else:
                placeholder = "Ask a follow-up question or share your thoughts..."
        else:
            placeholder = "Continue the conversation..."
    else:
        placeholder = "Start your architectural design journey..."
    
    # Get the chat input with enhanced styling
    user_input = st.chat_input(
        placeholder,
        key="enhanced_chat_input"
    )
    
    return user_input





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