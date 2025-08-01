"""
Simplified Graph ML Dashboard - Works without PyTorch dependencies
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter, defaultdict
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from linkography_analyzer import LinkographySessionAnalyzer
from thesis_colors import THESIS_COLORS, METRIC_COLORS


def render_enhanced_graph_ml_section(dashboard):
    """Enhanced Graph ML section that keeps useful tabs and adds linkography integration"""
    
    st.markdown('<h2 class="sub-header">Graph ML Analysis</h2>', unsafe_allow_html=True)
    
    # Check if PyVis visualizations exist for Knowledge Graph and Learning Trajectories
    pyvis_dir = dashboard.results_path / "visualizations" / "pyvis"
    
    # Initialize linkography analyzer for new tabs
    analyzer = LinkographySessionAnalyzer()
    sessions = analyzer.analyze_all_sessions()
    session_list = list(sessions.values()) if sessions else []
    
    # Create tabs - KEEP the first two, ADD new linkography-based tabs
    tabs = st.tabs([
        "Knowledge Graph",           # KEEP THIS
        "Learning Trajectories",     # KEEP THIS
        "Session Network",           # NEW - replaces Agent Collaboration
        "Pattern Discovery",         # NEW - replaces Cognitive Patterns
        "Evolution Timeline",        # NEW - replaces Session Evolution
        "Learning Metrics"           # NEW - additional insights
    ])
    
    # Tab 1: Knowledge Graph (ENHANCED)
    with tabs[0]:
        # Framework visualization first
        st.markdown("#### Framework")
        if pyvis_dir and pyvis_dir.exists():
            st.markdown("""
            This interactive graph shows the theoretical relationships between architectural concepts, 
            cognitive processes, and AI components that guide the MEGA system.
            """)
            
            html_file = pyvis_dir / "knowledge_graph_pyvis.html"
            if html_file.exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
            else:
                st.error("Knowledge graph visualization not found.")
            
            st.markdown("""
            #### Framework Components:
            - **Purple nodes**: Spatial & form concepts (Design Process, Spatial Reasoning)
            - **Orange nodes**: Context & environment (Site, Materials, Sustainability)
            - **Dark nodes**: Critical thinking processes
            - **Rose nodes**: Metacognitive & synthesis elements
            - **Coral nodes**: AI system components
            """)
        else:
            st.info("Framework visualization not available. Run full benchmarking to generate.")
        
        # Session-based graphs below
        st.markdown("---")
        st.markdown("#### Session-Based Concepts")
        st.markdown("""
        These 3D knowledge graphs are extracted from your actual design discussions and show
        the real concepts you've been exploring and how they connect.
        """)
        
        if session_list:
            # Import the knowledge graph builder
            try:
                from session_knowledge_graphs import SessionKnowledgeGraphBuilder
                kg_builder = SessionKnowledgeGraphBuilder()
                
                # Reverse session list to show most recent first
                reversed_sessions = list(reversed(session_list))
                
                # Session selector - default to most recent (index 0)
                selected_session_idx = st.selectbox(
                    "Select a session to view its concept network:",
                    range(len(reversed_sessions)),
                    index=0,  # Default to most recent
                    format_func=lambda i: f"Session {reversed_sessions[i].session_id[:8]} - {len(session_list)-i} sessions ago" if i > 0 else f"Session {reversed_sessions[i].session_id[:8]} - Most Recent"
                )
                
                # Build and display knowledge graph for selected session
                session = reversed_sessions[selected_session_idx]
                G = kg_builder.build_session_knowledge_graph(session)
                
                # Display the 3D graph
                fig = kg_builder.visualize_session_knowledge_graph_3d(G, session.session_id)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show statistics
                if len(G.nodes()) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Unique Concepts", len(G.nodes()))
                    with col2:
                        st.metric("Concept Links", len(G.edges()))
                    with col3:
                        # Most connected concept
                        degrees = dict(G.degree())
                        if degrees:
                            max_node = max(degrees, key=degrees.get)
                            st.metric("Most Connected", G.nodes[max_node]['label'])
                    with col4:
                        # Average connections
                        avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
                        st.metric("Avg Connections", f"{avg_degree:.1f}")
                
                # Always show concept evolution
                if len(reversed_sessions) > 1:
                    st.markdown("### Concept Evolution Across Sessions")
                    st.markdown("*Showing from oldest to newest sessions*")
                    # Use original order for evolution (oldest to newest)
                    evolution_fig = kg_builder.create_concept_evolution_graph(session_list[:10])
                    st.plotly_chart(evolution_fig, use_container_width=True)
                
                # Show comparison grid (always visible)
                if len(reversed_sessions) > 1:
                    st.markdown("### Session Concept Network Comparison")
                    st.markdown("*Showing the 4 most recent sessions with interactive, color-coded concept networks*")
                    
                    # Get individual session graphs
                    session_graphs = kg_builder.create_individual_session_graphs(reversed_sessions[:4])
                    
                    # Display in 2x2 grid
                    col1, col2 = st.columns(2)
                    
                    for idx, (session_id, fig) in enumerate(session_graphs):
                        if idx % 2 == 0:
                            with col1:
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            with col2:
                                st.plotly_chart(fig, use_container_width=True)
                
            except ImportError as e:
                st.error(f"Could not load session knowledge graph builder: {e}")
        else:
            st.warning("No session data available for concept extraction.")
    
    # Tab 2: Learning Trajectories (ENHANCED)
    with tabs[1]:
        # Theoretical framework visualization first
        st.markdown("#### Theoretical Framework")
        if pyvis_dir and pyvis_dir.exists():
            st.markdown("""
            This interactive graph shows the theoretical skill progression framework that guides 
            learning assessment in the MEGA system.
            """)
            
            html_file = pyvis_dir / "learning_trajectories_pyvis.html"
            if html_file.exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
            else:
                st.error("Learning trajectories visualization not found.")
            
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <h4 style="margin-top: 0;">Framework Components:</h4>
            
            - **Foundation → Expert**: Five proficiency levels for each skill
            - **Cross-skill dependencies**: Skills that unlock or enhance others
            - **Learning pathways**: Multiple valid routes to expertise
            
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("PyVis visualizations not available. Run full benchmarking to generate.")
        
        # Session-based trajectories below
        st.markdown("---")
        st.markdown("#### Session-Based Learning Trajectories")
        st.markdown("""
        These graphs show actual learning progressions extracted from your design sessions,
        revealing how skills develop through architectural thinking and problem-solving.
        """)
        
        if session_list:
            # Import the trajectory builder
            try:
                from session_learning_trajectories import SessionLearningTrajectoryBuilder
                trajectory_builder = SessionLearningTrajectoryBuilder()
                
                # Reverse session list to show most recent first
                reversed_sessions = list(reversed(session_list))
                
                # Session selector - default to most recent (index 0)
                selected_session_idx = st.selectbox(
                    "Select a session to view its learning trajectory:",
                    range(len(reversed_sessions)),
                    index=0,
                    format_func=lambda i: f"Session {reversed_sessions[i].session_id[:8]} - {len(session_list)-i} sessions ago" if i > 0 else f"Session {reversed_sessions[i].session_id[:8]} - Most Recent"
                )
                
                # Build and display trajectory for selected session
                session = reversed_sessions[selected_session_idx]
                G = trajectory_builder.build_session_trajectory_graph(session)
                
                # Display the trajectory graph
                fig = trajectory_builder.visualize_session_trajectory(G, session.session_id)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show session statistics
                if len(G.nodes()) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Count skills demonstrated
                    skill_counts = Counter(G.nodes[n]['skill'] for n in G.nodes())
                    
                    with col1:
                        st.metric("Skills Demonstrated", len(skill_counts))
                    with col2:
                        st.metric("Skill Instances", len(G.nodes()))
                    with col3:
                        # Most developed skill
                        if skill_counts:
                            top_skill = max(skill_counts, key=skill_counts.get)
                            st.metric("Most Developed", top_skill.replace('_', ' ').title())
                    with col4:
                        # Highest proficiency
                        proficiencies = [G.nodes[n]['proficiency'] for n in G.nodes()]
                        if proficiencies:
                            prof_levels = trajectory_builder.proficiency_levels
                            highest_idx = max(prof_levels.index(p) for p in proficiencies)
                            st.metric("Peak Proficiency", prof_levels[highest_idx])
                
                # Proficiency progression chart
                if len(reversed_sessions) > 1:
                    st.markdown("### Skill Development Over Time")
                    st.markdown("*Tracking proficiency progression across all sessions*")
                    
                    progression_fig = trajectory_builder.create_proficiency_progression_chart(session_list)
                    st.plotly_chart(progression_fig, use_container_width=True)
                
                # Session comparison
                if len(reversed_sessions) > 1:
                    st.markdown("### Learning Trajectory Comparison")
                    st.markdown("*Comparing skill development patterns across multiple sessions*")
                    
                    comparison_fig = trajectory_builder.compare_session_trajectories(reversed_sessions[:6])
                    st.plotly_chart(comparison_fig, use_container_width=True)
                
            except ImportError as e:
                st.error(f"Could not load session learning trajectory builder: {e}")
        else:
            st.warning("No session data available for trajectory extraction.")
    
    # Tab 3: Session Network (NEW - with linkography data)
    with tabs[2]:
        if session_list:
            render_session_network(session_list)
        else:
            st.warning("No linkography data available. Please run some test sessions first.")
    
    # Tab 4: Pattern Discovery (NEW - with linkography data)
    with tabs[3]:
        if session_list:
            render_pattern_analysis(session_list)
        else:
            st.warning("No linkography data available. Please run some test sessions first.")
    
    # Tab 5: Evolution Timeline (NEW - with linkography data)
    with tabs[4]:
        if session_list:
            render_evolution_timeline(session_list)
        else:
            st.warning("No linkography data available. Please run some test sessions first.")
    
    # Tab 6: Learning Metrics (NEW - comprehensive metrics dashboard)
    with tabs[5]:
        if session_list:
            render_learning_metrics(session_list)
        else:
            st.warning("No linkography data available. Please run some test sessions first.")


def render_session_network(sessions):
    """Render 3D network visualization of sessions"""
    st.markdown("### 3D Session Evolution Network")
    
    # Explanation
    st.markdown("""
    ### Understanding the Session Network
    This 3D network reveals how your design thinking evolves across sessions:
    
    - **Each node** represents a complete design session
    - **Node size** indicates complexity (number of design moves)
    - **Node color** shows learning progression (purple=low → orange=medium → coral=high)
    - **Connections** link sessions with similar design patterns
    - **Connection thickness** represents pattern similarity strength
    
    *Drag to rotate, scroll to zoom, click nodes for details!*
    """)
    
    # Create network graph
    G = nx.Graph()
    
    # Add nodes for each session with more meaningful metrics
    for i, session in enumerate(sessions[:20]):  # Limit to 20 sessions
        total_moves = sum(len(lg.moves) for lg in session.linkographs)
        total_links = sum(len(lg.links) for lg in session.linkographs)
        
        # Calculate a normalized learning score (0-1 scale)
        cognitive_metrics = session.cognitive_mapping.to_dict()
        learning_score = np.mean([
            cognitive_metrics.get('deep_thinking_engagement', 0),
            cognitive_metrics.get('knowledge_integration', 0),
            cognitive_metrics.get('learning_progression', 0)
        ])
        
        node_attrs = {
            'moves': total_moves,
            'links': total_links,
            'density': session.overall_metrics.link_density,
            'critical_ratio': session.overall_metrics.critical_move_ratio,
            'learning_score': learning_score,
            'phase_balance': session.overall_metrics.phase_balance,
            'patterns': len(session.patterns_detected),
            'session_id': session.session_id[:8]
        }
        G.add_node(f"S{i+1}", **node_attrs)
    
    # Add edges based on comprehensive similarity
    edge_data = []
    for i in range(len(sessions[:20])):
        for j in range(i+1, len(sessions[:20])):
            similarity = calculate_comprehensive_similarity(sessions[i], sessions[j])
            if similarity > 0.3:  # Lower threshold for more connections
                G.add_edge(f"S{i+1}", f"S{j+1}", weight=similarity)
                edge_data.append((i, j, similarity))
    
    # Create 3D layout using spring layout with 3D positions
    pos_2d = nx.spring_layout(G, k=3, iterations=50)
    pos_3d = {}
    for node, (x, y) in pos_2d.items():
        # Add z-coordinate based on learning progression
        z = G.nodes[node]['learning_score'] * 2 - 1  # Scale to -1 to 1
        pos_3d[node] = (x, y, z)
    
    # Create 3D edge traces
    edge_traces = []
    for edge in G.edges():
        x0, y0, z0 = pos_3d[edge[0]]
        x1, y1, z1 = pos_3d[edge[1]]
        weight = G[edge[0]][edge[1]]['weight']
        
        # Use thesis colors for edges based on weight
        if weight > 0.7:
            edge_color = THESIS_COLORS['primary_violet']
        elif weight > 0.5:
            edge_color = THESIS_COLORS['neutral_warm']
        else:
            edge_color = THESIS_COLORS['neutral_light']
        
        edge_trace = go.Scatter3d(
            x=[x0, x1, None],
            y=[y0, y1, None],
            z=[z0, z1, None],
            mode='lines',
            line=dict(
                width=weight*8,
                color=edge_color
            ),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create 3D node trace
    node_x = []
    node_y = []
    node_z = []
    node_text = []
    node_color = []
    node_size = []
    
    for node in G.nodes():
        x, y, z = pos_3d[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        
        attrs = G.nodes[node]
        
        # Create detailed hover text
        text = f"<b>{node} (ID: {attrs['session_id']})</b><br><br>"
        text += f"<b>Design Activity:</b><br>"
        text += f"• {attrs['moves']} design moves<br>"
        text += f"• {attrs['links']} connections<br>"
        text += f"• Link density: {attrs['density']:.2%}<br>"
        text += f"• Critical moves: {attrs['critical_ratio']:.1%}<br><br>"
        text += f"<b>Learning Metrics:</b><br>"
        text += f"• Overall score: {attrs['learning_score']:.2%}<br>"
        text += f"• Pattern types: {attrs['patterns']}<br><br>"
        text += f"<b>Phase Distribution:</b><br>"
        for phase, ratio in attrs['phase_balance'].items():
            text += f"• {phase.capitalize()}: {ratio:.1%}<br>"
        node_text.append(text)
        
        node_color.append(attrs['learning_score'])
        node_size.append(15 + attrs['moves']/3)  # Bigger nodes for better visibility
    
    # Create custom colorscale using thesis colors
    custom_colorscale = [
        [0.0, THESIS_COLORS['primary_purple']],    # Low learning
        [0.5, THESIS_COLORS['neutral_orange']],     # Medium learning
        [1.0, THESIS_COLORS['accent_coral']]        # High learning
    ]
    
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=list(G.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo='text',
        marker=dict(
            size=node_size,
            color=node_color,
            colorscale=custom_colorscale,
            colorbar=dict(
                title="Learning<br>Progress",
                tickmode="array",
                tickvals=[0, 0.5, 1],
                ticktext=["Low", "Medium", "High"],
                thickness=15,
                len=0.7,
                x=1.02
            ),
            line=dict(width=2, color=THESIS_COLORS['primary_dark']),
            sizemode='diameter'
        )
    )
    
    # Create figure with all traces
    fig = go.Figure(data=edge_traces + [node_trace])
    
    # Update layout for better 3D interaction
    fig.update_layout(
        title={
            'text': "3D Session Evolution Network",
            'font': {'size': 24, 'color': THESIS_COLORS['primary_dark']}
        },
        showlegend=False,
        scene=dict(
            xaxis=dict(showgrid=False, showticklabels=False, title=""),
            yaxis=dict(showgrid=False, showticklabels=False, title=""),
            zaxis=dict(showgrid=False, showticklabels=False, title="Learning Progress"),
            bgcolor='rgba(250, 248, 245, 0.1)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=700,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analysis metrics with better explanations
    st.markdown("### Network Insights")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sessions Analyzed", len(G.nodes()))
        st.caption("Total design sessions")
    
    with col2:
        st.metric("Pattern Connections", len(G.edges()))
        st.caption("Similar design approaches")
    
    with col3:
        if G.edges():
            avg_similarity = np.mean([G[e[0]][e[1]]['weight'] for e in G.edges()])
            st.metric("Avg Similarity", f"{avg_similarity:.1%}")
            st.caption("Pattern consistency")
        else:
            st.metric("Avg Similarity", "N/A")
            st.caption("No connections found")
    
    with col4:
        if len(sessions) > 0:
            avg_learning = np.mean([s.cognitive_mapping.learning_progression for s in sessions[:20]])
            st.metric("Avg Learning", f"{avg_learning:.1%}")
            st.caption("Overall progress")
        else:
            st.metric("Avg Learning", "N/A")
    
    # Interpretation guide
    st.markdown("""
    ### How to Interpret This Network:
    
    - **Isolated nodes** indicate unique design approaches that differ from other sessions
    - **Clusters** show sessions with similar design thinking patterns
    - **Height (Z-axis)** represents learning progress - higher nodes show better cognitive development
    - **Thick connections** indicate very similar design patterns between sessions
    """)


def render_pattern_analysis(sessions):
    """Render pattern analysis across sessions"""
    st.markdown("### Design Behavior Pattern Discovery")
    
    # Explanation of what patterns mean
    st.markdown("""
    This analysis reveals how your design thinking evolves by identifying recurring behavioral patterns
    in your problem-solving approach. These patterns help understand your cognitive style and learning progression.
    """)
    
    # Pattern explanations
    with st.expander("🔍 Understanding Design Patterns", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Chunk pattern with color indicator
            st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                       f'<div style="width: 20px; height: 20px; background-color: {THESIS_COLORS["primary_purple"]}; '
                       f'border-radius: 50%; margin-right: 10px;"></div>'
                       f'<b>Chunk Patterns (Focused Thinking)</b></div>', unsafe_allow_html=True)
            st.markdown("""
            - Indicates deep exploration of specific ideas
            - Shows systematic problem decomposition
            - Common in detailed design development
            """)
            
            # Web pattern with color indicator
            st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 20px;">'
                       f'<div style="width: 20px; height: 20px; background-color: {THESIS_COLORS["primary_violet"]}; '
                       f'border-radius: 50%; margin-right: 10px;"></div>'
                       f'<b>Web Patterns (Holistic Thinking)</b></div>', unsafe_allow_html=True)
            st.markdown("""
            - Reveals systems-level understanding
            - Shows ability to connect diverse concepts
            - Indicates mature design thinking
            """)
            
        with col2:
            # Sawtooth pattern with color indicator
            st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                       f'<div style="width: 20px; height: 20px; background-color: {THESIS_COLORS["neutral_warm"]}; '
                       f'border-radius: 50%; margin-right: 10px;"></div>'
                       f'<b>Sawtooth Patterns (Iterative Refinement)</b></div>', unsafe_allow_html=True)
            st.markdown("""
            - Shows cycles of exploration and consolidation
            - Indicates reflective practice
            - Common in experienced designers
            """)
            
            # Orphan pattern with color indicator
            st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 20px;">'
                       f'<div style="width: 20px; height: 20px; background-color: {THESIS_COLORS["accent_coral"]}; '
                       f'border-radius: 50%; margin-right: 10px;"></div>'
                       f'<b>Orphan Patterns (New Directions)</b></div>', unsafe_allow_html=True)
            st.markdown("""
            - Represents breakthrough moments or pivots
            - Can indicate creative leaps or confusion
            - Important for innovation tracking
            """)
    
    # Analyze patterns with behavioral interpretation
    pattern_data = []
    behavioral_insights = []
    
    for i, session in enumerate(sessions):
        patterns = {
            'chunk': 0, 'web': 0, 'sawtooth': 0, 'orphan': 0
        }
        
        for pattern in session.patterns_detected:
            if pattern.pattern_type in patterns:
                patterns[pattern.pattern_type] += pattern.strength
        
        pattern_data.append(patterns)
        
        # Generate behavioral insights
        total = sum(patterns.values())
        if total > 0:
            chunk_ratio = patterns['chunk'] / total
            web_ratio = patterns['web'] / total
            sawtooth_ratio = patterns['sawtooth'] / total
            orphan_ratio = patterns['orphan'] / total
            
            # Classify design behavior
            if web_ratio > 0.4:
                behavior = "Systems Thinker"
                description = "Strong ability to see connections and relationships"
            elif chunk_ratio > 0.4:
                behavior = "Detail-Oriented"
                description = "Focused on thorough exploration of specific aspects"
            elif sawtooth_ratio > 0.3:
                behavior = "Iterative Designer"
                description = "Balances exploration with refinement effectively"
            elif orphan_ratio > 0.3:
                behavior = "Exploratory"
                description = "High creativity but may need more structure"
            else:
                behavior = "Balanced"
                description = "Uses multiple thinking strategies adaptively"
            
            behavioral_insights.append({
                'session': i,
                'behavior': behavior,
                'description': description,
                'dominant_pattern': max(patterns, key=patterns.get)
            })
    
    # Create enhanced visualization
    df = pd.DataFrame(pattern_data)
    df['session'] = range(len(df))
    
    # Stacked area chart with better labels
    fig = go.Figure()
    
    colors = {
        'chunk': THESIS_COLORS['primary_purple'],
        'web': THESIS_COLORS['primary_violet'],
        'sawtooth': THESIS_COLORS['neutral_warm'],
        'orphan': THESIS_COLORS['accent_coral']
    }
    
    pattern_labels = {
        'chunk': 'Focused Thinking',
        'web': 'Holistic Thinking',
        'sawtooth': 'Iterative Refinement',
        'orphan': 'New Directions'
    }
    
    for pattern in ['chunk', 'web', 'sawtooth', 'orphan']:
        fig.add_trace(go.Scatter(
            x=df['session'],
            y=df[pattern],
            name=pattern_labels[pattern],
            mode='lines',
            stackgroup='one',
            fillcolor=colors[pattern],
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Session %{x}<br>' +
                         'Strength: %{y:.1f}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title="Design Thinking Pattern Evolution",
        xaxis_title="Session Number",
        yaxis_title="Pattern Strength",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Behavioral insights timeline
    if behavioral_insights:
        st.markdown("### Behavioral Pattern Timeline")
        
        # Create timeline visualization
        timeline_df = pd.DataFrame(behavioral_insights)
        
        fig_timeline = go.Figure()
        
        # Add markers for each session
        behavior_colors = {
            'Systems Thinker': THESIS_COLORS['primary_violet'],
            'Detail-Oriented': THESIS_COLORS['primary_purple'],
            'Iterative Designer': THESIS_COLORS['neutral_warm'],
            'Exploratory': THESIS_COLORS['accent_coral'],
            'Balanced': THESIS_COLORS['neutral_orange']
        }
        
        for behavior, color in behavior_colors.items():
            mask = timeline_df['behavior'] == behavior
            fig_timeline.add_trace(go.Scatter(
                x=timeline_df[mask]['session'],
                y=[behavior] * mask.sum(),
                mode='markers',
                marker=dict(size=15, color=color),
                name=behavior,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Session %{x}<br>' +
                             '<extra></extra>'
            ))
        
        fig_timeline.update_layout(
            title="Design Behavior Classification Over Time",
            xaxis_title="Session Number",
            yaxis_title="Behavioral Pattern",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Key insights and recommendations
    st.markdown("### Pattern-Based Insights")
    
    total_patterns = df[['chunk', 'web', 'sawtooth', 'orphan']].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Dominant pattern analysis
        dominant_pattern = total_patterns.idxmax()
        st.info(f"**Dominant Pattern**: {pattern_labels[dominant_pattern]}")
        st.metric("Pattern Strength", f"{total_patterns[dominant_pattern]:.1f}")
    
    with col2:
        # Pattern diversity
        pattern_diversity = len([p for p in ['chunk', 'web', 'sawtooth', 'orphan'] if total_patterns[p] > 0])
        st.info("**Pattern Diversity**")
        st.metric("Active Patterns", f"{pattern_diversity}/4")
    
    with col3:
        # Learning trajectory
        if len(behavioral_insights) > 1:
            behavior_changes = len(set(b['behavior'] for b in behavioral_insights))
            st.info("**Behavioral Flexibility**")
            st.metric("Behavior Types", behavior_changes)
    
    # Personalized recommendations
    st.markdown("### Personalized Recommendations")
    
    if total_patterns.sum() > 0:
        chunk_ratio = total_patterns['chunk'] / total_patterns.sum()
        web_ratio = total_patterns['web'] / total_patterns.sum()
        sawtooth_ratio = total_patterns['sawtooth'] / total_patterns.sum()
        orphan_ratio = total_patterns['orphan'] / total_patterns.sum()
        
        recommendations = []
        
        if orphan_ratio > 0.3:
            recommendations.append("🎯 **Improve Connectivity**: Your high rate of isolated ideas suggests potential for better integration. Try linking new concepts back to previous work.")
        
        if web_ratio < 0.2:
            recommendations.append("**Develop Systems Thinking**: Practice seeing relationships between different design elements. Ask 'how does this connect to...'")
        
        if chunk_ratio > 0.5:
            recommendations.append("🔄 **Balance Focus with Breadth**: While deep exploration is valuable, remember to step back and see the bigger picture.")
        
        if sawtooth_ratio < 0.1:
            recommendations.append("♻️ **Practice Iteration**: Develop a habit of revisiting and refining earlier ideas. Design is rarely linear.")
        
        if not recommendations:
            recommendations.append("✅ **Well-Balanced Approach**: Your pattern distribution shows good cognitive flexibility. Keep exploring different thinking strategies.")
        
        for rec in recommendations:
            st.markdown(rec)


def render_evolution_timeline(sessions):
    """Render cognitive evolution timeline"""
    st.markdown("### Cognitive Development Timeline")
    
    # Extract cognitive metrics over time
    timeline_data = []
    for i, session in enumerate(sessions):
        metrics = session.cognitive_mapping.to_dict()
        metrics['session'] = i
        timeline_data.append(metrics)
    
    df = pd.DataFrame(timeline_data)
    
    # Create multi-line chart
    fig = go.Figure()
    
    metric_colors = {
        'deep_thinking_engagement': THESIS_COLORS['primary_purple'],
        'cognitive_offloading_prevention': THESIS_COLORS['primary_violet'],
        'scaffolding_effectiveness': THESIS_COLORS['neutral_warm'],
        'knowledge_integration': THESIS_COLORS['neutral_orange'],
        'learning_progression': THESIS_COLORS['primary_rose'],
        'metacognitive_awareness': THESIS_COLORS['accent_coral']
    }
    
    for metric in metric_colors:
        if metric in df.columns:
            fig.add_trace(go.Scatter(
                x=df['session'],
                y=df[metric],
                name=metric.replace('_', ' ').title(),
                mode='lines+markers',
                line=dict(color=metric_colors[metric], width=2)
            ))
    
    fig.update_layout(
        title="Cognitive Metrics Evolution",
        xaxis_title="Session",
        yaxis_title="Score",
        yaxis=dict(range=[0, 1]),
        hovermode='x unified',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend analysis
    if len(df) > 1:
        st.markdown("### Trend Analysis")
        
        trends = {}
        for metric in metric_colors:
            if metric in df.columns:
                # Simple linear trend
                x = np.arange(len(df))
                y = df[metric].values
                z = np.polyfit(x, y, 1)
                trends[metric] = z[0]  # Slope
        
        # Sort by trend
        sorted_trends = sorted(trends.items(), key=lambda x: x[1], reverse=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Improving Metrics")
            for metric, trend in sorted_trends[:3]:
                if trend > 0:
                    st.success(f"{metric.replace('_', ' ').title()}: +{trend*10:.1%}/session")
        
        with col2:
            st.markdown("#### 📉 Declining Metrics")
            for metric, trend in sorted_trends[-3:]:
                if trend < 0:
                    st.warning(f"{metric.replace('_', ' ').title()}: {trend*10:.1%}/session")


def render_learning_metrics(sessions):
    """Render aggregated learning metrics"""
    st.markdown("### Learning Performance Overview")
    
    # Calculate aggregated metrics
    metrics_summary = {
        'Total Sessions': len(sessions),
        'Total Design Moves': sum(sum(len(lg.moves) for lg in s.linkographs) for s in sessions),
        'Total Links': sum(sum(len(lg.links) for lg in s.linkographs) for s in sessions),
        'Avg Link Density': np.mean([s.overall_metrics.link_density for s in sessions]),
        'Avg Critical Moves': np.mean([s.overall_metrics.critical_move_ratio for s in sessions]),
        'Avg Learning Progress': np.mean([s.cognitive_mapping.learning_progression for s in sessions])
    }
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, (metric, value) in enumerate(metrics_summary.items()):
        with cols[i % 3]:
            if isinstance(value, float):
                st.metric(metric, f"{value:.2f}")
            else:
                st.metric(metric, value)
    
    # Create radar chart for latest session
    if sessions:
        latest_session = sessions[-1]
        cognitive_metrics = latest_session.cognitive_mapping.to_dict()
        
        fig = go.Figure(data=go.Scatterpolar(
            r=list(cognitive_metrics.values()),
            theta=[m.replace('_', ' ').title() for m in cognitive_metrics.keys()],
            fill='toself',
            line_color=THESIS_COLORS['primary_violet']
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Latest Session Cognitive Profile",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("### Insights & Recommendations")
    
    avg_learning = metrics_summary['Avg Learning Progress']
    avg_density = metrics_summary['Avg Link Density']
    
    if avg_learning < 0.5:
        st.warning("**Low Learning Progress**: Consider increasing scaffolding support")
    else:
        st.success("**Good Learning Progress**: Students are showing positive development")
    
    if avg_density < 0.3:
        st.info("**Low Link Density**: Encourage more connection-making between concepts")
    elif avg_density > 0.7:
        st.info("**High Link Density**: Complex thinking patterns detected")


def calculate_session_similarity(session1, session2):
    """Calculate similarity between two sessions - DEPRECATED, use calculate_comprehensive_similarity"""
    return calculate_comprehensive_similarity(session1, session2)


def calculate_comprehensive_similarity(session1, session2):
    """Calculate comprehensive similarity between two sessions based on multiple factors"""
    similarities = []
    
    # 1. Cognitive metrics similarity (40% weight)
    metrics1 = session1.cognitive_mapping.to_dict()
    metrics2 = session2.cognitive_mapping.to_dict()
    
    cognitive_diffs = []
    for key in metrics1:
        if key in metrics2:
            # Normalize difference to 0-1
            diff = abs(metrics1[key] - metrics2[key])
            cognitive_diffs.append(diff)
    
    cognitive_similarity = 1.0 - (np.mean(cognitive_diffs) if cognitive_diffs else 1.0)
    similarities.append(('cognitive', cognitive_similarity, 0.4))
    
    # 2. Pattern similarity (30% weight)
    patterns1 = {p.pattern_type: p.strength for p in session1.patterns_detected}
    patterns2 = {p.pattern_type: p.strength for p in session2.patterns_detected}
    
    pattern_types = set(patterns1.keys()) | set(patterns2.keys())
    if pattern_types:
        pattern_diffs = []
        for ptype in pattern_types:
            p1 = patterns1.get(ptype, 0)
            p2 = patterns2.get(ptype, 0)
            pattern_diffs.append(abs(p1 - p2))
        pattern_similarity = 1.0 - (np.mean(pattern_diffs) / 2)  # Normalize by max diff of 2
    else:
        pattern_similarity = 0.5
    
    similarities.append(('pattern', pattern_similarity, 0.3))
    
    # 3. Structural similarity (20% weight)
    # Compare link density and critical move ratio
    density_diff = abs(session1.overall_metrics.link_density - session2.overall_metrics.link_density)
    critical_diff = abs(session1.overall_metrics.critical_move_ratio - session2.overall_metrics.critical_move_ratio)
    
    structural_similarity = 1.0 - ((density_diff + critical_diff) / 2)
    similarities.append(('structural', structural_similarity, 0.2))
    
    # 4. Phase balance similarity (10% weight)
    phase1 = session1.overall_metrics.phase_balance
    phase2 = session2.overall_metrics.phase_balance
    
    phase_diffs = []
    for phase in ['ideation', 'visualization', 'materialization']:
        p1 = phase1.get(phase, 0)
        p2 = phase2.get(phase, 0)
        phase_diffs.append(abs(p1 - p2))
    
    phase_similarity = 1.0 - (np.mean(phase_diffs) if phase_diffs else 1.0)
    similarities.append(('phase', phase_similarity, 0.1))
    
    # Calculate weighted average
    weighted_sum = sum(sim * weight for _, sim, weight in similarities)
    total_weight = sum(weight for _, _, weight in similarities)
    
    final_similarity = weighted_sum / total_weight if total_weight > 0 else 0
    
    return max(0, min(1, final_similarity))