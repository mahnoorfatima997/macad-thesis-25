"""
Cognitive Metrics Calculation Flow Diagram Generator
Creates visual representation of how cognitive metrics are calculated
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_cognitive_metrics_flow_diagram():
    """Create comprehensive cognitive metrics calculation flow diagram"""
    
    # Create figure with proper sizing
    fig, ax = plt.subplots(1, 1, figsize=(16, 14))
    
    # Define metric calculation components
    components = {
        # Input Data Sources
        'user_interactions': {'pos': (2, 12), 'size': (2.5, 1), 'color': THESIS_COLORS['primary_dark'], 'text': 'User Interactions\n(Text & Images)'},
        'agent_responses': {'pos': (6, 12), 'size': (2.5, 1), 'color': THESIS_COLORS['primary_purple'], 'text': 'Agent Responses\n& Behaviors'},
        'session_context': {'pos': (10, 12), 'size': (2.5, 1), 'color': THESIS_COLORS['primary_violet'], 'text': 'Session Context\n& Metadata'},
        
        # Core Cognitive Metrics (Original 6)
        'cognitive_offloading': {'pos': (2, 10), 'size': (2.2, 0.8), 'color': METRIC_COLORS['cognitive_offloading'], 'text': 'Cognitive Offloading\nPrevention (COP)'},
        'deep_thinking': {'pos': (5, 10), 'size': (2.2, 0.8), 'color': METRIC_COLORS['deep_thinking'], 'text': 'Deep Thinking\nEngagement (DTE)'},
        'scaffolding': {'pos': (8, 10), 'size': (2.2, 0.8), 'color': METRIC_COLORS['scaffolding'], 'text': 'Scaffolding\nEffectiveness (SE)'},
        'knowledge_integration': {'pos': (11, 10), 'size': (2.2, 0.8), 'color': METRIC_COLORS['knowledge_integration'], 'text': 'Knowledge\nIntegration (KI)'},
        'engagement': {'pos': (3.5, 8.5), 'size': (2.2, 0.8), 'color': METRIC_COLORS['engagement'], 'text': 'Learning\nProgression (LP)'},
        'metacognition': {'pos': (6.5, 8.5), 'size': (2.2, 0.8), 'color': METRIC_COLORS['metacognition'], 'text': 'Metacognitive\nAwareness (MA)'},
        
        # Anthropomorphism Prevention Metrics (New 5)
        'autonomy_index': {'pos': (1, 6.5), 'size': (2.2, 0.8), 'color': THESIS_COLORS['accent_coral'], 'text': 'Cognitive Autonomy\nIndex (CAI)'},
        'anthropomorphism': {'pos': (4, 6.5), 'size': (2.2, 0.8), 'color': THESIS_COLORS['accent_magenta'], 'text': 'Anthropomorphism\nDetection (ADS)'},
        'neural_engagement': {'pos': (7, 6.5), 'size': (2.2, 0.8), 'color': THESIS_COLORS['primary_pink'], 'text': 'Neural Engagement\nScore (NES)'},
        'professional_boundary': {'pos': (10, 6.5), 'size': (2.2, 0.8), 'color': THESIS_COLORS['neutral_warm'], 'text': 'Professional\nBoundary (PBI)'},
        'bias_resistance': {'pos': (5.5, 5), 'size': (2.2, 0.8), 'color': THESIS_COLORS['neutral_orange'], 'text': 'Bias Resistance\nScore (BRS)'},
        
        # Calculation Engines
        'pattern_analyzer': {'pos': (2, 3.5), 'size': (2.5, 1), 'color': THESIS_COLORS['primary_violet'], 'text': 'Pattern Analysis\nEngine'},
        'nlp_processor': {'pos': (6, 3.5), 'size': (2.5, 1), 'color': THESIS_COLORS['primary_rose'], 'text': 'NLP Processing\nEngine'},
        'behavioral_analyzer': {'pos': (10, 3.5), 'size': (2.5, 1), 'color': THESIS_COLORS['neutral_light'], 'text': 'Behavioral Analysis\nEngine'},
        
        # Output Integration
        'metric_aggregation': {'pos': (4, 2), 'size': (3, 0.8), 'color': THESIS_COLORS['primary_dark'], 'text': 'Metric Aggregation\n& Normalization'},
        'risk_assessment': {'pos': (8, 2), 'size': (3, 0.8), 'color': THESIS_COLORS['accent_coral'], 'text': 'Risk Assessment\n& Alerting'},
        
        # Final Output
        'comprehensive_report': {'pos': (6, 0.5), 'size': (4, 0.8), 'color': THESIS_COLORS['primary_purple'], 'text': 'Comprehensive Cognitive\nAssessment Report'},
    }
    
    # Draw components
    for name, config in components.items():
        x, y = config['pos']
        width, height = config['size']
        color = config['color']
        text = config['text']
        
        # Create different shapes for different types
        if y > 11:  # Input sources - rounded rectangles
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.8
            )
        elif 5 <= y <= 10.5:  # Metrics - hexagonal style
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="sawtooth,pad=0.05",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.8
            )
        elif 3 <= y < 5:  # Processing engines - diamond style
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.08",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.8
            )
        else:  # Output - rounded rectangles
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='white', linewidth=2.5, alpha=0.9
            )
        
        ax.add_patch(box)
        
        # Add text label
        font_size = 8 if y > 5 else 9
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=font_size, fontweight='bold', color='white')
    
    # Define data flow connections
    connections = [
        # Input to core metrics
        ('user_interactions', 'cognitive_offloading'),
        ('user_interactions', 'deep_thinking'),
        ('agent_responses', 'scaffolding'),
        ('agent_responses', 'knowledge_integration'),
        ('session_context', 'engagement'),
        ('session_context', 'metacognition'),
        
        # Input to anthropomorphism metrics
        ('user_interactions', 'autonomy_index'),
        ('user_interactions', 'anthropomorphism'),
        ('agent_responses', 'neural_engagement'),
        ('session_context', 'professional_boundary'),
        ('user_interactions', 'bias_resistance'),
        
        # Metrics to processing engines
        ('cognitive_offloading', 'pattern_analyzer'),
        ('deep_thinking', 'pattern_analyzer'),
        ('scaffolding', 'nlp_processor'),
        ('knowledge_integration', 'nlp_processor'),
        ('engagement', 'behavioral_analyzer'),
        ('metacognition', 'behavioral_analyzer'),
        
        ('autonomy_index', 'pattern_analyzer'),
        ('anthropomorphism', 'nlp_processor'),
        ('neural_engagement', 'behavioral_analyzer'),
        ('professional_boundary', 'behavioral_analyzer'),
        ('bias_resistance', 'nlp_processor'),
        
        # Processing to output
        ('pattern_analyzer', 'metric_aggregation'),
        ('nlp_processor', 'metric_aggregation'),
        ('behavioral_analyzer', 'risk_assessment'),
        
        # Final integration
        ('metric_aggregation', 'comprehensive_report'),
        ('risk_assessment', 'comprehensive_report'),
    ]
    
    # Draw connections
    for start, end in connections:
        start_pos = components[start]['pos']
        end_pos = components[end]['pos']
        
        # Create arrow
        arrow = FancyArrowPatch(
            start_pos, end_pos,
            arrowstyle='->', mutation_scale=12,
            color=THESIS_COLORS['primary_dark'], linewidth=1.5, alpha=0.6,
            connectionstyle="arc3,rad=0.1"
        )
        ax.add_patch(arrow)
    
    # Add calculation method annotations
    calculation_methods = [
        {'pos': (14, 10), 'text': 'Pattern Matching\n& Classification', 'metrics': ['COP', 'DTE']},
        {'pos': (14, 8.5), 'text': 'Response Analysis\n& Scoring', 'metrics': ['SE', 'KI', 'LP', 'MA']},
        {'pos': (14, 6.5), 'text': 'Language Analysis\n& Risk Detection', 'metrics': ['CAI', 'ADS', 'NES', 'PBI', 'BRS']},
        {'pos': (14, 3.5), 'text': 'Aggregation\n& Normalization', 'metrics': ['Final Scores']},
    ]
    
    for method in calculation_methods:
        # Create annotation box
        box = FancyBboxPatch(
            (method['pos'][0] - 1, method['pos'][1] - 0.6), 2, 1.2,
            boxstyle="round,pad=0.05",
            facecolor=THESIS_COLORS['neutral_light'], 
            edgecolor=THESIS_COLORS['primary_dark'],
            linewidth=1, alpha=0.7
        )
        ax.add_patch(box)
        
        ax.text(method['pos'][0], method['pos'][1], method['text'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               color=THESIS_COLORS['primary_dark'])
    
    # Add metric targets and thresholds
    targets = [
        {'pos': (0.2, 10), 'text': '>70%', 'color': METRIC_COLORS['cognitive_offloading']},
        {'pos': (0.2, 8.5), 'text': '>60%', 'color': METRIC_COLORS['deep_thinking']},
        {'pos': (0.2, 6.5), 'text': '>60%', 'color': THESIS_COLORS['accent_coral']},
        {'pos': (12.8, 10), 'text': '>80%', 'color': METRIC_COLORS['scaffolding']},
        {'pos': (12.8, 8.5), 'text': '>75%', 'color': METRIC_COLORS['knowledge_integration']},
        {'pos': (12.8, 6.5), 'text': '<20%', 'color': THESIS_COLORS['accent_magenta']},
    ]
    
    for target in targets:
        circle = Circle(target['pos'], 0.15, facecolor=target['color'], 
                       edgecolor='white', linewidth=2, alpha=0.8)
        ax.add_patch(circle)
        ax.text(target['pos'][0], target['pos'][1], target['text'],
               ha='center', va='center', fontsize=7, fontweight='bold', color='white')
    
    # Add processing flow labels
    flow_labels = [
        {'pos': (6, 11.2), 'text': 'INPUT DATA COLLECTION', 'color': THESIS_COLORS['primary_dark']},
        {'pos': (6, 9.2), 'text': 'COGNITIVE METRICS CALCULATION', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (6, 7.2), 'text': 'ANTHROPOMORPHISM PREVENTION METRICS', 'color': THESIS_COLORS['accent_coral']},
        {'pos': (6, 4.2), 'text': 'PROCESSING & ANALYSIS ENGINES', 'color': THESIS_COLORS['primary_rose']},
        {'pos': (6, 1.3), 'text': 'INTEGRATION & REPORTING', 'color': THESIS_COLORS['primary_dark']},
    ]
    
    for label in flow_labels:
        ax.text(label['pos'][0], label['pos'][1], label['text'],
               ha='center', va='center', fontsize=11, fontweight='bold',
               color=label['color'], style='italic',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    # Add separating lines
    separators = [11.5, 9.8, 7.8, 4.5, 2.8]
    for y in separators:
        ax.axhline(y=y, color=UI_COLORS['border'], linestyle='--', alpha=0.4, linewidth=1)
    
    # Set axis properties
    ax.set_xlim(-0.8, 15.5)
    ax.set_ylim(-0.2, 13)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title
    ax.text(6, 12.7, 'MEGA Architectural Mentor - Cognitive Metrics Calculation Flow',
           fontsize=16, fontweight='bold', ha='center',
           color=THESIS_COLORS['primary_dark'])
    
    # Add subtitle
    ax.text(6, 12.4, '11 Comprehensive Metrics for Educational AI Assessment',
           fontsize=11, ha='center', style='italic',
           color=THESIS_COLORS['primary_purple'])
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_dark'], label='Input/Output'),
        mpatches.Patch(color=THESIS_COLORS['primary_violet'], label='Core Cognitive Metrics'),
        mpatches.Patch(color=THESIS_COLORS['accent_coral'], label='Anthropomorphism Prevention'),
        mpatches.Patch(color=THESIS_COLORS['primary_rose'], label='Processing Engines'),
        mpatches.Patch(color=THESIS_COLORS['neutral_light'], label='Analysis Methods'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98),
             frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_cognitive_metrics_flow_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '03_cognitive_metrics_flow.png')
    svg_path = os.path.join(base_path, '03_cognitive_metrics_flow.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Cognitive Metrics Flow diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()