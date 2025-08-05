"""
Generate comprehensive measurement flow diagrams for the MEGA benchmarking system
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np

# Import the actual thesis colors
from thesis_colors import THESIS_COLORS, METRIC_COLORS, COLOR_GRADIENTS

def create_calculation_flow_diagram():
    """Create the overall calculation flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define component positions
    components = {
        'input': {'pos': (2, 9), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_purple']},
        'logger': {'pos': (2, 7), 'size': (3, 1.5), 'color': THESIS_COLORS['neutral_light']},
        'evaluator': {'pos': (7, 8), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_violet']},
        'graph_ml': {'pos': (12, 9), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_dark']},
        'linkography': {'pos': (12, 6.5), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_rose']},
        'anthropomorphism': {'pos': (12, 4), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_pink']},
        'benchmark': {'pos': (7, 4), 'size': (3, 1.5), 'color': THESIS_COLORS['neutral_warm']},
        'dashboard': {'pos': (7, 1), 'size': (3, 1.5), 'color': THESIS_COLORS['primary_purple']}
    }
    
    # Draw components
    for name, comp in components.items():
        box = FancyBboxPatch(
            comp['pos'], comp['size'][0], comp['size'][1],
            boxstyle="round,pad=0.1",
            facecolor=comp['color'],
            edgecolor='black',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(box)
        
        # Add labels
        labels = {
            'input': 'User Interactions\n(thesis_data/*.csv)',
            'logger': 'Interaction Logger\n(interaction_logger.py)',
            'evaluator': 'Evaluation Metrics\n(evaluation_metrics.py)',
            'graph_ml': 'Graph ML Analysis\n(graph_ml_benchmarking.py)',
            'linkography': 'Linkography Engine\n(linkography_analyzer.py)',
            'anthropomorphism': 'Anthropomorphism\n(anthropomorphism_metrics.py)',
            'benchmark': 'Benchmark Report\n(run_benchmarking.py)',
            'dashboard': 'Interactive Dashboard\n(benchmark_dashboard.py)'
        }
        
        ax.text(comp['pos'][0] + comp['size'][0]/2, comp['pos'][1] + comp['size'][1]/2,
                labels[name], ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Draw arrows with labels
    arrows = [
        ('input', 'logger', 'Raw interactions'),
        ('logger', 'evaluator', 'Session data'),
        ('evaluator', 'graph_ml', 'Metrics'),
        ('evaluator', 'linkography', 'Interactions'),
        ('evaluator', 'anthropomorphism', 'Text data'),
        ('graph_ml', 'benchmark', 'Graph features'),
        ('linkography', 'benchmark', 'Design patterns'),
        ('anthropomorphism', 'benchmark', 'Human factors'),
        ('benchmark', 'dashboard', 'Aggregated results')
    ]
    
    for start, end, label in arrows:
        start_pos = (components[start]['pos'][0] + components[start]['size'][0]/2,
                    components[start]['pos'][1])
        end_pos = (components[end]['pos'][0] + components[end]['size'][0]/2,
                  components[end]['pos'][1] + components[end]['size'][1])
        
        if start == 'evaluator' and end in ['graph_ml', 'linkography', 'anthropomorphism']:
            # Special handling for branching arrows
            mid_x = start_pos[0] + 2
            arrow = FancyArrowPatch(start_pos, (mid_x, start_pos[1]),
                                  arrowstyle='->', mutation_scale=20,
                                  color='black', linewidth=2)
            ax.add_patch(arrow)
            arrow2 = FancyArrowPatch((mid_x, start_pos[1]), end_pos,
                                   arrowstyle='->', mutation_scale=20,
                                   color='black', linewidth=2)
            ax.add_patch(arrow2)
        else:
            arrow = FancyArrowPatch(start_pos, end_pos,
                                  arrowstyle='->', mutation_scale=20,
                                  color='black', linewidth=2)
            ax.add_patch(arrow)
        
        # Add arrow labels
        mid_point = ((start_pos[0] + end_pos[0])/2, (start_pos[1] + end_pos[1])/2)
        ax.text(mid_point[0] + 0.5, mid_point[1], label, fontsize=8, style='italic')
    
    # Add title and annotations
    ax.text(8.5, 11, 'MEGA Benchmarking System - Calculation Flow', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Add metric boxes
    metric_y = 10.5
    metrics = [
        ('Cognitive Offloading Prevention', METRIC_COLORS['cognitive_offloading']),
        ('Deep Thinking Engagement', METRIC_COLORS['deep_thinking']),
        ('Scaffolding Effectiveness', METRIC_COLORS['scaffolding']),
        ('Knowledge Integration', METRIC_COLORS['knowledge_integration'])
    ]
    
    for i, (metric, color) in enumerate(metrics):
        x = 2 + i * 3.5
        box = Rectangle((x, metric_y), 3, 0.5, facecolor=color, alpha=0.6)
        ax.add_patch(box)
        ax.text(x + 1.5, metric_y + 0.25, metric, ha='center', va='center', fontsize=8)
    
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('benchmarking_calculation_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_metric_calculation_diagram():
    """Create detailed metric calculation diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Central metric node
    center = (7, 5)
    central_circle = Circle(center, 1.5, facecolor=THESIS_COLORS['primary_purple'], 
                           edgecolor='black', linewidth=2, alpha=0.8)
    ax.add_patch(central_circle)
    ax.text(center[0], center[1], 'Session\nMetrics', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')
    
    # Surrounding metric calculations
    metrics = [
        {'name': 'Cognitive\nOffloading\nPrevention', 'angle': 0, 'formula': 'prevented_count /\ntotal_direct_questions'},
        {'name': 'Deep Thinking\nEngagement', 'angle': 60, 'formula': 'deep_responses /\ntotal_responses'},
        {'name': 'Scaffolding\nEffectiveness', 'angle': 120, 'formula': 'scaffolded_gaps /\ntotal_gaps'},
        {'name': 'Knowledge\nIntegration', 'angle': 180, 'formula': 'integrated_sources /\ntotal_interactions'},
        {'name': 'Skill\nProgression', 'angle': 240, 'formula': '(final_level - initial_level) /\nmax_progression'},
        {'name': 'Engagement\nConsistency', 'angle': 300, 'formula': '1 - std_dev(response_times) /\nmean(response_times)'}
    ]
    
    radius = 3.5
    for metric in metrics:
        angle_rad = np.radians(metric['angle'])
        x = center[0] + radius * np.cos(angle_rad)
        y = center[1] + radius * np.sin(angle_rad)
        
        # Metric box
        box = FancyBboxPatch((x-1.2, y-0.8), 2.4, 1.6,
                            boxstyle="round,pad=0.1",
                            facecolor=THESIS_COLORS['neutral_warm'],
                            edgecolor='black',
                            linewidth=1.5,
                            alpha=0.8)
        ax.add_patch(box)
        
        # Metric name
        ax.text(x, y+0.3, metric['name'], ha='center', va='center',
                fontsize=9, fontweight='bold')
        
        # Formula
        ax.text(x, y-0.3, metric['formula'], ha='center', va='center',
                fontsize=7, style='italic', color='gray')
        
        # Arrow from center
        arrow = FancyArrowPatch((center[0] + 1.3*np.cos(angle_rad), 
                               center[1] + 1.3*np.sin(angle_rad)),
                              (x - 1.0*np.cos(angle_rad), y - 1.0*np.sin(angle_rad)),
                              arrowstyle='->', mutation_scale=15,
                              color='black', linewidth=1.5)
        ax.add_patch(arrow)
    
    # Add data flow indicators
    ax.text(7, 9, 'Metric Calculation Details', fontsize=16, fontweight='bold', ha='center')
    
    # Add baseline comparison box
    baseline_box = FancyBboxPatch((11, 7), 3, 2,
                                 boxstyle="round,pad=0.1",
                                 facecolor=THESIS_COLORS['primary_pink'],
                                 edgecolor='black',
                                 linewidth=2,
                                 alpha=0.8)
    ax.add_patch(baseline_box)
    ax.text(12.5, 8.3, 'Baseline Comparison', ha='center', fontweight='bold')
    ax.text(12.5, 7.8, 'Traditional: 30%', ha='center', fontsize=8)
    ax.text(12.5, 7.5, 'Deep Thinking: 35%', ha='center', fontsize=8)
    ax.text(12.5, 7.2, 'From Literature', ha='center', fontsize=7, style='italic')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('metric_calculation_details.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_linkography_measurement_diagram():
    """Create linkography measurement flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Step 1: Design Move Extraction
    step1_box = FancyBboxPatch((1, 7), 3, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=THESIS_COLORS['primary_rose'],
                              edgecolor='black', linewidth=2)
    ax.add_patch(step1_box)
    ax.text(2.5, 7.75, 'Step 1:\nDesign Move Extraction', ha='center', va='center', fontweight='bold')
    
    # Step 2: Semantic Embedding
    step2_box = FancyBboxPatch((5, 7), 3, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=THESIS_COLORS['primary_violet'],
                              edgecolor='black', linewidth=2)
    ax.add_patch(step2_box)
    ax.text(6.5, 7.75, 'Step 2:\nSemantic Embedding', ha='center', va='center', fontweight='bold')
    
    # Step 3: Link Generation
    step3_box = FancyBboxPatch((9, 7), 3, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=THESIS_COLORS['primary_rose'],
                              edgecolor='black', linewidth=2)
    ax.add_patch(step3_box)
    ax.text(10.5, 7.75, 'Step 3:\nFuzzy Link Generation', ha='center', va='center', fontweight='bold')
    
    # Arrows between steps
    arrow1 = FancyArrowPatch((4, 7.75), (5, 7.75),
                            arrowstyle='->', mutation_scale=20,
                            color='black', linewidth=2)
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((8, 7.75), (9, 7.75),
                            arrowstyle='->', mutation_scale=20,
                            color='black', linewidth=2)
    ax.add_patch(arrow2)
    
    # Details for each step
    # Step 1 details
    ax.text(2.5, 6, 'Extract meaningful\ndesign actions from\ninteractions', 
            ha='center', va='top', fontsize=8)
    
    # Step 2 details
    ax.text(6.5, 6, 'Convert moves to\nvector embeddings\n(all-MiniLM-L6-v2)', 
            ha='center', va='top', fontsize=8)
    
    # Step 3 details
    ax.text(10.5, 6, 'Calculate semantic\nsimilarity > 0.65\nfor links', 
            ha='center', va='top', fontsize=8)
    
    # Metrics calculation
    metrics_box = FancyBboxPatch((3, 3), 8, 2,
                                boxstyle="round,pad=0.1",
                                facecolor=THESIS_COLORS['neutral_warm'],
                                edgecolor='black', linewidth=2)
    ax.add_patch(metrics_box)
    
    ax.text(7, 4.5, 'Linkography Metrics', ha='center', fontweight='bold', fontsize=11)
    
    # Metric formulas
    metrics_text = [
        'Link Density = Total Links / Total Moves',
        'Critical Moves = Moves with links > mean + std_dev',
        'Phase Balance = Distribution across Ideation/Visualization/Materialization'
    ]
    
    for i, text in enumerate(metrics_text):
        ax.text(7, 3.8 - i*0.3, text, ha='center', fontsize=8)
    
    # Arrow from step 3 to metrics
    arrow3 = FancyArrowPatch((10.5, 7), (7, 5),
                            arrowstyle='->', mutation_scale=20,
                            color='black', linewidth=2, connectionstyle="arc3,rad=0.3")
    ax.add_patch(arrow3)
    
    # Title
    ax.text(7, 9, 'Linkography Measurement Process', fontsize=16, fontweight='bold', ha='center')
    
    # Add Goldschmidt reference
    ax.text(7, 1, 'Based on Goldschmidt (2014): "Linkography: Unfolding the Design Process"',
            ha='center', fontsize=8, style='italic')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('linkography_measurement_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_anthropomorphism_calculation_diagram():
    """Create anthropomorphism metrics calculation diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Input data
    input_box = FancyBboxPatch((5, 8.5), 4, 1,
                              boxstyle="round,pad=0.1",
                              facecolor=THESIS_COLORS['neutral_light'],
                              edgecolor='black', linewidth=2)
    ax.add_patch(input_box)
    ax.text(7, 9, 'Session Interactions', ha='center', va='center', fontweight='bold')
    
    # Four main metrics
    metrics_data = [
        {'name': 'CAI\n(Cognitive Autonomy)', 'pos': (1, 6), 'color': THESIS_COLORS['primary_violet']},
        {'name': 'ADS\n(Anthropomorphic\nDependency)', 'pos': (4.5, 6), 'color': THESIS_COLORS['primary_rose']},
        {'name': 'PBI\n(Professional\nBoundary)', 'pos': (8, 6), 'color': THESIS_COLORS['primary_pink']},
        {'name': 'NES\n(Neural\nEngagement)', 'pos': (11.5, 6), 'color': THESIS_COLORS['primary_purple']}
    ]
    
    for metric in metrics_data:
        box = FancyBboxPatch((metric['pos'][0]-1, metric['pos'][1]-0.75), 2, 1.5,
                            boxstyle="round,pad=0.1",
                            facecolor=metric['color'],
                            edgecolor='black', linewidth=2, alpha=0.8)
        ax.add_patch(box)
        ax.text(metric['pos'][0], metric['pos'][1], metric['name'], 
                ha='center', va='center', fontweight='bold', fontsize=9)
        
        # Arrow from input
        arrow = FancyArrowPatch((7, 8.5), metric['pos'],
                               arrowstyle='->', mutation_scale=15,
                               color='black', linewidth=1.5)
        ax.add_patch(arrow)
    
    # Calculation details for each metric
    calc_details = [
        {'pos': (1, 4.5), 'text': 'autonomy_ratio -\n0.5 * dependency_ratio'},
        {'pos': (4.5, 4.5), 'text': 'personal_attributions +\nemotional_language'},
        {'pos': (8, 4.5), 'text': '1 - conversation_drift -\npersonal_intrusions'},
        {'pos': (11.5, 4.5), 'text': 'concept_diversity +\ntechnical_vocabulary'}
    ]
    
    for detail in calc_details:
        ax.text(detail['pos'][0], detail['pos'][1], detail['text'],
                ha='center', va='center', fontsize=7, style='italic')
    
    # Overall dependency score
    dep_box = FancyBboxPatch((4.5, 2), 4, 1.2,
                            boxstyle="round,pad=0.1",
                            facecolor=THESIS_COLORS['neutral_warm'],
                            edgecolor='black', linewidth=2)
    ax.add_patch(dep_box)
    ax.text(6.5, 2.6, 'Overall Dependency Score', ha='center', va='center', fontweight='bold')
    ax.text(6.5, 2.2, '(1-CAI)*0.3 + ADS*0.3 + (1-BRS)*0.2 + (1-CIR)*0.2',
            ha='center', va='center', fontsize=7)
    
    # Arrows to dependency score
    for metric in metrics_data:
        arrow = FancyArrowPatch(metric['pos'], (6.5, 3.2),
                               arrowstyle='->', mutation_scale=10,
                               color='gray', linewidth=1, linestyle='dashed')
        ax.add_patch(arrow)
    
    # Title
    ax.text(7, 10, 'Anthropomorphism Metrics Calculation', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Reference
    ax.text(7, 0.5, 'Based on HCI research: Nass & Moon (2000), Self-Determination Theory: Deci & Ryan (1985)',
            ha='center', fontsize=7, style='italic')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.5)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('anthropomorphism_calculation_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_graph_ml_processing_diagram():
    """Create Graph ML processing flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Processing pipeline
    pipeline_steps = [
        {'name': 'Session\nInteractions', 'pos': (1, 7), 'color': THESIS_COLORS['neutral_light']},
        {'name': 'Graph\nConstruction', 'pos': (4, 7), 'color': THESIS_COLORS['primary_dark']},
        {'name': 'Feature\nExtraction', 'pos': (7, 7), 'color': THESIS_COLORS['primary_purple']},
        {'name': 'GNN\nProcessing', 'pos': (10, 7), 'color': THESIS_COLORS['primary_violet']},
        {'name': 'Proficiency\nClustering', 'pos': (13, 7), 'color': THESIS_COLORS['primary_rose']}
    ]
    
    for i, step in enumerate(pipeline_steps):
        box = FancyBboxPatch((step['pos'][0]-0.8, step['pos'][1]-0.6), 1.6, 1.2,
                            boxstyle="round,pad=0.1",
                            facecolor=step['color'],
                            edgecolor='black', linewidth=2, alpha=0.8)
        ax.add_patch(box)
        ax.text(step['pos'][0], step['pos'][1], step['name'],
                ha='center', va='center', fontweight='bold', fontsize=9)
        
        # Arrows between steps
        if i < len(pipeline_steps) - 1:
            arrow = FancyArrowPatch((step['pos'][0] + 0.8, step['pos'][1]),
                                   (pipeline_steps[i+1]['pos'][0] - 0.8, pipeline_steps[i+1]['pos'][1]),
                                   arrowstyle='->', mutation_scale=15,
                                   color='black', linewidth=2)
            ax.add_patch(arrow)
    
    # Details for each step
    details = [
        {'pos': (1, 5.5), 'text': 'Load CSV data\nwith interactions'},
        {'pos': (4, 5.5), 'text': 'Nodes: interactions\nEdges: semantic +\ntemporal links'},
        {'pos': (7, 5.5), 'text': 'Node degree\nClustering coeff\nBetweenness'},
        {'pos': (10, 5.5), 'text': 'GraphSAGE\nneighborhood\naggregation'},
        {'pos': (13, 5.5), 'text': 'K-means on\nlearned embeddings'}
    ]
    
    for detail in details:
        ax.text(detail['pos'][0], detail['pos'][1], detail['text'],
                ha='center', va='center', fontsize=7, style='italic')
    
    # Graph features visualization
    graph_box = FancyBboxPatch((3, 2.5), 8, 2,
                              boxstyle="round,pad=0.1",
                              facecolor=THESIS_COLORS['neutral_warm'],
                              edgecolor='black', linewidth=2)
    ax.add_patch(graph_box)
    
    ax.text(7, 3.8, 'Extracted Graph Features', ha='center', fontweight='bold')
    features = [
        'avg_degree: Average node connections',
        'clustering_coeff: Local graph density',
        'avg_path_length: Information flow efficiency',
        'modularity: Community structure strength'
    ]
    
    for i, feature in enumerate(features):
        ax.text(7, 3.3 - i*0.25, feature, ha='center', fontsize=7)
    
    # Title
    ax.text(7, 9, 'Graph ML Processing Pipeline', fontsize=16, fontweight='bold', ha='center')
    
    # Reference
    ax.text(7, 1, 'Based on GraphSAGE: Hamilton et al. (2017)',
            ha='center', fontsize=8, style='italic')
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('graph_ml_processing_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_comprehensive_benchmarking_structure():
    """Create comprehensive benchmarking structure diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Title
    ax.text(8, 11, 'MEGA Benchmarking System Structure', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Data layer
    data_box = FancyBboxPatch((1, 8.5), 14, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=THESIS_COLORS['neutral_light'],
                             edgecolor='black', linewidth=2)
    ax.add_patch(data_box)
    ax.text(8, 9.25, 'DATA LAYER', ha='center', fontweight='bold', fontsize=11)
    
    data_sources = ['thesis_data/*.csv', 'session_*.json', 'evaluation_reports/*.json', 'linkography/*.json']
    for i, source in enumerate(data_sources):
        ax.text(2 + i*3.5, 8.8, source, ha='center', fontsize=8)
    
    # Processing layer
    process_box = FancyBboxPatch((1, 5.5), 14, 2.5,
                                boxstyle="round,pad=0.1",
                                facecolor=THESIS_COLORS['neutral_warm'],
                                edgecolor='black', linewidth=2, alpha=0.7)
    ax.add_patch(process_box)
    ax.text(8, 7.5, 'PROCESSING LAYER', ha='center', fontweight='bold', fontsize=11)
    
    # Processing components
    processors = [
        {'name': 'Evaluation\nMetrics', 'pos': (3, 6.5), 'color': THESIS_COLORS['primary_violet']},
        {'name': 'Graph ML\nAnalysis', 'pos': (6, 6.5), 'color': THESIS_COLORS['primary_dark']},
        {'name': 'Linkography\nEngine', 'pos': (9, 6.5), 'color': THESIS_COLORS['primary_purple']},
        {'name': 'Anthropomorphism\nAnalysis', 'pos': (12, 6.5), 'color': THESIS_COLORS['primary_rose']}
    ]
    
    for proc in processors:
        circle = Circle(proc['pos'], 0.8, facecolor=proc['color'], 
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        ax.add_patch(circle)
        ax.text(proc['pos'][0], proc['pos'][1], proc['name'],
                ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Analytics layer
    analytics_box = FancyBboxPatch((1, 2.5), 14, 2.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor=THESIS_COLORS['primary_violet'],
                                  edgecolor='black', linewidth=2, alpha=0.7)
    ax.add_patch(analytics_box)
    ax.text(8, 4.5, 'ANALYTICS LAYER', ha='center', fontweight='bold', 
            fontsize=11, color='white')
    
    # Analytics components
    analytics = [
        'Cognitive Patterns', 'Learning Progression', 'Agent Performance',
        'Proficiency Analysis', 'Comparative Metrics'
    ]
    for i, comp in enumerate(analytics):
        ax.text(2.5 + i*2.5, 3.5, comp, ha='center', fontsize=8, color='white')
    
    # Visualization layer
    viz_box = FancyBboxPatch((1, 0.5), 14, 1.5,
                            boxstyle="round,pad=0.1",
                            facecolor=THESIS_COLORS['primary_purple'],
                            edgecolor='black', linewidth=2, alpha=0.8)
    ax.add_patch(viz_box)
    ax.text(8, 1.25, 'VISUALIZATION LAYER', ha='center', fontweight='bold', 
            fontsize=11, color='white')
    
    viz_types = ['Interactive Dashboard', 'PyVis Networks', 'Plotly Charts', 'Export Reports']
    for i, viz in enumerate(viz_types):
        ax.text(2.5 + i*3, 0.8, viz, ha='center', fontsize=8, color='white')
    
    # Arrows showing data flow
    for i in range(4):
        # Data to Processing
        arrow1 = FancyArrowPatch((2 + i*3.5, 8.5), (processors[i]['pos'][0], processors[i]['pos'][1] + 0.8),
                                arrowstyle='->', mutation_scale=10,
                                color='gray', linewidth=1)
        ax.add_patch(arrow1)
        
        # Processing to Analytics
        arrow2 = FancyArrowPatch((processors[i]['pos'][0], processors[i]['pos'][1] - 0.8), 
                                (processors[i]['pos'][0], 4.8),
                                arrowstyle='->', mutation_scale=10,
                                color='gray', linewidth=1)
        ax.add_patch(arrow2)
    
    # Analytics to Visualization
    arrow3 = FancyArrowPatch((8, 2.5), (8, 2),
                            arrowstyle='->', mutation_scale=15,
                            color='black', linewidth=2)
    ax.add_patch(arrow3)
    
    # Add theoretical foundations sidebar
    theory_box = FancyBboxPatch((15.5, 2), 3, 8,
                               boxstyle="round,pad=0.1",
                               facecolor=THESIS_COLORS['neutral_warm'],
                               edgecolor='black', linewidth=1.5)
    ax.add_patch(theory_box)
    ax.text(17, 9.5, 'Theoretical\nFoundations', ha='center', fontweight='bold')
    
    theories = [
        "Bloom's Taxonomy",
        "Vygotsky's ZPD",
        "Goldschmidt's\nLinkography",
        "Self-Determination\nTheory",
        "Graph Neural\nNetworks",
        "Cognitive Load\nTheory"
    ]
    
    for i, theory in enumerate(theories):
        ax.text(17, 8.5 - i*1.1, theory, ha='center', fontsize=7)
    
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('comprehensive_benchmarking_structure.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating measurement flow diagrams...")
    
    # Generate all diagrams
    create_calculation_flow_diagram()
    print("[OK] Created benchmarking_calculation_flow.png")
    
    create_metric_calculation_diagram()
    print("[OK] Created metric_calculation_details.png")
    
    create_linkography_measurement_diagram()
    print("[OK] Created linkography_measurement_flow.png")
    
    create_anthropomorphism_calculation_diagram()
    print("[OK] Created anthropomorphism_calculation_flow.png")
    
    create_graph_ml_processing_diagram()
    print("[OK] Created graph_ml_processing_flow.png")
    
    create_comprehensive_benchmarking_structure()
    print("[OK] Created comprehensive_benchmarking_structure.png")
    
    print("\nAll diagrams generated successfully!")