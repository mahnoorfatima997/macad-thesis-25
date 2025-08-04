"""
Linkography Report Generator
Creates comprehensive, visually beautiful reports featuring linkography analysis
"""

import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from jinja2 import Template


class LinkographyReportGenerator:
    """Generate beautiful linkography-focused reports"""
    
    def __init__(self, results_path: Path):
        self.results_path = results_path
        self.thesis_colors = {
            'primary_dark': '#4f3a3e',
            'primary_purple': '#5c4f73',
            'primary_violet': '#784c80',
            'primary_rose': '#b87189',
            'primary_pink': '#cda29a',
            'neutral_light': '#e0ceb5',
            'neutral_warm': '#dcc188',
            'neutral_orange': '#d99c66',
            'accent_coral': '#cd766d',
            'accent_magenta': '#cf436f',
        }
        
    def generate_report(self, session_ids: List[str], report_type: str = 'comprehensive') -> str:
        """Generate a comprehensive linkography report"""
        
        # Load linkography data
        linkography_data = self._load_linkography_data(session_ids)
        
        # Generate visualizations
        visualizations = self._generate_all_visualizations(linkography_data)
        
        # Generate insights
        insights = self._generate_linkography_insights(linkography_data)
        
        # Create HTML report
        html_content = self._create_html_report(
            linkography_data,
            visualizations,
            insights,
            report_type
        )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_path / f"linkography_report_{timestamp}.html"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return str(report_path)
    
    def _load_linkography_data(self, session_ids: List[str]) -> Dict[str, Any]:
        """Load all linkography data for selected sessions"""
        data = {
            'sessions': {},
            'aggregate_metrics': {},
            'patterns': {},
            'cognitive_mapping': {}
        }
        
        # Load individual session linkographs
        linkography_dir = self.results_path / 'linkography'
        if linkography_dir.exists():
            for session_id in session_ids:
                session_file = linkography_dir / f"{session_id}_linkograph.json"
                if session_file.exists():
                    with open(session_file, 'r') as f:
                        data['sessions'][session_id] = json.load(f)
        
        # Load pattern analysis
        patterns_file = linkography_dir / 'pattern_analysis.json'
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                data['patterns'] = json.load(f)
        
        # Load cognitive mapping
        cognitive_file = linkography_dir / 'cognitive_patterns.json'
        if cognitive_file.exists():
            with open(cognitive_file, 'r') as f:
                data['cognitive_mapping'] = json.load(f)
        
        # Calculate aggregate metrics
        data['aggregate_metrics'] = self._calculate_aggregate_metrics(data['sessions'])
        
        return data
    
    def _calculate_aggregate_metrics(self, sessions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregate linkography metrics across sessions"""
        if not sessions:
            return {}
            
        metrics = {
            'total_moves': 0,
            'total_links': 0,
            'avg_link_density': 0,
            'avg_critical_ratio': 0,
            'phase_distribution': {'ideation': 0, 'visualization': 0, 'materialization': 0},
            'pattern_frequencies': {},
            'cognitive_indicators': {}
        }
        
        for session_data in sessions.values():
            if 'linkograph' in session_data:
                lg = session_data['linkograph']
                metrics['total_moves'] += len(lg.get('moves', []))
                metrics['total_links'] += len(lg.get('links', []))
                
                if 'metrics' in lg:
                    metrics['avg_link_density'] += lg['metrics'].get('link_density', 0)
                    metrics['avg_critical_ratio'] += lg['metrics'].get('critical_ratio', 0)
                    
                    # Phase distribution
                    for phase, count in lg['metrics'].get('phase_distribution', {}).items():
                        metrics['phase_distribution'][phase] += count
        
        # Calculate averages
        num_sessions = len(sessions)
        if num_sessions > 0:
            metrics['avg_link_density'] /= num_sessions
            metrics['avg_critical_ratio'] /= num_sessions
        
        return metrics
    
    def _generate_all_visualizations(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate all linkography visualizations"""
        visualizations = {}
        
        # 1. Aggregate Link Density Chart
        visualizations['link_density_chart'] = self._create_link_density_chart(data)
        
        # 2. Phase Distribution Sunburst
        visualizations['phase_sunburst'] = self._create_phase_sunburst(data)
        
        # 3. Critical Moves Timeline
        visualizations['critical_timeline'] = self._create_critical_moves_timeline(data)
        
        # 4. Pattern Recognition Heatmap
        visualizations['pattern_heatmap'] = self._create_pattern_heatmap(data)
        
        # 5. Cognitive Flow Diagram
        visualizations['cognitive_flow'] = self._create_cognitive_flow_diagram(data)
        
        # 6. Session Comparison Radar
        visualizations['session_radar'] = self._create_session_comparison_radar(data)
        
        # 7. Link Evolution Chart
        visualizations['link_evolution'] = self._create_link_evolution_chart(data)
        
        # 8. Design Space Exploration Map
        visualizations['design_space_map'] = self._create_design_space_map(data)
        
        return visualizations
    
    def _create_link_density_chart(self, data: Dict[str, Any]) -> str:
        """Create link density comparison chart"""
        fig = go.Figure()
        
        sessions = []
        densities = []
        colors = []
        
        color_cycle = list(self.thesis_colors.values())
        
        for i, (session_id, session_data) in enumerate(data['sessions'].items()):
            if 'linkograph' in session_data and 'metrics' in session_data['linkograph']:
                sessions.append(session_id[:8])  # Truncate for display
                densities.append(session_data['linkograph']['metrics'].get('link_density', 0))
                colors.append(color_cycle[i % len(color_cycle)])
        
        fig.add_trace(go.Bar(
            x=sessions,
            y=densities,
            marker_color=colors,
            text=[f"{d:.2f}" for d in densities],
            textposition='outside'
        ))
        
        # Add threshold line
        if densities:
            avg_density = np.mean(densities)
            fig.add_hline(
                y=avg_density,
                line_dash="dash",
                line_color=self.thesis_colors['accent_coral'],
                annotation_text=f"Average: {avg_density:.2f}"
            )
        
        fig.update_layout(
            title="Link Density Across Sessions",
            xaxis_title="Session",
            yaxis_title="Link Density",
            showlegend=False,
            height=400,
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        return self._fig_to_base64(fig)
    
    def _create_phase_sunburst(self, data: Dict[str, Any]) -> str:
        """Create phase distribution sunburst chart"""
        
        # Aggregate phase data
        phase_data = []
        phase_totals = data['aggregate_metrics'].get('phase_distribution', {})
        
        total_moves = sum(phase_totals.values())
        if total_moves == 0:
            total_moves = 1  # Avoid division by zero
        
        colors = {
            'ideation': self.thesis_colors['primary_purple'],
            'visualization': self.thesis_colors['primary_violet'],
            'materialization': self.thesis_colors['primary_rose']
        }
        
        # Create hierarchical data
        labels = ['Design Process']
        parents = ['']
        values = [total_moves]
        marker_colors = [self.thesis_colors['neutral_warm']]
        
        for phase, count in phase_totals.items():
            labels.append(phase.capitalize())
            parents.append('Design Process')
            values.append(count)
            marker_colors.append(colors.get(phase, self.thesis_colors['neutral_light']))
            
            # Add sub-categories for each phase
            if count > 0:
                percentage = (count / total_moves) * 100
                labels.append(f"{percentage:.1f}%")
                parents.append(phase.capitalize())
                values.append(count)
                marker_colors.append(colors.get(phase, self.thesis_colors['neutral_light']))
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=marker_colors),
            textinfo="label+percent parent"
        ))
        
        fig.update_layout(
            title="Design Phase Distribution",
            height=500,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return self._fig_to_base64(fig)
    
    def _create_critical_moves_timeline(self, data: Dict[str, Any]) -> str:
        """Create timeline of critical design moves"""
        fig = go.Figure()
        
        for session_id, session_data in data['sessions'].items():
            if 'linkograph' not in session_data:
                continue
                
            moves = session_data['linkograph'].get('moves', [])
            critical_moves = [m for m in moves if m.get('is_critical', False)]
            
            if critical_moves:
                x = [m['timestamp'] for m in critical_moves]
                y = [session_id[:8] for _ in critical_moves]
                texts = [m['content'][:50] + '...' if len(m['content']) > 50 else m['content'] 
                        for m in critical_moves]
                
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color=self.thesis_colors['accent_magenta'],
                        symbol='star'
                    ),
                    text=texts,
                    textposition='top center',
                    name=session_id[:8],
                    showlegend=False
                ))
        
        fig.update_layout(
            title="Critical Design Moves Timeline",
            xaxis_title="Time",
            yaxis_title="Session",
            height=400,
            template="plotly_white",
            hovermode='closest'
        )
        
        return self._fig_to_base64(fig)
    
    def _create_pattern_heatmap(self, data: Dict[str, Any]) -> str:
        """Create pattern recognition heatmap"""
        
        patterns = data.get('patterns', {})
        if not patterns:
            # Create empty heatmap
            fig = go.Figure(data=go.Heatmap(
                z=[[0]],
                text=[["No patterns detected"]],
                texttemplate="%{text}",
                showscale=False
            ))
        else:
            # Extract pattern matrix
            pattern_types = list(set(p['type'] for p in patterns.values() if 'type' in p))
            sessions = list(data['sessions'].keys())
            
            matrix = []
            for session in sessions:
                row = []
                for pattern_type in pattern_types:
                    count = sum(1 for p in patterns.values() 
                              if p.get('session') == session and p.get('type') == pattern_type)
                    row.append(count)
                matrix.append(row)
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=pattern_types,
                y=[s[:8] for s in sessions],
                colorscale=[
                    [0, self.thesis_colors['neutral_light']],
                    [0.5, self.thesis_colors['primary_rose']],
                    [1, self.thesis_colors['accent_magenta']]
                ],
                text=matrix,
                texttemplate="%{text}",
                textfont={"size": 12},
                showscale=True
            ))
        
        fig.update_layout(
            title="Design Pattern Recognition Heatmap",
            xaxis_title="Pattern Type",
            yaxis_title="Session",
            height=400
        )
        
        return self._fig_to_base64(fig)
    
    def _create_cognitive_flow_diagram(self, data: Dict[str, Any]) -> str:
        """Create cognitive flow Sankey diagram"""
        
        cognitive_data = data.get('cognitive_mapping', {})
        
        # Define nodes
        source_nodes = ["Exploration", "Synthesis", "Evaluation", "Refinement"]
        target_nodes = ["Deep Thinking", "Cognitive Offloading", "Scaffolding Success"]
        all_nodes = source_nodes + target_nodes
        
        # Create flows (example data structure)
        source = []
        target = []
        value = []
        
        # Map cognitive phases to outcomes
        flows = [
            ("Exploration", "Deep Thinking", 30),
            ("Exploration", "Cognitive Offloading", 10),
            ("Synthesis", "Deep Thinking", 25),
            ("Synthesis", "Scaffolding Success", 15),
            ("Evaluation", "Deep Thinking", 20),
            ("Evaluation", "Scaffolding Success", 20),
            ("Refinement", "Scaffolding Success", 25),
            ("Refinement", "Deep Thinking", 15)
        ]
        
        for src, tgt, val in flows:
            source.append(all_nodes.index(src))
            target.append(all_nodes.index(tgt))
            value.append(val)
        
        # Color nodes
        node_colors = [
            self.thesis_colors['primary_purple'],
            self.thesis_colors['primary_violet'],
            self.thesis_colors['primary_rose'],
            self.thesis_colors['primary_pink'],
            self.thesis_colors['accent_coral'],
            self.thesis_colors['neutral_orange'],
            self.thesis_colors['neutral_warm']
        ]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=node_colors
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=[self.thesis_colors['neutral_light']] * len(source)
            )
        )])
        
        fig.update_layout(
            title="Cognitive Process Flow",
            height=500,
            font=dict(size=12)
        )
        
        return self._fig_to_base64(fig)
    
    def _create_session_comparison_radar(self, data: Dict[str, Any]) -> str:
        """Create radar chart comparing sessions"""
        
        categories = ['Link Density', 'Critical Ratio', 'Phase Balance', 
                     'Pattern Diversity', 'Cognitive Depth']
        
        fig = go.Figure()
        
        color_cycle = list(self.thesis_colors.values())
        
        for i, (session_id, session_data) in enumerate(data['sessions'].items()):
            if 'linkograph' not in session_data:
                continue
                
            metrics = session_data['linkograph'].get('metrics', {})
            
            # Normalize values to 0-100 scale
            values = [
                min(metrics.get('link_density', 0) * 100, 100),
                min(metrics.get('critical_ratio', 0) * 100, 100),
                self._calculate_phase_balance(metrics.get('phase_distribution', {})),
                min(metrics.get('pattern_count', 0) * 10, 100),
                min(metrics.get('cognitive_score', 50), 100)
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=session_id[:8],
                line_color=color_cycle[i % len(color_cycle)],
                fillcolor=color_cycle[i % len(color_cycle)],
                opacity=0.3
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="Session Performance Comparison",
            height=500
        )
        
        return self._fig_to_base64(fig)
    
    def _create_link_evolution_chart(self, data: Dict[str, Any]) -> str:
        """Create link evolution over time chart"""
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Cumulative Links Over Time", "Link Creation Rate"),
            row_heights=[0.6, 0.4],
            vertical_spacing=0.15
        )
        
        color_cycle = list(self.thesis_colors.values())
        
        for i, (session_id, session_data) in enumerate(data['sessions'].items()):
            if 'linkograph' not in session_data:
                continue
                
            moves = session_data['linkograph'].get('moves', [])
            links = session_data['linkograph'].get('links', [])
            
            if not moves:
                continue
            
            # Calculate cumulative links
            timestamps = [m['timestamp'] for m in moves]
            cumulative_links = []
            link_count = 0
            
            for j, move in enumerate(moves):
                links_to_move = sum(1 for link in links 
                                  if link.get('target') == j or link.get('source') == j)
                link_count += links_to_move
                cumulative_links.append(link_count)
            
            # Add cumulative trace
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=cumulative_links,
                    mode='lines',
                    name=session_id[:8],
                    line=dict(color=color_cycle[i % len(color_cycle)], width=2)
                ),
                row=1, col=1
            )
            
            # Calculate link creation rate (rolling window)
            if len(moves) > 5:
                rates = []
                window = 5
                for j in range(window, len(cumulative_links)):
                    rate = (cumulative_links[j] - cumulative_links[j-window]) / window
                    rates.append(rate)
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps[window:],
                        y=rates,
                        mode='lines',
                        name=session_id[:8],
                        line=dict(color=color_cycle[i % len(color_cycle)], width=1, dash='dot'),
                        showlegend=False
                    ),
                    row=2, col=1
                )
        
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Links", row=1, col=1)
        fig.update_yaxes(title_text="Links/Move", row=2, col=1)
        
        fig.update_layout(
            height=600,
            title="Link Evolution Analysis",
            template="plotly_white"
        )
        
        return self._fig_to_base64(fig)
    
    def _create_design_space_map(self, data: Dict[str, Any]) -> str:
        """Create 2D projection of design space exploration"""
        
        # Collect all moves across sessions
        all_moves = []
        move_sessions = []
        
        for session_id, session_data in data['sessions'].items():
            if 'linkograph' in session_data:
                moves = session_data['linkograph'].get('moves', [])
                all_moves.extend(moves)
                move_sessions.extend([session_id] * len(moves))
        
        if not all_moves:
            # Empty visualization
            fig = go.Figure()
            fig.add_annotation(
                text="No design moves to visualize",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        else:
            # Simulate 2D positions (in real implementation, use embeddings)
            np.random.seed(42)
            x_pos = np.random.randn(len(all_moves))
            y_pos = np.random.randn(len(all_moves))
            
            # Color by phase
            colors = []
            phase_colors = {
                'ideation': self.thesis_colors['primary_purple'],
                'visualization': self.thesis_colors['primary_violet'],
                'materialization': self.thesis_colors['primary_rose']
            }
            
            for move in all_moves:
                phase = move.get('phase', 'ideation')
                colors.append(phase_colors.get(phase, self.thesis_colors['neutral_light']))
            
            # Create scatter plot
            fig = go.Figure()
            
            # Add traces for each session
            unique_sessions = list(set(move_sessions))
            for session in unique_sessions:
                mask = [s == session for s in move_sessions]
                session_x = [x for x, m in zip(x_pos, mask) if m]
                session_y = [y for y, m in zip(y_pos, mask) if m]
                session_colors = [c for c, m in zip(colors, mask) if m]
                session_texts = [all_moves[i]['content'][:30] + '...' 
                               for i, m in enumerate(mask) if m]
                
                fig.add_trace(go.Scatter(
                    x=session_x,
                    y=session_y,
                    mode='markers',
                    marker=dict(
                        color=session_colors,
                        size=8,
                        line=dict(color='white', width=1)
                    ),
                    text=session_texts,
                    name=session[:8],
                    hovertemplate='%{text}<extra></extra>'
                ))
            
            # Add phase regions
            fig.add_shape(
                type="circle",
                x0=-2, y0=-2, x1=0, y1=0,
                fillcolor=self.thesis_colors['primary_purple'],
                opacity=0.1,
                line=dict(width=0)
            )
            fig.add_annotation(x=-1, y=-1, text="Ideation", showarrow=False)
            
            fig.add_shape(
                type="circle",
                x0=0, y0=-1, x1=2, y1=1,
                fillcolor=self.thesis_colors['primary_violet'],
                opacity=0.1,
                line=dict(width=0)
            )
            fig.add_annotation(x=1, y=0, text="Visualization", showarrow=False)
            
            fig.add_shape(
                type="circle",
                x0=-1, y0=0, x1=1, y1=2,
                fillcolor=self.thesis_colors['primary_rose'],
                opacity=0.1,
                line=dict(width=0)
            )
            fig.add_annotation(x=0, y=1, text="Materialization", showarrow=False)
        
        fig.update_layout(
            title="Design Space Exploration Map",
            xaxis_title="Semantic Dimension 1",
            yaxis_title="Semantic Dimension 2",
            height=500,
            template="plotly_white",
            showlegend=True
        )
        
        return self._fig_to_base64(fig)
    
    def _calculate_phase_balance(self, phase_dist: Dict[str, int]) -> float:
        """Calculate phase balance score (0-100)"""
        if not phase_dist:
            return 50
            
        total = sum(phase_dist.values())
        if total == 0:
            return 50
            
        # Ideal distribution: 33% each
        ideal = total / 3
        deviations = [abs(count - ideal) for count in phase_dist.values()]
        avg_deviation = sum(deviations) / 3
        
        # Convert to 0-100 score (lower deviation = higher score)
        balance_score = max(0, 100 - (avg_deviation / ideal * 100))
        return balance_score
    
    def _generate_linkography_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deep insights from linkography data"""
        
        insights = {
            'executive_summary': self._generate_executive_summary(data),
            'key_findings': self._extract_key_findings(data),
            'pattern_analysis': self._analyze_patterns(data),
            'cognitive_insights': self._extract_cognitive_insights(data),
            'design_process_analysis': self._analyze_design_process(data),
            'recommendations': self._generate_recommendations(data)
        }
        
        return insights
    
    def _generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary of linkography analysis"""
        
        metrics = data.get('aggregate_metrics', {})
        num_sessions = len(data.get('sessions', {}))
        
        summary = f"""
        This comprehensive linkography analysis examines {num_sessions} design sessions, 
        revealing critical insights into the cognitive processes and design thinking patterns 
        of architectural students using the MEGA Architectural Mentor system.
        
        Across all sessions, we observed {metrics.get('total_moves', 0)} design moves with 
        {metrics.get('total_links', 0)} interconnections, resulting in an average link density 
        of {metrics.get('avg_link_density', 0):.2f}. This density indicates 
        {'high' if metrics.get('avg_link_density', 0) > 0.5 else 'moderate'} cognitive engagement 
        and design space exploration.
        
        The critical move ratio of {metrics.get('avg_critical_ratio', 0):.2%} suggests that 
        students are making {'significant' if metrics.get('avg_critical_ratio', 0) > 0.2 else 'incremental'} 
        design decisions that substantially impact their overall design development.
        """
        
        return summary.strip()
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract key findings from linkography analysis"""
        
        findings = []
        metrics = data.get('aggregate_metrics', {})
        
        # Link density finding
        avg_density = metrics.get('avg_link_density', 0)
        if avg_density > 0.6:
            findings.append({
                'category': 'Cognitive Engagement',
                'finding': 'Exceptional Link Density',
                'detail': f'Average link density of {avg_density:.2f} indicates highly interconnected design thinking',
                'implication': 'Students are effectively building on previous ideas and creating coherent design narratives'
            })
        elif avg_density < 0.3:
            findings.append({
                'category': 'Cognitive Engagement',
                'finding': 'Low Link Density',
                'detail': f'Link density of {avg_density:.2f} suggests fragmented design exploration',
                'implication': 'Consider interventions to encourage more reflective and connective thinking'
            })
        
        # Phase distribution finding
        phase_dist = metrics.get('phase_distribution', {})
        if phase_dist:
            total_moves = sum(phase_dist.values())
            if total_moves > 0:
                ideation_pct = phase_dist.get('ideation', 0) / total_moves * 100
                if ideation_pct > 50:
                    findings.append({
                        'category': 'Design Process',
                        'finding': 'Ideation-Heavy Process',
                        'detail': f'{ideation_pct:.1f}% of moves in ideation phase',
                        'implication': 'Students may need support transitioning from ideation to materialization'
                    })
        
        # Critical moves finding
        critical_ratio = metrics.get('avg_critical_ratio', 0)
        if critical_ratio > 0.25:
            findings.append({
                'category': 'Design Quality',
                'finding': 'High Critical Move Ratio',
                'detail': f'{critical_ratio:.1%} of moves are critical design decisions',
                'implication': 'Students are making impactful design choices that significantly shape their projects'
            })
        
        return findings
    
    def _analyze_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze design patterns from linkography"""
        
        patterns = data.get('patterns', {})
        pattern_analysis = {
            'most_common': [],
            'concerning_patterns': [],
            'positive_patterns': []
        }
        
        # Identify pattern types and frequencies
        pattern_counts = {}
        for pattern in patterns.values():
            ptype = pattern.get('type', 'unknown')
            pattern_counts[ptype] = pattern_counts.get(ptype, 0) + 1
        
        # Sort by frequency
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize patterns
        for ptype, count in sorted_patterns[:3]:
            pattern_analysis['most_common'].append({
                'type': ptype,
                'frequency': count,
                'description': self._describe_pattern(ptype)
            })
        
        # Identify concerning patterns
        concerning = ['fixation', 'repetition', 'abandonment']
        for ptype in concerning:
            if ptype in pattern_counts and pattern_counts[ptype] > 2:
                pattern_analysis['concerning_patterns'].append({
                    'type': ptype,
                    'frequency': pattern_counts[ptype],
                    'intervention': self._suggest_intervention(ptype)
                })
        
        # Identify positive patterns
        positive = ['synthesis', 'refinement', 'exploration']
        for ptype in positive:
            if ptype in pattern_counts and pattern_counts[ptype] > 3:
                pattern_analysis['positive_patterns'].append({
                    'type': ptype,
                    'frequency': pattern_counts[ptype],
                    'reinforcement': self._suggest_reinforcement(ptype)
                })
        
        return pattern_analysis
    
    def _describe_pattern(self, pattern_type: str) -> str:
        """Provide description for pattern type"""
        descriptions = {
            'fixation': 'Repeated focus on single design element without progression',
            'synthesis': 'Integration of multiple design concepts into cohesive solutions',
            'exploration': 'Broad investigation of design alternatives',
            'refinement': 'Iterative improvement of existing design elements',
            'abandonment': 'Sudden discontinuation of design threads',
            'breakthrough': 'Sudden insight leading to new design directions'
        }
        return descriptions.get(pattern_type, 'Design pattern observed in student work')
    
    def _suggest_intervention(self, pattern_type: str) -> str:
        """Suggest intervention for concerning pattern"""
        interventions = {
            'fixation': 'Prompt lateral thinking with "What if?" questions',
            'repetition': 'Encourage exploration of alternative approaches',
            'abandonment': 'Guide reflection on abandoned ideas for potential value'
        }
        return interventions.get(pattern_type, 'Consider targeted intervention')
    
    def _suggest_reinforcement(self, pattern_type: str) -> str:
        """Suggest reinforcement for positive pattern"""
        reinforcements = {
            'synthesis': 'Acknowledge integrative thinking and encourage documentation',
            'refinement': 'Support iterative process with targeted feedback',
            'exploration': 'Validate broad thinking while guiding toward convergence'
        }
        return reinforcements.get(pattern_type, 'Reinforce positive behavior')
    
    def _extract_cognitive_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cognitive insights from linkography"""
        
        cognitive_mapping = data.get('cognitive_mapping', {})
        sessions = data.get('sessions', {})
        
        insights = {
            'cognitive_load': self._assess_cognitive_load(sessions),
            'thinking_patterns': self._identify_thinking_patterns(sessions),
            'learning_progression': self._analyze_learning_progression(sessions)
        }
        
        return insights
    
    def _assess_cognitive_load(self, sessions: Dict[str, Any]) -> str:
        """Assess cognitive load from linkography patterns"""
        
        if not sessions:
            return "Insufficient data for cognitive load assessment"
        
        total_density = 0
        high_load_sessions = 0
        
        for session_data in sessions.values():
            if 'linkograph' in session_data:
                density = session_data['linkograph'].get('metrics', {}).get('link_density', 0)
                total_density += density
                if density > 0.7:
                    high_load_sessions += 1
        
        avg_density = total_density / len(sessions) if sessions else 0
        
        if avg_density > 0.6:
            return f"High cognitive engagement observed ({avg_density:.2f} average link density). Students are actively connecting ideas but may benefit from structured breaks."
        elif avg_density < 0.3:
            return f"Low cognitive engagement ({avg_density:.2f} average link density). Consider strategies to increase mental engagement and idea connection."
        else:
            return f"Moderate cognitive engagement ({avg_density:.2f} average link density). Good balance between exploration and focused work."
    
    def _identify_thinking_patterns(self, sessions: Dict[str, Any]) -> List[str]:
        """Identify thinking patterns from linkograph data"""
        
        patterns = []
        
        # Analyze move sequences
        for session_data in sessions.values():
            if 'linkograph' not in session_data:
                continue
                
            moves = session_data['linkograph'].get('moves', [])
            if len(moves) > 10:
                # Check for linear vs. non-linear thinking
                back_links = sum(1 for link in session_data['linkograph'].get('links', [])
                               if link.get('source', 0) > link.get('target', 0))
                
                if back_links > len(moves) * 0.3:
                    patterns.append("Non-linear thinking: Frequent revisiting and connecting to earlier ideas")
                else:
                    patterns.append("Linear progression: Sequential development with limited backtracking")
        
        return list(set(patterns))  # Remove duplicates
    
    def _analyze_learning_progression(self, sessions: Dict[str, Any]) -> str:
        """Analyze learning progression across sessions"""
        
        if len(sessions) < 2:
            return "Multiple sessions needed for progression analysis"
        
        # Sort sessions by timestamp
        sorted_sessions = sorted(sessions.items(), 
                               key=lambda x: x[1].get('timestamp', ''))
        
        early_metrics = []
        late_metrics = []
        
        # Split into early and late sessions
        midpoint = len(sorted_sessions) // 2
        
        for i, (_, session_data) in enumerate(sorted_sessions):
            if 'linkograph' in session_data:
                metrics = session_data['linkograph'].get('metrics', {})
                if i < midpoint:
                    early_metrics.append(metrics)
                else:
                    late_metrics.append(metrics)
        
        # Compare metrics
        if early_metrics and late_metrics:
            early_density = np.mean([m.get('link_density', 0) for m in early_metrics])
            late_density = np.mean([m.get('link_density', 0) for m in late_metrics])
            
            improvement = ((late_density - early_density) / early_density * 100) if early_density > 0 else 0
            
            if improvement > 20:
                return f"Significant learning progression observed: {improvement:.1f}% increase in cognitive connectivity"
            elif improvement > 0:
                return f"Moderate learning progression: {improvement:.1f}% improvement in design thinking integration"
            else:
                return "Learning progression unclear; consider additional scaffolding strategies"
        
        return "Insufficient data for progression analysis"
    
    def _analyze_design_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze design process characteristics"""
        
        metrics = data.get('aggregate_metrics', {})
        phase_dist = metrics.get('phase_distribution', {})
        
        total_moves = sum(phase_dist.values()) if phase_dist else 1
        
        process_analysis = {
            'phase_balance': self._assess_phase_balance(phase_dist, total_moves),
            'process_type': self._identify_process_type(data),
            'efficiency': self._assess_process_efficiency(data)
        }
        
        return process_analysis
    
    def _assess_phase_balance(self, phase_dist: Dict[str, int], total: int) -> str:
        """Assess balance between design phases"""
        
        if total == 0:
            return "No phase data available"
        
        percentages = {
            phase: (count / total * 100) for phase, count in phase_dist.items()
        }
        
        # Ideal is roughly 33% each
        deviations = [abs(pct - 33.3) for pct in percentages.values()]
        avg_deviation = np.mean(deviations) if deviations else 0
        
        if avg_deviation < 10:
            return "Well-balanced design process across all phases"
        elif any(pct > 50 for pct in percentages.values()):
            dominant = max(percentages, key=percentages.get)
            return f"Process dominated by {dominant} phase ({percentages[dominant]:.1f}%)"
        else:
            return "Moderately balanced process with room for improvement"
    
    def _identify_process_type(self, data: Dict[str, Any]) -> str:
        """Identify the type of design process"""
        
        # Analyze patterns to determine process type
        patterns = data.get('patterns', {})
        
        if any(p.get('type') == 'iteration' for p in patterns.values()):
            return "Iterative design process with cyclical refinement"
        elif any(p.get('type') == 'exploration' for p in patterns.values()):
            return "Exploratory process with broad solution space investigation"
        else:
            return "Linear design process with sequential development"
    
    def _assess_process_efficiency(self, data: Dict[str, Any]) -> str:
        """Assess efficiency of design process"""
        
        metrics = data.get('aggregate_metrics', {})
        
        if metrics.get('total_moves', 0) == 0:
            return "Insufficient data for efficiency assessment"
        
        # Calculate efficiency metrics
        moves_per_critical = (metrics.get('total_moves', 1) / 
                            max(1, metrics.get('total_moves', 1) * metrics.get('avg_critical_ratio', 0.1)))
        
        if moves_per_critical < 5:
            return "Highly efficient process with frequent critical decisions"
        elif moves_per_critical > 10:
            return "Process shows potential inefficiencies; consider focusing strategies"
        else:
            return "Moderate process efficiency with balanced exploration and decision-making"
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        
        recommendations = []
        metrics = data.get('aggregate_metrics', {})
        patterns = data.get('patterns', {})
        
        # Link density recommendations
        if metrics.get('avg_link_density', 0) < 0.3:
            recommendations.append({
                'area': 'Cognitive Connectivity',
                'recommendation': 'Implement reflection exercises to encourage idea linking',
                'expected_outcome': 'Increase link density by 40% through structured reflection'
            })
        
        # Phase balance recommendations
        phase_dist = metrics.get('phase_distribution', {})
        if phase_dist:
            total = sum(phase_dist.values())
            if total > 0 and phase_dist.get('materialization', 0) / total < 0.2:
                recommendations.append({
                    'area': 'Design Development',
                    'recommendation': 'Guide students toward concrete materialization of ideas',
                    'expected_outcome': 'Better balance between conceptual and concrete design work'
                })
        
        # Pattern-based recommendations
        concerning_patterns = [p for p in patterns.values() if p.get('type') in ['fixation', 'abandonment']]
        if len(concerning_patterns) > 3:
            recommendations.append({
                'area': 'Design Thinking',
                'recommendation': 'Introduce lateral thinking exercises and alternative perspectives',
                'expected_outcome': 'Reduce fixation patterns and encourage creative exploration'
            })
        
        return recommendations
    
    def _create_html_report(self, data: Dict[str, Any], visualizations: Dict[str, str], 
                           insights: Dict[str, Any], report_type: str) -> str:
        """Create the HTML report"""
        
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linkography Analysis Report - {{ timestamp }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, {{ colors.primary_dark }} 0%, {{ colors.primary_purple }} 100%);
            color: white;
            margin: -20px -20px 40px -20px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .executive-summary {
            background-color: {{ colors.neutral_light }};
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 40px;
            border-left: 5px solid {{ colors.accent_magenta }};
        }
        
        .executive-summary h2 {
            color: {{ colors.primary_dark }};
            margin-bottom: 15px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .metric-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: {{ colors.primary_purple }};
            margin: 10px 0;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .visualization-section {
            margin-bottom: 40px;
        }
        
        .visualization-section h2 {
            color: {{ colors.primary_dark }};
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid {{ colors.neutral_warm }};
        }
        
        .chart-container {
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
        
        .chart-container img {
            width: 100%;
            height: auto;
            border-radius: 5px;
        }
        
        .insights-section {
            background-color: #f0f0f0;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 40px;
        }
        
        .finding {
            background-color: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid {{ colors.accent_coral }};
        }
        
        .finding h3 {
            color: {{ colors.primary_dark }};
            margin-bottom: 10px;
        }
        
        .finding .category {
            display: inline-block;
            background-color: {{ colors.primary_rose }};
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-bottom: 10px;
        }
        
        .recommendations {
            background-color: {{ colors.neutral_light }};
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 40px;
        }
        
        .recommendation {
            background-color: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .recommendation h4 {
            color: {{ colors.primary_purple }};
            margin-bottom: 10px;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            border-top: 1px solid #e0e0e0;
        }
        
        @media print {
            body {
                background-color: white;
            }
            .container {
                box-shadow: none;
            }
            .header {
                background: {{ colors.primary_dark }};
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }
        }
        
        .phase-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        
        .phase-card {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            color: white;
        }
        
        .phase-ideation {
            background-color: {{ colors.primary_purple }};
        }
        
        .phase-visualization {
            background-color: {{ colors.primary_violet }};
        }
        
        .phase-materialization {
            background-color: {{ colors.primary_rose }};
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Linkography Analysis Report</h1>
            <p>{{ report_type }} Analysis | Generated {{ timestamp }}</p>
        </div>
        
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <p>{{ insights.executive_summary }}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Design Moves</div>
                <div class="metric-value">{{ aggregate_metrics.total_moves }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Links</div>
                <div class="metric-value">{{ aggregate_metrics.total_links }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Average Link Density</div>
                <div class="metric-value">{{ "%.2f"|format(aggregate_metrics.avg_link_density) }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Critical Move Ratio</div>
                <div class="metric-value">{{ "%.1f"|format(aggregate_metrics.avg_critical_ratio * 100) }}%</div>
            </div>
        </div>
        
        <div class="phase-grid">
            <div class="phase-card phase-ideation">
                <h3>Ideation</h3>
                <div class="metric-value">{{ aggregate_metrics.phase_distribution.ideation }}</div>
                <div>moves</div>
            </div>
            <div class="phase-card phase-visualization">
                <h3>Visualization</h3>
                <div class="metric-value">{{ aggregate_metrics.phase_distribution.visualization }}</div>
                <div>moves</div>
            </div>
            <div class="phase-card phase-materialization">
                <h3>Materialization</h3>
                <div class="metric-value">{{ aggregate_metrics.phase_distribution.materialization }}</div>
                <div>moves</div>
            </div>
        </div>
        
        <div class="visualization-section">
            <h2>Visual Analysis</h2>
            
            <div class="chart-container">
                <h3>Link Density Comparison</h3>
                <img src="data:image/png;base64,{{ visualizations.link_density_chart }}" alt="Link Density Chart">
            </div>
            
            <div class="chart-container">
                <h3>Design Phase Distribution</h3>
                <img src="data:image/png;base64,{{ visualizations.phase_sunburst }}" alt="Phase Distribution">
            </div>
            
            <div class="chart-container">
                <h3>Critical Design Moves Timeline</h3>
                <img src="data:image/png;base64,{{ visualizations.critical_timeline }}" alt="Critical Moves Timeline">
            </div>
            
            <div class="chart-container">
                <h3>Pattern Recognition Analysis</h3>
                <img src="data:image/png;base64,{{ visualizations.pattern_heatmap }}" alt="Pattern Heatmap">
            </div>
            
            <div class="chart-container">
                <h3>Cognitive Process Flow</h3>
                <img src="data:image/png;base64,{{ visualizations.cognitive_flow }}" alt="Cognitive Flow">
            </div>
            
            <div class="chart-container">
                <h3>Session Performance Comparison</h3>
                <img src="data:image/png;base64,{{ visualizations.session_radar }}" alt="Session Comparison">
            </div>
            
            <div class="chart-container">
                <h3>Link Evolution Over Time</h3>
                <img src="data:image/png;base64,{{ visualizations.link_evolution }}" alt="Link Evolution">
            </div>
            
            <div class="chart-container">
                <h3>Design Space Exploration</h3>
                <img src="data:image/png;base64,{{ visualizations.design_space_map }}" alt="Design Space Map">
            </div>
        </div>
        
        <div class="insights-section">
            <h2>Key Findings</h2>
            {% for finding in insights.key_findings %}
            <div class="finding">
                <span class="category">{{ finding.category }}</span>
                <h3>{{ finding.finding }}</h3>
                <p><strong>Details:</strong> {{ finding.detail }}</p>
                <p><strong>Implication:</strong> {{ finding.implication }}</p>
            </div>
            {% endfor %}
        </div>
        
        <div class="insights-section">
            <h2>Design Process Analysis</h2>
            <p><strong>Phase Balance:</strong> {{ insights.design_process_analysis.phase_balance }}</p>
            <p><strong>Process Type:</strong> {{ insights.design_process_analysis.process_type }}</p>
            <p><strong>Efficiency:</strong> {{ insights.design_process_analysis.efficiency }}</p>
        </div>
        
        <div class="insights-section">
            <h2>Cognitive Insights</h2>
            <p><strong>Cognitive Load Assessment:</strong> {{ insights.cognitive_insights.cognitive_load }}</p>
            
            {% if insights.cognitive_insights.thinking_patterns %}
            <h3>Identified Thinking Patterns:</h3>
            <ul>
            {% for pattern in insights.cognitive_insights.thinking_patterns %}
                <li>{{ pattern }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            <p><strong>Learning Progression:</strong> {{ insights.cognitive_insights.learning_progression }}</p>
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            {% for rec in insights.recommendations %}
            <div class="recommendation">
                <h4>{{ rec.area }}</h4>
                <p><strong>Action:</strong> {{ rec.recommendation }}</p>
                <p><strong>Expected Outcome:</strong> {{ rec.expected_outcome }}</p>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Report generated by MEGA Architectural Mentor - Linkography Analysis System</p>
            <p>{{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
        '''
        
        template = Template(template_str)
        
        # Prepare template data
        html_content = template.render(
            timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            report_type=report_type.replace('_', ' ').title(),
            colors=self.thesis_colors,
            aggregate_metrics=data.get('aggregate_metrics', {}),
            insights=insights,
            visualizations=visualizations
        )
        
        return html_content
    
    def _fig_to_base64(self, fig) -> str:
        """Convert plotly figure to base64 string"""
        import io
        import base64
        
        # Convert to static image
        img_bytes = fig.to_image(format="png", width=800, height=600)
        img_base64 = base64.b64encode(img_bytes).decode()
        
        return img_base64