"""
Mega Architectural Mentor - Measurement Flow Diagram
Visual representation of how inputs produce measurable outputs
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_measurement_flow_diagram():
    """Create a comprehensive flow diagram showing input-output measurement relationships"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Color scheme
    input_color = '#E8F4FD'
    process_color = '#B8E0FF'
    output_color = '#FFE8CC'
    metric_color = '#E8FFE8'
    
    # Title
    ax.text(5, 9.5, 'MEGA Architectural Mentor - Measurement Flow', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(5, 9.1, 'From Student Inputs to Cognitive Metrics', 
            fontsize=14, ha='center', style='italic')
    
    # Input Section
    input_box = FancyBboxPatch((0.5, 6.5), 2, 2.5, 
                               boxstyle="round,pad=0.1", 
                               facecolor=input_color, 
                               edgecolor='black', 
                               linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.5, 8.5, 'STUDENT INPUTS', fontsize=12, fontweight='bold', ha='center')
    
    inputs = [
        '• Text queries',
        '• Design uploads', 
        '• Confusion signals',
        '• Direct questions',
        '• Reflection statements'
    ]
    for i, inp in enumerate(inputs):
        ax.text(0.7, 8.2 - i*0.3, inp, fontsize=10)
    
    # Processing Section
    process_box = FancyBboxPatch((3, 6.5), 4, 2.5,
                                boxstyle="round,pad=0.1",
                                facecolor=process_color,
                                edgecolor='black',
                                linewidth=2)
    ax.add_patch(process_box)
    ax.text(5, 8.5, 'AI PROCESSING & ANALYSIS', fontsize=12, fontweight='bold', ha='center')
    
    processes = [
        '• GPT-4 Classification',
        '• Skill Level Detection',
        '• Visual Analysis (GPT-4V + SAM)',
        '• Knowledge Base Search',
        '• Multi-Agent Orchestration'
    ]
    for i, proc in enumerate(processes):
        ax.text(3.2, 8.2 - i*0.3, proc, fontsize=10)
    
    # Output Section
    output_box = FancyBboxPatch((7.5, 6.5), 2, 2.5,
                               boxstyle="round,pad=0.1",
                               facecolor=output_color,
                               edgecolor='black',
                               linewidth=2)
    ax.add_patch(output_box)
    ax.text(8.5, 8.5, 'SYSTEM OUTPUTS', fontsize=12, fontweight='bold', ha='center')
    
    outputs = [
        '• Socratic questions',
        '• Scaffolded hints',
        '• Knowledge synthesis',
        '• Cognitive challenges',
        '• Reflection prompts'
    ]
    for i, out in enumerate(outputs):
        ax.text(7.7, 8.2 - i*0.3, out, fontsize=10)
    
    # Metrics Section - Top Row
    metric_boxes = [
        {'x': 0.5, 'y': 3.5, 'title': 'Cognitive Offloading\nPrevention (COP)', 
         'details': ['Direct answer\navoidance rate', 'Target: >70%']},
        {'x': 2.5, 'y': 3.5, 'title': 'Deep Thinking\nEngagement (DTE)', 
         'details': ['Question\ncomplexity', 'Target: >60%']},
        {'x': 4.5, 'y': 3.5, 'title': 'Scaffolding\nEffectiveness (SE)', 
         'details': ['Skill-appropriate\nsupport', 'Target: >80%']}
    ]
    
    # Metrics Section - Bottom Row
    metric_boxes.extend([
        {'x': 6.5, 'y': 3.5, 'title': 'Knowledge\nIntegration (KI)', 
         'details': ['Source relevance\n& synthesis', 'Target: >75%']},
        {'x': 2.5, 'y': 1.5, 'title': 'Learning\nProgression (LP)', 
         'details': ['Skill level\nadvancement', 'Target: >50%']},
        {'x': 5.5, 'y': 1.5, 'title': 'Metacognitive\nAwareness (MA)', 
         'details': ['Self-reflection\nprompts', 'Target: >40%']}
    ])
    
    for metric in metric_boxes:
        box = FancyBboxPatch((metric['x'], metric['y']), 1.8, 1.5,
                            boxstyle="round,pad=0.1",
                            facecolor=metric_color,
                            edgecolor='darkgreen',
                            linewidth=2)
        ax.add_patch(box)
        ax.text(metric['x'] + 0.9, metric['y'] + 1.3, metric['title'], 
                fontsize=10, fontweight='bold', ha='center', va='top')
        for i, detail in enumerate(metric['details']):
            ax.text(metric['x'] + 0.9, metric['y'] + 0.8 - i*0.4, detail,
                   fontsize=8, ha='center', va='top')
    
    # Add arrows showing flow
    # Input to Process
    arrow1 = ConnectionPatch((2.5, 7.75), (3, 7.75), "data", "data",
                            arrowstyle="->", shrinkA=0, shrinkB=0,
                            mutation_scale=20, fc="black", linewidth=2)
    ax.add_artist(arrow1)
    
    # Process to Output
    arrow2 = ConnectionPatch((7, 7.75), (7.5, 7.75), "data", "data",
                            arrowstyle="->", shrinkA=0, shrinkB=0,
                            mutation_scale=20, fc="black", linewidth=2)
    ax.add_artist(arrow2)
    
    # Output to Metrics (multiple arrows)
    metric_arrows = [
        ((8.5, 6.5), (1.4, 5)),    # to COP
        ((8.5, 6.5), (3.4, 5)),    # to DTE
        ((8.5, 6.5), (5.4, 5)),    # to SE
        ((8.5, 6.5), (7.4, 5)),    # to KI
        ((5, 6.5), (3.4, 3)),      # to LP
        ((5, 6.5), (6.4, 3))       # to MA
    ]
    
    for start, end in metric_arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                               arrowstyle="->", shrinkA=0, shrinkB=0,
                               mutation_scale=15, fc="gray", 
                               connectionstyle="arc3,rad=0.3",
                               alpha=0.6, linewidth=1.5)
        ax.add_artist(arrow)
    
    # Add research foundation box
    research_box = FancyBboxPatch((0.5, 0.2), 9, 0.8,
                                 boxstyle="round,pad=0.05",
                                 facecolor='#F0F0F0',
                                 edgecolor='black',
                                 linewidth=1)
    ax.add_patch(research_box)
    ax.text(5, 0.6, 'Research Foundations: Goldschmidt (1990) Linkography • Vygotsky (1978) ZPD • Sweller (1988) Cognitive Load • Chi et al. (2014) ICAP Framework', 
            fontsize=9, ha='center', style='italic')
    
    # Add legend
    legend_elements = [
        patches.Patch(color=input_color, label='Student Input'),
        patches.Patch(color=process_color, label='AI Processing'),
        patches.Patch(color=output_color, label='System Output'),
        patches.Patch(color=metric_color, label='Measured Metric')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.tight_layout()
    return fig

def create_linkography_measurement_diagram():
    """Create a diagram showing how linkography patterns map to cognitive metrics"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Linkography Pattern Analysis', 
            fontsize=18, fontweight='bold', ha='center')
    ax.text(5, 9.1, 'Mapping Design Moves to Cognitive Metrics', 
            fontsize=12, ha='center', style='italic')
    
    # Linkography Patterns Section
    pattern_box = FancyBboxPatch((0.5, 5.5), 4, 3,
                                boxstyle="round,pad=0.1",
                                facecolor='#E8E8FF',
                                edgecolor='black',
                                linewidth=2)
    ax.add_patch(pattern_box)
    ax.text(2.5, 8.2, 'LINKOGRAPHY PATTERNS', fontsize=12, fontweight='bold', ha='center')
    
    patterns = [
        ('Link Density', 'High interconnection → Deep thinking'),
        ('Critical Moves', 'Pivotal moments → Breakthroughs'),
        ('Orphan Sequences', 'Isolated moves → Struggling'),
        ('Web Formations', 'Complex links → Integration'),
        ('Sawtooth Patterns', 'Progressive links → Scaffolding')
    ]
    
    for i, (pattern, meaning) in enumerate(patterns):
        ax.text(0.7, 7.7 - i*0.5, f'• {pattern}:', fontsize=10, fontweight='bold')
        ax.text(0.9, 7.4 - i*0.5, f'  {meaning}', fontsize=9, style='italic')
    
    # Cognitive Mapping Section
    mapping_box = FancyBboxPatch((5.5, 5.5), 4, 3,
                                boxstyle="round,pad=0.1",
                                facecolor='#FFE8E8',
                                edgecolor='black',
                                linewidth=2)
    ax.add_patch(mapping_box)
    ax.text(7.5, 8.2, 'COGNITIVE MAPPINGS', fontsize=12, fontweight='bold', ha='center')
    
    mappings = [
        ('Deep Thinking:', 'Link density × Web structures'),
        ('Offloading Prevention:', 'Low orphan ratio'),
        ('Scaffolding:', 'Sawtooth + Phase balance'),
        ('Knowledge Integration:', 'Cross-phase links'),
        ('Learning Progression:', 'Expanding link range')
    ]
    
    for i, (metric, formula) in enumerate(mappings):
        ax.text(5.7, 7.7 - i*0.5, metric, fontsize=10, fontweight='bold')
        ax.text(5.9, 7.4 - i*0.5, formula, fontsize=9, style='italic')
    
    # Example Linkograph Visualization
    example_box = FancyBboxPatch((1, 1), 8, 3.5,
                                boxstyle="round,pad=0.1",
                                facecolor='#F5F5F5',
                                edgecolor='black',
                                linewidth=2)
    ax.add_patch(example_box)
    ax.text(5, 4.2, 'Example Linkograph Analysis', fontsize=12, fontweight='bold', ha='center')
    
    # Draw simplified linkograph
    moves = np.linspace(1.5, 8.5, 10)
    move_y = 2.8
    
    # Draw moves
    for i, x in enumerate(moves):
        circle = plt.Circle((x, move_y), 0.15, color='lightblue', ec='black')
        ax.add_patch(circle)
        ax.text(x, move_y, str(i+1), fontsize=8, ha='center', va='center')
    
    # Draw links (simplified)
    links = [(0, 2), (1, 3), (2, 5), (3, 4), (4, 6), (5, 7), (6, 8), (7, 9)]
    for start, end in links:
        ax.plot([moves[start], moves[end]], [move_y-0.15, move_y-0.15], 
               'k-', alpha=0.5, linewidth=1)
    
    # Label patterns
    ax.text(2.5, 2, 'Web formation', fontsize=9, ha='center', color='green')
    ax.text(7, 2, 'Sequential links', fontsize=9, ha='center', color='blue')
    
    # Metrics derived
    ax.text(5, 1.5, 'Derived Metrics: Link Density = 0.8 | Critical Moves = 3 | Deep Thinking = High',
           fontsize=10, ha='center', style='italic', 
           bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create and save both diagrams
    fig1 = create_measurement_flow_diagram()
    fig1.savefig('measurement_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    fig2 = create_linkography_measurement_diagram()
    fig2.savefig('linkography_measurement_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Measurement flow diagrams created successfully!")
    print("- measurement_flow_diagram.png")
    print("- linkography_measurement_diagram.png")