#!/usr/bin/env python3
"""
Mega Architectural Mentor - Unified AI System
Combines GPT Vision + SAM analysis with multi-agent cognitive enhancement
"""

import streamlit as st
import asyncio
import os
import tempfile
import json
from datetime import datetime
import base64
from PIL import Image
import cv2
import numpy as np

# Import all the thesis-agents components
import sys
sys.path.append('./thesis-agents')

from state_manager import ArchMentorState, VisualArtifact, StudentProfile
from agents.analysis_agent import AnalysisAgent
from agents.socratic_tutor import SocraticTutorAgent
from agents.domain_expert import DomainExpertAgent
from agents.cognitive_enhancement import CognitiveEnhancementAgent
from agents.context_agent import ContextAgent
from orchestration.langgraph_orchestrator import LangGraphOrchestrator
from vision.gpt_sam_analyzer import GPTSAMAnalyzer
from data_collection.interaction_logger import InteractionLogger

# Import detection components
sys.path.append('./src/core/detection')
from sam2_module_fixed import SAM2Segmenter

# Configure Streamlit
st.set_page_config(
    page_title="🏗️ Mega Architectural Mentor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'arch_state' not in st.session_state:
    st.session_state.arch_state = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'gpt_sam_results' not in st.session_state:
    st.session_state.gpt_sam_results = None
if 'uploaded_image_path' not in st.session_state:
    st.session_state.uploaded_image_path = None
if 'interaction_logger' not in st.session_state:
    st.session_state.interaction_logger = InteractionLogger()
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None

def main():
    """Main Streamlit application"""
    
    st.title("🏗️ Mega Architectural Mentor")
    st.markdown("### **Unified AI System: Vision Analysis + Multi-Agent Cognitive Enhancement**")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key handling
        st.subheader("🔑 OpenAI API Key")
        env_api_key = os.getenv("OPENAI_API_KEY")
        
        if env_api_key:
            st.success("✅ API key loaded from environment")
            api_key = env_api_key
        else:
            api_key = st.text_input(
                "Enter your OpenAI API Key:",
                type="password",
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            
            if not api_key:
                st.warning("⚠️ Please set OPENAI_API_KEY or enter your API key")
        
        # Student profile
        st.subheader("👤 Student Profile")
        skill_level = st.selectbox(
            "Skill Level", 
            ["beginner", "intermediate", "advanced"],
            index=1
        )
        
        domain = st.selectbox(
            "Domain",
            ["architecture", "game_design"],
            index=0
        )
        
        # Show dynamic skill level if detected
        if st.session_state.arch_state and hasattr(st.session_state.arch_state, 'student_profile'):
            detected_skill = st.session_state.arch_state.student_profile.skill_level
            if detected_skill != skill_level:
                st.info(f"🎯 AI detected skill level: **{detected_skill.title()}**")
        
        # System status
        if api_key:
            st.subheader("🤖 System Status")
            try:
                # Test GPT-SAM
                gpt_sam = GPTSAMAnalyzer(api_key)
                st.success("✅ GPT Vision: Ready")
                st.success("✅ SAM: Ready")
                
                # Test agents
                if st.session_state.orchestrator:
                    st.success("✅ Multi-Agent System: Ready")
                else:
                    st.info("⏳ Multi-Agent System: Not initialized")
                    
            except Exception as e:
                st.error(f"❌ System Error: {e}")
        
        # Pipeline information
        st.subheader("🔄 Unified Pipeline")
        st.markdown("""
        **Step 1**: 🧠 GPT Vision analyzes image and provides coordinates
        
        **Step 2**: 🎨 SAM segments based on GPT coordinates
        
        **Step 3**: 🔍 Analysis Agent processes results
        
        **Step 4**: 🤖 Multi-Agent System provides cognitive enhancement
        
        **Step 5**: 📊 Display comprehensive results and insights
        """)
        
        # Reset button
        if st.button("🔄 Start New Project"):
            st.session_state.analysis_complete = False
            st.session_state.chat_messages = []
            st.session_state.arch_state = None
            st.session_state.analysis_result = None
            st.session_state.gpt_sam_results = None
            st.session_state.uploaded_image_path = None
            st.session_state.orchestrator = None
            st.rerun()
    
    # Main interface
    if not st.session_state.analysis_complete:
        # PHASE 1: INITIAL ANALYSIS
        st.header("🔍 Phase 1: Design Analysis")
        st.markdown("Upload your design and brief to begin the comprehensive AI analysis.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 Design Brief")
            design_brief = st.text_area(
                "Describe your design project:",
                placeholder="Example: Design a community center for 200 people with accessible entrances, flexible meeting spaces, and consideration for Nordic lighting conditions...",
                height=150
            )
            
            st.subheader("🖼️ Upload Design")
            uploaded_file = st.file_uploader(
                "Upload your architectural drawing or floor plan",
                type=['png', 'jpg', 'jpeg'],
                help="Any hand-drawn or digital architectural drawing"
            )
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Your Design", use_container_width=True)
                
                # Image info
                width, height = image.size
                st.info(f"📐 Image dimensions: {width} × {height} pixels")
            
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
            
            if st.button("🔍 Analyze My Design", type="primary", disabled=not design_brief.strip() or not api_key):
                if design_brief.strip() and api_key:
                    with st.spinner("🧠 Running comprehensive AI analysis... This may take 1-2 minutes"):
                        progress_bar = st.progress(0)
                        
                        try:
                            # Step 1: Initialize state and save image
                            progress_bar.progress(10)
                            st.caption("Initializing system...")
                            
                            # Create state
                            state = ArchMentorState()
                            state.current_design_brief = design_brief
                            state.student_profile = StudentProfile(skill_level=skill_level)
                            state.domain = domain
                            
                            # Handle uploaded image
                            temp_image_path = None
                            if uploaded_file:
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                                    image.save(tmp_file.name)
                                    temp_image_path = tmp_file.name
                                
                                st.session_state.uploaded_image_path = temp_image_path
                                
                                artifact = VisualArtifact(
                                    id="uploaded_sketch",
                                    type="sketch",
                                    image_path=temp_image_path
                                )
                                state.current_sketch = artifact
                                state.visual_artifacts.append(artifact)
                            
                            # Step 2: GPT Vision + SAM Analysis
                            progress_bar.progress(30)
                            st.caption("Running GPT Vision + SAM analysis...")
                            
                            gpt_sam = GPTSAMAnalyzer(api_key)
                            if temp_image_path:
                                gpt_sam_results = gpt_sam.analyze_image(temp_image_path)
                                st.session_state.gpt_sam_results = gpt_sam_results
                            else:
                                gpt_sam_results = {"error": "No image provided"}
                                st.session_state.gpt_sam_results = gpt_sam_results
                            
                            # Step 3: Analysis Agent
                            progress_bar.progress(60)
                            st.caption("Running cognitive analysis...")
                            
                            analysis_agent = AnalysisAgent(domain)
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            analysis_result = loop.run_until_complete(analysis_agent.process(state))
                            
                            # Step 4: Initialize orchestrator
                            progress_bar.progress(80)
                            st.caption("Initializing multi-agent system...")
                            
                            orchestrator = LangGraphOrchestrator(domain)
                            st.session_state.orchestrator = orchestrator
                            
                            # Store results
                            st.session_state.arch_state = state
                            st.session_state.analysis_result = analysis_result
                            st.session_state.analysis_complete = True
                            
                            progress_bar.progress(100)
                            st.caption("Analysis complete!")
                            
                            st.success("🎉 Comprehensive Analysis Complete! Ready for cognitive enhancement.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
                            st.write("Please check your API keys and try again.")
                else:
                    if not design_brief.strip():
                        st.info("👆 Enter a design brief above to start the analysis")
                    if not api_key:
                        st.info("👆 Enter your OpenAI API key to analyze your design")
        
        # Show what the system will do
        if design_brief.strip() and api_key:
            st.markdown("---")
            st.subheader("🔮 What the Mega System Will Do")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown("**🤖 AI Agents That Will Help You:**")
                st.markdown("• **🔍 Analysis Agent**: Detects thinking gaps and learning opportunities")
                st.markdown("• **📚 Domain Expert**: Provides architectural knowledge and precedents")
                st.markdown("• **🤔 Socratic Tutor**: Asks guiding questions to develop understanding")
                st.markdown("• **🧠 Cognitive Enhancement**: Challenges assumptions and provides advanced thinking")
                st.markdown("• **🔍 Context Agent**: Understands your learning state and adapts responses")
            
            with col_info2:
                st.markdown("**🎯 Vision Analysis Capabilities:**")
                st.markdown("• **🧠 GPT Vision**: Analyzes your drawings and provides detailed insights")
                st.markdown("• **🎨 SAM Segmentation**: Creates precise masks of architectural elements")
                st.markdown("• **📊 Spatial Analysis**: Understands room relationships and circulation")
                st.markdown("• **💡 Design Insights**: Identifies strengths and improvement opportunities")
                st.markdown("• **♿ Accessibility Analysis**: Checks for universal design principles")
    
    else:
        # PHASE 2: COMPREHENSIVE RESULTS + INTERACTIVE CHAT
        
        # Top row: Project overview
        st.header("📋 Your Project")
        
        col_brief, col_image = st.columns([2, 1])
        
        with col_brief:
            brief = st.session_state.arch_state.current_design_brief
            st.markdown(f"**Design Brief:** {brief}")
            
            # Analysis summary
            result = st.session_state.analysis_result
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            
            with col_metric1:
                confidence = result.get('confidence_score', 0)
                st.metric("Analysis Confidence", f"{confidence:.1%}")
            
            with col_metric2:
                flags = len(result.get('cognitive_flags', []))
                st.metric("Learning Areas", flags)
            
            with col_metric3:
                building_type = result.get('text_analysis', {}).get('building_type', 'unknown')
                st.metric("Project Type", building_type.title())
            
            with col_metric4:
                gpt_sam_results = st.session_state.gpt_sam_results
                if gpt_sam_results and 'error' not in gpt_sam_results:
                    spatial_elements = gpt_sam_results.get('gpt_analysis', {}).get('spatial_elements', [])
                    st.metric("Spatial Elements", len(spatial_elements))
                else:
                    st.metric("Vision Analysis", "Not available")
        
        with col_image:
            if st.session_state.uploaded_image_path:
                st.image(st.session_state.uploaded_image_path, caption="Your Design", use_container_width=True)
        
        st.markdown("---")
        
        # Main content area
        col_analysis, col_chat = st.columns([1, 2])
        
        with col_analysis:
            st.subheader("🧠 Comprehensive Analysis Results")
            
            # GPT-SAM Results
            gpt_sam_results = st.session_state.gpt_sam_results
            if gpt_sam_results and 'error' not in gpt_sam_results:
                with st.expander("🤖 GPT Vision + SAM Analysis", expanded=True):
                    st.subheader("🎨 Vision Analysis Results")
                    
                    # Show visualization if available
                    if gpt_sam_results.get('visualization') is not None:
                        st.image(gpt_sam_results['visualization'], caption="AI Analysis Visualization", use_container_width=True)
                    
                    # Show detailed GPT analysis
                    gpt_analysis = gpt_sam_results.get('gpt_analysis', {})
                    if gpt_analysis:
                        col_gpt1, col_gpt2 = st.columns(2)
                        
                        with col_gpt1:
                            spatial_elements = gpt_analysis.get('spatial_elements', [])
                            if spatial_elements:
                                st.write("**🏗️ Spatial Elements Detected:**")
                                for elem in spatial_elements[:6]:
                                    elem_type = elem.get('type', 'unknown')
                                    label = elem.get('label', 'unnamed')
                                    confidence = elem.get('coordinate_confidence', 0)
                                    st.write(f"• {elem_type.title()}: {label} ({confidence:.1%})")
                            
                            circulation = gpt_analysis.get('circulation_analysis', {})
                            if circulation:
                                st.write("**🔄 Circulation Analysis:**")
                                primary = circulation.get('primary_path', 'Unknown')
                                st.write(f"• Primary: {primary}")
                                secondary = circulation.get('secondary_paths', [])
                                if secondary:
                                    st.write(f"• Secondary: {', '.join(secondary[:2])}")
                        
                        with col_gpt2:
                            design_insights = gpt_analysis.get('design_insights', {})
                            if design_insights:
                                strengths = design_insights.get('strengths', [])
                                if strengths:
                                    st.write("**✅ Design Strengths:**")
                                    for strength in strengths[:3]:
                                        st.write(f"• {strength}")
                                
                                issues = design_insights.get('issues', [])
                                if issues:
                                    st.write("**⚠️ Design Issues:**")
                                    for issue in issues[:3]:
                                        st.write(f"• {issue}")
                                
                                suggestions = design_insights.get('suggestions', [])
                                if suggestions:
                                    st.write("**💡 Suggestions:**")
                                    for suggestion in suggestions[:3]:
                                        st.write(f"• {suggestion}")
                    
                    # Show SAM segmentation results
                    sam_results = gpt_sam_results.get('sam_results', {})
                    if sam_results and 'error' not in sam_results:
                        st.write(f"**🎨 SAM Segments Created:** {sam_results.get('num_segments', 0)}")
            
            # Cognitive Analysis
            result = st.session_state.analysis_result
            cognitive_flags = result.get('cognitive_flags', [])
            synthesis = result.get('synthesis', {})
            
            with st.expander("🧠 Cognitive Analysis", expanded=True):
                if cognitive_flags:
                    st.warning("🚩 Areas for Cognitive Development Detected:")
                    
                    flag_explanations = {
                        "needs_accessibility_guidance": "♿ **Accessibility Awareness**: Consider universal design principles",
                        "needs_spatial_thinking_support": "🏗️ **Spatial Thinking**: Think about how spaces connect and flow",
                        "needs_brief_clarification": "📝 **Brief Development**: More specific requirements needed",
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
                
                # Learning opportunities
                opportunities = synthesis.get('learning_opportunities', [])
                if opportunities:
                    st.write("**🎯 Learning Opportunities:**")
                    for opp in opportunities:
                        st.write(f"• {opp}")
            
            # Text Analysis
            text_analysis = result.get('text_analysis', {})
            if text_analysis:
                with st.expander("📝 Text Brief Analysis", expanded=False):
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
                            for req in requirements[:5]:
                                st.write(f"• {req}")
                        
                        constraints = text_analysis.get('constraints', [])
                        if constraints:
                            st.write(f"**Constraints:** {', '.join(constraints)}")
            
            # Skill Assessment
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
            
            # Download results
            st.markdown("---")
            st.subheader("📥 Download Results")
            
            # Create comprehensive JSON for download
            download_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "pipeline_version": "mega_architectural_mentor_v1.0",
                "design_brief": st.session_state.arch_state.current_design_brief if st.session_state.arch_state else "",
                "student_profile": {
                    "skill_level": st.session_state.arch_state.student_profile.skill_level if st.session_state.arch_state else "unknown"
                },
                "gpt_sam_results": gpt_sam_results,
                "cognitive_analysis": result,
                "interaction_log": st.session_state.interaction_logger.get_session_summary() if st.session_state.interaction_logger else {}
            }
            
            json_str = json.dumps(download_data, indent=2, default=str)
            
            st.download_button(
                label="📥 Download Complete Analysis (JSON)",
                data=json_str,
                file_name=f"mega_architectural_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Download complete analysis results including vision analysis and cognitive assessment"
            )
        
        with col_chat:
            st.subheader("🤖 AI Mentor Conversation")
            
            # Initialize chat if not started
            if not st.session_state.chat_messages:
                # Generate initial response based on analysis
                cognitive_flags = result.get('cognitive_flags', [])
                building_type = result.get('text_analysis', {}).get('building_type', 'project')
                
                if cognitive_flags:
                    initial_message = f"I've analyzed your {building_type} design using both vision analysis and cognitive assessment. I notice some opportunities for development, particularly around {cognitive_flags[0].replace('_', ' ')}. What specific aspect would you like to explore first?"
                else:
                    initial_message = f"Excellent work on your {building_type} design! The comprehensive analysis shows strong development. What aspect would you like to discuss or improve further?"
                
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
                                    for source in sources[:3]:
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
                        # Process through LangGraph workflow
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        result = loop.run_until_complete(
                            st.session_state.orchestrator.process_student_input(
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
                st.info("💡 **Try asking**: 'What precedents exist for this type of project?' or 'How can I improve the lighting design?' or 'Can you review my spatial organization?'")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p><strong>🏗️ Mega Architectural Mentor</strong> | 
    Powered by GPT Vision + SAM + Multi-Agent Cognitive Enhancement | 
    Comprehensive AI system for architectural learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 