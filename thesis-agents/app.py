# simple_interface.py - ENHANCED VERSION
import streamlit as st
import asyncio
import os
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from state_manager import ArchMentorState, VisualArtifact, StudentProfile
import time
from data_collection.interaction_logger import InteractionLogger, compare_with_baseline, export_thesis_ready_data


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
if 'interaction_logger' not in st.session_state:
    st.session_state.interaction_logger = InteractionLogger()

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
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Thesis Data Collection")
    
    # Show session metrics
    if hasattr(st.session_state, 'interaction_logger') and st.session_state.interaction_logger.interactions:
        interactions_count = len(st.session_state.interaction_logger.interactions)
        st.sidebar.metric("Interactions Logged", interactions_count)
        
        # Get quick metrics
        recent_interactions = st.session_state.interaction_logger.interactions
        if recent_interactions:
            cognitive_prevention = sum(1 for i in recent_interactions if i['prevents_cognitive_offloading']) / len(recent_interactions)
            deep_thinking = sum(1 for i in recent_interactions if i['encourages_deep_thinking']) / len(recent_interactions)
            
            st.sidebar.metric("Cognitive Enhancement", f"{cognitive_prevention:.1%}")
            st.sidebar.metric("Deep Thinking", f"{deep_thinking:.1%}")

    # Export buttons
    col_export1, col_export2 = st.sidebar.columns(2)
    
    with col_export1:
        if st.button("📁 Export Session"):
            summary = st.session_state.interaction_logger.export_for_thesis_analysis()
            st.sidebar.success("Session data exported!")
            
            # Show key findings
            with st.sidebar.expander("📊 Session Summary"):
                st.write(f"**Duration:** {summary.get('session_duration_minutes', 0):.1f} min")
                st.write(f"**Cognitive Enhancement:** {summary.get('cognitive_offloading_prevention_rate', 0):.1%}")
                st.write(f"**Deep Thinking:** {summary.get('deep_thinking_encouragement_rate', 0):.1%}")
                st.write(f"**Knowledge Integration:** {summary.get('knowledge_integration_rate', 0):.1%}")
    
    with col_export2:
        if st.button("📈 Compare Baseline"):
            summary = st.session_state.interaction_logger.get_session_summary()
            comparison = compare_with_baseline(summary)
            
            st.sidebar.success("Baseline comparison complete!")
            
            with st.sidebar.expander("📊 vs Traditional Tutoring"):
                overall_improvement = comparison.get('overall_improvement', 0)
                st.write(f"**Overall Improvement:** {overall_improvement:+.1f}%")
                
                key_metrics = [
                    ('cognitive_offloading_prevention_rate', 'Prevents Cognitive Offloading'),
                    ('deep_thinking_encouragement_rate', 'Encourages Deep Thinking'),
                    ('scaffolding_rate', 'Provides Scaffolding')
                ]
                
                for metric, label in key_metrics:
                    improvement = comparison.get(f'{metric}_improvement', 0)
                    st.write(f"**{label}:** {improvement:+.1f}%")

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

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Data Collection:**")

# Export session data button
if st.session_state.interaction_logger and hasattr(st.session_state.interaction_logger, 'interactions') and len(st.session_state.interaction_logger.interactions) > 0:
    if st.sidebar.button("💾 Export Session Data"):
        try:
            # Export data for thesis analysis
            st.session_state.interaction_logger.export_for_thesis_analysis()
            
            # Get session summary
            summary = st.session_state.interaction_logger.get_session_summary()
            
            st.sidebar.success(f"✅ Data exported!")
            st.sidebar.info(f"Session: {st.session_state.interaction_logger.session_id[:8]}...")
            st.sidebar.info(f"Interactions: {len(st.session_state.interaction_logger.interactions)}")
        except Exception as e:
            st.sidebar.error(f"Export error: {str(e)}")
else:
    st.sidebar.info("No data to export yet")

# Reset button
if st.sidebar.button("🔄 Start New Project"):
    st.session_state.analysis_complete = False
    st.session_state.chat_messages = []
    st.session_state.arch_state = None
    st.session_state.analysis_result = None
    st.session_state.agents_initialized = False
    st.session_state.uploaded_image_path = None
    st.session_state.interaction_logger = InteractionLogger()  # Create new logger for new session
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
        st.subheader("🧠 Detailed Cognitive Analysis")
        
        # Cognitive flags and synthesis
        cognitive_flags = result.get('cognitive_flags', [])
        synthesis = result.get('synthesis', {})
        
        if cognitive_flags:
            st.warning("🚩 Areas for Cognitive Development Detected:")
            
            flag_explanations = {
                "needs_accessibility_guidance": "♿ **Accessibility Awareness**: Consider universal design principles",
                "needs_spatial_thinking_support": "🏗️ **Spatial Thinking**: Think about how spaces connect and flow",
                "needs_brief_clarification": "📝 **Brief Development**: More specific requirements needed",
                "low_confidence_analysis": "🔍 **Analysis Quality**: Need more detailed visual information",
                "complexity_mismatch_high": "📈 **Complexity**: Brief may be too advanced for current level",
                "complexity_mismatch_low": "📉 **Challenge Level**: Ready for more complex considerations",
                "needs_basic_guidance": "📚 **Foundational**: Building fundamental understanding",
                "needs_public_space_consideration": "🏛️ **Public Space**: Consider community interaction patterns",
                "needs_program_clarification": "📋 **Program**: Clarify functional requirements",
                "ready_for_advanced_challenge": "🎯 **Advanced Ready**: Can handle complex challenges",
                "showing_growth": "📈 **Growth Detected**: Demonstrating learning progression",
                "stuck_on_topic": "🔄 **Pattern**: Returning to same topic - trying new approach"
            }
            
            for flag in cognitive_flags:
                explanation = flag_explanations.get(flag, f"• **{flag.replace('_', ' ').title()}**")
                st.markdown(explanation)
        else:
            st.success("✅ Strong cognitive awareness demonstrated!")

        # DETAILED TEXT ANALYSIS - RESTORE THIS SECTION
        text_analysis = result.get('text_analysis', {})
        if text_analysis:
            with st.expander("📝 Text Brief Analysis Details", expanded=True):
                col_text1, col_text2 = st.columns(2)
                
                with col_text1:
                    st.write(f"**Building Type:** {text_analysis.get('building_type', 'unknown').title()}")
                    st.write(f"**Complexity:** {text_analysis.get('complexity', 'unknown')}")
                    st.write(f"**Detail Level:** {text_analysis.get('detail_level', 'unknown')}")
                    st.write(f"**Word Count:** {text_analysis.get('word_count', 0)}")
                
                with col_text2:
                    requirements = text_analysis.get('program_requirements', [])
                    st.write(f"**Requirements Found:** {len(requirements)}")
                    if requirements:
                        st.write("**Program Elements:**")
                        for req in requirements[:5]:  # Show up to 5
                            st.write(f"• {req}")
                    
                    constraints = text_analysis.get('constraints', [])
                    if constraints:
                        st.write(f"**Constraints:** {', '.join(constraints)}")
                    
                    considerations = text_analysis.get('design_considerations', [])
                    if considerations:
                        st.write("**Design Considerations:**")
                        for consideration in considerations[:3]:
                            st.write(f"• {consideration}")

        # DETAILED VISUAL ANALYSIS - RESTORE THIS SECTION
        visual_analysis = result.get('visual_analysis', {})
        if visual_analysis and not visual_analysis.get('error'):
            with st.expander("🖼️ Visual Analysis Details", expanded=True):
                
                # Check if GPT-SAM results are available
                gpt_sam_results = visual_analysis.get('gpt_sam_results')
                if gpt_sam_results and 'error' not in gpt_sam_results:
                    # Display GPT-SAM enhanced analysis
                    st.subheader("🤖 GPT Vision + SAM Analysis")
                    
                    # Show visualization if available
                    if gpt_sam_results.get('visualization') is not None:
                        st.image(gpt_sam_results['visualization'], caption="GPT Vision + SAM Analysis", use_container_width=True)
                    
                    # Show detailed GPT analysis
                    gpt_analysis = gpt_sam_results.get('gpt_analysis', {})
                    if gpt_analysis:
                        col_gpt1, col_gpt2 = st.columns(2)
                        
                        with col_gpt1:
                            spatial_elements = gpt_analysis.get('spatial_elements', [])
                            if spatial_elements:
                                st.write("**Spatial Elements Detected:**")
                                for elem in spatial_elements[:8]:
                                    elem_type = elem.get('type', 'unknown')
                                    label = elem.get('label', 'unnamed')
                                    confidence = elem.get('coordinate_confidence', 0)
                                    st.write(f"• {elem_type.title()}: {label} ({confidence:.1%})")
                            
                            circulation = gpt_analysis.get('circulation_analysis', {})
                            if circulation:
                                st.write("**Circulation Analysis:**")
                                primary = circulation.get('primary_path', 'Unknown')
                                st.write(f"• Primary: {primary}")
                                secondary = circulation.get('secondary_paths', [])
                                if secondary:
                                    st.write(f"• Secondary: {', '.join(secondary[:3])}")
                        
                        with col_gpt2:
                            design_insights = gpt_analysis.get('design_insights', {})
                            if design_insights:
                                strengths = design_insights.get('strengths', [])
                                if strengths:
                                    st.write("**Design Strengths:**")
                                    for strength in strengths[:4]:
                                        st.write(f"• {strength}")
                                
                                issues = design_insights.get('issues', [])
                                if issues:
                                    st.write("**Design Issues:**")
                                    for issue in issues[:4]:
                                        st.write(f"• {issue}")
                                
                                suggestions = design_insights.get('suggestions', [])
                                if suggestions:
                                    st.write("**Suggestions:**")
                                    for suggestion in suggestions[:3]:
                                        st.write(f"• {suggestion}")
                    
                    # Show SAM segmentation results
                    sam_results = gpt_sam_results.get('sam_results', {})
                    if sam_results and 'error' not in sam_results:
                        st.write(f"**SAM Segments Created:** {sam_results.get('num_segments', 0)}")
                    
                    # Download GPT-SAM results
                    st.markdown("---")
                    st.subheader("📥 Download Results")
                    
                    # Create JSON for download
                    import json
                    from datetime import datetime
                    
                    download_data = {
                        "analysis_timestamp": datetime.now().isoformat(),
                        "pipeline_version": "gpt_sam_v1.0",
                        "gpt_analysis": gpt_analysis,
                        "sam_results": sam_results,
                        "design_brief": st.session_state.arch_state.current_design_brief if st.session_state.arch_state else "",
                        "student_profile": {
                            "skill_level": st.session_state.arch_state.student_profile.skill_level if st.session_state.arch_state else "unknown"
                        }
                    }
                    
                    json_str = json.dumps(download_data, indent=2)
                    
                    st.download_button(
                        label="📥 Download GPT-SAM Analysis (JSON)",
                        data=json_str,
                        file_name=f"gpt_sam_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        help="Download complete GPT-SAM analysis results"
                    )
                    
                    st.markdown("---")
                
                # Original visual analysis display
                col_vis1, col_vis2 = st.columns(2)
                
                with col_vis1:
                    elements = visual_analysis.get('identified_elements', [])
                    if elements:
                        st.write("**Elements Identified:**")
                        for element in elements[:6]:  # Show up to 6
                            st.write(f"• {element}")
                    
                    accessibility = visual_analysis.get('accessibility_notes', [])
                    if accessibility:
                        st.write("**Accessibility Observations:**")
                        for note in accessibility[:4]:
                            st.write(f"• {note}")
                    
                    # Show confidence score
                    confidence = visual_analysis.get('confidence_score', 0)
                    st.write(f"**Visual Analysis Confidence:** {confidence:.1%}")
                
                with col_vis2:
                    strengths = visual_analysis.get('design_strengths', [])
                    if strengths:
                        st.write("**Design Strengths:**")
                        for strength in strengths[:4]:
                            st.write(f"• {strength}")
                    
                    opportunities = visual_analysis.get('improvement_opportunities', [])
                    if opportunities:
                        st.write("**Improvement Opportunities:**")
                        for opp in opportunities[:4]:
                            st.write(f"• {opp}")
                    
                    spatial = visual_analysis.get('spatial_relationships', [])
                    if spatial:
                        st.write("**Spatial Relationships:**")
                        for rel in spatial[:3]:
                            st.write(f"• {rel}")
                    
                    # Show any technical analysis
                    technical_notes = visual_analysis.get('technical_notes', [])
                    if technical_notes:
                        st.write("**Technical Notes:**")
                        for note in technical_notes[:3]:
                            st.write(f"• {note}")
        
        elif visual_analysis and visual_analysis.get('error'):
            with st.expander("🖼️ Visual Analysis", expanded=False):
                st.warning(f"Visual analysis encountered an issue: {visual_analysis.get('error', 'Unknown error')}")
        
        # SYNTHESIS DETAILS - RESTORE THIS SECTION  
        if synthesis:
            with st.expander("🧠 Cognitive Synthesis Details", expanded=True):
                
                # Alignment assessment
                alignment = synthesis.get('alignment_assessment', {})
                if alignment:
                    status = alignment.get('status', 'unknown')
                    st.write(f"**Alignment Status:** {status.replace('_', ' ').title()}")
                    
                    if alignment.get('alignment_score'):
                        alignment_score = alignment['alignment_score']
                        st.progress(alignment_score)
                        st.write(f"**Alignment Score:** {alignment_score:.1%}")
                    
                    missing_req = alignment.get('missing_requirements', [])
                    if missing_req:
                        st.write("**Missing Requirements:**")
                        for req in missing_req:
                            st.write(f"• {req}")
                
                # Missing considerations
                missing = synthesis.get('missing_considerations', [])
                if missing:
                    st.write("**Missing Considerations:**")
                    for item in missing:
                        st.write(f"• {item}")
                
                # Cognitive challenges identified
                challenges = synthesis.get('cognitive_challenges', [])
                if challenges:
                    st.write("**Cognitive Challenges Identified:**")
                    for challenge in challenges:
                        st.write(f"• {challenge.replace('_', ' ').title()}")
                
                # Learning opportunities
                opportunities = synthesis.get('learning_opportunities', [])
                if opportunities:
                    st.write("**Learning Opportunities:**")
                    for opp in opportunities:
                        st.write(f"• {opp}")
                
                # Next focus areas for agents
                next_focus = synthesis.get('next_focus_areas', [])
                if next_focus:
                    st.write("**Recommended Next Steps:**")
                    focus_explanations = {
                        "socratic_questioning": "🤔 Guided questioning to develop understanding",
                        "domain_expertise": "📚 Knowledge support needed",
                        "cognitive_challenge": "🧠 Ready for assumption challenges",
                        "brief_development": "📝 Brief needs more detail",
                        "spatial_analysis": "🏗️ Spatial relationships need exploration"
                    }
                    
                    for focus in next_focus:
                        explanation = focus_explanations.get(focus, f"• {focus.replace('_', ' ').title()}")
                        st.write(explanation)

        # SKILL ASSESSMENT DETAILS - ADD THIS NEW SECTION
        skill_assessment = result.get('skill_assessment', {})
        if skill_assessment:
            with st.expander("🎯 Dynamic Skill Assessment", expanded=False):
                col_skill1, col_skill2 = st.columns(2)
                
                with col_skill1:
                    detected = skill_assessment.get('detected_level', 'unknown')
                    previous = skill_assessment.get('previous_level', 'unknown')
                    updated = skill_assessment.get('updated', False)
                    
                    st.write(f"**Detected Level:** {detected.title()}")
                    st.write(f"**Previous Level:** {previous.title()}")
                    
                    if updated:
                        st.success(f"✅ Skill level updated: {previous} → {detected}")
                    else:
                        st.info(f"✅ Skill level confirmed: {detected}")
                
                with col_skill2:
                    confidence = skill_assessment.get('confidence', 0)
                    st.write(f"**Assessment Confidence:** {confidence:.1%}")
                    st.progress(confidence)
                    
                    if confidence < 0.5:
                        st.caption("📝 More interaction needed for reliable assessment")
                    elif confidence > 0.8:
                        st.caption("🎯 High confidence in skill assessment")

        # KNOWLEDGE ENHANCEMENT - ADD THIS SECTION
        knowledge_enhanced = result.get('knowledge_enhanced', {})
        if knowledge_enhanced and knowledge_enhanced.get('knowledge_enhanced'):
            with st.expander("📚 Knowledge Base Enhancement", expanded=False):
                enhancement_confidence = knowledge_enhanced.get('enhancement_confidence', 0)
                st.write(f"**Enhancement Confidence:** {enhancement_confidence:.1%}")
                
                relevant_knowledge = knowledge_enhanced.get('relevant_knowledge', [])
                if relevant_knowledge:
                    st.write(f"**Related Knowledge Found:** {len(relevant_knowledge)} sources")
                    for i, knowledge in enumerate(relevant_knowledge[:3]):
                        with st.expander(f"Source {i+1}: {knowledge.get('metadata', {}).get('title', 'Unknown')}"):
                            content = knowledge.get('content', '')
                            st.write(content[:300] + "..." if len(content) > 300 else content)

        # RAW ANALYSIS DISPLAY - RESTORE THIS
        if visual_analysis and visual_analysis.get('raw_analysis'):
            with st.expander("🔍 Raw GPT-4V Analysis", expanded=False):
                st.write(visual_analysis['raw_analysis'])

        # WHAT HAPPENS NEXT - RESTORE THIS SECTION
        st.subheader("🎯 Cognitive Enhancement Strategy")
        next_focus = synthesis.get('next_focus_areas', []) if synthesis else []
        
        if 'socratic_questioning' in next_focus:
            st.info("🤔 **Socratic Agent Active**: Will ask guiding questions to help you discover missing elements")
        
        if 'domain_expertise' in next_focus:
            st.info("📚 **Domain Expert Ready**: Can provide relevant examples and principles when needed")
        
        if 'cognitive_challenge' in next_focus:
            st.info("🚀 **Advanced Challenges**: Ready for more complex design considerations")
        
        if not next_focus:
            st.success("🎯 **Well-Developed Brief**: Continue with detailed design development")
        
        # Show which agents will likely be activated
        if cognitive_flags:
            primary_flags = cognitive_flags[:3]  # Show top 3 flags
            st.markdown("**🤖 Expected Agent Activation:**")
            
            if any("accessibility" in flag for flag in primary_flags):
                st.write("• 📚 **Domain Expert** will provide accessibility standards")
            if any("brief" in flag for flag in primary_flags):
                st.write("• 🤔 **Socratic Agent** will help clarify requirements")
            if any("spatial" in flag for flag in primary_flags):
                st.write("• 🤔 **Socratic Agent** will explore spatial relationships")
            if any("challenge" in flag for flag in primary_flags):
                st.write("• 🧠 **Cognitive Agent** will provide advanced challenges")
    
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
            
            # 🔍 DEBUG: Show what Context Agent detects
            with st.expander("🔍 DEBUG: What AI Detected", expanded=True):
                try:
                    from agents.context_agent import ContextAgent
                    debug_agent = ContextAgent("architecture")
                    
                    # Create a temporary state for testing
                    debug_state = st.session_state.arch_state
                    debug_state.messages.append({"role": "user", "content": user_input})
                    
                    # Get classification
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    context_result = loop.run_until_complete(
                        debug_agent.analyze_student_input(debug_state, user_input)
                    )
                    
                    classification = context_result["core_classification"]
                    
                    st.write("**🎯 Student Input:** ", user_input)
                    st.write("**🤖 AI Detected:**")
                    st.write(f"- Confidence Level: {classification['confidence_level']}")
                    st.write(f"- Understanding: {classification['understanding_level']}")
                    st.write(f"- Interaction Type: {classification['interaction_type']}")
                    st.write(f"- Is Technical Question: {classification['is_technical_question']}")
                    st.write(f"- Is Feedback Request: {classification['is_feedback_request']}")
                    
                    if classification.get('ai_reasoning'):
                        st.write(f"**🧠 AI Reasoning:** {classification['ai_reasoning']}")
                    
                    # Remove the test message
                    debug_state.messages.pop()
                    
                except Exception as e:
                    st.error(f"Debug failed: {e}")
            
            # Update conversation state (this was already in your code)
            st.session_state.arch_state.messages.append({
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
                    
                    # Log interaction for thesis data collection
                    if st.session_state.interaction_logger:
                        st.session_state.interaction_logger.log_interaction(
                            student_input=user_input,
                            agent_response=result["response"],
                            routing_path=result["routing_path"],
                            agents_used=result["metadata"]["agents_used"],
                            response_type=result["metadata"]["response_type"],
                            cognitive_flags=result["classification"].get("cognitive_flags", []),
                            student_skill_level=st.session_state.arch_state.student_profile.skill_level,
                            confidence_score=result["classification"].get("confidence", 0.5),
                            sources_used=result["metadata"]["sources"],
                            response_time=result["metadata"].get("response_time", 0),
                            context_classification=result["classification"],
                            metadata=result["metadata"]
                        )
                    
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