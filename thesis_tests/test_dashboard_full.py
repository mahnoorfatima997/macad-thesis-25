"""
MEGA Architectural Mentor - Full Test Dashboard
Supports all three test conditions: MENTOR, Generic AI, and Control
For cognitive benchmarking and linkography analysis
"""

import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime
import os
from typing import Dict, List, Optional, Any
import sys

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from thesis_tests.data_models import (
    TestSession, TestParticipant, DesignMove, TestPhase,
    InteractionData, AssessmentResult, TestGroup
)
from thesis_tests.logging_system import TestSessionLogger
from thesis_tests.mentor_environment import MentorTestEnvironment, MENTOR_AVAILABLE
from thesis_tests.generic_ai_environment import GenericAITestEnvironment
from thesis_tests.control_environment import ControlTestEnvironment
from thesis_tests.assessment_tools import PreTestAssessment, PostTestAssessment

# Try to import linkography logger
try:
    from thesis_tests.linkography_logger import LinkographyLogger
    LINKOGRAPHY_AVAILABLE = True
except ImportError:
    try:
        from thesis_tests.linkography_logger_simple import SimpleLinkographyLogger as LinkographyLogger
        LINKOGRAPHY_AVAILABLE = True
    except ImportError:
        LINKOGRAPHY_AVAILABLE = False
        print("Warning: Linkography logger not available")

# Page configuration
st.set_page_config(
    page_title="MEGA Cognitive Benchmarking Test Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TestDashboard:
    """Main test dashboard for all three test environments"""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_environments()
        
    def initialize_session_state(self):
        """Initialize all session state variables"""
        if 'test_session' not in st.session_state:
            st.session_state.test_session = None
        if 'participant' not in st.session_state:
            st.session_state.participant = None
        if 'current_phase' not in st.session_state:
            st.session_state.current_phase = TestPhase.PRE_TEST
        if 'test_group' not in st.session_state:
            st.session_state.test_group = None
        if 'session_logger' not in st.session_state:
            st.session_state.session_logger = None
        if 'linkography_logger' not in st.session_state:
            st.session_state.linkography_logger = None
        if 'interaction_history' not in st.session_state:
            st.session_state.interaction_history = []
        if 'design_moves' not in st.session_state:
            st.session_state.design_moves = []
        if 'pre_test_complete' not in st.session_state:
            st.session_state.pre_test_complete = False
        if 'test_complete' not in st.session_state:
            st.session_state.test_complete = False
            
    def setup_environments(self):
        """Initialize test environments"""
        self.mentor_env = MentorTestEnvironment()
        self.generic_ai_env = GenericAITestEnvironment()
        self.control_env = ControlTestEnvironment()
        
        self.pre_test = PreTestAssessment()
        self.post_test = PostTestAssessment()
    
    def render_sidebar(self):
        """Render test control sidebar"""
        with st.sidebar:
            st.header("🧪 Cognitive Benchmarking Controls")
            
            # System status
            status_container = st.container()
            with status_container:
                st.subheader("System Status")
                col1, col2 = st.columns(2)
                with col1:
                    if MENTOR_AVAILABLE:
                        st.success("✅ MENTOR Ready")
                    else:
                        st.error("❌ MENTOR Unavailable")
                with col2:
                    if LINKOGRAPHY_AVAILABLE:
                        st.success("✅ Linkography Ready")
                    else:
                        st.warning("⚠️ Linkography Limited")
            
            st.divider()
            
            # Participant setup
            if not st.session_state.participant:
                st.subheader("Participant Setup")
                participant_id = st.text_input("Participant ID", key="participant_id_input")
                
                # Test group selection with descriptions
                st.markdown("### Select Test Condition")
                
                if MENTOR_AVAILABLE:
                    test_groups = [
                        ("MENTOR - Multi-Agent Scaffolding", TestGroup.MENTOR.value),
                        ("Generic AI - Direct Assistance", TestGroup.GENERIC_AI.value),
                        ("Control - No AI Assistance", TestGroup.CONTROL.value)
                    ]
                else:
                    st.warning("MENTOR group requires additional dependencies")
                    test_groups = [
                        ("Generic AI - Direct Assistance", TestGroup.GENERIC_AI.value),
                        ("Control - No AI Assistance", TestGroup.CONTROL.value)
                    ]
                
                test_group = st.radio(
                    "Test Group", 
                    [g[1] for g in test_groups],
                    format_func=lambda x: next(g[0] for g in test_groups if g[1] == x),
                    key="test_group_select"
                )
                
                # Group descriptions
                if test_group == TestGroup.MENTOR.value:
                    st.info("**MENTOR**: Socratic questioning and cognitive scaffolding to prevent offloading")
                elif test_group == TestGroup.GENERIC_AI.value:
                    st.info("**Generic AI**: Direct answers and assistance (ChatGPT-like)")
                else:
                    st.info("**Control**: No AI assistance - baseline comparison")
                
                if st.button("Start Test Session", key="start_session_btn", type="primary"):
                    if participant_id:
                        if test_group == TestGroup.MENTOR.value and not MENTOR_AVAILABLE:
                            st.error("MENTOR group requires multi-agent dependencies. Please install them first.")
                        else:
                            self.start_test_session(participant_id, TestGroup(test_group))
                    else:
                        st.error("Please enter a participant ID")
            
            else:
                # Session info
                st.subheader("Session Info")
                st.write(f"**Participant:** {st.session_state.participant.id}")
                st.write(f"**Group:** {st.session_state.test_group.value}")
                st.write(f"**Phase:** {st.session_state.current_phase.value}")
                st.write(f"**Start Time:** {st.session_state.test_session.start_time.strftime('%H:%M:%S')}")
                
                # Linkography metrics
                if LINKOGRAPHY_AVAILABLE and st.session_state.linkography_logger:
                    st.divider()
                    st.subheader("Linkography Metrics")
                    metrics = st.session_state.linkography_logger.get_linkography_metrics()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Design Moves", metrics.get('total_moves', 0))
                        st.metric("Link Density", f"{metrics.get('link_density', 0):.2f}")
                    with col2:
                        st.metric("Total Links", metrics.get('total_links', 0))
                        st.metric("Move Diversity", f"{metrics.get('move_diversity', 0):.2f}")
                
                # Phase progression
                st.divider()
                st.subheader("Phase Progression")
                
                if st.session_state.current_phase == TestPhase.PRE_TEST:
                    if st.button("Complete Pre-Test", key="complete_pretest_btn"):
                        if st.session_state.pre_test_complete:
                            self.advance_to_main_test()
                        else:
                            st.error("Please complete the pre-test assessment first")
                
                elif st.session_state.current_phase in [TestPhase.IDEATION, TestPhase.VISUALIZATION, TestPhase.MATERIALIZATION]:
                    # Phase timer
                    phase_times = {
                        TestPhase.IDEATION: 15,
                        TestPhase.VISUALIZATION: 20,
                        TestPhase.MATERIALIZATION: 20
                    }
                    st.info(f"Time allocation: {phase_times[st.session_state.current_phase]} minutes")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Next Phase", key="next_phase_btn"):
                            self.advance_phase()
                    with col2:
                        if st.button("End Test", key="end_test_btn"):
                            self.end_test_session()
                
                elif st.session_state.current_phase == TestPhase.POST_TEST:
                    if st.button("Complete Post-Test", key="complete_posttest_btn"):
                        self.complete_test_session()
                
                # Export controls
                st.divider()
                st.subheader("Data Export")
                if st.button("Export Session Data", key="export_data_btn"):
                    self.export_session_data()
                
                # Cognitive metrics display
                if st.session_state.session_logger:
                    st.divider()
                    st.subheader("Cognitive Metrics")
                    summary = st.session_state.session_logger.get_session_summary()
                    if 'cognitive_metrics' in summary:
                        metrics = summary['cognitive_metrics']
                        st.metric("COP Score", f"{metrics.get('cop', 0):.2%}")
                        st.metric("DTE Score", f"{metrics.get('dte', 0):.2%}")
                        st.metric("KI Score", f"{metrics.get('ki', 0):.2%}")
    
    def start_test_session(self, participant_id: str, test_group: TestGroup):
        """Initialize a new test session"""
        # Create participant
        st.session_state.participant = TestParticipant(
            id=participant_id,
            test_group=test_group,
            session_id=str(uuid.uuid4())
        )
        
        # Create test session
        st.session_state.test_session = TestSession(
            id=st.session_state.participant.session_id,
            participant_id=participant_id,
            test_group=test_group,
            start_time=datetime.now()
        )
        
        # Initialize loggers
        st.session_state.session_logger = TestSessionLogger(
            session_id=st.session_state.test_session.id,
            participant_id=participant_id,
            test_group=test_group
        )
        
        if LINKOGRAPHY_AVAILABLE:
            st.session_state.linkography_logger = LinkographyLogger(
                session_id=st.session_state.test_session.id
            )
        
        # Set test group
        st.session_state.test_group = test_group
        
        # Log session start
        st.session_state.session_logger.log_session_start()
        
        st.success(f"Test session started for participant {participant_id} in {test_group.value} group")
        st.rerun()
    
    def render_main_content(self):
        """Render main test content based on current phase"""
        if not st.session_state.participant:
            self.render_welcome_screen()
        elif st.session_state.current_phase == TestPhase.PRE_TEST:
            self.render_pre_test()
        elif st.session_state.current_phase in [TestPhase.IDEATION, TestPhase.VISUALIZATION, TestPhase.MATERIALIZATION]:
            self.render_test_environment()
        elif st.session_state.current_phase == TestPhase.POST_TEST:
            self.render_post_test()
        elif st.session_state.current_phase == TestPhase.COMPLETED:
            self.render_completion_screen()
    
    def render_welcome_screen(self):
        """Render welcome screen before test starts"""
        st.title("🧠 MEGA Architectural Mentor - Cognitive Benchmarking Study")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ## Welcome to the Architectural Design Cognitive Benchmarking Study
            
            This research compares three different approaches to architectural design education:
            
            ### 1. MENTOR Group (Experimental)
            - **Multi-agent AI system** with Socratic questioning
            - **Prevents cognitive offloading** through scaffolding
            - **Builds critical thinking** skills progressively
            
            ### 2. Generic AI Group (Control 1)
            - **Direct AI assistance** like ChatGPT
            - **Provides immediate answers** and solutions
            - **May enable cognitive offloading**
            
            ### 3. No AI Group (Control 2)
            - **Traditional approach** without AI assistance
            - **Baseline comparison** for cognitive development
            - **Natural design thinking** patterns
            
            ### Test Structure:
            1. **Pre-Test Assessment** (10 minutes)
            2. **Design Task** (55 minutes total):
               - Ideation Phase (15 minutes)
               - Visualization Phase (20 minutes)
               - Materialization Phase (20 minutes)
            3. **Post-Test Assessment** (10 minutes)
            
            All interactions will be analyzed using **Linkography** to track your design thinking process in real-time.
            """)
        
        with col2:
            st.info("""
            ### Key Metrics Tracked:
            - **COP**: Cognitive Offloading Prevention
            - **DTE**: Deep Thinking Engagement
            - **SE**: Scaffolding Effectiveness
            - **KI**: Knowledge Integration
            - **LP**: Learning Progression
            - **MA**: Metacognitive Awareness
            """)
            
            st.warning("""
            ### Important:
            - Work at your natural pace
            - Think aloud when possible
            - All data is anonymized
            - You can withdraw at any time
            """)
        
        st.divider()
        st.markdown("**Please use the sidebar to begin when ready →**")
    
    def render_pre_test(self):
        """Render pre-test assessment"""
        st.header("Pre-Test Assessment")
        st.info("This assessment helps us understand your baseline cognitive and spatial reasoning abilities.")
        
        tab1, tab2, tab3 = st.tabs(["Critical Thinking", "Architectural Knowledge", "Spatial Reasoning"])
        
        with tab1:
            st.subheader("Critical Thinking Assessment")
            ct_responses = self.pre_test.render_critical_thinking_questions()
            
        with tab2:
            st.subheader("Architectural Knowledge Baseline")
            ak_responses = self.pre_test.render_architectural_knowledge_questions()
            
        with tab3:
            st.subheader("Spatial Reasoning Test")
            sr_responses = self.pre_test.render_spatial_reasoning_questions()
        
        # Submit button
        if st.button("Submit Pre-Test", key="submit_pretest_btn", type="primary"):
            if self.pre_test.validate_responses():
                # Log assessment results
                assessment_result = AssessmentResult(
                    assessment_type="pre_test",
                    scores={
                        "critical_thinking": self.pre_test.score_critical_thinking(),
                        "architectural_knowledge": self.pre_test.score_architectural_knowledge(),
                        "spatial_reasoning": self.pre_test.score_spatial_reasoning()
                    },
                    timestamp=datetime.now()
                )
                
                st.session_state.session_logger.log_assessment(assessment_result)
                st.session_state.pre_test_complete = True
                st.success("Pre-test completed! Use the sidebar to proceed to the main test.")
            else:
                st.error("Please answer all questions before submitting.")
    
    def render_test_environment(self):
        """Render the appropriate test environment based on group"""
        # Design brief header
        st.header(f"Design Phase: {st.session_state.current_phase.value}")
        
        # Cognitive metrics banner
        if st.session_state.session_logger:
            metrics_container = st.container()
            with metrics_container:
                cols = st.columns(6)
                summary = st.session_state.session_logger.get_session_summary()
                if 'cognitive_metrics' in summary:
                    metrics = summary['cognitive_metrics']
                    with cols[0]:
                        st.metric("COP", f"{metrics.get('cop', 0):.1%}", 
                                help="Cognitive Offloading Prevention")
                    with cols[1]:
                        st.metric("DTE", f"{metrics.get('dte', 0):.1%}",
                                help="Deep Thinking Engagement")
                    with cols[2]:
                        st.metric("SE", f"{metrics.get('se', 0):.1%}",
                                help="Scaffolding Effectiveness")
                    with cols[3]:
                        st.metric("KI", f"{metrics.get('ki', 0):.1%}",
                                help="Knowledge Integration")
                    with cols[4]:
                        st.metric("LP", f"{metrics.get('lp', 0):.1%}",
                                help="Learning Progression")
                    with cols[5]:
                        st.metric("MA", f"{metrics.get('ma', 0):.1%}",
                                help="Metacognitive Awareness")
        
        st.divider()
        
        if st.session_state.current_phase == TestPhase.IDEATION:
            self.render_design_brief()
        
        # Render appropriate environment
        if st.session_state.test_group == TestGroup.MENTOR:
            if MENTOR_AVAILABLE:
                self.mentor_env.render(st.session_state.current_phase)
            else:
                st.error("MENTOR environment requires multi-agent dependencies. Please install them.")
        elif st.session_state.test_group == TestGroup.GENERIC_AI:
            self.generic_ai_env.render(st.session_state.current_phase)
        else:  # CONTROL
            self.control_env.render(st.session_state.current_phase)
    
    def render_design_brief(self):
        """Render the design brief for all groups"""
        with st.expander("📋 Design Brief", expanded=True):
            st.markdown("""
            ## Urban Community Center Design Challenge
            
            You are tasked with designing a community center for a diverse urban neighborhood of 15,000 residents. 
            
            ### Site Information:
            - **Location**: Former industrial warehouse
            - **Dimensions**: 150m x 80m x 12m height
            - **Context**: Mixed-use urban neighborhood
            
            ### Design Requirements:
            - Community gathering spaces
            - Educational facilities
            - Recreation areas
            - Administrative offices
            - Support services
            
            ### Key Considerations:
            - **Community needs**: Diverse age groups and cultural backgrounds
            - **Cultural sensitivity**: Inclusive design for all community members
            - **Sustainability**: Environmental responsibility and energy efficiency
            - **Adaptive reuse**: Preserve and integrate industrial character
            
            ### Time Allocation:
            - **Ideation Phase**: 15 minutes - Develop concept and program
            - **Visualization Phase**: 20 minutes - Create spatial diagrams and sketches
            - **Materialization Phase**: 20 minutes - Technical development and detailing
            """)
    
    def advance_phase(self):
        """Advance to the next test phase"""
        current_phase = st.session_state.current_phase
        
        if current_phase == TestPhase.IDEATION:
            st.session_state.current_phase = TestPhase.VISUALIZATION
        elif current_phase == TestPhase.VISUALIZATION:
            st.session_state.current_phase = TestPhase.MATERIALIZATION
        elif current_phase == TestPhase.MATERIALIZATION:
            st.session_state.current_phase = TestPhase.POST_TEST
        
        # Log phase transition
        st.session_state.session_logger.log_phase_transition(
            from_phase=current_phase,
            to_phase=st.session_state.current_phase
        )
        
        st.rerun()
    
    def advance_to_main_test(self):
        """Advance from pre-test to main test"""
        st.session_state.current_phase = TestPhase.IDEATION
        st.session_state.session_logger.log_phase_transition(
            from_phase=TestPhase.PRE_TEST,
            to_phase=TestPhase.IDEATION
        )
        st.rerun()
    
    def end_test_session(self):
        """End the main test and move to post-test"""
        st.session_state.current_phase = TestPhase.POST_TEST
        st.session_state.session_logger.log_phase_transition(
            from_phase=st.session_state.current_phase,
            to_phase=TestPhase.POST_TEST
        )
        st.rerun()
    
    def render_post_test(self):
        """Render post-test assessment"""
        st.header("Post-Test Assessment")
        st.info("This final assessment helps us understand your learning and cognitive development during the test.")
        
        tab1, tab2 = st.tabs(["Reflection", "Knowledge Transfer"])
        
        with tab1:
            st.subheader("Design Process Reflection")
            reflection_responses = self.post_test.render_reflection_questions()
            
        with tab2:
            st.subheader("Knowledge Transfer Challenge")
            transfer_responses = self.post_test.render_transfer_task()
        
        if st.button("Submit Post-Test", key="submit_posttest_btn", type="primary"):
            if self.post_test.validate_responses():
                # Log assessment results
                assessment_result = AssessmentResult(
                    assessment_type="post_test",
                    scores={
                        "reflection_quality": self.post_test.score_reflection(),
                        "transfer_ability": self.post_test.score_transfer()
                    },
                    timestamp=datetime.now()
                )
                
                st.session_state.session_logger.log_assessment(assessment_result)
                self.complete_test_session()
            else:
                st.error("Please complete all questions before submitting.")
    
    def complete_test_session(self):
        """Complete the test session"""
        st.session_state.current_phase = TestPhase.COMPLETED
        st.session_state.test_complete = True
        
        # Finalize logging
        st.session_state.session_logger.finalize_session()
        if LINKOGRAPHY_AVAILABLE and st.session_state.linkography_logger:
            st.session_state.linkography_logger.finalize()
        
        st.rerun()
    
    def render_completion_screen(self):
        """Render test completion screen"""
        st.title("✅ Test Completed!")
        st.success("Thank you for participating in the architectural design cognitive benchmarking study.")
        
        # Show summary metrics
        if st.session_state.session_logger:
            st.subheader("Session Summary")
            summary = st.session_state.session_logger.get_session_summary()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Duration", f"{summary['duration_minutes']:.1f} minutes")
                st.metric("Design Moves", summary['total_moves'])
            with col2:
                st.metric("Interactions", summary['total_interactions'])
                st.metric("Test Group", st.session_state.test_group.value)
            with col3:
                if 'cognitive_metrics' in summary:
                    st.metric("Cognitive Score", f"{summary['avg_cognitive_score']:.2%}")
                    st.metric("Learning Progression", f"{summary['cognitive_metrics'].get('lp', 0):.2%}")
        
        # Linkography visualization placeholder
        if LINKOGRAPHY_AVAILABLE and st.session_state.linkography_logger:
            st.divider()
            st.subheader("Your Design Process Linkograph")
            st.info("Linkography visualization shows how your design moves connected throughout the session")
            # Placeholder for actual linkograph visualization
            st.markdown("*[Linkograph visualization would appear here]*")
        
        # Export option
        st.divider()
        if st.button("📥 Download Complete Session Data", key="download_final_btn", type="primary"):
            self.export_session_data()
    
    def export_session_data(self):
        """Export all session data"""
        if st.session_state.session_logger:
            # Export main session data
            session_file = st.session_state.session_logger.export_session_data()
            
            # Export linkography data if available
            linkography_file = None
            if LINKOGRAPHY_AVAILABLE and st.session_state.linkography_logger:
                linkography_file = st.session_state.linkography_logger.export_linkography_data()
            
            st.success(f"Data exported successfully!")
            
            # Offer download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                with open(session_file, 'r') as f:
                    st.download_button(
                        label="📊 Download Session Data",
                        data=f.read(),
                        file_name=f"session_{st.session_state.test_session.id}.json",
                        mime="application/json"
                    )
            
            with col2:
                if linkography_file and os.path.exists(linkography_file):
                    with open(linkography_file, 'r') as f:
                        st.download_button(
                            label="🔗 Download Linkography Data",
                            data=f.read(),
                            file_name=f"linkography_{st.session_state.test_session.id}.json",
                            mime="application/json"
                        )
    
    def run(self):
        """Main application loop"""
        self.render_sidebar()
        self.render_main_content()

def main():
    """Main entry point"""
    dashboard = TestDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()