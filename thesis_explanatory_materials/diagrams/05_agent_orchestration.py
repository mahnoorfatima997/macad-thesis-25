"""
Agent Orchestration Diagram Generator
Creates visual representation of the multi-agent system workflow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse, Wedge, Polygon
import numpy as np
import os
import sys

# Add the benchmarking directory to the path to import thesis colors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarking'))
from thesis_colors import THESIS_COLORS, METRIC_COLORS, UI_COLORS

def create_agent_orchestration_diagram():
    """Create comprehensive agent orchestration workflow diagram"""
    
    # Create figure with proper sizing
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define orchestration components
    components = {
        # Central Orchestrator
        'langgraph_orchestrator': {
            'pos': (8, 6), 'size': (2.5, 2.5), 
            'color': THESIS_COLORS['primary_dark'],
            'shape': 'circle',
            'text': 'LangGraph\nOrchestrator',
            'details': 'Central Coordination\nWorkflow Management\nState Tracking'
        },
        
        # Input Processing
        'user_input': {
            'pos': (8, 10), 'size': (2, 1), 
            'color': THESIS_COLORS['primary_purple'],
            'shape': 'rectangle',
            'text': 'User Input',
            'details': 'Text & Image\nProcessing'
        },
        
        # Context Analysis
        'context_agent': {
            'pos': (4, 8.5), 'size': (1.8, 1.2), 
            'color': METRIC_COLORS['context_agent'],
            'shape': 'hexagon',
            'text': 'Context\nAgent',
            'details': '• Input Classification\n• Skill Assessment\n• Routing Decision\n• Session Context'
        },
        
        # Multi-Agent System
        'socratic_tutor': {
            'pos': (2, 6), 'size': (1.8, 1.2), 
            'color': METRIC_COLORS['socratic_tutor'],
            'shape': 'hexagon',
            'text': 'Socratic\nTutor',
            'details': '• Questioning Strategy\n• Critical Thinking\n• Dialogue Management\n• Learning Guidance'
        },
        
        'domain_expert': {
            'pos': (5, 4), 'size': (1.8, 1.2), 
            'color': METRIC_COLORS['domain_expert'],
            'shape': 'hexagon',
            'text': 'Domain\nExpert',
            'details': '• Knowledge Retrieval\n• Technical Accuracy\n• Context Integration\n• Resource Provision'
        },
        
        'cognitive_enhancement': {
            'pos': (11, 4), 'size': (1.8, 1.2), 
            'color': METRIC_COLORS['cognitive_enhancement'],
            'shape': 'hexagon',
            'text': 'Cognitive\nEnhancement',
            'details': '• Scaffolding Design\n• Challenge Calibration\n• Metacognitive Prompts\n• Offloading Prevention'
        },
        
        'analysis_agent': {
            'pos': (14, 6), 'size': (1.8, 1.2), 
            'color': METRIC_COLORS['analysis_agent'],
            'shape': 'hexagon',
            'text': 'Analysis\nAgent',
            'details': '• Performance Tracking\n• Pattern Recognition\n• Metric Calculation\n• Progress Assessment'
        },
        
        # Knowledge Resources
        'knowledge_base': {
            'pos': (2, 3), 'size': (2, 1), 
            'color': THESIS_COLORS['neutral_warm'],
            'shape': 'rectangle',
            'text': 'Knowledge\nBase',
            'details': 'Architectural\nDocuments & Resources'
        },
        
        'vector_store': {
            'pos': (5, 2), 'size': (2, 1), 
            'color': THESIS_COLORS['neutral_orange'],
            'shape': 'rectangle',
            'text': 'Vector\nStore',
            'details': 'Semantic Search\n& Retrieval'
        },
        
        'image_analyzer': {
            'pos': (11, 2), 'size': (2, 1), 
            'color': THESIS_COLORS['accent_coral'],
            'shape': 'rectangle',
            'text': 'Image\nAnalyzer',
            'details': 'Visual Processing\n& Analysis'
        },
        
        # Output Synthesis
        'response_synthesizer': {
            'pos': (8, 2), 'size': (2, 1.2), 
            'color': THESIS_COLORS['primary_pink'],
            'shape': 'rectangle',
            'text': 'Response\nSynthesizer',
            'details': 'Multi-Agent\nResponse Integration'
        },
        
        # Final Output
        'final_response': {
            'pos': (8, 0.5), 'size': (2.5, 0.8), 
            'color': THESIS_COLORS['primary_violet'],
            'shape': 'rectangle',
            'text': 'Final Response',
            'details': 'Coherent Educational Response'
        },
    }
    
    # Draw components
    for name, config in components.items():
        x, y = config['pos']
        width, height = config['size']
        color = config['color']
        shape = config['shape']
        text = config['text']
        
        if shape == 'circle':
            # Central orchestrator as circle
            circle = Circle((x, y), width/2, facecolor=color, 
                          edgecolor='white', linewidth=3, alpha=0.85)
            ax.add_patch(circle)
        elif shape == 'hexagon':
            # Agents as hexagons
            angles = np.linspace(0, 2*np.pi, 7)
            hex_points = [(x + width/2 * np.cos(a), y + height/2 * np.sin(a)) for a in angles[:-1]]
            hexagon = Polygon(hex_points, facecolor=color, 
                            edgecolor='white', linewidth=2.5, alpha=0.85)
            ax.add_patch(hexagon)
        else:
            # Rectangles for other components
            box = FancyBboxPatch(
                (x - width/2, y - height/2), width, height,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='white', linewidth=2, alpha=0.85
            )
            ax.add_patch(box)
        
        # Add main text
        ax.text(x, y + 0.1, text, ha='center', va='center',
               fontsize=10, fontweight='bold', color='white')
    
    # Define orchestration workflow connections
    workflow_connections = [
        # Input flow
        ('user_input', 'context_agent'),
        ('context_agent', 'langgraph_orchestrator'),
        
        # Agent activation from orchestrator
        ('langgraph_orchestrator', 'socratic_tutor'),
        ('langgraph_orchestrator', 'domain_expert'),
        ('langgraph_orchestrator', 'cognitive_enhancement'),
        ('langgraph_orchestrator', 'analysis_agent'),
        
        # Knowledge resource connections
        ('domain_expert', 'knowledge_base'),
        ('domain_expert', 'vector_store'),
        ('cognitive_enhancement', 'image_analyzer'),
        
        # Response synthesis
        ('socratic_tutor', 'response_synthesizer'),
        ('domain_expert', 'response_synthesizer'),
        ('cognitive_enhancement', 'response_synthesizer'),
        ('analysis_agent', 'response_synthesizer'),
        
        # Final output
        ('response_synthesizer', 'final_response'),
    ]
    
    # Draw workflow connections
    for start, end in workflow_connections:
        start_pos = components[start]['pos']
        end_pos = components[end]['pos']
        
        # Different arrow styles for different connection types
        if start == 'langgraph_orchestrator':
            # Orchestrator to agents - thick arrows
            arrow = FancyArrowPatch(
                start_pos, end_pos,
                arrowstyle='->', mutation_scale=20,
                color=THESIS_COLORS['primary_dark'], linewidth=3, alpha=0.8,
                connectionstyle="arc3,rad=0.1"
            )
        elif end == 'response_synthesizer':
            # Agents to synthesizer - colored arrows
            agent_colors = {
                'socratic_tutor': METRIC_COLORS['socratic_tutor'],
                'domain_expert': METRIC_COLORS['domain_expert'],
                'cognitive_enhancement': METRIC_COLORS['cognitive_enhancement'],
                'analysis_agent': METRIC_COLORS['analysis_agent'],
            }
            arrow_color = agent_colors.get(start, THESIS_COLORS['primary_purple'])
            arrow = FancyArrowPatch(
                start_pos, end_pos,
                arrowstyle='->', mutation_scale=18,
                color=arrow_color, linewidth=2.5, alpha=0.7,
                connectionstyle="arc3,rad=0.2"
            )
        else:
            # Regular connections
            arrow = FancyArrowPatch(
                start_pos, end_pos,
                arrowstyle='->', mutation_scale=15,
                color=THESIS_COLORS['primary_purple'], linewidth=2, alpha=0.6
            )
        
        ax.add_patch(arrow)
    
    # Add decision flow indicators
    decision_points = [
        {
            'pos': (6, 7.5), 
            'text': 'Routing\nDecision', 
            'color': THESIS_COLORS['accent_coral'],
            'connections': ['socratic_tutor', 'domain_expert', 'cognitive_enhancement']
        }
    ]
    
    for decision in decision_points:
        # Decision diamond
        diamond_points = [
            (decision['pos'][0], decision['pos'][1] + 0.4),  # top
            (decision['pos'][0] + 0.4, decision['pos'][1]),  # right
            (decision['pos'][0], decision['pos'][1] - 0.4),  # bottom
            (decision['pos'][0] - 0.4, decision['pos'][1])   # left
        ]
        diamond = Polygon(diamond_points, facecolor=decision['color'],
                         edgecolor='white', linewidth=2, alpha=0.8)
        ax.add_patch(diamond)
        
        ax.text(decision['pos'][0], decision['pos'][1], decision['text'],
               ha='center', va='center', fontsize=8, fontweight='bold', color='white')
    
    # Add parallel processing indicators
    parallel_indicators = [
        {'center': (8, 4.5), 'agents': ['socratic_tutor', 'domain_expert', 'cognitive_enhancement']},
    ]
    
    for parallel in parallel_indicators:
        center = parallel['center']
        # Draw parallel processing arc
        arc = Wedge(center, 3, -45, 225, width=0.3, 
                   facecolor=THESIS_COLORS['neutral_light'], 
                   edgecolor=THESIS_COLORS['primary_dark'],
                   alpha=0.4, linewidth=2)
        ax.add_patch(arc)
        
        ax.text(center[0], center[1], 'Parallel\nProcessing', 
               ha='center', va='center', fontsize=9, fontweight='bold',
               color=THESIS_COLORS['primary_dark'], style='italic')
    
    # Add state management indicators
    state_flows = [
        {'pos': (10.5, 7), 'text': 'State\nUpdates', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (5.5, 7), 'text': 'Context\nSharing', 'color': THESIS_COLORS['primary_rose']},
    ]
    
    for state in state_flows:
        # Bidirectional arrow for state management
        arrow1 = FancyArrowPatch(
            (state['pos'][0] - 0.3, state['pos'][1]), 
            (8 - 1.25, 6),  # To orchestrator
            arrowstyle='<->', mutation_scale=12,
            color=state['color'], linewidth=1.5, alpha=0.5,
            linestyle='--'
        )
        ax.add_patch(arrow1)
        
        ax.text(state['pos'][0], state['pos'][1], state['text'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               color=state['color'],
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add agent specializations with small detail boxes
    specializations = [
        {'agent': 'socratic_tutor', 'details': components['socratic_tutor']['details']},
        {'agent': 'domain_expert', 'details': components['domain_expert']['details']},
        {'agent': 'cognitive_enhancement', 'details': components['cognitive_enhancement']['details']},
        {'agent': 'analysis_agent', 'details': components['analysis_agent']['details']},
    ]
    
    for spec in specializations:
        agent_pos = components[spec['agent']]['pos']
        detail_pos = (agent_pos[0], agent_pos[1] - 0.8)
        
        # Small detail box
        detail_box = FancyBboxPatch(
            (detail_pos[0] - 0.9, detail_pos[1] - 0.4), 1.8, 0.8,
            boxstyle="round,pad=0.05",
            facecolor=THESIS_COLORS['neutral_light'], 
            edgecolor=components[spec['agent']]['color'],
            linewidth=1, alpha=0.7
        )
        ax.add_patch(detail_box)
        
        ax.text(detail_pos[0], detail_pos[1], spec['details'],
               ha='center', va='center', fontsize=7, 
               color=THESIS_COLORS['primary_dark'])
    
    # Add timing and coordination indicators
    timing_indicators = [
        {'pos': (3, 8.5), 'text': '~2s\nAnalysis', 'color': THESIS_COLORS['neutral_warm']},
        {'pos': (8, 7.5), 'text': '~8s\nProcessing', 'color': THESIS_COLORS['neutral_warm']},
        {'pos': (13, 8.5), 'text': '~1s\nSynthesis', 'color': THESIS_COLORS['neutral_warm']},
    ]
    
    for timing in timing_indicators:
        ax.text(timing['pos'][0], timing['pos'][1], timing['text'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               color=timing['color'],
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Set axis properties
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add title
    ax.text(8, 11, 'MEGA Architectural Mentor - Agent Orchestration Workflow',
           fontsize=17, fontweight='bold', ha='center',
           color=THESIS_COLORS['primary_dark'])
    
    # Add subtitle
    ax.text(8, 10.7, 'Multi-Agent Coordination and Response Synthesis',
           fontsize=12, ha='center', style='italic',
           color=THESIS_COLORS['primary_purple'])
    
    # Add workflow phases
    phases = [
        {'pos': (2, 10.5), 'text': '1. CONTEXT\nANALYSIS', 'color': THESIS_COLORS['primary_violet']},
        {'pos': (8, 8.5), 'text': '2. AGENT\nORCHESTRATION', 'color': THESIS_COLORS['primary_dark']},
        {'pos': (8, 3.5), 'text': '3. PARALLEL\nPROCESSING', 'color': THESIS_COLORS['accent_magenta']},
        {'pos': (14, 1.5), 'text': '4. RESPONSE\nSYNTHESIS', 'color': THESIS_COLORS['primary_pink']},
    ]
    
    for phase in phases:
        ax.text(phase['pos'][0], phase['pos'][1], phase['text'],
               ha='center', va='center', fontsize=10, fontweight='bold',
               color=phase['color'], style='italic',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=THESIS_COLORS['primary_dark'], label='Orchestration Core'),
        mpatches.Patch(color=METRIC_COLORS['socratic_tutor'], label='Educational Agents'),
        mpatches.Patch(color=THESIS_COLORS['neutral_warm'], label='Knowledge Resources'),
        mpatches.Patch(color=THESIS_COLORS['primary_pink'], label='Response Processing'),
        mpatches.Patch(color=THESIS_COLORS['accent_coral'], label='Decision Points'),
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98),
             frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_diagram():
    """Save the diagram in multiple formats"""
    fig = create_agent_orchestration_diagram()
    
    # Define output paths
    base_path = os.path.dirname(__file__)
    png_path = os.path.join(base_path, '05_agent_orchestration.png')
    svg_path = os.path.join(base_path, '05_agent_orchestration.svg')
    
    # Save as PNG with high DPI
    fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Save as SVG for scalability
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Agent Orchestration diagram saved:")
    print(f"  PNG: {png_path}")
    print(f"  SVG: {svg_path}")
    
    plt.close(fig)

if __name__ == "__main__":
    save_diagram()