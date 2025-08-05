"""
Generic AI Test Environment
Implements the control condition with direct AI assistance (ChatGPT-like)
"""

import streamlit as st
import uuid
from datetime import datetime
import time
from typing import Dict, List, Optional, Any
import openai
import os

from thesis_tests.data_models import (
    DesignMove, InteractionData, TestPhase, MoveType, 
    MoveSource, Modality, DesignFocus
)
from thesis_tests.move_parser import MoveParser


class GenericAITestEnvironment:
    """Generic AI test environment with direct assistance"""
    
    def __init__(self):
        self.move_parser = MoveParser()
        self.initialize_openai()
        
    def initialize_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
            print("Warning: OPENAI_API_KEY not found. Generic AI will use fallback responses.")
        
    def render(self, phase: TestPhase):
        """Render Generic AI environment for current phase"""
        st.subheader(f"AI Assistant - {phase.value} Phase")
        
        # Show warning if no API key
        if not self.client:
            st.warning("No OpenAI API key found. Using pre-programmed responses for testing.")
        
        # Phase-specific instructions
        self._render_phase_instructions(phase)
        
        # Main interaction area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_chat_interface(phase)
        
        with col2:
            self._render_tools_panel(phase)
        
        # AI assistance panel
        self._render_ai_assistance_panel()
    
    def _render_phase_instructions(self, phase: TestPhase):
        """Render phase-specific instructions"""
        instructions = {
            TestPhase.IDEATION: """
            ### Ideation Phase (15 minutes)
            Develop your initial concept for the community center. The AI assistant will help
            answer your questions and provide design suggestions.
            """,
            TestPhase.VISUALIZATION: """
            ### Visualization Phase (20 minutes)
            Transform your concept into visual representations. The AI can help with spatial
            planning suggestions and visualization techniques.
            """,
            TestPhase.MATERIALIZATION: """
            ### Materialization Phase (20 minutes)
            Develop technical details and implementation strategies. The AI can provide
            technical specifications and material recommendations.
            """
        }
        
        if phase in instructions:
            with st.expander("Phase Instructions", expanded=True):
                st.markdown(instructions[phase])
    
    def _render_chat_interface(self, phase: TestPhase):
        """Render chat interface with direct AI assistance"""
        st.markdown("### Design Assistant")
        
        # Initialize chat history
        if "generic_ai_messages" not in st.session_state:
            st.session_state.generic_ai_messages = []
            # Add welcome message
            st.session_state.generic_ai_messages.append({
                "role": "assistant",
                "content": self._get_welcome_message(phase)
            })
        
        # Display chat history
        for message in st.session_state.generic_ai_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # User input
        user_input = st.chat_input("Ask me anything about your design...")
        
        if user_input:
            # Record interaction start time
            interaction_start = time.time()
            
            # Add user message
            st.session_state.generic_ai_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI response
            with st.spinner("AI is thinking..."):
                response = self._get_generic_ai_response(user_input, phase)
            
            # Calculate response time
            response_time = time.time() - interaction_start
            
            # Add AI response
            st.session_state.generic_ai_messages.append({
                "role": "assistant",
                "content": response
            })
            
            # Log interaction and extract moves
            self._log_interaction_and_moves(
                user_input, response, phase, response_time
            )
            
            st.rerun()
    
    def _render_tools_panel(self, phase: TestPhase):
        """Render tools panel"""
        st.markdown("### Tools & Resources")
        
        # Quick prompts for common questions
        st.markdown("#### Quick Questions")
        
        quick_prompts = {
            TestPhase.IDEATION: [
                "What are the key considerations for community center design?",
                "Show me examples of successful community centers",
                "How should I organize the spatial program?"
            ],
            TestPhase.VISUALIZATION: [
                "What's the best way to visualize circulation patterns?",
                "How should I arrange spaces for optimal flow?",
                "What drawing techniques should I use?"
            ],
            TestPhase.MATERIALIZATION: [
                "What materials are best for adaptive reuse?",
                "How do I detail the structural connections?",
                "What are sustainable building strategies?"
            ]
        }
        
        if phase in quick_prompts:
            for prompt in quick_prompts[phase]:
                if st.button(prompt, key=f"quick_{prompt}"):
                    # Simulate user asking this question
                    st.session_state.generic_ai_messages.append({
                        "role": "user",
                        "content": prompt
                    })
                    response = self._get_generic_ai_response(prompt, phase)
                    st.session_state.generic_ai_messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    self._log_interaction_and_moves(prompt, response, phase, 0.5)
                    st.rerun()
        
        # File upload
        st.divider()
        st.markdown("#### Upload Files")
        uploaded_file = st.file_uploader(
            "Upload sketches or documents",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            key=f"upload_{phase.value}"
        )
        if uploaded_file:
            self._process_file_upload(uploaded_file, phase)
    
    def _render_ai_assistance_panel(self):
        """Render AI assistance information"""
        with st.expander("AI Capabilities", expanded=False):
            st.markdown("""
            ### How I Can Help
            
            - **Answer Questions**: Ask me anything about architecture and design
            - **Provide Examples**: I can share precedents and case studies
            - **Technical Details**: Get specific information about materials and systems
            - **Design Suggestions**: I'll offer ideas and recommendations
            - **Problem Solving**: Help work through design challenges
            
            Feel free to ask for direct help at any time!
            """)
    
    def _get_welcome_message(self, phase: TestPhase) -> str:
        """Get welcome message for phase"""
        messages = {
            TestPhase.IDEATION: 
                "Hello! I'm here to help with your community center design. "
                "Feel free to ask me anything - I can provide examples, suggest "
                "design strategies, or help develop your concept.",
            TestPhase.VISUALIZATION: 
                "Let's work on visualizing your design! I can help with spatial "
                "arrangements, suggest drawing techniques, or provide examples "
                "of effective architectural visualizations.",
            TestPhase.MATERIALIZATION: 
                "Time to develop the technical aspects! I can help with material "
                "selection, structural systems, construction details, or any "
                "technical questions you have."
        }
        return messages.get(phase, "How can I help with your design today?")
    
    def _get_generic_ai_response(self, user_input: str, phase: TestPhase) -> str:
        """Get direct AI response using GPT-4"""
        if self.client:
            try:
                # Create context based on phase
                system_prompt = self._create_system_prompt(phase)
                
                # Get response from OpenAI
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                # Fallback response if API fails
                return self._get_fallback_response(user_input, phase)
        else:
            # No API key, use fallback
            return self._get_fallback_response(user_input, phase)
    
    def _create_system_prompt(self, phase: TestPhase) -> str:
        """Create system prompt for Generic AI"""
        base_prompt = """You are a helpful AI assistant for architectural design. 
        You provide direct answers, specific suggestions, and detailed information 
        to help users with their design projects. Be informative and comprehensive."""
        
        phase_context = {
            TestPhase.IDEATION: """
            The user is in the ideation phase, developing initial concepts for a 
            community center in a former industrial warehouse. Provide specific 
            ideas, examples, and suggestions to help them develop their concept.
            """,
            TestPhase.VISUALIZATION: """
            The user is visualizing their design through sketches and diagrams. 
            Help with spatial arrangements, visualization techniques, and specific 
            layout suggestions.
            """,
            TestPhase.MATERIALIZATION: """
            The user is developing technical details and construction strategies. 
            Provide specific material recommendations, structural solutions, and 
            technical specifications.
            """
        }
        
        return base_prompt + phase_context.get(phase, "")
    
    def _get_fallback_response(self, user_input: str, phase: TestPhase) -> str:
        """Fallback responses if API is unavailable"""
        user_lower = user_input.lower()
        
        # Pattern-based responses
        if "example" in user_lower or "precedent" in user_lower:
            return """Here are some excellent community center examples:
            
1. **Gando School Library, Burkina Faso** - Uses local materials and passive cooling
2. **Maggie's Oldham, UK** - Adaptive reuse of a Victorian hospital
3. **The Shed, NYC** - Flexible spaces with movable structures
4. **Kampung Admiralty, Singapore** - Integrated community hub with public plaza

Each demonstrates different approaches to community engagement and adaptive reuse."""

        elif "material" in user_lower:
            return """For adaptive reuse of an industrial warehouse, consider:
            
**Structural Materials:**
- Preserve existing steel/concrete structure where possible
- Use cross-laminated timber (CLT) for new additions
- Glass curtain walls to maintain industrial aesthetic

**Interior Materials:**
- Polished concrete floors (sustainable, durable)
- Exposed mechanical systems (celebrate industrial heritage)
- Warm wood accents for community spaces

**Sustainable Options:**
- Recycled/reclaimed materials from the site
- Low-VOC finishes
- High-performance insulation systems"""

        elif "space" in user_lower or "program" in user_lower:
            return """For a 15,000-resident community center, consider this program:
            
**Public Spaces (40%):**
- Multi-purpose hall (300 people)
- Exhibition/gallery space
- Café/social area

**Education (25%):**
- Classrooms (flexible sizes)
- Computer lab
- Library/resource center

**Recreation (20%):**
- Indoor sports court
- Fitness area
- Children's play space

**Support (15%):**
- Administration offices
- Storage
- Mechanical/service areas"""
        
        else:
            return f"For the {phase.value.lower()} phase, I recommend focusing on developing clear design intentions. Consider the specific needs of your community and how the existing warehouse structure can be adapted to serve those needs. Would you like specific suggestions for any aspect of your design?"
    
    def _log_interaction_and_moves(self, user_input: str, ai_response: str, 
                                   phase: TestPhase, response_time: float):
        """Log interaction and parse design moves"""
        # Create interaction record
        interaction = InteractionData(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            phase=phase,
            interaction_type="generic_ai_dialogue",
            user_input=user_input,
            system_response=ai_response,
            response_time=response_time,
            cognitive_metrics=self._calculate_cognitive_metrics()
        )
        
        # Parse moves - Generic AI provides more direct moves
        user_moves = self.move_parser.parse_user_input(
            user_input, phase, MoveSource.USER_GENERATED
        )
        
        # AI moves are marked as AI_PROVIDED (direct solutions)
        ai_moves = self.move_parser.parse_ai_response(
            ai_response, phase, MoveSource.AI_PROVIDED
        )
        
        # Mark AI moves with high directness
        for move in ai_moves:
            move.directness_level = "direct_answer"
            move.ai_influence_strength = 0.9  # High AI influence
        
        # Log all moves
        all_moves = user_moves + ai_moves
        move_ids = []
        
        for move in all_moves:
            # Set session ID and sequence number
            move.session_id = st.session_state.test_session.id
            move.sequence_number = len(st.session_state.design_moves) + 1
            
            # Add cognitive load
            move.cognitive_load = self._assess_cognitive_load(move)
            
            # Log the move
            st.session_state.session_logger.log_design_move(move)
            if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
                st.session_state.linkography_logger.log_design_move(move)
            st.session_state.design_moves.append(move)
            move_ids.append(move.id)
        
        # Update interaction with generated moves
        interaction.generated_moves = move_ids
        
        # Log interaction
        st.session_state.session_logger.log_interaction(interaction)
        st.session_state.interaction_history.append(interaction)
    
    def _calculate_cognitive_metrics(self) -> Dict[str, float]:
        """Calculate cognitive metrics for Generic AI group"""
        # Get linkography metrics
        linkography_metrics = {}
        if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
            linkography_metrics = st.session_state.linkography_logger.get_linkography_metrics()
        
        # Calculate Generic AI-specific metrics
        metrics = {
            'cop': self._calculate_cop_score(),  # Lower due to direct answers
            'dte': self._calculate_dte_score(linkography_metrics),  # Lower engagement
            'se': self._calculate_se_score(),  # Accidental scaffolding only
            'ki': linkography_metrics.get('link_density', 0) * 0.6,  # Reduced integration
            'lp': self._calculate_lp_score(),  # Slower progression
            'ma': self._calculate_ma_score()  # Lower metacognition
        }
        
        # Composite score
        metrics['composite'] = sum(metrics.values()) / len(metrics)
        
        # Log metrics
        st.session_state.session_logger.log_cognitive_metrics(metrics)
        
        return metrics
    
    def _calculate_cop_score(self) -> float:
        """Calculate Cognitive Offloading Prevention score for Generic AI"""
        if not st.session_state.interaction_history:
            return 0.3  # Low base score for Generic AI
        
        # Count AI-provided moves vs user-generated
        ai_moves = sum(1 for m in st.session_state.design_moves 
                      if m.move_source == MoveSource.AI_PROVIDED)
        user_moves = sum(1 for m in st.session_state.design_moves 
                        if m.move_source == MoveSource.USER_GENERATED)
        
        total_moves = ai_moves + user_moves
        if total_moves == 0:
            return 0.3
        
        # High AI dependency = low COP score
        cop_score = user_moves / total_moves * 0.7
        return max(0.1, cop_score)  # Minimum 0.1
    
    def _calculate_dte_score(self, linkography_metrics: Dict[str, float]) -> float:
        """Calculate Deep Thinking Engagement score"""
        # Base on linkography metrics
        link_density = linkography_metrics.get('link_density', 0)
        critical_ratio = linkography_metrics.get('critical_move_ratio', 0)
        
        # Generic AI reduces deep thinking
        dte_score = (link_density * 0.4 + critical_ratio * 0.4) * 0.7
        return dte_score
    
    def _calculate_se_score(self) -> float:
        """Calculate Scaffolding Effectiveness score"""
        # Generic AI provides minimal scaffolding
        # Some accidental scaffolding through examples
        
        # Check for scaffolding patterns in responses
        scaffolding_phrases = ['consider', 'think about', 'you might', 'perhaps']
        scaffolding_count = 0
        
        for interaction in st.session_state.interaction_history[-5:]:
            if any(phrase in interaction.system_response.lower() 
                  for phrase in scaffolding_phrases):
                scaffolding_count += 1
        
        # Low base score with small bonus for accidental scaffolding
        se_score = 0.3 + (scaffolding_count / 5) * 0.2
        return min(0.5, se_score)  # Cap at 0.5
    
    def _calculate_lp_score(self) -> float:
        """Calculate Learning Progression score"""
        if len(st.session_state.design_moves) < 5:
            return 0.3
        
        # Analyze move sophistication over time
        recent_moves = st.session_state.design_moves[-10:]
        early_moves = st.session_state.design_moves[:10]
        
        # Direct AI assistance may hinder natural progression
        recent_ai_dependency = sum(1 for m in recent_moves 
                                 if m.move_source == MoveSource.AI_PROVIDED) / len(recent_moves)
        
        # Lower progression with high AI dependency
        lp_score = 0.5 * (1 - recent_ai_dependency * 0.5)
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
        
        # Generic AI doesn't encourage reflection
        ma_score = (reflection_moves / total_moves) * 1.5
        return min(0.4, ma_score)  # Cap at 0.4
    
    def _assess_cognitive_load(self, move: DesignMove) -> str:
        """Assess cognitive load for a move"""
        # AI-provided moves reduce cognitive load
        if move.move_source == MoveSource.AI_PROVIDED:
            return "low"
        elif move.move_type in [MoveType.SYNTHESIS, MoveType.EVALUATION]:
            return "medium"
        else:
            return "low"
    
    def _process_file_upload(self, uploaded_file, phase: TestPhase):
        """Process uploaded file"""
        # Save file
        file_path = f"thesis_tests/uploads/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Log as design move
        move = DesignMove(
            id=str(uuid.uuid4()),
            session_id=st.session_state.test_session.id,
            timestamp=datetime.now(),
            sequence_number=len(st.session_state.design_moves) + 1,
            content=f"Uploaded file: {uploaded_file.name}",
            move_type=MoveType.TRANSFORMATION,
            phase=phase,
            modality=Modality.UPLOAD,
            cognitive_operation="proposal",
            design_focus=DesignFocus.FORM,
            move_source=MoveSource.USER_GENERATED,
            cognitive_load="medium",
            concurrent_sketch=file_path if uploaded_file.type.startswith('image') else None
        )
        
        st.session_state.session_logger.log_design_move(move)
        if hasattr(st.session_state, 'linkography_logger') and st.session_state.linkography_logger:
            st.session_state.linkography_logger.log_design_move(move)
        st.session_state.design_moves.append(move)
        
        # Generate AI response about the upload
        ai_response = "I've received your file. Would you like me to provide specific feedback or suggestions based on what you've uploaded?"
        
        st.session_state.generic_ai_messages.append({
            "role": "assistant",
            "content": ai_response
        })
        
        st.success("File uploaded successfully!")