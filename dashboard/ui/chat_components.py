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
    """Render a single message in the chat interface with image support."""
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

        # Display image if present
        if message.get("image_path"):
            try:
                st.image(message["image_path"], caption="Uploaded image", use_container_width=True)
            except Exception as e:
                st.error(f"Could not display image: {e}")
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
        display_type = gamification_info.get("display_type", "")

        print(f"🎮 DEBUG: Message gamification check:")
        print(f"🎮 DEBUG: Has gamification key: {'gamification' in message}")
        print(f"🎮 DEBUG: Is gamified: {is_gamified}")
        print(f"🎮 DEBUG: Display type: {display_type}")
        print(f"🎮 DEBUG: Should render enhanced: {is_gamified and display_type == 'enhanced_visual'}")

        if is_gamified and display_type == "enhanced_visual":
            print(f"🎮 DEBUG: Calling _render_gamified_message")
            # Render enhanced gamified challenge
            _render_gamified_message(message, mentor_label)
        else:
            print(f"🎮 DEBUG: Rendering normal message")
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

            # Display generated image if present in assistant message
            if message.get("generated_image"):
                _render_generated_image_in_chat(message["generated_image"])


def _render_gamified_message(message: Dict[str, Any], mentor_label: str):
    """Render a gamified challenge message with BOTH agent response AND interactive game."""
    try:
        print(f"🎮 DEBUG: Starting gamified message rendering")
        print(f"🎮 DEBUG: Message keys: {list(message.keys())}")
        print(f"🎮 DEBUG: Gamification info: {message.get('gamification', {})}")

        # Import the gamification components
        from dashboard.ui.gamification_components import render_gamified_challenge

        # Show the mentor header first
        st.markdown(
            f"""
            <div class="message agent-message gamified-message">
                <div class="message-avatar agent-avatar"></div>
                <div class="message-content agent-content">
                    <div class="message-header">
                        <span class="agent-name">🎮 {mentor_label} - Enhanced Challenge!</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # STEP 1: Show the agent's response in normal chat bubble format
        agent_response = message.get("content", "")
        if agent_response and agent_response.strip():
            # Clean the agent response from any HTML artifacts
            clean_agent_response = _clean_agent_response(agent_response)

            if clean_agent_response:
                # Render as normal chat message bubble
                st.markdown(
                    f"""
                    <div class="message agent-message">
                        <div class="message-avatar agent-avatar"></div>
                        <div class="message-content agent-content">
                            <div class="message-header">
                                <span class="agent-name">{mentor_label}</span>
                            </div>
                            <div class="message-text">{safe_markdown_to_html(clean_agent_response)}</div>
                            <div class="message-time">{_format_timestamp(message.get("timestamp", ""))}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # STEP 2: Then show the interactive game as an ENHANCEMENT
        gamification_info = message.get("gamification", {})
        challenge_data = gamification_info.get("challenge_data", {})

        # STEP 3: Prepare contextual challenge data for the game
        # Extract user's original message for contextual game generation
        user_message = challenge_data.get("user_message", "")
        if not user_message:
            # Try to get from session state or message history
            if hasattr(st.session_state, 'messages') and st.session_state.messages:
                for msg in reversed(st.session_state.messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break

        # Ensure challenge_data has all required fields for CONTEXTUAL game generation
        if not challenge_data:
            challenge_data = {}

        challenge_data.update({
            "user_message": user_message,  # Pass user's actual question for contextual games
            "challenge_type": challenge_data.get("challenge_type") or gamification_info.get("challenge_type", "constraint_challenge"),  # FIXED: Don't override existing challenge_type
            "building_type": gamification_info.get("building_type", "community center"),
            "mentor_label": mentor_label,
            "gamification_applied": True  # Ensure games are contextual, not hardcoded
        })

        print(f"🎮 DEBUG: Challenge data keys: {list(challenge_data.keys())}")
        print(f"🎮 DEBUG: About to call enhanced gamification renderer")

        # STEP 4: Render contextual interactive game (more subtle)
        st.markdown("**◉ Interactive Challenge**")
        st.markdown("*Explore this concept through an interactive experience:*")

        # Use enhanced gamification system for contextual games
        try:
            from dashboard.ui.enhanced_gamification import render_enhanced_gamified_challenge, inject_gamification_css

            # Inject CSS for animations
            inject_gamification_css()

            # Render enhanced gamification with user's context
            render_enhanced_gamified_challenge(challenge_data)
            print(f"🎮 DEBUG: Enhanced gamification rendered successfully")

        except ImportError as e:
            # Fallback to original system
            print(f"🎮 DEBUG: Enhanced gamification not available ({e}), using fallback")
            render_gamified_challenge(challenge_data)

        print(f"🎮 DEBUG: Gamification rendering completed successfully")

        # STEP 5: Add conversation continuity prompt
        st.markdown("---")
        st.markdown("💬 **Continue the conversation by sharing your thoughts, questions, or insights from this challenge.**")

        # Add timestamp
        st.markdown(
            f"""
            <div style="text-align: right; color: #888; font-size: 0.8em; margin-top: 10px;">
                {_format_timestamp(message.get("timestamp", ""))}
            </div>
            """,
            unsafe_allow_html=True,
        )

        print(f"🎮 DEBUG: Gamified message rendering completed successfully")

    except Exception as e:
        print(f"⚠️ Error rendering gamified message: {e}")
        import traceback
        traceback.print_exc()
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
                    <div class="message-time">{_format_timestamp(message.get("timestamp", ""))}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def _render_generated_image_in_chat(generated_image: dict):
    """Render a generated image within the chat interface."""
    try:
        if not generated_image or not generated_image.get('url'):
            return

        # Display the image with a nice caption
        phase = generated_image.get('phase', 'design')
        style = generated_image.get('style', 'visualization')

        st.markdown(f"""
        <div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;">
            <div style="font-weight: bold; color: #007bff; margin-bottom: 8px;">
                🎨 AI-Generated {phase.title()} Visualization
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Display the actual image
        st.image(
            generated_image['url'],
            caption=f"AI-generated {phase} visualization ({style})",
            use_container_width=True
        )

        # Add feedback buttons in a compact layout
        st.markdown("**Does this visualization match your design thinking?**")

        col1, col2, col3 = st.columns(3)

        # Use unique keys based on image URL to avoid conflicts
        image_key = str(hash(generated_image['url']))[-8:]

        with col1:
            if st.button("✅ Yes", key=f"feedback_yes_{image_key}", help="This captures my ideas well"):
                st.success("Great! This confirms we're aligned on your design direction.")
                _store_image_feedback(generated_image, 'positive')

        with col2:
            if st.button("🤔 Partially", key=f"feedback_partial_{image_key}", help="Close, but needs adjustment"):
                st.info("Thanks for the feedback! Let's continue refining your design ideas.")
                _store_image_feedback(generated_image, 'partial')

        with col3:
            if st.button("❌ No", key=f"feedback_no_{image_key}", help="This doesn't match my vision"):
                st.warning("No problem! Let's continue exploring your design ideas.")
                _store_image_feedback(generated_image, 'negative')

        # Show generation details in an expander
        with st.expander("🔍 View Generation Details"):
            st.markdown(f"**Phase:** {generated_image.get('phase', 'Unknown')}")
            st.markdown(f"**Style:** {generated_image.get('style', 'Unknown')}")
            st.markdown(f"**Prompt:** {generated_image.get('prompt', 'No prompt available')}")
            if generated_image.get('local_path'):
                st.markdown(f"**Saved to:** `{generated_image['local_path']}`")

    except Exception as e:
        st.error(f"Error displaying generated image: {e}")
        print(f"❌ Error displaying generated image in chat: {e}")

def _store_image_feedback(generated_image: dict, feedback: str):
    """Store user feedback for generated images."""
    try:
        import streamlit as st
        from datetime import datetime

        if 'image_feedback' not in st.session_state:
            st.session_state.image_feedback = []

        st.session_state.image_feedback.append({
            'phase': generated_image.get('phase'),
            'style': generated_image.get('style'),
            'url': generated_image.get('url'),
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })

        print(f"✅ Stored {feedback} feedback for {generated_image.get('phase')} image")

    except Exception as e:
        print(f"❌ Error storing image feedback: {e}")

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


def render_initial_image_upload():
    """Render initial image upload using popover - replaces input mode selection."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        # Center the popover
        col_left, col_center, col_right = st.columns([1, 1, 1])
        with col_center:
            st.markdown("""
            <style>
            div[data-testid="popover"] {
                margin-top: 0.5rem !important;
            }
            </style>
            """, unsafe_allow_html=True)

            with st.popover("📷 Upload Image", help="Upload your architectural drawing, plan, or sketch"):
                uploaded_file = st.file_uploader(
                    "Choose an image",
                    type=['png', 'jpg', 'jpeg'],
                    key="initial_image_upload"
                )

                if uploaded_file:
                    st.success(f"✅ {uploaded_file.name} uploaded successfully!")

            # Handle the case where no image is uploaded
            if 'uploaded_file' not in locals():
                uploaded_file = None

    return uploaded_file


def render_mentor_type_selection():
    """Render mentor type selection component."""
    mentor_type = st.selectbox(
        "Mentor Type:",
        MENTOR_TYPES,
        index=0,
        help="Socratic Agent: Multi-agent system that challenges and guides thinking\n"
             "Raw GPT: Direct GPT responses for comparison\n"
             "No AI: Hardcoded questions only, no AI assistance (control group)"
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


def render_project_description_input(template_text: str):
    """Render project description input area with inline image upload."""
    # Create columns for project description and image upload
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        project_description = st.text_area(
            "Project Description:",
            value=template_text,
            placeholder="Describe your architectural project here...",
            height=120,
            help="Provide details about your architectural project, design goals, constraints, or specific questions"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing to align with text area
        with st.popover("📷 Upload Image", help="Upload your architectural drawing, plan, or sketch"):
            uploaded_file = st.file_uploader(
                "Choose an image",
                type=['png', 'jpg', 'jpeg'],
                key="inline_image_upload"
            )

            if uploaded_file:
                st.success(f"✅ {uploaded_file.name} uploaded!")

        # Handle the case where no image is uploaded
        if 'uploaded_file' not in locals():
            uploaded_file = None

    return project_description, uploaded_file


# render_file_upload function removed - replaced by render_initial_image_upload


def render_chat_history():
    """Render all chat messages from session state - kept for backward compatibility."""
    # This function is now deprecated in favor of render_chat_interface()
    render_chat_interface()


def get_chat_input() -> tuple[str, any]:
    """Get chat input from user with enhanced styling and seamless image upload."""
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

    # Create columns for chat input and image upload
    col1, col2 = st.columns([0.9, 0.1])

    with col1:
        # Get the chat input with enhanced styling
        user_input = st.chat_input(
            placeholder,
            key="enhanced_chat_input"
        )

    with col2:
        st.markdown("""
        <style>
        div[data-testid="popover"] {
            margin-top: 2rem !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Initialize uploaded_image
        uploaded_image = None

        with st.popover("📷", help="Upload an image to analyze"):
            uploaded_image = st.file_uploader(
                "Choose an image",
                type=['png', 'jpg', 'jpeg'],
                key="seamless_image_upload"
            )

    return user_input, uploaded_image





def response_contains_questions(text: str) -> bool:
    """Light heuristic: treat response as already inquisitive if it contains a question."""
    if not text:
        return False
    return text.count('?') >= 1


def validate_input(project_description: str, uploaded_file) -> tuple[bool, str]:
    """Validate input - requires either description or image."""
    if not project_description.strip() and not uploaded_file:
        return False, "📝 Please provide either a project description or upload an image to get started"
    return True, ""


def _clean_agent_response(agent_response: str) -> str:
    """Clean agent response from HTML artifacts and return meaningful content."""
    if not agent_response:
        return ""

    # Remove HTML artifacts that might have been captured
    import re

    # Remove HTML comments
    clean_content = re.sub(r'<!--.*?-->', '', agent_response, flags=re.DOTALL)

    # Remove HTML tags
    clean_content = re.sub(r'<[^>]+>', '', clean_content)

    # Remove lines that are just CSS properties or HTML attributes
    lines = clean_content.split('\n')
    clean_lines = []

    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip lines that are just CSS properties or HTML attributes
        if (line.startswith('font-size:') or line.startswith('margin:') or
            line.startswith('color:') or line.startswith('background:') or
            line.startswith('border:') or line.startswith('padding:') or
            line.startswith('text-shadow:') or line.startswith('animation:') or
            line.startswith('width:') or line.startswith('height:') or
            line.startswith('border-radius:') or line.startswith('letter-spacing:') or
            'style=' in line or line.startswith('">') or line == '>' or line == '"):'):
            continue
        # Keep meaningful content lines
        clean_lines.append(line)

    clean_content = '\n'.join(clean_lines)

    # If content is too short or seems like artifacts, return empty
    if len(clean_content.strip()) < 10 or clean_content.strip().lower() in ['challenge', 'game', 'interactive']:
        return ""

    return clean_content.strip()