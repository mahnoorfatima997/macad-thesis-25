"""
Benchmarking Process Pipeline Diagram Generator
Creates visual representation of the 9-step benchmarking pipeline
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_benchmarking_pipeline_diagram():
    """Create comprehensive 9-step benchmarking pipeline diagram"""
    
    # Create figure with proper sizing
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    
    # Define the 9 benchmarking steps
    steps = {
        # Step 1: Setup & Configuration
        'step_1': {
            'pos': (2, 10), 'size': (2.5, 1.5), 
            'color': THESIS_COLORS['primary_dark'],
            'number': '1',
            'title': 'Setup &\nConfiguration',
            'details': '• Test Environment Setup\n• Agent Configuration\n• Knowledge Base Loading\n• Session Initialization'
        },
        
        # Step 2: User Input Collection
        'step_2': {
            'pos': (6, 10), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['primary_purple'],
            'number': '2', 
            'title': 'Input Collection\n& Validation',
            'details': '• User Query Processing\n• Image Upload Handling\n• Input Validation\n• Context Extraction'
        },
        
        # Step 3: Agent Orchestration
        'step_3': {
            'pos': (10, 10), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['primary_violet'],
            'number': '3',
            'title': 'Agent\nOrchestration',
            'details': '• Routing Decision\n• Multi-Agent Activation\n• Parallel Processing\n• Response Synthesis'
        },
        
        # Step 4: Real-time Metric Calculation
        'step_4': {
            'pos': (14, 10), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['primary_rose'],
            'number': '4',
            'title': 'Real-time\nMetric Calculation',
            'details': '• Cognitive Metrics\n• Anthropomorphism Detection\n• Pattern Analysis\n• Risk Assessment'
        },
        
        # Step 5: Design Move Extraction
        'step_5': {
            'pos': (2, 7), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['accent_coral'],
            'number': '5',
            'title': 'Design Move\nExtraction',
            'details': '• Move Identification\n• Classification\n• Temporal Sequencing\n• Link Analysis'
        },
        
        # Step 6: Linkography Analysis
        'step_6': {
            'pos': (6, 7), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['accent_magenta'],
            'number': '6',
            'title': 'Linkography\nAnalysis',
            'details': '• Link Pattern Detection\n• Critical Move Identification\n• Web Formation Analysis\n• Cognitive Flow Mapping'
        },
        
        # Step 7: Graph ML Processing
        'step_7': {
            'pos': (10, 7), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['primary_pink'],
            'number': '7',
            'title': 'Graph ML\nProcessing',
            'details': '• Network Construction\n• GNN Analysis\n• Pattern Recognition\n• Proficiency Classification'
        },
        
        # Step 8: Comprehensive Evaluation
        'step_8': {
            'pos': (14, 7), 'size': (2.5, 1.5),
            'color': THESIS_COLORS['neutral_warm'],
            'number': '8',
            'title': 'Comprehensive\nEvaluation',
            'details': '• Multi-dimensional Scoring\n• Comparative Analysis\n• Trend Identification\n• Performance Assessment'
        },
        
        # Step 9: Report Generation
        'step_9': {
            'pos': (8, 4), 'size': (3, 1.5),
            'color': THESIS_COLORS['neutral_orange'],
            'number': '9',
            'title': 'Report Generation\n& Visualization',
            'details': '• Dashboard Updates\n• Interactive Visualizations\n• PDF Report Generation\n• Data Export'
        }
    }
    
    # Draw steps
    for step_key, step_config in steps.items():
        x, y = step_config['pos']
        width, height = step_config['size']
        color = step_config['color']
        number = step_config['number']
        title = step_config['title']
        
        # Create main step box
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor='white', linewidth=3, alpha=0.85
        )
        ax.add_patch(box)
        
        # Create step number circle
        circle = Circle((x - width/2 + 0.3, y + height/2 - 0.3), 0.25, 
                       facecolor='white', edgecolor=color, linewidth=3)
        ax.add_patch(circle)
        
        # Add step number
        ax.text(x - width/2 + 0.3, y + height/2 - 0.3, number,
               ha='center', va='center', fontsize=14, fontweight='bold', color=color)
        
        # Add step title
        ax.text(x, y + 0.2, title, ha='center', va='center',
               fontsize=11, fontweight='bold', color='white')
        
        # Add details (smaller font)
        ax.text(x, y - 0.3, step_config['details'], ha='center', va='center',
               fontsize=8, color='white', linespacing=1.2)
    
    # Define process flow connections
    connections = [
        ('step_1', 'step_2'),
        ('step_2', 'step_3'),
        ('step_3', 'step_4'),
        ('step_4', 'step_5'),
        ('step_5', 'step_6'),
        ('step_6', 'step_7'),
        ('step_7', 'step_8'),
        ('step_8', 'step_9'),
        # Feedback loops
        ('step_4', 'step_3'),  # Real-time adjustment
        ('step_6', 'step_5'),  # Linkography feedback
    ]
    
    # Draw main flow arrows
    for start, end in connections:
        start_pos = steps[start]['pos']
        end_pos = steps[end]['pos']
        
        # Determine if this is a feedback loop
        is_feedback = (start == 'step_4' and end == 'step_3') or (start == 'step_6' and end == 'step_5')
        
        if is_feedback:
            # Feedback arrows (curved, thinner, different color)
            arrow = FancyArrowPatch(
                start_pos, end_pos,
                arrowstyle='->', mutation_scale=15,
                color=THESIS_COLORS['accent_coral'], linewidth=2, alpha=0.7,
                connectionstyle="arc3,rad=0.3", linestyle='--'
            )
        else:
            # Regular flow arrows
            arrow = FancyArrowPatch(
                start_pos, end_pos,
                arrowstyle='->', mutation_scale=20,
                color=THESIS_COLORS['primary_dark'], linewidth=3, alpha=0.8
            )
        
        ax.add_patch(arrow)
    
    # Add phase labels
    phases = [
        {'pos': (8, 11.2), 'text': 'COLLECTION & PROCESSING PHASE', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (8, 8.2), 'text': 'ANALYSIS & EVALUATION PHASE', 'color': THESIS_COLORS['accent_magenta']},
        {'pos': (8, 5.2), 'text': 'REPORTING & VISUALIZATION PHASE', 'color': THESIS_COLORS['neutral_orange']},
    ]
    
    for phase in phases:
        ax.text(phase['pos'][0], phase['pos'][1], phase['text'],
               ha='center', va='center', fontsize=13, fontweight='bold',
               color=phase['color'], style='italic',
               bbox=dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.9))
    
    # Add data flow indicators
    data_flows = [
        {'start': (4, 9), 'end': (4, 8), 'label': 'Session\nData', 'color': THESIS_COLORS['primary_purple']},
        {'start': (8, 9), 'end': (8, 8), 'label': 'Interaction\nLogs', 'color': THESIS_COLORS['primary_violet']},
        {'start': (12, 9), 'end': (12, 8), 'label': 'Metric\nScores', 'color': THESIS_COLORS['primary_rose']},
        {'start': (8, 6), 'end': (8, 5.5), 'label': 'Analysis\nResults', 'color': THESIS_COLORS['primary_pink']},
    ]
    
    for flow in data_flows:
        # Data flow arrow
        arrow = FancyArrowPatch(
            flow['start'], flow['end'],
            arrowstyle='->', mutation_scale=12,
            color=flow['color'], linewidth=2, alpha=0.6
        )
        ax.add_patch(arrow)
        
        # Data label
        mid_x = (flow['start'][0] + flow['end'][0]) / 2 + 0.5
        mid_y = (flow['start'][1] + flow['end'][1]) / 2
        ax.text(mid_x, mid_y, flow['label'], ha='center', va='center',
               fontsize=8, color=flow['color'], fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add quality gates
    quality_gates = [
        {'pos': (4, 9.5), 'label': 'Input\nValidation'},
        {'pos': (8, 9.5), 'label': 'Processing\nQuality'},
        {'pos': (12, 9.5), 'label': 'Metric\nThreshold'},
        {'pos': (8, 6.5), 'label': 'Analysis\nCompleteness'},
    ]
    
    for gate in quality_gates:
        # Quality gate diamond
        diamond = FancyBboxPatch(
            (gate['pos'][0] - 0.4, gate['pos'][1] - 0.3), 0.8, 0.6,
            boxstyle="round,pad=0.05",
            facecolor=THESIS_COLORS['accent_coral'], 
            edgecolor='white', linewidth=2, alpha=0.7,
            transform=ax.transData
        )
        ax.add_patch(diamond)
        
        ax.text(gate['pos'][0], gate['pos'][1], gate['label'],
               ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    
    # Add parallel processing indicators for Step 3
    parallel_agents = ['Socratic\nTutor', 'Domain\nExpert', 'Cognitive\nEnhancement']
    for i, agent in enumerate(parallel_agents):
        y_offset = (i - 1) * 0.4
        pos = (10, 10 + y_offset)
        
        small_box = FancyBboxPatch(
            (pos[0] - 0.6, pos[1] - 0.15), 1.2, 0.3,
            boxstyle="round,pad=0.02",
            facecolor=THESIS_COLORS['neutral_light'],
            edgecolor=THESIS_COLORS['primary_violet'],
            linewidth=1, alpha=0.6
        )
        ax.add_patch(small_box)
        
        ax.text(pos[0], pos[1], agent, ha='center', va='center',
               fontsize=7, color=THESIS_COLORS['primary_dark'])
    
    # Add timing indicators
    timings = [
        {'pos': (2, 9.2), 'text': '~5s', 'color': THESIS_COLORS['neutral_warm']},
        {'pos': (6, 9.2), 'text': '~2s', 'color': THESIS_COLORS['neutral_warm']},
        {'pos': (10, 9.2), 'text': '~10s', 'color': THESIS_COLORS['neutral_warm']},
        {'pos': (14, 9.2), 'text': '~3s', 'color': THESIS_COLORS['neutral_warm']},
        {'pos': (8, 5.7), 'text': '~15s', 'color': THESIS_COLORS['neutral_warm']},
    ]
    
    for timing in timings:
        ax.text(timing['pos'][0], timing['pos'][1], timing['text'],
               ha='center', va='center', fontsize=9, fontweight='bold',
               color=timing['color'],
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add phase separators
    ax.axhline(y=8.5, xmin=0.05, xmax=0.95, color=UI_COLORS['border'], linestyle='-', alpha=0.3, linewidth=2)
    ax.axhline(y=5.5, xmin=0.05, xmax=0.95, color=UI_COLORS['border'], linestyle='-', alpha=0.3, linewidth=2)
    
    # Set axis properties
    ax.set_xlim(0, 16)
    ax.set_ylim(2.5, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title
    ax.text(8, 11.7, 'MEGA Architectural Mentor - Benchmarking Pipeline',
           fontsize=18, fontweight='bold', ha='center',
           color=THESIS_COLORS['primary_dark'])
    
    # Add subtitle
    ax.text(8, 11.4, '9-Step Comprehensive Educational AI Assessment Process',
           fontsize=12, ha='center', style='italic',
           color=THESIS_COLORS['primary_purple'])
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_dark'], label='Setup & Input'),
        mpatches.Patch(color=THESIS_COLORS['primary_violet'], label='Processing & Analysis'),
        mpatches.Patch(color=THESIS_COLORS['accent_magenta'], label='Advanced Analytics'),
        mpatches.Patch(color=THESIS_COLORS['neutral_orange'], label='Output & Reporting'),
        mpatches.Patch(color=THESIS_COLORS['accent_coral'], label='Quality Gates'),
    ]
    
    ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.02),
             frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_benchmarking_pipeline_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '04_benchmarking_pipeline.png')
    svg_path = os.path.join(base_path, '04_benchmarking_pipeline.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Benchmarking Pipeline diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()