"""
Professional Report Generator for MEGA Architectural Mentor Benchmarking
Uses WeasyPrint for beautiful PDF generation from HTML/CSS templates
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader, select_autoescape
import plotly.graph_objects as go
import plotly.io as pio
from weasyprint import HTML, CSS
import base64
from io import BytesIO

from benchmarking.report_insights_generator import ReportInsightsGenerator


class ProfessionalReportGenerator:
    """Generate beautiful PDF reports with data insights and visualizations"""
    
    def __init__(self, results_path: Path = Path("benchmarking/results")):
        self.results_path = results_path
        self.template_path = Path(__file__).parent / "report_templates"
        self.output_path = results_path / "exports"
        self.output_path.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_path),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Initialize insights generator
        self.insights_generator = ReportInsightsGenerator(results_path)
        
        # Configure Plotly for static image export
        pio.kaleido.scope.default_width = 800
        pio.kaleido.scope.default_height = 500
        
    def generate_report(self, report_type: str, **kwargs) -> str:
        """
        Generate a professional PDF report based on the specified type
        
        Args:
            report_type: Type of report to generate
                - 'comparative': Compare MENTOR vs GENERIC_AI vs CONTROL groups
                - 'group_analysis': Deep dive into a specific group
                - 'session_analysis': Analysis of specific sessions
                - 'full_benchmark': Complete benchmarking report
            **kwargs: Additional parameters based on report type
                
        Returns:
            Path to generated PDF report
        """
        
        # Load data
        data = self._load_report_data(report_type, **kwargs)
        
        # Generate insights
        insights = self.insights_generator.generate_insights(report_type, data)
        
        # Create visualizations
        visualizations = self._generate_visualizations(report_type, data)
        
        # Prepare template context
        context = {
            'title': self._get_report_title(report_type, **kwargs),
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'report_type': report_type,
            'data': data,
            'insights': insights,
            'visualizations': visualizations,
            'metadata': self._get_report_metadata(report_type, **kwargs)
        }
        
        # Select appropriate template
        template_name = f"{report_type}_report.html"
        if not (self.template_path / template_name).exists():
            template_name = "base_report.html"
            
        # Render HTML
        template = self.env.get_template(template_name)
        html_content = template.render(**context)
        
        # Generate PDF
        output_filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = self.output_path / output_filename
        
        # Create PDF with custom CSS
        css_path = self.template_path / "report_styles.css"
        HTML(string=html_content, base_url=str(self.template_path)).write_pdf(
            output_path,
            stylesheets=[CSS(css_path)] if css_path.exists() else []
        )
        
        return str(output_path)
    
    def _generate_html_content(self, report_type: str, **kwargs) -> str:
        """Generate HTML content without converting to PDF
        
        Args:
            report_type: Type of report to generate
            **kwargs: Additional parameters based on report type
            
        Returns:
            HTML content as string
        """
        # Load data
        data = self._load_report_data(report_type, **kwargs)
        
        # Generate insights
        insights = self.insights_generator.generate_insights(report_type, data)
        
        # Create visualizations
        visualizations = self._generate_visualizations(report_type, data)
        
        # Prepare template context
        context = {
            'title': self._get_report_title(report_type, **kwargs),
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'report_type': report_type,
            'data': data,
            'insights': insights,
            'visualizations': visualizations,
            'metadata': self._get_report_metadata(report_type, **kwargs)
        }
        
        # Select appropriate template
        template_name = f"{report_type}_report.html"
        if not (self.template_path / template_name).exists():
            template_name = "base_report.html"
            
        # Render HTML with embedded CSS
        template = self.env.get_template(template_name)
        html_content = template.render(**context)
        
        # Embed CSS inline for standalone HTML
        css_path = self.template_path / "report_styles.css"
        if css_path.exists():
            css_content = css_path.read_text()
            # Replace the CSS link with inline styles
            html_content = html_content.replace(
                '<link rel="stylesheet" href="report_styles.css">',
                f'<style>{css_content}</style>'
            )
        
        return html_content
    
    def _load_report_data(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Load data based on report type"""
        data = {}
        
        # Load master metrics
        master_metrics_path = self.results_path / "master_session_metrics.csv"
        if master_metrics_path.exists():
            data['master_metrics'] = pd.read_csv(master_metrics_path)
        
        # Load evaluation reports
        eval_dir = self.results_path / "evaluation_reports"
        if eval_dir.exists():
            data['evaluation_reports'] = {}
            for eval_file in eval_dir.glob("*.json"):
                with open(eval_file, 'r') as f:
                    session_data = json.load(f)
                    session_id = session_data.get('session_metrics', {}).get('session_id', eval_file.stem)
                    data['evaluation_reports'][session_id] = session_data
        
        # Filter data based on report type
        if report_type == 'comparative':
            data = self._filter_comparative_data(data)
        elif report_type == 'group_analysis':
            group = kwargs.get('group', 'MENTOR')
            data = self._filter_group_data(data, group)
        elif report_type == 'session_analysis':
            sessions = kwargs.get('sessions', [])
            data = self._filter_session_data(data, sessions)
            
        return data
    
    def _generate_visualizations(self, report_type: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate visualizations as base64 encoded images"""
        visualizations = {}
        
        if report_type == 'comparative':
            visualizations['group_comparison'] = self._create_group_comparison_chart(data)
            visualizations['improvement_trends'] = self._create_improvement_trends_chart(data)
            visualizations['cognitive_metrics'] = self._create_cognitive_metrics_radar(data)
            
        elif report_type == 'group_analysis':
            visualizations['performance_distribution'] = self._create_performance_distribution(data)
            visualizations['session_progression'] = self._create_session_progression_chart(data)
            visualizations['pattern_heatmap'] = self._create_pattern_heatmap(data)
            
        elif report_type == 'full_benchmark':
            visualizations['overall_metrics'] = self._create_overall_metrics_dashboard(data)
            visualizations['proficiency_breakdown'] = self._create_proficiency_breakdown(data)
            visualizations['feature_impact'] = self._create_feature_impact_chart(data)
            
        return visualizations
    
    def _create_group_comparison_chart(self, data: Dict[str, Any]) -> str:
        """Create group comparison bar chart"""
        # Group data by test group
        if 'master_metrics' in data and not data['master_metrics'].empty:
            df = data['master_metrics']
            
            # Calculate averages by group (assuming group info is in metadata or derived)
            groups = ['MENTOR', 'GENERIC_AI', 'CONTROL']
            metrics = ['prevention_rate', 'deep_thinking_rate', 'improvement_score']
            
            fig = go.Figure()
            
            for metric in metrics:
                values = []
                for group in groups:
                    # Filter by group (this assumes group info is available)
                    group_data = df[df['session_id'].str.contains(group.lower())] if 'session_id' in df else df
                    avg_value = group_data[metric].mean() if metric in group_data else 0
                    values.append(avg_value * 100 if metric.endswith('_rate') else avg_value)
                
                fig.add_trace(go.Bar(
                    name=metric.replace('_', ' ').title(),
                    x=groups,
                    y=values,
                    text=[f'{v:.1f}%' for v in values],
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
            
            # Convert to base64 image
            img_bytes = fig.to_image(format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            return f"data:image/png;base64,{img_base64}"
            
        return ""
    
    def _create_improvement_trends_chart(self, data: Dict[str, Any]) -> str:
        """Create improvement trends line chart"""
        if 'master_metrics' in data and not data['master_metrics'].empty:
            df = data['master_metrics'].sort_index()
            
            fig = go.Figure()
            
            metrics = ['prevention_rate', 'deep_thinking_rate']
            colors = ['#8B5CF6', '#EC4899']
            
            for metric, color in zip(metrics, colors):
                if metric in df.columns:
                    fig.add_trace(go.Scatter(
                        x=list(range(len(df))),
                        y=df[metric] * 100,
                        mode='lines+markers',
                        name=metric.replace('_', ' ').title(),
                        line=dict(color=color, width=3),
                        marker=dict(size=8)
                    ))
            
            fig.update_layout(
                title="Cognitive Enhancement Trends Over Sessions",
                xaxis_title="Session Number",
                yaxis_title="Percentage",
                template='plotly_white',
                hovermode='x unified',
                height=500,
                width=800
            )
            
            img_bytes = fig.to_image(format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            return f"data:image/png;base64,{img_base64}"
            
        return ""
    
    def _get_report_title(self, report_type: str, **kwargs) -> str:
        """Generate appropriate report title"""
        titles = {
            'comparative': "Comparative Analysis: MENTOR vs GENERIC AI vs CONTROL",
            'group_analysis': f"{kwargs.get('group', 'Group')} Performance Analysis",
            'session_analysis': "Selected Sessions Analysis Report",
            'full_benchmark': "Complete Cognitive Benchmarking Report"
        }
        return titles.get(report_type, "Benchmarking Report")
    
    def _get_report_metadata(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Get report metadata"""
        return {
            'report_version': '1.0',
            'system': 'MEGA Architectural Mentor',
            'analysis_type': report_type,
            'parameters': kwargs
        }
    
    def _filter_comparative_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data for comparative analysis"""
        # Implementation depends on how groups are identified in your data
        return data
    
    def _filter_group_data(self, data: Dict[str, Any], group: str) -> Dict[str, Any]:
        """Filter data for specific group"""
        # Implementation depends on how groups are identified in your data
        return data
    
    def _filter_session_data(self, data: Dict[str, Any], sessions: List[str]) -> Dict[str, Any]:
        """Filter data for specific sessions"""
        filtered_data = {}
        
        if 'master_metrics' in data:
            df = data['master_metrics']
            filtered_data['master_metrics'] = df[df['session_id'].isin(sessions)]
            
        if 'evaluation_reports' in data:
            filtered_data['evaluation_reports'] = {
                k: v for k, v in data['evaluation_reports'].items() 
                if k in sessions
            }
            
        return filtered_data
    
    def _create_cognitive_metrics_radar(self, data: Dict[str, Any]) -> str:
        """Create radar chart for cognitive metrics"""
        # Implementation for radar chart
        return ""
    
    def _create_performance_distribution(self, data: Dict[str, Any]) -> str:
        """Create performance distribution visualization"""
        # Implementation for distribution chart
        return ""
    
    def _create_session_progression_chart(self, data: Dict[str, Any]) -> str:
        """Create session progression visualization"""
        # Implementation for progression chart
        return ""
    
    def _create_pattern_heatmap(self, data: Dict[str, Any]) -> str:
        """Create pattern heatmap visualization"""
        # Implementation for heatmap
        return ""
    
    def _create_overall_metrics_dashboard(self, data: Dict[str, Any]) -> str:
        """Create overall metrics dashboard"""
        # Implementation for metrics dashboard
        return ""
    
    def _create_proficiency_breakdown(self, data: Dict[str, Any]) -> str:
        """Create proficiency breakdown visualization"""
        # Implementation for proficiency chart
        return ""
    
    def _create_feature_impact_chart(self, data: Dict[str, Any]) -> str:
        """Create feature impact visualization"""
        # Implementation for feature impact chart
        return ""