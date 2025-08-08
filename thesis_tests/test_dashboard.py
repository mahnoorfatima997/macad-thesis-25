"""
MEGA Architectural Mentor - Test Dashboard
Comprehensive testing environment for three test conditions:
1. MENTOR (Experimental) - With multi-agent scaffolding
2. GENERIC AI (Control) - Direct AI assistance
3. NO AI (Baseline Control) - No assistance
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

# Also add thesis-agents directory
thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
if os.path.exists(thesis_agents_dir):
    sys.path.append(thesis_agents_dir)

from thesis_tests.data_models import (
    TestSession, TestParticipant, DesignMove, TestPhase,
    InteractionData, AssessmentResult, TestGroup
)
from thesis_tests.logging_system import TestSessionLogger
from thesis_tests.mentor_environment import MentorTestEnvironment
from thesis_tests.generic_ai_environment import GenericAITestEnvironment
from thesis_tests.control_environment import ControlTestEnvironment
from thesis_tests.assessment_tools import PreTestAssessment, PostTestAssessment
from thesis_tests.linkography_logger import LinkographyLogger

# Page configuration
st.set_page_config(
    page_title="MEGA Test Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TestDashboard:
    """Main test dashboard orchestrating all three test environments"""
    
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
        if 'bypass_pre_test' not in st.session_state:
            st.session_state.bypass_pre_test = False
            
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
            st.header("Test Controls")
            
            # Participant setup
            if not st.session_state.participant:
                st.subheader("Participant Setup")
                participant_id = st.text_input("Participant ID", key="participant_id_input")
                test_group = st.selectbox(
                    "Test Group", 
                    [TestGroup.MENTOR.value, TestGroup.GENERIC_AI.value, TestGroup.CONTROL.value],
                    key="test_group_select"
                )
                
                # Pre-test bypass toggle
                st.divider()
                st.subheader("Test Configuration")
                bypass_pre_test = st.checkbox(
                    "Skip Pre-Test Assessment", 
                    value=False,
                    key="bypass_pre_test_checkbox",
                    help="Check this to skip the pre-test assessment and go directly to the main design test"
                )
                
                if st.button("Start Test Session", key="start_session_btn"):
                    if participant_id:
                        # Store bypass preference
                        st.session_state.bypass_pre_test = bypass_pre_test
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
                
                # Phase progression
                st.divider()
                st.subheader("Phase Progression")
                
                if st.session_state.current_phase == TestPhase.PRE_TEST:
                    if st.session_state.bypass_pre_test:
                        st.info("Pre-test assessment was skipped")
                        if st.button("Start Main Test", key="start_main_test_btn"):
                            self.advance_to_main_test()
                    else:
                        if st.button("Complete Pre-Test", key="complete_pretest_btn"):
                            if st.session_state.pre_test_complete:
                                self.advance_to_main_test()
                            else:
                                st.error("Please complete the pre-test assessment first")
                
                elif st.session_state.current_phase in [TestPhase.IDEATION, TestPhase.VISUALIZATION, TestPhase.MATERIALIZATION]:
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
                
                # Metrics display
                if st.session_state.session_logger:
                    st.divider()
                    st.subheader("Real-time Metrics")
                    metrics = st.session_state.session_logger.get_current_metrics()
                    for metric, value in metrics.items():
                        # Handle different value types safely
                        if isinstance(value, (int, float)):
                            display_value = f"{value:.2%}" if value <= 1.0 else f"{value:.2f}"
                        else:
                            display_value = str(value)
                        st.metric(metric, display_value)
                
                # Export controls
                st.divider()
                st.subheader("Data Export")
                if st.button("Export Session Data", key="export_data_btn"):
                    self.export_session_data()
    
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
        
        st.session_state.linkography_logger = LinkographyLogger(
            session_id=st.session_state.test_session.id
        )
        
        # Set test group
        st.session_state.test_group = test_group
        
        # Check if pre-test should be bypassed
        if st.session_state.bypass_pre_test:
            st.session_state.current_phase = TestPhase.IDEATION
            st.session_state.pre_test_complete = True
            st.info("Pre-test assessment skipped - proceeding directly to main test")
        else:
            st.session_state.current_phase = TestPhase.PRE_TEST
            st.session_state.pre_test_complete = False
        
        # Log session start
        st.session_state.session_logger.log_session_start()
        
        st.success(f"Test session started for participant {participant_id}")
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
        st.title("MEGA Architectural Mentor - Test Dashboard")
        st.markdown("""
        ## Welcome to the Architectural Design Test
        
        This test evaluates different approaches to architectural design assistance:
        - **MENTOR Group**: Scaffolded learning with Socratic guidance
        - **Generic AI Group**: Direct AI assistance (ChatGPT-like)
        - **Control Group**: No AI assistance
        
        ### Test Structure:
        1. **Pre-Test Assessment** (10 minutes) - *Optional*
        2. **Design Phases** (45 minutes total):
           - Ideation (15 minutes)
           - Visualization (20 minutes)
           - Materialization (20 minutes)
        3. **Post-Test Assessment** (10 minutes)
        
        **Note**: You can choose to skip the pre-test assessment if you prefer to go directly to the main design test.
        
        Please use the sidebar to configure your test session and begin when ready.
        """)
    
    def render_pre_test(self):
        """Render pre-test assessment"""
        st.header("Pre-Test Assessment")
        
        # Check if pre-test was bypassed
        if st.session_state.bypass_pre_test:
            st.info("Pre-test assessment was skipped for this session.")
            st.markdown("""
            ### Skipped Assessment Components:
            - **Critical Thinking Assessment**
            - **Architectural Knowledge Baseline** 
            - **Spatial Reasoning Test**
            
            You can proceed directly to the main design test using the sidebar controls.
            """)
            return
        
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
        if st.button("Submit Pre-Test", key="submit_pretest_btn"):
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
        # Design brief for all groups
        st.header(f"Design Phase: {st.session_state.current_phase.value}")
        
        if st.session_state.current_phase == TestPhase.IDEATION:
            self.render_design_brief()
        
        # Render appropriate environment
        if st.session_state.test_group == TestGroup.MENTOR:
            self.mentor_env.render(st.session_state.current_phase)
        elif st.session_state.test_group == TestGroup.GENERIC_AI:
            self.generic_ai_env.render(st.session_state.current_phase)
        else:  # CONTROL
            self.control_env.render(st.session_state.current_phase)
    
    def render_design_brief(self):
        """Render the design brief for all groups"""
        with st.expander("Design Brief", expanded=True):
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
        
        tab1, tab2 = st.tabs(["Reflection", "Knowledge Transfer"])
        
        with tab1:
            st.subheader("Design Process Reflection")
            reflection_responses = self.post_test.render_reflection_questions()
            
        with tab2:
            st.subheader("Knowledge Transfer Challenge")
            transfer_responses = self.post_test.render_transfer_task()
        
        if st.button("Submit Post-Test", key="submit_posttest_btn"):
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
        st.session_state.linkography_logger.finalize()
        
        st.rerun()
    
    def render_completion_screen(self):
        """Render test completion screen"""
        st.title("Test Completed!")
        st.success("Thank you for participating in the architectural design test.")
        
        # Show summary metrics
        if st.session_state.session_logger:
            st.subheader("Session Summary")
            summary = st.session_state.session_logger.get_session_summary()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Duration", f"{summary['duration_minutes']:.1f} minutes")
                st.metric("Design Moves", summary['total_moves'])
            with col2:
                st.metric("Interactions", summary['total_interactions'])
                st.metric("Cognitive Score", f"{summary['avg_cognitive_score']:.2%}")
        
        # Export option
        if st.button("Download Session Data", key="download_final_btn"):
            self.export_session_data()
    
    def export_session_data(self):
        """Export all session data"""
        if st.session_state.session_logger:
            # Export main session data
            session_file = st.session_state.session_logger.export_session_data()
            
            # Export linkography data
            linkography_file = st.session_state.linkography_logger.export_linkography_data()
            
            st.success(f"Data exported to:\n- {session_file}\n- {linkography_file}")
            
            # Offer download buttons
            col1, col2 = st.columns(2)
            with col1:
                with open(session_file, 'r') as f:
                    st.download_button(
                        label="Download Session Data",
                        data=f.read(),
                        file_name=f"session_{st.session_state.test_session.id}.json",
                        mime="application/json"
                    )
            
            with col2:
                with open(linkography_file, 'r') as f:
                    st.download_button(
                        label="Download Linkography Data",
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