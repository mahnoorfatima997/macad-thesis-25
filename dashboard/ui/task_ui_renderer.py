"""
Clean Task UI Renderer - Matches Gamification Design Style
Provides clean, focused task presentation with thesis colors and geometric shapes
"""

import streamlit as st
from typing import Dict, Any, List
from dashboard.processors.dynamic_task_manager import ActiveTask, TaskType

# Import thesis colors for consistent styling
try:
    from benchmarking.thesis_colors import THESIS_COLORS, UI_COLORS
except ImportError:
    # Fallback colors if import fails
    THESIS_COLORS = {
        'primary_dark': '#4f3a3e',
        'primary_purple': '#5c4f73',
        'primary_violet': '#784c80',
        'primary_rose': '#b87189',
        'primary_pink': '#cda29a',
        'neutral_warm': '#dcc188',
        'neutral_orange': '#d99c66',
        'accent_coral': '#cd766d',
        'accent_magenta': '#cf436f',
    }
    UI_COLORS = {
        'background': '#faf8f5',
        'text_primary': '#2c2328',
        'border': '#e0ceb5',
    }


class TaskUIRenderer:
    """Clean task renderer matching gamification UI style with thesis colors"""

    def __init__(self):
        self.test_group_themes = self._initialize_clean_themes()

    def _initialize_clean_themes(self) -> Dict[str, Dict[str, str]]:
        """Initialize clean visual themes using thesis colors and geometric shapes"""
        return {
            "MENTOR": {
                "primary": THESIS_COLORS['primary_violet'],
                "secondary": THESIS_COLORS['primary_rose'],
                "accent": THESIS_COLORS['primary_pink'],
                "gradient": f"linear-gradient(135deg, {THESIS_COLORS['primary_violet']} 0%, {THESIS_COLORS['primary_rose']} 50%, {THESIS_COLORS['primary_pink']} 100%)",
                "icon": "◈",  # Geometric shape instead of emoji
                "style_name": "Guided Exploration",
                "emphasis": "Socratic Questioning"
            },
            "GENERIC_AI": {
                "primary": THESIS_COLORS['primary_purple'],
                "secondary": THESIS_COLORS['accent_coral'],
                "accent": THESIS_COLORS['neutral_warm'],
                "gradient": f"linear-gradient(135deg, {THESIS_COLORS['primary_purple']} 0%, {THESIS_COLORS['accent_coral']} 50%, {THESIS_COLORS['neutral_warm']} 100%)",
                "icon": "◉",  # Geometric shape instead of emoji
                "style_name": "Direct Information",
                "emphasis": "information delivery"
            },
            "CONTROL": {
                "primary": THESIS_COLORS['primary_dark'],
                "secondary": THESIS_COLORS['primary_purple'],
                "accent": UI_COLORS['border'],
                "gradient": f"linear-gradient(135deg, {THESIS_COLORS['primary_dark']} 0%, {THESIS_COLORS['primary_purple']} 50%, {UI_COLORS['border']} 100%)",
                "icon": "◐",  # Geometric shape instead of emoji
                "style_name": "Self-Direction",
                "emphasis": "independent work"
            }
        }
    
    def render_task_as_enhanced_message(self, task: ActiveTask, base_response: str,
                                      task_content: str, guidance_type: str) -> str:
        """Render task as clean UI component separate from chat message (like gamification)"""

        # Tasks should NOT be embedded in agent messages
        # They should be rendered separately like gamification components
        # Return only the base response - task will be rendered separately
        return base_response

    def render_task_component(self, task: ActiveTask, task_content: str, guidance_type: str) -> None:
        """Render task as separate UI component matching gamification style"""

        # Clear any existing task UI to prevent conflicts
        import streamlit as st

        theme = self.test_group_themes.get(task.test_group, self.test_group_themes["MENTOR"])

        # Extract clean task information
        task_title = self._extract_clean_task_title(task_content)
        task_assignment = self._extract_clean_assignment(task_content)

        # Ensure content is properly formatted for HTML
        task_title = task_title if task_title else "DESIGN TASK"
        task_assignment = task_assignment if task_assignment else "Complete the design challenge."

        # Render clean task UI matching gamification style
        self._render_clean_task_ui(task, task_title, task_assignment, task_content, guidance_type, theme)
    
    def _render_clean_task_ui(self, task: ActiveTask, task_title: str, task_assignment: str,
                             task_content: str, guidance_type: str, theme: Dict[str, str]) -> None:
        """Render clean task UI matching gamification component style"""

        # Use container to isolate task UI rendering
        with st.container():
            # Add separator to ensure clean rendering
            st.markdown("---")

            # Inject CSS for animations (matching gamification)
            self._inject_task_animations()

            # FIXED: Simple HTML structure matching working gamification approach
            st.markdown(f"""
            <div style="
                background: {theme['gradient']};
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 15px;
                    font-size: 1.8em;
                    color: white;
                ">
                    {theme['icon']}
                </div>
                <h2 style="
                    color: white;
                    margin: 0;
                    font-weight: bold;
                    font-size: 1.6em;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    letter-spacing: 1px;
                ">{task_title}</h2>
                <div style="
                    color: rgba(255,255,255,0.9);
                    font-size: 1em;
                    margin-top: 8px;
                    font-weight: 500;
                ">{theme['style_name']} • {theme['emphasis']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Render task assignment in clean box
        duration = self._extract_task_duration(task_content)
        considerations = self._extract_task_considerations_list(task_content)

        self._render_task_assignment_box(
            task_assignment,
            theme,
            duration=duration,
            considerations=considerations
        )




        # Render guidance based on type with actual content
        self._render_clean_guidance_with_content(task_content, guidance_type, theme)

        # Render phase progress indicator (clean, no manual completion button)
        self._render_phase_progress(task, theme)

        # Add final separator to ensure clean separation
        st.markdown("---")
    
    def _extract_clean_task_title(self, content: str) -> str:
        """Extract clean task title from content"""
        lines = content.split('\n')
        for line in lines:
            # Look for task titles in different formats
            if ('🎯 TASK' in line or '◉ TASK' in line) and ':' in line:
                # Clean up the title - remove emojis and formatting
                title = line.replace('🎯 TASK', '').replace('◉ TASK', '').replace('**', '').replace(':', '').strip()
                return title if title else "DESIGN TASK"
            elif line.startswith('**◉ TASK') and ':' in line:
                # Handle the format: **◉ TASK 1.1: Architectural Concept Development**
                title = line.replace('**◉ TASK', '').replace('**', '').replace(':', '').strip()
                return title if title else "DESIGN TASK"
        return "DESIGN TASK"
    #2708
    def _extract_clean_assignment(self, content: str) -> str:
        """Extract assignment text ONLY (exclude Consider bullets and Duration)."""
        lines = content.split('\n')
        assignment_lines = []
        in_assignment = False

        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            # Enter assignment block
            if (
                '**Your Assignment**' in line
                or line.startswith('Your Assignment:')
                or line.startswith('Assignment:')
                or line.startswith('**Your Assignment')
            ):
                in_assignment = True
                # If the assignment starts on this same line after a colon, grab it
                if ':' in line:
                    part = line.split(':', 1)[1].strip()
                    if part:
                        assignment_lines.append(self._strip_md(part))
                continue

            if in_assignment:
                # STOP when we reach Consider or Duration or a new bold header
                if (
                    line.startswith('**Consider**')
                    or line.startswith('Consider')
                    or line.lower().startswith('duration')
                    or (line.startswith('**') and 'Assignment' not in line)
                ):
                    break

                # Skip bullet lines (they belong to Consider)
                if line.startswith('•') or line.startswith('- '):
                    continue

                # Keep normal text as part of the assignment
                assignment_lines.append(self._strip_md(line))

        return ' '.join(assignment_lines).strip() or "Complete the design challenge assignment."
    
    def _strip_md(self, s: str) -> str:
        """Remove simple Markdown emphasis markers."""
        return s.replace('**', '').replace('*', '').strip()

    def _inject_task_animations(self) -> None:
        """Inject CSS animations matching gamification style"""
        st.markdown("""
        <style>
        @keyframes float {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        @keyframes glow {
            0% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        </style>
        """, unsafe_allow_html=True)

    #2708
    def _extract_task_considerations_list(self, content: str) -> list[str]:
        """Return bullet items (no HTML) from the '**Consider**' section."""
        lines = content.split('\n')
        items, in_block = [], False
        for line in lines:
            if '**Consider**' in line:
                in_block = True
                continue
            if in_block:
                if line.startswith('•'):
                    items.append(line[1:].strip())  # drop the leading bullet
                elif line.startswith('**'):  # next bold header ends the block
                    break
        return items

    from typing import Optional, Dict

    def _render_task_assignment_box(
        self,
        assignment: str,
        theme: Dict[str, str],
        duration: Optional[str] = None,
        considerations: Optional[list[str]] = None,
    ) -> None:
        """Render assignment with optional duration + considerations using native Streamlit (no HTML)."""
        with st.container():
            # Header
            st.markdown(f"**◆ Your Assignment**")
            # Body
            st.markdown(assignment)

            # Duration (small caption)
            if duration:
                st.caption(f"⏱ Duration: {duration}")

            # Considerations as a normal Markdown list
            if considerations:
                st.markdown("**Key considerations**")
                st.markdown("\n".join(f"- {c}" for c in considerations))

    def _render_clean_guidance(self, task: ActiveTask, guidance_type: str, theme: Dict[str, str]) -> None:
        """Render clean guidance based on test group"""
        if guidance_type == "socratic":
            self._render_socratic_guidance_clean(theme)
        elif guidance_type == "direct":
            self._render_direct_guidance_clean(theme)
        elif guidance_type == "minimal":
            self._render_minimal_guidance_clean(theme)

    def _render_phase_progress(self, task: ActiveTask, theme: Dict[str, str]) -> None:
        """Render clean phase progress indicator (no manual completion button)"""
        st.markdown(f"""
        <div style="
            background: {UI_COLORS['background']};
            border: 2px solid {theme['primary']};
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                margin-bottom: 10px;
            ">◉ Task Progress</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 0.95em;
                line-height: 1.4;
            ">
                <strong>Phase:</strong> {task.current_phase.title()}<br>
                <strong>Triggered at:</strong> {task.triggered_at_completion}% completion<br>
                <strong>Status:</strong> Active - Linked to phase progression
            </div>
            <div style="
                background: {UI_COLORS['border']};
                height: 6px;
                border-radius: 3px;
                margin: 10px 0;
                overflow: hidden;
            ">
                <div style="
                    background: {theme['gradient']};
                    height: 100%;
                    width: 60%;
                    border-radius: 3px;
                    animation: pulse 2s infinite;
                "></div>
            </div>
            <div style="
                color: {theme['secondary']};
                font-size: 0.9em;
                font-style: italic;
            ">Task completion is automatically tracked through phase progression</div>
        </div>
        """, unsafe_allow_html=True)

    def _render_clean_guidance_with_content(self, task_content: str, guidance_type: str, theme: Dict[str, str]) -> None:
        """Render clean guidance with actual content extracted from task"""
        if guidance_type == "socratic":
            # Extract Socratic question from content
            guidance_content = self._extract_socratic_question(task_content)
            self._render_socratic_guidance_with_content(guidance_content, theme)
        elif guidance_type == "direct":
            # Extract direct information from content
            guidance_content = self._extract_direct_information(task_content)
            self._render_direct_guidance_with_content(guidance_content, theme)
        elif guidance_type == "minimal":
            # Extract minimal guidance from content
            guidance_content = self._extract_minimal_guidance(task_content)
            self._render_minimal_guidance_with_content(guidance_content, theme)

    def _extract_socratic_question(self, content: str) -> str:
        """Extract Socratic question from task content"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Look for guided exploration question section
            if ('Guided Exploration Question:' in line or
                'Exploration Question:' in line or
                '**Guided Exploration Question:**' in line):
                # Check next line for the question
                if i + 1 < len(lines):
                    question = lines[i + 1].strip()
                    if question and len(question) > 10:
                        return question
            # Look for any line that's a question and reasonably long
            elif line.strip().endswith('?') and len(line.strip()) > 30:
                # Make sure it's not a generic question
                if ('design' in line.lower() or 'community' in line.lower() or
                    'space' in line.lower() or 'architecture' in line.lower()):
                    return line.strip()
        return "Consider the deeper implications of your design decisions."

    def _extract_direct_information(self, content: str) -> str:
        """Extract direct information from task content"""
        lines = content.split('\n')
        info_lines = []
        in_info_section = False

        for line in lines:
            if 'Helpful Information:' in line:
                in_info_section = True
                continue
            elif in_info_section and line.startswith('•'):
                info_lines.append(line.strip())
            elif in_info_section and line.strip() and not line.startswith('•'):
                break

        if info_lines:
            return '\n'.join(info_lines[:2])  # Show first 2 items
        return "Direct information and examples will be provided to help you complete this task effectively."

    def _extract_minimal_guidance(self, content: str) -> str:
        """Extract minimal guidance from task content"""
        lines = content.split('\n')
        for line in lines:
            if 'Guidance:' in line:
                return line.replace('**Guidance:**', '').strip()
        return "Work through this task independently using your design knowledge and experience."

    def _render_socratic_guidance_clean(self, theme: Dict[str, str]) -> None:
        """Render clean Socratic guidance matching gamification style"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['primary']}12, {theme['secondary']}12);
            border: 2px solid {theme['primary']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                font-size: 0.95em;
                margin-bottom: 10px;
            ">◈ Guided Exploration</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 0.95em;
                line-height: 1.5;
                font-style: italic;
            ">
                Explore this challenge through thoughtful questioning and reflection.
                Consider multiple perspectives and approaches.
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_direct_guidance_clean(self, theme: Dict[str, str]) -> None:
        """Render clean direct guidance matching gamification style"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['primary']}12, {theme['secondary']}12);
            border: 2px solid {theme['primary']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                font-size: 1.0em;
                margin-bottom: 10px;
            ">◉ Information Support</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 1.00em;
                line-height: 1.5;
            ">
                Direct information and examples will be provided to help you
                complete this task effectively.
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_minimal_guidance_clean(self, theme: Dict[str, str]) -> None:
        """Render clean minimal guidance matching gamification style"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['primary']}12, {theme['secondary']}12);
            border: 2px solid {theme['primary']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            text-align: center;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 10px;
            ">◐ Self-Directed Work</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 1.05em;
                line-height: 1.5;
            ">
                Work through this task independently using your design knowledge and experience.
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_socratic_guidance_with_content(self, guidance_content: str, theme: Dict[str, str]) -> None:
        """Render Socratic guidance with actual question content"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['primary']}12, {theme['secondary']}12);
            border: 2px solid {theme['primary']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 15px;
                text-align: center;
            ">◈ Guided Exploration</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 1.05em;
                line-height: 1.6;
                font-style: italic;
                background: rgba(255,255,255,0.7);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid {theme['primary']};
            ">
                {guidance_content}
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_direct_guidance_with_content(self, guidance_content: str, theme: Dict[str, str]) -> None:
        """Render direct guidance with actual information content"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['primary']}12, {theme['secondary']}12);
            border: 2px solid {theme['primary']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                font-size: 1em;
                margin-bottom: 15px;
                text-align: center;
            ">◉ Helpful Information</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 1em;
                line-height: 1.6;
                background: rgba(255,255,255,0.7);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid {theme['primary']};
                font-style: italic;
            ">
                {guidance_content.replace('•', '▸')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_minimal_guidance_with_content(self, guidance_content: str, theme: Dict[str, str]) -> None:
        """Render minimal guidance with actual content"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(45deg, {theme['primary']}12, {theme['secondary']}12);
            border: 2px solid {theme['primary']};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        ">
            <div style="
                color: {theme['primary']};
                font-weight: bold;
                font-size: 1.0em;
                margin-bottom: 15px;
                text-align: center;
            ">◐ Self-Directed Work</div>
            <div style="
                color: {UI_COLORS['text_primary']};
                font-size: 1.00em;
                font-style: italic;
                line-height: 1.6;
                background: rgba(255,255,255,0.7);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid {theme['primary']};
            ">
                {guidance_content}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # REMOVED: Old cluttered methods - keeping only essential ones for compatibility
    def _extract_task_considerations(self, content: str) -> str:
        """Extract key considerations as formatted list"""
        lines = content.split('\n')
        considerations = []
        in_considerations = False
        
        for line in lines:
            if '**Consider**' in line:
                in_considerations = True
                continue
            elif in_considerations and line.startswith('•'):
                considerations.append(line.strip())
            elif in_considerations and line.startswith('**'):
                break
        
        if considerations:
            considerations_html = f"""
            <div style="margin-top: 10px;">
                <h4 style="color: #666; margin: 0 0 8px 0; font-size: 1em;">KEY CONSIDERATIONS</h4>
                <ul style="margin: 0; padding-left: 20px; color: #555;">
                    {''.join([f'<li style="margin-bottom: 5px;">{item[1:].strip()}</li>' for item in considerations])}
                </ul>
            </div>
            """
            return considerations_html
        return ""
    
    def _extract_task_duration(self, content: str) -> str:
        """Extract duration information"""
        if 'Duration' in content:
            lines = content.split('\n')
            for line in lines:
                if 'Duration' in line:
                    return line.replace('**', '').replace('Duration:', '').strip()
        return "15 minutes"
    
    # REMOVED: Old cluttered guidance and progress methods
    # These have been replaced with clean methods matching gamification style
    
    def render_task_completion_feedback(self, task: ActiveTask) -> str:
        """Render feedback when task is completed"""
        theme = self.test_group_themes.get(task.test_group, self.test_group_themes["MENTOR"])
        
        return f"""
        <div style="
            background: linear-gradient(135deg, {theme['primary_color']}20, {theme['primary_color']}10);
            border: 2px solid {theme['primary_color']};
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
        ">
            <div style="font-size: 2em; margin-bottom: 10px;">✅</div>
            <h3 style="
                color: {theme['primary_color']};
                margin: 0 0 5px 0;
            ">Task Completed!</h3>
            <p style="
                color: #666;
                margin: 0;
                font-size: 0.9em;
            ">
                {task.task_type.value.replace('_', ' ').title()} has been marked as complete.
            </p>
        </div>
        """
