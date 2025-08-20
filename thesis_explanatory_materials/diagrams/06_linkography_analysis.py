"""
Linkography Analysis Visualization Generator
Creates visual representation explaining design move analysis and linkography patterns
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_linkography_analysis_diagram():
    """Create comprehensive linkography analysis visualization"""
    
    # Create figure with subplots for different aspects
    fig = plt.figure(figsize=(18, 14))
    
    # Create subplot layout
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1.5, 1], width_ratios=[1, 1, 1], 
                         hspace=0.3, wspace=0.2)
    
    # Main linkography example (center large plot)
    ax_main = fig.add_subplot(gs[1, :])
    
    # Design moves sequence (top)
    ax_moves = fig.add_subplot(gs[0, :])
    
    # Analysis components (bottom)
    ax_analysis = fig.add_subplot(gs[2, :])
    
    # ===== MAIN LINKOGRAPHY DIAGRAM =====
    
    # Define design moves for a sample session
    moves = [
        {'id': 1, 'text': 'Initial Problem\nStatement', 'type': 'problem', 'pos': (1, 4)},
        {'id': 2, 'text': 'Site Analysis\nRequest', 'type': 'analysis', 'pos': (2, 4)},
        {'id': 3, 'text': 'Climate\nConsiderations', 'type': 'knowledge', 'pos': (3, 4)},
        {'id': 4, 'text': 'Spatial Program\nDefinition', 'type': 'synthesis', 'pos': (4, 4)},
        {'id': 5, 'text': 'Form Generation\nIdeas', 'type': 'generation', 'pos': (5, 4)},
        {'id': 6, 'text': 'Material\nSelection', 'type': 'specification', 'pos': (6, 4)},
        {'id': 7, 'text': 'Structural\nConsiderations', 'type': 'analysis', 'pos': (7, 4)},
        {'id': 8, 'text': 'Environmental\nIntegration', 'type': 'synthesis', 'pos': (8, 4)},
        {'id': 9, 'text': 'Design\nRefinement', 'type': 'evaluation', 'pos': (9, 4)},
        {'id': 10, 'text': 'Final\nProposal', 'type': 'presentation', 'pos': (10, 4)},
    ]
    
    # Define move type colors
    move_colors = {
        'problem': THESIS_COLORS['accent_coral'],
        'analysis': THESIS_COLORS['primary_violet'],
        'knowledge': THESIS_COLORS['neutral_warm'],
        'synthesis': THESIS_COLORS['primary_rose'],
        'generation': THESIS_COLORS['accent_magenta'],
        'specification': THESIS_COLORS['primary_pink'],
        'evaluation': THESIS_COLORS['neutral_orange'],
        'presentation': THESIS_COLORS['primary_dark']
    }
    
    # Draw design moves
    for move in moves:
        x, y = move['pos']
        color = move_colors[move['type']]
        
        # Move box
        box = FancyBboxPatch(
            (x - 0.4, y - 0.4), 0.8, 0.8,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor='white', linewidth=2, alpha=0.8
        )
        ax_main.add_patch(box)
        
        # Move number
        circle = Circle((x - 0.3, y + 0.3), 0.12, facecolor='white', 
                       edgecolor=color, linewidth=2)
        ax_main.add_patch(circle)
        ax_main.text(x - 0.3, y + 0.3, str(move['id']), ha='center', va='center',
                    fontsize=8, fontweight='bold', color=color)
        
        # Move text
        ax_main.text(x, y - 0.1, move['text'], ha='center', va='center',
                    fontsize=8, fontweight='bold', color='white')
    
    # Define linkography connections (design links)
    links = [
        # Backward links (solid lines)
        {'from': 2, 'to': 1, 'type': 'backward', 'strength': 'strong'},
        {'from': 3, 'to': 2, 'type': 'backward', 'strength': 'medium'},
        {'from': 4, 'to': 1, 'type': 'backward', 'strength': 'strong'},
        {'from': 4, 'to': 3, 'type': 'backward', 'strength': 'medium'},
        {'from': 5, 'to': 4, 'type': 'backward', 'strength': 'strong'},
        {'from': 6, 'to': 5, 'type': 'backward', 'strength': 'medium'},
        {'from': 7, 'to': 6, 'type': 'backward', 'strength': 'strong'},
        {'from': 7, 'to': 4, 'type': 'backward', 'strength': 'medium'},
        {'from': 8, 'to': 7, 'type': 'backward', 'strength': 'strong'},
        {'from': 8, 'to': 3, 'type': 'backward', 'strength': 'weak'},
        {'from': 9, 'to': 8, 'type': 'backward', 'strength': 'strong'},
        {'from': 9, 'to': 5, 'type': 'backward', 'strength': 'medium'},
        {'from': 10, 'to': 9, 'type': 'backward', 'strength': 'strong'},
        
        # Forward links (dashed lines)
        {'from': 1, 'to': 4, 'type': 'forward', 'strength': 'strong'},
        {'from': 3, 'to': 8, 'type': 'forward', 'strength': 'medium'},
        {'from': 5, 'to': 9, 'type': 'forward', 'strength': 'medium'},
    ]
    
    # Draw links
    for link in links:
        from_move = next(m for m in moves if m['id'] == link['from'])
        to_move = next(m for m in moves if m['id'] == link['to'])
        
        from_pos = from_move['pos']
        to_pos = to_move['pos']
        
        # Link styling based on type and strength
        if link['type'] == 'backward':
            linestyle = '-'
            color = THESIS_COLORS['primary_dark']
        else:  # forward
            linestyle = '--'
            color = THESIS_COLORS['accent_magenta']
        
        if link['strength'] == 'strong':
            linewidth = 3
            alpha = 0.8
        elif link['strength'] == 'medium':
            linewidth = 2
            alpha = 0.6
        else:  # weak
            linewidth = 1
            alpha = 0.4
        
        # Draw curved connection
        if from_pos[0] < to_pos[0]:  # Forward in time
            arc_height = 0.3 + 0.2 * abs(to_pos[0] - from_pos[0])
            connectionstyle = f"arc3,rad={arc_height}"
        else:  # Backward in time
            arc_height = -(0.3 + 0.2 * abs(to_pos[0] - from_pos[0]))
            connectionstyle = f"arc3,rad={arc_height}"
        
        arrow = FancyArrowPatch(
            from_pos, to_pos,
            arrowstyle='->', mutation_scale=15,
            color=color, linewidth=linewidth, alpha=alpha,
            linestyle=linestyle,
            connectionstyle=connectionstyle
        )
        ax_main.add_patch(arrow)
    
    # Identify and highlight critical moves (moves with many connections)
    move_connections = {}
    for link in links:
        move_connections[link['from']] = move_connections.get(link['from'], 0) + 1
        move_connections[link['to']] = move_connections.get(link['to'], 0) + 1
    
    # Highlight critical moves (>3 connections)
    for move in moves:
        connections = move_connections.get(move['id'], 0)
        if connections > 3:
            x, y = move['pos']
            # Critical move indicator
            star_points = []
            for i in range(5):
                angle = i * 4 * np.pi / 5
                if i % 2 == 0:
                    r = 0.15
                else:
                    r = 0.07
                star_points.append((x + r * np.cos(angle), y + 0.5 + r * np.sin(angle)))
            
            star = Polygon(star_points, facecolor=THESIS_COLORS['accent_magenta'],
                          edgecolor='white', linewidth=1)
            ax_main.add_patch(star)
    
    # ===== DESIGN MOVES SEQUENCE (TOP) =====
    
    # Timeline visualization
    timeline_y = 0.5
    ax_moves.axhline(y=timeline_y, color=THESIS_COLORS['primary_dark'], linewidth=3)
    
    # Move types legend and timeline points
    move_types = list(set(move['type'] for move in moves))
    for i, move_type in enumerate(move_types):
        color = move_colors[move_type]
        # Legend
        ax_moves.scatter(0.5, 0.8 - i*0.15, c=color, s=100, alpha=0.8)
        ax_moves.text(0.7, 0.8 - i*0.15, move_type.title(), va='center', fontsize=9,
                     color=THESIS_COLORS['primary_dark'], fontweight='bold')
    
    # Timeline points for each move
    for move in moves:
        x = move['id']
        color = move_colors[move['type']]
        ax_moves.scatter(x, timeline_y, c=color, s=150, alpha=0.8, edgecolor='white', linewidth=2)
        ax_moves.text(x, timeline_y - 0.2, f"M{move['id']}", ha='center', va='center',
                     fontsize=8, fontweight='bold', color=THESIS_COLORS['primary_dark'])
    
    ax_moves.text(5.5, 0.9, 'Design Moves Sequence & Classification', ha='center', va='center',
                 fontsize=14, fontweight='bold', color=THESIS_COLORS['primary_dark'])
    
    # ===== ANALYSIS COMPONENTS (BOTTOM) =====
    
    # Linkography metrics visualization
    metrics_data = {
        'Link Density': 0.65,
        'Critical Moves': 0.3,
        'Orphan Moves': 0.1,
        'Web Formation': 0.4,
        'Cognitive Flow': 0.7
    }
    
    # Metrics bars
    bar_width = 0.6
    x_positions = np.arange(len(metrics_data))
    colors = [THESIS_COLORS['primary_violet'], THESIS_COLORS['accent_magenta'], 
              THESIS_COLORS['accent_coral'], THESIS_COLORS['primary_rose'],
              THESIS_COLORS['primary_dark']]
    
    bars = ax_analysis.bar(x_positions, list(metrics_data.values()), 
                          width=bar_width, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    
    # Add value labels on bars
    for i, (metric, value) in enumerate(metrics_data.items()):
        ax_analysis.text(i, value + 0.02, f'{value:.2f}', ha='center', va='bottom',
                        fontweight='bold', fontsize=10, color=THESIS_COLORS['primary_dark'])
    
    ax_analysis.set_xticks(x_positions)
    ax_analysis.set_xticklabels(metrics_data.keys(), rotation=45, ha='right')
    ax_analysis.set_ylabel('Metric Score', fontweight='bold', color=THESIS_COLORS['primary_dark'])
    ax_analysis.set_title('Linkography Analysis Metrics', fontweight='bold', 
                         color=THESIS_COLORS['primary_dark'], fontsize=12)
    ax_analysis.set_ylim(0, 1)
    ax_analysis.grid(True, alpha=0.3)
    
    # Set axis properties for all subplots
    ax_main.set_xlim(0.5, 10.5)
    ax_main.set_ylim(2, 6)
    ax_main.set_aspect('equal')
    ax_main.axis('off')
    ax_main.set_title('Linkography Network - Design Move Connections', 
                     fontsize=14, fontweight='bold', color=THESIS_COLORS['primary_dark'], pad=20)
    
    ax_moves.set_xlim(0, 11)
    ax_moves.set_ylim(0, 1)
    ax_moves.axis('off')
    
    # Add overall title
    fig.suptitle('MEGA Architectural Mentor - Linkography Analysis Framework', 
                fontsize=18, fontweight='bold', color=THESIS_COLORS['primary_dark'], y=0.95)
    
    # Add explanation text boxes
    explanations = [
        {
            'pos': (12, 5),
            'text': 'Critical Moves\n(4+ connections)\nIndicate pivotal\ndesign decisions',
            'color': THESIS_COLORS['accent_magenta']
        },
        {
            'pos': (12, 3.5),
            'text': 'Backward Links\n(solid lines)\nReference previous\ndesign moves',
            'color': THESIS_COLORS['primary_dark']
        },
        {
            'pos': (12, 2),
            'text': 'Forward Links\n(dashed lines)\nAnticipate future\ndevelopments',
            'color': THESIS_COLORS['accent_magenta']
        }
    ]
    
    for explanation in explanations:
        x, y = explanation['pos']
        box = FancyBboxPatch(
            (x - 0.7, y - 0.5), 1.4, 1,
            boxstyle="round,pad=0.1",
            facecolor=THESIS_COLORS['neutral_light'], 
            edgecolor=explanation['color'],
            linewidth=2, alpha=0.8
        )
        ax_main.add_patch(box)
        
        ax_main.text(x, y, explanation['text'], ha='center', va='center',
                    fontsize=9, fontweight='bold', color=explanation['color'])
    
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_linkography_analysis_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '06_linkography_analysis.png')
    svg_path = os.path.join(base_path, '06_linkography_analysis.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Linkography Analysis diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()