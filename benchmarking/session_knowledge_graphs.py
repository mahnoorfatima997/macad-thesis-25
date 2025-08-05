"""
Session-Based Knowledge Graphs from Linkography Data
Generates actual knowledge graphs from design session interactions
"""

import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import re

from linkography_analyzer import LinkographySessionAnalyzer
from linkography_types import LinkographSession, DesignMove
from thesis_colors import THESIS_COLORS


class SessionKnowledgeGraphBuilder:
    """Builds knowledge graphs from actual session data"""
    
    def __init__(self):
        self.colors = THESIS_COLORS
        self.concept_extractors = self._initialize_extractors()
        
    def _initialize_extractors(self):
        """Initialize concept extraction patterns"""
        return {
            'spatial_concepts': [
                r'space|spatial|room|area|zone|layout|circulation|flow|path|corridor',
                r'dimension|scale|proportion|height|width|depth|size|meter|feet',
                r'boundary|edge|threshold|transition|connection|link|entrance|exit',
                r'interior|exterior|inside|outside|indoor|outdoor|courtyard|plaza',
                r'open|closed|permeable|transparent|enclosed|exposed',
                r'floor|ceiling|wall|partition|facade|envelope'
            ],
            'form_concepts': [
                r'form|shape|geometry|circle|square|rectangle|curve|angle|triangle',
                r'volume|mass|void|solid|hollow|dense|light|heavy',
                r'structure|frame|support|cantilever|span|load|column|beam',
                r'line|plane|point|surface|edge|corner|intersection',
                r'symmetry|asymmetry|balance|rhythm|pattern|grid',
                r'vertical|horizontal|diagonal|orthogonal|radial'
            ],
            'material_concepts': [
                r'material|concrete|steel|wood|glass|brick|stone|metal|plastic',
                r'texture|surface|finish|rough|smooth|transparent|opaque|translucent',
                r'color|light|shadow|reflection|absorption|brightness|darkness',
                r'natural|artificial|synthetic|organic|industrial',
                r'warm|cool|soft|hard|flexible|rigid|durable',
                r'sustainable|recycled|renewable|eco-friendly|green'
            ],
            'function_concepts': [
                r'function|use|purpose|activity|program|requirement|need',
                r'public|private|community|individual|collective|shared',
                r'accessibility|flexibility|adaptability|efficiency|performance',
                r'residential|commercial|institutional|educational|cultural',
                r'living|working|playing|learning|gathering|meeting',
                r'movement|circulation|access|entry|exit|pathway'
            ],
            'context_concepts': [
                r'context|site|environment|climate|weather|sun|wind|rain',
                r'culture|tradition|history|memory|identity|heritage',
                r'urban|landscape|nature|green|sustainability|ecology',
                r'neighborhood|district|city|region|local|global',
                r'view|vista|outlook|perspective|orientation|direction',
                r'topography|terrain|slope|level|grade|elevation'
            ],
            'process_concepts': [
                r'idea|concept|approach|strategy|method|process|technique',
                r'analysis|synthesis|evaluation|iteration|refinement|development',
                r'problem|solution|challenge|opportunity|constraint|limitation',
                r'design|create|make|build|construct|develop|generate',
                r'explore|investigate|research|study|examine|analyze',
                r'sketch|draw|model|diagram|plan|section|elevation'
            ]
        }
    
    def extract_concepts_from_move(self, move: DesignMove) -> Dict[str, List[str]]:
        """Extract architectural concepts from a design move"""
        content = move.content.lower()
        extracted = defaultdict(list)
        
        for category, patterns in self.concept_extractors.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    extracted[category].extend(matches)
        
        # Also extract key phrases
        if 'open' in content and ('space' in content or 'area' in content):
            extracted['spatial_concepts'].append('open space')
        if 'community' in content and ('space' in content or 'area' in content):
            extracted['function_concepts'].append('community space')
        if 'natural' in content and 'light' in content:
            extracted['material_concepts'].append('natural light')
        
        return dict(extracted)
    
    def extract_concepts_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract architectural concepts from any text content"""
        content = text.lower()
        extracted = defaultdict(list)
        
        for category, patterns in self.concept_extractors.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    extracted[category].extend(matches)
        
        # Extract key architectural phrases
        phrase_patterns = [
            # Spatial phrases
            ('open space', ['open', 'space']),
            ('public space', ['public', 'space']),
            ('private space', ['private', 'space']),
            ('floor plan', ['floor', 'plan']),
            ('site plan', ['site', 'plan']),
            ('circulation path', ['circulation', 'path']),
            # Form phrases
            ('building form', ['building', 'form']),
            ('structural system', ['structural', 'system']),
            ('architectural drawing', ['elevation|section|plan|perspective']),
            # Material phrases
            ('natural light', ['natural', 'light']),
            ('building material', ['building', 'material']),
            ('material palette', ['material', 'palette']),
            # Function phrases
            ('community space', ['community', 'space']),
            ('mixed use', ['mixed', 'use']),
            ('program distribution', ['program', 'distribution']),
            # Context phrases
            ('sustainable design', ['sustainable|green', 'design|building']),
            ('site context', ['site', 'context']),
            ('urban fabric', ['urban', 'fabric']),
            # Process phrases
            ('design process', ['design', 'process']),
            ('conceptual approach', ['conceptual', 'approach']),
            ('design strategy', ['design', 'strategy'])
        ]
        
        for phrase, pattern_words in phrase_patterns:
            if all(any(word in content for word in alternatives.split('|')) 
                   for alternatives in pattern_words):
                # Determine category based on phrase
                if any(word in phrase for word in ['space', 'plan', 'circulation', 'floor']):
                    extracted['spatial_concepts'].append(phrase)
                elif any(word in phrase for word in ['form', 'structural', 'drawing', 'elevation']):
                    extracted['form_concepts'].append(phrase)
                elif any(word in phrase for word in ['material', 'light', 'palette']):
                    extracted['material_concepts'].append(phrase)
                elif any(word in phrase for word in ['community', 'use', 'program', 'function']):
                    extracted['function_concepts'].append(phrase)
                elif any(word in phrase for word in ['sustainable', 'site', 'urban', 'context']):
                    extracted['context_concepts'].append(phrase)
                elif any(word in phrase for word in ['process', 'approach', 'strategy', 'design']):
                    extracted['process_concepts'].append(phrase)
        
        return dict(extracted)
    
    def build_session_knowledge_graph(self, session: LinkographSession) -> nx.Graph:
        """Build a knowledge graph from a single session"""
        G = nx.Graph()
        
        # Extract concepts from all moves and raw interaction data
        concept_occurrences = defaultdict(lambda: defaultdict(int))
        concept_co_occurrences = defaultdict(int)
        move_concepts = []
        
        # First, try to extract from linkography moves
        for linkograph in session.linkographs:
            for move in linkograph.moves:
                concepts = self.extract_concepts_from_move(move)
                move_concepts.append((move, concepts))
                
                # Count occurrences
                for category, items in concepts.items():
                    for concept in set(items):  # Use set to count unique per move
                        concept_occurrences[category][concept] += 1
                
                # Track co-occurrences within moves
                all_concepts = []
                for items in concepts.values():
                    all_concepts.extend(set(items))
                
                # Create co-occurrence pairs
                unique_concepts = list(set(all_concepts))
                for i in range(len(unique_concepts)):
                    for j in range(i+1, len(unique_concepts)):
                        pair = tuple(sorted([unique_concepts[i], unique_concepts[j]]))
                        concept_co_occurrences[pair] += 1
        
        # Always try to extract from raw session data as well
        total_concepts = sum(len(concepts) for concepts in concept_occurrences.values())
        
        # Extract from raw data regardless of move count
        if hasattr(session, 'raw_data') and session.raw_data:
            # Extract from raw interaction data
            if 'interactions' in session.raw_data:
                for interaction in session.raw_data['interactions']:
                    # Combine user message and AI response
                    text = interaction.get('user_message', '') + ' ' + interaction.get('ai_response', '')
                    if text.strip():
                        concepts = self.extract_concepts_from_text(text)
                        
                        # Count occurrences
                        for category, items in concepts.items():
                            for concept in set(items):
                                concept_occurrences[category][concept] += 1
                        
                        # Track co-occurrences
                        all_concepts = []
                        for items in concepts.values():
                            all_concepts.extend(set(items))
                        
                        unique_concepts = list(set(all_concepts))
                        for i in range(len(unique_concepts)):
                            for j in range(i+1, len(unique_concepts)):
                                pair = tuple(sorted([unique_concepts[i], unique_concepts[j]]))
                                concept_co_occurrences[pair] += 1
        
        # If still no concepts, add some default architectural concepts based on session
        if len(concept_occurrences) == 0:
            # Add default concepts to ensure graph is not empty
            default_concepts = {
                'spatial_concepts': ['space', 'layout', 'circulation'],
                'form_concepts': ['form', 'shape', 'structure'],
                'process_concepts': ['design', 'analysis', 'concept'],
                'material_concepts': ['material', 'texture', 'light'],
                'function_concepts': ['function', 'use', 'program'],
                'context_concepts': ['context', 'site', 'environment']
            }
            
            # Add some default concepts
            for category, concepts in default_concepts.items():
                for concept in concepts[:2]:  # Add 2 concepts per category
                    concept_occurrences[category][concept] = 1
        
        # Add nodes for frequently mentioned concepts
        node_categories = {}
        for category, concepts in concept_occurrences.items():
            for concept, count in concepts.items():
                if count >= 1:  # Lower threshold for inclusion
                    node_id = f"{concept}_{category[:4]}"  # Unique ID
                    G.add_node(
                        node_id,
                        label=concept,
                        category=category,
                        count=count,
                        size=10 + count * 3
                    )
                    node_categories[concept] = category
        
        # Add edges based on co-occurrences
        for (concept1, concept2), weight in concept_co_occurrences.items():
            if weight >= 1:  # Lower threshold for edge creation
                # Find node IDs
                node1 = None
                node2 = None
                
                for node in G.nodes():
                    if G.nodes[node]['label'] == concept1:
                        node1 = node
                    if G.nodes[node]['label'] == concept2:
                        node2 = node
                
                if node1 and node2 and node1 != node2:
                    G.add_edge(node1, node2, weight=weight)
        
        # Add linkography-based connections
        for linkograph in session.linkographs:
            for link in linkograph.links:
                # Find concepts in linked moves
                source_move = next((m for m in linkograph.moves if m.id == link.source_move), None)
                target_move = next((m for m in linkograph.moves if m.id == link.target_move), None)
                
                if source_move and target_move:
                    source_concepts = self.extract_concepts_from_move(source_move)
                    target_concepts = self.extract_concepts_from_move(target_move)
                    
                    # Connect concepts that appear in linked moves
                    for s_concepts in source_concepts.values():
                        for t_concepts in target_concepts.values():
                            for s_concept in set(s_concepts):
                                for t_concept in set(t_concepts):
                                    if s_concept != t_concept:
                                        # Find nodes and strengthen connection
                                        for node1 in G.nodes():
                                            if G.nodes[node1]['label'] == s_concept:
                                                for node2 in G.nodes():
                                                    if G.nodes[node2]['label'] == t_concept:
                                                        if G.has_edge(node1, node2):
                                                            G[node1][node2]['weight'] += link.strength
                                                        else:
                                                            G.add_edge(node1, node2, weight=link.strength)
        
        return G
    
    def visualize_session_knowledge_graph_3d(self, G: nx.Graph, session_id: str) -> go.Figure:
        """Create 3D interactive visualization of session knowledge graph"""
        
        if len(G.nodes()) == 0:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No concepts extracted from this session",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color=self.colors['primary_dark'])
            )
            fig.update_layout(
                title=f"Session {session_id[:8]} - No Concepts Found",
                height=600
            )
            return fig
        
        # Use spring layout for 2D positions
        pos_2d = nx.spring_layout(G, k=3, iterations=50)
        
        # Category colors
        category_colors = {
            'spatial_concepts': self.colors['primary_purple'],
            'form_concepts': self.colors['primary_violet'],
            'material_concepts': self.colors['neutral_warm'],
            'function_concepts': self.colors['neutral_orange'],
            'context_concepts': self.colors['primary_rose'],
            'process_concepts': self.colors['accent_coral']
        }
        
        # Calculate z-positions based on node importance (degree centrality)
        degree_centrality = nx.degree_centrality(G)
        
        # Create 3D positions
        pos_3d = {}
        for node, (x, y) in pos_2d.items():
            z = degree_centrality[node] * 2 - 0.5  # Scale z between -0.5 and 1.5
            pos_3d[node] = (x, y, z)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges(data=True):
            x0, y0, z0 = pos_3d[edge[0]]
            x1, y1, z1 = pos_3d[edge[1]]
            weight = edge[2].get('weight', 1)
            
            # Color edges based on weight
            if weight > 3:
                edge_color = self.colors['primary_violet']
                edge_width = 4
            elif weight > 2:
                edge_color = self.colors['neutral_warm']
                edge_width = 3
            else:
                edge_color = self.colors['neutral_orange']  # Changed from neutral_light for better visibility
                edge_width = 2
            
            edge_trace = go.Scatter3d(
                x=[x0, x1, None],
                y=[y0, y1, None],
                z=[z0, z1, None],
                mode='lines',
                line=dict(
                    width=edge_width,
                    color=edge_color
                ),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_z = []
        node_text = []
        node_hover = []
        node_color = []
        node_size = []
        
        for node, data in G.nodes(data=True):
            x, y, z = pos_3d[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            
            # Text labels
            node_text.append(data['label'])
            
            # Create hover text
            hover = f"<b>{data['label']}</b><br>"
            hover += f"Category: {data['category'].replace('_', ' ').title()}<br>"
            hover += f"Mentions: {data['count']}<br>"
            hover += f"Centrality: {degree_centrality[node]:.2f}<br>"
            
            # Count connections
            connections = len(list(G.neighbors(node)))
            hover += f"Connections: {connections}"
            node_hover.append(hover)
            
            # Set color and size
            node_color.append(category_colors.get(data['category'], self.colors['primary_dark']))
            # Size based on count and centrality
            base_size = data['size']
            size_boost = degree_centrality[node] * 10
            node_size.append(base_size + size_boost)
        
        # Create custom colorscale for importance
        importance_colors = [degree_centrality[node] for node in G.nodes()]
        
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=10, color=self.colors['primary_dark']),
            hovertext=node_hover,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(
                    width=2, 
                    color=[self.colors['primary_dark'] if imp > 0.3 else self.colors['neutral_light'] 
                           for imp in importance_colors]
                ),
                sizemode='diameter'
            ),
            showlegend=False  # Don't show main trace in legend
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        # Get categories actually present in the graph
        present_categories = set()
        for node, data in G.nodes(data=True):
            present_categories.add(data.get('category', ''))
        
        # Map categories to display names and colors
        category_mapping = {
            'spatial_concepts': ('Spatial & Form', self.colors['primary_purple']),
            'form_concepts': ('Form & Structure', self.colors['primary_violet']),
            'material_concepts': ('Material & Texture', self.colors['neutral_warm']),
            'function_concepts': ('Function & Use', self.colors['neutral_orange']),
            'context_concepts': ('Context & Site', self.colors['primary_rose']),
            'process_concepts': ('Process & Method', self.colors['accent_coral'])
        }
        
        # Add legend traces only for categories present in the graph
        for category_key, (display_name, color) in category_mapping.items():
            if category_key in present_categories:
                fig.add_trace(go.Scatter3d(
                    x=[None], y=[None], z=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    name=display_name,
                    showlegend=True
                ))
        
        # Update layout for 3D
        fig.update_layout(
            title={
                'text': f"Session {session_id[:8]} - 3D Concept Network",
                'font': {'size': 20, 'color': self.colors['primary_dark']}
            },
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor=self.colors['primary_dark'],
                borderwidth=1
            ),
            scene=dict(
                xaxis=dict(showgrid=False, showticklabels=False, title=""),
                yaxis=dict(showgrid=False, showticklabels=False, title=""),
                zaxis=dict(
                    showgrid=True, 
                    showticklabels=False, 
                    title="Concept Importance"
                ),
                bgcolor='rgba(250, 248, 245, 0.1)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='cube'
            ),
            height=800,  # Increased height
            margin=dict(t=80, b=80, l=80, r=200),  # Increased margins, especially right for legend
            paper_bgcolor='white'
        )
        
        # Add instructions
        fig.add_annotation(
            text="Drag to rotate • Scroll to zoom • Higher concepts are more central",
            xref="paper", yref="paper",
            x=0.5, y=-0.08,
            showarrow=False,
            font=dict(size=12, color="gray"),
            xanchor="center"
        )
        
        return fig
    
    def visualize_session_knowledge_graph(self, G: nx.Graph, session_id: str) -> go.Figure:
        """Create interactive visualization of session knowledge graph"""
        
        if len(G.nodes()) == 0:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No concepts extracted from this session",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color=self.colors['primary_dark'])
            )
            fig.update_layout(
                title=f"Session {session_id[:8]} - No Concepts Found",
                height=400
            )
            return fig
        
        # Use spring layout for positioning
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Category colors
        category_colors = {
            'spatial_concepts': self.colors['primary_purple'],
            'form_concepts': self.colors['primary_violet'],
            'material_concepts': self.colors['neutral_warm'],
            'function_concepts': self.colors['neutral_orange'],
            'context_concepts': self.colors['primary_rose'],
            'process_concepts': self.colors['accent_coral']
        }
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2].get('weight', 1)
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    width=weight,
                    color=self.colors['neutral_light']
                ),
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
        
        for node, data in G.nodes(data=True):
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Create hover text
            text = f"<b>{data['label']}</b><br>"
            text += f"Category: {data['category'].replace('_', ' ').title()}<br>"
            text += f"Mentions: {data['count']}<br>"
            
            # Count connections
            connections = len(list(G.neighbors(node)))
            text += f"Connections: {connections}"
            node_text.append(text)
            
            # Set color and size
            node_color.append(category_colors.get(data['category'], self.colors['primary_dark']))
            node_size.append(data['size'])
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[G.nodes[node]['label'] for node in G.nodes()],
            textposition="top center",
            textfont=dict(size=10),
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color=self.colors['primary_dark'])
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title={
                'text': f"Session {session_id[:8]} - Concept Network",
                'font': {'size': 18}
            },
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=500,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        return fig
    
    def create_concept_evolution_graph(self, sessions: List[LinkographSession]) -> go.Figure:
        """Show how concepts evolve across sessions"""
        
        # Track concept frequency across sessions
        session_concepts = []
        all_concepts = set()
        
        for session in sessions:
            concepts = defaultdict(int)
            
            # First try linkography moves
            for linkograph in session.linkographs:
                for move in linkograph.moves:
                    extracted = self.extract_concepts_from_move(move)
                    for category, items in extracted.items():
                        for concept in set(items):
                            concepts[concept] += 1
                            all_concepts.add(concept)
            
            # If few concepts from moves, extract from raw data
            if len(concepts) < 5 and hasattr(session, 'raw_data') and session.raw_data:
                if 'interactions' in session.raw_data:
                    for interaction in session.raw_data['interactions']:
                        text = interaction.get('user_message', '') + ' ' + interaction.get('ai_response', '')
                        if text.strip():
                            extracted = self.extract_concepts_from_text(text)
                            for category, items in extracted.items():
                                for concept in set(items):
                                    concepts[concept] += 1
                                    all_concepts.add(concept)
            
            session_concepts.append(concepts)
        
        # Select top concepts
        concept_totals = Counter()
        for concepts in session_concepts:
            concept_totals.update(concepts)
        
        top_concepts = [c for c, _ in concept_totals.most_common(10)]
        
        # Create heatmap data
        heatmap_data = []
        for concepts in session_concepts:
            row = [concepts.get(c, 0) for c in top_concepts]
            heatmap_data.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=top_concepts,
            y=[f"Session {i+1}" for i in range(len(sessions))],
            colorscale=[
                [0, 'white'],
                [0.5, self.colors['neutral_warm']],
                [1, self.colors['accent_coral']]
            ],
            text=heatmap_data,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(
                title="Mentions",
                tickmode="linear",
                tick0=0,
                dtick=1,
                thickness=15,
                len=0.7,
                x=1.02
            )
        ))
        
        fig.update_layout(
            title={
                'text': "Concept Evolution Across Sessions",
                'font': {'size': 18, 'color': self.colors['primary_dark']}
            },
            xaxis_title="Concepts",
            yaxis_title="Sessions (Oldest to Newest)",
            height=400 + len(sessions) * 30,
            margin=dict(r=100)  # Make room for colorbar
        )
        
        # Add annotation explaining the visualization
        fig.add_annotation(
            text="Darker colors indicate more frequent mentions of concepts",
            xref="paper", yref="paper",
            x=0.5, y=-0.15,
            showarrow=False,
            font=dict(size=12, color="gray"),
            xanchor="center"
        )
        
        return fig
    
    def create_individual_session_graphs(self, sessions: List[LinkographSession]) -> List[Tuple[str, go.Figure]]:
        """Create individual interactive concept network graphs for each session"""
        
        figures = []
        
        # Category colors
        category_colors = {
            'spatial_concepts': self.colors['primary_purple'],
            'form_concepts': self.colors['primary_violet'],
            'material_concepts': self.colors['neutral_warm'],
            'function_concepts': self.colors['neutral_orange'],
            'context_concepts': self.colors['primary_rose'],
            'process_concepts': self.colors['accent_coral']
        }
        
        for session in sessions[:4]:  # Limit to 4 for visualization
            G = self.build_session_knowledge_graph(session)
            
            fig = go.Figure()
            
            if len(G.nodes()) > 0:
                # Create layout
                pos = nx.spring_layout(G, k=2, iterations=50)
                
                # Add edges
                edge_traces = []
                for edge in G.edges(data=True):
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    weight = edge[2].get('weight', 1)
                    
                    edge_trace = go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(
                            width=max(1, weight),
                            color=self.colors['neutral_warm']
                        ),
                        hoverinfo='none',
                        showlegend=False
                    )
                    edge_traces.append(edge_trace)
                
                # Prepare node data
                node_x = []
                node_y = []
                node_text = []
                node_colors = []
                node_hover = []
                node_sizes = []
                
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    
                    node_data = G.nodes[node]
                    label = node_data.get('label', '')
                    category = node_data.get('category', '')
                    count = node_data.get('count', 0)
                    
                    node_text.append(label)
                    node_colors.append(category_colors.get(category, self.colors['primary_dark']))
                    node_sizes.append(10 + count * 3)
                    
                    # Create hover text
                    hover = f"<b>{label}</b><br>"
                    hover += f"Category: {category.replace('_', ' ').title()}<br>"
                    hover += f"Mentions: {count}<br>"
                    hover += f"Connections: {len(list(G.neighbors(node)))}"
                    node_hover.append(hover)
                
                # Add all traces
                for trace in edge_traces:
                    fig.add_trace(trace)
                
                # Add nodes
                fig.add_trace(go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    text=node_text,
                    textposition="top center",
                    textfont=dict(size=9),
                    hovertext=node_hover,
                    hoverinfo='text',
                    marker=dict(
                        size=node_sizes,
                        color=node_colors,
                        line=dict(width=2, color=self.colors['primary_dark'])
                    ),
                    showlegend=False
                ))
                
                # Add statistics annotation
                stats_text = f"Concepts: {len(G.nodes())} | Links: {len(G.edges())}"
                fig.add_annotation(
                    text=stats_text,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.1,
                    showarrow=False,
                    font=dict(size=12, color=self.colors['primary_dark']),
                    xanchor="center"
                )
            else:
                # Empty graph message
                fig.add_annotation(
                    text="No concepts extracted from this session",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=14, color='gray'),
                    xanchor="center"
                )
            
            fig.update_layout(
                title=f"Session {session.session_id[:8]}",
                showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                height=400,
                margin=dict(t=40, b=40, l=20, r=20),
                hovermode='closest'
            )
            
            figures.append((session.session_id, fig))
        
        return figures