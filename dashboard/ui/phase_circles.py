"""
Phase Circles Component
Renders the 3-circle phase progression display with actual metrics from the phase progression system.
"""

import streamlit as st
from typing import Dict, Any, Optional


def render_phase_circles(phase_system, session_id: str) -> None:
    """
    Render the 3-circle phase progression display with percentages underneath.

    Args:
        phase_system: The PhaseProgressionSystem instance
        session_id: The current session ID
    """
    try:
        # Get actual progress data from the phase system
        summary = phase_system.get_session_summary(session_id)
        phase_summaries = summary.get('phase_summaries', {})
        current_phase = summary.get('current_phase', 'ideation')

        # Extract completion percentages for each phase
        ideation_percent = phase_summaries.get('ideation', {}).get('completion_percent', 0.0)
        visualization_percent = phase_summaries.get('visualization', {}).get('completion_percent', 0.0)
        materialization_percent = phase_summaries.get('materialization', {}).get('completion_percent', 0.0)

        # Determine which phase is currently active
        active_phase = current_phase.lower()

    except Exception as e:
        # Fallback to default values if phase system is unavailable
        print(f"Phase system unavailable, using defaults: {e}")
        ideation_percent = 0.0
        visualization_percent = 0.0
        materialization_percent = 0.0
        active_phase = 'ideation'

    # Render the phase circles
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <h4 style="color: #4A4A4A; margin-bottom: 20px;">Design Phase Progress</h4>
    </div>
    """, unsafe_allow_html=True)

    # Create three columns for the circles
    col1, col2, col3 = st.columns(3)
    with col1:
        _render_single_phase_circle(
            phase_name="Ideation",
            percentage=ideation_percent,
            is_active=(active_phase == 'ideation'),
            color='#dcc188'  # Yellow
        )

    with col2:
        _render_single_phase_circle(
            phase_name="Visualization",
            percentage=visualization_percent,
            is_active=(active_phase == 'visualization'),
            color='#cf436f' #Pink
        )

    with col3:
        _render_single_phase_circle(
            phase_name="Materialization",
            percentage=materialization_percent,
            is_active=(active_phase == 'materialization'),
            color='#784c80'  # Purple
        )


def _render_single_phase_circle(phase_name: str, percentage: float, is_active: bool, color: str) -> None:
    """
    Render a single phase circle with percentage.

    Args:
        phase_name: Name of the phase
        percentage: Completion percentage (0-100)
        is_active: Whether this phase is currently active
        color: Color for the circle
    """
    # Ensure percentage is within bounds
    percentage = max(0.0, min(100.0, percentage))

    # Calculate the stroke-dasharray for the progress circle
    circumference = 2 * 3.14159 * 45  # radius = 45
    progress_length = (percentage / 100) * circumference
    gap_length = circumference - progress_length

    # Determine opacity and border style based on active state
    opacity = "1.0" if is_active else "0.7"
    border_width = "3" if is_active else "2"

    circle_html = f"""
    <div style="text-align: center; margin: 10px 0;">
        <svg width="120" height="120" style="margin-bottom: 10px;">
            <!-- Background circle -->
            <circle cx="60" cy="60" r="45"
                    fill="none"
                    stroke="#e0e0e0"
                    stroke-width="8"/>
            <!-- Progress circle -->
            <circle cx="60" cy="60" r="45"
                    fill="none"
                    stroke="{color}"
                    stroke-width="{border_width}"
                    stroke-linecap="round"
                    stroke-dasharray="{progress_length} {gap_length}"
                    stroke-dashoffset="0"
                    transform="rotate(-90 60 60)"
                    opacity="{opacity}"/>
            <!-- Center text -->
            <text x="60" y="65"
                  text-anchor="middle"
                  font-family="Arial, sans-serif"
                  font-size="14"
                  font-weight="bold"
                  fill="{color}">
                {percentage:.0f}%
            </text>
        </svg>
        <div style="font-weight: bold; color: {color}; font-size: 14px; margin-top: 5px;">
            {phase_name}
        </div>
        <div style="font-size: 12px; color: #666; margin-top: 2px;">
            {percentage:.1f}%
        </div>
    </div>
    """

    st.markdown(circle_html, unsafe_allow_html=True)


def render_phase_metrics(phase_system, session_id: str) -> None:
    """
    Render detailed phase metrics below the circles.

    Args:
        phase_system: The PhaseProgressionSystem instance
        session_id: The current session ID
    """
    try:
        # Get detailed metrics from the phase system
        summary = phase_system.get_session_summary(session_id)
        phase_summaries = summary.get('phase_summaries', {})

        if not phase_summaries:
            return

        st.markdown("### 📊 Detailed Phase Metrics")

        # Create columns for each phase
        col1, col2, col3 = st.columns(3)

        phases = [
            ("Ideation", "ideation", col1),
            ("Visualization", "visualization", col2),
            ("Materialization", "materialization", col3)
        ]

        for phase_display, phase_key, col in phases:
            phase_data = phase_summaries.get(phase_key, {})

            with col:
                st.markdown(f"**{phase_display}**")

                # Show completion percentage
                completion = phase_data.get('completion_percent', 0.0)
                st.metric("Completion", f"{completion:.1f}%")

                # Show average score if available
                avg_score = phase_data.get('average_score', 0.0)
                if avg_score > 0:
                    st.metric("Avg Score", f"{avg_score:.2f}/5.0")

                # Show completed steps
                completed_steps = phase_data.get('completed_steps', 0)
                total_steps = phase_data.get('total_steps', 4)
                st.metric("Steps", f"{completed_steps}/{total_steps}")

    except Exception as e:
        st.error(f"Unable to load phase metrics: {e}")