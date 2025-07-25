# simple_interface.py - ENHANCED VERSION
import streamlit as st
import asyncio
import os
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from state_manager import ArchMentorState, VisualArtifact, StudentProfile
import time

# Page config
st.set_page_config(
    page_title="ArchMentor - Cognitive Enhancement System",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ ArchMentor: AI-Powered Architecture Mentor")
st.markdown("### Multi-Agent Cognitive Enhancement System")
st.markdown("---")

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'arch_state' not in st.session_state:
    st.session_state.arch_state = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'agents_initialized' not in st.session_state:
    st.session_state.agents_initialized = False
if 'uploaded_image_path' not in st.session_state:
    st.session_state.uploaded_image_path = None

# Sidebar - Always show current project context
st.sidebar.header("👤 Student Profile")
skill_level = st.sidebar.selectbox(
    "Skill Level", 
    ["beginner", "intermediate", "advanced"],
    index=1
)

domain = st.sidebar.selectbox(
    "Domain",
    ["architecture", "game_design"],
    index=0
)

# Show dynamic skill level if detected
if st.session_state.arch_state and hasattr(st.session_state.arch_state, 'student_profile'):
    detected_skill = st.session_state.arch_state.student_profile.skill_level
    if detected_skill != skill_level:
        st.sidebar.info(f"🎯 AI detected skill level: **{detected_skill.title()}**")

st.sidebar.markdown("---")

# ALWAYS show current project context if analysis is complete
if st.session_state.analysis_complete and st.session_state.arch_state:
    st.sidebar.subheader("📋 Current Project")
    
    # Show brief
    brief = st.session_state.arch_state.current_design_brief
    st.sidebar.markdown(f"**Brief:** {brief[:100]}..." if len(brief) > 100 else f"**Brief:** {brief}")
    
    # Show image if available
    if st.session_state.uploaded_image_path:
        st.sidebar.image(st.session_state.uploaded_image_path, caption="Your Design", width=200)
    
    # Show key analysis metrics
    result = st.session_state.analysis_result
    if result:
        confidence = result.get('confidence_score', 0)
        flags = len(result.get('cognitive_flags', []))
        building_type = result.get('text_analysis', {}).get('building_type', 'unknown')
        
        st.sidebar.markdown(f"**Type:** {building_type.title()}")
        st.sidebar.markdown(f"**Analysis Confidence:** {confidence:.1%}")
        st.sidebar.markdown(f"**Learning Opportunities:** {flags}")

st.sidebar.markdown("---")

# Enhanced interaction guidance
st.sidebar.markdown("**💬 You Can Ask:**")
st.sidebar.markdown("• *'What are precedents for this type of project?'*")
st.sidebar.markdown("• *'How can I improve the lighting in my design?'*")
st.sidebar.markdown("• *'What accessibility standards should I consider?'*")
st.sidebar.markdown("• *'Can you review my spatial organization?'*")
st.sidebar.markdown("• *'I think my design is perfect'* (for challenges)")

st.sidebar.markdown("---")
st.sidebar.markdown("**🤖 AI Agents:**")
st.sidebar.markdown("🔍 **Analysis**: Detects thinking gaps")
st.sidebar.markdown("📚 **Knowledge**: Provides architectural principles & precedents")
st.sidebar.markdown("🤔 **Socratic**: Asks guiding questions")
st.sidebar.markdown("🧠 **Cognitive**: Challenges assumptions")

# Reset button
if st.sidebar.button("🔄 Start New Project"):
    st.session_state.analysis_complete = False
    st.session_state.chat_messages = []
    st.session_state.arch_state = None
    st.session_state.analysis_result = None
    st.session_state.agents_initialized = False
    st.session_state.uploaded_image_path = None
    st.rerun()

# Main content
if not st.session_state.analysis_complete:
    # PHASE 1: INITIAL ANALYSIS (same as before)
    st.header("🔍 Phase 1: Design Analysis")
    st.markdown("Upload your design and brief to begin the cognitive enhancement journey.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Design Brief")
        design_brief = st.text_area(
            "Describe your design project:",
            placeholder="Example: Design a community center for 200 people with accessible entrances, flexible meeting spaces, and consideration for Nordic lighting conditions...",
            height=150
        )
        
        st.subheader("🖼️ Upload Sketch")
        uploaded_file = st.file_uploader(
            "Upload your architectural sketch or floor plan",
            type=['png', 'jpg', 'jpeg'],
            help="Any hand-drawn or digital architectural drawing"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Your uploaded sketch", use_container_width=True)
        
        # Quick test scenarios
        st.subheader("🧪 Quick Test Scenarios")
        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            if st.button("📝 Test: Nordic Community Center"):
                design_brief = "Design a community center for 200 people in a Nordic country with central gathering space, considering limited natural light and accessibility requirements"
                st.rerun()
            
            if st.button("♿ Test: Accessibility Focus"):
                design_brief = "Design a community center with universal design principles, ensuring accessibility for all users including wheelchair access and visual/hearing accommodations"
                st.rerun()
        
        with col_test2:
            if st.button("🏗️ Test: Complex Brief"):
                design_brief = "Design a 2000 sq ft community center for 200 people with accessible entrances, flexible meeting spaces, commercial kitchen, childcare area, and parking for 50 cars in an urban setting"
                st.rerun()
            
            if st.button("🎮 Test: Game Design"):
                design_brief = "Design a platformer level with multiple paths to the goal, considering player progression and challenge curve"
                st.rerun()
    
    with col2:
        st.subheader("🚀 Ready to Begin?")
        
        if st.button("🔍 Analyze My Design", type="primary", disabled=not design_brief.strip()):
            if design_brief.strip():
                with st.spinner("🧠 AI analyzing your design..."):
                    # Initialize agents
                    analysis_agent = AnalysisAgent(domain)
                    socratic_agent = SocraticTutorAgent(domain)
                    
                    # Create state
                    state = ArchMentorState()
                    state.current_design_brief = design_brief
                    state.student_profile = StudentProfile(skill_level=skill_level)
                    state.domain = domain
                    
                    # Handle uploaded image
                    if uploaded_file:
                        upload_dir = "./uploads"
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        file_path = os.path.join(upload_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Store image path for persistent display
                        st.session_state.uploaded_image_path = file_path
                        
                        artifact = VisualArtifact(
                            id="uploaded_sketch",
                            type="sketch",
                            image_path=file_path
                        )
                        state.current_sketch = artifact
                        state.visual_artifacts.append(artifact)
                    
                    # Run analysis
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Get analysis
                        analysis_result = loop.run_until_complete(analysis_agent.process(state))
                        
                        # Store results in session state
                        st.session_state.arch_state = state
                        st.session_state.analysis_result = analysis_result
                        st.session_state.analysis_agent = analysis_agent
                        st.session_state.socratic_agent = socratic_agent
                        st.session_state.agents_initialized = True
                        st.session_state.analysis_complete = True
                        
                        st.success("🎉 Analysis Complete! Ready for cognitive enhancement.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.write("Please check your API keys and try again.")
        
        if not design_brief.strip():
            st.info("👆 Enter a design brief above to start the analysis")

else:
    # PHASE 2: ENHANCED ANALYSIS RESULTS + FLEXIBLE CHAT
    
    # Top row: Brief + Image (always visible)
    st.header("📋 Your Project")
    
    col_brief, col_image = st.columns([2, 1])
    
    with col_brief:
        brief = st.session_state.arch_state.current_design_brief
        st.markdown(f"**Design Brief:** {brief}")
        
        # Analysis summary
        result = st.session_state.analysis_result
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        
        with col_metric1:
            confidence = result.get('confidence_score', 0)
            st.metric("Analysis Confidence", f"{confidence:.1%}")
        
        with col_metric2:
            flags = len(result.get('cognitive_flags', []))
            st.metric("Learning Areas", flags)
        
        with col_metric3:
            building_type = result.get('text_analysis', {}).get('building_type', 'unknown')
            st.metric("Project Type", building_type.title())
    
    with col_image:
        if st.session_state.uploaded_image_path:
            st.image(st.session_state.uploaded_image_path, caption="Your Design", use_container_width=True)
    
    st.markdown("---")
    
    # Main interaction area
    col_analysis, col_chat = st.columns([1, 2])
    
    with col_analysis:
        st.subheader("🧠 Analysis Insights")
        
        # Expandable detailed analysis
        with st.expander("📊 Detailed Analysis", expanded=False):
            # [Keep all your existing detailed analysis display code here]
            cognitive_flags = result.get('cognitive_flags', [])
            if cognitive_flags:
                st.markdown("**Learning Opportunities Detected:**")
                for flag in cognitive_flags[:5]:  # Show top 5
                    st.write(f"• {flag.replace('_', ' ').title()}")
            
            text_analysis = result.get('text_analysis', {})
            if text_analysis:
                st.markdown("**Brief Analysis:**")
                st.write(f"Complexity: {text_analysis.get('complexity', 'unknown')}")
                st.write(f"Detail Level: {text_analysis.get('detail_level', 'unknown')}")
        
        # Suggested questions based on analysis
        st.subheader("💡 Suggested Questions")
        
        building_type = result.get('text_analysis', {}).get('building_type', 'building')
        cognitive_flags = result.get('cognitive_flags', [])
        
        suggestions = []
        if 'needs_accessibility_guidance' in cognitive_flags:
            suggestions.append("What accessibility standards should I consider?")
        if 'needs_spatial_thinking_support' in cognitive_flags:
            suggestions.append("How can I improve the spatial organization?")
        if building_type == "community center":
            suggestions.append("What are good precedents for community centers?")
            suggestions.append("How can I enhance the lighting in central spaces?")
        
        suggestions.extend([
            "Can you review my design approach?",
            "What improvements would you suggest?",
            "I think my design solution is optimal"
        ])
        
        for suggestion in suggestions[:6]:
            if st.button(f"💬 {suggestion}", key=f"suggest_{suggestion}", use_container_width=True):
                # Add to chat as if user typed it
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": suggestion
                })
                
                # Update state
                st.session_state.arch_state.messages.append({
                    "role": "user",
                    "content": suggestion
                })
                
                st.rerun()
    
    with col_chat:
        st.subheader("🤖 AI Mentor Conversation")
        
        # Initialize chat if not started
        if not st.session_state.chat_messages:
            # Generate initial response based on analysis
            cognitive_flags = result.get('cognitive_flags', [])
            if cognitive_flags:
                initial_message = f"I've analyzed your {building_type} design. I notice some opportunities for development, particularly around {cognitive_flags[0].replace('_', ' ')}. What specific aspect would you like to explore first?"
            else:
                initial_message = f"Great work on your {building_type} design! The analysis shows strong development. What aspect would you like to discuss or improve further?"
            
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": initial_message,
                    "type": "initial_analysis"
                }
            ]
        
        # Display chat messages with enhanced formatting
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_messages:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                
                elif message["role"] == "assistant":
                    with st.chat_message("assistant"):
                        st.write(message["content"])
                        
                        # Enhanced agent info display
                        response_type = message.get("type", "unknown")
                        routing_path = message.get("routing_path", "unknown")
                        sources = message.get("sources", [])
                        
                        # Show response type with appropriate emoji
                        type_display = {
                            "knowledge_primary": "📚 Knowledge Response",
                            "knowledge_enhanced_socratic": "📚🤔 Knowledge + Questions",
                            "cognitive_primary": "🧠 Cognitive Challenge",
                            "socratic_primary": "🤔 Socratic Guidance",
                            "multi_agent": "🤖 Multi-Agent Analysis",
                            "initial_analysis": "🔍 Initial Analysis"
                        }
                        
                        if response_type in type_display:
                            st.caption(f"**{type_display[response_type]}**")
                        
                        # Show knowledge sources if available
                        if sources:
                            with st.expander("📚 Sources Referenced"):
                                for source in sources[:3]:  # Show top 3
                                    st.write(f"• {source}")
        
        # Enhanced chat input with examples
        user_input = st.chat_input("Ask about improvements, precedents, standards, or request a review...")
        
        if user_input:
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Update conversation state
            st.session_state.arch_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate multi-agent response
            with st.spinner("🧠 AI agents collaborating..."):
                try:
                    # Initialize LangGraph orchestrator if needed
                    if 'langgraph_orchestrator' not in st.session_state:
                        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
                        st.session_state.langgraph_orchestrator = LangGraphOrchestrator(domain)
                    
                    # Process through LangGraph workflow
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        st.session_state.langgraph_orchestrator.process_student_input(
                            st.session_state.arch_state
                        )
                    )
                    
                    # Add enhanced response
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "type": result["metadata"]["response_type"],
                        "routing_path": result["routing_path"],
                        "agents_used": result["metadata"]["agents_used"],
                        "sources": result["metadata"]["sources"],
                        "classification": result["classification"]
                    })
                    
                    # Update state
                    st.session_state.arch_state.messages.append({
                        "role": "assistant",
                        "content": result["response"]
                    })
                    
                except Exception as e:
                    # Fallback response
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"I'd love to help with that. Can you be more specific about what aspect you'd like to explore?",
                        "type": "error_fallback"
                    })
            
            st.rerun()
        
        # Interaction guidance
        if len(st.session_state.chat_messages) <= 1:
            st.info("💡 **Try asking**: 'What precedents exist for this type of project?' or 'How can I improve the lighting design?'")

# Footer
st.markdown("---")
st.markdown("""
**🔬 Research System**: Multi-agent AI that provides knowledge, asks questions, and challenges assumptions 
to enhance learning without cognitive offloading.
            (""")