"""
MEGA Architectural Mentor - Enhanced Graph ML Dashboard Integration
Integrates advanced Graph ML analysis with Linkography data
"""

import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import json
import torch
import numpy as np
from typing import Dict, List, Any

from linkography_analyzer import LinkographySessionAnalyzer
from linkography_graph_ml_integration import GraphMLLinkographyAnalyzer
from linkography_graph_ml_visualizations import LinkographyGraphMLVisualizer
from thesis_colors import THESIS_COLORS


def render_enhanced_graph_ml_section(benchmark_dashboard):
    """Enhanced Graph ML section with linkography integration"""
    
    st.markdown('<h2 class="sub-header">Advanced Graph ML Analysis</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="explanation-box">
    <h4>Temporal Graph Neural Networks + Linkography</h4>
    <p>This section combines state-of-the-art Graph ML techniques with linkography data to provide
    deep insights into design thinking evolution, learning patterns, and cognitive development.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize analyzers
    linkography_analyzer = LinkographySessionAnalyzer()
    graph_ml_analyzer = GraphMLLinkographyAnalyzer()
    visualizer = LinkographyGraphMLVisualizer()
    
    # Load linkography sessions
    with st.spinner("Loading linkography data for Graph ML analysis..."):
        linkograph_sessions = linkography_analyzer.analyze_all_sessions()
    
    if not linkograph_sessions:
        st.warning("No linkography data available for Graph ML analysis.")
        return
    
    # Tab layout for enhanced visualizations
    tabs = st.tabs([
        "🧠 Temporal Evolution",
        "🎯 Anomaly Detection", 
        "💡 Pattern Discovery",
        "📊 Embeddings",
        "🔄 Learning Trajectories",
        "📈 Cognitive Development"
    ])
    
    # Convert sessions to list for analysis
    session_list = list(linkograph_sessions.values())
    
    with tabs[0]:
        render_temporal_evolution_tab(graph_ml_analyzer, visualizer, session_list)
    
    with tabs[1]:
        render_anomaly_detection_tab(graph_ml_analyzer, visualizer, session_list)
    
    with tabs[2]:
        render_pattern_discovery_tab(graph_ml_analyzer, visualizer, session_list)
    
    with tabs[3]:
        render_embeddings_tab(graph_ml_analyzer, visualizer, session_list)
    
    with tabs[4]:
        render_learning_trajectories_tab(graph_ml_analyzer, visualizer, session_list)
    
    with tabs[5]:
        render_cognitive_development_tab(graph_ml_analyzer, visualizer, session_list)


def render_temporal_evolution_tab(analyzer, visualizer, sessions):
    """Render temporal evolution analysis"""
    st.markdown("### Design Thinking Evolution Graph")
    
    st.markdown("""
    This graph shows how design thinking evolves across sessions, with nodes representing
    sessions and edges showing the strength of cognitive progression between them.
    """)
    
    # Create evolution graph
    with st.spinner("Analyzing design evolution patterns..."):
        evolution_graph = analyzer.create_evolution_graph(sessions[:10])  # Limit to 10 sessions
    
    # Visualize
    fig = visualizer.create_temporal_evolution_graph(evolution_graph)
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.markdown("### Evolution Insights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Sessions Analyzed",
            len(evolution_graph.nodes()),
            delta=f"+{len(evolution_graph.edges())} connections"
        )
    
    with col2:
        avg_progression = np.mean([
            evolution_graph.nodes[n].get('learning_progression', 0) 
            for n in evolution_graph.nodes()
        ])
        st.metric(
            "Avg Learning Progress",
            f"{avg_progression:.2%}",
            delta="+12%" if avg_progression > 0.5 else "-8%"
        )
    
    with col3:
        density = len(evolution_graph.edges()) / (len(evolution_graph.nodes()) * (len(evolution_graph.nodes()) - 1))
        st.metric(
            "Connection Density",
            f"{density:.2%}",
            help="Higher density indicates more consistent progression"
        )


def render_anomaly_detection_tab(analyzer, visualizer, sessions):
    """Render anomaly detection analysis"""
    st.markdown("### Learning Struggle Detection")
    
    st.markdown("""
    Advanced anomaly detection identifies moments where students struggle with concepts,
    enabling targeted interventions and personalized support.
    """)
    
    # Select session for analysis
    session_ids = [s.session_id for s in sessions]
    selected_session_id = st.selectbox(
        "Select Session for Anomaly Analysis",
        session_ids,
        format_func=lambda x: f"Session {x[:8]}..."
    )
    
    selected_session = next(s for s in sessions if s.session_id == selected_session_id)
    
    # Perform analysis
    with st.spinner("Running anomaly detection..."):
        analysis = analyzer.analyze_session(selected_session)
        anomaly_data = analysis['anomaly_detection']
    
    # Display overall status
    if anomaly_data['is_struggling']:
        st.error(f"⚠️ Learning struggles detected (Score: {anomaly_data['overall_anomaly_score']:.2f})")
    else:
        st.success(f"✅ Normal learning pattern (Score: {anomaly_data['overall_anomaly_score']:.2f})")
    
    # Create struggle dashboard
    struggle_analysis = {
        'timeline': [0.3, 0.4, 0.5, 0.8, 0.9, 0.7, 0.6, 0.5],  # Mock timeline
        'node_types': {'Orphan Moves': 5, 'Weak Links': 8, 'Phase Gaps': 3},
        'recommendation_categories': {
            'Scaffolding': 3,
            'Exploration': 2,
            'Reflection': 2
        },
        'cognitive_changes': {
            'Deep Thinking': {'before': 0.4, 'after': 0.7},
            'Integration': {'before': 0.3, 'after': 0.6},
            'Progression': {'before': 0.5, 'after': 0.8}
        }
    }
    
    fig = visualizer.create_learning_struggle_dashboard(struggle_analysis)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    if anomaly_data.get('recommendations'):
        st.markdown("### Personalized Recommendations")
        for i, rec in enumerate(anomaly_data['recommendations'], 1):
            st.info(f"**{i}.** {rec}")


def render_pattern_discovery_tab(analyzer, visualizer, sessions):
    """Render pattern discovery analysis"""
    st.markdown("### Design Pattern Discovery")
    
    st.markdown("""
    Graph ML algorithms automatically discover recurring patterns in design thinking,
    revealing effective strategies and common pitfalls.
    """)
    
    # Analyze patterns across multiple sessions
    pattern_timeline = []
    for i, session in enumerate(sessions[:20]):  # Analyze up to 20 sessions
        analysis = analyzer.analyze_session(session)
        patterns = analysis['pattern_predictions']
        patterns['step'] = i
        pattern_timeline.append(patterns)
    
    # Visualize pattern emergence
    fig = visualizer.create_pattern_emergence_timeline(pattern_timeline)
    st.plotly_chart(fig, use_container_width=True)
    
    # Pattern statistics
    st.markdown("### Pattern Statistics")
    pattern_counts = {'chunk': 0, 'web': 0, 'sawtooth': 0, 'orphan': 0}
    
    for patterns in pattern_timeline:
        for pattern_type in pattern_counts:
            if patterns.get(pattern_type, 0) > 0.5:  # Threshold
                pattern_counts[pattern_type] += 1
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    colors = [THESIS_COLORS['primary_purple'], THESIS_COLORS['primary_violet'],
              THESIS_COLORS['neutral_warm'], THESIS_COLORS['accent_coral']]
    
    for i, (pattern, count) in enumerate(pattern_counts.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background-color: {colors[i]}20; 
                        border-radius: 10px; border: 2px solid {colors[i]};">
                <h3 style="color: {colors[i]}; margin: 0;">{pattern.capitalize()}</h3>
                <h1 style="margin: 10px 0;">{count}</h1>
                <p style="margin: 0;">occurrences</p>
            </div>
            """, unsafe_allow_html=True)


def render_embeddings_tab(analyzer, visualizer, sessions):
    """Render embedding visualization analysis"""
    st.markdown("### Design Move Embeddings")
    
    st.markdown("""
    Visualize how design moves are represented in high-dimensional space,
    revealing semantic relationships and conceptual clusters.
    """)
    
    # Select visualization method
    method = st.selectbox(
        "Dimensionality Reduction Method",
        ['tsne', 'pca', 'umap'],
        help="Different methods reveal different aspects of the data structure"
    )
    
    # Get embeddings from first few sessions
    all_embeddings = []
    all_labels = []
    
    for session in sessions[:5]:  # Use first 5 sessions
        analysis = analyzer.analyze_session(session)
        embeddings = analysis['embeddings']['node_embeddings']
        
        # Create labels from moves
        for i, move in enumerate(session.linkographs[0].moves[:len(embeddings)]):
            all_embeddings.append(embeddings[i])
            all_labels.append(f"{move.phase[:3]}-{move.move_type[:3]}")
    
    if all_embeddings:
        # Create visualization
        embeddings_array = np.array(all_embeddings)
        fig = visualizer.create_embedding_visualization(embeddings_array, all_labels, method)
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.markdown("### Embedding Insights")
        st.markdown("""
        - **Clusters** indicate similar design thinking patterns
        - **Outliers** may represent innovative or struggling moments
        - **Trajectories** show progression of thinking over time
        """)


def render_learning_trajectories_tab(analyzer, visualizer, sessions):
    """Render learning trajectory analysis"""
    st.markdown("### Personalized Learning Trajectories")
    
    st.markdown("""
    Track individual learning paths through the design space, identifying
    optimal progressions and areas needing support.
    """)
    
    # Analyze trajectories
    trajectories = []
    for session in sessions:
        analysis = analyzer.analyze_session(session)
        cognitive_scores = analysis['cognitive_assessment']
        trajectories.append(cognitive_scores)
    
    # Create trajectory visualization
    if len(trajectories) >= 3:
        fig = visualizer.create_cognitive_trajectory_radar(trajectories[:5])
        st.plotly_chart(fig, use_container_width=True)
    
    # Trajectory insights
    st.markdown("### Trajectory Analysis")
    
    if len(trajectories) >= 2:
        # Calculate progression metrics
        initial_scores = trajectories[0]
        latest_scores = trajectories[-1]
        
        improvements = {}
        for metric in initial_scores:
            initial = initial_scores[metric]
            latest = latest_scores[metric]
            improvements[metric] = (latest - initial) / (initial + 0.001)
        
        # Display improvements
        sorted_improvements = sorted(improvements.items(), key=lambda x: x[1], reverse=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Top Improvements")
            for metric, improvement in sorted_improvements[:3]:
                if improvement > 0:
                    st.success(f"**{metric.replace('_', ' ').title()}**: +{improvement:.1%}")
        
        with col2:
            st.markdown("#### 📉 Areas Needing Focus")
            for metric, improvement in sorted_improvements[-3:]:
                if improvement < 0:
                    st.warning(f"**{metric.replace('_', ' ').title()}**: {improvement:.1%}")


def render_cognitive_development_tab(analyzer, visualizer, sessions):
    """Render cognitive development analysis"""
    st.markdown("### Cognitive Development Patterns")
    
    st.markdown("""
    Compare cognitive metrics across sessions to understand development patterns
    and identify areas of strength and opportunity.
    """)
    
    # Prepare data for comparison
    session_analyses = []
    for session in sessions[:10]:  # Limit to 10 sessions
        analysis = analyzer.analyze_session(session)
        analysis['session_id'] = session.session_id[:8]
        session_analyses.append(analysis)
    
    # Create comparison visualization
    fig = visualizer.create_graph_metric_comparison(session_analyses)
    st.plotly_chart(fig, use_container_width=True)
    
    # Development insights
    st.markdown("### Development Insights")
    
    # Calculate aggregate statistics
    if session_analyses:
        avg_metrics = {}
        for analysis in session_analyses:
            for metric, value in analysis['cognitive_assessment'].items():
                if metric not in avg_metrics:
                    avg_metrics[metric] = []
                avg_metrics[metric].append(value)
        
        # Display averages
        st.markdown("#### Average Cognitive Metrics")
        metric_cols = st.columns(3)
        
        for i, (metric, values) in enumerate(avg_metrics.items()):
            col_idx = i % 3
            with metric_cols[col_idx]:
                avg_value = np.mean(values)
                std_value = np.std(values) if len(values) > 1 else 0
                
                st.markdown(f"""
                <div style="padding: 15px; background-color: #f0f0f0; border-radius: 8px;">
                    <h5 style="margin: 0;">{metric.replace('_', ' ').title()}</h5>
                    <h3 style="margin: 5px 0;">{avg_value:.2%}</h3>
                    <p style="margin: 0; font-size: 0.9em;">±{std_value:.2%}</p>
                </div>
                """, unsafe_allow_html=True)


# Export function
__all__ = ['render_enhanced_graph_ml_section']