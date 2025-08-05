"""Simple HTML Report Generator for MEGA Architectural Mentor
No complex dependencies - just generates beautiful HTML reports
"""

import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

class SimpleReportGenerator:
    """Generate beautiful HTML reports without complex dependencies"""
    
    def __init__(self, results_path: Path, insights_generator):
        self.results_path = Path(results_path)
        self.insights_generator = insights_generator
        self.output_path = self.results_path / "exports"
        self.output_path.mkdir(exist_ok=True)
        
    def generate_report(self, report_type: str, **kwargs) -> str:
        """Generate HTML report and return the content"""
        
        # Load data
        data = self._load_report_data(report_type, **kwargs)
        
        # Generate insights
        insights = self.insights_generator.generate_insights(report_type, data)
        
        # Create visualizations as base64 images
        visualizations = self._generate_embedded_visualizations(report_type, data)
        
        # Generate HTML
        html_content = self._generate_html(
            title=self._get_report_title(report_type, **kwargs),
            report_type=report_type,
            data=data,
            insights=insights,
            visualizations=visualizations,
            metadata=self._get_report_metadata(report_type, **kwargs)
        )
        
        return html_content
    
    def _generate_html(self, title: str, report_type: str, data: Dict, 
                      insights: Dict, visualizations: Dict, metadata: Dict) -> str:
        """Generate complete HTML report with embedded CSS"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {self._get_embedded_css()}
    </style>
</head>
<body>
    <div class="report-container">
        {self._generate_cover_page(title, report_type)}
        {self._generate_executive_summary(insights)}
        {self._generate_key_findings(insights)}
        {self._generate_visualizations_section(visualizations)}
        {self._generate_statistical_analysis(insights)}
        {self._generate_patterns_section(insights)}
        {self._generate_recommendations_section(insights)}
        {self._generate_metadata_section(metadata)}
        {self._generate_footer()}
    </div>
</body>
</html>"""
        return html
    
    def _get_embedded_css(self) -> str:
        """Return embedded CSS for beautiful reports"""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #1a1a1a;
            background: #f5f5f5;
        }
        
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .cover-page {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .report-title {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
        }
        
        .subtitle {
            font-size: 24px;
            opacity: 0.9;
            margin-bottom: 40px;
        }
        
        .report-meta {
            font-size: 16px;
            opacity: 0.8;
        }
        
        section {
            padding: 60px 40px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        h2 {
            font-size: 32px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }
        
        h3 {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        }
        
        .executive-summary {
            background: #f8f9fa;
        }
        
        .summary-content {
            font-size: 16px;
            line-height: 1.8;
            padding: 30px;
            background: white;
            border-left: 4px solid #667eea;
            border-radius: 8px;
        }
        
        .findings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .finding-card {
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        
        .finding-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        
        .finding-card.high {
            border-left: 4px solid #DC2626;
            background: #FEF2F2;
        }
        
        .finding-card.positive {
            border-left: 4px solid #059669;
            background: #F0FDF4;
        }
        
        .finding-card.concern {
            border-left: 4px solid #F59E0B;
            background: #FFFBEB;
        }
        
        .visualization-container {
            margin: 40px 0;
            text-align: center;
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .stat-card {
            padding: 25px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }
        
        .stat-table {
            width: 100%;
            margin-top: 15px;
        }
        
        .stat-table td {
            padding: 8px 0;
            font-size: 14px;
        }
        
        .stat-table td:first-child {
            color: #666;
        }
        
        .stat-table td:last-child {
            font-weight: 600;
            text-align: right;
        }
        
        .recommendation-card {
            padding: 30px;
            margin-bottom: 25px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .rec-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .priority-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .priority-high .priority-badge {
            background: #DC2626;
            color: white;
        }
        
        .priority-medium .priority-badge {
            background: #F59E0B;
            color: white;
        }
        
        .priority-low .priority-badge {
            background: #6B7280;
            color: white;
        }
        
        .metadata-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }
        
        .metadata-table th,
        .metadata-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .metadata-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        
        footer {
            padding: 40px;
            text-align: center;
            background: #f8f9fa;
            color: #666;
        }
        
        @media print {
            .cover-page { page-break-after: always; }
            section { page-break-inside: avoid; }
            .finding-card, .recommendation-card { page-break-inside: avoid; }
        }
        """
    
    def _generate_cover_page(self, title: str, report_type: str) -> str:
        return f"""
        <div class="cover-page">
            <h1 class="report-title">{title}</h1>
            <div class="subtitle">MEGA Architectural Mentor - Cognitive Benchmarking System</div>
            <div class="report-meta">
                <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
                <p>Report Type: {report_type.replace('_', ' ').title()}</p>
            </div>
        </div>
        """
    
    def _generate_executive_summary(self, insights: Dict) -> str:
        return f"""
        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <div class="summary-content">
                {insights.get('summary', 'No summary available.')}
            </div>
        </section>
        """
    
    def _generate_key_findings(self, insights: Dict) -> str:
        findings_html = '<section><h2>Key Findings</h2><div class="findings-grid">'
        
        for finding in insights.get('key_findings', []):
            findings_html += f"""
            <div class="finding-card {finding.get('impact', 'neutral')}">
                <h3>{finding.get('category', 'General')}</h3>
                <h4>{finding.get('finding', '')}</h4>
                <p>{finding.get('detail', '')}</p>
            </div>
            """
        
        findings_html += '</div></section>'
        return findings_html
    
    def _generate_visualizations_section(self, visualizations: Dict) -> str:
        if not visualizations:
            return ""
            
        viz_html = '<section><h2>Data Visualizations</h2>'
        
        for viz_name, viz_data in visualizations.items():
            if viz_data:
                viz_html += f"""
                <div class="visualization-container">
                    <h3>{viz_name.replace('_', ' ').title()}</h3>
                    <img src="{viz_data}" alt="{viz_name}" class="chart-image">
                </div>
                """
        
        viz_html += '</section>'
        return viz_html
    
    def _generate_statistical_analysis(self, insights: Dict) -> str:
        stats = insights.get('statistical_analysis', {})
        if not stats:
            return ""
            
        stats_html = '<section><h2>Statistical Analysis</h2><div class="stats-grid">'
        
        for metric, values in stats.items():
            if metric != 'correlations' and isinstance(values, dict):
                stats_html += f"""
                <div class="stat-card">
                    <h3>{metric.replace('_', ' ').title()}</h3>
                    <table class="stat-table">
                        <tr><td>Mean</td><td>{values.get('mean', 0):.2f}</td></tr>
                        <tr><td>Std Dev</td><td>{values.get('std', 0):.2f}</td></tr>
                        <tr><td>Median</td><td>{values.get('median', 0):.2f}</td></tr>
                        <tr><td>Range</td><td>{values.get('min', 0):.2f} - {values.get('max', 0):.2f}</td></tr>
                    </table>
                </div>
                """
        
        stats_html += '</div></section>'
        return stats_html
    
    def _generate_patterns_section(self, insights: Dict) -> str:
        patterns = insights.get('patterns', {})
        if not patterns:
            return ""
            
        patterns_html = '<section><h2>Identified Patterns</h2>'
        
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                patterns_html += f"""
                <div class="pattern-section">
                    <h3>{pattern_type.replace('_', ' ').title()} Patterns</h3>
                    <ul>
                """
                for pattern in pattern_list:
                    patterns_html += f"<li>{pattern}</li>"
                patterns_html += "</ul></div>"
        
        patterns_html += '</section>'
        return patterns_html
    
    def _generate_recommendations_section(self, insights: Dict) -> str:
        recommendations = insights.get('recommendations', [])
        if not recommendations:
            return ""
            
        rec_html = '<section><h2>Recommendations</h2>'
        
        for rec in recommendations:
            rec_html += f"""
            <div class="recommendation-card priority-{rec.get('priority', 'medium')}">
                <div class="rec-header">
                    <h3>{rec.get('area', 'General')}</h3>
                    <span class="priority-badge">{rec.get('priority', 'medium').upper()}</span>
                </div>
                <h4>{rec.get('recommendation', '')}</h4>
                <p style="color: #666; font-style: italic; margin: 15px 0;">
                    {rec.get('rationale', '')}
                </p>
                <p style="color: #059669;">
                    <strong>Expected Impact:</strong> {rec.get('expected_impact', '')}
                </p>
            </div>
            """
        
        rec_html += '</section>'
        return rec_html
    
    def _generate_metadata_section(self, metadata: Dict) -> str:
        return f"""
        <section>
            <h2>Report Metadata</h2>
            <table class="metadata-table">
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
                {"".join(f'<tr><td>{k.replace("_", " ").title()}</td><td>{v}</td></tr>' 
                         for k, v in metadata.items())}
            </table>
        </section>
        """
    
    def _generate_footer(self) -> str:
        return f"""
        <footer>
            <p>Generated by MEGA Architectural Mentor Benchmarking System</p>
            <p>{datetime.now().strftime('%B %d, %Y')}</p>
        </footer>
        """
    
    def _generate_embedded_visualizations(self, report_type: str, data: Dict) -> Dict[str, str]:
        """Generate comprehensive visualizations as base64 embedded images"""
        visualizations = {}
        
        # Configure plotly for static image export
        pio.kaleido.scope.default_width = 800
        pio.kaleido.scope.default_height = 500
        
        # Generate visualizations based on report type
        if report_type == "comparative":
            # Group comparison charts
            chart = self._create_group_comparison_chart(data)
            if chart:
                visualizations['group_comparison'] = chart
                
            # Performance evolution
            timeline = self._create_performance_timeline_comparison(data)
            if timeline:
                visualizations['performance_evolution'] = timeline
                
            # Metric distribution
            dist = self._create_metric_distribution_chart(data)
            if dist:
                visualizations['metric_distribution'] = dist
                
        elif report_type == "group_analysis":
            # Single group performance
            chart = self._create_performance_timeline(data)
            if chart:
                visualizations['performance_timeline'] = chart
                
            # Session breakdown
            breakdown = self._create_session_breakdown_chart(data)
            if breakdown:
                visualizations['session_breakdown'] = breakdown
                
        elif report_type == "session_analysis":
            # Individual session metrics
            metrics = self._create_session_metrics_chart(data)
            if metrics:
                visualizations['session_metrics'] = metrics
                
            # Temporal patterns
            patterns = self._create_temporal_patterns_chart(data)
            if patterns:
                visualizations['temporal_patterns'] = patterns
                
        # Common visualizations for all report types
        # Correlation heatmap
        heatmap = self._create_correlation_heatmap(data)
        if heatmap:
            visualizations['correlation_heatmap'] = heatmap
            
        # Prevention vs Deep Thinking scatter
        scatter = self._create_prevention_vs_thinking_scatter(data)
        if scatter:
            visualizations['prevention_vs_thinking'] = scatter
            
        # Overall performance radar chart
        radar = self._create_performance_radar_chart(data)
        if radar:
            visualizations['performance_radar'] = radar
            
        # Improvement trends
        trends = self._create_improvement_trends_chart(data)
        if trends:
            visualizations['improvement_trends'] = trends
        
        return visualizations
    
    def _create_group_comparison_chart(self, data: Dict) -> Optional[str]:
        """Create group comparison chart"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                # Create comparison chart
                fig = go.Figure()
                
                # Add traces for different metrics
                metrics = ['prevention_rate', 'deep_thinking_rate', 'improvement_score']
                for metric in metrics:
                    if metric in df.columns:
                        fig.add_trace(go.Bar(
                            name=metric.replace('_', ' ').title(),
                            x=['MENTOR', 'GENERIC AI', 'CONTROL'],
                            y=[df[metric].mean() * 100 if metric.endswith('_rate') else df[metric].mean()],
                            text=[f'{df[metric].mean()*100:.1f}%' if metric.endswith('_rate') else f'{df[metric].mean():.1f}'],
                            textposition='auto',
                        ))
                
                fig.update_layout(
                    title="Performance Comparison Across Test Groups",
                    xaxis_title="Test Group",
                    yaxis_title="Score / Percentage",
                    barmode='group',
                    template='plotly_white',
                    height=500,
                    width=800
                )
                
                # Convert to base64
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating visualization: {e}")
            
        return None
    
    def _create_performance_timeline(self, data: Dict) -> Optional[str]:
        """Create performance timeline chart"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                fig = go.Figure()
                
                # Add line for prevention rate over time
                if 'prevention_rate' in df.columns:
                    fig.add_trace(go.Scatter(
                        x=list(range(len(df))),
                        y=df['prevention_rate'] * 100,
                        mode='lines+markers',
                        name='Prevention Rate',
                        line=dict(color='#667eea', width=3)
                    ))
                
                fig.update_layout(
                    title="Performance Evolution Over Sessions",
                    xaxis_title="Session Number",
                    yaxis_title="Rate (%)",
                    template='plotly_white',
                    height=500,
                    width=800
                )
                
                # Convert to base64
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating visualization: {e}")
            
        return None
    
    def _load_report_data(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Load data based on report type"""
        data = {}
        
        # Load master metrics
        master_metrics_path = self.results_path / "master_session_metrics.csv"
        if master_metrics_path.exists():
            data['master_metrics'] = pd.read_csv(master_metrics_path)
        
        # Load aggregate metrics
        aggregate_path = self.results_path / "master_aggregate_metrics.csv"
        if aggregate_path.exists():
            data['aggregate_metrics'] = pd.read_csv(aggregate_path)
        
        # Filter based on report type and parameters
        if report_type == "group_analysis" and 'group' in kwargs:
            # Filter for specific group
            group = kwargs['group']
            if 'master_metrics' in data:
                # Implement group filtering logic
                pass
                
        elif report_type == "session_analysis" and 'sessions' in kwargs:
            # Filter for specific sessions
            sessions = kwargs['sessions']
            if 'master_metrics' in data and sessions:
                data['master_metrics'] = data['master_metrics'][
                    data['master_metrics']['session_id'].isin(sessions)
                ]
        
        return data
    
    def _get_report_title(self, report_type: str, **kwargs) -> str:
        """Generate appropriate title based on report type"""
        titles = {
            'comparative': 'Comparative Analysis Report',
            'group_analysis': f'{kwargs.get("group", "Group")} Analysis Report',
            'session_analysis': 'Session Analysis Report',
            'full_benchmark': 'Complete Benchmarking Report'
        }
        return titles.get(report_type, 'Benchmarking Report')
    
    def _get_report_metadata(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Generate metadata for the report"""
        metadata = {
            'report_type': report_type,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tool_version': '1.0.0',
            'data_source': str(self.results_path)
        }
        
        # Add type-specific metadata
        if 'group' in kwargs:
            metadata['test_group'] = kwargs['group']
        if 'sessions' in kwargs:
            metadata['sessions_analyzed'] = len(kwargs['sessions'])
            
        return metadata
    
    def _infer_groups(self, df: pd.DataFrame) -> List[str]:
        """Infer test groups from data"""
        if 'group' in df.columns:
            return df['group'].unique().tolist()
        elif 'test_group' in df.columns:
            return df['test_group'].unique().tolist()
        else:
            # Try to infer from session IDs
            groups = []
            if df['session_id'].str.contains('mentor', case=False).any():
                groups.append('MENTOR')
            if df['session_id'].str.contains('generic', case=False).any():
                groups.append('GENERIC AI')
            if df['session_id'].str.contains('control', case=False).any():
                groups.append('CONTROL')
            return groups if groups else ['All Sessions']
    
    def _create_performance_timeline_comparison(self, data: Dict) -> Optional[str]:
        """Create performance timeline comparison across groups"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                groups = self._infer_groups(df)
                
                fig = go.Figure()
                
                for group in groups:
                    group_df = df[df['group'] == group] if 'group' in df else df
                    if not group_df.empty:
                        # Sort by timestamp if available
                        if 'timestamp' in group_df.columns:
                            group_df = group_df.sort_values('timestamp')
                        
                        fig.add_trace(go.Scatter(
                            x=list(range(len(group_df))),
                            y=group_df['prevention_rate'] * 100,
                            mode='lines+markers',
                            name=f'{group} - Prevention Rate',
                            line=dict(width=3)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=list(range(len(group_df))),
                            y=group_df['deep_thinking_rate'] * 100,
                            mode='lines+markers',
                            name=f'{group} - Deep Thinking',
                            line=dict(width=3, dash='dash')
                        ))
                
                fig.update_layout(
                    title="Performance Evolution Over Time by Group",
                    xaxis_title="Session Number",
                    yaxis_title="Rate (%)",
                    template='plotly_white',
                    height=600,
                    width=1000,
                    hovermode='x unified'
                )
                
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating timeline comparison: {e}")
            
        return None
    
    def _create_metric_distribution_chart(self, data: Dict) -> Optional[str]:
        """Create metric distribution box plots"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                groups = self._infer_groups(df)
                
                fig = go.Figure()
                
                metrics = ['prevention_rate', 'deep_thinking_rate', 'improvement_score']
                colors = ['#667eea', '#059669', '#F59E0B']
                
                for i, metric in enumerate(metrics):
                    if metric in df.columns:
                        for group in groups:
                            group_df = df[df['group'] == group] if 'group' in df else df
                            values = group_df[metric] * 100 if metric.endswith('_rate') else group_df[metric]
                            
                            fig.add_trace(go.Box(
                                y=values,
                                name=f'{group} - {metric.replace("_", " ").title()}',
                                boxpoints='all',
                                jitter=0.3,
                                pointpos=-1.8,
                                marker_color=colors[i]
                            ))
                
                fig.update_layout(
                    title="Metric Distribution Analysis",
                    yaxis_title="Value",
                    template='plotly_white',
                    height=600,
                    width=1000,
                    showlegend=True
                )
                
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating distribution chart: {e}")
            
        return None
    
    def _create_correlation_heatmap(self, data: Dict) -> Optional[str]:
        """Create correlation heatmap of metrics"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                # Select numeric columns for correlation
                numeric_cols = ['prevention_rate', 'deep_thinking_rate', 'improvement_score',
                               'scaffolding_score', 'question_depth_score', 'avg_response_time']
                numeric_cols = [col for col in numeric_cols if col in df.columns]
                
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu',
                        zmid=0,
                        text=corr_matrix.round(2).values,
                        texttemplate='%{text}',
                        textfont={"size": 10},
                        colorbar=dict(title="Correlation")
                    ))
                    
                    fig.update_layout(
                        title="Metric Correlation Matrix",
                        height=600,
                        width=700,
                        template='plotly_white'
                    )
                    
                    img_bytes = fig.to_image(format="png")
                    img_base64 = base64.b64encode(img_bytes).decode()
                    return f"data:image/png;base64,{img_base64}"
                    
        except Exception as e:
            print(f"Error creating correlation heatmap: {e}")
            
        return None
    
    def _create_prevention_vs_thinking_scatter(self, data: Dict) -> Optional[str]:
        """Create scatter plot of prevention vs deep thinking rates"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                if 'prevention_rate' in df.columns and 'deep_thinking_rate' in df.columns:
                    groups = self._infer_groups(df)
                    
                    fig = go.Figure()
                    
                    colors = ['#667eea', '#059669', '#F59E0B']
                    for i, group in enumerate(groups):
                        group_df = df[df['group'] == group] if 'group' in df else df
                        
                        fig.add_trace(go.Scatter(
                            x=group_df['prevention_rate'] * 100,
                            y=group_df['deep_thinking_rate'] * 100,
                            mode='markers',
                            name=group,
                            marker=dict(
                                size=10,
                                color=colors[i % len(colors)],
                                line=dict(width=1, color='white')
                            ),
                            text=[f"Session: {s}" for s in group_df['session_id']],
                            hovertemplate='Prevention: %{x:.1f}%<br>Deep Thinking: %{y:.1f}%<br>%{text}'
                        ))
                    
                    # Add diagonal reference line
                    fig.add_trace(go.Scatter(
                        x=[0, 100],
                        y=[0, 100],
                        mode='lines',
                        name='Reference',
                        line=dict(dash='dash', color='gray'),
                        showlegend=False
                    ))
                    
                    fig.update_layout(
                        title="Prevention Rate vs Deep Thinking Engagement",
                        xaxis_title="Cognitive Offloading Prevention Rate (%)",
                        yaxis_title="Deep Thinking Engagement Rate (%)",
                        template='plotly_white',
                        height=600,
                        width=800
                    )
                    
                    img_bytes = fig.to_image(format="png")
                    img_base64 = base64.b64encode(img_bytes).decode()
                    return f"data:image/png;base64,{img_base64}"
                    
        except Exception as e:
            print(f"Error creating scatter plot: {e}")
            
        return None
    
    def _create_performance_radar_chart(self, data: Dict) -> Optional[str]:
        """Create radar chart showing overall performance profile"""
        try:
            if 'aggregate_metrics' in data and not data['aggregate_metrics'].empty:
                df = data['aggregate_metrics']
                
                categories = ['Prevention Rate', 'Deep Thinking', 'Improvement Score', 
                             'Scaffolding', 'Question Depth']
                
                fig = go.Figure()
                
                # Add trace for each proficiency level if available
                if 'proficiency_level' in df.columns:
                    for _, row in df.iterrows():
                        values = [
                            row.get('prevention_rate', 0) * 100,
                            row.get('deep_thinking_rate', 0) * 100,
                            row.get('improvement_score', 0) * 100,
                            row.get('scaffolding_score', 0) * 100,
                            row.get('question_depth_score', 0) * 100
                        ]
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=row['proficiency_level']
                        ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=True,
                    title="Performance Profile by Proficiency Level",
                    height=600,
                    width=700
                )
                
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating radar chart: {e}")
            
        return None
    
    def _create_improvement_trends_chart(self, data: Dict) -> Optional[str]:
        """Create improvement trends chart"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                # Calculate rolling averages for smoother trends
                if 'timestamp' in df.columns:
                    df = df.sort_values('timestamp')
                
                fig = go.Figure()
                
                # Add improvement score trend
                if 'improvement_score' in df.columns:
                    fig.add_trace(go.Scatter(
                        x=list(range(len(df))),
                        y=df['improvement_score'].rolling(window=3, min_periods=1).mean(),
                        mode='lines+markers',
                        name='Overall Improvement',
                        line=dict(width=3, color='#667eea')
                    ))
                
                # Add component trends
                metrics = ['prevention_rate', 'deep_thinking_rate']
                colors = ['#059669', '#F59E0B']
                
                for metric, color in zip(metrics, colors):
                    if metric in df.columns:
                        fig.add_trace(go.Scatter(
                            x=list(range(len(df))),
                            y=df[metric].rolling(window=3, min_periods=1).mean() * 100,
                            mode='lines',
                            name=metric.replace('_', ' ').title(),
                            line=dict(width=2, color=color, dash='dash')
                        ))
                
                fig.update_layout(
                    title="Improvement Trends Over Time (3-Session Moving Average)",
                    xaxis_title="Session Number",
                    yaxis_title="Score / Rate (%)",
                    template='plotly_white',
                    height=500,
                    width=1000,
                    hovermode='x unified'
                )
                
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating improvement trends: {e}")
            
        return None
    
    def _create_session_breakdown_chart(self, data: Dict) -> Optional[str]:
        """Create session breakdown chart for group analysis"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                # Create stacked bar chart of session components
                fig = go.Figure()
                
                sessions = df['session_id'].unique()[:10]  # Limit to 10 sessions for readability
                
                metrics = {
                    'Cognitive Offloading Prevention': 'prevention_rate',
                    'Deep Thinking Engagement': 'deep_thinking_rate',
                    'Scaffolding Effectiveness': 'scaffolding_score'
                }
                
                for name, col in metrics.items():
                    if col in df.columns:
                        values = [df[df['session_id'] == s][col].mean() * 100 for s in sessions]
                        fig.add_trace(go.Bar(
                            name=name,
                            x=[s[:8] for s in sessions],
                            y=values
                        ))
                
                fig.update_layout(
                    barmode='stack',
                    title="Session Performance Breakdown",
                    xaxis_title="Session ID",
                    yaxis_title="Score (%)",
                    template='plotly_white',
                    height=500,
                    width=1000
                )
                
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating session breakdown: {e}")
            
        return None
    
    def _create_session_metrics_chart(self, data: Dict) -> Optional[str]:
        """Create detailed metrics chart for specific sessions"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                # Create multi-metric bar chart
                fig = go.Figure()
                
                metrics = ['prevention_rate', 'deep_thinking_rate', 'improvement_score',
                          'scaffolding_score', 'question_depth_score']
                
                for _, session in df.iterrows():
                    values = []
                    labels = []
                    
                    for metric in metrics:
                        if metric in session:
                            value = session[metric]
                            if metric.endswith('_rate') or metric.endswith('_score'):
                                value *= 100
                            values.append(value)
                            labels.append(metric.replace('_', ' ').title())
                    
                    fig.add_trace(go.Bar(
                        x=labels,
                        y=values,
                        name=str(session['session_id'])[:8],
                        text=[f'{v:.1f}%' for v in values],
                        textposition='auto'
                    ))
                
                fig.update_layout(
                    title="Detailed Session Metrics Comparison",
                    xaxis_title="Metric",
                    yaxis_title="Value (%)",
                    template='plotly_white',
                    height=500,
                    width=1000,
                    barmode='group'
                )
                
                img_bytes = fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error creating session metrics: {e}")
            
        return None
    
    def _create_temporal_patterns_chart(self, data: Dict) -> Optional[str]:
        """Create temporal patterns analysis chart"""
        try:
            if 'master_metrics' in data and not data['master_metrics'].empty:
                df = data['master_metrics']
                
                # Create time-based heatmap if timestamp data available
                if 'timestamp' in df.columns and 'avg_response_time' in df.columns:
                    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                    df['day'] = pd.to_datetime(df['timestamp']).dt.day_name()
                    
                    # Aggregate by hour and day
                    pivot = df.pivot_table(
                        values='avg_response_time',
                        index='hour',
                        columns='day',
                        aggfunc='mean'
                    )
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot.values,
                        x=pivot.columns,
                        y=pivot.index,
                        colorscale='Viridis',
                        colorbar=dict(title="Avg Response Time (s)")
                    ))
                    
                    fig.update_layout(
                        title="Response Time Patterns by Day and Hour",
                        xaxis_title="Day of Week",
                        yaxis_title="Hour of Day",
                        template='plotly_white',
                        height=500,
                        width=800
                    )
                    
                    img_bytes = fig.to_image(format="png")
                    img_base64 = base64.b64encode(img_bytes).decode()
                    return f"data:image/png;base64,{img_base64}"
                    
        except Exception as e:
            print(f"Error creating temporal patterns: {e}")
            
        return None