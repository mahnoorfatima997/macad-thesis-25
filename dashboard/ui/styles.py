"""
CSS styles and theme management for the dashboard.
"""

import streamlit as st
from string import Template
from benchmarking.thesis_colors import THESIS_COLORS

def get_dashboard_css() -> str:
    """Generate the complete CSS for the dashboard using thesis colors."""
    css_template = Template(
        """
<style>
    :root {
        --primary-dark: $primary_dark;
        --primary-purple: $primary_purple;
        --primary-violet: $primary_violet;
        --primary-rose: $primary_rose;
        --primary-pink: $primary_pink;
        --neutral-light: $neutral_light;
        --neutral-warm: $neutral_warm;
        --neutral-orange: $neutral_orange;
        --accent-coral: $accent_coral;
        --accent-magenta: $accent_magenta;
    }

    /* App background and text */
    .stApp {
        background: #ffffff !important;
        color: var(--primary-dark) !important;
    }

    /* Ensure full width layout */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: none !important;
    }

    /* Full width for columns */
    .row-widget.stHorizontal > div {
        width: 100% !important;
    }

    /* Chat interface full width */
    .chat-window {
        width: 100% !important;
        max-width: none !important;
        margin: 20px 0 !important;
    }

    .chat-messages {
        width: 100% !important;
        max-width: none !important;
    }

    .message {
        width: 100% !important;
        max-width: none !important;
    }

    /* Better spacing for form elements */
    .stForm > div {
        margin-bottom: 1rem !important;
    }

    /* Full width for text areas and inputs */
    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox > div {
        width: 100% !important;
    }

    /* Better spacing between sections */
    .element-container {
        margin-bottom: 1.5rem !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        background: #ffffff !important;
        border-right: 1px solid var(--primary-dark) !important;
    }

    /* Main container card feel */
    .main .block-container {
        background: #ffffff !important;
        max-width: none !important;
        padding-top: 1rem;
        padding-bottom: 2rem;
        margin-left: 0 !important;
        border-radius: 12px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* Hide Streamlit misc */
    .stDeployButton{ display: none; }
    #MainMenu{ visibility: hidden; }
    footer{ visibility: hidden; }

    /* Headings + badges */
    .top-section { text-align: center; margin-bottom: 2rem; padding-top: 1rem; }
    .plan-badge {
        display: inline-block; background: #fff; color: var(--primary-dark);
        padding: 4px 12px; border-radius: 16px; font-size: 0.8rem;
        border: 1px solid var(--neutral-orange);
    }
    .greeting { font-size: 2.3rem; font-weight: 800; color: var(--primary-purple); margin-bottom: .25rem; }
    .compact-text { font-size: 14px; line-height: 1.5; color: var(--primary-dark); }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--primary-purple), var(--primary-violet)) !important;
        color: #fff !important;
        border: 0 !important;
        border-radius: 10px !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        transition: transform .05s ease, box-shadow .2s ease, filter .2s ease;
    }
    .stButton button:hover { filter: brightness(1.05); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
    .stButton button:active { transform: translateY(1px); }
    /* Make Start button (form submit) larger and full-width */
    .stFormSubmitButton button {
        width: 100% !important;
        min-height: 46px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        letter-spacing: 0.2px !important;
        border-radius: 12px !important;
    }
    /* Make Start button inside forms larger and full-width */
    .stForm .stButton button {
        width: 100% !important;
        min-height: 46px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        letter-spacing: 0.2px !important;
        border-radius: 12px !important;
    }

    /* Inputs (scoped to main container to avoid global side effects) */
    .main .block-container textarea,
    .main .block-container input:not([type="checkbox"]),
    .main .block-container select {
        border-radius: 10px !important;
        border: 1px solid var(--neutral-orange) !important;
        box-shadow: none !important;
    }
    .main .block-container textarea:focus,
    .main .block-container input:not([type="checkbox"]):focus,
    .main .block-container select:focus {
        outline: 2px solid var(--accent-magenta) !important;
        border-color: var(--accent-magenta) !important;
        box-shadow: 0 0 0 3px rgba(207, 67, 111, 0.15) !important;
    }

    /* Streamlit selectbox/combobox (BaseWeb) */
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border: 1px solid var(--neutral-orange) !important;
        background: #fff !important;
        box-shadow: none !important;
        min-height: 40px;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: var(--neutral-orange) !important;
        background: #fff !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        outline: 2px solid var(--accent-magenta) !important;
        border-color: var(--accent-magenta) !important;
        box-shadow: 0 0 0 3px rgba(207, 67, 111, 0.15) !important;
    }
    /* Dropdown menu panel */
    div[data-baseweb="popover"] div[data-baseweb="menu"] {
        background: #fff !important;
        border: 1px solid var(--neutral-orange) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
        overflow: hidden;
    }
    /* Ensure popover/layer doesn't dim the page */
    div[data-baseweb="layer"],
    div[data-baseweb="layer-container"],
    div[data-baseweb="portal"] { background: transparent !important; }
    div[data-baseweb="menu"] ul { background: #fff !important; }
    div[data-baseweb="menu"] li[role="option"] {
        background: #fff !important;
        color: var(--primary-dark) !important;
        padding: 10px 12px !important;
    }
    div[data-baseweb="menu"] li[role="option"][aria-selected="true"],
    div[data-baseweb="menu"] li[role="option"][data-focus="true"],
    div[data-baseweb="menu"] li[role="option"]:hover {
        background: rgba(92,79,115,0.10) !important; /* primary-purple tint */
        color: var(--primary-purple) !important;
    }
    /* Fallback for environments using role=listbox */
    ul[role="listbox"] {
        background: #fff !important;
        border: 1px solid var(--neutral-orange) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
    }
    ul[role="listbox"] > li[role="option"] { color: var(--primary-dark) !important; }
    ul[role="listbox"] > li[role="option"][aria-selected="true"],
    ul[role="listbox"] > li[role="option"][data-focus="true"],
    ul[role="listbox"] > li[role="option"]:hover {
        background: rgba(92,79,115,0.10) !important;
        color: var(--primary-purple) !important;
    }
    /* Fallback for environments using role="combobox" */
    div[role="combobox"] {
        border-radius: 10px !important;
        border: 1px solid var(--neutral-orange) !important;
        background: #fff !important;
        min-height: 40px;
    }

    /* Enhanced Chat Input Styling */
    div[data-testid="stChatInput"] {
        background: white !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
        border: 2px solid rgba(92,79,115,0.1) !important;
        padding: 8px !important;
        margin: 20px 0 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        max-width: none !important;
    }

    div[data-testid="stChatInput"]:hover {
        box-shadow: 0 6px 25px rgba(0,0,0,0.12) !important;
        border-color: rgba(92,79,115,0.2) !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        box-shadow: 0 0 0 3px rgba(92,79,115,0.15), 0 8px 30px rgba(0,0,0,0.15) !important;
        border-color: var(--primary-purple) !important;
        transform: translateY(-3px) !important;
    }

    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 18px 24px !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        color: var(--primary-dark) !important;
        resize: vertical !important;
        min-height: 100px !important;
        max-height: 300px !important;
        height: auto !important;
        font-family: inherit !important;
        box-shadow: none !important;
        outline: none !important;
        width: 100% !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }

    div[data-testid="stChatInput"] textarea:focus {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: rgba(92,79,115,0.6) !important;
        font-style: italic !important;
        font-size: 15px !important;
    }

    /* Enhanced Send Button */
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, var(--primary-purple), var(--primary-violet)) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 52px !important;
        height: 52px !important;
        min-width: 52px !important;
        min-height: 52px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(92,79,115,0.3) !important;
        transition: all 0.3s ease !important;
        margin: 4px !important;
        position: relative !important;
        overflow: hidden !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background: linear-gradient(135deg, var(--primary-violet), var(--primary-purple)) !important;
        box-shadow: 0 6px 20px rgba(92,79,115,0.4) !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="stChatInput"] button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 10px rgba(92,79,115,0.3) !important;
    }

    /* Send button icon - removed custom icon to prevent duplicates */

    /* Input container enhancements */
    div[data-testid="stChatInput"] > div {
        display: flex !important;
        align-items: flex-end !important;
        gap: 12px !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    /* Textarea container */
    div[data-testid="stChatInput"] > div > div:first-child {
        flex: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }

    /* Button container */
    div[data-testid="stChatInput"] > div > div:last-child {
        margin: 0 !important;
        padding: 0 !important;
        flex-shrink: 0 !important;
    }

    /* Modern Chat Interface - Clean & Seamless */
    .chat-window {
        background: #f8f9fa !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
        max-height: 600px !important;
        overflow-y: auto !important;
        width: 100% !important;
        max-width: none !important;
    }

    .chat-messages {
        display: flex !important;
        flex-direction: column !important;
        gap: 0 !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .message {
        display: flex !important;
        align-items: flex-start !important;
        gap: 12px !important;
        width: 100% !important;
        max-width: none !important;
        margin: 0 !important;
        padding: 8px 0 !important;
        position: relative !important;
        border: none !important;
        background: transparent !important;
        box-sizing: border-box !important;
    }

    .user-message {
        flex-direction: row-reverse !important;
        align-self: flex-end !important;
        margin-left: auto !important;
        max-width: 70% !important;
        margin-bottom: 0 !important;
        justify-content: flex-end !important;
    }

    .agent-message {
        flex-direction: row !important;
        align-self: flex-start !important;
        margin-right: auto !important;
        max-width: 70% !important;
        margin-bottom: 0 !important;
        justify-content: flex-start !important;
    }

    /* Clean avatar circles */
    .message-avatar {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 20px !important;
        flex-shrink: 0 !important;
        background: transparent !important;
        border: 2px solid rgba(0,0,0,0.1) !important;
        margin-top: 4px !important;
    }

    .user-avatar {
        background: transparent !important;
        border-color: var(--accent-coral) !important;
    }

    .agent-avatar {
        background: transparent !important;
        border-color: var(--primary-purple) !important;
    }

    /* Clean message content */
    .message-content {
        background: transparent !important;
        padding: 12px 16px !important;
        border-radius: 18px !important;
        box-shadow: none !important;
        border: none !important;
        position: relative !important;
        width: 100% !important;
        max-width: none !important;
        margin: 0 !important;
        box-sizing: border-box !important;
    }

    .user-content {
        background: linear-gradient(135deg, var(--accent-coral), var(--accent-magenta)) !important;
        color: white !important;
        border-radius: 18px !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    .agent-content {
        background: white !important;
        color: var(--primary-dark) !important;
        border-radius: 18px !important;
        border: 1px solid rgba(92,79,115,0.1) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    .message-header {
        margin-bottom: 6px !important;
    }

    .agent-name {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--primary-purple) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .message-text {
        line-height: 1.5 !important;
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
        margin: 0 !important;
    }

    .message-time {
        font-size: 11px !important;
        opacity: 0.7 !important;
        margin-top: 6px !important;
        text-align: right !important;
    }

    .user-content .message-time {
        text-align: left !important;
    }

    /* Create flowing conversation */
    .message:not(:last-child) {
        margin-bottom: 0 !important;
    }

    .user-message + .agent-message,
    .agent-message + .user-message {
        margin-top: 0 !important;
        padding-top: 0 !important;
        border-top: none !important;
    }

    /* Smooth spacing between messages */
    .user-message + .user-message,
    .agent-message + .agent-message {
        margin-top: -4px !important;
        padding-top: 4px !important;
    }

    .user-message + .agent-message {
        margin-top: 8px !important;
        padding-top: 8px !important;
    }

    .agent-message + .user-message {
        margin-top: 8px !important;
        padding-top: 8px !important;
    }

    /* Clean typing indicator */
    .typing-indicator {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 16px !important;
        background: white !important;
        border-radius: 18px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        border: 1px solid rgba(92,79,115,0.1) !important;
        margin-top: 16px !important;
        max-width: 200px !important;
        margin-left: 52px !important;
        position: relative !important;
    }

    .typing-dots {
        display: flex !important;
        gap: 4px !important;
    }

    .typing-dots span {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background: var(--primary-purple) !important;
        animation: typing 1.4s infinite ease-in-out !important;
    }

    .typing-dots span:nth-child(1) { animation-delay: -0.32s !important; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s !important; }

    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }

    /* Message animations */
    .message {
        opacity: 1;
        transform: translateY(0);
        transition: all 0.3s ease;
    }

    .message.fade-in {
        animation: fadeInUp 0.3s ease forwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Hover effects for messages */
    .message-content:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }

    /* Responsive design for mobile */
    @media (max-width: 768px) {
        .message {
            max-width: 95%;
        }
        
        .chat-window {
            padding: 15px;
            margin: 15px 0;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            font-size: 16px;
        }
        
        .message-content {
            padding: 12px;
        }

        div[data-testid="stChatInput"] {
            margin: 15px 0 !important;
            border-radius: 18px !important;
        }
        
        div[data-testid="stChatInput"] textarea {
            padding: 16px 20px !important;
            font-size: 15px !important;
            min-height: 100px !important;
            max-height: 300px !important;
        }
        
        div[data-testid="stChatInput"] button {
            width: 48px !important;
            height: 48px !important;
            min-width: 48px !important;
            min-height: 48px !important;
        }
    }

    /* Old chat message styles removed - new seamless interface takes precedence */

    /* Cards */
    .metric-card, .mode-selector, .chat-container {
        background: #fff;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 8px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
    }

    /* Status chips */
    .status-indicator { display:inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
    .status-ready { background: var(--accent-coral); }
    .status-warning { background: var(--neutral-orange); }
    .status-error { background: var(--accent-magenta); }

    /* Tabs (if present) */
    div[role="tablist"] { gap: .5rem; border-bottom: 1px solid var(--neutral-orange); }
    div[role="tab"] {
        padding: .5rem 1rem; border-radius: 10px 10px 0 0; color: var(--primary-dark);
    }
    div[role="tab"][aria-selected="true"] {
        background: #fff; color: var(--primary-purple); border: 1px solid var(--neutral-orange); border-bottom-color: #fff;
    }

    /* Info blocks: Socratic/Agentic boxes */
    .info-tile {
        background: #fff; border: 1px solid var(--neutral-orange); border-left: 5px solid var(--primary-purple);
        border-radius: 12px; padding: 16px;
    }

    /* Animation for new messages */
    .message-input-animation {
        animation: slideInUp 0.4s ease-out !important;
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }


</style>
"""
    )
    return css_template.substitute(**THESIS_COLORS)

def apply_dashboard_styles():
    """Apply the dashboard CSS styles to the current Streamlit app."""
    st.markdown(get_dashboard_css(), unsafe_allow_html=True) 