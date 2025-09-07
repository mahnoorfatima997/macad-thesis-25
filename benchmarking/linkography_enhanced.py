"""
MEGA Architectural Mentor - Enhanced Linkography with Intersection Nodes
Complete implementation including intersection detection and critical move analysis
Based on Goldschmidt's linkography methodology
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import math

from linkography_types import Linkograph, DesignMove, LinkographLink, LinkographPattern
from thesis_colors import THESIS_COLORS
from linkography_intersection_cache import (
    find_arc_intersection_cached, 
    check_arcs_cross_cached,
    clear_intersection_cache
)


@dataclass
class IntersectionNode:
    """Represents an intersection point where links cross"""
    position: Tuple[float, float]  # (x, y) coordinates
    links: List[Tuple[str, str]]  # List of (source_id, target_id) pairs
    complexity: int  # Number of intersecting links
    cognitive_significance: float  # Calculated significance score
    
    def calculate_significance(self, link_strengths: Dict[Tuple[str, str], float]) -> float:
        """Calculate cognitive significance based on link strengths"""
        total_strength = sum(link_strengths.get((s, t), 0.5) for s, t in self.links)
        return total_strength * math.log(1 + self.complexity)


class EnhancedLinkographVisualizer:
    """Enhanced linkography visualization with intersection nodes and advanced features"""
    
    def __init__(self):
        self.colors = THESIS_COLORS
        # Extended color gradient for link strengths (8 levels)
        self.link_strength_colors = [
            THESIS_COLORS['neutral_light'],    # 0.0-0.125
            THESIS_COLORS['neutral_warm'],      # 0.125-0.25  
            THESIS_COLORS['primary_pink'],      # 0.25-0.375
            THESIS_COLORS['primary_rose'],      # 0.375-0.5
            THESIS_COLORS['primary_violet'],    # 0.5-0.625
            THESIS_COLORS['primary_purple'],    # 0.625-0.75
            THESIS_COLORS['primary_dark'],      # 0.75-0.875
            THESIS_COLORS['primary_dark']       # 0.875-1.0
        ]
        
    def create_enhanced_linkograph(self,
                                  linkograph: Linkograph,
                                  show_intersections: bool = True,
                                  show_critical_moves: bool = True,
                                  show_patterns: bool = True,
                                  patterns: Optional[List[LinkographPattern]] = None,
                                  interactive: bool = True) -> go.Figure:
        """
        Create enhanced triangular linkograph with intersection nodes.
        
        Args:
            linkograph: The linkograph to visualize
            show_intersections: Whether to show intersection nodes
            show_critical_moves: Whether to highlight critical moves
            show_patterns: Whether to show detected patterns
            patterns: Optional list of patterns to highlight
            interactive: Whether to enable interactivity
            
        Returns:
            Plotly figure object
        """
        moves = linkograph.moves
        links = linkograph.links
        n_moves = len(moves)
        
        if n_moves == 0:
            return self._create_empty_figure("No moves to display")
        
        # Create figure
        fig = go.Figure()
        
        # Calculate move positions on horizontal line
        move_positions = [(i, 0) for i in range(n_moves)]
        
        # Calculate link arcs and find intersections
        link_paths = {}
        link_strengths = {}
        
        for link in links:
            source_idx = self._get_move_index(link.source_move, moves)
            target_idx = self._get_move_index(link.target_move, moves)
            
            if source_idx is None or target_idx is None or source_idx == target_idx:
                continue
            
            # Store link path for intersection calculation
            link_key = (link.source_move, link.target_move)
            link_paths[link_key] = (source_idx, target_idx)
            link_strengths[link_key] = link.strength
        
        # Find intersection nodes
        intersection_nodes = []
        if show_intersections:
            intersection_nodes = self._find_intersection_nodes(link_paths, link_strengths)
        
        # Draw links with enhanced styling
        self._draw_enhanced_links(fig, links, moves, link_strengths)
        
        # Draw intersection nodes (filter out very low significance ones)
        if show_intersections and intersection_nodes:
            # Only show intersection nodes with meaningful complexity
            significant_nodes = [n for n in intersection_nodes if n.complexity >= 2 or n.cognitive_significance > 0.5]
            if significant_nodes:
                self._draw_intersection_nodes(fig, significant_nodes)
        
        # Identify critical moves (always calculate for statistics, highlight only if requested)
        critical_moves = self._identify_critical_moves(linkograph)
        
        # Draw design moves with critical move highlighting (only if requested)
        critical_moves_for_display = critical_moves if show_critical_moves else {}
        self._draw_enhanced_moves(fig, moves, links, critical_moves_for_display)
        
        # Highlight patterns if requested
        if show_patterns and patterns:
            self._draw_pattern_overlays(fig, patterns, moves)
        
        # Add phase regions and labels
        self._add_enhanced_phase_regions(fig, moves)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="Enhanced Linkograph with Intersection Analysis",
                font=dict(size=22, color=self.colors['primary_dark'], family='Arial')
            ),
            xaxis=dict(
                title="Design Moves (Temporal Sequence)",
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=False,
                tickmode='linear',
                tick0=0,
                dtick=1 if n_moves < 20 else 5
            ),
            yaxis=dict(
                title="Link Depth & Intersections",
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.2)',
                autorange='reversed'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest' if interactive else False,
            height=700,
            margin=dict(t=100, b=100, l=80, r=80),
            dragmode='pan' if interactive else False,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add critical move and intersection statistics annotation
        self._add_statistics_annotation(fig, critical_moves, intersection_nodes, n_moves, linkograph)
        
        return fig
    
    def _find_intersection_nodes(self, 
                                 link_paths: Dict[Tuple[str, str], Tuple[int, int]], 
                                 link_strengths: Dict[Tuple[str, str], float]) -> List[IntersectionNode]:
        """Find intersection points where links cross using cached calculations"""
        intersections = []
        link_list = list(link_paths.items())
        
        for i in range(len(link_list)):
            for j in range(i + 1, len(link_list)):
                link1_key, (s1, t1) = link_list[i]
                link2_key, (s2, t2) = link_list[j]
                
                # Use cached check for whether arcs actually cross
                if check_arcs_cross_cached(s1, t1, s2, t2):
                    # Calculate intersection with caching and moderate precision
                    intersection_point = find_arc_intersection_cached(s1, t1, s2, t2, precision=300)
                    
                    if intersection_point:  # Only add if we found a real intersection
                        # Check if we already have an intersection very close to this point
                        existing = None
                        for node in intersections:
                            dist = math.sqrt((node.position[0] - intersection_point[0])**2 + 
                                           (node.position[1] - intersection_point[1])**2)
                            if dist < 0.1:  # Threshold for considering points the same
                                existing = node
                                break
                        
                        if existing:
                            # Add to existing intersection node
                            if link1_key not in existing.links:
                                existing.links.append(link1_key)
                            if link2_key not in existing.links:
                                existing.links.append(link2_key)
                            existing.complexity = len(existing.links)
                        else:
                            # Create new intersection node only for real intersections
                            node = IntersectionNode(
                                position=intersection_point,
                                links=[link1_key, link2_key],
                                complexity=2,
                                cognitive_significance=0
                            )
                            intersections.append(node)
        
        # Calculate significance for all nodes
        for node in intersections:
            node.cognitive_significance = node.calculate_significance(link_strengths)
        
        return intersections
    
    
    def _draw_enhanced_links(self, fig: go.Figure, links: List[LinkographLink], 
                            moves: List[DesignMove], link_strengths: Dict):
        """Draw links with enhanced gradient coloring"""
        for link in links:
            source_idx = self._get_move_index(link.source_move, moves)
            target_idx = self._get_move_index(link.target_move, moves)
            
            if source_idx is None or target_idx is None or source_idx == target_idx:
                continue
            
            # Calculate arc path with more points for smoother curves
            points = self._calculate_arc_points(source_idx, target_idx, num_points=20)
            
            # Get color based on enhanced gradient
            link_color = self._get_enhanced_link_color(link.strength)
            
            # Determine line width based on strength
            line_width = 0.5 + link.strength * 3
            
            # Add link arc
            fig.add_trace(go.Scatter(
                x=[p[0] for p in points],
                y=[p[1] for p in points],
                mode='lines',
                line=dict(
                    color=link_color,
                    width=line_width,
                    shape='spline'
                ),
                hovertemplate=f'Link: {link.source_move[:8]} → {link.target_move[:8]}<br>' +
                             f'Strength: {link.strength:.3f}<br>' +
                             f'Type: {link.link_type}<br>' +
                             f'Temporal Distance: {link.temporal_distance}<extra></extra>',
                showlegend=False,
                opacity=0.6 + link.strength * 0.3  # Variable opacity
            ))
    
    def _draw_intersection_nodes(self, fig: go.Figure, intersection_nodes: List[IntersectionNode]):
        """Draw intersection nodes with size based on complexity"""
        if not intersection_nodes:
            return
        
        x_coords = [node.position[0] for node in intersection_nodes]
        y_coords = [node.position[1] for node in intersection_nodes]
        # Larger sizes for better visibility - base size 6, increment by 2 per complexity level
        sizes = [6 + node.complexity * 2 for node in intersection_nodes]
        
        # Color based on significance
        max_significance = max(node.cognitive_significance for node in intersection_nodes) or 1
        colors = [node.cognitive_significance / max_significance for node in intersection_nodes]
        
        # Hover text
        hover_texts = []
        for node in intersection_nodes:
            hover_texts.append(
                f'Intersection Node<br>' +
                f'Complexity: {node.complexity} links<br>' +
                f'Significance: {node.cognitive_significance:.2f}<br>' +
                f'Position: ({node.position[0]:.1f}, {node.position[1]:.2f})'
            )
        
        # Use full color spectrum from thesis palette
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                colorscale=[
                    [0.0, self.colors['neutral_light']],    # Light beige
                    [0.14, self.colors['neutral_warm']],     # Warm sand
                    [0.28, self.colors['neutral_orange']],   # Orange
                    [0.42, self.colors['primary_pink']],     # Pink
                    [0.57, self.colors['primary_rose']],     # Rose
                    [0.71, self.colors['primary_violet']],   # Violet
                    [0.85, self.colors['primary_purple']],   # Purple
                    [1.0, self.colors['primary_dark']]       # Dark
                ],
                showscale=True,
                colorbar=dict(
                    title="Intersection<br>Significance",
                    x=1.1
                ),
                symbol='diamond',
                line=dict(color=self.colors['primary_dark'], width=0.5)
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            name='Intersection Nodes',
            legendgroup='intersections'
        ))
    
    def _identify_critical_moves(self, linkograph: Linkograph) -> Dict[str, str]:
        """
        Identify critical moves with bidirectional classification.
        Returns dict with move_id: criticality_type ('forward', 'backward', 'bidirectional')
        """
        moves = linkograph.moves
        n_moves = len(moves)
        
        if n_moves == 0:
            return {}
        
        # Dynamic threshold based on session complexity
        threshold = max(3, int(n_moves * 0.1))
        
        critical_moves = {}
        
        for move in moves:
            source_links, target_links = linkograph.get_links_for_move(move.id)
            
            # Count forelinks and backlinks
            forelinks = len([l for l in source_links if self._get_move_index(l.target_move, moves) > 
                           self._get_move_index(move.id, moves)])
            backlinks = len([l for l in target_links if self._get_move_index(l.source_move, moves) < 
                           self._get_move_index(move.id, moves)])
            
            # Classify criticality
            is_forward_critical = forelinks >= threshold
            is_backward_critical = backlinks >= threshold
            
            if is_forward_critical and is_backward_critical:
                critical_moves[move.id] = 'bidirectional'
            elif is_forward_critical:
                critical_moves[move.id] = 'forward'
            elif is_backward_critical:
                critical_moves[move.id] = 'backward'
        
        return critical_moves
    
    def _draw_enhanced_moves(self, fig: go.Figure, moves: List[DesignMove], 
                            links: List[LinkographLink], critical_moves: Dict[str, str]):
        """Draw design moves with critical move highlighting"""
        x_coords = []
        y_coords = []
        colors = []
        sizes = []
        hover_texts = []
        edge_colors = []
        edge_widths = []
        
        for i, move in enumerate(moves):
            x_coords.append(i)
            y_coords.append(0)
            
            # Determine color based on phase
            phase_color = self._get_phase_color(move.phase)
            colors.append(phase_color)
            
            # Calculate connectivity
            source_links = [l for l in links if l.source_move == move.id]
            target_links = [l for l in links if l.target_move == move.id]
            connectivity = len(source_links) + len(target_links)
            
            # Determine size and edge styling based on criticality
            # ALL moves are circles, only size and border changes
            # Making all moves larger for better visibility
            if move.id in critical_moves:
                criticality = critical_moves[move.id]
                if criticality == 'bidirectional':
                    # Largest size for bidirectional critical moves
                    sizes.append(20 + connectivity * 1.2)
                    edge_colors.append(self.colors['accent_magenta'])
                    edge_widths.append(3)
                elif criticality == 'forward':
                    # Medium-large for forward critical
                    sizes.append(16 + connectivity * 1.0)
                    edge_colors.append(self.colors['primary_dark'])
                    edge_widths.append(2.5)
                else:  # backward
                    # Medium-large for backward critical
                    sizes.append(16 + connectivity * 1.0)
                    edge_colors.append(self.colors['primary_purple'])
                    edge_widths.append(2.5)
            else:
                # Regular moves - also larger now
                sizes.append(12 + connectivity * 0.5)
                edge_colors.append(self.colors['primary_dark'])
                edge_widths.append(1)
            
            # Create hover text
            criticality_text = f"<br>CRITICAL ({critical_moves.get(move.id, '')})" if move.id in critical_moves else ""
            hover_texts.append(
                f'Move {i}: {move.id[:8]}<br>' +
                f'Phase: {move.phase}<br>' +
                f'Type: {move.move_type}<br>' +
                f'Connections: {connectivity}<br>' +
                f'Content: {move.content[:50]}...' +
                criticality_text
            )
        
        # Add all moves as a single trace with circles
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=colors,
                symbol='circle',  # ALL moves are circles
                line=dict(color=edge_colors, width=edge_widths)
            ),
            text=[str(i) for i in range(len(moves))],
            textposition='top center',
            textfont=dict(size=9, color=self.colors['primary_dark']),
            hovertext=hover_texts,
            hoverinfo='text',
            showlegend=False
        ))
    
    def _draw_pattern_overlays(self, fig: go.Figure, patterns: List[LinkographPattern], 
                              moves: List[DesignMove]):
        """Draw semi-transparent overlays for detected patterns"""
        for pattern in patterns:
            pattern_indices = []
            for move_id in pattern.moves:
                idx = self._get_move_index(move_id, moves)
                if idx is not None:
                    pattern_indices.append(idx)
            
            if pattern_indices:
                min_idx = min(pattern_indices)
                max_idx = max(pattern_indices)
                
                # Get pattern color
                pattern_color = self._get_pattern_color(pattern.pattern_type)
                
                # Add semi-transparent rectangle
                fig.add_shape(
                    type="rect",
                    x0=min_idx - 0.3,
                    x1=max_idx + 0.3,
                    y0=-10,
                    y1=0.5,
                    fillcolor=pattern_color,
                    opacity=0.15,
                    layer="below",
                    line=dict(
                        color=pattern_color,
                        width=2,
                        dash="dash"
                    )
                )
                
                # Add pattern label
                fig.add_annotation(
                    x=(min_idx + max_idx) / 2,
                    y=-9,
                    text=f"{pattern.pattern_type.upper()}<br>Strength: {pattern.strength:.2f}",
                    showarrow=False,
                    font=dict(size=10, color=pattern_color),
                    bgcolor="white",
                    opacity=0.8
                )
    
    def _add_enhanced_phase_regions(self, fig: go.Figure, moves: List[DesignMove]):
        """Add colored background regions for design phases with labels"""
        if not moves:
            return
        
        current_phase = moves[0].phase
        phase_start = 0
        
        for i, move in enumerate(moves + [None]):
            if move is None or move.phase != current_phase:
                # Add background shape
                fig.add_shape(
                    type="rect",
                    x0=phase_start - 0.5,
                    x1=(i - 1) + 0.5 if i > 0 else 0.5,
                    y0=-10,
                    y1=1,
                    fillcolor=self._get_phase_color(current_phase),
                    opacity=0.08,
                    layer="below",
                    line_width=0
                )
                
                # Add phase label at top
                fig.add_annotation(
                    x=(phase_start + i - 1) / 2 if i > 0 else phase_start,
                    y=0.8,
                    text=current_phase.upper(),
                    showarrow=False,
                    font=dict(
                        size=12,
                        color=self._get_phase_color(current_phase),
                        family="Arial Black"
                    ),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor=self._get_phase_color(current_phase),
                    borderwidth=1
                )
                
                if move is not None:
                    current_phase = move.phase
                    phase_start = i
    
    def _add_statistics_annotation(self, fig: go.Figure, critical_moves: Dict[str, str], 
                                  intersection_nodes: List[IntersectionNode], n_moves: int, linkograph):
        """Add statistics box with key metrics"""
        # CALCULATE CRITICAL MOVES DIRECTLY HERE - FUCK THE BROKEN FLOW
        actual_critical_moves = self._identify_critical_moves(linkograph)
        
        forward_critical = len([m for m in actual_critical_moves.values() if m == 'forward'])
        backward_critical = len([m for m in actual_critical_moves.values() if m == 'backward'])
        bidirectional_critical = len([m for m in actual_critical_moves.values() if m == 'bidirectional'])
        
        total_intersections = len(intersection_nodes)
        avg_complexity = np.mean([n.complexity for n in intersection_nodes]) if intersection_nodes else 0
        
        stats_text = (
            f"<b>Linkograph Statistics</b><br>" +
            f"Total Moves: {n_moves}<br>" +
            f"Critical Moves: {len(actual_critical_moves)} ({len(actual_critical_moves)/n_moves*100:.1f}%)<br>" +
            f"  • Forward: {forward_critical}<br>" +
            f"  • Backward: {backward_critical}<br>" +
            f"  • Bidirectional: {bidirectional_critical}<br>" +
            f"Intersection Nodes: {total_intersections}<br>" +
            f"Avg Intersection Complexity: {avg_complexity:.1f}"
        )
        
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.98,
            text=stats_text,
            showarrow=False,
            font=dict(size=11, family="monospace"),
            align="left",
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=self.colors['primary_dark'],
            borderwidth=1,
            borderpad=8
        )
    
    def _calculate_arc_points(self, source: int, target: int, num_points: int = 20) -> List[Tuple[float, float]]:
        """Calculate points along a parabolic arc between two moves"""
        points = []
        distance = abs(target - source)
        depth = -distance * 0.5  # Arc depth proportional to distance
        
        for i in range(num_points + 1):
            t = i / num_points
            x = source + (target - source) * t
            # Parabolic arc equation
            y = 4 * depth * t * (1 - t)
            points.append((x, y))
        
        return points
    
    def _get_enhanced_link_color(self, strength: float) -> str:
        """Get color from enhanced 8-level gradient based on link strength"""
        index = min(int(strength * 8), 7)
        return self.link_strength_colors[index]
    
    def _get_phase_color(self, phase: str) -> str:
        """Get color for design phase"""
        phase_colors = {
            'ideation': self.colors['accent_coral'],
            'visualization': self.colors['neutral_orange'],
            'materialization': self.colors['primary_violet']
        }
        return phase_colors.get(phase, self.colors['neutral_warm'])
    
    def _get_pattern_color(self, pattern_type: str) -> str:
        """Get color for pattern type"""
        pattern_colors = {
            'chunk': self.colors['primary_purple'],
            'web': self.colors['primary_violet'],
            'sawtooth': self.colors['neutral_warm'],
            'orphan': self.colors['accent_coral']
        }
        return pattern_colors.get(pattern_type, self.colors['neutral_light'])
    
    def _get_move_index(self, move_id: str, moves: List[DesignMove]) -> Optional[int]:
        """Get the index of a move by its ID"""
        for i, move in enumerate(moves):
            if move.id == move_id:
                return i
        return None
    
    def _create_empty_figure(self, message: str) -> go.Figure:
        """Create an empty figure with a message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color=self.colors['primary_dark'])
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig


def create_breakthrough_detection_chart(linkograph: Linkograph) -> go.Figure:
    """
    Create a chart showing breakthrough moments in the design process.
    Breakthrough moments are identified by sudden increases in link density.
    """
    moves = linkograph.moves
    n_moves = len(moves)
    
    if n_moves < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough moves for breakthrough detection",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Calculate rolling link density
    window_size = min(3, n_moves // 3)
    densities = []
    positions = []
    
    for i in range(n_moves - window_size + 1):
        window_moves = moves[i:i + window_size]
        window_ids = [m.id for m in window_moves]
        
        # Count links in window
        window_links = [
            link for link in linkograph.links
            if link.source_move in window_ids or link.target_move in window_ids
        ]
        
        density = len(window_links) / window_size
        densities.append(density)
        positions.append(i + window_size // 2)
    
    # Detect breakthroughs (>150% increase)
    breakthroughs = []
    for i in range(1, len(densities)):
        if densities[i-1] > 0 and densities[i] / densities[i-1] > 1.5:
            breakthroughs.append((positions[i], densities[i]))
    
    # Create figure
    fig = go.Figure()
    
    # Add density line
    fig.add_trace(go.Scatter(
        x=positions,
        y=densities,
        mode='lines+markers',
        name='Link Density',
        line=dict(color=THESIS_COLORS['primary_violet'], width=2),
        marker=dict(size=6)
    ))
    
    # Mark breakthroughs
    if breakthroughs:
        fig.add_trace(go.Scatter(
            x=[b[0] for b in breakthroughs],
            y=[b[1] for b in breakthroughs],
            mode='markers',
            name='Breakthrough Moments',
            marker=dict(
                size=15,
                color=THESIS_COLORS['accent_magenta'],
                symbol='star',
                line=dict(color=THESIS_COLORS['primary_dark'], width=2)
            )
        ))
    
    fig.update_layout(
        title="Breakthrough Moment Detection",
        xaxis_title="Design Move Position",
        yaxis_title="Link Density",
        height=400,
        showlegend=True
    )
    
    return fig