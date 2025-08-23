"""
Data Flow Pipeline Diagram Generator
Creates visual representation of data flow from user interaction to final reports
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, FancyArrowPatch, Circle
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_data_flow_pipeline_diagram():
    """Create comprehensive data flow pipeline diagram"""
    
    # Create figure with proper sizing for horizontal flow
    fig, ax = plt.subplots(1, 1, figsize=(18, 10))
    
    # Define flow stages with positions and colors
    flow_stages = {
        # Input Stage
        'user_input': {'pos': (1, 8), 'size': (1.8, 1.2), 'color': THESIS_COLORS['primary_dark'], 'text': 'User Input\n(Text/Image)'},
        'input_parsing': {'pos': (1, 6), 'size': (1.8, 1), 'color': THESIS_COLORS['primary_purple'], 'text': 'Input Parsing\n& Validation'},
        
        # Classification Stage
        'context_analysis': {'pos': (4, 8), 'size': (1.8, 1.2), 'color': THESIS_COLORS['primary_violet'], 'text': 'Context\nAnalysis'},
        'skill_assessment': {'pos': (4, 6), 'size': (1.8, 1), 'color': THESIS_COLORS['primary_rose'], 'text': 'Skill Level\nAssessment'},
        'routing_decision': {'pos': (4, 4), 'size': (1.8, 1), 'color': THESIS_COLORS['accent_coral'], 'text': 'Agent Routing\nDecision'},
        
        # Processing Stage
        'agent_processing': {'pos': (7, 7), 'size': (2, 2.5), 'color': THESIS_COLORS['accent_magenta'], 'text': 'Multi-Agent\nProcessing'},
        'knowledge_retrieval': {'pos': (7, 4), 'size': (2, 1), 'color': THESIS_COLORS['neutral_warm'], 'text': 'Knowledge\nRetrieval'},
        
        # Response Generation Stage
        'response_synthesis': {'pos': (10, 8), 'size': (1.8, 1.2), 'color': THESIS_COLORS['primary_pink'], 'text': 'Response\nSynthesis'},
        'quality_check': {'pos': (10, 6), 'size': (1.8, 1), 'color': THESIS_COLORS['neutral_orange'], 'text': 'Quality\nAssurance'},
        'response_delivery': {'pos': (10, 4), 'size': (1.8, 1), 'color': THESIS_COLORS['neutral_light'], 'text': 'Response\nDelivery'},
        
        # Logging & Analytics Stage
        'interaction_logging': {'pos': (13, 8), 'size': (1.8, 1.2), 'color': THESIS_COLORS['primary_violet'], 'text': 'Interaction\nLogging'},
        'design_move_extraction': {'pos': (13, 6), 'size': (1.8, 1), 'color': THESIS_COLORS['primary_rose'], 'text': 'Design Move\nExtraction'},
        'metric_calculation': {'pos': (13, 4), 'size': (1.8, 1), 'color': THESIS_COLORS['accent_coral'], 'text': 'Metric\nCalculation'},
        
        # Analysis & Reporting Stage
        'linkography_analysis': {'pos': (16, 8), 'size': (1.8, 1.2), 'color': THESIS_COLORS['primary_pink'], 'text': 'Linkography\nAnalysis'},
        'cognitive_assessment': {'pos': (16, 6), 'size': (1.8, 1), 'color': THESIS_COLORS['neutral_warm'], 'text': 'Cognitive\nAssessment'},
        'report_generation': {'pos': (16, 4), 'size': (1.8, 1), 'color': THESIS_COLORS['primary_dark'], 'text': 'Report\nGeneration'},
    }
    
    # Draw flow stages
    for name, config in flow_stages.items():
        x, y = config['pos']
        width, height = config['size']
        color = config['color']
        text = config['text']
        
        # Create fancy box
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.08",
            facecolor=color,
            edgecolor='white',
            linewidth=2.5,
            alpha=0.85
        )
        ax.add_patch(box)
        
        # Add text label
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=9, fontweight='bold', color='white')
    
    # Define main flow connections
    main_flow = [
        ('user_input', 'context_analysis'),
        ('input_parsing', 'skill_assessment'),
        ('context_analysis', 'agent_processing'),
        ('skill_assessment', 'routing_decision'),
        ('routing_decision', 'knowledge_retrieval'),
        ('agent_processing', 'response_synthesis'),
        ('knowledge_retrieval', 'quality_check'),
        ('response_synthesis', 'interaction_logging'),
        ('quality_check', 'response_delivery'),
        ('response_delivery', 'design_move_extraction'),
        ('interaction_logging', 'linkography_analysis'),
        ('design_move_extraction', 'metric_calculation'),
        ('metric_calculation', 'cognitive_assessment'),
        ('linkography_analysis', 'report_generation'),
        ('cognitive_assessment', 'report_generation'),
    ]
    
    # Draw main flow arrows
    for start, end in main_flow:
        start_pos = flow_stages[start]['pos']
        end_pos = flow_stages[end]['pos']
        
        # Create curved arrow
        arrow = FancyArrowPatch(
            start_pos, end_pos,
            arrowstyle='->', mutation_scale=20,
            color=THESIS_COLORS['primary_dark'],
            linewidth=2.5, alpha=0.7,
            connectionstyle="arc3,rad=0.1"
        )
        ax.add_patch(arrow)
    
    # Add vertical flow connections
    vertical_connections = [
        ('user_input', 'input_parsing'),
        ('context_analysis', 'skill_assessment'),
        ('skill_assessment', 'routing_decision'),
        ('response_synthesis', 'quality_check'),
        ('quality_check', 'response_delivery'),
        ('interaction_logging', 'design_move_extraction'),
        ('design_move_extraction', 'metric_calculation'),
        ('linkography_analysis', 'cognitive_assessment'),
        ('cognitive_assessment', 'report_generation'),
    ]
    
    for start, end in vertical_connections:
        start_pos = flow_stages[start]['pos']
        end_pos = flow_stages[end]['pos']
        
        arrow = FancyArrowPatch(
            start_pos, end_pos,
            arrowstyle='->', mutation_scale=15,
            color=THESIS_COLORS['primary_purple'],
            linewidth=2, alpha=0.6
        )
        ax.add_patch(arrow)
    
    # Add data flow labels
    data_types = [
        {'pos': (2.5, 9), 'text': 'Raw Input Data', 'color': THESIS_COLORS['primary_dark']},
        {'pos': (5.5, 9), 'text': 'Structured Data', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (8.5, 9), 'text': 'Processed Response', 'color': THESIS_COLORS['accent_magenta']},
        {'pos': (11.5, 9), 'text': 'Quality-Assured Output', 'color': THESIS_COLORS['primary_pink']},
        {'pos': (14.5, 9), 'text': 'Analytics Data', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (17.5, 9), 'text': 'Final Reports', 'color': THESIS_COLORS['primary_dark']},
    ]
    
    for label in data_types:
        ax.text(label['pos'][0], label['pos'][1], label['text'], 
               ha='center', va='center', fontsize=10, fontweight='bold',
               color=label['color'], style='italic',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add pipeline stage separators
    separators = [3, 6, 9, 12, 15]
    for x in separators:
        ax.axvline(x=x, color=UI_COLORS['border'], linestyle='--', alpha=0.5, linewidth=1)
    
    # Add stage headers
    stage_headers = [
        {'pos': (1, 9.5), 'text': 'INPUT', 'color': THESIS_COLORS['primary_dark']},
        {'pos': (4, 9.5), 'text': 'CLASSIFICATION', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (7, 9.5), 'text': 'PROCESSING', 'color': THESIS_COLORS['accent_magenta']},
        {'pos': (10, 9.5), 'text': 'RESPONSE', 'color': THESIS_COLORS['primary_pink']},
        {'pos': (13, 9.5), 'text': 'LOGGING', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (16, 9.5), 'text': 'ANALYSIS', 'color': THESIS_COLORS['primary_dark']},
    ]
    
    for header in stage_headers:
        ax.text(header['pos'][0], header['pos'][1], header['text'], 
               ha='center', va='center', fontsize=12, fontweight='bold',
               color=header['color'])
    
    # Add parallel processing indicators
    parallel_processes = [
        {'center': (7, 7), 'processes': ['Socratic\nTutor', 'Domain\nExpert', 'Cognitive\nEnhancement']},
    ]
    
    for parallel in parallel_processes:
        center = parallel['center']
        processes = parallel['processes']
        
        # Draw smaller boxes for each process
        for i, process in enumerate(processes):
            y_offset = (i - 1) * 0.7
            pos = (center[0], center[1] + y_offset)
            
            box = FancyBboxPatch(
                (pos[0] - 0.7, pos[1] - 0.3), 1.4, 0.6,
                boxstyle="round,pad=0.05",
                facecolor=THESIS_COLORS['neutral_light'],
                edgecolor=THESIS_COLORS['accent_magenta'],
                linewidth=1.5,
                alpha=0.7
            )
            ax.add_patch(box)
            
            ax.text(pos[0], pos[1], process, ha='center', va='center',
                   fontsize=8, color=THESIS_COLORS['primary_dark'])
    
    # Set axis properties
    ax.set_xlim(-0.5, 18)
    ax.set_ylim(2.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title
    ax.text(9, 10.2, 'MEGA Architectural Mentor - Data Flow Pipeline',
           fontsize=18, fontweight='bold', ha='center',
           color=THESIS_COLORS['primary_dark'])
    
    # Add subtitle
    ax.text(9, 9.9, 'From User Interaction to Comprehensive Educational Reports',
           fontsize=12, ha='center', style='italic',
           color=THESIS_COLORS['primary_purple'])
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_dark'], label='Input/Output'),
        mpatches.Patch(color=THESIS_COLORS['primary_violet'], label='Analysis & Classification'),
        mpatches.Patch(color=THESIS_COLORS['accent_magenta'], label='AI Processing'),
        mpatches.Patch(color=THESIS_COLORS['primary_pink'], label='Response Generation'),
        mpatches.Patch(color=THESIS_COLORS['neutral_warm'], label='Data Management'),
    ]
    
    ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.02),
             frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_data_flow_pipeline_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '02_data_flow_pipeline.png')
    svg_path = os.path.join(base_path, '02_data_flow_pipeline.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Data Flow Pipeline diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()