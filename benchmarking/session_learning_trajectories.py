"""
Session-Based Learning Trajectories from Linkography Data
Generates learning progression graphs from design session interactions
"""

import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
import re

from linkography_analyzer import LinkographySessionAnalyzer
from linkography_types import LinkographSession, DesignMove
from thesis_colors import THESIS_COLORS


class SessionLearningTrajectoryBuilder:
    """Builds learning trajectory graphs from actual session data"""
    
    def __init__(self):
        self.colors = THESIS_COLORS
        self.skill_categories = {
            'spatial_reasoning': {
                'keywords': ['space', 'spatial', 'layout', 'circulation', 'dimension', 'scale', 'proportion'],
                'color': self.colors['primary_purple']
            },
            'design_principles': {
                'keywords': ['design', 'principle', 'concept', 'approach', 'strategy', 'composition', 'balance'],
                'color': self.colors['primary_violet']
            },
            'critical_analysis': {
                'keywords': ['analyze', 'critique', 'evaluate', 'assess', 'compare', 'examine', 'question'],
                'color': self.colors['neutral_warm']
            },
            'technical_skills': {
                'keywords': ['structure', 'material', 'construction', 'detail', 'system', 'technical', 'build'],
                'color': self.colors['neutral_orange']
            },
            'contextual_thinking': {
                'keywords': ['context', 'site', 'environment', 'culture', 'history', 'urban', 'social'],
                'color': self.colors['primary_rose']
            },
            'creative_synthesis': {
                'keywords': ['create', 'innovate', 'synthesis', 'combine', 'transform', 'generate', 'imagine'],
                'color': self.colors['accent_coral']
            }
        }
        
        self.proficiency_levels = ['Novice', 'Developing', 'Proficient', 'Advanced', 'Expert']
        
    def extract_skill_progression(self, session: LinkographSession) -> Dict[str, List[Tuple[int, str]]]:
        """Extract skill progression timeline from a session"""
        skill_timeline = defaultdict(list)
        
        # Analyze each linkograph in the session
        for lg_idx, linkograph in enumerate(session.linkographs):
            for move_idx, move in enumerate(linkograph.moves):
                content_lower = move.content.lower()
                
                # Check which skills are demonstrated in this move
                for skill, info in self.skill_categories.items():
                    skill_score = 0
                    keyword_matches = 0
                    
                    for keyword in info['keywords']:
                        if keyword in content_lower:
                            keyword_matches += 1
                    
                    if keyword_matches > 0:
                        # Determine proficiency level based on move complexity
                        proficiency = self._assess_proficiency(move, linkograph, keyword_matches)
                        
                        # Add to timeline (linkograph_index, move_index, proficiency)
                        skill_timeline[skill].append((lg_idx, move_idx, proficiency))
        
        return dict(skill_timeline)
    
    def _assess_proficiency(self, move: DesignMove, linkograph, keyword_matches: int) -> str:
        """Assess proficiency level based on move characteristics"""
        # Calculate complexity factors
        move_length = len(move.content.split())
        links_count = sum(1 for link in linkograph.links if link.source_move == move.id or link.target_move == move.id)
        
        # Simple proficiency calculation
        score = 0
        score += min(keyword_matches * 10, 30)  # Keywords (max 30)
        score += min(move_length // 10, 20)     # Length (max 20)
        score += min(links_count * 15, 50)      # Connections (max 50)
        
        # Map score to proficiency level
        if score >= 80:
            return 'Expert'
        elif score >= 60:
            return 'Advanced'
        elif score >= 40:
            return 'Proficient'
        elif score >= 20:
            return 'Developing'
        else:
            return 'Novice'
    
    def build_session_trajectory_graph(self, session: LinkographSession) -> nx.DiGraph:
        """Build a learning trajectory graph for a single session"""
        G = nx.DiGraph()
        
        # Extract skill progression
        skill_progression = self.extract_skill_progression(session)
        
        # Add nodes for each skill development point
        node_id = 0
        skill_nodes = defaultdict(list)
        
        for skill, timeline in skill_progression.items():
            for lg_idx, move_idx, proficiency in timeline:
                node_attrs = {
                    'skill': skill,
                    'proficiency': proficiency,
                    'linkograph': lg_idx,
                    'move': move_idx,
                    'label': f"{skill.replace('_', ' ').title()}\n{proficiency}",
                    'color': self.skill_categories[skill]['color'],
                    'size': self.proficiency_levels.index(proficiency) * 5 + 15
                }
                G.add_node(node_id, **node_attrs)
                skill_nodes[skill].append(node_id)
                node_id += 1
        
        # Add edges showing progression within each skill
        for skill, nodes in skill_nodes.items():
            for i in range(len(nodes) - 1):
                G.add_edge(nodes[i], nodes[i+1], skill=skill, weight=1)
        
        # Add cross-skill connections based on temporal proximity
        all_nodes = sorted(G.nodes(), key=lambda n: (G.nodes[n]['linkograph'], G.nodes[n]['move']))
        
        for i in range(len(all_nodes) - 1):
            curr = all_nodes[i]
            next_node = all_nodes[i + 1]
            
            # If nodes are from same linkograph and close moves, add connection
            if (G.nodes[curr]['linkograph'] == G.nodes[next_node]['linkograph'] and 
                abs(G.nodes[curr]['move'] - G.nodes[next_node]['move']) <= 3 and
                G.nodes[curr]['skill'] != G.nodes[next_node]['skill']):
                
                G.add_edge(curr, next_node, 
                          type='cross_skill', 
                          weight=0.5,
                          style='dashed')
        
        return G
    
    def visualize_session_trajectory(self, G: nx.DiGraph, session_id: str) -> go.Figure:
        """Create interactive visualization of session learning trajectory"""
        
        if len(G.nodes()) == 0:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No skill progression detected in this session",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color=self.colors['primary_dark'])
            )
            fig.update_layout(
                title=f"Session {session_id[:8]} - No Skills Detected",
                height=400
            )
            return fig
        
        # Use hierarchical layout for trajectory
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Separate edges by type
        skill_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') != 'cross_skill']
        cross_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'cross_skill']
        
        # Create edge traces
        edge_traces = []
        
        # Skill progression edges (solid)
        for edge in skill_edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=2, color=self.colors['primary_dark']),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Cross-skill edges (dashed)
        for edge in cross_edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color=self.colors['neutral_light'], dash='dash'),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        node_hover = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            node_text.append(node_data['label'])
            node_color.append(node_data['color'])
            node_size.append(node_data['size'])
            
            # Create hover text
            hover = f"<b>{node_data['skill'].replace('_', ' ').title()}</b><br>"
            hover += f"Proficiency: {node_data['proficiency']}<br>"
            hover += f"Linkograph: {node_data['linkograph'] + 1}<br>"
            hover += f"Move: {node_data['move'] + 1}"
            node_hover.append(hover)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=9),
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color=self.colors['primary_dark'])
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        # Add arrows to show direction
        for edge in skill_edges:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            fig.add_annotation(
                x=x1, y=y1,
                ax=x0, ay=y0,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor=self.colors['primary_dark'],
                opacity=0.6
            )
        
        fig.update_layout(
            title={
                'text': f"Session {session_id[:8]} - Learning Trajectory",
                'font': {'size': 18, 'color': self.colors['primary_dark']}
            },
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=500,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        return fig
    
    def compare_session_trajectories(self, sessions: List[LinkographSession]) -> go.Figure:
        """Create comparison visualization of multiple session trajectories"""
        
        # Calculate skill development metrics for each session
        session_metrics = []
        
        for session in sessions[:6]:  # Limit to 6 sessions
            metrics = {
                'session_id': session.session_id[:8],
                'skills': defaultdict(lambda: {'count': 0, 'max_proficiency': 'Novice'})
            }
            
            skill_progression = self.extract_skill_progression(session)
            
            for skill, timeline in skill_progression.items():
                metrics['skills'][skill]['count'] = len(timeline)
                
                # Find highest proficiency achieved
                if timeline:
                    proficiencies = [t[2] for t in timeline]
                    max_prof_idx = max(self.proficiency_levels.index(p) for p in proficiencies)
                    metrics['skills'][skill]['max_proficiency'] = self.proficiency_levels[max_prof_idx]
            
            session_metrics.append(metrics)
        
        # Create radar chart for skill coverage
        skills = list(self.skill_categories.keys())
        skill_labels = [s.replace('_', ' ').title() for s in skills]
        
        fig = go.Figure()
        
        for i, metrics in enumerate(session_metrics):
            values = []
            for skill in skills:
                # Score based on count and max proficiency
                count_score = min(metrics['skills'][skill]['count'] * 10, 50)
                prof_score = self.proficiency_levels.index(metrics['skills'][skill]['max_proficiency']) * 20
                values.append(count_score + prof_score)
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=skill_labels,
                fill='toself',
                name=f"Session {metrics['session_id']}",
                line=dict(color=self.colors[list(self.colors.keys())[i % len(self.colors)]])
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title={
                'text': "Session Learning Trajectory Comparison",
                'font': {'size': 20, 'color': self.colors['primary_dark']}
            },
            showlegend=True,
            height=600
        )
        
        return fig
    
    def create_proficiency_progression_chart(self, sessions: List[LinkographSession]) -> go.Figure:
        """Create a chart showing proficiency progression across sessions"""
        
        # Track proficiency levels over time
        skill_progressions = defaultdict(list)
        
        for session_idx, session in enumerate(sessions):
            skill_progression = self.extract_skill_progression(session)
            
            # Calculate average proficiency for each skill in this session
            for skill in self.skill_categories:
                if skill in skill_progression and skill_progression[skill]:
                    proficiencies = [t[2] for t in skill_progression[skill]]
                    avg_prof_idx = np.mean([self.proficiency_levels.index(p) for p in proficiencies])
                    skill_progressions[skill].append((session_idx, avg_prof_idx))
                else:
                    skill_progressions[skill].append((session_idx, 0))
        
        # Create line chart
        fig = go.Figure()
        
        for skill, progression in skill_progressions.items():
            x = [p[0] for p in progression]
            y = [p[1] for p in progression]
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=skill.replace('_', ' ').title(),
                line=dict(color=self.skill_categories[skill]['color'], width=2),
                marker=dict(size=8)
            ))
        
        # Add proficiency level labels
        fig.update_layout(
            title={
                'text': "Skill Proficiency Progression Across Sessions",
                'font': {'size': 20, 'color': self.colors['primary_dark']}
            },
            xaxis_title="Session Number",
            yaxis=dict(
                title="Average Proficiency Level",
                tickmode='array',
                tickvals=list(range(len(self.proficiency_levels))),
                ticktext=self.proficiency_levels
            ),
            height=500,
            hovermode='x unified'
        )
        
        return fig