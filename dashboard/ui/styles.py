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
        max-width: 1200px;
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

    /* Chat input */
    div[data-testid="stChatInput"] textarea {
        background: #fff;
        border: 1px solid var(--neutral-orange);
        border-radius: 12px;
    }
    div[data-testid="stChatInput"] button {
        background: var(--accent-magenta) !important;
        color: #fff !important;
        border-radius: 10px !important;
    }

    /* Chat messages */
    .chat-message {
        background: #fff;
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
        border: 1px solid rgba(0,0,0,0.06);
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .chat-message.user {
        border-left: 5px solid var(--accent-coral);
        background: linear-gradient(0deg, rgba(205,118,109,0.06), rgba(205,118,109,0.06)), #fff;
    }
    .chat-message.assistant {
        border-left: 5px solid var(--primary-purple);
        background: linear-gradient(0deg, rgba(92,79,115,0.06), rgba(92,79,115,0.06)), #fff;
    }

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
</style>
"""
    )
    return css_template.substitute(**THESIS_COLORS)

def apply_dashboard_styles():
    """Apply the dashboard CSS styles to the current Streamlit app."""
    st.markdown(get_dashboard_css(), unsafe_allow_html=True) 