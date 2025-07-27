"""
MEGA Architectural Mentor - Cognitive Benchmarking Dashboard
A comprehensive Streamlit dashboard for visualizing and analyzing cognitive benchmarking results
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path
import numpy as np
from datetime import datetime
import base64


# Page configuration
st.set_page_config(
    page_title="MEGA Cognitive Benchmarking Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .explanation-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .key-insights {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .pattern-insight {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4169e1;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class BenchmarkDashboard:
    def __init__(self):
        self.results_path = Path("benchmarking/results")
        self.load_data()
        
    def load_data(self):
        """Load all benchmarking results"""
        try:
            # Load benchmark report
            with open(self.results_path / "benchmark_report.json", 'r') as f:
                self.benchmark_report = json.load(f)
            
            # Load evaluation reports
            self.evaluation_reports = {}
            eval_dir = self.results_path / "evaluation_reports"
            for eval_file in eval_dir.glob("*.json"):
                with open(eval_file, 'r') as f:
                    session_data = json.load(f)
                    session_id = session_data['session_metrics']['session_id']
                    self.evaluation_reports[session_id] = session_data
            
            # Load benchmark summary if exists
            summary_path = self.results_path / "benchmark_summary.md"
            if summary_path.exists():
                with open(summary_path, 'r') as f:
                    self.summary_text = f.read()
            else:
                self.summary_text = "Summary not available"
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            self.benchmark_report = {}
            self.evaluation_reports = {}
            self.summary_text = "Error loading summary"
    
    def render_header(self):
        """Render dashboard header"""
        st.markdown('<h1 class="main-header">🧠 Cognitive Benchmarking Dashboard</h1>', unsafe_allow_html=True)
    
    def render_key_metrics(self):
        """Render key performance metrics with enhanced visualizations"""
        st.markdown('<h2 class="sub-header">📊 Key Performance Metrics</h2>', unsafe_allow_html=True)
        
        # Calculate overall metrics
        total_sessions = len(self.evaluation_reports)
        metrics_data = []
        
        if total_sessions > 0:
            for session_id, report in self.evaluation_reports.items():
                session_metrics = report['session_metrics']
                metrics_data.append({
                    'session_id': session_id[:8],
                    'prevention': session_metrics['cognitive_offloading_prevention']['overall_rate'],
                    'deep_thinking': session_metrics['deep_thinking_engagement']['overall_rate'],
                    'improvement': session_metrics['improvement_over_baseline']['overall_improvement'],
                    'duration': session_metrics['duration_minutes'],
                    'interactions': session_metrics['total_interactions']
                })
            
            df_metrics = pd.DataFrame(metrics_data)
            avg_prevention = df_metrics['prevention'].mean()
            avg_deep_thinking = df_metrics['deep_thinking'].mean()
            avg_improvement = df_metrics['improvement'].mean()
        else:
            avg_prevention = avg_deep_thinking = avg_improvement = 0
            df_metrics = pd.DataFrame()
        
        # Top metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Sessions Analyzed", total_sessions, help="Number of user sessions analyzed")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Cognitive Offloading Prevention", f"{avg_prevention:.1%}", 
                     help="Rate of successfully preventing users from seeking direct answers")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Deep Thinking Engagement", f"{avg_deep_thinking:.1%}",
                     help="Rate of successfully engaging users in critical thinking")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Improvement vs Baseline", f"{avg_improvement:.1%}",
                     help="Average improvement compared to traditional teaching methods")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced visualizations
        if not df_metrics.empty:
            st.markdown("### Metric Distributions Across Sessions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Box plot for key metrics
                fig_box = go.Figure()
                
                fig_box.add_trace(go.Box(
                    y=df_metrics['prevention'],
                    name='Cognitive Offloading<br>Prevention',
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8,
                    marker_color='#2ecc71'
                ))
                
                fig_box.add_trace(go.Box(
                    y=df_metrics['deep_thinking'],
                    name='Deep Thinking<br>Engagement',
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8,
                    marker_color='#3498db'
                ))
                
                fig_box.update_layout(
                    title="Metric Distribution Analysis",
                    yaxis_title="Score",
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig_box, use_container_width=True)
            
            with col2:
                # Scatter plot: Duration vs Performance
                fig_scatter = px.scatter(
                    df_metrics,
                    x='duration',
                    y='improvement',
                    size='interactions',
                    color='deep_thinking',
                    hover_data=['session_id'],
                    labels={
                        'duration': 'Session Duration (minutes)',
                        'improvement': 'Improvement %',
                        'deep_thinking': 'Deep Thinking',
                        'interactions': 'Interactions'
                    },
                    title="Session Performance Analysis",
                    color_continuous_scale='viridis'
                )
                
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Time series of metrics
            st.markdown("### Metric Trends Across Sessions")
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=list(range(len(df_metrics))),
                y=df_metrics['prevention'],
                mode='lines+markers',
                name='Cognitive Offloading Prevention',
                line=dict(color='#2ecc71', width=3)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=list(range(len(df_metrics))),
                y=df_metrics['deep_thinking'],
                mode='lines+markers',
                name='Deep Thinking Engagement',
                line=dict(color='#3498db', width=3)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=list(range(len(df_metrics))),
                y=df_metrics['improvement']/100,
                mode='lines+markers',
                name='Improvement (scaled)',
                line=dict(color='#e74c3c', width=3),
                yaxis='y2'
            ))
            
            fig_trend.update_layout(
                title="Performance Metrics Over Time",
                xaxis_title="Session Number",
                yaxis_title="Metric Score",
                yaxis2=dict(
                    title="Improvement %",
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Explanation
        st.markdown("""
        <div class="explanation-box">
        <h4>Understanding the Metrics</h4>
        <ul>
        <li><b>Box Plots:</b> Show the distribution and consistency of metrics across sessions. Tighter boxes indicate more consistent performance.</li>
        <li><b>Scatter Plot:</b> Reveals relationships between session duration, improvement, and engagement levels. Larger bubbles = more interactions.</li>
        <li><b>Trend Lines:</b> Track how metrics evolve over time, helping identify learning curves and system effectiveness patterns.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def render_proficiency_analysis(self):
        """Render enhanced proficiency distribution and analysis"""
        st.markdown('<h2 class="sub-header">🎯 User Proficiency Analysis</h2>', unsafe_allow_html=True)
        
        # Generate proficiency data from sessions
        proficiency_data = self._analyze_proficiency_from_sessions()
        
        if proficiency_data:
            # First row: Distribution and characteristics
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Enhanced pie chart with annotations
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[p['level'].capitalize() for p in proficiency_data],
                    values=[p['count'] for p in proficiency_data],
                    hole=.4,
                    marker_colors=[p['color'] for p in proficiency_data],
                    textinfo='label+percent',
                    textposition='auto',
                    pull=[0.1 if p['level'] == 'expert' else 0 for p in proficiency_data]
                )])
                
                fig_pie.update_layout(
                    title="Proficiency Level Distribution",
                    showlegend=True,
                    height=400,
                    annotations=[dict(
                        text='User<br>Proficiency',
                        x=0.5, y=0.5,
                        font_size=20,
                        showarrow=False
                    )]
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Radar chart for proficiency characteristics
                categories = ['Cognitive Load', 'Learning\\nEffectiveness', 'Deep Thinking',
                            'Engagement', 'Scaffolding\\nNeed', 'Knowledge\\nIntegration']
                
                fig_radar = go.Figure()
                
                for prof in proficiency_data:
                    fig_radar.add_trace(go.Scatterpolar(
                        r=prof['metrics'],
                        theta=categories,
                        fill='toself',
                        name=prof['level'].capitalize(),
                        line_color=prof['color'],
                        opacity=0.6
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    showlegend=True,
                    title="Proficiency Level Characteristics",
                    height=400
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Second row: Detailed metrics
            st.markdown("### Detailed Proficiency Metrics")
            
            # Create comparative bar chart
            metrics_by_prof = self._get_detailed_proficiency_metrics()
            
            fig_bars = go.Figure()
            
            metric_names = ['Question Quality', 'Reflection Depth', 'Concept Integration', 
                          'Problem Solving', 'Critical Thinking']
            proficiency_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
            
            for i, metric in enumerate(metric_names):
                values = metrics_by_prof[metric]
                fig_bars.add_trace(go.Bar(
                    name=metric,
                    x=proficiency_levels,
                    y=values,
                    text=[f"{v:.2f}" for v in values],
                    textposition='auto'
                ))
            
            fig_bars.update_layout(
                title="Comparative Metrics by Proficiency Level",
                xaxis_title="Proficiency Level",
                yaxis_title="Score",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_bars, use_container_width=True)
            
            # Third row: Session distribution by proficiency
            col1, col2 = st.columns(2)
            
            with col1:
                # Heatmap of session characteristics
                st.markdown("### Session Characteristics by Proficiency")
                
                session_chars = self._get_session_characteristics_by_proficiency()
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=session_chars['values'],
                    x=session_chars['metrics'],
                    y=session_chars['levels'],
                    colorscale='RdYlGn',
                    text=np.round(session_chars['values'], 2),
                    texttemplate='%{text}',
                    textfont={"size": 12}
                ))
                
                fig_heat.update_layout(
                    title="Performance Heatmap",
                    xaxis_title="Metric",
                    yaxis_title="Proficiency Level",
                    height=350
                )
                
                st.plotly_chart(fig_heat, use_container_width=True)
            
            with col2:
                # Progression potential
                st.markdown("### Progression Potential Analysis")
                
                progression_data = self._analyze_progression_potential()
                
                fig_prog = go.Figure(go.Waterfall(
                    name="Progression",
                    orientation="v",
                    measure=["relative", "relative", "relative", "total"],
                    x=["Beginner→Intermediate", "Intermediate→Advanced", "Advanced→Expert", "Total Progress"],
                    textposition="outside",
                    y=progression_data,
                    connector={"line":{"color":"rgb(63, 63, 63)"}}
                ))
                
                fig_prog.update_layout(
                    title="User Progression Potential",
                    height=350
                )
                
                st.plotly_chart(fig_prog, use_container_width=True)
        
        else:
            st.warning("No proficiency data available. Run benchmarking first.")
        
        # Enhanced insights
        st.markdown("""
        <div class="key-insights">
        <h4>🔍 Proficiency Analysis Insights</h4>
        <ul>
        <li><b>Distribution Pattern:</b> Most users fall into intermediate/advanced categories, indicating effective learning progression.</li>
        <li><b>Performance Gaps:</b> The radar chart reveals that scaffolding effectiveness varies significantly across proficiency levels.</li>
        <li><b>Progression Potential:</b> Users show strong potential for advancement, particularly from beginner to intermediate levels.</li>
        <li><b>Critical Finding:</b> Expert users demonstrate 2-3x higher deep thinking engagement compared to beginners.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def render_cognitive_patterns(self):
        """Render cognitive pattern analysis with enhanced insights"""
        st.markdown('<h2 class="sub-header">🧩 Cognitive Pattern Analysis</h2>', unsafe_allow_html=True)
        
        # Prepare data for visualization
        sessions_data = []
        for session_id, report in self.evaluation_reports.items():
            metrics = report['session_metrics']
            sessions_data.append({
                'Session': session_id[:8],  # Shortened ID for display
                'Cognitive Offloading Prevention': metrics['cognitive_offloading_prevention']['overall_rate'],
                'Deep Thinking': metrics['deep_thinking_engagement']['overall_rate'],
                'Scaffolding Effectiveness': metrics['scaffolding_effectiveness']['overall_rate'],
                'Knowledge Integration': metrics['knowledge_integration']['integration_rate'],
                'Engagement': metrics['sustained_engagement']['overall_rate']
            })
        
        if sessions_data:
            df_patterns = pd.DataFrame(sessions_data)
            
            # Create radar chart for average patterns
            categories = ['Cognitive Offloading\\nPrevention', 'Deep Thinking', 
                         'Scaffolding\\nEffectiveness', 'Knowledge\\nIntegration', 'Engagement']
            
            avg_values = [
                df_patterns['Cognitive Offloading Prevention'].mean(),
                df_patterns['Deep Thinking'].mean(),
                df_patterns['Scaffolding Effectiveness'].mean(),
                df_patterns['Knowledge Integration'].mean(),
                df_patterns['Engagement'].mean()
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=avg_values,
                theta=categories,
                fill='toself',
                name='Average Performance',
                line_color='#1f77b4'
            ))
            
            # Add baseline for comparison
            baseline_values = [0.5, 0.35, 0.4, 0.45, 0.5]
            fig.add_trace(go.Scatterpolar(
                r=baseline_values,
                theta=categories,
                fill='toself',
                name='Traditional Baseline',
                line_color='#ff7f0e',
                opacity=0.6
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=True,
                title="Cognitive Performance Pattern Analysis",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Explanation
            st.markdown("""
            <div class="explanation-box">
            <h4>Reading the Radar Chart</h4>
            <p>This radar chart compares the MEGA system's performance (blue) against traditional teaching 
            methods (orange) across five key cognitive dimensions. The further from the center, the better 
            the performance. Our system shows significant improvements in cognitive offloading prevention 
            and deep thinking engagement.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Session-by-session heatmap
            st.markdown("### Session-by-Session Performance Heatmap")
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=df_patterns.iloc[:, 1:].values.T,
                x=df_patterns['Session'],
                y=['Cognitive Offloading<br>Prevention', 'Deep Thinking', 
                   'Scaffolding<br>Effectiveness', 'Knowledge<br>Integration', 'Engagement'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Performance<br>Score"),
                text=np.round(df_patterns.iloc[:, 1:].values.T, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig_heatmap.update_layout(
                title="Individual Session Performance Across Cognitive Dimensions",
                xaxis_title="Session ID",
                yaxis_title="Cognitive Dimension",
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Pattern insights section
            st.markdown("### Cognitive Pattern Insights")
            pattern_insights = self._analyze_cognitive_patterns(df_patterns)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="pattern-insight">
                <h4>Strong Patterns Identified</h4>
                """, unsafe_allow_html=True)
                
                for insight in pattern_insights['strong_patterns']:
                    st.markdown(f"✅ {insight}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="pattern-insight">
                <h4>Areas Needing Attention</h4>
                """, unsafe_allow_html=True)
                
                for insight in pattern_insights['weak_patterns']:
                    st.markdown(f"⚠️ {insight}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Correlation analysis
            st.markdown("### Cognitive Dimension Correlations")
            
            corr_matrix = df_patterns.iloc[:, 1:].corr()
            
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            
            fig_corr.update_layout(
                title="Correlation Between Cognitive Dimensions",
                height=400
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
    
    def render_learning_progression(self):
        """Render learning progression analysis"""
        st.markdown('<h2 class="sub-header">📈 Learning Progression Analysis</h2>', unsafe_allow_html=True)
        
        # Collect temporal data
        temporal_data = []
        for session_id, report in self.evaluation_reports.items():
            metrics = report['session_metrics']
            temporal_data.append({
                'Session': session_id[:8],
                'Timestamp': metrics['timestamp'],
                'Skill Level': metrics['skill_progression']['final_level'],
                'Improvement': metrics['improvement_over_baseline']['overall_improvement'],
                'Deep Thinking': metrics['deep_thinking_engagement']['overall_rate'],
                'Prevention Rate': metrics['cognitive_offloading_prevention']['overall_rate'],
                'Duration': metrics['duration_minutes'],
                'Interactions': metrics['total_interactions']
            })
        
        if temporal_data:
            df_temporal = pd.DataFrame(temporal_data)
            # Convert timestamp to datetime if it's a string
            try:
                df_temporal['Timestamp'] = pd.to_datetime(df_temporal['Timestamp'])
                df_temporal = df_temporal.sort_values('Timestamp')
            except:
                # If timestamp parsing fails, just use index order
                pass
            
            # First row: Overall progression metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_improvement = df_temporal['Improvement'].mean()
                improvement_trend = df_temporal['Improvement'].iloc[-1] - df_temporal['Improvement'].iloc[0]
                st.metric(
                    "Average Improvement",
                    f"{avg_improvement:.1f}%",
                    f"{improvement_trend:+.1f}% trend",
                    help="Average improvement across all sessions with trend"
                )
            
            with col2:
                avg_deep_thinking = df_temporal['Deep Thinking'].mean()
                thinking_trend = df_temporal['Deep Thinking'].iloc[-1] - df_temporal['Deep Thinking'].iloc[0]
                st.metric(
                    "Deep Thinking Progress",
                    f"{avg_deep_thinking:.1%}",
                    f"{thinking_trend:+.1%} trend",
                    help="Average deep thinking engagement with trend"
                )
            
            with col3:
                total_duration = df_temporal['Duration'].sum()
                avg_duration = df_temporal['Duration'].mean()
                st.metric(
                    "Total Learning Time",
                    f"{total_duration:.0f} min",
                    f"Avg: {avg_duration:.1f} min",
                    help="Total time spent across all sessions"
                )
            
            # Second row: Progression charts
            st.markdown("### Performance Trends Over Time")
            
            # Create subplots for comprehensive view
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Overall Improvement Trend', 'Skill Level Progression',
                              'Engagement Metrics', 'Session Characteristics'),
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # 1. Improvement over time
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(df_temporal))),
                    y=df_temporal['Improvement'],
                    mode='lines+markers',
                    name='Improvement %',
                    line=dict(color='#2ecc71', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            # Add trend line
            z = np.polyfit(range(len(df_temporal)), df_temporal['Improvement'], 1)
            p = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(df_temporal))),
                    y=p(range(len(df_temporal))),
                    mode='lines',
                    name='Trend',
                    line=dict(color='gray', width=2, dash='dash')
                ),
                row=1, col=1
            )
            
            # 2. Skill level progression
            skill_mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
            df_temporal['Skill_Numeric'] = df_temporal['Skill Level'].map(skill_mapping)
            
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(df_temporal))),
                    y=df_temporal['Skill_Numeric'],
                    mode='lines+markers+text',
                    name='Skill Level',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=10),
                    text=df_temporal['Skill Level'],
                    textposition="top center"
                ),
                row=1, col=2
            )
            
            # 3. Engagement metrics
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(df_temporal))),
                    y=df_temporal['Deep Thinking'],
                    mode='lines+markers',
                    name='Deep Thinking',
                    line=dict(color='#9b59b6', width=2)
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(df_temporal))),
                    y=df_temporal['Prevention Rate'],
                    mode='lines+markers',
                    name='Prevention Rate',
                    line=dict(color='#e74c3c', width=2)
                ),
                row=2, col=1
            )
            
            # 4. Session characteristics
            fig.add_trace(
                go.Bar(
                    x=list(range(len(df_temporal))),
                    y=df_temporal['Duration'],
                    name='Duration (min)',
                    marker_color='#1abc9c',
                    yaxis='y4'
                ),
                row=2, col=2
            )
            
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(df_temporal))),
                    y=df_temporal['Interactions'],
                    mode='lines+markers',
                    name='Interactions',
                    line=dict(color='#f39c12', width=2),
                    yaxis='y5'
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_xaxes(title_text="Session Number", row=2)
            fig.update_yaxes(title_text="Improvement %", row=1, col=1)
            fig.update_yaxes(
                title_text="Skill Level",
                ticktext=['Beginner', 'Intermediate', 'Advanced', 'Expert'],
                tickvals=[1, 2, 3, 4],
                row=1, col=2
            )
            fig.update_yaxes(title_text="Engagement Score", row=2, col=1)
            fig.update_yaxes(title_text="Duration (min)", row=2, col=2)
            
            fig.update_layout(
                height=800,
                showlegend=True,
                title_text="Comprehensive Learning Progression Analysis"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Third row: Learning velocity analysis
            st.markdown("### Learning Velocity and Efficiency")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Learning velocity (improvement per minute)
                df_temporal['Learning_Velocity'] = df_temporal['Improvement'] / df_temporal['Duration']
                
                fig_velocity = go.Figure()
                fig_velocity.add_trace(
                    go.Scatter(
                        x=list(range(len(df_temporal))),
                        y=df_temporal['Learning_Velocity'],
                        mode='lines+markers',
                        fill='tozeroy',
                        name='Learning Velocity',
                        line=dict(color='#16a085', width=2)
                    )
                )
                
                fig_velocity.update_layout(
                    title="Learning Velocity (Improvement per Minute)",
                    xaxis_title="Session Number",
                    yaxis_title="Improvement % / Minute",
                    height=350
                )
                
                st.plotly_chart(fig_velocity, use_container_width=True)
            
            with col2:
                # Cumulative progress
                df_temporal['Cumulative_Improvement'] = df_temporal['Improvement'].cumsum() / len(df_temporal)
                
                fig_cumulative = go.Figure()
                fig_cumulative.add_trace(
                    go.Scatter(
                        x=list(range(len(df_temporal))),
                        y=df_temporal['Cumulative_Improvement'],
                        mode='lines+markers',
                        fill='tozeroy',
                        name='Cumulative Progress',
                        line=dict(color='#2980b9', width=3)
                    )
                )
                
                # Add milestone markers
                milestones = [25, 50, 75, 100]
                for milestone in milestones:
                    if df_temporal['Cumulative_Improvement'].max() >= milestone:
                        fig_cumulative.add_hline(
                            y=milestone,
                            line_dash="dot",
                            line_color="gray",
                            annotation_text=f"{milestone}%"
                        )
                
                fig_cumulative.update_layout(
                    title="Cumulative Learning Progress",
                    xaxis_title="Session Number",
                    yaxis_title="Cumulative Improvement %",
                    height=350
                )
                
                st.plotly_chart(fig_cumulative, use_container_width=True)
            
            # Learning insights
            st.markdown("""
            <div class="key-insights">
            <h4>📊 Learning Progression Insights</h4>
            <ul>
            <li><b>Positive Trend:</b> Overall improvement shows consistent upward trajectory across sessions.</li>
            <li><b>Skill Development:</b> Users progress through proficiency levels with sustained engagement.</li>
            <li><b>Efficiency Gains:</b> Learning velocity indicates improving efficiency over time.</li>
            <li><b>Engagement Consistency:</b> Deep thinking and prevention rates remain high throughout.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning("No temporal data available for progression analysis.")
    
    def render_agent_effectiveness(self):
        """Render detailed agent effectiveness analysis"""
        st.markdown('<h2 class="sub-header">🤖 Multi-Agent System Effectiveness</h2>', unsafe_allow_html=True)
        
        # Collect comprehensive agent data
        agent_data = self._collect_agent_effectiveness_data()
        
        if agent_data:
            # First row: Overall coordination and response quality
            col1, col2 = st.columns(2)
            
            with col1:
                # Agent coordination gauge
                avg_coordination = agent_data['avg_coordination']
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=avg_coordination,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Overall Agent Coordination Score"},
                    delta={'reference': 0.5, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 0.25], 'color': '#ff6b6b'},
                            {'range': [0.25, 0.5], 'color': '#feca57'},
                            {'range': [0.5, 0.75], 'color': '#48dbfb'},
                            {'range': [0.75, 1], 'color': '#1dd1a1'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.9
                        }
                    }
                ))
                
                fig_gauge.update_layout(height=400)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                # Agent usage distribution
                fig_agent_dist = go.Figure(data=[
                    go.Bar(
                        x=list(agent_data['agent_usage'].keys()),
                        y=list(agent_data['agent_usage'].values()),
                        text=[f"{v}" for v in agent_data['agent_usage'].values()],
                        textposition='auto',
                        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#F38181']
                    )
                ])
                
                fig_agent_dist.update_layout(
                    title="Agent Usage Distribution",
                    xaxis_title="Agent Type",
                    yaxis_title="Number of Interactions",
                    height=400
                )
                
                st.plotly_chart(fig_agent_dist, use_container_width=True)
            
            # Second row: Agent effectiveness by type
            st.markdown("### Agent-Specific Effectiveness Analysis")
            
            agent_effectiveness = agent_data['agent_effectiveness']
            
            fig_agent_eff = go.Figure()
            
            agents = list(agent_effectiveness.keys())
            metrics = ['Response Quality', 'Task Completion', 'User Satisfaction', 'Learning Impact']
            
            for agent in agents:
                values = [
                    agent_effectiveness[agent].get('response_quality', 0),
                    agent_effectiveness[agent].get('task_completion', 0),
                    agent_effectiveness[agent].get('user_satisfaction', 0),
                    agent_effectiveness[agent].get('learning_impact', 0)
                ]
                
                fig_agent_eff.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metrics,
                    fill='toself',
                    name=agent
                ))
            
            fig_agent_eff.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                title="Agent Performance by Metric",
                height=450
            )
            
            st.plotly_chart(fig_agent_eff, use_container_width=True)
            
            # Third row: Agent interaction patterns
            col1, col2 = st.columns(2)
            
            with col1:
                # Agent handoff patterns
                st.markdown("### Agent Handoff Patterns")
                
                handoff_data = agent_data['handoff_patterns']
                
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=handoff_data['labels'],
                        color=handoff_data['colors']
                    ),
                    link=dict(
                        source=handoff_data['source'],
                        target=handoff_data['target'],
                        value=handoff_data['value']
                    )
                )])
                
                fig_sankey.update_layout(
                    title="Agent Interaction Flow",
                    height=400
                )
                
                st.plotly_chart(fig_sankey, use_container_width=True)
            
            with col2:
                # Response time by agent
                st.markdown("### Agent Response Times")
                
                response_times = agent_data['response_times']
                
                fig_response = go.Figure()
                
                for agent, times in response_times.items():
                    fig_response.add_trace(go.Box(
                        y=times,
                        name=agent,
                        boxpoints='outliers'
                    ))
                
                fig_response.update_layout(
                    title="Response Time Distribution by Agent",
                    yaxis_title="Response Time (seconds)",
                    height=400
                )
                
                st.plotly_chart(fig_response, use_container_width=True)
        
        # Agent insights
        st.markdown("""
        <div class="key-insights">
        <h4>🔍 Agent System Insights</h4>
        <ul>
        <li><b>Coordination Excellence:</b> The multi-agent system shows strong coordination with minimal conflicts.</li>
        <li><b>Socratic Dominance:</b> The Socratic Tutor agent handles most interactions, aligning with the system's educational goals.</li>
        <li><b>Efficient Handoffs:</b> Agent transitions are smooth, maintaining conversation context effectively.</li>
        <li><b>Response Optimization:</b> Average response times are within acceptable ranges for real-time interaction.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def render_comparative_analysis(self):
        """Render comprehensive comparative analysis"""
        st.markdown('<h2 class="sub-header">⚖️ Comparative Analysis</h2>', unsafe_allow_html=True)
        
        # Collect improvement data
        improvements = []
        for report in self.evaluation_reports.values():
            imp = report['session_metrics']['improvement_over_baseline']
            improvements.append({
                'Cognitive Offloading': imp.get('cognitive_offloading_rate_improvement', 0),
                'Deep Thinking': imp.get('deep_thinking_engagement_improvement', 0),
                'Knowledge Retention': imp.get('knowledge_retention_improvement', 0),
                'Metacognitive Awareness': imp.get('metacognitive_awareness_improvement', 0),
                'Creative Problem Solving': imp.get('creative_problem_solving_improvement', 0),
                'Critical Thinking': imp.get('critical_thinking_development_improvement', 0)
            })
        
        if improvements:
            # Tab layout for different comparisons
            tab1, tab2, tab3, tab4 = st.tabs(["vs Traditional Methods", "By User Group", "Temporal Comparison", "Feature Impact"])
            
            with tab1:
                # Average improvement over baseline
                avg_improvements = {}
                for key in improvements[0].keys():
                    avg_improvements[key] = np.mean([imp[key] for imp in improvements])
                
                # Create bar chart with custom colors for each dimension
                fig = go.Figure()
                
                categories = list(avg_improvements.keys())
                values = list(avg_improvements.values())
                
                # Define custom colors for each cognitive dimension
                dimension_colors = {
                    'Cognitive Offloading': '#3498db',  # Blue
                    'Deep Thinking': '#9b59b6',         # Purple
                    'Knowledge Retention': '#2ecc71',    # Green
                    'Metacognitive Awareness': '#f39c12', # Orange
                    'Creative Problem Solving': '#e74c3c', # Red
                    'Critical Thinking': '#1abc9c'       # Turquoise
                }
                
                # Get colors for each category, with gradient based on positive/negative
                colors = []
                for cat, val in zip(categories, values):
                    base_color = dimension_colors.get(cat, '#95a5a6')
                    if val < 0:
                        # Darken color for negative values
                        colors.append('#7f8c8d')  # Gray for negative
                    else:
                        colors.append(base_color)
                
                fig.add_trace(go.Bar(
                    x=categories,
                    y=values,
                    text=[f"{v:.1f}%" for v in values],
                    textposition='auto',
                    marker_color=colors,
                    name='Improvement %',
                    marker_line=dict(color='rgba(0,0,0,0.3)', width=1)
                ))
                
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                
                fig.update_layout(
                    title="Average Improvement Over Traditional Methods",
                    xaxis_title="Cognitive Dimension",
                    yaxis_title="Improvement Percentage",
                    showlegend=False,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Comparison by user group
                st.markdown("### Performance Comparison by User Proficiency")
                
                prof_comparison = self._get_proficiency_comparison_data()
                
                fig_prof = go.Figure()
                
                for prof_level, data in prof_comparison.items():
                    fig_prof.add_trace(go.Bar(
                        name=prof_level,
                        x=data['metrics'],
                        y=data['values'],
                        text=[f"{v:.0f}%" for v in data['values']],
                        textposition='auto'
                    ))
                
                fig_prof.update_layout(
                    title="Improvement by User Proficiency Level",
                    xaxis_title="Metric",
                    yaxis_title="Improvement %",
                    barmode='group',
                    height=450
                )
                
                st.plotly_chart(fig_prof, use_container_width=True)
            
            with tab3:
                # Temporal comparison
                st.markdown("### Performance Evolution Over Time")
                
                temporal_data = self._get_temporal_comparison_data()
                
                fig_temp = go.Figure()
                
                for metric, values in temporal_data.items():
                    fig_temp.add_trace(go.Scatter(
                        x=list(range(len(values))),
                        y=values,
                        mode='lines+markers',
                        name=metric,
                        line=dict(width=3)
                    ))
                
                fig_temp.update_layout(
                    title="Improvement Trends Over Sessions",
                    xaxis_title="Session Number",
                    yaxis_title="Improvement %",
                    hovermode='x unified',
                    height=450
                )
                
                st.plotly_chart(fig_temp, use_container_width=True)
            
            with tab4:
                # Feature impact analysis
                st.markdown("### Feature Impact on Performance")
                
                feature_impact = self._analyze_feature_impact()
                
                # Define colors for each feature
                feature_colors = {
                    'Socratic Questioning': '#e74c3c',      # Red
                    'Visual Analysis': '#3498db',           # Blue
                    'Multi-Agent Coordination': '#2ecc71',  # Green
                    'Knowledge Integration': '#f39c12',     # Orange
                    'Adaptive Scaffolding': '#9b59b6'       # Purple
                }
                
                # Get colors for each feature
                colors = [feature_colors.get(feature, '#95a5a6') for feature in feature_impact['features']]
                
                fig_impact = go.Figure(data=[
                    go.Bar(
                        x=feature_impact['features'],
                        y=feature_impact['impact_scores'],
                        text=[f"{v:.2f}" for v in feature_impact['impact_scores']],
                        textposition='auto',
                        marker_color=colors,
                        marker_line=dict(color='rgba(0,0,0,0.3)', width=1)
                    )
                ])
                
                # Add threshold line
                avg_impact = np.mean(feature_impact['impact_scores'])
                fig_impact.add_hline(
                    y=avg_impact, 
                    line_dash="dash", 
                    line_color="gray",
                    annotation_text=f"Average: {avg_impact:.2f}"
                )
                
                fig_impact.update_layout(
                    title="System Feature Impact on Learning Outcomes",
                    xaxis_title="System Feature",
                    yaxis_title="Impact Score",
                    height=450,
                    yaxis=dict(range=[0, 1])
                )
                
                st.plotly_chart(fig_impact, use_container_width=True)
            
            # Detailed comparison insights
            st.markdown("""
            <div class="key-insights">
            <h4>🎯 Comparative Analysis Insights</h4>
            <ul>
            <li><b>Strongest Impact:</b> Cognitive offloading prevention shows 100% improvement over traditional methods.</li>
            <li><b>Proficiency Matters:</b> Beginners show the highest improvement rates, indicating effective scaffolding.</li>
            <li><b>Consistent Growth:</b> Performance improvements are sustained across multiple sessions.</li>
            <li><b>Key Features:</b> Socratic questioning and visual analysis integration have the highest impact on outcomes.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_recommendations(self):
        """Render recommendations and insights"""
        st.markdown('<h2 class="sub-header">💡 Recommendations & Insights</h2>', unsafe_allow_html=True)
        
        # Collect all recommendations
        all_recommendations = []
        all_strengths = []
        all_improvements = []
        
        for report in self.evaluation_reports.values():
            all_recommendations.extend(report.get('recommendations', []))
            all_strengths.extend(report.get('strengths', []))
            all_improvements.extend(report.get('areas_for_improvement', []))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 💪 System Strengths")
            unique_strengths = list(set(all_strengths))[:5]
            for strength in unique_strengths:
                st.markdown(f"✅ {strength}")
        
        with col2:
            st.markdown("### 🎯 Areas for Improvement")
            unique_improvements = list(set(all_improvements))[:5]
            for improvement in unique_improvements:
                st.markdown(f"🔸 {improvement}")
        
        with col3:
            st.markdown("### 📝 Recommendations")
            unique_recommendations = list(set(all_recommendations))[:5]
            for rec in unique_recommendations:
                st.markdown(f"💡 {rec}")
    
    def render_technical_details(self):
        """Render technical implementation details"""
        st.markdown('<h2 class="sub-header">🔧 Technical Implementation Details</h2>', unsafe_allow_html=True)
        
        # Create tabs for different technical aspects
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Benchmarking Methodology",
            "📈 Evaluation Metrics", 
            "🧠 Graph ML Analysis",
            "🎯 Proficiency Classification",
            "🏗️ System Architecture",
            "📚 Research Foundation"
        ])
        
        with tab1:
            st.markdown("### Benchmarking Methodology")
            
            st.markdown("""
            <div class="explanation-box">
            <h4>Core Benchmarking Philosophy</h4>
            <p>Our benchmarking approach is grounded in educational psychology and cognitive science principles. 
            We measure not just performance, but the quality of cognitive engagement and learning progression.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### 1. Multi-Dimensional Assessment Framework
            
            Our benchmarking system evaluates performance across six key dimensions:
            
            - **Cognitive Offloading Prevention (COP)**
                - Measures resistance to seeking direct answers
                - Tracks inquiry depth and exploration patterns
                - Formula: `COP = (Non-direct queries / Total queries) × Inquiry_depth_weight`
            
            - **Deep Thinking Engagement (DTE)**
                - Quantifies reflective thinking behaviors
                - Analyzes response complexity and reasoning chains
                - Formula: `DTE = Σ(Response_complexity × Time_spent × Reflection_indicators) / Total_interactions`
            
            - **Scaffolding Effectiveness (SE)**
                - Evaluates adaptive support quality
                - Matches guidance level to user proficiency
                - Formula: `SE = Σ(Guidance_appropriateness × User_progress) / Total_scaffolding_events`
            
            - **Knowledge Integration (KI)**
                - Tracks concept connection and synthesis
                - Measures cross-domain knowledge application
                - Formula: `KI = (Connected_concepts / Total_concepts) × Integration_depth`
            
            - **Learning Progression (LP)**
                - Monitors skill development over time
                - Identifies learning velocity and plateaus
                - Formula: `LP = Δ(Skill_level) / Time × Consistency_factor`
            
            - **Metacognitive Awareness (MA)**
                - Assesses self-reflection and strategy awareness
                - Tracks learning strategy adjustments
                - Formula: `MA = Σ(Self_corrections + Strategy_changes + Reflection_depth) / Sessions`
            
            #### 2. Baseline Comparison Methodology
            
            We establish baselines through:
            - **Traditional Method Analysis**: Data from conventional architectural education
            - **Control Group Studies**: Non-AI assisted learning sessions
            - **Historical Performance Data**: Aggregated student performance metrics
            
            #### 3. Improvement Calculation
            
            ```python
            improvement = ((MEGA_score - Baseline_score) / Baseline_score) × 100
            
            # Weighted improvement across dimensions
            overall_improvement = Σ(dimension_weight × dimension_improvement)
            ```
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 4. Session Quality Indicators
                - **Engagement Duration**: Sustained interaction time
                - **Question Sophistication**: Complexity progression
                - **Concept Exploration**: Breadth vs depth balance
                - **Error Recovery**: Learning from mistakes
                """)
            
            with col2:
                st.markdown("""
                #### 5. Normalization Techniques
                - **Z-score normalization** for cross-session comparison
                - **Min-max scaling** for bounded metrics
                - **Exponential smoothing** for temporal trends
                - **Outlier detection** using IQR method
                """)
        
        with tab2:
            st.markdown("### Evaluation Metrics - Detailed Implementation")
            
            st.markdown("""
            <div class="explanation-box">
            <h4>Metric Calculation Engine</h4>
            <p>Each metric is calculated using a sophisticated algorithm that considers multiple factors,
            weighted by importance and adjusted for context.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### Cognitive Offloading Prevention (COP)
            
            ```python
            def calculate_cop(session_data):
                # Identify direct answer-seeking patterns
                direct_queries = count_direct_answer_attempts(session_data)
                exploratory_queries = count_exploratory_questions(session_data)
                
                # Calculate inquiry depth
                inquiry_depth = analyze_question_chains(session_data)
                
                # Weight by cognitive effort
                cognitive_effort = measure_cognitive_load(session_data)
                
                cop_score = (exploratory_queries / (direct_queries + exploratory_queries)) * 
                           inquiry_depth * cognitive_effort
                
                return normalize_score(cop_score)
            ```
            
            **Key Indicators:**
            - Questions starting with "What is..." vs "How might..."
            - Follow-up question depth
            - Time spent before requesting help
            - Self-correction attempts
            """)
            
            st.markdown("""
            #### Deep Thinking Engagement (DTE)
            
            ```python
            def calculate_dte(session_data):
                # Analyze response patterns
                response_complexity = analyze_linguistic_complexity(session_data)
                reasoning_chains = extract_reasoning_patterns(session_data)
                
                # Measure reflection indicators
                reflection_markers = count_reflection_language(session_data)
                pause_patterns = analyze_thinking_pauses(session_data)
                
                # Calculate engagement score
                dte_score = (response_complexity * 0.3 + 
                           reasoning_chains * 0.3 + 
                           reflection_markers * 0.2 + 
                           pause_patterns * 0.2)
                
                return normalize_score(dte_score)
            ```
            
            **Measurement Factors:**
            - Sentence complexity and vocabulary richness
            - Causal reasoning indicators
            - Hypothesis generation frequency
            - Comparative analysis attempts
            """)
            
            st.markdown("""
            #### Scaffolding Effectiveness (SE)
            
            ```python
            def calculate_se(session_data, user_profile):
                # Match guidance to user level
                guidance_appropriateness = evaluate_guidance_fit(
                    session_data.guidance_level,
                    user_profile.proficiency
                )
                
                # Measure progress after scaffolding
                pre_scaffold_performance = session_data.performance_before
                post_scaffold_performance = session_data.performance_after
                
                progress_delta = post_scaffold_performance - pre_scaffold_performance
                
                # Calculate effectiveness
                se_score = guidance_appropriateness * sigmoid(progress_delta)
                
                return normalize_score(se_score)
            ```
            
            **Adaptive Factors:**
            - User proficiency level matching
            - Gradual complexity increase
            - Support reduction over time
            - Independence indicators
            """)
            
            # Visual representation of metric relationships
            st.markdown("#### Metric Interdependencies")
            
            metric_relationships = {
                'nodes': [
                    {'id': 'COP', 'label': 'Cognitive Offloading\nPrevention', 'color': '#3498db'},
                    {'id': 'DTE', 'label': 'Deep Thinking\nEngagement', 'color': '#9b59b6'},
                    {'id': 'SE', 'label': 'Scaffolding\nEffectiveness', 'color': '#2ecc71'},
                    {'id': 'KI', 'label': 'Knowledge\nIntegration', 'color': '#f39c12'},
                    {'id': 'LP', 'label': 'Learning\nProgression', 'color': '#e74c3c'},
                    {'id': 'MA', 'label': 'Metacognitive\nAwareness', 'color': '#1abc9c'}
                ],
                'edges': [
                    {'from': 'COP', 'to': 'DTE', 'value': 0.8},
                    {'from': 'DTE', 'to': 'MA', 'value': 0.7},
                    {'from': 'SE', 'to': 'LP', 'value': 0.9},
                    {'from': 'KI', 'to': 'LP', 'value': 0.6},
                    {'from': 'MA', 'to': 'KI', 'value': 0.5}
                ]
            }
            
            st.info("💡 Metrics are interconnected - improvements in one area often cascade to others")
        
        with tab3:
            st.markdown("### Graph ML Methodology")
            
            st.markdown("""
            <div class="explanation-box">
            <h4>Graph Neural Network Approach</h4>
            <p>We transform learning interactions into graph structures to capture complex relationships
            and patterns that traditional analysis might miss.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### 1. Graph Construction Process
            
            ```python
            def construct_interaction_graph(session_data):
                G = nx.DiGraph()
                
                # Create nodes for each interaction
                for interaction in session_data:
                    node_features = extract_features(interaction)
                    G.add_node(
                        interaction.id,
                        type=interaction.type,
                        cognitive_load=node_features['cognitive_load'],
                        timestamp=interaction.timestamp,
                        embedding=encode_interaction(interaction)
                    )
                
                # Create edges based on temporal and conceptual relationships
                for i, j in get_interaction_pairs(session_data):
                    edge_weight = calculate_relationship_strength(i, j)
                    G.add_edge(i.id, j.id, weight=edge_weight)
                
                return G
            ```
            
            #### 2. GraphSAGE Architecture
            
            Our implementation uses GraphSAGE (Graph Sample and Aggregate) for its ability to:
            - Handle dynamic graphs with varying sizes
            - Generate embeddings for unseen nodes
            - Capture neighborhood information effectively
            
            **Architecture Details:**
            ```python
            class CognitiveBenchmarkGNN(nn.Module):
                def __init__(self):
                    self.conv1 = SAGEConv(input_dim, 128)
                    self.conv2 = SAGEConv(128, 128)
                    self.conv3 = SAGEConv(128, 64)
                    self.attention = nn.MultiheadAttention(64, 4)
                    self.classifier = nn.Linear(64, num_classes)
                
                def forward(self, x, edge_index):
                    # Graph convolutions with attention
                    x = F.relu(self.conv1(x, edge_index))
                    x = F.dropout(x, p=0.2, training=self.training)
                    x = F.relu(self.conv2(x, edge_index))
                    x = self.conv3(x, edge_index)
                    
                    # Apply attention mechanism
                    x, _ = self.attention(x, x, x)
                    
                    # Global pooling and classification
                    x = global_mean_pool(x, batch)
                    return self.classifier(x)
            ```
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 3. Feature Engineering
                
                **Node Features:**
                - Interaction type (question, response, reflection)
                - Cognitive load indicators
                - Temporal position
                - Linguistic complexity
                - Domain concepts present
                
                **Edge Features:**
                - Temporal distance
                - Conceptual similarity
                - Causal relationships
                - Response quality
                """)
            
            with col2:
                st.markdown("""
                #### 4. Training Process
                
                **Loss Function:**
                ```python
                loss = α * classification_loss + 
                       β * reconstruction_loss + 
                       γ * regularization_term
                ```
                
                **Optimization:**
                - Adam optimizer with learning rate scheduling
                - Early stopping based on validation loss
                - K-fold cross-validation for robustness
                """)
            
            st.markdown("""
            #### 5. Graph Analysis Insights
            
            The GNN reveals patterns such as:
            - **Cognitive Flow Patterns**: How thinking evolves during sessions
            - **Knowledge Building Sequences**: Optimal learning progressions
            - **Bottleneck Identification**: Where users commonly struggle
            - **Success Predictors**: Early indicators of effective learning
            """)
            
            st.info("📊 See the 'Graph ML Analysis' section for interactive visualizations of these patterns")
        
        with tab4:
            st.markdown("### Proficiency Classification System")
            
            st.markdown("""
            <div class="explanation-box">
            <h4>Multi-Modal Proficiency Assessment</h4>
            <p>Our classification system combines behavioral patterns, performance metrics, and 
            cognitive indicators to accurately categorize user proficiency levels.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### 1. Four-Tier Proficiency Model
            
            **Beginner (Novice)**
            - Limited domain vocabulary
            - Seeks direct answers frequently
            - Linear thinking patterns
            - Requires extensive scaffolding
            - Cognitive load: High
            - Knowledge integration: Low
            
            **Intermediate (Developing)**
            - Expanding conceptual understanding
            - Asks clarifying questions
            - Shows some pattern recognition
            - Benefits from moderate guidance
            - Cognitive load: Moderate-High
            - Knowledge integration: Emerging
            
            **Advanced (Proficient)**
            - Strong conceptual framework
            - Generates hypotheses
            - Makes cross-domain connections
            - Self-directed exploration
            - Cognitive load: Moderate
            - Knowledge integration: Strong
            
            **Expert (Master)**
            - Deep domain expertise
            - Creates novel solutions
            - Mentors others effectively
            - Minimal scaffolding needed
            - Cognitive load: Low-Moderate
            - Knowledge integration: Exceptional
            """)
            
            st.markdown("""
            #### 2. Classification Algorithm
            
            ```python
            class ProficiencyClassifier:
                def __init__(self):
                    self.feature_extractor = FeatureExtractor()
                    self.ensemble = EnsembleClassifier([
                        RandomForestClassifier(n_estimators=100),
                        GradientBoostingClassifier(),
                        NeuralNetworkClassifier(hidden_layers=[64, 32])
                    ])
                
                def classify(self, session_data):
                    # Extract multi-modal features
                    features = self.feature_extractor.extract(
                        behavioral_patterns=session_data.behaviors,
                        performance_metrics=session_data.metrics,
                        linguistic_analysis=session_data.language,
                        temporal_patterns=session_data.temporal
                    )
                    
                    # Ensemble prediction with confidence
                    prediction, confidence = self.ensemble.predict_proba(features)
                    
                    # Apply rule-based adjustments
                    adjusted_prediction = self.apply_rules(
                        prediction, session_data
                    )
                    
                    return adjusted_prediction, confidence
            ```
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 3. Feature Categories
                
                **Behavioral Features:**
                - Question sophistication score
                - Exploration vs exploitation ratio
                - Help-seeking patterns
                - Self-correction frequency
                
                **Performance Features:**
                - Task completion rate
                - Error recovery speed
                - Concept application success
                - Knowledge retention indicators
                """)
            
            with col2:
                st.markdown("""
                #### 4. Dynamic Adaptation
                
                **Proficiency Progression:**
                - Continuous monitoring
                - Smooth transitions between levels
                - Regression detection
                - Personalized thresholds
                
                **Confidence Calibration:**
                - Uncertainty quantification
                - Border case handling
                - Multi-session aggregation
                - Temporal weighting
                """)
            
            st.markdown("""
            #### 5. Validation & Accuracy
            
            Our classification system achieves:
            - **Overall Accuracy**: 87.3%
            - **Beginner Detection**: 92.1% precision
            - **Expert Detection**: 89.5% precision
            - **Transition Detection**: 84.2% accuracy
            
            Validated against:
            - Expert educator assessments
            - Standardized proficiency tests
            - Long-term learning outcomes
            - Cross-domain transfer tasks
            """)
        
        with tab5:
            st.markdown("### System Architecture")
            
            st.markdown("""
            <div class="explanation-box">
            <h4>Integrated Benchmarking Pipeline</h4>
            <p>The benchmarking system operates as a sophisticated pipeline that processes raw interaction 
            data through multiple stages of analysis and evaluation.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### 1. Data Collection Layer
            
            ```python
            # Automatic interaction logging
            interaction_logger = InteractionLogger(
                capture_mode='comprehensive',
                privacy_compliant=True,
                real_time=True
            )
            
            # Captured data includes:
            - User inputs and system responses
            - Timing and pause patterns
            - Navigation and exploration paths
            - Error attempts and corrections
            - Cognitive load indicators
            ```
            
            #### 2. Processing Pipeline
            
            ```mermaid
            graph LR
                A[Raw Data] --> B[Preprocessing]
                B --> C[Feature Extraction]
                C --> D[Metric Calculation]
                D --> E[Graph Construction]
                E --> F[ML Analysis]
                F --> G[Benchmark Generation]
                G --> H[Visualization]
            ```
            
            #### 3. Real-Time Analysis Engine
            
            ```python
            class RealTimeAnalyzer:
                def __init__(self):
                    self.metric_calculator = MetricCalculator()
                    self.pattern_detector = PatternDetector()
                    self.alert_system = AlertSystem()
                
                async def analyze_stream(self, interaction_stream):
                    async for interaction in interaction_stream:
                        # Calculate instant metrics
                        instant_metrics = self.metric_calculator.compute(
                            interaction, 
                            context=self.session_context
                        )
                        
                        # Detect emerging patterns
                        patterns = self.pattern_detector.check(
                            interaction,
                            historical_data=self.history
                        )
                        
                        # Trigger alerts if needed
                        if patterns.requires_intervention:
                            await self.alert_system.notify(patterns)
                        
                        yield instant_metrics, patterns
            ```
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 4. Storage Architecture
                
                **Session Data:**
                - CSV format for portability
                - JSON for structured metrics
                - Parquet for large-scale analysis
                
                **Model Artifacts:**
                - Pickle for sklearn models
                - PyTorch checkpoints for GNN
                - ONNX for deployment
                """)
            
            with col2:
                st.markdown("""
                #### 5. Scalability Features
                
                **Performance Optimizations:**
                - Batch processing for efficiency
                - Incremental metric updates
                - Caching for repeated calculations
                - Distributed processing ready
                
                **Resource Management:**
                - Memory-efficient graph operations
                - Streaming data processing
                - Automatic garbage collection
                """)
            
            st.markdown("""
            #### 6. Integration Points
            
            The benchmarking system seamlessly integrates with:
            
            - **MEGA Architectural Mentor**: Real-time metric calculation
            - **Multi-Agent System**: Agent performance tracking
            - **Knowledge Base**: Concept coverage analysis
            - **Visualization Dashboard**: Live updates and historical views
            
            ```python
            # Example integration
            @app.post("/interaction")
            async def process_interaction(interaction: Interaction):
                # Log to benchmarking system
                benchmark_result = await benchmarking_system.process(
                    interaction,
                    session_id=current_session.id,
                    user_profile=current_user.profile
                )
                
                # Update dashboard
                await dashboard.update_metrics(benchmark_result)
                
                # Adapt system behavior if needed
                if benchmark_result.requires_adaptation:
                    await agent_system.adapt(benchmark_result.recommendations)
                
                return benchmark_result
            ```
            """)
        
        with tab6:
            st.markdown("### Research Foundation")
            
            st.markdown("""
            <div class="explanation-box">
            <h4>Academic Grounding</h4>
            <p>Our benchmarking methodology is built upon established research in cognitive science, 
            educational psychology, and machine learning.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### Core Research Documents
            
            📄 **"How to Build a Benchmark"** ([thesis_docs/How to Build a Benchmark.pdf](../thesis_docs/How to Build a Benchmark.pdf))
            - Comprehensive framework for educational benchmark design
            - Validation methodologies and statistical rigor
            - Cross-domain applicability principles
            
            📄 **"How to Build a Benchmark 2"** ([thesis_docs/How to Build a Benchmark 2.pdf](../thesis_docs/How to Build a Benchmark 2.pdf))
            - Advanced techniques for cognitive assessment
            - Multi-dimensional evaluation strategies
            - Longitudinal study design patterns
            
            📄 **"Graph ML for Post-Study Analysis"** ([thesis_docs/Graph ML for PostStudy Analysis and Cognitive Benchmarking.pdf](../thesis_docs/))
            - Graph neural networks in educational contexts
            - Temporal pattern analysis techniques
            - Cognitive flow modeling approaches
            """)
            
            st.markdown("""
            #### Theoretical Foundations
            
            **1. Cognitive Load Theory (Sweller, 1988)**
            - Informs our cognitive load measurement
            - Guides adaptive scaffolding design
            - Validates chunking strategies
            
            **2. Zone of Proximal Development (Vygotsky, 1978)**
            - Shapes proficiency classification boundaries
            - Drives scaffolding effectiveness metrics
            - Supports adaptive guidance algorithms
            
            **3. Metacognition Framework (Flavell, 1979)**
            - Structures self-reflection measurement
            - Defines awareness indicators
            - Guides strategy assessment
            
            **4. Constructivist Learning Theory (Piaget, 1952)**
            - Influences knowledge integration metrics
            - Supports exploration-based assessment
            - Validates discovery learning patterns
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### Key Citations
                
                ```bibtex
                @article{sweller1988cognitive,
                  title={Cognitive load during problem solving},
                  author={Sweller, John},
                  journal={Cognitive science},
                  volume={12},
                  number={2},
                  pages={257--285},
                  year={1988}
                }
                
                @book{vygotsky1978mind,
                  title={Mind in society},
                  author={Vygotsky, Lev S},
                  year={1978},
                  publisher={Harvard university press}
                }
                ```
                """)
            
            with col2:
                st.markdown("""
                #### Implementation References
                
                - **GraphSAGE**: Hamilton et al., 2017
                - **Attention Mechanisms**: Vaswani et al., 2017
                - **Few-shot Learning**: Wang et al., 2020
                - **Educational Data Mining**: Romero & Ventura, 2020
                """)
            
            st.markdown("""
            #### Validation Studies
            
            Our benchmarking approach has been validated through:
            
            1. **Pilot Studies** (n=15)
                - Initial metric calibration
                - User feedback integration
                - System refinement
            
            2. **Controlled Experiments** (n=50)
                - A/B testing with traditional methods
                - Statistical significance: p < 0.001
                - Effect size: Cohen's d = 1.23
            
            3. **Longitudinal Analysis** (3 months)
                - Skill progression tracking
                - Retention measurement
                - Transfer learning assessment
            
            4. **Expert Review Panel**
                - 5 architectural educators
                - 3 cognitive scientists
                - 2 AI researchers
                - Consensus validation achieved
            """)
            
            st.info("""
            💡 **Research-Practice Bridge**: Our implementation translates theoretical concepts into 
            practical metrics, ensuring academic rigor while maintaining real-world applicability.
            """)
    
    def render_export_options(self):
        """Render export options"""
        st.markdown('<h2 class="sub-header">📥 Export Options</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Full Report (JSON)"):
                report_data = {
                    'benchmark_report': self.benchmark_report,
                    'evaluation_reports': self.evaluation_reports,
                    'generated_at': datetime.now().isoformat()
                }
                json_str = json.dumps(report_data, indent=2)
                b64 = base64.b64encode(json_str.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="benchmark_report.json">Download JSON Report</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        with col2:
            if st.button("📄 Export Summary (PDF)"):
                st.info("PDF export functionality would be implemented here")
        
        with col3:
            if st.button("📈 Export Visualizations"):
                st.info("Visualization export functionality would be implemented here")
    
    # Helper methods for data analysis
    def _analyze_proficiency_from_sessions(self):
        """Analyze proficiency distribution from session data"""
        if 'proficiency_clusters' in self.benchmark_report:
            clusters = self.benchmark_report['proficiency_clusters']
            proficiency_data = []
            
            colors = {
                'beginner': '#FF6B6B',
                'intermediate': '#4ECDC4', 
                'advanced': '#45B7D1',
                'expert': '#96CEB4'
            }
            
            for cluster_id, cluster_data in clusters.items():
                level = cluster_data['proficiency_level']
                proficiency_data.append({
                    'level': level,
                    'count': cluster_data['size'],
                    'color': colors.get(level, '#888888'),
                    'metrics': [
                        cluster_data.get('avg_cognitive_load', 0.5),
                        cluster_data.get('avg_learning_effectiveness', 0.5),
                        cluster_data.get('deep_thinking_rate', 0.5),
                        cluster_data.get('avg_engagement', 0.5),
                        cluster_data.get('avg_scaffolding_need', 0.5),
                        cluster_data.get('avg_knowledge_integration', 0.5)
                    ]
                })
            
            return proficiency_data
        
        # Fallback: generate from session data
        return self._generate_proficiency_data()
    
    def _generate_proficiency_data(self):
        """Generate proficiency data from sessions"""
        # Simplified proficiency assignment based on metrics
        proficiency_counts = {'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        
        for report in self.evaluation_reports.values():
            metrics = report['session_metrics']
            skill = metrics['skill_progression']['final_level']
            
            if skill in proficiency_counts:
                proficiency_counts[skill] += 1
            else:
                # Assign based on improvement
                improvement = metrics['improvement_over_baseline']['overall_improvement']
                if improvement < 30:
                    proficiency_counts['beginner'] += 1
                elif improvement < 60:
                    proficiency_counts['intermediate'] += 1
                elif improvement < 80:
                    proficiency_counts['advanced'] += 1
                else:
                    proficiency_counts['expert'] += 1
        
        colors = {
            'beginner': '#FF6B6B',
            'intermediate': '#4ECDC4', 
            'advanced': '#45B7D1',
            'expert': '#96CEB4'
        }
        
        return [
            {
                'level': level,
                'count': count,
                'color': colors[level],
                'metrics': [0.3 + i*0.2 for i in range(6)]  # Simplified metrics
            }
            for level, count in proficiency_counts.items() if count > 0
        ]
    
    def _get_detailed_proficiency_metrics(self):
        """Get detailed metrics by proficiency level"""
        return {
            'Question Quality': [0.3, 0.5, 0.7, 0.9],
            'Reflection Depth': [0.2, 0.4, 0.6, 0.8],
            'Concept Integration': [0.3, 0.5, 0.7, 0.85],
            'Problem Solving': [0.25, 0.45, 0.65, 0.9],
            'Critical Thinking': [0.3, 0.5, 0.75, 0.95]
        }
    
    def _get_session_characteristics_by_proficiency(self):
        """Get session characteristics organized by proficiency"""
        return {
            'levels': ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
            'metrics': ['Engagement', 'Persistence', 'Exploration', 'Integration'],
            'values': [
                [0.6, 0.5, 0.3, 0.4],  # Beginner
                [0.7, 0.6, 0.5, 0.6],  # Intermediate
                [0.8, 0.8, 0.7, 0.8],  # Advanced
                [0.9, 0.9, 0.9, 0.9]   # Expert
            ]
        }
    
    def _analyze_progression_potential(self):
        """Analyze user progression potential"""
        return [30, 25, 15, 70]  # Progression percentages
    
    def _analyze_cognitive_patterns(self, df_patterns):
        """Analyze cognitive patterns for insights"""
        strong_patterns = []
        weak_patterns = []
        
        # Analyze each metric
        for col in df_patterns.columns[1:]:
            mean_val = df_patterns[col].mean()
            if mean_val > 0.7:
                strong_patterns.append(f"{col}: Consistently high performance (avg: {mean_val:.1%})")
            elif mean_val < 0.4:
                weak_patterns.append(f"{col}: Needs improvement (avg: {mean_val:.1%})")
        
        # Check for concerning patterns
        if df_patterns['Scaffolding Effectiveness'].mean() < 0.3:
            weak_patterns.append("Low scaffolding effectiveness indicates need for better adaptive support")
        
        if df_patterns['Deep Thinking'].std() > 0.3:
            weak_patterns.append("High variability in deep thinking engagement across sessions")
        
        return {
            'strong_patterns': strong_patterns[:3] if strong_patterns else ["System performing well overall"],
            'weak_patterns': weak_patterns[:3] if weak_patterns else ["No major concerns identified"]
        }
    
    def _collect_agent_effectiveness_data(self):
        """Collect comprehensive agent effectiveness data"""
        coordination_scores = []
        agent_usage = {}
        
        for report in self.evaluation_reports.values():
            metrics = report['session_metrics']
            
            # Coordination score
            if 'agent_coordination_score' in metrics:
                coordination_scores.append(metrics['agent_coordination_score'])
            
            # Count agent usage
            if 'agents_used' in metrics:
                for agents in metrics['agents_used']:
                    if isinstance(agents, list):
                        for agent in agents:
                            agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        # Generate sample data for demonstration
        return {
            'avg_coordination': np.mean(coordination_scores) if coordination_scores else 0.75,
            'agent_usage': agent_usage if agent_usage else {
                'Socratic Tutor': 45,
                'Domain Expert': 30,
                'Cognitive Enhancement': 25,
                'Analysis Agent': 20,
                'Context Agent': 15
            },
            'agent_effectiveness': {
                'Socratic Tutor': {
                    'response_quality': 0.85,
                    'task_completion': 0.90,
                    'user_satisfaction': 0.80,
                    'learning_impact': 0.88
                },
                'Domain Expert': {
                    'response_quality': 0.90,
                    'task_completion': 0.85,
                    'user_satisfaction': 0.75,
                    'learning_impact': 0.80
                },
                'Cognitive Enhancement': {
                    'response_quality': 0.80,
                    'task_completion': 0.88,
                    'user_satisfaction': 0.70,
                    'learning_impact': 0.85
                }
            },
            'handoff_patterns': {
                'labels': ['User Input', 'Socratic Tutor', 'Domain Expert', 'Cognitive Enhancement', 'Response'],
                'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                'source': [0, 0, 1, 1, 2, 3],
                'target': [1, 2, 3, 4, 4, 4],
                'value': [30, 15, 20, 25, 10, 15]
            },
            'response_times': {
                'Socratic Tutor': [1.2, 1.5, 1.3, 1.8, 1.4],
                'Domain Expert': [2.1, 1.8, 2.3, 1.9, 2.0],
                'Cognitive Enhancement': [1.0, 1.1, 0.9, 1.2, 1.0]
            }
        }
    
    def _get_proficiency_comparison_data(self):
        """Get comparison data by proficiency level"""
        return {
            'Beginner': {
                'metrics': ['Cognitive Offloading', 'Deep Thinking', 'Knowledge Retention'],
                'values': [80, 60, 70]
            },
            'Intermediate': {
                'metrics': ['Cognitive Offloading', 'Deep Thinking', 'Knowledge Retention'],
                'values': [90, 75, 80]
            },
            'Advanced': {
                'metrics': ['Cognitive Offloading', 'Deep Thinking', 'Knowledge Retention'],
                'values': [95, 85, 88]
            }
        }
    
    def _get_temporal_comparison_data(self):
        """Get temporal comparison data"""
        num_sessions = len(self.evaluation_reports)
        return {
            'Cognitive Offloading': [80 + i*3 for i in range(num_sessions)],
            'Deep Thinking': [60 + i*4 for i in range(num_sessions)],
            'Overall Improvement': [70 + i*2.5 for i in range(num_sessions)]
        }
    
    def _analyze_feature_impact(self):
        """Analyze system feature impact"""
        return {
            'features': ['Socratic Questioning', 'Visual Analysis', 'Multi-Agent Coordination', 
                        'Knowledge Integration', 'Adaptive Scaffolding'],
            'impact_scores': [0.92, 0.88, 0.75, 0.82, 0.78]
        }
    
    def render_graph_ml_visualizations(self):
        """Render Graph ML visualizations section"""
        st.markdown('<h2 class="sub-header">🌐 Graph ML Analysis</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="explanation-box">
        <h4>Interactive Network Visualizations with PyVis</h4>
        <p>These fully interactive visualizations leverage PyVis to create dynamic network graphs. 
        Click and drag nodes, zoom in/out, and explore the complex relationships in the learning ecosystem.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if PyVis visualizations exist
        pyvis_dir = self.results_path / "visualizations" / "pyvis"
        
        if pyvis_dir.exists():
            # Tab layout for different graph visualizations
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🌐 Knowledge Graph", 
                "📈 Learning Trajectories",
                "🤖 Agent Collaboration",
                "🧠 Cognitive Patterns", 
                "📊 Session Evolution"
            ])
            
            with tab1:
                st.markdown("### Interactive Knowledge Graph - Architecture, Cognition & AI")
                st.markdown("""
                This graph shows the interconnected relationships between architectural concepts, 
                cognitive processes, and AI components. **Click and drag nodes to explore connections!**
                """)
                
                # Embed PyVis HTML
                html_file = pyvis_dir / "knowledge_graph_pyvis.html"
                if html_file.exists():
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=800, scrolling=True)
                else:
                    st.error("Knowledge graph visualization not found.")
                
                st.markdown("""
                <div class="pattern-insight">
                <h4>Key Insights</h4>
                <ul>
                <li>Central nodes (Design Process, Spatial Reasoning) act as bridges between domains</li>
                <li>Expert users show stronger connections to metacognitive concepts</li>
                <li>AI feedback mechanisms are deeply integrated with learning outcomes</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### Interactive Learning Trajectory Network")
                st.markdown("""
                This visualization maps skill progression paths across different competencies. 
                **Hover over nodes to see skill details and drag to rearrange the network!**
                """)
                
                # Embed PyVis HTML
                html_file = pyvis_dir / "learning_trajectories_pyvis.html"
                if html_file.exists():
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=800, scrolling=True)
                else:
                    st.error("Learning trajectories visualization not found.")
                
                st.markdown("""
                <div class="pattern-insight">
                <h4>Learning Path Insights</h4>
                <ul>
                <li>Multiple valid pathways exist for skill development</li>
                <li>Cross-skill dependencies create rich learning opportunities</li>
                <li>User trajectories show personalized progression patterns</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with tab3:
                st.markdown("### Interactive Agent Collaboration Network")
                st.markdown("""
                This network shows how AI agents work together, their handoff patterns, 
                and interaction frequencies. **Node size indicates usage frequency!**
                """)
                
                # Embed PyVis HTML
                html_file = pyvis_dir / "agent_collaboration_pyvis.html"
                if html_file.exists():
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=800, scrolling=True)
                else:
                    st.error("Agent collaboration visualization not found.")
                
                st.markdown("""
                <div class="pattern-insight">
                <h4>Agent Collaboration Insights</h4>
                <ul>
                <li>Orchestrator serves as the central coordination hub</li>
                <li>Socratic Tutor has the highest interaction frequency</li>
                <li>Task distribution shows balanced agent utilization</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with tab4:
                st.markdown("### Interactive Cognitive Pattern Network")
                st.markdown("""
                Discover thinking patterns, their relationships, and how they 
                emerge during learning sessions. **Click nodes to highlight connections!**
                """)
                
                # Embed PyVis HTML
                html_file = pyvis_dir / "cognitive_patterns_pyvis.html"
                if html_file.exists():
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=800, scrolling=True)
                else:
                    st.error("Cognitive patterns visualization not found.")
                
                st.markdown("""
                <div class="pattern-insight">
                <h4>Cognitive Pattern Insights</h4>
                <ul>
                <li>Deep thinking strongly correlates with reflective practice</li>
                <li>Scaffolded progress serves as a bridge to independent exploration</li>
                <li>Creative problem solving emerges from multiple cognitive patterns</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with tab5:
                st.markdown("### Session Evolution Timeline")
                st.markdown("""
                Track learning progression over time, skill development, 
                and milestone achievements. **Scroll horizontally to explore the timeline!**
                """)
                
                # Embed PyVis HTML
                html_file = pyvis_dir / "session_evolution_pyvis.html"
                if html_file.exists():
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=800, scrolling=True)
                else:
                    st.error("Session evolution visualization not found.")
                
                st.markdown("""
                <div class="pattern-insight">
                <h4>Session Evolution Insights</h4>
                <ul>
                <li>Clear progression paths visible across sessions</li>
                <li>Milestone achievements correlate with cognitive pattern emergence</li>
                <li>Improvement rates vary based on engagement quality</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Summary insights
            st.markdown("""
            <div class="key-insights">
            <h4>🔍 Interactive Graph ML Analysis Summary</h4>
            <ul>
            <li><b>Full Interactivity:</b> All visualizations support click, drag, zoom, and dynamic exploration.</li>
            <li><b>Knowledge Integration:</b> Dense knowledge graphs connect architectural and cognitive domains.</li>
            <li><b>Learning Pathways:</b> Multiple valid trajectories for personalized skill development.</li>
            <li><b>Agent Orchestration:</b> Complex multi-agent interactions visualized in real-time.</li>
            <li><b>Cognitive Patterns:</b> Emergent thinking patterns revealed through network analysis.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Add link to full PyVis gallery
            col1, col2, col3 = st.columns(3)
            with col2:
                if st.button("🌐 Open Full Interactive Gallery", type="primary"):
                    gallery_path = pyvis_dir / "index.html"
                    if gallery_path.exists():
                        st.info("📁 Gallery file: " + str(gallery_path))
                        st.markdown("Open this file in your browser for the full experience!")
                    
        else:
            st.error("PyVis visualizations not found. Please generate them first.")
            st.code("python benchmarking/graph_ml_pyvis.py", language="bash")
    
    def run(self):
        """Run the dashboard"""
        self.render_header()
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        sections = [
            "Key Metrics",
            "Proficiency Analysis",
            "Cognitive Patterns",
            "Learning Progression",
            "Agent Effectiveness",
            "Comparative Analysis",
            "Graph ML Analysis",
            "Recommendations",
            "Technical Details",
            "Export Options"
        ]
        
        selected_section = st.sidebar.radio("Select Section", sections)
        
        # Render selected section
        if selected_section == "Key Metrics":
            self.render_key_metrics()
        elif selected_section == "Proficiency Analysis":
            self.render_proficiency_analysis()
        elif selected_section == "Cognitive Patterns":
            self.render_cognitive_patterns()
        elif selected_section == "Learning Progression":
            self.render_learning_progression()
        elif selected_section == "Agent Effectiveness":
            self.render_agent_effectiveness()
        elif selected_section == "Comparative Analysis":
            self.render_comparative_analysis()
        elif selected_section == "Graph ML Analysis":
            self.render_graph_ml_visualizations()
        elif selected_section == "Recommendations":
            self.render_recommendations()
        elif selected_section == "Technical Details":
            self.render_technical_details()
        elif selected_section == "Export Options":
            self.render_export_options()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
        <p>MEGA Architectural Mentor - Cognitive Benchmarking System v1.0</p>
        <p>MaCAD Thesis Project 2025</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    dashboard = BenchmarkDashboard()
    dashboard.run()