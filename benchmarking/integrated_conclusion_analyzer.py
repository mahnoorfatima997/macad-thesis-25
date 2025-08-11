"""
Integrated Conclusion Analysis Module
Synthesizes insights from all dashboard sections to generate holistic session conclusions
Based on multi-metric synthesis framework and cross-sectional analysis
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from thesis_colors import THESIS_COLORS, COLOR_GRADIENTS, METRIC_COLORS

@dataclass
class DomainInsight:
    """Represents insights from a single analytical domain"""
    domain_name: str
    key_metrics: Dict[str, float]
    primary_finding: str
    confidence_level: str  # "HIGH", "MEDIUM", "LOW"
    correlations: List[str]
    anomaly_flags: List[str]
    narrative_contribution: str

@dataclass
class HolisticConclusion:
    """Complete integrated conclusion for a session"""
    session_id: str
    executive_summary: str
    domain_insights: List[DomainInsight]
    cross_domain_patterns: List[str]
    contradictions: List[str]
    overall_effectiveness: float
    confidence_score: float
    priority_recommendations: List[str]
    detailed_narrative: str
    performance_category: str  # "EXCELLENT", "GOOD", "MODERATE", "NEEDS_IMPROVEMENT"

class IntegratedConclusionAnalyzer:
    """
    Analyzes and synthesizes insights from all dashboard sections to create
    comprehensive session conclusions with narrative insights
    """
    
    def __init__(self):
        self.colors = THESIS_COLORS
        self.domain_weights = {
            'linkography': 0.20,
            'cognitive': 0.25,
            'agent_effectiveness': 0.15,
            'learning_progression': 0.20,
            'proficiency': 0.10,
            'anthropomorphism': 0.10
        }
        
    def analyze_session(self, 
                       session_id: str,
                       linkography_data: Optional[Dict] = None,
                       cognitive_data: Optional[Dict] = None,
                       agent_data: Optional[Dict] = None,
                       learning_data: Optional[Dict] = None,
                       proficiency_data: Optional[Dict] = None,
                       anthropomorphism_data: Optional[Dict] = None) -> HolisticConclusion:
        """
        Generate holistic conclusion by analyzing all available session data
        """
        
        # Extract insights from each domain
        domain_insights = []
        
        if linkography_data:
            domain_insights.append(self._analyze_linkography(linkography_data))
        
        if cognitive_data:
            domain_insights.append(self._analyze_cognitive_metrics(cognitive_data))
        
        if agent_data:
            domain_insights.append(self._analyze_agent_effectiveness(agent_data))
        
        if learning_data:
            domain_insights.append(self._analyze_learning_progression(learning_data))
        
        if proficiency_data:
            domain_insights.append(self._analyze_proficiency(proficiency_data))
        
        if anthropomorphism_data:
            domain_insights.append(self._analyze_anthropomorphism(anthropomorphism_data))
        
        # Identify cross-domain patterns
        cross_patterns = self._identify_cross_domain_patterns(domain_insights)
        
        # Detect contradictions
        contradictions = self._detect_contradictions(domain_insights)
        
        # Calculate overall effectiveness
        overall_effectiveness = self._calculate_overall_effectiveness(domain_insights)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(domain_insights, contradictions)
        
        # Generate recommendations
        recommendations = self._generate_priority_recommendations(
            domain_insights, cross_patterns, contradictions
        )
        
        # Determine performance category
        performance_category = self._categorize_performance(overall_effectiveness)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            domain_insights, overall_effectiveness, performance_category
        )
        
        # Generate detailed narrative
        detailed_narrative = self._generate_detailed_narrative(
            domain_insights, cross_patterns, contradictions, recommendations
        )
        
        return HolisticConclusion(
            session_id=session_id,
            executive_summary=executive_summary,
            domain_insights=domain_insights,
            cross_domain_patterns=cross_patterns,
            contradictions=contradictions,
            overall_effectiveness=overall_effectiveness,
            confidence_score=confidence_score,
            priority_recommendations=recommendations,
            detailed_narrative=detailed_narrative,
            performance_category=performance_category
        )
    
    def _analyze_linkography(self, data: Dict) -> DomainInsight:
        """Extract insights from linkography analysis"""
        
        # Extract key metrics
        total_moves = data.get('total_moves', 0)
        total_links = data.get('total_links', 0)
        link_density = total_links / max(total_moves, 1)
        critical_ratio = data.get('overall_metrics', {}).get('critical_move_ratio', 0)
        patterns = data.get('patterns_detected', [])
        
        # Determine primary finding
        if link_density > 5:
            primary_finding = f"High cognitive connectivity (density: {link_density:.1f}) with rich idea integration"
        elif link_density > 2:
            primary_finding = f"Moderate connectivity (density: {link_density:.1f}) with balanced exploration"
        else:
            primary_finding = f"Low connectivity (density: {link_density:.1f}) suggesting linear thinking"
        
        # Determine pattern type - handle both string and dict patterns
        if isinstance(patterns, list) and patterns:
            if isinstance(patterns[0], dict):
                chunk_count = sum(1 for p in patterns if p.get('pattern_type') == 'chunk')
                web_count = sum(1 for p in patterns if p.get('pattern_type') == 'web')
            else:
                # patterns is a list of strings
                chunk_count = sum(1 for p in patterns if p == 'chunk')
                web_count = sum(1 for p in patterns if p == 'web')
        else:
            chunk_count = 0
            web_count = 0
        
        if chunk_count > web_count:
            pattern_narrative = "Convergent thinking with deep focused exploration"
        elif web_count > chunk_count:
            pattern_narrative = "Divergent thinking with parallel idea exploration"
        else:
            pattern_narrative = "Balanced cognitive approach"
        
        # Identify correlations
        correlations = []
        if link_density > 3 and critical_ratio > 0.2:
            correlations.append("High connectivity correlates with strategic decision-making")
        
        # Check for anomalies
        anomalies = []
        if total_moves > 10 and link_density < 1:
            anomalies.append("Unusually low connectivity for session length")
        
        return DomainInsight(
            domain_name="Linkography",
            key_metrics={
                'total_moves': total_moves,
                'total_links': total_links,
                'link_density': link_density,
                'critical_ratio': critical_ratio
            },
            primary_finding=primary_finding,
            confidence_level="HIGH" if total_moves > 5 else "MEDIUM",
            correlations=correlations,
            anomaly_flags=anomalies,
            narrative_contribution=f"{primary_finding}. {pattern_narrative}"
        )
    
    def _analyze_cognitive_metrics(self, data: Dict) -> DomainInsight:
        """Extract insights from cognitive metrics"""
        
        cop = data.get('cognitive_offloading_prevention', 0)
        dte = data.get('deep_thinking_engagement', 0)
        ki = data.get('knowledge_integration', 0)
        se = data.get('scaffolding_effectiveness', 0)
        
        # Determine primary finding
        if cop > 0.8 and dte > 0.7:
            primary_finding = "Excellent cognitive independence with deep engagement"
        elif cop > 0.5 and dte > 0.5:
            primary_finding = "Good cognitive balance with moderate engagement"
        else:
            primary_finding = "Opportunity to enhance cognitive independence"
        
        # Check for correlations
        correlations = []
        if dte > 0.7:
            correlations.append("Deep thinking correlates with knowledge integration")
        
        # Check for anomalies
        anomalies = []
        if cop > 0.8 and ki < 0.3:
            anomalies.append("High prevention but low integration - possible isolation")
        
        return DomainInsight(
            domain_name="Cognitive Metrics",
            key_metrics={
                'offloading_prevention': cop,
                'deep_thinking': dte,
                'knowledge_integration': ki,
                'scaffolding': se
            },
            primary_finding=primary_finding,
            confidence_level="HIGH",
            correlations=correlations,
            anomaly_flags=anomalies,
            narrative_contribution=primary_finding
        )
    
    def _analyze_agent_effectiveness(self, data: Dict) -> DomainInsight:
        """Extract insights from agent effectiveness metrics"""
        
        coordination = data.get('agent_coordination_score', 0)
        response_quality = data.get('response_quality', 0)
        routing = data.get('routing_appropriateness', 0)
        
        if coordination > 0.8:
            primary_finding = "Optimal multi-agent coordination achieved"
        elif coordination > 0.5:
            primary_finding = "Adequate agent coordination with room for improvement"
        else:
            primary_finding = "Agent coordination needs attention"
        
        return DomainInsight(
            domain_name="Agent Effectiveness",
            key_metrics={
                'coordination': coordination,
                'response_quality': response_quality,
                'routing': routing
            },
            primary_finding=primary_finding,
            confidence_level="HIGH" if response_quality > 0.9 else "MEDIUM",
            correlations=[],
            anomaly_flags=[],
            narrative_contribution=primary_finding
        )
    
    def _analyze_learning_progression(self, data: Dict) -> DomainInsight:
        """Extract insights from learning progression data"""
        
        progression_rate = data.get('learning_progression', 0)
        metacognitive = data.get('metacognitive_awareness', 0)
        
        if progression_rate > 0.7:
            primary_finding = "Strong learning trajectory with positive skill development"
        elif progression_rate > 0.4:
            primary_finding = "Moderate learning progression"
        else:
            primary_finding = "Limited learning progression detected"
        
        return DomainInsight(
            domain_name="Learning Progression",
            key_metrics={
                'progression_rate': progression_rate,
                'metacognitive': metacognitive
            },
            primary_finding=primary_finding,
            confidence_level="MEDIUM",
            correlations=[],
            anomaly_flags=[],
            narrative_contribution=primary_finding
        )
    
    def _analyze_proficiency(self, data: Dict) -> DomainInsight:
        """Extract insights from proficiency analysis"""
        
        level = data.get('proficiency_level', 'intermediate')
        confidence = data.get('classification_confidence', 0.5)
        
        primary_finding = f"Classified as {level.upper()} proficiency level"
        
        return DomainInsight(
            domain_name="Proficiency Analysis",
            key_metrics={'confidence': confidence},
            primary_finding=primary_finding,
            confidence_level="HIGH" if confidence > 0.8 else "MEDIUM",
            correlations=[],
            anomaly_flags=[],
            narrative_contribution=primary_finding
        )
    
    def _analyze_anthropomorphism(self, data: Dict) -> DomainInsight:
        """Extract insights from anthropomorphism detection"""
        
        cai = data.get('cognitive_autonomy_index', 0.5)
        ads = data.get('anthropomorphism_score', 0.5)
        
        if cai > 0.7 and ads < 0.3:
            primary_finding = "Healthy cognitive autonomy with minimal dependency"
        elif ads > 0.7:
            primary_finding = "High anthropomorphic dependency detected"
        else:
            primary_finding = "Balanced human-AI interaction"
        
        return DomainInsight(
            domain_name="Anthropomorphism",
            key_metrics={'autonomy': cai, 'dependency': ads},
            primary_finding=primary_finding,
            confidence_level="MEDIUM",
            correlations=[],
            anomaly_flags=["Dependency risk" if ads > 0.7 else None],
            narrative_contribution=primary_finding
        )
    
    def _identify_cross_domain_patterns(self, insights: List[DomainInsight]) -> List[str]:
        """Identify patterns that span multiple domains"""
        
        patterns = []
        
        # Check for consistent high performance
        high_performing = sum(1 for i in insights 
                            if any(v > 0.7 for v in i.key_metrics.values()))
        if high_performing >= len(insights) * 0.7:
            patterns.append("Consistent high performance across multiple domains")
        
        # Check for engagement-outcome alignment
        cognitive = next((i for i in insights if i.domain_name == "Cognitive Metrics"), None)
        learning = next((i for i in insights if i.domain_name == "Learning Progression"), None)
        
        if cognitive and learning:
            if cognitive.key_metrics.get('deep_thinking', 0) > 0.7 and \
               learning.key_metrics.get('progression_rate', 0) > 0.7:
                patterns.append("Strong alignment between cognitive engagement and learning outcomes")
        
        return patterns
    
    def _detect_contradictions(self, insights: List[DomainInsight]) -> List[str]:
        """Detect contradictions between different domain insights"""
        
        contradictions = []
        
        # Check for high engagement but low progression
        cognitive = next((i for i in insights if i.domain_name == "Cognitive Metrics"), None)
        learning = next((i for i in insights if i.domain_name == "Learning Progression"), None)
        
        if cognitive and learning:
            if cognitive.key_metrics.get('deep_thinking', 0) > 0.7 and \
               learning.key_metrics.get('progression_rate', 0) < 0.3:
                contradictions.append("High cognitive engagement without corresponding learning progression")
        
        return contradictions
    
    def _calculate_overall_effectiveness(self, insights: List[DomainInsight]) -> float:
        """Calculate weighted overall effectiveness score"""
        
        total_score = 0
        total_weight = 0
        
        for insight in insights:
            domain_weight = self.domain_weights.get(
                insight.domain_name.lower().replace(" ", "_"), 0.1
            )
            
            # Calculate domain score from metrics
            if insight.key_metrics:
                domain_score = np.mean(list(insight.key_metrics.values()))
                total_score += domain_score * domain_weight
                total_weight += domain_weight
        
        return total_score / max(total_weight, 0.01)
    
    def _calculate_confidence_score(self, 
                                   insights: List[DomainInsight], 
                                   contradictions: List[str]) -> float:
        """Calculate confidence in the overall conclusion"""
        
        # Start with base confidence
        confidence = 0.8
        
        # Adjust for domain confidence levels
        high_confidence = sum(1 for i in insights if i.confidence_level == "HIGH")
        confidence += (high_confidence / len(insights)) * 0.1
        
        # Reduce for contradictions
        confidence -= len(contradictions) * 0.1
        
        # Reduce for anomalies
        total_anomalies = sum(len(i.anomaly_flags) for i in insights)
        confidence -= total_anomalies * 0.05
        
        return max(min(confidence, 1.0), 0.0)
    
    def _generate_priority_recommendations(self, 
                                          insights: List[DomainInsight],
                                          patterns: List[str],
                                          contradictions: List[str]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Check linkography insights
        linkography = next((i for i in insights if i.domain_name == "Linkography"), None)
        if linkography and linkography.key_metrics.get('link_density', 0) < 2:
            recommendations.append("Implement concept mapping exercises to increase idea connectivity")
        
        # Check cognitive insights
        cognitive = next((i for i in insights if i.domain_name == "Cognitive Metrics"), None)
        if cognitive and cognitive.key_metrics.get('deep_thinking', 0) < 0.5:
            recommendations.append("Introduce reflection prompts to deepen cognitive engagement")
        
        # Check for dependency issues
        anthropomorphism = next((i for i in insights if i.domain_name == "Anthropomorphism"), None)
        if anthropomorphism and anthropomorphism.key_metrics.get('dependency', 0) > 0.7:
            recommendations.append("Gradually reduce AI assistance to build independence")
        
        # Address contradictions
        if contradictions:
            recommendations.append(f"Investigate: {contradictions[0]}")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _categorize_performance(self, effectiveness: float) -> str:
        """Categorize overall performance level"""
        
        if effectiveness >= 0.8:
            return "EXCELLENT"
        elif effectiveness >= 0.6:
            return "GOOD"
        elif effectiveness >= 0.4:
            return "MODERATE"
        else:
            return "NEEDS_IMPROVEMENT"
    
    def _generate_executive_summary(self, 
                                   insights: List[DomainInsight],
                                   effectiveness: float,
                                   category: str) -> str:
        """Generate concise executive summary"""
        
        # Find the most significant insight
        primary_insight = insights[0].primary_finding if insights else "No data available"
        
        return f"""This session demonstrated {category.lower().replace('_', ' ')} performance 
        with {effectiveness:.0%} overall effectiveness. {primary_insight}. 
        Analysis based on {len(insights)} analytical domains."""
    
    def _generate_detailed_narrative(self,
                                    insights: List[DomainInsight],
                                    patterns: List[str],
                                    contradictions: List[str],
                                    recommendations: List[str]) -> str:
        """Generate comprehensive narrative conclusion"""
        
        narrative_parts = []
        
        # Opening
        narrative_parts.append("## Comprehensive Session Analysis\n")
        
        # Domain insights
        narrative_parts.append("### Domain-Specific Findings\n")
        for insight in insights:
            narrative_parts.append(f"**{insight.domain_name}**: {insight.narrative_contribution}\n")
        
        # Cross-domain patterns
        if patterns:
            narrative_parts.append("\n### Cross-Domain Patterns\n")
            for pattern in patterns:
                narrative_parts.append(f"• {pattern}\n")
        
        # Contradictions
        if contradictions:
            narrative_parts.append("\n### Areas Requiring Investigation\n")
            for contradiction in contradictions:
                narrative_parts.append(f"⚠ {contradiction}\n")
        
        # Recommendations
        if recommendations:
            narrative_parts.append("\n### Priority Recommendations\n")
            for i, rec in enumerate(recommendations, 1):
                narrative_parts.append(f"{i}. {rec}\n")
        
        # Closing interpretation
        narrative_parts.append("\n### Overall Interpretation\n")
        narrative_parts.append(self._generate_interpretation(insights, patterns, contradictions))
        
        return "".join(narrative_parts)
    
    def _generate_interpretation(self, 
                                insights: List[DomainInsight],
                                patterns: List[str],
                                contradictions: List[str]) -> str:
        """Generate interpretative conclusion"""
        
        if len(contradictions) == 0 and len(patterns) > 0:
            return """The session shows strong internal consistency with aligned performance 
            across multiple domains. This suggests effective learning conditions and 
            appropriate system utilization."""
        elif len(contradictions) > 0:
            return f"""The session reveals some inconsistencies that warrant further investigation. 
            While certain domains show strong performance, the identified contradictions 
            ({len(contradictions)} found) suggest opportunities for targeted intervention."""
        else:
            return """The session demonstrates baseline performance with opportunities for 
            enhancement across multiple domains. Focus on the priority recommendations 
            will likely yield the most significant improvements."""
    
    def create_session_breakdown_table(self, 
                                       conclusion: HolisticConclusion) -> go.Figure:
        """Create visual table showing session breakdown across domains"""
        
        # Prepare data for table
        domains = []
        metrics = []
        findings = []
        confidence = []
        flags = []
        
        for insight in conclusion.domain_insights:
            domains.append(insight.domain_name)
            
            # Format key metrics
            metric_text = ", ".join([f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" 
                                    for k, v in list(insight.key_metrics.items())[:2]])
            metrics.append(metric_text)
            
            # Truncate findings for table
            findings.append(insight.primary_finding[:50] + "..." 
                          if len(insight.primary_finding) > 50 
                          else insight.primary_finding)
            
            # Confidence with color coding
            conf_color = {
                "HIGH": self.colors['primary_dark'],
                "MEDIUM": self.colors['neutral_orange'],
                "LOW": self.colors['accent_coral']
            }
            confidence.append(f"<span style='color:{conf_color[insight.confidence_level]}'>{insight.confidence_level}</span>")
            
            # Anomaly flags
            flag_text = ", ".join(insight.anomaly_flags) if insight.anomaly_flags else "None"
            flags.append(flag_text)
        
        # Create table figure
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Domain</b>', '<b>Key Metrics</b>', '<b>Primary Finding</b>', 
                       '<b>Confidence</b>', '<b>Flags</b>'],
                fill_color=self.colors['primary_dark'],
                font=dict(color='white', size=12),
                align='left',
                height=30
            ),
            cells=dict(
                values=[domains, metrics, findings, confidence, flags],
                fill_color=['white'] * len(domains),
                font=dict(size=11),
                align='left',
                height=25
            )
        )])
        
        # Add overall metrics as annotations
        fig.add_annotation(
            text=f"<b>Overall Effectiveness: {conclusion.overall_effectiveness:.1%}</b>",
            xref="paper", yref="paper",
            x=0, y=1.15,
            showarrow=False,
            font=dict(size=14, color=self.colors['primary_dark']),
            align="left"
        )
        
        fig.add_annotation(
            text=f"<b>Confidence Score: {conclusion.confidence_score:.1%}</b>",
            xref="paper", yref="paper",
            x=0.5, y=1.15,
            showarrow=False,
            font=dict(size=14, color=self.colors['primary_purple']),
            align="center"
        )
        
        fig.add_annotation(
            text=f"<b>Category: {conclusion.performance_category}</b>",
            xref="paper", yref="paper",
            x=1, y=1.15,
            showarrow=False,
            font=dict(size=14, color=self.colors['primary_violet']),
            align="right"
        )
        
        fig.update_layout(
            title="Session Performance Breakdown Across Analytical Domains",
            height=400,
            margin=dict(t=80, b=20, l=20, r=20)
        )
        
        return fig
    
    def create_correlation_heatmap(self, 
                                  sessions: List[HolisticConclusion]) -> go.Figure:
        """Create correlation heatmap showing relationships between domains"""
        
        # Extract metrics from all sessions
        domain_names = set()
        for session in sessions:
            for insight in session.domain_insights:
                domain_names.add(insight.domain_name)
        
        domain_names = sorted(list(domain_names))
        n_domains = len(domain_names)
        
        # Calculate correlation matrix
        correlation_matrix = np.random.rand(n_domains, n_domains)  # Placeholder
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=domain_names,
            y=domain_names,
            colorscale=[
                [0, self.colors['neutral_light']],
                [0.5, self.colors['primary_rose']],
                [1, self.colors['primary_dark']]
            ],
            text=correlation_matrix.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Cross-Domain Correlation Analysis",
            height=500,
            xaxis=dict(tickangle=45),
            margin=dict(t=60, b=100, l=100, r=40)
        )
        
        return fig
    
    def create_session_radar_chart(self, conclusion: HolisticConclusion) -> go.Figure:
        """Create a radar chart showing performance across all domains for a session"""
        
        # Extract metrics for each domain
        categories = []
        values = []
        
        for insight in conclusion.domain_insights:
            categories.append(insight.domain_name)
            
            # Calculate average metric value for this domain
            if insight.key_metrics:
                avg_value = np.mean([v for v in insight.key_metrics.values() if isinstance(v, (int, float))])
                values.append(avg_value)
            else:
                values.append(0)
        
        # Create radar chart
        fig = go.Figure()
        
        # Add trace
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(120, 76, 128, 0.4)',  # primary_violet with 40% opacity
            line=dict(color=THESIS_COLORS['primary_dark'], width=2),
            marker=dict(
                color=THESIS_COLORS['primary_purple'],
                size=8,
                line=dict(color=THESIS_COLORS['primary_dark'], width=1)
            ),
            name='Session Performance'
        ))
        
        # Add reference line at 0.5 (moderate performance)
        fig.add_trace(go.Scatterpolar(
            r=[0.5] * len(categories),
            theta=categories,
            mode='lines',
            line=dict(color=THESIS_COLORS['neutral_orange'], width=1, dash='dash'),
            name='Baseline',
            showlegend=True
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                    ticktext=['0%', '25%', '50%', '75%', '100%'],
                    gridcolor=THESIS_COLORS['neutral_light']
                ),
                angularaxis=dict(
                    gridcolor=THESIS_COLORS['neutral_light']
                ),
                bgcolor='white'
            ),
            title=f"Multi-Domain Performance Profile - {conclusion.performance_category}",
            title_font=dict(size=16, color=THESIS_COLORS['primary_dark']),
            showlegend=True,
            legend=dict(
                x=1.1,
                y=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor=THESIS_COLORS['primary_dark'],
                borderwidth=1
            ),
            height=450,
            margin=dict(t=80, b=40, l=40, r=120)
        )
        
        return fig
    
    def create_domain_comparison_chart(self, conclusion: HolisticConclusion) -> go.Figure:
        """Create a bar chart comparing domain performance with confidence indicators"""
        
        domains = []
        metrics = []
        colors = []
        confidence_symbols = []
        
        # Define unique colors for each domain from thesis palette
        domain_colors = [
            THESIS_COLORS['primary_dark'],      # Dark burgundy
            THESIS_COLORS['primary_purple'],    # Deep purple
            THESIS_COLORS['primary_violet'],    # Rich violet
            THESIS_COLORS['primary_rose'],      # Dusty rose
            THESIS_COLORS['primary_pink'],      # Soft pink
            THESIS_COLORS['neutral_orange'],    # Soft orange
            THESIS_COLORS['accent_coral'],      # Coral red
            THESIS_COLORS['neutral_warm']       # Warm sand
        ]
        
        for i, insight in enumerate(conclusion.domain_insights):
            domains.append(insight.domain_name)
            
            # Calculate primary metric
            if insight.key_metrics:
                primary_value = list(insight.key_metrics.values())[0] if insight.key_metrics else 0
                metrics.append(primary_value)
            else:
                metrics.append(0)
            
            # Use different color for each domain
            colors.append(domain_colors[i % len(domain_colors)])
            
            # Confidence symbols
            if insight.confidence_level == "HIGH":
                confidence_symbols.append('●')
            elif insight.confidence_level == "MEDIUM":
                confidence_symbols.append('◐')
            else:
                confidence_symbols.append('○')
        
        # Create figure
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=domains,
            y=metrics,
            marker_color=colors,
            text=[f"{m:.1%}<br>{s}" for m, s in zip(metrics, confidence_symbols)],
            textposition='outside',
            textfont=dict(size=10),
            name='Performance',
            hovertemplate='%{x}<br>Value: %{y:.2%}<extra></extra>'
        ))
        
        # Add target line
        fig.add_shape(
            type="line",
            x0=-0.5, x1=len(domains)-0.5,
            y0=0.7, y1=0.7,
            line=dict(color=THESIS_COLORS['primary_rose'], width=2, dash="dash")
        )
        
        fig.add_annotation(
            x=len(domains)-0.5,
            y=0.7,
            text="Target",
            showarrow=False,
            xanchor="left",
            font=dict(size=10, color=THESIS_COLORS['primary_rose'])
        )
        
        fig.update_layout(
            title="Domain Performance Breakdown with Confidence Indicators",
            title_font=dict(size=16, color=THESIS_COLORS['primary_dark']),
            xaxis=dict(
                title="Analysis Domain",
                tickangle=45,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title="Performance Score",
                range=[0, 1.2],
                tickformat='.0%',
                gridcolor='rgba(0,0,0,0.05)'
            ),
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=60, b=100, l=60, r=40)
        )
        
        # Add legend for confidence symbols
        fig.add_annotation(
            text="Confidence: ● High  ◐ Medium  ○ Low",
            xref="paper", yref="paper",
            x=0.5, y=-0.25,
            showarrow=False,
            font=dict(size=10, color=THESIS_COLORS['primary_dark']),
            xanchor="center"
        )
        
        return fig
    
    def create_effectiveness_timeline(self, sessions: List[HolisticConclusion]) -> go.Figure:
        """Create a timeline showing effectiveness progression across sessions"""
        
        if not sessions:
            return go.Figure()
        
        # Sort sessions by ID (assuming chronological)
        sessions = sorted(sessions, key=lambda x: x.session_id)
        
        session_ids = [s.session_id[:8] for s in sessions]
        effectiveness = [s.overall_effectiveness for s in sessions]
        confidence = [s.confidence_score for s in sessions]
        categories = [s.performance_category for s in sessions]
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add effectiveness line
        fig.add_trace(
            go.Scatter(
                x=session_ids,
                y=effectiveness,
                mode='lines+markers',
                name='Effectiveness',
                line=dict(color=THESIS_COLORS['primary_purple'], width=3),
                marker=dict(
                    size=10,
                    color=[METRIC_COLORS.get(cat.lower(), THESIS_COLORS['neutral_warm']) 
                          for cat in categories],
                    line=dict(color=THESIS_COLORS['primary_dark'], width=2)
                ),
                hovertemplate='Session: %{x}<br>Effectiveness: %{y:.1%}<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Add confidence line
        fig.add_trace(
            go.Scatter(
                x=session_ids,
                y=confidence,
                mode='lines+markers',
                name='Confidence',
                line=dict(color=THESIS_COLORS['primary_rose'], width=2, dash='dot'),
                marker=dict(size=8, color=THESIS_COLORS['accent_coral']),
                hovertemplate='Session: %{x}<br>Confidence: %{y:.1%}<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Add performance zones
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(session_ids)-0.5,
            y0=0.8, y1=1.0,
            fillcolor=THESIS_COLORS['primary_dark'],
            opacity=0.1,
            layer="below",
            line_width=0
        )
        
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(session_ids)-0.5,
            y0=0.6, y1=0.8,
            fillcolor=THESIS_COLORS['primary_violet'],
            opacity=0.1,
            layer="below",
            line_width=0
        )
        
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(session_ids)-0.5,
            y0=0.4, y1=0.6,
            fillcolor=THESIS_COLORS['neutral_orange'],
            opacity=0.1,
            layer="below",
            line_width=0
        )
        
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(session_ids)-0.5,
            y0=0, y1=0.4,
            fillcolor=THESIS_COLORS['accent_coral'],
            opacity=0.1,
            layer="below",
            line_width=0
        )
        
        # Add zone labels
        fig.add_annotation(x=0, y=0.9, text="EXCELLENT", showarrow=False,
                          font=dict(size=9, color=THESIS_COLORS['primary_dark']),
                          xanchor="left", opacity=0.7)
        fig.add_annotation(x=0, y=0.7, text="GOOD", showarrow=False,
                          font=dict(size=9, color=THESIS_COLORS['primary_purple']),
                          xanchor="left", opacity=0.7)
        fig.add_annotation(x=0, y=0.5, text="MODERATE", showarrow=False,
                          font=dict(size=9, color=THESIS_COLORS['neutral_orange']),
                          xanchor="left", opacity=0.7)
        fig.add_annotation(x=0, y=0.2, text="NEEDS IMPROVEMENT", showarrow=False,
                          font=dict(size=9, color=THESIS_COLORS['accent_coral']),
                          xanchor="left", opacity=0.7)
        
        # Update axes
        fig.update_xaxes(title_text="Session ID", gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(title_text="Effectiveness", secondary_y=False,
                        range=[0, 1], tickformat='.0%', gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(title_text="Confidence", secondary_y=True,
                        range=[0, 1], tickformat='.0%')
        
        fig.update_layout(
            title="Session Performance Timeline",
            title_font=dict(size=16, color=THESIS_COLORS['primary_dark']),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='x unified',
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor=THESIS_COLORS['primary_dark'],
                borderwidth=1
            )
        )
        
        return fig
    
    def create_pattern_sunburst(self, conclusion: HolisticConclusion) -> go.Figure:
        """Create a sunburst chart showing hierarchical performance breakdown"""
        
        # Build hierarchical data - use consistent sizing for visualization
        labels = ["Overall"]
        parents = [""]
        values = [1.0]  # Root value
        colors = [self._get_performance_color(conclusion.overall_effectiveness)]
        text_values = [f"{conclusion.overall_effectiveness:.1%}"]
        
        # Count domains for equal distribution
        num_domains = len(conclusion.domain_insights)
        domain_size = 1.0 / num_domains if num_domains > 0 else 0
        
        for insight in conclusion.domain_insights:
            # Add domain level
            labels.append(insight.domain_name)
            parents.append("Overall")
            values.append(domain_size)
            
            # Calculate average metric for color
            if insight.key_metrics:
                avg_metric = np.mean([v for v in insight.key_metrics.values() if isinstance(v, (int, float))])
            else:
                avg_metric = 0.5
            
            colors.append(self._get_performance_color(avg_metric))
            text_values.append(f"{avg_metric:.1%}")
            
            # Add individual metrics
            metric_items = list(insight.key_metrics.items()) if insight.key_metrics else []
            num_metrics = len([m for m in metric_items if isinstance(m[1], (int, float))])
            
            if num_metrics > 0:
                metric_size = domain_size / num_metrics
                
                for metric_name, metric_value in metric_items:
                    if isinstance(metric_value, (int, float)):
                        display_name = metric_name.replace('_', ' ').title()
                        labels.append(display_name)
                        parents.append(insight.domain_name)
                        values.append(metric_size)
                        colors.append(self._get_performance_color(metric_value))
                        text_values.append(f"{metric_value:.1%}")
        
        # Create sunburst
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                line=dict(color=THESIS_COLORS['primary_dark'], width=1)
            ),
            text=text_values,
            textinfo="label+text",
            hovertemplate='<b>%{label}</b><br>Performance: %{text}<extra></extra>',
            insidetextorientation='radial'
        ))
        
        fig.update_layout(
            title="Hierarchical Performance Breakdown",
            title_font=dict(size=16, color=THESIS_COLORS['primary_dark']),
            height=500,
            margin=dict(t=60, b=20, l=20, r=20)
        )
        
        return fig
    
    def _get_performance_color(self, value: float) -> str:
        """Get color based on performance value using thesis gradient"""
        if value >= 0.8:
            return THESIS_COLORS['primary_dark']
        elif value >= 0.6:
            return THESIS_COLORS['primary_purple']
        elif value >= 0.4:
            return THESIS_COLORS['primary_violet']
        elif value >= 0.2:
            return THESIS_COLORS['neutral_orange']
        else:
            return THESIS_COLORS['accent_coral']
    
    def create_cognitive_correlation_heatmap(self, session_data: Dict) -> go.Figure:
        """Create correlation heatmap between cognitive dimensions for a session"""
        
        # Define cognitive dimensions
        dimensions = [
            'Offloading Prevention',
            'Deep Thinking',
            'Knowledge Integration',
            'Scaffolding',
            'Metacognition',
            'Critical Thinking'
        ]
        
        # Extract metrics if available
        metrics = {
            'Offloading Prevention': session_data.get('cognitive_offloading_prevention', 0.5),
            'Deep Thinking': session_data.get('deep_thinking_engagement', 0.5),
            'Knowledge Integration': session_data.get('knowledge_integration', 0.5),
            'Scaffolding': session_data.get('scaffolding_effectiveness', 0.5),
            'Metacognition': session_data.get('metacognitive_awareness', 0.5),
            'Critical Thinking': session_data.get('critical_thinking', 0.5)
        }
        
        # Create correlation matrix (simplified - in reality would calculate actual correlations)
        n_dims = len(dimensions)
        correlation_matrix = np.zeros((n_dims, n_dims))
        
        for i in range(n_dims):
            for j in range(n_dims):
                if i == j:
                    correlation_matrix[i][j] = 1.0
                else:
                    # Simulate correlation based on metric values
                    val_i = list(metrics.values())[i]
                    val_j = list(metrics.values())[j]
                    correlation_matrix[i][j] = min(val_i, val_j) * 0.8 + 0.2
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=dimensions,
            y=dimensions,
            colorscale=[
                [0, THESIS_COLORS['neutral_light']],
                [0.25, THESIS_COLORS['neutral_warm']],
                [0.5, THESIS_COLORS['primary_pink']],
                [0.75, THESIS_COLORS['primary_violet']],
                [1, THESIS_COLORS['primary_dark']]
            ],
            text=correlation_matrix.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Correlation", x=1.02)
        ))
        
        fig.update_layout(
            title="Cognitive Dimensions Correlation Matrix",
            title_font=dict(size=14, color=THESIS_COLORS['primary_dark']),
            height=400,
            xaxis=dict(tickangle=45),
            yaxis=dict(tickangle=0),
            margin=dict(t=60, b=100, l=100, r=100)
        )
        
        return fig
    
    def create_learning_progression_chart(self, session_id: str, session_metrics: Dict) -> go.Figure:
        """Create learning progression trends over time for a session"""
        
        # Simulate temporal data points (in real implementation, would use actual temporal data)
        time_points = ['Start', '25%', '50%', '75%', 'End']
        
        # Get actual metrics from session
        prevention_rate = session_metrics.get('prevention_rate', 0.5)
        deep_thinking = session_metrics.get('deep_thinking_rate', 0.5)
        engagement_rate = session_metrics.get('engagement_rate', 0.5)
        improvement_score = session_metrics.get('improvement_score', 0)
        
        # Create unique progression based on session metrics
        # Use improvement score to determine trajectory
        if improvement_score > 0:
            # Positive improvement trajectory
            progression = [
                prevention_rate * 0.7,
                prevention_rate * 0.85,
                prevention_rate,
                prevention_rate * 1.1,
                prevention_rate * (1 + improvement_score/100)
            ]
        elif improvement_score < 0:
            # Negative trajectory
            progression = [
                prevention_rate * 1.2,
                prevention_rate * 1.1,
                prevention_rate,
                prevention_rate * 0.9,
                prevention_rate * (1 + improvement_score/100)
            ]
        else:
            # Flat trajectory
            progression = [prevention_rate * 0.95, prevention_rate * 0.98, prevention_rate, 
                         prevention_rate * 1.01, prevention_rate * 1.02]
        
        # Create engagement data based on actual metrics
        engagement = [
            engagement_rate * 0.8,
            engagement_rate * 0.9,
            engagement_rate,
            engagement_rate * (1.05 if deep_thinking > 0.5 else 0.95),
            engagement_rate * (1.1 if deep_thinking > 0.7 else 0.9)
        ]
        
        fig = go.Figure()
        
        # Add progression line
        fig.add_trace(go.Scatter(
            x=time_points,
            y=progression,
            mode='lines+markers',
            name='Learning Progression',
            line=dict(color=THESIS_COLORS['primary_purple'], width=3),
            marker=dict(size=10, color=THESIS_COLORS['primary_dark'])
        ))
        
        # Add engagement line
        fig.add_trace(go.Scatter(
            x=time_points,
            y=engagement,
            mode='lines+markers',
            name='Cognitive Engagement',
            line=dict(color=THESIS_COLORS['primary_rose'], width=2, dash='dash'),
            marker=dict(size=8, color=THESIS_COLORS['primary_violet'])
        ))
        
        # Add trend line
        z = np.polyfit(range(len(progression)), progression, 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=time_points,
            y=p(range(len(time_points))),
            mode='lines',
            name='Trend',
            line=dict(color=THESIS_COLORS['neutral_orange'], width=1, dash='dot'),
            opacity=0.5
        ))
        
        fig.update_layout(
            title="Learning Progression Trends",
            title_font=dict(size=14, color=THESIS_COLORS['primary_dark']),
            xaxis_title="Session Progress",
            yaxis_title="Score",
            yaxis=dict(range=[0, 1], tickformat='.0%'),
            height=350,
            showlegend=True,
            legend=dict(x=0.02, y=0.98),
            plot_bgcolor='white'
        )
        
        return fig
    
    def create_dependency_risk_matrix(self, anthropomorphism_data: Dict) -> go.Figure:
        """Create dependency risk matrix from anthropomorphism analysis"""
        
        cai = anthropomorphism_data.get('cognitive_autonomy_index', 0.5)
        ads = anthropomorphism_data.get('anthropomorphism_score', 0.5)
        
        # Create quadrant chart
        fig = go.Figure()
        
        # Add quadrant backgrounds with proper RGBA colors
        fig.add_shape(type="rect", x0=0, x1=0.5, y0=0, y1=0.5,
                     fillcolor='rgba(205, 118, 109, 0.2)')  # accent_coral with transparency
        fig.add_shape(type="rect", x0=0.5, x1=1, y0=0, y1=0.5,
                     fillcolor='rgba(217, 156, 102, 0.2)')  # neutral_orange with transparency
        fig.add_shape(type="rect", x0=0, x1=0.5, y0=0.5, y1=1,
                     fillcolor='rgba(120, 76, 128, 0.2)')  # primary_violet with transparency
        fig.add_shape(type="rect", x0=0.5, x1=1, y0=0.5, y1=1,
                     fillcolor='rgba(79, 58, 62, 0.2)')  # primary_dark with transparency
        
        # Add grid lines for better readability
        for i in [0.25, 0.5, 0.75]:
            fig.add_shape(type="line", x0=i, x1=i, y0=0, y1=1,
                         line=dict(color='rgba(79, 58, 62, 0.1)', width=1, dash='dot'))
            fig.add_shape(type="line", x0=0, x1=1, y0=i, y1=i,
                         line=dict(color='rgba(79, 58, 62, 0.1)', width=1, dash='dot'))
        
        # Add session point
        fig.add_trace(go.Scatter(
            x=[cai],
            y=[1 - ads],  # Invert dependency for better visualization
            mode='markers+text',
            marker=dict(
                size=20,
                color=THESIS_COLORS['primary_purple'],
                line=dict(color=THESIS_COLORS['primary_dark'], width=3)
            ),
            text=['Current Session'],
            textposition='top center',
            showlegend=False,
            hovertemplate='CAI: %{x:.1%}<br>Independence: %{y:.1%}<extra></extra>'
        ))
        
        # Add quadrant labels
        fig.add_annotation(x=0.25, y=0.25, text="HIGH RISK<br>Low Autonomy<br>High Dependency",
                          showarrow=False, font=dict(size=10, color=THESIS_COLORS['accent_coral']))
        fig.add_annotation(x=0.75, y=0.25, text="MODERATE RISK<br>High Autonomy<br>High Dependency",
                          showarrow=False, font=dict(size=10, color=THESIS_COLORS['neutral_orange']))
        fig.add_annotation(x=0.25, y=0.75, text="MODERATE RISK<br>Low Autonomy<br>Low Dependency",
                          showarrow=False, font=dict(size=10, color=THESIS_COLORS['primary_violet']))
        fig.add_annotation(x=0.75, y=0.75, text="OPTIMAL<br>High Autonomy<br>Low Dependency",
                          showarrow=False, font=dict(size=10, color=THESIS_COLORS['primary_dark']))
        
        fig.update_layout(
            title="Cognitive Dependency Risk Matrix",
            title_font=dict(size=14, color=THESIS_COLORS['primary_dark']),
            xaxis=dict(
                title="Cognitive Autonomy Index", 
                range=[0, 1], 
                tickformat='.0%',
                showgrid=True,
                gridcolor='rgba(224, 206, 181, 0.3)'
            ),
            yaxis=dict(
                title="Independence Level", 
                range=[0, 1], 
                tickformat='.0%',
                showgrid=True,
                gridcolor='rgba(224, 206, 181, 0.3)'
            ),
            height=400,
            plot_bgcolor='white',
            margin=dict(l=60, r=40, t=60, b=60)
        )
        
        return fig
    
    def create_proficiency_characteristics_spider(self, session_metrics: Dict) -> go.Figure:
        """Create spider chart showing proficiency characteristics for the session"""
        
        categories = ['Question Quality', 'Reflection Depth', 'Concept Integration',
                     'Problem Solving', 'Critical Thinking', 'Engagement']
        
        # Extract values from session metrics
        values = [
            session_metrics.get('question_quality', 0.5),
            session_metrics.get('reflection_depth', 0.5),
            session_metrics.get('concept_integration', 0.5),
            session_metrics.get('problem_solving', 0.5),
            session_metrics.get('critical_thinking', 0.5),
            session_metrics.get('engagement_rate', 0.5)
        ]
        
        # Close the polygon
        values = values + [values[0]]
        categories = categories + [categories[0]]
        
        fig = go.Figure()
        
        # Add trace
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(184, 113, 137, 0.3)',  # primary_rose with transparency
            line=dict(color=THESIS_COLORS['primary_purple'], width=2),
            marker=dict(size=8, color=THESIS_COLORS['primary_dark'])
        ))
        
        # Add reference line
        fig.add_trace(go.Scatterpolar(
            r=[0.7] * len(categories),
            theta=categories,
            mode='lines',
            line=dict(color=THESIS_COLORS['neutral_orange'], width=1, dash='dash'),
            name='Target Level',
            showlegend=True
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0, 0.25, 0.5, 0.75, 1],
                    ticktext=['0%', '25%', '50%', '75%', '100%']
                )
            ),
            title="Proficiency Characteristics Profile",
            title_font=dict(size=14, color=THESIS_COLORS['primary_dark']),
            height=400,
            showlegend=True
        )
        
        return fig