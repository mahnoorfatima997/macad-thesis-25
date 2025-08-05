"""
Control Group Test Environment
Implements the baseline condition with no AI assistance
"""

import streamlit as st
import uuid
from datetime import datetime
import time
from typing import Dict, List, Optional, Any

from thesis_tests.data_models import (
    DesignMove, InteractionData, TestPhase, MoveType, 
    MoveSource, Modality, DesignFocus
)
from thesis_tests.move_parser import MoveParser


class ControlTestEnvironment:
    """Control test environment with no AI assistance"""
    
    def __init__(self):
        self.move_parser = MoveParser()
        
    def render(self, phase: TestPhase):
        """Render Control environment for current phase"""
        st.subheader(f"Design Workspace - {phase.value} Phase")
        
        # Phase-specific instructions
        self._render_phase_instructions(phase)
        
        # Main workspace
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_workspace(phase)
        
        with col2:
            self._render_resources_panel(phase)
        
        # Progress tracking
        self._render_progress_panel()
    
    def _render_phase_instructions(self, phase: TestPhase):
        """Render phase-specific instructions"""
        instructions = {
            TestPhase.IDEATION: """
            ### Ideation Phase (15 minutes)
            Develop your initial concept for the community center. Use the workspace below
            to document your ideas and design thinking process.
            """,
            TestPhase.VISUALIZATION: """
            ### Visualization Phase (20 minutes)
            Transform your concept into visual representations. Use sketching tools or
            upload drawings to document your spatial ideas.
            """,
            TestPhase.MATERIALIZATION: """
            ### Materialization Phase (20 minutes)
            Develop technical details and implementation strategies. Document your
            material choices, structural systems, and construction approach.
            """
        }
        
        if phase in instructions:
            with st.expander("Phase Instructions", expanded=True):
                st.markdown(instructions[phase])
    
    def _render_workspace(self, phase: TestPhase):
        """Render main workspace for independent work"""
        st.markdown("### Design Development")
        
        # Text workspace
        st.markdown("#### Document Your Design Process")
        
        # Get previous content if exists
        workspace_key = f"control_workspace_{phase.value}"
        if workspace_key not in st.session_state:
            st.session_state[workspace_key] = ""
        
        # Large text area for design documentation
        design_text = st.text_area(
            "Write about your design decisions, ideas, and reasoning:",
            value=st.session_state[workspace_key],
            height=300,
            key=f"workspace_input_{phase.value}",
            placeholder="Describe your design thinking here..."
        )
        
        # Save button
        if st.button("Save Progress", key=f"save_progress_{phase.value}"):
            if design_text != st.session_state[workspace_key]:
                # Save new content
                st.session_state[workspace_key] = design_text
                # Log as design moves
                self._log_design_documentation(design_text, phase)
                st.success("Progress saved!")
        
        # Phase-specific tools
        if phase == TestPhase.VISUALIZATION:
            st.divider()
            st.markdown("#### Visual Documentation")
            
            # File upload for sketches
            uploaded_file = st.file_uploader(
                "Upload your sketches or drawings",
                type=['png', 'jpg', 'jpeg', 'pdf'],
                key=f"control_upload_{phase.value}"
            )
            
            if uploaded_file:
                self._process_sketch_upload(uploaded_file, phase)
            
            # Note about external tools
            st.info("You may use any external drawing tools and upload your work here.")
        
        elif phase == TestPhase.MATERIALIZATION:
            st.divider()
            st.markdown("#### Technical Documentation")
            
            # Structured input for technical details
            with st.expander("Material Specifications"):
                materials = st.text_area(
                    "List and describe your material choices:",
                    key=f"materials_{phase.value}",
                    height=150
                )
                if st.button("Save Materials", key=f"save_materials_{phase.value}"):
                    if materials.strip():
                        self._log_technical_specs(materials, "materials", phase)
                        st.success("Materials saved!")
            
            with st.expander("Structural Systems"):
                structure = st.text_area(
                    "Describe your structural approach:",
                    key=f"structure_{phase.value}",
                    height=150
                )
                if st.button("Save Structure", key=f"save_structure_{phase.value}"):
                    if structure.strip():
                        self._log_technical_specs(structure, "structure", phase)
                        st.success("Structure details saved!")
    
    def _render_resources_panel(self, phase: TestPhase):
        """Render static resources panel"""
        st.markdown("### Resources")
        
        # Reference materials (static, no AI)
        with st.expander("Design References"):
            st.markdown("""
            #### General Guidelines
            
            **Community Center Design Principles:**
            - Accessibility for all users
            - Flexible spaces for multiple uses
            - Natural lighting and ventilation
            - Connection to outdoor spaces
            - Clear circulation patterns
            
            **Adaptive Reuse Considerations:**
            - Preserve character-defining features
            - Structural assessment requirements
            - Code compliance for change of use
            - Environmental upgrade opportunities
            """)
        
        # Phase-specific references
        phase_references = {
            TestPhase.IDEATION: """
            #### Ideation Resources
            
            **Program Development:**
            - Survey community needs
            - Consider diverse user groups
            - Balance public and private spaces
            - Plan for future flexibility
            
            **Site Analysis:**
            - Document existing conditions
            - Identify opportunities and constraints
            - Consider context and surroundings
            """,
            TestPhase.VISUALIZATION: """
            #### Visualization Resources
            
            **Drawing Techniques:**
            - Plans, sections, elevations
            - Axonometric views
            - Perspective sketches
            - Diagram types
            
            **Spatial Representation:**
            - Scale and proportion
            - Circulation diagrams
            - Zoning diagrams
            """,
            TestPhase.MATERIALIZATION: """
            #### Technical Resources
            
            **Material Options:**
            - Steel frame systems
            - Concrete structures
            - Timber construction
            - Composite systems
            
            **Building Systems:**
            - HVAC considerations
            - Natural ventilation
            - Daylighting strategies
            - Structural grid planning
            """
        }
        
        if phase in phase_references:
            with st.expander(f"{phase.value} References"):
                st.markdown(phase_references[phase])
        
        # Note taking area
        st.divider()
        st.markdown("#### Quick Notes")
        notes = st.text_area(
            "Jot down quick thoughts:",
            key=f"control_notes_{phase.value}",
            height=100
        )
    
    def _render_progress_panel(self):
        """Render progress tracking panel"""
        with st.expander("Your Progress", expanded=False):
            st.markdown("### Design Development Tracking")
            
            # Show move count by phase
            moves_by_phase = {}
            for move in st.session_state.design_moves:
                phase = move.phase.value
                moves_by_phase[phase] = moves_by_phase.get(phase, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ideation Moves", moves_by_phase.get("IDEATION", 0))
            with col2:
                st.metric("Visualization Moves", moves_by_phase.get("VISUALIZATION", 0))
            with col3:
                st.metric("Materialization Moves", moves_by_phase.get("MATERIALIZATION", 0))
            
            # Show activity timeline
            if st.session_state.design_moves:
                st.markdown("#### Recent Activity")
                recent_moves = st.session_state.design_moves[-5:]
                for move in reversed(recent_moves):
                    time_str = move.timestamp.strftime("%H:%M:%S")
                    st.text(f"{time_str} - {move.move_type.value}: {move.content[:50]}...")
    
    def _log_design_documentation(self, text: str, phase: TestPhase):
        """Log design documentation as moves"""
        if not text.strip():
            return
        
        # Parse text into moves
        moves = self.move_parser.parse_user_input(
            text, phase, MoveSource.SELF_GENERATED
        )
        
        # If no moves parsed, create one from entire text
        if not moves:
            moves = [self._create_documentation_move(text, phase)]
        
        # Log each move
        for move in moves:
            # Set session ID and sequence number
            move.session_id = st.session_state.test_session.id
            move.sequence_number = len(st.session_state.design_moves) + 1
            
            # Control group has high self-generation strength
            move.self_generation_strength = 1.0
            move.ai_influence_strength = 0.0
            
            # Assess cognitive load
            move.cognitive_load = self._assess_cognitive_load(move)
            
            # Log the move
            st.session_state.session_logger.log_design_move(move)
            if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
                st.session_state.linkography_logger.log_design_move(move)
            st.session_state.design_moves.append(move)
        
        # Log as interaction (self-directed)
        interaction = InteractionData(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            phase=phase,
            interaction_type="self_documentation",
            user_input=text,
            system_response="[Self-directed work - no AI response]",
            response_time=0.0,
            cognitive_metrics=self._calculate_cognitive_metrics(),
            generated_moves=[m.id for m in moves]
        )
        
        st.session_state.session_logger.log_interaction(interaction)
        st.session_state.interaction_history.append(interaction)
    
    def _create_documentation_move(self, text: str, phase: TestPhase) -> DesignMove:
        """Create a design move from documentation text"""
        # Determine move type based on content
        move_type = MoveType.SYNTHESIS  # Default for documentation
        
        # Simple heuristics for move type
        if any(word in text.lower() for word in ['analyze', 'consider', 'examine']):
            move_type = MoveType.ANALYSIS
        elif any(word in text.lower() for word in ['evaluate', 'compare', 'assess']):
            move_type = MoveType.EVALUATION
        elif any(word in text.lower() for word in ['change', 'modify', 'transform']):
            move_type = MoveType.TRANSFORMATION
        elif any(word in text.lower() for word in ['think', 'reflect', 'realize']):
            move_type = MoveType.REFLECTION
        
        return DesignMove(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            sequence_number=0,  # Will be set by logger
            content=text[:500],  # Limit length
            move_type=move_type,
            phase=phase,
            modality=Modality.TEXT,
            cognitive_operation="proposal",
            design_focus=self._determine_design_focus(text),
            move_source=MoveSource.SELF_GENERATED,
            cognitive_load="medium",
            self_generation_strength=1.0,
            ai_influence_strength=0.0
        )
    
    def _determine_design_focus(self, text: str) -> DesignFocus:
        """Determine design focus from text"""
        text_lower = text.lower()
        
        # Check for keywords
        if any(word in text_lower for word in ['function', 'use', 'activity', 'program']):
            return DesignFocus.FUNCTION
        elif any(word in text_lower for word in ['form', 'shape', 'geometry', 'aesthetic']):
            return DesignFocus.FORM
        elif any(word in text_lower for word in ['structure', 'construction', 'technical']):
            return DesignFocus.STRUCTURE
        elif any(word in text_lower for word in ['material', 'texture', 'surface']):
            return DesignFocus.MATERIAL
        elif any(word in text_lower for word in ['environment', 'sustainability', 'climate']):
            return DesignFocus.ENVIRONMENT
        elif any(word in text_lower for word in ['community', 'culture', 'social']):
            return DesignFocus.CULTURE
        
        return DesignFocus.FUNCTION  # Default
    
    def _process_sketch_upload(self, uploaded_file, phase: TestPhase):
        """Process uploaded sketch"""
        # Save file
        file_path = f"thesis_tests/uploads/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Create move for sketch
        move = DesignMove(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            sequence_number=len(st.session_state.design_moves) + 1,
            content=f"Sketch: {uploaded_file.name}",
            move_type=MoveType.SYNTHESIS,
            phase=phase,
            modality=Modality.SKETCH,
            cognitive_operation="proposal",
            design_focus=DesignFocus.FORM,
            move_source=MoveSource.SELF_GENERATED,
            cognitive_load="high",
            self_generation_strength=1.0,
            ai_influence_strength=0.0,
            concurrent_sketch=file_path
        )
        
        st.session_state.session_logger.log_design_move(move)
        if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
            st.session_state.linkography_logger.log_design_move(move)
        st.session_state.design_moves.append(move)
        
        st.success("Sketch uploaded and logged!")
    
    def _log_technical_specs(self, specs: str, spec_type: str, phase: TestPhase):
        """Log technical specifications"""
        # Determine design focus based on spec type
        focus_map = {
            "materials": DesignFocus.MATERIAL,
            "structure": DesignFocus.STRUCTURE
        }
        
        move = DesignMove(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            sequence_number=len(st.session_state.design_moves) + 1,
            content=f"{spec_type.title()}: {specs}",
            move_type=MoveType.ANALYSIS,
            phase=phase,
            modality=Modality.TEXT,
            cognitive_operation="clarification",
            design_focus=focus_map.get(spec_type, DesignFocus.STRUCTURE),
            move_source=MoveSource.SELF_GENERATED,
            cognitive_load="high",
            self_generation_strength=1.0,
            ai_influence_strength=0.0
        )
        
        st.session_state.session_logger.log_design_move(move)
        if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
            st.session_state.linkography_logger.log_design_move(move)
        st.session_state.design_moves.append(move)
    
    def _calculate_cognitive_metrics(self) -> Dict[str, float]:
        """Calculate cognitive metrics for control group"""
        # Get linkography metrics
        linkography_metrics = {}
        if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
            linkography_metrics = st.session_state.linkography_logger.get_linkography_metrics()
        
        # Calculate control group metrics (baseline)
        metrics = {
            'cop': self._calculate_cop_score(),  # Natural resistance
            'dte': self._calculate_dte_score(linkography_metrics),  # Natural depth
            'se': self._calculate_se_score(),  # Self-scaffolding
            'ki': linkography_metrics.get('link_density', 0) * 0.7,  # Natural integration
            'lp': self._calculate_lp_score(),  # Autonomous progression
            'ma': self._calculate_ma_score()  # Natural metacognition
        }
        
        # Composite score
        metrics['composite'] = sum(metrics.values()) / len(metrics)
        
        # Log metrics
        st.session_state.session_logger.log_cognitive_metrics(metrics)
        
        return metrics
    
    def _calculate_cop_score(self) -> float:
        """Calculate Cognitive Offloading Prevention score"""
        # Control group has perfect COP (no external assistance available)
        return 1.0
    
    def _calculate_dte_score(self, linkography_metrics: Dict[str, float]) -> float:
        """Calculate Deep Thinking Engagement score"""
        # Base on natural linkography patterns
        link_density = linkography_metrics.get('link_density', 0)
        critical_ratio = linkography_metrics.get('critical_move_ratio', 0)
        
        # Natural deep thinking without AI influence
        dte_score = link_density * 0.5 + critical_ratio * 0.5
        return dte_score
    
    def _calculate_se_score(self) -> float:
        """Calculate Scaffolding Effectiveness score"""
        # Self-scaffolding ability
        # Check for self-directed structure in moves
        if len(st.session_state.design_moves) < 5:
            return 0.3
        
        # Look for patterns of self-organization
        move_types = [m.move_type for m in st.session_state.design_moves[-10:]]
        
        # Variety in move types indicates self-scaffolding
        unique_types = len(set(move_types))
        se_score = unique_types / 5  # Max 5 move types
        
        return min(0.6, se_score)  # Cap at 0.6 for control group
    
    def _calculate_lp_score(self) -> float:
        """Calculate Learning Progression score"""
        if len(st.session_state.design_moves) < 5:
            return 0.4
        
        # Natural progression without assistance
        # Check move complexity over time
        recent_moves = st.session_state.design_moves[-10:]
        early_moves = st.session_state.design_moves[:10]
        
        # Simple progression metric based on move diversity
        recent_diversity = len(set(m.design_focus for m in recent_moves))
        early_diversity = len(set(m.design_focus for m in early_moves[:len(recent_moves)]))
        
        if early_diversity > 0:
            progression = recent_diversity / early_diversity
            lp_score = min(1.0, 0.4 + (progression - 1) * 0.3)
        else:
            lp_score = 0.4
        
        return lp_score
    
    def _calculate_ma_score(self) -> float:
        """Calculate Metacognitive Awareness score"""
        # Count reflection moves
        reflection_moves = sum(
            1 for m in st.session_state.design_moves
            if m.move_type == MoveType.REFLECTION
        )
        
        total_moves = len(st.session_state.design_moves)
        if total_moves == 0:
            return 0.2
        
        # Natural metacognition without prompting
        ma_score = (reflection_moves / total_moves) * 2.0
        return min(0.6, ma_score)  # Cap at 0.6 for control
    
    def _assess_cognitive_load(self, move: DesignMove) -> str:
        """Assess cognitive load for a move"""
        # Control group bears full cognitive load
        if move.move_type in [MoveType.SYNTHESIS, MoveType.EVALUATION]:
            return "high"
        elif move.move_type in [MoveType.ANALYSIS, MoveType.TRANSFORMATION]:
            return "medium"
        else:
            return "medium"  # Even simple moves require more effort without assistance