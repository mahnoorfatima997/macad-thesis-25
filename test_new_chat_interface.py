#!/usr/bin/env python3
"""
Test script for the new chat interface.
Run this to test the modern chat interface with user messages on right and agent messages on left.
"""

import streamlit as st
import sys
import os

# Add the dashboard directory to the path
dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard')
sys.path.insert(0, dashboard_path)

# Now import using absolute paths
from dashboard.ui.chat_components import render_chat_interface, render_single_message
from dashboard.ui.styles import apply_dashboard_styles

# Configure Streamlit
st.set_page_config(
    page_title="Chat Interface Test",
    page_icon="",  # No icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styles
apply_dashboard_styles()

# Initialize session state for testing
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "user",
            "content": "Hello! I'm designing a sustainable office building.",
            "timestamp": "2024-01-01T10:00:00"
        },
        {
            "role": "assistant",
            "content": "Great! A sustainable office building is an excellent project. What specific aspects of sustainability are you focusing on? Energy efficiency, materials, or overall design approach?",
            "timestamp": "2024-01-01T10:01:00",
            "mentor_type": "MENTOR"
        },
        {
            "role": "user",
            "content": "I'm particularly interested in energy efficiency and natural lighting.",
            "timestamp": "2024-01-01T10:02:00"
        },
        {
            "role": "assistant",
            "content": "Excellent choices! For energy efficiency, consider:\n\n• **Orientation**: Position the building to maximize southern exposure\n• **Glazing**: Use high-performance windows with proper shading\n• **Thermal mass**: Incorporate materials that absorb and release heat slowly\n\nFor natural lighting:\n• **Skylights**: Strategic placement for even light distribution\n• **Light shelves**: Bounce light deeper into spaces\n• **Atriums**: Create central light wells\n\nWould you like me to elaborate on any of these strategies?",
            "timestamp": "2024-01-01T10:03:00",
            "mentor_type": "MENTOR"
        }
    ]

st.title("New Chat Interface Test (Icon-Free)")
st.markdown("This demonstrates the new modern chat interface with user messages on the right and agent messages on the left. All icons and emojis have been removed for a clean, professional look.")

# Test the new chat interface
render_chat_interface()

# Add some controls for testing
st.markdown("---")
st.subheader("Test Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Add User Message"):
        import datetime
        new_message = {
            "role": "user",
            "content": f"Test user message at {datetime.datetime.now().strftime('%H:%M:%S')}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.messages.append(new_message)
        st.rerun()

with col2:
    if st.button("Add Agent Message"):
        import datetime
        new_message = {
            "role": "assistant",
            "content": f"This is a test agent response at {datetime.datetime.now().strftime('%H:%M:%S')}. It demonstrates how the new chat interface looks with longer messages.",
            "timestamp": datetime.datetime.now().isoformat(),
            "mentor_type": "MENTOR"
        }
        st.session_state.messages.append(new_message)
        st.rerun()

with col3:
    if st.button("Clear Messages"):
        st.session_state.messages = []
        st.rerun()

# Show current message count
st.caption(f"Total messages: {len(st.session_state.messages)}")

# Display raw message data for debugging
with st.expander("Debug: Raw Message Data"):
    st.json(st.session_state.messages)
