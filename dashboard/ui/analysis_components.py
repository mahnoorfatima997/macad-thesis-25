"""
Analysis dashboard components for displaying comprehensive cognitive and phase analysis.
"""

import streamlit as st
from typing import Dict, Any, Optional


def safe_get_nested_dict(obj, *keys, default=None):
    """Safely get nested dictionary values, handling both dict and AgentResponse objects"""
    if obj is None:
        return default
    
    # Convert AgentResponse to dict if needed
    if hasattr(obj, 'response_text'):
        obj = convert_agent_response_to_dict(obj)
    
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def convert_agent_response_to_dict(agent_response):
    """Convert AgentResponse object to dictionary format for backward compatibility"""
    if hasattr(agent_response, 'response_text'):  # AgentResponse object
        return {
            'response_text': agent_response.response_text,
            'response_type': agent_response.response_type.value if hasattr(agent_response.response_type, 'value') else str(agent_response.response_type),
            'cognitive_flags': [flag.value if hasattr(flag, 'value') else str(flag) for flag in agent_response.cognitive_flags],
            'enhancement_metrics': {
                'cognitive_offloading_prevention_score': agent_response.enhancement_metrics.cognitive_offloading_prevention_score,
                'deep_thinking_engagement_score': agent_response.enhancement_metrics.deep_thinking_engagement_score,
                'knowledge_integration_score': agent_response.enhancement_metrics.knowledge_integration_score,
                'scaffolding_effectiveness_score': agent_response.enhancement_metrics.scaffolding_effectiveness_score,
                'learning_progression_score': agent_response.enhancement_metrics.learning_progression_score,
                'metacognitive_awareness_score': agent_response.enhancement_metrics.metacognitive_awareness_score,
                'overall_cognitive_score': agent_response.enhancement_metrics.overall_cognitive_score,
                'scientific_confidence': agent_response.enhancement_metrics.scientific_confidence
            },
            'agent_name': agent_response.agent_name,
            'metadata': agent_response.metadata,
            'journey_alignment': {
                'current_phase': agent_response.journey_alignment.current_phase,
                'phase_progress': agent_response.journey_alignment.phase_progress,
                'phase_questions_asked': agent_response.journey_alignment.phase_questions_asked if hasattr(agent_response.journey_alignment, 'phase_questions_asked') else 0,
                'next_phase': agent_response.journey_alignment.next_phase if hasattr(agent_response.journey_alignment, 'next_phase') else None,
                'journey_progress': agent_response.journey_alignment.journey_progress,
                'phase_confidence': agent_response.journey_alignment.phase_confidence,
            },
            'progress_update': {
                'phase_progress': agent_response.progress_update.phase_progress,
                'cognitive_state': agent_response.progress_update.cognitive_state,
                'learning_progression': agent_response.progress_update.learning_progression,
                'skill_level_update': agent_response.progress_update.skill_level_update,
                'engagement_level_update': agent_response.progress_update.engagement_level_update
            }
        }
    else:  # Already a dictionary
        return agent_response


def render_cognitive_analysis_dashboard(analysis_result: Dict[str, Any]):
    """Render the comprehensive cognitive analysis dashboard."""
    if not analysis_result:
        return
    
    # Ensure analysis_result is a dictionary
    if hasattr(analysis_result, 'response_text'):
        analysis_result = convert_agent_response_to_dict(analysis_result)
        
    with st.expander("🧠 Cognitive Analysis Dashboard", expanded=True):
        st.markdown("""
        <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center; color: #1f77b4;">
            🧠 Your Learning Journey Analysis
        </div>
        <style>
        .stExpander .stMarkdown p { font-size: 13px !important; line-height: 1.3 !important; margin-bottom: 8px !important; }
        .stExpander .stMarkdown strong { font-size: 13px !important; }
        .stExpander .stMarkdown div { font-size: 13px !important; }
        </style>
        """, unsafe_allow_html=True)
        
        # Create three columns for different analysis sections
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            _render_current_phase_section(analysis_result)
        
        with col2:
            _render_learning_insights_section(analysis_result)
        
        with col3:
            _render_project_context_section(analysis_result)
        
        # Dynamic recommendations section
        _render_recommendations_section(analysis_result)
        
        # Overall progress summary
        _render_progress_summary(analysis_result)


def _render_current_phase_section(analysis_result: Dict[str, Any]):
    """Render the current design phase section."""
    st.markdown("**🎯 Current Design Phase**")
    
    # Prefer engine-driven phase status if available
    engine_status = safe_get_nested_dict(analysis_result, 'phase_engine_status') or {}
    conversation_progression = analysis_result.get('conversation_progression', {})
    phase_analysis = safe_get_nested_dict(analysis_result, 'phase_analysis') or {}

    if engine_status:
        current_phase = engine_status.get('current_phase', 'unknown')
        phase_completion = engine_status.get('completion_percent', 0)
        phase_confidence = engine_status.get('phase_confidence', 0)
    elif conversation_progression:
        current_phase = conversation_progression.get('conversation_phase', 'unknown')
        phase_completion = conversation_progression.get('phase_progress', 0) * 100
        phase_confidence = conversation_progression.get('confidence', 0)
    elif phase_analysis:
        current_phase = phase_analysis.get('phase', 'unknown')
        phase_confidence = phase_analysis.get('confidence', 0)
        phase_completion = phase_analysis.get('progression_score', 0) * 100
    else:
        current_phase = 'unknown'
        phase_confidence = 0
        phase_completion = 0

    # Phase status with color coding
    if phase_confidence > 0.8:
        phase_color = "🟢"
    elif phase_confidence > 0.6:
        phase_color = "🟡"
    else:
        phase_color = "🔴"

    st.write(f"{phase_color} **{current_phase.title()}**")
    st.write(f"Confidence: {phase_confidence:.1%}")
    st.write(f"Progress: {phase_completion:.0f}%")

    # Show next phase if available
    next_phase = phase_analysis.get('next_phase')
    if next_phase:
        phase_names = {
            'ideation': 'Ideation',
            'visualization': 'Visualization',
            'materialization': 'Materialization'
        }
        next_phase_name = phase_names.get(next_phase, next_phase.replace('_', ' ').title())
        st.write(f"🎯 **Next:** {next_phase_name}")
    else:
        st.write("🔍 Phase not detected yet")


def _render_learning_insights_section(analysis_result: Dict[str, Any]):
    """Render the learning insights section."""
    st.markdown("**💡 Learning Insights**")
    synthesis = safe_get_nested_dict(analysis_result, 'synthesis') or {}
    
    # Cognitive Challenges
    cognitive_challenges = synthesis.get('cognitive_challenges', [])
    if cognitive_challenges:
        st.write(f"🚧 **Challenges** ({len(cognitive_challenges)}):")
        for challenge in cognitive_challenges[:3]:  # Show top 3
            challenge_name = challenge.replace('_', ' ').title()
            st.write(f"• {challenge_name}")
        if len(cognitive_challenges) > 3:
            st.write(f"• ... and {len(cognitive_challenges) - 3} more")
    else:
        st.write("✅ No major challenges detected")
    
    # Learning Opportunities
    learning_opportunities = synthesis.get('learning_opportunities', [])
    if learning_opportunities:
        st.write(f"🌟 **Opportunities** ({len(learning_opportunities)}):")
        for opportunity in learning_opportunities[:3]:  # Show top 3
            st.write(f"• {opportunity}")
        if len(learning_opportunities) > 3:
            st.write(f"• ... and {len(learning_opportunities) - 3} more")
    else:
        st.write("📚 Ready for new challenges")


def _render_project_context_section(analysis_result: Dict[str, Any]):
    """Render the project context section."""
    st.markdown("**📋 Project Context**")
    text_analysis = safe_get_nested_dict(analysis_result, 'text_analysis') or {}
    synthesis = safe_get_nested_dict(analysis_result, 'synthesis') or {}
    
    # Building Type
    building_type = text_analysis.get('building_type', 'unknown')
    if building_type != 'unknown':
        st.write(f"🏗️ **Type:** {building_type.title()}")
    else:
        st.write("🏗️ **Type:** Not specified")
    
    # Program Requirements
    requirements = text_analysis.get('program_requirements', [])
    if requirements:
        st.write(f"📝 **Requirements** ({len(requirements)}):")
        for req in requirements[:2]:  # Show top 2
            st.write(f"• {req}")
        if len(requirements) > 2:
            st.write(f"• ... and {len(requirements) - 2} more")
    else:
        st.write("📝 **Requirements:** Not specified")
    
    # Missing Considerations
    missing_considerations = synthesis.get('missing_considerations', [])
    if missing_considerations:
        st.write(f"⚠️ **Missing** ({len(missing_considerations)}):")
        for consideration in missing_considerations[:2]:  # Show top 2
            st.write(f"• {consideration}")
        if len(missing_considerations) > 2:
            st.write(f"• ... and {len(missing_considerations) - 2} more")


def _render_recommendations_section(analysis_result: Dict[str, Any]):
    """Render the recommendations section."""
    synthesis = safe_get_nested_dict(analysis_result, 'synthesis') or {}
    phase_analysis = safe_get_nested_dict(analysis_result, 'phase_analysis') or {}
    
    # Check if we have any meaningful recommendations
    next_focus_areas = synthesis.get('next_focus_areas', [])
    phase_recommendations = phase_analysis.get('phase_recommendations', [])
    missing_considerations = synthesis.get('missing_considerations', [])
    
    if next_focus_areas or phase_recommendations or missing_considerations:
        st.markdown("---")
        st.markdown("**🎯 Smart Recommendations**")
        
        # Next Focus Areas
        if next_focus_areas:
            st.write("**Focus on these areas next:**")
            for i, focus in enumerate(next_focus_areas[:3], 1):  # Show top 3
                focus_name = focus.replace('_', ' ').title()
                st.write(f"{i}. {focus_name}")
        
        # Phase Recommendations
        if phase_recommendations:
            st.write("**Phase-specific guidance:**")
            for rec in phase_recommendations[:2]:  # Show top 2
                st.write(f"• {rec}")
        
        # Missing Considerations
        if missing_considerations:
            st.write("**Consider addressing:**")
            for consideration in missing_considerations[:2]:  # Show top 2
                st.write(f"• {consideration}")


def _render_progress_summary(analysis_result: Dict[str, Any]):
    """Render the overall progress summary."""
    phase_analysis = safe_get_nested_dict(analysis_result, 'phase_analysis') or {}
    engine_status = safe_get_nested_dict(analysis_result, 'phase_engine_status') or {}
    
    if engine_status:
        phase_completion = engine_status.get('completion_percent', 0)
        st.markdown("---")
        st.markdown(f"**📊 Phase Progress: {phase_completion:.0f}% complete**")
        progress_ratio = phase_completion / 100
        st.progress(progress_ratio)
    elif phase_analysis:
        # Show phase-based progress (legacy)
        phase_completion = phase_analysis.get('progression_score', 0) * 100
        st.markdown("---")
        st.markdown(f"**📊 Phase Progress: {phase_completion:.0f}% complete**")
        
        # Progress visualization
        progress_ratio = phase_completion / 100
        st.progress(progress_ratio)
        
        if progress_ratio < 0.25:
            st.write("🔄 **Getting Started** - Building foundational knowledge")
        elif progress_ratio < 0.5:
            st.write("📝 **In Progress** - Developing design thinking")
        elif progress_ratio < 0.75:
            st.write("🎯 **Making Good Progress** - Applying concepts effectively")
        elif progress_ratio < 1.0:
            st.write("✨ **Almost Complete** - Refining and polishing")
        else:
            st.write("✅ **Phase Complete** - Ready for next phase!")


def render_metrics_summary(analysis_result: Dict[str, Any]):
    """Render the metrics summary in a 4-column layout."""
    if not analysis_result:
        return
    
    # Ensure analysis_result is a dictionary
    if hasattr(analysis_result, 'response_text'):
        analysis_result = convert_agent_response_to_dict(analysis_result)
        
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        _render_current_phase_metric(analysis_result)
    
    with col_metric2:
        _render_learning_balance_metric(analysis_result)
    
    with col_metric3:
        _render_phase_progress_metric(analysis_result)
    
    with col_metric4:
        _render_project_type_metric(analysis_result)


def _render_current_phase_metric(analysis_result: Dict[str, Any]):
    """Render current phase metric."""
    engine_status = safe_get_nested_dict(analysis_result, 'phase_engine_status') or {}
    conversation_progression = analysis_result.get('conversation_progression', {})
    phase_analysis = safe_get_nested_dict(analysis_result, 'phase_analysis') or {}
    
    if engine_status:
        current_phase = engine_status.get('current_phase', 'unknown')
        phase_completion = engine_status.get('completion_percent', 0)
    elif conversation_progression:
        current_phase = conversation_progression.get('current_phase', 'unknown')
        phase_completion = conversation_progression.get('phase_progress', 0) * 100
    elif phase_analysis:
        current_phase = phase_analysis.get('phase', 'unknown')
        phase_completion = phase_analysis.get('progression_score', 0) * 100
    else:
        current_phase = 'unknown'
        phase_completion = 0
    
    # Format phase display
    phase_display = {
        'ideation': '💡 Ideation',
        'visualization': '🎨 Visualization', 
        'materialization': '🏗️ Materialization',
        'completion': '✅ Completion',
        'discovery': '🔍 Discovery',
        'exploration': '🔬 Exploration',
        'synthesis': '🧠 Synthesis',
        'application': '⚡ Application',
        'reflection': '🤔 Reflection',
        'unknown': '❓ Unknown'
    }
    
    phase_name = phase_display.get(current_phase, f"❓ {current_phase.title()}")
    
    st.markdown(f"""
        <div style='text-align: center;'>
            <h5 style='margin-bottom: 0.2rem;'>Current Phase</h5>
            <p style='font-size: 1rem; margin: 0;'>{phase_name}</p>
            <p style='font-size: 0.8rem; color: gray;'>{phase_completion:.0f}% complete</p>
        </div>
    """, unsafe_allow_html=True)


def _render_learning_balance_metric(analysis_result: Dict[str, Any]):
    """Render learning balance metric."""
    conversation_progression = analysis_result.get('conversation_progression', {})
    
    # Use conversation progression data if available
    if conversation_progression:
        conversation_summary = conversation_progression.get('conversation_summary', {})
        challenges = len(conversation_summary.get('challenges', []))
        opportunities = len(conversation_summary.get('opportunities', []))
    else:
        # Fallback to synthesis data
        synthesis = safe_get_nested_dict(analysis_result, 'synthesis') or {}
        challenges = len(synthesis.get('cognitive_challenges', []))
        opportunities = len(synthesis.get('learning_opportunities', []))
    
    # Calculate learning balance
    if challenges + opportunities > 0:
        balance_ratio = opportunities / (challenges + opportunities)
        if balance_ratio > 0.6:
            balance_status = "🌟 Strong"
        elif balance_ratio > 0.4:
            balance_status = "📈 Good"
        else:
            balance_status = "⚠️ Needs Focus"
    else:
        balance_status = "🔄 Starting"
    
    st.markdown(f"""
        <div style='text-align: center;'>
            <h5 style='margin-bottom: 0.2rem;'>Learning Balance</h5>
            <p style='font-size: 1rem; margin: 0;'>{balance_status}</p>
            <p style='font-size: 0.8rem; color: gray;'>{challenges} challenges, {opportunities} opportunities</p>
        </div>
    """, unsafe_allow_html=True)


def _render_phase_progress_metric(analysis_result: Dict[str, Any]):
    """Render phase progress metric."""
    phase_analysis = safe_get_nested_dict(analysis_result, 'phase_analysis') or {}
    engine_status = safe_get_nested_dict(analysis_result, 'phase_engine_status') or {}
    
    if engine_status:
        # Prefer engine-driven percent when available
        completed_phases = engine_status.get('completed_phases', 0)
        total_phases = engine_status.get('total_phases', 3)
        phase_progress = engine_status.get('completion_percent', 0)
    else:
        completed_phases = phase_analysis.get('completed_phases', 0)
        total_phases = phase_analysis.get('total_phases', 0)
        phase_progress = (completed_phases / total_phases) * 100 if total_phases > 0 else 0
    
    if total_phases > 0:
        if completed_phases > 0:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <h5 style='margin-bottom: 0.2rem;'>Phase Progress</h5>
                    <p style='font-size: 1rem; margin: 0;'>{completed_phases}/{total_phases}</p>
                    <p style='font-size: 0.8rem; color: gray;'>{phase_progress:.0f}%</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Show next milestone when none completed
            next_phase = phase_analysis.get('next_phase')
            if next_phase:
                phase_names = {
                    'ideation': 'Ideation',
                    'visualization': 'Visualization',
                    'materialization': 'Materialization'
                }
                next_phase_name = phase_names.get(next_phase, next_phase.replace('_', ' ').title())
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <h5 style='margin-bottom: 0.2rem;'>Next Phase</h5>
                        <p style='font-size: 1rem; margin: 0;'>{next_phase_name}</p>
                        <p style='font-size: 0.8rem; color: gray;'>Phase progression</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <h5 style='margin-bottom: 0.2rem;'>Phase Progress</h5>
                        <p style='font-size: 1rem; margin: 0;'>Getting started</p>
                        <p style='font-size: 0.8rem; color: gray;'>Phase-based assessment</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        # Show phase-based progress instead
        phase_completion = engine_status.get('completion_percent', 0) if engine_status else phase_analysis.get('progression_score', 0) * 100
        st.markdown(f"""
            <div style='text-align: center;'>
                <h5 style='margin-bottom: 0.2rem;'>Phase Progress</h5>
                <p style='font-size: 1rem; margin: 0;'>{phase_completion:.0f}%</p>
                <p style='font-size: 0.8rem; color: gray;'>Based on conversation</p>
            </div>
        """, unsafe_allow_html=True)


def _render_project_type_metric(analysis_result: Dict[str, Any]):
    """Render project type metric."""
    conversation_progression = analysis_result.get('conversation_progression', {})
    
    # Use conversation progression data if available
    if conversation_progression:
        conversation_summary = conversation_progression.get('conversation_summary', {})
        project_context = conversation_summary.get('project_context', {})
        building_type = project_context.get('building_type', 'Unknown')
        complexity_level = project_context.get('complexity_level', 'moderate')
    else:
        # Get building type from text analysis
        text_analysis = safe_get_nested_dict(analysis_result, 'text_analysis') or {}
        building_type = text_analysis.get('building_type', 'Unknown')
        complexity_level = 'moderate'  # Default complexity level
    
    if building_type and building_type != 'Unknown':
        # Format building type for display
        formatted_type = building_type.replace('_', ' ').title()
        
        # Determine complexity indicator
        if complexity_level in ['high', 'complex', 'advanced']:
            complexity = "🔴 Complex"
        elif complexity_level in ['medium', 'moderate', 'intermediate']:
            complexity = "🟡 Moderate"
        else:
            complexity = "🟢 Simple"
        
        st.markdown(f"""
            <div style='text-align: center;'>
                <h5 style='margin-bottom: 0.2rem;'>Project Type</h5>
                <p style='font-size: 1rem; margin: 0;'>{formatted_type}</p>
                <p style='font-size: 0.8rem; color: gray;'>{complexity}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='text-align: center;'>
                <h5 style='margin-bottom: 0.2rem;'>Project Type</h5>
                <p style='font-size: 1rem; margin: 0;'>Unknown</p>
                <p style='font-size: 0.8rem; color: gray;'>Not specified</p>
            </div>
        """, unsafe_allow_html=True)


def render_phase_progress_section(analysis_result: Dict[str, Any]):
    """Render the detailed phase progress section."""
    if not analysis_result:
        return
    
    # Ensure analysis_result is a dictionary
    if hasattr(analysis_result, 'response_text'):
        analysis_result = convert_agent_response_to_dict(analysis_result)
        
    phase_analysis = safe_get_nested_dict(analysis_result, 'phase_analysis') or {}
    if not phase_analysis:
        return
        
    st.markdown("---")
    st.markdown("""
    <div class="compact-text" style="font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center;">
        🎯 Design Phase Progress
    </div>
    """, unsafe_allow_html=True)
    
    current_phase = phase_analysis.get('phase', 'unknown')
    phase_completion = phase_analysis.get('progression_score', 0) * 100
    next_phase = phase_analysis.get('next_phase')
    progression_ready = phase_analysis.get('progression_ready', False)
    
    # Phase descriptions
    phase_descriptions = {
        'ideation': 'Concept development and problem framing',
        'visualization': 'Spatial development and form exploration', 
        'materialization': 'Technical development and implementation',
        'completion': 'Final refinement and presentation'
    }
    
    # Phase activities
    phase_activities = {
        'ideation': ['Site analysis', 'Program development', 'Concept exploration'],
        'visualization': ['Spatial planning', 'Form development', 'Circulation design'],
        'materialization': ['Construction details', 'Material specification', 'Technical systems'],
        'completion': ['Final details', 'Presentation preparation', 'Documentation']
    }
    
    col_phase1, col_phase2 = st.columns([1, 1])
    
    with col_phase1:
        # Progress bar with meaningful progress
        meaningful_progress = phase_completion / 100
        st.progress(meaningful_progress)
        
        # Display progress with context
        if meaningful_progress < 0.25:
            progress_status = "🔄 Getting Started"
        elif meaningful_progress < 0.5:
            progress_status = "📝 In Progress"
        elif meaningful_progress < 0.75:
            progress_status = "🎯 Making Good Progress"
        elif meaningful_progress < 1.0:
            progress_status = "✨ Almost Complete"
        else:
            progress_status = "✅ Phase Complete"
        
        st.write(f"**{progress_status}** ({phase_completion:.0f}% Complete)")
        
        # Show milestone information if available
        milestone_completion = phase_analysis.get('milestone_completion', 0)
        completed_milestones = phase_analysis.get('completed_milestones', 0)
        total_milestones = phase_analysis.get('total_milestones', 0)
        
        if total_milestones > 0:
            st.write(f"📋 **Milestones:** {completed_milestones}/{total_milestones} completed")
            
            # Show next milestone if available
            next_milestone = phase_analysis.get('next_milestone')
            if next_milestone:
                milestone_names = {
                    'site_analysis': 'Site Analysis',
                    'program_requirements': 'Program Requirements',
                    'concept_development': 'Concept Development',
                    'spatial_organization': 'Spatial Organization',
                    'circulation_design': 'Circulation Design',
                    'form_development': 'Form Development',
                    'lighting_strategy': 'Lighting Strategy',
                    'construction_systems': 'Construction Systems',
                    'material_selection': 'Material Selection',
                    'technical_details': 'Technical Details',
                    'presentation_prep': 'Presentation Preparation',
                    'documentation': 'Documentation'
                }
                next_milestone_name = milestone_names.get(next_milestone, next_milestone.replace('_', ' ').title())
                st.write(f"🎯 **Next Focus:** {next_milestone_name}")
        
        # Show phase recommendations if available
        phase_recommendations = phase_analysis.get('phase_recommendations', [])
        if phase_recommendations:
            st.write("💡 **Recommendations:**")
            for rec in phase_recommendations[:3]:  # Show top 3 recommendations
                st.write(f"• {rec}")
        
        # Phase description
        description = phase_descriptions.get(current_phase, 'Phase description not available')
        st.write(f"**Current Focus:** {description}")
        
        # Next phase info
        if next_phase and progression_ready:
            next_phase_name = next_phase.replace('_', ' ').title()
            st.success(f"🎉 Ready to progress to **{next_phase_name}** phase!")
        elif next_phase:
            next_phase_name = next_phase.replace('_', ' ').title()
            st.info(f"Next phase: **{next_phase_name}**")
    
    with col_phase2:
        # Current phase activities
        activities = phase_activities.get(current_phase, [])
        if activities:
            st.write("**Key Activities for This Phase:**")
            for activity in activities:
                st.write(f"• {activity}")
        
        # Learning opportunities from synthesis
        synthesis = safe_get_nested_dict(analysis_result, 'synthesis') or {}
        learning_opportunities = synthesis.get('learning_opportunities', [])
        if learning_opportunities:
            st.write("**Learning Opportunities:**")
            for opportunity in learning_opportunities[:2]:  # Show top 2
                st.write(f"• {opportunity}") 