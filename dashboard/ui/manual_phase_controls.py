"""
Manual Phase Controls Component
Provides UI buttons for manual phase progression in GENERIC_AI and CONTROL modes
"""

import streamlit as st
from typing import Optional
from thesis_tests.data_models import TestGroup


def render_manual_phase_controls(mode_processor, test_group: TestGroup) -> None:
    """
    Render manual phase progression controls for GENERIC_AI and CONTROL modes
    
    Args:
        mode_processor: The mode processor instance with manual phase advancement methods
        test_group: The current test group (GENERIC_AI or CONTROL)
    """
    
    # Only show manual controls for GENERIC_AI and CONTROL modes
    if test_group not in [TestGroup.GENERIC_AI, TestGroup.CONTROL]:
        return
    
    current_phase = st.session_state.get('test_current_phase', 'Ideation')
    
    # Don't show controls if already at final phase
    if current_phase == 'Complete':
        return
    
    # Phase progression mapping
    phase_progression = {
        'Ideation': 'Visualization',
        'Visualization': 'Materialization',
        'Materialization': 'Complete'
    }
    
    next_phase = phase_progression.get(current_phase, 'Complete')
    
    if next_phase == 'Complete':
        return
    
    # Create a container for the manual phase controls
    st.markdown("---")
    
    # Different styling for each test group
    if test_group == TestGroup.GENERIC_AI:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #5c4f73 0%, #7a6b8a 50%, #9b8ba3 100%);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
            color: white;
        ">
            <h4 style="margin: 0 0 10px 0; color: white;">◉ Phase Progression Control</h4>
            <p style="margin: 0 0 15px 0; font-size: 14px; opacity: 0.9;">
                Ready to move to the next phase? Click below when you've completed your work.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        button_style = "primary"
        button_text = f"◉ Advance to {next_phase} Phase"
        
    elif test_group == TestGroup.CONTROL:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4f3a3e 0%, #6b4f54 50%, #8a6b70 100%);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
            color: white;
        ">
            <h4 style="margin: 0 0 10px 0; color: white;">◐ Self-Directed Phase Control</h4>
            <p style="margin: 0 0 15px 0; font-size: 14px; opacity: 0.9;">
                Proceed to the next phase when you're ready to continue.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        button_style = "secondary"
        button_text = f"◐ Continue to {next_phase} Phase"
    
    # Create columns for button layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Manual phase advancement button
        if st.button(
            button_text,
            type=button_style,
            use_container_width=True,
            key=f"manual_phase_advance_{current_phase}_{test_group.value}"
        ):
            # Advance phase manually
            reason = f"User-initiated advancement from {current_phase}"
            mode_processor.advance_phase_manually(reason)
    
    # Show current phase status
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px; font-size: 12px; color: #666;">
        Current Phase: <strong>{current_phase}</strong> → Next: <strong>{next_phase}</strong>
    </div>
    """, unsafe_allow_html=True)


def render_phase_completion_indicator(test_group: TestGroup) -> None:
    """
    Render a phase completion indicator for manual progression modes using Streamlit native components

    Args:
        test_group: The current test group
    """

    # Only show for GENERIC_AI and CONTROL modes
    if test_group not in [TestGroup.GENERIC_AI, TestGroup.CONTROL]:
        return

    current_phase = st.session_state.get('test_current_phase', 'Ideation')

    # Phase completion status
    phases = ['Ideation', 'Visualization', 'Materialization']
    current_index = phases.index(current_phase) if current_phase in phases else 0

    # Header
    st.markdown("##### Phase Progress")

    # Create columns for phase indicators
    cols = st.columns([1, 0.3, 1, 0.3, 1])

    for i, phase in enumerate(phases):
        col_index = i * 2  # Skip arrow columns

        with cols[col_index]:
            if i < current_index:
                # Completed phase
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: #28a745;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        margin: 0 auto 5px;
                        line-height: 40px;
                    ">✓</div>
                    <div style="font-size: 12px; color: #28a745; font-weight: bold; text-align: center;">{phase}</div>
                </div>
                """, unsafe_allow_html=True)
            elif i == current_index:
                # Current phase
                if test_group == TestGroup.GENERIC_AI:
                    color = "#5c4f73"
                    icon = "◉"
                else:  # CONTROL
                    color = "#4f3a3e"
                    icon = "◐"

                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: {color};
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        margin: 0 auto 5px;
                        line-height: 40px;
                    ">{icon}</div>
                    <div style="font-size: 12px; color: {color}; font-weight: bold; text-align: center;">{phase}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Future phase
                st.markdown(f"""
                <div style="text-align: center; opacity: 0.5;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: #e0e0e0;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        margin: 0 auto 5px;
                        line-height: 40px;
                    ">○</div>
                    <div style="font-size: 12px; color: #e0e0e0; font-weight: bold; text-align: center;">{phase}</div>
                </div>
                """, unsafe_allow_html=True)

        # Add arrow between phases (except after last phase)
        if i < len(phases) - 1:
            with cols[col_index + 1]:
                st.markdown("""
                <div style="text-align: center; margin-top: 15px;">
                    <span style="color: #ccc; font-size: 20px;">→</span>
                </div>
                """, unsafe_allow_html=True)


def should_show_manual_controls(test_group: TestGroup) -> bool:
    """
    Check if manual phase controls should be shown for the current test group
    
    Args:
        test_group: The current test group
        
    Returns:
        bool: True if manual controls should be shown
    """
    return test_group in [TestGroup.GENERIC_AI, TestGroup.CONTROL]


def get_phase_advancement_message(current_phase: str, next_phase: str, test_group: TestGroup) -> str:
    """
    Get an appropriate message for phase advancement based on test group
    
    Args:
        current_phase: Current phase name
        next_phase: Next phase name  
        test_group: Current test group
        
    Returns:
        str: Appropriate advancement message
    """
    
    if test_group == TestGroup.GENERIC_AI:
        messages = {
            ('Ideation', 'Visualization'): "Great work on your concept development! Ready to move into visual design?",
            ('Visualization', 'Materialization'): "Excellent visual development! Time to focus on technical implementation?",
            ('Materialization', 'Complete'): "Outstanding technical work! Ready to complete your design process?"
        }
    elif test_group == TestGroup.CONTROL:
        messages = {
            ('Ideation', 'Visualization'): "Continue to the next phase when you're ready to proceed.",
            ('Visualization', 'Materialization'): "Advance to technical development when you feel prepared.",
            ('Materialization', 'Complete'): "Complete your design process when you're satisfied with your work."
        }
    else:
        # Default messages
        messages = {
            ('Ideation', 'Visualization'): f"Ready to advance from {current_phase} to {next_phase}?",
            ('Visualization', 'Materialization'): f"Ready to advance from {current_phase} to {next_phase}?",
            ('Materialization', 'Complete'): f"Ready to complete your design process?"
        }
    
    return messages.get((current_phase, next_phase), f"Ready to advance from {current_phase} to {next_phase}?")
