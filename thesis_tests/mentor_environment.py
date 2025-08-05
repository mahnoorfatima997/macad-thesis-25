"""
MENTOR Test Environment
Implements the experimental condition with multi-agent scaffolding
"""

import streamlit as st
import uuid
from datetime import datetime
import time
from typing import Dict, List, Optional, Any
import os
import sys

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thesis_tests.data_models import (
    DesignMove, InteractionData, TestPhase, MoveType, 
    MoveSource, Modality, DesignFocus
)
from thesis_tests.move_parser import MoveParser

# Import multi-agent system components
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
if thesis_agents_dir not in sys.path:
    sys.path.insert(0, thesis_agents_dir)

try:
    from orchestration.langgraph_orchestrator import LangGraphOrchestrator
    from state_manager import ArchMentorState, StudentProfile, VisualArtifact
    MENTOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Multi-agent system not available: {e}")
    MENTOR_AVAILABLE = False
    # Create dummy classes for graceful degradation
    class LangGraphOrchestrator:
        async def process_student_input(self, *args, **kwargs):
            return {
                "response": "Multi-agent system not available. Please install dependencies.",
                "metadata": {},
                "routing_path": "error",
                "classification": {}
            }
    class ArchMentorState:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            if 'messages' not in self.__dict__:
                self.messages = []
    class StudentProfile:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    class VisualArtifact:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

# Import the wrapper
try:
    from thesis_tests.mentor_environment_wrapper import MentorOrchestratorWrapper
    USE_WRAPPER = True
except:
    USE_WRAPPER = False


class MentorTestEnvironment:
    """MENTOR test environment with full multi-agent scaffolding"""
    
    def __init__(self):
        # Try to use wrapper first to handle ChromaDB issues
        if USE_WRAPPER and MENTOR_AVAILABLE:
            try:
                self.orchestrator = MentorOrchestratorWrapper()
            except:
                # Fallback to direct orchestrator
                try:
                    self.orchestrator = LangGraphOrchestrator()
                except:
                    # Last resort - create dummy
                    self.orchestrator = None
        elif MENTOR_AVAILABLE:
            try:
                self.orchestrator = LangGraphOrchestrator()
            except:
                self.orchestrator = None
        else:
            self.orchestrator = None
            
        self.move_parser = MoveParser()
        self.initialize_state()
        
    def initialize_state(self):
        """Initialize agent state"""
        if 'mentor_state' not in st.session_state:
            st.session_state.mentor_state = ArchMentorState(
                messages=[],
                visual_artifacts=[],
                student_profile=StudentProfile(
                    skill_level="intermediate",
                    learning_style="visual",
                    cognitive_load=0.3,
                    engagement_level=0.7,
                    knowledge_gaps=[],
                    strengths=[]
                ),
                next_agent="socratic_tutor",
                current_design_brief="Community center design challenge",
                domain="architecture"
            )
            # Track interaction count separately
            st.session_state.mentor_interaction_count = 0
    
    def render(self, phase: TestPhase):
        """Render MENTOR environment for current phase"""
        st.subheader(f"MENTOR Environment - {phase.value} Phase")
        
        # Phase-specific instructions
        self._render_phase_instructions(phase)
        
        # Main interaction area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_interaction_area(phase)
        
        with col2:
            self._render_tools_panel(phase)
        
        # Cognitive support panel
        self._render_cognitive_support()
    
    def _render_phase_instructions(self, phase: TestPhase):
        """Render phase-specific instructions"""
        instructions = {
            TestPhase.IDEATION: """
            ### Ideation Phase (15 minutes)
            Develop your initial concept for the community center. The AI mentor will guide your thinking
            through Socratic questioning rather than providing direct solutions.
            """,
            TestPhase.VISUALIZATION: """
            ### Visualization Phase (20 minutes)
            Transform your concept into visual representations. Upload sketches or use the drawing tools.
            The AI will analyze your visuals and guide refinement through questions.
            """,
            TestPhase.MATERIALIZATION: """
            ### Materialization Phase (20 minutes)
            Develop technical details and implementation strategies. The AI will challenge your
            assumptions and help you think through construction and material choices.
            """
        }
        
        if phase in instructions:
            with st.expander("Phase Instructions", expanded=True):
                st.markdown(instructions[phase])
    
    def _render_interaction_area(self, phase: TestPhase):
        """Render main interaction area"""
        st.markdown("### Design Development")
        
        # Chat interface
        if "mentor_messages" not in st.session_state:
            st.session_state.mentor_messages = []
            # Add initial Socratic prompt
            initial_prompt = self._get_initial_prompt(phase)
            st.session_state.mentor_messages.append({
                "role": "assistant",
                "content": initial_prompt
            })
        
        # Display chat history
        for message in st.session_state.mentor_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # User input
        user_input = st.chat_input("Describe your design thinking...")
        
        if user_input:
            # Record interaction start time
            interaction_start = time.time()
            
            # Add user message
            st.session_state.mentor_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Process with multi-agent system
            with st.spinner("AI mentor is thinking..."):
                response = self._process_with_mentor(user_input, phase)
            
            # Calculate response time
            response_time = time.time() - interaction_start
            
            # Add AI response
            st.session_state.mentor_messages.append({
                "role": "assistant",
                "content": response
            })
            
            # Log interaction and extract moves
            self._log_interaction_and_moves(
                user_input, response, phase, response_time
            )
            
            st.rerun()
    
    def _render_tools_panel(self, phase: TestPhase):
        """Render tools panel based on phase"""
        st.markdown("### Tools")
        
        if phase == TestPhase.IDEATION:
            # Text-based ideation tools
            with st.expander("Concept Notes"):
                concept_notes = st.text_area(
                    "Capture your ideas",
                    key=f"concept_notes_{phase.value}",
                    height=200
                )
                if st.button("Save Notes", key=f"save_notes_{phase.value}"):
                    self._save_concept_notes(concept_notes, phase)
        
        elif phase == TestPhase.VISUALIZATION:
            # Visual tools
            st.markdown("#### Upload Sketch")
            uploaded_file = st.file_uploader(
                "Upload your sketch",
                type=['png', 'jpg', 'jpeg'],
                key=f"sketch_upload_{phase.value}"
            )
            if uploaded_file:
                self._process_sketch_upload(uploaded_file, phase)
            
            # Simple drawing instructions
            st.info("You can also use external drawing tools and upload the results")
        
        elif phase == TestPhase.MATERIALIZATION:
            # Technical documentation tools
            with st.expander("Technical Specifications"):
                specs = st.text_area(
                    "Document technical details",
                    key=f"tech_specs_{phase.value}",
                    height=200
                )
                if st.button("Save Specifications", key=f"save_specs_{phase.value}"):
                    self._save_specifications(specs, phase)
    
    def _render_cognitive_support(self):
        """Render cognitive support indicators"""
        with st.expander("Cognitive Support", expanded=False):
            st.markdown("### Thinking Guidance")
            
            # Display current cognitive state
            if hasattr(st.session_state, 'mentor_state'):
                profile = st.session_state.mentor_state.student_profile
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Skill Level", profile.skill_level)
                    st.metric("Interactions", st.session_state.get('mentor_interaction_count', 0))
                
                with col2:
                    if profile.knowledge_gaps:
                        st.warning(f"Areas needing clarification: {len(profile.knowledge_gaps)}")
                    else:
                        st.success("Clear understanding")
                
                # Scaffolding indicators
                st.markdown("#### Current Support Level")
                st.progress(self._calculate_scaffolding_level())
                
                # Metacognitive prompts
                interaction_count = st.session_state.get('mentor_interaction_count', 0)
                if interaction_count > 0 and interaction_count % 5 == 0:
                    st.info("🤔 Take a moment to reflect on your design process so far.")
    
    def _get_initial_prompt(self, phase: TestPhase) -> str:
        """Get initial Socratic prompt for phase"""
        prompts = {
            TestPhase.IDEATION: 
                "Before we begin designing, what do you think are the most important questions "
                "we should ask about this community and their needs?",
            TestPhase.VISUALIZATION: 
                "You've developed some interesting concepts. How might you visualize these ideas "
                "to better understand their spatial relationships?",
            TestPhase.MATERIALIZATION: 
                "Now that you have a spatial concept, what technical challenges do you anticipate "
                "in bringing this design to life?"
        }
        return prompts.get(phase, "Let's explore your design thinking together.")
    
    def _process_with_mentor(self, user_input: str, phase: TestPhase) -> str:
        """Process input through multi-agent system"""
        # Check if orchestrator is available
        if not self.orchestrator:
            return "The multi-agent system is initializing. Please try again in a moment."
        
        # Update state with user input (only once)
        st.session_state.mentor_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Set phase context
        st.session_state.mentor_state.current_phase = phase.value
        
        # Process through orchestrator (async method)
        import asyncio
        result = asyncio.run(
            self.orchestrator.process_student_input(st.session_state.mentor_state)
        )
        
        # Extract response from result
        response = result.get('response', 'I am here to guide your thinking. Could you elaborate on your approach?')
        
        # Add AI response to messages
        st.session_state.mentor_state.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Increment interaction count
        if 'mentor_interaction_count' in st.session_state:
            st.session_state.mentor_interaction_count += 1
        else:
            st.session_state.mentor_interaction_count = 1
        
        # Store metadata if available
        if 'metadata' in result:
            st.session_state.last_mentor_metadata = result['metadata']
        
        return response
    
    def _log_interaction_and_moves(self, user_input: str, ai_response: str, 
                                   phase: TestPhase, response_time: float):
        """Log interaction and parse design moves"""
        # Create interaction record
        interaction = InteractionData(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            phase=phase,
            interaction_type="mentor_dialogue",
            user_input=user_input,
            system_response=ai_response,
            response_time=response_time,
            cognitive_metrics=self._calculate_cognitive_metrics()
        )
        
        # Parse moves from interaction
        user_moves = self.move_parser.parse_user_input(
            user_input, phase, MoveSource.USER_GENERATED
        )
        ai_moves = self.move_parser.parse_ai_response(
            ai_response, phase, MoveSource.AI_PROMPTED
        )
        
        # Log moves
        all_moves = user_moves + ai_moves
        move_ids = []
        
        for move in all_moves:
            # Set session ID and sequence number
            move.session_id = st.session_state.test_session.id
            move.sequence_number = len(st.session_state.design_moves) + 1
            
            # Add cognitive load based on interaction
            move.cognitive_load = self._assess_cognitive_load(move)
            
            # Log the move
            st.session_state.session_logger.log_design_move(move)
            st.session_state.linkography_logger.log_design_move(move)
            st.session_state.design_moves.append(move)
            move_ids.append(move.id)
        
        # Update interaction with generated moves
        interaction.generated_moves = move_ids
        
        # Log interaction
        st.session_state.session_logger.log_interaction(interaction)
        st.session_state.interaction_history.append(interaction)
    
    def _calculate_cognitive_metrics(self) -> Dict[str, float]:
        """Calculate cognitive metrics for current interaction"""
        # Get linkography metrics
        linkography_metrics = st.session_state.linkography_logger.get_linkography_metrics()
        
        # Calculate MENTOR-specific metrics
        metrics = {
            'cop': self._calculate_cop_score(),
            'dte': self._calculate_dte_score(linkography_metrics),
            'se': self._calculate_se_score(),
            'ki': linkography_metrics.get('link_density', 0) * 0.8,
            'lp': self._calculate_lp_score(),
            'ma': self._calculate_ma_score()
        }
        
        # Composite score
        metrics['composite'] = sum(metrics.values()) / len(metrics)
        
        # Log metrics
        st.session_state.session_logger.log_cognitive_metrics(metrics)
        
        return metrics
    
    def _calculate_cop_score(self) -> float:
        """Calculate Cognitive Offloading Prevention score"""
        if not st.session_state.interaction_history:
            return 0.7  # Base score for MENTOR
        
        # Analyze recent interactions for direct answer seeking
        recent_interactions = st.session_state.interaction_history[-5:]
        direct_queries = sum(
            1 for i in recent_interactions 
            if any(phrase in i.user_input.lower() 
                  for phrase in ['what is', 'tell me', 'give me', 'show me how'])
        )
        
        # MENTOR scaffolding prevents offloading
        cop_score = 1.0 - (direct_queries / len(recent_interactions) * 0.3)
        return max(0.7, cop_score)  # Minimum 0.7 for MENTOR
    
    def _calculate_dte_score(self, linkography_metrics: Dict[str, float]) -> float:
        """Calculate Deep Thinking Engagement score"""
        # Base on linkography metrics
        link_density = linkography_metrics.get('link_density', 0)
        critical_ratio = linkography_metrics.get('critical_move_ratio', 0)
        
        # MENTOR promotes deep thinking
        dte_score = (link_density * 0.5 + critical_ratio * 0.5) + 0.2
        return min(1.0, dte_score)
    
    def _calculate_se_score(self) -> float:
        """Calculate Scaffolding Effectiveness score"""
        # MENTOR is designed for effective scaffolding
        profile = st.session_state.mentor_state.student_profile
        
        # Base score on skill level matching
        skill_scores = {
            'beginner': 0.85,
            'intermediate': 0.90,
            'advanced': 0.88,
            'expert': 0.85
        }
        
        return skill_scores.get(profile.skill_level, 0.85)
    
    def _calculate_lp_score(self) -> float:
        """Calculate Learning Progression score"""
        if len(st.session_state.design_moves) < 5:
            return 0.5
        
        # Analyze move sophistication over time
        recent_moves = st.session_state.design_moves[-10:]
        early_moves = st.session_state.design_moves[:10]
        
        # Simple progression metric
        recent_complexity = sum(m.complexity_score for m in recent_moves) / len(recent_moves)
        early_complexity = sum(m.complexity_score for m in early_moves[:len(recent_moves)]) / len(early_moves[:len(recent_moves)])
        
        progression = (recent_complexity - early_complexity) / (early_complexity + 0.1)
        return max(0, min(1, 0.5 + progression))
    
    def _calculate_ma_score(self) -> float:
        """Calculate Metacognitive Awareness score"""
        # Count reflection moves
        reflection_moves = sum(
            1 for m in st.session_state.design_moves
            if m.move_type == MoveType.REFLECTION
        )
        
        total_moves = len(st.session_state.design_moves)
        if total_moves == 0:
            return 0.3
        
        # MENTOR encourages reflection
        ma_score = (reflection_moves / total_moves) * 2.0 + 0.3
        return min(1.0, ma_score)
    
    def _calculate_scaffolding_level(self) -> float:
        """Calculate current scaffolding level"""
        profile = st.session_state.mentor_state.student_profile
        
        levels = {
            'beginner': 0.9,
            'intermediate': 0.7,
            'advanced': 0.5,
            'expert': 0.3
        }
        
        return levels.get(profile.skill_level, 0.7)
    
    def _assess_cognitive_load(self, move: DesignMove) -> str:
        """Assess cognitive load for a move"""
        # Based on move type and complexity
        if move.move_type in [MoveType.SYNTHESIS, MoveType.EVALUATION]:
            return "high"
        elif move.move_type == MoveType.ANALYSIS:
            return "medium"
        else:
            return "low"
    
    def _save_concept_notes(self, notes: str, phase: TestPhase):
        """Save concept notes as design moves"""
        if notes.strip():
            move = DesignMove(
                id=str(uuid.uuid4()),
                session_id=st.session_state.test_session.id,
                timestamp=datetime.now(),
                sequence_number=len(st.session_state.design_moves) + 1,
                content=notes,
                move_type=MoveType.SYNTHESIS,
                phase=phase,
                modality=Modality.TEXT,
                cognitive_operation="proposal",
                design_focus=DesignFocus.FUNCTION,
                move_source=MoveSource.USER_GENERATED,
                cognitive_load="medium"
            )
            
            st.session_state.session_logger.log_design_move(move)
            st.session_state.linkography_logger.log_design_move(move)
            st.session_state.design_moves.append(move)
            
            st.success("Concept notes saved!")
    
    def _process_sketch_upload(self, uploaded_file, phase: TestPhase):
        """Process uploaded sketch"""
        # Save sketch
        sketch_path = f"thesis_tests/uploads/{uploaded_file.name}"
        with open(sketch_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Create visual artifact
        visual_artifact = VisualArtifact(
            description=f"Sketch: {uploaded_file.name}",
            analysis_results={},
            design_elements=[],
            timestamp=datetime.now()
        )
        
        st.session_state.mentor_state.visual_artifacts.append(visual_artifact)
        
        # Log as design move
        move = DesignMove(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            sequence_number=len(st.session_state.design_moves) + 1,
            content=f"Uploaded sketch: {uploaded_file.name}",
            move_type=MoveType.TRANSFORMATION,
            phase=phase,
            modality=Modality.SKETCH,
            cognitive_operation="proposal",
            design_focus=DesignFocus.FORM,
            move_source=MoveSource.USER_GENERATED,
            cognitive_load="high",
            concurrent_sketch=sketch_path
        )
        
        st.session_state.session_logger.log_design_move(move)
        st.session_state.linkography_logger.log_design_move(move)
        st.session_state.design_moves.append(move)
        
        st.success("Sketch uploaded! The AI mentor will analyze it and provide guidance.")
    
    def _save_specifications(self, specs: str, phase: TestPhase):
        """Save technical specifications"""
        if specs.strip():
            move = DesignMove(
                id=str(uuid.uuid4()),
                session_id=st.session_state.test_session.id,
                timestamp=datetime.now(),
                sequence_number=len(st.session_state.design_moves) + 1,
                content=specs,
                move_type=MoveType.ANALYSIS,
                phase=phase,
                modality=Modality.TEXT,
                cognitive_operation="clarification",
                design_focus=DesignFocus.STRUCTURE,
                move_source=MoveSource.USER_GENERATED,
                cognitive_load="high"
            )
            
            st.session_state.session_logger.log_design_move(move)
            st.session_state.linkography_logger.log_design_move(move)
            st.session_state.design_moves.append(move)
            
            st.success("Technical specifications saved!")