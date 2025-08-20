"""
System Architecture Diagram Generator
Creates comprehensive visual representation of the MEGA Architectural Mentor system components
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_system_architecture_diagram():
    """Create comprehensive system architecture diagram"""
    
    # Create figure with proper sizing
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define component positions and sizes
    components = {
        # User Interface Layer
        'streamlit_ui': {'pos': (2, 10), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_dark']},
        'dashboard': {'pos': (6, 10), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_purple']},
        
        # Orchestration Layer
        'langgraph_orchestrator': {'pos': (4, 8), 'size': (4, 1), 'color': THESIS_COLORS['primary_violet']},
        
        # Multi-Agent System
        'socratic_tutor': {'pos': (1, 6), 'size': (2.5, 1), 'color': METRIC_COLORS['socratic_tutor']},
        'domain_expert': {'pos': (4, 6), 'size': (2.5, 1), 'color': METRIC_COLORS['domain_expert']},
        'cognitive_enhancement': {'pos': (7, 6), 'size': (2.5, 1), 'color': METRIC_COLORS['cognitive_enhancement']},
        'analysis_agent': {'pos': (10, 6), 'size': (2.5, 1), 'color': METRIC_COLORS['analysis_agent']},
        'context_agent': {'pos': (13, 6), 'size': (2.5, 1), 'color': METRIC_COLORS['context_agent']},
        
        # Knowledge & Processing Layer
        'knowledge_base': {'pos': (1, 4), 'size': (3, 1), 'color': THESIS_COLORS['neutral_warm']},
        'vector_store': {'pos': (5, 4), 'size': (2.5, 1), 'color': THESIS_COLORS['neutral_orange']},
        'image_analysis': {'pos': (8.5, 4), 'size': (2.5, 1), 'color': THESIS_COLORS['accent_coral']},
        'phase_management': {'pos': (12, 4), 'size': (3, 1), 'color': THESIS_COLORS['primary_rose']},
        
        # Analytics & Benchmarking Layer
        'linkography_engine': {'pos': (1, 2), 'size': (3, 1), 'color': THESIS_COLORS['primary_pink']},
        'cognitive_metrics': {'pos': (5, 2), 'size': (3, 1), 'color': THESIS_COLORS['accent_magenta']},
        'graph_ml_analysis': {'pos': (9, 2), 'size': (3, 1), 'color': THESIS_COLORS['neutral_light']},
        'benchmarking_system': {'pos': (13, 2), 'size': (2.5, 1), 'color': THESIS_COLORS['primary_violet']},
        
        # Data Storage Layer
        'session_data': {'pos': (2, 0.3), 'size': (2.5, 0.8), 'color': THESIS_COLORS['neutral_warm']},
        'interaction_logs': {'pos': (5.5, 0.3), 'size': (2.5, 0.8), 'color': THESIS_COLORS['neutral_warm']},
        'design_moves': {'pos': (9, 0.3), 'size': (2.5, 0.8), 'color': THESIS_COLORS['neutral_warm']},
        'evaluation_reports': {'pos': (12.5, 0.3), 'size': (2.5, 0.8), 'color': THESIS_COLORS['neutral_warm']},
    }
    
    # Draw components
    for name, config in components.items():
        x, y = config['pos']
        width, height = config['size']
        color = config['color']
        
        # Create fancy box
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor='white',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(box)
        
        # Add text label
        label = name.replace('_', ' ').title()
        ax.text(x, y, label, ha='center', va='center', 
               fontsize=9, fontweight='bold', color='white',
               wrap=True)
    
    # Define connections with proper layering (lines behind boxes)
    connections = [
        # UI to Orchestration
        ('streamlit_ui', 'langgraph_orchestrator'),
        ('dashboard', 'langgraph_orchestrator'),
        
        # Orchestration to Agents
        ('langgraph_orchestrator', 'socratic_tutor'),
        ('langgraph_orchestrator', 'domain_expert'),
        ('langgraph_orchestrator', 'cognitive_enhancement'),
        ('langgraph_orchestrator', 'analysis_agent'),
        ('langgraph_orchestrator', 'context_agent'),
        
        # Agents to Knowledge Layer
        ('domain_expert', 'knowledge_base'),
        ('domain_expert', 'vector_store'),
        ('cognitive_enhancement', 'image_analysis'),
        ('analysis_agent', 'phase_management'),
        
        # Knowledge to Analytics
        ('knowledge_base', 'linkography_engine'),
        ('vector_store', 'cognitive_metrics'),
        ('image_analysis', 'graph_ml_analysis'),
        ('phase_management', 'benchmarking_system'),
        
        # Analytics to Data Storage
        ('linkography_engine', 'session_data'),
        ('cognitive_metrics', 'interaction_logs'),
        ('graph_ml_analysis', 'design_moves'),
        ('benchmarking_system', 'evaluation_reports'),
        
        # Cross-layer connections
        ('benchmarking_system', 'dashboard'),
    ]
    
    # Draw connections (behind components)
    for start, end in connections:
        start_pos = components[start]['pos']
        end_pos = components[end]['pos']
        
        # Create connection line
        line = ConnectionPatch(
            start_pos, end_pos, "data", "data",
            arrowstyle="->", shrinkA=20, shrinkB=20,
            mutation_scale=15, fc=UI_COLORS['text_secondary'],
            ec=UI_COLORS['text_secondary'], alpha=0.6, linewidth=1.5,
            zorder=0  # Behind other elements
        )
        ax.add_patch(line)
    
    # Add layer labels
    layer_labels = [
        {'label': 'User Interface Layer', 'y': 11, 'color': THESIS_COLORS['primary_dark']},
        {'label': 'Orchestration Layer', 'y': 8.8, 'color': THESIS_COLORS['primary_violet']},
        {'label': 'Multi-Agent System', 'y': 6.8, 'color': THESIS_COLORS['accent_magenta']},
        {'label': 'Knowledge & Processing Layer', 'y': 4.8, 'color': THESIS_COLORS['neutral_orange']},
        {'label': 'Analytics & Benchmarking Layer', 'y': 2.8, 'color': THESIS_COLORS['primary_pink']},
        {'label': 'Data Storage Layer', 'y': 1.3, 'color': THESIS_COLORS['neutral_warm']},
    ]
    
    for layer in layer_labels:
        ax.text(0.5, layer['y'], layer['label'], fontsize=12, fontweight='bold',
               color=layer['color'], rotation=90, va='center', ha='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Set axis properties
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title
    ax.text(8, 11.5, 'MEGA Architectural Mentor - System Architecture',
           fontsize=18, fontweight='bold', ha='center',
           color=THESIS_COLORS['primary_dark'])
    
    # Add subtitle
    ax.text(8, 11.2, 'Comprehensive Multi-Agent Educational System',
           fontsize=12, ha='center', style='italic',
           color=THESIS_COLORS['primary_purple'])
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_dark'], label='User Interface'),
        mpatches.Patch(color=THESIS_COLORS['primary_violet'], label='Orchestration'),
        mpatches.Patch(color=THESIS_COLORS['accent_magenta'], label='Agents'),
        mpatches.Patch(color=THESIS_COLORS['neutral_orange'], label='Knowledge Processing'),
        mpatches.Patch(color=THESIS_COLORS['primary_pink'], label='Analytics'),
        mpatches.Patch(color=THESIS_COLORS['neutral_warm'], label='Data Storage'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98),
             frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_system_architecture_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '01_system_architecture.png')
    svg_path = os.path.join(base_path, '01_system_architecture.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"System Architecture diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()