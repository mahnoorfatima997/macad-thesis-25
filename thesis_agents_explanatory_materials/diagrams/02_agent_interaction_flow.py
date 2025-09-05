#!/usr/bin/env python3
"""
MEGA Architectural Mentor - Professional Agent Interaction Flow Diagram

This script generates a visually sophisticated diagram showing the dynamic interactions
between the 5 specialized agents, including routing decisions, collaboration patterns,
and response synthesis workflows.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, FancyArrowPatch
from matplotlib.collections import LineCollection
import matplotlib.patheffects as path_effects
from matplotlib.colors import ListedColormap
import numpy as np
import matplotlib.gridspec as gridspec

# Enhanced thesis color palette
COLORS = {
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
    'gradient_light': '#f5f2f0',
    'shadow_color': '#2a1f22',
    'highlight_color': '#ffffff',
    'connection_color': '#6b5b73',
    'flow_color': '#8b7d85'
}

# Professional typography
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'font.weight': 'normal'
})

def create_agent_node(ax, x, y, agent_name, agent_role, color, size=1.0):
    """Create a sophisticated agent node with professional styling"""
    
    # Shadow effect
    shadow_circle = Circle((x + 0.05, y - 0.05), size*0.8, 
                          facecolor=COLORS['shadow_color'], alpha=0.3, zorder=10)
    ax.add_patch(shadow_circle)
    
    # Glow effect
    for i in range(3):
        glow_alpha = 0.15 - i * 0.05
        glow_radius = size * (0.9 + i * 0.1)
        glow_circle = Circle((x, y), glow_radius, 
                           facecolor=color, alpha=glow_alpha, zorder=11+i)
        ax.add_patch(glow_circle)
    
    # Main agent circle
    main_circle = Circle((x, y), size*0.8, facecolor=color, 
                        edgecolor=COLORS['primary_dark'], linewidth=3, zorder=15)
    ax.add_patch(main_circle)
    
    # Inner highlight
    highlight_circle = Circle((x, y), size*0.3, facecolor=COLORS['highlight_color'], 
                            alpha=0.4, zorder=16)
    ax.add_patch(highlight_circle)
    
    # Agent name with effects
    name_text = ax.text(x, y+0.1, agent_name, fontsize=11, fontweight='bold', 
                       ha='center', va='center', color='white', zorder=20)
    name_text.set_path_effects([
        path_effects.withStroke(linewidth=2, foreground=COLORS['primary_dark']),
        path_effects.Normal()
    ])
    
    # Agent role
    ax.text(x, y-size*1.2, agent_role, fontsize=9, ha='center', va='center',
           color=COLORS['primary_dark'], fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    return main_circle

def create_flow_arrow(ax, start_pos, end_pos, label, color, style='solid', curve=0):
    """Create sophisticated flow arrows with labels"""
    
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    # Create curved arrow
    if curve != 0:
        connectionstyle = f"arc3,rad={curve}"
    else:
        connectionstyle = "arc3,rad=0"
    
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           connectionstyle=connectionstyle,
                           arrowstyle='->', mutation_scale=20,
                           color=color, linewidth=3, alpha=0.8,
                           linestyle=style, zorder=18)
    ax.add_patch(arrow)
    
    # Add flow label
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    if curve != 0:
        mid_y += curve * 0.5  # Adjust label position for curved arrows
    
    ax.text(mid_x, mid_y, label, fontsize=8, ha='center', va='center',
           color=color, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9))

def create_agent_interaction_diagram():
    """Create professional agent interaction flow diagram"""
    
    # Create figure with advanced layout
    fig = plt.figure(figsize=(20, 16))
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[3, 1], width_ratios=[1, 1])
    
    # Main interaction diagram
    ax_main = fig.add_subplot(gs[0, :])
    ax_main.set_xlim(0, 20)
    ax_main.set_ylim(0, 12)
    ax_main.axis('off')
    
    # Timeline diagram
    ax_timeline = fig.add_subplot(gs[1, 0])
    ax_timeline.set_xlim(0, 10)
    ax_timeline.set_ylim(0, 3)
    ax_timeline.axis('off')
    
    # Routing decision tree
    ax_routing = fig.add_subplot(gs[1, 1])
    ax_routing.set_xlim(0, 10)
    ax_routing.set_ylim(0, 3)
    ax_routing.axis('off')
    
    # Professional title
    title_text = ax_main.text(10, 11.5, 'Multi-Agent Interaction & Collaboration Flow', 
                             fontsize=24, fontweight='bold', ha='center', 
                             color=COLORS['primary_dark'])
    title_text.set_path_effects([
        path_effects.withStroke(linewidth=4, foreground='white'),
        path_effects.Normal()
    ])
    
    # Agent positions and definitions
    agents = [
        ('Context\nAgent', 'Input Analysis\n& Routing', 3, 8, COLORS['primary_rose']),
        ('Socratic\nTutor', 'Questioning\n& Discovery', 7, 9, COLORS['accent_magenta']),
        ('Domain\nExpert', 'Knowledge\n& RAG', 13, 9, COLORS['neutral_orange']),
        ('Cognitive\nEnhancement', 'Learning\nSupport', 17, 8, COLORS['primary_purple']),
        ('Analysis\nAgent', 'Synthesis\n& Coordination', 10, 6, COLORS['accent_coral'])
    ]
    
    # Create agent nodes
    agent_circles = []
    for name, role, x, y, color in agents:
        circle = create_agent_node(ax_main, x, y, name, role, color, 1.2)
        agent_circles.append((name, x, y, circle))
    
    # Create interaction flows
    interactions = [
        # Primary flows
        ((3, 8), (10, 6), "Context\nAnalysis", COLORS['primary_rose'], 'solid', 0),
        ((10, 6), (7, 9), "Socratic\nActivation", COLORS['accent_coral'], 'solid', 0.2),
        ((10, 6), (13, 9), "Knowledge\nRequest", COLORS['accent_coral'], 'solid', -0.2),
        ((10, 6), (17, 8), "Cognitive\nSupport", COLORS['accent_coral'], 'solid', 0),
        
        # Secondary flows
        ((7, 9), (13, 9), "Knowledge\nIntegration", COLORS['flow_color'], 'dashed', 0.3),
        ((13, 9), (17, 8), "Enhanced\nResponse", COLORS['flow_color'], 'dashed', 0.2),
        ((17, 8), (7, 9), "Challenge\nFeedback", COLORS['flow_color'], 'dashed', -0.3),
        
        # Synthesis flows
        ((7, 9), (10, 6), "Socratic\nResult", COLORS['accent_magenta'], 'solid', -0.2),
        ((13, 9), (10, 6), "Knowledge\nResult", COLORS['neutral_orange'], 'solid', 0.2),
        ((17, 8), (10, 6), "Cognitive\nResult", COLORS['primary_purple'], 'solid', 0),
    ]
    
    for start, end, label, color, style, curve in interactions:
        create_flow_arrow(ax_main, start, end, label, color, style, curve)
    
    # Add central coordination hub
    hub_circle = Circle((10, 6), 0.4, facecolor=COLORS['primary_dark'], 
                       edgecolor=COLORS['highlight_color'], linewidth=4, zorder=25)
    ax_main.add_patch(hub_circle)
    ax_main.text(10, 6, '🎯', fontsize=20, ha='center', va='center', zorder=26)
    
    # Add workflow phases
    phases = [
        (2, 10.5, "1. INPUT", "Student query\nprocessing"),
        (6, 10.5, "2. ANALYSIS", "Context & intent\nclassification"),
        (10, 10.5, "3. ROUTING", "Agent selection\n& coordination"),
        (14, 10.5, "4. EXECUTION", "Multi-agent\nprocessing"),
        (18, 10.5, "5. SYNTHESIS", "Response\nintegration")
    ]
    
    for x, y, phase, desc in phases:
        # Phase box
        phase_box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor=COLORS['neutral_light'],
                                  edgecolor=COLORS['primary_dark'], linewidth=2)
        ax_main.add_patch(phase_box)
        
        ax_main.text(x, y+0.1, phase, fontsize=10, fontweight='bold', 
                    ha='center', va='center', color=COLORS['primary_dark'])
        ax_main.text(x, y-0.2, desc, fontsize=8, ha='center', va='center',
                    color=COLORS['primary_dark'])
        
        # Phase connections
        if x < 18:
            arrow = FancyArrowPatch((x+0.8, y), (x+2.4, y),
                                   arrowstyle='->', mutation_scale=15,
                                   color=COLORS['connection_color'], linewidth=2)
            ax_main.add_patch(arrow)
    
    # Timeline visualization
    ax_timeline.text(5, 2.5, 'Interaction Timeline', fontsize=14, fontweight='bold', 
                    ha='center', color=COLORS['primary_dark'])
    
    timeline_events = [
        (1, 1.5, "Input", COLORS['primary_rose']),
        (3, 1.5, "Route", COLORS['primary_pink']),
        (5, 1.5, "Process", COLORS['primary_violet']),
        (7, 1.5, "Synthesize", COLORS['accent_coral']),
        (9, 1.5, "Output", COLORS['neutral_orange'])
    ]
    
    # Timeline line
    ax_timeline.plot([0.5, 9.5], [1.5, 1.5], color=COLORS['primary_dark'], linewidth=3)
    
    for x, y, event, color in timeline_events:
        event_circle = Circle((x, y), 0.2, facecolor=color, 
                            edgecolor=COLORS['primary_dark'], linewidth=2)
        ax_timeline.add_patch(event_circle)
        ax_timeline.text(x, y-0.5, event, fontsize=9, ha='center', va='center',
                        fontweight='bold', color=COLORS['primary_dark'])
    
    # Routing decision visualization
    ax_routing.text(5, 2.5, 'Routing Decision Matrix', fontsize=14, fontweight='bold', 
                   ha='center', color=COLORS['primary_dark'])
    
    routing_options = [
        ("Knowledge Only", 2, 1.8, COLORS['neutral_orange']),
        ("Socratic Focus", 5, 1.8, COLORS['accent_magenta']),
        ("Multi-Agent", 8, 1.8, COLORS['accent_coral']),
        ("Cognitive Support", 2, 1.2, COLORS['primary_purple']),
        ("Balanced Guidance", 5, 1.2, COLORS['primary_rose']),
        ("Comprehensive", 8, 1.2, COLORS['primary_violet'])
    ]
    
    for option, x, y, color in routing_options:
        option_box = FancyBboxPatch((x-0.7, y-0.2), 1.4, 0.4,
                                   boxstyle="round,pad=0.05",
                                   facecolor=color, alpha=0.7,
                                   edgecolor=COLORS['primary_dark'])
        ax_routing.add_patch(option_box)
        ax_routing.text(x, y, option, fontsize=8, ha='center', va='center',
                       fontweight='bold', color='white')
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the professional agent interaction diagram"""
    print("🤖 Generating professional agent interaction flow diagram...")
    
    fig = create_agent_interaction_diagram()
    
    # Ensure output directory exists
    import os
    os.makedirs('thesis_agents_explanatory_materials/diagrams', exist_ok=True)
    
    # Save in multiple formats
    fig.savefig('thesis_agents_explanatory_materials/diagrams/02_agent_interaction_flow.png', 
                dpi=300, bbox_inches='tight', facecolor='white', format='png')
    fig.savefig('thesis_agents_explanatory_materials/diagrams/02_agent_interaction_flow.svg', 
                format='svg', bbox_inches='tight', facecolor='white')
    fig.savefig('thesis_agents_explanatory_materials/diagrams/02_agent_interaction_flow.pdf', 
                format='pdf', bbox_inches='tight', facecolor='white')
    
    print("✅ Professional Agent Interaction Flow diagram generated!")
    print("   📁 High-Res PNG: thesis_agents_explanatory_materials/diagrams/02_agent_interaction_flow.png")
    print("   📁 Vector SVG: thesis_agents_explanatory_materials/diagrams/02_agent_interaction_flow.svg")
    print("   📁 Academic PDF: thesis_agents_explanatory_materials/diagrams/02_agent_interaction_flow.pdf")
    print("   🎯 Features: Dynamic flows, timeline visualization, routing matrix")
    
    plt.close()

if __name__ == "__main__":
    save_diagram()
