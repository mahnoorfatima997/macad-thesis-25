"""
Chat components and message rendering for the dashboard.
"""

import streamlit as st
import re
import sys
import os
from html import escape
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.config.settings import INPUT_MODES, MENTOR_TYPES, TEMPLATE_PROMPTS, SKILL_LEVELS

# COMMENTED AND REPLACED WITH THE FUNCTION BELOW
# def safe_markdown_to_html(text: str) -> str:
#     """
#     Convert markdown formatting to HTML while safely escaping other content.
#     Handles **bold** formatting and preserves line breaks.
#     """
#     if text is None:
#         return ""

#     # Normalize newlines and preserve line breaks
#     normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")

#     # Convert markdown bold (**text**) to HTML <strong> while safely escaping other content
#     html_parts: List[str] = []
#     last_idx = 0

#     for match in re.finditer(r"\*\*(.+?)\*\*", normalized, flags=re.DOTALL):
#         start, end = match.span()
#         inner = match.group(1)
#         # escape text before bold
#         html_parts.append(escape(normalized[last_idx:start]))
#         # add bold with escaped inner text
#         html_parts.append(f"<strong>{escape(inner)}</strong>")
#         last_idx = end

#     # Add remaining text
#     html_parts.append(escape(normalized[last_idx:]))
#     html = "".join(html_parts)

#     # Convert newlines to <br> tags for proper display
#     html = html.replace("\n", "<br>")

#     return html


#ADDED FOR TRUNCATION
def safe_markdown_to_html(text: str) -> str:
    """
    Convert markdown formatting to HTML while safely escaping other content.
    Handles **bold**, *italic*, ### headers, [links](url), and preserves line breaks.
    """
    if text is None:
        return ""

    # Normalize newlines and preserve line breaks
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")

    # Step 1: Convert markdown headers (### Header) to HTML <h3> tags
    def replace_header(match):
        level = len(match.group(1))  # Count the # symbols
        header_text = match.group(2).strip()
        return f'<h{level}>{escape(header_text)}</h{level}>'

    # Process headers first (supports h1-h6)
    header_processed = re.sub(r'^(#{1,6})\s+(.+)$', replace_header, normalized, flags=re.MULTILINE)

    # Step 2: Convert markdown links [text](url) to HTML <a> tags
    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        # Escape the link text but keep the URL as-is for functionality
        return f'<a href="{escape(link_url)}" target="_blank" rel="noopener noreferrer">{escape(link_text)}</a>'

    # Process links
    link_processed = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, header_processed)

    # Step 3: Convert markdown bold (**text**) and italic (*text*) to HTML
    html_parts: List[str] = []
    last_idx = 0

    # Process both bold and italic formatting - bold first to avoid conflicts
    for match in re.finditer(r'(\*\*(.+?)\*\*|\*([^*]+?)\*)', link_processed, flags=re.DOTALL):
        start, end = match.span()

        # Add escaped text before the match
        before_text = link_processed[last_idx:start]
        if '<a href=' in before_text or '</a>' in before_text or '<h' in before_text:
            # Don't escape if it contains HTML tags
            html_parts.append(before_text)
        else:
            html_parts.append(escape(before_text))

        # Determine if it's bold or italic
        if match.group(0).startswith('**'):
            # Bold formatting
            bold_content = match.group(2)
            if '<a href=' in bold_content or '</a>' in bold_content:
                html_parts.append(f"<strong>{bold_content}</strong>")
            else:
                html_parts.append(f"<strong>{escape(bold_content)}</strong>")
        else:
            # Italic formatting
            italic_content = match.group(3)
            if '<a href=' in italic_content or '</a>' in italic_content:
                html_parts.append(f"<em>{italic_content}</em>")
            else:
                html_parts.append(f"<em>{escape(italic_content)}</em>")

        last_idx = end

    # Add any remaining text after the last match
    remaining_text = link_processed[last_idx:]
    if '<a href=' in remaining_text or '</a>' in remaining_text or '<h' in remaining_text:
        # Don't escape if it contains HTML tags
        html_parts.append(remaining_text)
    else:
        html_parts.append(escape(remaining_text))

    # Join all parts and convert newlines to <br> tags
    html_content = "".join(html_parts)
    html_with_breaks = html_content.replace("\n", "<br>")

    return html_with_breaks





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

            # CRITICAL FIX: Render tasks that should appear after this specific message
            _render_tasks_for_message(i)
        
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

        # Image display removed - images are now bundled with text content
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

        # PERFORMANCE: Disable debug prints
        # print(f"🎮 DEBUG: Message gamification check:")
        # print(f"🎮 DEBUG: Has gamification key: {'gamification' in message}")
        # print(f"🎮 DEBUG: Is gamified: {is_gamified}")
        # print(f"🎮 DEBUG: Display type: {display_type}")
        # print(f"🎮 DEBUG: Should render enhanced: {is_gamified and display_type == 'enhanced_visual'}")

        if is_gamified and display_type == "enhanced_visual":
            # print(f"🎮 DEBUG: Calling _render_gamified_message")
            # Render enhanced gamified challenge
            _render_gamified_message(message, mentor_label)
        else:
            # print(f"🎮 DEBUG: Rendering normal message")
            pass
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
            print(f"🎨 DEBUG: Checking for generated_image in message: {bool(message.get('generated_image'))}")
            if message.get("generated_image"):
                print(f"🎨 DEBUG: Found generated_image in message, calling render function")
                _render_generated_image_in_chat(message["generated_image"])

            # REMOVED: Centralized task rendering - tasks now render per message chronologically
            # else:
            #     print(f"🎨 DEBUG: No generated_image found in message keys: {list(message.keys())}")


def _render_gamified_message(message: Dict[str, Any], mentor_label: str):
    """Render a gamified challenge message with BOTH agent response AND interactive game."""
    try:
        # PERFORMANCE: Disable debug prints
        # print(f"🎮 DEBUG: Starting gamified message rendering")
        # print(f"🎮 DEBUG: Message keys: {list(message.keys())}")
        # print(f"🎮 DEBUG: Gamification info: {message.get('gamification', {})}")

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

        # PERFORMANCE: Disable debug prints
        # print(f"🎮 DEBUG: Challenge data keys: {list(challenge_data.keys())}")
        # print(f"🎮 DEBUG: About to call enhanced gamification renderer")

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
            # print(f"🎮 DEBUG: Enhanced gamification rendered successfully")
            pass

        except ImportError as e:
            # Fallback to original system
            # print(f"🎮 DEBUG: Enhanced gamification not available ({e}), using fallback")
            render_gamified_challenge(challenge_data)

        # print(f"🎮 DEBUG: Gamification rendering completed successfully")

        # STEP 5: Add conversation continuity prompt
        st.markdown("---")
        st.markdown("**Continue the conversation by sharing your thoughts, questions, or insights from this challenge.**")

        # Add timestamp
        st.markdown(
            f"""
            <div style="text-align: right; color: #888; font-size: 0.8em; margin-top: 10px;">
                {_format_timestamp(message.get("timestamp", ""))}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # print(f"🎮 DEBUG: Gamified message rendering completed successfully")

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
        print(f"🎨 DEBUG: Attempting to render generated image")
        print(f"🎨 DEBUG: Generated image keys: {list(generated_image.keys()) if generated_image else 'None'}")

        if not generated_image:
            print(f"❌ DEBUG: No generated_image data provided")
            return

        if not generated_image.get('url') and not generated_image.get('local_path'):
            print(f"❌ DEBUG: No URL or local_path found in generated_image")
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

        # Display the actual image - handle cloud vs local deployment
        image_source = None
        source_type = "unknown"

        # Check if we're running on Streamlit Cloud
        is_cloud = (
            os.environ.get('STREAMLIT_SHARING_MODE') or
            'streamlit.app' in os.environ.get('HOSTNAME', '') or
            os.environ.get('STREAMLIT_SERVER_PORT') or
            'streamlit' in os.environ.get('SERVER_SOFTWARE', '').lower()
        )

        if is_cloud:
            # On Streamlit Cloud, prefer URL over local path since local files don't persist
            image_source = generated_image.get('url') or generated_image.get('local_path')
            source_type = "URL (cloud)" if generated_image.get('url') else "local (cloud)"
        else:
            # On local deployment, prefer local path over URL for reliability
            image_source = generated_image.get('local_path') or generated_image.get('url')
            source_type = "local file" if generated_image.get('local_path') else "URL"

        print(f"🎨 DEBUG: Cloud deployment: {is_cloud}")
        print(f"🎨 DEBUG: Image source: {image_source}")
        print(f"🎨 DEBUG: Source type: {source_type}")

        # Validate URL accessibility if using URL source
        if image_source and image_source.startswith('http'):
            try:
                import requests
                response = requests.head(image_source, timeout=5)
                print(f"🎨 DEBUG: URL accessibility check: {response.status_code}")
                if response.status_code != 200:
                    print(f"⚠️ WARNING: Image URL may not be accessible: {response.status_code}")
            except Exception as e:
                print(f"⚠️ WARNING: Could not verify URL accessibility: {e}")

        if image_source:
            try:
                st.image(
                    image_source,
                    caption=f"AI-generated {phase} visualization ({style})",
                    use_container_width=True
                )
                print(f"✅ Displayed generated image from: {source_type}")
            except Exception as e:
                print(f"❌ Error displaying image from {source_type}: {e}")
                # Fallback: try the other source if available
                fallback_source = generated_image.get('url') if source_type.startswith('local') else generated_image.get('local_path')
                if fallback_source:
                    try:
                        st.image(
                            fallback_source,
                            caption=f"AI-generated {phase} visualization ({style})",
                            use_container_width=True
                        )
                        print(f"✅ Displayed generated image from fallback source")
                    except Exception as e2:
                        st.error("❌ Generated image could not be displayed - both sources failed")
                        print(f"❌ Both image sources failed: {e}, {e2}")
                else:
                    st.error("❌ Generated image could not be displayed - primary source failed and no fallback available")
        else:
            st.error("❌ Generated image could not be displayed - no valid source found")
            print(f"❌ No valid image source found in generated_image: {list(generated_image.keys())}")

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
        Welcome to Mentor!
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
    """Render mentor type selection component - conditional based on mode."""
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

    if dashboard_mode == "Test Mode":
        # Test mode: display current test condition (read-only)
        test_group = st.session_state.get('test_group_selection', 'MENTOR')
        mentor_type = st.session_state.get('mentor_type', 'Socratic Agent')

        test_group_descriptions = {
            "MENTOR": "Socratic Agent - Multi-agent scaffolding system",
            "GENERIC_AI": "Raw GPT - Direct AI assistance",
            "CONTROL": "No AI - Self-directed design work"
        }

        st.info(f"**Test Condition**: {test_group_descriptions.get(test_group, 'Unknown')}")
        return mentor_type
    else:
        # Flexible mode: original mentor type selection
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
    """Render template selection component - only in flexible mode."""
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

    if dashboard_mode == "Flexible Mode":
        selected_template = st.selectbox(
            "Quick Start Templates:",
            list(TEMPLATE_PROMPTS.keys()),
            help="Choose a template to get started quickly, or write your own description below"
        )
        return selected_template
    else:
        # Test mode: no template selection
        return "Select a template..."


def render_skill_level_selection():
    """Render skill level selection component - conditional based on mode."""
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

    if dashboard_mode == "Test Mode":
        # Test mode: fixed intermediate level
        skill_level = "Intermediate"
        st.info(f"**Skill Level**: {skill_level} (Fixed for research consistency)")
        return skill_level
    # else:
    #     # Flexible mode: original selection
    #     skill_level = st.selectbox(
    #         "Your Skill Level:",
    #         SKILL_LEVELS,
    #         index=1,
    #         help="This helps the AI provide appropriate guidance"
    #     )
        return skill_level


def render_main_design_task():
    """Render the main design task prominently for test mode."""
    st.markdown("### Design Challenge")

    # Main task from test documents
    main_task = """
    **You are tasked with designing a community center for a diverse urban neighborhood of 15,000 residents.**

    **Site**: Former industrial warehouse (150m x 80m x 12m height)

    **Key Considerations**:
    - Community needs assessment and cultural sensitivity
    - Sustainability and adaptive reuse principles
    - Flexible programming for diverse activities
    - Integration with existing urban fabric
    """

    st.markdown(main_task)

    # Phase-specific subtasks
    current_phase = st.session_state.get('test_current_phase', 'Ideation')

    if current_phase == 'Ideation':
        subtask = """
        **Current Phase: Ideation**

        Develop your initial concept considering:
        - What questions should we ask about this community?
        - How can the existing industrial character be preserved and enhanced?
        - What successful warehouse-to-community transformations can inform your approach?
        """
    elif current_phase == 'Visualization':
        subtask = """
        **Current Phase: Visualization**

        Based on your concept, develop spatial visualizations:
        - Create diagrams showing circulation patterns and adjacency requirements
        - Sketch key spatial relationships and community interaction zones
        - Visualize how the existing structure integrates with new program elements
        """
    elif current_phase == 'Materialization':
        subtask = """
        **Current Phase: Materialization**

        Develop technical implementation details:
        - Specify materials and construction methods that support your design vision
        - Detail how new systems integrate with preserved industrial elements
        - Address structural modifications within the existing grid system
        """
    else:
        subtask = "**Ready to begin design process**"

    st.markdown(subtask)

    return main_task

def render_project_description_input(template_text: str):
    """Render project description input area with inline image upload."""
    dashboard_mode = st.session_state.get('dashboard_mode', 'Test Mode')

    if dashboard_mode == "Test Mode":
        # Test mode: Display fixed design challenge
        render_main_design_task()

        # st.markdown("### Let`s Start!")
        # st.write("Define your project first: I am designing ...")
    else:
        # Flexible mode: Original template-based input
        st.markdown("### 📝 Project Description")
        st.write("Describe your architectural project or use a template below:")

    # Create columns for project description and image upload
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        if dashboard_mode == "Test Mode":
            project_description = st.text_area(
                "Define your project first:",
                value="",  # Start empty for test mode
                placeholder="I am designing ...",
                height=120,
                help="I am designing ..."
            )
        else:
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


def _render_tasks_for_message(message_index: int):
    """Render tasks that should appear after this specific message"""
    try:
        task_display_queue = st.session_state.get('task_display_queue', [])

        if not task_display_queue:
            return

        # Find tasks linked to this message
        for task_entry in task_display_queue:
            linked_message = task_entry.get('message_index', -1)
            should_render = task_entry.get('should_render', False)
            already_displayed = task_entry.get('displayed', False)

            # Render task if it's linked to this message and not yet displayed
            if (linked_message == message_index and should_render and not already_displayed):
                task = task_entry['task']
                task_id = task_entry['task_id']

                print(f"🎯 MESSAGE_TASK: Rendering {task.task_type.value} after message {message_index}")

                # Create unique container for this message-task combination
                container_key = f"msg_{message_index}_task_{task_id}"

                with st.container(key=container_key):
                    _render_single_task_component(task_entry)

                # Mark as displayed
                task_entry['displayed'] = True
                task_entry['display_time'] = datetime.now().isoformat()

                print(f"🎯 MESSAGE_TASK: {task.task_type.value} rendered after message {message_index}")

    except Exception as e:
        print(f"⚠️ Error rendering tasks for message {message_index}: {e}")


def _render_task_if_active():
    """DEPRECATED: Legacy function - tasks now render per message"""
    # This function is no longer used - tasks render chronologically per message
    pass


def _render_single_task_component(task_entry):
    """Render a single task component with unique container"""
    try:
        task = task_entry['task']
        task_id = task_entry['task_id']
        guidance_type = task_entry.get('guidance_type', 'socratic')

        # Get actual task content from guidance system
        from dashboard.processors.task_guidance_system import TaskGuidanceSystem
        guidance_system = TaskGuidanceSystem()

        # Get the real task assignment based on test group
        if task.test_group == "MENTOR":
            task_data = guidance_system.mentor_tasks.get(task.task_type, {})
        elif task.test_group == "GENERIC_AI":
            task_data = guidance_system.generic_ai_tasks.get(task.task_type, {})
        elif task.test_group == "CONTROL":
            task_data = guidance_system.control_tasks.get(task.task_type, {})
        else:
            task_data = {}

        if not task_data:
            print(f"⚠️ No task data found for {task.task_type.value} in {guidance_type} mode")
            return

        # Get the actual task assignment content
        task_content = task_data.get("task_assignment", f"🎯 TASK {task.task_type.value.replace('_', ' ').title()}: Complete the design challenge")

        # Add specific guidance content based on type
        if guidance_type == "socratic" and task_data.get("socratic_questions"):
            questions = task_data["socratic_questions"]
            if questions:
                task_content += f"\n\n**Guided Exploration Question:**\n{questions[0]}"
        elif guidance_type == "direct" and task_data.get("direct_information"):
            info_list = task_data["direct_information"]
            if info_list:
                info_text = "\n".join([f"• {info}" for info in info_list[:2]])  # Show first 2 items
                task_content += f"\n\n**Helpful Information:**\n{info_text}"
        elif guidance_type == "minimal" and task_data.get("minimal_prompt"):
            task_content += f"\n\n**Guidance:** {task_data['minimal_prompt']}"

        # CRITICAL FIX: Create unique container for this specific task instance
        container_key = f"task_container_{task_id}"
        print(f"🚨 CONTAINER_DEBUG: Creating container with key: {container_key}")
        print(f"🚨 CONTAINER_DEBUG: Task type: {task.task_type.value}")
        print(f"🚨 CONTAINER_DEBUG: Task content preview: {task_content[:100]}...")

        try:
            with st.container(key=container_key):
                print(f"🚨 INSIDE_CONTAINER: Rendering {task.task_type.value} in container {container_key}")

                # Import and render task UI
                from dashboard.ui.task_ui_renderer import TaskUIRenderer
                renderer = TaskUIRenderer()
                renderer.render_task_component(task, task_content, guidance_type)

                print(f"🚨 CONTAINER_SUCCESS: Task {task_id} rendered in container {container_key}")

        except Exception as container_error:
            print(f"🚨 CONTAINER_ERROR: Failed to create container {container_key}: {container_error}")
            # Fallback: render without container
            from dashboard.ui.task_ui_renderer import TaskUIRenderer
            renderer = TaskUIRenderer()
            renderer.render_task_component(task, task_content, guidance_type)
            print(f"🚨 FALLBACK_RENDER: Task {task_id} rendered without container")

    except Exception as e:
        print(f"⚠️ Error rendering single task component: {e}")
        import traceback
        traceback.print_exc()